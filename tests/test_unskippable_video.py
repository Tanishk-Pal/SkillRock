import unittest
from datetime import datetime, timezone, timedelta
from app import create_app
from models.mongo import get_db, Course, Enrollment, User

class TestUnskippableVideoAndAntiCheat(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()
        self.db = get_db()

        # Unique identifiers for test isolation
        ts = datetime.now().timestamp()
        self.test_email = f"student_anticheat_{ts}@example.com"
        self.test_user_id = f"user_anticheat_{ts}"

        # Insert test user
        self.db.users.insert_one({
            "_id": self.test_user_id,
            "email": self.test_email,
            "name": "AntiCheat Test Student",
            "is_admin": False,
            "created_at": datetime.now(timezone.utc)
        })

        # Insert test course (1000 seconds duration)
        self.test_course_id = f"course_anticheat_{ts}"
        self.db.courses.insert_one({
            "_id": self.test_course_id,
            "slug": f"course-anticheat-{ts}",
            "title": "AntiCheat Verification Course",
            "category": "Programming",
            "difficulty": "Beginner",
            "estimated_duration": "16 Minutes",
            "instructor": "SkillRock Engineering",
            "youtube_url": "https://www.youtube.com/watch?v=xk4_1vDrzzo",
            "youtube_video_id": "xk4_1vDrzzo",
            "description": "Comprehensive course for unskippable testing.",
            "is_published": True,
            "created_at": datetime.now(timezone.utc)
        })

    def tearDown(self):
        self.db.users.delete_one({"_id": self.test_user_id})
        self.db.courses.delete_one({"_id": self.test_course_id})
        self.db.enrollments.delete_many({"user_id": self.test_user_id})

    def _login_session(self):
        with self.client.session_transaction() as sess:
            sess["_user_id"] = self.test_user_id
            sess["user_id"] = self.test_user_id
            sess["_fresh"] = True

    def test_course_embed_url_contains_unskippable_params(self):
        """Test that Course.embed_url contains all required suppression parameters."""
        course = Course.get_by_id(self.test_course_id)
        self.assertIsNotNone(course)
        embed_url = course.embed_url
        self.assertIn("controls=0", embed_url)
        self.assertIn("disablekb=1", embed_url)
        self.assertIn("rel=0", embed_url)
        self.assertIn("playsinline=1", embed_url)
        self.assertIn("iv_load_policy=3", embed_url)

    def test_normal_incremental_playback_progress(self):
        """Test normal legitimate incremental watch progress."""
        self._login_session()

        # Send initial watch ping: 20 seconds out of 1000s duration
        resp = self.client.post("/learning/save-progress", json={
            "course_id": self.test_course_id,
            "watch_seconds": 20,
            "video_duration": 1000
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["watch_seconds"], 20)
        self.assertEqual(data["max_watch_seconds"], 20)
        self.assertEqual(data["watch_percent"], 2)
        self.assertFalse(data["video_completed"])

    def test_forward_leap_cheating_is_clamped(self):
        """Test that attempting to skip forward from 20s to 900s without elapsed wall-clock time is clamped."""
        self._login_session()

        # Step 1: Initial legitimate ping at 20 seconds
        self.client.post("/learning/save-progress", json={
            "course_id": self.test_course_id,
            "watch_seconds": 20,
            "video_duration": 1000
        })

        # Step 2: Immediate fraudulent leap to 950 seconds (95% to get certificate)
        resp2 = self.client.post("/learning/save-progress", json={
            "course_id": self.test_course_id,
            "watch_seconds": 950,
            "video_duration": 1000
        })
        self.assertEqual(resp2.status_code, 200)
        data2 = resp2.get_json()

        # Progress MUST be clamped to allowed delta (stored 20 + ~5s allowance), NOT 950s!
        self.assertLess(data2["watch_seconds"], 50)
        self.assertLess(data2["max_watch_seconds"], 50)
        self.assertLess(data2["watch_percent"], 10)
        self.assertFalse(data2["video_completed"], "Cheating student must NOT unlock video completion!")

    def test_backward_seek_preserves_max_watch_seconds(self):
        """Test that seeking backward to review earlier material preserves max_watch_seconds."""
        self._login_session()

        # Step 1: Reach 25 seconds
        self.client.post("/learning/save-progress", json={
            "course_id": self.test_course_id,
            "watch_seconds": 25,
            "video_duration": 1000
        })

        # Step 2: Student rewinds 15 seconds to timestamp 10s
        resp = self.client.post("/learning/save-progress", json={
            "course_id": self.test_course_id,
            "watch_seconds": 10,
            "video_duration": 1000
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()

        self.assertEqual(data["watch_seconds"], 10)
        self.assertEqual(data["max_watch_seconds"], 25, "Max watched timestamp must be preserved on rewind")

    def test_certification_gate_80_percent_requirement(self):
        """Test that video_completed only unlocks when verified progress legitimately reaches 80%."""
        enrollment = Enrollment({
            "user_id": self.test_user_id,
            "course_id": self.test_course_id,
            "watch_seconds": 790,
            "max_watch_seconds": 790,
            "video_duration": 1000,
            "watch_percent": 79,
            "video_completed": False,
            "last_progress_ping": datetime.now(timezone.utc) - timedelta(seconds=20)
        })
        enrollment.save()

        self._login_session()

        # Student watches 15 more seconds (from 790s to 805s) after 20 wall-clock seconds elapsed
        resp = self.client.post("/learning/save-progress", json={
            "course_id": self.test_course_id,
            "watch_seconds": 805,
            "video_duration": 1000
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()

        self.assertGreaterEqual(data["watch_percent"], 80)
        self.assertTrue(data["video_completed"], "Certificate gate unlocks once 80% is legitimately reached")

if __name__ == "__main__":
    unittest.main()
