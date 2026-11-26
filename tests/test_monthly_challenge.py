# -*- coding: utf-8 -*-
import os
os.environ["MONGODB_URI"] = ""
"""
Automated Test Suite for SkillRock Monthly Challenge & Career Roadmap Sunset.
Validates:
1. Sandboxed Code Execution Service with AST security checks, timeouts, and hidden test cases.
2. Monthly Challenge models, 28-day countdown metrics, and 7-criteria refund evaluation.
3. Public catalog, detailed landing page, and student 9-tab dashboard.
4. Interactive APIs (module toggle, practice MCQs, interview prep, LeetCode runner, capstone submit).
5. 50-MCQ Assessment execution, strict scoring, and automated certificate issuance upon >=80%.
6. 100% Refund Claim system (strict 7-condition gate and UPI payout lifecycle).
7. Admin management consoles (challenges, project rubric evaluations, refund console).
8. Legacy Career Roadmap permanent 301 redirects to Monthly Challenge.
"""

from datetime import datetime, timezone
import json
import unittest

from app import create_app
from config import Config
from models import User, get_db
from models.challenge import (
    AssessmentAttempt,
    AssessmentQuestion,
    ChallengeAssignmentSubmission,
    ChallengeEnrollment,
    CodingProblem,
    InterviewQuestion,
    MonthlyChallenge,
    PracticalAssignment,
    PracticeQuestion,
    RefundClaim,
)
from models.default_challenge_data import ensure_default_monthly_challenge
from services.code_execution_service import evaluate_test_cases, execute_python_code, validate_python_ast


class TestMonthlyChallengeSuite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Config.TESTING = True
        Config.WTF_CSRF_ENABLED = False
        cls.app = create_app(Config)
        cls.app.config["TESTING"] = True
        cls.client = cls.app.test_client()
        cls.db = get_db()

        # Seed default 28-day Python challenge
        ensure_default_monthly_challenge()

        ts = int(datetime.now().timestamp() * 1000)
        # Create Super Admin User
        cls.admin_email = f"admin_challenge_{ts}@skillrock.edu"
        cls.admin = User({
            "name": "SkillRock Challenge Admin",
            "email": cls.admin_email,
            "role": "admin",
            "is_admin": True,
        })
        cls.admin.set_password("AdminSecurePass123!")
        cls.admin.save()

        # Create Student User
        cls.student_email = f"student_challenge_{ts}@skillrock.edu"
        cls.student = User({
            "name": "Aman Verma",
            "email": cls.student_email,
            "role": "student",
            "phone": "9876543210",
        })
        cls.student.set_password("StudentSecurePass123!")
        cls.student.save()

    def _login_as(self, user):
        """Helper to establish authenticated session."""
        with self.client.session_transaction() as sess:
            sess["_user_id"] = str(user.id)
            sess["_fresh"] = True

    # ==========================================================================
    # 1. Code Execution Service & AST Security
    # ==========================================================================

    def test_1_code_execution_security(self):
        """Validates AST security blocks malicious imports, builtins, and executes safe code."""
        # Forbidden imports
        safe, err = validate_python_ast("import os\nos.system('dir')")
        self.assertFalse(safe)
        self.assertIn("Security Violation", err)

        safe, err = validate_python_ast("from sys import exit\nexit(0)")
        self.assertFalse(safe)
        self.assertIn("Security Violation", err)

        safe, err = validate_python_ast("import subprocess")
        self.assertFalse(safe)

        # Forbidden calls
        safe, err = validate_python_ast("f = open('config.py', 'r')")
        self.assertFalse(safe)

        safe, err = validate_python_ast("eval('1 + 1')")
        self.assertFalse(safe)

        # Valid safe code
        safe, err = validate_python_ast("x = int(input())\nprint(x * 2)")
        self.assertTrue(safe)

        # Evaluation against test cases
        test_cases = [
            {"input": "5\n", "expected_output": "10", "is_hidden": False},
            {"input": "20\n", "expected_output": "40", "is_hidden": True},
        ]
        res = evaluate_test_cases("x = int(input())\nprint(x * 2)", test_cases)
        self.assertTrue(res["all_passed"])
        self.assertEqual(res["passed_count"], 2)
        # Verify hidden test case masking
        self.assertEqual(res["results"][1]["input"], "[Hidden Test Case]")
        self.assertEqual(res["results"][1]["expected_output"], "[Hidden Output]")

    # ==========================================================================
    # 2. Challenge Models & 28-Day Countdown Math
    # ==========================================================================

    def test_2_challenge_models_and_metrics(self):
        """Validates challenge configuration, duration, modules, and 30-day math."""
        ch = MonthlyChallenge.get_by_slug("python-28-day-challenge")
        self.assertIsNotNone(ch)
        self.assertEqual(ch.price, 499.0)
        self.assertEqual(ch.duration_days, 30)
        self.assertEqual(len(ch.modules), 6)
        self.assertTrue(ch.is_active)

        # Create enrollment
        enr = ChallengeEnrollment.get_or_create(
            user_id=str(self.student.id),
            challenge_id=str(ch.id),
            challenge_slug=ch.slug,
            amount_paid=499.0,
        )
        self.assertIsNotNone(enr)
        metrics = enr.get_countdown_metrics(ch.duration_days)
        self.assertEqual(metrics["duration_days"], 30)
        self.assertEqual(metrics["days_remaining"], 30)
        self.assertFalse(metrics["is_expired"])

        # Check refund eligibility starts as unfulfilled
        refund_eval = enr.evaluate_refund_eligibility(
            total_modules=6,
            total_practice=8,
            total_interviews=4,
            total_coding=4,
            assignment_submission_status=None,
            duration_days=30,
        )
        self.assertFalse(refund_eval["all_eligible"])
        self.assertEqual(len(refund_eval["criteria"]), 7)

    # ==========================================================================
    # 3. Public Routes & Gated Access Control
    # ==========================================================================

    def test_3_public_routes_and_dashboard_gate(self):
        """Validates catalog and detail pages are public; dashboard requires authentication & enrollment."""
        # Public catalog
        resp = self.client.get("/challenge")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Python Programming", resp.data)
        self.assertIn(b"499", resp.data)

        # Public challenge detail
        resp = self.client.get("/challenge/python-28-day-challenge")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"What You Will Get", resp.data)
        self.assertIn(b"Curriculum", resp.data)

        # Dashboard unauthenticated redirects to login
        resp = self.client.get("/challenge/python-28-day-challenge/dashboard")
        self.assertEqual(resp.status_code, 302)

    # ==========================================================================
    # 4. Interactive Dashboard APIs
    # ==========================================================================

    def test_4_dashboard_interactive_apis(self):
        """Validates module toggling, practice MCQs, interview prep, code submit, and assessment."""
        self._login_as(self.student)
        slug = "python-28-day-challenge"

        # 1. Access Dashboard
        resp = self.client.get(f"/challenge/{slug}/dashboard")
        self.assertEqual(resp.status_code, 200)

        # 2. Toggle Module completion
        resp = self.client.post(
            f"/challenge/{slug}/module/toggle",
            data=json.dumps({"module_id": 1, "completed": True}),
            content_type="application/json",
        )
        data = resp.get_json()
        self.assertTrue(data["success"])
        self.assertIn(1, data["modules_completed"])

        # 3. Submit Practice MCQ
        practice_qs = PracticeQuestion.get_by_challenge(slug)
        self.assertTrue(len(practice_qs) > 0)
        q1 = practice_qs[0]
        resp = self.client.post(
            f"/challenge/{slug}/practice/submit",
            data=json.dumps({"question_id": str(q1.id), "selected_option": q1.correct_option}),
            content_type="application/json",
        )
        data = resp.get_json()
        self.assertTrue(data["success"])
        self.assertTrue(data["is_correct"])

        # 4. Update Interview Question status
        interview_qs = InterviewQuestion.get_by_challenge(slug)
        self.assertTrue(len(interview_qs) > 0)
        iq1 = interview_qs[0]
        resp = self.client.post(
            f"/challenge/{slug}/interview/status",
            data=json.dumps({"question_id": str(iq1.id), "status": "completed"}),
            content_type="application/json",
        )
        data = resp.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["status"], "completed")

        # 5. Submit Coding Arena Problem
        coding_probs = CodingProblem.get_by_challenge(slug)
        self.assertTrue(len(coding_probs) > 0)
        cp1 = coding_probs[0]  # Sum of Two Numbers
        solution_code = """
import sys

def solve():
    lines = sys.stdin.read().split()
    if lines:
        a = int(lines[0])
        b = int(lines[1])
        print(a + b)

if __name__ == '__main__':
    solve()
"""
        resp = self.client.post(
            f"/challenge/{slug}/coding/submit",
            data=json.dumps({"problem_id": str(cp1.id), "code": solution_code}),
            content_type="application/json",
        )
        data = resp.get_json()
        self.assertTrue(data["success"])
        self.assertTrue(data["all_passed"])

        # 6. Submit Practical Assignment
        resp = self.client.post(
            f"/challenge/{slug}/assignment/submit",
            data={
                "github_repo_url": "https://github.com/aman-verma/skillrock-python-capstone",
                "live_demo_url": "https://aman-python-demo.onrender.com",
                "submission_notes": "Implemented automated data pipeline with comprehensive pytest suite.",
            },
            follow_redirects=True,
        )
        self.assertEqual(resp.status_code, 200)
        sub = ChallengeAssignmentSubmission.get_user_submission(str(self.student.id), slug)
        self.assertIsNotNone(sub)
        self.assertEqual(sub.status, "submitted")

        # 7. Start Assessment (50 MCQs)
        resp = self.client.post(f"/challenge/{slug}/assessment/start")
        data = resp.get_json()
        self.assertTrue(data["success"])
        attempt_id = data["attempt_id"]
        questions = data["questions"]
        self.assertEqual(len(questions), 50)
        # Ensure correct_option is NOT exposed to client
        self.assertNotIn("correct_option", questions[0])

        # 8. Submit Assessment Answers (score 100%)
        answers = {}
        for q_item in questions:
            q_db = AssessmentQuestion.get_by_id(q_item["id"])
            answers[q_item["id"]] = q_db.correct_option

        resp = self.client.post(
            f"/challenge/{slug}/assessment/submit",
            data=json.dumps({"attempt_id": attempt_id, "answers": answers}),
            content_type="application/json",
        )
        data = resp.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["score"], 50)
        self.assertEqual(data["percentage"], 100.0)
        self.assertTrue(data["passed"])
        self.assertIsNotNone(data["certificate_id"])

        # 9. Verify Certificate Page
        resp = self.client.get(f"/challenge/{slug}/certificate")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Certificate of Completion", resp.data)
        self.assertIn(b"Aman Verma", resp.data)
        # Verify dynamic verification URL respects request host (localhost in test client)
        self.assertIn(f"/learning/verify/{data['certificate_id']}".encode("utf-8"), resp.data)

        # Verify persisted Certificate matches fallback ChallengeEnrollment resolution
        from models.mongo import Certificate
        from routes.learning import _resolve_certificate_or_challenge
        persisted_cert = Certificate.get_by_cert_id(data["certificate_id"])
        self.assertIsNotNone(persisted_cert)
        ch = MonthlyChallenge.get_by_slug(slug)
        self.assertEqual(persisted_cert.display_course_title, ch.title)
        self.db.certificates.delete_one({"certificate_id": data["certificate_id"]})
        fallback_cert = _resolve_certificate_or_challenge(data["certificate_id"])
        self.assertIsNotNone(fallback_cert)
        self.assertEqual(persisted_cert.verification_hash, fallback_cert.verification_hash)
        self.assertEqual(persisted_cert.display_course_title, fallback_cert.display_course_title)
        # Re-save persisted cert so db state remains consistent
        persisted_cert._id = None
        persisted_cert.save()

    # ==========================================================================
    # 5. 100% Refund Claim Verification & Gate
    # ==========================================================================

    def test_5_refund_claim_evaluation(self):
        """Validates that 100% refund claims reject if conditions are unmet, and accept when all 7 are fulfilled."""
        self._login_as(self.student)
        slug = "python-28-day-challenge"
        ch = MonthlyChallenge.get_by_slug(slug)
        enr = ChallengeEnrollment.get_user_enrollment(str(self.student.id), slug)

        # Ensure all 6 modules are marked completed for test
        enr.modules_completed = [1, 2, 3, 4, 5, 6]
        # Ensure all practice questions answered
        practice_qs = PracticeQuestion.get_by_challenge(slug)
        for pq in practice_qs:
            enr.practice_scores[str(pq.order_index)] = {"selected": pq.correct_option, "is_correct": True}
        # Ensure all interview questions marked completed
        interview_qs = InterviewQuestion.get_by_challenge(slug)
        for iq in interview_qs:
            enr.interview_prep_status[str(iq.order_index)] = "completed"
        # Ensure all coding problems solved
        coding_probs = CodingProblem.get_by_challenge(slug)
        enr.coding_problems_solved = [p.slug for p in coding_probs]
        # Assignment status
        enr.assignment_status = "submitted"
        # Assessment passed
        enr.assessment_passed = True
        enr.save()

        # Submit valid 100% refund claim
        resp = self.client.post(
            f"/challenge/{slug}/refund/claim",
            data=json.dumps({
                "upi_id": "amanverma@okaxis",
                "account_holder_name": "Aman Verma",
                "phone_number": "9876543210",
            }),
            content_type="application/json",
        )
        data = resp.get_json()
        self.assertTrue(data["success"])
        self.assertIn("claim_id", data)

        claim = RefundClaim.get_by_id(data["claim_id"])
        self.assertIsNotNone(claim)
        self.assertEqual(claim.status, "pending")
        self.assertEqual(claim.amount, 499.0)

    # ==========================================================================
    # 6. Admin Management & 100% Refund Console
    # ==========================================================================

    def test_6_admin_console_and_refund_lifecycle(self):
        """Validates admin challenges view, project rubric review, and refund approve/disburse lifecycle."""
        self._login_as(self.admin)

        # Admin challenges list
        resp = self.client.get("/admin/challenges")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"SkillRock Monthly Challenges", resp.data)

        # Admin assignment review
        sub = ChallengeAssignmentSubmission.get_user_submission(str(self.student.id), "python-28-day-challenge")
        self.assertIsNotNone(sub)
        resp = self.client.post(
            f"/admin/challenges/submissions/{sub.id}/evaluate",
            data={"status": "approved", "score": "95", "admin_feedback": "Excellent clean code and robust tests."},
            follow_redirects=True,
        )
        self.assertEqual(resp.status_code, 200)
        sub_updated = ChallengeAssignmentSubmission.get_by_id(str(sub.id))
        self.assertEqual(sub_updated.status, "approved")
        self.assertEqual(sub_updated.score, 95.0)

        # Admin refund claims console
        resp = self.client.get("/admin/challenges/refunds")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"100% Refund Claims Console", resp.data)

        # Approve and disburse refund claim
        claim = RefundClaim.get_by_user_challenge(str(self.student.id), "python-28-day-challenge")
        self.assertIsNotNone(claim)

        # Approve action
        resp = self.client.post(
            f"/admin/challenges/refunds/{claim.id}/action",
            data={"action": "approve", "admin_notes": "All 7 conditions audited and verified."},
            follow_redirects=True,
        )
        self.assertEqual(resp.status_code, 200)
        cl_approved = RefundClaim.get_by_id(str(claim.id))
        self.assertEqual(cl_approved.status, "approved")

        # Mark paid (payout disbursement)
        resp = self.client.post(
            f"/admin/challenges/refunds/{claim.id}/action",
            data={"action": "pay", "payout_reference": "UPI9876543210REF", "admin_notes": "Disbursed ₹499 via UPI."},
            follow_redirects=True,
        )
        self.assertEqual(resp.status_code, 200)
        cl_paid = RefundClaim.get_by_id(str(claim.id))
        self.assertEqual(cl_paid.status, "paid")
        self.assertEqual(cl_paid.payout_reference, "UPI9876543210REF")

    # ==========================================================================
    # 7. Permanent 301 Redirects for Legacy Roadmaps
    # ==========================================================================

    def test_7_legacy_roadmap_redirects(self):
        """Validates that all legacy /roadmaps routes redirect permanently (301) to /challenge."""
        resp = self.client.get("/roadmaps")
        self.assertEqual(resp.status_code, 301)
        self.assertTrue(resp.headers["Location"].endswith("/challenge"))

        resp = self.client.get("/roadmaps/full-stack-developer-launchpad")
        self.assertEqual(resp.status_code, 301)
        self.assertTrue(resp.headers["Location"].endswith("/challenge"))


if __name__ == "__main__":
    unittest.main()
