from pydantic import BaseModel
from typing import List


class ProblemOptionBase(BaseModel):
    option_text: str
    order_index: int


class ProblemOptionResponse(ProblemOptionBase):
    id: int
    
    class Config:
        from_attributes = True


class ProblemBase(BaseModel):
    question: str
    problem_type: str
    xp_value: int
    order_index: int


class ProblemResponse(BaseModel):
    id: int
    question: str
    problem_type: str
    xp_value: int
    order_index: int
    options: List[ProblemOptionResponse] = []
    
    class Config:
        from_attributes = True

