"""
SkillRock — Monthly Challenge Platform Models
Defines MongoDB models for Monthly Challenges, Curriculum Modules, Student Enrollments (28-day tracking),
Practice Arena MCQs, Placement Interview Preparation, Coding Arena Problems, 50-MCQ Assessment Engine,
Practical Assignments, Rubric Reviews, and the 100% Refund Claim & Verification System.
"""

from datetime import datetime, timezone, timedelta
from bson import ObjectId
import re
import uuid
import logging
from models.mongo import db, get_db, _to_obj_id, slugify

logger = logging.getLogger(__name__)


class MonthlyChallenge:
    """
    SkillRock Monthly Challenge Course Document.
    Launches each month at ₹499 enrolment fee with a 28-day completion window and 100% refund eligibility.
    """
    collection_name = "monthly_challenges"

    def __init__(self, data=None):
        self._data = data or {}
        self._id = self._data.get("_id")
        self.id = str(self._id) if self._id else str(self._data.get("challenge_id", ""))
        self.challenge_id = str(self._data.get("challenge_id", self.id or f"mc-{uuid.uuid4().hex[:8]}"))
        self.slug = self._data.get("slug") or slugify(self._data.get("title", "monthly-challenge"))
        self.title = self._data.get("title", "Python Programming — 28-Day Challenge")
        self.tagline = self._data.get("tagline", "Learn. Practice. Complete. Get Certified.")
        self.promotional_message = self._data.get(
            "promotional_message",
            "Complete your learning challenge within 28 days and get 100% of your eligible enrolment fee back!"
        )
        self.short_description = self._data.get(
            "short_description",
            "Learn Python through a curated YouTube course, solve practical problems, prepare for technical interviews, and earn your SkillRock certificate."
        )
        self.full_description = self._data.get("full_description", self._data.get("description", ""))
        self.description = self.full_description
        self.badge_text = self._data.get("badge_text", "MONTHLY CHALLENGE")
        self.month_display = self._data.get("month_display", "November 2026")
        self.instructor = self._data.get("instructor", "Programming with Mosh & SkillRock Faculty")
        self.thumbnail_url = self._data.get("thumbnail_url", "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=800&auto=format&fit=crop&q=80")
        self.banner_url = self._data.get("banner_url", "")
        self.price = float(self._data.get("price", 499.0))
        self.original_price = float(self._data.get("original_price", 1999.0))
        self.currency = self._data.get("currency", "INR")
        self.duration_days = int(self._data.get("duration_days", 28))
        self.difficulty = self._data.get("difficulty", "Beginner to Placement Ready")
        self.skills_covered = self._data.get("skills_covered", ["Python", "DSA", "OOP", "File Handling", "Problem Solving"])
        self.learning_outcomes = self._data.get("learning_outcomes", [
            "Master Python syntax, data types, control flow, functions and modules.",
            "Write modular, object-oriented code with clean classes and inheritance.",
            "Solve 20+ algorithmic coding problems and strengthen logical thinking.",
            "Ace technical interview rounds with curated placement questions.",
            "Build and deploy an evaluated real-world practical capstone application.",
            "Pass the rigorous 50-MCQ Final Assessment and receive a verified SkillRock Certificate.",
            "Claim a 100% refund of your ₹499 enrolment fee upon completing all 28-day requirements."
        ])
        self.youtube_course_url = self._data.get("youtube_course_url", "https://www.youtube.com/watch?v=_uQrJ0TkZlc")
        self.youtube_video_id = self._data.get("youtube_video_id", "_uQrJ0TkZlc")
        self.is_published = bool(self._data.get("is_published", self._data.get("is_active", True)))
        self.is_programming = bool(self._data.get("is_programming", True))
        self.supported_languages = self._data.get("supported_languages", ["python"])
        self.modules = self._data.get("modules", [])
        self.refund_terms = self._data.get(
            "refund_terms",
            "Complete all mandatory learning modules, pass the 50-question final assessment (>=80%), receive approved practical assignment review, and earn your verified certificate within 28 days of enrollment to receive a 100% refund."
        )
        self.start_date = self._data.get("start_date") or datetime.now(timezone.utc)
        self.end_date = self._data.get("end_date") or (datetime.now(timezone.utc) + timedelta(days=60))
        self.created_at = self._data.get("created_at") or datetime.now(timezone.utc)
        self.updated_at = self._data.get("updated_at") or datetime.now(timezone.utc)

    @property
    def is_active(self):
        return bool(self.is_published)

    @is_active.setter
    def is_active(self, val):
        self.is_published = bool(val)

    @property
    def fallback_thumbnail(self):
        return self.thumbnail_url or "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=800&auto=format&fit=crop&q=80"

    @property
    def enrolled_count(self):
        try:
            database = get_db()
            return database.challenge_enrollments.count_documents({
                "$or": [{"challenge_id": self.challenge_id}, {"challenge_slug": self.slug}]
            })
        except Exception:
            return 0

    def to_dict(self):
        return {
            "challenge_id": self.challenge_id,
            "slug": self.slug,
            "title": self.title,
            "tagline": self.tagline,
            "promotional_message": self.promotional_message,
            "short_description": self.short_description,
            "full_description": self.full_description,
            "badge_text": self.badge_text,
            "month_display": self.month_display,
            "instructor": self.instructor,
            "thumbnail_url": self.thumbnail_url,
            "price": self.price,
            "original_price": self.original_price,
            "duration_days": self.duration_days,
            "difficulty": self.difficulty,
            "skills_covered": self.skills_covered,
            "learning_outcomes": self.learning_outcomes,
            "youtube_course_url": self.youtube_course_url,
            "youtube_video_id": self.youtube_video_id,
            "is_published": self.is_published,
            "is_active": self.is_active,
            "is_programming": self.is_programming,
            "modules": self.modules,
            "refund_terms": self.refund_terms,
            "enrolled_count": self.enrolled_count,
        }

    def save(self):
        database = get_db()
        self.updated_at = datetime.now(timezone.utc)
        doc = {
            "challenge_id": self.challenge_id,
            "slug": self.slug,
            "title": self.title,
            "tagline": self.tagline,
            "promotional_message": self.promotional_message,
            "short_description": self.short_description,
            "full_description": self.full_description,
            "description": self.full_description,
            "badge_text": self.badge_text,
            "month_display": self.month_display,
            "instructor": self.instructor,
            "thumbnail_url": self.thumbnail_url,
            "banner_url": self.banner_url,
            "price": self.price,
            "original_price": self.original_price,
            "currency": self.currency,
            "duration_days": self.duration_days,
            "difficulty": self.difficulty,
            "skills_covered": self.skills_covered,
            "learning_outcomes": self.learning_outcomes,
            "youtube_course_url": self.youtube_course_url,
            "youtube_video_id": self.youtube_video_id,
            "is_published": self.is_published,
            "is_active": self.is_active,
            "is_programming": self.is_programming,
            "supported_languages": self.supported_languages,
            "modules": self.modules,
            "refund_terms": self.refund_terms,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
        res = database[self.collection_name].update_one(
            {"challenge_id": self.challenge_id},
            {"$set": doc},
            upsert=True
        )
        if not self._id and res.upserted_id:
            self._id = res.upserted_id
            self.id = str(self._id)
        return self

    @classmethod
    def get_by_id(cls, challenge_id):
        if not challenge_id:
            return None
        database = get_db()
        doc = database[cls.collection_name].find_one({
            "$or": [{"challenge_id": str(challenge_id)}, {"_id": _to_obj_id(challenge_id)}]
        })
        return cls(doc) if doc else None

    @classmethod
    def get_by_slug(cls, slug):
        if not slug:
            return None
        database = get_db()
        doc = database[cls.collection_name].find_one({"slug": str(slug).strip().lower()})
        return cls(doc) if doc else None

    @classmethod
    def get_active(cls):
        """Returns the current featured active Monthly Challenge."""
        database = get_db()
        doc = database[cls.collection_name].find_one({"is_published": True}, sort=[("created_at", -1)])
        return cls(doc) if doc else None

    @classmethod
    def get_all_active(cls):
        """Returns all active published Monthly Challenges."""
        return cls.get_all(published_only=True)

    @classmethod
    def get_all(cls, published_only=True, active_only=None):
        if active_only is not None:
            published_only = active_only
        database = get_db()
        q = {"is_published": True} if published_only else {}
        cursor = database[cls.collection_name].find(q).sort("created_at", -1)
        return [cls(doc) for doc in cursor]


class ChallengeEnrollment:
    """
    Student Enrollment in a 28-day Monthly Challenge.
    Calculates remaining days accurately from enrolment timestamp and enforces the 28-day refund deadline.
    """
    collection_name = "challenge_enrollments"

    STATUS_ACTIVE = "active"
    STATUS_COMPLETED = "completed"
    STATUS_EXPIRED = "expired"

    REFUND_NOT_ELIGIBLE = "not_eligible"
    REFUND_ELIGIBLE = "eligible"
    REFUND_CLAIM_SUBMITTED = "claim_submitted"
    REFUND_UNDER_VERIFICATION = "under_verification"
    REFUND_APPROVED = "approved"
    REFUND_PROCESSING = "processing"
    REFUND_REFUNDED = "refunded"
    REFUND_REJECTED = "rejected"

    def __init__(self, data=None):
        self._data = data or {}
        self._id = self._data.get("_id")
        self.id = str(self._id) if self._id else str(self._data.get("enrollment_id", ""))
        self.enrollment_id = str(self._data.get("enrollment_id", self.id or f"enr-{uuid.uuid4().hex[:10]}"))
        self.user_id = str(self._data.get("user_id", ""))
        self.challenge_id = str(self._data.get("challenge_id", ""))
        self._challenge_slug = str(self._data.get("challenge_slug", self.challenge_id))
        self.payment_id = str(self._data.get("payment_id", ""))
        self.amount_paid = float(self._data.get("amount_paid", 499.0))
        
        # Exact Timestamps for 28-Day Countdown
        enrolled_raw = self._data.get("enrolled_at")
        if isinstance(enrolled_raw, str):
            try:
                self.enrolled_at = datetime.fromisoformat(enrolled_raw.replace("Z", "+00:00"))
            except Exception:
                self.enrolled_at = datetime.now(timezone.utc)
        elif isinstance(enrolled_raw, datetime):
            self.enrolled_at = enrolled_raw if enrolled_raw.tzinfo else enrolled_raw.replace(tzinfo=timezone.utc)
        else:
            self.enrolled_at = datetime.now(timezone.utc)

        deadline_raw = self._data.get("deadline_at")
        if isinstance(deadline_raw, str):
            try:
                self.deadline_at = datetime.fromisoformat(deadline_raw.replace("Z", "+00:00"))
            except Exception:
                self.deadline_at = self.enrolled_at + timedelta(days=28)
        elif isinstance(deadline_raw, datetime):
            self.deadline_at = deadline_raw if deadline_raw.tzinfo else deadline_raw.replace(tzinfo=timezone.utc)
        else:
            self.deadline_at = self.enrolled_at + timedelta(days=28)

        # Progress Milestones
        self.completed_modules = list(self._data.get("completed_modules", self._data.get("modules_completed", [])))
        self.completed_practice_questions = list(self._data.get("completed_practice_questions", []))
        self.interview_progress = dict(self._data.get("interview_progress", self._data.get("interview_prep_status", {})))
        self.completed_coding_problems = list(self._data.get("completed_coding_problems", self._data.get("coding_problems_solved", [])))
        self.assignment_submission_id = str(self._data.get("assignment_submission_id", ""))
        self.assignment_approved = bool(self._data.get("assignment_approved", False))
        self.assignment_score = float(self._data.get("assignment_score", 0.0))
        self._assignment_status = self._data.get("assignment_status", "approved" if self.assignment_approved else ("submitted" if self.assignment_submission_id else "pending"))
        
        # 50-MCQ Final Assessment Milestones
        self.assessment_passed = bool(self._data.get("assessment_passed", False))
        self.assessment_score = int(self._data.get("assessment_score", 0))  # 0 to 50
        self.assessment_attempts_count = int(self._data.get("assessment_attempts_count", 0))
        self.max_assessment_attempts = int(self._data.get("max_assessment_attempts", 2))

        # Certificate Milestone
        self.certificate_id = str(self._data.get("certificate_id", ""))
        self.certificate_issued_at = self._data.get("certificate_issued_at")

        # 100% Refund Status
        self.refund_status = self._data.get("refund_status", self.REFUND_NOT_ELIGIBLE)
        self.refund_claim_id = str(self._data.get("refund_claim_id", ""))

        self.status = self._data.get("status", self.STATUS_ACTIVE)
        self.updated_at = self._data.get("updated_at") or datetime.now(timezone.utc)

    # Property Aliases for clean routing & testing integration
    @property
    def challenge_slug(self):
        return self._challenge_slug or self.challenge_id

    @challenge_slug.setter
    def challenge_slug(self, val):
        self._challenge_slug = str(val)

    @property
    def modules_completed(self):
        return self.completed_modules

    @modules_completed.setter
    def modules_completed(self, val):
        self.completed_modules = list(val)

    @property
    def coding_problems_solved(self):
        return self.completed_coding_problems

    @coding_problems_solved.setter
    def coding_problems_solved(self, val):
        self.completed_coding_problems = list(val)

    @property
    def practice_scores(self):
        return self._data.setdefault("practice_scores", {})

    @practice_scores.setter
    def practice_scores(self, val):
        self._data["practice_scores"] = dict(val)

    @property
    def interview_prep_status(self):
        return self.interview_progress

    @interview_prep_status.setter
    def interview_prep_status(self, val):
        self.interview_progress = dict(val)

    @property
    def assignment_status(self):
        return self._assignment_status

    @assignment_status.setter
    def assignment_status(self, val):
        self._assignment_status = str(val)
        if val == "approved":
            self.assignment_approved = True

    @property
    def remaining_seconds(self):
        now = datetime.now(timezone.utc)
        delta = (self.deadline_at - now).total_seconds()
        return max(0, int(delta))

    @property
    def remaining_days(self):
        import math
        sec = self.remaining_seconds
        if sec <= 0:
            return 0
        return int(math.ceil(sec / 86400.0))

    @property
    def is_expired(self):
        return self.remaining_seconds <= 0 and not self.is_completed

    @property
    def is_completed(self):
        return self.status == self.STATUS_COMPLETED or (
            self.assessment_passed and self.assignment_approved and bool(self.certificate_id)
        )

    def get_countdown_metrics(self, duration_days=28):
        now = datetime.now(timezone.utc)
        rem_sec = self.remaining_seconds
        rem_days = self.remaining_days
        elapsed_sec = max(0, int((now - self.enrolled_at).total_seconds()))
        elapsed_days = min(duration_days, max(1, elapsed_sec // 86400 + 1))
        pct_time = min(100.0, round(((now - self.enrolled_at).total_seconds() / max(1, duration_days * 86400)) * 100, 1))
        return {
            "days_remaining": rem_days,
            "days_elapsed": elapsed_days,
            "duration_days": duration_days,
            "percent_time_elapsed": pct_time,
            "is_expired": (rem_sec <= 0),
            "enrolled_date_str": self.enrolled_at.strftime("%b %d, %Y"),
            "deadline_date_str": self.deadline_at.strftime("%b %d, %Y")
        }

    def calculate_progress(self, total_modules=6, total_practice=8, total_interviews=4, total_coding=4, has_assignment_submitted=False, assessment_passed=False):
        mod_pct = min(100, round((len(self.completed_modules) / max(1, total_modules)) * 100, 1))
        prac_pct = min(100, round((len(self.practice_scores) / max(1, total_practice)) * 100, 1))
        int_pct = min(100, round((len(self.interview_progress) / max(1, total_interviews)) * 100, 1))
        code_pct = min(100, round((len(self.completed_coding_problems) / max(1, total_coding)) * 100, 1))
        overall = round((mod_pct * 0.20) + (prac_pct * 0.15) + (int_pct * 0.15) + (code_pct * 0.20) + (20.0 if (has_assignment_submitted or self.assignment_approved) else 0.0) + (10.0 if (assessment_passed or self.assessment_passed) else 0.0), 1)
        return {
            "overall_completion_percentage": min(100.0, overall),
            "modules_percent": int(mod_pct),
            "practice_percent": int(prac_pct),
            "interviews_percent": int(int_pct),
            "coding_percent": int(code_pct)
        }

    def calculate_completion_percentage(self, total_modules_count=6):
        """Calculates realistic completion percentage across all required milestones."""
        modules_done = len(self.completed_modules)
        mod_score = (modules_done / max(1, total_modules_count)) * 25.0
        assign_score = 25.0 if self.assignment_approved else (10.0 if self.assignment_submission_id else 0.0)
        assess_score = 30.0 if self.assessment_passed else (10.0 if self.assessment_attempts_count > 0 else 0.0)
        cert_score = 20.0 if self.certificate_id else 0.0
        return min(100.0, round(mod_score + assign_score + assess_score + cert_score, 1))

    def evaluate_refund_eligibility(self, total_modules_count=6, **kwargs):
        """
        Server-side validation of the 7 Published Refund Conditions:
        1. 100% Video Course Modules Completed
        2. 100% Practice Arena Questions Attempted
        3. 100% Interview Prep Questions Completed
        4. 100% Coding Arena Problems Solved
        5. Practical Capstone Assignment Submitted / Approved
        6. Final Assessment Passed (>=80%)
        7. Completed Within 28 Days Deadline
        """
        total_m = kwargs.get("total_modules", total_modules_count)
        total_p = kwargs.get("total_practice", 8)
        total_i = kwargs.get("total_interviews", 4)
        total_c = kwargs.get("total_coding", 4)
        assign_st = kwargs.get("assignment_submission_status", self.assignment_status)
        duration_d = kwargs.get("duration_days", 28)

        now = datetime.now(timezone.utc)
        within_deadline = now <= self.deadline_at
        modules_ok = len(self.completed_modules) >= total_m and total_m > 0
        practice_ok = len(self.practice_scores) >= total_p and total_p > 0
        interview_ok = len(self.interview_progress) >= total_i and total_i > 0
        coding_ok = len(self.completed_coding_problems) >= total_c and total_c > 0
        assign_ok = bool(assign_st in ("submitted", "approved") or self.assignment_status in ("submitted", "approved") or self.assignment_approved)
        assess_ok = bool(self.assessment_passed)

        all_eligible = bool(within_deadline and modules_ok and practice_ok and interview_ok and coding_ok and assign_ok and assess_ok)

        criteria = [
            {"condition": "100% Video Course Modules Completed", "fulfilled": modules_ok, "status": f"{len(self.completed_modules)}/{total_m}"},
            {"condition": "100% Practice Arena Questions Attempted", "fulfilled": practice_ok, "status": f"{len(self.practice_scores)}/{total_p}"},
            {"condition": "100% Interview Prep Questions Completed", "fulfilled": interview_ok, "status": f"{len(self.interview_progress)}/{total_i}"},
            {"condition": "100% Coding Arena Problems Solved", "fulfilled": coding_ok, "status": f"{len(self.completed_coding_problems)}/{total_c}"},
            {"condition": "Practical Capstone Assignment Submitted", "fulfilled": assign_ok, "status": assign_st or self.assignment_status or "Pending"},
            {"condition": "Final Assessment Passed (>=80%)", "fulfilled": assess_ok, "status": f"{self.assessment_score}/50" if self.assessment_passed else "Pending"},
            {"condition": "Completed Within 28 Days Deadline", "fulfilled": within_deadline, "status": f"{self.remaining_days} days left" if within_deadline else "Expired"}
        ]
        fulfilled_count = sum(1 for c in criteria if c["fulfilled"])

        # Update refund status automatically if not yet claimed
        if self.refund_status in (self.REFUND_NOT_ELIGIBLE, self.REFUND_ELIGIBLE):
            self.refund_status = self.REFUND_ELIGIBLE if all_eligible else self.REFUND_NOT_ELIGIBLE

        return {
            "all_eligible": all_eligible,
            "fulfilled_count": fulfilled_count,
            "total_criteria": len(criteria),
            "criteria": criteria
        }

    def save(self):
        database = get_db()
        self.updated_at = datetime.now(timezone.utc)
        doc = {
            "enrollment_id": self.enrollment_id,
            "user_id": self.user_id,
            "challenge_id": self.challenge_id,
            "challenge_slug": self.challenge_slug,
            "payment_id": self.payment_id,
            "amount_paid": self.amount_paid,
            "enrolled_at": self.enrolled_at,
            "deadline_at": self.deadline_at,
            "completed_modules": self.completed_modules,
            "modules_completed": self.completed_modules,
            "completed_practice_questions": self.completed_practice_questions,
            "practice_scores": self.practice_scores,
            "interview_progress": self.interview_progress,
            "interview_prep_status": self.interview_progress,
            "completed_coding_problems": self.completed_coding_problems,
            "coding_problems_solved": self.completed_coding_problems,
            "assignment_submission_id": self.assignment_submission_id,
            "assignment_approved": self.assignment_approved,
            "assignment_score": self.assignment_score,
            "assignment_status": self.assignment_status,
            "assessment_passed": self.assessment_passed,
            "assessment_score": self.assessment_score,
            "assessment_attempts_count": self.assessment_attempts_count,
            "max_assessment_attempts": self.max_assessment_attempts,
            "certificate_id": self.certificate_id,
            "certificate_issued_at": self.certificate_issued_at,
            "refund_status": self.refund_status,
            "refund_claim_id": self.refund_claim_id,
            "status": self.status,
            "updated_at": self.updated_at,
        }
        res = database[self.collection_name].update_one(
            {"enrollment_id": self.enrollment_id},
            {"$set": doc},
            upsert=True
        )
        if not self._id and res.upserted_id:
            self._id = res.upserted_id
            self.id = str(self._id)
        return self

    @classmethod
    def get_user_enrollment(cls, user_id, challenge_slug_or_id):
        if not user_id or not challenge_slug_or_id:
            return None
        database = get_db()
        doc = database[cls.collection_name].find_one({
            "user_id": str(user_id),
            "$or": [
                {"challenge_slug": str(challenge_slug_or_id)},
                {"challenge_id": str(challenge_slug_or_id)}
            ]
        })
        return cls(doc) if doc else None

    @classmethod
    def get_by_user_and_challenge(cls, user_id, challenge_id):
        return cls.get_user_enrollment(user_id, challenge_id)

    @classmethod
    def get_or_create(cls, user_id, challenge_id, challenge_slug, amount_paid=499.0, payment_id=""):
        enr = cls.get_user_enrollment(user_id, challenge_slug) or cls.get_user_enrollment(user_id, challenge_id)
        if not enr:
            enr = cls({
                "user_id": str(user_id),
                "challenge_id": str(challenge_id),
                "challenge_slug": str(challenge_slug),
                "amount_paid": float(amount_paid or 499.0),
                "payment_id": str(payment_id or ""),
                "enrolled_at": datetime.now(timezone.utc),
                "deadline_at": datetime.now(timezone.utc) + timedelta(days=28)
            })
            enr.save()
        return enr

    @classmethod
    def get_user_all(cls, user_id):
        database = get_db()
        cursor = database[cls.collection_name].find({"user_id": str(user_id)})
        return [cls(doc) for doc in cursor]

    @classmethod
    def get_all_for_challenge(cls, challenge_id):
        database = get_db()
        cursor = database[cls.collection_name].find({
            "$or": [{"challenge_id": str(challenge_id)}, {"challenge_slug": str(challenge_id)}]
        }).sort("enrolled_at", -1)
        return [cls(doc) for doc in cursor]

    @classmethod
    def get_by_certificate_id(cls, cert_id):
        """Finds a challenge enrollment by its issued certificate ID."""
        if not cert_id:
            return None
        database = get_db()
        clean_id = str(cert_id).strip()
        doc = database[cls.collection_name].find_one({"certificate_id": clean_id})
        if not doc:
            doc = database[cls.collection_name].find_one({"certificate_id": clean_id.upper()})
        return cls(doc) if doc else None



class PracticeQuestion:
    """
    Practice Arena Question (Module & Topic Wise).
    Allows students to test concepts without affecting final assessment score.
    """
    collection_name = "challenge_practice_questions"

    def __init__(self, data=None):
        self._data = data or {}
        self._id = self._data.get("_id")
        self.id = str(self._id) if self._id else str(self._data.get("question_id", ""))
        self.question_id = str(self._data.get("question_id", self.id or f"pq-{uuid.uuid4().hex[:8]}"))
        self.challenge_id = str(self._data.get("challenge_id", ""))
        self._challenge_slug = str(self._data.get("challenge_slug", self.challenge_id))
        self.module_id = str(self._data.get("module_id", "module-1"))
        self.topic = self._data.get("topic", "General")
        self.difficulty = self._data.get("difficulty", "Easy")  # Easy, Medium, Hard
        self.question = self._data.get("question", "")
        self.code_snippet = self._data.get("code_snippet", "")
        self.options = self._data.get("options", [])
        self.correct_answer_index = int(self._data.get("correct_answer_index", self._data.get("correct_option", 0)))
        self.explanation = self._data.get("explanation", "")
        self.hint = self._data.get("hint", "")
        self.order_index = self._data.get("order_index", self.question_id)

    @property
    def challenge_slug(self):
        return self._challenge_slug or self.challenge_id

    @property
    def correct_option(self):
        return self.correct_answer_index

    @correct_option.setter
    def correct_option(self, val):
        self.correct_answer_index = int(val)

    def to_dict(self, include_answer=False):
        d = {
            "question_id": self.question_id,
            "challenge_id": self.challenge_id,
            "challenge_slug": self.challenge_slug,
            "module_id": self.module_id,
            "topic": self.topic,
            "difficulty": self.difficulty,
            "question": self.question,
            "code_snippet": self.code_snippet,
            "options": self.options,
            "hint": self.hint,
        }
        if include_answer:
            d["correct_answer_index"] = self.correct_answer_index
            d["correct_option"] = self.correct_option
            d["explanation"] = self.explanation
        return d

    def save(self):
        database = get_db()
        doc = {
            "question_id": self.question_id,
            "challenge_id": self.challenge_id,
            "challenge_slug": self.challenge_slug,
            "module_id": self.module_id,
            "topic": self.topic,
            "difficulty": self.difficulty,
            "question": self.question,
            "code_snippet": self.code_snippet,
            "options": self.options,
            "correct_answer_index": self.correct_answer_index,
            "correct_option": self.correct_option,
            "explanation": self.explanation,
            "hint": self.hint,
            "order_index": self.order_index,
        }
        res = database[self.collection_name].update_one(
            {"question_id": self.question_id},
            {"$set": doc},
            upsert=True
        )
        if not self._id and res.upserted_id:
            self._id = res.upserted_id
            self.id = str(self._id)
        return self

    @classmethod
    def get_by_id(cls, qid):
        if not qid:
            return None
        database = get_db()
        doc = database[cls.collection_name].find_one({
            "$or": [{"question_id": str(qid)}, {"_id": _to_obj_id(qid)}]
        })
        return cls(doc) if doc else None

    @classmethod
    def get_by_challenge(cls, challenge_slug_or_id, module_id=None):
        database = get_db()
        q = {
            "$or": [
                {"challenge_id": str(challenge_slug_or_id)},
                {"challenge_slug": str(challenge_slug_or_id)}
            ]
        }
        if module_id:
            q["module_id"] = str(module_id)
        cursor = database[cls.collection_name].find(q)
        return [cls(doc) for doc in cursor]


class InterviewQuestion:
    """
    Placement Interview Question with structured answers, concept explanations, and study tracking.
    """
    collection_name = "challenge_interview_questions"

    def __init__(self, data=None):
        self._data = data or {}
        self._id = self._data.get("_id")
        self.id = str(self._id) if self._id else str(self._data.get("question_id", ""))
        self.question_id = str(self._data.get("question_id", self.id or f"iq-{uuid.uuid4().hex[:8]}"))
        self.challenge_id = str(self._data.get("challenge_id", ""))
        self._challenge_slug = str(self._data.get("challenge_slug", self.challenge_id))
        self.topic = self._data.get("topic", "Core Concepts")
        self.level = self._data.get("level", "Beginner")  # Beginner, Intermediate, Advanced
        self.category = self._data.get("category", "Conceptual")  # Conceptual, Scenario, Technical
        self.question = self._data.get("question", "")
        self.sample_answer = self._data.get("sample_answer", "")
        self.explanation = self._data.get("explanation", "")
        self.interviewer_tips = self._data.get("interviewer_tips", "")
        self.code_example = self._data.get("code_example", "")
        self.order_index = self._data.get("order_index", self.question_id)

    @property
    def challenge_slug(self):
        return self._challenge_slug or self.challenge_id

    def to_dict(self):
        return {
            "question_id": self.question_id,
            "challenge_id": self.challenge_id,
            "challenge_slug": self.challenge_slug,
            "topic": self.topic,
            "level": self.level,
            "category": self.category,
            "question": self.question,
            "sample_answer": self.sample_answer,
            "explanation": self.explanation,
            "interviewer_tips": self.interviewer_tips,
            "code_example": self.code_example,
            "order_index": self.order_index,
        }

    def save(self):
        database = get_db()
        doc = {
            "question_id": self.question_id,
            "challenge_id": self.challenge_id,
            "challenge_slug": self.challenge_slug,
            "topic": self.topic,
            "level": self.level,
            "category": self.category,
            "question": self.question,
            "sample_answer": self.sample_answer,
            "explanation": self.explanation,
            "interviewer_tips": self.interviewer_tips,
            "code_example": self.code_example,
            "order_index": self.order_index,
        }
        res = database[self.collection_name].update_one(
            {"question_id": self.question_id},
            {"$set": doc},
            upsert=True
        )
        if not self._id and res.upserted_id:
            self._id = res.upserted_id
            self.id = str(self._id)
        return self

    @classmethod
    def get_by_id(cls, qid):
        if not qid:
            return None
        database = get_db()
        doc = database[cls.collection_name].find_one({
            "$or": [{"question_id": str(qid)}, {"_id": _to_obj_id(qid)}]
        })
        return cls(doc) if doc else None

    @classmethod
    def get_by_challenge(cls, challenge_slug_or_id):
        database = get_db()
        cursor = database[cls.collection_name].find({
            "$or": [
                {"challenge_id": str(challenge_slug_or_id)},
                {"challenge_slug": str(challenge_slug_or_id)}
            ]
        })
        return [cls(doc) for doc in cursor]


class CodingProblem:
    """
    LeetCode-Style Coding Arena Problem with sample and hidden test cases.
    """
    collection_name = "challenge_coding_problems"

    def __init__(self, data=None):
        self._data = data or {}
        self._id = self._data.get("_id")
        self.id = str(self._id) if self._id else str(self._data.get("problem_id", ""))
        self.problem_id = str(self._data.get("problem_id", self.id or f"cp-{uuid.uuid4().hex[:8]}"))
        self.challenge_id = str(self._data.get("challenge_id", ""))
        self._challenge_slug = str(self._data.get("challenge_slug", self.challenge_id))
        self.slug = self._data.get("slug") or slugify(self._data.get("title", "problem"))
        self.title = self._data.get("title", "")
        self.difficulty = self._data.get("difficulty", "Easy")  # Easy, Medium, Hard
        self.order = int(self._data.get("order", 1))
        self.description = self._data.get("description", "")
        self.input_format = self._data.get("input_format", "")
        self.output_format = self._data.get("output_format", "")
        self.constraints = self._data.get("constraints", "")
        self.language = self._data.get("language", "python")
        self.examples = self._data.get("examples", [])  # list of {input, output, explanation}
        self.starter_code = self._data.get("starter_code", {
            "python": "def solution():\n    # Write your code here\n    pass\n"
        })
        self.sample_test_cases = self._data.get("sample_test_cases", [])  # {input, expected_output}
        self.hidden_test_cases = self._data.get("hidden_test_cases", [])  # {input, expected_output}

    @property
    def challenge_slug(self):
        return self._challenge_slug or self.challenge_id

    @property
    def test_cases(self):
        cases = []
        for tc in self.sample_test_cases:
            cases.append({
                "input": tc.get("input", ""),
                "expected_output": tc.get("expected_output", ""),
                "is_hidden": False
            })
        for tc in self.hidden_test_cases:
            cases.append({
                "input": tc.get("input", ""),
                "expected_output": tc.get("expected_output", ""),
                "is_hidden": True
            })
        return cases

    def to_dict(self, include_hidden=False):
        d = {
            "problem_id": self.problem_id,
            "challenge_id": self.challenge_id,
            "challenge_slug": self.challenge_slug,
            "slug": self.slug,
            "title": self.title,
            "difficulty": self.difficulty,
            "order": self.order,
            "description": self.description,
            "input_format": self.input_format,
            "output_format": self.output_format,
            "constraints": self.constraints,
            "examples": self.examples,
            "starter_code": self.starter_code,
            "sample_test_cases": self.sample_test_cases,
        }
        if include_hidden:
            d["hidden_test_cases"] = self.hidden_test_cases
        return d

    def save(self):
        database = get_db()
        doc = {
            "problem_id": self.problem_id,
            "challenge_id": self.challenge_id,
            "challenge_slug": self.challenge_slug,
            "slug": self.slug,
            "title": self.title,
            "difficulty": self.difficulty,
            "order": self.order,
            "description": self.description,
            "input_format": self.input_format,
            "output_format": self.output_format,
            "constraints": self.constraints,
            "language": self.language,
            "examples": self.examples,
            "starter_code": self.starter_code,
            "sample_test_cases": self.sample_test_cases,
            "hidden_test_cases": self.hidden_test_cases,
        }
        res = database[self.collection_name].update_one(
            {"problem_id": self.problem_id},
            {"$set": doc},
            upsert=True
        )
        if not self._id and res.upserted_id:
            self._id = res.upserted_id
            self.id = str(self._id)
        return self

    @classmethod
    def get_by_challenge(cls, challenge_slug_or_id):
        database = get_db()
        cursor = database[cls.collection_name].find({
            "$or": [
                {"challenge_id": str(challenge_slug_or_id)},
                {"challenge_slug": str(challenge_slug_or_id)}
            ]
        }).sort("order", 1)
        return [cls(doc) for doc in cursor]

    @classmethod
    def get_by_id(cls, problem_id):
        if not problem_id:
            return None
        database = get_db()
        doc = database[cls.collection_name].find_one({
            "$or": [
                {"problem_id": str(problem_id)},
                {"slug": str(problem_id)},
                {"_id": _to_obj_id(problem_id)}
            ]
        })
        return cls(doc) if doc else None


class AssessmentQuestion:
    """
    Approved Question in the 50-MCQ Final Assessment Question Bank.
    """
    collection_name = "challenge_assessment_questions"

    def __init__(self, data=None):
        self._data = data or {}
        self._id = self._data.get("_id")
        self.id = str(self._id) if self._id else str(self._data.get("question_id", ""))
        self.question_id = str(self._data.get("question_id", self.id or f"aq-{uuid.uuid4().hex[:8]}"))
        self.challenge_id = str(self._data.get("challenge_id", ""))
        self._challenge_slug = str(self._data.get("challenge_slug", self.challenge_id))
        self.topic = self._data.get("topic", "General")
        self.question = self._data.get("question", self._data.get("question_text", ""))
        self.options = self._data.get("options", [])  # Exactly 4 options
        self.correct_answer_index = int(self._data.get("correct_answer_index", self._data.get("correct_option", 0)))
        self.explanation = self._data.get("explanation", "")

    @property
    def challenge_slug(self):
        return self._challenge_slug or self.challenge_id

    @property
    def question_text(self):
        return self.question

    @question_text.setter
    def question_text(self, val):
        self.question = str(val)

    @property
    def correct_option(self):
        return self.correct_answer_index

    @correct_option.setter
    def correct_option(self, val):
        self.correct_answer_index = int(val)

    def to_client_dict(self):
        return {
            "id": self.id or self.question_id,
            "question_id": self.question_id,
            "topic": self.topic,
            "question": self.question,
            "question_text": self.question_text,
            "options": self.options,
        }

    def save(self):
        database = get_db()
        doc = {
            "question_id": self.question_id,
            "challenge_id": self.challenge_id,
            "challenge_slug": self.challenge_slug,
            "topic": self.topic,
            "question": self.question,
            "question_text": self.question_text,
            "options": self.options,
            "correct_answer_index": self.correct_answer_index,
            "correct_option": self.correct_option,
            "explanation": self.explanation,
        }
        res = database[self.collection_name].update_one(
            {"question_id": self.question_id},
            {"$set": doc},
            upsert=True
        )
        if not self._id and res.upserted_id:
            self._id = res.upserted_id
            self.id = str(self._id)
        return self

    @classmethod
    def get_by_id(cls, qid):
        if not qid:
            return None
        database = get_db()
        doc = database[cls.collection_name].find_one({
            "$or": [{"question_id": str(qid)}, {"_id": _to_obj_id(qid)}]
        })
        return cls(doc) if doc else None

    @classmethod
    def get_by_challenge(cls, challenge_slug_or_id):
        database = get_db()
        cursor = database[cls.collection_name].find({
            "$or": [
                {"challenge_id": str(challenge_slug_or_id)},
                {"challenge_slug": str(challenge_slug_or_id)}
            ]
        })
        return [cls(doc) for doc in cursor]


class AssessmentAttempt:
    """
    Student Final Assessment Attempt.
    Stores exact submitted answers, score (out of 50), percentage, and pass/fail result.
    """
    collection_name = "challenge_assessment_attempts"

    def __init__(self, data=None):
        self._data = data or {}
        self._id = self._data.get("_id")
        self.id = str(self._id) if self._id else str(self._data.get("attempt_id", ""))
        self.attempt_id = str(self._data.get("attempt_id", self.id or f"att-{uuid.uuid4().hex[:10]}"))
        self.user_id = str(self._data.get("user_id", ""))
        self.challenge_id = str(self._data.get("challenge_id", self._data.get("challenge_slug", "")))
        self.challenge_slug = str(self._data.get("challenge_slug", self.challenge_id))
        self.attempt_number = int(self._data.get("attempt_number", 1))
        self.question_ids = list(self._data.get("question_ids", []))
        self.student_answers = dict(self._data.get("student_answers", self._data.get("answers", {})))
        self.answers = self.student_answers
        self.total_questions = int(self._data.get("total_questions", len(self.question_ids) or 50))
        self.score = int(self._data.get("score", self._data.get("correct_count", 0)))
        self.correct_count = self.score
        self.percentage = float(self._data.get("percentage", self._data.get("score_percentage", 0.0)))
        self.score_percentage = self.percentage
        self.passed = bool(self._data.get("passed", False))  # >= 40 (80%)
        self.started_at = self._data.get("started_at") or self._data.get("submitted_at") or datetime.now(timezone.utc)
        self.completed_at = self._data.get("completed_at")
        self.submitted_at = self.completed_at or self.started_at

    def save(self):
        database = get_db()
        doc = {
            "attempt_id": self.attempt_id,
            "user_id": self.user_id,
            "challenge_id": self.challenge_id,
            "challenge_slug": self.challenge_slug,
            "attempt_number": self.attempt_number,
            "question_ids": self.question_ids,
            "answers": self.student_answers,
            "student_answers": self.student_answers,
            "total_questions": self.total_questions,
            "score": self.score,
            "correct_count": self.score,
            "percentage": self.percentage,
            "score_percentage": self.percentage,
            "passed": self.passed,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "submitted_at": self.submitted_at,
        }
        res = database[self.collection_name].update_one(
            {"attempt_id": self.attempt_id},
            {"$set": doc},
            upsert=True
        )
        if not self._id and res.upserted_id:
            self._id = res.upserted_id
            self.id = str(self._id)
        return self

    @classmethod
    def get_by_id(cls, att_id):
        if not att_id:
            return None
        database = get_db()
        doc = database[cls.collection_name].find_one({
            "$or": [{"attempt_id": str(att_id)}, {"_id": _to_obj_id(att_id)}]
        })
        return cls(doc) if doc else None

    @classmethod
    def get_user_attempts(cls, user_id, challenge_slug_or_id):
        database = get_db()
        cursor = database[cls.collection_name].find({
            "user_id": str(user_id),
            "$or": [
                {"challenge_id": str(challenge_slug_or_id)},
                {"challenge_slug": str(challenge_slug_or_id)}
            ]
        }).sort("attempt_number", 1)
        return [cls(doc) for doc in cursor]


class PracticalAssignment:
    """
    Mandatory Final Practical Assignment problem statement and evaluation rubric.
    """
    collection_name = "challenge_assignments"

    def __init__(self, data=None):
        self._data = data or {}
        self._id = self._data.get("_id")
        self.id = str(self._id) if self._id else str(self._data.get("assignment_id", ""))
        self.assignment_id = str(self._data.get("assignment_id", self.id or f"asg-{uuid.uuid4().hex[:8]}"))
        self.challenge_id = str(self._data.get("challenge_id", ""))
        self._challenge_slug = str(self._data.get("challenge_slug", self.challenge_id))
        self.title = self._data.get("title", "Final Practical Project: Task & Habit Tracker CLI")
        self.description = self._data.get("description", "")
        self.requirements = self._data.get("requirements", [
            "Implement a modular command-line application using classes and clean functions.",
            "Persist tasks, categories, and streak counts in a JSON or SQLite file.",
            "Include input validation, error handling, and a readable terminal UI.",
            "Write comprehensive docstrings and provide a clear README.md with setup instructions."
        ])
        self.rubric = self._data.get("rubric", [
            {"criterion": "Code Quality & Modularity", "max_points": 25, "desc": "Clean functions, classes, type hints, error handling."},
            {"criterion": "Functionality & Features", "max_points": 35, "desc": "All CRUD operations and data persistence work seamlessly."},
            {"criterion": "Documentation & Repository", "max_points": 20, "desc": "Clear README, clean commit history, license."},
            {"criterion": "Demonstration & Polish", "max_points": 20, "desc": "Live video or screenshots showing successful usage."}
        ])
        self.passing_score = int(self._data.get("passing_score", 70))  # 70/100 to approve

    @property
    def challenge_slug(self):
        return self._challenge_slug or self.challenge_id

    def save(self):
        database = get_db()
        doc = {
            "assignment_id": self.assignment_id,
            "challenge_id": self.challenge_id,
            "challenge_slug": self.challenge_slug,
            "title": self.title,
            "description": self.description,
            "requirements": self.requirements,
            "rubric": self.rubric,
            "passing_score": self.passing_score,
        }
        res = database[self.collection_name].update_one(
            {"assignment_id": self.assignment_id},
            {"$set": doc},
            upsert=True
        )
        if not self._id and res.upserted_id:
            self._id = res.upserted_id
            self.id = str(self._id)
        return self

    @classmethod
    def get_by_challenge(cls, challenge_slug_or_id):
        database = get_db()
        doc = database[cls.collection_name].find_one({
            "$or": [
                {"challenge_id": str(challenge_slug_or_id)},
                {"challenge_slug": str(challenge_slug_or_id)}
            ]
        })
        return cls(doc) if doc else None

    @classmethod
    def get_by_id(cls, asg_id):
        if not asg_id:
            return None
        database = get_db()
        doc = database[cls.collection_name].find_one({
            "$or": [{"assignment_id": str(asg_id)}, {"_id": _to_obj_id(asg_id)}]
        })
        return cls(doc) if doc else None


class ChallengeAssignmentSubmission:
    """
    Student Practical Assignment Submission evaluated by faculty/admin.
    """
    collection_name = "challenge_submissions"

    STATUS_PENDING = "submitted"
    STATUS_APPROVED = "approved"
    STATUS_REJECTED = "rejected"

    def __init__(self, data=None):
        self._data = data or {}
        self._id = self._data.get("_id")
        self.id = str(self._id) if self._id else str(self._data.get("submission_id", ""))
        self.submission_id = str(self._data.get("submission_id", self.id or f"sub-{uuid.uuid4().hex[:10]}"))
        self.user_id = str(self._data.get("user_id", ""))
        self.user_name = self._data.get("user_name", "")
        self.user_email = self._data.get("user_email", "")
        self.challenge_id = str(self._data.get("challenge_id", self._data.get("challenge_slug", "")))
        self.challenge_slug = str(self._data.get("challenge_slug", self.challenge_id))
        self.assignment_id = str(self._data.get("assignment_id", ""))
        self.github_repo_url = self._data.get("github_repo_url", self._data.get("github_url", ""))
        self.github_url = self.github_repo_url
        self.live_demo_url = self._data.get("live_demo_url", self._data.get("live_url", ""))
        self.live_url = self.live_demo_url
        self.file_reference = self._data.get("file_reference", "")
        self.submission_notes = self._data.get("submission_notes", self._data.get("explanation", ""))
        self.explanation = self.submission_notes
        self.status = self._data.get("status", self.STATUS_PENDING)
        self.score = float(self._data.get("score", 0.0))
        self.rubric_scores = dict(self._data.get("rubric_scores", {}))
        self.feedback = self._data.get("feedback", self._data.get("admin_feedback", ""))
        self.admin_feedback = self.feedback
        self.reviewed_by = self._data.get("reviewed_by", "")
        self.reviewed_at = self._data.get("reviewed_at")
        self.submitted_at = self._data.get("submitted_at") or datetime.now(timezone.utc)

    def save(self):
        database = get_db()
        doc = {
            "submission_id": self.submission_id,
            "user_id": self.user_id,
            "user_name": self.user_name,
            "user_email": self.user_email,
            "challenge_id": self.challenge_id,
            "challenge_slug": self.challenge_slug,
            "assignment_id": self.assignment_id,
            "github_repo_url": self.github_repo_url,
            "github_url": self.github_repo_url,
            "live_demo_url": self.live_demo_url,
            "live_url": self.live_demo_url,
            "file_reference": self.file_reference,
            "submission_notes": self.submission_notes,
            "explanation": self.submission_notes,
            "status": self.status,
            "score": self.score,
            "rubric_scores": self.rubric_scores,
            "feedback": self.feedback,
            "admin_feedback": self.feedback,
            "reviewed_by": self.reviewed_by,
            "reviewed_at": self.reviewed_at,
            "submitted_at": self.submitted_at,
        }
        res = database[self.collection_name].update_one(
            {"submission_id": self.submission_id},
            {"$set": doc},
            upsert=True
        )
        if not self._id and res.upserted_id:
            self._id = res.upserted_id
            self.id = str(self._id)
        return self

    @classmethod
    def get_by_id(cls, submission_id):
        if not submission_id:
            return None
        database = get_db()
        doc = database[cls.collection_name].find_one({
            "$or": [{"submission_id": str(submission_id)}, {"_id": _to_obj_id(submission_id)}]
        })
        return cls(doc) if doc else None

    @classmethod
    def get_user_submission(cls, user_id, challenge_slug_or_id):
        if not user_id or not challenge_slug_or_id:
            return None
        database = get_db()
        doc = database[cls.collection_name].find_one({
            "user_id": str(user_id),
            "$or": [
                {"challenge_slug": str(challenge_slug_or_id)},
                {"challenge_id": str(challenge_slug_or_id)}
            ]
        }, sort=[("submitted_at", -1)])
        return cls(doc) if doc else None

    @classmethod
    def get_by_user_and_challenge(cls, user_id, challenge_id):
        return cls.get_user_submission(user_id, challenge_id)

    @classmethod
    def list_all(cls, challenge_id=None, status=None):
        database = get_db()
        q = {}
        if challenge_id:
            q["$or"] = [{"challenge_id": str(challenge_id)}, {"challenge_slug": str(challenge_id)}]
        if status:
            q["status"] = status
        cursor = database[cls.collection_name].find(q).sort("submitted_at", -1)
        return [cls(doc) for doc in cursor]


class RefundClaim:
    """
    100% Refund Claim Record.
    Tracks transparent refund processing through verified payment gateway or bank transfer with audit logs.
    """
    collection_name = "refund_claims"

    STATUS_PENDING = "pending"
    STATUS_CLAIM_SUBMITTED = "pending"
    STATUS_UNDER_VERIFICATION = "under_verification"
    STATUS_APPROVED = "approved"
    STATUS_PROCESSING = "processing"
    STATUS_PAID = "paid"
    STATUS_REFUNDED = "paid"
    STATUS_REJECTED = "rejected"

    def __init__(self, data=None):
        self._data = data or {}
        self._id = self._data.get("_id")
        self.id = str(self._id) if self._id else str(self._data.get("claim_id", ""))
        self.claim_id = str(self._data.get("claim_id", self.id or f"REF-{uuid.uuid4().hex[:8].upper()}"))
        self.user_id = str(self._data.get("user_id", ""))
        self.user_name = self._data.get("user_name", self._data.get("account_holder_name", ""))
        self.user_email = self._data.get("user_email", "")
        self.challenge_id = str(self._data.get("challenge_id", self._data.get("challenge_slug", "")))
        self.challenge_slug = str(self._data.get("challenge_slug", self.challenge_id))
        self.challenge_title = self._data.get("challenge_title", "")
        self.payment_id = str(self._data.get("payment_id", ""))
        self.amount = float(self._data.get("amount", self._data.get("refund_amount", self._data.get("original_amount", 499.0))))
        self.original_amount = self.amount
        self.refund_amount = self.amount
        self.upi_id = self._data.get("upi_id", "")
        self.account_holder_name = self._data.get("account_holder_name", self.user_name)
        self.phone_number = self._data.get("phone_number", "")
        self.bank_account_info = self._data.get("bank_account_info", "")
        self.status = self._data.get("status", self.STATUS_PENDING)
        self.criteria_snapshot = list(self._data.get("criteria_snapshot", []))
        self.admin_notes = self._data.get("admin_notes", "")
        self.rejection_reason = self._data.get("rejection_reason", "")
        self.payout_reference = self._data.get("payout_reference", self._data.get("transaction_reference", ""))
        self.transaction_reference = self.payout_reference
        self.refund_mode = self._data.get("refund_mode", "upi")  # gateway, upi, bank
        self.reviewed_by = self._data.get("reviewed_by", "")
        self.reviewed_at = self._data.get("reviewed_at")
        self.submitted_at = self._data.get("submitted_at") or datetime.now(timezone.utc)
        self.processed_at = self._data.get("processed_at")
        self.audit_log = list(self._data.get("audit_log", []))

    def add_audit_entry(self, action, actor, notes=""):
        self.audit_log.append({
            "action": action,
            "actor": actor,
            "notes": notes,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })

    def save(self):
        database = get_db()
        doc = {
            "claim_id": self.claim_id,
            "user_id": self.user_id,
            "user_name": self.user_name,
            "user_email": self.user_email,
            "challenge_id": self.challenge_id,
            "challenge_slug": self.challenge_slug,
            "challenge_title": self.challenge_title,
            "payment_id": self.payment_id,
            "amount": self.amount,
            "original_amount": self.original_amount,
            "refund_amount": self.refund_amount,
            "upi_id": self.upi_id,
            "account_holder_name": self.account_holder_name,
            "phone_number": self.phone_number,
            "bank_account_info": self.bank_account_info,
            "status": self.status,
            "criteria_snapshot": self.criteria_snapshot,
            "admin_notes": self.admin_notes,
            "rejection_reason": self.rejection_reason,
            "payout_reference": self.payout_reference,
            "transaction_reference": self.transaction_reference,
            "refund_mode": self.refund_mode,
            "reviewed_by": self.reviewed_by,
            "reviewed_at": self.reviewed_at,
            "submitted_at": self.submitted_at,
            "processed_at": self.processed_at,
            "audit_log": self.audit_log,
        }
        res = database[self.collection_name].update_one(
            {"claim_id": self.claim_id},
            {"$set": doc},
            upsert=True
        )
        if not self._id and res.upserted_id:
            self._id = res.upserted_id
            self.id = str(self._id)
        return self

    @classmethod
    def get_by_id(cls, claim_id):
        if not claim_id:
            return None
        database = get_db()
        doc = database[cls.collection_name].find_one({
            "$or": [{"claim_id": str(claim_id)}, {"_id": _to_obj_id(claim_id)}]
        })
        return cls(doc) if doc else None

    @classmethod
    def get_by_user_challenge(cls, user_id, challenge_slug_or_id):
        if not user_id or not challenge_slug_or_id:
            return None
        database = get_db()
        doc = database[cls.collection_name].find_one({
            "user_id": str(user_id),
            "$or": [
                {"challenge_slug": str(challenge_slug_or_id)},
                {"challenge_id": str(challenge_slug_or_id)}
            ]
        }, sort=[("submitted_at", -1)])
        return cls(doc) if doc else None

    @classmethod
    def get_by_user_and_challenge(cls, user_id, challenge_id):
        return cls.get_by_user_challenge(user_id, challenge_id)

    @classmethod
    def list_all(cls, status=None):
        database = get_db()
        q = {}
        if status and status != "all":
            q["status"] = status
        cursor = database[cls.collection_name].find(q).sort("submitted_at", -1)
        return [cls(doc) for doc in cursor]
