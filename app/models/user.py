from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.orm import relationship
from .base import BaseModel


class User(BaseModel):
    __tablename__ = "users"
    
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=True)
    total_xp = Column(Integer, default=0, nullable=False)
    current_streak = Column(Integer, default=0, nullable=False)
    last_activity_date = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    submissions = relationship("Submission", back_populates="user")
    progress = relationship("UserProgress", back_populates="user")

