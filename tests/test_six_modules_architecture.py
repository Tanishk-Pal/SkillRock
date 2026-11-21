# -*- coding: utf-8 -*-
"""
SkillRock — Six Modules Architecture & Platform Transformation Test Suite
"""

import unittest
from app import create_app
from models.course_modules import (
    get_course_modules_data,
    TECHNICAL_INTERVIEW_QUESTIONS,
    HR_INTERVIEW_QUESTIONS,
    ENGLISH_ACADEMY_LESSONS,
    INTERNSHIP_OPPORTUNITIES,
    CAREER_DEVELOPMENT_RESOURCES
)
from models import User, Course

class TestSixModulesArchitecture(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.app.config["TESTING"] = True
        cls.app.config["WTF_CSRF_ENABLED"] = False
        cls.client = cls.app.test_client()

    def test_01_course_modules_data_generator(self):
        """Verify course modules data generator returns all 6 module data structures."""
        data = get_course_modules_data("artificial-intelligence-machine-learning-master", "Artificial intelligence & Machine Learning Master")
        self.assertIn("chapters", data)
        self.assertIn("practice_test", data)
        self.assertIn("tech_questions", data)
        self.assertIn("hr_questions", data)
        self.assertIn("english_lessons", data)
        self.assertIn("career_resources", data)
        self.assertIn("internships", data)
        self.assertGreaterEqual(len(data["chapters"]), 5)
        self.assertGreaterEqual(len(data["tech_questions"]), 8)
        self.assertEqual(len(data["english_lessons"]), 10)

    def test_02_standalone_english_academy_route(self):
        """Verify /learning/english-academy renders the 10 English lessons."""
        response = self.client.get("/learning/english-academy")
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn("English & Communication Academy", html)
        self.assertIn("Introducing Yourself in English", html)
        self.assertIn("Hindi:", html)

    def test_03_standalone_internships_route(self):
        """Verify /learning/internships renders opportunity listings."""
        response = self.client.get("/learning/internships")
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn("Opportunity & Internship Centre", html)
        self.assertIn("Google Summer of Code", html)
        self.assertIn("Smart India Hackathon", html)

    def test_04_standalone_career_guide_route(self):
        """Verify /learning/career-guide renders ATS checklist and Google XYZ formula."""
        response = self.client.get("/learning/career-guide")
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn("Career, Resume & Portfolio Toolkit", html)
        self.assertIn("Google XYZ Formula", html)
        self.assertIn("Accomplished [X] as measured by [Y], by doing [Z]", html)
        self.assertIn("ATS Resume Checklist", html)

    def test_05_homepage_educational_transformation(self):
        """Verify the homepage displays the new educational hero, stats, and real courses."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn("Learn Skills. Build Projects.", html)
        self.assertIn("Prepare for Your Career.", html)
        self.assertIn("Explore Courses", html)
        self.assertIn("Featured Practical Courses", html)
        self.assertIn("How SkillRock Accelerates Your Growth", html)
        self.assertIn("Tamper-Proof Cryptographic Verification", html)

    def test_06_mobile_bottom_navigation(self):
        """Verify base template contains app-like bottom navigation items for authenticated users."""
        with self.app.app_context():
            users = User.find_all(limit=1)
            user_id = str(users[0].id) if users else "mock_id"

        with self.client.session_transaction() as sess:
            sess["_user_id"] = user_id
            sess["_fresh"] = True

        response = self.client.get("/learning/courses")
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn("mobile-bottom-nav", html)
        self.assertIn("Bhavishya", html)
        self.assertIn("Ski", html)

    def test_07_course_detail_six_modules_rendering(self):
        """Verify course classroom renders all 6 modules on /learning/courses/<slug>."""
        with self.app.app_context():
            courses = Course.get_published_courses()
            slug = courses[0].slug if courses else "artificial-intelligence-machine-learning-master"

        response = self.client.get(f"/learning/courses/{slug}")
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn("course-module-tabs-bar", html)
        self.assertIn("Learn & Lectures", html)
        self.assertIn("Practice & Test", html)
        self.assertIn("Build Project", html)
        self.assertIn("Interview Prep", html)
        self.assertIn("Career & English", html)
        self.assertIn("Certificate", html)

if __name__ == "__main__":
    unittest.main()
