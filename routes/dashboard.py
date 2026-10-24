"""
Skill Rock — E-Learning Student Dashboard Route
Provides students with their personalized learning command center:
Active enrolled courses, project submissions, review statuses,
verified certificates, XP achievements, and campus skill exchange partners.
"""

from datetime import datetime
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models import (
    Session,
    Connection,
    Course,
    Assignment,
    Enrollment,
    Submission,
    Certificate
)
from services.matching import get_top_matches_for_user

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/dashboard")
@login_required
def dashboard():
    # Calculate time-based friendly greeting
    hour = datetime.now().hour
    if hour < 12:
        greeting = "Good morning"
    elif hour < 17:
        greeting = "Good afternoon"
    else:
        greeting = "Good evening"

    # Display name with sensible fallback
    display_name = current_user.name.split()[0] if current_user.name else (current_user.email.split("@")[0] if current_user.email else "Student")

    # 1. Enrolled Courses with genuine progress tracking
    enrollments = Enrollment.find_by_user(current_user.id) or []
    enrolled_courses = []
    for enr in enrollments:
        try:
            crs = getattr(enr, "course", None)
            if crs:
                asg = getattr(crs, "assignment", None)
                sub = Submission.get_latest(current_user.id, asg.id) if asg else None
                cert = Certificate.get_by_user_course(current_user.id, crs.id)
                enrolled_courses.append({
                    "enrollment": enr,
                    "course": crs,
                    "assignment": asg,
                    "submission": sub,
                    "certificate": cert
                })
        except Exception:
            continue

    # 2. Student Projects and Submissions
    submissions = Submission.find_by_user(current_user.id) or []
    for sub in submissions:
        try:
            sub.certificate = Certificate.get_by_user_course(current_user.id, getattr(sub, "course_id", None))
        except Exception:
            sub.certificate = None

    # 3. Verified Certificates
    certificates = Certificate.find_by_user(current_user.id) or []

    # 4. Peer Learning / Skill Exchange (Secondary compact matches & upcoming sessions)
    try:
        top_matches = get_top_matches_for_user(current_user, limit=3)
    except Exception:
        top_matches = []

    try:
        upcoming_sessions = Session.find_upcoming_for_user(current_user.id, limit=2)
    except Exception:
        upcoming_sessions = []

    # Skills count for overview
    teaching_skills = current_user.teaching_skills
    learning_skills = current_user.learning_skills
    skills_count = len(teaching_skills) + len(learning_skills)

    # Connections count
    try:
        connections_count = Connection.count({
            "$or": [{"user1_id": str(current_user.id)}, {"user2_id": str(current_user.id)}]
        })
    except Exception:
        connections_count = 0

    return render_template(
        "dashboard.html",
        user=current_user,
        greeting=greeting,
        display_name=display_name,
        enrolled_courses=enrolled_courses,
        submissions=submissions,
        certificates=certificates,
        top_matches=top_matches,
        upcoming_sessions=upcoming_sessions,
        skills_count=skills_count,
        connections_count=connections_count,
        Submission=Submission,
        Certificate=Certificate
    )
