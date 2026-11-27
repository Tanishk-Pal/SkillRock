"""
SkillRock — College Academic Assessment & Examination Platform Models
Defines AcademicSubject, AcademicQuestion, CollegeAssessment, and CollegeAssessmentAttempt.
Provides robust multi-role academic exam management, configurable anti-cheat enforcement,
and automated objective + teacher rubric evaluation.
"""

from datetime import datetime, timezone, timedelta
from bson import ObjectId
from models.mongo import db, get_db, _to_obj_id, slugify

class AcademicSubject:
    collection_name = "academic_subjects"

    def __init__(self, data=None):
        self._data = data or {}
        self._id = self._data.get("_id")
        self.id = str(self._id) if self._id else ""
        self.name = self._data.get("name", "")
        self.code = self._data.get("code", "")
        self.year = str(self._data.get("year", "1"))  # "1", "2", "3", "4"
        self.department = self._data.get("department", "Computer Science & Engineering")
        self.semester = int(self._data.get("semester", 1))
        self.description = self._data.get("description", "")
        self.teacher_ids = [str(tid) for tid in self._data.get("teacher_ids", [])]
        self.teacher_name = self._data.get("teacher_name", "Department Faculty")
        self.icon = self._data.get("icon", "book-open")
        self.is_active = bool(self._data.get("is_active", True))
        self.created_at = self._data.get("created_at") or datetime.now(timezone.utc)
        self.updated_at = self._data.get("updated_at") or datetime.now(timezone.utc)

    @property
    def year_label(self):
        mapping = {
            "1": "First Year",
            "2": "Second Year",
            "3": "Third Year",
            "4": "Fourth Year"
        }
        return mapping.get(str(self.year), f"Year {self.year}")

    def save(self):
        database = get_db()
        self.updated_at = datetime.now(timezone.utc)
        data = {
            "name": self.name,
            "code": self.code,
            "year": str(self.year),
            "department": self.department,
            "semester": self.semester,
            "description": self.description,
            "teacher_ids": self.teacher_ids,
            "teacher_name": self.teacher_name,
            "icon": self.icon,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
        if self._id:
            database[self.collection_name].update_one({"_id": self._id}, {"$set": data})
        else:
            res = database[self.collection_name].insert_one(data)
            self._id = res.inserted_id
            self.id = str(self._id)
        return self

    @classmethod
    def get_by_id(cls, subject_id):
        database = get_db()
        obj_id = _to_obj_id(subject_id)
        if not obj_id:
            return None
        doc = database[cls.collection_name].find_one({"_id": obj_id})
        return cls(doc) if doc else None

    @classmethod
    def find_all(cls, query=None, sort=None):
        database = get_db()
        query = query or {}
        cursor = database[cls.collection_name].find(query)
        if sort:
            cursor = cursor.sort(sort)
        else:
            cursor = cursor.sort([("year", 1), ("name", 1)])
        return [cls(doc) for doc in cursor]

    @classmethod
    def find_by_year(cls, year, department=None):
        query = {"year": str(year), "is_active": True}
        if department:
            query["department"] = department
        return cls.find_all(query)

    def delete(self):
        if not self._id:
            return False
        database = get_db()
        database[self.collection_name].delete_one({"_id": self._id})
        return True


class AcademicQuestion:
    collection_name = "academic_questions"

    TYPE_MCQ = "mcq"
    TYPE_MULTIPLE_SELECT = "multiple_select"
    TYPE_TRUE_FALSE = "true_false"
    TYPE_FILL_BLANKS = "fill_blanks"
    TYPE_NUMERICAL = "numerical"
    TYPE_SHORT_ANSWER = "short_answer"
    TYPE_LONG_ANSWER = "long_answer"
    TYPE_CODING = "coding"

    VALID_TYPES = [
        TYPE_MCQ,
        TYPE_MULTIPLE_SELECT,
        TYPE_TRUE_FALSE,
        TYPE_FILL_BLANKS,
        TYPE_NUMERICAL,
        TYPE_SHORT_ANSWER,
        TYPE_LONG_ANSWER,
        TYPE_CODING,
    ]

    def __init__(self, data=None):
        self._data = data or {}
        self._id = self._data.get("_id")
        self.id = str(self._id) if self._id else ""
        self.teacher_id = str(self._data.get("teacher_id", ""))
        self.teacher_name = self._data.get("teacher_name", "")
        self.subject_id = str(self._data.get("subject_id", ""))
        self.subject_name = self._data.get("subject_name", "")
        self.topic = self._data.get("topic", "General")
        self.chapter = self._data.get("chapter", "")
        self.question_text = self._data.get("question_text", "")
        self.question_type = self._data.get("question_type", self.TYPE_MCQ)
        self.difficulty = self._data.get("difficulty", "Intermediate")  # Beginner, Intermediate, Advanced
        self.marks = float(self._data.get("marks", 2.0))
        self.negative_marks = float(self._data.get("negative_marks", 0.0))
        self.options = self._data.get("options", [])  # [{"id": "opt_1", "text": "..."}]
        self.correct_answers = self._data.get("correct_answers", [])
        self.numeric_tolerance = float(self._data.get("numeric_tolerance", 0.05))
        self.explanation = self._data.get("explanation", "")
        self.evaluation_rubric = self._data.get("evaluation_rubric", "")
        self.grading_keywords = self._data.get("grading_keywords", [])

        # Coding Question Attributes
        self.coding_language = self._data.get("coding_language", "python")
        self.coding_starter_code = self._data.get("coding_starter_code", "")
        self.coding_sample_input = self._data.get("coding_sample_input", "")
        self.coding_sample_output = self._data.get("coding_sample_output", "")
        self.coding_hidden_test_cases = self._data.get("coding_hidden_test_cases", [])  # [{"input": "...", "output": "..."}]
        self.coding_constraints = self._data.get("coding_constraints", "")

        self.is_published = bool(self._data.get("is_published", True))
        self.created_at = self._data.get("created_at") or datetime.now(timezone.utc)
        self.updated_at = self._data.get("updated_at") or datetime.now(timezone.utc)

    def to_dict(self, include_solutions=False):
        """Serializes question, stripping answer keys & hidden test cases for students."""
        payload = {
            "id": self.id,
            "subject_id": self.subject_id,
            "subject_name": self.subject_name,
            "topic": self.topic,
            "chapter": self.chapter,
            "question_text": self.question_text,
            "question_type": self.question_type,
            "difficulty": self.difficulty,
            "marks": self.marks,
            "negative_marks": self.negative_marks,
            "options": self.options,
            "coding_language": self.coding_language,
            "coding_starter_code": self.coding_starter_code,
            "coding_sample_input": self.coding_sample_input,
            "coding_sample_output": self.coding_sample_output,
            "coding_constraints": self.coding_constraints,
        }
        if include_solutions:
            payload["correct_answers"] = self.correct_answers
            payload["numeric_tolerance"] = self.numeric_tolerance
            payload["explanation"] = self.explanation
            payload["evaluation_rubric"] = self.evaluation_rubric
            payload["grading_keywords"] = self.grading_keywords
            payload["coding_hidden_test_cases"] = self.coding_hidden_test_cases
        return payload

    def save(self):
        database = get_db()
        self.updated_at = datetime.now(timezone.utc)
        data = {
            "teacher_id": self.teacher_id,
            "teacher_name": self.teacher_name,
            "subject_id": self.subject_id,
            "subject_name": self.subject_name,
            "topic": self.topic,
            "chapter": self.chapter,
            "question_text": self.question_text,
            "question_type": self.question_type,
            "difficulty": self.difficulty,
            "marks": self.marks,
            "negative_marks": self.negative_marks,
            "options": self.options,
            "correct_answers": self.correct_answers,
            "numeric_tolerance": self.numeric_tolerance,
            "explanation": self.explanation,
            "evaluation_rubric": self.evaluation_rubric,
            "grading_keywords": self.grading_keywords,
            "coding_language": self.coding_language,
            "coding_starter_code": self.coding_starter_code,
            "coding_sample_input": self.coding_sample_input,
            "coding_sample_output": self.coding_sample_output,
            "coding_hidden_test_cases": self.coding_hidden_test_cases,
            "coding_constraints": self.coding_constraints,
            "is_published": self.is_published,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
        if self._id:
            database[self.collection_name].update_one({"_id": self._id}, {"$set": data})
        else:
            res = database[self.collection_name].insert_one(data)
            self._id = res.inserted_id
            self.id = str(self._id)
        return self

    @classmethod
    def get_by_id(cls, qid):
        database = get_db()
        obj_id = _to_obj_id(qid)
        if not obj_id:
            return None
        doc = database[cls.collection_name].find_one({"_id": obj_id})
        return cls(doc) if doc else None

    @classmethod
    def find_all(cls, query=None, limit=0, sort=None):
        database = get_db()
        query = query or {}
        cursor = database[cls.collection_name].find(query)
        if sort:
            cursor = cursor.sort(sort)
        else:
            cursor = cursor.sort("created_at", -1)
        if limit > 0:
            cursor = cursor.limit(limit)
        return [cls(doc) for doc in cursor]

    def delete(self):
        if not self._id:
            return False
        database = get_db()
        database[self.collection_name].delete_one({"_id": self._id})
        return True


class CollegeAssessment:
    collection_name = "college_assessments"

    STATUS_DRAFT = "draft"
    STATUS_SCHEDULED = "scheduled"
    STATUS_PUBLISHED = "published"
    STATUS_CLOSED = "closed"
    STATUS_ARCHIVED = "archived"

    ASSESSMENT_TYPES = [
        "Unit Test",
        "Internal Assessment",
        "Mid-Semester Examination",
        "End-Semester Examination",
        "Practice Test",
        "Coding Assessment",
        "Surprise Test",
        "Custom Assessment"
    ]

    def __init__(self, data=None):
        self._data = data or {}
        self._id = self._data.get("_id")
        self.id = str(self._id) if self._id else ""
        self.title = self._data.get("title", "")
        self.slug = self._data.get("slug", "") or slugify(self.title)
        self.description = self._data.get("description", "")
        self.subject_id = str(self._data.get("subject_id", ""))
        self.subject_name = self._data.get("subject_name", "")
        self.subject_code = self._data.get("subject_code", "")
        self.academic_year = str(self._data.get("academic_year", "1"))  # "1", "2", "3", "4"
        self.semester = int(self._data.get("semester", 1))
        self.department = self._data.get("department", "Computer Science & Engineering")
        self.class_section = self._data.get("class_section", "All Sections")
        self.assessment_type = self._data.get("assessment_type", "Unit Test")
        self.teacher_id = str(self._data.get("teacher_id", ""))
        self.teacher_name = self._data.get("teacher_name", "")
        self.duration_minutes = int(self._data.get("duration_minutes", 45))
        self.total_marks = float(self._data.get("total_marks", 30.0))
        self.passing_marks = float(self._data.get("passing_marks", 12.0))
        self.exam_date = self._data.get("exam_date", "")  # YYYY-MM-DD
        self.start_time = self._data.get("start_time", "09:00")
        self.end_time = self._data.get("end_time", "23:59")
        self.start_datetime = self._data.get("start_datetime")
        self.end_datetime = self._data.get("end_datetime")
        self.max_attempts = int(self._data.get("max_attempts", 1))
        self.status = self._data.get("status", self.STATUS_PUBLISHED)
        self.result_published = bool(self._data.get("result_published", False))
        self.result_publish_date = self._data.get("result_publish_date")
        self.question_ids = [str(qid) for qid in self._data.get("question_ids", [])]

        # Configurable Anti-Cheat & Integrity Settings
        integrity = self._data.get("integrity_settings", {}) or {}
        self.integrity_settings = {
            "preset": integrity.get("preset", "standard"),  # basic, standard, strict, custom
            "fullscreen_monitoring": bool(integrity.get("fullscreen_monitoring", True)),
            "tab_switch_monitoring": bool(integrity.get("tab_switch_monitoring", True)),
            "copy_paste_monitoring": bool(integrity.get("copy_paste_monitoring", True)),
            "context_menu_monitoring": bool(integrity.get("context_menu_monitoring", True)),
            "keyboard_shortcut_monitoring": bool(integrity.get("keyboard_shortcut_monitoring", True)),
            "camera_permission": integrity.get("camera_permission", "optional"),  # off, optional, required
            "attempt_resumption": integrity.get("attempt_resumption", "allowed"),  # allowed, restricted
            "max_warnings": int(integrity.get("max_warnings", 3)),
            "auto_submit_on_limit": bool(integrity.get("auto_submit_on_limit", True)),
            "randomize_questions": bool(integrity.get("randomize_questions", True)),
            "randomize_options": bool(integrity.get("randomize_options", True)),
        }

        self.created_at = self._data.get("created_at") or datetime.now(timezone.utc)
        self.updated_at = self._data.get("updated_at") or datetime.now(timezone.utc)

    @property
    def questions(self):
        """Resolves linked AcademicQuestion instances."""
        if not self.question_ids:
            return []
        database = get_db()
        obj_ids = [_to_obj_id(qid) for qid in self.question_ids if _to_obj_id(qid)]
        cursor = database[AcademicQuestion.collection_name].find({"_id": {"$in": obj_ids}})
        doc_map = {str(doc["_id"]): AcademicQuestion(doc) for doc in cursor}
        return [doc_map[qid] for qid in self.question_ids if qid in doc_map]

    @property
    def computed_total_marks(self):
        qs = self.questions
        return sum(q.marks for q in qs) if qs else self.total_marks

    @property
    def live_status(self):
        """
        Dynamically calculates assessment lifecycle:
        - Upcoming
        - Live
        - Completed / Closed
        - Result Published
        """
        if self.result_published:
            return "Result Published"

        now = datetime.now(timezone.utc)
        if self.start_datetime:
            s_dt = self.start_datetime if self.start_datetime.tzinfo else self.start_datetime.replace(tzinfo=timezone.utc)
            if now < s_dt:
                return "Upcoming"
        if self.end_datetime:
            e_dt = self.end_datetime if self.end_datetime.tzinfo else self.end_datetime.replace(tzinfo=timezone.utc)
            if now > e_dt:
                return "Closed"

        if self.status == self.STATUS_CLOSED:
            return "Closed"
        if self.status == self.STATUS_DRAFT:
            return "Draft"
        if self.status in [self.STATUS_PUBLISHED, self.STATUS_SCHEDULED]:
            return "Live"
        return self.status.capitalize()

    def save(self):
        database = get_db()
        self.updated_at = datetime.now(timezone.utc)
        data = {
            "title": self.title,
            "slug": self.slug,
            "description": self.description,
            "subject_id": self.subject_id,
            "subject_name": self.subject_name,
            "subject_code": self.subject_code,
            "academic_year": str(self.academic_year),
            "semester": self.semester,
            "department": self.department,
            "class_section": self.class_section,
            "assessment_type": self.assessment_type,
            "teacher_id": self.teacher_id,
            "teacher_name": self.teacher_name,
            "duration_minutes": self.duration_minutes,
            "total_marks": self.total_marks,
            "passing_marks": self.passing_marks,
            "exam_date": self.exam_date,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "start_datetime": self.start_datetime,
            "end_datetime": self.end_datetime,
            "max_attempts": self.max_attempts,
            "status": self.status,
            "result_published": self.result_published,
            "result_publish_date": self.result_publish_date,
            "question_ids": self.question_ids,
            "integrity_settings": self.integrity_settings,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
        if self._id:
            database[self.collection_name].update_one({"_id": self._id}, {"$set": data})
        else:
            res = database[self.collection_name].insert_one(data)
            self._id = res.inserted_id
            self.id = str(self._id)
        return self

    @classmethod
    def get_by_id(cls, aid):
        database = get_db()
        obj_id = _to_obj_id(aid)
        if not obj_id:
            return None
        doc = database[cls.collection_name].find_one({"_id": obj_id})
        return cls(doc) if doc else None

    @classmethod
    def get_by_slug(cls, slug):
        database = get_db()
        doc = database[cls.collection_name].find_one({"slug": slug})
        return cls(doc) if doc else None

    @classmethod
    def find_all(cls, query=None, limit=0, sort=None):
        database = get_db()
        query = query or {}
        cursor = database[cls.collection_name].find(query)
        if sort:
            cursor = cursor.sort(sort)
        else:
            cursor = cursor.sort("created_at", -1)
        if limit > 0:
            cursor = cursor.limit(limit)
        return [cls(doc) for doc in cursor]

    def delete(self):
        if not self._id:
            return False
        database = get_db()
        database[self.collection_name].delete_one({"_id": self._id})
        return True


class CollegeAssessmentAttempt:
    collection_name = "college_assessment_attempts"

    STATUS_IN_PROGRESS = "in_progress"
    STATUS_SUBMITTED = "submitted"
    STATUS_EVALUATED = "evaluated"
    STATUS_CANCELLED = "cancelled"
    STATUS_TIMED_OUT = "timed_out"

    def __init__(self, data=None):
        self._data = data or {}
        self._id = self._data.get("_id")
        self.id = str(self._id) if self._id else ""
        self.user_id = str(self._data.get("user_id", ""))
        self.user_name = self._data.get("user_name", "")
        self.user_email = self._data.get("user_email", "")
        self.roll_number = self._data.get("roll_number", "")
        self.assessment_id = str(self._data.get("assessment_id", ""))
        self.assessment_title = self._data.get("assessment_title", "")
        self.subject_id = str(self._data.get("subject_id", ""))
        self.subject_name = self._data.get("subject_name", "")
        self.subject_code = self._data.get("subject_code", "")
        self.academic_year = str(self._data.get("academic_year", "1"))
        self.status = self._data.get("status", self.STATUS_IN_PROGRESS)
        self.started_at = self._data.get("started_at") or datetime.now(timezone.utc)
        self.duration_minutes = int(self._data.get("duration_minutes", 45))
        self.deadline_at = self._data.get("deadline_at") or (self.started_at + timedelta(minutes=self.duration_minutes))
        self.submitted_at = self._data.get("submitted_at")
        self.time_taken_seconds = int(self._data.get("time_taken_seconds", 0))

        # Stored responses: question_id -> {"answer": ..., "marked_for_review": bool, "saved_at": ...}
        self.responses = self._data.get("responses", {}) or {}

        # Integrity & Anti-Cheat Events Log
        self.integrity_events = self._data.get("integrity_events", []) or []
        self.warning_count = int(self._data.get("warning_count", len(self.integrity_events)))
        self.cancellation_reason = self._data.get("cancellation_reason", "")
        self.cancelled_at = self._data.get("cancelled_at")
        self.webcam_verified = bool(self._data.get("webcam_verified", False))

        # Scoring & Evaluation
        self.score = float(self._data.get("score", 0.0))
        self.max_score = float(self._data.get("max_score", 0.0))
        self.percentage = float(self._data.get("percentage", 0.0))
        self.is_passed = bool(self._data.get("is_passed", False))
        self.correct_count = int(self._data.get("correct_count", 0))
        self.incorrect_count = int(self._data.get("incorrect_count", 0))
        self.unanswered_count = int(self._data.get("unanswered_count", 0))
        self.needs_manual_review = bool(self._data.get("needs_manual_review", False))
        self.question_evaluations = self._data.get("question_evaluations", {}) or {}  # qid -> {score, feedback, evaluated_by}
        self.teacher_feedback = self._data.get("teacher_feedback", "")
        self.evaluator_id = self._data.get("evaluator_id", "")
        self.evaluated_at = self._data.get("evaluated_at")
        self.grade_audit_trail = self._data.get("grade_audit_trail", []) or []

        self.created_at = self._data.get("created_at") or self.started_at
        self.updated_at = self._data.get("updated_at") or datetime.now(timezone.utc)

    @property
    def remaining_seconds(self):
        if self.status != self.STATUS_IN_PROGRESS:
            return 0
        now = datetime.now(timezone.utc)
        deadline = self.deadline_at
        if deadline.tzinfo is None:
            deadline = deadline.replace(tzinfo=timezone.utc)
        rem = int((deadline - now).total_seconds())
        return max(0, rem)

    @property
    def is_expired(self):
        return self.remaining_seconds <= 0

    def add_integrity_event(self, event_type, details="Violation detected", max_warnings=3):
        """
        Records an anti-cheat event with a 4s debounce.
        Enforces configurable warning limit and auto-cancels if policy dictates.
        """
        now = datetime.now(timezone.utc)
        cooldown_sec = 4

        if self.integrity_events:
            last = self.integrity_events[-1]
            last_ts = last.get("timestamp")
            if isinstance(last_ts, str):
                try:
                    last_ts = datetime.fromisoformat(last_ts)
                except Exception:
                    last_ts = None
            if last_ts:
                if last_ts.tzinfo is None:
                    last_ts = last_ts.replace(tzinfo=timezone.utc)
                if (now - last_ts).total_seconds() < cooldown_sec:
                    return False, self.warning_count, False

        self.warning_count += 1
        event_record = {
            "warning_number": self.warning_count,
            "event_type": event_type,
            "timestamp": now.isoformat(),
            "details": details
        }
        self.integrity_events.append(event_record)

        cancelled = False
        if self.warning_count > max_warnings:
            self.status = self.STATUS_CANCELLED
            self.cancelled_at = now
            self.cancellation_reason = f"Assessment auto-cancelled: exceeded maximum integrity warnings limit ({self.warning_count} recorded)."
            cancelled = True

        self.save()
        return True, self.warning_count, cancelled

    def save(self):
        database = get_db()
        self.updated_at = datetime.now(timezone.utc)
        data = {
            "user_id": self.user_id,
            "user_name": self.user_name,
            "user_email": self.user_email,
            "roll_number": self.roll_number,
            "assessment_id": self.assessment_id,
            "assessment_title": self.assessment_title,
            "subject_id": self.subject_id,
            "subject_name": self.subject_name,
            "subject_code": self.subject_code,
            "academic_year": str(self.academic_year),
            "status": self.status,
            "started_at": self.started_at,
            "duration_minutes": self.duration_minutes,
            "deadline_at": self.deadline_at,
            "submitted_at": self.submitted_at,
            "time_taken_seconds": self.time_taken_seconds,
            "responses": self.responses,
            "integrity_events": self.integrity_events,
            "warning_count": self.warning_count,
            "cancellation_reason": self.cancellation_reason,
            "cancelled_at": self.cancelled_at,
            "webcam_verified": self.webcam_verified,
            "score": self.score,
            "max_score": self.max_score,
            "percentage": self.percentage,
            "is_passed": self.is_passed,
            "correct_count": self.correct_count,
            "incorrect_count": self.incorrect_count,
            "unanswered_count": self.unanswered_count,
            "needs_manual_review": self.needs_manual_review,
            "question_evaluations": self.question_evaluations,
            "teacher_feedback": self.teacher_feedback,
            "evaluator_id": self.evaluator_id,
            "evaluated_at": self.evaluated_at,
            "grade_audit_trail": self.grade_audit_trail,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
        if self._id:
            database[self.collection_name].update_one({"_id": self._id}, {"$set": data})
        else:
            res = database[self.collection_name].insert_one(data)
            self._id = res.inserted_id
            self.id = str(self._id)
        return self

    @classmethod
    def get_by_id(cls, aid):
        database = get_db()
        obj_id = _to_obj_id(aid)
        if not obj_id:
            return None
        doc = database[cls.collection_name].find_one({"_id": obj_id})
        return cls(doc) if doc else None

    @classmethod
    def get_active_attempt(cls, user_id, assessment_id):
        database = get_db()
        doc = database[cls.collection_name].find_one({
            "user_id": str(user_id),
            "assessment_id": str(assessment_id),
            "status": cls.STATUS_IN_PROGRESS
        })
        return cls(doc) if doc else None

    @classmethod
    def find_by_user(cls, user_id, limit=0):
        database = get_db()
        cursor = database[cls.collection_name].find({"user_id": str(user_id)}).sort("started_at", -1)
        if limit > 0:
            cursor = cursor.limit(limit)
        return [cls(doc) for doc in cursor]

    @classmethod
    def find_by_assessment(cls, assessment_id):
        database = get_db()
        cursor = database[cls.collection_name].find({"assessment_id": str(assessment_id)}).sort("submitted_at", -1)
        return [cls(doc) for doc in cursor]

    @classmethod
    def find_all(cls, query=None, limit=0, sort=None):
        database = get_db()
        query = query or {}
        cursor = database[cls.collection_name].find(query)
        if sort:
            cursor = cursor.sort(sort)
        else:
            cursor = cursor.sort("started_at", -1)
        if limit > 0:
            cursor = cursor.limit(limit)
        return [cls(doc) for doc in cursor]


def seed_default_academic_curriculum(database):
    """
    Seeds production-ready standard engineering curriculum across all 4 years
    if academic_subjects collection is empty.
    Allows Teachers & Admins to extend, modify, or add custom subjects.
    """
    if database[AcademicSubject.collection_name].count_documents({}) > 0:
        return

    curriculum = [
        # Year 1 (First Year)
        {"name": "Engineering Mathematics I & II", "code": "MATH101", "year": "1", "semester": 1, "icon": "calculator", "description": "Calculus, Linear Algebra, Differential Equations, and Vector Spaces for Engineers."},
        {"name": "Programming Fundamentals (C & Python)", "code": "CS101", "year": "1", "semester": 1, "icon": "code-2", "description": "Structured programming, logic design, pointers, memory allocation, and algorithmic problem solving."},
        {"name": "Basic Electrical & Electronics", "code": "EE101", "year": "1", "semester": 1, "icon": "zap", "description": "Circuit theorems, AC/DC fundamentals, semiconductor diodes, transistors, and operational amplifiers."},
        {"name": "Engineering Physics", "code": "PHY101", "year": "1", "semester": 2, "icon": "atom", "description": "Quantum mechanics, electromagnetic theory, optics, laser physics, and nanotechnology fundamentals."},
        {"name": "Engineering Chemistry", "code": "CHEM101", "year": "1", "semester": 2, "icon": "flask-conical", "description": "Spectroscopic techniques, polymers, electrochemistry, and corrosion science."},
        {"name": "English & Professional Communication", "code": "ENG101", "year": "1", "semester": 2, "icon": "message-square", "description": "Technical writing, interview presentation skills, professional articulation, and listening comprehension."},

        # Year 2 (Second Year)
        {"name": "Data Structures & Algorithms", "code": "CS201", "year": "2", "semester": 3, "icon": "binary", "description": "Arrays, Linked Lists, Trees, Graphs, Sorting, Dynamic Programming, and Asymptotic Complexity."},
        {"name": "Object-Oriented Programming (Java/C++)", "code": "CS202", "year": "2", "semester": 3, "icon": "boxes", "description": "Encapsulation, Polymorphism, Inheritance, Exception Handling, Design Patterns, and Collections."},
        {"name": "Database Management Systems (DBMS)", "code": "CS203", "year": "2", "semester": 4, "icon": "database", "description": "Relational algebra, SQL, Normalization, ACID transactions, Concurrency Control, and Indexing."},
        {"name": "Digital Logic & Computer Organization", "code": "CS204", "year": "2", "semester": 3, "icon": "cpu", "description": "Boolean algebra, Karnaugh maps, ALU design, Pipelining, Cache memory, and Instruction Sets."},
        {"name": "Discrete Mathematics", "code": "MATH201", "year": "2", "semester": 4, "icon": "sigma", "description": "Set theory, Graph theory, Combinatorics, Recurrence relations, and Propositional Logic."},

        # Year 3 (Third Year)
        {"name": "Operating Systems", "code": "CS301", "year": "3", "semester": 5, "icon": "terminal", "description": "Process scheduling, Multithreading, Deadlocks, Virtual memory paging, and Linux Kernel I/O."},
        {"name": "Computer Networks", "code": "CS302", "year": "3", "semester": 5, "icon": "network", "description": "OSI 7-layer model, TCP/IP, Routing algorithms, Congestion control, DNS, and Socket programming."},
        {"name": "Design & Analysis of Algorithms", "code": "CS303", "year": "3", "semester": 5, "icon": "git-branch", "description": "Greedy algorithms, Divide and Conquer, NP-Completeness, Approximation, and Graph Flows."},
        {"name": "Software Engineering & Agile", "code": "CS304", "year": "3", "semester": 6, "icon": "check-circle", "description": "SDLC, Scrum/Kanban, Software architecture, Unit testing, CI/CD, and Code Refactoring."},
        {"name": "Artificial Intelligence Fundamentals", "code": "CS305", "year": "3", "semester": 6, "icon": "brain", "description": "Heuristic search, A* algorithm, Knowledge representation, Minimax, and Expert Systems."},
        {"name": "Full Stack Web Development", "code": "CS306", "year": "3", "semester": 6, "icon": "globe", "description": "RESTful APIs, Client-Server architecture, React/Vite, Modern CSS, and Cloud Deployment."},

        # Year 4 (Fourth Year)
        {"name": "Machine Learning & Deep Learning", "code": "CS401", "year": "4", "semester": 7, "icon": "sparkles", "description": "Supervised & Unsupervised Learning, Neural Networks, CNNs, Transformers, and Model Evaluation."},
        {"name": "Cloud Computing & Distributed Systems", "code": "CS402", "year": "4", "semester": 7, "icon": "cloud", "description": "Virtualization, Docker, Kubernetes, AWS/GCP architectures, Microservices, and Serverless."},
        {"name": "Cyber Security & Cryptography", "code": "CS403", "year": "4", "semester": 7, "icon": "shield-check", "description": "Symmetric/Asymmetric encryption, RSA, AES, Network Penetration Testing, OWASP Top 10."},
        {"name": "Compiler Design", "code": "CS404", "year": "4", "semester": 8, "icon": "file-code", "description": "Lexical analysis, Lex/Yacc, Syntax-directed translation, Code optimization, and Register allocation."},
        {"name": "Capstone Project & Technical Assessment", "code": "CS405", "year": "4", "semester": 8, "icon": "award", "description": "Industry project evaluation, defense viva, system architecture audit, and code quality review."}
    ]

    now = datetime.now(timezone.utc)
    for item in curriculum:
        item["created_at"] = now
        item["updated_at"] = now
        item["is_active"] = True
        item["department"] = "Computer Science & Engineering"
        item["teacher_ids"] = []
        item["teacher_name"] = "Department Faculty"
        database[AcademicSubject.collection_name].insert_one(item)

    # Seed Sample Baseline Academic Tests if none exist
    if database[CollegeAssessment.collection_name].count_documents({}) == 0:
        # 1. Year 1 - CS101 Unit Test
        cs101 = database[AcademicSubject.collection_name].find_one({"code": "CS101"})
        if cs101:
            q1 = AcademicQuestion({
                "subject_id": str(cs101["_id"]),
                "subject_name": cs101["name"],
                "topic": "Pointers & Arrays",
                "question_text": "What is the output of the following C code?\n```c\nint a = 10;\nint *p = &a;\n*p = 25;\nprintf(\"%d\", a);\n```",
                "question_type": AcademicQuestion.TYPE_MCQ,
                "difficulty": "Beginner",
                "marks": 2.0,
                "options": [
                    {"id": "opt_1", "text": "10"},
                    {"id": "opt_2", "text": "25"},
                    {"id": "opt_3", "text": "Garbage Value"},
                    {"id": "opt_4", "text": "Compilation Error"}
                ],
                "correct_answers": ["opt_2"],
                "explanation": "Dereferencing pointer `*p = 25` modifies the original memory location of `a` directly."
            }).save()

            q2 = AcademicQuestion({
                "subject_id": str(cs101["_id"]),
                "subject_name": cs101["name"],
                "topic": "Python Datatypes",
                "question_text": "In Python, which of the following standard data types are immutable? (Select all that apply)",
                "question_type": AcademicQuestion.TYPE_MULTIPLE_SELECT,
                "difficulty": "Intermediate",
                "marks": 3.0,
                "options": [
                    {"id": "opt_a", "text": "Tuple"},
                    {"id": "opt_b", "text": "List"},
                    {"id": "opt_c", "text": "String"},
                    {"id": "opt_d", "text": "Integer"}
                ],
                "correct_answers": ["opt_a", "opt_c", "opt_d"],
                "explanation": "Tuples, Strings, and Integers are immutable in Python, whereas Lists and Dictionaries are mutable."
            }).save()

            q3 = AcademicQuestion({
                "subject_id": str(cs101["_id"]),
                "subject_name": cs101["name"],
                "topic": "Algorithmic Logic",
                "question_text": "Write a Python function `find_factorial(n)` that takes integer `n` and returns its factorial. Handle `0` and positive integers.",
                "question_type": AcademicQuestion.TYPE_CODING,
                "difficulty": "Intermediate",
                "marks": 5.0,
                "coding_language": "python",
                "coding_starter_code": "def find_factorial(n):\n    # Write your solution here\n    pass\n",
                "coding_sample_input": "5",
                "coding_sample_output": "120",
                "coding_hidden_test_cases": [
                    {"input": "0", "output": "1"},
                    {"input": "1", "output": "1"},
                    {"input": "4", "output": "24"},
                    {"input": "6", "output": "720"}
                ]
            }).save()

            CollegeAssessment({
                "title": "Unit Test 1: Programming Logic & Memory Pointers",
                "slug": "unit-test-1-cs101-logic-pointers",
                "description": "Standard college unit test evaluating pointer semantics, array allocation, and function recursion.",
                "subject_id": str(cs101["_id"]),
                "subject_name": cs101["name"],
                "subject_code": cs101["code"],
                "academic_year": "1",
                "semester": 1,
                "department": "Computer Science & Engineering",
                "class_section": "Section A & B",
                "assessment_type": "Unit Test",
                "teacher_name": "Prof. R. Sharma (HOD CSE)",
                "duration_minutes": 30,
                "total_marks": 10.0,
                "passing_marks": 4.0,
                "exam_date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                "start_time": "09:00",
                "end_time": "23:59",
                "start_datetime": datetime.now(timezone.utc) - timedelta(hours=1),
                "end_datetime": datetime.now(timezone.utc) + timedelta(days=7),
                "status": CollegeAssessment.STATUS_PUBLISHED,
                "result_published": True,
                "question_ids": [q1.id, q2.id, q3.id],
                "integrity_settings": {
                    "preset": "standard",
                    "fullscreen_monitoring": True,
                    "tab_switch_monitoring": True,
                    "copy_paste_monitoring": True,
                    "context_menu_monitoring": True,
                    "keyboard_shortcut_monitoring": True,
                    "camera_permission": "optional",
                    "max_warnings": 3,
                    "auto_submit_on_limit": True
                }
            }).save()

        # 2. Year 2 - CS201 Data Structures
        cs201 = database[AcademicSubject.collection_name].find_one({"code": "CS201"})
        if cs201:
            q_ds1 = AcademicQuestion({
                "subject_id": str(cs201["_id"]),
                "subject_name": cs201["name"],
                "topic": "Binary Search Trees",
                "question_text": "What is the worst-case time complexity of searching an element in a degenerate (skewed) Binary Search Tree with n nodes?",
                "question_type": AcademicQuestion.TYPE_MCQ,
                "difficulty": "Intermediate",
                "marks": 2.0,
                "options": [
                    {"id": "opt_1", "text": "O(1)"},
                    {"id": "opt_2", "text": "O(log n)"},
                    {"id": "opt_3", "text": "O(n)"},
                    {"id": "opt_4", "text": "O(n log n)"}
                ],
                "correct_answers": ["opt_3"],
                "explanation": "A skewed BST degrades to a linked list, requiring linear O(n) traversal."
            }).save()

            CollegeAssessment({
                "title": "Unit Test 2: Trees, Graphs & Dynamic Programming",
                "slug": "unit-test-2-cs201-trees-graphs",
                "description": "Internal assessment covering non-linear data structures, traversal algorithms, and asymptotic space-time bounds.",
                "subject_id": str(cs201["_id"]),
                "subject_name": cs201["name"],
                "subject_code": cs201["code"],
                "academic_year": "2",
                "semester": 3,
                "department": "Computer Science & Engineering",
                "class_section": "All Sections",
                "assessment_type": "Internal Assessment",
                "teacher_name": "Dr. V. Verma (Faculty Guide)",
                "duration_minutes": 45,
                "total_marks": 20.0,
                "passing_marks": 8.0,
                "exam_date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                "start_time": "10:00",
                "end_time": "23:59",
                "start_datetime": datetime.now(timezone.utc) - timedelta(hours=2),
                "end_datetime": datetime.now(timezone.utc) + timedelta(days=14),
                "status": CollegeAssessment.STATUS_PUBLISHED,
                "result_published": True,
                "question_ids": [q_ds1.id],
                "integrity_settings": {
                    "preset": "standard",
                    "fullscreen_monitoring": True,
                    "tab_switch_monitoring": True,
                    "copy_paste_monitoring": True,
                    "context_menu_monitoring": True,
                    "keyboard_shortcut_monitoring": True,
                    "camera_permission": "optional",
                    "max_warnings": 3,
                    "auto_submit_on_limit": True
                }
            }).save()

