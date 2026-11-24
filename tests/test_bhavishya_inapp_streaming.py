# -*- coding: utf-8 -*-
"""
Tests for SkillRock Bhavishya 1.0 Native In-App Live Streaming & Isolated Recording Vault.
Validates:
1. Complete removal of Google Meet and YouTube video embeds from Bhavishya lectures.
2. Native in-app Educator Broadcast Studio (for teachers) & Student Live Player (for students).
3. Stream lifecycle APIs (status, start, end).
4. Real-time in-app live classroom chat.
5. Storage of recordings in the isolated database vault.
"""

import os
import io
import json
import unittest
from datetime import datetime
from config import Config
from app import create_app
from models import User, get_db
from models.bhavishya import BhavishyaLiveLecture
from models.bhavishya_recordings import BhavishyaLectureRecording, get_recordings_db


class TestBhavishyaInAppStreaming(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Config.TESTING = True
        Config.WTF_CSRF_ENABLED = False
        cls.app = create_app(Config)
        cls.app.config["TESTING"] = True
        cls.client = cls.app.test_client()
        cls.db = get_db()

        ts = int(datetime.now().timestamp() * 1000)
        cls.teacher_email = f"lead_teacher_{ts}@skillrock.edu"
        cls.teacher = User({
            "name": "Tanishk Pal Sir",
            "email": cls.teacher_email,
            "role": "admin"
        })
        cls.teacher.set_password("TeacherSecure123!")
        cls.teacher.save()

        cls.student_email = f"live_student_{ts}@skillrock.edu"
        cls.student = User({
            "name": "Rohit Verma",
            "email": cls.student_email,
            "role": "student"
        })
        cls.student.set_password("StudentSecure123!")
        cls.student.save()

        cls.lecture_id = "py-live-01"

    @classmethod
    def tearDownClass(cls):
        try:
            cls.db.users.delete_many({"email": {"$in": [cls.teacher_email, cls.student_email]}})
        except Exception:
            pass

    def setUp(self):
        self.client = self.app.test_client()

    def tearDown(self):
        with self.client.session_transaction() as sess:
            sess.clear()

    def login_teacher(self):
        with self.client.session_transaction() as sess:
            sess["_user_id"] = str(self.teacher.id)
            sess["_fresh"] = True

    def login_student(self):
        with self.client.session_transaction() as sess:
            sess["_user_id"] = str(self.student.id)
            sess["_fresh"] = True

    def test_classroom_ui_renders_without_youtube_or_meet(self):
        """Verifies classroom UI renders with native in-app streaming components and zero YouTube iframes."""
        # 1. Student / Public view
        res = self.client.get(f"/bhavishya/lecture/{self.lecture_id}")
        self.assertEqual(res.status_code, 200)
        html = res.get_data(as_text=True)

        # Strict checks: No YouTube or Google Meet links
        self.assertNotIn("www.youtube.com/embed", html)
        self.assertNotIn("https://meet.google.com", html)
        self.assertIn("studentLiveVideo", html)
        self.assertIn("liveChatMessagesStream", html)

        # 2. Teacher view (includes Educator Broadcast Studio)
        self.login_teacher()
        res_teacher = self.client.get(f"/bhavishya/lecture/{self.lecture_id}")
        self.assertEqual(res_teacher.status_code, 200)
        teacher_html = res_teacher.get_data(as_text=True)
        self.assertIn("Educator Broadcast Studio", teacher_html)
        self.assertIn("Go Live on SkillRock", teacher_html)

    def test_stream_status_api(self):
        """Tests stream status check endpoint."""
        res = self.client.get(f"/bhavishya/api/lecture/{self.lecture_id}/stream_status")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data.get("success"))
        self.assertIn("is_live", data)
        self.assertIn("stream_room_id", data)
        self.assertIn("viewers_count", data)

    def test_stream_start_and_end_lifecycle(self):
        """Tests teacher starting and ending in-app stream."""
        self.login_teacher()

        # Start stream
        res_start = self.client.post(
            f"/bhavishya/api/lecture/{self.lecture_id}/stream_start",
            json={"room_id": f"room-{self.lecture_id}"}
        )
        self.assertEqual(res_start.status_code, 200)
        data_start = res_start.get_json()
        self.assertTrue(data_start.get("success"))
        self.assertTrue(data_start.get("is_live"))

        # Verify status endpoint reflects live
        res_status = self.client.get(f"/bhavishya/api/lecture/{self.lecture_id}/stream_status")
        self.assertTrue(res_status.get_json().get("is_live"))

        # End stream
        res_end = self.client.post(f"/bhavishya/api/lecture/{self.lecture_id}/stream_end")
        self.assertEqual(res_end.status_code, 200)
        data_end = res_end.get_json()
        self.assertTrue(data_end.get("success"))
        self.assertFalse(data_end.get("is_live"))

    def test_inapp_live_chat(self):
        """Tests classroom real-time live chat messages."""
        self.login_student()

        # Post message
        res_post = self.client.post(
            f"/bhavishya/api/lecture/{self.lecture_id}/chat",
            json={"message": "Sir, can you explain list comprehension again?"}
        )
        self.assertEqual(res_post.status_code, 200)
        post_data = res_post.get_json()
        self.assertTrue(post_data.get("success"))

        # Read chat
        res_get = self.client.get(f"/bhavishya/api/lecture/{self.lecture_id}/chat")
        self.assertEqual(res_get.status_code, 200)
        get_data = res_get.get_json()
        self.assertTrue(get_data.get("success"))
        messages = get_data.get("messages", [])
        self.assertGreaterEqual(len(messages), 1)
        self.assertTrue(any("list comprehension" in m.get("message", "") for m in messages))

    def test_recording_vault_upload_and_isolation(self):
        """Tests uploading stream recording to isolated database vault."""
        self.login_teacher()

        mock_video_bytes = b"SkillRock Live Lecture Recording Binary WebM Stream"
        data = {
            "recording_file": (io.BytesIO(mock_video_bytes), "test_live_rec.webm"),
            "duration_seconds": "3600"
        }
        res_upload = self.client.post(
            f"/bhavishya/api/recordings/upload/{self.lecture_id}",
            data=data,
            content_type="multipart/form-data"
        )
        self.assertEqual(res_upload.status_code, 200)
        upload_data = res_upload.get_json()
        self.assertTrue(upload_data.get("success"))
        self.assertIn("file_url", upload_data)

        # Verify retrieval from vault API
        res_rec = self.client.get(f"/bhavishya/api/recordings/{self.lecture_id}")
        self.assertEqual(res_rec.status_code, 200)
        rec_data = res_rec.get_json()
        self.assertTrue(rec_data.get("success"))
        self.assertTrue(rec_data.get("has_recording"))
        self.assertIn("static/recordings/bhavishya", rec_data.get("recording", {}).get("file_url", ""))

    def test_dashboard_and_subject_detail_clean(self):
        """Verifies Bhavishya dashboard and subject detail pages do not contain Google Meet buttons."""
        res_dash = self.client.get("/bhavishya")
        self.assertEqual(res_dash.status_code, 200)
        dash_html = res_dash.get_data(as_text=True)
        self.assertNotIn("Join Google Meet", dash_html)
        self.assertNotIn("https://meet.google.com", dash_html)

        res_subj = self.client.get("/bhavishya/subject/python")
        self.assertEqual(res_subj.status_code, 200)
        subj_html = res_subj.get_data(as_text=True)
        self.assertNotIn("Join Google Meet", subj_html)
        self.assertNotIn("https://meet.google.com", subj_html)


if __name__ == "__main__":
    unittest.main()
