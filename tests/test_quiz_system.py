import sys
import os
import json
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.stdout.reconfigure(encoding="utf-8")

from app import create_app
from models.mongo import Assignment, Submission, Course, User, Enrollment, get_db
from services.quiz_evaluator import sanitize_for_student, evaluate_quiz_submission
from bson import ObjectId


class TestQuizSystem(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.app.config["TESTING"] = True
        cls.app.config["WTF_CSRF_ENABLED"] = False
        cls.client = cls.app.test_client()

    def setUp(self):
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    def _login_test_user(self, course_id=None):
        """Creates or retrieves a test student and sets the session."""
        user = User.get_by_email("test_quiz_student@example.com")
        if not user:
            user = User({
                "email": "test_quiz_student@example.com",
                "name": "Quiz Student",
                "role": "student",
                "is_admin": True
            })
            user.set_password("SecurePassword123!")
            user.save()

        if course_id:
            enrollment = Enrollment.get_by_user_course(user.id, course_id)
            if not enrollment:
                enrollment = Enrollment({
                    "user_id": str(user.id),
                    "course_id": str(course_id),
                    "watch_percent": 100,
                    "video_completed": True,
                    "status": "in_progress"
                })
                enrollment.save()
            else:
                enrollment.watch_percent = 100
                enrollment.video_completed = True
                enrollment.save()

        with self.client.session_transaction() as sess:
            sess["_user_id"] = str(user.id)
            sess["_fresh"] = True
        return user

    # =========================================================================
    # 1. Evaluator Service Unit Tests
    # =========================================================================

    def test_evaluator_single_choice(self):
        """Verify single choice question grading."""
        quiz_data = {
            "questions": [
                {
                    "id": "q1",
                    "type": "single_choice",
                    "question": "What is Python?",
                    "marks": 5,
                    "options": [{"id": "opt_1", "text": "Language"}, {"id": "opt_2", "text": "Snake"}],
                    "correct_option_ids": ["opt_1"]
                }
            ]
        }
        # Correct answer
        res_correct = evaluate_quiz_submission(quiz_data, {"q1": "opt_1"}, passing_score=70)
        self.assertEqual(res_correct["marks_obtained"], 5.0)
        self.assertEqual(res_correct["percentage"], 100.0)
        self.assertTrue(res_correct["is_passed"])
        self.assertEqual(res_correct["status"], "approved")

        # Incorrect answer
        res_wrong = evaluate_quiz_submission(quiz_data, {"q1": "opt_2"}, passing_score=70)
        self.assertEqual(res_wrong["marks_obtained"], 0.0)
        self.assertEqual(res_wrong["percentage"], 0.0)
        self.assertFalse(res_wrong["is_passed"])
        self.assertEqual(res_wrong["status"], "rejected")

    def test_evaluator_multiple_select_partial_credit(self):
        """Verify multiple select grading and proportional partial credit."""
        quiz_data = {
            "questions": [
                {
                    "id": "q_multi",
                    "type": "multiple_select",
                    "question": "Which of these are mutable types in Python?",
                    "marks": 10,
                    "options": [
                        {"id": "opt_list", "text": "list"},
                        {"id": "opt_dict", "text": "dict"},
                        {"id": "opt_tuple", "text": "tuple"},
                        {"id": "opt_str", "text": "str"}
                    ],
                    "correct_option_ids": ["opt_list", "opt_dict"]
                }
            ]
        }
        # Both correct
        res_all = evaluate_quiz_submission(quiz_data, {"q_multi": ["opt_list", "opt_dict"]})
        self.assertEqual(res_all["marks_obtained"], 10.0)
        self.assertTrue(res_all["is_passed"])

        # Partial credit: 1 correct chosen out of 2 correct, 0 incorrect chosen -> 50% = 5.0 marks
        res_part = evaluate_quiz_submission(quiz_data, {"q_multi": ["opt_list"]})
        self.assertEqual(res_part["marks_obtained"], 5.0)
        self.assertEqual(res_part["percentage"], 50.0)

        # 1 correct and 1 incorrect chosen -> net = 0 marks
        res_net_zero = evaluate_quiz_submission(quiz_data, {"q_multi": ["opt_list", "opt_tuple"]})
        self.assertEqual(res_net_zero["marks_obtained"], 0.0)

    def test_evaluator_true_false(self):
        """Verify true/false question grading."""
        quiz_data = {
            "questions": [
                {
                    "id": "q_tf",
                    "type": "true_false",
                    "question": "Is Python dynamically typed?",
                    "marks": 4,
                    "options": [{"id": "true", "text": "True"}, {"id": "false", "text": "False"}],
                    "correct_option_ids": ["true"]
                }
            ]
        }
        res_true = evaluate_quiz_submission(quiz_data, {"q_tf": "true"})
        self.assertEqual(res_true["marks_obtained"], 4.0)
        self.assertTrue(res_true["is_passed"])

        res_false = evaluate_quiz_submission(quiz_data, {"q_tf": "false"})
        self.assertEqual(res_false["marks_obtained"], 0.0)

    def test_evaluator_short_answer(self):
        """Verify short answer automated matching and manual review flag."""
        quiz_data = {
            "questions": [
                {
                    "id": "q_sa",
                    "type": "short_answer",
                    "question": "What keyword defines a function in Python?",
                    "marks": 5,
                    "accepted_answers": ["def", "def keyword"],
                    "case_sensitive": False,
                    "requires_manual_review": False
                },
                {
                    "id": "q_essay",
                    "type": "short_answer",
                    "question": "Explain closure in 1 sentence.",
                    "marks": 5,
                    "accepted_answers": ["closure"],
                    "requires_manual_review": True
                }
            ]
        }
        # Matched answer (case-insensitive)
        res = evaluate_quiz_submission(quiz_data, {"q_sa": "  DEF  ", "q_essay": "closure"})
        self.assertEqual(res["marks_obtained"], 10.0)
        self.assertTrue(res["is_passed"])
        self.assertFalse(res["requires_manual_review"])

        # Essay question requires manual review when no exact match
        res_review = evaluate_quiz_submission(quiz_data, {"q_sa": "def", "q_essay": "A nested function that retains scope."})
        self.assertEqual(res_review["status"], "pending_review")
        self.assertTrue(res_review["requires_manual_review"])

    def test_sanitizer_security(self):
        """Verify sanitize_for_student strips all correct answers, accepted keys, and explanations."""
        raw_quiz = {
            "time_limit_minutes": 15,
            "max_attempts": 2,
            "questions": [
                {
                    "id": "q1",
                    "type": "single_choice",
                    "question": "Secret Question?",
                    "marks": 5,
                    "options": [{"id": "opt_1", "text": "A"}, {"id": "opt_2", "text": "B"}],
                    "correct_option_ids": ["opt_1"],
                    "accepted_answers": ["secret"],
                    "explanation": "This is why A is correct."
                }
            ]
        }
        sanitized = sanitize_for_student(raw_quiz)
        q = sanitized["questions"][0]

        self.assertNotIn("correct_option_ids", q)
        self.assertNotIn("accepted_answers", q)
        self.assertNotIn("explanation", q)
        self.assertEqual(q["question"], "Secret Question?")
        self.assertEqual(len(q["options"]), 2)

    # =========================================================================
    # 2. Assignment & Submission Model Tests
    # =========================================================================

    def test_assignment_quiz_based_properties(self):
        """Verify Assignment properties for quiz_based mode."""
        asg = Assignment({
            "title": "Python Theory Quiz",
            "evaluation_type": "quiz_based",
            "passing_score": 80,
            "quiz_data": {
                "time_limit_minutes": 20,
                "max_attempts": 3,
                "shuffle_questions": True,
                "questions": [
                    {"id": "q1", "type": "single_choice", "marks": 10},
                    {"id": "q2", "type": "multiple_select", "marks": 15}
                ]
            }
        })
        self.assertTrue(asg.is_quiz_based)
        self.assertFalse(asg.is_project_based)
        self.assertFalse(asg.is_algorithmic)
        self.assertEqual(asg.passing_score, 80)
        self.assertEqual(asg.quiz_total_marks, 25)
        self.assertEqual(asg.quiz_time_limit_minutes, 20)
        self.assertEqual(asg.quiz_max_attempts, 3)
        self.assertTrue(asg.quiz_shuffle_questions)

    def test_submission_quiz_data_persistence(self):
        """Verify Submission correctly stores and retrieves quiz results and attempts."""
        user = self._login_test_user()
        sub = Submission({
            "user_id": str(user.id),
            "assignment_id": "test_asg_123",
            "course_id": "test_course_123",
            "evaluation_type": "quiz_based",
            "quiz_answers": {"q1": "opt_1"},
            "quiz_results": {"percentage": 100, "marks_obtained": 10},
            "attempt_number": 1,
            "time_spent_seconds": 120,
            "status": Submission.STATUS_APPROVED
        })
        sub.save()

        fetched = Submission.get_by_id(sub.id)
        self.assertIsNotNone(fetched)
        self.assertTrue(fetched.is_quiz)
        self.assertEqual(fetched.attempt_number, 1)
        self.assertEqual(fetched.time_spent_seconds, 120)
        self.assertEqual(fetched.quiz_answers["q1"], "opt_1")
        self.assertEqual(fetched.status, Submission.STATUS_APPROVED)

        # Clean up
        sub.delete()

    # =========================================================================
    # 3. Integration & Route Tests
    # =========================================================================

    def test_quiz_assessment_student_workflow(self):
        """End-to-end integration: load assessment, submit answers, evaluate score, and view result."""
        # Create course & quiz assignment
        course = Course({
            "title": "Cybersecurity Fundamentals",
            "slug": f"cybersec-quiz-{ObjectId()}",
            "is_published": True
        })
        course.save()

        user = self._login_test_user(course.id)

        quiz_data = {
            "time_limit_minutes": 10,
            "max_attempts": 2,
            "allow_review_answers": True,
            "questions": [
                {
                    "id": "q_cia",
                    "type": "single_choice",
                    "question": "What does CIA triad stand for?",
                    "marks": 10,
                    "options": [
                        {"id": "opt_1", "text": "Confidentiality, Integrity, Availability"},
                        {"id": "opt_2", "text": "Central Intelligence Agency"}
                    ],
                    "correct_option_ids": ["opt_1"],
                    "explanation": "CIA in info-sec stands for Confidentiality, Integrity, Availability."
                }
            ]
        }

        assignment = Assignment({
            "course_id": str(course.id),
            "title": "Cybersecurity Knowledge Check",
            "step_number": 1,
            "total_steps": 1,
            "evaluation_type": "quiz_based",
            "passing_score": 70,
            "quiz_data": quiz_data,
            "is_published": True
        })
        assignment.save()

        # 1. GET assessment page
        resp_get = self.client.get(f"/learning/assignments/{assignment.id}/quiz")
        self.assertEqual(resp_get.status_code, 200)
        self.assertIn(b"Cybersecurity Knowledge Check", resp_get.data)
        # Verify correct answer keys and explanations are NOT leaked into student HTML
        self.assertNotIn(b"correct_option_ids", resp_get.data)
        self.assertNotIn(b"CIA in info-sec stands for", resp_get.data)

        # 2. POST failing answer
        resp_fail = self.client.post(
            f"/learning/assignments/{assignment.id}/quiz/submit",
            json={"answers": {"q_cia": "opt_2"}, "time_spent_seconds": 45}
        )
        self.assertEqual(resp_fail.status_code, 200)
        data_fail = resp_fail.get_json()
        self.assertFalse(data_fail["is_passed"])
        self.assertEqual(data_fail["status"], "rejected")

        # 3. POST passing answer (Attempt #2)
        resp_pass = self.client.post(
            f"/learning/assignments/{assignment.id}/quiz/submit",
            json={"answers": {"q_cia": "opt_1"}, "time_spent_seconds": 60}
        )
        self.assertEqual(resp_pass.status_code, 200)
        data_pass = resp_pass.get_json()
        self.assertTrue(data_pass["is_passed"])
        self.assertEqual(data_pass["status"], "approved")

        # 4. GET result page
        resp_res = self.client.get(f"/learning/assignments/{assignment.id}/quiz/result")
        self.assertEqual(resp_res.status_code, 200)
        self.assertIn(b"Assessment Passed", resp_res.data)
        self.assertIn(b"100%", resp_res.data)

        # Clean up
        db = get_db()
        db.courses.delete_one({"_id": course._id})
        db.assignments.delete_one({"_id": assignment._id})
        db.submissions.delete_many({"assignment_id": str(assignment.id)})
        db.enrollments.delete_many({"course_id": str(course.id)})


if __name__ == "__main__":
    unittest.main()
