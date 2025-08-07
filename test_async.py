#!/usr/bin/env python3
"""
Test script to verify async functionality
"""
import asyncio
import sys
import os

# Add the app directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_async_imports():
    """Test that all async components can be imported"""
    try:
        print("Testing async imports...")
        
        # Test core imports
        from app.core.database import get_async_db, AsyncSessionLocal
        from app.core.config import settings
        print("✅ Core imports successful")
        
        # Test model imports
        from app.models import User, Lesson, Problem
        print("✅ Model imports successful")
        
        # Test schema imports
        from app.schemas import LessonResponse, SubmissionRequest
        print("✅ Schema imports successful")
        
        # Test service imports
        from app.services import LessonService, UserService, SubmissionService
        print("✅ Service imports successful")
        
        # Test route imports
        from app.routes import lessons_router, users_router
        print("✅ Route imports successful")
        
        # Test database connection
        async with AsyncSessionLocal() as session:
            print("✅ Async database session created successfully")
        
        print("\n🎉 All async components imported successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_async_imports())
    sys.exit(0 if success else 1)

