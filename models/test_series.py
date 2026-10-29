"""
SkillRock — Interview Test Series Models & Persistence Layer
Defines Questions, TestDefinitions, TestPacks, TestAttempts, and UserEntitlements
supporting timed assessments, focus-loss monitoring, and server-side evaluation.
"""

from datetime import datetime, timezone, timedelta
from bson import ObjectId
from models.mongo import db, get_db, _to_obj_id, slugify

class Question:
    collection_name = "test_questions"

    TYPE_SINGLE_CHOICE = "single_choice"
    TYPE_MULTIPLE_SELECT = "multiple_select"
    TYPE_TRUE_FALSE = "true_false"
    TYPE_CODE_OUTPUT = "code_output"
    TYPE_SHORT_ANSWER = "short_answer"

    VALID_TYPES = [
        TYPE_SINGLE_CHOICE,
        TYPE_MULTIPLE_SELECT,
        TYPE_TRUE_FALSE,
        TYPE_CODE_OUTPUT,
        TYPE_SHORT_ANSWER
    ]

    def __init__(self, data=None):
        self._data = data or {}
        self._id = self._data.get("_id")
        self.id = str(self._id) if self._id else ""
        self.question_text = self._data.get("question_text", "")
        self.question_type = self._data.get("question_type", self.TYPE_SINGLE_CHOICE)
        self.category = self._data.get("category", "General Aptitude")
        self.subtopic = self._data.get("subtopic", "General")
        self.difficulty = self._data.get("difficulty", "Beginner")  # Beginner, Intermediate, Advanced
        self.options = self._data.get("options", [])  # [{"id": "opt_1", "text": "...", "code": "..."}]
        self.correct_answers = self._data.get("correct_answers", [])  # List of correct option IDs or values
        self.explanation = self._data.get("explanation", "")
        self.code_snippet = self._data.get("code_snippet", "")
        self.language = self._data.get("language", "")
        self.marks = float(self._data.get("marks", 1.0))
        self.negative_marks = float(self._data.get("negative_marks", 0.0))
        self.tags = self._data.get("tags", [])
        self.is_published = bool(self._data.get("is_published", True))
        self.created_at = self._data.get("created_at") or datetime.now(timezone.utc)
        self.updated_at = self._data.get("updated_at") or datetime.now(timezone.utc)

    def to_dict(self, include_solutions=False):
        """
        Serializes question. CRITICAL: include_solutions=False strips correct_answers
        and explanation to prevent leaking answers to active exam takers.
        """
        payload = {
            "id": self.id,
            "question_text": self.question_text,
            "question_type": self.question_type,
            "category": self.category,
            "subtopic": self.subtopic,
            "difficulty": self.difficulty,
            "options": self.options,
            "code_snippet": self.code_snippet,
            "language": self.language,
            "marks": self.marks,
            "negative_marks": self.negative_marks,
            "tags": self.tags,
            "is_published": self.is_published,
        }
        if include_solutions:
            payload["correct_answers"] = self.correct_answers
            payload["explanation"] = self.explanation
        return payload

    def save(self):
        database = get_db()
        self.updated_at = datetime.now(timezone.utc)
        data = {
            "question_text": self.question_text,
            "question_type": self.question_type,
            "category": self.category,
            "subtopic": self.subtopic,
            "difficulty": self.difficulty,
            "options": self.options,
            "correct_answers": self.correct_answers,
            "explanation": self.explanation,
            "code_snippet": self.code_snippet,
            "language": self.language,
            "marks": self.marks,
            "negative_marks": self.negative_marks,
            "tags": self.tags,
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
    def get_by_id(cls, question_id):
        database = get_db()
        obj_id = _to_obj_id(question_id)
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

    @classmethod
    def count(cls, query=None):
        database = get_db()
        query = query or {}
        return database[cls.collection_name].count_documents(query)

    def delete(self):
        if not self._id:
            return False
        database = get_db()
        database[self.collection_name].delete_one({"_id": self._id})
        return True


class TestDefinition:
    collection_name = "test_series_tests"

    def __init__(self, data=None):
        self._data = data or {}
        self._id = self._data.get("_id")
        self.id = str(self._id) if self._id else ""
        self.title = self._data.get("title", "")
        self.slug = self._data.get("slug", "") or slugify(self.title)
        self.description = self._data.get("description", "")
        self.category = self._data.get("category", "Quantitative Aptitude")
        self.difficulty = self._data.get("difficulty", "Beginner")  # Beginner, Intermediate, Advanced
        self.duration_minutes = int(self._data.get("duration_minutes", 30))
        self.total_questions_count = int(self._data.get("total_questions_count", 30))
        self.passing_percentage = float(self._data.get("passing_percentage", 50.0))
        self.is_free = bool(self._data.get("is_free", True))
        self.pack_ids = [str(pid) for pid in self._data.get("pack_ids", [])]
        self.question_ids = [str(qid) for qid in self._data.get("question_ids", [])]
        self.question_selection_mode = self._data.get("question_selection_mode", "manual")  # manual or category_rule
        self.category_rule = self._data.get("category_rule", {})  # e.g. {"category": "...", "difficulty": "..."}
        
        # Focus loss anti-cheating configuration
        focus_policy = self._data.get("focus_loss_policy", {}) or {}
        self.focus_loss_policy = {
            "enabled": bool(focus_policy.get("enabled", True)),
            "max_warnings": int(focus_policy.get("max_warnings", 3)),
            "warning_cooldown_seconds": int(focus_policy.get("warning_cooldown_seconds", 5))
        }

        # Attached YouTube preparation videos
        self.video_resources = self._data.get("video_resources", [])  # [{"title": "", "youtube_url": "", "topic": "", "description": ""}]
        self.is_published = bool(self._data.get("is_published", True))
        self.is_archived = bool(self._data.get("is_archived", False))
        self.display_order = int(self._data.get("display_order", 0))
        self.created_at = self._data.get("created_at") or datetime.now(timezone.utc)
        self.updated_at = self._data.get("updated_at") or datetime.now(timezone.utc)

    @property
    def questions(self):
        """Resolves attached Question instances from the question bank."""
        if not self.question_ids:
            return []
        database = get_db()
        obj_ids = [_to_obj_id(qid) for qid in self.question_ids if _to_obj_id(qid)]
        cursor = database[Question.collection_name].find({"_id": {"$in": obj_ids}, "is_published": True})
        doc_map = {str(doc["_id"]): Question(doc) for doc in cursor}
        # Maintain order of question_ids
        ordered = []
        for qid in self.question_ids:
            if qid in doc_map:
                ordered.append(doc_map[qid])
        return ordered

    @property
    def total_marks(self):
        qs = self.questions
        if qs:
            return sum(q.marks for q in qs)
        return float(self.total_questions_count)

    def validate_publishable(self):
        """Validates that test has sufficient approved questions before publication."""
        qs = self.questions
        if len(qs) < self.total_questions_count:
            return False, f"Test requires {self.total_questions_count} questions, but only {len(qs)} are linked."
        return True, "Valid"

    def save(self):
        database = get_db()
        self.updated_at = datetime.now(timezone.utc)
        data = {
            "title": self.title,
            "slug": self.slug,
            "description": self.description,
            "category": self.category,
            "difficulty": self.difficulty,
            "duration_minutes": self.duration_minutes,
            "total_questions_count": self.total_questions_count,
            "passing_percentage": self.passing_percentage,
            "is_free": self.is_free,
            "pack_ids": self.pack_ids,
            "question_ids": self.question_ids,
            "question_selection_mode": self.question_selection_mode,
            "category_rule": self.category_rule,
            "focus_loss_policy": self.focus_loss_policy,
            "video_resources": self.video_resources,
            "is_published": self.is_published,
            "is_archived": self.is_archived,
            "display_order": self.display_order,
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
    def get_by_id(cls, test_id):
        database = get_db()
        obj_id = _to_obj_id(test_id)
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
            cursor = cursor.sort("display_order", 1)
        if limit > 0:
            cursor = cursor.limit(limit)
        return [cls(doc) for doc in cursor]

    def delete(self):
        if not self._id:
            return False
        database = get_db()
        database[self.collection_name].delete_one({"_id": self._id})
        return True


class TestPack:
    collection_name = "test_series_packs"

    STATUS_PUBLISHED = "published"
    STATUS_COMING_SOON = "coming_soon"
    STATUS_UNPUBLISHED = "unpublished"
    STATUS_ARCHIVED = "archived"

    def __init__(self, data=None):
        self._data = data or {}
        self._id = self._data.get("_id")
        self.id = str(self._id) if self._id else ""
        self.title = self._data.get("title", "")
        self.slug = self._data.get("slug", "") or slugify(self.title)
        self.short_description = self._data.get("short_description", "")
        self.description = self._data.get("description", "")
        self.price_inr = int(self._data.get("price_inr", 0))
        self.is_free = bool(self._data.get("is_free", self.price_inr == 0))
        self.badge_text = self._data.get("badge_text", "")
        self.test_ids = [str(tid) for tid in self._data.get("test_ids", [])]
        self.features = self._data.get("features", [])
        self.video_resources = self._data.get("video_resources", [])
        self.status = self._data.get("status", self.STATUS_PUBLISHED if self.is_free else self.STATUS_COMING_SOON)
        self.display_order = int(self._data.get("display_order", 0))
        self.created_at = self._data.get("created_at") or datetime.now(timezone.utc)
        self.updated_at = self._data.get("updated_at") or datetime.now(timezone.utc)

    @property
    def tests(self):
        if not self.test_ids:
            return []
        database = get_db()
        obj_ids = [_to_obj_id(tid) for tid in self.test_ids if _to_obj_id(tid)]
        cursor = database[TestDefinition.collection_name].find({"_id": {"$in": obj_ids}, "is_published": True})
        doc_map = {str(doc["_id"]): TestDefinition(doc) for doc in cursor}
        return [doc_map[tid] for tid in self.test_ids if tid in doc_map]

    @property
    def total_tests_count(self):
        return len(self.test_ids)

    @property
    def total_questions_count(self):
        """Accurately sums questions across unique tests without double counting."""
        ts = self.tests
        return sum(t.total_questions_count for t in ts)

    def save(self):
        database = get_db()
        self.updated_at = datetime.now(timezone.utc)
        data = {
            "title": self.title,
            "slug": self.slug,
            "short_description": self.short_description,
            "description": self.description,
            "price_inr": self.price_inr,
            "is_free": self.is_free,
            "badge_text": self.badge_text,
            "test_ids": self.test_ids,
            "features": self.features,
            "video_resources": self.video_resources,
            "status": self.status,
            "display_order": self.display_order,
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
    def get_by_id(cls, pack_id):
        database = get_db()
        obj_id = _to_obj_id(pack_id)
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
            cursor = cursor.sort("display_order", 1)
        if limit > 0:
            cursor = cursor.limit(limit)
        return [cls(doc) for doc in cursor]

    def delete(self):
        if not self._id:
            return False
        database = get_db()
        database[self.collection_name].delete_one({"_id": self._id})
        return True


class TestAttempt:
    collection_name = "test_series_attempts"

    STATUS_IN_PROGRESS = "in_progress"
    STATUS_COMPLETED = "completed"
    STATUS_CANCELLED = "cancelled"
    STATUS_TIMED_OUT = "timed_out"

    def __init__(self, data=None):
        self._data = data or {}
        self._id = self._data.get("_id")
        self.id = str(self._id) if self._id else ""
        self.user_id = str(self._data.get("user_id", ""))
        self.test_id = str(self._data.get("test_id", ""))
        self.test_title = self._data.get("test_title", "")
        self.test_slug = self._data.get("test_slug", "")
        self.status = self._data.get("status", self.STATUS_IN_PROGRESS)
        self.started_at = self._data.get("started_at") or datetime.now(timezone.utc)
        self.duration_minutes = int(self._data.get("duration_minutes", 30))
        self.deadline_at = self._data.get("deadline_at") or (self.started_at + timedelta(minutes=self.duration_minutes))
        self.submitted_at = self._data.get("submitted_at")
        self.time_taken_seconds = int(self._data.get("time_taken_seconds", 0))

        # Stored responses: question_id -> {"answer": ..., "marked_for_review": bool, "saved_at": ...}
        self.responses = self._data.get("responses", {}) or {}

        # Focus loss anti-cheating events
        self.focus_loss_events = self._data.get("focus_loss_events", []) or []
        self.warning_count = int(self._data.get("warning_count", len(self.focus_loss_events)))
        self.cancellation_reason = self._data.get("cancellation_reason", "")
        self.cancelled_at = self._data.get("cancelled_at")

        # Scoring & Results
        self.score = float(self._data.get("score", 0.0))
        self.max_score = float(self._data.get("max_score", 0.0))
        self.percentage = float(self._data.get("percentage", 0.0))
        self.is_passed = bool(self._data.get("is_passed", False))
        self.correct_count = int(self._data.get("correct_count", 0))
        self.incorrect_count = int(self._data.get("incorrect_count", 0))
        self.unanswered_count = int(self._data.get("unanswered_count", 0))
        self.accuracy_percentage = float(self._data.get("accuracy_percentage", 0.0))
        self.topic_breakdown = self._data.get("topic_breakdown", {})
        self.question_results = self._data.get("question_results", [])
        self.created_at = self._data.get("created_at") or self.started_at
        self.updated_at = self._data.get("updated_at") or datetime.now(timezone.utc)

    @property
    def remaining_seconds(self):
        """Server-authoritative calculation of remaining assessment time."""
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

    def add_focus_loss_event(self, event_type, reason="Focus loss or tab visibility changed."):
        """
        Records a focus-loss event with a 5-second cooldown debounce.
        Enforces 3 warnings and auto-cancels on the 4th qualifying violation.
        """
        now = datetime.now(timezone.utc)
        cooldown_sec = 5

        # Check debounce against latest recorded event
        if self.focus_loss_events:
            last_event = self.focus_loss_events[-1]
            last_time = last_event.get("timestamp")
            if isinstance(last_time, str):
                try:
                    last_time = datetime.fromisoformat(last_time)
                except Exception:
                    last_time = None
            if last_time:
                if last_time.tzinfo is None:
                    last_time = last_time.replace(tzinfo=timezone.utc)
                if (now - last_time).total_seconds() < cooldown_sec:
                    return False, self.warning_count, False

        self.warning_count += 1
        event_record = {
            "warning_number": self.warning_count,
            "event_type": event_type,
            "timestamp": now.isoformat(),
            "reason": reason
        }
        self.focus_loss_events.append(event_record)

        cancelled = False
        if self.warning_count >= 4:
            self.status = self.STATUS_CANCELLED
            self.cancelled_at = now
            self.cancellation_reason = f"Test cancelled because allowed focus-loss limit was exceeded ({self.warning_count} violations recorded)."
            cancelled = True

        self.save()
        return True, self.warning_count, cancelled

    def save(self):
        database = get_db()
        self.updated_at = datetime.now(timezone.utc)
        data = {
            "user_id": self.user_id,
            "test_id": self.test_id,
            "test_title": self.test_title,
            "test_slug": self.test_slug,
            "status": self.status,
            "started_at": self.started_at,
            "duration_minutes": self.duration_minutes,
            "deadline_at": self.deadline_at,
            "submitted_at": self.submitted_at,
            "time_taken_seconds": self.time_taken_seconds,
            "responses": self.responses,
            "focus_loss_events": self.focus_loss_events,
            "warning_count": self.warning_count,
            "cancellation_reason": self.cancellation_reason,
            "cancelled_at": self.cancelled_at,
            "score": self.score,
            "max_score": self.max_score,
            "percentage": self.percentage,
            "is_passed": self.is_passed,
            "correct_count": self.correct_count,
            "incorrect_count": self.incorrect_count,
            "unanswered_count": self.unanswered_count,
            "accuracy_percentage": self.accuracy_percentage,
            "topic_breakdown": self.topic_breakdown,
            "question_results": self.question_results,
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
    def get_by_id(cls, attempt_id):
        database = get_db()
        obj_id = _to_obj_id(attempt_id)
        if not obj_id:
            return None
        doc = database[cls.collection_name].find_one({"_id": obj_id})
        return cls(doc) if doc else None

    @classmethod
    def get_active_attempt(cls, user_id, test_id):
        database = get_db()
        doc = database[cls.collection_name].find_one({
            "user_id": str(user_id),
            "test_id": str(test_id),
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


class UserEntitlement:
    collection_name = "user_entitlements"

    def __init__(self, data=None):
        self._data = data or {}
        self._id = self._data.get("_id")
        self.id = str(self._id) if self._id else ""
        self.user_id = str(self._data.get("user_id", ""))
        self.pack_id = str(self._data.get("pack_id", ""))
        self.pack_slug = self._data.get("pack_slug", "")
        self.granted_at = self._data.get("granted_at") or datetime.now(timezone.utc)
        self.granted_by = self._data.get("granted_by", "system_free")
        self.notes = self._data.get("notes", "")
        self.is_active = bool(self._data.get("is_active", True))

    def save(self):
        database = get_db()
        data = {
            "user_id": self.user_id,
            "pack_id": self.pack_id,
            "pack_slug": self.pack_slug,
            "granted_at": self.granted_at,
            "granted_by": self.granted_by,
            "notes": self.notes,
            "is_active": self.is_active,
        }
        if self._id:
            database[self.collection_name].update_one({"_id": self._id}, {"$set": data})
        else:
            res = database[self.collection_name].insert_one(data)
            self._id = res.inserted_id
            self.id = str(self._id)
        return self

    @classmethod
    def has_access_to_pack(cls, user_id, pack_id_or_slug):
        database = get_db()
        doc = database[cls.collection_name].find_one({
            "user_id": str(user_id),
            "$or": [{"pack_id": str(pack_id_or_slug)}, {"pack_slug": str(pack_id_or_slug)}],
            "is_active": True
        })
        return bool(doc)

    @classmethod
    def has_access_to_test(cls, user, test_definition):
        """
        Determines if user has access to a test:
        1. If test is free -> True for all authenticated students.
        2. If user is admin -> True.
        3. If test belongs to a pack -> Check if user has entitlement for any pack containing it.
        """
        if not user or not user.is_authenticated:
            return False
        if test_definition.is_free:
            return True
        if getattr(user, "is_admin", False):
            return True
        for pid in test_definition.pack_ids:
            if cls.has_access_to_pack(user.id, pid):
                return True
        return False
