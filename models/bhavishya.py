"""
SkillRock — Bhavishya 1.0 Data Models
Defines BhavishyaSubject, BhavishyaProgress, BhavishyaMemory,
BhavishyaSubmission, BhavishyaSimulatorAttempt, BhavishyaCashback, and BhavishyaUsage.
Follows SkillRock MongoDB standards with strict server-side validation.
"""

from datetime import datetime, timezone, timedelta
from bson import ObjectId
from models.mongo import db, get_db, _to_obj_id, slugify


class BhavishyaPackage:
    id = "bhavishya-1-0"
    slug = "bhavishya-1-0"
    title = "Bhavishya 1.0 — Free Live & Masterclass Batch"
    short_description = "Live Interactive Lectures on Google Meet with Teachers (Python & English), Daily Practice Problems (DPP), Class Notes & 24/7 AI Doubt Solver. 100% Free for all students."
    duration = "8 Weeks (Live Batches)"
    level = "Zero to Placement (Beginner to Advanced)"
    price = 0.0
    original_price = 0.0
    currency = "INR"
    is_paid = False
    is_free = True
    cashback_enabled = False
    cashback_percentage = 0.0
    completion_deadline_days = 180

    def to_dict(self):
        return {
            "id": self.id,
            "slug": self.slug,
            "title": self.title,
            "price": self.price,
            "original_price": self.original_price,
            "duration": self.duration,
            "cashback_enabled": self.cashback_enabled,
            "cashback_percentage": self.cashback_percentage,
        }


class BhavishyaSubject:
    collection_name = "bhavishya_subjects"

    CATEGORY_TECHNICAL = "Technical Skills"
    CATEGORY_PLACEMENT = "Placement Preparation"
    CATEGORY_PROJECTS = "Practical Projects"

    def __init__(self, data=None):
        self._data = data or {}
        self._id = self._data.get("_id")
        self.id = str(self._id) if self._id else ""
        self.slug = self._data.get("slug", "")
        self.title = self._data.get("title", "")
        self.category = self._data.get("category", self.CATEGORY_TECHNICAL)
        self.order = int(self._data.get("order", 1))
        self.short_description = self._data.get("short_description", "")
        self.full_description = self._data.get("full_description", "")
        self.estimated_hours = int(self._data.get("estimated_hours", 15))
        self.difficulty = self._data.get("difficulty", "Beginner to Intermediate")
        self.icon = self._data.get("icon", "book-open")
        self.color_accent = self._data.get("color_accent", "#38BDF8")
        self.prerequisites = self._data.get("prerequisites", [])
        self.chapters = self._data.get("chapters", [])
        self.is_published = bool(self._data.get("is_published", True))
        self.created_at = self._data.get("created_at") or datetime.now(timezone.utc)
        self.updated_at = self._data.get("updated_at") or datetime.now(timezone.utc)

    @property
    def total_lessons_count(self):
        count = 0
        for ch in self.chapters:
            count += len(ch.get("lessons", []))
        return count

    def get_lesson_by_id(self, lesson_id):
        for ch in self.chapters:
            for l in ch.get("lessons", []):
                if str(l.get("id")) == str(lesson_id):
                    return l, ch
        return None, None

    def save(self):
        db = get_db()
        self.updated_at = datetime.now(timezone.utc)
        doc = {
            "slug": self.slug,
            "title": self.title,
            "category": self.category,
            "order": self.order,
            "short_description": self.short_description,
            "full_description": self.full_description,
            "estimated_hours": self.estimated_hours,
            "difficulty": self.difficulty,
            "icon": self.icon,
            "color_accent": self.color_accent,
            "prerequisites": self.prerequisites,
            "chapters": self.chapters,
            "is_published": self.is_published,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
        if self._id:
            db[self.collection_name].update_one({"_id": self._id}, {"$set": doc})
        else:
            res = db[self.collection_name].insert_one(doc)
            self._id = res.inserted_id
            self.id = str(self._id)
        return self

    @classmethod
    def get_by_slug(cls, slug):
        if not slug:
            return None
        db = get_db()
        doc = db[cls.collection_name].find_one({"slug": str(slug).strip()})
        return cls(doc) if doc else None

    @classmethod
    def get_by_id(cls, item_id):
        if not item_id:
            return None
        db = get_db()
        obj_id = _to_obj_id(item_id)
        doc = db[cls.collection_name].find_one({"$or": [{"_id": obj_id}, {"_id": str(item_id)}, {"slug": str(item_id)}]})
        return cls(doc) if doc else None

    @classmethod
    def get_all(cls, published_only=False):
        db = get_db()
        query = {"is_published": True} if published_only else {}
        cursor = db[cls.collection_name].find(query).sort("order", 1)
        return [cls(doc) for doc in cursor]

    @classmethod
    def get_by_category(cls, category, published_only=True):
        db = get_db()
        query = {"category": category}
        if published_only:
            query["is_published"] = True
        cursor = db[cls.collection_name].find(query).sort("order", 1)
        return [cls(doc) for doc in cursor]


class BhavishyaProgress:
    collection_name = "bhavishya_progress"

    def __init__(self, data=None):
        self._data = data or {}
        self._id = self._data.get("_id")
        self.id = str(self._id) if self._id else ""
        self.user_id = str(self._data.get("user_id", ""))
        self.completed_lesson_ids = set(self._data.get("completed_lesson_ids", []))
        self.completed_chapter_ids = set(self._data.get("completed_chapter_ids", []))
        self.completed_subject_slugs = set(self._data.get("completed_subject_slugs", []))
        self.current_week = int(self._data.get("current_week", 1))
        self.active_streak_days = int(self._data.get("active_streak_days", 1))
        self.last_learned_at = self._data.get("last_learned_at") or datetime.now(timezone.utc)
        self.last_subject_slug = self._data.get("last_subject_slug", "python-programming")
        self.last_lesson_id = self._data.get("last_lesson_id", "")
        self.placement_readiness_score = float(self._data.get("placement_readiness_score", 0.0))
        self.started_at = self._data.get("started_at") or datetime.now(timezone.utc)
        self.updated_at = self._data.get("updated_at") or datetime.now(timezone.utc)

    def is_lesson_completed(self, lesson_id):
        return str(lesson_id) in self.completed_lesson_ids

    def toggle_lesson(self, lesson_id, subject_slug=None):
        s_id = str(lesson_id)
        if s_id in self.completed_lesson_ids:
            self.completed_lesson_ids.remove(s_id)
            completed = False
        else:
            self.completed_lesson_ids.add(s_id)
            completed = True
        if subject_slug:
            self.last_subject_slug = subject_slug
            self.last_lesson_id = s_id
        self.last_learned_at = datetime.now(timezone.utc)
        self.save()
        return completed

    def calculate_subject_progress(self, subject):
        if not subject or not subject.total_lessons_count:
            return 0
        subject_lesson_ids = set()
        for ch in subject.chapters:
            for l in ch.get("lessons", []):
                subject_lesson_ids.add(str(l.get("id")))
        if not subject_lesson_ids:
            return 0
        done = len(self.completed_lesson_ids.intersection(subject_lesson_ids))
        pct = (done / float(len(subject_lesson_ids))) * 100.0
        return min(100, round(pct, 1))

    def calculate_overall_percentage(self, total_all_lessons):
        if not total_all_lessons:
            return 0
        pct = (len(self.completed_lesson_ids) / float(total_all_lessons)) * 100.0
        return min(100, round(pct, 1))

    def save(self):
        db = get_db()
        self.updated_at = datetime.now(timezone.utc)
        doc = {
            "user_id": self.user_id,
            "completed_lesson_ids": list(self.completed_lesson_ids),
            "completed_chapter_ids": list(self.completed_chapter_ids),
            "completed_subject_slugs": list(self.completed_subject_slugs),
            "current_week": self.current_week,
            "active_streak_days": self.active_streak_days,
            "last_learned_at": self.last_learned_at,
            "last_subject_slug": self.last_subject_slug,
            "last_lesson_id": self.last_lesson_id,
            "placement_readiness_score": self.placement_readiness_score,
            "started_at": self.started_at,
            "updated_at": self.updated_at,
        }
        res = db[self.collection_name].update_one(
            {"user_id": self.user_id},
            {"$set": doc},
            upsert=True
        )
        if not self._id and res.upserted_id:
            self._id = res.upserted_id
            self.id = str(self._id)
        return self

    @classmethod
    def get_or_create_for_user(cls, user_id):
        if not user_id:
            return None
        db = get_db()
        doc = db[cls.collection_name].find_one({"user_id": str(user_id)})
        if doc:
            return cls(doc)
        new_prog = cls({"user_id": str(user_id)})
        new_prog.save()
        return new_prog


class BhavishyaMemory:
    collection_name = "bhavishya_memory"

    def __init__(self, data=None):
        self._data = data or {}
        self._id = self._data.get("_id")
        self.id = str(self._id) if self._id else ""
        self.user_id = str(self._data.get("user_id", ""))
        self.subject_slug = self._data.get("subject_slug", "")
        self.weak_concepts = self._data.get("weak_concepts", [])  # list of strings
        self.frequent_errors = self._data.get("frequent_errors", [])  # list of error notes
        self.last_topic_discussed = self._data.get("last_topic_discussed", "")
        self.learning_style_notes = self._data.get("learning_style_notes", "")
        self.updated_at = self._data.get("updated_at") or datetime.now(timezone.utc)

    def add_weak_concept(self, concept):
        clean = str(concept).strip()
        if clean and clean not in self.weak_concepts:
            self.weak_concepts.append(clean)
            if len(self.weak_concepts) > 10:
                self.weak_concepts.pop(0)
            self.save()

    def remove_weak_concept(self, concept):
        clean = str(concept).strip()
        if clean in self.weak_concepts:
            self.weak_concepts.remove(clean)
            self.save()

    def save(self):
        db = get_db()
        self.updated_at = datetime.now(timezone.utc)
        doc = {
            "user_id": self.user_id,
            "subject_slug": self.subject_slug,
            "weak_concepts": self.weak_concepts,
            "frequent_errors": self.frequent_errors,
            "last_topic_discussed": self.last_topic_discussed,
            "learning_style_notes": self.learning_style_notes,
            "updated_at": self.updated_at,
        }
        res = db[self.collection_name].update_one(
            {"user_id": self.user_id, "subject_slug": self.subject_slug},
            {"$set": doc},
            upsert=True
        )
        if not self._id and res.upserted_id:
            self._id = res.upserted_id
            self.id = str(self._id)
        return self

    @classmethod
    def get_for_user_and_subject(cls, user_id, subject_slug):
        db = get_db()
        doc = db[cls.collection_name].find_one({"user_id": str(user_id), "subject_slug": str(subject_slug)})
        if doc:
            return cls(doc)
        mem = cls({"user_id": str(user_id), "subject_slug": str(subject_slug)})
        mem.save()
        return mem


class BhavishyaSubmission:
    collection_name = "bhavishya_submissions"

    STATUS_SUBMITTED = "submitted"
    STATUS_PASSED = "passed"
    STATUS_NEEDS_IMPROVEMENT = "needs_improvement"

    def __init__(self, data=None):
        self._data = data or {}
        self._id = self._data.get("_id")
        self.id = str(self._id) if self._id else ""
        self.user_id = str(self._data.get("user_id", ""))
        self.subject_slug = self._data.get("subject_slug", "")
        self.item_id = self._data.get("item_id", "")  # lesson_id or project_id
        self.item_type = self._data.get("item_type", "coding_lab")  # coding_lab, project, capstone
        self.submitted_code = self._data.get("submitted_code", "")
        self.github_url = self._data.get("github_url", "")
        self.deployment_url = self._data.get("deployment_url", "")
        self.notes = self._data.get("notes", "")
        self.status = self._data.get("status", self.STATUS_SUBMITTED)
        self.score = float(self._data.get("score", 0.0))
        self.evaluation_feedback = self._data.get("evaluation_feedback", "")
        self.submitted_at = self._data.get("submitted_at") or datetime.now(timezone.utc)
        self.reviewed_at = self._data.get("reviewed_at")

    def save(self):
        db = get_db()
        doc = {
            "user_id": self.user_id,
            "subject_slug": self.subject_slug,
            "item_id": self.item_id,
            "item_type": self.item_type,
            "submitted_code": self.submitted_code,
            "github_url": self.github_url,
            "deployment_url": self.deployment_url,
            "notes": self.notes,
            "status": self.status,
            "score": self.score,
            "evaluation_feedback": self.evaluation_feedback,
            "submitted_at": self.submitted_at,
            "reviewed_at": self.reviewed_at,
        }
        res = db[self.collection_name].update_one(
            {"user_id": self.user_id, "subject_slug": self.subject_slug, "item_id": self.item_id},
            {"$set": doc},
            upsert=True
        )
        if not self._id and res.upserted_id:
            self._id = res.upserted_id
            self.id = str(self._id)
        return self

    @classmethod
    def get_user_submission(cls, user_id, subject_slug, item_id):
        db = get_db()
        doc = db[cls.collection_name].find_one({
            "user_id": str(user_id),
            "subject_slug": str(subject_slug),
            "item_id": str(item_id)
        })
        return cls(doc) if doc else None


class BhavishyaSimulatorAttempt:
    collection_name = "bhavishya_simulator_attempts"

    def __init__(self, data=None):
        self._data = data or {}
        self._id = self._data.get("_id")
        self.id = str(self._id) if self._id else ""
        self.user_id = str(self._data.get("user_id", ""))
        self.round_scores = self._data.get("round_scores", {
            "aptitude": 0,
            "coding": 0,
            "gd": 0,
            "technical": 0,
            "hr": 0
        })
        self.overall_score = float(self._data.get("overall_score", 0.0))
        self.strengths = self._data.get("strengths", [])
        self.weaknesses = self._data.get("weaknesses", [])
        self.recommendations = self._data.get("recommendations", [])
        self.readiness_status = self._data.get("readiness_status", "Developing")  # Developing, Placement Ready, Advanced
        self.created_at = self._data.get("created_at") or datetime.now(timezone.utc)

    def save(self):
        db = get_db()
        doc = {
            "user_id": self.user_id,
            "round_scores": self.round_scores,
            "overall_score": self.overall_score,
            "strengths": self.strengths,
            "weaknesses": self.weaknesses,
            "recommendations": self.recommendations,
            "readiness_status": self.readiness_status,
            "created_at": self.created_at,
        }
        res = db[self.collection_name].insert_one(doc)
        self._id = res.inserted_id
        self.id = str(self._id)
        return self

    @classmethod
    def get_latest_for_user(cls, user_id):
        db = get_db()
        doc = db[cls.collection_name].find_one({"user_id": str(user_id)}, sort=[("created_at", -1)])
        return cls(doc) if doc else None


class BhavishyaCashback:
    collection_name = "bhavishya_cashback"

    STATUS_NOT_ELIGIBLE = "not_eligible"
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_REQUIREMENTS_COMPLETED = "requirements_completed"
    STATUS_UNDER_VERIFICATION = "under_verification"
    STATUS_APPROVED = "approved"
    STATUS_PROCESSING = "processing"
    STATUS_PAID = "paid"
    STATUS_REJECTED = "rejected"

    def __init__(self, data=None):
        self._data = data or {}
        self._id = self._data.get("_id")
        self.id = str(self._id) if self._id else ""
        self.user_id = str(self._data.get("user_id", ""))
        self.user_name = self._data.get("user_name", "")
        self.user_email = self._data.get("user_email", "")
        self.original_payment_id = self._data.get("original_payment_id", "")
        self.original_amount = float(self._data.get("original_amount", 299.0))
        self.cashback_amount = float(self._data.get("cashback_amount", 149.50))
        self.status = self._data.get("status", self.STATUS_NOT_ELIGIBLE)
        self.upi_id = self._data.get("upi_id", "")
        self.admin_notes = self._data.get("admin_notes", "")
        self.rejection_reason = self._data.get("rejection_reason", "")
        self.applied_at = self._data.get("applied_at")
        self.approved_at = self._data.get("approved_at")
        self.paid_at = self._data.get("paid_at")
        self.created_at = self._data.get("created_at") or datetime.now(timezone.utc)

    def save(self):
        db = get_db()
        doc = {
            "user_id": self.user_id,
            "user_name": self.user_name,
            "user_email": self.user_email,
            "original_payment_id": self.original_payment_id,
            "original_amount": self.original_amount,
            "cashback_amount": self.cashback_amount,
            "status": self.status,
            "upi_id": self.upi_id,
            "admin_notes": self.admin_notes,
            "rejection_reason": self.rejection_reason,
            "applied_at": self.applied_at,
            "approved_at": self.approved_at,
            "paid_at": self.paid_at,
            "created_at": self.created_at,
        }
        res = db[self.collection_name].update_one(
            {"user_id": self.user_id},
            {"$set": doc},
            upsert=True
        )
        if not self._id and res.upserted_id:
            self._id = res.upserted_id
            self.id = str(self._id)
        return self

    @classmethod
    def get_by_user(cls, user_id):
        db = get_db()
        doc = db[cls.collection_name].find_one({"user_id": str(user_id)})
        return cls(doc) if doc else None

    @classmethod
    def get_all(cls, status=None):
        db = get_db()
        query = {"status": status} if status else {}
        cursor = db[cls.collection_name].find(query).sort("applied_at", -1)
        return [cls(doc) for doc in cursor]


class BhavishyaUsage:
    collection_name = "bhavishya_usage"

    # Default monthly Fair-Usage Limits
    MAX_VOICE_MINUTES_MONTHLY = 300
    MAX_TEXT_QUERIES_MONTHLY = 1000
    MAX_CODE_RUNS_WEEKLY = 150

    def __init__(self, data=None):
        self._data = data or {}
        self._id = self._data.get("_id")
        self.id = str(self._id) if self._id else ""
        self.user_id = str(self._data.get("user_id", ""))
        self.month_key = self._data.get("month_key") or datetime.now(timezone.utc).strftime("%Y-%m")
        self.voice_minutes = float(self._data.get("voice_minutes", 0.0))
        self.text_queries = int(self._data.get("text_queries", 0))
        self.code_runs = int(self._data.get("code_runs", 0))
        self.updated_at = self._data.get("updated_at") or datetime.now(timezone.utc)

    def record_interaction(self, voice_delta_minutes=0.0, text_delta=0, code_delta=0):
        self.voice_minutes += float(voice_delta_minutes)
        self.text_queries += int(text_delta)
        self.code_runs += int(code_delta)
        self.save()

    def check_limits(self):
        """Returns tuple (can_use_voice: bool, can_use_text: bool, can_run_code: bool)"""
        can_v = self.voice_minutes < self.MAX_VOICE_MINUTES_MONTHLY
        can_t = self.text_queries < self.MAX_TEXT_QUERIES_MONTHLY
        can_c = self.code_runs < self.MAX_CODE_RUNS_WEEKLY
        return can_v, can_t, can_c

    def save(self):
        db = get_db()
        self.updated_at = datetime.now(timezone.utc)
        doc = {
            "user_id": self.user_id,
            "month_key": self.month_key,
            "voice_minutes": self.voice_minutes,
            "text_queries": self.text_queries,
            "code_runs": self.code_runs,
            "updated_at": self.updated_at,
        }
        res = db[self.collection_name].update_one(
            {"user_id": self.user_id, "month_key": self.month_key},
            {"$set": doc},
            upsert=True
        )
        if not self._id and res.upserted_id:
            self._id = res.upserted_id
            self.id = str(self._id)
        return self

    @classmethod
    def get_or_create(cls, user_id):
        m_key = datetime.now(timezone.utc).strftime("%Y-%m")
        db = get_db()
        doc = db[cls.collection_name].find_one({"user_id": str(user_id), "month_key": m_key})
        if doc:
            return cls(doc)
        usage = cls({"user_id": str(user_id), "month_key": m_key})
        usage.save()
        return usage


# ==============================================================================
# 8. Bhavishya 1.0 — Physics Wallah-Style Live Batch & Live Lectures
# ==============================================================================

class BhavishyaBatchConfig:
    collection_name = "bhavishya_batch_config"
    batch_id = "bhavishya-1-0"

    def __init__(self, data=None):
        self._data = data or {}
        self._id = self._data.get("_id")
        self.id = str(self._id) if self._id else "bhavishya-1-0"
        self.batch_id = self._data.get("batch_id", "bhavishya-1-0")
        self.title = self._data.get("title", "Bhavishya 1.0 — Python Master Live Batch")
        self.tagline = self._data.get("tagline", "Interactive Live Lectures on Google Meet with Teacher, Daily Practice Problems (DPP), Handwritten Notes, and 24/7 AI Doubt Solving")
        self.teacher_name = self._data.get("teacher_name", "Tanishk Pal")
        self.teacher_title = self._data.get("teacher_title", "Lead Python Educator & Software Architect")
        self.teacher_bio = self._data.get("teacher_bio", "Passionate about making programming intuitive, crystal clear, and placement-focused just like Physics Wallah live classes.")
        self.global_meet_url = self._data.get("global_meet_url", "https://meet.google.com/new")
        self.announcement = self._data.get("announcement", "🚀 Welcome to Bhavishya 1.0 Live Batch! Live classes are conducted on Google Meet. Join 5 minutes before scheduled time with VS Code ready!")
        self.announcement_updated_at = self._data.get("announcement_updated_at") or datetime.now(timezone.utc)
        self.whatsapp_url = self._data.get("whatsapp_url", "https://chat.whatsapp.com/SkillRockPython")
        self.telegram_url = self._data.get("telegram_url", "https://t.me/SkillRockCampus")
        self.total_lectures = int(self._data.get("total_lectures", 16))
        self.price = float(self._data.get("price", 0.0))
        self.original_price = float(self._data.get("original_price", 0.0))

    def save(self):
        db = get_db()
        doc = {
            "batch_id": self.batch_id,
            "title": self.title,
            "tagline": self.tagline,
            "teacher_name": self.teacher_name,
            "teacher_title": self.teacher_title,
            "teacher_bio": self.teacher_bio,
            "global_meet_url": self.global_meet_url,
            "announcement": self.announcement,
            "announcement_updated_at": datetime.now(timezone.utc),
            "whatsapp_url": self.whatsapp_url,
            "telegram_url": self.telegram_url,
            "total_lectures": self.total_lectures,
            "price": self.price,
            "original_price": self.original_price,
            "updated_at": datetime.now(timezone.utc),
        }
        res = db[self.collection_name].update_one({"batch_id": self.batch_id}, {"$set": doc}, upsert=True)
        if not self._id and res.upserted_id:
            self._id = res.upserted_id
            self.id = str(self._id)
        return self

    @classmethod
    def get_config(cls, batch_id="bhavishya-1-0"):
        db = get_db()
        doc = db[cls.collection_name].find_one({"batch_id": batch_id})
        if doc:
            return cls(doc)
        config = cls({"batch_id": batch_id})
        config.save()
        return config


class BhavishyaLiveLecture:
    collection_name = "bhavishya_live_lectures"

    STATUS_SCHEDULED = "scheduled"
    STATUS_LIVE = "live"
    STATUS_COMPLETED = "completed"

    def __init__(self, data=None):
        self._data = data or {}
        self._id = self._data.get("_id")
        self.id = str(self._id) if self._id else str(self._data.get("lecture_id", ""))
        self.lecture_id = str(self._data.get("lecture_id", self.id))
        self.batch_id = self._data.get("batch_id", "bhavishya-1-0")
        self.subject_slug = str(self._data.get("subject_slug", "python")).strip().lower()
        self.module_number = int(self._data.get("module_number", 1))
        self.module_name = self._data.get("module_name", "Module 1: Python Essentials")
        self.lecture_number = int(self._data.get("lecture_number", 1))
        self.title = self._data.get("title", "")
        self.description = self._data.get("description", "")
        self.teacher_name = self._data.get("teacher_name", "Tanishk Pal")
        self.teacher_title = self._data.get("teacher_title", "")
        self.teacher_avatar = self._data.get("teacher_avatar", "")
        self.scheduled_at = self._data.get("scheduled_at", "")
        self.scheduled_display = self._data.get("scheduled_display", "")
        self.duration_minutes = int(self._data.get("duration_minutes", 90))
        self.status = self._data.get("status", self.STATUS_SCHEDULED)
        self.google_meet_url = self._data.get("google_meet_url", "")
        self.recording_url = self._data.get("recording_url", "")
        self.notes_url = self._data.get("notes_url", "")
        self.notes_content = self._data.get("notes_content", "")
        self.starter_code = self._data.get("starter_code", "# Python Live Code Playground\nprint('Hello SkillRock Bhavishya Live!')\n")
        self.dpp_list = self._data.get("dpp_list", [])
        self.order = int(self._data.get("order", self.lecture_number))
        self.created_at = self._data.get("created_at") or datetime.now(timezone.utc)
        self.updated_at = self._data.get("updated_at") or datetime.now(timezone.utc)

    @property
    def is_live(self):
        return self.status == self.STATUS_LIVE

    @property
    def is_completed(self):
        return self.status == self.STATUS_COMPLETED

    @property
    def is_scheduled(self):
        return self.status == self.STATUS_SCHEDULED

    @property
    def active_meet_url(self):
        if self.google_meet_url and self.google_meet_url.strip():
            return self.google_meet_url.strip()
        config = BhavishyaBatchConfig.get_config(self.batch_id)
        return config.global_meet_url

    def save(self):
        db = get_db()
        self.updated_at = datetime.now(timezone.utc)
        doc = {
            "lecture_id": self.lecture_id,
            "batch_id": self.batch_id,
            "subject_slug": self.subject_slug,
            "module_number": self.module_number,
            "module_name": self.module_name,
            "lecture_number": self.lecture_number,
            "order": self.order,
            "title": self.title,
            "description": self.description,
            "teacher_name": self.teacher_name,
            "teacher_title": self.teacher_title,
            "teacher_avatar": self.teacher_avatar,
            "scheduled_at": self.scheduled_at,
            "scheduled_display": self.scheduled_display,
            "duration_minutes": self.duration_minutes,
            "status": self.status,
            "google_meet_url": self.google_meet_url,
            "recording_url": self.recording_url,
            "notes_url": self.notes_url,
            "notes_content": self.notes_content,
            "starter_code": self.starter_code,
            "dpp_list": self.dpp_list,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
        res = db[self.collection_name].update_one(
            {"lecture_id": self.lecture_id},
            {"$set": doc},
            upsert=True
        )
        if not self._id and res.upserted_id:
            self._id = res.upserted_id
            self.id = str(self._id)
        return self

    @classmethod
    def get_by_id(cls, lecture_id):
        if not lecture_id:
            return None
        db = get_db()
        doc = db[cls.collection_name].find_one({
            "$or": [{"lecture_id": str(lecture_id)}, {"_id": _to_obj_id(lecture_id)}]
        })
        return cls(doc) if doc else None

    @classmethod
    def get_all(cls, batch_id="bhavishya-1-0", subject_slug=None):
        db = get_db()
        q = {"batch_id": batch_id}
        if subject_slug:
            q["subject_slug"] = str(subject_slug).strip().lower()
        cursor = db[cls.collection_name].find(q).sort("order", 1)
        return [cls(doc) for doc in cursor]

    @classmethod
    def get_active_live(cls, batch_id="bhavishya-1-0", subject_slug=None):
        db = get_db()
        q = {"batch_id": batch_id, "status": cls.STATUS_LIVE}
        if subject_slug:
            q["subject_slug"] = str(subject_slug).strip().lower()
        doc = db[cls.collection_name].find_one(q)
        return cls(doc) if doc else None

    @classmethod
    def get_next_scheduled(cls, batch_id="bhavishya-1-0", subject_slug=None):
        db = get_db()
        q = {"batch_id": batch_id, "status": cls.STATUS_SCHEDULED}
        if subject_slug:
            q["subject_slug"] = str(subject_slug).strip().lower()
        doc = db[cls.collection_name].find_one(q, sort=[("order", 1)])
        return cls(doc) if doc else None

    @classmethod
    def get_modules_grouped(cls, batch_id="bhavishya-1-0", subject_slug=None):
        lectures = cls.get_all(batch_id, subject_slug=subject_slug)
        modules = {}
        for l in lectures:
            m_key = l.module_number
            if m_key not in modules:
                modules[m_key] = {
                    "module_number": l.module_number,
                    "module_name": l.module_name,
                    "lectures": []
                }
            modules[m_key]["lectures"].append(l)
        return sorted(modules.values(), key=lambda x: x["module_number"])
        return [modules[k] for k in sorted(modules.keys())]
