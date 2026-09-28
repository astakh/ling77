from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from database import get_db
from models import User, LearningProfile, Lesson, UserWord
from schemas import DashboardSummary
from auth import get_current_user
from srs import is_due, is_mastered

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


def get_local_date(timezone_str: str) -> str:
    """Get current date in user's timezone."""
    # Simplified — in production use pytz or zoneinfo
    from zoneinfo import ZoneInfo
    tz = ZoneInfo(timezone_str)
    return datetime.now(tz).strftime("%Y-%m-%d")


@router.get("/summary", response_model=DashboardSummary)
async def get_dashboard_summary(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Get profile
    result = await db.execute(
        select(LearningProfile).where(LearningProfile.user_id == user.id)
    )
    profile = result.scalar_one_or_none()

    if not profile:
        return DashboardSummary(
            cta="start",
            streak=0,
            total_lessons=0,
            total_words=0,
            mastered_words=0,
            due_words=0,
            lessons_today=0,
            current_lesson_id=None,
        )

    today = get_local_date(user.timezone)

    # Get lessons today
    result = await db.execute(
        select(func.count(Lesson.id)).where(
            Lesson.learning_profile_id == profile.id,
            Lesson.started_local_date == today,
            Lesson.status != "abandoned",
        )
    )
    lessons_today = result.scalar() or 0

    # Check for in_progress lesson
    result = await db.execute(
        select(Lesson).where(
            Lesson.learning_profile_id == profile.id,
            Lesson.status == "in_progress",
        )
    )
    in_progress = result.scalar_one_or_none()

    # Get user words
    result = await db.execute(
        select(UserWord).where(UserWord.learning_profile_id == profile.id)
    )
    user_words = result.scalars().all()

    total_words = len(user_words)
    mastered_words = sum(1 for uw in user_words if is_mastered(uw.stage))
    due_words = sum(1 for uw in user_words if is_due(uw.stage, uw.due_lesson_number, profile.last_lesson_number))

    # Get total completed lessons
    result = await db.execute(
        select(func.count(Lesson.id)).where(
            Lesson.learning_profile_id == profile.id,
            Lesson.status == "completed",
        )
    )
    total_lessons = result.scalar() or 0

    # Calculate streak (simplified — would need lesson completed_local_date chain)
    # For now, return 0 (would need full implementation)
    streak = 0  # TODO: implement streak calculation

    # Determine CTA
    if in_progress:
        cta = "resume"
        current_lesson_id = in_progress.id
    elif lessons_today >= profile.daily_lesson_limit:
        cta = "limit_reached"
        current_lesson_id = None
    else:
        cta = "start"
        current_lesson_id = None

    return DashboardSummary(
        cta=cta,
        streak=streak,
        total_lessons=total_lessons,
        total_words=total_words,
        mastered_words=mastered_words,
        due_words=due_words,
        lessons_today=lessons_today,
        current_lesson_id=current_lesson_id,
    )
