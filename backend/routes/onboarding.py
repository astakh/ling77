from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models import User, LearningProfile, Dictionary
from schemas import OnboardingRequest
from auth import get_current_user

router = APIRouter(prefix="/onboarding", tags=["onboarding"])


@router.post("/complete")
async def complete_onboarding(
    body: OnboardingRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if user.is_onboarded:
        # Return success instead of error - makes API more resilient
        return {"status": "already_onboarded"}

    # Get or create default dictionary for level
    from sqlalchemy import select
    result = await db.execute(
        select(Dictionary).where(Dictionary.name == f"Default {body.level}")
    )
    dictionary = result.scalar_one_or_none()

    if not dictionary:
        dictionary = Dictionary(name=f"Default {body.level}", description=f"Default dictionary for level {body.level}")
        db.add(dictionary)
        await db.flush()

    # Create learning profile
    profile = LearningProfile(
        user_id=user.id,
        level=body.level,
        dictionary_id=dictionary.id,
        daily_lesson_limit=5,
        last_lesson_number=0,
    )
    db.add(profile)

    # Update user
    user.is_onboarded = True
    user.timezone = body.timezone

    await db.flush()

    return {"status": "ok", "level": body.level}
