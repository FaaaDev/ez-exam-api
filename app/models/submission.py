from sqlalchemy import Column, String, Integer, ForeignKey, Boolean, DateTime, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Submission(Base):
    __tablename__ = "submissions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    problem_id = Column(Integer, ForeignKey("problems.id"), nullable=False)
    attempt_id = Column(String(100), nullable=False)  # For idempotence
    option_id = Column(Integer, ForeignKey("problem_options.id"), nullable=False)
    is_correct = Column(Boolean, nullable=False)
    xp_earned = Column(Integer, default=0, nullable=False)
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="submissions")
    problem = relationship("Problem", back_populates="submissions")
    option = relationship("ProblemOption", back_populates="submissions")
    
    # Indexes
    __table_args__ = (
        Index('idx_submission_user_attempt', 'user_id', 'attempt_id'),
        Index('idx_submission_user_problem', 'user_id', 'problem_id'),
        Index('idx_submission_attempt_problem', 'attempt_id', 'problem_id'),
        Index('idx_submission_problem_problem_problem_option', 'problem_id', 'option_id'),
    )

