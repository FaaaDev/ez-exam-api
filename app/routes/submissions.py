from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging

from app.core.database import get_async_db
from app.core.config import settings
from app.models import Lesson
from app.schemas import SubmissionRequest, SubmissionResponse, SingleSubmissionRequest
from app.services import SubmissionService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/lessons", tags=["Submissions"])


@router.post("/{lesson_id}/submit", response_model=SubmissionResponse)
async def submit_lesson(
    lesson_id: int, 
    submission: SubmissionRequest, 
    db: AsyncSession = Depends(get_async_db)
):
    try:
        lesson_stmt = select(Lesson).where(Lesson.id == lesson_id)
        lesson_result = await db.execute(lesson_stmt)
        lesson = lesson_result.scalar_one_or_none()
        
        if not lesson:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Lesson with id {lesson_id} not found"
            )
        
        # Process submission
        result = await SubmissionService.process_submission(
            db, user_id=settings.demo_user_id, lesson_id=lesson_id, submission=submission
        )
        return result
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error processing submission: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process submission"
        )

@router.post("/{lesson_id}/single", response_model=SubmissionResponse)
async def single_submit_lesson(
    lesson_id: int, 
    submission: SingleSubmissionRequest, 
    db: AsyncSession = Depends(get_async_db)
):
    try:
        lesson_stmt = select(Lesson).where(Lesson.id == lesson_id)
        lesson_result = await db.execute(lesson_stmt)
        lesson = lesson_result.scalar_one_or_none()
        
        if not lesson:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Lesson with id {lesson_id} not found"
            )
        
        result = await SubmissionService.process_single_submission(
            db, user_id=settings.demo_user_id, lesson_id=lesson_id, submission=submission
        )
        return result
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error processing submission: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process submission"
        )


