import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import get_db, Base
from app.models import User, Lesson, Problem


# Test database setup
@pytest.fixture
def test_db():
    """Create a test database session"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    # Create test data
    user = User(id=1, username="test_user", total_xp=0, current_streak=0)
    lesson = Lesson(id=1, title="Test Lesson", description="Test Description", order_index=1)
    problem1 = Problem(id=1, lesson_id=1, question="What is 2+2?", problem_type="numeric", 
                      correct_answer="4", xp_value=10, order_index=1)
    problem2 = Problem(id=2, lesson_id=1, question="What is 3+3?", problem_type="numeric",
                      correct_answer="6", xp_value=10, order_index=2)
    
    db.add_all([user, lesson, problem1, problem2])
    db.commit()
    
    yield db
    db.close()


@pytest.fixture
def client(test_db):
    """Create a test client with test database"""
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


class TestLessonsAPI:
    """Test lessons API endpoints"""
    
    def test_get_lessons_returns_list(self, client):
        """GET /api/lessons should return list of lessons with progress"""
        response = client.get("/api/lessons")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == 1
        assert data[0]["title"] == "Test Lesson"
        assert "progress_status" in data[0]
        assert data[0]["progress_status"]["is_completed"] == False
        assert data[0]["progress_status"]["completion_percentage"] == 0
    
    def test_get_lesson_detail_returns_problems(self, client):
        """GET /api/lessons/{id} should return lesson with problems (no answers)"""
        response = client.get("/api/lessons/1")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["title"] == "Test Lesson"
        assert len(data["problems"]) == 2
        
        # Check that answers are not revealed
        problem = data["problems"][0]
        assert "correct_answer" not in problem
        assert problem["question"] == "What is 2+2?"
        assert problem["xp_value"] == 10
    
    def test_get_nonexistent_lesson_returns_404(self, client):
        """GET /api/lessons/{invalid_id} should return 404"""
        response = client.get("/api/lessons/999")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestSubmissionAPI:
    """Test submission API endpoint"""
    
    def test_submit_correct_answers_awards_xp(self, client):
        """POST /api/lessons/{id}/submit with correct answers should award XP"""
        submission_data = {
            "attempt_id": "test_001",
            "answers": [
                {"problem_id": 1, "answer": "4"},
                {"problem_id": 2, "answer": "6"}
            ]
        }
        
        response = client.post("/api/lessons/1/submit", json=submission_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["total_xp_earned"] == 20
        assert data["new_total_xp"] == 20
        assert data["current_streak"] == 1
        assert data["streak_increased"] == True
        assert len(data["results"]) == 2
        assert all(result["is_correct"] for result in data["results"])
    
    def test_submit_incorrect_answers_no_xp(self, client):
        """POST /api/lessons/{id}/submit with incorrect answers should award no XP"""
        submission_data = {
            "attempt_id": "test_002",
            "answers": [
                {"problem_id": 1, "answer": "wrong"},
                {"problem_id": 2, "answer": "also_wrong"}
            ]
        }
        
        response = client.post("/api/lessons/1/submit", json=submission_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["total_xp_earned"] == 0
        assert data["new_total_xp"] == 0  # Assuming no previous XP
        assert all(not result["is_correct"] for result in data["results"])
        assert all(result["xp_earned"] == 0 for result in data["results"])
    
    def test_submit_duplicate_attempt_id_idempotent(self, client):
        """Submitting with same attempt_id should be idempotent"""
        submission_data = {
            "attempt_id": "test_003",
            "answers": [
                {"problem_id": 1, "answer": "4"}
            ]
        }
        
        # First submission
        response1 = client.post("/api/lessons/1/submit", json=submission_data)
        assert response1.status_code == 200
        data1 = response1.json()
        
        # Duplicate submission
        response2 = client.post("/api/lessons/1/submit", json=submission_data)
        assert response2.status_code == 200
        data2 = response2.json()
        
        # Should return same results
        assert data1["total_xp_earned"] == data2["total_xp_earned"]
        assert data1["new_total_xp"] == data2["new_total_xp"]
        assert "already processed" in data2["message"].lower()
        assert data2["streak_increased"] == False
    
    def test_submit_invalid_problem_id_returns_422(self, client):
        """Submitting with invalid problem ID should return 422"""
        submission_data = {
            "attempt_id": "test_004",
            "answers": [
                {"problem_id": 999, "answer": "4"}  # Invalid problem ID
            ]
        }
        
        response = client.post("/api/lessons/1/submit", json=submission_data)
        
        assert response.status_code == 422
        assert "invalid problem ids" in response.json()["detail"].lower()
    
    def test_submit_to_nonexistent_lesson_returns_404(self, client):
        """Submitting to nonexistent lesson should return 404"""
        submission_data = {
            "attempt_id": "test_005",
            "answers": [
                {"problem_id": 1, "answer": "4"}
            ]
        }
        
        response = client.post("/api/lessons/999/submit", json=submission_data)
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_submit_empty_answers_invalid(self, client):
        """Submitting with empty answers should be invalid"""
        submission_data = {
            "attempt_id": "test_006",
            "answers": []
        }
        
        response = client.post("/api/lessons/1/submit", json=submission_data)
        
        # Should return validation error
        assert response.status_code == 422


class TestProfileAPI:
    """Test profile API endpoint"""
    
    def test_get_profile_returns_user_stats(self, client):
        """GET /api/profile should return user statistics"""
        response = client.get("/api/profile")
        
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == 1
        assert data["username"] == "test_user"
        assert data["total_xp"] == 0
        assert data["current_streak"] == 0
        assert data["progress_percentage"] == 0.0
        assert data["lessons_completed"] == 0
        assert data["total_lessons"] == 1


class TestHealthAPI:
    """Test health check endpoint"""
    
    def test_health_check_returns_healthy(self, client):
        """GET /health should return healthy status"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "running" in data["message"].lower()


class TestRootAPI:
    """Test root endpoint"""
    
    def test_root_returns_api_info(self, client):
        """GET / should return API information"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "Learning Platform API" in data["message"]
        assert "version" in data

