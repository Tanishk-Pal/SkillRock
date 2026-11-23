"""
SkillRock — Bhavishya 1.0 Automated Test Suite
Validates:
1. Model persistence & MongoDB seeding for all 19 Bhavishya subjects.
2. Student progress tracking, streak counter, and persistent Socratic memory.
3. Protected classroom gating & ₹299 unlock verification.
4. Isolated Python code execution sandbox & security blocking.
5. Socratic AI teacher conversation loop & Fair-Usage limits.
6. 5-Round Placement Simulator scoring & readiness rubric.
7. 50% Completion Cashback claim workflow.
8. Backward compatibility with existing courses, roadmaps, and checkout.
"""

import unittest
from unittest.mock import patch
from datetime import datetime, timezone
from app import create_app
from config import Config
from models import (
    get_db,
    User,
    BhavishyaPackage,
    BhavishyaSubject,
    BhavishyaProgress,
    BhavishyaMemory,
    BhavishyaSimulatorAttempt,
    BhavishyaCashback,
    BhavishyaUsage,
    ensure_default_bhavishya_subjects,
)
from services.payment_service import grant_student_access, verify_student_unlock


class BhavishyaPlatformTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Config.TESTING = True
        Config.WTF_CSRF_ENABLED = False
        cls.app = create_app(Config)
        cls.app.config["TESTING"] = True
        cls.client = cls.app.test_client()
        cls.db = get_db()
        ensure_default_bhavishya_subjects()

    def setUp(self):
        self.client = self.app.test_client()
        User._user_cache.clear()
        self.db = get_db()

        # Seed test student
        ts = int(datetime.now().timestamp() * 1000)
        self.student_email = f"bhavishya_tester_{ts}@skillrock.edu"
        self.student = User({
            "name": "Aarav Developer",
            "email": self.student_email,
            "role": "student"
        })
        self.student.set_password("SecurePassword123!")
        self.student.save()

        self.admin_email = f"bhavishya_admin_{ts}@skillrock.edu"
        self.admin = User({
            "name": "Super Admin",
            "email": self.admin_email,
            "role": "admin"
        })
        self.admin.set_password("AdminPassword123!")
        self.admin.save()

    def tearDown(self):
        with self.client.session_transaction() as sess:
            sess.clear()
        if hasattr(self, "student_email"):
            self.db.users.delete_many({"email": {"$in": [self.student_email, self.admin_email]}})
        if hasattr(self, "student") and self.student.id:
            self.db.bhavishya_progress.delete_many({"user_id": str(self.student.id)})
            self.db.bhavishya_cashback.delete_many({"user_id": str(self.student.id)})
            self.db.user_access.delete_many({"user_id": str(self.student.id)})

    def login_student(self):
        with self.client.session_transaction() as sess:
            sess['_user_id'] = str(self.student.id)
            sess['_fresh'] = True

    def login_admin(self):
        with self.client.session_transaction() as sess:
            sess['_user_id'] = str(self.admin.id)
            sess['_fresh'] = True

    # ==========================================================================
    # 1. Seeding and 19-Subject Verification
    # ==========================================================================

    def test_01_ensure_19_subjects_seeded(self):
        """Verifies all 19 Bhavishya subjects across 3 categories are seeded in MongoDB."""
        ensure_default_bhavishya_subjects()
        all_subjects = BhavishyaSubject.get_all(published_only=False)
        self.assertGreaterEqual(len(all_subjects), 19)

        tech_subjects = BhavishyaSubject.get_by_category(BhavishyaSubject.CATEGORY_TECHNICAL)
        placement_subjects = BhavishyaSubject.get_by_category(BhavishyaSubject.CATEGORY_PLACEMENT)
        project_subjects = BhavishyaSubject.get_by_category(BhavishyaSubject.CATEGORY_PROJECTS)

        self.assertGreaterEqual(len(tech_subjects), 8)
        self.assertGreaterEqual(len(placement_subjects), 6)
        self.assertGreaterEqual(len(project_subjects), 5)

        # Check Python subject
        py_subj = BhavishyaSubject.get_by_slug("python-programming")
        self.assertIsNotNone(py_subj)
        self.assertIn("Python Programming", py_subj.title)
        self.assertGreater(py_subj.total_lessons_count, 5)

    # ==========================================================================
    # 2. Package Pricing & Unlocking
    # ==========================================================================

    def test_02_bhavishya_package_pricing(self):
        """Verifies Bhavishya 1.0 package is 100% free for all students."""
        pkg = BhavishyaPackage()
        self.assertEqual(pkg.price, 0.0)
        self.assertFalse(pkg.is_paid)

    def test_03_access_gating_and_unlock(self):
        """Verifies Bhavishya is 100% free and accessible."""
        self.assertTrue(verify_student_unlock(self.admin, "bhavishya", "bhavishya-1-0"))

    # ==========================================================================
    # 3. Routes & UI Rendering
    # ==========================================================================

    def test_04_dashboard_route_renders(self):
        """Verifies /bhavishya dashboard renders HTTP 200 with all cards."""
        resp = self.client.get("/bhavishya", follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        body = resp.data.decode("utf-8")
        self.assertIn("Bhavishya 1.0", body)
        self.assertIn("Python Mastery", body)
        self.assertIn("English", body)
        self.assertIn("Let's Study", body)

    def test_05_roadmap_route_renders(self):
        """Verifies /bhavishya/roadmap renders HTTP 200 with 6 phases."""
        resp = self.client.get("/bhavishya/roadmap", follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        body = resp.data.decode("utf-8")
        self.assertIn("24-Week", body)
        self.assertIn("Phase 1: Foundations", body)
        self.assertIn("Phase 6: Recruitment Arena", body)

    def test_06_subject_detail_renders(self):
        """Verifies /bhavishya/subject/python renders HTTP 200 with full chapters."""
        resp = self.client.get("/bhavishya/subject/python", follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        body = resp.data.decode("utf-8")
        self.assertIn("All Chapters", body)
        self.assertIn("Live Lecture", body)

    # ==========================================================================
    # 4. AI Classroom Gating & Interaction
    # ==========================================================================

    def test_07_classroom_access_gating(self):
        """Verifies students have 100% free access to classroom lessons."""
        self.login_student()

        # Unlocked student: loads classroom directly without paywall
        resp = self.client.get("/bhavishya/learn/python-programming/py-l1")
        self.assertEqual(resp.status_code, 200)
        body = resp.data.decode("utf-8")
        self.assertIn("100% Free Access", body)
        self.assertIn("Conceptual Notes & Breakdown", body)
        self.assertIn("Try It Yourself — Interactive Lab", body)
        self.assertIn("Ski Assistant", body)

    @patch("routes.bhavishya.call_bhavishya_gemini", return_value="Great question! Variables in Python act like labels attached to memory objects.")
    def test_08_ai_teacher_interaction_api(self, mock_gemini):
        """Verifies /bhavishya/api/ai-teacher/interact processes student question and records memory."""
        self.login_student()
        grant_student_access(self.student.id, "bhavishya", "bhavishya-1-0")

        resp = self.client.post("/bhavishya/api/ai-teacher/interact", json={
            "subject_slug": "python-programming",
            "lesson_id": "py-l1",
            "message": "I am confused about why variables are pointers in Python.",
            "mode": "classroom",
            "language": "english"
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data.get("status"), "success")
        self.assertTrue(len(data.get("reply", "")) > 10)

        # Verify persistent memory updated with confusion
        mem = BhavishyaMemory.get_for_user_and_subject(str(self.student.id), "python-programming")
        self.assertIsNotNone(mem)
        self.assertTrue(len(mem.weak_concepts) > 0)

    # ==========================================================================
    # 5. Secure Python Sandbox Execution
    # ==========================================================================

    def test_09_sandbox_runs_valid_code(self):
        """Verifies safe Python code executes and returns stdout in milliseconds."""
        self.login_student()

        code = "print(sum([x * 2 for x in range(5)]))"
        resp = self.client.post("/bhavishya/api/code/run", json={"code": code})
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data.get("status"), "success")
        self.assertIn("20", data.get("stdout"))
        self.assertGreaterEqual(data.get("execution_time_ms", 0), 0)

    def test_10_sandbox_blocks_security_hazards(self):
        """Verifies dangerous modules (import os, subprocess) are rejected by security gate."""
        self.login_student()

        malicious_code = "import os\nos.system('echo hacked')"
        resp = self.client.post("/bhavishya/api/code/run", json={"code": malicious_code})
        self.assertEqual(resp.status_code, 400)
        data = resp.get_json()
        self.assertEqual(data.get("status"), "security_block")
        self.assertIn("restricted", data.get("stderr"))

    # ==========================================================================
    # 6. Placement Simulator & 50% Cashback
    # ==========================================================================

    def test_11_placement_simulator_submission(self):
        """Verifies 5-round scores generate cumulative placement readiness metrics."""
        self.login_student()
        grant_student_access(self.student.id, "bhavishya", "bhavishya-1-0")

        scores = {
            "aptitude": 85,
            "coding": 90,
            "gd": 75,
            "technical": 85,
            "hr": 80
        }
        resp = self.client.post("/bhavishya/api/simulator/submit", json={"scores": scores})
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data.get("status"), "success")
        self.assertGreaterEqual(data.get("overall_score"), 80)
        self.assertEqual(data.get("readiness_status"), "Placement Ready")

    def test_12_cashback_claim_flow(self):
        """Verifies 50% cashback claim form persists with under_verification status."""
        self.login_student()

        resp = self.client.post("/bhavishya/cashback/claim", data={
            "upi_id": "aarav.dev@okaxis"
        }, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)

        record = BhavishyaCashback.get_by_user(str(self.student.id))
        self.assertIsNotNone(record)
        self.assertEqual(record.upi_id, "aarav.dev@okaxis")
        self.assertEqual(record.status, BhavishyaCashback.STATUS_UNDER_VERIFICATION)
        self.assertEqual(record.cashback_amount, 149.50)

    # ==========================================================================
    # 7. Bhavishya Payment Gateway Checkout & Ski Companion Tests
    # ==========================================================================

    def test_13_bhavishya_checkout_screen_loads(self):
        """Verifies Bhavishya 1.0 is 100% free: checkout redirects directly to free enrollment and unlocks."""
        self.login_student()

        resp = self.client.get("/payment/checkout/bhavishya/bhavishya-1-0", follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        body = resp.data.decode("utf-8")
        self.assertIn("Bhavishya 1.0", body)
        self.assertIn("100% Free", body)

    def test_14_ski_bot_hub_and_api(self):
        """Verifies Ski Grok-style companion hub renders and chat/quote endpoints respond with high motivation."""
        self.login_student()

        # 1. Fullscreen Hub
        resp = self.client.get("/ski")
        self.assertEqual(resp.status_code, 200)
        body = resp.data.decode("utf-8")
        self.assertIn("Meet Ski", body)
        self.assertIn("Grok", body)

        # 2. Ski Chat API
        chat_resp = self.client.post("/api/ski/chat", json={
            "message": "Hey Ski, hype me up for coding!",
            "mood": "hype"
        })
        self.assertEqual(chat_resp.status_code, 200)
        data = chat_resp.get_json()
        self.assertTrue(data.get("success"))
        self.assertEqual(data.get("bot_name"), "Ski")
        self.assertTrue(len(data.get("reply", "")) > 5)

        # 3. Ski Quote API
        quote_resp = self.client.get("/api/ski/quote?mood=roast")
        self.assertEqual(quote_resp.status_code, 200)
        qdata = quote_resp.get_json()
        self.assertTrue(qdata.get("success"))
        self.assertTrue(len(qdata.get("quote", "")) > 10)

    # ==========================================================================
    # 8. Faculty & Teacher Role Management Tests
    # ==========================================================================

    def test_15_admin_teacher_assignment_and_privileges(self):
        """Verifies Super Admin can appoint teacher by email and teacher can access course/bhavishya admin consoles."""
        ts = int(datetime.now().timestamp() * 1000)
        faculty_email = f"lead_faculty_{ts}@skillrock.edu"
        candidate = User({
            "name": "Dr. Ramanujan",
            "email": faculty_email,
            "role": "student"
        })
        candidate.set_password("FacultyPass123!")
        candidate.save()

        # 1. Non-teacher student cannot access admin console
        self.login_student()
        resp = self.client.get("/admin/bhavishya")
        self.assertIn(resp.status_code, [302, 403])

        # 2. Admin assigns teacher via email
        self.login_admin()
        get_resp = self.client.get("/admin/teachers")
        self.assertEqual(get_resp.status_code, 200)

        assign_resp = self.client.post("/admin/teachers/assign", data={
            "email": faculty_email,
            "teacher_title": "Lead Python Faculty"
        }, follow_redirects=True)
        self.assertEqual(assign_resp.status_code, 200)

        # 3. Verify user model privileges
        updated_faculty = User.get_by_id(str(candidate.id))
        self.assertTrue(updated_faculty.is_teacher)
        self.assertEqual(updated_faculty.role, "teacher")
        self.assertTrue(updated_faculty.can_manage_courses)

        # 4. Teacher logs in and accesses Bhavishya and Courses admin consoles
        with self.client.session_transaction() as sess:
            sess['_user_id'] = str(candidate.id)
            sess['_fresh'] = True

        teach_bhavishya_resp = self.client.get("/admin/bhavishya")
        self.assertEqual(teach_bhavishya_resp.status_code, 200)

        teach_courses_resp = self.client.get("/admin/courses")
        self.assertEqual(teach_courses_resp.status_code, 200)

        # 5. Clean up
        self.db.users.delete_one({"_id": candidate._id})
        self.db.authorized_teachers.delete_one({"email": faculty_email.lower().strip()})



if __name__ == "__main__":
    unittest.main()
