"""
Automated Unit & Integration Test Suite for Milestone 1 (Requirement R1):
Automatic Course Enrollment & Registration Flow

Covers:
1. Unauthenticated "Start Learning" redirect to /register?next=...
2. Retention and forwarding of next parameter across /register and /login
3. New user registration auto-enrolls into course and navigates to player
4. Existing user login auto-enrolls into course and navigates to player
5. Authenticated direct "Start Learning" auto-enrolls and navigates to player
6. Course detail page ?start=1 / ?enrol=1 auto-enrolls authenticated student
7. Video streaming content protection (unauthenticated visitors blocked from streaming)
8. Authenticated access to interactive player and controls
9. Open redirect attack defense (malicious next URLs safely rejected)
10. Idempotent enrollment without duplicate records or progress reset
11. Course resolution by both slug and MongoDB ObjectId
"""

import os
import unittest
from urllib.parse import unquote

# Force mongomock for fast, isolated in-memory unit testing
os.environ["MONGODB_URI"] = ""
os.environ["TESTING"] = "1"

import models.mongo as mongo_mod
mongo_mod._db = None
mongo_mod._mongo_client = None

from flask import url_for
from app import create_app
from models import (
    get_db,
    User,
    Course,
    Enrollment,
    ensure_default_courses
)


class TestR1EnrollmentAuthFlow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        mongo_mod._db = None
        mongo_mod._mongo_client = None
        cls.app = create_app()
        cls.app.config["TESTING"] = True
        cls.app.config["WTF_CSRF_ENABLED"] = False
        cls.client = cls.app.test_client()

        with cls.app.app_context():
            ensure_default_courses()
            courses = Course.find_all()
            cls.course = courses[0]
            cls.course_slug = cls.course.slug

    def setUp(self):
        self.db = get_db()
        User._user_cache.clear()
        # Clean test accounts and enrollments
        self.db.users.delete_many({"email": {"$regex": r"^test_r1_.*@skillrock\.org$"}})
        self.db.enrollments.delete_many({})

    def tearDown(self):
        self.db.users.delete_many({"email": {"$regex": r"^test_r1_.*@skillrock\.org$"}})
        self.db.enrollments.delete_many({})

    # -------------------------------------------------------------------------
    # 1. Unauthenticated "Start Learning" Redirect
    # -------------------------------------------------------------------------
    def test_01_unauthenticated_start_learning_redirects_to_register(self):
        """Unauthenticated GET /learning/courses/<slug>/start must 302 redirect to /register?next=..."""
        res = self.client.get(f"/learning/courses/{self.course_slug}/start")
        self.assertEqual(res.status_code, 302)
        location = unquote(res.headers.get("Location", ""))
        self.assertIn("/register", location)
        self.assertIn(self.course_slug, location)

    # -------------------------------------------------------------------------
    # 2. Registration Page Preserves and Forwards next Parameter
    # -------------------------------------------------------------------------
    def test_02_register_page_preserves_next_parameter(self):
        """GET /register?next=... must retain next in redirect to /login and in rendered login form."""
        target_next = f"/learning/courses/{self.course_slug}?player=1#skillrockPlayerFrame"
        res = self.client.get(f"/register?next={target_next}", follow_redirects=False)
        self.assertEqual(res.status_code, 302)
        loc = unquote(res.headers.get("Location", ""))
        self.assertIn("/login", loc)
        self.assertIn(self.course_slug, loc)

        # Follow redirect and verify next is preserved in login form
        res_login = self.client.get(f"/register?next={target_next}", follow_redirects=True)
        self.assertEqual(res_login.status_code, 200)
        html = res_login.get_data(as_text=True)
        self.assertTrue(
            (f'name="next" value="{target_next}"' in html) or
            (self.course_slug in html),
            "The login form must preserve the target course next parameter."
        )

    # -------------------------------------------------------------------------
    # 3. New User Registration Auto-Enrolls and Navigates to Player
    # -------------------------------------------------------------------------
    def test_03_registration_auto_enrolls_and_navigates_to_player(self):
        """New student registering via /login with next=/learning/courses/<slug> auto-enrolls and redirects to player."""
        test_email = "test_r1_new_student@skillrock.org"
        target_next = f"/learning/courses/{self.course_slug}"

        res = self.client.post("/login", data={
            "email": test_email,
            "password": "Password123!",
            "name": "R1 New Student",
            "next": target_next
        }, follow_redirects=False)

        self.assertEqual(res.status_code, 302)
        location = res.headers.get("Location", "")
        self.assertIn(self.course_slug, location)
        self.assertIn("player=1", location)

        # Verify enrollment is recorded in database
        user = User.get_by_email(test_email)
        self.assertIsNotNone(user)
        enrollment = Enrollment.get_by_user_course(user.id, self.course.id)
        self.assertIsNotNone(enrollment, "New student must be enrolled in course immediately.")
        self.assertEqual(enrollment.status, "enrolled")

    # -------------------------------------------------------------------------
    # 4. Existing User Login Auto-Enrolls and Navigates to Player
    # -------------------------------------------------------------------------
    def test_04_login_auto_enrolls_and_navigates_to_player(self):
        """Existing student logging in with next auto-enrolls if unenrolled and redirects to player."""
        test_email = "test_r1_existing_student@skillrock.org"
        user = User.create(email=test_email, name="R1 Existing Student")
        user.set_password("Password123!")
        user.save()

        # Ensure not enrolled prior to login
        self.assertIsNone(Enrollment.get_by_user_course(user.id, self.course.id))

        target_next = f"/learning/courses/{self.course_slug}"
        res = self.client.post("/login", data={
            "email": test_email,
            "password": "Password123!",
            "next": target_next
        }, follow_redirects=False)

        self.assertEqual(res.status_code, 302)
        location = res.headers.get("Location", "")
        self.assertIn(self.course_slug, location)
        self.assertIn("player=1", location)

        # Verify auto-enrollment
        enrollment = Enrollment.get_by_user_course(user.id, self.course.id)
        self.assertIsNotNone(enrollment, "Existing student must be auto-enrolled on login.")

    # -------------------------------------------------------------------------
    # 5. Authenticated Student "Start Learning" Auto-Enrollment
    # -------------------------------------------------------------------------
    def test_05_authenticated_start_learning_auto_enrolls_and_redirects(self):
        """Authenticated student visiting /learning/courses/<slug>/start auto-enrolls and enters player."""
        test_email = "test_r1_auth_start@skillrock.org"
        user = User.create(email=test_email, name="Auth Start Student")
        user.set_password("Password123!")
        user.save()

        # Log in student
        self.client.post("/login", data={"email": test_email, "password": "Password123!"})

        res = self.client.get(f"/learning/courses/{self.course_slug}/start", follow_redirects=False)
        self.assertEqual(res.status_code, 302)
        location = res.headers.get("Location", "")
        self.assertIn(self.course_slug, location)
        self.assertIn("player=1", location)

        # Verify enrollment
        enrollment = Enrollment.get_by_user_course(user.id, self.course.id)
        self.assertIsNotNone(enrollment, "Authenticated user must be enrolled immediately.")

    # -------------------------------------------------------------------------
    # 6. Course Detail Page ?start=1 / ?enrol=1 Auto-Enrollment
    # -------------------------------------------------------------------------
    def test_06_course_detail_start_param_auto_enrolls(self):
        """Authenticated student navigating to course_detail with ?start=1 is auto-enrolled."""
        test_email = "test_r1_query_start@skillrock.org"
        user = User.create(email=test_email, name="Query Start Student")
        user.set_password("Password123!")
        user.save()

        self.client.post("/login", data={"email": test_email, "password": "Password123!"})

        # Not enrolled yet
        self.assertIsNone(Enrollment.get_by_user_course(user.id, self.course.id))

        res = self.client.get(f"/learning/courses/{self.course_slug}?start=1")
        self.assertEqual(res.status_code, 200)

        # Verify auto-enrolled
        enrollment = Enrollment.get_by_user_course(user.id, self.course.id)
        self.assertIsNotNone(enrollment, "Student must be auto-enrolled when landing with ?start=1")

    # -------------------------------------------------------------------------
    # 7. Unauthenticated Visitor Restricted Content Protection
    # -------------------------------------------------------------------------
    def test_07_unauthenticated_cannot_stream_restricted_lessons(self):
        """Anonymous visitor to course detail page cannot access active YouTube stream player."""
        res = self.client.get(f"/learning/courses/{self.course_slug}")
        self.assertEqual(res.status_code, 200)
        html = res.get_data(as_text=True)

        # Check for locked content overlay
        self.assertIn("Restricted Course Content", html)
        self.assertIn("Start Learning", html)

        # Ensure active player script and slot are NOT present for unauthenticated visitors
        self.assertNotIn('initYouTubePlayer()', html)
        self.assertNotIn('youtube.com/iframe_api', html)
        self.assertNotIn('id="skillrockYtPlayer"', html)

    # -------------------------------------------------------------------------
    # 8. Authenticated Student Can Access Player
    # -------------------------------------------------------------------------
    def test_08_authenticated_student_can_view_player(self):
        """Authenticated enrolled student can view full learning player container and script."""
        test_email = "test_r1_player_access@skillrock.org"
        user = User.create(email=test_email, name="Player Access Student")
        user.set_password("Password123!")
        user.save()

        self.client.post("/login", data={"email": test_email, "password": "Password123!"})

        res = self.client.get(f"/learning/courses/{self.course_slug}")
        self.assertEqual(res.status_code, 200)
        html = res.get_data(as_text=True)
        self.assertIn('id="skillrockYtPlayer"', html)
        self.assertIn('youtube.com/iframe_api', html)
        self.assertIn('initYouTubePlayer()', html)

    # -------------------------------------------------------------------------
    # 9. Open Redirect Vulnerability Prevention
    # -------------------------------------------------------------------------
    def test_09_open_redirect_defense(self):
        """Malicious external next URLs must be safely rejected and fall back to internal routes."""
        test_email = "test_r1_redirect_defense@skillrock.org"
        user = User.create(email=test_email, name="Redirect Defense")
        user.set_password("Password123!")
        user.save()

        malicious_urls = [
            "https://attacker-phishing.com/steal-credentials",
            "//attacker-phishing.com",
            "/\\attacker-phishing.com"
        ]

        for bad_url in malicious_urls:
            res = self.client.post("/login", data={
                "email": test_email,
                "password": "Password123!",
                "next": bad_url
            }, follow_redirects=False)

            self.assertEqual(res.status_code, 302)
            location = res.headers.get("Location", "")
            self.assertFalse(location.startswith("https://attacker-phishing.com"))
            self.assertFalse(location.startswith("//attacker-phishing.com"))
            self.assertTrue(location.startswith("/") or "localhost" in location)

    # -------------------------------------------------------------------------
    # 10. Idempotent Enrollment (Duplicate-Safe & Progress Preserved)
    # -------------------------------------------------------------------------
    def test_10_idempotent_enrollment_preserves_progress(self):
        """Triggering enrollment multiple times must not crash or reset existing watch progress."""
        test_email = "test_r1_idempotent@skillrock.org"
        user = User.create(email=test_email, name="Idempotent Student")
        user.set_password("Password123!")
        user.save()

        self.client.post("/login", data={"email": test_email, "password": "Password123!"})

        # Pre-seed enrollment with 55% progress
        enrollment = Enrollment({
            "user_id": str(user.id),
            "course_id": str(self.course.id),
            "status": "in_progress",
            "watch_percent": 55,
            "watch_seconds": 1980,
            "max_watch_seconds": 1980,
            "video_duration": 3600
        })
        enrollment.save()

        # Trigger start endpoint again
        res = self.client.get(f"/learning/courses/{self.course_slug}/start", follow_redirects=False)
        self.assertEqual(res.status_code, 302)

        # Ensure exactly one enrollment document exists and progress is preserved
        count = self.db.enrollments.count_documents({"user_id": str(user.id), "course_id": str(self.course.id)})
        self.assertEqual(count, 1)

        refreshed = Enrollment.get_by_user_course(user.id, self.course.id)
        self.assertEqual(refreshed.watch_percent, 55, "Existing watch progress must not be overwritten.")

    # -------------------------------------------------------------------------
    # 11. Course Resolution by Slug and ObjectId
    # -------------------------------------------------------------------------
    def test_11_course_resolution_by_slug_and_id(self):
        """Course start endpoint must resolve course whether accessed by slug or ObjectId."""
        test_email = "test_r1_resolve@skillrock.org"
        user = User.create(email=test_email, name="Resolve Student")
        user.set_password("Password123!")
        user.save()

        self.client.post("/login", data={"email": test_email, "password": "Password123!"})

        # By slug
        res_slug = self.client.get(f"/learning/courses/{self.course.slug}/start")
        self.assertEqual(res_slug.status_code, 302)

        # By ObjectId
        res_id = self.client.get(f"/learning/courses/{self.course.id}/start")
        self.assertEqual(res_id.status_code, 302)


if __name__ == "__main__":
    unittest.main()
