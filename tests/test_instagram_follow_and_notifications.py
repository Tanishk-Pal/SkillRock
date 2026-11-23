# -*- coding: utf-8 -*-
"""
Unit tests for Instagram-Fast Follow/Unfollow, Real-time Peer Notifications,
and 4-Account Suggested Peers on Learn & Build.
"""

import os
import unittest
from datetime import datetime, timezone
from app import create_app
from models import get_db, User, SwapRequest, Connection, Notification

class TestInstagramFollowAndNotifications(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.app.config["TESTING"] = True
        cls.app.config["WTF_CSRF_ENABLED"] = False
        cls.client = cls.app.test_client()
        cls.db = get_db()

    def setUp(self):
        ts = int(datetime.now().timestamp() * 1000)
        self.user_a_email = f"user_a_{ts}@skillrock.edu"
        self.user_b_email = f"user_b_{ts}@skillrock.edu"

        self.user_a = User({
            "name": "Aryan Dev",
            "email": self.user_a_email,
            "role": "student",
            "branch": "Computer Science",
            "college": "IIT Delhi",
            "teaching_skills": [{"id": "s1", "name": "Python"}],
            "learning_skills": [{"id": "s2", "name": "DSA"}]
        })
        self.user_a.set_password("Pass123!")
        self.user_a.save()

        self.user_b = User({
            "name": "Sneha Sharma",
            "email": self.user_b_email,
            "role": "student",
            "branch": "Information Technology",
            "college": "BITS Pilani",
            "teaching_skills": [{"id": "s2", "name": "DSA"}],
            "learning_skills": [{"id": "s1", "name": "Python"}]
        })
        self.user_b.set_password("Pass123!")
        self.user_b.save()

    def tearDown(self):
        with self.client.session_transaction() as sess:
            sess.clear()
        if hasattr(self, "user_a") and self.user_a.id:
            self.db.users.delete_many({"_id": {"$in": [self.user_a._id, self.user_b._id]}})
            self.db.swap_requests.delete_many({"$or": [{"sender_id": str(self.user_a.id)}, {"receiver_id": str(self.user_a.id)}]})
            self.db.connections.delete_many({"$or": [{"user1_id": str(self.user_a.id)}, {"user2_id": str(self.user_a.id)}]})
            self.db.notifications.delete_many({"$or": [{"recipient_id": str(self.user_a.id)}, {"recipient_id": str(self.user_b.id)}]})

    def login_user(self, user):
        with self.client.session_transaction() as sess:
            sess['_user_id'] = str(user.id)
            sess['_fresh'] = True

    def test_01_follow_and_instant_notification(self):
        """User A follows User B -> User B receives instant in-app notification."""
        self.login_user(self.user_a)

        # User A sends follow via API
        resp = self.client.post(f"/api/follow/{self.user_b.id}", headers={"X-Requested-With": "XMLHttpRequest"})
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data.get("success"))
        self.assertEqual(data.get("status"), "requested")
        self.assertTrue(data.get("is_pending"))

        # Verify User B received notification
        unread_b = Notification.count_unread(str(self.user_b.id))
        self.assertEqual(unread_b, 1)

        # Login as User B and check notifications endpoint
        self.login_user(self.user_b)
        notif_resp = self.client.get("/api/notifications")
        self.assertEqual(notif_resp.status_code, 200)
        ndata = notif_resp.get_json()
        self.assertEqual(ndata.get("unread_count"), 1)
        self.assertTrue(len(ndata.get("notifications")) >= 1)
        self.assertIn("Aryan Dev", ndata["notifications"][0]["message"])

    def test_02_mutual_follow_back_creates_connection(self):
        """When User B follows User A back, mutual connection is established instantly (+20 XP)."""
        # User A follows User B
        self.login_user(self.user_a)
        self.client.post(f"/api/follow/{self.user_b.id}")

        # User B follows User A back
        self.login_user(self.user_b)
        resp = self.client.post(f"/api/follow/{self.user_a.id}", headers={"X-Requested-With": "XMLHttpRequest"})
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data.get("success"))
        self.assertEqual(data.get("status"), "connected")
        self.assertTrue(data.get("is_connected"))

        # Verify Connection exists
        conn = Connection.find_between(self.user_a.id, self.user_b.id)
        self.assertIsNotNone(conn)

    def test_03_notification_mark_all_read(self):
        """User can mark all unread notifications as read via /api/notifications/read-all."""
        Notification.notify(str(self.user_b.id), str(self.user_a.id), "follow_request", "New Follower", "Test message")
        self.assertEqual(Notification.count_unread(str(self.user_b.id)), 1)

        self.login_user(self.user_b)
        resp = self.client.post("/api/notifications/read-all")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Notification.count_unread(str(self.user_b.id)), 0)

    def test_04_learn_and_build_middle_suggestions(self):
        """Learn & Build page (/learning/courses) renders suggested campus peers in the middle."""
        self.login_user(self.user_a)
        resp = self.client.get("/learning/courses")
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)
        self.assertIn("Suggested Study Buddies", html)
        self.assertIn("See All on Skill Exchange", html)
        self.assertIn("btn-insta-follow", html)

    def test_05_discover_page_renders_with_instagram_cards(self):
        """Discover page (/discover) renders with Instagram-style peer cards and follow buttons."""
        self.login_user(self.user_a)
        resp = self.client.get("/discover")
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)
        self.assertIn("Discover Peers", html)
        self.assertIn("Follow Requests", html)
        self.assertIn("btn-insta-follow", html)
        self.assertIn("CAN TEACH", html)


if __name__ == "__main__":
    unittest.main()
