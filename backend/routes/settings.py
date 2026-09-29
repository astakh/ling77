"""
Settings routes — user profile settings management.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import get_db
from models import User, LearningProfile, Dictionary
from schemas import SettingsUpdateRequest
from auth import get_current_user

router = APIRouter(prefix="/settings", tags=["settings"])


@router.patch("")
async def update_settings(
    body: SettingsUpdateRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update user settings (level, words per lesson, lessons per day, dictionary)."""
    
    # Get profile
    result = await db.execute(
        select(LearningProfile).where(LearningProfile.user_id == user.id)
    )
    profile = result.scalar_one_or_none()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Learning profile not found")
    
    # Validate dictionary if provided
    if body.dictionary_id:
        result = await db.execute(
            select(Dictionary).where(Dictionary.id == body.dictionary_id)
        )
        dictionary = result.scalar_one_or_none()
        if not dictionary:
            raise HTTPException(status_code=404, detail="Dictionary not found")
        profile.dictionary_id = body.dictionary_id
    
    # Update fields
    if body.level:
        profile.level = body.level
    
    if body.words_per_lesson:
        profile.words_per_lesson = body.words_per_lesson
    
    if body.lessons_per_day:
        profile.daily_lesson_limit = body.lessons_per_day
    
    await db.flush()
    
    return {"status": "ok"}
