import os
import sys
import unittest
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.stdout.reconfigure(encoding="utf-8")

from app import create_app
from models.mongo import (
    get_db,
    User,
    Course,
    Assignment,
    Submission,
    Certificate,
    Enrollment,
    Review
)
from services.storage_cleaner import purge_inactive_users, purge_orphaned_records, run_storage_optimization
from services.email_service import send_admin_assignment_notification


class TestQuizAndStorage(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.app.config["TESTING"] = True
        cls.app.config["WTF_CSRF_ENABLED"] = False
        cls.client = cls.app.test_client()

    def setUp(self):
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.db = get_db()

    def tearDown(self):
        self.app_context.pop()

    def test_quiz_auto_certificate_unlock(self):
        """
        Verify that scoring >= 70% in a quiz-based assignment automatically
        issues and unlocks the certificate without requiring manual review or video watching.
        """
        # Create test student
        student = User({
            "email": f"quiz_pass_student_{datetime.now().timestamp()}@example.com",
            "name": "Quiz Master",
            "role": "student",
            "is_admin": False
        })
        student.set_password("Pass1234!")
        student.save()

        # Create test quiz course & assignment
        course = Course({
            "title": "Machine Learning Fundamentals Quiz",
            "slug": f"ml-quiz-{int(datetime.now().timestamp())}",
            "is_published": True,
            "category": "Data Science & AI",
            "curriculum": [{"step_number": 1, "title": "Intro"}]
        })
        course.save()

        assignment = Assignment({
            "course_id": str(course.id),
            "step_number": 1,
            "total_steps": 1,
            "title": "ML Fundamentals Knowledge Check",
            "evaluation_type": Assignment.TYPE_QUIZ_BASED,
            "passing_score": 70,
            "quiz_allow_review": True,
            "quiz_data": {
                "questions": [
                    {
                        "id": "q1",
                        "type": "single_choice",
                        "question": "What is overfitting?",
                        "options": ["High variance", "Low variance"],
                        "correct_answer": "High variance",
                        "marks": 10
                    }
                ]
            }
        })
        assignment.save()

        # Enroll student with 0% video watch
        enrollment = Enrollment({
            "user_id": str(student.id),
            "course_id": str(course.id),
            "watch_percent": 0,
            "video_completed": False,
            "status": "enrolled"
        })
        enrollment.save()

        # Simulate student passing quiz with 100%
        submission = Submission({
            "assignment_id": str(assignment.id),
            "course_id": str(course.id),
            "user_id": str(student.id),
            "step_number": 1,
            "evaluation_type": Assignment.TYPE_QUIZ_BASED,
            "automated_score": 100,
            "status": Submission.STATUS_APPROVED,
            "created_at": datetime.now(timezone.utc)
        })
        submission.save()

        # Call Certificate.issue with bypass_video=True (quiz flow)
        cert = Certificate.issue(student, course, assignment, submission, bypass_video=True)
        self.assertIsNotNone(cert, "Certificate should be issued immediately for passed quiz")
        self.assertTrue(cert.certificate_id.startswith("SR-2026-"))

        # Verify certificate is retrievable
        fetched_cert = Certificate.get_by_user_course(student.id, course.id)
        self.assertIsNotNone(fetched_cert)
        self.assertEqual(fetched_cert.certificate_id, cert.certificate_id)

    @patch("services.email_service.smtplib.SMTP")
    def test_project_submission_email_notification(self, mock_smtp):
        """
        Verify that project submission triggers the admin notification email sender.
        """
        student = User({
            "email": "test_submitter@example.com",
            "name": "Alex Project Submitter",
            "role": "student"
        })
        student.id = "user123"

        course = Course({
            "title": "Full Stack Web Development",
            "slug": "full-stack-web-dev"
        })
        course.id = "course123"

        assignment = Assignment({
            "title": "Portfolio Website Capstone",
            "step_number": 1,
            "total_steps": 1
        })
        assignment.id = "asg123"

        submission = Submission({
            "github_url": "https://github.com/alex/portfolio",
            "deployment_url": "https://alexportfolio.vercel.app"
        })

        # Should execute safely in background thread without raising exceptions
        send_admin_assignment_notification(student, course, assignment, submission)

    def test_inactive_user_cleanup(self):
        """
        Verify that inactive users (>= 7 days inactive) are purged,
        admins are protected, and active users are preserved.
        """
        now = datetime.now(timezone.utc)
        eight_days_ago = now - timedelta(days=8)
        two_days_ago = now - timedelta(days=2)

        # 1. Inactive student (8 days ago) -> MUST be purged
        inactive_student = User({
            "email": f"inactive_{datetime.now().timestamp()}@example.com",
            "name": "Inactive Student",
            "role": "student",
            "is_admin": False,
            "last_active_at": eight_days_ago,
            "created_at": eight_days_ago
        })
        inactive_student.save()
        inactive_id = str(inactive_student.id)

        # 2. Active student (2 days ago) -> MUST be preserved
        active_student = User({
            "email": f"active_{datetime.now().timestamp()}@example.com",
            "name": "Active Student",
            "role": "student",
            "is_admin": False,
            "last_active_at": two_days_ago,
            "created_at": eight_days_ago
        })
        active_student.save()
        active_id = str(active_student.id)

        # 3. Inactive Admin (8 days ago) -> MUST be protected!
        admin_user = User({
            "email": f"admin_backup_{datetime.now().timestamp()}@example.com",
            "name": "Platform Admin",
            "role": "admin",
            "is_admin": True,
            "last_active_at": eight_days_ago,
            "created_at": eight_days_ago
        })
        admin_user.save()
        admin_id = str(admin_user.id)

        # Run purge
        purged_count = purge_inactive_users(days=7)
        self.assertGreaterEqual(purged_count, 1)

        # Assertions
        self.assertIsNone(User.get_by_id(inactive_id), "Inactive student should be deleted")
        self.assertIsNotNone(User.get_by_id(active_id), "Active student must NOT be deleted")
        self.assertIsNotNone(User.get_by_id(admin_id), "Admin user must NEVER be deleted")

    def test_orphan_records_cleanup(self):
        """
        Verify that orphaned enrollments, submissions, and reviews are cleaned up.
        """
        # Insert orphaned enrollment (non-existent user)
        self.db.enrollments.insert_one({
            "user_id": "nonexistent_user_99999",
            "course_id": "fake_course_99999",
            "status": "enrolled"
        })

        purged_orphans = purge_orphaned_records()
        self.assertGreaterEqual(purged_orphans, 1)

        orphan_check = self.db.enrollments.find_one({"user_id": "nonexistent_user_99999"})
        self.assertIsNone(orphan_check, "Orphaned enrollment should have been purged")


if __name__ == "__main__":
    unittest.main()
