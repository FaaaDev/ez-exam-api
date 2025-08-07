from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from .problem import ProblemResponse


class LessonBase(BaseModel):
    title: str
    description: Optional[str] = None
    order_index: int
    is_active: bool = True


class LessonResponse(LessonBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class LessonWithProgressResponse(LessonResponse):
    progress_status: Optional[dict] = None  # {is_completed, completion_percentage}


class LessonDetailResponse(LessonResponse):
    problems: List[ProblemResponse] = []

