"""
Automated Test Suite for Student Ambassador Referral & Checkout Persistence
Covers all 9 scenarios from Phase 15.B of SkillRock Specification:
1. Scenario 1: No referral checkout & payment.
2. Scenario 2: Valid 4-digit SRID normalization (SR1001) & persistence in checkout_sessions + payments.
3. Scenario 3: Invalid SRID format handling.
4. Scenario 4: Incomplete SRID input (< 4 digits).
5. Scenario 5: External API unavailable / cold-start fallback (checkout never blocked).
6. Scenario 6: Payment submission attribution from form and active session.
7. Scenario 7: Admin payment approval strictly preserves SRID (verified via MongoDB).
8. Scenario 8: Referral update before payment submission (latest SRID persisted).
9. Scenario 9: Multi-student referral isolation (zero cross-user contamination).
"""

import os
import unittest
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock

os.environ["MONGODB_URI"] = ""
os.environ["TESTING"] = "1"

import models.mongo as mongo_mod
mongo_mod._db = None
mongo_mod._mongo_client = None

from app import create_app
from models import get_db, User, Course
from services.payment_service import (
    register_checkout_session,
    process_incoming_bank_credit,
)
from routes.payment import validate_srid_authoritative


class TestAmbassadorReferralCheckout(unittest.TestCase):
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
        self.db.checkout_sessions.delete_many({})
        self.db.bank_credits.delete_many({})
        self.db.user_access.delete_many({})

        # Create student 1
        self.student1 = User({
            "name": "Student Alpha",
            "email": "alpha.student@skillrock.test",
            "role": "student",
            "is_banned": False,
        })
        self.student1.set_password("StudentPass123!")
        self.student1.save()

        # Create student 2
        self.student2 = User({
            "name": "Student Beta",
            "email": "beta.student@skillrock.test",
            "role": "student",
            "is_banned": False,
        })
        self.student2.set_password("StudentPass123!")
        self.student2.save()

        # Create admin user
        self.admin = User({
            "name": "Super Admin",
            "email": "admin@skillrock.test",
            "role": "admin",
            "is_banned": False,
        })
        self.admin.set_password("AdminPass123!")
        self.admin.save()

        # Create paid course
        self.paid_course = Course({
            "title": "Systems Programming with C++",
            "slug": "systems-programming-cpp",
            "youtube_url": "https://www.youtube.com/watch?v=kqtD5dpn9C8",
            "instructor": "Master Instructor",
            "is_published": True,
            "is_paid": True,
            "price": 699.0,
        })
        self.paid_course.save()

    def _login(self, email, password):
        self.client.get("/logout", follow_redirects=True)
        return self.client.post("/login", data={
            "email": email,
            "password": password
        }, follow_redirects=True)

    # -------------------------------------------------------------------------
    # Scenario 1: No referral
    # -------------------------------------------------------------------------
    def test_scenario_1_no_referral(self):
        """Student checks out and pays with no referral code."""
        self._login("alpha.student@skillrock.test", "StudentPass123!")

        # 1. Access checkout without referral
        res = self.client.get(f"/payment/checkout/course/{self.paid_course.id}")
        self.assertEqual(res.status_code, 200)

        # Session was registered with no srid
        sess = self.db.checkout_sessions.find_one({"user_id": str(self.student1.id)})
        self.assertIsNotNone(sess)
        self.assertNotIn("srid", sess)

        # 2. Submit payment with empty srid
        utr = "481225049001"
        submit_res = self.client.post("/payment/submit", data={
            "item_type": "course",
            "item_id": str(self.paid_course.id),
            "utr_number": utr,
            "srid": ""
        }, follow_redirects=True)
        self.assertEqual(submit_res.status_code, 200)

        pay = self.db.payments.find_one({"utr_number": utr})
        self.assertIsNotNone(pay)
        self.assertEqual(pay["status"], "pending")
        self.assertNotIn("srid", pay)

    # -------------------------------------------------------------------------
    # Scenario 2: Valid 4-digit SRID normalization & persistence
    # -------------------------------------------------------------------------
    def test_scenario_2_valid_srid_persistence(self):
        """Student enters '1001', persists as 'SR1001' in checkout_sessions & payments."""
        self._login("alpha.student@skillrock.test", "StudentPass123!")

        # Mock external ambassador API returning verified ambassador
        with patch("routes.payment.validate_srid_authoritative") as mock_val:
            mock_val.return_value = (True, "Tanishk Pal", True)

            # 1. Test backend proxy validation
            val_res = self.client.get("/api/sales/validate-srid/1001")
            self.assertEqual(val_res.status_code, 200)
            data = val_res.get_json()
            self.assertTrue(data["valid"])
            self.assertEqual(data["srid"], "SR1001")
            self.assertEqual(data["name"], "Tanishk Pal")

            # 2. Load checkout with ?ref=1001
            res = self.client.get(f"/payment/checkout/course/{self.paid_course.id}?ref=1001")
            self.assertEqual(res.status_code, 200)

            # Verify checkout_sessions document holds 'SR1001'
            sess = self.db.checkout_sessions.find_one({"user_id": str(self.student1.id)})
            self.assertIsNotNone(sess)
            self.assertEqual(sess.get("srid"), "SR1001")

            # 3. Submit payment with srid='SR1001'
            utr = "481225049002"
            submit_res = self.client.post("/payment/submit", data={
                "item_type": "course",
                "item_id": str(self.paid_course.id),
                "utr_number": utr,
                "srid": "SR1001"
            }, follow_redirects=True)
            self.assertEqual(submit_res.status_code, 200)

            pay = self.db.payments.find_one({"utr_number": utr})
            self.assertIsNotNone(pay)
            self.assertEqual(pay.get("srid"), "SR1001")
            self.assertEqual(pay["amount"], 699.0)

    # -------------------------------------------------------------------------
    # Scenario 3: Invalid SRID format handling
    # -------------------------------------------------------------------------
    def test_scenario_3_invalid_srid_handling(self):
        """Malformed or invalid ambassador ID does not crash and is rejected gracefully."""
        self._login("alpha.student@skillrock.test", "StudentPass123!")

        # Non-numeric format or bad length
        val_res = self.client.get("/api/sales/validate-srid/ABCD")
        data = val_res.get_json()
        self.assertFalse(data["valid"])

        # When API returns non-existent ambassador
        with patch("routes.payment.validate_srid_authoritative") as mock_val:
            mock_val.return_value = (False, None, True)
            val_res2 = self.client.get("/api/sales/validate-srid/9999")
            data2 = val_res2.get_json()
            self.assertFalse(data2["valid"])
            self.assertIn("Invalid Ambassador ID", data2["message"])

    # -------------------------------------------------------------------------
    # Scenario 4: Incomplete SRID input (< 4 digits)
    # -------------------------------------------------------------------------
    def test_scenario_4_incomplete_srid(self):
        """Entering 1-3 digits does not qualify as a valid SRID."""
        self._login("alpha.student@skillrock.test", "StudentPass123!")

        for short_id in ["1", "10", "100"]:
            val_res = self.client.get(f"/api/sales/validate-srid/{short_id}")
            data = val_res.get_json()
            self.assertFalse(data["valid"])

    # -------------------------------------------------------------------------
    # Scenario 5: External API unavailable / cold-start fallback
    # -------------------------------------------------------------------------
    def test_scenario_5_api_unavailable_fallback(self):
        """When ambassador server is sleeping (404/no-server/timeout), checkout is NEVER blocked."""
        self._login("alpha.student@skillrock.test", "StudentPass123!")

        # Simulate service down / cold start
        with patch("routes.payment.validate_srid_authoritative") as mock_val:
            mock_val.return_value = (False, None, False)

            val_res = self.client.get("/api/sales/validate-srid/1001")
            self.assertEqual(val_res.status_code, 200)
            data = val_res.get_json()
            self.assertFalse(data["valid"])
            self.assertFalse(data["available"])
            self.assertIn("temporarily unavailable", data["message"])

            # Student still proceeds with checkout cleanly
            utr = "481225049005"
            submit_res = self.client.post("/payment/submit", data={
                "item_type": "course",
                "item_id": str(self.paid_course.id),
                "utr_number": utr,
                "srid": "1001"
            }, follow_redirects=True)
            self.assertEqual(submit_res.status_code, 200)

            # Payment succeeds and preserves srid
            pay = self.db.payments.find_one({"utr_number": utr})
            self.assertIsNotNone(pay)
            self.assertEqual(pay.get("srid"), "SR1001")

    # -------------------------------------------------------------------------
    # Scenario 6: Payment proof submission attribution from active session
    # -------------------------------------------------------------------------
    def test_scenario_6_payment_proof_submission_attribution(self):
        """Even if form omits srid, it falls back to active checkout session srid."""
        self._login("alpha.student@skillrock.test", "StudentPass123!")

        # Register checkout session with SR1001
        session_token = "TESTSESS6"
        register_checkout_session(
            user_id=str(self.student1.id),
            item_type="course",
            item_id=str(self.paid_course.id),
            session_token=session_token,
            amount=699.0,
            srid="SR1001",
        )

        # Submit payment without srid in form payload
        utr = "481225049006"
        submit_res = self.client.post("/payment/submit", data={
            "item_type": "course",
            "item_id": str(self.paid_course.id),
            "utr_number": utr,
        }, follow_redirects=True)
        self.assertEqual(submit_res.status_code, 200)

        pay = self.db.payments.find_one({"utr_number": utr})
        self.assertIsNotNone(pay)
        self.assertEqual(pay.get("srid"), "SR1001")

    # -------------------------------------------------------------------------
    # Scenario 7: Admin payment approval strictly preserves SRID
    # -------------------------------------------------------------------------
    def test_scenario_7_admin_approval_preserves_srid(self):
        """CRITICAL: Admin approval does NOT delete, overwrite, or reset srid."""
        now = datetime.now(timezone.utc)
        payment_id = "PAY-20261108-TEST7"
        utr = "481225049007"

        # Create pending payment document with srid
        self.db.payments.insert_one({
            "payment_id": payment_id,
            "user_id": str(self.student1.id),
            "user_name": "Student Alpha",
            "user_email": "alpha.student@skillrock.test",
            "item_type": "course",
            "item_id": str(self.paid_course.id),
            "item_title": "Systems Programming with C++",
            "amount": 699.0,
            "utr_number": utr,
            "status": "pending",
            "srid": "SR1001",
            "submitted_at": now,
            "reviewed_at": None,
            "reviewed_by": None,
            "created_at": now,
            "updated_at": now,
        })
        self.db.ambassador_sales.insert_one({
            "payment_id": payment_id,
            "srid": "SR1001",
            "status": "pending",
            "amount": 699.0,
        })

        # Login as Admin
        self._login("admin@skillrock.test", "AdminPass123!")

        # Approve payment
        approve_res = self.client.post(f"/admin/payments/{payment_id}/approve", follow_redirects=True)
        self.assertEqual(approve_res.status_code, 200)

        # Query MongoDB directly to verify srid is intact
        approved_pay = self.db.payments.find_one({"payment_id": payment_id})
        self.assertIsNotNone(approved_pay)
        self.assertEqual(approved_pay["status"], "approved")
        self.assertEqual(approved_pay.get("srid"), "SR1001", "CRITICAL: srid was modified or wiped by admin approval!")
        self.assertEqual(approved_pay.get("amount"), 699.0)
        self.assertEqual(approved_pay.get("utr_number"), utr)

        # Verify ambassador_sales updated to approved
        approved_sale = self.db.ambassador_sales.find_one({"payment_id": payment_id})
        self.assertIsNotNone(approved_sale)
        self.assertEqual(approved_sale["status"], "approved")

    # -------------------------------------------------------------------------
    # Scenario 8: Referral update before payment submission
    # -------------------------------------------------------------------------
    def test_scenario_8_referral_update_before_submission(self):
        """Student updates referral code before submitting; latest valid SRID is persisted."""
        self._login("alpha.student@skillrock.test", "StudentPass123!")

        session_token = "SESS-TOKEN-8"
        register_checkout_session(
            user_id=str(self.student1.id),
            item_type="course",
            item_id=str(self.paid_course.id),
            session_token=session_token,
            amount=699.0,
            srid="SR1001",
        )

        # Update referral via AJAX
        update_res = self.client.post("/payment/update-referral", json={
            "session_token": session_token,
            "srid": "1002"
        })
        self.assertEqual(update_res.status_code, 200)
        self.assertEqual(update_res.get_json()["srid"], "SR1002")

        sess = self.db.checkout_sessions.find_one({"session_token": session_token})
        self.assertEqual(sess.get("srid"), "SR1002")

        # Submit payment with the updated referral
        utr = "481225049008"
        submit_res = self.client.post("/payment/submit", data={
            "item_type": "course",
            "item_id": str(self.paid_course.id),
            "utr_number": utr,
            "srid": "SR1002"
        }, follow_redirects=True)
        self.assertEqual(submit_res.status_code, 200)

        pay = self.db.payments.find_one({"utr_number": utr})
        self.assertEqual(pay.get("srid"), "SR1002")

    # -------------------------------------------------------------------------
    # Scenario 9: Multi-student referral isolation
    # -------------------------------------------------------------------------
    def test_scenario_9_multiple_students_referral_isolation(self):
        """Two concurrent students purchasing the same course with different SRIDs remain isolated."""
        # Student 1 with SR1001
        self._login("alpha.student@skillrock.test", "StudentPass123!")
        token1 = "SESS-ALPHA"
        register_checkout_session(
            user_id=str(self.student1.id),
            item_type="course",
            item_id=str(self.paid_course.id),
            session_token=token1,
            amount=699.0,
            srid="SR1001"
        )
        self.client.post("/payment/submit", data={
            "item_type": "course",
            "item_id": str(self.paid_course.id),
            "utr_number": "481225049011",
            "srid": "SR1001"
        })

        # Student 2 with SR1002
        self._login("beta.student@skillrock.test", "StudentPass123!")
        token2 = "SESS-BETA"
        register_checkout_session(
            user_id=str(self.student2.id),
            item_type="course",
            item_id=str(self.paid_course.id),
            session_token=token2,
            amount=699.0,
            srid="SR1002"
        )
        self.client.post("/payment/submit", data={
            "item_type": "course",
            "item_id": str(self.paid_course.id),
            "utr_number": "481225049012",
            "srid": "SR1002"
        })

        # Verify Student 1 records
        sess1 = self.db.checkout_sessions.find_one({"session_token": token1})
        pay1 = self.db.payments.find_one({"utr_number": "481225049011"})
        self.assertEqual(sess1.get("srid"), "SR1001")
        self.assertEqual(pay1.get("srid"), "SR1001")
        self.assertEqual(pay1.get("user_id"), str(self.student1.id))

        # Verify Student 2 records
        sess2 = self.db.checkout_sessions.find_one({"session_token": token2})
        pay2 = self.db.payments.find_one({"utr_number": "481225049012"})
        self.assertEqual(sess2.get("srid"), "SR1002")
        self.assertEqual(pay2.get("srid"), "SR1002")
        self.assertEqual(pay2.get("user_id"), str(self.student2.id))

    # -------------------------------------------------------------------------
    # Scenario 10: Admin payment rejection updates ambassador sale status
    # -------------------------------------------------------------------------
    def test_scenario_10_ambassador_sales_admin_rejection(self):
        """Admin rejection marks both payment and ambassador sale as rejected."""
        now = datetime.now(timezone.utc)
        payment_id = "PAY-20261108-REJ10"
        utr = "481225049013"

        self.db.payments.insert_one({
            "payment_id": payment_id,
            "user_id": str(self.student1.id),
            "user_name": "Student Alpha",
            "user_email": "alpha.student@skillrock.test",
            "item_type": "course",
            "item_id": str(self.paid_course.id),
            "amount": 699.0,
            "utr_number": utr,
            "status": "pending",
            "srid": "SR1001",
            "submitted_at": now,
        })
        self.db.ambassador_sales.insert_one({
            "payment_id": payment_id,
            "srid": "SR1001",
            "status": "pending",
            "amount": 699.0,
        })

        self._login("admin@skillrock.test", "AdminPass123!")
        rej_res = self.client.post(f"/admin/payments/{payment_id}/reject", data={
            "reason": "UTR fake or invalid"
        }, follow_redirects=True)
        self.assertEqual(rej_res.status_code, 200)

        rej_pay = self.db.payments.find_one({"payment_id": payment_id})
        self.assertEqual(rej_pay["status"], "rejected")

        rej_sale = self.db.ambassador_sales.find_one({"payment_id": payment_id})
        self.assertIsNotNone(rej_sale)
        self.assertEqual(rej_sale["status"], "rejected")

    # -------------------------------------------------------------------------
    # Scenario 11: SRID:SR Prefix Normalization (?ref=SRID:SR1001)
    # -------------------------------------------------------------------------
    def test_scenario_11_srid_prefix_normalization(self):
        """Both ?ref=SRID:SR1001 and ?ref=1001 normalize into SR1001 in session."""
        self._login("alpha.student@skillrock.test", "StudentPass123!")

        res = self.client.get(f"/payment/checkout/course/{self.paid_course.id}?ref=SRID:SR1001")
        self.assertEqual(res.status_code, 200)
        sess = self.db.checkout_sessions.find_one({"user_id": str(self.student1.id)})
        self.assertIsNotNone(sess)
        self.assertEqual(sess.get("srid"), "SR1001")

    # -------------------------------------------------------------------------
    # Scenario 12: Admin Search By SRID and Badge Rendering
    # -------------------------------------------------------------------------
    def test_scenario_12_admin_search_by_srid_and_badge_rendering(self):
        """Admin can search payments by SRID and see the printed SRID:SR1001 badge."""
        now = datetime.now(timezone.utc)
        payment_id = "PAY-20261108-SRCH12"
        utr = "481225049014"

        self.db.payments.insert_one({
            "payment_id": payment_id,
            "user_id": str(self.student1.id),
            "user_name": "Student Alpha",
            "user_email": "alpha.student@skillrock.test",
            "item_type": "course",
            "item_id": str(self.paid_course.id),
            "item_title": "Systems Programming with C++",
            "amount": 699.0,
            "utr_number": utr,
            "status": "pending",
            "srid": "SR1001",
            "submitted_at": now,
        })

        self._login("admin@skillrock.test", "AdminPass123!")
        search_res = self.client.get("/admin/payments?q=SR1001")
        self.assertEqual(search_res.status_code, 200)
        html = search_res.get_data(as_text=True)
        self.assertIn("Ambassador SRID:SR1001", html)
        self.assertIn(utr, html)


if __name__ == "__main__":
    unittest.main()
