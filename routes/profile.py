"""
SkillSwap Campus — Profile & Skill Management Routes
Handles real profile viewing, editing, and skill additions/removals in MongoDB.
Enforces strict server-side authorization.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import User, Skill, Badge, Session, Connection, SwapRequest
from services.matching import calculate_match_score
from services.ai_service import normalize_skill

profile_bp = Blueprint("profile", __name__)

@profile_bp.route("/profile")
@login_required
def profile():
    teach_user_skills = current_user.teaching_skills
    learn_user_skills = current_user.learning_skills
    all_skills = Skill.find_all()
    earned_badges = current_user.badges
    all_system_badges = Badge.get_all()

    # User's completed sessions count from MongoDB
    completed_sessions_count = Session.count({
        "$or": [{"teacher_id": str(current_user.id)}, {"learner_id": str(current_user.id)}],
        "status": "completed"
    })

    connections_count = Connection.count({
        "$or": [{"user1_id": str(current_user.id)}, {"user2_id": str(current_user.id)}]
    })

    return render_template(
        "profile.html",
        user=current_user,
        is_own_profile=True,
        teach_user_skills=teach_user_skills,
        learn_user_skills=learn_user_skills,
        all_skills=all_skills,
        earned_badges=earned_badges,
        all_system_badges=all_system_badges,
        completed_sessions_count=completed_sessions_count,
        connections_count=connections_count
    )


@profile_bp.route("/profile/<user_id>")
def view_user_profile(user_id):
    if current_user.is_authenticated and str(current_user.id) == str(user_id):
        return redirect(url_for("profile.profile"))

    target_user = User.get_by_id(user_id)
    if not target_user:
        flash("Student profile not found.", "warning")
        return redirect(url_for("discover.discover"))

    teach_user_skills = target_user.teaching_skills
    learn_user_skills = target_user.learning_skills
    earned_badges = target_user.badges
    all_system_badges = Badge.get_all()

    completed_sessions_count = Session.count({
        "$or": [{"teacher_id": str(target_user.id)}, {"learner_id": str(target_user.id)}],
        "status": "completed"
    })

    connections_count = Connection.count({
        "$or": [{"user1_id": str(target_user.id)}, {"user2_id": str(target_user.id)}]
    })

    match_info = None
    is_connected = False
    is_pending_sent = False
    is_pending_received = False

    if current_user.is_authenticated and current_user.id:
        match_info = calculate_match_score(current_user, target_user)
        conn = Connection.find_between(current_user.id, target_user.id)
        if conn:
            is_connected = True
        else:
            req_sent = SwapRequest.find_pending_between(current_user.id, target_user.id)
            if req_sent:
                is_pending_sent = True
            else:
                req_rec = SwapRequest.find_pending_between(target_user.id, current_user.id)
                if req_rec:
                    is_pending_received = True

    return render_template(
        "profile.html",
        user=target_user,
        is_own_profile=False,
        teach_user_skills=teach_user_skills,
        learn_user_skills=learn_user_skills,
        earned_badges=earned_badges,
        all_system_badges=all_system_badges,
        completed_sessions_count=completed_sessions_count,
        connections_count=connections_count,
        match_info=match_info,
        is_connected=is_connected,
        is_pending_sent=is_pending_sent,
        is_pending_received=is_pending_received
    )


@profile_bp.route("/profile/edit", methods=["GET", "POST"])
@login_required
def edit_profile():
    if request.method == "POST":
        current_user.name = request.form.get("name", "").strip() or current_user.name
        current_user.college = request.form.get("college", "").strip() or current_user.college
        current_user.branch = request.form.get("branch", "").strip() or current_user.branch
        current_user.year = request.form.get("year", "").strip() or current_user.year
        current_user.bio = request.form.get("bio", "").strip() or current_user.bio
        current_user.avatar_seed = request.form.get("avatar_seed", "").strip() or current_user.avatar_seed

        current_user.save()
        flash("Profile updated successfully!", "success")
        return redirect(url_for("profile.profile"))

    return render_template("edit_profile.html", user=current_user)


@profile_bp.route("/skills/add", methods=["POST"])
@login_required
def add_skill():
    skill_input = request.form.get("skill_name", "").strip()
    skill_type = request.form.get("skill_type", "teach").strip().lower()
    proficiency = request.form.get("proficiency", "Intermediate").strip()

    if not skill_input:
        flash("Please enter a skill name.", "warning")
        return redirect(url_for("profile.profile"))

    if skill_type not in ["teach", "learn"]:
        skill_type = "teach"

    normalized_name = normalize_skill(skill_input)
    if not normalized_name:
        normalized_name = skill_input.title()

    # Prevent duplicates using MongoDB user document method
    added = current_user.add_skill(normalized_name, skill_type=skill_type, proficiency=proficiency)
    if added:
        flash(f"Added '{normalized_name}' to your {skill_type.title()} skills!", "success")
    else:
        flash(f"'{normalized_name}' is already in your {skill_type.title()} skills list.", "info")

    return redirect(url_for("profile.profile"))


@profile_bp.route("/skills/remove/<path:user_skill_id>", methods=["POST"])
@login_required
def remove_skill(user_skill_id):
    skill_type = request.form.get("skill_type", "teach").strip().lower()
    removed = current_user.remove_skill(user_skill_id, skill_type=skill_type)
    if not removed and skill_type == "teach":
        # Try learn as fallback
        removed = current_user.remove_skill(user_skill_id, skill_type="learn")

    if removed:
        flash(f"Removed '{user_skill_id}' from your skills list.", "info")
    else:
        flash("Skill was not found in your profile.", "warning")

    return redirect(url_for("profile.profile"))
