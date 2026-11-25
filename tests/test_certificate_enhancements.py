import os
os.environ["MONGODB_URI"] = ""
import sys
import unittest
from datetime import datetime, timezone

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.stdout.reconfigure(encoding="utf-8")

from app import create_app
from models.mongo import (
    get_db,
    User,
    Course,
    Assignment,
    Submission,
    Certificate
)


class TestCertificateEnhancements(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        from config import Config
        Config.TESTING = True
        Config.WTF_CSRF_ENABLED = False
        cls.app = create_app(Config)
        cls.app.config["TESTING"] = True
        cls.app.config["WTF_CSRF_ENABLED"] = False
        cls.app.config["SESSION_COOKIE_SECURE"] = False
        cls.client = cls.app.test_client()

    def setUp(self):
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.db = get_db()

    def tearDown(self):
        self.app_context.pop()

    def test_canonical_course_titles(self):
        """Verify that course titles are properly cleaned and canonicalized for certificates."""
        # Predefined canonical course
        course_sql = Course({
            "title": "SQL Complete Course in 3 Hours — MySQL",
            "slug": "sql-complete-course-in-3-hours-mysql"
        })
        self.assertEqual(course_sql.get_certificate_title(), "SQL & Relational Database Management")

        course_aiml = Course({
            "title": "Complete AI/ML Job Ready Batch — Introduction",
            "slug": "complete-aiml-job-ready-batch-introduction"
        })
        self.assertEqual(course_aiml.get_certificate_title(), "Artificial Intelligence & Machine Learning Fundamentals")

        # Unknown course with clickbait noise
        course_custom = Course({
            "title": "Learn Docker in 4 Hours: Complete Bootcamp from Scratch",
            "slug": "learn-docker-in-4-hours"
        })
        clean_title = course_custom.get_certificate_title()
        self.assertNotIn("4 Hours", clean_title)
        self.assertNotIn("Bootcamp", clean_title)
        self.assertIn("Docker", clean_title)

    def test_one_time_name_lock(self):
        """
        Verify that a user can update their name once, that it permanently locks,
        re-hashes the certificate, syncs the user profile, and rejects subsequent edits.
        """
        # Create test student
        student = User({
            "email": f"namelock_{datetime.now().timestamp()}@example.com",
            "name": "Initial Nickname",
            "role": "student"
        })
        student.save()

        # Get or create course
        course = Course.get_by_slug("sql-complete-course-in-3-hours-mysql")
        if not course:
            course = Course({
                "title": "SQL Complete Course in 3 Hours — MySQL",
                "slug": f"sql-course-{datetime.now().timestamp()}"
            })
            course.save()

        cert = Certificate({
            "certificate_id": Certificate.generate_cert_id(),
            "user_id": str(student.id),
            "user_name": student.name,
            "user_email": student.email,
            "course_id": str(course.id),
            "course_title": course.title,
            "issued_at": datetime.now(timezone.utc),
            "verification_hash": "old_hash_123",
            "name_locked": False
        })
        cert.save()

        self.assertFalse(cert.name_locked)
        self.assertEqual(cert.user_name, "Initial Nickname")

        # 1. First Name Lock (Must Succeed)
        success, msg = cert.lock_legal_name("Alexander J. Mercer")
        self.assertTrue(success)
        self.assertTrue(cert.name_locked)
        self.assertEqual(cert.user_name, "Alexander J. Mercer")
        self.assertNotEqual(cert.verification_hash, "old_hash_123")

        # Verify User profile was synchronized
        updated_user = User.get_by_id(student.id)
        self.assertEqual(updated_user.name, "Alexander J. Mercer")

        # 2. Second Name Lock Attempt (MUST Fail)
        success_second, msg_second = cert.lock_legal_name("Attempted Fraud Name")
        self.assertFalse(success_second)
        self.assertIn("already been permanently locked", msg_second)
        self.assertEqual(cert.user_name, "Alexander J. Mercer")

    def test_certificate_display_course_title(self):
        """Verify Certificate.display_course_title resolves to clean title."""
        course = Course.get_by_slug("complete-c-programming-tutorial-for-beginners")
        if not course:
            course = Course({
                "title": "Complete C++ Programming Tutorial for Beginners",
                "slug": f"cpp-{datetime.now().timestamp()}"
            })
            course.save()

        unique_user_id = f"test_user_disp_{datetime.now().timestamp()}"
        cert = Certificate({
            "certificate_id": Certificate.generate_cert_id(),
            "user_id": unique_user_id,
            "user_name": "Test User",
            "course_id": str(course.id),
            "course_title": course.title,
            "issued_at": datetime.now(timezone.utc)
        })
        cert.save()

        self.assertEqual(cert.display_course_title, "C++ Systems Programming & Software Development")

    def test_lock_name_route(self):
        """Verify the lock-name route updates the name and requires authentication."""
        student = User({
            "email": f"route_lock_{datetime.now().timestamp()}@example.com",
            "name": "Demo Student",
            "role": "student"
        })
        student.set_password("Pass1234!")
        student.save()

        course = Course.get_by_slug("sql-complete-course-in-3-hours-mysql")
        if not course:
            course = Course({
                "title": "SQL Complete Course in 3 Hours — MySQL",
                "slug": f"sql-{datetime.now().timestamp()}"
            })
            course.save()

        cert = Certificate({
            "certificate_id": Certificate.generate_cert_id(),
            "user_id": str(student.id),
            "user_name": "Demo Student",
            "course_id": str(course.id),
            "course_title": course.title,
            "issued_at": datetime.now(timezone.utc),
            "name_locked": False
        })
        cert.save()

        # Login as student
        with self.client.session_transaction() as sess:
            sess["_user_id"] = str(student.id)

        # POST lock-name
        resp = self.client.post(
            f"/learning/certificate/{cert.certificate_id}/lock-name",
            json={"legal_name": "Official Verified Name"}
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["updated_name"], "Official Verified Name")

        # Refetch from DB
        updated_cert = Certificate.get_by_cert_id(cert.certificate_id)
        self.assertTrue(updated_cert.name_locked)
        self.assertEqual(updated_cert.user_name, "Official Verified Name")

    def test_whitespace_cert_id_returns_none_and_unverified(self):
        """
        Regression test: whitespace-only cert_ids (' ', '%20', '\\t') must return None
        and never match uncertified ChallengeEnrollment records (certificate_id='').
        """
        from models.challenge import ChallengeEnrollment
        from routes.learning import _resolve_certificate_or_challenge

        unfinished_student = User({
            "email": f"unfinished_{datetime.now().timestamp()}@example.com",
            "name": "Unfinished Whitespace Student",
            "role": "student"
        })
        unfinished_student.save()

        # Uncertified enrollment persists certificate_id="" in MongoDB
        enr = ChallengeEnrollment({
            "user_id": str(unfinished_student.id),
            "challenge_slug": "python-28-day-challenge",
            "certificate_id": ""
        })
        enr.save()

        for bad_id in ("", " ", "   ", "\t", "\n"):
            self.assertIsNone(ChallengeEnrollment.get_by_certificate_id(bad_id))
            self.assertIsNone(Certificate.get_by_cert_id(bad_id))
            self.assertIsNone(_resolve_certificate_or_challenge(bad_id))

        # HTTP verification with %20 and %09 must render unverified/not-found
        for encoded in ("%20", "%09"):
            resp = self.client.get(f"/learning/verify/{encoded}")
            self.assertEqual(resp.status_code, 200)
            self.assertNotIn(b"Verified Authentic Credential", resp.data)
            self.assertNotIn(b"Unfinished Whitespace Student", resp.data)
            self.assertIn(b"Certificate Not Found", resp.data)

        # Certificate view with %20 must redirect and not leak uncertified student
        resp_view = self.client.get("/learning/certificate/%20")
        self.assertEqual(resp_view.status_code, 302)
        self.assertNotIn(b"Unfinished Whitespace Student", resp_view.data)

    def test_course_title_sanitization_and_no_slug_hijacking(self):
        """
        Verify unrelated slugs are not hijacked by canonical matching and
        'Full Stack' / '28-Day Coding Challenge' are preserved by regex sanitization.
        """
        rust_course = Course({"title": "Introduction to Rust", "slug": "introduction"})
        self.assertEqual(rust_course.get_certificate_title(), "Introduction to Rust")

        cpp_engine = Course({"title": "C++ Game Engine Design", "slug": "cpp-game-engine"})
        self.assertEqual(cpp_engine.get_certificate_title(), "C++ Game Engine Design")

        fullstack = Course({"title": "Full Stack Django Development", "slug": "full-stack-django"})
        self.assertEqual(fullstack.get_certificate_title(), "Full Stack Django Development")

        complete_fullstack = Course({"title": "Complete Full Stack Web Course", "slug": "complete-full-stack-web"})
        self.assertEqual(complete_fullstack.get_certificate_title(), "Full Stack Web")

        challenge_cert = Certificate({
            "course_id": "nonexistent_challenge_id",
            "course_title": "Python 28-Day Coding Challenge"
        })
        self.assertEqual(challenge_cert.display_course_title, "Python 28-Day Coding Challenge")

        cpp_engine_cert = Certificate({
            "course_id": "nonexistent_cpp_id",
            "course_title": "C++ Game Engine Design"
        })
        self.assertEqual(cpp_engine_cert.display_course_title, "C++ Game Engine Design")

    def test_challenge_certificate_hash_and_title_consistency(self):
        """
        Verify persisted challenge certificates and fallback ChallengeEnrollment resolution
        produce identical verification_hash and display_course_title.
        """
        from models.challenge import ChallengeEnrollment, MonthlyChallenge
        from routes.learning import _resolve_certificate_or_challenge

        student = User({
            "email": f"ch_hash_{datetime.now().timestamp()}@example.com",
            "name": "Hash Consistency Student",
            "role": "student"
        })
        student.save()

        challenge = MonthlyChallenge.get_by_slug("python-28-day-challenge")
        if not challenge:
            challenge = MonthlyChallenge({
                "title": "Python 28-Day Coding Challenge",
                "slug": "python-28-day-challenge",
                "is_active": True
            })
            challenge.save()

        cert_id = f"SR-MCH-202611-{datetime.now().strftime('%H%M%S')}"
        issued_at = datetime.now(timezone.utc)
        enr = ChallengeEnrollment({
            "user_id": str(student.id),
            "challenge_id": str(challenge.id),
            "challenge_slug": challenge.slug,
            "certificate_id": cert_id,
            "certificate_issued_at": issued_at,
        })
        enr.save()

        # Persisted path (as used by routes/challenge.py)
        persisted = Certificate.build_challenge_certificate(enr, challenge=challenge, user=student)
        persisted.save()
        loaded = _resolve_certificate_or_challenge(cert_id)
        self.assertIsNotNone(loaded)

        # Fallback path (simulate missing db.certificates entry)
        self.db.certificates.delete_one({"certificate_id": cert_id})
        fallback = _resolve_certificate_or_challenge(cert_id)
        self.assertIsNotNone(fallback)

        self.assertEqual(loaded.verification_hash, fallback.verification_hash)
        self.assertEqual(loaded.display_course_title, fallback.display_course_title)
        self.assertEqual(fallback.display_course_title, challenge.title)

    def test_template_hardening_modal_gate_and_js_escaping(self):
        """
        Verify #nameLockModal is only rendered when is_owner and not locked,
        and JS variables use safe JSON serialization.
        """
        student = User({
            "email": f"tmpl_hard_{datetime.now().timestamp()}@example.com",
            "name": 'Aarav \\ "Test" Student',
            "role": "student"
        })
        student.set_password("Pass1234!")
        student.save()

        cert = Certificate({
            "certificate_id": Certificate.generate_cert_id(),
            "user_id": str(student.id),
            "user_name": student.name,
            "user_email": student.email,
            "course_id": "missing_course",
            "course_title": "Full Stack Web Development",
            "issued_at": datetime.now(timezone.utc),
            "name_locked": False
        })
        cert.save()

        # Anonymous viewer should NOT see #nameLockModal in DOM
        anon_client = self.app.test_client()
        resp_anon = anon_client.get(f"/learning/certificate/{cert.certificate_id}")
        self.assertEqual(resp_anon.status_code, 200)
        self.assertNotIn(b'id="nameLockModal"', resp_anon.data)
        # Backslash/quote in studentName must be JSON-escaped
        self.assertIn(b'const studentName = "Aarav_\\\\_\\"Test\\"_Student"', resp_anon.data)

        # Owner should see #nameLockModal when unlocked
        owner_client = self.app.test_client()
        owner_client.post("/login", data={"email": student.email, "password": "Pass1234!"})
        resp_owner = owner_client.get(f"/learning/certificate/{cert.certificate_id}")
        self.assertEqual(resp_owner.status_code, 200)
        self.assertIn(b'id="nameLockModal"', resp_owner.data)

        # Once locked, owner should no longer see #nameLockModal
        cert.lock_legal_name("Aarav Verified")
        resp_locked = owner_client.get(f"/learning/certificate/{cert.certificate_id}")
        self.assertEqual(resp_locked.status_code, 200)
        self.assertNotIn(b'id="nameLockModal"', resp_locked.data)


if __name__ == "__main__":
    unittest.main()
