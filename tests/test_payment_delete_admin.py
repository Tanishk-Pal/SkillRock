import os
import unittest
from datetime import datetime, timezone

os.environ["MONGODB_URI"] = ""
os.environ["TESTING"] = "1"

import models.mongo as mongo_mod
mongo_mod._db = None
mongo_mod._mongo_client = None

from app import create_app
from models import get_db, User, Course
from services.payment_service import grant_student_access, verify_student_unlock


class TestPaymentDeleteAdmin(unittest.TestCase):
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
        self.db.users.delete_many({"email": {"$regex": r"@skillrock\.test$"}})
        self.db.payments.delete_many({"user_email": {"$regex": r"@skillrock\.test$"}})
        self.db.ambassador_sales.delete_many({"student_email": {"$regex": r"@skillrock\.test$"}})

        # Create student
        self.student = User({
            "name": "Delete Test Student",
            "email": "student.delete@skillrock.test",
            "role": "student",
            "is_banned": False,
        })
        self.student.set_password("StudentPass123!")
        self.student.save()

        # Create admin
        self.admin = User({
            "name": "Admin Tester",
            "email": "admin.delete@skillrock.test",
            "role": "admin",
            "is_banned": False,
        })
        self.admin.set_password("AdminPass123!")
        self.admin.save()

        # Create test paid course
        self.course = Course({
            "title": "Test Delete Course",
            "slug": "test-delete-course",
            "youtube_url": "https://www.youtube.com/watch?v=kqtD5dpn9C8",
            "instructor": "Test Instructor",
            "is_published": True,
            "is_paid": True,
            "price": 199.0,
        })
        self.course.save()

        # Create test payment
        self.payment_id = "PAY-TEST-DELETE-001"
        self.db.payments.insert_one({
            "payment_id": self.payment_id,
            "user_id": str(self.student.id),
            "user_name": self.student.name,
            "user_email": self.student.email,
            "item_type": "course",
            "item_id": str(self.course.id),
            "item_title": self.course.title,
            "amount": 199.0,
            "utr_number": "999888777666",
            "srid": "SR1001",
            "status": "approved",
            "submitted_at": datetime.now(timezone.utc),
        })

        # Insert linked ambassador sale
        self.db.ambassador_sales.insert_one({
            "payment_id": self.payment_id,
            "srid": "SR1001",
            "student_email": self.student.email,
            "amount": 199.0,
            "status": "approved",
        })

        # Grant access
        grant_student_access(
            user_id=str(self.student.id),
            item_type="course",
            item_id=str(self.course.id),
            payment_id=self.payment_id,
            amount=199.0,
        )

    def tearDown(self):
        self.db.users.delete_many({"email": {"$regex": r"@skillrock\.test$"}})
        self.db.courses.delete_many({"slug": "test-delete-course"})
        self.db.payments.delete_many({"user_email": {"$regex": r"@skillrock\.test$"}})
        self.db.ambassador_sales.delete_many({"student_email": {"$regex": r"@skillrock\.test$"}})
        if hasattr(self, "course"):
            self.db.user_access.delete_many({"item_id": str(self.course.id)})

    def _login(self, email, password):
        self.client.get("/logout", follow_redirects=True)
        return self.client.post("/login", data={
            "email": email,
            "password": password
        }, follow_redirects=True)

    def test_admin_can_permanently_delete_payment_and_purge_sale(self):
        """Admin can delete a payment record; access is revoked and sales purged."""
        self._login(self.admin.email, "AdminPass123!")

        # Verify payment & sale exist
        self.assertIsNotNone(self.db.payments.find_one({"payment_id": self.payment_id}))
        self.assertIsNotNone(self.db.ambassador_sales.find_one({"payment_id": self.payment_id}))
        self.assertTrue(verify_student_unlock(self.student, "course", str(self.course.id)))

        # Execute delete
        res = self.client.post(f"/admin/payments/{self.payment_id}/delete", follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        # Verify payment is deleted
        self.assertIsNone(self.db.payments.find_one({"payment_id": self.payment_id}))
        # Verify ambassador sale is purged
        self.assertIsNone(self.db.ambassador_sales.find_one({"payment_id": self.payment_id}))
        # Verify access is revoked
        self.assertFalse(verify_student_unlock(self.student, "course", str(self.course.id)))

    def test_non_admin_cannot_delete_payment(self):
        """Students cannot delete payment records."""
        self._login(self.student.email, "StudentPass123!")
        res = self.client.post(f"/admin/payments/{self.payment_id}/delete", follow_redirects=True)
        # Should be redirected away or forbidden
        self.assertIn(res.status_code, [302, 403, 200])
        # Payment must STILL exist
        self.assertIsNotNone(self.db.payments.find_one({"payment_id": self.payment_id}))

    def test_admin_purge_test_records_endpoint(self):
        """Admin can sweep and purge test records with 1 click."""
        self._login(self.admin.email, "AdminPass123!")
        res = self.client.post("/admin/payments/purge-test-records", follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIsNone(self.db.payments.find_one({"payment_id": self.payment_id}))
