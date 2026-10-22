"""
Verification Script for SkillRock Production Level 1.0
Tests:
1. User model interests persistence and 3-item limit.
2. Onboarding bubble interest selection GET and POST.
3. Recommendation algorithm prioritizes courses matching student interest bubbles.
4. On-demand campus skill swap setup endpoint.
5. Physics Wallah navbar, sidebar, profile dropdown with merged logout.
"""

import unittest
from app import create_app
from models import get_db, User, Course, Assignment, Enrollment

class TestSkillRockProduction10(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.app.config["TESTING"] = True
        cls.app.config["WTF_CSRF_ENABLED"] = False
        cls.client = cls.app.test_client()

    def setUp(self):
        self.db = get_db()
        self.db.users.delete_many({"email": {"$regex": "@campus\\.edu$"}})
        self.client.get("/logout")

    def test_01_user_interests_model(self):
        """Verify User model supports interests up to 3 topics."""
        user = User.create(
            name="Alice Builder",
            email="alice.test@campus.edu",
            college="MIT",
            branch="CS",
            year="2nd Year"
        )
        self.assertEqual(user.interests, [])
        self.assertFalse(user.has_interests)

        # Set 2 interests
        user.set_interests(["Programming", "Web Development"])
        reloaded = User.get_by_id(user.id)
        self.assertEqual(reloaded.interests, ["Programming", "Web Development"])
        self.assertTrue(reloaded.has_interests)

        # Enforce maximum 3 interests
        user.set_interests(["Programming", "Web Development", "AI & Machine Learning", "Data Science"])
        reloaded2 = User.get_by_id(user.id)
        self.assertEqual(len(reloaded2.interests), 3)
        self.assertEqual(reloaded2.interests, ["Programming", "Web Development", "AI & Machine Learning"])

    def test_02_onboarding_route_and_selection(self):
        """Verify GET and POST /learning/onboarding for bubble interest selection."""
        user = User.create(
            name="Bob Learner",
            email="bob.test@campus.edu",
            college="Stanford",
            branch="EE",
            year="3rd Year"
        )
        user.set_password("Secret123")
        user.save()

        # Login Bob
        self.client.post("/login", data={"email": "bob.test@campus.edu", "password": "Secret123"}, follow_redirects=True)

        # GET onboarding screen
        resp = self.client.get("/learning/onboarding")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"What are you excited to learn and build?", resp.data)
        self.assertIn(b"Programming", resp.data)
        self.assertIn(b"Web Development", resp.data)

        # POST select 2 bubbles
        post_resp = self.client.post(
            "/learning/onboarding",
            data={"interests": ["Programming", "AI & Machine Learning"]},
            follow_redirects=True
        )
        self.assertEqual(post_resp.status_code, 200)
        # Should redirect to courses catalogue
        self.assertIn(b"Learn. Build. Deploy.", post_resp.data)

        # Verify persisted in database
        updated_bob = User.get_by_id(user.id)
        self.assertEqual(updated_bob.interests, ["Programming", "AI & Machine Learning"])

    def test_03_recommendation_algorithm_courses(self):
        """Verify Course catalog highlights courses matching student's selected interests."""
        user = User.create(
            name="Charlie Coder",
            email="charlie.test@campus.edu",
            college="BITS",
            branch="IT",
            year="1st Year"
        )
        user.set_password("Secret123")
        user.set_interests(["Programming"])
        user.save()

        self.client.post("/login", data={"email": "charlie.test@campus.edu", "password": "Secret123"}, follow_redirects=True)

        resp = self.client.get("/learning/courses")
        self.assertEqual(resp.status_code, 200)
        # Check that recommended section appears
        self.assertIn(b"Recommended for Your Interests", resp.data)
        self.assertIn(b"Your Focus Topics:", resp.data)
        self.assertIn(b"Programming", resp.data)

    def test_04_on_demand_skill_swap_setup(self):
        """Verify on-demand campus skill swap configuration endpoint."""
        user = User.create(
            name="Diana Swapper",
            email="diana.test@campus.edu",
            college="IIT",
            branch="Mechanical",
            year="4th Year"
        )
        user.set_password("Secret123")
        user.save()

        self.client.post("/login", data={"email": "diana.test@campus.edu", "password": "Secret123"}, follow_redirects=True)

        # Call quick-setup endpoint
        resp = self.client.post(
            "/skills/quick-setup",
            data={
                "teaching_skills": ["Python", "3D Modeling"],
                "learning_skills": ["Machine Learning", "Flutter"]
            },
            follow_redirects=True
        )
        self.assertEqual(resp.status_code, 200)

        updated_diana = User.get_by_id(user.id)
        teach_names = [s.name for s in updated_diana.teaching_skills]
        learn_names = [s.name for s in updated_diana.learning_skills]
        self.assertIn("Python", teach_names)
        self.assertIn("Machine Learning", learn_names)

    def test_05_merged_logout_and_pw_sidebar(self):
        """Verify Physics Wallah layout elements render properly."""
        user = User.create(
            name="Ethan Test",
            email="ethan.test@campus.edu",
            college="Harvard",
            branch="CS",
            year="2nd Year"
        )
        user.set_password("Secret123")
        user.set_interests(["Web Development"])
        user.save()

        self.client.post("/login", data={"email": "ethan.test@campus.edu", "password": "Secret123"}, follow_redirects=True)

        resp = self.client.get("/learning/courses")
        self.assertEqual(resp.status_code, 200)

        # Check Physics Wallah top navbar and sidebar elements
        self.assertIn(b"navbar-pw", resp.data)
        self.assertIn(b"pw-sidebar", resp.data)
        self.assertIn(b"LEARN ONLINE", resp.data)
        self.assertIn(b"CAMPUS EXCHANGE", resp.data)
        self.assertIn(b"profileDropdownMenu", resp.data)
        self.assertIn(b"pw-logout-item", resp.data)

        # Test Logout
        logout_resp = self.client.get("/logout", follow_redirects=True)
        self.assertEqual(logout_resp.status_code, 200)
        self.assertIn(b"signed out", logout_resp.data.lower())


if __name__ == "__main__":
    unittest.main()
