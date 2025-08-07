from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class UserProgressBase(BaseModel):
    is_completed: bool = False
    completion_percentage: int = Field(ge=0, le=100, default=0)


class UserProgressResponse(UserProgressBase):
    id: int
    lesson_id: int
    last_accessed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

