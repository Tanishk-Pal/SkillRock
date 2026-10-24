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

    from models.mongo import _to_obj_id

    # 1. Verified Certificates (Fetched once and indexed into in-memory map)
    certificates = Certificate.find_by_user(current_user.id) or []
    cert_map = {str(getattr(c, "course_id", "")): c for c in certificates if getattr(c, "course_id", None)}

    # 2. Student Projects and Submissions (Fetched once, certificate attached in O(1) memory lookup)
    submissions = Submission.find_by_user(current_user.id) or []
    sub_by_asg = {}
    for sub in submissions:
        sub.certificate = cert_map.get(str(getattr(sub, "course_id", None)))
        asg_id = str(getattr(sub, "assignment_id", ""))
        if asg_id and asg_id not in sub_by_asg:
            sub_by_asg[asg_id] = sub

    # 3. Enrolled Courses with batch pre-fetching (zero N+1 database roundtrips)
    enrollments = Enrollment.find_by_user(current_user.id) or []
    enrolled_courses = []
    
    c_ids = [_to_obj_id(e.course_id) for e in enrollments if getattr(e, "course_id", None)]
    c_objs = Course.find_all({"_id": {"$in": c_ids}}) if c_ids else []
    c_map = {str(c.id): c for c in c_objs}
    asg_map = Assignment.get_by_courses([str(c.id) for c in c_objs]) if c_objs else {}
    for crs in c_objs:
        crs._cached_assignment = asg_map.get(str(crs.id))

    for enr in enrollments:
        try:
            crs = c_map.get(str(enr.course_id)) or getattr(enr, "course", None)
            if crs:
                asg = asg_map.get(str(crs.id)) or getattr(crs, "assignment", None)
                sub = sub_by_asg.get(str(asg.id)) if asg else None
                cert = cert_map.get(str(crs.id))
                enrolled_courses.append({
                    "enrollment": enr,
                    "course": crs,
                    "assignment": asg,
                    "submission": sub,
                    "certificate": cert
                })
        except Exception:
            continue

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
