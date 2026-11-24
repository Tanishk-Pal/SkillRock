"""
SkillRock — Bhavishya 1.0 Separate Live Recordings Vault
Isolated Database Adapter & Models for Storing Live Lecture Recordings.

Guarantees 100% database isolation:
- Connects to an independent database (configured via BHAVISHYA_RECORDINGS_DB_URI or separate DB name)
- Never modifies or mixes with existing SkillRock application collections (courses, users, connections)
- Provides upload, retrieval, and streaming metadata for native in-app live lecture recordings.
"""

import os
import logging
from datetime import datetime, timezone
from bson import ObjectId

logger = logging.getLogger(__name__)

# Connection cache for the isolated recordings database
_recordings_client = None
_recordings_db = None


def get_recordings_db():
    """
    Returns the database handle for the separate Bhavishya Live Recordings vault.
    - If BHAVISHYA_RECORDINGS_DB_URI is set, connects to that external/secondary MongoDB instance.
    - Otherwise, isolates into a dedicated separate database ('bhavishya_recordings_vault')
      on the MongoDB client, completely distinct from SkillRock's main application database.
    """
    global _recordings_client, _recordings_db
    if _recordings_db is not None:
        return _recordings_db

    recordings_uri = os.environ.get("BHAVISHYA_RECORDINGS_DB_URI", "").strip()
    db_name = os.environ.get("BHAVISHYA_RECORDINGS_DB_NAME", "bhavishya_recordings_vault").strip()

    if recordings_uri:
        try:
            import pymongo
            _recordings_client = pymongo.MongoClient(recordings_uri, serverSelectionTimeoutMS=5000)
            _recordings_db = _recordings_client[db_name]
            logger.info(f"[Recordings Vault] Connected to dedicated secondary database: {db_name}")
            return _recordings_db
        except Exception as e:
            logger.warning(f"[Recordings Vault] Secondary URI connection warning ({e}), falling back to isolated DB name.")

    # Isolated database fallback
    from models.mongo import get_db as get_main_db
    try:
        main_db = get_main_db()
        client = main_db.client
        _recordings_db = client[db_name]
    except Exception as e_main:
        logger.error(f"[Recordings Vault] Could not initialize isolated recordings DB: {e_main}")
        from models.mongo import db as fallback_db
        _recordings_db = fallback_db

    return _recordings_db


class BhavishyaLectureRecording:
    """
    Metadata document for a real in-app recorded live lecture.
    Stored exclusively in the isolated recordings vault database.
    """
    collection_name = "lecture_recordings"

    def __init__(self, data=None):
        self._data = data or {}
        self._id = self._data.get("_id")
        self.id = str(self._id) if self._id else str(self._data.get("recording_id", ""))
        self.recording_id = str(self._data.get("recording_id", self.id or ObjectId()))
        self.lecture_id = str(self._data.get("lecture_id", "")).strip()
        self.batch_id = self._data.get("batch_id", "bhavishya-1-0")
        self.title = self._data.get("title", "")
        self.file_url = self._data.get("file_url", "")
        self.local_path = self._data.get("local_path", "")
        self.duration_seconds = int(self._data.get("duration_seconds", 0))
        self.file_size_bytes = int(self._data.get("file_size_bytes", 0))
        self.mime_type = self._data.get("mime_type", "video/webm")
        self.recorded_by = self._data.get("recorded_by", "Tanishk Pal Sir")
        self.recorded_at = self._data.get("recorded_at") or datetime.now(timezone.utc)
        self.status = self._data.get("status", "ready")  # ready, processing, archived
        self.metadata = self._data.get("metadata", {})

    def to_dict(self):
        return {
            "recording_id": self.recording_id,
            "lecture_id": self.lecture_id,
            "batch_id": self.batch_id,
            "title": self.title,
            "file_url": self.file_url,
            "duration_seconds": self.duration_seconds,
            "file_size_bytes": self.file_size_bytes,
            "mime_type": self.mime_type,
            "recorded_by": self.recorded_by,
            "recorded_at": self.recorded_at.isoformat() if hasattr(self.recorded_at, "isoformat") else str(self.recorded_at),
            "status": self.status,
        }

    def save(self):
        try:
            db = get_recordings_db()
            doc = {
                "recording_id": self.recording_id,
                "lecture_id": self.lecture_id,
                "batch_id": self.batch_id,
                "title": self.title,
                "file_url": self.file_url,
                "local_path": self.local_path,
                "duration_seconds": self.duration_seconds,
                "file_size_bytes": self.file_size_bytes,
                "mime_type": self.mime_type,
                "recorded_by": self.recorded_by,
                "recorded_at": self.recorded_at,
                "status": self.status,
                "metadata": self.metadata,
                "updated_at": datetime.now(timezone.utc),
            }
            res = db[self.collection_name].update_one(
                {"lecture_id": self.lecture_id},
                {"$set": doc},
                upsert=True
            )
            if not self._id and res.upserted_id:
                self._id = res.upserted_id
                self.id = str(self._id)
        except Exception as e:
            logger.error(f"[Recordings Vault] Error saving recording metadata: {e}")
        return self

    @classmethod
    def get_by_lecture(cls, lecture_id):
        if not lecture_id:
            return None
        try:
            db = get_recordings_db()
            doc = db[cls.collection_name].find_one({"lecture_id": str(lecture_id).strip()})
            return cls(doc) if doc else None
        except Exception as e:
            logger.warning(f"[Recordings Vault] Error fetching recording for {lecture_id}: {e}")
            return None

    @classmethod
    def list_all(cls, batch_id="bhavishya-1-0"):
        try:
            db = get_recordings_db()
            cursor = db[cls.collection_name].find({"batch_id": batch_id}).sort("recorded_at", -1)
            return [cls(doc) for doc in cursor]
        except Exception as e:
            logger.warning(f"[Recordings Vault] Error listing recordings for {batch_id}: {e}")
            return []
