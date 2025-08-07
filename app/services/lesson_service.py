from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Optional
import logging

from app.models import Lesson, Problem, ProblemOption, UserProgress
from app.schemas import LessonWithProgressResponse, LessonDetailResponse, ProblemResponse, ProblemOptionResponse

logger = logging.getLogger(__name__)


class LessonService:
    @staticmethod
    async def get_lessons_with_progress(db: AsyncSession, user_id: int) -> List[LessonWithProgressResponse]:
        # Get all active lessons
        stmt = select(Lesson).where(Lesson.is_active == True).order_by(Lesson.order_index)
        result = await db.execute(stmt)
        lessons = result.scalars().all()
        
        # Get user progress for all lessons
        progress_stmt = select(UserProgress).where(UserProgress.user_id == user_id)
        progress_result = await db.execute(progress_stmt)
        progress_records = {p.lesson_id: p for p in progress_result.scalars().all()}
        
        # Build response
        lesson_responses = []
        for lesson in lessons:
            progress = progress_records.get(lesson.id)
            lesson_data = LessonWithProgressResponse(
                id=lesson.id,
                title=lesson.title,
                description=lesson.description,
                order_index=lesson.order_index,
                is_active=lesson.is_active,
                created_at=lesson.created_at,
                updated_at=lesson.updated_at,
                progress_status={
                    "is_completed": progress.is_completed if progress else False,
                    "completion_percentage": progress.completion_percentage if progress else 0
                }
            )
            lesson_responses.append(lesson_data)
        
        return lesson_responses
    
    @staticmethod
    async def get_lesson_detail(db: AsyncSession, lesson_id: int) -> Optional[LessonDetailResponse]:
        stmt = (
            select(Lesson)
            .options(
                selectinload(Lesson.problems).selectinload(Problem.options)
            )
            .where(Lesson.id == lesson_id)
        )
        result = await db.execute(stmt)
        lesson = result.scalar_one_or_none()
        
        if not lesson:
            return None
        
        # Build problem responses
        problem_responses = []
        for problem in sorted(lesson.problems, key=lambda p: p.order_index):
            option_responses = [
                ProblemOptionResponse(
                    id=option.id,
                    option_text=option.option_text,
                    order_index=option.order_index
                ) for option in sorted(problem.options, key=lambda o: o.order_index)
            ]
            
            problem_response = ProblemResponse(
                id=problem.id,
                question=problem.question,
                problem_type=problem.problem_type,
                xp_value=problem.xp_value,
                order_index=problem.order_index,
                options=option_responses
            )
            problem_responses.append(problem_response)
        
        return LessonDetailResponse(
            id=lesson.id,
            title=lesson.title,
            description=lesson.description,
            order_index=lesson.order_index,
            is_active=lesson.is_active,
            created_at=lesson.created_at,
            updated_at=lesson.updated_at,
            problems=problem_responses
        )

