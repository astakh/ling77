from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from database import get_db
from models import User, LearningProfile, UserWord, Word
from schemas import VocabularyListResponse, VocabularyWord, UpdateWordStatusRequest
from auth import get_current_user

router = APIRouter(prefix="/vocabulary", tags=["vocabulary"])


@router.get("/list", response_model=VocabularyListResponse)
async def get_vocabulary_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str | None = Query(None),
    search: str | None = Query(None),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get paginated vocabulary list with filters."""
    result = await db.execute(
        select(LearningProfile).where(LearningProfile.user_id == user.id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=400, detail="No learning profile")

    # Base query
    query = (
        select(UserWord, Word)
        .join(Word, UserWord.word_id == Word.id)
        .where(UserWord.learning_profile_id == profile.id)
    )

    # Filters
    if status:
        query = query.where(UserWord.status == status)
    if search:
        search_lower = f"%{search.lower()}%"
        query = query.where(
            Word.lemma.ilike(search_lower) |
            Word.translations.cast(str).ilike(search_lower)
        )

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Paginate
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    rows = result.all()

    words = []
    for uw, word in rows:
        words.append(VocabularyWord(
            id=uw.id,
            word_id=word.id,
            lemma=word.lemma,
            pos=word.pos,
            translations=word.translations,
            status=uw.status,
            stage=uw.stage,
            due_lesson_number=uw.due_lesson_number,
        ))

    return VocabularyListResponse(
        words=words,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.patch("/word/{user_word_id}/status")
async def update_word_status(
    user_word_id: int,
    body: UpdateWordStatusRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update word status (active/ignored/mastered)."""
    result = await db.execute(
        select(UserWord, LearningProfile)
        .join(LearningProfile, UserWord.learning_profile_id == LearningProfile.id)
        .where(
            UserWord.id == user_word_id,
            LearningProfile.user_id == user.id,
        )
    )
    row = result.one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail="Word not found")

    uw, _ = row
    uw.status = body.status

    if body.status == "mastered":
        uw.due_lesson_number = None

    await db.flush()

    return {"status": "ok"}
