"""
Empirical Adversarial Challenge Suite for Milestone 1:
Automatic Course Enrollment & Authentication Enforcement (Requirement R1)

Authored by: teamwork_challenger_m1_1 (Empirical Challenger)
Integrity mode: development / mongomock

Stress Dimensions:
1. Open Redirect Vector Fuzzing (//evil.com, /\\, backslashes, schemes, whitespace, encoded slashes)
2. Concurrency, Race Conditions & Rapid Start Idempotency
3. Existing Student Progress Retention Under Repeated Start/Enroll Triggers
4. Malformed Slugs, Path Traversal, XSS, and SQL Injection in Start Routes
5. Registration & Login Flow Robustness with Malformed vs Real Next Parameters
6. Unauthenticated Lesson Video Stream Protection & Gating Integrity
"""

import os
import unittest
import threading
from urllib.parse import unquote, urlparse
from concurrent.futures import ThreadPoolExecutor

# Force in-memory mongomock for fast, isolated verification
os.environ["MONGODB_URI"] = ""
os.environ["TESTING"] = "1"

import models.mongo as mongo_mod
mongo_mod._db = None
mongo_mod._mongo_client = None

from app import create_app
from models import (
    get_db,
    User,
    Course,
    Enrollment,
    ensure_default_courses
)


class TestM1AdversarialChallenge(unittest.TestCase):
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
            courses = Course.find_all()
            if not courses:
                raise RuntimeError("Default courses could not be initialized.")
            cls.course = courses[0]
            cls.course_slug = cls.course.slug or "python-full-stack"
            cls.course_id = str(cls.course.id)

    def setUp(self):
        self.db = get_db()
        User._user_cache.clear()
        # Clean challenge test users and enrollments
        self.db.users.delete_many({"email": {"$regex": r"^challenger_.*@skillrock\.org$"}})
        self.db.enrollments.delete_many({})

    def tearDown(self):
        self.db.users.delete_many({"email": {"$regex": r"^challenger_.*@skillrock\.org$"}})
        self.db.enrollments.delete_many({})

    # =========================================================================
    # 1. Open Redirect Vector Fuzzing
    # =========================================================================
    def test_adv_01a_register_never_redirects_off_domain(self):
        """
        Adversarial fuzzing of next parameter on GET /register with open redirect payloads.
        Must never issue a 302 Location pointing off-domain or into dangerous schemes.
        """
        malicious_payloads = [
            "//evil.com",
            "///evil.com",
            "////evil.com",
            "/\\evil.com",
            "\\/evil.com",
            "\\\\evil.com",
            "https://attacker.com",
            "http://attacker.com",
            "http://attacker.com/learning/courses/python",
            "javascript:alert(1)",
            "javascript://attacker.com/%0Aalert(1)",
            "data:text/html;base64,PHNjcmlwdD5hbGVydCgxKTwvc2NyaXB0Pg==",
            "vbscript:msgbox(1)",
            "%2F%2Fevil.com",
            "https://evil.com%2F%40skillrock.org",
            "//google.com%2f..",
            "http://localhost.evil.com",
            "http://127.0.0.1.evil.com",
            "   //evil.com",
            "/evil.com/..//attacker.com",
            "\\\\attacker.com\\share",
        ]

        for payload in malicious_payloads:
            with self.subTest(payload=payload):
                res = self.client.get(f"/register?next={payload}", follow_redirects=False)
                self.assertIn(res.status_code, [200, 302, 303], f"Unexpected status {res.status_code} for {payload}")
                if res.status_code in [302, 303]:
                    loc = res.headers.get("Location", "")
                    parsed = urlparse(loc)
                    # Destination host MUST NOT be external
                    self.assertNotIn(parsed.netloc, ["evil.com", "attacker.com", "localhost.evil.com", "127.0.0.1.evil.com"],
                                     f"Open redirect destination host detected: {parsed.netloc}")
                    self.assertFalse(loc.startswith("javascript:"), f"Dangerous javascript scheme in redirect: {loc}")
                    self.assertFalse(loc.startswith("data:"), f"Dangerous data scheme in redirect: {loc}")
                    # Path must be local login route
                    self.assertTrue(parsed.path in ["/login", "/signin", "/register"] or parsed.path.startswith("/learning"),
                                    f"Unexpected redirect path: {parsed.path}")

    def test_adv_01b_unsafe_next_propagation_behavior(self):
        """
        Empirically test whether GET /register strips unsafe next parameters or forwards them to /login.
        Checks routes/auth.py line 404 behavior where **request.args retains unsafe next.
        """
        res = self.client.get("/register?next=//evil.com", follow_redirects=False)
        self.assertEqual(res.status_code, 302)
        loc = res.headers.get("Location", "")
        # Record whether the unsafe query parameter is forwarded to /login
        has_forwarded_unsafe_next = "next=" in loc and "evil.com" in loc
        # Document this finding empirically
        self.assertTrue(has_forwarded_unsafe_next,
                        "Expected empirical observation: register forwarded unsafe next via **request.args")


    def test_adv_02_open_redirect_vectors_in_login_post(self):
        """
        Adversarial POST to /login with open redirect payloads in form next field.
        Must authenticate safely without redirecting to external malicious hosts.
        """
        # Create an existing user
        user = User.create(
            name="Login Target User",
            email="challenger_login_redirect@skillrock.org",
            college="Test College",
            branch="CS",
            year="2nd Year",
            xp=100
        )
        user.set_password("TargetSecret123")
        user.save()

        malicious_payloads = [
            "//evil.com",
            "https://attacker.com/pwned",
            "/\\evil.com/path",
            "javascript:alert(document.cookie)",
            "\\\\attacker.com\\share",
        ]

        for payload in malicious_payloads:
            with self.subTest(payload=payload):
                res = self.client.post("/login", data={
                    "email": "challenger_login_redirect@skillrock.org",
                    "password": "TargetSecret123",
                    "next": payload
                }, follow_redirects=False)

                self.assertIn(res.status_code, [302, 303])
                loc = res.headers.get("Location", "")
                self.assertNotIn("evil.com", loc)
                self.assertNotIn("attacker.com", loc)
                self.assertFalse(loc.startswith("javascript:"))
                # Should safely redirect to default local page (courses or interests)
                self.assertTrue(loc.startswith("/") and not loc.startswith("//"))

    # =========================================================================
    # 2. Race Conditions & Rapid Start Idempotency
    # =========================================================================
    def test_adv_03_concurrent_start_learning_race_condition(self):
        """
        Execute 10 concurrent requests to /learning/courses/<slug>/start for the same authenticated user.
        Must result in exactly ONE enrollment record in MongoDB without 500 server errors or duplicate key crashes.
        """
        user = User.create(
            name="Race Student",
            email="challenger_race@skillrock.org",
            college="Race Institute",
            branch="Concurrency",
            year="3rd Year"
        )
        user.set_password("RacePassword123")
        user.save()

        # Log in the user to obtain session cookie
        login_res = self.client.post("/login", data={
            "email": "challenger_race@skillrock.org",
            "password": "RacePassword123"
        }, follow_redirects=False)
        self.assertIn(login_res.status_code, [302, 303])

        results = []
        def hit_start():
            # Use test client to request start endpoint
            r = self.client.get(f"/learning/courses/{self.course_slug}/start", follow_redirects=False)
            results.append(r.status_code)

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(hit_start) for _ in range(10)]
            for f in futures:
                f.result()

        # None of the requests should crash with 500
        for code in results:
            self.assertIn(code, [302, 303], f"Concurrent request returned unexpected status {code}")

        # Verify MongoDB has exactly 1 enrollment for this user and course
        enrollments = list(self.db.enrollments.find({
            "user_id": str(user.id),
            "course_id": str(self.course.id)
        }))
        self.assertEqual(len(enrollments), 1, f"Expected exactly 1 enrollment record, found {len(enrollments)}")

    # =========================================================================
    # 3. Existing Student Progress Retention Under Repeated Triggers
    # =========================================================================
    def test_adv_04_watch_progress_retention_across_multiple_start_methods(self):
        """
        A student who is already 75% through a course (with 2700 watch seconds)
        must NOT have their progress wiped or reset when:
        1. Hitting /learning/courses/<slug>/start
        2. Hitting /learning/courses/<slug>?start=1
        3. Logging in again with next=/learning/courses/<slug>
        """
        user = User.create(
            name="Progress Student",
            email="challenger_progress@skillrock.org",
            college="Progress College",
            branch="IT",
            year="4th Year"
        )
        user.set_password("ProgressPass123")
        user.save()

        # Create an existing enrollment with 75% progress and specific watch time
        self.db.enrollments.insert_one({
            "user_id": str(user.id),
            "course_id": str(self.course.id),
            "status": "in_progress",
            "watch_percent": 75,
            "last_position_seconds": 2700,
            "video_completed": False
        })

        # Log in
        self.client.post("/login", data={
            "email": "challenger_progress@skillrock.org",
            "password": "ProgressPass123"
        }, follow_redirects=False)

        # Trigger 1: GET /courses/<slug>/start
        res1 = self.client.get(f"/learning/courses/{self.course_slug}/start", follow_redirects=False)
        self.assertEqual(res1.status_code, 302)

        enr1 = self.db.enrollments.find_one({"user_id": str(user.id), "course_id": str(self.course.id)})
        self.assertEqual(enr1.get("watch_percent"), 75, "Trigger 1 wiped watch_percent!")
        self.assertEqual(enr1.get("last_position_seconds"), 2700, "Trigger 1 wiped last_position_seconds!")

        # Trigger 2: GET /courses/<slug>?start=1
        res2 = self.client.get(f"/learning/courses/{self.course_slug}?start=1", follow_redirects=False)
        self.assertEqual(res2.status_code, 200)

        enr2 = self.db.enrollments.find_one({"user_id": str(user.id), "course_id": str(self.course.id)})
        self.assertEqual(enr2.get("watch_percent"), 75, "Trigger 2 wiped watch_percent!")
        self.assertEqual(enr2.get("last_position_seconds"), 2700, "Trigger 2 wiped last_position_seconds!")

        # Trigger 3: Re-login with next=/learning/courses/<slug>
        self.client.get("/logout", follow_redirects=True)
        res3 = self.client.post("/login", data={
            "email": "challenger_progress@skillrock.org",
            "password": "ProgressPass123",
            "next": f"/learning/courses/{self.course_slug}"
        }, follow_redirects=False)
        self.assertEqual(res3.status_code, 302)

        enr3 = self.db.enrollments.find_one({"user_id": str(user.id), "course_id": str(self.course.id)})
        self.assertEqual(enr3.get("watch_percent"), 75, "Trigger 3 (re-login) wiped watch_percent!")
        self.assertEqual(enr3.get("last_position_seconds"), 2700, "Trigger 3 (re-login) wiped last_position_seconds!")

    # =========================================================================
    # 4. Malformed Slugs, Injections, and Edge Cases
    # =========================================================================
    def test_adv_05_malformed_and_injection_slugs_in_start_route(self):
        """
        Adversarial course slugs (SQL injection, XSS, Path Traversal, Null Bytes, Unicode)
        passed to /learning/courses/<slug>/start must not trigger uncaught 500 exceptions.
        """
        adversarial_slugs = [
            "non-existent-course-slug-99999",
            "' OR '1'='1",
            "<script>alert(1)</script>",
            "../../etc/passwd",
            "..\\..\\windows\\system32",
            "%00nullbyte",
            "🐍💻🚀-unicode-slug",
            "A" * 2000,  # Buffer stress
            "!@#$%^&*()_+-=[]{}|;':,.<>/?",
        ]

        for slug in adversarial_slugs:
            with self.subTest(slug=slug[:30]):
                res = self.client.get(f"/learning/courses/{slug}/start", follow_redirects=False)
                # Must handle gracefully: either redirect (302) to courses list / register, or return 404
                self.assertIn(res.status_code, [302, 303, 404], f"Slug '{slug[:20]}' triggered status {res.status_code}")
                self.assertNotEqual(res.status_code, 500, f"Slug '{slug[:20]}' caused a 500 server crash!")

    def test_adv_06_malformed_query_parameters_in_start_and_detail(self):
        """
        Malformed or unexpected query parameters on /courses/<slug> and /courses/<slug>/start
        must not cause runtime crashes.
        """
        malformed_queries = [
            "?start=invalid_boolean_string",
            "?player=not_an_int",
            "?player=9999999999999999999999999999999999999999",
            "?start=1&start=2&start=true",
            "?next=&&&&&&",
            "?enrol=true&start=0",
        ]

        for q in malformed_queries:
            with self.subTest(query=q):
                res = self.client.get(f"/learning/courses/{self.course_slug}{q}")
                self.assertIn(res.status_code, [200, 302, 303])
                self.assertNotEqual(res.status_code, 500)

    # =========================================================================
    # 5. Registration Flow with Malformed vs Real Next Parameters
    # =========================================================================
    def test_adv_07_new_user_registration_with_real_course_auto_enrolls(self):
        """
        Registering a new account with a valid course target in next must:
        1. Create new user account
        2. Auto-enroll into the course immediately
        3. Redirect directly to the course player frame (player=1#skillrockPlayerFrame)
        """
        reg_data = {
            "name": "New Valid Course Student",
            "email": "challenger_new_valid@skillrock.org",
            "password": "SecurePassword123!",
            "college": "Engineering Institute",
            "branch": "Computer Science",
            "year": "1st Year",
            "next": f"/learning/courses/{self.course_slug}"
        }

        res = self.client.post("/login", data=reg_data, follow_redirects=False)
        self.assertEqual(res.status_code, 302)
        loc = res.headers.get("Location", "")
        self.assertIn(self.course_slug, loc)
        self.assertIn("player=1", loc)
        self.assertIn("#skillrockPlayerFrame", loc)

        # Check DB enrollment
        new_user = User.get_by_email("challenger_new_valid@skillrock.org")
        self.assertIsNotNone(new_user)
        enr = self.db.enrollments.find_one({"user_id": str(new_user.id), "course_id": str(self.course.id)})
        self.assertIsNotNone(enr, "New user was not enrolled in course upon registration with next param")

    def test_adv_08_new_user_registration_with_malformed_course_slug(self):
        """
        Registering a new account with next targeting a non-existent course slug:
        Must create account, must NOT raise 500 exception, and must fallback gracefully.
        """
        reg_data = {
            "name": "New Bogus Course Student",
            "email": "challenger_new_bogus@skillrock.org",
            "password": "SecurePassword123!",
            "college": "Testing College",
            "branch": "IT",
            "year": "2nd Year",
            "next": "/learning/courses/this-slug-does-not-exist-at-all-12345"
        }

        res = self.client.post("/login", data=reg_data, follow_redirects=False)
        self.assertIn(res.status_code, [302, 303])
        self.assertNotEqual(res.status_code, 500)

        new_user = User.get_by_email("challenger_new_bogus@skillrock.org")
        self.assertIsNotNone(new_user)

    def test_adv_09_new_user_registration_with_non_course_safe_next(self):
        """
        Registering a new account with next targeting a safe non-course page (e.g. /learning):
        Must create account and redirect safely to the non-course local page.
        """
        reg_data = {
            "name": "New Non Course Student",
            "email": "challenger_new_noncourse@skillrock.org",
            "password": "SecurePassword123!",
            "next": "/learning"
        }

        res = self.client.post("/login", data=reg_data, follow_redirects=False)
        self.assertIn(res.status_code, [302, 303])
        loc = res.headers.get("Location", "")
        self.assertIn("/learning", loc)

    # =========================================================================
    # 6. Learning Content Gating & Route Protection
    # =========================================================================
    def test_adv_10_unauthenticated_visitor_cannot_stream_or_load_player(self):
        """
        Unauthenticated visitor GET /learning/courses/<slug>:
        - Must NOT contain YouTube player iframe (#skillrockYtPlayer)
        - Must NOT contain YouTube iframe API (<script src="...youtube.com/iframe_api">)
        - Must contain locked preview overlay and 'Start Learning' action
        """
        res = self.client.get(f"/learning/courses/{self.course_slug}")
        self.assertEqual(res.status_code, 200)
        html = res.get_data(as_text=True)

        self.assertNotIn('id="skillrockYtPlayer"', html, "Unauthenticated visitor received YouTube player container!")
        self.assertNotIn("https://www.youtube.com/iframe_api", html, "Unauthenticated visitor received YouTube iframe API script!")
        self.assertIn("Start Learning", html, "Course preview page must feature 'Start Learning' action")

    def test_adv_11_authenticated_student_receives_player_and_api(self):
        """
        Authenticated student GET /learning/courses/<slug>:
        - MUST contain the interactive YouTube player container
        - MUST contain the YouTube iframe API script
        """
        user = User.create(
            name="Enrolled Viewer",
            email="challenger_viewer@skillrock.org",
            college="Player College",
            branch="Media",
            year="3rd Year"
        )
        user.set_password("ViewerPass123!")
        user.save()

        # Log in
        self.client.post("/login", data={
            "email": "challenger_viewer@skillrock.org",
            "password": "ViewerPass123!"
        }, follow_redirects=False)

        res = self.client.get(f"/learning/courses/{self.course_slug}")
        self.assertEqual(res.status_code, 200)
        html = res.get_data(as_text=True)

        self.assertIn('id="skillrockYtPlayer"', html, "Authenticated student did not receive YouTube player!")
        self.assertIn("https://www.youtube.com/iframe_api", html, "Authenticated student did not receive YouTube iframe API script!")

    # =========================================================================
    # 7. Additional Adversarial Surface: OAuth, Ref Resolution & Session Gating
    # =========================================================================
    def test_adv_12_google_oauth_next_retention_and_sanitization(self):
        """
        GET /auth/google?next=...:
        - Valid course next target must be recorded in session['oauth_next']
        - Malicious next target (//evil.com) must be sanitized to fallback (/learning/courses)
        """
        # Case A: Valid course target
        valid_next = f"/learning/courses/{self.course_slug}"
        with self.client as c:
            c.get(f"/auth/google?next={valid_next}")
            from flask import session
            self.assertEqual(session.get("oauth_next"), valid_next)

        # Case B: Malicious open redirect target
        with self.client as c:
            c.get("/auth/google?next=//evil.com")
            from flask import session
            oauth_target = session.get("oauth_next", "")
            self.assertNotIn("evil.com", oauth_target)
            self.assertTrue(oauth_target.startswith("/learning"))

    def test_adv_13_auto_enroll_target_ref_formats(self):
        """
        auto_enroll_student_in_course must robustly handle diverse target_ref representations:
        - Raw slug
        - Raw ObjectId
        - Relative path: /learning/courses/<slug>
        - Path with query params: /learning/courses/<slug>?player=1
        - Path with anchor: /learning/courses/<slug>#skillrockPlayerFrame
        - Full URL: http://localhost:5000/learning/courses/<slug>
        """
        from routes.learning import auto_enroll_student_in_course

        user = User.create(
            name="Format Student",
            email="challenger_formats@skillrock.org",
            college="Testing University",
            branch="QA",
            year="4th Year"
        )
        user.set_password("Pass123!")
        user.save()

        # Log in
        self.client.post("/login", data={"email": "challenger_formats@skillrock.org", "password": "Pass123!"})

        target_variants = [
            self.course_slug,
            str(self.course.id),
            f"/learning/courses/{self.course_slug}",
            f"/learning/courses/{self.course_slug}?player=1&start=1",
            f"/learning/courses/{self.course_slug}#skillrockPlayerFrame",
            f"http://localhost:5000/learning/courses/{self.course_slug}?start=1#frame",
        ]

        for variant in target_variants:
            with self.subTest(variant=variant):
                resolved_course = auto_enroll_student_in_course(user, variant)
                self.assertIsNotNone(resolved_course, f"Failed to resolve course with target_ref variant: {variant}")
                self.assertEqual(str(resolved_course.id), str(self.course.id))

        # Check only 1 enrollment was created despite 6 calls with different format variants
        enrs = list(self.db.enrollments.find({"user_id": str(user.id), "course_id": str(self.course.id)}))
        self.assertEqual(len(enrs), 1, "Format variants created duplicate enrollment records!")

    def test_adv_14_unauthenticated_api_save_progress_rejected(self):
        """Unauthenticated requests to /learning/save-progress must be rejected with 401 or redirect to login."""
        res = self.client.post("/learning/save-progress", json={
            "course_id": str(self.course.id),
            "watch_percent": 80,
            "last_position_seconds": 3000
        })
        self.assertIn(res.status_code, [302, 303, 401, 403], f"Unauthenticated API call returned {res.status_code}")

    def test_adv_15_case_insensitive_email_registration_and_enrollment(self):
        """Mixed-case email in registration/login (e.g. Challenger_MixedCase@SkillRock.org) auto-enrolls correctly."""
        reg_data = {
            "name": "Case Sensitive Student",
            "email": "Challenger_MixedCase@SkillRock.org",
            "password": "Password123!",
            "next": f"/learning/courses/{self.course_slug}"
        }
        res = self.client.post("/login", data=reg_data, follow_redirects=False)
        self.assertEqual(res.status_code, 302)
        loc = res.headers.get("Location", "")
        self.assertIn(self.course_slug, loc)
        self.assertIn("player=1", loc)

        # Check DB user was saved with normalized email and enrolled
        user = User.get_by_email("challenger_mixedcase@skillrock.org")
        self.assertIsNotNone(user)
        enr = self.db.enrollments.find_one({"user_id": str(user.id), "course_id": str(self.course.id)})
        self.assertIsNotNone(enr)


if __name__ == "__main__":
    unittest.main()

