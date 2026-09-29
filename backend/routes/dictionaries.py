"""
Dictionaries routes — management of word dictionaries.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from database import get_db
from models import User, Dictionary, Word, LearningProfile, DictionaryWord
from schemas import (
    DictionaryResponse, DictionaryDetailResponse,
    DictionaryCreateRequest, DictionaryListResponse,
    ChangeDictionaryRequest
)
from auth import get_current_user, get_current_admin

router = APIRouter(prefix="/dictionaries", tags=["dictionaries"])


@router.get("/profile")
async def get_profile(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get the current user's learning profile."""
    result = await db.execute(
        select(LearningProfile).where(LearningProfile.user_id == user.id)
    )
    profile = result.scalar_one_or_none()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Learning profile not found")
    
    return {
        "user_id": profile.user_id,
        "level": profile.level,
        "dictionary_id": profile.dictionary_id,
        "daily_lesson_limit": profile.daily_lesson_limit,
        "words_per_lesson": profile.words_per_lesson,
        "last_lesson_number": profile.last_lesson_number,
    }


@router.get("", response_model=DictionaryListResponse)
async def list_dictionaries(
    category: str | None = Query(None, description="Filter by category (general, it, travel, business, food, medical, daily)"),
    search: str | None = Query(None, description="Search by name"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get list of all available dictionaries with word counts.
    
    Dictionaries are THEMATIC (IT, travel, business, etc.) — NOT level-based.
    Word level (A1-B2) is a property of the word itself.
    """
    query = select(Dictionary).where(Dictionary.is_active == True)

    if search:
        query = query.where(Dictionary.name.ilike(f"%{search}%"))
    
    if category:
        query = query.where(Dictionary.category == category)

    result = await db.execute(query)
    dictionaries = result.scalars().all()

    # Get word counts for each dictionary
    dict_responses = []
    for d in dictionaries:
        # Count words by level via DictionaryWord association
        count_result = await db.execute(
            select(
                Word.level,
                func.count(Word.id)
            )
            .join(DictionaryWord, DictionaryWord.word_id == Word.id)
            .where(DictionaryWord.dictionary_id == d.id)
            .group_by(Word.level)
        )
        level_counts = {row[0]: row[1] for row in count_result.all()}
        total_words = sum(level_counts.values())

        dict_responses.append(DictionaryResponse(
            id=d.id,
            name=d.name,
            description=d.description,
            category=d.category,
            total_words=total_words,
            levels=list(level_counts.keys()),
            level_counts=level_counts,
            created_at=d.created_at,
        ))

    return DictionaryListResponse(dictionaries=dict_responses)


@router.get("/{dictionary_id}", response_model=DictionaryDetailResponse)
async def get_dictionary(
    dictionary_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get detailed information about a dictionary."""
    result = await db.execute(
        select(Dictionary).where(Dictionary.id == dictionary_id)
    )
    dictionary = result.scalar_one_or_none()

    if not dictionary:
        raise HTTPException(status_code=404, detail="Dictionary not found")

    # Get word counts by level via DictionaryWord
    count_result = await db.execute(
        select(
            Word.level,
            func.count(Word.id)
        )
        .join(DictionaryWord, DictionaryWord.word_id == Word.id)
        .where(DictionaryWord.dictionary_id == dictionary.id)
        .group_by(Word.level)
    )
    level_counts = {row[0]: row[1] for row in count_result.all()}
    total_words = sum(level_counts.values())

    # Get sample words (first 10) via DictionaryWord
    sample_result = await db.execute(
        select(Word)
        .join(DictionaryWord, DictionaryWord.word_id == Word.id)
        .where(DictionaryWord.dictionary_id == dictionary.id)
        .limit(10)
    )
    sample_words = [
        {
            "id": w.id,
            "lemma": w.lemma,
            "pos": w.pos,
            "level": w.level,
            "translations": w.translations,
        }
        for w in sample_result.scalars().all()
    ]

    return DictionaryDetailResponse(
        id=dictionary.id,
        name=dictionary.name,
        description=dictionary.description,
        total_words=total_words,
        levels=list(level_counts.keys()),
        level_counts=level_counts,
        sample_words=sample_words,
        created_at=dictionary.created_at,
    )


@router.post("", response_model=DictionaryResponse)
async def create_dictionary(
    body: DictionaryCreateRequest,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Create a new dictionary (admin only)."""
    # Check if name already exists
    result = await db.execute(
        select(Dictionary).where(Dictionary.name == body.name)
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Dictionary with this name already exists")

    dictionary = Dictionary(
        name=body.name,
        description=body.description,
    )
    db.add(dictionary)
    await db.flush()

    return DictionaryResponse(
        id=dictionary.id,
        name=dictionary.name,
        description=dictionary.description,
        total_words=0,
        levels=[],
        level_counts={},
        created_at=dictionary.created_at,
    )


@router.patch("/profile/dictionary")
async def change_profile_dictionary(
    body: ChangeDictionaryRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Change the active dictionary for the current user's profile."""
    # Get profile
    result = await db.execute(
        select(LearningProfile).where(LearningProfile.user_id == user.id)
    )
    profile = result.scalar_one_or_none()

    if not profile:
        raise HTTPException(status_code=400, detail="No learning profile found")

    # Check dictionary exists
    result = await db.execute(
        select(Dictionary).where(Dictionary.id == body.dictionary_id)
    )
    dictionary = result.scalar_one_or_none()

    if not dictionary:
        raise HTTPException(status_code=404, detail="Dictionary not found")

    # Update profile
    profile.dictionary_id = dictionary.id
    await db.flush()

    return {
        "status": "ok",
        "dictionary_id": dictionary.id,
        "dictionary_name": dictionary.name,
    }


@router.get("/profile/current")
async def get_current_dictionary(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get the current active dictionary for the user's profile."""
    result = await db.execute(
        select(LearningProfile, Dictionary)
        .outerjoin(Dictionary, LearningProfile.dictionary_id == Dictionary.id)
        .where(LearningProfile.user_id == user.id)
    )
    row = result.one_or_none()

    if not row:
        raise HTTPException(status_code=400, detail="No learning profile found")

    profile, dictionary = row

    if not dictionary:
        return {"dictionary": None, "message": "No dictionary assigned"}

    # Get word count via DictionaryWord
    count_result = await db.execute(
        select(func.count(Word.id))
        .join(DictionaryWord, DictionaryWord.word_id == Word.id)
        .where(DictionaryWord.dictionary_id == dictionary.id)
    )
    total_words = count_result.scalar() or 0

    return {
        "dictionary": {
            "id": dictionary.id,
            "name": dictionary.name,
            "description": dictionary.description,
            "total_words": total_words,
        }
    }
