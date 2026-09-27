"""
SkillSwap Campus — Sessions & Ratings Routes
Handles scheduling, Google Calendar & Google Meet creation, completion,
cancellation, and 5-star peer ratings in MongoDB.
Enforces strict server-side authorization and idempotency.
"""

from datetime import datetime, timezone
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import Session, Connection, Skill, User, Rating
from services.xp_service import award_session_completed_xp, award_rating_xp, update_user_rating
from services.google_calendar import create_calendar_event_with_meet, cancel_calendar_event

sessions_bp = Blueprint("sessions", __name__)

@sessions_bp.route("/sessions")
@login_required
def sessions_list():
    upcoming_sessions = Session.find_by_user(current_user.id, status="scheduled")
    past_sessions = Session.find_by_user(current_user.id, status=["completed", "cancelled"])

    return render_template(
        "sessions.html",
        upcoming_sessions=upcoming_sessions,
        past_sessions=past_sessions
    )


@sessions_bp.route("/sessions/schedule", methods=["POST"])
@login_required
def schedule_session():
    connection_id = request.form.get("connection_id", "").strip()
    partner_id = request.form.get("partner_id", "").strip()
    role = request.form.get("role", "learn").strip().lower()
    skill_name = request.form.get("skill_name", "").strip() or request.form.get("skill_id", "").strip()
    title = request.form.get("title", "").strip()
    date_val = request.form.get("date", "").strip()
    time_val = request.form.get("time", "").strip()
    duration = int(request.form.get("duration", 60) or 60)
    notes = request.form.get("notes", "").strip()

    if not partner_id or not skill_name or not date_val or not time_val:
        flash("Please provide skill, date, and time.", "danger")
        return redirect(request.referrer or url_for("sessions.sessions_list"))

    partner = User.get_by_id(partner_id)
    if not partner:
        flash("Partner student not found.", "danger")
        return redirect(url_for("sessions.sessions_list"))

    # Server-side validation: must have an active connection
    conn = Connection.find_between(current_user.id, partner.id)
    if not conn:
        flash("You can only schedule sessions with connected students.", "danger")
        return redirect(url_for("connections.connections_list"))

    if role == "teach":
        teacher_id = str(current_user.id)
        learner_id = str(partner.id)
    else:
        teacher_id = str(partner.id)
        learner_id = str(current_user.id)

    # Check for identical scheduled session to prevent duplicates (Idempotency)
    existing_session = Session.count({
        "connection_id": str(conn.id),
        "scheduled_date": date_val,
        "scheduled_time": time_val,
        "status": "scheduled"
    })
    if existing_session > 0:
        flash("A session is already scheduled at this date and time with your partner.", "warning")
        return redirect(url_for("sessions.sessions_list"))

    # Check if a custom meeting link was provided
    custom_link = request.form.get("meeting_link", "").strip()
    initial_meeting_link = ""
    if custom_link and custom_link.lower() not in ["campus library / google meet", "google meet", "campus library", ""]:
        if not (custom_link.startswith("http://") or custom_link.startswith("https://")):
            initial_meeting_link = f"https://{custom_link}"
        else:
            initial_meeting_link = custom_link

    # Create session in MongoDB
    session_obj = Session({
        "connection_id": str(conn.id),
        "teacher_id": teacher_id,
        "learner_id": learner_id,
        "skill_name": skill_name,
        "title": title or f"{skill_name} Learning Session",
        "notes": notes,
        "scheduled_date": date_val,
        "scheduled_time": time_val,
        "duration_minutes": duration,
        "meeting_link": initial_meeting_link,
        "status": "scheduled",
        "xp_awarded": False
    })
    session_obj.save()

    # Create real Google Calendar event + Google Meet link with 60-min reminder if Google is connected
    cal_result = create_calendar_event_with_meet(session_obj, current_user)
    if cal_result.get("success") and cal_result.get("meet_link"):
        session_obj.meeting_link = cal_result["meet_link"]
        if cal_result.get("event_id"):
            session_obj.calendar_event_id = cal_result["event_id"]
        session_obj.save()
        flash(f"Session scheduled! Real Google Meet link created: {cal_result['meet_link']}", "success")
    elif session_obj.meeting_link:
        flash(f"Session scheduled for {skill_name} on {date_val} with your meeting link.", "success")
    else:
        # If Google is not connected yet, assign an instant reliable video room so link is never blank
        instant_room = f"https://meet.jit.si/SkillSwapCampus-{session_obj.id}"
        session_obj.meeting_link = instant_room
        session_obj.save()
        flash(
            f"Session scheduled! Instant video call room created. You can also connect Google Meet to generate an official Google Meet invite anytime.",
            "info"
        )

    return redirect(url_for("sessions.sessions_list"))


@sessions_bp.route("/sessions/<session_id>/generate-meet", methods=["POST"])
@login_required
def generate_meet_link(session_id):
    """Generates a real Google Meet link for an existing session using user's Google connection."""
    sess = Session.get_by_id(session_id)
    if not sess:
        flash("Session not found.", "warning")
        return redirect(url_for("sessions.sessions_list"))

    # Server-side authorization guard
    if str(current_user.id) not in [sess.teacher_id, sess.learner_id]:
        flash("Unauthorized action.", "danger")
        return redirect(url_for("sessions.sessions_list"))

    if not current_user.google_access_token:
        flash("Please connect your Google account first to generate a real Google Meet link.", "info")
        return redirect(url_for("auth.google_login", next=url_for("sessions.sessions_list")))

    cal_result = create_calendar_event_with_meet(sess, current_user)
    if cal_result.get("success") and cal_result.get("meet_link"):
        sess.meeting_link = cal_result["meet_link"]
        if cal_result.get("event_id"):
            sess.calendar_event_id = cal_result["event_id"]
        sess.save()
        flash(f"Real Google Meet link created: {cal_result['meet_link']}", "success")
    elif cal_result.get("error"):
        flash(f"Could not generate Google Meet link: {cal_result['error']}", "warning")
    else:
        flash("Google Meet link could not be created. Please try connecting Google again.", "warning")

    return redirect(url_for("sessions.sessions_list"))


@sessions_bp.route("/sessions/<session_id>/set-link", methods=["POST"])
@login_required
def set_meeting_link(session_id):
    """Allows student to save or paste a custom Google Meet or video link."""
    sess = Session.get_by_id(session_id)
    if not sess:
        flash("Session not found.", "warning")
        return redirect(url_for("sessions.sessions_list"))

    if str(current_user.id) not in [sess.teacher_id, sess.learner_id]:
        flash("Unauthorized action.", "danger")
        return redirect(url_for("sessions.sessions_list"))

    link = request.form.get("meeting_link", "").strip()
    if not link:
        link = f"https://meet.jit.si/SkillSwapCampus-{sess.id}"
    elif not (link.startswith("http://") or link.startswith("https://")):
        if link.startswith("meet.google.com"):
            link = f"https://{link}"
        else:
            link = f"https://meet.google.com/{link}"

    sess.meeting_link = link
    sess.save()
    flash("Meeting link updated successfully!", "success")
    return redirect(url_for("sessions.sessions_list"))


@sessions_bp.route("/sessions/<session_id>/complete", methods=["POST"])
@login_required
def complete_session(session_id):
    sess = Session.get_by_id(session_id)
    if not sess:
        flash("Session not found.", "warning")
        return redirect(url_for("sessions.sessions_list"))

    # Authorization guard: only participants can complete
    if str(current_user.id) not in [sess.teacher_id, sess.learner_id]:
        flash("Unauthorized action.", "danger")
        return redirect(url_for("sessions.sessions_list"))

    if sess.status == "completed":
        flash("This session is already marked completed.", "info")
        return redirect(url_for("sessions.sessions_list"))

    sess.status = "completed"
    sess.completed_at = datetime.now(timezone.utc)
    sess.save()

    # Exact XP: Teacher +20 XP, Learner +10 XP (strictly once)
    award_session_completed_xp(sess)

    flash("Session completed! Teacher (+20 XP), Learner (+10 XP). You can now exchange ratings.", "success")
    return redirect(url_for("sessions.sessions_list"))


@sessions_bp.route("/sessions/<session_id>/rate", methods=["POST"])
@login_required
def rate_session(session_id):
    sess = Session.get_by_id(session_id)
    if not sess:
        flash("Session not found.", "warning")
        return redirect(url_for("sessions.sessions_list"))

    # Authorization guard
    if str(current_user.id) not in [sess.teacher_id, sess.learner_id]:
        flash("Unauthorized action.", "danger")
        return redirect(url_for("sessions.sessions_list"))

    if sess.status != "completed":
        flash("You can only rate a session once it has been completed.", "warning")
        return redirect(url_for("sessions.sessions_list"))

    # Prevent duplicate ratings
    existing_rating = Rating.find_by_session_and_reviewer(sess.id, current_user.id)
    if existing_rating:
        flash("You have already submitted a rating for this session.", "info")
        return redirect(url_for("sessions.sessions_list"))

    score = int(request.form.get("score", 5) or 5)
    feedback = request.form.get("feedback", "").strip()

    if score < 1 or score > 5:
        flash("Please provide a valid star rating (1–5).", "danger")
        return redirect(url_for("sessions.sessions_list"))

    # Reviewee is the other participant
    reviewee = sess.teacher if str(current_user.id) == sess.learner_id else sess.learner
    if not reviewee:
        flash("Reviewee student not found.", "danger")
        return redirect(url_for("sessions.sessions_list"))

    rating = Rating({
        "session_id": str(sess.id),
        "reviewer_id": str(current_user.id),
        "reviewee_id": str(reviewee.id),
        "score": score,
        "feedback": feedback,
        "xp_awarded": False
    })
    rating.save()

    # Update recipient's average rating dynamically from MongoDB without fake bias
    update_user_rating(reviewee, score)

    # Award +5 XP if 5 stars (strictly once)
    awarded_bonus = award_rating_xp(rating)

    msg = f"Rating submitted for {reviewee.name}."
    if awarded_bonus:
        msg += f" (Awarded +5 XP to {reviewee.name} for 5-star rating!)"
    flash(msg, "success")
    return redirect(url_for("sessions.sessions_list"))


@sessions_bp.route("/sessions/<session_id>/cancel", methods=["POST"])
@login_required
def cancel_session(session_id):
    sess = Session.get_by_id(session_id)
    if not sess:
        flash("Session not found.", "warning")
        return redirect(url_for("sessions.sessions_list"))

    # Authorization guard
    if str(current_user.id) not in [sess.teacher_id, sess.learner_id]:
        flash("Unauthorized action.", "danger")
        return redirect(url_for("sessions.sessions_list"))

    sess.status = "cancelled"
    sess.save()

    # Cancel Google Calendar event if present
    cancel_calendar_event(sess, current_user)

    flash("Session cancelled.", "info")
    return redirect(url_for("sessions.sessions_list"))
