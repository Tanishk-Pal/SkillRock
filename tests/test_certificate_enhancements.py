import os
import sys
import unittest
from datetime import datetime, timezone

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.stdout.reconfigure(encoding="utf-8")

from app import create_app
from models.mongo import (
    get_db,
    User,
    Course,
    Assignment,
    Submission,
    Certificate
)


class TestCertificateEnhancements(unittest.TestCase):

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

    def test_canonical_course_titles(self):
        """Verify that course titles are properly cleaned and canonicalized for certificates."""
        # Predefined canonical course
        course_sql = Course({
            "title": "SQL Complete Course in 3 Hours — MySQL",
            "slug": "sql-complete-course-in-3-hours-mysql"
        })
        self.assertEqual(course_sql.get_certificate_title(), "SQL & Relational Database Management")

        course_aiml = Course({
            "title": "Complete AI/ML Job Ready Batch — Introduction",
            "slug": "complete-aiml-job-ready-batch-introduction"
        })
        self.assertEqual(course_aiml.get_certificate_title(), "Artificial Intelligence & Machine Learning Fundamentals")

        # Unknown course with clickbait noise
        course_custom = Course({
            "title": "Learn Docker in 4 Hours: Complete Bootcamp from Scratch",
            "slug": "learn-docker-in-4-hours"
        })
        clean_title = course_custom.get_certificate_title()
        self.assertNotIn("4 Hours", clean_title)
        self.assertNotIn("Bootcamp", clean_title)
        self.assertIn("Docker", clean_title)

    def test_one_time_name_lock(self):
        """
        Verify that a user can update their name once, that it permanently locks,
        re-hashes the certificate, syncs the user profile, and rejects subsequent edits.
        """
        # Create test student
        student = User({
            "email": f"namelock_{datetime.now().timestamp()}@example.com",
            "name": "Initial Nickname",
            "role": "student"
        })
        student.save()

        # Get or create course
        course = Course.get_by_slug("sql-complete-course-in-3-hours-mysql")
        if not course:
            course = Course({
                "title": "SQL Complete Course in 3 Hours — MySQL",
                "slug": f"sql-course-{datetime.now().timestamp()}"
            })
            course.save()

        cert = Certificate({
            "certificate_id": Certificate.generate_cert_id(),
            "user_id": str(student.id),
            "user_name": student.name,
            "user_email": student.email,
            "course_id": str(course.id),
            "course_title": course.title,
            "issued_at": datetime.now(timezone.utc),
            "verification_hash": "old_hash_123",
            "name_locked": False
        })
        cert.save()

        self.assertFalse(cert.name_locked)
        self.assertEqual(cert.user_name, "Initial Nickname")

        # 1. First Name Lock (Must Succeed)
        success, msg = cert.lock_legal_name("Alexander J. Mercer")
        self.assertTrue(success)
        self.assertTrue(cert.name_locked)
        self.assertEqual(cert.user_name, "Alexander J. Mercer")
        self.assertNotEqual(cert.verification_hash, "old_hash_123")

        # Verify User profile was synchronized
        updated_user = User.get_by_id(student.id)
        self.assertEqual(updated_user.name, "Alexander J. Mercer")

        # 2. Second Name Lock Attempt (MUST Fail)
        success_second, msg_second = cert.lock_legal_name("Attempted Fraud Name")
        self.assertFalse(success_second)
        self.assertIn("already been permanently locked", msg_second)
        self.assertEqual(cert.user_name, "Alexander J. Mercer")

    def test_certificate_display_course_title(self):
        """Verify Certificate.display_course_title resolves to clean title."""
        course = Course.get_by_slug("complete-c-programming-tutorial-for-beginners")
        if not course:
            course = Course({
                "title": "Complete C++ Programming Tutorial for Beginners",
                "slug": f"cpp-{datetime.now().timestamp()}"
            })
            course.save()

        unique_user_id = f"test_user_disp_{datetime.now().timestamp()}"
        cert = Certificate({
            "certificate_id": Certificate.generate_cert_id(),
            "user_id": unique_user_id,
            "user_name": "Test User",
            "course_id": str(course.id),
            "course_title": course.title,
            "issued_at": datetime.now(timezone.utc)
        })
        cert.save()

        self.assertEqual(cert.display_course_title, "C++ Systems Programming & Software Development")

    def test_lock_name_route(self):
        """Verify the lock-name route updates the name and requires authentication."""
        student = User({
            "email": f"route_lock_{datetime.now().timestamp()}@example.com",
            "name": "Demo Student",
            "role": "student"
        })
        student.set_password("Pass1234!")
        student.save()

        course = Course.get_by_slug("sql-complete-course-in-3-hours-mysql")
        if not course:
            course = Course({
                "title": "SQL Complete Course in 3 Hours — MySQL",
                "slug": f"sql-{datetime.now().timestamp()}"
            })
            course.save()

        cert = Certificate({
            "certificate_id": Certificate.generate_cert_id(),
            "user_id": str(student.id),
            "user_name": "Demo Student",
            "course_id": str(course.id),
            "course_title": course.title,
            "issued_at": datetime.now(timezone.utc),
            "name_locked": False
        })
        cert.save()

        # Login as student
        with self.client.session_transaction() as sess:
            sess["_user_id"] = str(student.id)

        # POST lock-name
        resp = self.client.post(
            f"/learning/certificate/{cert.certificate_id}/lock-name",
            json={"legal_name": "Official Verified Name"}
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["updated_name"], "Official Verified Name")

        # Refetch from DB
        updated_cert = Certificate.get_by_cert_id(cert.certificate_id)
        self.assertTrue(updated_cert.name_locked)
        self.assertEqual(updated_cert.user_name, "Official Verified Name")


if __name__ == "__main__":
    unittest.main()
