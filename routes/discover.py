"""
SkillSwap Campus — Discover Students Route
Discovers real students from MongoDB and computes match scores dynamically.
"""

from flask import Blueprint, render_template, request
from flask_login import current_user
from models import User, Connection, SwapRequest
from models.mongo import _to_obj_id
from services.matching import calculate_match_score

discover_bp = Blueprint("discover", __name__)

@discover_bp.route("/discover")
def discover():
    # Filter parameters
    query = request.args.get("q", "").strip().lower()
    selected_college = request.args.get("college", "").strip()
    selected_branch = request.args.get("branch", "").strip()

    # Query all students except current user from MongoDB
    mongo_query = {}
    if current_user.is_authenticated and current_user.id:
        mongo_query = {"_id": {"$ne": _to_obj_id(current_user.id)}}

    all_users = User.find_all(mongo_query)

    # Pre-fetch distinct filter values for the UI dropdowns
    colleges = sorted(list({u.college for u in all_users if u.college}))
    branches = sorted(list({u.branch for u in all_users if u.branch}))

    # Calculate match scores and filter
    student_cards = []
    for user in all_users:
        if current_user.is_authenticated:
            match_data = calculate_match_score(current_user, user)
            score = match_data["score"]
            reasons = match_data["reasons"]
            b_teaches_a_wants = match_data["b_teaches_a_wants"]
            a_teaches_b_wants = match_data["a_teaches_b_wants"]
        else:
            score = 0
            reasons = ["Log in to view compatibility based on your skills."]
            b_teaches_a_wants = []
            a_teaches_b_wants = []

        teach_skills = [s.name for s in user.teaching_skills]
        learn_skills = [s.name for s in user.learning_skills]

        # Apply search query (matches skill name, user name, college, branch)
        if query:
            match_text = f"{user.name} {user.college} {user.branch} {' '.join(teach_skills)} {' '.join(learn_skills)}".lower()
            if query not in match_text:
                continue

        # Apply college filter
        if selected_college and user.college.lower() != selected_college.lower():
            continue

        # Apply branch filter
        if selected_branch and user.branch.lower() != selected_branch.lower():
            continue

        # Check follow/connection status with current user
        is_conn = False
        is_pending = False
        if current_user.is_authenticated and current_user.id:
            if Connection.find_between(current_user.id, user.id):
                is_conn = True
            elif SwapRequest.find_pending_between(current_user.id, user.id):
                is_pending = True

        student_cards.append({
            "user": user,
            "score": score,
            "reasons": reasons,
            "teach_skills": teach_skills,
            "learn_skills": learn_skills,
            "b_teaches_a_wants": b_teaches_a_wants,
            "a_teaches_b_wants": a_teaches_b_wants,
            "is_connected": is_conn,
            "is_pending": is_pending
        })

    # Sort by compatibility score descending
    student_cards.sort(key=lambda x: x["score"], reverse=True)

    return render_template(
        "discover.html",
        student_cards=student_cards,
        colleges=colleges,
        branches=branches,
        query=query,
        selected_college=selected_college,
        selected_branch=selected_branch
    )
