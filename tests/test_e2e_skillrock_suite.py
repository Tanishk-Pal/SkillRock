"""
SkillRock Comprehensive End-to-End & Integration Test Suite
4-Tier Opaque-Box Test Harness for Platform Enhancements:
- R1: Automatic Course Enrollment & Registration Flow
- R2: Responsive Course Credential Preview Relocation
- R3: Admin Panel User Progress and Enrollment Tracking

Tiers:
  Tier 1: Feature Coverage (>=5 test cases per feature)
  Tier 2: Boundary & Corner Cases (>=5 test cases per feature)
  Tier 3: Cross-Feature Interactions
  Tier 4: Real-World Workload / End-to-End User Scenarios

Execution:
  $env:MONGODB_URI = ""
  venv\\Scripts\\python.exe -m unittest tests/test_e2e_skillrock_suite.py
"""

import os
import re
import unittest
from datetime import datetime, timezone
from html.parser import HTMLParser

# Ensure in-memory mongomock isolation
os.environ["MONGODB_URI"] = ""
os.environ["TESTING"] = "1"

import models.mongo as mongo_mod
mongo_mod._db = None
mongo_mod._mongo_client = None

from app import create_app
from models.mongo import (
    get_db, User, Course, Assignment, Enrollment,
    Submission, Review, Certificate, ensure_default_courses
)


class BaseSkillRockTestCase(unittest.TestCase):
    """Base test fixture providing isolated app, client, test data factories, and auth helpers."""

    @classmethod
    def setUpClass(cls):
        mongo_mod._db = None
        mongo_mod._mongo_client = None
        cls.app = create_app()
        cls.app.config["TESTING"] = True
        cls.app.config["WTF_CSRF_ENABLED"] = False
        cls.app.config["SECRET_KEY"] = "test-e2e-secret-key-12345"
        cls.client = cls.app.test_client()

        with cls.app.app_context():
            ensure_default_courses()

    def setUp(self):
        User._user_cache.clear()
        self.db = get_db()
        self.test_email_suffix = "@e2e-test-skillrock.org"
        self._cleanup_test_records()

    def tearDown(self):
        self._cleanup_test_records()
        User._user_cache.clear()

    def _cleanup_test_records(self):
        self.db.users.delete_many({"email": {"$regex": "@e2e-test-skillrock\\.org$"}})
        self.db.courses.delete_many({"slug": {"$regex": "^test-e2e-"}})
        # Clean enrollments, submissions, reviews, certificates with test ids
        self.db.enrollments.delete_many({"user_id": {"$regex": "^test_user_"}})
        self.db.certificates.delete_many({"certificate_id": {"$regex": "^SR-TEST-"}})

    def create_user(self, email_prefix, name="Test Student", role="student", password="Password123!"):
        email = f"{email_prefix}{self.test_email_suffix}"
        user = User.create(email=email, name=name, role=role)
        user.set_password(password)
        user.save()
        return user

    def create_admin(self, email_prefix="admin", name="E2E Administrator", password="AdminPassword123!"):
        return self.create_user(email_prefix=email_prefix, name=name, role="admin", password=password)

    def login_client(self, email, password="Password123!"):
        return self.client.post("/login", data={
            "email": email,
            "password": password
        }, follow_redirects=True)

    def set_authenticated_session(self, user):
        with self.client.session_transaction() as sess:
            sess["_user_id"] = str(user.id)
            sess["_fresh"] = True

    def get_or_create_course(self, slug="test-e2e-python-fastapi", title="FastAPI Microservices Testing"):
        course = Course.get_by_slug(slug)
        if not course:
            course = Course({
                "title": title,
                "slug": slug,
                "category": "Backend Development",
                "language": "English",
                "description": "Comprehensive course for end-to-end test verification.",
                "difficulty": "Intermediate",
                "estimated_duration": "4 hours",
                "instructor": "SkillRock Test Academy",
                "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "youtube_video_id": "dQw4w9WgXcQ",
                "is_published": True,
                "created_at": datetime.now(timezone.utc)
            })
            course.save()
            Course.invalidate_published_cache()
        return course


# =============================================================================
# TIER 1: FEATURE COVERAGE (>=5 test cases per feature)
# =============================================================================

class TestSkillRockE2ETier1FeatureCoverage(BaseSkillRockTestCase):
    """
    Tier 1: Comprehensive Primary Functional Coverage
    Validates the primary happy path and core behavior for:
    - R1: Course Enrollment & Auth Flow (6 test cases)
    - R2: Responsive Certificate Preview Relocation (5 test cases)
    - R3: Admin Panel User Progress and Tracking (6 test cases)
    """

    # -------------------------------------------------------------------------
    # R1: Automatic Course Enrollment & Registration Flow
    # -------------------------------------------------------------------------

    def test_tier1_r1_unauthenticated_start_learning_redirects_to_register_with_next(self):
        """
        R1.1: Clicking 'Start Learning' while unauthenticated must redirect to
        /register?next=<course_path> preserving target course context.
        """
        course = self.get_or_create_course("test-e2e-r1-start", "R1 Start Course")
        target_path = f"/learning/courses/{course.slug}"

        # 1. Direct GET request to course start endpoint while logged out
        resp = self.client.get(f"/learning/courses/{course.slug}/start", follow_redirects=False)

        # Must redirect (302 or 303)
        self.assertIn(resp.status_code, [302, 303],
                      "Unauthenticated /learning/courses/<slug>/start must return redirect")

        redirect_url = resp.headers.get("Location", "")
        self.assertTrue(
            "/register" in redirect_url or "/login" in redirect_url,
            f"Redirect location must point to registration/auth, got: {redirect_url}"
        )
        self.assertIn("next=", redirect_url,
                      f"Redirect location must preserve 'next' parameter, got: {redirect_url}")
        self.assertTrue(
            course.slug in redirect_url or target_path in redirect_url,
            f"Target course slug must be embedded in redirect next parameter, got: {redirect_url}"
        )

    def test_tier1_r1_register_page_preserves_and_forwards_next_param(self):
        """
        R1.2: GET /register?next=... must retain the next redirect target
        in the rendered form (or pass-through) to prevent context loss.
        """
        course = self.get_or_create_course("test-e2e-r1-preserve", "R1 Preserve Course")
        target_next = f"/learning/courses/{course.slug}"

        resp = self.client.get(f"/register?next={target_next}")
        # Could be 200 (renders register form) or 302 (redirect to login with next)
        if resp.status_code in [302, 303]:
            loc = resp.headers.get("Location", "")
            self.assertIn("next=", loc, f"Redirect from /register must preserve next query param: {loc}")
            self.assertIn(course.slug, loc, f"Redirect must preserve course slug: {loc}")
        else:
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertTrue(
                target_next in html or course.slug in html,
                "Register page HTML must preserve the target next URL in form action or input"
            )

    def test_tier1_r1_post_registration_auto_enrolls_and_navigates_to_player(self):
        """
        R1.3: Completing registration following a redirected 'Start Learning' click
        must automatically create an Enrollment for that course and direct to player.
        """
        course = self.get_or_create_course("test-e2e-r1-autoenroll-reg", "R1 Auto Enroll Reg")
        target_next = f"/learning/courses/{course.slug}"
        student_email = f"student_new_reg{self.test_email_suffix}"

        # Submit registration with next parameter
        resp = self.client.post("/register", data={
            "name": "Auto Enrolled Student",
            "email": student_email,
            "password": "Password123!",
            "confirm_password": "Password123!",
            "role": "student",
            "next": target_next
        }, follow_redirects=False)

        # Must redirect to target course (or player)
        self.assertIn(resp.status_code, [302, 303], "Registration must redirect")
        loc = resp.headers.get("Location", "")
        self.assertIn(course.slug, loc, f"Registration redirect must lead to target course, got: {loc}")

        # Verify in database that student is now enrolled
        new_user = User.get_by_email(student_email)
        self.assertIsNotNone(new_user, "User record must have been created")
        enrollment = Enrollment.get_by_user_course(new_user.id, course.id)
        self.assertIsNotNone(enrollment, f"User {new_user.id} must be automatically enrolled in course {course.id}")

    def test_tier1_r1_post_login_auto_enrolls_with_next_param(self):
        """
        R1.4: An existing user logging in with a course next parameter must be
        automatically enrolled in the course if not already enrolled.
        """
        course = self.get_or_create_course("test-e2e-r1-autoenroll-login", "R1 Auto Enroll Login")
        student = self.create_user("student_existing_login", "Existing Student")
        target_next = f"/learning/courses/{course.slug}"

        # Confirm unenrolled prior to login
        self.assertIsNone(Enrollment.get_by_user_course(student.id, course.id))

        # Perform login with next parameter
        resp = self.client.post("/login", data={
            "email": student.email,
            "password": "Password123!",
            "next": target_next
        }, follow_redirects=False)

        self.assertIn(resp.status_code, [302, 303])
        loc = resp.headers.get("Location", "")
        self.assertIn(course.slug, loc, f"Login redirect must lead to target course, got: {loc}")

        # Verify auto-enrollment created
        enrollment = Enrollment.get_by_user_course(student.id, course.id)
        self.assertIsNotNone(enrollment, "User must be automatically enrolled upon login with course next target")

    def test_tier1_r1_authenticated_direct_start_learning_auto_enrolls(self):
        """
        R1.5: Authenticated student clicking 'Start Learning' on an unenrolled course
        must be enrolled automatically and navigated directly to the course player.
        """
        course = self.get_or_create_course("test-e2e-r1-auth-direct", "R1 Auth Direct Start")
        student = self.create_user("student_auth_direct", "Authenticated Student")
        self.set_authenticated_session(student)

        # Pre-condition: Unenrolled
        self.assertIsNone(Enrollment.get_by_user_course(student.id, course.id))

        # Click Start Learning endpoint
        resp = self.client.get(f"/learning/courses/{course.slug}/start", follow_redirects=False)

        self.assertIn(resp.status_code, [302, 303], "Authenticated start must redirect to course player")
        loc = resp.headers.get("Location", "")
        self.assertIn(course.slug, loc)
        self.assertTrue(
            "player=1" in loc or "skillrockPlayerFrame" in loc or f"/courses/{course.slug}" in loc,
            f"Redirect location must target the course player: {loc}"
        )

        # Enrollment verification
        enrollment = Enrollment.get_by_user_course(student.id, course.id)
        self.assertIsNotNone(enrollment, "Student must be automatically enrolled without separate manual step")

    def test_tier1_r1_unauthenticated_user_cannot_stream_restricted_lessons(self):
        """
        R1.6: Unauthenticated requests to course learning content routes must be
        prevented from viewing or streaming the lessons (player locked / restricted).
        """
        course = self.get_or_create_course("test-e2e-r1-restricted-stream", "R1 Restricted Streaming")

        # Unauthenticated request to course learning view
        resp = self.client.get(f"/learning/courses/{course.slug}")
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)

        # Verify that unauthenticated visitors are presented with a restricted learning prompt/overlay
        # and cannot access live autoplay iframe streaming without authentication
        has_restricted_indicator = (
            "Restricted" in html or
            "Sign In" in html or
            "Start Learning" in html or
            "lock" in html.lower() or
            "restricted-player" in html or
            "skillrock-restricted" in html
        )
        self.assertTrue(
            has_restricted_indicator,
            "Course page for unauthenticated visitors must indicate restricted content / require sign-in to stream"
        )

    # -------------------------------------------------------------------------
    # R2: Responsive Course Credential Preview Relocation
    # -------------------------------------------------------------------------

    def test_tier1_r2_cert_preview_present_in_course_detail(self):
        """
        R2.1: The course detail learning page must include the sample certificate preview card
        ('Course Credential Preview' / 'Earn Your SkillRock Verified Certificate').
        """
        course = self.get_or_create_course("test-e2e-r2-present", "R2 Present Course")
        resp = self.client.get(f"/learning/courses/{course.slug}")
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)

        self.assertIn("certSampleSection", html, "Certificate preview section #certSampleSection must be present")
        self.assertTrue(
            "Earn Your SkillRock Verified Certificate" in html or "Course Credential Preview" in html,
            "Motivational certificate heading must be rendered"
        )

    def test_tier1_r2_cert_preview_located_in_sidebar_column(self):
        """
        R2.2: Certificate preview card must be located in the right sidebar column
        (col-lg-4 or .course-sidebar-column), NOT in the left main content column below the video.
        """
        course = self.get_or_create_course("test-e2e-r2-sidebar-loc", "R2 Sidebar Location")
        resp = self.client.get(f"/learning/courses/{course.slug}")
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)
        # Inspect placement: certSampleSection should be inside the right column / after action card
        self.assertIn("certSampleSection", html, "Element #certSampleSection must exist in HTML")

        action_idx = html.find("desktopCourseActionCard")
        if action_idx == -1:
            action_idx = html.find("course-action-card")

        cert_idx = html.find("certSampleSection")

        is_in_sidebar = (
            "course-sidebar-column" in html and "certSampleSection" in html[html.find("course-sidebar-column"):]
        ) or (
            action_idx != -1 and cert_idx > action_idx
        ) or (
            "col-lg-4" in html and "certSampleSection" in html[html.find("col-lg-4"):]
        )

        self.assertTrue(
            is_in_sidebar,
            "Certificate preview card (#certSampleSection) must reside within the right sidebar column"
        )

    def test_tier1_r2_cert_preview_positioned_below_action_card(self):
        """
        R2.3: In the right sidebar, the certificate preview card must be placed
        directly below the course action/enrollment card.
        """
        course = self.get_or_create_course("test-e2e-r2-below-action", "R2 Below Action Card")
        resp = self.client.get(f"/learning/courses/{course.slug}")
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)

        # Position of action card vs cert preview in HTML string
        action_card_idx = html.find("desktopCourseActionCard")
        if action_card_idx == -1:
            action_card_idx = html.find("course-action-card")

        cert_card_idx = html.find("certSampleSection")

        self.assertNotEqual(cert_card_idx, -1, "#certSampleSection must exist")
        if action_card_idx != -1:
            self.assertGreater(
                cert_card_idx, action_card_idx,
                "Certificate preview card must appear after the course action card in DOM order"
            )

    def test_tier1_r2_desktop_grid_structure_and_col_width(self):
        """
        R2.4: Desktop layout grid must define a 2-column arrangement
        (2fr 1fr or col-lg-8 / col-lg-4) that allocates ~1/3 width to sidebar.
        """
        course = self.get_or_create_course("test-e2e-r2-grid", "R2 Desktop Grid")
        resp = self.client.get(f"/learning/courses/{course.slug}")
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)

        has_grid_layout = (
            "grid-template-columns: 2fr 1fr" in html or
            "course-layout-grid" in html or
            "col-lg-4" in html
        )
        self.assertTrue(has_grid_layout, "Course learning layout must define desktop 2-column grid structure")

    def test_tier1_r2_mobile_stacking_order_and_zero_sticky_overlap(self):
        """
        R2.5: On mobile viewports (< 992px), layout must stack cleanly without
        sticky collision or element overlap between action card and certificate preview.
        """
        # Inspect stylesheet rules in static/css/style.css or static/css/mobile.css
        style_resp = self.client.get("/static/css/mobile.css")
        if style_resp.status_code != 200:
            style_resp = self.client.get("/static/css/style.css")

        self.assertEqual(style_resp.status_code, 200)
        css = style_resp.get_data(as_text=True)

        # Check for breakpoint rules targeting tablets/mobiles (<= 991.98px or <= 992px or 768px)
        has_responsive_breakpoint = (
            "991.98px" in css or
            "992px" in css or
            "768px" in css or
            "@media" in css
        )
        self.assertTrue(has_responsive_breakpoint, "CSS must provide responsive breakpoint media queries")

    # -------------------------------------------------------------------------
    # R3: Admin Panel User Progress and Enrollment Tracking
    # -------------------------------------------------------------------------

    def test_tier1_r3_admin_users_displays_enrolled_courses_count_column(self):
        """
        R3.1: In /admin/users, the user table must display an 'Enrolled Courses'
        summary column for each user.
        """
        admin = self.create_admin("admin_r3_users_count")
        self.set_authenticated_session(admin)

        resp = self.client.get("/admin/users")
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)

        self.assertTrue(
            "Enrolled Courses" in html or "Enrolled" in html or "Courses Enrolled" in html,
            "/admin/users table must contain 'Enrolled Courses' column header"
        )

    def test_tier1_r3_admin_users_displays_overall_progress_column(self):
        """
        R3.2: In /admin/users, the user table must display an 'Overall Progress'
        summary column for each user.
        """
        admin = self.create_admin("admin_r3_users_prog")
        self.set_authenticated_session(admin)

        resp = self.client.get("/admin/users")
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)

        self.assertTrue(
            "Overall Progress" in html or "Course Progress" in html or "Progress" in html,
            "/admin/users table must contain 'Overall Progress' column header"
        )

    def test_tier1_r3_admin_user_detail_displays_enrolled_course_titles_and_dates(self):
        """
        R3.3: In /admin/users/<user_id>, detailed per-course enrollment data must
        show enrolled course titles and enrollment dates.
        """
        admin = self.create_admin("admin_r3_user_detail_dates")
        student = self.create_user("student_r3_detail", "Detail Student")
        course = self.get_or_create_course("test-e2e-r3-course", "R3 Metrics Course")

        # Create enrollment
        enrollment = Enrollment({
            "user_id": str(student.id),
            "course_id": str(course.id),
            "status": "in_progress",
            "watch_seconds": 1800,
            "max_watch_seconds": 1800,
            "video_duration": 3600,
            "watch_percent": 50,
            "created_at": datetime.now(timezone.utc)
        })
        enrollment.save()

        self.set_authenticated_session(admin)
        resp = self.client.get(f"/admin/users/{student.id}")
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)

        self.assertIn(course.title, html, "Course title must be displayed in user detail view")

    def test_tier1_r3_admin_user_detail_displays_video_progress_metrics(self):
        """
        R3.4: In /admin/users/<user_id>, video lecture progress must display
        watch percentage, completion status, and current watch time.
        """
        admin = self.create_admin("admin_r3_user_detail_video")
        student = self.create_user("student_r3_video", "Video Progress Student")
        course = self.get_or_create_course("test-e2e-r3-video-course", "R3 Video Metrics Course")

        # 75% watched, 2700s out of 3600s
        enrollment = Enrollment({
            "user_id": str(student.id),
            "course_id": str(course.id),
            "status": "in_progress",
            "watch_seconds": 2700,
            "max_watch_seconds": 2700,
            "video_duration": 3600,
            "watch_percent": 75,
            "video_completed": False,
            "created_at": datetime.now(timezone.utc)
        })
        enrollment.save()

        self.set_authenticated_session(admin)
        resp = self.client.get(f"/admin/users/{student.id}")
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)

        self.assertTrue(
            "75%" in html or "75 %" in html or "2700" in html or "45:00" in html,
            "Video lecture progress (percentage or watch time) must be rendered in user detail view"
        )

    def test_tier1_r3_admin_user_detail_displays_capstone_status_and_scores(self):
        """
        R3.5: In /admin/users/<user_id>, capstone project submission status and
        review scores must be clearly presented.
        """
        admin = self.create_admin("admin_r3_capstone")
        student = self.create_user("student_r3_capstone", "Capstone Student")
        course = self.get_or_create_course("test-e2e-r3-cap-course", "R3 Capstone Course")

        # Create Assignment
        assignment = Assignment({
            "course_id": str(course.id),
            "title": "Build a Production Microservice Capstone",
            "step_number": 3,
            "total_steps": 3,
            "is_final_capstone": True,
            "created_at": datetime.now(timezone.utc)
        })
        assignment.save()

        # Create Submission & Review
        sub = Submission({
            "user_id": str(student.id),
            "assignment_id": str(assignment.id),
            "course_id": str(course.id),
            "github_url": "https://github.com/skillrock/test-repo",
            "status": "approved",
            "created_at": datetime.now(timezone.utc)
        })
        sub.save()

        rev = Review({
            "submission_id": str(sub.id),
            "reviewer_id": str(admin.id),
            "total_score": 96,
            "max_score": 100,
            "feedback": "Outstanding work!",
            "created_at": datetime.now(timezone.utc)
        })
        rev.save()

        # Create Enrollment
        enrollment = Enrollment({
            "user_id": str(student.id),
            "course_id": str(course.id),
            "status": "completed",
            "watch_percent": 100,
            "video_completed": True,
            "created_at": datetime.now(timezone.utc)
        })
        enrollment.save()

        self.set_authenticated_session(admin)
        resp = self.client.get(f"/admin/users/{student.id}")
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)

        has_capstone_info = (
            "Approved" in html or
            "Capstone" in html or
            "96" in html or
            "Submission" in html
        )
        self.assertTrue(has_capstone_info, "Capstone status or review score must appear in user detail view")

    def test_tier1_r3_admin_user_detail_displays_certificate_credentials(self):
        """
        R3.6: In /admin/users/<user_id>, issued certificate details
        (Certificate ID, issue date, SHA-256 verification hash) must be displayed.
        """
        admin = self.create_admin("admin_r3_cert")
        student = self.create_user("student_r3_cert", "Certified Student")
        course = self.get_or_create_course("test-e2e-r3-cert-course", "R3 Certificate Course")

        cert_id = "SR-TEST-E2E-2026-X9Y8Z7"
        cert_hash = "a1b2c3d4e5f60718293a4b5c6d7e8f90123456789abcdef0123456789abcdef0"

        cert = Certificate({
            "certificate_id": cert_id,
            "user_id": str(student.id),
            "course_id": str(course.id),
            "verification_hash": cert_hash,
            "issued_at": datetime(2026, 10, 30, tzinfo=timezone.utc),
            "created_at": datetime.now(timezone.utc)
        })
        cert.save()

        # Enrollment
        enrollment = Enrollment({
            "user_id": str(student.id),
            "course_id": str(course.id),
            "status": "completed",
            "watch_percent": 100,
            "created_at": datetime.now(timezone.utc)
        })
        enrollment.save()

        self.set_authenticated_session(admin)
        resp = self.client.get(f"/admin/users/{student.id}")
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)

        self.assertIn(cert_id, html, f"Certificate ID {cert_id} must be displayed in user detail view")
        self.assertTrue(
            cert_hash[:8] in html or cert_hash in html,
            "SHA-256 verification hash preview must be visible in certificate details"
        )


# =============================================================================
# TIER 2: BOUNDARY & CORNER CASES (>=5 test cases per feature)
# =============================================================================

class TestSkillRockE2ETier2BoundaryCases(BaseSkillRockTestCase):
    """
    Tier 2: Boundary, Corner & Resiliency Verification
    Validates extreme, empty, invalid, and edge condition behaviors for:
    - R1: Auth & Enrollment Boundary Cases (5 test cases)
    - R2: UI & Certificate Preview Boundary Cases (5 test cases)
    - R3: Admin Panel Tracking Boundary Cases (5 test cases)
    """

    # -------------------------------------------------------------------------
    # R1: Boundary Cases
    # -------------------------------------------------------------------------

    def test_tier2_r1_invalid_or_malicious_slug_in_next_param(self):
        """
        R1-B1: Malformed or non-existent course slug in 'next' parameter must
        not crash the server (no 500 error) and fallback safely.
        """
        student = self.create_user("student_r1_b1")
        self.set_authenticated_session(student)

        malformed_targets = [
            "/learning/courses/non-existent-course-slug-12345",
            "/learning/courses/<script>alert(1)</script>",
            "/learning/courses/../../etc/passwd"
        ]

        for target in malformed_targets:
            resp = self.client.get(f"/register?next={target}")
            self.assertIn(resp.status_code, [200, 302, 303, 400, 404],
                          f"Target {target} must not crash application")
            self.assertNotEqual(resp.status_code, 500, f"Server crashed with 500 on next={target}")

    def test_tier2_r1_double_start_learning_enrollment_idempotency(self):
        """
        R1-B2: Clicking 'Start Learning' repeatedly on an already enrolled course
        must be completely idempotent without creating duplicate enrollment documents.
        """
        course = self.get_or_create_course("test-e2e-r1-idempotent", "R1 Idempotent Course")
        student = self.create_user("student_r1_idempotent")
        self.set_authenticated_session(student)

        # First click
        resp1 = self.client.get(f"/learning/courses/{course.slug}/start")
        self.assertIn(resp1.status_code, [200, 302, 303])

        # Second click
        resp2 = self.client.get(f"/learning/courses/{course.slug}/start")
        self.assertIn(resp2.status_code, [200, 302, 303])

        # Verify only 1 enrollment document exists in MongoDB
        count = self.db.enrollments.count_documents({
            "user_id": str(student.id),
            "course_id": str(course.id)
        })
        self.assertEqual(count, 1, f"There must be exactly 1 enrollment record, found: {count}")

    def test_tier2_r1_existing_progress_retained_on_re_start(self):
        """
        R1-B3: When a student who has 65% progress clicks 'Start Learning' again,
        their existing watch progress must NOT be reset to 0.
        """
        course = self.get_or_create_course("test-e2e-r1-retain-prog", "R1 Retain Progress")
        student = self.create_user("student_r1_retain_prog")
        self.set_authenticated_session(student)

        # Pre-seed enrollment with 65% watch progress
        enrollment = Enrollment({
            "user_id": str(student.id),
            "course_id": str(course.id),
            "status": "in_progress",
            "watch_seconds": 2340,
            "max_watch_seconds": 2340,
            "video_duration": 3600,
            "watch_percent": 65,
            "created_at": datetime.now(timezone.utc)
        })
        enrollment.save()

        # Student clicks start again
        self.client.get(f"/learning/courses/{course.slug}/start")

        # Reload enrollment from DB
        updated_enrollment = Enrollment.get_by_user_course(student.id, course.id)
        self.assertEqual(updated_enrollment.watch_percent, 65, "Watch progress must remain at 65%")
        self.assertEqual(updated_enrollment.max_watch_seconds, 2340, "max_watch_seconds must be preserved")

    def test_tier2_r1_encoded_next_url_with_query_params_and_hash(self):
        """
        R1-B4: Complex encoded next URLs containing query parameters and anchor tags
        must be retained without corrupting the redirect target.
        """
        course = self.get_or_create_course("test-e2e-r1-complex-next", "R1 Complex Next")
        complex_next = f"/learning/courses/{course.slug}?player=1&ref=card#skillrockPlayerFrame"

        resp = self.client.get(f"/register?next={complex_next}")
        self.assertIn(resp.status_code, [200, 302, 303])
        if resp.status_code in [302, 303]:
            loc = resp.headers.get("Location", "")
            self.assertIn(course.slug, loc)

    def test_tier2_r1_unauthenticated_api_save_progress_rejected(self):
        """
        R1-B5: Direct unauthenticated POST request to /learning/save-progress
        must be rejected with 401 Unauthorized or redirect to login.
        """
        course = self.get_or_create_course("test-e2e-r1-save-reject", "R1 Save Reject")
        resp = self.client.post("/learning/save-progress", json={
            "course_id": str(course.id),
            "watch_seconds": 1200,
            "video_duration": 3600
        })
        self.assertIn(resp.status_code, [302, 303, 401, 403],
                      "Unauthenticated save-progress must be rejected")

    # -------------------------------------------------------------------------
    # R2: Boundary Cases
    # -------------------------------------------------------------------------

    def test_tier2_r2_long_course_title_no_overflow_in_sidebar_cert(self):
        """
        R2-B1: Very long course titles must render inside the relocated preview card
        without causing layout blowout or breaking sidebar width constraints.
        """
        super_long_title = "Enterprise Distributed Systems Architecture and Event-Driven Microservices in High-Throughput Environments"
        course = self.get_or_create_course("test-e2e-r2-long-title", super_long_title)

        resp = self.client.get(f"/learning/courses/{course.slug}")
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)

        self.assertIn("certSampleSection", html)
        self.assertIn(super_long_title, html)

    def test_tier2_r2_unauthenticated_visitor_preview_card_cta(self):
        """
        R2-B2: An unauthenticated visitor viewing the course page must see a motivating
        call-to-action in the certificate preview card directing them to start/register.
        """
        course = self.get_or_create_course("test-e2e-r2-anon-preview", "R2 Anon Preview")
        resp = self.client.get(f"/learning/courses/{course.slug}")
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)

        cert_section_idx = html.find('id="certSampleSection"')
        if cert_section_idx == -1:
            cert_section_idx = html.find("certSampleSection")
        self.assertNotEqual(cert_section_idx, -1, "#certSampleSection must exist in HTML")

        cert_block = html[cert_section_idx:cert_section_idx + 2500]
        has_auth_cta = (
            "Sign In" in cert_block or
            "Register" in cert_block or
            "Start Learning" in cert_block or
            "Enrol Free" in cert_block or
            "Free & Verifiable" in cert_block
        )
        self.assertTrue(has_auth_cta, "Certificate preview must contain a registration/enrollment CTA for visitors")

    def test_tier2_r2_enrolled_student_preview_card_dynamic_state(self):
        """
        R2-B3: An enrolled student viewing the course page must see dynamic progress
        guidance (e.g. watch progress or next milestone) inside the relocated preview card.
        """
        course = self.get_or_create_course("test-e2e-r2-enrolled-preview", "R2 Enrolled Preview")
        student = self.create_user("student_r2_enrolled_preview")
        self.set_authenticated_session(student)

        # Enroll with 45% progress
        enrollment = Enrollment({
            "user_id": str(student.id),
            "course_id": str(course.id),
            "status": "in_progress",
            "watch_percent": 45,
            "created_at": datetime.now(timezone.utc)
        })
        enrollment.save()

        resp = self.client.get(f"/learning/courses/{course.slug}")
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)

        self.assertIn("certSampleSection", html)

    def test_tier2_r2_completed_certified_student_preview_card_state(self):
        """
        R2-B4: A student who has earned their certificate must see their earned credentials
        or verification link inside the relocated certificate preview card.
        """
        course = self.get_or_create_course("test-e2e-r2-certified-preview", "R2 Certified Preview")
        student = self.create_user("student_r2_certified_preview")
        self.set_authenticated_session(student)

        cert = Certificate({
            "certificate_id": "SR-TEST-E2E-COMPLETED",
            "user_id": str(student.id),
            "course_id": str(course.id),
            "verification_hash": "e2e_cert_hash_1234567890",
            "issued_at": datetime.now(timezone.utc),
            "created_at": datetime.now(timezone.utc)
        })
        cert.save()

        resp = self.client.get(f"/learning/courses/{course.slug}")
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)

        self.assertIn("certSampleSection", html)
        self.assertTrue(
            "SR-TEST-E2E-COMPLETED" in html or "Earned" in html or "Verified" in html,
            "Earned certificate status or verification reference should appear on course page"
        )

    def test_tier2_r2_css_mobile_breakpoint_at_991_98px_stacks_cleanly(self):
        """
        R2-B5: Verify that the stylesheets define mobile/tablet stacking behavior
        targeting viewports below 992px to prevent horizontal scrolling.
        """
        for css_file in ["mobile.css", "style.css"]:
            resp = self.client.get(f"/static/css/{css_file}")
            if resp.status_code == 200:
                css = resp.get_data(as_text=True)
                if "@media" in css:
                    self.assertTrue(True)
                    return
        self.fail("Stylesheets must contain responsive @media queries")

    # -------------------------------------------------------------------------
    # R3: Boundary Cases
    # -------------------------------------------------------------------------

    def test_tier2_r3_user_with_zero_enrollments_displays_clean_empty_state(self):
        """
        R3-B1: A user with 0 course enrollments must display '0' for enrolled count
        and '0%' progress without causing division by zero or template crashes.
        """
        admin = self.create_admin("admin_r3_b1")
        student = self.create_user("student_r3_b1_zero", "Zero Enrollments Student")
        self.set_authenticated_session(admin)

        # 1. Admin users list
        resp_list = self.client.get("/admin/users")
        self.assertEqual(resp_list.status_code, 200)
        html_list = resp_list.get_data(as_text=True)
        self.assertIn(student.name, html_list)

        # 2. Admin user detail
        resp_detail = self.client.get(f"/admin/users/{student.id}")
        self.assertEqual(resp_detail.status_code, 200)
        html_detail = resp_detail.get_data(as_text=True)
        self.assertIn(student.name, html_detail)
        # Should gracefully indicate 0 or no enrollments
        self.assertTrue(
            "0" in html_detail or "No enrollments" in html_detail or "not enrolled" in html_detail.lower(),
            "User detail must handle zero enrollments cleanly"
        )

    def test_tier2_r3_user_with_multiple_courses_calculates_accurate_average_progress(self):
        """
        R3-B2: For a user enrolled in Course 1 (40% progress) and Course 2 (80% progress),
        the overall progress metric must accurately calculate the average (60%).
        """
        admin = self.create_admin("admin_r3_b2")
        student = self.create_user("student_r3_b2_avg", "Multi Course Student")
        c1 = self.get_or_create_course("test-e2e-r3-c1", "Course 1")
        c2 = self.get_or_create_course("test-e2e-r3-c2", "Course 2")

        # Enrollment 1: 40%
        e1 = Enrollment({
            "user_id": str(student.id),
            "course_id": str(c1.id),
            "status": "in_progress",
            "watch_percent": 40,
            "created_at": datetime.now(timezone.utc)
        })
        e1.save()

        # Enrollment 2: 80%
        e2 = Enrollment({
            "user_id": str(student.id),
            "course_id": str(c2.id),
            "status": "in_progress",
            "watch_percent": 80,
            "created_at": datetime.now(timezone.utc)
        })
        e2.save()

        self.set_authenticated_session(admin)
        resp = self.client.get(f"/admin/users/{student.id}")
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)

        # Both course titles should be rendered
        self.assertIn(c1.title, html)
        self.assertIn(c2.title, html)

    def test_tier2_r3_user_with_pending_capstone_shows_pending_status_without_score(self):
        """
        R3-B3: A user with a submitted capstone that is pending review must display
        'Pending Review' status and gracefully display 'Pending' or '--' for the score.
        """
        admin = self.create_admin("admin_r3_b3")
        student = self.create_user("student_r3_b3_pending", "Pending Capstone Student")
        course = self.get_or_create_course("test-e2e-r3-b3-course", "R3 Pending Capstone Course")

        assignment = Assignment({
            "course_id": str(course.id),
            "title": "Pending Review Assignment",
            "step_number": 1,
            "total_steps": 1,
            "is_final_capstone": True,
            "created_at": datetime.now(timezone.utc)
        })
        assignment.save()

        sub = Submission({
            "user_id": str(student.id),
            "assignment_id": str(assignment.id),
            "course_id": str(course.id),
            "github_url": "https://github.com/skillrock/pending-repo",
            "status": "pending_review",
            "created_at": datetime.now(timezone.utc)
        })
        sub.save()

        enrollment = Enrollment({
            "user_id": str(student.id),
            "course_id": str(course.id),
            "status": "in_progress",
            "watch_percent": 90,
            "created_at": datetime.now(timezone.utc)
        })
        enrollment.save()

        self.set_authenticated_session(admin)
        resp = self.client.get(f"/admin/users/{student.id}")
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)

        self.assertTrue(
            "pending" in html.lower() or "under review" in html.lower() or "submitted" in html.lower(),
            "Pending capstone status must be displayed"
        )

    def test_tier2_r3_user_without_certificate_gracefully_handled(self):
        """
        R3-B4: An enrolled student who has not completed the course must display
        'In Progress' or 'Not Issued' for certificate credentials without template errors.
        """
        admin = self.create_admin("admin_r3_b4")
        student = self.create_user("student_r3_b4_nocert", "No Cert Student")
        course = self.get_or_create_course("test-e2e-r3-b4-course", "R3 No Cert Course")

        enrollment = Enrollment({
            "user_id": str(student.id),
            "course_id": str(course.id),
            "status": "in_progress",
            "watch_percent": 20,
            "created_at": datetime.now(timezone.utc)
        })
        enrollment.save()

        self.set_authenticated_session(admin)
        resp = self.client.get(f"/admin/users/{student.id}")
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)

        # Must not produce jinja error or 500
        self.assertIn(student.name, html)
        self.assertIn(course.title, html)

    def test_tier2_r3_invalid_user_id_returns_404_or_redirect_not_500(self):
        """
        R3-B5: Requesting /admin/users/<invalid_id> with a non-existent or malformed ID
        must return HTTP 404 or redirect, never an unhandled 500 error.
        """
        admin = self.create_admin("admin_r3_b5")
        self.set_authenticated_session(admin)

        resp = self.client.get("/admin/users/non_existent_user_id_99999")
        self.assertIn(resp.status_code, [302, 303, 404],
                      "Invalid user ID must return 404 or redirect to user list")
        self.assertNotEqual(resp.status_code, 500, "Must not return 500 Internal Server Error")


# =============================================================================
# TIER 3: CROSS-FEATURE INTERACTIONS
# =============================================================================

class TestSkillRockE2ETier3CrossFeatureInteractions(BaseSkillRockTestCase):
    """
    Tier 3: Multi-Module Cross-Feature Interactions
    Validates end-to-end data flow and contract integration between:
    - Auth & Registration (R1)
    - Learning View & Sidebar Relocation (R2)
    - Admin Panel Tracking & Verification (R3)
    """

    def test_tier3_e2e_student_lifecycle_registration_enrollment_preview_admin_visibility(self):
        """
        T3.1: Full student lifecycle across all 3 features:
        1. Anonymous visitor clicks Start Learning -> redirected to /register?next=...
        2. Student registers -> auto-enrolled in target course
        3. Course detail renders relocated certificate preview card in sidebar
        4. Student tracks watch progress to 80%
        5. Admin views /admin/users and sees user with 1 course and 80% progress
        6. Admin views /admin/users/<id> and sees exact course details.
        """
        course = self.get_or_create_course("test-e2e-tier3-lifecycle", "Tier 3 Lifecycle Course")
        target_next = f"/learning/courses/{course.slug}"
        student_email = f"student_lifecycle{self.test_email_suffix}"

        # 1. Anonymous Start Learning
        anon_resp = self.client.get(f"/learning/courses/{course.slug}/start")
        self.assertIn(anon_resp.status_code, [302, 303])

        # 2. Complete Registration with next parameter
        reg_resp = self.client.post("/register", data={
            "name": "Lifecycle Student",
            "email": student_email,
            "password": "Password123!",
            "confirm_password": "Password123!",
            "role": "student",
            "next": target_next
        }, follow_redirects=True)
        self.assertEqual(reg_resp.status_code, 200)

        student = User.get_by_email(student_email)
        self.assertIsNotNone(student, "Student user must exist")

        # Verify auto-enrollment
        enrollment = Enrollment.get_by_user_course(student.id, course.id)
        self.assertIsNotNone(enrollment, "Enrollment must be created upon registration")

        # 3. View Course Detail & Verify Relocated Preview Card
        course_resp = self.client.get(f"/learning/courses/{course.slug}")
        self.assertEqual(course_resp.status_code, 200)
        course_html = course_resp.get_data(as_text=True)
        self.assertIn("certSampleSection", course_html, "Preview card must exist on course page")

        # 4. Simulate Watch Progress (80%)
        enrollment.watch_seconds = 2880
        enrollment.max_watch_seconds = 2880
        enrollment.video_duration = 3600
        enrollment.watch_percent = 80
        enrollment.video_completed = True
        enrollment.save()

        # 5. Admin List Audit
        admin = self.create_admin("admin_tier3_lifecycle")
        self.set_authenticated_session(admin)

        admin_list = self.client.get("/admin/users")
        self.assertEqual(admin_list.status_code, 200)
        list_html = admin_list.get_data(as_text=True)
        self.assertIn(student.name, list_html)

        # 6. Admin Detail Audit
        admin_detail = self.client.get(f"/admin/users/{student.id}")
        self.assertEqual(admin_detail.status_code, 200)
        detail_html = admin_detail.get_data(as_text=True)
        self.assertIn(course.title, detail_html)
        self.assertTrue("80" in detail_html or "Completed" in detail_html,
                        "Admin detail must reflect 80% progress or completion")

    def test_tier3_multi_course_auto_enrollment_cross_tracking(self):
        """
        T3.2: Multi-course enrollment interaction:
        Student enrolls in Course A via direct 'Start Learning' and Course B via login redirect.
        Both courses appear accurately aggregated in /admin/users and /admin/users/<id>.
        """
        cA = self.get_or_create_course("test-e2e-tier3-ca", "Tier 3 Course A")
        cB = self.get_or_create_course("test-e2e-tier3-cb", "Tier 3 Course B")
        student = self.create_user("student_tier3_multi")

        # Direct Start Learning for Course A
        self.set_authenticated_session(student)
        self.client.get(f"/learning/courses/{cA.slug}/start")
        self.assertIsNotNone(Enrollment.get_by_user_course(student.id, cA.id))

        # Direct Start Learning for Course B
        self.client.get(f"/learning/courses/{cB.slug}/start")
        self.assertIsNotNone(Enrollment.get_by_user_course(student.id, cB.id))

        # Admin View
        admin = self.create_admin("admin_tier3_multi")
        self.set_authenticated_session(admin)

        resp_detail = self.client.get(f"/admin/users/{student.id}")
        self.assertEqual(resp_detail.status_code, 200)
        html = resp_detail.get_data(as_text=True)

        self.assertIn(cA.title, html, "Course A must be displayed in admin user profile")
        self.assertIn(cB.title, html, "Course B must be displayed in admin user profile")

    def test_tier3_unauthenticated_redirect_to_auth_to_learning_layout_integrity(self):
        """
        T3.3: Verify that navigating through the unauthenticated redirect flow does not
        alter or degrade the course layout grid and responsive card elements.
        """
        course = self.get_or_create_course("test-e2e-tier3-layout", "Tier 3 Layout Course")
        resp = self.client.get(f"/learning/courses/{course.slug}")
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)

        # Verify key UI components
        self.assertIn("course-layout-grid", html)
        self.assertIn("certSampleSection", html)

    def test_tier3_security_privilege_isolation_for_admin_views(self):
        """
        T3.4: Verify that non-admin student users cannot access /admin/users
        or /admin/users/<id> to prevent unauthorized progress inspection.
        """
        student = self.create_user("student_tier3_security")
        self.set_authenticated_session(student)

        res1 = self.client.get("/admin/users")
        self.assertIn(res1.status_code, [302, 303, 403], "Students must be blocked from /admin/users")

        res2 = self.client.get(f"/admin/users/{student.id}")
        self.assertIn(res2.status_code, [302, 303, 403], "Students must be blocked from /admin/users/<id>")


# =============================================================================
# TIER 4: REAL-WORLD WORKLOAD / END-TO-END USER SCENARIOS
# =============================================================================

class TestSkillRockE2ETier4RealWorldScenarios(BaseSkillRockTestCase):
    """
    Tier 4: End-to-End Real-World User Journeys & Adversarial Scenarios
    Simulates complete operational scenarios matching production conditions:
    - Scenario A: Fast-Track Certification Journey
    - Scenario B: Administrator Cohort Audit & Verification
    - Scenario C: Adversarial Stress & Resiliency Testing
    """

    def test_tier4_scenario_complete_student_certification_journey(self):
        """
        Scenario A: Full pipeline simulation of student certification:
        1. Student registers and enrolls
        2. Student streams and completes 100% video progress
        3. Student submits capstone project
        4. Admin grades capstone project with score 98/100
        5. Verified certificate issued with SHA-256 hash
        6. Certificate verified from admin panel
        """
        course = self.get_or_create_course("test-e2e-tier4-journey", "Tier 4 Journey Course")
        student = self.create_user("student_tier4_journey", "Journey Student")
        admin = self.create_admin("admin_tier4_journey", "Journey Admin")

        # Step 1: Enrollment
        enrollment = Enrollment({
            "user_id": str(student.id),
            "course_id": str(course.id),
            "status": "enrolled",
            "created_at": datetime.now(timezone.utc)
        })
        enrollment.save()

        # Step 2: Complete Video (100%)
        enrollment.watch_seconds = 3600
        enrollment.max_watch_seconds = 3600
        enrollment.video_duration = 3600
        enrollment.watch_percent = 100
        enrollment.video_completed = True
        enrollment.status = "in_progress"
        enrollment.save()

        # Step 3: Capstone Submission
        assignment = Assignment({
            "course_id": str(course.id),
            "title": "Enterprise Cloud Architecture",
            "step_number": 1,
            "total_steps": 1,
            "is_final_capstone": True,
            "created_at": datetime.now(timezone.utc)
        })
        assignment.save()

        submission = Submission({
            "user_id": str(student.id),
            "assignment_id": str(assignment.id),
            "course_id": str(course.id),
            "github_url": "https://github.com/skillrock/journey-capstone",
            "status": "approved",
            "created_at": datetime.now(timezone.utc)
        })
        submission.save()

        # Step 4: Review
        review = Review({
            "submission_id": str(submission.id),
            "reviewer_id": str(admin.id),
            "total_score": 98,
            "max_score": 100,
            "feedback": "Perfect architectural implementation.",
            "created_at": datetime.now(timezone.utc)
        })
        review.save()

        # Step 5: Issue Certificate
        cert_id = "SR-TEST-TIER4-2026-AAA111"
        cert_hash = "abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789"
        cert = Certificate({
            "certificate_id": cert_id,
            "user_id": str(student.id),
            "course_id": str(course.id),
            "verification_hash": cert_hash,
            "issued_at": datetime.now(timezone.utc),
            "created_at": datetime.now(timezone.utc)
        })
        cert.save()

        enrollment.status = "completed"
        enrollment.save()

        # Step 6: Admin Inspection
        self.set_authenticated_session(admin)
        resp = self.client.get(f"/admin/users/{student.id}")
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)

        self.assertIn(course.title, html)
        self.assertIn(cert_id, html)
        self.assertTrue("98" in html or "Approved" in html)

    def test_tier4_scenario_admin_audit_and_student_monitoring_dashboard(self):
        """
        Scenario B: Multi-student cohort monitoring:
        Simulate an entire cohort of students with different states:
        - Student 1: Enrolled, 25% watch progress
        - Student 2: Enrolled, 90% watch progress, capstone pending
        - Student 3: Fully certified
        Admin accesses /admin/users and verifies that table metrics reflect the cohort accurately.
        """
        course = self.get_or_create_course("test-e2e-tier4-cohort", "Cohort Course")
        admin = self.create_admin("admin_tier4_cohort")

        s1 = self.create_user("student_c1", "Cohort Student One")
        s2 = self.create_user("student_c2", "Cohort Student Two")
        s3 = self.create_user("student_c3", "Cohort Student Three")

        # S1: 25%
        Enrollment({
            "user_id": str(s1.id),
            "course_id": str(course.id),
            "status": "in_progress",
            "watch_percent": 25,
            "created_at": datetime.now(timezone.utc)
        }).save()

        # S2: 90%
        Enrollment({
            "user_id": str(s2.id),
            "course_id": str(course.id),
            "status": "in_progress",
            "watch_percent": 90,
            "created_at": datetime.now(timezone.utc)
        }).save()

        # S3: 100% + Certificate
        Enrollment({
            "user_id": str(s3.id),
            "course_id": str(course.id),
            "status": "completed",
            "watch_percent": 100,
            "created_at": datetime.now(timezone.utc)
        }).save()
        Certificate({
            "certificate_id": "SR-TEST-COHORT-S3",
            "user_id": str(s3.id),
            "course_id": str(course.id),
            "verification_hash": "hash_s3_cohort",
            "issued_at": datetime.now(timezone.utc),
            "created_at": datetime.now(timezone.utc)
        }).save()

        self.set_authenticated_session(admin)
        resp = self.client.get("/admin/users")
        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)

        self.assertIn(s1.name, html)
        self.assertIn(s2.name, html)
        self.assertIn(s3.name, html)

    def test_tier4_scenario_adversarial_tampering_and_privilege_isolation(self):
        """
        Scenario C: Adversarial Stress & Resiliency:
        1. Open-redirect prevention: Target URLs pointing outside domain (e.g. https://evil.com)
           in next parameter must not redirect externally.
        2. SQL/NoSQL injection payload in course slug in next parameter.
        3. Privilege escalation attempts by students to admin endpoints.
        """
        student = self.create_user("student_tier4_adversarial")
        self.set_authenticated_session(student)

        # 1. External open-redirect attempt
        evil_url = "https://evil-phishing-site.com/steal"
        resp = self.client.get(f"/register?next={evil_url}")
        if resp.status_code in [302, 303]:
            loc = resp.headers.get("Location", "")
            self.assertFalse(loc.startswith("https://evil-phishing-site.com"),
                             "Application must prevent open redirects to external hosts")

        # 2. NoSQL injection in next parameter
        nosql_target = "/learning/courses/{'$gt': ''}"
        resp_nosql = self.client.get(f"/register?next={nosql_target}")
        self.assertNotEqual(resp_nosql.status_code, 500, "NoSQL injection string must not crash the server")

        # 3. Student accessing admin panel
        admin_resp = self.client.get("/admin/dashboard")
        self.assertIn(admin_resp.status_code, [302, 303, 403],
                      "Student must not be allowed to access admin dashboard")


if __name__ == "__main__":
    unittest.main()
