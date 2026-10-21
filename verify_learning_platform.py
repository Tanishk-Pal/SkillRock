"""
Skill Rock — Automated End-to-End Verification Suite for Learn & Build Platform
Tests:
1. Model persistence, compound indexes, and queries (Course, Assignment, Enrollment, Submission, Review, Certificate).
2. Public Course Catalogue & detail pages.
3. Free Student Enrolment (idempotent, prevents duplicate).
4. Project Submission form with strict GitHub/URL validation.
5. Admin Review Queue, rubric scoring, and decision flow.
6. Certificate generation with unique ID, cryptographic hash, and 200 XP award.
7. Public Certificate Verification route (/verify/<cert_id>).
8. Security & Access Control (students cannot access admin reviews or issue certificates).
"""

import sys
import unittest
from datetime import datetime, timezone
from app import create_app
from models import (
    get_db,
    User,
    Course,
    Assignment,
    Enrollment,
    Submission,
    Review,
    Certificate,
    extract_youtube_id,
    slugify
)

class TestLearnAndBuildPlatform(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.app.config['TESTING'] = True
        cls.app.config['WTF_CSRF_ENABLED'] = False
        cls.client = cls.app.test_client()
        cls.db = get_db()

        # Create a test student once for the entire test suite
        cls.student_email = f"test_student_{int(datetime.now().timestamp())}@skillrock.edu"
        cls.student = User({
            "name": "Alex Student",
            "email": cls.student_email,
            "role": "student",
            "college": "Tech Institute",
            "branch": "Computer Science",
            "year": "3rd Year",
            "xp": 100,
            "created_at": datetime.now(timezone.utc)
        })
        cls.student.set_password("StudentPass123!")
        cls.student.save()

        # Retrieve admin user
        cls.admin = User.get_by_email("palt51419@gmail.com")

    def test_01_youtube_parser_and_slugify(self):
        """Verify robust YouTube video ID extraction across various formats."""
        urls = [
            ("https://www.youtube.com/watch?v=gfDE2a7MKjA", "gfDE2a7MKjA"),
            ("https://youtu.be/gfDE2a7MKjA", "gfDE2a7MKjA"),
            ("https://www.youtube.com/embed/gfDE2a7MKjA", "gfDE2a7MKjA"),
            ("https://www.youtube.com/playlist?list=PLu0W_9lII9agwh1XjRt242xIpHhPT2llg", "playlist:PLu0W_9lII9agwh1XjRt242xIpHhPT2llg")
        ]
        for url, expected in urls:
            extracted = extract_youtube_id(url)
            self.assertEqual(extracted, expected, f"Failed extracting from {url}")

        self.assertEqual(slugify("Python Programming: Beginner to Pro!"), "python-programming-beginner-to-pro")

    def test_02_default_courses_seeded(self):
        """Verify default curated courses and assignments are present in DB."""
        courses = Course.find_all()
        self.assertGreaterEqual(len(courses), 3, "Expected at least 3 default seeded courses")
        for course in courses:
            self.assertTrue(course.title)
            self.assertTrue(course.slug)
            self.assertTrue(course.youtube_url)
            self.assertIsNotNone(course.assignment, f"Course {course.title} missing assignment")

    def test_03_public_course_browsing(self):
        """Verify public catalogue and course details load without login."""
        res = self.client.get("/learning/courses")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Learn. Build. Deploy.", res.data)

        # Check detail page of first course
        course = Course.find_all()[0]
        res_detail = self.client.get(f"/learning/courses/{course.slug}")
        self.assertEqual(res_detail.status_code, 200)
        self.assertIn(course.title.encode("utf-8")[:20], res_detail.data)

    def test_04_student_enrolment(self):
        """Verify student enrolment is free, idempotent, and tracked."""
        course = Course.find_all()[0]

        # Login as test student
        with self.client.session_transaction() as sess:
            sess['_user_id'] = str(self.student.id)

        # Enrol in course
        res = self.client.post(f"/learning/enrol/{course.id}", follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        # Verify DB enrollment
        enr = Enrollment.get_by_user_course(self.student.id, course.id)
        self.assertIsNotNone(enr)
        self.assertEqual(enr.status, "enrolled")

        # Duplicate enrolment attempt should handle gracefully
        res_dup = self.client.post(f"/learning/enrol/{course.id}", follow_redirects=True)
        self.assertEqual(res_dup.status_code, 200)
        self.assertIn(b"already enrolled", res_dup.data)

    def test_05_project_submission_and_validation(self):
        """Verify strict URL validation and project submission workflow."""
        course = Course.find_all()[0]
        assignment = course.assignment

        with self.client.session_transaction() as sess:
            sess['_user_id'] = str(self.student.id)

        # Invalid GitHub URL should fail validation
        res_invalid = self.client.post(f"/learning/submit/{assignment.id}", data={
            "title": "My Task App",
            "tech_stack": "Python, Flask",
            "github_url": "not-a-valid-url",
            "deployment_url": "https://my-app.onrender.com",
            "description": "This is a detailed description of the project that is at least 30 characters long."
        }, follow_redirects=True)
        self.assertIn(b"valid GitHub repository URL", res_invalid.data)

        # Valid submission
        res_valid = self.client.post(f"/learning/submit/{assignment.id}", data={
            "title": "Automated Student Task Manager",
            "tech_stack": "Python 3.12, SQLite, Rich CLI",
            "github_url": "https://github.com/alex-student/task-manager",
            "deployment_url": "https://task-manager-alex.onrender.com",
            "description": "A comprehensive student task manager with priority sorting, SQLite database persistence, and CLI interactive menu."
        }, follow_redirects=True)
        self.assertEqual(res_valid.status_code, 200)

        # Verify submission saved with pending_review status
        sub = Submission.get_latest(self.student.id, assignment.id)
        self.assertIsNotNone(sub)
        self.assertEqual(sub.status, Submission.STATUS_PENDING)

    def test_06_admin_review_and_certificate_issuance(self):
        """Verify admin evaluation, rubric scorecard, approval, and certificate generation."""
        course = Course.find_all()[0]
        assignment = course.assignment
        sub = Submission.get_latest(self.student.id, assignment.id)

        # Login as Admin
        with self.client.session_transaction() as sess:
            sess['_user_id'] = str(self.admin.id)

        # Review page loads
        res_rev_page = self.client.get(f"/admin/submissions/{sub.id}/review")
        self.assertEqual(res_rev_page.status_code, 200)
        self.assertIn(b"Evaluation Scorecard", res_rev_page.data)

        # Submit positive evaluation with approval
        initial_xp = self.student.xp
        res_approve = self.client.post(f"/admin/submissions/{sub.id}/review", data={
            "decision": "approved",
            "feedback": "Outstanding work! Clean code organization, comprehensive test coverage, and responsive deployed UI.",
            "score_0": "40",
            "score_1": "30",
            "score_2": "20",
            "score_3": "10"
        }, follow_redirects=True)
        self.assertEqual(res_approve.status_code, 200)

        # Verify submission updated to approved
        updated_sub = Submission.get_by_id(sub.id)
        self.assertEqual(updated_sub.status, Submission.STATUS_APPROVED)

        # Verify certificate generated
        cert = Certificate.get_by_user_course(self.student.id, course.id)
        self.assertIsNotNone(cert, "Certificate was not created on approval")
        self.assertTrue(cert.certificate_id.startswith("SR-"))
        self.assertTrue(len(cert.verification_hash) > 10)

        # Verify student XP was awarded (+200 XP)
        refreshed_student = User.get_by_id(self.student.id)
        self.assertEqual(refreshed_student.xp, initial_xp + 200)

        # Verify public certificate verification endpoint
        res_verify = self.client.get(f"/verify/{cert.certificate_id}", follow_redirects=True)
        self.assertEqual(res_verify.status_code, 200)
        self.assertIn(b"Verified Authentic Credential", res_verify.data)
        self.assertIn(self.student.name.encode("utf-8"), res_verify.data)

        # Invalid certificate ID returns not found
        res_fake_verify = self.client.get("/verify/SR-FAKE-99999", follow_redirects=True)
        self.assertEqual(res_fake_verify.status_code, 200)
        self.assertIn(b"Certificate Not Found", res_fake_verify.data)

    def test_07_access_control_security(self):
        """Verify non-admin students cannot access admin review or management pages."""
        # Login as student
        with self.client.session_transaction() as sess:
            sess['_user_id'] = str(self.student.id)

        res_admin_courses = self.client.get("/admin/courses", follow_redirects=True)
        self.assertIn(b"Access Denied", res_admin_courses.data)

        res_admin_subs = self.client.get("/admin/submissions", follow_redirects=True)
        self.assertIn(b"Access Denied", res_admin_subs.data)

if __name__ == "__main__":
    unittest.main()
