"""
SkillSwap Campus — Dashboard Route
Calculates real platform statistics, top matches, and upcoming sessions from MongoDB.
No hardcoded stats or demo data.
"""

from datetime import datetime
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models import Session, Connection
from services.matching import get_top_matches_for_user

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/dashboard")
@login_required
def dashboard():
    # Calculate time-based greeting
    hour = datetime.now().hour
    if hour < 12:
        greeting = "Good morning"
    elif hour < 17:
        greeting = "Good afternoon"
    else:
        greeting = "Good evening"

    # Real user stats from MongoDB
    teaching_skills = current_user.teaching_skills
    learning_skills = current_user.learning_skills
    skills_count = len(teaching_skills) + len(learning_skills)

    # Active connections count from MongoDB
    connections_count = Connection.count({
        "$or": [{"user1_id": str(current_user.id)}, {"user2_id": str(current_user.id)}]
    })

    # Top Recommended Matches calculated by matching engine
    top_matches = get_top_matches_for_user(current_user, limit=3)

    # Real upcoming sessions from MongoDB
    upcoming_sessions = Session.find_upcoming_for_user(current_user.id, limit=3)

    return render_template(
        "dashboard.html",
        user=current_user,
        greeting=greeting,
        skills_count=skills_count,
        connections_count=connections_count,
        top_matches=top_matches,
        upcoming_sessions=upcoming_sessions,
        teaching_skills=teaching_skills,
        learning_skills=learning_skills
    )
