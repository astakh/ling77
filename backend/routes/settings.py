"""
Settings routes — user profile settings management.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import get_db
from models import User, LearningProfile, Dictionary
from schemas import SettingsUpdateRequest
from auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/settings", tags=["settings"])


@router.patch("")
async def update_settings(
    body: SettingsUpdateRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update user settings (level, words per lesson, lessons per day, dictionary)."""
    
    logger.info(f"📝 Updating settings for user {user.id}")
    logger.info(f"   Request body: level={body.level}, words_per_lesson={body.words_per_lesson}, lessons_per_day={body.lessons_per_day}, dictionary_id={body.dictionary_id}")
    
    # Get profile
    result = await db.execute(
        select(LearningProfile).where(LearningProfile.user_id == user.id)
    )
    profile = result.scalar_one_or_none()
    
    if not profile:
        logger.error(f"❌ Learning profile not found for user {user.id}")
        raise HTTPException(status_code=404, detail="Learning profile not found")
    
    logger.info(f"   Current profile: level={profile.level}, words_per_lesson={profile.words_per_lesson}, daily_lesson_limit={profile.daily_lesson_limit}, dictionary_id={profile.dictionary_id}")
    
    # Validate dictionary if provided
    if body.dictionary_id:
        result = await db.execute(
            select(Dictionary).where(Dictionary.id == body.dictionary_id)
        )
        dictionary = result.scalar_one_or_none()
        if not dictionary:
            logger.error(f"❌ Dictionary {body.dictionary_id} not found")
            raise HTTPException(status_code=404, detail="Dictionary not found")
        profile.dictionary_id = body.dictionary_id
        logger.info(f"   ✓ Updated dictionary_id to {body.dictionary_id}")
    
    # Update fields
    if body.level:
        profile.level = body.level
        logger.info(f"   ✓ Updated level to {body.level}")
    
    if body.words_per_lesson:
        profile.words_per_lesson = body.words_per_lesson
        logger.info(f"   ✓ Updated words_per_lesson to {body.words_per_lesson}")
    
    if body.lessons_per_day:
        profile.daily_lesson_limit = body.lessons_per_day
        logger.info(f"   ✓ Updated daily_lesson_limit to {body.lessons_per_day}")
    
    await db.commit()
    
    logger.info(f"✅ Settings saved successfully for user {user.id}")
    logger.info(f"   New profile: level={profile.level}, words_per_lesson={profile.words_per_lesson}, daily_lesson_limit={profile.daily_lesson_limit}, dictionary_id={profile.dictionary_id}")
    
    return {"status": "ok"}
