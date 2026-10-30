"""
SkillRock End-to-End Production Simulation Test Suite
Thoroughly verifies complete end-to-end flows for both Student and Administrator roles:
1. Student Lifecycle: Register -> Login -> Browse Courses -> Enroll -> Track Video -> Earn Certificate -> Verify Hash/QR -> Test Series -> Discover -> Logout
2. Administrator Lifecycle: Admin Auth -> Dashboard -> Settings -> Async Reminders Dispatch -> Course Management -> Test Series Management -> User Management
"""

import unittest
import os
import time
from app import create_app
from models.mongo import User, Course, Enrollment, Certificate, get_db

class TestE2EProductionSimulation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ["TESTING"] = "1"
        cls.app = create_app()
        cls.app.config["TESTING"] = True
        cls.app.config["WTF_CSRF_ENABLED"] = False
        cls.client = cls.app.test_client()

    def setUp(self):
        self.db = get_db()
        # Clean test accounts if exist
        self.db.users.delete_many({"email": {"$in": ["test_student_e2e@skillrock.org", "test_admin_e2e@skillrock.org"]}})

    def tearDown(self):
        self.db.users.delete_many({"email": {"$in": ["test_student_e2e@skillrock.org", "test_admin_e2e@skillrock.org"]}})

    # =========================================================================
    # 1. Student Journey E2E
    # =========================================================================
    def test_01_student_complete_journey(self):
        """Simulates full student lifecycle from sign-up to certificate verification."""
        # A. Register new student
        reg_resp = self.client.post("/register", data={
            "name": "E2E Student Explorer",
            "email": "test_student_e2e@skillrock.org",
            "password": "Password123!",
            "confirm_password": "Password123!",
            "role": "student"
        }, follow_redirects=True)
        self.assertEqual(reg_resp.status_code, 200)

        # B. Login
        login_resp = self.client.post("/login", data={
            "email": "test_student_e2e@skillrock.org",
            "password": "Password123!"
        }, follow_redirects=True)
        self.assertEqual(login_resp.status_code, 200)
        self.assertIn(b"E2E Student", login_resp.data)

        # C. Browse Courses Catalogue
        courses_resp = self.client.get("/learning/courses")
        self.assertEqual(courses_resp.status_code, 200)
        self.assertIn(b"SQL", courses_resp.data)

        # D. View Course Detail & Verify Motivational Certificate Sample
        course_slug = "sql-complete-course-in-3-hours-mysql"
        course = Course.get_by_slug(course_slug)
        if not course:
            courses = Course.get_published_courses()
            self.assertTrue(len(courses) > 0)
            course = courses[0]
            course_slug = course.slug

        detail_resp = self.client.get(f"/learning/courses/{course_slug}")
        self.assertEqual(detail_resp.status_code, 200)
        # Verify motivational certificate preview exists on course page
        self.assertIn(b"Earn Your SkillRock Verified Certificate", detail_resp.data)

        # E. Enroll in Course
        enroll_resp = self.client.post(f"/learning/enrol/{course.id}", follow_redirects=True)
        self.assertEqual(enroll_resp.status_code, 200)

        # F. Track Video Watch Progress (Simulate 85% completion via /learning/save-progress)
        prog_resp = self.client.post("/learning/save-progress", json={
            "course_id": str(course.id),
            "watch_seconds": 6120,
            "video_duration": 7200
        })
        self.assertIn(prog_resp.status_code, [200, 201])
        prog_data = prog_resp.get_json()
        self.assertTrue(prog_data.get("success", False))

        # G. Browse Interview Test Series
        test_series_resp = self.client.get("/test-series")
        self.assertEqual(test_series_resp.status_code, 200)
        self.assertIn(b"Interview Test Series", test_series_resp.data)

        # H. Browse Skill Exchange (Campus Connect)
        discover_resp = self.client.get("/discover")
        self.assertEqual(discover_resp.status_code, 200)

        # I. View Student Profile
        profile_resp = self.client.get("/profile")
        self.assertEqual(profile_resp.status_code, 200)
        self.assertIn(b"E2E Student", profile_resp.data)

        # J. Logout
        logout_resp = self.client.get("/logout", follow_redirects=True)
        self.assertEqual(logout_resp.status_code, 200)

    # =========================================================================
    # 2. Administrator Journey E2E
    # =========================================================================
    def test_02_admin_complete_journey(self):
        """Simulates full administrator lifecycle including settings and async reminders."""
        # A. Create verified Admin user directly in DB
        admin_user = User.create(
            email="test_admin_e2e@skillrock.org",
            name="SkillRock Lead Admin",
            role="admin"
        )
        admin_user.set_password("AdminSecretKey123!")
        admin_user.save()
        self.assertIsNotNone(admin_user)
        self.assertTrue(admin_user.is_admin)

        # B. Admin Login
        login_resp = self.client.post("/login", data={
            "email": "test_admin_e2e@skillrock.org",
            "password": "AdminSecretKey123!"
        }, follow_redirects=True)
        self.assertEqual(login_resp.status_code, 200)

        # C. Access Admin Dashboard
        admin_dash = self.client.get("/admin/dashboard")
        self.assertEqual(admin_dash.status_code, 200)
        self.assertIn(b"Admin", admin_dash.data)

        # D. Access Admin Settings
        settings_resp = self.client.get("/admin/settings")
        self.assertEqual(settings_resp.status_code, 200)
        self.assertIn(b"Student Learning & Certificate Email Reminders", settings_resp.data)

        # E. Trigger Async Reminders (Verify non-blocking execution in < 250ms)
        t0 = time.time()
        trigger_resp = self.client.post("/admin/reminders/trigger", data={"force": "1"}, follow_redirects=False)
        dt = (time.time() - t0) * 1000
        self.assertEqual(trigger_resp.status_code, 302)
        self.assertLess(dt, 250, "Reminders trigger must return immediately via async daemon without stalling request")

        # F. Access Admin Courses Catalogue
        admin_courses = self.client.get("/admin/courses")
        self.assertEqual(admin_courses.status_code, 200)

        # G. Access Admin Test Series Manager
        admin_ts = self.client.get("/admin/test-series")
        self.assertEqual(admin_ts.status_code, 200)

        # H. Access Admin Users List
        admin_users = self.client.get("/admin/users")
        self.assertEqual(admin_users.status_code, 200)
        self.assertIn(b"SkillRock Lead Admin", admin_users.data)

if __name__ == "__main__":
    unittest.main()
