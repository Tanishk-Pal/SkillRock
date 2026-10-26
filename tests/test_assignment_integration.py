import sys
import os
import unittest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.stdout.reconfigure(encoding="utf-8")

from app import create_app
from models.mongo import Assignment, Submission, Course, User, Enrollment, get_db
from bson import ObjectId


class TestAssignmentIntegration(unittest.TestCase):

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

    def _login_test_user(self, course_id=None):
        """Find or create an active test user and log them into the test client with completed video enrollment."""
        user = User.get_by_email("test_student@example.com")
        if not user:
            user = User({
                "email": "test_student@example.com",
                "name": "Test Student",
                "role": "student",
                "is_admin": True  # Admin flag allows testing all steps and gates
            })
            user.set_password("SecurePassword123!")
            user.save()

        # If a course is specified, ensure enrollment has >= 80% watch progress
        if course_id:
            enrollment = Enrollment.get_by_user_course(user.id, course_id)
            if not enrollment:
                enrollment = Enrollment({
                    "user_id": str(user.id),
                    "course_id": str(course_id),
                    "watch_percent": 100,
                    "video_completed": True,
                    "status": "in_progress"
                })
                enrollment.save()
            else:
                enrollment.watch_percent = 100
                enrollment.video_completed = True
                enrollment.save()

        with self.client.session_transaction() as sess:
            sess["_user_id"] = str(user.id)
            sess["_fresh"] = True
        return user

    def test_html_fundamentals_detail_view(self):
        """Verify HTML Developer Challenge renders project-based deliverables and rubric."""
        resp = self.client.get("/learning/assignment/6adeba95f5e6cf2a48b909e1")
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)

        self.assertIn("Personal Portfolio Website", html)
        self.assertIn("Mandatory Core Features", html)
        self.assertIn("Required Project Deliverables", html)
        self.assertIn("Live Deployment URL", html)
        self.assertIn("Public GitHub Repository", html)
        self.assertIn("Passing Score: 70%", html)
        self.assertIn("Evaluation Rubric", html)

        # Must NOT render algorithmic test suite elements
        self.assertNotIn("Expected Target Function: solution()", html)
        self.assertNotIn("Automated Test Suite Assertions", html)

    def test_html_fundamentals_submission_portal(self):
        """Verify HTML Developer Challenge renders dedicated project submission interface."""
        html_asg = Assignment.get_by_id("6adeba95f5e6cf2a48b909e1")
        self._login_test_user(course_id=html_asg.course_id)
        resp = self.client.get("/learning/submit/6adeba95f5e6cf2a48b909e1")
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)

        self.assertIn("Project Submission Portal", html)
        self.assertIn('name="github_url"', html)
        self.assertIn('name="deployment_url"', html)
        self.assertIn('name="tech_stack"', html)
        self.assertIn('name="description"', html)
        self.assertIn("Passing Score: 70%", html)

        # Must NOT render Python solution editor or test runner
        self.assertNotIn("solution.py", html)
        self.assertNotIn('id="codeSnippet"', html)
        self.assertNotIn("btnRunTests", html)

    def test_algorithmic_assignment_renders_code_editor(self):
        """Verify algorithmic assignment renders Python solution.py editor and test runner."""
        # Find an algorithmic assignment in the DB
        db = get_db()
        algo_doc = db.assignments.find_one({"evaluation_type": "algorithmic"})
        if not algo_doc:
            self.skipTest("No algorithmic assignment found in DB")

        self._login_test_user(course_id=algo_doc.get("course_id"))
        resp = self.client.get(f"/learning/submit/{algo_doc['_id']}")
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)

        self.assertIn("solution.py", html)
        self.assertIn('id="codeSnippet"', html)
        self.assertIn("btnRunTests", html)
        self.assertIn("Run Tests & Diagnostics", html)

    def test_project_submission_validation_flow(self):
        """Verify backend rejects invalid URLs and accepts valid submissions."""
        asg_id = "6adeba95f5e6cf2a48b909e1"
        html_asg = Assignment.get_by_id(asg_id)
        user = self._login_test_user(course_id=html_asg.course_id)

        # 1. Invalid GitHub URL
        resp = self.client.post(f"/learning/submit/{asg_id}", data={
            "title": "My HTML Portfolio",
            "tech_stack": "HTML5, CSS3",
            "github_url": "https://invalid-site.com/repo",
            "deployment_url": "https://my-app.onrender.com",
            "description": "This is a comprehensive description of my portfolio website with semantic HTML."
        }, follow_redirects=True)
        html = resp.get_data(as_text=True)
        self.assertIn("Please provide a valid GitHub repository URL", html)

        # 2. Invalid Deployment URL
        resp = self.client.post(f"/learning/submit/{asg_id}", data={
            "title": "My HTML Portfolio",
            "tech_stack": "HTML5, CSS3",
            "github_url": "https://github.com/teststudent/html-portfolio",
            "deployment_url": "invalid-url-without-http",
            "description": "This is a comprehensive description of my portfolio website with semantic HTML."
        }, follow_redirects=True)
        html = resp.get_data(as_text=True)
        self.assertIn("Please provide a valid live deployment URL", html)

        # 3. Valid submission
        resp = self.client.post(f"/learning/submit/{asg_id}", data={
            "title": "My HTML Portfolio",
            "tech_stack": "HTML5, CSS3",
            "github_url": "https://github.com/teststudent/html-portfolio",
            "deployment_url": "https://my-app.onrender.com",
            "description": "This is a comprehensive description of my portfolio website with semantic HTML."
        }, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)

        # Verify submission saved in DB
        db = get_db()
        sub = db.submissions.find_one({"assignment_id": asg_id, "user_id": str(user.id)})
        self.assertIsNotNone(sub)
        self.assertEqual(sub["status"], "pending_review")
        self.assertEqual(sub["github_url"], "https://github.com/teststudent/html-portfolio")
        self.assertEqual(sub["deployment_url"], "https://my-app.onrender.com")


if __name__ == "__main__":
    unittest.main()
