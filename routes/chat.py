"""
SkillSwap Campus — Direct Messaging & Chat Route
Provides Instagram-style direct messaging between connection members.
Supports real-time chat polling, unread badges, and live message sending in MongoDB.
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from models import User, Connection, Message
from datetime import datetime

chat_bp = Blueprint("chat", __name__)

def _get_user_conversations(current_user_id):
    """
    Fetches all connections for current_user, enriched with their latest message
    and unread count, sorted with the most recent active chat at the top.
    """
    connections = Connection.find_by_user(current_user_id)
    conversations = []
    
    for conn in connections:
        partner = conn.get_partner(current_user_id)
        if not partner:
            continue
        
        last_msg = Message.get_latest_message(current_user_id, partner.id)
        # Count unread messages from this partner
        unread_count = Message.count({
            "sender_id": str(partner.id),
            "receiver_id": str(current_user_id),
            "is_read": False
        })
        
        sort_time = last_msg.created_at if (last_msg and hasattr(last_msg, "created_at")) else conn.created_at
        
        conversations.append({
            "connection": conn,
            "partner": partner,
            "last_message": last_msg,
            "unread_count": unread_count,
            "sort_time": sort_time or datetime.min
        })
    
    # Sort conversations by most recent message/connection time
    conversations.sort(key=lambda c: c["sort_time"], reverse=True)
    return conversations


@chat_bp.route("/messages")
@chat_bp.route("/chat")
@login_required
def chat_inbox():
    """Main messages view. Defaults to first active connection if available."""
    conversations = _get_user_conversations(current_user.id)
    
    # Check if a specific partner was requested via query param
    partner_id = request.args.get("user")
    active_partner = None
    messages = []
    
    if partner_id:
        active_partner = User.get_by_id(partner_id)
    elif conversations:
        active_partner = conversations[0]["partner"]
        
    if active_partner:
        # Mark incoming messages as read
        Message.mark_conversation_as_read(current_user.id, active_partner.id)
        messages = Message.get_conversation(current_user.id, active_partner.id)
        
    return render_template(
        "chat.html",
        conversations=conversations,
        active_partner=active_partner,
        messages=messages
    )


@chat_bp.route("/messages/<partner_id>")
@chat_bp.route("/chat/<partner_id>")
@login_required
def conversation(partner_id):
    """Direct chat view with a specific connection partner."""
    partner = User.get_by_id(partner_id)
    if not partner:
        flash("Student not found.", "warning")
        return redirect(url_for("chat.chat_inbox"))
        
    if str(partner.id) == str(current_user.id):
        flash("You cannot chat with yourself.", "info")
        return redirect(url_for("chat.chat_inbox"))
        
    conversations = _get_user_conversations(current_user.id)
    
    # Mark incoming messages as read
    Message.mark_conversation_as_read(current_user.id, partner.id)
    messages = Message.get_conversation(current_user.id, partner.id)
    
    # Verify if they are connected
    is_connected = bool(Connection.find_between(current_user.id, partner.id))
    
    return render_template(
        "chat.html",
        conversations=conversations,
        active_partner=partner,
        messages=messages,
        is_connected=is_connected
    )


@chat_bp.route("/api/chat/<partner_id>/messages", methods=["GET"])
@login_required
def api_get_messages(partner_id):
    """API endpoint to poll recent messages in real time."""
    partner = User.get_by_id(partner_id)
    if not partner:
        return jsonify({"error": "User not found"}), 404
        
    # Mark as read
    Message.mark_conversation_as_read(current_user.id, partner.id)
    messages = Message.get_conversation(current_user.id, partner.id)
    
    response = jsonify({
        "success": True,
        "messages": [m.to_dict() for m in messages],
        "partner": {
            "id": str(partner.id),
            "name": partner.name,
            "avatar_url": partner.avatar_url
        }
    })
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


@chat_bp.route("/api/chat/unread_summary", methods=["GET"])
@login_required
def api_unread_summary():
    """Lightweight endpoint for polling navbar unread badge."""
    total_unread = Message.count_unread(current_user.id)
    res = jsonify({"success": True, "total_unread": total_unread})
    res.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
    return res


@chat_bp.route("/api/chat/<partner_id>/messages", methods=["POST"])
@login_required
def api_send_message(partner_id):
    """API endpoint to send a direct message in real time."""
    partner = User.get_by_id(partner_id)
    if not partner:
        return jsonify({"error": "User not found"}), 404
        
    data = request.get_json(silent=True) or {}
    text = data.get("text", "").strip() or request.form.get("text", "").strip()
    
    if not text:
        return jsonify({"error": "Message cannot be empty."}), 400
        
    # Create and persist message in MongoDB
    msg = Message.send(
        sender_id=str(current_user.id),
        receiver_id=str(partner.id),
        text=text
    )
    
    if not msg:
        return jsonify({"error": "Could not send message."}), 500
        
    return jsonify({
        "success": True,
        "message": msg.to_dict()
    })


@chat_bp.route("/api/chat/messages/<message_id>/edit", methods=["POST", "PUT", "PATCH"])
@login_required
def api_edit_message(message_id):
    """API endpoint to edit a previously sent message."""
    data = request.get_json(silent=True) or {}
    new_text = data.get("text", "").strip() or request.form.get("text", "").strip()
    if not new_text:
        return jsonify({"error": "Message text cannot be empty."}), 400
        
    updated = Message.edit_message(message_id, current_user.id, new_text)
    if not updated:
        return jsonify({"error": "Could not edit message or permission denied."}), 403
        
    return jsonify({
        "success": True,
        "message": updated.to_dict()
    })


@chat_bp.route("/api/chat/messages/<message_id>/delete", methods=["POST", "DELETE"])
@login_required
def api_delete_message(message_id):
    """API endpoint to delete / unsend a message for everyone."""
    success = Message.delete_message(message_id, current_user.id)
    if not success:
        return jsonify({"error": "Could not delete message or permission denied."}), 403
        
    return jsonify({
        "success": True,
        "deleted_id": str(message_id)
    })

