"""
Automated Test Suite for Free vs. Paid Pricing & Dynamic UPI QR Access System
Tests:
1. Strict 12-digit UTR format validation and anti-dummy filters.
2. In-memory dynamic UPI QR code generator (zero disk writes, authoritative price embedding).
3. Course and Test Series model backward compatibility (defaulting legacy items to Free).
4. Free Enrollment Security Gate: /enroll-free/<item_type>/<id> strictly enforces 403 on paid items.
5. Anti-Replay Payment Submission: MongoDB uniqueness and duplicate submission prevention.
6. Unified Student Access Guard (verify_student_unlock): admin override, free access, paid unlock.
7. Admin Payments Dashboard & Verification: One-click Approve & Unlock, auto-enrollment, and Rejection.
"""

import os
import unittest
from datetime import datetime, timezone

os.environ["MONGODB_URI"] = ""
os.environ["TESTING"] = "1"

import models.mongo as mongo_mod
mongo_mod._db = None
mongo_mod._mongo_client = None

from app import create_app
from models import get_db, User, Course, Assignment, Enrollment
from models.test_series import TestDefinition, TestPack, UserEntitlement
from services.payment_service import (
    validate_utr,
    generate_upi_qr_base64,
    verify_student_unlock,
    grant_student_access,
    revoke_student_access,
    get_item_by_type_and_id,
)


class TestPaymentPricingSystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        mongo_mod._db = None
        mongo_mod._mongo_client = None
        cls.app = create_app()
        cls.app.config["TESTING"] = True
        cls.app.config["WTF_CSRF_ENABLED"] = False
        cls.client = cls.app.test_client()

    def setUp(self):
        self.db = get_db()
        User._user_cache.clear()
        self.db.users.delete_many({})
        self.db.courses.delete_many({})
        self.db.payments.delete_many({})
        self.db.user_access.delete_many({})
        self.db.enrollments.delete_many({})
        self.db.tests.delete_many({})

        # Create student user
        self.student = User({
            "name": "Aarav Sharma",
            "email": "aarav.student@skillrock.test",
            "role": "student",
            "is_banned": False,
        })
        self.student.set_password("StudentPass123!")
        self.student.save()

        # Create admin user
        self.admin = User({
            "name": "Super Admin",
            "email": "admin@skillrock.test",
            "role": "admin",
            "is_banned": False,
        })
        self.admin.set_password("AdminPass123!")
        self.admin.save()

        # Create a Free Course (legacy course simulation)
        self.free_course = Course({
            "title": "Introduction to Python Programming",
            "slug": "intro-python-programming",
            "youtube_url": "https://www.youtube.com/watch?v=kqtD5dpn9C8",
            "instructor": "Curated Instructor",
            "is_published": True,
            # No is_paid or price passed -> tests backward compatibility
        })
        self.free_course.save()

        # Create a Paid Course (₹699)
        self.paid_course = Course({
            "title": "Full-Stack Web Development Bootcamp",
            "slug": "full-stack-web-development-bootcamp",
            "youtube_url": "https://www.youtube.com/watch?v=kqtD5dpn9C8",
            "instructor": "Master Instructor",
            "is_published": True,
            "is_paid": True,
            "price": 699.0,
        })
        self.paid_course.save()

        # Create a Paid Mock Test (₹99)
        self.paid_test = TestDefinition({
            "title": "TCS NQT Advanced Quantitative Mock Test",
            "slug": "tcs-nqt-adv-quant",
            "category": "Quantitative Aptitude",
            "difficulty": "Intermediate",
            "duration_minutes": 45,
            "total_questions_count": 30,
            "passing_percentage": 60.0,
            "is_free": False,
            "is_paid": True,
            "price": 99.0,
            "is_published": True,
        }).save()

    def login_user(self, email, password):
        return self.client.post("/login", data={
            "email": email,
            "password": password
        }, follow_redirects=True)

    def logout_user(self):
        return self.client.get("/logout", follow_redirects=True)

    # --------------------------------------------------------------------------
    # 1. 12-Digit UTR Validation & Anti-Dummy Tests
    # --------------------------------------------------------------------------
    def test_utr_validation(self):
        # Valid 12-digit genuine UTRs
        valid_utrs = ["429381749201", "837192048572", "192837465019"]
        for utr in valid_utrs:
            is_valid, msg = validate_utr(utr)
            self.assertTrue(is_valid, f"Expected {utr} to be valid, got error: {msg}")

        # Invalid lengths or characters
        invalid_lengths = ["", "123", "12345678901", "1234567890123", "42938174920A"]
        for utr in invalid_lengths:
            is_valid, msg = validate_utr(utr)
            self.assertFalse(is_valid, f"Expected {utr} to fail validation")

        # Blocked dummy sequences
        dummy_utrs = ["123456789012", "000000000000", "111111111111", "999999999999"]
        for utr in dummy_utrs:
            is_valid, msg = validate_utr(utr)
            self.assertFalse(is_valid, f"Expected dummy UTR {utr} to be blocked")

        # Repetitive sequences with low unique digits (< 4 unique digits)
        repetitive = ["121212121212", "112211221122"]
        for utr in repetitive:
            is_valid, msg = validate_utr(utr)
            self.assertFalse(is_valid, f"Expected low-entropy UTR {utr} to be rejected")

    # --------------------------------------------------------------------------
    # 2. In-Memory Dynamic UPI QR Generation Tests (5-Minute Expiry & 9243494968@nyes)
    # --------------------------------------------------------------------------
    def test_in_memory_upi_qr_generation(self):
        qr_info = generate_upi_qr_base64(
            amount=699.0,
            item_type="course",
            item_id=str(self.paid_course.id),
            item_title=self.paid_course.title
        )
        self.assertIn("qr_data_uri", qr_info)
        self.assertTrue(qr_info["qr_data_uri"].startswith("data:image/png;base64,"))
        self.assertIn("am=699.00", qr_info["upi_uri"])
        self.assertIn("cu=INR", qr_info["upi_uri"])
        self.assertIn("9243494968%40nyes", qr_info["upi_uri"])
        self.assertEqual(qr_info["merchant_upi"], "9243494968@nyes")
        self.assertEqual(qr_info["amount"], 699.0)
        self.assertEqual(qr_info["expires_in"], 300)  # Exactly 5 minutes
        self.assertIn("gpay_uri", qr_info)
        self.assertIn("phonepe_uri", qr_info)
        self.assertIn("paytm_uri", qr_info)

    def test_refresh_qr_endpoint(self):
        self.login_user(self.student.email, "StudentPass123!")
        res = self.client.get(f"/payment/refresh-qr/course/{self.paid_course.id}")
        self.assertEqual(res.status_code, 200)
        json_data = res.get_json()
        self.assertTrue(json_data["success"])
        self.assertTrue(json_data["qr_data_uri"].startswith("data:image/png;base64,"))
        self.assertEqual(json_data["merchant_upi"], "9243494968@nyes")
        self.assertEqual(json_data["expires_in"], 300)
        self.assertIsNotNone(json_data["session_token"])

    # --------------------------------------------------------------------------
    # 3. Model Backward Compatibility
    # --------------------------------------------------------------------------
    def test_legacy_course_backward_compatibility(self):
        # Legacy course had no is_paid or price in MongoDB document
        self.assertFalse(self.free_course.is_paid)
        self.assertEqual(self.free_course.price, 0.0)

        # Paid course retains exact price and is_paid flag
        self.assertTrue(self.paid_course.is_paid)
        self.assertEqual(self.paid_course.price, 699.0)

    # --------------------------------------------------------------------------
    # 4. Strict Free Enrollment Security Gate (/enroll-free)
    # --------------------------------------------------------------------------
    def test_enroll_free_security_gate(self):
        self.login_user(self.student.email, "StudentPass123!")

        # Free course allows enrollment (returns 302 redirect to course player)
        res_free = self.client.get(f"/enroll-free/course/{self.free_course.id}")
        self.assertEqual(res_free.status_code, 302)
        self.assertIn(f"/learning/courses/{self.free_course.slug}", res_free.location)

        # CRITICAL SECURITY CHECK: Student attempting free enrollment on ₹699 paid course MUST get 403 Forbidden
        res_paid_attack = self.client.get(f"/enroll-free/course/{self.paid_course.id}")
        self.assertEqual(res_paid_attack.status_code, 403)

        # Paid test attempt on /enroll-free MUST also get 403 Forbidden
        res_test_attack = self.client.get(f"/enroll-free/test_series/{self.paid_test.id}")
        self.assertEqual(res_test_attack.status_code, 403)

    # --------------------------------------------------------------------------
    # 5. Payment Checkout & Anti-Replay UTR Submission
    # --------------------------------------------------------------------------
    def test_payment_checkout_and_submission_anti_replay(self):
        self.login_user(self.student.email, "StudentPass123!")

        # 1. Checkout view renders dynamic QR and price
        res_checkout = self.client.get(f"/payment/checkout/course/{self.paid_course.id}")
        self.assertEqual(res_checkout.status_code, 200)
        self.assertIn(b"699", res_checkout.data)
        self.assertIn(b"data:image/png;base64,", res_checkout.data)

        # 2. Submit payment with valid 12-digit UTR
        test_utr = "938201847592"
        res_submit = self.client.post("/payment/submit", data={
            "item_type": "course",
            "item_id": str(self.paid_course.id),
            "utr_number": test_utr,
            "amount": "1.0"  # Client forgery attempt! Server must ignore this client value
        }, follow_redirects=True)
        self.assertEqual(res_submit.status_code, 200)

        # Verify payment document in MongoDB
        payment_doc = self.db.payments.find_one({"utr_number": test_utr})
        self.assertIsNotNone(payment_doc)
        self.assertEqual(payment_doc["amount"], 699.0)  # Server-locked authoritative price
        self.assertEqual(payment_doc["status"], "pending")
        self.assertEqual(payment_doc["user_id"], str(self.student.id))

        # 3. Anti-Replay Guarantee: Submitting the SAME UTR again must be rejected!
        res_duplicate = self.client.post("/payment/submit", data={
            "item_type": "course",
            "item_id": str(self.paid_course.id),
            "utr_number": test_utr,
        }, follow_redirects=True)
        self.assertEqual(res_duplicate.status_code, 200)
        self.assertIn(b"already been submitted", res_duplicate.data)

    # --------------------------------------------------------------------------
    # 6. Unified Access Guard & Admin Verification Workflow
    # --------------------------------------------------------------------------
    def test_unified_access_guard_and_admin_approval(self):
        # A. Unauthenticated user has NO unlock
        self.assertFalse(verify_student_unlock(None, "course", str(self.paid_course.id)))

        # B. Authenticated student before payment approval has NO unlock on paid item
        self.assertFalse(verify_student_unlock(self.student, "course", str(self.paid_course.id)))

        # C. Free course is automatically unlocked for student
        self.assertTrue(verify_student_unlock(self.student, "course", str(self.free_course.id)))

        # D. Admin user ALWAYS has unlock (Super Admin bypass)
        self.assertTrue(verify_student_unlock(self.admin, "course", str(self.paid_course.id)))

        # E. Student submits payment
        test_utr = "748291039485"
        self.login_user(self.student.email, "StudentPass123!")
        self.client.post("/payment/submit", data={
            "item_type": "course",
            "item_id": str(self.paid_course.id),
            "utr_number": test_utr,
        })
        self.logout_user()

        payment_doc = self.db.payments.find_one({"utr_number": test_utr})
        payment_id = payment_doc["payment_id"]

        # F. Admin approves payment via POST /admin/payments/<payment_id>/approve
        self.login_user(self.admin.email, "AdminPass123!")
        res_approve = self.client.post(f"/admin/payments/{payment_id}/approve", follow_redirects=True)
        self.assertEqual(res_approve.status_code, 200)

        # Verify payment status is approved
        payment_doc_updated = self.db.payments.find_one({"payment_id": payment_id})
        self.assertEqual(payment_doc_updated["status"], "approved")

        # Verify student now has active unlocked access!
        self.assertTrue(verify_student_unlock(self.student, "course", str(self.paid_course.id)))

        # Verify student was auto-enrolled in the course
        enrollment = self.db.enrollments.find_one({
            "user_id": str(self.student.id),
            "course_id": str(self.paid_course.id)
        })
        self.assertIsNotNone(enrollment)

        # G. Admin rejects payment -> revokes access
        res_reject = self.client.post(f"/admin/payments/{payment_id}/reject", data={
            "reason": "Test revocation"
        }, follow_redirects=True)
        self.assertEqual(res_reject.status_code, 200)

        payment_doc_rejected = self.db.payments.find_one({"payment_id": payment_id})
        self.assertEqual(payment_doc_rejected["status"], "rejected")

        # Student no longer has active access
        self.assertFalse(verify_student_unlock(self.student, "course", str(self.paid_course.id)))


if __name__ == "__main__":
    unittest.main()
