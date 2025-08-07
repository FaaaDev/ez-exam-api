from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://learning_user:learning_pass@localhost/ez_exam"
    
    # API
    api_title: str = "EZ.Exam"
    api_description: str = "A FastAPI-based learning platform with XP and streak mechanics"
    api_version: str = "1.0.0"
    
    # CORS
    allowed_origins: list = ["*"]
    
    # Demo user
    demo_user_id: int = 1
    
    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()

