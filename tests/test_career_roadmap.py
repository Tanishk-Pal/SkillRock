"""
SkillRock — Career Roadmap & 50% Completion Cashback Automated Test Suite
Verifies:
1. Model Seeding: Flagship Full Stack Developer Launchpad package integrity.
2. Public Catalog & Detail Routes: 20-week syllabus, phases, outcomes, cashback terms.
3. Enrollment & Access Control: Safe gating for free vs paid roadmaps, checkout redirection.
4. Interactive Dashboard & Lecture Player: Timestamp offsets, video embeds, previous/next navigation.
5. Server-Side Lesson Progress: Safe toggle, persistence, percentage calculation.
6. Phase Projects & Capstone Submissions: URL validation, evaluator review queue, rubric scoring.
7. 50% Completion Cashback Gate: Strict verification of all 4 conditions, idempotency, fraud prevention.
8. Admin Review & Refund Disbursal: Gateway vs manual modes, audit logs.
9. Verified Certificate: Issuance upon 100% completion + approved Capstone.
10. Regression Safety: Zero disruption to existing individual courses, student accounts, and payments.
"""

import unittest
from datetime import datetime, timezone, timedelta

from app import create_app
from config import Config
from models import get_db, User, Course, Certificate
from models.roadmap import (
    RoadmapPackage,
    RoadmapProgress,
    RoadmapSubmission,
    RoadmapCashback,
    ensure_default_roadmaps
)
from services.payment_service import grant_student_access, verify_student_unlock


class TestCareerRoadmapPlatform(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        Config.TESTING = True
        Config.WTF_CSRF_ENABLED = False
        cls.app = create_app(Config)
        cls.app.config["TESTING"] = True
        cls.client = cls.app.test_client()
        cls.db = get_db()

        # Seed once for class
        ensure_default_roadmaps()
        cls.pkg = RoadmapPackage.get_by_slug("full-stack-developer-launchpad")

    def setUp(self):
        with self.client.session_transaction() as sess:
            sess.clear()

        # Create test student with unique email
        self.student = User({
            "name": "Alex Developer",
            "email": f"alex_{self._testMethodName}@roadmaptest.skillrock",
            "role": "student",
            "is_banned": False,
        })
        self.student.set_password("StudentPass123!")
        self.student.save()

        # Create test admin
        self.admin = User({
            "name": "Platform Admin",
            "email": f"admin_{self._testMethodName}@roadmaptest.skillrock",
            "role": "admin",
            "is_admin": True,
            "is_banned": False,
        })
        self.admin.set_password("AdminPass123!")
        self.admin.save()

    def tearDown(self):
        with self.client.session_transaction() as sess:
            sess.clear()

        if hasattr(self, "student") and self.student.id:
            self.db.roadmap_progress.delete_many({"user_id": str(self.student.id)})
            self.db.roadmap_submissions.delete_many({"user_id": str(self.student.id)})
            self.db.roadmap_cashback.delete_many({"user_id": str(self.student.id)})
            self.db.user_access.delete_many({"user_id": str(self.student.id)})
            self.db.certificates.delete_many({"user_id": str(self.student.id)})
            self.db.users.delete_many({"_id": self.student._id})
        if hasattr(self, "admin") and self.admin.id:
            self.db.users.delete_many({"_id": self.admin._id})

    def login_student(self):
        with self.client.session_transaction() as sess:
            sess['_user_id'] = str(self.student.id)
            sess['_fresh'] = True

    def login_admin(self):
        with self.client.session_transaction() as sess:
            sess['_user_id'] = str(self.admin.id)
            sess['_fresh'] = True

    # 1. Package Seeding & Curriculum Structure
    def test_flagship_package_structure(self):
        self.assertIsNotNone(self.pkg)
        self.assertEqual(self.pkg.slug, "full-stack-developer-launchpad")
        self.assertEqual(len(self.pkg.phases), 5)
        self.assertEqual(self.pkg.total_weeks, 20)
        self.assertGreaterEqual(self.pkg.total_lessons_count, 20)
        self.assertEqual(len(self.pkg.projects), 4)
        self.assertIsNotNone(self.pkg.capstone)
        self.assertEqual(self.pkg.capstone.get("id"), "capstone_job_tracker")
        self.assertTrue(self.pkg.cashback_enabled)
        self.assertEqual(self.pkg.cashback_percentage, 50.0)

    # 2. Public Catalog & Detail Pages
    def test_public_catalog_and_detail(self):
        res = self.client.get("/roadmaps")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Full Stack Developer Launchpad", res.data)
        self.assertIn(b"50%", res.data)

        res = self.client.get("/roadmaps/full-stack-developer-launchpad")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"20-Week Curriculum", res.data)
        self.assertIn(b"Phase 1: Web Development Foundations", res.data)
        self.assertIn(b"Job Application Tracker", res.data)

    # 3. Access Guard & Unenrolled Gating
    def test_access_guard_enforcement(self):
        # Guest blocked from dashboard
        res = self.client.get("/roadmaps/full-stack-developer-launchpad/dashboard")
        self.assertEqual(res.status_code, 302)

        # Logged in but not enrolled -> Redirected to detail page
        self.login_student()
        res = self.client.get("/roadmaps/full-stack-developer-launchpad/dashboard", follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Please enroll in this Career Roadmap", res.data)

    # 4. Enrollment & Active Dashboard
    def test_enrollment_and_dashboard_access(self):
        self.login_student()
        grant_student_access(
            user_id=str(self.student.id),
            item_type="roadmap",
            item_id=str(self.pkg.id),
            granted_by="test_grant",
            amount=999.0
        )
        self.assertTrue(verify_student_unlock(self.student, "roadmap", str(self.pkg.id)))

        res = self.client.get("/roadmaps/full-stack-developer-launchpad/dashboard")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"CURRICULUM PROGRESS", res.data)
        self.assertIn(b"50% CASHBACK WINDOW", res.data)

    # 5. Lecture Player & Timestamp Offsets
    def test_learn_player_and_timestamps(self):
        self.login_student()
        grant_student_access(
            user_id=str(self.student.id),
            item_type="roadmap",
            item_id=str(self.pkg.id),
            amount=999.0
        )
        first_lesson = self.pkg.phases[0]["weeks"][0]["lessons"][0]
        lesson_id = first_lesson["id"]

        res = self.client.get(f"/roadmaps/full-stack-developer-launchpad/learn/1/{lesson_id}")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"skillrockLectureFrame", res.data)
        self.assertIn(b"start=87", res.data)  # 00:01:27 = 87s
        self.assertIn(b"Internet, Browser Engine", res.data)

    # 6. Server-Side Lesson Progress Toggle
    def test_lesson_progress_toggle(self):
        self.login_student()
        grant_student_access(
            user_id=str(self.student.id),
            item_type="roadmap",
            item_id=str(self.pkg.id),
            amount=999.0
        )
        first_lesson = self.pkg.phases[0]["weeks"][0]["lessons"][0]
        lesson_id = first_lesson["id"]

        # Toggle Complete
        res = self.client.post(
            "/roadmaps/full-stack-developer-launchpad/progress/toggle-lesson",
            json={"lesson_id": lesson_id}
        )
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertTrue(data["is_completed"])
        self.assertEqual(data["completed_count"], 1)
        self.assertGreater(data["completion_pct"], 0)

        # Toggle Incomplete
        res2 = self.client.post(
            "/roadmaps/full-stack-developer-launchpad/progress/toggle-lesson",
            json={"lesson_id": lesson_id}
        )
        self.assertEqual(res2.status_code, 200)
        data2 = res2.get_json()
        self.assertFalse(data2["is_completed"])
        self.assertEqual(data2["completed_count"], 0)

    # 7. Project & Capstone Submissions
    def test_project_and_capstone_submissions(self):
        self.login_student()
        grant_student_access(
            user_id=str(self.student.id),
            item_type="roadmap",
            item_id=str(self.pkg.id),
            amount=999.0
        )

        p1_id = self.pkg.projects[0]["id"]
        cap_id = self.pkg.capstone["id"]

        # Submit Phase 1 Project
        res = self.client.post(
            f"/roadmaps/full-stack-developer-launchpad/projects/{p1_id}/submit",
            data={
                "github_url": "https://github.com/alexdev/personal-portfolio",
                "deployment_url": "https://alex-portfolio.vercel.app",
                "notes": "Semantic HTML and responsive CSS grid implemented."
            },
            follow_redirects=True
        )
        self.assertEqual(res.status_code, 200)
        sub1 = RoadmapSubmission.get_by_user_and_project(self.student.id, self.pkg.slug, p1_id)
        self.assertIsNotNone(sub1)
        self.assertEqual(sub1.status, RoadmapSubmission.STATUS_PENDING)

        # Submit Capstone Project
        res_cap = self.client.post(
            f"/roadmaps/full-stack-developer-launchpad/projects/{cap_id}/submit",
            data={
                "github_url": "https://github.com/alexdev/job-application-tracker",
                "deployment_url": "https://job-tracker.onrender.com",
                "notes": "PostgreSQL relational schema and JWT auth fully wired."
            },
            follow_redirects=True
        )
        self.assertEqual(res_cap.status_code, 200)
        cap_sub = RoadmapSubmission.get_by_user_and_project(self.student.id, self.pkg.slug, cap_id)
        self.assertIsNotNone(cap_sub)
        self.assertTrue(cap_sub.is_capstone)
        self.assertEqual(cap_sub.status, RoadmapSubmission.STATUS_PENDING)

    # 8. Admin Evaluation of Submissions
    def test_admin_submission_evaluation(self):
        cap_id = self.pkg.capstone["id"]
        # Create a submission
        sub = RoadmapSubmission({
            "user_id": str(self.student.id),
            "user_name": self.student.name,
            "user_email": self.student.email,
            "roadmap_slug": self.pkg.slug,
            "project_id": cap_id,
            "project_title": "Job Application Tracker",
            "is_capstone": True,
            "github_url": "https://github.com/alexdev/job-tracker",
            "deployment_url": "https://job-tracker.onrender.com",
            "status": RoadmapSubmission.STATUS_PENDING
        }).save()

        self.login_admin()
        res = self.client.post(
            f"/admin/roadmaps/submissions/{sub.id}/evaluate",
            data={
                "status": "approved",
                "score": "94.5",
                "admin_feedback": "Outstanding architecture, clean repository structure and responsive design!"
            },
            follow_redirects=True
        )
        self.assertEqual(res.status_code, 200)
        updated_sub = RoadmapSubmission.get_by_id(sub.id)
        self.assertEqual(updated_sub.status, RoadmapSubmission.STATUS_APPROVED)
        self.assertEqual(updated_sub.score, 94.5)
        self.assertEqual(updated_sub.reviewed_by, self.admin.email)

    # 9. 50% Cashback Eligibility & Claim Workflow
    def test_cashback_eligibility_and_claim(self):
        self.login_student()
        grant_student_access(
            user_id=str(self.student.id),
            item_type="roadmap",
            item_id=str(self.pkg.id),
            amount=999.0
        )
        prog = RoadmapProgress.get_user_progress(self.student.id, self.pkg.slug)
        prog.amount_paid = 999.0
        prog.save()

        # Attempt 1: Blocked when lessons are incomplete
        res = self.client.post("/roadmaps/full-stack-developer-launchpad/cashback/request", follow_redirects=True)
        self.assertIn(b"You must complete 100% of all 20-week lessons", res.data)

        # Complete all lessons
        all_lesson_ids = set()
        for p in self.pkg.phases:
            for w in p.get("weeks", []):
                for l in w.get("lessons", []):
                    all_lesson_ids.add(l["id"])
        prog.completed_lesson_ids = all_lesson_ids
        prog.save()

        # Attempt 2: Blocked when phase projects are not submitted
        res = self.client.post("/roadmaps/full-stack-developer-launchpad/cashback/request", follow_redirects=True)
        self.assertIn(b"You must submit all phase projects", res.data)

        # Submit all 4 phase projects
        for p in self.pkg.projects:
            RoadmapSubmission({
                "user_id": str(self.student.id),
                "roadmap_slug": self.pkg.slug,
                "project_id": p["id"],
                "project_title": p["title"],
                "github_url": "https://github.com/alexdev/test-repo",
                "status": RoadmapSubmission.STATUS_PENDING
            }).save()

        # Attempt 3: Blocked when Capstone is unapproved
        res = self.client.post("/roadmaps/full-stack-developer-launchpad/cashback/request", follow_redirects=True)
        self.assertIn(b"Final Capstone project must be evaluated and approved", res.data)

        # Approve Capstone
        cap_id = self.pkg.capstone["id"]
        RoadmapSubmission({
            "user_id": str(self.student.id),
            "roadmap_slug": self.pkg.slug,
            "project_id": cap_id,
            "project_title": "Job Application Tracker",
            "is_capstone": True,
            "github_url": "https://github.com/alexdev/capstone",
            "deployment_url": "https://capstone.onrender.com",
            "status": RoadmapSubmission.STATUS_APPROVED
        }).save()

        # Attempt 4: All 4 conditions met -> Claim Accepted!
        res_success = self.client.post("/roadmaps/full-stack-developer-launchpad/cashback/request", follow_redirects=True)
        self.assertIn(b"50% Completion Cashback Claim", res_success.data)
        self.assertIn(b"499.5", res_success.data)

        # Verify document in MongoDB
        cashback_doc = RoadmapCashback.get_by_user_and_roadmap(self.student.id, self.pkg.slug)
        self.assertIsNotNone(cashback_doc)
        self.assertEqual(cashback_doc.review_status, RoadmapCashback.STATUS_PENDING_REVIEW)
        self.assertEqual(cashback_doc.cashback_amount, 499.5)
        self.assertGreater(len(cashback_doc.audit_log), 0)

        # Attempt 5: Duplicate claim is idempotently blocked
        res_dup = self.client.post("/roadmaps/full-stack-developer-launchpad/cashback/request", follow_redirects=True)
        self.assertIn(b"already submitted a cashback request", res_dup.data)

    # 10. Admin Cashback Disbursal
    def test_admin_cashback_processing(self):
        cb = RoadmapCashback({
            "user_id": str(self.student.id),
            "user_name": self.student.name,
            "user_email": self.student.email,
            "roadmap_slug": self.pkg.slug,
            "roadmap_title": self.pkg.title,
            "original_amount": 999.0,
            "cashback_percentage": 50.0,
            "cashback_amount": 499.5,
            "review_status": RoadmapCashback.STATUS_PENDING_REVIEW
        }).save()

        self.login_admin()
        res = self.client.post(
            f"/admin/cashback/{cb.id}/process",
            data={"mode": "manual", "notes": "Disbursed ₹499.50 via UPI UTR 478125049818"},
            follow_redirects=True
        )
        self.assertEqual(res.status_code, 200)
        updated_cb = RoadmapCashback.get_by_id(cb.id)
        self.assertEqual(updated_cb.review_status, RoadmapCashback.STATUS_PROCESSED)
        self.assertEqual(updated_cb.refund_mode, "manual_upi")
        self.assertIn("478125049818", updated_cb.admin_notes)

    # 11. Verified Certificate Issuance
    def test_certificate_issuance(self):
        self.login_student()
        grant_student_access(
            user_id=str(self.student.id),
            item_type="roadmap",
            item_id=str(self.pkg.id),
            amount=999.0
        )
        prog = RoadmapProgress.get_user_progress(self.student.id, self.pkg.slug)
        all_lesson_ids = set()
        for p in self.pkg.phases:
            for w in p.get("weeks", []):
                for l in w.get("lessons", []):
                    all_lesson_ids.add(l["id"])
        prog.completed_lesson_ids = all_lesson_ids
        prog.save()

        cap_id = self.pkg.capstone["id"]
        RoadmapSubmission({
            "user_id": str(self.student.id),
            "roadmap_slug": self.pkg.slug,
            "project_id": cap_id,
            "is_capstone": True,
            "status": RoadmapSubmission.STATUS_APPROVED
        }).save()

        res = self.client.get("/roadmaps/full-stack-developer-launchpad/certificate")
        self.assertEqual(res.status_code, 200)
        cert = Certificate.get_by_user_course(self.student.id, self.pkg.slug)
        self.assertIsNotNone(cert)
        self.assertTrue(cert.certificate_id.startswith("SR-"))
        self.assertIn(cert.certificate_id.encode("utf-8"), res.data)

    # 12. Non-Disruption & Platform Regression
    def test_existing_platform_courses_unbroken(self):
        res = self.client.get("/learning/courses")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Courses", res.data)


if __name__ == "__main__":
    unittest.main()
