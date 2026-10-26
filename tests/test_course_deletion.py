import sys
import os
import unittest
from datetime import datetime, timezone
from bson import ObjectId

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.stdout.reconfigure(encoding="utf-8")

from app import create_app
from models.mongo import (
    Course,
    Assignment,
    Submission,
    Enrollment,
    Review,
    Certificate,
    User,
    get_db,
    ensure_default_courses
)


class TestCourseDeletion(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.app.config["TESTING"] = True
        cls.app.config["WTF_CSRF_ENABLED"] = False
        cls.client = cls.app.test_client()

    def setUp(self):
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.db = get_db()

    def tearDown(self):
        self.app_context.pop()

    def test_model_cascade_deletion(self):
        """Verify Course.delete() permanently removes the course and all cascading records."""
        # Create a course
        course = Course({
            "title": "Temporary Test Deletion Course",
            "slug": f"temp-test-deletion-{ObjectId()}",
            "is_published": True
        })
        course.save()
        cid = str(course.id)

        # Create student user
        student = User({
            "email": f"student_{ObjectId()}@skillrock.test",
            "name": "Deletion Test Student",
            "role": "student"
        })
        student.save()

        # Create assignment
        asg = Assignment({
            "course_id": cid,
            "title": "Milestone 1 Test",
            "step_number": 1,
            "total_steps": 1,
            "evaluation_type": "project_based"
        })
        asg.save()
        asg_id = str(asg.id)

        # Create enrollment
        enrollment = Enrollment({
            "user_id": str(student.id),
            "course_id": cid,
            "status": "enrolled"
        })
        enrollment.save()

        # Create submission
        sub = Submission({
            "user_id": str(student.id),
            "course_id": cid,
            "assignment_id": asg_id,
            "status": Submission.STATUS_PENDING,
            "submission_type": "project"
        })
        sub.save()
        sub_id = str(sub.id)

        # Create review
        rev = Review({
            "submission_id": sub_id,
            "reviewer_id": "test_reviewer",
            "verdict": "approved"
        })
        rev.save()

        # Create certificate
        cert = Certificate({
            "user_id": str(student.id),
            "course_id": cid,
            "certificate_id": f"CERT-{ObjectId()}"
        })
        cert.save()

        # Verify all records exist prior to deletion
        self.assertIsNotNone(Course.get_by_id(cid))
        self.assertGreater(self.db.assignments.count_documents({"course_id": cid}), 0)
        self.assertGreater(self.db.enrollments.count_documents({"course_id": cid}), 0)
        self.assertGreater(self.db.submissions.count_documents({"course_id": cid}), 0)
        self.assertGreater(self.db.reviews.count_documents({"submission_id": sub_id}), 0)
        self.assertGreater(self.db.certificates.count_documents({"course_id": cid}), 0)

        # Execute permanent deletion
        slug = course.slug
        course.delete()

        # Verify course is completely deleted
        self.assertIsNone(Course.get_by_id(cid))
        self.assertIsNone(Course.get_by_slug(slug))
        self.assertEqual(self.db.courses.count_documents({"_id": ObjectId(cid)}), 0)

        # Verify all cascading records are completely deleted
        self.assertEqual(self.db.assignments.count_documents({"course_id": cid}), 0)
        self.assertEqual(self.db.enrollments.count_documents({"course_id": cid}), 0)
        self.assertEqual(self.db.submissions.count_documents({"course_id": cid}), 0)
        self.assertEqual(self.db.reviews.count_documents({"submission_id": sub_id}), 0)
        self.assertEqual(self.db.certificates.count_documents({"course_id": cid}), 0)

        # Verify slug is recorded in deleted_courses
        self.assertIsNotNone(self.db.deleted_courses.find_one({"slug": slug}))

    def test_deleted_course_not_resurrected_by_ensure_default_courses(self):
        """Verify that ensure_default_courses() will NOT re-seed an admin-deleted course."""
        from models.default_curriculum import get_default_curriculum
        curriculum = get_default_curriculum()
        if not curriculum:
            self.skipTest("No default curriculum defined")

        target_course_data = dict(curriculum[0])
        target_slug = target_course_data.get("slug")

        try:
            # 1. Ensure initial state has target course seeded
            self.db.deleted_courses.delete_many({"slug": target_slug})
            self.db.platform_settings.delete_one({"key": "default_courses_seeded"})
            ensure_default_courses()

            existing = Course.get_by_slug(target_slug)
            self.assertIsNotNone(existing, f"Course with slug '{target_slug}' should exist after seeding")

            # 2. Admin permanently deletes the course
            existing.delete()
            self.assertIsNone(Course.get_by_slug(target_slug))
            self.assertIsNotNone(self.db.deleted_courses.find_one({"slug": target_slug}))

            # 3. Simulate server restart / Render wake-up by re-running ensure_default_courses()
            ensure_default_courses()

            # 4. Verify the course was NOT resurrected
            re_checked = Course.get_by_slug(target_slug)
            self.assertIsNone(re_checked, f"Course '{target_slug}' should remain permanently deleted and NOT be resurrected")
        finally:
            # Restore the default course so platform curriculum remains intact for other tests
            self.db.deleted_courses.delete_many({"slug": target_slug})
            self.db.platform_settings.delete_one({"key": "default_courses_seeded"})
            ensure_default_courses()

    def test_admin_route_course_delete_post_and_get(self):
        """Verify admin route permanently deletes a course via POST and GET."""
        # Setup admin user
        admin_email = f"admin_{ObjectId()}@skillrock.test"
        admin = User({
            "email": admin_email,
            "name": "Admin Tester",
            "role": "admin",
            "is_admin": True
        })
        admin.set_password("AdminPass123!")
        admin.save()

        # Create course to delete via POST
        course_post = Course({
            "title": "Post Delete Test",
            "slug": f"post-delete-{ObjectId()}",
            "is_published": True
        })
        course_post.save()
        c_post_id = str(course_post.id)

        # Create course to delete via GET
        course_get = Course({
            "title": "Get Delete Test",
            "slug": f"get-delete-{ObjectId()}",
            "is_published": True
        })
        course_get.save()
        c_get_id = str(course_get.id)

        # Login as admin
        with self.client.session_transaction() as sess:
            sess["_user_id"] = str(admin.id)

        # Delete course_post via POST
        resp = self.client.post(f"/admin/courses/{c_post_id}/delete", follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIsNone(Course.get_by_id(c_post_id))

        # Delete course_get via GET
        resp_get = self.client.get(f"/admin/courses/{c_get_id}/delete", follow_redirects=True)
        self.assertEqual(resp_get.status_code, 200)
        self.assertIsNone(Course.get_by_id(c_get_id))

    def test_unauthorized_user_cannot_delete_course(self):
        """Verify non-admin users cannot delete courses."""
        student = User({
            "email": f"student_noadmin_{ObjectId()}@skillrock.test",
            "name": "Regular Student",
            "role": "student",
            "is_admin": False
        })
        student.save()

        course = Course({
            "title": "Protected Course",
            "slug": f"protected-{ObjectId()}",
            "is_published": True
        })
        course.save()
        cid = str(course.id)

        with self.client.session_transaction() as sess:
            sess["_user_id"] = str(student.id)

        # Attempt to delete
        resp = self.client.post(f"/admin/courses/{cid}/delete", follow_redirects=True)
        # Should be redirected away or access denied
        self.assertIsNotNone(Course.get_by_id(cid), "Course must not be deleted by regular student")


if __name__ == "__main__":
    unittest.main()
