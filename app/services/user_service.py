from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
import logging

from app.models import User, Lesson, UserProgress
from app.schemas import ProfileResponse

logger = logging.getLogger(__name__)


class UserService:
    @staticmethod
    async def get_user_profile(db: AsyncSession, user_id: int) -> Optional[ProfileResponse]:
        """Get user profile with statistics"""
        # Get user
        user_stmt = select(User).where(User.id == user_id)
        user_result = await db.execute(user_stmt)
        user = user_result.scalar_one_or_none()
        
        if not user:
            return None
        
        # Get total lessons count
        total_lessons_stmt = select(func.count(Lesson.id)).where(Lesson.is_active == True)
        total_lessons_result = await db.execute(total_lessons_stmt)
        total_lessons = total_lessons_result.scalar()
        
        # Get completed lessons count
        completed_lessons_stmt = select(func.count(UserProgress.id)).where(
            UserProgress.user_id == user_id,
            UserProgress.is_completed == True
        )
        completed_lessons_result = await db.execute(completed_lessons_stmt)
        completed_lessons = completed_lessons_result.scalar()
        
        # Calculate progress percentage
        progress_percentage = (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0
        
        return ProfileResponse(
            user_id=user.id,
            username=user.username,
            total_xp=user.total_xp,
            current_streak=user.current_streak,
            last_activity_date=user.last_activity_date,
            progress_percentage=round(progress_percentage, 2),
            lessons_completed=completed_lessons,
            total_lessons=total_lessons
        )

