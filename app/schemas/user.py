from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ProfileResponse(BaseModel):
    user_id: int
    username: str
    total_xp: int
    current_streak: int
    last_activity_date: Optional[datetime] = None
    progress_percentage: float  # Overall progress across all lessons
    lessons_completed: int
    total_lessons: int

