import pytest
from datetime import datetime, timezone, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models import User, Lesson, Problem, Submission, UserProgress
from app.services import _update_user_streak, process_submission
from app.schemas import SubmissionRequest


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
    lesson = Lesson(id=1, title="Test Lesson", order_index=1)
    problem = Problem(id=1, lesson_id=1, question="Test?", problem_type="numeric", 
                     correct_answer="42", xp_value=10, order_index=1)
    
    db.add_all([user, lesson, problem])
    db.commit()
    
    yield db
    db.close()


class TestStreakLogic:
    """Test streak calculation logic"""
    
    def test_first_activity_sets_streak_to_1(self, test_db):
        """First submission on a new user should set streak to 1"""
        user = test_db.query(User).first()
        current_time = datetime.now(timezone.utc)
        
        streak_increased = _update_user_streak(user, current_time)
        
        assert user.current_streak == 1
        assert streak_increased == True
    
    def test_same_day_activity_no_streak_change(self, test_db):
        """Multiple submissions on same day should not change streak"""
        user = test_db.query(User).first()
        current_time = datetime.now(timezone.utc)
        
        # First activity
        user.current_streak = 1
        user.last_activity_date = current_time
        
        # Same day activity
        streak_increased = _update_user_streak(user, current_time)
        
        assert user.current_streak == 1
        assert streak_increased == False
    
    def test_consecutive_day_increases_streak(self, test_db):
        """Activity on consecutive days should increase streak"""
        user = test_db.query(User).first()
        yesterday = datetime.now(timezone.utc) - timedelta(days=1)
        today = datetime.now(timezone.utc)
        
        # Set up previous day activity
        user.current_streak = 1
        user.last_activity_date = yesterday
        
        # Next day activity
        streak_increased = _update_user_streak(user, today)
        
        assert user.current_streak == 2
        assert streak_increased == True
    
    def test_gap_in_activity_resets_streak(self, test_db):
        """Gap in activity should reset streak to 1"""
        user = test_db.query(User).first()
        three_days_ago = datetime.now(timezone.utc) - timedelta(days=3)
        today = datetime.now(timezone.utc)
        
        # Set up previous activity with gap
        user.current_streak = 5
        user.last_activity_date = three_days_ago
        
        # Activity after gap
        streak_increased = _update_user_streak(user, today)
        
        assert user.current_streak == 1
        assert streak_increased == True


class TestIdempotentScoring:
    """Test idempotent submission logic"""
    
    def test_first_submission_processes_normally(self, test_db):
        """First submission should process normally and award XP"""
        submission_data = SubmissionRequest(
            attempt_id="test_001",
            answers=[{"problem_id": 1, "answer": "42"}]
        )
        
        result = process_submission(test_db, user_id=1, lesson_id=1, submission=submission_data)
        
        assert result.success == True
        assert result.total_xp_earned == 10
        assert result.new_total_xp == 10
        assert len(result.results) == 1
        assert result.results[0]["is_correct"] == True
    
    def test_duplicate_attempt_id_returns_same_result(self, test_db):
        """Duplicate attempt_id should return same result without awarding more XP"""
        submission_data = SubmissionRequest(
            attempt_id="test_002",
            answers=[{"problem_id": 1, "answer": "42"}]
        )
        
        # First submission
        result1 = process_submission(test_db, user_id=1, lesson_id=1, submission=submission_data)
        
        # Duplicate submission
        result2 = process_submission(test_db, user_id=1, lesson_id=1, submission=submission_data)
        
        assert result1.total_xp_earned == result2.total_xp_earned
        assert result1.new_total_xp == result2.new_total_xp
        assert result2.message == "Submission already processed (idempotent response)"
        assert result2.streak_increased == False
    
    def test_different_attempt_id_same_day_no_streak_increase(self, test_db):
        """Different attempt_id on same day should not increase streak"""
        submission1 = SubmissionRequest(
            attempt_id="test_003a",
            answers=[{"problem_id": 1, "answer": "42"}]
        )
        submission2 = SubmissionRequest(
            attempt_id="test_003b", 
            answers=[{"problem_id": 1, "answer": "42"}]
        )
        
        # First submission
        result1 = process_submission(test_db, user_id=1, lesson_id=1, submission=submission1)
        
        # Second submission same day
        result2 = process_submission(test_db, user_id=1, lesson_id=1, submission=submission2)
        
        assert result1.streak_increased == True  # First submission increases streak
        assert result2.streak_increased == False  # Same day, no increase
    
    def test_invalid_problem_id_raises_error(self, test_db):
        """Invalid problem ID should raise ValueError"""
        submission_data = SubmissionRequest(
            attempt_id="test_004",
            answers=[{"problem_id": 999, "answer": "42"}]  # Invalid problem ID
        )
        
        with pytest.raises(ValueError, match="Invalid problem IDs"):
            process_submission(test_db, user_id=1, lesson_id=1, submission=submission_data)


class TestXPCalculation:
    """Test XP calculation logic"""
    
    def test_correct_answer_awards_full_xp(self, test_db):
        """Correct answer should award full XP value"""
        submission_data = SubmissionRequest(
            attempt_id="test_005",
            answers=[{"problem_id": 1, "answer": "42"}]
        )
        
        result = process_submission(test_db, user_id=1, lesson_id=1, submission=submission_data)
        
        assert result.results[0]["xp_earned"] == 10
        assert result.total_xp_earned == 10
    
    def test_incorrect_answer_awards_no_xp(self, test_db):
        """Incorrect answer should award no XP"""
        submission_data = SubmissionRequest(
            attempt_id="test_006",
            answers=[{"problem_id": 1, "answer": "wrong"}]
        )
        
        result = process_submission(test_db, user_id=1, lesson_id=1, submission=submission_data)
        
        assert result.results[0]["xp_earned"] == 0
        assert result.total_xp_earned == 0
        assert result.results[0]["is_correct"] == False
    
    def test_mixed_answers_partial_xp(self, test_db):
        """Mix of correct and incorrect answers should award partial XP"""
        # Add another problem
        problem2 = Problem(id=2, lesson_id=1, question="Test2?", problem_type="numeric",
                          correct_answer="24", xp_value=15, order_index=2)
        test_db.add(problem2)
        test_db.commit()
        
        submission_data = SubmissionRequest(
            attempt_id="test_007",
            answers=[
                {"problem_id": 1, "answer": "42"},    # Correct (10 XP)
                {"problem_id": 2, "answer": "wrong"}  # Incorrect (0 XP)
            ]
        )
        
        result = process_submission(test_db, user_id=1, lesson_id=1, submission=submission_data)
        
        assert result.total_xp_earned == 10  # Only correct answer
        assert result.results[0]["xp_earned"] == 10
        assert result.results[1]["xp_earned"] == 0

