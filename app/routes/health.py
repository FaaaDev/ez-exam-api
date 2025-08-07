from fastapi import APIRouter
from app.core.config import settings

router = APIRouter(tags=["Health"])


@router.get("/")
async def root():
    return {
        "message": settings.api_title, 
        "version": settings.api_version
    }


@router.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "message": f"{settings.api_title} is running",
        "version": settings.api_version
    }

