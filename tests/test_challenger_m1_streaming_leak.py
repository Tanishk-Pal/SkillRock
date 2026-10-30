"""
Empirical Adversarial Challenge Harness for Milestone 1:
Streaming & Content Leak Gating (R1)

Conducted by: teamwork_challenger_m1_2 (Empirical Challenger)
Target: SkillRock Web Application - Milestone 1

Hypotheses Tested:
1. Unauthenticated Raw HTML Content Leakage across all published courses
2. Query Parameter Forging & Tampering Attacks (?player=1, ?start=1, ?stream=1, ?auth=true, etc.)
3. Header Spoofing & Session Tampering
4. Unauthenticated Progress & Enrollment API Invocations (/learning/save-progress, /learning/progress/save, /learning/enrol/<id>)
5. Course /start Endpoint Fuzzing, Path Traversal & Injection Resiliency
6. Open Redirect Evasion & Schema Tampering
7. Authenticated Enrolled Student Positive Oracle & Progress Integrity
8. Concurrency & Idempotency Stress
"""

import os
import re
import unittest
from urllib.parse import unquote

# Force mongomock for fast, isolated in-memory unit testing
os.environ["MONGODB_URI"] = ""
os.environ["TESTING"] = "1"

import models.mongo as mongo_mod
mongo_mod._db = None
mongo_mod._mongo_client = None

from flask import url_for
from app import create_app
from models import (
    get_db,
    User,
    Course,
    Enrollment,
    ensure_default_courses
)
from routes.learning import auto_enroll_student_in_course
from routes.auth import is_safe_url


class TestMilestone1AdversarialChallenge(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        mongo_mod._db = None
        mongo_mod._mongo_client = None
        cls.app = create_app()
        cls.app.config["TESTING"] = True
        cls.app.config["WTF_CSRF_ENABLED"] = False
        cls.client = cls.app.test_client()

        with cls.app.app_context():
            ensure_default_courses()
            cls.all_courses = Course.find_all()
            assert len(cls.all_courses) > 0, "Default courses must be populated"
            cls.test_course = cls.all_courses[0]
            cls.test_slug = cls.test_course.slug

    def setUp(self):
        self.db = get_db()
        User._user_cache.clear()
        self.db.users.delete_many({"email": {"$regex": r"^challenger_.*@skillrock\.org$"}})
        self.db.enrollments.delete_many({})

    def tearDown(self):
        self.db.users.delete_many({"email": {"$regex": r"^challenger_.*@skillrock\.org$"}})
        self.db.enrollments.delete_many({})

    # =========================================================================
    # CHALLENGE 1: All Published Courses Raw HTML Content Leak Audit
    # =========================================================================
    def test_challenge_01_all_courses_unauthenticated_leak_audit(self):
        """
        Verify that for EVERY course in the database, an unauthenticated GET
        to the course detail route returns 200 without exposing:
        - Iframe players (<iframe)
        - YouTube API player initialization scripts (initYouTubePlayer)
        - Official YouTube Iframe API script (youtube.com/iframe_api)
        - Active player mount point (id="skillrockYtPlayer")
        - Custom player control bar (skillrock-controls-bar)
        - Click / top shields (player-click-shield, player-top-shield)
        - Direct youtube.com/embed links
        """
        self.assertGreater(len(self.all_courses), 0)
        courses_tested = 0

        for course in self.all_courses:
            slug = course.slug or course.id
            resp = self.client.get(f"/learning/courses/{slug}")
            self.assertEqual(resp.status_code, 200, f"Course {slug} detail page should return 200")
            html = resp.get_data(as_text=True)

            # Assert strict absence of playable video components
            self.assertNotIn('<iframe', html, f"Course {slug} leaks <iframe> to unauthenticated visitors!")
            self.assertNotIn('id="skillrockYtPlayer"', html, f"Course {slug} exposes #skillrockYtPlayer to unauthenticated visitors!")
            self.assertNotIn('https://www.youtube.com/iframe_api', html, f"Course {slug} loads YouTube iframe API for unauthenticated visitors!")
            self.assertNotIn('initYouTubePlayer', html, f"Course {slug} leaks initYouTubePlayer script to unauthenticated visitors!")
            self.assertNotIn('skillrock-controls-bar', html, f"Course {slug} renders skillrock-controls-bar for unauthenticated visitors!")
            self.assertNotIn('player-click-shield', html, f"Course {slug} renders player-click-shield for unauthenticated visitors!")
            self.assertNotIn('player-top-shield', html, f"Course {slug} renders player-top-shield for unauthenticated visitors!")
            self.assertNotIn('https://www.youtube.com/embed', html, f"Course {slug} leaks youtube.com/embed link in HTML to unauthenticated visitors!")

            # Assert presence of restricted preview gating UI
            self.assertIn("Restricted Course Content", html, f"Course {slug} missing 'Restricted Course Content' header")
            self.assertIn("Start Learning", html, f"Course {slug} missing 'Start Learning' CTA")
            self.assertIn("Sign Up Free to Stream Lessons", html, f"Course {slug} missing registration prompt")
            courses_tested += 1

        print(f"\n[CHALLENGE 1 PASSED] Verified {courses_tested} courses: zero content leaks detected.")

    # =========================================================================
    # CHALLENGE 2: Query Parameter Forging & Tampering Attacks
    # =========================================================================
    def test_challenge_02_query_parameter_forging_bypasses(self):
        """
        Adversarially inject common bypass query parameters into unauthenticated
        GET requests to verify they CANNOT trick the template or view into rendering
        the video player or iframe.
        """
        tampered_params = [
            "?player=1",
            "?player=true",
            "?start=1",
            "?start=true",
            "?stream=1",
            "?stream=true",
            "?auth=1",
            "?auth=true",
            "?authenticated=1",
            "?authenticated=true",
            "?is_authenticated=1",
            "?is_authenticated=true",
            "?enrol=1",
            "?enrol=true",
            "?preview=0",
            "?preview=false",
            "?admin=1",
            "?role=admin",
            "?current_user=admin",
            "?force_player=1",
            "?embed=1",
            "?watch=1",
            "?player=1&start=1&stream=1&auth=true&admin=1&enrol=1"
        ]

        for param in tampered_params:
            url = f"/learning/courses/{self.test_slug}{param}"
            resp = self.client.get(url)
            self.assertEqual(resp.status_code, 200, f"Query parameter {param} caused unexpected status code {resp.status_code}")
            html = resp.get_data(as_text=True)

            self.assertNotIn('<iframe', html, f"Query param {param} unlocked <iframe>!")
            self.assertNotIn('id="skillrockYtPlayer"', html, f"Query param {param} unlocked #skillrockYtPlayer!")
            self.assertNotIn('https://www.youtube.com/iframe_api', html, f"Query param {param} unlocked iframe API!")
            self.assertNotIn('initYouTubePlayer', html, f"Query param {param} unlocked initYouTubePlayer!")
            self.assertNotIn('https://www.youtube.com/embed', html, f"Query param {param} unlocked embed URL!")
            self.assertIn("Restricted Course Content", html, f"Query param {param} bypassed restricted overlay!")

        print(f"\n[CHALLENGE 2 PASSED] Tested {len(tampered_params)} parameter tampering vectors: all rejected.")

    # =========================================================================
    # CHALLENGE 3: Header Spoofing & Session Tampering Attacks
    # =========================================================================
    def test_challenge_03_header_spoofing_attacks(self):
        """
        Adversarially send requests with spoofed proxy/identity headers
        to ensure Flask-Login does not honor unauthenticated client headers.
        """
        spoofed_header_sets = [
            {"X-Forwarded-User": "admin"},
            {"X-Remote-User": "admin"},
            {"X-User-Id": "1"},
            {"X-Authenticated": "true"},
            {"X-Role": "admin"},
            {"Authorization": "Bearer evil-token"},
            {"Cookie": "remember_token=evil; session=evil"}
        ]

        for headers in spoofed_header_sets:
            resp = self.client.get(f"/learning/courses/{self.test_slug}", headers=headers)
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertNotIn('<iframe', html, f"Spoofed headers {headers} unlocked <iframe>!")
            self.assertNotIn('id="skillrockYtPlayer"', html, f"Spoofed headers {headers} unlocked #skillrockYtPlayer!")
            self.assertNotIn('initYouTubePlayer', html, f"Spoofed headers {headers} unlocked script!")

        print(f"\n[CHALLENGE 3 PASSED] Tested {len(spoofed_header_sets)} header spoofing attacks: all safely ignored.")

    # =========================================================================
    # CHALLENGE 4: Unauthenticated Mutation & Progress API Rejection
    # =========================================================================
    def test_challenge_04_unauthenticated_api_rejections(self):
        """
        Verify that all learning mutation endpoints reject unauthenticated
        calls and do NOT modify database state or record false progress.
        """
        course_id_str = str(self.test_course.id)

        # 1. /learning/save-progress (JSON POST)
        resp1 = self.client.post("/learning/save-progress", json={
            "course_id": course_id_str,
            "watch_seconds": 1500,
            "video_duration": 3600
        })
        self.assertIn(resp1.status_code, [302, 303, 401, 403], "Unauthenticated /learning/save-progress must reject")
        self.assertEqual(self.db.enrollments.count_documents({}), 0, "No enrollment created on unauth save-progress")

        # 2. /learning/progress/save (JSON POST alias)
        resp2 = self.client.post("/learning/progress/save", json={
            "course_id": course_id_str,
            "watch_seconds": 1500,
            "video_duration": 3600
        })
        self.assertIn(resp2.status_code, [302, 303, 401, 403], "Unauthenticated /learning/progress/save must reject")
        self.assertEqual(self.db.enrollments.count_documents({}), 0, "No enrollment created on unauth progress/save")

        # 3. Form-encoded progress save attempt
        resp3 = self.client.post("/learning/save-progress", data={
            "course_id": course_id_str,
            "watch_seconds": "1500"
        })
        self.assertIn(resp3.status_code, [302, 303, 401, 403])
        self.assertEqual(self.db.enrollments.count_documents({}), 0)

        # 4. /learning/enrol/<course_id> (POST)
        resp4 = self.client.post(f"/learning/enrol/{course_id_str}")
        self.assertIn(resp4.status_code, [302, 303, 401, 403], "Unauthenticated /learning/enrol must redirect to login")
        self.assertEqual(self.db.enrollments.count_documents({}), 0, "No enrollment created on unauth enrol call")

        # 5. Non-existent /learning/api/save-progress
        resp5 = self.client.post("/learning/api/save-progress", json={"course_id": course_id_str})
        self.assertIn(resp5.status_code, [404, 302, 303, 401, 403])
        self.assertEqual(self.db.enrollments.count_documents({}), 0)

        print("\n[CHALLENGE 4 PASSED] Unauthenticated API endpoints strictly rejected; database remained unmodified.")

    # =========================================================================
    # CHALLENGE 5: Course /start Endpoint Fuzzing & Injection Defense
    # =========================================================================
    def test_challenge_05_start_endpoint_fuzzing_and_injection(self):
        """
        Fuzz and inject adversarial payloads into /learning/courses/<slug>/start:
        - Unauthenticated access redirects to /register?next=...
        - Extra query parameters on start endpoint
        - Non-existent slugs
        - Special characters, XSS attempts, SQLi attempts, and path traversals
        """
        # Baseline valid slug
        res = self.client.get(f"/learning/courses/{self.test_slug}/start")
        self.assertEqual(res.status_code, 302)
        loc = unquote(res.headers.get("Location", ""))
        self.assertIn("/register", loc)
        self.assertIn(self.test_slug, loc)

        # With extra parameters
        res_params = self.client.get(f"/learning/courses/{self.test_slug}/start?player=1&enrol=1")
        self.assertEqual(res_params.status_code, 302)
        loc_params = unquote(res_params.headers.get("Location", ""))
        self.assertIn("/register", loc_params)
        self.assertIn(self.test_slug, loc_params)

        # Fuzz payloads
        fuzz_slugs = [
            "non-existent-course-slug-99999",
            "<script>alert(1)</script>",
            "../../etc/passwd",
            "..%2F..%2Fetc%2Fpasswd",
            "' OR '1'='1",
            "course-slug; DROP TABLE courses;--",
            "A" * 500,
            "%00nullbyte"
        ]

        for bad_slug in fuzz_slugs:
            res_bad = self.client.get(f"/learning/courses/{bad_slug}/start")
            # Should gracefully redirect or 404, never 500
            self.assertIn(res_bad.status_code, [302, 303, 404],
                          f"Fuzz slug '{bad_slug}' produced unexpected status {res_bad.status_code}")
            if res_bad.status_code in [302, 303]:
                bad_loc = res_bad.headers.get("Location", "")
                self.assertNotIn("<script>", bad_loc)

        print(f"\n[CHALLENGE 5 PASSED] Tested {len(fuzz_slugs)} fuzz and injection payloads on /start without server error.")

    # =========================================================================
    # CHALLENGE 6: Open Redirect Evasion & Schema Tampering
    # =========================================================================
    def test_challenge_06_open_redirect_evasion(self):
        """
        Verify that is_safe_url rejects sneaky open redirect evasion vectors.
        """
        evasion_vectors = [
            "https://evil.com",
            "http://evil.com",
            "//evil.com",
            "///evil.com",
            "/\\evil.com",
            "\\/evil.com",
            "\\\\evil.com",
            "javascript:alert(1)",
            "data:text/html,<script>alert(1)</script>",
            "vbscript:msgbox(1)",
            "http://localhost:5000@evil.com",
            "https://skillrock.org@evil.com",
            "/learning/courses/test%0d%0aSet-Cookie:bad=1"
        ]

        for evil_url in evasion_vectors:
            self.assertFalse(is_safe_url(evil_url), f"is_safe_url incorrectly trusted malicious URL: {evil_url}")

            # Also test through POST /login with the payload
            resp = self.client.post("/login", data={
                "email": "challenger_redirect@skillrock.org",
                "password": "Password123!",
                "next": evil_url
            }, follow_redirects=False)
            self.assertEqual(resp.status_code, 302)
            loc = resp.headers.get("Location", "")
            self.assertFalse(loc.startswith("https://evil.com"))
            self.assertFalse(loc.startswith("//evil.com"))
            self.assertFalse(loc.startswith("javascript:"))

        print(f"\n[CHALLENGE 6 PASSED] Tested {len(evasion_vectors)} open redirect evasion vectors: all rejected.")

    # =========================================================================
    # CHALLENGE 7: Authenticated Enrolled Student Positive Oracle
    # =========================================================================
    def test_challenge_07_authenticated_student_positive_oracle(self):
        """
        Verify that an authenticated user who starts a course:
        1. Auto-enrolls without requiring any manual step.
        2. Successfully navigates to the player (?player=1#skillrockPlayerFrame).
        3. Receives the complete, interactive video player with controls.
        4. Successfully reports watch progress via POST /learning/save-progress.
        """
        student_email = "challenger_student_auth@skillrock.org"
        user = User.create(email=student_email, name="Challenger Student")
        user.set_password("SecurePassword123!")
        user.save()

        # Log in
        login_res = self.client.post("/login", data={"email": student_email, "password": "SecurePassword123!"})
        self.assertEqual(login_res.status_code, 302)

        # Confirm unenrolled
        self.assertIsNone(Enrollment.get_by_user_course(user.id, self.test_course.id))

        # Invoke /learning/courses/<slug>/start
        start_res = self.client.get(f"/learning/courses/{self.test_slug}/start", follow_redirects=False)
        self.assertEqual(start_res.status_code, 302)
        loc = start_res.headers.get("Location", "")
        self.assertIn(self.test_slug, loc)
        self.assertIn("player=1", loc)
        self.assertIn("skillrockPlayerFrame", loc)

        # Confirm enrollment exists in DB
        enrollment = Enrollment.get_by_user_course(user.id, self.test_course.id)
        self.assertIsNotNone(enrollment, "User must be enrolled in MongoDB")
        self.assertEqual(enrollment.status, "enrolled")

        # Now GET the course player page as authenticated user
        player_res = self.client.get(f"/learning/courses/{self.test_slug}?player=1")
        self.assertEqual(player_res.status_code, 200)
        html = player_res.get_data(as_text=True)

        # Assert presence of authorized player DOM elements
        self.assertIn('id="skillrockYtPlayer"', html, "Player slot must be present for authenticated enrolled user")
        self.assertIn('https://www.youtube.com/iframe_api', html, "YouTube iframe API script must load for authenticated user")
        self.assertIn('initYouTubePlayer()', html, "initYouTubePlayer function call must be present for authenticated user")
        self.assertIn('skillrock-controls-bar', html, "Custom control bar must be rendered for authenticated user")
        self.assertIn('player-click-shield', html, "Click shield must be rendered for authenticated user")
        self.assertIn('player-top-shield', html, "Top shield must be rendered for authenticated user")
        self.assertNotIn('Restricted Course Content', html, "Restricted locked card must NOT be shown to authenticated enrolled user")

        # Test authenticated save progress with legitimate initial ping (25s)
        progress_res = self.client.post("/learning/save-progress", json={
            "course_id": str(self.test_course.id),
            "watch_seconds": 25,
            "video_duration": 1800
        })
        self.assertEqual(progress_res.status_code, 200)
        json_data = progress_res.get_json()
        self.assertTrue(json_data.get("success"), f"Save progress returned non-success: {json_data}")

        # Verify DB updated
        refreshed_enrollment = Enrollment.get_by_user_course(user.id, self.test_course.id)
        self.assertEqual(refreshed_enrollment.watch_seconds, 25)

        # Test anti-skip clamp: jump attempt to 5000s without elapsed wall time
        skip_res = self.client.post("/learning/save-progress", json={
            "course_id": str(self.test_course.id),
            "watch_seconds": 5000,
            "video_duration": 1800
        })
        self.assertEqual(skip_res.status_code, 200)
        clamped_enrollment = Enrollment.get_by_user_course(user.id, self.test_course.id)
        # Should be clamped near 25 + max_allowed_delta, NOT 5000
        self.assertLess(clamped_enrollment.watch_seconds, 100, "Anti-skip must clamp unauthorized forward jump!")

        print("\n[CHALLENGE 7 PASSED] Authenticated student player access, progress recording, and anti-skip clamp verified.")

    # =========================================================================
    # CHALLENGE 8: Concurrency & Idempotency Stress
    # =========================================================================
    def test_challenge_08_concurrency_and_idempotency_stress(self):
        """
        Stress test auto_enroll_student_in_course by triggering it repeatedly
        across multiple course formats and asserting progress is never wiped.
        """
        stress_email = "challenger_stress@skillrock.org"
        user = User.create(email=stress_email, name="Stress Student")
        user.set_password("SecurePassword123!")
        user.save()

        # Pre-seed existing enrollment with 65% watch progress
        enrollment = Enrollment({
            "user_id": str(user.id),
            "course_id": str(self.test_course.id),
            "status": "in_progress",
            "watch_percent": 65,
            "watch_seconds": 2340,
            "max_watch_seconds": 2340,
            "video_duration": 3600
        })
        enrollment.save()

        # Fire 25 sequential auto-enroll calls simulating rapid multi-tab clicks
        for _ in range(25):
            auto_enroll_student_in_course(user, self.test_slug)
            auto_enroll_student_in_course(user, self.test_course.id)
            auto_enroll_student_in_course(user, f"/learning/courses/{self.test_slug}?player=1#frame")

        # Verify only 1 record exists and watch_percent is still 65%
        count = self.db.enrollments.count_documents({"user_id": str(user.id), "course_id": str(self.test_course.id)})
        self.assertEqual(count, 1, f"Expected exactly 1 enrollment document, found {count}")

        refreshed = Enrollment.get_by_user_course(user.id, self.test_course.id)
        self.assertEqual(refreshed.watch_percent, 65, "Watch percent was mutated or reset!")
        self.assertEqual(refreshed.watch_seconds, 2340, "Watch seconds was mutated or reset!")

        print("\n[CHALLENGE 8 PASSED] 75 rapid enrollment attempts executed: idempotency and progress integrity held.")


if __name__ == "__main__":
    unittest.main()
