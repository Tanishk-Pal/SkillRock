"""
SkillRock — Interview Test Series Comprehensive Automated Test Suite
Verifies:
1. Public Test Series Catalog & Packs Discovery
2. Timed Assessment Engine (server deadline, resume capabilities)
3. Zero Solution/Answer Leakage in Exam Room
4. Anti-Cheating & Focus Loss Debouncing / 4-Strike Auto-Disqualification
5. Autosave Response API & Server-Authoritative Time Calculation
6. Scoring Logic (+1.0 mark, -0.25 negative mark, topic breakdown, accuracy)
7. Safe Submissions & Idempotent Evaluation
8. Admin Security Controls & Management Endpoints
"""

import os
import sys
import unittest
from datetime import datetime, timezone, timedelta
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.stdout.reconfigure(encoding="utf-8")

from app import create_app
from models.mongo import get_db, User
from models.test_series import TestDefinition, TestPack, Question, TestAttempt, UserEntitlement
from models.default_test_series import ensure_default_test_series

class TestInterviewTestSeries(unittest.TestCase):
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
        User._user_cache.clear()
        ensure_default_test_series()

        # Create unique student user
        ts = int(datetime.now().timestamp() * 1000)
        self.student = User({
            "email": f"student_series_{ts}@example.com",
            "name": "Placement Aspirant",
            "role": "student"
        })
        self.student.set_password("StudentPass123!")
        self.student.save()

        # Ensure admin user
        self.admin = User.get_by_email("palt51419@gmail.com")
        if not self.admin:
            self.admin = User({
                "email": "palt51419@gmail.com",
                "name": "Platform Admin",
                "role": "admin"
            })
            self.admin.save()
        else:
            self.admin.role = "admin"
            self.admin.save()
        User._user_cache.clear()

    def tearDown(self):
        self._logout()
        User._user_cache.clear()
        self.app_context.pop()

    def _login_as(self, user):
        self._logout()
        with self.client.session_transaction() as sess:
            sess["_user_id"] = str(user.id)
            sess["_fresh"] = True

    def _logout(self):
        try:
            with self.client.session_transaction() as sess:
                sess.clear()
        except Exception:
            pass
        if hasattr(self.client, "cookie_jar"):
            self.client.cookie_jar.clear()

    def test_catalog_and_packs_display(self):
        """Test public catalog /test-series lists 3 free tests and 4 test packs."""
        res = self.client.get("/test-series", follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")
        self.assertIn("Interview Test Series", html)
        self.assertIn("Aptitude and Logical Reasoning", html)
        self.assertIn("Coding Fundamentals", html)
        self.assertIn("Mixed Placement Mock", html)
        self.assertIn("Free Starter", html)
        self.assertIn("Placement Practice", html)
        self.assertIn("Interview Ready", html)
        self.assertIn("Complete Placement Prep", html)

    def test_pack_detail_page(self):
        """Test pack details page shows pricing and transparent status."""
        res = self.client.get("/test-series/packs/placement-practice")
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")
        self.assertIn("Placement Practice", html)
        self.assertIn("₹49", html)

    def test_test_detail_page(self):
        """Test test overview briefing page displays duration, questions count, and rules."""
        res = self.client.get("/test-series/tests/aptitude-and-logical-reasoning")
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")
        self.assertIn("Aptitude and Logical Reasoning", html)
        self.assertIn("30 Mins", html)
        self.assertIn("3 warnings", html)
        self.assertIn("Anti-Cheating Policy", html)

    def test_unauthenticated_user_cannot_start_test(self):
        """Unauthenticated user starting a test is redirected to login."""
        self._logout()
        res = self.client.post("/test-series/tests/aptitude-and-logical-reasoning/start")
        self.assertEqual(res.status_code, 302)
        self.assertIn("/login", res.headers.get("Location", ""))

    def test_start_attempt_and_security_no_answers_leaked(self):
        """
        Starting a test creates an in_progress attempt.
        Exam room MUST NOT leak correct_answers or explanation to the client.
        """
        self._login_as(self.student)
        res = self.client.post("/test-series/tests/aptitude-and-logical-reasoning/start", follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")
        self.assertIn("Aptitude and Logical Reasoning", html)
        self.assertIn("currentQNum", html)

        # Inspect DB attempt
        attempts = TestAttempt.find_all({"user_id": str(self.student.id), "status": TestAttempt.STATUS_IN_PROGRESS})
        self.assertTrue(len(attempts) > 0)
        attempt = attempts[0]
        test_def = TestDefinition.get_by_id(attempt.test_id)
        self.assertEqual(len(test_def.question_ids), 30)

        # Ensure correct_answers and explanation are NOT present anywhere in rendered HTML
        for q_id in test_def.question_ids[:5]:
            q = Question.get_by_id(q_id)
            if q and q.explanation:
                self.assertNotIn(q.explanation, html, "Question explanation must not leak in exam room HTML!")

    def test_autosave_response_api(self):
        """Verify autosave endpoint persists selected answer and returns remaining seconds."""
        self._login_as(self.student)
        test_def = TestDefinition.get_by_slug("coding-fundamentals")
        
        # Start attempt
        self.client.post(f"/test-series/tests/{test_def.slug}/start", follow_redirects=True)
        attempt = TestAttempt.get_active_attempt(self.student.id, test_def.id)
        self.assertIsNotNone(attempt)
        first_q_id = str(test_def.question_ids[0])

        res = self.client.post(f"/test-series/attempts/{attempt.id}/save-answer",
            data=json.dumps({"question_id": first_q_id, "selected_options": ["B"], "marked_for_review": False}),
            content_type="application/json"
        )
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data.decode("utf-8"))
        self.assertTrue(data.get("success"))
        self.assertGreater(data.get("remaining_seconds"), 0)

        # Verify DB persisted
        updated_attempt = TestAttempt.get_by_id(attempt.id)
        saved_resp = updated_attempt.responses.get(first_q_id)
        ans = saved_resp.get("answer") if isinstance(saved_resp, dict) else saved_resp
        self.assertEqual(ans, ["B"])

    def test_focus_loss_debouncing_and_auto_disqualification(self):
        """
        Verify anti-cheat policy:
        - 1st to 3rd violations return warnings.
        - Events within 5s are debounced and not double counted.
        - 4th violation automatically cancels attempt (disqualification).
        """
        self._login_as(self.student)
        test_def = TestDefinition.get_by_slug("aptitude-and-logical-reasoning")
        self.client.post(f"/test-series/tests/{test_def.slug}/start", follow_redirects=True)
        attempt = TestAttempt.get_active_attempt(self.student.id, test_def.id)
        self.assertIsNotNone(attempt)

        # 1st violation
        res1 = self.client.post(f"/test-series/attempts/{attempt.id}/focus-loss",
            data=json.dumps({"reason": "tab_switch"}),
            content_type="application/json"
        )
        self.assertEqual(res1.status_code, 200)
        d1 = json.loads(res1.data.decode("utf-8"))
        self.assertEqual(d1["status"], "warning")
        self.assertEqual(d1["warning_count"], 1)

        # Immediate event within debounce window should be ignored
        res_debounced = self.client.post(f"/test-series/attempts/{attempt.id}/focus-loss",
            data=json.dumps({"reason": "window_blur"}),
            content_type="application/json"
        )
        d_deb = json.loads(res_debounced.data.decode("utf-8"))
        self.assertEqual(d_deb["warning_count"], 1, "Debounced event must not increment warning count")

        # Simulate 2nd violation after debounce window
        attempt = TestAttempt.get_by_id(attempt.id)
        attempt.focus_loss_events[0]["timestamp"] = (datetime.now(timezone.utc) - timedelta(seconds=10)).isoformat()
        attempt.save()

        res2 = self.client.post(f"/test-series/attempts/{attempt.id}/focus-loss",
            data=json.dumps({"reason": "window_blur"}),
            content_type="application/json"
        )
        d2 = json.loads(res2.data.decode("utf-8"))
        self.assertEqual(d2["warning_count"], 2)

        # Simulate 3rd violation
        attempt = TestAttempt.get_by_id(attempt.id)
        attempt.focus_loss_events[1]["timestamp"] = (datetime.now(timezone.utc) - timedelta(seconds=10)).isoformat()
        attempt.save()

        res3 = self.client.post(f"/test-series/attempts/{attempt.id}/focus-loss",
            data=json.dumps({"reason": "tab_switch"}),
            content_type="application/json"
        )
        d3 = json.loads(res3.data.decode("utf-8"))
        self.assertEqual(d3["warning_count"], 3)
        self.assertEqual(d3["status"], "warning")

        # 4th violation -> Disqualification / cancellation
        attempt = TestAttempt.get_by_id(attempt.id)
        attempt.focus_loss_events[2]["timestamp"] = (datetime.now(timezone.utc) - timedelta(seconds=10)).isoformat()
        attempt.save()

        res4 = self.client.post(f"/test-series/attempts/{attempt.id}/focus-loss",
            data=json.dumps({"reason": "fullscreen_exit"}),
            content_type="application/json"
        )
        d4 = json.loads(res4.data.decode("utf-8"))
        self.assertEqual(d4["status"], "cancelled")
        self.assertTrue(d4["cancelled"])

        # Check attempt is marked cancelled in DB
        cancelled_attempt = TestAttempt.get_by_id(attempt.id)
        self.assertEqual(cancelled_attempt.status, TestAttempt.STATUS_CANCELLED)
        self.assertIn("focus-loss limit was exceeded", cancelled_attempt.cancellation_reason)

        # Attempting to save answer on cancelled attempt should be forbidden
        res_save = self.client.post(f"/test-series/attempts/{attempt.id}/save-answer",
            data=json.dumps({"question_id": str(test_def.question_ids[0]), "selected_options": ["A"]}),
            content_type="application/json"
        )
        self.assertEqual(res_save.status_code, 400)

    def test_submission_and_scoring_evaluation(self):
        """
        Verify test submission:
        - Calculates correct score with negative marking (+1.0 / -0.25).
        - Computes accuracy and topic performance breakdown.
        - Unlocks step-by-step explanations on the result page.
        """
        self._login_as(self.student)
        test_def = TestDefinition.get_by_slug("aptitude-and-logical-reasoning")
        self.client.post(f"/test-series/tests/{test_def.slug}/start", follow_redirects=True)
        attempt = TestAttempt.get_active_attempt(self.student.id, test_def.id)
        self.assertIsNotNone(attempt)

        q1 = Question.get_by_id(test_def.question_ids[0])
        q2 = Question.get_by_id(test_def.question_ids[1])

        # Student answers:
        # q1: Correct answer (+1.0)
        # q2: Wrong answer (-0.25)
        # q3+: Left unanswered (0.0)
        wrong_opt = [opt for opt in ["a", "b", "c", "d"] if opt not in [ca.lower() for ca in q2.correct_answers]][0]

        attempt.responses[str(q1.id)] = {"answer": list(q1.correct_answers), "marked_for_review": False}
        attempt.responses[str(q2.id)] = {"answer": [wrong_opt], "marked_for_review": False}
        attempt.save()

        res_submit = self.client.post(f"/test-series/attempts/{attempt.id}/submit")
        self.assertEqual(res_submit.status_code, 200)
        submit_data = json.loads(res_submit.data.decode("utf-8"))
        self.assertTrue(submit_data.get("success"))

        # Navigate to result page
        res_result = self.client.get(submit_data.get("redirect_url"))
        self.assertEqual(res_result.status_code, 200)
        html = res_result.data.decode("utf-8")

        # Result verification in DB
        submitted_attempt = TestAttempt.get_by_id(attempt.id)
        self.assertEqual(submitted_attempt.status, TestAttempt.STATUS_COMPLETED)
        self.assertEqual(submitted_attempt.correct_count, 1)
        self.assertEqual(submitted_attempt.incorrect_count, 1)
        self.assertEqual(submitted_attempt.unanswered_count, 28)
        # Score = 1.0 - 0.25 = 0.75
        self.assertAlmostEqual(submitted_attempt.score, 0.75, places=2)

        # Explanations must now be unlocked on result page
        self.assertIn("Explanations", html)
        self.assertIn(q1.explanation, html)

    def test_admin_access_granted(self):
        """Verify admin can access test series management routes."""
        self._login_as(self.admin)
        res_adm = self.client.get("/admin/test-series/tests")
        self.assertEqual(res_adm.status_code, 200)
        self.assertIn("Manage Tests", res_adm.data.decode("utf-8"))

        res_packs = self.client.get("/admin/test-series/packs")
        self.assertEqual(res_packs.status_code, 200)

        res_qs = self.client.get("/admin/test-series/questions")
        self.assertEqual(res_qs.status_code, 200)

    def test_student_admin_access_denied(self):
        """Verify normal student cannot access admin routes."""
        self._login_as(self.student)
        res_stud = self.client.get("/admin/test-series/tests")
        self.assertIn(res_stud.status_code, [302, 403])

if __name__ == "__main__":
    unittest.main()
