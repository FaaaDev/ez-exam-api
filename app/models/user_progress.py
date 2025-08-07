from sqlalchemy import Column, Integer, ForeignKey, Boolean, DateTime, Index
from sqlalchemy.orm import relationship
from .base import BaseModel


class UserProgress(BaseModel):
    __tablename__ = "user_progress"
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False)
    is_completed = Column(Boolean, default=False, nullable=False)
    completion_percentage = Column(Integer, default=0, nullable=False)  # 0-100
    last_accessed_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="progress")
    lesson = relationship("Lesson", back_populates="progress")
    
    # Indexes
    __table_args__ = (
        Index('idx_progress_user_lesson', 'user_id', 'lesson_id'),
    )

