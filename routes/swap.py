"""
SkillSwap Campus — Skill Swap Request Routes
Handles sending, accepting, rejecting, and cancelling skill swap requests in MongoDB.
Enforces strict server-side authorization and duplicate prevention.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import User, Skill, SwapRequest, Connection, Notification
from services.xp_service import award_swap_accepted_xp

swap_bp = Blueprint("swap", __name__)

@swap_bp.route("/requests")
@login_required
def requests_list():
    # Merged into unified Campus Exchange & Peers Hub
    return redirect(url_for("discover.discover", tab="requests"))


@swap_bp.route("/requests/send", methods=["POST"])
@login_required
def send_request():
    receiver_id = request.form.get("receiver_id", "").strip()
    teach_skill_name = request.form.get("teach_skill_name", "").strip() or request.form.get("teach_skill_id", "").strip()
    learn_skill_name = request.form.get("learn_skill_name", "").strip() or request.form.get("learn_skill_id", "").strip()
    message = request.form.get("message", "").strip()

    if not receiver_id:
        flash("Please select a student to follow.", "danger")
        return redirect(request.referrer or url_for("discover.discover"))

    if str(receiver_id) == str(current_user.id):
        flash("You cannot follow yourself.", "warning")
        return redirect(url_for("discover.discover"))

    receiver = User.get_by_id(receiver_id)
    if not receiver:
        flash("Selected student could not be found.", "danger")
        return redirect(url_for("discover.discover"))

    # Fallback default skills if omitted for fast following
    if not teach_skill_name:
        teach_skill_name = current_user.teaching_skills[0].name if current_user.teaching_skills else "Knowledge Sharing"
    if not learn_skill_name:
        learn_skill_name = receiver.teaching_skills[0].name if receiver.teaching_skills else "Peer Learning"

    # Check if already connected
    existing_conn = Connection.find_between(current_user.id, receiver_id)
    if existing_conn:
        flash(f"You and {receiver.name} are already connected!", "info")
        return redirect(url_for("chat.conversation", partner_id=receiver_id))

    # Check if receiver already sent current_user a pending request -> Instant Follow Back & Connect!
    incoming_pending = SwapRequest.find_pending_between(receiver_id, current_user.id)
    if incoming_pending and str(incoming_pending.receiver_id) == str(current_user.id):
        incoming_pending.status = "accepted"
        incoming_pending.save()
        Connection.create(
            user1_id=incoming_pending.sender_id,
            user2_id=incoming_pending.receiver_id,
            swap_request_id=incoming_pending.id
        )
        award_swap_accepted_xp(incoming_pending)

        # Notify both users
        Notification.notify(
            recipient_id=str(receiver.id),
            sender_id=str(current_user.id),
            notif_type="connection_new",
            title="Connected! 🎉",
            message=f"<strong>{current_user.name}</strong> followed you back! You are now connected (+20 XP).",
            link=url_for("chat.conversation", partner_id=str(current_user.id))
        )
        Notification.notify(
            recipient_id=str(current_user.id),
            sender_id=str(receiver.id),
            notif_type="connection_new",
            title="Connected! 🎉",
            message=f"You followed back <strong>{receiver.name}</strong>! You are now connected (+20 XP).",
            link=url_for("chat.conversation", partner_id=str(receiver.id))
        )

        flash(f"You followed back {receiver.name}! You are now connected on campus (+20 XP).", "success")
        return redirect(url_for("chat.conversation", partner_id=receiver_id))

    # Check for existing pending request to prevent duplicates
    existing = SwapRequest.find_pending_between(current_user.id, receiver_id)
    if existing:
        flash(f"You already sent a follow request to {receiver.name}.", "info")
        return redirect(url_for("swap.requests_list"))

    new_request = SwapRequest.create(
        sender_id=str(current_user.id),
        receiver_id=str(receiver.id),
        teach_skill_name=teach_skill_name,
        learn_skill_name=learn_skill_name,
        message=message or f"Hey {receiver.name}! I followed you on SkillRock Campus.",
        status="pending",
        xp_awarded=False
    )

    # Notify receiver of new follow request
    Notification.notify(
        recipient_id=str(receiver.id),
        sender_id=str(current_user.id),
        notif_type="follow_request",
        title="New Follower 👤",
        message=f"<strong>{current_user.name}</strong> started following you on Skill Exchange.",
        link=url_for("discover.discover", tab="requests")
    )

    flash(f"Follow request sent to {receiver.name}.", "success")
    return redirect(url_for("swap.requests_list"))


@swap_bp.route("/follow/<user_id>", methods=["GET", "POST"])
@login_required
def quick_follow(user_id):
    """
    1-Click Instagram-style Follow route.
    Automatically handles mutual follow (auto-connect) or sends a follow request.
    Supports both JSON AJAX callers and full-page redirects.
    """
    is_ajax = request.is_json or request.headers.get("X-Requested-With") == "XMLHttpRequest" or request.args.get("format") == "json"

    if str(user_id) == str(current_user.id):
        if is_ajax:
            return jsonify({"success": False, "error": "You cannot follow yourself."}), 400
        flash("You cannot follow yourself.", "warning")
        return redirect(request.referrer or url_for("discover.discover"))

    target_user = User.get_by_id(user_id)
    if not target_user:
        if is_ajax:
            return jsonify({"success": False, "error": "Student not found."}), 404
        flash("Student not found.", "danger")
        return redirect(request.referrer or url_for("discover.discover"))

    # 1. Already connected?
    if Connection.find_between(current_user.id, user_id):
        if is_ajax:
            return jsonify({
                "success": True,
                "status": "connected",
                "is_connected": True,
                "is_pending": False,
                "message": f"Already connected with {target_user.name}!",
                "chat_url": url_for("chat.conversation", partner_id=user_id)
            })
        flash(f"You are already connected with {target_user.name}!", "info")
        return redirect(url_for("chat.conversation", partner_id=user_id))

    # 2. Mutual follow back check: did target_user already send a request to current_user?
    incoming = SwapRequest.find_pending_between(user_id, current_user.id)
    if incoming and str(incoming.receiver_id) == str(current_user.id):
        incoming.status = "accepted"
        incoming.save()
        Connection.create(
            user1_id=incoming.sender_id,
            user2_id=incoming.receiver_id,
            swap_request_id=incoming.id
        )
        award_swap_accepted_xp(incoming)

        # Notify both users
        Notification.notify(
            recipient_id=str(target_user.id),
            sender_id=str(current_user.id),
            notif_type="connection_new",
            title="Connected! 🎉",
            message=f"<strong>{current_user.name}</strong> followed you back! You are now connected (+20 XP).",
            link=url_for("chat.conversation", partner_id=str(current_user.id))
        )
        Notification.notify(
            recipient_id=str(current_user.id),
            sender_id=str(target_user.id),
            notif_type="connection_new",
            title="Connected! 🎉",
            message=f"You followed back <strong>{target_user.name}</strong>! You are now connected (+20 XP).",
            link=url_for("chat.conversation", partner_id=str(target_user.id))
        )

        if is_ajax:
            return jsonify({
                "success": True,
                "status": "connected",
                "action": "connected",
                "is_connected": True,
                "is_pending": False,
                "message": f"You followed back {target_user.name}! You are now connected (+20 XP).",
                "chat_url": url_for("chat.conversation", partner_id=user_id)
            })
        flash(f"You followed back {target_user.name}! You are now connected (+20 XP).", "success")
        return redirect(url_for("chat.conversation", partner_id=user_id))

    # 3. Already pending from current user? If toggle requested, cancel it
    existing_sent = SwapRequest.find_pending_between(current_user.id, user_id)
    action_param = request.args.get("action", "") or (request.get_json(silent=True) or {}).get("action", "")

    if existing_sent:
        if action_param in ["unfollow", "cancel", "toggle"]:
            existing_sent.status = "cancelled"
            existing_sent.save()
            if is_ajax:
                return jsonify({
                    "success": True,
                    "status": "unfollowed",
                    "action": "unfollowed",
                    "is_connected": False,
                    "is_pending": False,
                    "message": f"Unfollowed {target_user.name}."
                })
            flash(f"Follow request cancelled.", "info")
            return redirect(request.referrer or url_for("discover.discover"))

        if is_ajax:
            return jsonify({
                "success": True,
                "status": "requested",
                "action": "requested",
                "is_connected": False,
                "is_pending": True,
                "message": f"Follow request already pending for {target_user.name}."
            })
        flash(f"You already sent a follow request to {target_user.name}.", "info")
        return redirect(request.referrer or url_for("swap.requests_list"))

    # 4. Send new follow request
    my_teach = current_user.teaching_skills[0].name if current_user.teaching_skills else "Knowledge Sharing"
    their_teach = target_user.teaching_skills[0].name if target_user.teaching_skills else "Peer Learning"

    SwapRequest.create(
        sender_id=str(current_user.id),
        receiver_id=str(target_user.id),
        teach_skill_name=my_teach,
        learn_skill_name=their_teach,
        message=f"Hey {target_user.name}! I followed you on SkillRock Campus.",
        status="pending",
        xp_awarded=False
    )

    # Dispatch notification to target user
    Notification.notify(
        recipient_id=str(target_user.id),
        sender_id=str(current_user.id),
        notif_type="follow_request",
        title="New Follower 👤",
        message=f"<strong>{current_user.name}</strong> started following you on Skill Exchange.",
        link=url_for("discover.discover", tab="requests")
    )

    if is_ajax:
        return jsonify({
            "success": True,
            "status": "requested",
            "action": "requested",
            "is_connected": False,
            "is_pending": True,
            "message": f"You followed {target_user.name}!"
        })

    flash(f"You followed {target_user.name}! When they follow back, you can chat and schedule sessions.", "success")
    return redirect(request.referrer or url_for("discover.discover"))


@swap_bp.route("/api/follow/<user_id>", methods=["POST"])
@login_required
def api_follow(user_id):
    """Direct alias for AJAX Instagram-style 1-click Follow/Connect."""
    return quick_follow(user_id)


@swap_bp.route("/api/unfollow/<user_id>", methods=["POST"])
@login_required
def api_unfollow(user_id):
    """Unfollows a user or removes an existing connection."""
    target_user = User.get_by_id(user_id)
    target_name = target_user.name if target_user else "Peer"

    existing_sent = SwapRequest.find_pending_between(current_user.id, user_id)
    if existing_sent:
        existing_sent.status = "cancelled"
        existing_sent.save()

    existing_conn = Connection.find_between(current_user.id, user_id)
    if existing_conn:
        existing_conn.delete()

    return jsonify({
        "success": True,
        "status": "unfollowed",
        "action": "unfollowed",
        "is_connected": False,
        "is_pending": False,
        "message": f"Unfollowed {target_name}."
    })


@swap_bp.route("/requests/<request_id>/accept", methods=["POST"])
@login_required
def accept_request(request_id):
    swap_req = SwapRequest.get_by_id(request_id)
    if not swap_req:
        flash("Swap request not found.", "warning")
        return redirect(url_for("swap.requests_list"))

    # Authorization guard: only receiver can accept
    if str(swap_req.receiver_id) != str(current_user.id):
        flash("Unauthorized action.", "danger")
        return redirect(url_for("swap.requests_list"))

    swap_req.status = "accepted"
    swap_req.save()

    # Prevent duplicate connections
    existing_conn = Connection.find_between(swap_req.sender_id, swap_req.receiver_id)
    if not existing_conn:
        new_conn = Connection.create(
            user1_id=swap_req.sender_id,
            user2_id=swap_req.receiver_id,
            swap_request_id=swap_req.id
        )

    # Award exact +20 XP once
    awarded = award_swap_accepted_xp(swap_req)

    # Notify sender that receiver accepted their follow/swap request
    Notification.notify(
        recipient_id=str(swap_req.sender_id),
        sender_id=str(current_user.id),
        notif_type="connection_new",
        title="Connection Accepted! 🎉",
        message=f"<strong>{current_user.name}</strong> accepted your follow request! You are now connected (+20 XP).",
        link=url_for("chat.conversation", partner_id=str(current_user.id))
    )

    is_ajax = request.is_json or request.headers.get("X-Requested-With") == "XMLHttpRequest"
    if is_ajax:
        return jsonify({
            "success": True,
            "status": "connected",
            "message": f"Connected with {swap_req.sender.name if swap_req.sender else 'Peer'}! (+20 XP)",
            "chat_url": url_for("chat.conversation", partner_id=str(swap_req.sender_id))
        })

    sender_name = swap_req.sender.name if swap_req.sender else "Peer"
    msg = f"You followed back {sender_name}! You are now connected on campus."
    if awarded:
        msg += " (+20 XP earned)"
    flash(msg, "success")
    return redirect(url_for("connections.connections_list"))


@swap_bp.route("/requests/<request_id>/reject", methods=["POST"])
@login_required
def reject_request(request_id):
    is_ajax = request.is_json or request.headers.get("X-Requested-With") == "XMLHttpRequest"
    swap_req = SwapRequest.get_by_id(request_id)
    if not swap_req:
        if is_ajax:
            return jsonify({"success": False, "error": "Follow request not found."}), 404
        flash("Follow request not found.", "warning")
        return redirect(url_for("swap.requests_list"))

    # Authorization guard
    if str(swap_req.receiver_id) != str(current_user.id):
        if is_ajax:
            return jsonify({"success": False, "error": "Unauthorized action."}), 403
        flash("Unauthorized action.", "danger")
        return redirect(url_for("swap.requests_list"))

    swap_req.status = "declined"
    swap_req.save()
    if is_ajax:
        return jsonify({"success": True, "message": "Declined follow request."})
    flash(f"Declined follow request.", "info")
    return redirect(url_for("swap.requests_list"))


@swap_bp.route("/requests/<request_id>/cancel", methods=["POST"])
@login_required
def cancel_request(request_id):
    is_ajax = request.is_json or request.headers.get("X-Requested-With") == "XMLHttpRequest"
    swap_req = SwapRequest.get_by_id(request_id)
    if not swap_req:
        if is_ajax:
            return jsonify({"success": False, "error": "Follow request not found."}), 404
        flash("Follow request not found.", "warning")
        return redirect(url_for("swap.requests_list"))

    # Authorization guard: only sender can cancel
    if str(swap_req.sender_id) != str(current_user.id):
        if is_ajax:
            return jsonify({"success": False, "error": "Unauthorized action."}), 403
        flash("Unauthorized action.", "danger")
        return redirect(url_for("swap.requests_list"))

    swap_req.status = "cancelled"
    swap_req.save()
    if is_ajax:
        return jsonify({"success": True, "message": "Follow request cancelled."})
    flash("Follow request cancelled.", "info")
    return redirect(url_for("swap.requests_list"))
