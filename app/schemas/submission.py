from pydantic import BaseModel, Field
from typing import List


class SubmissionRequest(BaseModel):
    attempt_id: str = Field(..., min_length=1, max_length=100)
    answers: List[dict] = Field(..., description="List of {problem_id: int, option_id: int}")
    
    class Config:
        json_schema_extra = {
            "example": {
                "attempt_id": "attempt_123456",
                "answers": [
                    {"problem_id": 1, "option_id": 3},
                    {"problem_id": 2, "option_id": 4}
                ]
            }
        }


class SingleSubmissionRequest(BaseModel):
    attempt_id: str = Field(..., min_length=1, max_length=100)
    answer: dict = Field(..., description="Object of {problem_id: int, answer: str}")
    
    class Config:
        json_schema_extra = {
            "example": {
                "attempt_id": "attempt_123456",
                "answer": {"problem_id": 1, "answer": "8"}
            }
        }


class SubmissionResponse(BaseModel):
    success: bool
    message: str
    results: List[dict]  # List of {problem_id, is_correct, xp_earned}
    total_xp_earned: int
    new_total_xp: int
    current_streak: int
    streak_increased: bool

