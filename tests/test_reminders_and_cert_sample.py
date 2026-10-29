"""
Automated Test Suite for:
1) Resolution of admin test series route aliases (preventing 500 BuildError)
2) Certificate sample preview on video lecture / course detail page
3) Server-side security headers (OWASP, nosniff, HSTS, Permissions-Policy)
4) Student email reminder builder and scanning logic
"""

import os
import unittest

# Force mongomock for ultra-fast, isolated unit testing without external network dependencies
os.environ["MONGODB_URI"] = ""

from flask import url_for
from app import create_app
from models import get_db, User, Course, Assignment, Enrollment, ensure_default_courses
from services.reminder_service import build_reminder_email_content, scan_and_send_student_reminders


class TestRemindersAndCertSample(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import models.mongo as mongo_mod
        mongo_mod._db = None
        mongo_mod._mongo_client = None
        cls.app = create_app()
        cls.app.config["TESTING"] = True
        cls.app.config["WTF_CSRF_ENABLED"] = False
        cls.client = cls.app.test_client()
        with cls.app.app_context():
            ensure_default_courses()

    def setUp(self):
        User._user_cache.clear()

    def test_admin_route_aliases_no_build_error(self):
        """Verifies that both admin.test_series_list and admin.test_series_tests_list resolve."""
        with self.app.test_request_context():
            url1 = url_for("admin.test_series_list")
            url2 = url_for("admin.test_series_tests_list")
            self.assertTrue(url1.startswith("/admin/test-series"))
            self.assertTrue(url2.startswith("/admin/test-series/tests"))

    def test_courses_catalogue_renders_for_anonymous_and_admin(self):
        """Ensures /learning/courses loads with HTTP 200 without raising 500 error."""
        # 1. Anonymous visitor
        res_anon = self.client.get("/learning/courses")
        self.assertEqual(res_anon.status_code, 200)

        # 2. Authenticated Admin
        with self.client.session_transaction() as sess:
            sess["_user_id"] = "admin_mock_id"
            sess["_fresh"] = True

        res_admin = self.client.get("/learning/courses")
        self.assertEqual(res_admin.status_code, 200)

    def test_security_headers_present(self):
        """Checks presence of OWASP security headers in response."""
        res = self.client.get("/learning/courses")
        self.assertEqual(res.headers.get("X-Content-Type-Options"), "nosniff")
        self.assertEqual(res.headers.get("X-Frame-Options"), "SAMEORIGIN")
        self.assertEqual(res.headers.get("Referrer-Policy"), "strict-origin-when-cross-origin")
        self.assertIn("Permissions-Policy", res.headers)

    def test_certificate_sample_in_course_detail(self):
        """Ensures the course detail page includes the new motivating certificate preview."""
        courses = Course.get_published_courses()
        if not courses:
            courses = Course.find_all()
        if courses:
            target_slug = courses[0].slug
            res = self.client.get(f"/learning/courses/{target_slug}")
            self.assertEqual(res.status_code, 200)
            html = res.get_data(as_text=True)
            self.assertIn("certSampleSection", html)
            self.assertIn("Earn Your SkillRock Verified Certificate", html)
            self.assertIn("CERTIFICATE OF ACHIEVEMENT", html)
            self.assertIn("SKILL ROCK STUDENT ACADEMY", html)

    def test_reminder_email_content_builder(self):
        """Verifies email template formatting for both reminder modes."""
        # Lecture pending
        subj_p, html_p, text_p = build_reminder_email_content(
            student_name="Rahul Sharma",
            course_title="Python Full Stack",
            course_slug="python-full-stack",
            reminder_type="lecture_pending",
            watch_percent=45,
            resume_time="12:30"
        )
        self.assertIn("Rahul", subj_p)
        self.assertIn("45%", subj_p)
        self.assertIn("Python Full Stack", html_p)
        self.assertIn("Resume Lecture Now", html_p)

        # Certificate waiting
        subj_c, html_c, text_c = build_reminder_email_content(
            student_name="Rahul Sharma",
            course_title="Python Full Stack",
            course_slug="python-full-stack",
            reminder_type="certificate_waiting",
            watch_percent=85,
            resume_time="25:10"
        )
        self.assertIn("certificate", subj_c.lower())
        self.assertIn("Claim Your Certificate Now", html_c)

    def test_reminder_scanner_dry_run(self):
        """Checks scan_and_send_student_reminders execution without unhandled exceptions."""
        summary = scan_and_send_student_reminders(app=self.app)
        self.assertIn("scanned_students", summary)
        self.assertIn("eligible_students", summary)
        self.assertIn("sent_emails", summary)


if __name__ == "__main__":
    unittest.main()
