from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import datetime, timezone
from typing import List
import logging

from app.models import ProblemOption, User, Problem, Submission, UserProgress
from app.schemas import SubmissionRequest, SubmissionResponse, SingleSubmissionRequest

logger = logging.getLogger(__name__)


class SubmissionService:
    @staticmethod
    async def process_submission(
        db: AsyncSession,
        user_id: int,
        lesson_id: int,
        submission: SubmissionRequest
    ) -> SubmissionResponse:
        existing_stmt = select(Submission).where(
            and_(
                Submission.user_id == user_id,
                Submission.attempt_id == submission.attempt_id
            )
        )
        existing_result = await db.execute(existing_stmt)
        existing_submissions = existing_result.scalars().all()

        if existing_submissions:
            logger.info(
                f"Returning existing submission results for attempt_id: {submission.attempt_id}")
            return await SubmissionService._build_submission_response_from_existing(
                db, user_id, existing_submissions
            )

        problem_ids = [answer["problem_id"] for answer in submission.answers]
        problems_stmt = select(Problem).where(
            and_(
                Problem.id.in_(problem_ids),
                Problem.lesson_id == lesson_id
            )
        )
        problems_result = await db.execute(problems_stmt)
        valid_problems = problems_result.scalars().all()

        if len(valid_problems) != len(problem_ids):
            invalid_ids = set(problem_ids) - {p.id for p in valid_problems}
            raise ValueError(
                f"Invalid problem IDs for lesson {lesson_id}: {invalid_ids}")

        problems_dict = {p.id: p for p in valid_problems}

        problem_option_ids = [answer["otpion_id"]
                              for answer in submission.answers]
        problem_option_stmt = select(ProblemOption).where(
            ProblemOption.id.in_(problem_option_ids))
        problem_options_result = await db.execute(problem_option_stmt)
        problem_options = problem_options_result.scalars().all()

        problem_options_dict = {po.id: po for po in problem_options}

        results = []
        total_xp_earned = 0
        current_time = datetime.now(timezone.utc)

        try:
            for answer_data in submission.answers:
                problem_id = answer_data["problem_id"]
                option_id = answer_data["option_id"]

                problem = problems_dict[problem_id]
                problem_option = problem_options_dict[option_id]
                is_correct = problem_option.is_correct
                xp_earned = problem.xp_value if is_correct else 0

                submission_record = Submission(
                    user_id=user_id,
                    problem_id=problem_id,
                    attempt_id=submission.attempt_id,
                    option_id=option_id,
                    is_correct=is_correct,
                    xp_earned=xp_earned,
                    submitted_at=current_time
                )
                db.add(submission_record)

                results.append({
                    "problem_id": problem_id,
                    "is_correct": is_correct,
                    "xp_earned": xp_earned
                })

                total_xp_earned += xp_earned

            user_stmt = select(User).where(User.id == user_id)
            user_result = await db.execute(user_stmt)
            user = user_result.scalar_one_or_none()

            if not user:
                raise ValueError(f"User {user_id} not found")

            streak_increased = SubmissionService._update_user_streak(
                user, current_time)

            user.total_xp += total_xp_earned
            user.last_activity_date = current_time

            await db.commit()

            try:
                await SubmissionService._update_lesson_progress(db, user_id, lesson_id)
                await db.commit()
            except Exception as e:
                logger.error(f"Error updating lesson progress: {e}")

            return SubmissionResponse(
                success=True,
                message="Submission processed successfully",
                results=results,
                total_xp_earned=total_xp_earned,
                new_total_xp=user.total_xp,
                current_streak=user.current_streak,
                streak_increased=streak_increased
            )

        except Exception as e:
            await db.rollback()
            logger.error(f"Error processing submission: {e}")
            raise

    @staticmethod
    async def process_single_submission(
        db: AsyncSession,
        user_id: int,
        lesson_id: int,
        submission: SingleSubmissionRequest
    ) -> SubmissionResponse:
        problem_id = submission.answer['problem_id']
        problem_option_id = submission.answer['option_id']
        existing_stmt = select(Submission).where(
            and_(
                Submission.user_id == user_id,
                Submission.attempt_id == submission.attempt_id
            )
        )
        existing_result = await db.execute(existing_stmt)
        existing_submissions = existing_result.scalars().all()

        if existing_submissions:
            logger.info(
                f"Returning existing submission results for attempt_id: {submission.attempt_id}")
            return await SubmissionService._build_submission_response_from_existing(
                db, user_id, existing_submissions
            )

        problems_stmt = select(Problem).where(
            and_(
                Problem.id == problem_id,
                Problem.lesson_id == lesson_id
            )
        )
        problems_result = await db.execute(problems_stmt)
        valid_problem = problems_result.scalar_one_or_none()

        if not valid_problem:
            raise ValueError(
                f"Invalid problem IDs for lesson {lesson_id}: {problem_id}")

        problem_option_stmt = select(ProblemOption).where(
            ProblemOption.id == submission.answer["option_id"])
        problem_option_result = await db.execute(problem_option_stmt)
        problem_option = problem_option_result.scalar_one_or_none()

        results = []
        total_xp_earned = 0
        current_time = datetime.now(timezone.utc)

        try:
            is_correct = problem_option.is_correct
            xp_earned = valid_problem.xp_value if is_correct else 0

            submission_record = Submission(
                user_id=user_id,
                problem_id=problem_id,
                attempt_id=submission.attempt_id,
                option_id=problem_option_id,
                is_correct=is_correct,
                xp_earned=xp_earned,
                submitted_at=current_time
            )
            db.add(submission_record)

            results.append({
                "problem_id": problem_id,
                "is_correct": is_correct,
                "xp_earned": xp_earned
            })

            total_xp_earned += xp_earned

            user_stmt = select(User).where(User.id == user_id)
            user_result = await db.execute(user_stmt)
            user = user_result.scalar_one_or_none()

            if not user:
                raise ValueError(f"User {user_id} not found")

            streak_increased = SubmissionService._update_user_streak(
                user, current_time)

            user.total_xp += total_xp_earned
            user.last_activity_date = current_time

            await db.commit()

            try:
                await SubmissionService._update_lesson_progress(db, user_id, lesson_id)
                await db.commit()
            except Exception as e:
                logger.error(f"Error updating lesson progress: {e}")

            return SubmissionResponse(
                success=True,
                message="Submission processed successfully",
                results=results,
                total_xp_earned=total_xp_earned,
                new_total_xp=user.total_xp,
                current_streak=user.current_streak,
                streak_increased=streak_increased
            )

        except Exception as e:
            await db.rollback()
            logger.error(f"Error processing submission: {e}")
            raise

    @staticmethod
    async def _build_submission_response_from_existing(
        db: AsyncSession,
        user_id: int,
        existing_submissions: List[Submission]
    ) -> SubmissionResponse:
        results = []
        total_xp_earned = 0

        for sub in existing_submissions:
            results.append({
                "problem_id": sub.problem_id,
                "is_correct": sub.is_correct,
                "xp_earned": sub.xp_earned
            })
            total_xp_earned += sub.xp_earned

        user_stmt = select(User).where(User.id == user_id)
        user_result = await db.execute(user_stmt)
        user = user_result.scalar_one()

        return SubmissionResponse(
            success=True,
            message="Submission already processed (idempotent response)",
            results=results,
            total_xp_earned=total_xp_earned,
            new_total_xp=user.total_xp,
            current_streak=user.current_streak,
            streak_increased=False  # No streak increase for duplicate submissions
        )

    @staticmethod
    def _update_user_streak(user: User, current_time: datetime) -> bool:
        current_date = current_time.date()

        if user.last_activity_date is None:
            user.current_streak = 1
            return True

        last_activity_date = user.last_activity_date.date()

        if current_date == last_activity_date:
            return False
        elif current_date == last_activity_date.replace(day=last_activity_date.day + 1):
            # Next day - increase streak
            user.current_streak += 1
            return True
        else:
            # Gap in activity - reset streak
            user.current_streak = 1
            return True

    @staticmethod
    async def _update_lesson_progress(db: AsyncSession, user_id: int, lesson_id: int):
        progress_stmt = select(UserProgress).where(
            and_(UserProgress.user_id == user_id,
                 UserProgress.lesson_id == lesson_id)
        )
        progress_result = await db.execute(progress_stmt)
        progress = progress_result.scalar_one_or_none()

        if not progress:
            progress = UserProgress(
                user_id=user_id,
                lesson_id=lesson_id,
                is_completed=False,
                completion_percentage=0
            )
            db.add(progress)

        # Calculate completion percentage
        total_problems_stmt = select(func.count(Problem.id)).where(
            Problem.lesson_id == lesson_id)
        total_problems_result = await db.execute(total_problems_stmt)
        total_problems = total_problems_result.scalar()

        # Count correct submissions for this lesson
        correct_submissions_stmt = select(func.count(func.distinct(Submission.problem_id))).where(
            and_(
                Submission.user_id == user_id,
                Submission.is_correct == True,
                Submission.problem_id.in_(
                    select(Problem.id).where(Problem.lesson_id == lesson_id)
                )
            )
        )
        correct_submissions_result = await db.execute(correct_submissions_stmt)
        correct_submissions = correct_submissions_result.scalar()

        completion_percentage = int(
            (correct_submissions / total_problems) * 100) if total_problems > 0 else 0
        is_completed = completion_percentage == 100

        progress.completion_percentage = completion_percentage
        progress.is_completed = is_completed
        progress.last_accessed_at = datetime.now(timezone.utc)

        if is_completed and not progress.completed_at:
            progress.completed_at = datetime.now(timezone.utc)
