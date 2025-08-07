from sqlalchemy import Column, String, Integer, Boolean, Text
from sqlalchemy.orm import relationship
from .base import BaseModel


class Lesson(BaseModel):
    __tablename__ = "lessons"
    
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    order_index = Column(Integer, nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    problems = relationship("Problem", back_populates="lesson", cascade="all, delete-orphan")
    progress = relationship("UserProgress", back_populates="lesson")

