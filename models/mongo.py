"""
SkillSwap Campus — MongoDB Database & Model Layer
Provides real MongoDB collections, models, indexes, validation,
and duplicate prevention for:
- Users
- Skills
- Swap Requests
- Connections
- Sessions (with Google Calendar & Meet link info)
- Ratings
- Badges
"""

import os
import re
import uuid
import hashlib
import logging
from datetime import datetime, timezone
from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

logger = logging.getLogger(__name__)

# Global MongoDB Client & Database instance
_mongo_client = None
_db = None

def get_db():
    """
    Initializes and returns the MongoDB database.
    If MONGODB_URI is configured and reachable, connects to MongoDB.
    Otherwise, falls back to mongomock for local testing.
    """
    global _mongo_client, _db
    if _db is not None:
        return _db

    from config import Config
    uri = Config.MONGODB_URI
    db_name = Config.MONGODB_DB_NAME or "skillswap_campus"

    if uri and "YOUR_MONGODB" not in uri:
        try:
            from pymongo import MongoClient
            client = MongoClient(uri, serverSelectionTimeoutMS=8000)
            # Test connection
            client.admin.command('ping')
            _mongo_client = client
            _db = client[db_name]
            logger.info(f"[MONGODB] Connected successfully to MongoDB database: {db_name}")
            init_indexes(_db)
            return _db
        except Exception as e:
            logger.warning(f"[MONGODB WARNING] Could not connect to real MongoDB ({e}). Falling back to local mongomock instance.")

    # Fallback to mongomock for local environment or unit testing
    try:
        import mongomock
        logger.info("[MONGODB NOTICE] MONGODB_URI not set or unreachable. Using mongomock in-memory database. MANUAL CONFIGURATION REQUIRED: Set MONGODB_URI in your .env file for production persistence.")
        _mongo_client = mongomock.MongoClient()
        _db = _mongo_client[db_name]
        init_indexes(_db)
        return _db
    except ImportError:
        from pymongo import MongoClient
        _mongo_client = MongoClient("mongodb://127.0.0.1:27017/", serverSelectionTimeoutMS=2000)
        _db = _mongo_client[db_name]
        init_indexes(_db)
        return _db

def init_indexes(db):
    """Creates proper MongoDB indexes and enforces uniqueness."""
    try:
        # Users
        db.users.create_index("email", unique=True)
        db.users.create_index("google_id", sparse=True)

        # Skills
        db.skills.create_index("name", unique=True)

        # Swap Requests
        db.swap_requests.create_index([("sender_id", 1), ("receiver_id", 1), ("status", 1)])
        db.swap_requests.create_index("receiver_id")
        db.swap_requests.create_index("sender_id")

        # Connections (unique pair of users)
        db.connections.create_index([("user1_id", 1), ("user2_id", 1)], unique=True)

        # Sessions
        db.sessions.create_index("connection_id")
        db.sessions.create_index("teacher_id")
        db.sessions.create_index("learner_id")
        db.sessions.create_index("scheduled_date")
        db.sessions.create_index("calendar_event_id", sparse=True)

        # Ratings (single rating per session per reviewer)
        db.ratings.create_index([("session_id", 1), ("reviewer_id", 1)], unique=True)

        # Badges
        db.badges.create_index("slug", unique=True)

        # Messages (direct chat)
        db.messages.create_index([("sender_id", 1), ("receiver_id", 1), ("created_at", 1)])
        db.messages.create_index([("receiver_id", 1), ("is_read", 1)])

        # Courses & Learning Platform
        db.courses.create_index("slug", unique=True)
        db.courses.create_index("category")
        db.courses.create_index("is_published")

        # Assignments
        db.assignments.create_index("course_id")

        # Enrollments (unique student per course)
        db.enrollments.create_index([("user_id", 1), ("course_id", 1)], unique=True)
        db.enrollments.create_index("user_id")

        # Submissions
        db.submissions.create_index([("user_id", 1), ("assignment_id", 1)])
        db.submissions.create_index("status")
        db.submissions.create_index("created_at")

        # Reviews
        db.reviews.create_index("submission_id")

        # Certificates (tamper-proof uniqueness)
        db.certificates.create_index("certificate_id", unique=True)
        db.certificates.create_index([("user_id", 1), ("course_id", 1)], unique=True)
    except Exception as e:
        logger.debug(f"Index creation note: {e}")


def _to_obj_id(val):
    if isinstance(val, ObjectId):
        return val
    try:
        return ObjectId(str(val))
    except Exception:
        return val


class _ModelQueryDescriptor:
    """Provides backward-compatibility shim for legacy SQLAlchemy-style .query calls."""
    def __get__(self, instance, owner):
        class _QueryShim:
            def __init__(self, model_cls):
                self.model_cls = model_cls
            def order_by(self, *args, **kwargs):
                return self
            def filter_by(self, **kwargs):
                return self
            def all(self):
                return self.model_cls.find_all()
            def first(self):
                items = self.model_cls.find_all(limit=1)
                return items[0] if items else None
            def count(self):
                return self.model_cls.count()
        return _QueryShim(owner)


# ==============================================================================
# 1. Skill & SkillItem Models
# ==============================================================================

class Skill:
    collection_name = "skills"
    query = _ModelQueryDescriptor()

    def __init__(self, data=None):
        self._data = data or {}
        self.id = str(self._data.get("_id", ""))
        self.name = self._data.get("name", "")
        self.category = self._data.get("category", "General")
        self.icon = self._data.get("icon", "code")
        self.description = self._data.get("description", "")

    def to_dict(self):
        return self._data

    @classmethod
    def get_by_id(cls, skill_id):
        db = get_db()
        doc = db[cls.collection_name].find_one({"_id": _to_obj_id(skill_id)})
        return cls(doc) if doc else None

    @classmethod
    def get_by_name(cls, name):
        if not name:
            return None
        db = get_db()
        pattern = f"^{re.escape(name.strip())}$"
        doc = db[cls.collection_name].find_one({"name": {"$regex": pattern, "$options": "i"}})
        return cls(doc) if doc else None

    @classmethod
    def create_or_get(cls, name, category="General", icon="code", description=""):
        existing = cls.get_by_name(name)
        if existing:
            return existing
        db = get_db()
        doc = {
            "name": name.strip(),
            "category": category.strip(),
            "icon": icon,
            "description": description.strip(),
            "created_at": datetime.now(timezone.utc)
        }
        res = db[cls.collection_name].insert_one(doc)
        doc["_id"] = res.inserted_id
        return cls(doc)

    @classmethod
    def create(cls, **kwargs):
        return cls.create_or_get(
            name=kwargs.get("name", ""),
            category=kwargs.get("category", "General"),
            icon=kwargs.get("icon", "code"),
            description=kwargs.get("description", "")
        )

    @classmethod
    def find_all(cls, limit=None):
        db = get_db()
        cursor = db[cls.collection_name].find().sort("name", 1)
        if limit:
            cursor = cursor.limit(limit)
        return [cls(doc) for doc in cursor]

    @classmethod
    def count(cls, query=None):
        db = get_db()
        return db[cls.collection_name].count_documents(query or {})


class SkillItem:
    """Represents a skill attached to a user's profile."""
    def __init__(self, name, category="General", proficiency="Intermediate", skill_type="teach", id=None):
        self.name = name
        self.category = category
        self.proficiency = proficiency
        self.skill_type = skill_type
        self.id = id or name

    @property
    def skill(self):
        return self

    def __repr__(self):
        return f"<SkillItem {self.name} ({self.skill_type})>"


# ==============================================================================
# 2. Badge Model
# ==============================================================================

class Badge:
    collection_name = "badges"

    STANDARD_BADGES = [
        {
            "name": "First Swap",
            "slug": "first-swap",
            "description": "Completed first skill exchange on campus",
            "icon": "zap",
            "color": "#2563EB"
        },
        {
            "name": "Knowledge Sharer",
            "slug": "knowledge-sharer",
            "description": "Taught 5 or more peer learning sessions",
            "icon": "book-open",
            "color": "#4F46E5"
        },
        {
            "name": "Fast Learner",
            "slug": "fast-learner",
            "description": "Completed 5 or more student learning sessions",
            "icon": "award",
            "color": "#10B981"
        },
        {
            "name": "Community Builder",
            "slug": "community-builder",
            "description": "Connected and swapped skills with 10+ students",
            "icon": "users",
            "color": "#8B5CF6"
        },
        {
            "name": "Skill Mentor",
            "slug": "skill-mentor",
            "description": "Reached 1000+ XP in skill exchanges",
            "icon": "crown",
            "color": "#F59E0B"
        }
    ]

    def __init__(self, data=None):
        self._data = data or {}
        self.id = str(self._data.get("_id", self._data.get("slug", "")))
        self.name = self._data.get("name", "")
        self.slug = self._data.get("slug", "")
        self.description = self._data.get("description", "")
        self.icon = self._data.get("icon", "award")
        self.color = self._data.get("color", "#2563EB")

    @classmethod
    def get_by_slug(cls, slug):
        db = get_db()
        doc = db[cls.collection_name].find_one({"slug": slug})
        if doc:
            return cls(doc)
        for b in cls.STANDARD_BADGES:
            if b["slug"] == slug:
                return cls(b)
        return None

    @classmethod
    def get_all(cls):
        db = get_db()
        docs = list(db[cls.collection_name].find())
        if not docs:
            # Seed standard badges
            for b in cls.STANDARD_BADGES:
                try:
                    db[cls.collection_name].update_one({"slug": b["slug"]}, {"$set": b}, upsert=True)
                except Exception:
                    pass
            docs = list(db[cls.collection_name].find())
        return [cls(d) for d in docs] if docs else [cls(b) for b in cls.STANDARD_BADGES]


# ==============================================================================
# 3. User Model (Flask-Login compatible)
# ==============================================================================

class User(UserMixin):
    collection_name = "users"
    query = _ModelQueryDescriptor()

    def __init__(self, data=None):
        self._data = data or {}
        self._id = self._data.get("_id")
        self.id = str(self._id) if self._id else ""
        self.email = self._data.get("email", "").lower()
        self.name = self._data.get("name", "")
        self.google_id = self._data.get("google_id")
        self.google_picture = self._data.get("google_picture", "")
        self.google_access_token = self._data.get("google_access_token")
        self.google_refresh_token = self._data.get("google_refresh_token")
        self.google_token_expiry = self._data.get("google_token_expiry")
        self.password_hash = self._data.get("password_hash")
        self.college = self._data.get("college", "")
        self.branch = self._data.get("branch", "")
        self.year = self._data.get("year", "")
        self.bio = self._data.get("bio", "")
        self.avatar_seed = self._data.get("avatar_seed", "")
        self.xp = int(self._data.get("xp", 0))
        self.rating = float(self._data.get("rating", 0.0))
        self.rating_count = int(self._data.get("rating_count", 0))
        self.role = self._data.get("role", "admin" if self.email == "palt51419@gmail.com" else "student")
        self.is_banned = bool(self._data.get("is_banned", False))
        self.ban_reason = self._data.get("ban_reason", "")
        self.created_at = self._data.get("created_at")

    def get_id(self):
        return str(self.id)

    @property
    def is_admin(self):
        return self.role == "admin" or self.email.lower() == "palt51419@gmail.com"

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return not self.is_banned

    @property
    def is_anonymous(self):
        return False

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        self._data["password_hash"] = self.password_hash

    def check_password(self, password):
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    # 5-Tier Progression Levels
    @property
    def level_name(self):
        if self.xp < 100:
            return "Beginner"
        elif self.xp < 250:
            return "Learner"
        elif self.xp < 500:
            return "Skill Builder"
        elif self.xp < 1000:
            return "Knowledge Sharer"
        else:
            return "Skill Mentor"

    @property
    def level_tier(self):
        if self.xp < 100:
            return 1
        elif self.xp < 250:
            return 2
        elif self.xp < 500:
            return 3
        elif self.xp < 1000:
            return 4
        else:
            return 5

    @property
    def next_level_xp(self):
        if self.xp < 100:
            return 100
        elif self.xp < 250:
            return 250
        elif self.xp < 500:
            return 500
        elif self.xp < 1000:
            return 1000
        else:
            return 1000

    @property
    def level_progress_percent(self):
        if self.xp < 100:
            return max(0, min(100, int((self.xp / 100) * 100)))
        elif self.xp < 250:
            return max(0, min(100, int(((self.xp - 100) / 150) * 100)))
        elif self.xp < 500:
            return max(0, min(100, int(((self.xp - 250) / 250) * 100)))
        elif self.xp < 1000:
            return max(0, min(100, int(((self.xp - 500) / 500) * 100)))
        else:
            return 100

    @property
    def level_progress_display(self):
        if self.xp >= 1000:
            return f"{self.xp} XP • Maximum level reached"
        return f"{self.xp} / {self.next_level_xp} XP"

    @property
    def rating_display(self):
        if not self.rating_count or self.rating_count == 0:
            return "New member • No ratings yet"
        return f"★ {self.rating:.1f} ({self.rating_count} ratings)"

    @property
    def has_ratings(self):
        return bool(self.rating_count and self.rating_count > 0)

    @property
    def initials(self):
        parts = self.name.strip().split()
        if not parts:
            return "S"
        if len(parts) == 1:
            return parts[0][:2].upper()
        return (parts[0][0] + parts[-1][0]).upper()

    @property
    def avatar_url(self):
        if self.google_picture:
            return self.google_picture
        seed = self.avatar_seed or self.name.replace(" ", "_")
        return f"https://api.dicebear.com/7.x/notionists/svg?seed={seed}&backgroundColor=e2e8f0,cbd5e1,f1f5f9"

    @property
    def has_google_connected(self):
        return bool(self.google_access_token)

    # Skills accessors
    @property
    def teaching_skills(self):
        raw = self._data.get("teaching_skills", [])
        return [SkillItem(s["name"], s.get("category", "General"), s.get("proficiency", "Intermediate"), "teach", s.get("id")) for s in raw]

    @property
    def learning_skills(self):
        raw = self._data.get("learning_skills", [])
        return [SkillItem(s["name"], s.get("category", "General"), s.get("proficiency", "Beginner"), "learn", s.get("id")) for s in raw]

    @property
    def badges(self):
        slugs = self._data.get("badges", [])
        badge_objs = []
        for slug in slugs:
            b = Badge.get_by_slug(slug)
            if b:
                badge_objs.append(b)
        return badge_objs

    # Compatibility shim for legacy user.user_skills.filter_by(...)
    @property
    def user_skills(self):
        class _UserSkillsProxy:
            def __init__(self, user):
                self.user = user
            def filter_by(self, skill_type="teach"):
                skills = self.user.teaching_skills if skill_type == "teach" else self.user.learning_skills
                class _ListWrapper(list):
                    def all(self):
                        return list(self)
                return _ListWrapper(skills)
        return _UserSkillsProxy(self)

    # Compatibility shim for legacy user.user_badges
    @property
    def user_badges(self):
        class _BadgeProxy:
            def __init__(self, badge):
                self.badge = badge
                self.badge_id = badge.slug
        return [_BadgeProxy(b) for b in self.badges]

    def add_skill(self, name, skill_type="teach", proficiency="Intermediate"):
        """Adds a skill ensuring no duplicates."""
        field = "teaching_skills" if skill_type == "teach" else "learning_skills"
        items = list(self._data.get(field, []))
        norm_name = name.strip()
        # Check duplicate
        for item in items:
            if item["name"].lower() == norm_name.lower():
                return False
        
        # Ensure registered in global skills collection
        Skill.create_or_get(norm_name)

        items.append({
            "name": norm_name,
            "category": "General",
            "proficiency": proficiency,
            "id": norm_name
        })
        self._data[field] = items
        self.save()
        return True

    def remove_skill(self, name_or_id, skill_type="teach"):
        """Removes a skill from user profile."""
        field = "teaching_skills" if skill_type == "teach" else "learning_skills"
        items = list(self._data.get(field, []))
        norm_target = str(name_or_id).lower()
        new_items = [it for it in items if it.get("name", "").lower() != norm_target and str(it.get("id", "")).lower() != norm_target]
        if len(new_items) != len(items):
            self._data[field] = new_items
            self.save()
            return True
        return False

    def add_badge(self, badge_slug):
        """Awards a badge if not already held."""
        current_badges = list(self._data.get("badges", []))
        if badge_slug not in current_badges:
            current_badges.append(badge_slug)
            self._data["badges"] = current_badges
            self.save()
            return True
        return False

    def save(self):
        db = get_db()
        self._data["updated_at"] = datetime.now(timezone.utc)
        self._data["xp"] = int(self.xp)
        self._data["rating"] = float(self.rating)
        self._data["rating_count"] = int(self.rating_count)
        self._data["name"] = self.name
        self._data["email"] = self.email.lower()
        self._data["college"] = self.college
        self._data["branch"] = self.branch
        self._data["year"] = self.year
        self._data["bio"] = self.bio
        self._data["avatar_seed"] = self.avatar_seed
        self._data["google_id"] = self.google_id
        self._data["google_picture"] = self.google_picture
        self._data["google_access_token"] = self.google_access_token
        self._data["google_refresh_token"] = self.google_refresh_token
        self._data["google_token_expiry"] = self.google_token_expiry
        self._data["role"] = getattr(self, "role", "student")
        self._data["is_banned"] = bool(getattr(self, "is_banned", False))
        self._data["ban_reason"] = getattr(self, "ban_reason", "")
        if self.password_hash:
            self._data["password_hash"] = self.password_hash

        if self._id:
            db[self.collection_name].update_one({"_id": self._id}, {"$set": self._data})
        else:
            self._data["created_at"] = datetime.now(timezone.utc)
            res = db[self.collection_name].insert_one(self._data)
            self._id = res.inserted_id
            self.id = str(self._id)
        return self

    def delete(self):
        if self._id:
            User.delete_cascading(self.id)

    @classmethod
    def delete_cascading(cls, user_id):
        """Permanently deletes a user and cascades deletion to all their relations."""
        if not user_id:
            return False
        db = get_db()
        uid = str(user_id)
        oid = _to_obj_id(uid)
        # Delete user
        db[cls.collection_name].delete_one({"_id": oid})
        # Delete connections
        db.connections.delete_many({"$or": [{"user1_id": uid}, {"user2_id": uid}]})
        # Delete swap requests
        db.swap_requests.delete_many({"$or": [{"sender_id": uid}, {"receiver_id": uid}]})
        # Delete messages
        db.messages.delete_many({"$or": [{"sender_id": uid}, {"receiver_id": uid}]})
        # Delete sessions
        db.sessions.delete_many({"$or": [{"teacher_id": uid}, {"learner_id": uid}]})
        # Delete ratings
        db.ratings.delete_many({"$or": [{"reviewer_id": uid}, {"reviewee_id": uid}]})
        return True

    @classmethod
    def create(cls, **kwargs):
        user = cls(kwargs)
        user.save()
        return user

    @classmethod
    def get_by_id(cls, user_id):
        if not user_id:
            return None
        db = get_db()
        doc = db[cls.collection_name].find_one({"_id": _to_obj_id(user_id)})
        return cls(doc) if doc else None

    @classmethod
    def get_by_email(cls, email):
        if not email:
            return None
        db = get_db()
        doc = db[cls.collection_name].find_one({"email": email.strip().lower()})
        return cls(doc) if doc else None

    @classmethod
    def get_by_google_id(cls, google_id):
        if not google_id:
            return None
        db = get_db()
        doc = db[cls.collection_name].find_one({"google_id": google_id})
        return cls(doc) if doc else None

    @classmethod
    def find_all(cls, query=None, limit=None):
        db = get_db()
        cursor = db[cls.collection_name].find(query or {}).sort("created_at", -1)
        if limit:
            cursor = cursor.limit(limit)
        return [cls(doc) for doc in cursor]

    @classmethod
    def count(cls, query=None):
        db = get_db()
        return db[cls.collection_name].count_documents(query or {})


# ==============================================================================
# 4. SwapRequest Model
# ==============================================================================

class SwapRequest:
    collection_name = "swap_requests"

    def __init__(self, data=None):
        self._data = data or {}
        self._id = self._data.get("_id")
        self.id = str(self._id) if self._id else ""
        self.sender_id = str(self._data.get("sender_id", ""))
        self.receiver_id = str(self._data.get("receiver_id", ""))
        self.teach_skill_name = self._data.get("teach_skill_name", "")
        self.learn_skill_name = self._data.get("learn_skill_name", "")
        self.message = self._data.get("message", "")
        self.status = self._data.get("status", "pending")
        self.xp_awarded = bool(self._data.get("xp_awarded", False))
        self.created_at = self._data.get("created_at") or datetime.now(timezone.utc)

    @property
    def sender(self):
        return User.get_by_id(self.sender_id)

    @property
    def receiver(self):
        return User.get_by_id(self.receiver_id)

    @property
    def teach_skill(self):
        return SkillItem(self.teach_skill_name)

    @property
    def learn_skill(self):
        return SkillItem(self.learn_skill_name)

    @property
    def status_label(self):
        labels = {
            "pending": "Waiting",
            "accepted": "Accepted",
            "rejected": "Declined",
            "declined": "Declined",
            "cancelled": "Cancelled"
        }
        return labels.get(self.status, self.status.capitalize())

    def save(self):
        db = get_db()
        self._data["sender_id"] = str(self.sender_id)
        self._data["receiver_id"] = str(self.receiver_id)
        self._data["teach_skill_name"] = self.teach_skill_name
        self._data["learn_skill_name"] = self.learn_skill_name
        self._data["message"] = self.message
        self._data["status"] = self.status
        self._data["xp_awarded"] = bool(self.xp_awarded)
        self._data["updated_at"] = datetime.now(timezone.utc)

        if self._id:
            db[self.collection_name].update_one({"_id": self._id}, {"$set": self._data})
        else:
            self._data["created_at"] = datetime.now(timezone.utc)
            res = db[self.collection_name].insert_one(self._data)
            self._id = res.inserted_id
            self.id = str(self._id)
        return self

    def delete(self):
        if self._id:
            db = get_db()
            db[self.collection_name].delete_one({"_id": self._id})

    @classmethod
    def create(cls, **kwargs):
        req = cls(kwargs)
        req.save()
        return req

    @classmethod
    def get_by_id(cls, req_id):
        db = get_db()
        doc = db[cls.collection_name].find_one({"_id": _to_obj_id(req_id)})
        return cls(doc) if doc else None

    @classmethod
    def find_by_receiver(cls, receiver_id):
        db = get_db()
        docs = db[cls.collection_name].find({"receiver_id": str(receiver_id)}).sort("created_at", -1)
        return [cls(d) for d in docs]

    @classmethod
    def find_by_sender(cls, sender_id):
        db = get_db()
        docs = db[cls.collection_name].find({"sender_id": str(sender_id)}).sort("created_at", -1)
        return [cls(d) for d in docs]

    @classmethod
    def find_pending_between(cls, sender_id, receiver_id):
        db = get_db()
        doc = db[cls.collection_name].find_one({
            "sender_id": str(sender_id),
            "receiver_id": str(receiver_id),
            "status": "pending"
        })
        return cls(doc) if doc else None

    @classmethod
    def count(cls, query=None):
        db = get_db()
        return db[cls.collection_name].count_documents(query or {})


# ==============================================================================
# 5. Connection Model
# ==============================================================================

class Connection:
    collection_name = "connections"

    def __init__(self, data=None):
        self._data = data or {}
        self._id = self._data.get("_id")
        self.id = str(self._id) if self._id else ""
        self.user1_id = str(self._data.get("user1_id", ""))
        self.user2_id = str(self._data.get("user2_id", ""))
        self.swap_request_id = str(self._data.get("swap_request_id", ""))
        self.created_at = self._data.get("created_at") or datetime.now(timezone.utc)

    @property
    def user1(self):
        return User.get_by_id(self.user1_id)

    @property
    def user2(self):
        return User.get_by_id(self.user2_id)

    @property
    def swap_request(self):
        return SwapRequest.get_by_id(self.swap_request_id) if self.swap_request_id else None

    def get_other_user(self, current_user_id):
        return self.get_partner(current_user_id)

    def get_partner(self, current_user_id):
        curr_str = str(current_user_id)
        if self.user1_id == curr_str:
            return User.get_by_id(self.user2_id)
        return User.get_by_id(self.user1_id)

    @property
    def sessions(self):
        class _SessionCountProxy:
            def __init__(self, conn_id):
                self.conn_id = conn_id
            def count(self):
                db = get_db()
                return db["sessions"].count_documents({"connection_id": str(self.conn_id)})
            def all(self):
                db = get_db()
                docs = db["sessions"].find({"connection_id": str(self.conn_id)}).sort("scheduled_date", -1)
                return [Session(d) for d in docs]
        return _SessionCountProxy(self.id)

    def save(self):
        db = get_db()
        # Canonical order: user1_id < user2_id to prevent duplicates
        u1, u2 = sorted([str(self.user1_id), str(self.user2_id)])
        self.user1_id = u1
        self.user2_id = u2
        self._data["user1_id"] = u1
        self._data["user2_id"] = u2
        self._data["swap_request_id"] = str(self.swap_request_id)

        if self._id:
            db[self.collection_name].update_one({"_id": self._id}, {"$set": self._data})
        else:
            self._data["created_at"] = datetime.now(timezone.utc)
            res = db[self.collection_name].insert_one(self._data)
            self._id = res.inserted_id
            self.id = str(self._id)
        return self

    def delete(self):
        if self._id:
            db = get_db()
            db[self.collection_name].delete_one({"_id": self._id})

    @classmethod
    def create(cls, **kwargs):
        conn = cls(kwargs)
        conn.save()
        return conn

    @classmethod
    def get_by_id(cls, conn_id):
        db = get_db()
        doc = db[cls.collection_name].find_one({"_id": _to_obj_id(conn_id)})
        return cls(doc) if doc else None

    @classmethod
    def find_between(cls, user_a_id, user_b_id):
        u_a = str(user_a_id)
        u_b = str(user_b_id)
        u1, u2 = sorted([u_a, u_b])
        db = get_db()
        doc = db[cls.collection_name].find_one({
            "$or": [
                {"user1_id": u1, "user2_id": u2},
                {"user1_id": u_a, "user2_id": u_b},
                {"user1_id": u_b, "user2_id": u_a}
            ]
        })
        return cls(doc) if doc else None

    @classmethod
    def find_by_user(cls, user_id):
        u_str = str(user_id)
        db = get_db()
        docs = db[cls.collection_name].find({
            "$or": [{"user1_id": u_str}, {"user2_id": u_str}]
        }).sort("created_at", -1)
        return [cls(d) for d in docs]

    @classmethod
    def count(cls, query=None):
        db = get_db()
        return db[cls.collection_name].count_documents(query or {})


# ==============================================================================
# 6. Session Model
# ==============================================================================

class Session:
    collection_name = "sessions"

    def __init__(self, data=None):
        self._data = data or {}
        self._id = self._data.get("_id")
        self.id = str(self._id) if self._id else ""
        self.connection_id = str(self._data.get("connection_id", ""))
        self.teacher_id = str(self._data.get("teacher_id", ""))
        self.learner_id = str(self._data.get("learner_id", ""))
        self.skill_name = self._data.get("skill_name", "")
        self.title = self._data.get("title", "")
        self.notes = self._data.get("notes", "")
        self.scheduled_date = self._data.get("scheduled_date", "")
        self.scheduled_time = self._data.get("scheduled_time", "")
        self.duration_minutes = int(self._data.get("duration_minutes", 60))
        self.status = self._data.get("status", "scheduled")
        self.meeting_link = self._data.get("meeting_link", "")
        self.calendar_event_id = self._data.get("calendar_event_id", "")
        self.calendar_event_data = self._data.get("calendar_event_data", {})
        self.xp_awarded = bool(self._data.get("xp_awarded", False))
        self.created_at = self._data.get("created_at") or datetime.now(timezone.utc)
        self.completed_at = self._data.get("completed_at")

    @property
    def teacher(self):
        return User.get_by_id(self.teacher_id)

    @property
    def learner(self):
        return User.get_by_id(self.learner_id)

    @property
    def skill(self):
        return SkillItem(self.skill_name)

    @property
    def rating(self):
        db = get_db()
        doc = db["ratings"].find_one({"session_id": str(self.id)})
        return Rating(doc) if doc else None

    @property
    def connection(self):
        return Connection.get_by_id(self.connection_id) if self.connection_id else None

    def get_other_user(self, current_user_id):
        curr_str = str(current_user_id)
        if self.teacher_id == curr_str:
            return self.learner
        return self.teacher

    def save(self):
        db = get_db()
        self._data["connection_id"] = str(self.connection_id)
        self._data["teacher_id"] = str(self.teacher_id)
        self._data["learner_id"] = str(self.learner_id)
        self._data["skill_name"] = self.skill_name
        self._data["title"] = self.title
        self._data["notes"] = self.notes
        self._data["scheduled_date"] = self.scheduled_date
        self._data["scheduled_time"] = self.scheduled_time
        self._data["duration_minutes"] = int(self.duration_minutes)
        self._data["status"] = self.status
        self._data["meeting_link"] = self.meeting_link
        self._data["calendar_event_id"] = self.calendar_event_id
        self._data["calendar_event_data"] = self.calendar_event_data
        self._data["xp_awarded"] = bool(self.xp_awarded)
        if self.completed_at:
            self._data["completed_at"] = self.completed_at

        if self._id:
            db[self.collection_name].update_one({"_id": self._id}, {"$set": self._data})
        else:
            self._data["created_at"] = datetime.now(timezone.utc)
            res = db[self.collection_name].insert_one(self._data)
            self._id = res.inserted_id
            self.id = str(self._id)
        return self

    def delete(self):
        if self._id:
            db = get_db()
            db[self.collection_name].delete_one({"_id": self._id})

    @classmethod
    def create(cls, **kwargs):
        sess = cls(kwargs)
        sess.save()
        return sess

    @classmethod
    def get_by_id(cls, sess_id):
        db = get_db()
        doc = db[cls.collection_name].find_one({"_id": _to_obj_id(sess_id)})
        return cls(doc) if doc else None

    @classmethod
    def find_upcoming_for_user(cls, user_id, limit=3):
        u_str = str(user_id)
        db = get_db()
        docs = db[cls.collection_name].find({
            "$or": [{"teacher_id": u_str}, {"learner_id": u_str}],
            "status": "scheduled"
        }).sort([("scheduled_date", 1), ("scheduled_time", 1)]).limit(limit)
        return [cls(d) for d in docs]

    @classmethod
    def find_by_user(cls, user_id, status=None):
        u_str = str(user_id)
        query = {"$or": [{"teacher_id": u_str}, {"learner_id": u_str}]}
        if status:
            if isinstance(status, list):
                query["status"] = {"$in": status}
            else:
                query["status"] = status
        db = get_db()
        sort_order = [("scheduled_date", 1), ("scheduled_time", 1)] if status == "scheduled" else [("scheduled_date", -1)]
        docs = db[cls.collection_name].find(query).sort(sort_order)
        return [cls(d) for d in docs]

    @classmethod
    def count(cls, query=None):
        db = get_db()
        return db[cls.collection_name].count_documents(query or {})


# ==============================================================================
# 7. Rating Model
# ==============================================================================

class Rating:
    collection_name = "ratings"

    def __init__(self, data=None):
        self._data = data or {}
        self._id = self._data.get("_id")
        self.id = str(self._id) if self._id else ""
        self.session_id = str(self._data.get("session_id", ""))
        self.reviewer_id = str(self._data.get("reviewer_id", ""))
        self.reviewee_id = str(self._data.get("reviewee_id", ""))
        self.score = int(self._data.get("score", 5))
        self.feedback = self._data.get("feedback", "")
        self.xp_awarded = bool(self._data.get("xp_awarded", False))
        self.created_at = self._data.get("created_at") or datetime.now(timezone.utc)

    @property
    def reviewer(self):
        return User.get_by_id(self.reviewer_id)

    @property
    def reviewee(self):
        return User.get_by_id(self.reviewee_id)

    @property
    def session(self):
        return Session.get_by_id(self.session_id)

    def save(self):
        db = get_db()
        self._data["session_id"] = str(self.session_id)
        self._data["reviewer_id"] = str(self.reviewer_id)
        self._data["reviewee_id"] = str(self.reviewee_id)
        self._data["score"] = int(self.score)
        self._data["feedback"] = self.feedback
        self._data["xp_awarded"] = bool(self.xp_awarded)

        if self._id:
            db[self.collection_name].update_one({"_id": self._id}, {"$set": self._data})
        else:
            self._data["created_at"] = datetime.now(timezone.utc)
            res = db[self.collection_name].insert_one(self._data)
            self._id = res.inserted_id
            self.id = str(self._id)
        return self

    @classmethod
    def create(cls, **kwargs):
        rating = cls(kwargs)
        rating.save()
        return rating

    @classmethod
    def get_by_id(cls, rating_id):
        db = get_db()
        doc = db[cls.collection_name].find_one({"_id": _to_obj_id(rating_id)})
        return cls(doc) if doc else None

    @classmethod
    def find_by_session_and_reviewer(cls, session_id, reviewer_id):
        db = get_db()
        doc = db[cls.collection_name].find_one({
            "session_id": str(session_id),
            "reviewer_id": str(reviewer_id)
        })
        return cls(doc) if doc else None

    @classmethod
    def find_by_reviewee(cls, reviewee_id):
        db = get_db()
        docs = db[cls.collection_name].find({"reviewee_id": str(reviewee_id)}).sort("created_at", -1)
        return [cls(d) for d in docs]

    @classmethod
    def count(cls, query=None):
        db = get_db()
        return db[cls.collection_name].count_documents(query or {})


# ==============================================================================
# 8. Message Model (Direct Chat between Connections)
# ==============================================================================

class Message:
    collection_name = "messages"
    query = _ModelQueryDescriptor()

    def __init__(self, data=None):
        self._data = data or {}
        self._id = self._data.get("_id")
        self.id = str(self._id) if self._id else ""
        self.sender_id = str(self._data.get("sender_id", ""))
        self.receiver_id = str(self._data.get("receiver_id", ""))
        self.text = self._data.get("text", "")
        self.is_read = bool(self._data.get("is_read", False))
        self.is_edited = bool(self._data.get("is_edited", False))
        self.created_at = self._data.get("created_at") or datetime.now(timezone.utc)

    @property
    def sender(self):
        return User.get_by_id(self.sender_id)

    @property
    def receiver(self):
        return User.get_by_id(self.receiver_id)

    def to_dict(self):
        created_str = ""
        iso_str = ""
        if isinstance(self.created_at, datetime):
            if self.created_at.tzinfo is None:
                iso_str = self.created_at.replace(tzinfo=timezone.utc).isoformat()
            else:
                iso_str = self.created_at.isoformat()
            created_str = self.created_at.strftime("%I:%M %p")
        elif self.created_at:
            created_str = str(self.created_at)
            iso_str = str(self.created_at)
        return {
            "id": str(self.id),
            "sender_id": str(self.sender_id),
            "receiver_id": str(self.receiver_id),
            "text": self.text,
            "is_read": self.is_read,
            "is_edited": bool(self.is_edited),
            "created_at": created_str,
            "timestamp": iso_str
        }

    @classmethod
    def get_by_id(cls, message_id):
        if not message_id:
            return None
        db = get_db()
        doc = None
        try:
            from bson import ObjectId
            doc = db[cls.collection_name].find_one({"_id": ObjectId(str(message_id))})
        except Exception:
            pass
        if not doc:
            doc = db[cls.collection_name].find_one({"_id": str(message_id)})
        return cls(doc) if doc else None

    @classmethod
    def edit_message(cls, message_id, user_id, new_text):
        clean_text = str(new_text or "").strip()
        if not clean_text or not message_id or not user_id:
            return None
        db = get_db()
        msg = cls.get_by_id(message_id)
        if not msg:
            return None
        if str(msg.sender_id) != str(user_id):
            return None
        
        update_data = {
            "text": clean_text,
            "is_edited": True,
            "updated_at": datetime.now(timezone.utc)
        }
        try:
            from bson import ObjectId
            db[cls.collection_name].update_one(
                {"_id": ObjectId(str(message_id))},
                {"$set": update_data}
            )
        except Exception:
            db[cls.collection_name].update_one(
                {"_id": str(message_id)},
                {"$set": update_data}
            )
        return cls.get_by_id(message_id)

    @classmethod
    def delete_message(cls, message_id, user_id):
        if not message_id or not user_id:
            return False
        db = get_db()
        msg = cls.get_by_id(message_id)
        if not msg:
            return False
        if str(msg.sender_id) != str(user_id):
            return False
        
        try:
            from bson import ObjectId
            res = db[cls.collection_name].delete_one({"_id": ObjectId(str(message_id))})
            return res.deleted_count > 0
        except Exception:
            res = db[cls.collection_name].delete_one({"_id": str(message_id)})
            return res.deleted_count > 0

    @classmethod
    def send(cls, sender_id, receiver_id, text):
        clean_text = str(text or "").strip()
        if not clean_text or not sender_id or not receiver_id:
            return None
        db = get_db()
        now = datetime.now(timezone.utc)
        doc = {
            "sender_id": str(sender_id),
            "receiver_id": str(receiver_id),
            "text": clean_text,
            "is_read": False,
            "created_at": now
        }
        res = db[cls.collection_name].insert_one(doc)
        doc["_id"] = res.inserted_id
        return cls(doc)

    @classmethod
    def get_conversation(cls, user1_id, user2_id, limit=200):
        db = get_db()
        u1 = str(user1_id)
        u2 = str(user2_id)
        query = {
            "$or": [
                {"sender_id": u1, "receiver_id": u2},
                {"sender_id": u2, "receiver_id": u1}
            ]
        }
        total = db[cls.collection_name].count_documents(query)
        skip_count = max(0, total - limit) if limit else 0
        docs = db[cls.collection_name].find(query).sort("created_at", 1).skip(skip_count)
        return [cls(d) for d in docs]

    @classmethod
    def mark_conversation_as_read(cls, current_user_id, partner_id):
        db = get_db()
        db[cls.collection_name].update_many(
            {"sender_id": str(partner_id), "receiver_id": str(current_user_id), "is_read": False},
            {"$set": {"is_read": True}}
        )

    @classmethod
    def count(cls, query=None):
        db = get_db()
        return db[cls.collection_name].count_documents(query or {})

    @classmethod
    def count_unread(cls, user_id):
        db = get_db()
        return db[cls.collection_name].count_documents({"receiver_id": str(user_id), "is_read": False})

    @classmethod
    def get_latest_message(cls, user1_id, user2_id):
        db = get_db()
        u1 = str(user1_id)
        u2 = str(user2_id)
        doc = db[cls.collection_name].find_one(
            {"$or": [
                {"sender_id": u1, "receiver_id": u2},
                {"sender_id": u2, "receiver_id": u1}
            ]},
            sort=[("created_at", -1)]
        )
        return cls(doc) if doc else None


# ==============================================================================
# 9. Learn & Build — Courses, Assignments, Submissions & Certificates
# ==============================================================================

def extract_youtube_id(url):
    """Extracts YouTube 11-char video ID or playlist ID from diverse YouTube URL formats."""
    if not url:
        return ""
    url = str(url).strip()
    if "list=" in url:
        match = re.search(r"list=([a-zA-Z0-9_-]+)", url)
        if match:
            return "playlist:" + match.group(1)
    patterns = [
        r"(?:v=|\/embed\/|\/v\/|youtu\.be\/|\/shorts\/)([0-9A-Za-z_-]{11})(?:\&|\?|$)",
        r"^([0-9A-Za-z_-]{11})$"
    ]
    for pattern in patterns:
        m = re.search(pattern, url)
        if m:
            return m.group(1)
    return ""


def slugify(text):
    """Converts a title or string into a clean, URL-friendly slug."""
    if not text:
        return "course"
    text = str(text).lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    return text.strip('-') or "course"


class Course:
    collection_name = "courses"

    def __init__(self, data=None):
        self._data = data or {}
        self._id = self._data.get("_id")
        self.id = str(self._id) if self._id else ""
        self.title = self._data.get("title", "")
        self.slug = self._data.get("slug", "") or slugify(self.title)
        self.thumbnail_url = self._data.get("thumbnail_url", "")
        self.category = self._data.get("category", "Programming")
        self.description = self._data.get("description", "")
        self.learning_objectives = self._data.get("learning_objectives", [])
        self.difficulty = self._data.get("difficulty", "Beginner")  # Beginner, Intermediate, Advanced
        self.estimated_duration = self._data.get("estimated_duration", "10 Hours")
        self.instructor = self._data.get("instructor", "Curated Instructor")
        self.youtube_url = self._data.get("youtube_url", "")
        self.youtube_video_id = self._data.get("youtube_video_id", "") or extract_youtube_id(self.youtube_url)
        self.is_published = bool(self._data.get("is_published", True))
        self.created_at = self._data.get("created_at") or datetime.now(timezone.utc)
        self.updated_at = self._data.get("updated_at") or datetime.now(timezone.utc)

    @property
    def embed_url(self):
        yt_id = self.youtube_video_id or extract_youtube_id(self.youtube_url)
        if not yt_id:
            return ""
        if yt_id.startswith("playlist:"):
            playlist_id = yt_id.split(":", 1)[1]
            return f"https://www.youtube-nocookie.com/embed/videoseries?list={playlist_id}"
        return f"https://www.youtube-nocookie.com/embed/{yt_id}"

    @property
    def fallback_thumbnail(self):
        if self.thumbnail_url:
            return self.thumbnail_url
        yt_id = self.youtube_video_id or extract_youtube_id(self.youtube_url)
        if yt_id and not yt_id.startswith("playlist:"):
            return f"https://img.youtube.com/vi/{yt_id}/hqdefault.jpg"
        return "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=800&auto=format&fit=crop&q=80"

    @property
    def assignment(self):
        return Assignment.get_by_course(self.id)

    @property
    def enrolled_count(self):
        db = get_db()
        return db.enrollments.count_documents({"course_id": str(self.id)})

    def save(self):
        db = get_db()
        if not self.slug:
            self.slug = slugify(self.title)
        if not self.youtube_video_id and self.youtube_url:
            self.youtube_video_id = extract_youtube_id(self.youtube_url)

        self._data["title"] = self.title
        self._data["slug"] = self.slug
        self._data["thumbnail_url"] = self.thumbnail_url
        self._data["category"] = self.category
        self._data["description"] = self.description
        self._data["learning_objectives"] = self.learning_objectives if isinstance(self.learning_objectives, list) else [self.learning_objectives]
        self._data["difficulty"] = self.difficulty
        self._data["estimated_duration"] = self.estimated_duration
        self._data["instructor"] = self.instructor
        self._data["youtube_url"] = self.youtube_url
        self._data["youtube_video_id"] = self.youtube_video_id
        self._data["is_published"] = bool(self.is_published)
        self._data["updated_at"] = datetime.now(timezone.utc)

        if self._id:
            db[self.collection_name].update_one({"_id": self._id}, {"$set": self._data})
        else:
            self._data["created_at"] = datetime.now(timezone.utc)
            res = db[self.collection_name].insert_one(self._data)
            self._id = res.inserted_id
            self.id = str(self._id)
        return self

    def delete(self):
        if self._id:
            db = get_db()
            db.assignments.delete_many({"course_id": str(self.id)})
            db.enrollments.delete_many({"course_id": str(self.id)})
            db.submissions.delete_many({"course_id": str(self.id)})
            db.certificates.delete_many({"course_id": str(self.id)})
            db[self.collection_name].delete_one({"_id": self._id})

    @classmethod
    def get_by_id(cls, course_id):
        if not course_id:
            return None
        db = get_db()
        doc = db[cls.collection_name].find_one({"_id": _to_obj_id(course_id)})
        return cls(doc) if doc else None

    @classmethod
    def get_by_slug(cls, slug):
        if not slug:
            return None
        db = get_db()
        doc = db[cls.collection_name].find_one({"slug": slug.strip()})
        return cls(doc) if doc else None

    @classmethod
    def find_all(cls, query=None, limit=None, skip=0, sort=None):
        db = get_db()
        cursor = db[cls.collection_name].find(query or {})
        if sort:
            cursor = cursor.sort(sort)
        else:
            cursor = cursor.sort("created_at", -1)
        if skip:
            cursor = cursor.skip(skip)
        if limit:
            cursor = cursor.limit(limit)
        return [cls(d) for d in cursor]

    @classmethod
    def count(cls, query=None):
        db = get_db()
        return db[cls.collection_name].count_documents(query or {})


class Assignment:
    collection_name = "assignments"

    DEFAULT_RUBRIC = [
        {"criterion": "Core Functionality & Requirements", "max_points": 40, "description": "All specified mandatory features implemented and functional."},
        {"criterion": "Code Quality, Architecture & Structure", "max_points": 30, "description": "Clean, organized, readable code with sensible design patterns."},
        {"criterion": "Live Deployment & Practical Testing", "max_points": 20, "description": "Application successfully deployed, responsive, and working smoothly online."},
        {"criterion": "Documentation & Repository Quality", "max_points": 10, "description": "Clear README with project overview, setup instructions, and tech stack details."}
    ]

    def __init__(self, data=None):
        self._data = data or {}
        self._id = self._data.get("_id")
        self.id = str(self._id) if self._id else ""
        self.course_id = str(self._data.get("course_id", ""))
        self.title = self._data.get("title", "")
        self.short_description = self._data.get("short_description", "")
        self.problem_statement = self._data.get("problem_statement", "")
        self.required_features = self._data.get("required_features", [])
        self.optional_features = self._data.get("optional_features", [])
        self.tech_requirements = self._data.get("tech_requirements", "")
        self.is_deployment_required = bool(self._data.get("is_deployment_required", True))
        self.rubric = self._data.get("rubric") or self.DEFAULT_RUBRIC
        self.is_published = bool(self._data.get("is_published", True))
        self.created_at = self._data.get("created_at") or datetime.now(timezone.utc)
        self.updated_at = self._data.get("updated_at") or datetime.now(timezone.utc)

    @property
    def course(self):
        return Course.get_by_id(self.course_id)

    def save(self):
        db = get_db()
        self._data["course_id"] = str(self.course_id)
        self._data["title"] = self.title
        self._data["short_description"] = self.short_description
        self._data["problem_statement"] = self.problem_statement
        self._data["required_features"] = self.required_features if isinstance(self.required_features, list) else [self.required_features]
        self._data["optional_features"] = self.optional_features if isinstance(self.optional_features, list) else [self.optional_features]
        self._data["tech_requirements"] = self.tech_requirements
        self._data["is_deployment_required"] = bool(self.is_deployment_required)
        self._data["rubric"] = self.rubric if isinstance(self.rubric, list) else self.DEFAULT_RUBRIC
        self._data["is_published"] = bool(self.is_published)
        self._data["updated_at"] = datetime.now(timezone.utc)

        if self._id:
            db[self.collection_name].update_one({"_id": self._id}, {"$set": self._data})
        else:
            self._data["created_at"] = datetime.now(timezone.utc)
            res = db[self.collection_name].insert_one(self._data)
            self._id = res.inserted_id
            self.id = str(self._id)
        return self

    def delete(self):
        if self._id:
            db = get_db()
            db[self.collection_name].delete_one({"_id": self._id})

    @classmethod
    def get_by_id(cls, assignment_id):
        if not assignment_id:
            return None
        db = get_db()
        doc = db[cls.collection_name].find_one({"_id": _to_obj_id(assignment_id)})
        return cls(doc) if doc else None

    @classmethod
    def get_by_course(cls, course_id):
        if not course_id:
            return None
        db = get_db()
        doc = db[cls.collection_name].find_one({"course_id": str(course_id)})
        return cls(doc) if doc else None


class Enrollment:
    collection_name = "enrollments"

    def __init__(self, data=None):
        self._data = data or {}
        self._id = self._data.get("_id")
        self.id = str(self._id) if self._id else ""
        self.user_id = str(self._data.get("user_id", ""))
        self.course_id = str(self._data.get("course_id", ""))
        self.status = self._data.get("status", "enrolled")  # enrolled, in_progress, completed
        self.created_at = self._data.get("created_at") or datetime.now(timezone.utc)
        self.updated_at = self._data.get("updated_at") or datetime.now(timezone.utc)

    @property
    def user(self):
        return User.get_by_id(self.user_id)

    @property
    def course(self):
        return Course.get_by_id(self.course_id)

    @property
    def submission(self):
        course = self.course
        if course and course.assignment:
            return Submission.get_latest(self.user_id, course.assignment.id)
        return None

    @property
    def certificate(self):
        return Certificate.get_by_user_course(self.user_id, self.course_id)

    @property
    def status_label(self):
        labels = {
            "enrolled": "Enrolled",
            "in_progress": "In Progress",
            "completed": "Completed & Certified"
        }
        return labels.get(self.status, self.status.capitalize())

    def save(self):
        db = get_db()
        self._data["user_id"] = str(self.user_id)
        self._data["course_id"] = str(self.course_id)
        self._data["status"] = self.status
        self._data["updated_at"] = datetime.now(timezone.utc)

        if self._id:
            db[self.collection_name].update_one({"_id": self._id}, {"$set": self._data})
        else:
            self._data["created_at"] = datetime.now(timezone.utc)
            res = db[self.collection_name].insert_one(self._data)
            self._id = res.inserted_id
            self.id = str(self._id)
        return self

    def delete(self):
        if self._id:
            db = get_db()
            db[self.collection_name].delete_one({"_id": self._id})

    @classmethod
    def get_by_user_course(cls, user_id, course_id):
        if not user_id or not course_id:
            return None
        db = get_db()
        doc = db[cls.collection_name].find_one({"user_id": str(user_id), "course_id": str(course_id)})
        return cls(doc) if doc else None

    @classmethod
    def find_by_user(cls, user_id):
        if not user_id:
            return []
        db = get_db()
        docs = db[cls.collection_name].find({"user_id": str(user_id)}).sort("created_at", -1)
        return [cls(d) for d in docs]

    @classmethod
    def count(cls, query=None):
        db = get_db()
        return db[cls.collection_name].count_documents(query or {})


class Submission:
    collection_name = "submissions"

    STATUS_PENDING = "pending_review"
    STATUS_CHANGES = "changes_requested"
    STATUS_REJECTED = "rejected"
    STATUS_APPROVED = "approved"

    def __init__(self, data=None):
        self._data = data or {}
        self._id = self._data.get("_id")
        self.id = str(self._id) if self._id else ""
        self.assignment_id = str(self._data.get("assignment_id", ""))
        self.course_id = str(self._data.get("course_id", ""))
        self.user_id = str(self._data.get("user_id", ""))
        self.title = self._data.get("title", "")
        self.description = self._data.get("description", "")
        self.github_url = self._data.get("github_url", "")
        self.deployment_url = self._data.get("deployment_url", "")
        self.tech_stack = self._data.get("tech_stack", "")
        self.status = self._data.get("status", self.STATUS_PENDING)
        self.reviewer_id = str(self._data.get("reviewer_id", ""))
        self.review_feedback = self._data.get("review_feedback", "")
        self.reviewed_at = self._data.get("reviewed_at")
        self.created_at = self._data.get("created_at") or datetime.now(timezone.utc)
        self.updated_at = self._data.get("updated_at") or datetime.now(timezone.utc)

    @property
    def user(self):
        return User.get_by_id(self.user_id)

    @property
    def course(self):
        return Course.get_by_id(self.course_id)

    @property
    def assignment(self):
        return Assignment.get_by_id(self.assignment_id)

    @property
    def reviewer(self):
        return User.get_by_id(self.reviewer_id) if self.reviewer_id else None

    @property
    def review(self):
        return Review.get_by_submission(self.id)

    @property
    def status_label(self):
        labels = {
            self.STATUS_PENDING: "Pending Review",
            self.STATUS_CHANGES: "Changes Requested",
            self.STATUS_REJECTED: "Needs Revision / Rejected",
            self.STATUS_APPROVED: "Approved & Certified"
        }
        return labels.get(self.status, self.status.replace("_", " ").title())

    @property
    def status_badge_class(self):
        classes = {
            self.STATUS_PENDING: "badge-warning",
            self.STATUS_CHANGES: "badge-info",
            self.STATUS_REJECTED: "badge-danger",
            self.STATUS_APPROVED: "badge-success"
        }
        return classes.get(self.status, "badge-secondary")

    def save(self):
        db = get_db()
        self._data["assignment_id"] = str(self.assignment_id)
        self._data["course_id"] = str(self.course_id)
        self._data["user_id"] = str(self.user_id)
        self._data["title"] = self.title
        self._data["description"] = self.description
        self._data["github_url"] = self.github_url
        self._data["deployment_url"] = self.deployment_url
        self._data["tech_stack"] = self.tech_stack
        self._data["status"] = self.status
        self._data["reviewer_id"] = str(self.reviewer_id) if self.reviewer_id else ""
        self._data["review_feedback"] = self.review_feedback
        self._data["reviewed_at"] = self.reviewed_at
        self._data["updated_at"] = datetime.now(timezone.utc)

        if self._id:
            db[self.collection_name].update_one({"_id": self._id}, {"$set": self._data})
        else:
            self._data["created_at"] = datetime.now(timezone.utc)
            res = db[self.collection_name].insert_one(self._data)
            self._id = res.inserted_id
            self.id = str(self._id)
        return self

    def delete(self):
        if self._id:
            db = get_db()
            db.reviews.delete_many({"submission_id": str(self.id)})
            db[self.collection_name].delete_one({"_id": self._id})

    @classmethod
    def get_by_id(cls, submission_id):
        if not submission_id:
            return None
        db = get_db()
        doc = db[cls.collection_name].find_one({"_id": _to_obj_id(submission_id)})
        return cls(doc) if doc else None

    @classmethod
    def get_latest(cls, user_id, assignment_id):
        if not user_id or not assignment_id:
            return None
        db = get_db()
        doc = db[cls.collection_name].find_one(
            {"user_id": str(user_id), "assignment_id": str(assignment_id)},
            sort=[("created_at", -1)]
        )
        return cls(doc) if doc else None

    @classmethod
    def find_by_user(cls, user_id):
        if not user_id:
            return []
        db = get_db()
        docs = db[cls.collection_name].find({"user_id": str(user_id)}).sort("created_at", -1)
        return [cls(d) for d in docs]

    @classmethod
    def find_all(cls, query=None, limit=None, skip=0, sort=None):
        db = get_db()
        cursor = db[cls.collection_name].find(query or {})
        if sort:
            cursor = cursor.sort(sort)
        else:
            cursor = cursor.sort("created_at", -1)
        if skip:
            cursor = cursor.skip(skip)
        if limit:
            cursor = cursor.limit(limit)
        return [cls(d) for d in cursor]

    @classmethod
    def count(cls, query=None):
        db = get_db()
        return db[cls.collection_name].count_documents(query or {})


class Review:
    collection_name = "reviews"

    def __init__(self, data=None):
        self._data = data or {}
        self._id = self._data.get("_id")
        self.id = str(self._id) if self._id else ""
        self.submission_id = str(self._data.get("submission_id", ""))
        self.reviewer_id = str(self._data.get("reviewer_id", ""))
        self.decision = self._data.get("decision", "pending")  # approved, changes_requested, rejected
        self.scores = self._data.get("scores", {})  # { "Criterion": score }
        self.total_score = self._data.get("total_score", 0)
        self.max_score = self._data.get("max_score", 100)
        self.feedback = self._data.get("feedback", "")
        self.created_at = self._data.get("created_at") or datetime.now(timezone.utc)

    @property
    def reviewer(self):
        return User.get_by_id(self.reviewer_id)

    @property
    def submission(self):
        return Submission.get_by_id(self.submission_id)

    def save(self):
        db = get_db()
        self._data["submission_id"] = str(self.submission_id)
        self._data["reviewer_id"] = str(self.reviewer_id)
        self._data["decision"] = self.decision
        self._data["scores"] = self.scores
        self._data["total_score"] = self.total_score
        self._data["max_score"] = self.max_score
        self._data["feedback"] = self.feedback
        self._data["created_at"] = self.created_at

        if self._id:
            db[self.collection_name].update_one({"_id": self._id}, {"$set": self._data})
        else:
            res = db[self.collection_name].insert_one(self._data)
            self._id = res.inserted_id
            self.id = str(self._id)
        return self

    @classmethod
    def get_by_submission(cls, submission_id):
        if not submission_id:
            return None
        db = get_db()
        doc = db[cls.collection_name].find_one({"submission_id": str(submission_id)}, sort=[("created_at", -1)])
        return cls(doc) if doc else None


class Certificate:
    collection_name = "certificates"

    def __init__(self, data=None):
        self._data = data or {}
        self._id = self._data.get("_id")
        self.id = str(self._id) if self._id else ""
        self.certificate_id = self._data.get("certificate_id", "")
        self.user_id = str(self._data.get("user_id", ""))
        self.user_name = self._data.get("user_name", "")
        self.user_email = self._data.get("user_email", "")
        self.course_id = str(self._data.get("course_id", ""))
        self.course_title = self._data.get("course_title", "")
        self.assignment_id = str(self._data.get("assignment_id", ""))
        self.submission_id = str(self._data.get("submission_id", ""))
        self.issued_at = self._data.get("issued_at") or datetime.now(timezone.utc)
        self.verification_hash = self._data.get("verification_hash", "")

    @property
    def user(self):
        return User.get_by_id(self.user_id)

    @property
    def course(self):
        return Course.get_by_id(self.course_id)

    @property
    def submission(self):
        return Submission.get_by_id(self.submission_id)

    @property
    def formatted_date(self):
        if isinstance(self.issued_at, datetime):
            return self.issued_at.strftime("%B %d, %Y")
        return str(self.issued_at)

    def save(self):
        db = get_db()
        self._data["certificate_id"] = self.certificate_id
        self._data["user_id"] = str(self.user_id)
        self._data["user_name"] = self.user_name
        self._data["user_email"] = self.user_email
        self._data["course_id"] = str(self.course_id)
        self._data["course_title"] = self.course_title
        self._data["assignment_id"] = str(self.assignment_id)
        self._data["submission_id"] = str(self.submission_id)
        self._data["issued_at"] = self.issued_at
        self._data["verification_hash"] = self.verification_hash

        if self._id:
            db[self.collection_name].update_one({"_id": self._id}, {"$set": self._data})
        else:
            res = db[self.collection_name].insert_one(self._data)
            self._id = res.inserted_id
            self.id = str(self._id)
        return self

    @classmethod
    def generate_cert_id(cls):
        year = datetime.now().year
        token = uuid.uuid4().hex[:8].upper()
        return f"SR-{year}-{token}"

    @classmethod
    def get_by_id(cls, cert_id):
        if not cert_id:
            return None
        db = get_db()
        doc = db[cls.collection_name].find_one({"_id": _to_obj_id(cert_id)})
        return cls(doc) if doc else None

    @classmethod
    def get_by_cert_id(cls, cert_id):
        if not cert_id:
            return None
        db = get_db()
        doc = db[cls.collection_name].find_one({"certificate_id": cert_id.strip().upper()})
        if not doc:
            doc = db[cls.collection_name].find_one({"certificate_id": cert_id.strip()})
        return cls(doc) if doc else None

    @classmethod
    def get_by_user_course(cls, user_id, course_id):
        if not user_id or not course_id:
            return None
        db = get_db()
        doc = db[cls.collection_name].find_one({"user_id": str(user_id), "course_id": str(course_id)})
        return cls(doc) if doc else None

    @classmethod
    def find_by_user(cls, user_id):
        if not user_id:
            return []
        db = get_db()
        docs = db[cls.collection_name].find({"user_id": str(user_id)}).sort("issued_at", -1)
        return [cls(d) for d in docs]

    @classmethod
    def issue(cls, user, course, assignment=None, submission=None):
        """Atomically checks and issues a verified certificate for a course completion."""
        existing = cls.get_by_user_course(user.id, course.id)
        if existing:
            return existing

        cert_id = cls.generate_cert_id()
        issued_at = datetime.now(timezone.utc)
        raw_hash_data = f"{cert_id}:{user.id}:{course.id}:{issued_at.isoformat()}"
        verification_hash = hashlib.sha256(raw_hash_data.encode("utf-8")).hexdigest()[:24]

        cert = cls({
            "certificate_id": cert_id,
            "user_id": str(user.id),
            "user_name": user.name,
            "user_email": user.email,
            "course_id": str(course.id),
            "course_title": course.title,
            "assignment_id": str(assignment.id if assignment else ""),
            "submission_id": str(submission.id if submission else ""),
            "issued_at": issued_at,
            "verification_hash": verification_hash
        })
        cert.save()

        # Update enrollment status to completed
        enrollment = Enrollment.get_by_user_course(user.id, course.id)
        if enrollment:
            enrollment.status = "completed"
            enrollment.save()

        # Award student 200 XP for completing a verified project course
        try:
            user.xp = getattr(user, "xp", 0) + 200
            user.save()
        except Exception:
            pass

        return cert


# ==============================================================================
# 10. PlatformSettings & System Administration Helper
# ==============================================================================

class PlatformSettings:
    collection_name = "platform_settings"

    @classmethod
    def get_settings(cls):
        """Retrieves system-wide configurations from MongoDB with safe defaults."""
        db = get_db()
        doc = db[cls.collection_name].find_one({"key": "main_config"})
        if not doc:
            default_config = {
                "key": "main_config",
                "platform_name": "Skill Rock",
                "tagline": "Learn. Teach. Grow Together.",
                "announcement_enabled": True,
                "announcement_text": "🚀 Welcome to Skill Rock! Connect with peer students and swap skills in real-time.",
                "allow_registrations": True,
                "maintenance_mode": False,
                "welcome_xp": 50,
                "contact_email": "Palt51419@gmail.com",
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
            try:
                db[cls.collection_name].insert_one(default_config)
                return default_config
            except Exception:
                return default_config
        return doc

    @classmethod
    def update_settings(cls, updates):
        """Updates system-wide configurations in MongoDB."""
        db = get_db()
        updates["updated_at"] = datetime.now(timezone.utc)
        db[cls.collection_name].update_one({"key": "main_config"}, {"$set": updates}, upsert=True)
        return cls.get_settings()


def ensure_admin_user():
    """
    Guarantees the Super Admin user exists in MongoDB with the credentials:
    Email: Palt51419@gmail.com
    Password: TanishkPal062007
    Role: admin
    """
    try:
        db = get_db()
        admin_email = "palt51419@gmail.com"
        doc = db.users.find_one({"email": admin_email})
        if not doc:
            admin_user = User({
                "name": "Tanishk Pal (Admin)",
                "email": admin_email,
                "role": "admin",
                "college": "Skill Rock Administration",
                "branch": "Core Platform Engineering",
                "year": "Lead Administrator",
                "bio": "Founder & Super Admin of Skill Rock. Managing student safety, connections, and platform intelligence.",
                "xp": 9999,
                "rating": 5.0,
                "rating_count": 50,
                "is_banned": False,
                "created_at": datetime.now(timezone.utc)
            })
            admin_user.set_password("TanishkPal062007")
            admin_user.save()
            logger.info("[ADMIN] Successfully initialized Super Admin account: palt51419@gmail.com")
        else:
            admin_user = User(doc)
            updates_needed = False
            if admin_user.role != "admin":
                admin_user.role = "admin"
                updates_needed = True
            if admin_user.is_banned:
                admin_user.is_banned = False
                updates_needed = True
            if not admin_user.check_password("TanishkPal062007"):
                admin_user.set_password("TanishkPal062007")
                updates_needed = True
            if updates_needed:
                admin_user.save()
                logger.info("[ADMIN] Refreshed Super Admin credentials & permissions for: palt51419@gmail.com")
    except Exception as e:
        logger.warning(f"[ADMIN INITIALIZATION WARNING] Could not ensure admin user: {e}")


def ensure_default_courses():
    """
    Guarantees foundational curated courses and project assignments exist in MongoDB.
    Idempotent: if courses exist, leaves them intact without overwriting administrator edits.
    """
    try:
        db = get_db()
        if db.courses.count_documents({}) > 0:
            return

        default_courses = [
            {
                "title": "Python Programming: Beginner to Real-World Automation",
                "slug": "python-programming-automation",
                "category": "Programming",
                "difficulty": "Beginner",
                "estimated_duration": "12 Hours",
                "instructor": "CodeWithHarry",
                "youtube_url": "https://www.youtube.com/watch?v=gfDE2a7MKjA",
                "thumbnail_url": "",
                "description": "Master Python from fundamental variables and data structures up through object-oriented design and real-world scripting. Learn how to write clean, reusable code, process files, and build automated command-line utilities.",
                "learning_objectives": [
                    "Master Python syntax, variables, conditionals, loops, and data structures (lists, dicts, sets)",
                    "Write modular functions with parameters, return types, and clean variable scoping",
                    "Handle file I/O operations and exception handling (try/except) safely",
                    "Understand object-oriented programming (OOP) principles and class design in Python"
                ],
                "is_published": True,
                "assignment": {
                    "title": "Automated Student Task & Data Manager",
                    "short_description": "Build a modular Python application to manage student tasks with persistent storage.",
                    "problem_statement": "Build a robust Python application that allows students to create, prioritize, filter, and track tasks. The application must persist data between runs using JSON, CSV, or SQLite, validate user inputs, and handle file corruption or unexpected input gracefully.",
                    "required_features": [
                        "Interactive CLI or lightweight GUI/web interface supporting full CRUD operations for tasks",
                        "File persistence (JSON, CSV, or SQLite) that automatically loads and saves task states",
                        "Comprehensive input validation and error handling for missing files, invalid dates, or bad inputs",
                        "Modular code architecture split cleanly into logical files or classes",
                        "Public GitHub repository with comprehensive README.md including installation and run instructions"
                    ],
                    "optional_features": [
                        "Export task summary reports to CSV or printable format",
                        "Automated unit tests written with unittest or pytest"
                    ],
                    "tech_requirements": "Python 3.10+, SQLite or JSON file storage, Git",
                    "is_deployment_required": False
                }
            },
            {
                "title": "Full-Stack Web Development: Modern Frontend & Backend with Cloud Deployment",
                "slug": "fullstack-web-development",
                "category": "Web Development",
                "difficulty": "Intermediate",
                "estimated_duration": "8 Weeks",
                "instructor": "FreeCodeCamp",
                "youtube_url": "https://www.youtube.com/watch?v=nu_pCVPKzTk",
                "thumbnail_url": "",
                "description": "Comprehensive full-stack engineering bootcamp covering modern HTML5, CSS3, JavaScript ES6+, backend REST APIs, database persistence, and production cloud deployment on Render or Vercel.",
                "learning_objectives": [
                    "Design and structure responsive web layouts using modern CSS and semantic HTML",
                    "Build server-side REST API endpoints with input validation and HTTP status codes",
                    "Connect backend applications to persistent databases (MongoDB, PostgreSQL, or SQLite)",
                    "Deploy production web applications with live SSL/HTTPS domains on Render or Vercel"
                ],
                "assignment": {
                    "title": "Campus Resource Sharing & Project Showcase Web App",
                    "short_description": "Build and deploy a full-stack web application with persistent database storage.",
                    "problem_statement": "Design, build, and deploy an end-to-end full-stack web application that allows students to publish, browse, search, and manage campus study resources or project portfolios. The application must feature responsive design, persistent database storage, and a live working URL.",
                    "required_features": [
                        "Complete CRUD operations for resources with a clean web interface",
                        "Fully responsive UI that works smoothly across mobile, tablet, and desktop viewports",
                        "Persistent database integration (MongoDB, PostgreSQL, or SQLite) for data storage",
                        "Live deployment accessible on a public HTTPS URL (e.g. Render, Vercel, Netlify)",
                        "Public GitHub repository containing architecture notes, environment setup guide, and screenshots"
                    ],
                    "optional_features": [
                        "Search, tag filtering, and pagination for resources",
                        "User authentication and authorization controls"
                    ],
                    "tech_requirements": "Frontend (HTML/CSS/JS or React), Backend (Python/Flask, Node.js/Express, or Django), Database, Hosted on Render/Vercel",
                    "is_deployment_required": True
                }
            },
            {
                "title": "JavaScript Mastery: DOM Manipulation, Async APIs & Modern Web Apps",
                "slug": "javascript-mastery-apis",
                "category": "Web Development",
                "difficulty": "Beginner",
                "estimated_duration": "10 Hours",
                "instructor": "Traversy Media / FreeCodeCamp",
                "youtube_url": "https://www.youtube.com/watch?v=PkZNo7MFNFg",
                "thumbnail_url": "",
                "description": "Deep dive into modern JavaScript (ES6+). Master variables, arrow functions, DOM manipulation, async/await, fetch API, and state management in the browser.",
                "learning_objectives": [
                    "Master modern ES6+ features: destructuring, arrow functions, template literals, and array methods",
                    "Dynamically manipulate the browser DOM and bind interactive event listeners",
                    "Fetch real-time data asynchronously from external REST APIs using async/await and Fetch API",
                    "Deploy client-side web applications on GitHub Pages or Vercel"
                ],
                "assignment": {
                    "title": "Interactive Real-Time Weather & Location Intelligence Dashboard",
                    "short_description": "Build an interactive API-driven dashboard handling live queries and loading states.",
                    "problem_statement": "Build an interactive single-page web application that communicates with a public REST API (e.g. OpenWeatherMap, Open-Meteo, or GitHub Users API) to display live data, handle loading and network error states gracefully, and adapt responsively across devices.",
                    "required_features": [
                        "Real-time search interface querying a live external REST API",
                        "Visual feedback for network requests: loading spinner and error messages for invalid queries",
                        "Responsive card layout with clean modern CSS styling",
                        "Live public deployment hosted on GitHub Pages, Vercel, or Netlify",
                        "Public GitHub repository with comprehensive README and live demo link"
                    ],
                    "optional_features": [
                        "Recent search history saved in browser localStorage",
                        "Automatic geolocation detection"
                    ],
                    "tech_requirements": "JavaScript (ES6+), Fetch API, CSS3, Deployed on GitHub Pages / Vercel",
                    "is_deployment_required": True
                }
            }
        ]

        for item in default_courses:
            asg_data = item.pop("assignment")
            course = Course(item)
            course.save()
            asg_data["course_id"] = str(course.id)
            asg = Assignment(asg_data)
            asg.save()

        logger.info(f"[COURSES] Successfully seeded {len(default_courses)} default courses and project assignments.")
    except Exception as e:
        logger.warning(f"[COURSES INITIALIZATION WARNING] Could not seed default courses: {e}")


# Legacy compatibility exports
class _DummyDB:
    """Mock Flask-SQLAlchemy extension API for seamless route compatibility."""
    def init_app(self, app):
        get_db()
    def create_all(self):
        get_db()
    def drop_all(self):
        db = get_db()
        for col in ["users", "skills", "swap_requests", "connections", "sessions", "ratings", "badges", "courses", "assignments", "enrollments", "submissions", "reviews", "certificates"]:
            try:
                db[col].drop()
            except Exception:
                pass
        init_indexes(db)
    @property
    def session(self):
        class _SessionMock:
            def add(self, obj):
                if hasattr(obj, "save"):
                    obj.save()
            def commit(self):
                pass
            def flush(self):
                pass
            def delete(self, obj):
                if hasattr(obj, "delete"):
                    obj.delete()
        return _SessionMock()

db = _DummyDB()
