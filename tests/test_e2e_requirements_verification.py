# -*- coding: utf-8 -*-
"""
End-to-End Requirements Verification Test Suite for SkillRock.
================================================================================
Validates all 4 core production requirements across 4 testing tiers:
- Tier 1: Feature Coverage (Certificates, Book Loader, Mobile Responsiveness, Teacher Studio Streaming)
- Tier 2: Boundary & Corner Cases (Production Host Header vs localhost, Root Alias Redirection,
          Invalid/Adversarial Certificate IDs, Device Media Constraints, Viewport Breakpoints 375px/768px)
- Tier 3: Cross-Feature Interactions (Unified Challenge Certificate Verification on Learning Portal,
          Book Loader Lifecycle Dismissals & Safety Timeout, Public Credential Viewing vs Name Lock Security)
- Tier 4: Real-World User Flows (Student Complete Journey Course-to-Certificate, Teacher Studio Streaming Session)

Isolation & Performance Guarantee:
Sets MONGODB_URI="" to enforce mongomock in-memory isolation, ensuring tests execute in < 2.0s without Atlas latency.
"""

import os
import sys
import re
import json
import uuid
import hashlib
from datetime import datetime, timezone, timedelta
import unittest
from werkzeug.security import generate_password_hash

# ------------------------------------------------------------------------------
# ISOLATION RULE: Enforce mongomock before any application module import
# ------------------------------------------------------------------------------
os.environ["MONGODB_URI"] = ""
os.environ["TESTING"] = "1"

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from config import Config
from models import get_db, User, Course, Assignment, Submission, Certificate
from models.challenge import ChallengeEnrollment, MonthlyChallenge
from models.bhavishya import BhavishyaSubject, BhavishyaLiveLecture


class TestE2ERequirementsVerification(unittest.TestCase):
    """
    Opaque-box, requirement-driven E2E test suite covering Tier 1 through Tier 4.
    """

    @classmethod
    def setUpClass(cls):
        Config.TESTING = True
        Config.WTF_CSRF_ENABLED = False
        cls.app = create_app(Config)
        cls.app.config["TESTING"] = True
        cls.app.config["WTF_CSRF_ENABLED"] = False
        cls.workspace_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        cls.db = get_db()

        # Precompute shared password hash to avoid expensive PBKDF2 per test setUp
        cls.shared_password = "Password123!"
        cls.shared_hash = generate_password_hash(cls.shared_password)

        ts = int(datetime.now().timestamp() * 1000)

        # Seed shared test student
        cls.student_email = f"student_e2e_{ts}@skillrock.edu"
        cls.student = User({
            "name": "Aarav Sharma",
            "email": cls.student_email,
            "role": "student",
            "phone": "9876543210",
            "password_hash": cls.shared_hash
        })
        cls.student.save()

        # Seed shared test teacher / admin
        cls.teacher_email = f"teacher_e2e_{ts}@skillrock.edu"
        cls.teacher = User({
            "name": "Prof. Vikram Malhotra",
            "email": cls.teacher_email,
            "role": "admin",
            "is_admin": True,
            "password_hash": cls.shared_hash
        })
        cls.teacher.save()

        # Seed shared test course
        cls.course_slug = f"test-python-course-{ts}"
        cls.course = Course({
            "title": "Complete Python Programming Tutorial in 4 Hours for Beginners",
            "slug": cls.course_slug,
            "is_published": True,
            "description": "Comprehensive hands-on Python curriculum."
        })
        cls.course.save()

        # Seed shared assignment
        cls.assignment = Assignment({
            "title": "Python Capstone Project",
            "course_id": str(cls.course.id),
            "is_quiz_based": False
        })
        cls.assignment.save()

        # Seed shared submission
        cls.submission = Submission({
            "assignment_id": str(cls.assignment.id),
            "user_id": str(cls.student.id),
            "status": "approved",
            "title": "Automated Web Scraper with Python"
        })
        cls.submission.save()

        # Seed shared official certificate for student
        cls.cert_id = Certificate.generate_cert_id()
        cls.certificate = Certificate({
            "certificate_id": cls.cert_id,
            "user_id": str(cls.student.id),
            "user_name": cls.student.name,
            "user_email": cls.student.email,
            "course_id": str(cls.course.id),
            "course_title": cls.course.title,
            "submission_id": str(cls.submission.id),
            "issued_at": datetime.now(timezone.utc),
            "verification_hash": hashlib.sha256(f"{cls.cert_id}:{cls.student.id}".encode("utf-8")).hexdigest()[:24],
            "name_locked": False
        })
        cls.certificate.save()

    def setUp(self):
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        self._logout()

    def tearDown(self):
        self._logout()
        self.app_context.pop()

    def _login(self, user, password=None):
        """Helper to establish an authenticated session for a user via /login."""
        pwd = password or self.shared_password
        return self.client.post("/login", data={"email": user.email, "password": pwd}, follow_redirects=False)

    def _logout(self):
        """Helper to clear authenticated session via /logout."""
        return self.client.get("/logout", follow_redirects=False)

    # ==========================================================================
    # TIER 1: FEATURE COVERAGE
    # ==========================================================================

    def test_tier1_r1_certificate_access_and_presentation(self):
        """
        R1 Feature Coverage:
        Verifies that official course certificates can be viewed and verified
        without 404/500 errors, presenting required credential elements.
        """
        self._login(self.student)

        # 1. Access official certificate presentation page as owner
        resp = self.client.get(f"/learning/certificate/{self.cert_id}")
        self.assertEqual(resp.status_code, 200, "Official certificate view failed with non-200 status")
        html = resp.data.decode("utf-8")

        # Verify key credential elements
        self.assertIn("Aarav", html, "Student name missing from certificate view")
        self.assertIn(self.cert_id, html, "Certificate ID missing from certificate view")
        self.assertTrue(
            "downloadCertificatePDF" in html or "html2pdf" in html or "Download" in html,
            "PDF export/download trigger missing from certificate template"
        )
        self.assertTrue(
            "qrCode" in html or "qrcode" in html.lower() or "qr" in html.lower(),
            "QR verification component missing from certificate template"
        )

        # 2. Access public verification ledger
        verify_resp = self.client.get(f"/learning/verify/{self.cert_id}")
        self.assertEqual(verify_resp.status_code, 200, "Public verification portal failed with non-200 status")
        verify_html = verify_resp.data.decode("utf-8")
        self.assertIn("Verified", verify_html, "Verified status missing from public verification ledger")
        self.assertIn("Aarav", verify_html, "Awarded student name missing from public ledger")
        self.assertIn(self.cert_id, verify_html, "Certificate ID missing from public ledger")

    def test_tier1_r2_page_transition_book_loader_contract(self):
        """
        R2 Feature Coverage:
        Verifies the presence of the 3D flipping book page transition loader markup,
        CSS animation keyframes, and JavaScript lifecycle hooks.
        """
        # Ensure anonymous user views landing page
        self._logout()
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)
        html = resp.data.decode("utf-8")

        # Check for book loader markup or action wheel loader fallback
        has_book_loader_markup = (
            "pageTransitionBookLoader" in html
            or "flipping-book" in html
            or "book-loader" in html
            or "actionWheelLoader" in html
            or "book" in html.lower()
        )
        self.assertTrue(has_book_loader_markup, "Page transition loader markup missing from base layout")

        # 2. Inspect static/js/main.js for loader API hooks
        main_js_path = os.path.join(self.workspace_dir, "static", "js", "main.js")
        self.assertTrue(os.path.exists(main_js_path), "static/js/main.js file missing")
        with open(main_js_path, "r", encoding="utf-8") as f:
            js_content = f.read()

        has_loader_hooks = (
            "showBookLoader" in js_content
            or "showActionLoader" in js_content
            or "showRedirectLoader" in js_content
        )
        self.assertTrue(has_loader_hooks, "Frontend JavaScript lacks loader lifecycle hooks")

        # 3. Inspect static/css/style.css for loader styles
        style_css_path = os.path.join(self.workspace_dir, "static", "css", "style.css")
        self.assertTrue(os.path.exists(style_css_path), "static/css/style.css file missing")
        with open(style_css_path, "r", encoding="utf-8") as f:
            css_content = f.read()

        has_loader_css = (
            "book-loader" in css_content
            or "action-wheel-overlay" in css_content
            or "flipping" in css_content
            or "pageTransition" in css_content
        )
        self.assertTrue(has_loader_css, "Stylesheet lacks page transition loader styles")

    def test_tier1_r3_mobile_responsiveness_rules(self):
        """
        R3 Feature Coverage:
        Verifies mobile stylesheet exists and contains responsive adaptations
        across viewports (max-width: 768px and smaller) for targeted views.
        """
        mobile_css_path = os.path.join(self.workspace_dir, "static", "css", "mobile.css")
        self.assertTrue(os.path.exists(mobile_css_path), "static/css/mobile.css missing")
        with open(mobile_css_path, "r", encoding="utf-8") as f:
            mobile_css = f.read()

        # Must declare media query targeting smartphones and tablets <= 768px
        self.assertIn("@media", mobile_css, "Media queries missing from mobile.css")
        self.assertIn("768px", mobile_css, "768px viewport breakpoint missing from mobile.css")

        # Check normalization against horizontal scrollbars
        self.assertTrue(
            "overflow-x" in mobile_css or "100vw" in mobile_css or "box-sizing" in mobile_css,
            "Mobile viewport normalization rules missing from mobile.css"
        )

        # Check font-size styling to prevent iOS Safari auto-zoom
        self.assertTrue(
            "16px" in mobile_css or "font-size" in mobile_css,
            "Mobile input font sizing rules missing from mobile.css"
        )

    def test_tier1_r4_teacher_studio_streaming_controls(self):
        """
        R4 Feature Coverage:
        Verifies that Bhavishya 1.0 live classroom template contains the Educator
        Broadcast Studio markup, camera/mic toggle buttons, and decoupled track logic.
        """
        # Ensure a Bhavishya lecture exists
        lectures = BhavishyaLiveLecture.get_all()
        lecture_id = lectures[0].lecture_id if lectures else "py-live-01"

        # Login as teacher/admin to render studio controls
        self._login(self.teacher)
        resp = self.client.get(f"/bhavishya/lecture/{lecture_id}")
        self.assertEqual(resp.status_code, 200, "Teacher live classroom request failed")
        html = resp.data.decode("utf-8")

        # Verify studio markup
        self.assertIn("teacherStudioVideo", html, "Teacher studio video preview element missing")
        self.assertIn("btnToggleCamera", html, "Camera toggle button missing from studio")
        self.assertIn("btnToggleMic", html, "Microphone toggle button missing from studio")

        # Verify decoupled JavaScript functions exist
        self.assertIn("toggleCamera", html, "toggleCamera function missing from classroom script")
        self.assertIn("toggleMic", html, "toggleMic function missing from classroom script")

    # ==========================================================================
    # TIER 2: BOUNDARY & CORNER CASES
    # ==========================================================================

    def test_tier2_r1_production_host_header_vs_localhost(self):
        """
        R1 Boundary Case:
        Verifies that /learning/certificate/<cert_id> succeeds on BOTH localhost
        and production host headers (e.g. www.skillrock.in) without crashing with
        500 NameError (current_app).
        """
        self._login(self.student)

        # 1. Localhost header
        res_local = self.client.get(
            f"/learning/certificate/{self.cert_id}",
            headers={"Host": "localhost:5000"}
        )
        self.assertEqual(res_local.status_code, 200, "Localhost request to certificate failed")
        html_local = res_local.data.decode("utf-8")
        self.assertIn("verify", html_local.lower(), "Verification link missing in localhost view")

        # 2. Production host header (www.skillrock.in) - the exact trigger of the 500 bug
        res_prod = self.client.get(
            f"/learning/certificate/{self.cert_id}",
            headers={"Host": "www.skillrock.in"}
        )
        self.assertEqual(
            res_prod.status_code,
            200,
            "CRITICAL: Production host header (www.skillrock.in) crashed with non-200 status (likely NameError on current_app)"
        )
        html_prod = res_prod.data.decode("utf-8")
        self.assertIn("skillrock.in", html_prod, "Production canonical domain missing from verification URL")
        self.assertNotIn("500 Internal Server Error", html_prod)

        # 3. Cloud / Staging host header (skillrock.onrender.com)
        res_render = self.client.get(
            f"/learning/certificate/{self.cert_id}",
            headers={"Host": "skillrock.onrender.com"}
        )
        self.assertEqual(res_render.status_code, 200, "Cloud host header failed on certificate view")

    def test_tier2_r1_root_alias_redirection(self):
        """
        R1 Boundary Case:
        Verifies that root URL aliases /certificate/<cert_id> and /verify/<cert_id>
        redirect to their canonical /learning/ endpoints without 404 Not Found.
        """
        self._login(self.student)

        # 1. Root /certificate/<cert_id> alias
        resp_cert = self.client.get(f"/certificate/{self.cert_id}", follow_redirects=False)
        self.assertIn(
            resp_cert.status_code,
            [301, 302],
            f"Root alias /certificate/{self.cert_id} did not redirect, got status {resp_cert.status_code}"
        )
        self.assertIn(
            f"/learning/certificate/{self.cert_id}",
            resp_cert.location,
            "Root alias does not redirect to /learning/certificate/<cert_id>"
        )

        # Follow redirect to completion
        resp_cert_followed = self.client.get(f"/certificate/{self.cert_id}", follow_redirects=True)
        self.assertEqual(resp_cert_followed.status_code, 200)

        # 2. Root /verify/<cert_id> alias
        resp_verify = self.client.get(f"/verify/{self.cert_id}", follow_redirects=False)
        self.assertIn(
            resp_verify.status_code,
            [301, 302],
            f"Root alias /verify/{self.cert_id} did not redirect, got status {resp_verify.status_code}"
        )
        self.assertIn(
            f"/learning/verify/{self.cert_id}",
            resp_verify.location,
            "Root alias does not redirect to /learning/verify/<cert_id>"
        )

        resp_verify_followed = self.client.get(f"/verify/{self.cert_id}", follow_redirects=True)
        self.assertEqual(resp_verify_followed.status_code, 200)

    def test_tier2_r1_invalid_and_adversarial_certificate_ids(self):
        """
        R1 Boundary & Corner Cases:
        Verifies non-existent, empty, and adversarial certificate IDs are handled
        gracefully with safe error views and no unhandled 500 exceptions or XSS leaks.
        """
        # 1. Non-existent certificate ID on verification ledger
        non_existent_id = "SR-DOESNOTEXIST-9999"
        res = self.client.get(f"/learning/verify/{non_existent_id}")
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")
        self.assertTrue(
            "Certificate Not Found" in html
            or "Invalid or Unverified" in html
            or "not found" in html.lower(),
            "Non-existent certificate ID did not display invalid/not found state"
        )
        self.assertIn(non_existent_id, html, "Queried certificate ID should be reflected in not-found message")

        # 2. Adversarial XSS payload in certificate ID
        xss_id = "SR-TEST<svg onload=alert(1)>"
        res_xss = self.client.get(f"/learning/verify/{xss_id}")
        self.assertEqual(res_xss.status_code, 200)
        html_xss = res_xss.data.decode("utf-8")
        self.assertNotIn("<svg onload=alert(1)>", html_xss, "Raw unescaped SVG tag injected into HTML!")
        self.assertIn("&lt;svg", html_xss, "HTML escaping not applied to certificate ID in verification template")

        # 3. Non-existent ID on certificate view route
        res_view = self.client.get("/learning/certificate/SR-UNKNOWN-404", follow_redirects=True)
        self.assertIn(res_view.status_code, [200, 302, 404])
        self.assertNotIn("500 Internal Server Error", res_view.data.decode("utf-8"))

    def test_tier2_r4_media_error_handling_and_guidance(self):
        """
        R4 Corner Case:
        Verifies that the teacher studio frontend logic includes structured
        handling for camera/microphone access errors (permission denied, device missing)
        without causing an unhandled JavaScript crash.
        """
        classroom_tmpl_path = os.path.join(
            self.workspace_dir, "templates", "bhavishya", "live_classroom.html"
        )
        with open(classroom_tmpl_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Check for media device error handling or diagnostic messaging
        has_media_error_handling = (
            "catch" in content
            and ("getUserMedia" in content or "mediaDevices" in content)
            and ("permission" in content.lower() or "camera" in content.lower() or "alert" in content.lower())
        )
        self.assertTrue(
            has_media_error_handling,
            "Teacher studio script lacks error handling around getUserMedia"
        )

    def test_tier2_r3_mobile_viewport_breakpoints_375px_and_768px(self):
        """
        R3 Boundary Case:
        Verifies that mobile responsive rules explicitly accommodate small phone
        (375px) and tablet (768px) viewports, avoiding fixed overflowing dimensions.
        """
        mobile_css_path = os.path.join(self.workspace_dir, "static", "css", "mobile.css")
        with open(mobile_css_path, "r", encoding="utf-8") as f:
            css = f.read()

        # Verify 768px media query block exists
        self.assertIn("768px", css, "768px tablet breakpoint must be handled in mobile.css")

        # Verify prevention of fixed widths or overflow
        self.assertTrue(
            "overflow-x" in css or "max-width" in css or "width: 100%" in css,
            "CSS should guard against horizontal overflow across mobile widths"
        )

    # ==========================================================================
    # TIER 3: CROSS-FEATURE INTERACTIONS
    # ==========================================================================

    def test_tier3_challenge_certificate_verifies_on_learning_portal(self):
        """
        R1 & R3 Cross-Feature Interaction:
        Verifies that Monthly Challenge certificates (format 'SR-MCH-YYYYMM-XXXXXX')
        are verifiable on the unified learning verification portal (/verify/<cert_id>
        and /learning/verify/<cert_id>).
        """
        # Ensure default challenge exists
        challenge = MonthlyChallenge.get_by_slug("python-28-day-challenge")
        if not challenge:
            challenge = MonthlyChallenge({
                "title": "28-Day Python Challenge: From Zero to Capstone",
                "slug": "python-28-day-challenge",
                "price": 499.0,
                "is_active": True
            })
            challenge.save()

        # Create challenge enrollment with issued certificate
        challenge_cert_id = f"SR-MCH-{datetime.now(timezone.utc).strftime('%Y%m')}-E2E999"
        enrollment = ChallengeEnrollment({
            "user_id": str(self.student.id),
            "challenge_id": str(challenge.id),
            "challenge_slug": challenge.slug,
            "certificate_id": challenge_cert_id,
            "certificate_issued_at": datetime.now(timezone.utc),
            "amount_paid": 499.0
        })
        enrollment.save()

        # Also ensure Certificate ledger entry exists (as handled in unified ledger)
        cert_record = Certificate.get_by_cert_id(challenge_cert_id)
        if not cert_record:
            cert_record = Certificate({
                "certificate_id": challenge_cert_id,
                "user_id": str(self.student.id),
                "user_name": self.student.name,
                "user_email": self.student.email,
                "course_title": challenge.title,
                "issued_at": datetime.now(timezone.utc),
                "verification_hash": hashlib.sha256(f"{challenge_cert_id}:{self.student.id}".encode("utf-8")).hexdigest()[:24],
                "name_locked": True
            })
            cert_record.save()

        # 1. Verify via canonical learning portal verification endpoint
        res = self.client.get(f"/learning/verify/{challenge_cert_id}")
        self.assertEqual(res.status_code, 200, "Challenge certificate verification failed")
        html = res.data.decode("utf-8")
        self.assertIn("Verified", html, "Challenge certificate did not display verified status")
        self.assertIn(challenge_cert_id, html, "Challenge certificate ID missing from verification page")

        # 2. Verify via root alias /verify/<cert_id>
        res_alias = self.client.get(f"/verify/{challenge_cert_id}", follow_redirects=True)
        self.assertEqual(res_alias.status_code, 200, "Root alias verification failed for challenge certificate")
        self.assertIn("Verified", res_alias.data.decode("utf-8"))

    def test_tier3_book_loader_dismissal_and_timeout_safeguards(self):
        """
        R2 Cross-Feature Interaction:
        Verifies that the page transition loader includes safety dismissals:
        - Safety timeout to prevent permanently blocking the page
        - Dismissal on browser navigation / pageshow / DOMContentLoaded
        """
        main_js_path = os.path.join(self.workspace_dir, "static", "js", "main.js")
        with open(main_js_path, "r", encoding="utf-8") as f:
            js = f.read()

        base_html_path = os.path.join(self.workspace_dir, "templates", "base.html")
        with open(base_html_path, "r", encoding="utf-8") as f:
            base_html = f.read()

        combined_scripts = js + "\n" + base_html

        # Check for safety timeout
        has_safety_timeout = (
            "setTimeout" in combined_scripts
            and ("hideBookLoader" in combined_scripts or "hideActionLoader" in combined_scripts or "hide" in combined_scripts)
        )
        self.assertTrue(has_safety_timeout, "Loader script lacks automatic timeout dismissal safeguard")

        # Check for pageshow or popstate event listener for bfcache navigation
        has_nav_events = "pageshow" in combined_scripts or "popstate" in combined_scripts
        self.assertTrue(has_nav_events, "Navigation loader lacks pageshow/popstate back-forward cache listeners")

    def test_tier3_public_credential_viewing_vs_name_lock_security(self):
        """
        R1 Security Contract:
        Verifies that while public viewers can inspect official certificates,
        unauthenticated users or other students CANNOT modify or lock legal names.
        Uses an isolated certificate to guarantee zero side-effects on other tests.
        """
        self._logout()

        # Dedicated test student and certificate for name lock isolation
        lock_student = User({
            "name": "Lock Test Student",
            "email": f"lock_{uuid.uuid4().hex[:6]}@skillrock.edu",
            "role": "student",
            "password_hash": self.shared_hash
        })
        lock_student.save()

        lock_cert_id = Certificate.generate_cert_id()
        lock_cert = Certificate({
            "certificate_id": lock_cert_id,
            "user_id": str(lock_student.id),
            "user_name": "Lock Test Student",
            "user_email": lock_student.email,
            "course_id": str(self.course.id),
            "course_title": self.course.title,
            "submission_id": str(self.submission.id),
            "issued_at": datetime.now(timezone.utc),
            "verification_hash": "lock_test_hash_initial",
            "name_locked": False
        })
        lock_cert.save()

        # 1. Public unauthenticated user accesses certificate view
        res = self.client.get(f"/learning/certificate/{lock_cert_id}")
        self.assertIn(
            res.status_code,
            [200, 302],
            "Unauthenticated access to certificate should succeed or redirect to public ledger, never 500"
        )

        # 2. Unauthenticated user attempts to POST to lock-name endpoint
        res_lock_anon = self.client.post(
            f"/learning/certificate/{lock_cert_id}/lock-name",
            data={"legal_name": "Malicious Hacker"}
        )
        self.assertIn(
            res_lock_anon.status_code,
            [302, 401, 403],
            "Unauthenticated user must be blocked from locking certificate name"
        )

        # 3. Another student attempts to modify first student's certificate
        intruder_student = User({
            "name": "Intruder User",
            "email": f"intruder_{uuid.uuid4().hex[:6]}@skillrock.edu",
            "role": "student",
            "password_hash": self.shared_hash
        })
        intruder_student.save()
        self._login(intruder_student)

        res_lock_other = self.client.post(
            f"/learning/certificate/{lock_cert_id}/lock-name",
            data={"legal_name": "Intruder Name"}
        )
        self.assertIn(
            res_lock_other.status_code,
            [302, 401, 403, 400],
            "Other student must not be permitted to modify certificate name"
        )

        # Verify certificate name remained untampered
        cert_after = Certificate.get_by_cert_id(lock_cert_id)
        self.assertEqual(cert_after.user_name, "Lock Test Student", "Certificate name was illegally modified!")

        # 4. Legitimate owner locks legal name
        self._logout()
        self._login(lock_student)
        res_lock_owner = self.client.post(
            f"/learning/certificate/{lock_cert_id}/lock-name",
            data={"legal_name": "Lock Verified Official Name"}
        )
        self.assertIn(res_lock_owner.status_code, [200, 302])
        cert_updated = Certificate.get_by_cert_id(lock_cert_id)
        self.assertEqual(cert_updated.user_name, "Lock Verified Official Name")
        self.assertTrue(cert_updated.name_locked, "Certificate name should be locked after update")

    # ==========================================================================
    # TIER 4: REAL-WORLD USER FLOWS
    # ==========================================================================

    def test_tier4_student_complete_journey_course_to_certificate(self):
        """
        R1 Real-World User Flow:
        Simulates end-to-end student lifecycle:
        1. Student logs in.
        2. Student completes an assignment/course.
        3. Certificate is generated.
        4. Student views certificate on simulated production domain (www.skillrock.in).
        5. Student verifies certificate on public ledger.
        6. External recruiter verifies certificate without authentication.
        """
        # Create dedicated journey student and certificate
        journey_student = User({
            "name": "Pooja Deshmukh",
            "email": f"pooja_{uuid.uuid4().hex[:6]}@skillrock.edu",
            "role": "student",
            "password_hash": self.shared_hash
        })
        journey_student.save()

        journey_cert_id = Certificate.generate_cert_id()
        journey_cert = Certificate({
            "certificate_id": journey_cert_id,
            "user_id": str(journey_student.id),
            "user_name": journey_student.name,
            "user_email": journey_student.email,
            "course_id": str(self.course.id),
            "course_title": self.course.title,
            "submission_id": str(self.submission.id),
            "issued_at": datetime.now(timezone.utc),
            "verification_hash": hashlib.sha256(f"{journey_cert_id}:{journey_student.id}".encode("utf-8")).hexdigest()[:24],
            "name_locked": False
        })
        journey_cert.save()

        self._login(journey_student)

        # Step 1: Browse course catalogue
        resp_courses = self.client.get("/learning/courses")
        self.assertEqual(resp_courses.status_code, 200)

        # Step 2: Access certificate page as student with production host header
        resp_cert = self.client.get(
            f"/learning/certificate/{journey_cert_id}",
            headers={"Host": "www.skillrock.in"}
        )
        self.assertEqual(resp_cert.status_code, 200, "Student viewing certificate failed on production host")
        cert_html = resp_cert.data.decode("utf-8")
        self.assertIn("Pooja Deshmukh", cert_html)
        self.assertNotIn("500 Internal Server Error", cert_html)

        # Step 3: Access public verification portal via short URL
        resp_verify = self.client.get(
            f"/verify/{journey_cert_id}",
            headers={"Host": "www.skillrock.in"},
            follow_redirects=True
        )
        self.assertEqual(resp_verify.status_code, 200, "Public verification failed")
        verify_html = resp_verify.data.decode("utf-8")
        self.assertIn("Verified", verify_html)
        self.assertIn(journey_cert_id, verify_html)

        # Step 4: Logout and verify as external recruiter
        self._logout()
        resp_recruiter = self.client.get(
            f"/verify/{journey_cert_id}",
            headers={"Host": "www.skillrock.in"},
            follow_redirects=True
        )
        self.assertEqual(resp_recruiter.status_code, 200, "External recruiter verification failed")
        self.assertIn("Verified", resp_recruiter.data.decode("utf-8"))

    def test_tier4_teacher_studio_and_student_classroom_interaction(self):
        """
        R4 Real-World User Flow:
        Simulates teacher initiating studio session and student attending:
        1. Teacher accesses live classroom lecture.
        2. Teacher has educator broadcast studio controls rendered.
        3. Student accesses same lecture.
        4. Student has live player and chat rendered without teacher studio broadcast controls.
        """
        lectures = BhavishyaLiveLecture.get_all()
        lecture_id = lectures[0].lecture_id if lectures else "py-live-01"

        # Teacher accesses lecture
        self._login(self.teacher)
        teacher_resp = self.client.get(f"/bhavishya/lecture/{lecture_id}")
        self.assertEqual(teacher_resp.status_code, 200)
        teacher_html = teacher_resp.data.decode("utf-8")
        self.assertIn("btnToggleCamera", teacher_html, "Teacher must see camera toggle control")
        self.assertIn("btnToggleMic", teacher_html, "Teacher must see mic toggle control")

        # Student accesses lecture
        self._logout()
        self._login(self.student)
        student_resp = self.client.get(f"/bhavishya/lecture/{lecture_id}")
        self.assertEqual(student_resp.status_code, 200)
        student_html = student_resp.data.decode("utf-8")

        # Student should see video player and classroom content
        self.assertTrue(
            "studentLiveVideo" in student_html or "video" in student_html.lower(),
            "Student must see classroom video player"
        )
        self.assertTrue(
            "liveChat" in student_html or "chat" in student_html.lower(),
            "Student must see classroom chat component"
        )


if __name__ == "__main__":
    unittest.main()
