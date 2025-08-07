#!/usr/bin/env python3
"""
Seed script to populate the database with initial data
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models import User, Lesson, Problem, ProblemOption
from app.core.database import non_async_engine
from sqlalchemy.orm import sessionmaker



# Create session
SessionLocal = sessionmaker(bind=non_async_engine)
db = SessionLocal()


def seed_data():
    try:
        user_count = db.query(User).count()
        # Create demo user
        if user_count == 0:
            demo_user = User(
                id=1,
                username="demo_user",
                email="demo@example.com",
                total_xp=0,
                current_streak=0
            )
            db.add(demo_user)

        lesson_count = db.query(Lesson).count()

        if lesson_count == 0:
            # Lesson 1: Basic Arithmetic
            lesson1 = Lesson(
                title="Basic Arithmetic",
                description="Learn addition and subtraction fundamentals",
                order_index=1,
                is_active=True
            )
            db.add(lesson1)
            db.flush()  # Get the lesson ID

            # Lesson 1 Problems
            problems_lesson1 = [
                {
                    "question": "What is 5 + 3?",
                    "xp_value": 10,
                    "order_index": 1,
                    "options": [
                        {
                            "option_text": "12",
                            "order_index": 1,
                            "is_correct": False
                        },
                        {
                            "option_text": "2",
                            "order_index": 2,
                            "is_correct": False
                        },
                        {
                            "option_text": "8",
                            "order_index": 3,
                            "is_correct": True
                        },
                        {
                            "option_text": "10",
                            "order_index": 4,
                            "is_correct": False
                        }
                    ]
                },
                {
                    "question": "What is 12 - 7?",
                    "xp_value": 10,
                    "order_index": 2,
                    "options": [
                        {
                            "option_text": "6",
                            "order_index": 1,
                            "is_correct": False
                        },
                        {
                            "option_text": "5",
                            "order_index": 2,
                            "is_correct": True
                        },
                        {
                            "option_text": "8",
                            "order_index": 3,
                            "is_correct": False
                        },
                        {
                            "option_text": "10",
                            "order_index": 4,
                            "is_correct": False
                        }
                    ]
                },
                {
                    "question": "What is 9 + 6?",
                    "xp_value": 10,
                    "order_index": 3,
                    "options": [
                        {
                            "option_text": "14",
                            "order_index": 1,
                            "is_correct": False
                        },
                        {
                            "option_text": "3",
                            "order_index": 2,
                            "is_correct": False
                        },
                        {
                            "option_text": "16",
                            "order_index": 3,
                            "is_correct": False
                        },
                        {
                            "option_text": "15",
                            "order_index": 4,
                            "is_correct": True
                        }
                    ]
                },
                {
                    "question": "What is 20 - 8?",
                    "xp_value": 10,
                    "order_index": 4,
                    "options": [
                        {
                            "option_text": "12",
                            "order_index": 1,
                            "is_correct": True
                        },
                        {
                            "option_text": "10",
                            "order_index": 2,
                            "is_correct": False
                        },
                        {
                            "option_text": "28",
                            "order_index": 3,
                            "is_correct": False
                        },
                        {
                            "option_text": "11",
                            "order_index": 4,
                            "is_correct": False
                        }
                    ]
                }
            ]

            for prob_data in problems_lesson1:
                problem = Problem(
                    lesson_id=lesson1.id,
                    question=prob_data["question"],
                    problem_type="options",
                    xp_value=prob_data["xp_value"],
                    order_index=prob_data["order_index"]
                )
                db.add(problem)
                db.flush()
                for option_data in prob_data["options"]:
                    option = ProblemOption(
                        problem_id=problem.id,
                        option_text=option_data["option_text"],
                        order_index=option_data["order_index"],
                        is_correct=option_data["is_correct"],
                    )
                    db.add(option)

            # Lesson 2: Multiplication Mastery
            lesson2 = Lesson(
                title="Multiplication Mastery",
                description="Master multiplication tables and techniques",
                order_index=2,
                is_active=True
            )
            db.add(lesson2)
            db.flush()

            # Lesson 2 Problems
            problems_lesson2 = [
                {
                    "question": "What is 4 × 6?",
                    "xp_value": 15,
                    "order_index": 1,
                    "options": [
                        {
                            "option_text": "20",
                            "order_index": 1,
                            "is_correct": False
                        },
                        {
                            "option_text": "24",
                            "order_index": 2,
                            "is_correct": True
                        },
                        {
                            "option_text": "28",
                            "order_index": 3,
                            "is_correct": False
                        },
                        {
                            "option_text": "2",
                            "order_index": 4,
                            "is_correct": False
                        }
                    ]
                },
                {
                    "question": "What is 7 × 8?",
                    "correct_answer": "56",
                    "xp_value": 15,
                    "order_index": 2,
                    "options": [
                        {
                            "option_text": "32",
                            "order_index": 1,
                            "is_correct": False
                        },
                        {
                            "option_text": "62",
                            "order_index": 2,
                            "is_correct": False
                        },
                        {
                            "option_text": "56",
                            "order_index": 3,
                            "is_correct": True
                        },
                        {
                            "option_text": "15",
                            "order_index": 4,
                            "is_correct": False
                        }
                    ]
                },
                {
                    "question": "What is 9 × 5?",
                    "xp_value": 15,
                    "order_index": 3,
                    "options": [
                        {
                            "option_text": "40",
                            "order_index": 1,
                            "is_correct": False
                        },
                        {
                            "option_text": "4",
                            "order_index": 2,
                            "is_correct": False
                        },
                        {
                            "option_text": "14",
                            "order_index": 3,
                            "is_correct": False
                        },
                        {
                            "option_text": "45",
                            "order_index": 4,
                            "is_correct": True
                        }
                    ]
                },
                {
                    "question": "What is 6 × 7?",
                    "xp_value": 15,
                    "order_index": 4,
                    "options": [
                        {
                            "option_text": "42",
                            "order_index": 1,
                            "is_correct": True
                        },
                        {
                            "option_text": "70",
                            "order_index": 2,
                            "is_correct": False
                        },
                        {
                            "option_text": "67",
                            "order_index": 3,
                            "is_correct": False
                        },
                        {
                            "option_text": "13",
                            "order_index": 4,
                            "is_correct": False
                        }
                    ]
                }
            ]

            for prob_data in problems_lesson2:
                problem = Problem(
                    lesson_id=lesson2.id,
                    question=prob_data["question"],
                    problem_type="options",
                    xp_value=prob_data["xp_value"],
                    order_index=prob_data["order_index"]
                )
                db.add(problem)
                db.flush()
                for option_data in prob_data["options"]:
                    option = ProblemOption(
                        problem_id=problem.id,
                        option_text=option_data["option_text"],
                        order_index=option_data["order_index"],
                        is_correct=option_data["is_correct"],
                    )
                    db.add(option)

            # Lesson 3: Division Basics
            lesson3 = Lesson(
                title="Division Basics",
                description="Learn division fundamentals and techniques",
                order_index=3,
                is_active=True
            )
            db.add(lesson3)
            db.flush()

            # Lesson 3 Problems
            problems_lesson3 = [
                {
                    "question": "What is 24 ÷ 6?",
                    "xp_value": 20,
                    "order_index": 1,
                    "options": [
                        {
                            "option_text": "4",
                            "order_index": 1,
                            "is_correct": True
                        },
                        {
                            "option_text": "10",
                            "order_index": 31,
                            "is_correct": False
                        },
                        {
                            "option_text": "18",
                            "order_index": 3,
                            "is_correct": False
                        },
                        {
                            "option_text": "20",
                            "order_index": 4,
                            "is_correct": False
                        }
                    ]
                },
                {
                    "question": "What is 35 ÷ 7?",
                    "xp_value": 20,
                    "order_index": 2,
                    "options": [
                        {
                            "option_text": "42",
                            "order_index": 1,
                            "is_correct": False
                        },
                        {
                            "option_text": "28",
                            "order_index": 2,
                            "is_correct": False
                        },
                        {
                            "option_text": "5",
                            "order_index": 3,
                            "is_correct": True
                        },
                        {
                            "option_text": "20",
                            "order_index": 4,
                            "is_correct": False
                        }
                    ]
                },
                {
                    "question": "What is 48 ÷ 8?",
                    "xp_value": 20,
                    "order_index": 3,
                    "options": [
                        {
                            "option_text": "52",
                            "order_index": 1,
                            "is_correct": False
                        },
                        {
                            "option_text": "6",
                            "order_index": 2,
                            "is_correct": True
                        },
                        {
                            "option_text": "40",
                            "order_index": 3,
                            "is_correct": False
                        },
                        {
                            "option_text": "20",
                            "order_index": 4,
                            "is_correct": False
                        }
                    ]
                },
                {
                    "question": "What is 63 ÷ 9?",
                    "xp_value": 20,
                    "order_index": 4,
                    "options": [
                        {
                            "option_text": "12",
                            "order_index": 1,
                            "is_correct": False
                        },
                        {
                            "option_text": "7",
                            "order_index": 2,
                            "is_correct": True
                        },
                        {
                            "option_text": "56",
                            "order_index": 3,
                            "is_correct": False
                        },
                        {
                            "option_text": "11",
                            "order_index": 4,
                            "is_correct": False
                        }
                    ]
                },
                {
                    "question": "What is 56 ÷ 7?",
                    "xp_value": 20,
                    "order_index": 5,
                    "options": [
                        {
                            "option_text": "20",
                            "order_index": 1,
                            "is_correct": False
                        },
                        {
                            "option_text": "61",
                            "order_index": 2,
                            "is_correct": False
                        },
                        {
                            "option_text": "49",
                            "order_index": 3,
                            "is_correct": False
                        },
                        {
                            "option_text": "8",
                            "order_index": 4,
                            "is_correct": True
                        }
                    ]
                }
            ]

            for prob_data in problems_lesson3:
                problem = Problem(
                    lesson_id=lesson3.id,
                    question=prob_data["question"],
                    problem_type="options",
                    xp_value=prob_data["xp_value"],
                    order_index=prob_data["order_index"]
                )
                db.add(problem)
                db.flush()
                for option_data in prob_data["options"]:
                    option = ProblemOption(
                        problem_id=problem.id,
                        option_text=option_data["option_text"],
                        order_index=option_data["order_index"],
                        is_correct=option_data["is_correct"],
                    )
                    db.add(option)

        # Commit all changes
        db.commit()
        print("✅ Seed data created successfully!")
        print(f"Created {db.query(User).count()} users")
        print(f"Created {db.query(Lesson).count()} lessons")
        print(f"Created {db.query(Problem).count()} problems")
        print(f"Created {db.query(ProblemOption).count()} problem options")

    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding data: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_data()
