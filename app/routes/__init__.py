from .lessons import router as lessons_router
from .submissions import router as submissions_router
from .users import router as users_router
from .health import router as health_router

__all__ = [
    "lessons_router",
    "submissions_router",
    "users_router", 
    "health_router"
]

