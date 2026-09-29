"""
Lesson routes — core business logic for starting lessons and evaluating exercises.
"""

import hashlib
import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text
from zoneinfo import ZoneInfo

from database import get_db
from models import (
    User, LearningProfile, Lesson, LessonExercise, LessonExerciseWord,
    Word, UserWord, Event, DictionaryWord
)
from schemas import (
    LessonPreviewResponse, LessonPreviewWord, LessonPreviewRequest, DeclineWordRequest,
    LessonStartRequest, LessonStartResponse, ExerciseResponse, ExerciseWordResponse,
    EvaluateRequest, EvaluateResponse, LessonSummaryResponse, DontKnowRequest
)
from auth import get_current_user
from srs import calculate_new_stage, calculate_due_lesson_number, is_due, is_mastered
from llm_client import gigachat_client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/lesson", tags=["lesson"])


def get_local_date(timezone_str: str) -> str:
    tz = ZoneInfo(timezone_str)
    return datetime.now(tz).strftime("%Y-%m-%d")


def deterministic_hash(profile_id: int, lesson_number: int, word_id: int) -> int:
    """Deterministic random for word selection."""
    seed = f"{profile_id}:{lesson_number}:{word_id}"
    return int(hashlib.sha256(seed.encode()).hexdigest(), 16)


async def select_words_for_lesson(
    db: AsyncSession,
    profile: LearningProfile,
    declined_word_ids: set[int] | None = None,
) -> tuple[list[dict], list[dict]]:
    """
    Select words for lesson: due words first, then new words.
    Returns (due_words, new_words) as dicts with word info.
    """
    declined = declined_word_ids or set()
    next_lesson = profile.last_lesson_number + 1

    # Get due words
    result = await db.execute(
        select(UserWord, Word)
        .join(Word, UserWord.word_id == Word.id)
        .where(
            UserWord.learning_profile_id == profile.id,
            UserWord.status == "active",
        )
    )
    all_user_words = result.all()

    due_words = []
    for uw, word in all_user_words:
        if word.id in declined:
            continue
        if is_due(uw.stage, uw.due_lesson_number, profile.last_lesson_number):
            due_words.append({
                "word_id": word.id,
                "lemma": word.lemma,
                "pos": word.pos,
                "translations": word.translations,
                "stage": uw.stage,
                "is_new": False,
                "hash": deterministic_hash(profile.id, next_lesson, word.id),
            })

    # Sort by deterministic hash
    due_words.sort(key=lambda x: x["hash"])
    due_words = due_words[:5]  # max 5 due words

    # Get new words (not in user_words) from the selected dictionary
    existing_ids = {uw.word_id for uw, _ in all_user_words}
    
    # Level hierarchy: A1 < A2 < B1 < B2
    # User sees words with level <= their own level
    level_order = {"A1": 1, "A2": 2, "B1": 3, "B2": 4}
    allowed_levels = [
        lvl for lvl, order in level_order.items()
        if order <= level_order.get(profile.level, 4)
    ]
    
    # Join with DictionaryWord to get words from the selected dictionary
    # Filter by word level <= user level
    result = await db.execute(
        select(Word)
        .join(DictionaryWord, DictionaryWord.word_id == Word.id)
        .where(
            DictionaryWord.dictionary_id == profile.dictionary_id,
            Word.level.in_(allowed_levels),
        )
    )
    all_dict_words = result.scalars().all()

    new_words = []
    for word in all_dict_words:
        if word.id in existing_ids or word.id in declined:
            continue
        new_words.append({
            "word_id": word.id,
            "lemma": word.lemma,
            "pos": word.pos,
            "translations": word.translations,
            "stage": 0,
            "is_new": True,
            "hash": deterministic_hash(profile.id, next_lesson, word.id),
        })

    new_words.sort(key=lambda x: x["hash"])
    remaining = max(8 - len(due_words), 3)
    new_words = new_words[:remaining]

    return due_words, new_words


@router.post("/preview", response_model=LessonPreviewResponse)
async def preview_lesson(
    body: LessonPreviewRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Preview lesson composition without writing to DB."""
    result = await db.execute(
        select(LearningProfile).where(LearningProfile.user_id == user.id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=400, detail="No learning profile")

    due_words, new_words = await select_words_for_lesson(
        db, profile, declined_word_ids=set(body.declined_word_ids)
    )

    words = []
    for w in due_words + new_words:
        words.append(LessonPreviewWord(
            id=w["word_id"],
            lemma=w["lemma"],
            translations=w["translations"],
            is_new=w["is_new"],
            is_due=not w["is_new"],
        ))

    return LessonPreviewResponse(words=words)


@router.post("/new-word/decline")
async def decline_word(
    body: DeclineWordRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Decline a word from preview — it won't appear in this lesson."""
    # In production, store declined words in session/cache
    # For now, just acknowledge
    return {"status": "ok", "declined_word_id": body.word_id}


@router.post("/start", response_model=LessonStartResponse)
async def start_lesson(
    body: LessonStartRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    idempotency_key: Optional[str] = Header(None),
):
    """
    Start a new lesson:
    1. Pre-checks (onboarded, no in_progress, limit not reached)
    2. Advisory lock
    3. Select words
    4. LLM generation
    5. Validate response
    6. Transaction write
    """
    # Get profile with FOR UPDATE
    result = await db.execute(
        select(LearningProfile).where(LearningProfile.user_id == user.id).with_for_update()
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=400, detail="No learning profile")

    if not user.is_onboarded:
        raise HTTPException(status_code=400, detail="Onboarding not completed")

    # Check for in_progress lesson
    result = await db.execute(
        select(Lesson).where(
            Lesson.learning_profile_id == profile.id,
            Lesson.status == "in_progress",
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="start_in_progress")

    # Check daily limit
    today = get_local_date(user.timezone)
    result = await db.execute(
        select(func.count(Lesson.id)).where(
            Lesson.learning_profile_id == profile.id,
            Lesson.started_local_date == today,
            Lesson.status != "abandoned",
        )
    )
    lessons_today = result.scalar() or 0
    if lessons_today >= profile.daily_lesson_limit:
        raise HTTPException(status_code=429, detail="Daily lesson limit reached")

    # Select words (excluding declined)
    due_words, new_words = await select_words_for_lesson(
        db, profile, declined_word_ids=set(body.declined_word_ids)
    )
    all_words = due_words + new_words

    if not all_words:
        raise HTTPException(status_code=400, detail="No words available for lesson")

    # Group into clusters of 2-3
    clusters = []
    i = 0
    while i < len(all_words):
        cluster_size = min(2 + (i % 2), len(all_words) - i)  # alternate 2 and 3
        cluster = all_words[i:i + cluster_size]
        clusters.append({"words": cluster})
        i += cluster_size

    # LLM Generation
    try:
        llm_results = await gigachat_client.generate_exercises(
            word_clusters=clusters,
            level=profile.level,
            db=db,
            user_id=user.id,
        )
        logger.info(f"✅ Generated {len(llm_results)} exercises using GigaChat LLM")
    except Exception as e:
        logger.error(f"LLM generation failed: {e}")
        raise HTTPException(status_code=503, detail="Сервис временно недоступен. Попробуйте позже.")

    # Create lesson
    next_lesson_number = profile.last_lesson_number + 1
    lesson = Lesson(
        learning_profile_id=profile.id,
        lesson_number=next_lesson_number,
        status="in_progress",
        started_local_date=today,
    )
    db.add(lesson)
    await db.flush()

    # Create exercises
    exercises_response = []
    for idx, (cluster, llm_result) in enumerate(zip(clusters, llm_results)):
        exercise = LessonExercise(
            lesson_id=lesson.id,
            order_index=idx,
            target_sentence=llm_result["sentence"],
            reference_translation=llm_result["reference_translation"],
            status="pending",
        )
        db.add(exercise)
        await db.flush()

        # Create exercise words
        exercise_words_response = []
        for word_data in cluster["words"]:
            ew = LessonExerciseWord(
                exercise_id=exercise.id,
                word_id=word_data["word_id"],
                is_target=True,
                is_new=word_data["is_new"],
                surface_form=word_data["lemma"],
                stage_before=word_data["stage"],
                stage_after=word_data["stage"],
            )
            db.add(ew)

            exercise_words_response.append(ExerciseWordResponse(
                word_id=word_data["word_id"],
                is_target=True,
                is_new=word_data["is_new"],
                surface_form=word_data["lemma"],
                stage_before=word_data["stage"],
                stage_after=word_data["stage"],
            ))

        exercises_response.append(ExerciseResponse(
            id=exercise.id,
            order_index=idx,
            target_sentence=exercise.target_sentence,
            reference_translation=exercise.reference_translation,
            status="pending",
            words=exercise_words_response,
        ))

    # Update profile
    profile.last_lesson_number = next_lesson_number

    # Log event
    db.add(Event(
        user_id=user.id,
        event_type="lesson_started",
        payload={"lesson_id": lesson.id, "lesson_number": next_lesson_number},
    ))

    await db.flush()

    return LessonStartResponse(
        lesson_id=lesson.id,
        lesson_number=next_lesson_number,
        exercises=exercises_response,
    )


@router.post("/evaluate", response_model=EvaluateResponse)
async def evaluate_exercise(
    body: EvaluateRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    idempotency_key: Optional[str] = Header(None),
):
    """
    Evaluate user translation for an exercise:
    1. Check exercise is pending and in in_progress lesson
    2. Idempotency: if already evaluated, return cached result
    3. Call LLM for evaluation
    4. Update SRS stages
    5. If last exercise → auto-complete lesson
    """
    # Get exercise with lesson
    result = await db.execute(
        select(LessonExercise, Lesson, LearningProfile)
        .join(Lesson, LessonExercise.lesson_id == Lesson.id)
        .join(LearningProfile, Lesson.learning_profile_id == LearningProfile.id)
        .where(
            LessonExercise.id == body.exercise_id,
            LearningProfile.user_id == user.id,
        )
    )
    row = result.one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail="Exercise not found")

    exercise, lesson, profile = row

    if lesson.status != "in_progress":
        raise HTTPException(status_code=400, detail="Lesson not in progress")

    # Idempotency: if already evaluated, return cached
    if exercise.status == "evaluated":
        result = await db.execute(
            select(LessonExerciseWord).where(LessonExerciseWord.exercise_id == exercise.id)
        )
        exercise_words = result.scalars().all()

        # Check if this is the last exercise
        result = await db.execute(
            select(func.count(LessonExercise.id)).where(
                LessonExercise.lesson_id == lesson.id,
            )
        )
        total_exercises = result.scalar()
        is_last = exercise.order_index == total_exercises - 1

        return EvaluateResponse(
            exercise_id=exercise.id,
            result=exercise_words[0].result if exercise_words else "incorrect",
            words=[
                ExerciseWordResponse(
                    word_id=ew.word_id,
                    is_target=ew.is_target,
                    is_new=ew.is_new,
                    surface_form=ew.surface_form,
                    result=ew.result,
                    stage_before=ew.stage_before,
                    stage_after=ew.stage_after,
                )
                for ew in exercise_words if ew.is_target
            ],
            reference_translation=exercise.reference_translation,
            is_last=is_last,
        )

    # Get target words
    result = await db.execute(
        select(LessonExerciseWord, Word)
        .join(Word, LessonExerciseWord.word_id == Word.id)
        .where(
            LessonExerciseWord.exercise_id == exercise.id,
            LessonExerciseWord.is_target == True,
        )
    )
    target_word_rows = result.all()

    if not target_word_rows:
        raise HTTPException(status_code=400, detail="No target words")

    target_words_data = [
        {"lemma": word.lemma, "translations": word.translations}
        for _, word in target_word_rows
    ]

    # Check if user said "don't know" (empty or special marker)
    is_dont_know = not body.user_translation.strip() or body.user_translation.strip().lower() in ("не знаю", "dont_know", "skip")

    if is_dont_know:
        # Don't call LLM — mark all as incorrect
        overall_result = "incorrect"
        evaluations = [
            {"word_lemma": word.lemma, "result": "incorrect", "user_fragment": ""}
            for _, word in target_word_rows
        ]
    else:
        # Call LLM
        try:
            llm_result = await gigachat_client.evaluate_translation(
                target_sentence=exercise.target_sentence,
                reference_translation=exercise.reference_translation,
                user_translation=body.user_translation,
                target_words=target_words_data,
                db=db,
                user_id=user.id,
                lesson_id=lesson.id,
            )
            overall_result = llm_result["overall_result"]
            evaluations = llm_result["evaluations"]
            logger.info(f"✅ Translation evaluated using GigaChat LLM")
        except Exception as e:
            logger.error(f"LLM evaluation failed: {e}")
            raise HTTPException(status_code=503, detail="Сервис временно недоступен. Попробуйте позже.")

    # Update exercise
    exercise.user_translation = body.user_translation
    exercise.status = "evaluated"

    # Update word stages
    exercise_words_response = []
    for ew, word in target_word_rows:
        # Find evaluation for this word
        eval_data = next(
            (e for e in evaluations if e["word_lemma"] == word.lemma),
            {"result": "incorrect", "user_fragment": ""}
        )

        result_str = eval_data["result"]
        new_stage = calculate_new_stage(ew.stage_before, result_str)
        new_due = calculate_due_lesson_number(lesson.lesson_number, new_stage)

        ew.result = result_str
        ew.user_fragment = eval_data.get("user_fragment", "")
        ew.stage_after = new_stage

        # Update or create user_word
        result = await db.execute(
            select(UserWord).where(
                UserWord.learning_profile_id == profile.id,
                UserWord.word_id == ew.word_id,
            ).with_for_update()
        )
        user_word = result.scalar_one_or_none()

        if user_word:
            user_word.stage = new_stage
            user_word.due_lesson_number = new_due
            user_word.status = "mastered" if is_mastered(new_stage) else "active"
        else:
            user_word = UserWord(
                learning_profile_id=profile.id,
                word_id=ew.word_id,
                stage=new_stage,
                due_lesson_number=new_due,
                status="mastered" if is_mastered(new_stage) else "active",
            )
            db.add(user_word)

        exercise_words_response.append(ExerciseWordResponse(
            word_id=ew.word_id,
            is_target=ew.is_target,
            is_new=ew.is_new,
            surface_form=ew.surface_form,
            result=result_str,
            stage_before=ew.stage_before,
            stage_after=new_stage,
        ))

    # Check if this is the last exercise
    result = await db.execute(
        select(func.count(LessonExercise.id)).where(
            LessonExercise.lesson_id == lesson.id,
        )
    )
    total_exercises = result.scalar()
    is_last = exercise.order_index == total_exercises - 1

    # If last exercise → auto-complete lesson
    if is_last:
        lesson.status = "completed"
        lesson.completed_local_date = get_local_date(user.timezone)

        db.add(Event(
            user_id=user.id,
            event_type="lesson_completed",
            payload={"lesson_id": lesson.id, "lesson_number": lesson.lesson_number},
        ))

    # Log event
    db.add(Event(
        user_id=user.id,
        event_type="exercise_evaluated",
        payload={
            "exercise_id": exercise.id,
            "result": overall_result,
            "is_last": is_last,
        },
    ))

    await db.flush()

    return EvaluateResponse(
        exercise_id=exercise.id,
        result=overall_result,
        words=exercise_words_response,
        reference_translation=exercise.reference_translation,
        is_last=is_last,
    )


@router.get("/{lesson_id}/summary", response_model=LessonSummaryResponse)
async def get_lesson_summary(
    lesson_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get summary statistics for a completed lesson."""
    result = await db.execute(
        select(Lesson, LearningProfile)
        .join(LearningProfile, Lesson.learning_profile_id == LearningProfile.id)
        .where(
            Lesson.id == lesson_id,
            LearningProfile.user_id == user.id,
        )
    )
    row = result.one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail="Lesson not found")

    lesson, profile = row

    # Get all exercise words
    result = await db.execute(
        select(LessonExerciseWord, LessonExercise)
        .join(LessonExercise, LessonExerciseWord.exercise_id == LessonExercise.id)
        .where(
            LessonExercise.lesson_id == lesson.id,
            LessonExerciseWord.is_target == True,
        )
    )
    all_words = result.all()

    correct_count = sum(1 for ew, _ in all_words if ew.result == "correct")
    typo_count = sum(1 for ew, _ in all_words if ew.result == "typo")
    incorrect_count = sum(1 for ew, _ in all_words if ew.result in ("incorrect", "dont_know"))
    total = len(all_words)

    accuracy = round(((correct_count + typo_count) / total) * 100) if total > 0 else 0
    new_words_learned = sum(1 for ew, _ in all_words if ew.is_new and ew.stage_after > 0)
    words_reviewed = sum(1 for ew, _ in all_words if not ew.is_new)

    # Calculate streak (simplified)
    streak = 0  # TODO: implement

    words_summary = []
    for ew, ex in all_words:
        words_summary.append({
            "word_id": ew.word_id,
            "surface_form": ew.surface_form,
            "result": ew.result,
            "stage_before": ew.stage_before,
            "stage_after": ew.stage_after,
            "is_new": ew.is_new,
        })

    return LessonSummaryResponse(
        lesson_id=lesson.id,
        lesson_number=lesson.lesson_number,
        accuracy=accuracy,
        correct_count=correct_count,
        typo_count=typo_count,
        incorrect_count=incorrect_count,
        new_words_learned=new_words_learned,
        words_reviewed=words_reviewed,
        streak=streak,
        words=words_summary,
    )


@router.get("/current")
async def get_current_lesson(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get the current in-progress lesson for the user."""
    logger.info(f"🔍 Getting current lesson for user {user.id}")
    
    result = await db.execute(
        select(Lesson, LearningProfile)
        .join(LearningProfile, Lesson.learning_profile_id == LearningProfile.id)
        .where(
            LearningProfile.user_id == user.id,
            Lesson.status == "in_progress",
        )
    )
    row = result.one_or_none()
    
    if not row:
        logger.info(f"   ❌ No in-progress lesson found for user {user.id}")
        return {"lesson": None}
    
    lesson, _ = row
    logger.info(f"   ✅ Found lesson #{lesson.lesson_number} (id={lesson.id}, status={lesson.status})")
    
    # Load exercises
    result = await db.execute(
        select(LessonExercise)
        .where(LessonExercise.lesson_id == lesson.id)
        .order_by(LessonExercise.order_index)
    )
    exercises = result.scalars().all()
    
    exercises_data = []
    for ex in exercises:
        # Load exercise words
        result = await db.execute(
            select(LessonExerciseWord)
            .where(LessonExerciseWord.exercise_id == ex.id)
        )
        words = result.scalars().all()
        
        exercises_data.append({
            "id": ex.id,
            "order_index": ex.order_index,
            "target_sentence": ex.target_sentence,
            "reference_translation": ex.reference_translation,
            "user_translation": ex.user_translation,
            "status": ex.status,
            "words": [
                {
                    "word_id": w.word_id,
                    "is_target": w.is_target,
                    "is_new": w.is_new,
                    "surface_form": w.surface_form,
                    "result": w.result,
                    "user_fragment": w.user_fragment,
                    "stage_before": w.stage_before,
                    "stage_after": w.stage_after,
                }
                for w in words
            ]
        })
    
    logger.info(f"   Loaded {len(exercises_data)} exercises")
    
    return {
        "lesson": {
            "id": lesson.id,
            "lesson_number": lesson.lesson_number,
            "status": lesson.status,
            "started_local_date": lesson.started_local_date,
            "completed_local_date": lesson.completed_local_date,
            "exercises": exercises_data,
        }
    }


@router.post("/{lesson_id}/abandon")
async def abandon_lesson(
    lesson_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Abandon an in-progress lesson. Daily limit is NOT returned."""
    result = await db.execute(
        select(Lesson, LearningProfile)
        .join(LearningProfile, Lesson.learning_profile_id == LearningProfile.id)
        .where(
            Lesson.id == lesson_id,
            LearningProfile.user_id == user.id,
            Lesson.status == "in_progress",
        )
    )
    row = result.one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail="Lesson not found or not in progress")

    lesson, _ = row
    lesson.status = "abandoned"
    await db.flush()

    return {"status": "ok"}
