"""
SkillRock — Career Roadmap Platform & 50% Completion Cashback Models
Defines RoadmapPackage, RoadmapProgress, RoadmapSubmission, and RoadmapCashback
collections adhering to SkillRock MongoDB conventions and strict server-side validation.
"""

from datetime import datetime, timezone, timedelta
from bson import ObjectId
from models.mongo import db, get_db, _to_obj_id, slugify


class RoadmapPackage:
    collection_name = "roadmap_packages"

    def __init__(self, data=None):
        self._data = data or {}
        self._id = self._data.get("_id")
        self.id = str(self._id) if self._id else ""
        self.slug = self._data.get("slug", "")
        self.title = self._data.get("title", "")
        self.short_description = self._data.get("short_description", "")
        self.full_description = self._data.get("full_description", "")
        self.duration = self._data.get("duration", "20 Weeks")
        self.level = self._data.get("level", "Beginner to Intermediate")
        self.language = self._data.get("language", "Hinglish & English")
        self.tech_stack = self._data.get("tech_stack", [])
        self.career_outcomes = self._data.get("career_outcomes", [])
        self.phases = self._data.get("phases", [])  # List of 5 phases
        self.projects = self._data.get("projects", [])  # Phase projects
        self.capstone = self._data.get("capstone", {})  # Final Capstone Project
        self.price = float(self._data.get("price", 999.0))
        self.original_price = float(self._data.get("original_price", 2999.0))
        self.currency = self._data.get("currency", "INR")
        self.cashback_enabled = bool(self._data.get("cashback_enabled", True))
        self.cashback_percentage = float(self._data.get("cashback_percentage", 50.0))
        self.completion_deadline_days = int(self._data.get("completion_deadline_days", 180))  # e.g. ~25 weeks for 20-week program
        self.is_published = bool(self._data.get("is_published", True))
        self.thumbnail_url = self._data.get("thumbnail_url", "")
        self.created_at = self._data.get("created_at") or datetime.now(timezone.utc)
        self.updated_at = self._data.get("updated_at") or datetime.now(timezone.utc)

    @property
    def is_paid(self):
        return self.price > 0

    @property
    def total_weeks(self):
        count = 0
        for p in self.phases:
            count += len(p.get("weeks", []))
        return count or 20

    @property
    def total_lessons_count(self):
        count = 0
        for p in self.phases:
            for w in p.get("weeks", []):
                count += len(w.get("lessons", []))
        return count

    def get_week_by_number(self, week_num):
        for p in self.phases:
            for w in p.get("weeks", []):
                if int(w.get("week_number", 0)) == int(week_num):
                    return w, p
        return None, None

    def get_lesson_by_id(self, lesson_id):
        for p in self.phases:
            for w in p.get("weeks", []):
                for l in w.get("lessons", []):
                    if l.get("id") == str(lesson_id):
                        return l, w, p
        return None, None, None

    def get_project_by_id(self, project_id):
        if self.capstone and self.capstone.get("id") == str(project_id):
            return self.capstone, True
        for p in self.projects:
            if p.get("id") == str(project_id):
                return p, False
        return None, False

    def save(self):
        db = get_db()
        self.updated_at = datetime.now(timezone.utc)
        doc = {
            "slug": self.slug,
            "title": self.title,
            "short_description": self.short_description,
            "full_description": self.full_description,
            "duration": self.duration,
            "level": self.level,
            "language": self.language,
            "tech_stack": self.tech_stack,
            "career_outcomes": self.career_outcomes,
            "phases": self.phases,
            "projects": self.projects,
            "capstone": self.capstone,
            "price": self.price,
            "original_price": self.original_price,
            "currency": self.currency,
            "cashback_enabled": self.cashback_enabled,
            "cashback_percentage": self.cashback_percentage,
            "completion_deadline_days": self.completion_deadline_days,
            "is_published": self.is_published,
            "thumbnail_url": self.thumbnail_url,
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
        cursor = db[cls.collection_name].find(query).sort("created_at", 1)
        return [cls(doc) for doc in cursor]


class RoadmapProgress:
    collection_name = "roadmap_progress"

    def __init__(self, data=None):
        self._data = data or {}
        self._id = self._data.get("_id")
        self.id = str(self._id) if self._id else ""
        self.user_id = str(self._data.get("user_id", ""))
        self.roadmap_slug = self._data.get("roadmap_slug", "")
        self.payment_id = self._data.get("payment_id", "")
        self.amount_paid = float(self._data.get("amount_paid", 0.0))
        self.cashback_percentage_enrolled = float(self._data.get("cashback_percentage_enrolled", 50.0))
        self.completed_lesson_ids = set(self._data.get("completed_lesson_ids", []))
        self.completed_week_ids = set(self._data.get("completed_week_ids", []))
        self.completed_assignment_ids = set(self._data.get("completed_assignment_ids", []))
        self.completed_quiz_ids = set(self._data.get("completed_quiz_ids", []))
        self.current_week = int(self._data.get("current_week", 1))
        self.started_at = self._data.get("started_at") or datetime.now(timezone.utc)
        self.updated_at = self._data.get("updated_at") or datetime.now(timezone.utc)
        self.completion_status = self._data.get("completion_status", "in_progress")  # in_progress, completed
        self.completed_at = self._data.get("completed_at")

    def is_lesson_completed(self, lesson_id):
        return str(lesson_id) in self.completed_lesson_ids

    def toggle_lesson(self, lesson_id):
        """Server-side safe toggle for lesson completion."""
        s_id = str(lesson_id)
        if s_id in self.completed_lesson_ids:
            self.completed_lesson_ids.remove(s_id)
            completed = False
        else:
            self.completed_lesson_ids.add(s_id)
            completed = True
        self.save()
        return completed

    def calculate_completion_percentage(self, total_lessons):
        if not total_lessons:
            return 0
        pct = (len(self.completed_lesson_ids) / float(total_lessons)) * 100.0
        return min(100, round(pct, 1))

    def save(self):
        db = get_db()
        self.updated_at = datetime.now(timezone.utc)
        doc = {
            "user_id": self.user_id,
            "roadmap_slug": self.roadmap_slug,
            "payment_id": self.payment_id,
            "amount_paid": self.amount_paid,
            "cashback_percentage_enrolled": self.cashback_percentage_enrolled,
            "completed_lesson_ids": list(self.completed_lesson_ids),
            "completed_week_ids": list(self.completed_week_ids),
            "completed_assignment_ids": list(self.completed_assignment_ids),
            "completed_quiz_ids": list(self.completed_quiz_ids),
            "current_week": self.current_week,
            "started_at": self.started_at,
            "updated_at": self.updated_at,
            "completion_status": self.completion_status,
            "completed_at": self.completed_at,
        }
        res = db[self.collection_name].update_one(
            {"user_id": self.user_id, "roadmap_slug": self.roadmap_slug},
            {"$set": doc},
            upsert=True
        )
        if not self._id and res.upserted_id:
            self._id = res.upserted_id
            self.id = str(self._id)
        return self

    @classmethod
    def get_user_progress(cls, user_id, roadmap_slug):
        if not user_id or not roadmap_slug:
            return None
        db = get_db()
        doc = db[cls.collection_name].find_one({"user_id": str(user_id), "roadmap_slug": str(roadmap_slug)})
        return cls(doc) if doc else None


class RoadmapSubmission:
    collection_name = "roadmap_submissions"

    STATUS_PENDING = "pending_review"
    STATUS_APPROVED = "approved"
    STATUS_CHANGES = "changes_requested"

    def __init__(self, data=None):
        self._data = data or {}
        self._id = self._data.get("_id")
        self.id = str(self._id) if self._id else ""
        self.user_id = str(self._data.get("user_id", ""))
        self.user_name = self._data.get("user_name", "")
        self.user_email = self._data.get("user_email", "")
        self.roadmap_slug = self._data.get("roadmap_slug", "")
        self.project_id = str(self._data.get("project_id", ""))
        self.project_title = self._data.get("project_title", "")
        self.is_capstone = bool(self._data.get("is_capstone", False))
        self.github_url = self._data.get("github_url", "")
        self.deployment_url = self._data.get("deployment_url", "")
        self.notes = self._data.get("notes", "")
        self.status = self._data.get("status", self.STATUS_PENDING)
        self.score = self._data.get("score")  # float 0-100
        self.rubric_scores = self._data.get("rubric_scores", {})  # {"criterion": score}
        self.admin_feedback = self._data.get("admin_feedback", "")
        self.submitted_at = self._data.get("submitted_at") or datetime.now(timezone.utc)
        self.reviewed_at = self._data.get("reviewed_at")
        self.reviewed_by = self._data.get("reviewed_by")

    def save(self):
        db = get_db()
        doc = {
            "user_id": self.user_id,
            "user_name": self.user_name,
            "user_email": self.user_email,
            "roadmap_slug": self.roadmap_slug,
            "project_id": self.project_id,
            "project_title": self.project_title,
            "is_capstone": self.is_capstone,
            "github_url": self.github_url,
            "deployment_url": self.deployment_url,
            "notes": self.notes,
            "status": self.status,
            "score": self.score,
            "rubric_scores": self.rubric_scores,
            "admin_feedback": self.admin_feedback,
            "submitted_at": self.submitted_at,
            "reviewed_at": self.reviewed_at,
            "reviewed_by": self.reviewed_by,
        }
        res = db[self.collection_name].update_one(
            {"user_id": self.user_id, "roadmap_slug": self.roadmap_slug, "project_id": self.project_id},
            {"$set": doc},
            upsert=True
        )
        if not self._id and res.upserted_id:
            self._id = res.upserted_id
            self.id = str(self._id)
        return self

    @classmethod
    def get_by_user_and_project(cls, user_id, roadmap_slug, project_id):
        db = get_db()
        doc = db[cls.collection_name].find_one({
            "user_id": str(user_id),
            "roadmap_slug": str(roadmap_slug),
            "project_id": str(project_id)
        })
        return cls(doc) if doc else None

    @classmethod
    def get_by_id(cls, sub_id):
        db = get_db()
        obj_id = _to_obj_id(sub_id)
        doc = db[cls.collection_name].find_one({"$or": [{"_id": obj_id}, {"_id": str(sub_id)}]})
        return cls(doc) if doc else None

    @classmethod
    def get_user_submissions(cls, user_id, roadmap_slug):
        db = get_db()
        cursor = db[cls.collection_name].find({
            "user_id": str(user_id),
            "roadmap_slug": str(roadmap_slug)
        }).sort("submitted_at", -1)
        return [cls(doc) for doc in cursor]

    @classmethod
    def get_all_pending(cls):
        db = get_db()
        cursor = db[cls.collection_name].find({"status": cls.STATUS_PENDING}).sort("submitted_at", 1)
        return [cls(doc) for doc in cursor]


class RoadmapCashback:
    collection_name = "roadmap_cashback"

    STATUS_NOT_ELIGIBLE = "not_eligible"
    STATUS_ELIGIBLE = "eligible"
    STATUS_PENDING_REVIEW = "pending_review"
    STATUS_APPROVED = "approved"
    STATUS_PROCESSING = "processing"
    STATUS_PROCESSED = "processed"
    STATUS_REJECTED = "rejected"
    STATUS_FAILED = "failed"

    def __init__(self, data=None):
        self._data = data or {}
        self._id = self._data.get("_id")
        self.id = str(self._id) if self._id else ""
        self.user_id = str(self._data.get("user_id", ""))
        self.user_name = self._data.get("user_name", "")
        self.user_email = self._data.get("user_email", "")
        self.roadmap_slug = self._data.get("roadmap_slug", "")
        self.roadmap_title = self._data.get("roadmap_title", "")
        self.original_payment_id = self._data.get("original_payment_id", "")
        self.original_amount = float(self._data.get("original_amount", 0.0))
        self.cashback_percentage = float(self._data.get("cashback_percentage", 50.0))
        self.cashback_amount = float(self._data.get("cashback_amount", 0.0))
        self.currency = self._data.get("currency", "INR")
        self.eligibility_status = self._data.get("eligibility_status", self.STATUS_NOT_ELIGIBLE)
        self.review_status = self._data.get("review_status", self.STATUS_NOT_ELIGIBLE)
        self.refund_status = self._data.get("refund_status", "none")  # none, initiated, processed, failed, manual_completed
        self.payment_provider_refund_id = self._data.get("payment_provider_refund_id", "")
        self.refund_mode = self._data.get("refund_mode", "gateway")  # gateway, manual_upi
        self.requested_at = self._data.get("requested_at")
        self.approved_at = self._data.get("approved_at")
        self.processed_at = self._data.get("processed_at")
        self.admin_notes = self._data.get("admin_notes", "")
        self.failure_reason = self._data.get("failure_reason", "")
        self.audit_log = self._data.get("audit_log", [])  # [{"timestamp": ..., "action": ..., "by": ...}]

    def add_audit_entry(self, action, by="system", note=""):
        self.audit_log.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": action,
            "by": str(by),
            "note": str(note)
        })

    def save(self):
        db = get_db()
        doc = {
            "user_id": self.user_id,
            "user_name": self.user_name,
            "user_email": self.user_email,
            "roadmap_slug": self.roadmap_slug,
            "roadmap_title": self.roadmap_title,
            "original_payment_id": self.original_payment_id,
            "original_amount": self.original_amount,
            "cashback_percentage": self.cashback_percentage,
            "cashback_amount": self.cashback_amount,
            "currency": self.currency,
            "eligibility_status": self.eligibility_status,
            "review_status": self.review_status,
            "refund_status": self.refund_status,
            "payment_provider_refund_id": self.payment_provider_refund_id,
            "refund_mode": self.refund_mode,
            "requested_at": self.requested_at,
            "approved_at": self.approved_at,
            "processed_at": self.processed_at,
            "admin_notes": self.admin_notes,
            "failure_reason": self.failure_reason,
            "audit_log": self.audit_log,
        }
        res = db[self.collection_name].update_one(
            {"user_id": self.user_id, "roadmap_slug": self.roadmap_slug},
            {"$set": doc},
            upsert=True
        )
        if not self._id and res.upserted_id:
            self._id = res.upserted_id
            self.id = str(self._id)
        return self

    @classmethod
    def get_by_user_and_roadmap(cls, user_id, roadmap_slug):
        db = get_db()
        doc = db[cls.collection_name].find_one({"user_id": str(user_id), "roadmap_slug": str(roadmap_slug)})
        return cls(doc) if doc else None

    @classmethod
    def get_by_id(cls, request_id):
        db = get_db()
        obj_id = _to_obj_id(request_id)
        doc = db[cls.collection_name].find_one({"$or": [{"_id": obj_id}, {"_id": str(request_id)}]})
        return cls(doc) if doc else None

    @classmethod
    def get_all(cls, status=None):
        db = get_db()
        query = {}
        if status:
            query["review_status"] = status
        cursor = db[cls.collection_name].find(query).sort("requested_at", -1)
        return [cls(doc) for doc in cursor]


def ensure_default_roadmaps():
    """
    Guarantees the flagship Full Stack Developer Launchpad package exists in MongoDB.
    Safely seeds initial roadmap without overwriting custom admin price adjustments.
    """
    try:
        from models.default_roadmap_curriculum import get_fullstack_roadmap_curriculum
        db = get_db()
        pkg_data = get_fullstack_roadmap_curriculum()
        slug = pkg_data.get("slug")
        existing = db.roadmap_packages.find_one({"slug": slug})
        if not existing:
            pkg = RoadmapPackage(pkg_data)
            pkg.save()
            print(f"[ROADMAP] Successfully seeded default career package: {pkg.title} ({slug})")
        else:
            # Update curriculum contents while preserving admin pricing & cashback custom overrides
            update_fields = {
                "title": pkg_data.get("title"),
                "short_description": pkg_data.get("short_description"),
                "full_description": pkg_data.get("full_description"),
                "duration": pkg_data.get("duration"),
                "level": pkg_data.get("level"),
                "language": pkg_data.get("language"),
                "tech_stack": pkg_data.get("tech_stack"),
                "career_outcomes": pkg_data.get("career_outcomes"),
                "phases": pkg_data.get("phases"),
                "projects": pkg_data.get("projects"),
                "capstone": pkg_data.get("capstone"),
                "thumbnail_url": pkg_data.get("thumbnail_url"),
                "updated_at": datetime.now(timezone.utc),
            }
            db.roadmap_packages.update_one({"slug": slug}, {"$set": update_fields})
            print(f"[ROADMAP] Verified and refreshed curriculum for: {slug}")
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning(f"[ROADMAP SEED WARNING] Could not ensure default roadmaps: {e}")

