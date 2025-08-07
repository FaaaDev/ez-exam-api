from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import logging

from app.core.database import get_async_db
from app.core.config import settings
from app.schemas import LessonWithProgressResponse, LessonDetailResponse
from app.services import LessonService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/lessons", tags=["Lessons"])


@router.get("/", response_model=List[LessonWithProgressResponse])
async def get_lessons(db: AsyncSession = Depends(get_async_db)):
    """Get list of lessons with progress status for demo user"""
    try:
        lessons = await LessonService.get_lessons_with_progress(db, user_id=settings.demo_user_id)
        return lessons
    except Exception as e:
        logger.error(f"Error getting lessons: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve lessons"
        )


@router.get("/{lesson_id}", response_model=LessonDetailResponse)
async def get_lesson_detail(lesson_id: int, db: AsyncSession = Depends(get_async_db)):
    """Get lesson details with list of questions (without revealing answers)"""
    try:
        lesson = await LessonService.get_lesson_detail(db, lesson_id)
        if not lesson:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Lesson with id {lesson_id} not found"
            )
        return lesson
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting lesson detail: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve lesson details"
        )

