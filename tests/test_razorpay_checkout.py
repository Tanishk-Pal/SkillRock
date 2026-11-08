"""
Comprehensive Automated Test Suite for Razorpay Standard Web Checkout Integration
Tests:
1. Create Order API:
   - Valid order creation with amount in paise
   - Course-based order creation with authoritative server pricing
   - Rejection of amounts < 100 paise (HTTP 400)
   - Missing parameter validation (HTTP 400)
   - Handling of Razorpay client errors
2. Verify Payment API:
   - Missing required fields rejection (HTTP 400)
   - Cryptographic HMAC-SHA256 signature verification
   - Signature mismatch rejection (HTTP 400, no access granted)
   - Successful signature verification -> Instant approval & access unlock
   - Ambassador referral attribution persistence in db.ambassador_sales
   - Anti-replay duplicate prevention
"""

import hmac
import hashlib
import unittest
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock

from app import create_app
from config import Config
from models import get_db, User, Course


class TestRazorpayStandardCheckout(unittest.TestCase):

    def setUp(self):
        Config.TESTING = True
        Config.WTF_CSRF_ENABLED = False
        self.app = create_app(Config)
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()
        self.db = get_db()

        self.test_key_id = "rzp_test_TxeO2bqvHBawXV"
        self.test_key_secret = "NXO31DDo2ra8jY755OFJMpZU"

        # Clean collections
        self.db.users.delete_many({"email": {"$regex": r".*@razorpaytest\.skillrock$"}})
        self.db.courses.delete_many({"slug": "razorpay-test-course"})
        self.db.payments.delete_many({"gateway": "razorpay"})
        self.db.razorpay_orders.delete_many({})
        self.db.user_access.delete_many({"item_type": "course"})
        self.db.ambassador_sales.delete_many({"srid": "SR9999"})

        # Create test student
        self.student = User({
            "name": "Razorpay Student",
            "email": "student@razorpaytest.skillrock",
            "role": "student",
            "is_banned": False,
        })
        self.student.set_password("StudentPass123!")
        self.student.save()

        # Create test course
        self.course = Course({
            "title": "Full Stack Mastery with Razorpay",
            "slug": "razorpay-test-course",
            "instructor": "Lead Engineer",
            "is_published": True,
            "is_paid": True,
            "price": 499.0,
        })
        self.course.save()

    def tearDown(self):
        self.db.users.delete_many({"email": {"$regex": r".*@razorpaytest\.skillrock$"}})
        self.db.courses.delete_many({"slug": "razorpay-test-course"})
        self.db.payments.delete_many({"gateway": "razorpay"})
        self.db.razorpay_orders.delete_many({})
        self.db.user_access.delete_many({"item_type": "course"})
        self.db.ambassador_sales.delete_many({"srid": "SR9999"})

    def _login(self):
        self.client.get("/logout")
        return self.client.post("/login", data={
            "email": "student@razorpaytest.skillrock",
            "password": "StudentPass123!"
        }, follow_redirects=True)

    # -------------------------------------------------------------------------
    # 1. Create Order Endpoint Tests
    # -------------------------------------------------------------------------

    def test_create_order_below_minimum_amount(self):
        """Reject order if amount < 100 paise."""
        res = self.client.post("/api/create-order", json={"amount": 99})
        self.assertEqual(res.status_code, 400)
        data = res.get_json()
        self.assertIn("100 paise", data.get("error", ""))

    def test_create_order_missing_parameters(self):
        """Reject if neither item nor amount is provided."""
        res = self.client.post("/api/create-order", json={})
        self.assertEqual(res.status_code, 400)
        data = res.get_json()
        self.assertIn("provided", data.get("error", ""))

    def test_create_order_with_valid_direct_amount(self):
        """Creates order when given direct amount >= 100 paise."""
        fake_order = {
            "id": "order_test_direct_123",
            "amount": 49900,
            "currency": "INR",
        }
        with patch("routes.payment.get_razorpay_client") as mock_client:
            mock_inst = MagicMock()
            mock_inst.order.create.return_value = fake_order
            mock_client.return_value = mock_inst

            res = self.client.post("/api/create-order", json={
                "amount": 49900,
                "currency": "INR",
                "receipt": "rcpt_direct_001"
            })
            self.assertEqual(res.status_code, 200)
            data = res.get_json()
            self.assertEqual(data["order_id"], "order_test_direct_123")
            self.assertEqual(data["amount"], 49900)
            self.assertEqual(data["currency"], "INR")
            self.assertIn("key_id", data)

    def test_create_order_with_course_item(self):
        """Creates order based on authoritative course price from database."""
        self._login()
        fake_order = {
            "id": "order_course_456",
            "amount": 49900,
            "currency": "INR",
        }
        with patch("routes.payment.get_razorpay_client") as mock_client:
            mock_inst = MagicMock()
            mock_inst.order.create.return_value = fake_order
            mock_client.return_value = mock_inst

            res = self.client.post("/api/create-order", json={
                "item_type": "course",
                "item_id": str(self.course.id),
                "srid": "9999"
            })
            self.assertEqual(res.status_code, 200)
            data = res.get_json()
            self.assertEqual(data["order_id"], "order_course_456")
            self.assertEqual(data["amount"], 49900)

            # Check that order record is saved in MongoDB
            saved_order = self.db.razorpay_orders.find_one({"order_id": "order_course_456"})
            self.assertIsNotNone(saved_order)
            self.assertEqual(saved_order["amount"], 49900)
            self.assertEqual(saved_order["srid"], "SR9999")

    # -------------------------------------------------------------------------
    # 2. Verify Payment Signature Endpoint Tests
    # -------------------------------------------------------------------------

    def test_verify_payment_missing_fields(self):
        """Rejects request missing order_id, payment_id, or signature."""
        res = self.client.post("/api/verify-payment", json={
            "razorpay_order_id": "order_123"
        })
        self.assertEqual(res.status_code, 400)
        data = res.get_json()
        self.assertFalse(data.get("success", True))
        self.assertIn("Missing required fields", data.get("error", ""))

    def test_verify_payment_invalid_signature(self):
        """Rejects forged or invalid HMAC-SHA256 signature and refuses access."""
        self._login()
        order_id = "order_test_invalid_sig"
        payment_id = "pay_test_999"
        tampered_sig = "abcdef0123456789invalid"

        res = self.client.post("/api/verify-payment", json={
            "razorpay_order_id": order_id,
            "razorpay_payment_id": payment_id,
            "razorpay_signature": tampered_sig,
            "item_type": "course",
            "item_id": str(self.course.id),
        })
        self.assertEqual(res.status_code, 400)
        data = res.get_json()
        self.assertFalse(data.get("success", True))
        self.assertIn("Invalid signature", data.get("error", ""))

        # Verify NO payment or unlock was created
        pay = self.db.payments.find_one({"razorpay_payment_id": payment_id})
        self.assertIsNone(pay)

        ua = self.db.user_access.find_one({"user_id": str(self.student.id), "item_id": str(self.course.id)})
        self.assertIsNone(ua)

    def test_verify_payment_valid_signature_success(self):
        """Authentic HMAC-SHA256 signature approves payment and unlocks student access."""
        self._login()
        order_id = "order_test_valid_ok"
        payment_id = "pay_test_real_789"

        # Generate authentic HMAC-SHA256 signature using test secret
        msg = f"{order_id}|{payment_id}".encode("utf-8")
        valid_signature = hmac.new(
            self.test_key_secret.encode("utf-8"),
            msg,
            hashlib.sha256
        ).hexdigest()

        # Seed pre-existing order in db
        self.db.razorpay_orders.insert_one({
            "order_id": order_id,
            "amount": 49900,
            "currency": "INR",
            "user_id": str(self.student.id),
            "item_type": "course",
            "item_id": str(self.course.id),
            "srid": "SR9999",
            "status": "created",
            "created_at": datetime.now(timezone.utc),
        })

        res = self.client.post("/api/verify-payment", json={
            "razorpay_order_id": order_id,
            "razorpay_payment_id": payment_id,
            "razorpay_signature": valid_signature,
            "item_type": "course",
            "item_id": str(self.course.id),
            "srid": "SR9999"
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data.get("success"))
        self.assertIn("redirect_url", data)

        # Verify payment record in MongoDB
        payment_doc = self.db.payments.find_one({"razorpay_payment_id": payment_id})
        self.assertIsNotNone(payment_doc)
        self.assertEqual(payment_doc["status"], "approved")
        self.assertEqual(payment_doc["amount"], 499.0)
        self.assertEqual(payment_doc["gateway"], "razorpay")
        self.assertEqual(payment_doc["srid"], "SR9999")

        # Verify student access was unlocked
        ua = self.db.user_access.find_one({"user_id": str(self.student.id), "item_id": str(self.course.id)})
        self.assertIsNotNone(ua)
        self.assertTrue(ua.get("is_active"))

        # Verify Ambassador sales record was created
        sale = self.db.ambassador_sales.find_one({"srid": "SR9999"})
        self.assertIsNotNone(sale)
        self.assertEqual(sale["status"], "approved")
        self.assertEqual(sale["amount"], 499.0)

    def test_verify_payment_replay_protection(self):
        """Duplicate verify-payment submissions return success without duplicating payments."""
        self._login()
        order_id = "order_test_replay"
        payment_id = "pay_test_replay_001"

        msg = f"{order_id}|{payment_id}".encode("utf-8")
        valid_signature = hmac.new(
            self.test_key_secret.encode("utf-8"),
            msg,
            hashlib.sha256
        ).hexdigest()

        payload = {
            "razorpay_order_id": order_id,
            "razorpay_payment_id": payment_id,
            "razorpay_signature": valid_signature,
            "item_type": "course",
            "item_id": str(self.course.id),
        }

        # First verification
        res1 = self.client.post("/api/verify-payment", json=payload)
        self.assertEqual(res1.status_code, 200)

        # Second verification (replay)
        res2 = self.client.post("/api/verify-payment", json=payload)
        self.assertEqual(res2.status_code, 200)
        data2 = res2.get_json()
        self.assertTrue(data2.get("success"))

        # Confirm only 1 payment was inserted
        count = self.db.payments.count_documents({"razorpay_payment_id": payment_id})
        self.assertEqual(count, 1)


if __name__ == "__main__":
    unittest.main()
