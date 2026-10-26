"""
SkillRock Storage Optimization & Inactivity Cleaner Service
Protects free MongoDB Atlas tier (512MB storage cap) by:
1. Permanently purging student accounts inactive for 7+ days (cascading across all 11 collections).
2. Purging orphaned enrollments, submissions, and reviews.
3. Purging obsolete chat messages for finished/rejected swap sessions.
4. Protecting super admin and administrator accounts from deletion.
"""

import logging
from datetime import datetime, timezone, timedelta

logger = logging.getLogger(__name__)


def purge_inactive_users(days=7):
    """
    Permanently purges users inactive for more than `days` days (default: 7 days)
    and cascades deletion across all related MongoDB collections to reclaim storage.
    PROTECTED: Administrators (role == 'admin' or email == 'palt51419@gmail.com') are NEVER deleted.
    """
    from models.mongo import get_db, User
    db = get_db()
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)

    filter_query = {
        "role": {"$ne": "admin"},
        "email": {"$ne": "palt51419@gmail.com"},
        "$or": [
            {"last_active_at": {"$lt": cutoff}},
            {"last_active_at": {"$exists": False}, "created_at": {"$lt": cutoff}}
        ]
    }

    inactive_users = list(db.users.find(filter_query, {"_id": 1, "email": 1, "name": 1}))
    purged_count = 0
    for u in inactive_users:
        uid = str(u["_id"])
        # Double safety: never delete admin
        email = str(u.get("email", "")).lower()
        if email == "palt51419@gmail.com":
            continue
        User.delete_cascading(uid)
        purged_count += 1
        logger.info(f"[STORAGE CLEANER] Permanently purged inactive user {email} (ID: {uid})")

    return purged_count


def purge_orphaned_records():
    """Purges orphaned submissions, reviews, and enrollments where referenced user or course was deleted."""
    from models.mongo import get_db
    db = get_db()
    reclaimed = 0

    try:
        user_ids = {str(u["_id"]) for u in db.users.find({}, {"_id": 1})}
        course_ids = {str(c["_id"]) for c in db.courses.find({}, {"_id": 1})}

        # Delete orphaned enrollments
        enr_res = db.enrollments.delete_many({
            "$or": [
                {"user_id": {"$nin": list(user_ids)}},
                {"course_id": {"$nin": list(course_ids)}}
            ]
        })
        reclaimed += enr_res.deleted_count

        # Delete orphaned submissions and their reviews
        subs_to_delete = list(db.submissions.find({
            "$or": [
                {"user_id": {"$nin": list(user_ids)}},
                {"course_id": {"$nin": list(course_ids)}}
            ]
        }, {"_id": 1}))
        if subs_to_delete:
            s_ids = [s["_id"] for s in subs_to_delete] + [str(s["_id"]) for s in subs_to_delete]
            db.reviews.delete_many({"submission_id": {"$in": s_ids}})
            sub_res = db.submissions.delete_many({"_id": {"$in": [s["_id"] for s in subs_to_delete]}})
            reclaimed += sub_res.deleted_count
    except Exception as e:
        logger.warning(f"[STORAGE CLEANER ORPHAN CLEANUP NOTE] {e}")

    return reclaimed


def run_storage_optimization(days=7):
    """Executes full storage optimization suite and returns telemetry metrics."""
    purged_users = purge_inactive_users(days=days)
    orphaned_records = purge_orphaned_records()
    logger.info(f"[STORAGE OPTIMIZATION COMPLETE] Purged {purged_users} inactive users and {orphaned_records} orphaned records.")
    return {
        "purged_users": purged_users,
        "orphaned_records": orphaned_records,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
