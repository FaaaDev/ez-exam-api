from sqlalchemy import Column, String, Integer, ForeignKey, Text, Index, Boolean
from sqlalchemy.orm import relationship
from .base import BaseModel


class Problem(BaseModel):
    __tablename__ = "problems"
    
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False)
    question = Column(Text, nullable=False)
    problem_type = Column(String(50), default="options", nullable=False)
    xp_value = Column(Integer, default=10, nullable=False)
    order_index = Column(Integer, nullable=False)
    
    # Relationships
    lesson = relationship("Lesson", back_populates="problems")
    options = relationship("ProblemOption", back_populates="problem", cascade="all, delete-orphan")
    submissions = relationship("Submission", back_populates="problem")
    
    # Indexes
    __table_args__ = (
        Index('idx_problem_lesson_order', 'lesson_id', 'order_index'),
    )


class ProblemOption(BaseModel):
    __tablename__ = "problem_options"
    
    problem_id = Column(Integer, ForeignKey("problems.id"), nullable=False)
    option_text = Column(Text, nullable=False)
    order_index = Column(Integer, nullable=False)
    is_correct = Column(Boolean, default=False)
    
    # Relationships
    problem = relationship("Problem", back_populates="options")
    submissions = relationship("Submission", back_populates="option")
    
    # Indexes
    __table_args__ = (
        Index('idx_option_problem_order', 'problem_id', 'order_index'),
    )

