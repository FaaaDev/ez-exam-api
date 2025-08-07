from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.core.database import get_async_db
from app.core.config import settings
from app.schemas import ProfileResponse
from app.services import UserService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/profiles", tags=["Profile"])


@router.get("/", response_model=ProfileResponse)
async def get_profile(db: AsyncSession = Depends(get_async_db)):
    try:
        profile = await UserService.get_user_profile(db, user_id=settings.demo_user_id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
        return profile
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user profile"
        )

