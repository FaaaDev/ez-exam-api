from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
import os

# Database URL for async operations
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql+asyncpg://learning_user:learning_pass@localhost/ez_exam"
)

# Create async engine
engine = create_async_engine(DATABASE_URL, echo=False)
# Create non async engine (for migrations and seeding)
non_async_engine = create_engine(DATABASE_URL.replace("+asyncpg", ""), echo=False)

# Create async session maker
AsyncSessionLocal = async_sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

# Create Base class
Base = declarative_base()

# Dependency to get async DB session
async def get_async_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

