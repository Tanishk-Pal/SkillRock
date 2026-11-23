"""
SkillRock â€” Notifications Routes & API
Handles fetching, reading, and managing user notifications for real-time peer interactions.
"""

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from models import Notification

notifications_bp = Blueprint("notifications", __name__, url_prefix="/api/notifications")

@notifications_bp.route("", methods=["GET"])
@login_required
def get_notifications():
    """Returns the latest notifications and unread count for current user."""
    unread_count = Notification.count_unread(current_user.id)
    notifs = Notification.find_by_recipient(current_user.id, limit=20)
    return jsonify({
        "success": True,
        "unread_count": unread_count,
        "notifications": [n.to_dict() for n in notifs]
    })

@notifications_bp.route("/read/<notif_id>", methods=["POST"])
@login_required
def mark_read(notif_id):
    """Marks a single notification as read."""
    Notification.mark_as_read(notif_id, current_user.id)
    unread_count = Notification.count_unread(current_user.id)
    return jsonify({"success": True, "unread_count": unread_count})

@notifications_bp.route("/read-all", methods=["POST"])
@login_required
def mark_all_read():
    """Marks all notifications for current user as read."""
    Notification.mark_all_read(current_user.id)
    return jsonify({"success": True, "unread_count": 0})
