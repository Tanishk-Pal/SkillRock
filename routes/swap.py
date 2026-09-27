"""
SkillSwap Campus — Skill Swap Request Routes
Handles sending, accepting, rejecting, and cancelling skill swap requests in MongoDB.
Enforces strict server-side authorization and duplicate prevention.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import User, Skill, SwapRequest, Connection
from services.xp_service import award_swap_accepted_xp

swap_bp = Blueprint("swap", __name__)

@swap_bp.route("/requests")
@login_required
def requests_list():
    received_requests = SwapRequest.find_by_receiver(current_user.id)
    sent_requests = SwapRequest.find_by_sender(current_user.id)

    return render_template(
        "requests.html",
        received_requests=received_requests,
        sent_requests=sent_requests
    )


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
        message=message or f"Hey {receiver.name}! I followed you on SkillSwap Campus.",
        status="pending",
        xp_awarded=False
    )

    flash(f"Follow request sent to {receiver.name}.", "success")
    return redirect(url_for("swap.requests_list"))


@swap_bp.route("/follow/<user_id>", methods=["GET", "POST"])
@login_required
def quick_follow(user_id):
    """
    1-Click Instagram-style Follow route.
    Automatically handles mutual follow (auto-connect) or sends a follow request.
    """
    if str(user_id) == str(current_user.id):
        flash("You cannot follow yourself.", "warning")
        return redirect(request.referrer or url_for("discover.discover"))

    target_user = User.get_by_id(user_id)
    if not target_user:
        flash("Student not found.", "danger")
        return redirect(request.referrer or url_for("discover.discover"))

    # Already connected?
    if Connection.find_between(current_user.id, user_id):
        flash(f"You are already connected with {target_user.name}!", "info")
        return redirect(url_for("chat.conversation", partner_id=user_id))

    # Mutual follow back check: did target_user already send a request to current_user?
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
        flash(f"You followed back {target_user.name}! You are now connected (+20 XP).", "success")
        return redirect(url_for("chat.conversation", partner_id=user_id))

    # Already pending from current user?
    existing_sent = SwapRequest.find_pending_between(current_user.id, user_id)
    if existing_sent:
        flash(f"You already sent a follow request to {target_user.name}.", "info")
        return redirect(request.referrer or url_for("swap.requests_list"))

    # Send new follow request
    my_teach = current_user.teaching_skills[0].name if current_user.teaching_skills else "Knowledge Sharing"
    their_teach = target_user.teaching_skills[0].name if target_user.teaching_skills else "Peer Learning"

    SwapRequest.create(
        sender_id=str(current_user.id),
        receiver_id=str(target_user.id),
        teach_skill_name=my_teach,
        learn_skill_name=their_teach,
        message=f"Hey {target_user.name}! I followed you on SkillSwap Campus.",
        status="pending",
        xp_awarded=False
    )
    flash(f"You followed {target_user.name}! When they follow back, you can chat and schedule sessions.", "success")
    return redirect(request.referrer or url_for("discover.discover"))


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

    sender_name = swap_req.sender.name if swap_req.sender else "Peer"
    msg = f"You followed back {sender_name}! You are now connected on campus."
    if awarded:
        msg += " (+20 XP earned)"
    flash(msg, "success")
    return redirect(url_for("connections.connections_list"))


@swap_bp.route("/requests/<request_id>/reject", methods=["POST"])
@login_required
def reject_request(request_id):
    swap_req = SwapRequest.get_by_id(request_id)
    if not swap_req:
        flash("Follow request not found.", "warning")
        return redirect(url_for("swap.requests_list"))

    # Authorization guard
    if str(swap_req.receiver_id) != str(current_user.id):
        flash("Unauthorized action.", "danger")
        return redirect(url_for("swap.requests_list"))

    swap_req.status = "declined"
    swap_req.save()
    flash(f"Declined follow request.", "info")
    return redirect(url_for("swap.requests_list"))


@swap_bp.route("/requests/<request_id>/cancel", methods=["POST"])
@login_required
def cancel_request(request_id):
    swap_req = SwapRequest.get_by_id(request_id)
    if not swap_req:
        flash("Follow request not found.", "warning")
        return redirect(url_for("swap.requests_list"))

    # Authorization guard: only sender can cancel
    if str(swap_req.sender_id) != str(current_user.id):
        flash("Unauthorized action.", "danger")
        return redirect(url_for("swap.requests_list"))

    swap_req.status = "cancelled"
    swap_req.save()
    flash("Follow request cancelled.", "info")
    return redirect(url_for("swap.requests_list"))
