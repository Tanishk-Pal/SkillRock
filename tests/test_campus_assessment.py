# -*- coding: utf-8 -*-
import os
os.environ["MONGODB_URI"] = ""

"""
SkillRock — Automated Unit Test Suite for Campus Assessment Platform
Tests Teacher Role Management, RBAC Security Gates, 4-Year Academic Curriculum,
Multi-Step Test Creation, Configurable Anti-Cheat Proctoring, Autosave,
and Evaluation Engine.
"""

import unittest
from datetime import datetime, timezone, timedelta
from app import create_app
from config import Config
from models.mongo import get_db, User
from models.academic_assessment import (
    AcademicSubject, AcademicQuestion, CollegeAssessment, CollegeAssessmentAttempt, seed_default_academic_curriculum
)

class TestCampusAssessmentConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    LOGIN_DISABLED = False

class TestCampusAssessmentSystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        TestCampusAssessmentConfig.TESTING = True
        TestCampusAssessmentConfig.WTF_CSRF_ENABLED = False
        cls.app = create_app(TestCampusAssessmentConfig)
        cls.app.config["TESTING"] = True
        cls.client = cls.app.test_client()
        cls.db = get_db()

    def setUp(self):
        # 1. Clean test data
        self.db.users.delete_many({"email": {"$regex": r"@campus\.test$"}})
        self.db.academic_subjects.delete_many({"department": "Test Department"})
        self.db.college_assessments.delete_many({"class_section": "Test Section"})
        self.db.college_assessment_attempts.delete_many({"user_email": {"$regex": r"@campus\.test$"}})

        # 2. Create Student User
        self.student = User({
            "name": "Rohan Student",
            "email": "rohan.student@campus.test",
            "role": "student",
            "is_teacher": False,
            "college": "IIT Delhi",
            "branch": "CSE",
            "year": "2"
        })
        self.student.set_password("StudentPass123!")
        self.student.save()

        # 3. Create Teacher User
        self.teacher = User({
            "name": "Prof. Alok Sharma",
            "email": "prof.sharma@campus.test",
            "role": "teacher",
            "is_teacher": True,
            "teacher_title": "Associate Professor",
            "college": "IIT Delhi",
            "branch": "CSE"
        })
        self.teacher.set_password("TeacherPass123!")
        self.teacher.save()

        # 4. Create Admin User
        self.admin = User({
            "name": "Super Admin",
            "email": "admin@campus.test",
            "role": "admin",
            "is_admin": True,
            "is_teacher": True
        })
        self.admin.set_password("AdminPass123!")
        self.admin.save()

        # 5. Create Test Subject
        self.subject = AcademicSubject({
            "name": "Data Structures & Algorithms Test",
            "code": "CS201-TEST",
            "year": "2",
            "semester": 3,
            "department": "Test Department",
            "teacher_ids": [str(self.teacher.id)],
            "teacher_name": self.teacher.name,
            "is_active": True
        }).save()

        # 6. Create Questions in Question Bank
        self.q1_mcq = AcademicQuestion({
            "subject_id": str(self.subject.id),
            "subject_name": self.subject.name,
            "teacher_id": str(self.teacher.id),
            "question_text": "What is the worst-case lookup time for a hash table with chaining?",
            "question_type": AcademicQuestion.TYPE_MCQ,
            "marks": 2.0,
            "options": [
                {"id": "opt_1", "text": "O(1)"},
                {"id": "opt_2", "text": "O(n)"},
                {"id": "opt_3", "text": "O(log n)"}
            ],
            "correct_answers": ["opt_2"],
            "explanation": "If all keys hash to the same bucket, the lookup degrades to linear O(n)."
        }).save()

        self.q2_coding = AcademicQuestion({
            "subject_id": str(self.subject.id),
            "subject_name": self.subject.name,
            "teacher_id": str(self.teacher.id),
            "question_text": "Write Python code that prints the square of input integer.",
            "question_type": AcademicQuestion.TYPE_CODING,
            "marks": 5.0,
            "coding_hidden_test_cases": [
                {"input": "4", "output": "16"},
                {"input": "5", "output": "25"}
            ]
        }).save()

        # 7. Create Test Assessment
        now = datetime.now(timezone.utc)
        self.assessment = CollegeAssessment({
            "title": "Unit Test 1: Advanced Data Structures",
            "slug": "unit-test-1-dsa-test",
            "subject_id": str(self.subject.id),
            "subject_name": self.subject.name,
            "subject_code": self.subject.code,
            "academic_year": "2",
            "semester": 3,
            "department": "Test Department",
            "class_section": "Test Section",
            "assessment_type": "Unit Test",
            "teacher_id": str(self.teacher.id),
            "teacher_name": self.teacher.name,
            "duration_minutes": 30,
            "total_marks": 7.0,
            "passing_marks": 3.0,
            "start_datetime": now - timedelta(hours=1),
            "end_datetime": now + timedelta(days=2),
            "status": CollegeAssessment.STATUS_PUBLISHED,
            "result_published": True,
            "question_ids": [self.q1_mcq.id, self.q2_coding.id],
            "integrity_settings": {
                "preset": "standard",
                "tab_switch_monitoring": True,
                "copy_paste_monitoring": True,
                "max_warnings": 3
            }
        }).save()

    def tearDown(self):
        self._logout()
        self.db.users.delete_many({"email": {"$regex": r"@campus\.test$"}})
        self.db.academic_subjects.delete_many({"department": "Test Department"})
        self.db.college_assessments.delete_many({"class_section": "Test Section"})
        self.db.college_assessment_attempts.delete_many({"user_email": {"$regex": r"@campus\.test$"}})

    def _login_as(self, user):
        """Helper to establish deterministic authenticated session."""
        with self.client.session_transaction() as sess:
            sess["_user_id"] = str(user.id)
            sess["_fresh"] = True

    def _logout(self):
        """Helper to clear session."""
        with self.client.session_transaction() as sess:
            sess.clear()

    # --------------------------------------------------------------------------
    # 1. RBAC & Security Gates
    # --------------------------------------------------------------------------
    def test_teacher_role_security_gates(self):
        # Student cannot access /teacher/assessments -> MUST receive 403 Forbidden
        self._login_as(self.student)
        res_student = self.client.get("/teacher/assessments")
        self.assertEqual(res_student.status_code, 403)

        # Teacher CAN access /teacher/assessments -> 200 OK
        self._login_as(self.teacher)
        res_teacher = self.client.get("/teacher/assessments")
        self.assertEqual(res_teacher.status_code, 200)
        self.assertIn(b"Teacher Workspace", res_teacher.data)

        # Admin CAN access /teacher/assessments -> 200 OK
        self._login_as(self.admin)
        res_admin = self.client.get("/teacher/assessments")
        self.assertEqual(res_admin.status_code, 200)

    # --------------------------------------------------------------------------
    # 2. Admin Role Management (Assign & Revoke Teacher)
    # --------------------------------------------------------------------------
    def test_admin_teacher_promotion_and_demotion(self):
        self._login_as(self.admin)

        # Promote student to Teacher
        res_promote = self.client.post(f"/admin/users/{self.student.id}/toggle_teacher", follow_redirects=True)
        self.assertEqual(res_promote.status_code, 200)

        updated_student = User.get_by_id(self.student.id)
        self.assertTrue(updated_student.is_teacher)
        self.assertEqual(updated_student.role, "teacher")

        # Demote back to student
        res_demote = self.client.post(f"/admin/teachers/remove/{self.student.id}", follow_redirects=True)
        self.assertEqual(res_demote.status_code, 200)

        demoted_student = User.get_by_id(self.student.id)
        self.assertFalse(demoted_student.is_teacher)
        self.assertEqual(demoted_student.role, "student")

    # --------------------------------------------------------------------------
    # 3. Student Test Series Landing Page (4 Years + Curriculum)
    # --------------------------------------------------------------------------
    def test_student_test_series_academic_curriculum(self):
        # Open /test-series as student
        self._login_as(self.student)
        res = self.client.get("/test-series?year=2")
        self.assertEqual(res.status_code, 200)

        # Check 4 Year Cards are present
        self.assertIn(b"First Year", res.data)
        self.assertIn(b"Second Year", res.data)
        self.assertIn(b"Third Year", res.data)
        self.assertIn(b"Fourth Year", res.data)

        # Check academic subject is loaded
        self.assertIn(b"CS201-TEST", res.data)
        self.assertIn(b"Unit Test 1: Advanced Data Structures", res.data)

        # Check existing Placement Test Series below is preserved
        self.assertIn(b"Campus Placement Preparation", res.data)

    # --------------------------------------------------------------------------
    # 4. Exam Runtime: Autosave, Anti-Cheat & Automatic Evaluation
    # --------------------------------------------------------------------------
    def test_exam_runtime_autosave_and_evaluation(self):
        self._login_as(self.student)

        # 1. Take Assessment
        res_start = self.client.get(f"/teacher/exam/{self.assessment.slug}")
        self.assertEqual(res_start.status_code, 200)
        self.assertIn(b"SkillRock Academic Portal", res_start.data)

        # Retrieve newly created attempt
        attempt = CollegeAssessmentAttempt.get_active_attempt(self.student.id, self.assessment.id)
        self.assertIsNotNone(attempt)
        self.assertEqual(attempt.status, CollegeAssessmentAttempt.STATUS_IN_PROGRESS)
        self.assertGreater(attempt.remaining_seconds, 0)

        # 2. Autosave Answer for MCQ (q1)
        res_save = self.client.post(f"/teacher/exam/{attempt.id}/save-answer", json={
            "question_id": self.q1_mcq.id,
            "answer": "opt_2",
            "marked_for_review": False
        })
        self.assertEqual(res_save.status_code, 200)
        data = res_save.get_json()
        self.assertTrue(data["success"])

        # 3. Anti-Cheat Integrity Warning Event
        res_warn = self.client.post(f"/teacher/exam/{attempt.id}/integrity-event", json={
            "event_type": "tab_switch",
            "details": "User switched browser tab during examination"
        })
        self.assertEqual(res_warn.status_code, 200)
        warn_data = res_warn.get_json()
        self.assertTrue(warn_data["recorded"])
        self.assertEqual(warn_data["warning_count"], 1)

        # 4. Submit Examination
        res_submit = self.client.post(f"/teacher/exam/{attempt.id}/submit", follow_redirects=True)
        self.assertEqual(res_submit.status_code, 200)

        evaluated_attempt = CollegeAssessmentAttempt.get_by_id(attempt.id)
        self.assertIn(evaluated_attempt.status, [CollegeAssessmentAttempt.STATUS_SUBMITTED, CollegeAssessmentAttempt.STATUS_EVALUATED])
        # q1 was correct ("opt_2"), marks=2.0
        self.assertGreaterEqual(evaluated_attempt.score, 2.0)
        self.assertEqual(evaluated_attempt.warning_count, 1)

    # --------------------------------------------------------------------------
    # 5. Teacher Grading Adjustment & Audit Trail
    # --------------------------------------------------------------------------
    def test_teacher_grading_adjustment_audit_trail(self):
        # Create an attempt to grade
        attempt = CollegeAssessmentAttempt({
            "user_id": str(self.student.id),
            "user_name": self.student.name,
            "user_email": self.student.email,
            "assessment_id": str(self.assessment.id),
            "assessment_title": self.assessment.title,
            "subject_id": str(self.subject.id),
            "status": CollegeAssessmentAttempt.STATUS_SUBMITTED,
            "score": 2.0,
            "max_score": 7.0,
            "percentage": 28.57,
            "needs_manual_review": True
        }).save()

        # Teacher logs in and modifies grade
        self._login_as(self.teacher)
        res_grade = self.client.post(f"/teacher/attempts/{attempt.id}/grade", data={
            "total_score": "5.5",
            "teacher_feedback": "Excellent derivation in subjective steps."
        }, follow_redirects=True)
        self.assertEqual(res_grade.status_code, 200)

        updated_att = CollegeAssessmentAttempt.get_by_id(attempt.id)
        self.assertEqual(updated_att.score, 5.5)
        self.assertEqual(updated_att.status, CollegeAssessmentAttempt.STATUS_EVALUATED)
        self.assertIn("Excellent derivation", updated_att.teacher_feedback)
        self.assertEqual(len(updated_att.grade_audit_trail), 1)
        self.assertEqual(updated_att.grade_audit_trail[0]["old_score"], 2.0)
        self.assertEqual(updated_att.grade_audit_trail[0]["new_score"], 5.5)

if __name__ == "__main__":
    unittest.main()
