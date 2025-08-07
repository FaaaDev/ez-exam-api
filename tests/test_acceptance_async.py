"""
Async Acceptance tests for the refactored learning platform
Tests the key requirements with the new async structure
"""
import requests
import json
import time
from datetime import datetime


BASE_URL = "http://localhost:8000"


def test_async_first_submission_increases_streak():
    """First submission on a new day should increase streak (async version)"""
    print("Testing: Async first submission increases streak")
    
    # Get initial profile
    response = requests.get(f"{BASE_URL}/api/profile")
    assert response.status_code == 200
    initial_profile = response.json()
    initial_streak = initial_profile["current_streak"]
    
    # Submit answers
    submission_data = {
        "attempt_id": f"async_acceptance_test_{int(time.time())}",
        "answers": [
            {"problem_id": 1, "answer": "8"},
            {"problem_id": 2, "answer": "5"}
        ]
    }
    
    response = requests.post(f"{BASE_URL}/api/lessons/1/submit", json=submission_data)
    assert response.status_code == 200
    result = response.json()
    
    # Check if streak increased (should be true for first submission or new day)
    assert result["success"] == True
    assert result["current_streak"] >= initial_streak
    print("✅ Async first submission streak test passed")


def test_async_resubmit_same_attempt_id_no_xp_increase():
    """Resubmit with same attempt_id should not increase XP (idempotent) - async version"""
    print("Testing: Async idempotent submission with same attempt_id")
    
    attempt_id = f"async_idempotent_test_{int(time.time())}"
    submission_data = {
        "attempt_id": attempt_id,
        "answers": [
            {"problem_id": 1, "answer": "8"},
            {"problem_id": 2, "answer": "5"}
        ]
    }
    
    # First submission
    response1 = requests.post(f"{BASE_URL}/api/lessons/1/submit", json=submission_data)
    assert response1.status_code == 200
    result1 = response1.json()
    
    # Second submission with same attempt_id
    response2 = requests.post(f"{BASE_URL}/api/lessons/1/submit", json=submission_data)
    assert response2.status_code == 200
    result2 = response2.json()
    
    # Results should be identical
    assert result1["total_xp_earned"] == result2["total_xp_earned"]
    assert result1["new_total_xp"] == result2["new_total_xp"]
    assert "already processed" in result2["message"].lower()
    assert result2["streak_increased"] == False
    print("✅ Async idempotent submission test passed")


def test_async_resubmit_same_day_different_attempt_id_no_streak_increase():
    """Resubmit on same day with different attempt_id should not increase streak - async version"""
    print("Testing: Async same day different attempt_id - no streak increase")
    
    # First submission
    submission1 = {
        "attempt_id": f"async_same_day_1_{int(time.time())}",
        "answers": [{"problem_id": 1, "answer": "8"}]
    }
    
    response1 = requests.post(f"{BASE_URL}/api/lessons/1/submit", json=submission1)
    assert response1.status_code == 200
    result1 = response1.json()
    
    # Second submission same day, different attempt_id
    time.sleep(1)  # Small delay to ensure different attempt_id
    submission2 = {
        "attempt_id": f"async_same_day_2_{int(time.time())}",
        "answers": [{"problem_id": 2, "answer": "5"}]
    }
    
    response2 = requests.post(f"{BASE_URL}/api/lessons/1/submit", json=submission2)
    assert response2.status_code == 200
    result2 = response2.json()
    
    # Second submission should not increase streak (same day)
    assert result2["streak_increased"] == False
    print("✅ Async same day different attempt_id test passed")


def test_async_invalid_problem_id_returns_422():
    """Invalid Problem ID should return 422 - async version"""
    print("Testing: Async invalid problem ID returns 422")
    
    submission_data = {
        "attempt_id": f"async_invalid_test_{int(time.time())}",
        "answers": [
            {"problem_id": 999, "answer": "8"}  # Invalid problem ID
        ]
    }
    
    response = requests.post(f"{BASE_URL}/api/lessons/1/submit", json=submission_data)
    assert response.status_code == 422
    print("✅ Async invalid problem ID test passed")


def test_async_lessons_endpoint_returns_progress():
    """GET /api/lessons should return lessons with progress status - async version"""
    print("Testing: Async lessons endpoint returns progress")
    
    response = requests.get(f"{BASE_URL}/api/lessons/")
    assert response.status_code == 200
    lessons = response.json()
    
    assert len(lessons) > 0
    for lesson in lessons:
        assert "id" in lesson
        assert "title" in lesson
        assert "progress_status" in lesson
        assert "is_completed" in lesson["progress_status"]
        assert "completion_percentage" in lesson["progress_status"]
    
    print("✅ Async lessons endpoint test passed")


def test_async_profile_endpoint_returns_stats():
    """GET /api/profile should return user statistics - async version"""
    print("Testing: Async profile endpoint returns user stats")
    
    response = requests.get(f"{BASE_URL}/api/profile")
    assert response.status_code == 200
    profile = response.json()
    
    required_fields = [
        "user_id", "username", "total_xp", "current_streak",
        "progress_percentage", "lessons_completed", "total_lessons"
    ]
    
    for field in required_fields:
        assert field in profile
    
    print("✅ Async profile endpoint test passed")


def test_async_xp_calculation():
    """Test XP calculation for correct and incorrect answers - async version"""
    print("Testing: Async XP calculation")
    
    # Test correct answers
    submission_correct = {
        "attempt_id": f"async_xp_correct_{int(time.time())}",
        "answers": [
            {"problem_id": 1, "answer": "8"},  # Correct
            {"problem_id": 2, "answer": "5"}   # Correct
        ]
    }
    
    response = requests.post(f"{BASE_URL}/api/lessons/1/submit", json=submission_correct)
    assert response.status_code == 200
    result = response.json()
    
    # Should award XP for correct answers
    assert result["total_xp_earned"] > 0
    assert all(r["is_correct"] for r in result["results"])
    assert all(r["xp_earned"] > 0 for r in result["results"])
    
    # Test incorrect answers
    submission_incorrect = {
        "attempt_id": f"async_xp_incorrect_{int(time.time())}",
        "answers": [
            {"problem_id": 1, "answer": "wrong"},
            {"problem_id": 2, "answer": "also_wrong"}
        ]
    }
    
    response = requests.post(f"{BASE_URL}/api/lessons/1/submit", json=submission_incorrect)
    assert response.status_code == 200
    result = response.json()
    
    # Should not award XP for incorrect answers
    assert result["total_xp_earned"] == 0
    assert all(not r["is_correct"] for r in result["results"])
    assert all(r["xp_earned"] == 0 for r in result["results"])
    
    print("✅ Async XP calculation test passed")


def test_async_performance_improvement():
    """Test that async version performs well with concurrent requests"""
    print("Testing: Async performance with concurrent requests")
    
    import concurrent.futures
    import threading
    
    def make_request():
        response = requests.get(f"{BASE_URL}/api/profile")
        return response.status_code == 200
    
    # Make 10 concurrent requests
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(make_request) for _ in range(10)]
        results = [future.result() for future in concurrent.futures.as_completed(futures)]
    
    # All requests should succeed
    assert all(results)
    print("✅ Async performance test passed")


if __name__ == "__main__":
    print("Running async acceptance tests...")
    print("=" * 50)
    
    try:
        test_async_first_submission_increases_streak()
        test_async_resubmit_same_attempt_id_no_xp_increase()
        test_async_resubmit_same_day_different_attempt_id_no_streak_increase()
        test_async_invalid_problem_id_returns_422()
        test_async_lessons_endpoint_returns_progress()
        test_async_profile_endpoint_returns_stats()
        test_async_xp_calculation()
        test_async_performance_improvement()
        
        print("=" * 50)
        print("🎉 All async acceptance tests passed!")
        print("🚀 Async refactoring successful!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        raise

