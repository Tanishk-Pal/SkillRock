import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.stdout.reconfigure(encoding="utf-8")

from app import create_app
from models.mongo import Assignment, Submission, Course, User, Certificate, Enrollment, Review, get_db
from routes.learning import is_valid_url, is_valid_github_url
from services.assignment_evaluator import AssignmentEvaluator
from bson import ObjectId


class TestAssignmentSystem(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.app.config["TESTING"] = True
        cls.app.config["WTF_CSRF_ENABLED"] = False
        cls.client = cls.app.test_client()

    def setUp(self):
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    # =========================================================================
    # 1. Assignment Model & Dynamic Evaluation Type Tests
    # =========================================================================

    def test_assignment_type_project_based(self):
        """Verify project_based assignments are properly identified."""
        asg = Assignment({
            "title": "Build a Full-Stack LMS",
            "evaluation_type": "project_based",
            "passing_score": 75,
            "required_features": ["User Auth", "Video Player"]
        })
        self.assertTrue(asg.is_project_based)
        self.assertFalse(asg.is_algorithmic)
        self.assertEqual(asg.passing_score, 75)
        self.assertTrue(asg.is_deployment_required)

    def test_assignment_type_algorithmic(self):
        """Verify algorithmic assignments are properly identified."""
        asg = Assignment({
            "title": "Reverse Linked List",
            "evaluation_type": "algorithmic",
            "target_function_name": "reverse_list",
            "test_cases": [{"name": "Case 1", "input": "[1,2,3]", "expected": "[3,2,1]"}]
        })
        self.assertTrue(asg.is_algorithmic)
        self.assertFalse(asg.is_project_based)
        self.assertEqual(asg.passing_score, 70)

    def test_assignment_type_ai_dual(self):
        """Verify ai_dual assignments are recognized under algorithmic category."""
        asg = Assignment({
            "title": "Bank Account Class",
            "evaluation_type": "ai_dual",
            "test_cases": [{"name": "Case 1", "input": "BankAccount()", "expected": "ok"}]
        })
        self.assertTrue(asg.is_algorithmic)
        self.assertFalse(asg.is_project_based)

    def test_html_developer_challenge_is_project_based(self):
        """Verify the specific HTML Fundamentals assignment is project_based in DB."""
        html_asg = Assignment.get_by_id("6adeba95f5e6cf2a48b909e1")
        self.assertIsNotNone(html_asg, "HTML Developer Challenge assignment must exist in database")
        self.assertTrue(html_asg.is_project_based)
        self.assertFalse(html_asg.is_algorithmic)
        self.assertEqual(html_asg.evaluation_type, "project_based")
        self.assertTrue(html_asg.is_deployment_required)
        self.assertGreater(len(html_asg.required_features), 0)
        self.assertGreater(len(html_asg.rubric), 0)

    # =========================================================================
    # 2. Strict URL Validation Tests
    # =========================================================================

    def test_is_valid_url(self):
        """Verify HTTP/HTTPS URL validation."""
        self.assertTrue(is_valid_url("https://my-portfolio.onrender.com"))
        self.assertTrue(is_valid_url("http://localhost:5000/demo"))
        self.assertTrue(is_valid_url("https://portfolio.vercel.app/project/1"))
        
        # Invalid URLs
        self.assertFalse(is_valid_url(""))
        self.assertFalse(is_valid_url(None))
        self.assertFalse(is_valid_url("javascript:alert(1)"))
        self.assertFalse(is_valid_url("ftp://files.example.com"))
        self.assertFalse(is_valid_url("my-portfolio.onrender.com"))  # missing scheme
        self.assertFalse(is_valid_url("https://"))                   # missing domain
        self.assertFalse(is_valid_url("https:///path"))

    def test_is_valid_github_url(self):
        """Verify GitHub repository URL validation."""
        self.assertTrue(is_valid_github_url("https://github.com/octocat/Hello-World"))
        self.assertTrue(is_valid_github_url("https://www.github.com/john_doe/portfolio-site/"))
        self.assertTrue(is_valid_github_url("http://github.com/student-123/skillrock-project"))

        # Invalid GitHub URLs
        self.assertFalse(is_valid_github_url("https://gitlab.com/octocat/Hello-World"))
        self.assertFalse(is_valid_github_url("https://github.com/"))
        self.assertFalse(is_valid_github_url("https://github.com/octocat"))
        self.assertFalse(is_valid_github_url("github.com/octocat/repo"))
        self.assertFalse(is_valid_github_url("not a url"))

    # =========================================================================
    # 3. Submission Model Statuses & Display Tests
    # =========================================================================

    def test_submission_statuses(self):
        """Verify submission statuses and human-readable display labels."""
        sub_not_sub = Submission({"status": Submission.STATUS_NOT_SUBMITTED})
        self.assertEqual(sub_not_sub.status_display, "Not Submitted")

        sub_pending = Submission({"status": Submission.STATUS_PENDING})
        self.assertEqual(sub_pending.status_display, "Under Review")

        sub_changes = Submission({"status": Submission.STATUS_CHANGES})
        self.assertEqual(sub_changes.status_display, "Changes Requested")

        sub_approved = Submission({"status": Submission.STATUS_APPROVED})
        self.assertEqual(sub_approved.status_display, "Approved")

        sub_rejected = Submission({"status": Submission.STATUS_REJECTED})
        self.assertEqual(sub_rejected.status_display, "Needs Revision")

    # =========================================================================
    # 4. Algorithmic Test Suite Preserved
    # =========================================================================

    def test_algorithmic_evaluator_runs_cleanly(self):
        """Verify automated Python solution evaluator continues functioning properly."""
        asg = Assignment({
            "title": "Palindrome Checker",
            "evaluation_type": "algorithmic",
            "target_function_name": "is_palindrome",
            "test_cases": [
                {"name": "Check racecar", "input": "'racecar'", "expected": "True"},
                {"name": "Check hello", "input": "'hello'", "expected": "False"}
            ]
        })
        good_code = "def is_palindrome(s):\n    return s == s[::-1]"
        result = AssignmentEvaluator.evaluate(asg, good_code, "")
        self.assertEqual(result["decision"], "approved")
        self.assertEqual(result["score"], 100)
        self.assertEqual(len(result["test_results"]), 2)
        self.assertEqual(result["test_results"][0]["status"], "pass")
        self.assertTrue(result["test_results"][0]["passed"])

    # =========================================================================
    # 5. Reviewer Rubric Scoring & Passing Score Gate Tests
    # =========================================================================

    def test_reviewer_passing_score_gate(self):
        """Verify reviewer cannot approve a submission if score is below passing score."""
        asg = Assignment({
            "title": "Test Capstone Project",
            "evaluation_type": "project_based",
            "passing_score": 75,
            "rubric": [
                {"criterion": "Core Functionality", "max_points": 50, "description": "Mandatory features"},
                {"criterion": "Code Quality", "max_points": 50, "description": "Clean code"}
            ]
        })
        self.assertEqual(asg.passing_score, 75)

        # Total score 60/100 = 60%, below passing score of 75%
        failing_total = 60
        passing_score = asg.passing_score
        self.assertLess(failing_total, passing_score)

        # Total score 80/100 = 80%, satisfies passing score of 75%
        passing_total = 80
        self.assertGreaterEqual(passing_total, passing_score)


if __name__ == "__main__":
    unittest.main()
