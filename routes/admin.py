"""
SkillSwap Campus — Master Administration Suite
Comprehensive administrative dashboard, user control, profile management,
password reset, database inspection, and dynamic system settings.
"""

import os
import sys
import platform
import logging
import json
import threading
from datetime import datetime, timezone
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify,
    current_app
)
from flask_login import login_user, logout_user, login_required, current_user
from bson import ObjectId
from models.test_series import (
    Question,
    TestDefinition,
    TestPack,
    TestAttempt,
    UserEntitlement
)
from models import (
    get_db,
    User,
    Skill,
    Connection,
    SwapRequest,
    Session,
    Message,
    PlatformSettings,
    Course,
    Assignment,
    Enrollment,
    Submission,
    Review,
    Certificate,
    slugify,
    extract_youtube_id
)
from config import Config

logger = logging.getLogger(__name__)

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


# ==============================================================================
# Security & Access Control
# ==============================================================================

@admin_bp.before_request
def require_admin():
    """Restricts entire /admin suite exclusively to verified administrators."""
    # Allow public access to dedicated admin login route
    if request.endpoint == "admin.admin_login":
        return

    if not current_user.is_authenticated:
        flash("Please log in with administrator credentials to access the Admin Panel.", "warning")
        return redirect(url_for("admin.admin_login", next=request.url))

    if not getattr(current_user, "is_admin", False):
        flash("Access Denied: Administrator privileges required.", "danger")
        return redirect(url_for("learning.courses_list"))


# ==============================================================================
# Dedicated Admin Authentication
# ==============================================================================

@admin_bp.route("/login", methods=["GET", "POST"])
def admin_login():
    """Dedicated high-security login portal for the SkillSwap Administrator."""
    if current_user.is_authenticated and getattr(current_user, "is_admin", False):
        return redirect(url_for("admin.admin_dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Please enter both administrator email and password.", "danger")
            return render_template("admin/admin_login.html", email=email)

        user = User.get_by_email(email)
        if not user or not user.check_password(password):
            flash("Invalid administrator credentials. Access denied.", "danger")
            return render_template("admin/admin_login.html", email=email)

        if not user.is_admin:
            flash("This account does not have administrator privileges.", "danger")
            return render_template("admin/admin_login.html", email=email)

        login_user(user, remember=True)
        flash(f"Welcome to SkillSwap Admin Suite, {user.name}!", "success")

        next_url = request.args.get("next")
        if not next_url or any(x in str(next_url).lower() for x in ["login", "register"]):
            next_url = url_for("admin.admin_dashboard")
        return redirect(next_url)

    return render_template("admin/admin_login.html")


# ==============================================================================
# 1. Main Dashboard & System Overview
# ==============================================================================

@admin_bp.route("/")
@admin_bp.route("/dashboard")
def admin_dashboard():
    """Executive dashboard with real-time telemetry, user stats, and health metrics."""
    db = get_db()

    # Core Metrics
    total_users = User.count()
    total_students = User.count({"role": {"$ne": "admin"}})
    total_admins = User.count({"role": "admin"})
    banned_users = User.count({"is_banned": True})

    total_connections = Connection.count()
    total_requests = SwapRequest.count()
    total_skills = Skill.count()
    total_messages = Message.count()
    total_sessions = Session.count()

    # Database Telemetry
    db_status = "Connected"
    db_name = db.name
    ping_latency_ms = 0
    try:
        start_t = datetime.now()
        db.command("ping")
        ping_latency_ms = round((datetime.now() - start_t).total_seconds() * 1000, 1)
    except Exception as e:
        db_status = f"Degraded ({e})"

    # AI Configuration Status
    gemini_keys_configured = 0
    for i in range(1, 11):
        suffix = f"_{i}" if i > 1 else ""
        if os.getenv(f"GEMINI_API_KEY{suffix}"):
            gemini_keys_configured += 1

    # Recent Registrations
    recent_users = User.find_all(limit=8)

    # Recent Messages
    recent_messages_raw = list(db.messages.find().sort("created_at", -1).limit(6))
    recent_messages = []
    for m in recent_messages_raw:
        sender = User.get_by_id(m.get("sender_id"))
        receiver = User.get_by_id(m.get("receiver_id"))
        recent_messages.append({
            "id": str(m.get("_id")),
            "sender_name": sender.name if sender else "Unknown Student",
            "receiver_name": receiver.name if receiver else "Unknown Student",
            "content": m.get("content", ""),
            "created_at": m.get("created_at")
        })

    # System Environment
    sys_info = {
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "db_name": db_name,
        "db_status": db_status,
        "ping_latency_ms": ping_latency_ms,
        "gemini_keys_count": max(1, gemini_keys_configured),
        "google_oauth": bool(os.getenv("GOOGLE_CLIENT_ID")),
    }

    settings = PlatformSettings.get_settings()

    return render_template(
        "admin/dashboard.html",
        total_users=total_users,
        total_students=total_students,
        total_admins=total_admins,
        banned_users=banned_users,
        total_connections=total_connections,
        total_requests=total_requests,
        total_skills=total_skills,
        total_messages=total_messages,
        total_sessions=total_sessions,
        sys_info=sys_info,
        recent_users=recent_users,
        recent_messages=recent_messages,
        settings=settings
    )


# ==============================================================================
# 2. Comprehensive User Management
# ==============================================================================

@admin_bp.route("/users")
def users_list():
    """Interactive table listing all users with search, filtering, and quick actions."""
    db = get_db()
    q = request.args.get("q", "").strip()
    role_filter = request.args.get("role", "all")
    status_filter = request.args.get("status", "all")

    mongo_query = {}

    if q:
        mongo_query["$or"] = [
            {"name": {"$regex": q, "$options": "i"}},
            {"email": {"$regex": q, "$options": "i"}},
            {"college": {"$regex": q, "$options": "i"}},
            {"branch": {"$regex": q, "$options": "i"}},
        ]

    if role_filter in ["student", "admin"]:
        if role_filter == "admin":
            mongo_query["$or"] = [
                {"role": "admin"},
                {"email": "palt51419@gmail.com"}
            ]
        else:
            mongo_query["role"] = {"$ne": "admin"}
            mongo_query["email"] = {"$ne": "palt51419@gmail.com"}

    if status_filter == "banned":
        mongo_query["is_banned"] = True
    elif status_filter == "active":
        mongo_query["is_banned"] = {"$ne": True}

    users_cursor = db.users.find(mongo_query).sort("created_at", -1).limit(200)
    users = [User(doc) for doc in users_cursor]

    # Pre-calculate counts for each user (connections, messages, course enrollments & progress)
    enriched_users = []
    for u in users:
        conn_count = Connection.count({"$or": [{"user1_id": u.id}, {"user2_id": u.id}]})
        has_local_password = bool(u.password_hash)
        has_google = bool(u.google_id or u.google_access_token)

        # Enrolled courses and progress calculation
        u_enrollments = list(db.enrollments.find({"user_id": str(u.id)}))
        enrolled_count = len(u_enrollments)
        if enrolled_count > 0:
            avg_progress = round(sum(int(e.get("watch_percent", 0) or 0) for e in u_enrollments) / enrolled_count)
        else:
            avg_progress = 0

        enriched_users.append({
            "user": u,
            "connections_count": conn_count,
            "has_local_password": has_local_password,
            "has_google": has_google,
            "enrolled_courses_count": enrolled_count,
            "overall_progress": avg_progress
        })

    return render_template(
        "admin/users.html",
        users=enriched_users,
        q=q,
        role_filter=role_filter,
        status_filter=status_filter,
        total_count=len(enriched_users)
    )


@admin_bp.route("/users/<user_id>")
def user_detail(user_id):
    """Full 360-degree user profile inspector with security metadata and activity logs."""
    user = User.get_by_id(user_id)
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for("admin.users_list"))

    db = get_db()
    uid = str(user.id)

    # Connections
    conn_docs = list(db.connections.find({"$or": [{"user1_id": uid}, {"user2_id": uid}]}).limit(20))
    connections = []
    for c in conn_docs:
        partner_id = c["user2_id"] if c["user1_id"] == uid else c["user1_id"]
        partner = User.get_by_id(partner_id)
        connections.append({
            "id": str(c["_id"]),
            "partner": partner,
            "created_at": c.get("created_at")
        })

    # Recent Messages
    message_docs = list(db.messages.find(
        {"$or": [{"sender_id": uid}, {"receiver_id": uid}]}
    ).sort("created_at", -1).limit(25))

    messages = []
    for m in message_docs:
        other_id = m["receiver_id"] if m["sender_id"] == uid else m["sender_id"]
        other = User.get_by_id(other_id)
        messages.append({
            "id": str(m["_id"]),
            "is_outgoing": m["sender_id"] == uid,
            "partner_name": other.name if other else "Unknown Student",
            "content": m.get("content", ""),
            "created_at": m.get("created_at"),
            "is_read": m.get("is_read", False)
        })

    # Security Metadata
    password_hash = user.password_hash or ""
    hash_algorithm = "None"
    hash_preview = "No local password set"
    if password_hash:
        parts = password_hash.split("$")
        hash_algorithm = parts[0] if parts else "pbkdf2 / scrypt"
        hash_preview = f"{parts[0]}$...${password_hash[-8:]}" if len(parts) >= 2 else f"Hash length {len(password_hash)}"

    # Enrolled Courses & Academic Progress Tracking
    enrollment_docs = list(db.enrollments.find({"user_id": uid}).sort("created_at", -1))
    enrollments_data = []
    for ed in enrollment_docs:
        cid = ed.get("course_id")
        course = Course.get_by_id(cid) or Course.get_by_slug(cid)
        c_title = course.title if course else f"Course #{cid}"
        c_slug = course.slug if course else cid

        watch_secs = int(ed.get("watch_seconds", 0) or 0)
        mins = watch_secs // 60
        secs = watch_secs % 60
        formatted_watch_time = f"{mins:02d}:{secs:02d}"

        duration_secs = int(ed.get("video_duration", 0) or 0)
        d_mins = duration_secs // 60
        d_secs = duration_secs % 60
        formatted_duration = f"{d_mins:02d}:{d_secs:02d}" if duration_secs > 0 else (course.estimated_duration if course else "N/A")

        # Capstone project submission & review
        submission = db.submissions.find_one({"user_id": uid, "course_id": str(cid)})
        if not submission:
            course_assignments = list(db.assignments.find({"course_id": str(cid)}))
            assign_ids = [str(a["_id"]) for a in course_assignments]
            if assign_ids:
                submission = db.submissions.find_one({"user_id": uid, "assignment_id": {"$in": assign_ids}})
        if not submission:
            submission = db.submissions.find_one({"user_id": uid})

        capstone_status = "Not Submitted"
        capstone_score = None
        capstone_feedback = None
        if submission:
            raw_status = submission.get("status", "submitted")
            capstone_status = raw_status.title() if isinstance(raw_status, str) else "Submitted"
            review = db.reviews.find_one({"submission_id": str(submission["_id"])})
            if review:
                capstone_score = review.get("total_score")
                capstone_feedback = review.get("feedback")

        # Issued Certificate details
        cert_doc = db.certificates.find_one({"user_id": uid, "course_id": str(cid)})
        if not cert_doc:
            cert_doc = db.certificates.find_one({"user_id": uid})

        cert_data = None
        if cert_doc:
            cert_data = {
                "certificate_id": cert_doc.get("certificate_id"),
                "issued_at": cert_doc.get("issued_at") or cert_doc.get("created_at"),
                "verification_hash": cert_doc.get("verification_hash")
            }

        enrollments_data.append({
            "course": course,
            "course_title": c_title,
            "course_slug": c_slug,
            "enrolled_at": ed.get("created_at"),
            "status": ed.get("status", "enrolled"),
            "watch_percent": int(ed.get("watch_percent", 0) or 0),
            "video_completed": bool(ed.get("video_completed", False)),
            "watch_seconds": watch_secs,
            "formatted_watch_time": formatted_watch_time,
            "formatted_duration": formatted_duration,
            "capstone_status": capstone_status,
            "capstone_score": capstone_score,
            "capstone_feedback": capstone_feedback,
            "certificate": cert_data
        })

    return render_template(
        "admin/user_detail.html",
        target_user=user,
        connections=connections,
        messages=messages,
        hash_algorithm=hash_algorithm,
        hash_preview=hash_preview,
        enrollments_data=enrollments_data
    )


@admin_bp.route("/users/<user_id>/edit", methods=["POST"])
def user_edit(user_id):
    """Admin modification of any user's profile attributes directly from dashboard."""
    user = User.get_by_id(user_id)
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for("admin.users_list"))

    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    college = request.form.get("college", "").strip()
    branch = request.form.get("branch", "").strip()
    year = request.form.get("year", "").strip()
    bio = request.form.get("bio", "").strip()
    role = request.form.get("role", "student")
    xp_val = request.form.get("xp", "").strip()

    if not name or not email:
        flash("Name and email are mandatory fields.", "danger")
        return redirect(url_for("admin.user_detail", user_id=user_id))

    # Check email duplicate if changed
    if email != user.email:
        existing = User.get_by_email(email)
        if existing and str(existing.id) != str(user.id):
            flash("Another user is already registered with this email address.", "danger")
            return redirect(url_for("admin.user_detail", user_id=user_id))

    user.name = name
    user.email = email
    user.college = college
    user.branch = branch
    user.year = year
    user.bio = bio
    user.role = role

    try:
        user.xp = int(xp_val) if xp_val else user.xp
    except ValueError:
        pass

    user.save()
    flash(f"Successfully updated profile for {user.name} ({user.email}).", "success")
    return redirect(url_for("admin.user_detail", user_id=user_id))


@admin_bp.route("/users/<user_id>/reset_password", methods=["POST"])
def user_reset_password(user_id):
    """Instantly overwrite or set a new password for any user directly from the admin panel."""
    user = User.get_by_id(user_id)
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for("admin.users_list"))

    new_password = request.form.get("new_password", "").strip()
    if not new_password or len(new_password) < 6:
        flash("New password must be at least 6 characters long.", "danger")
        return redirect(url_for("admin.user_detail", user_id=user_id))

    user.set_password(new_password)
    user.save()

    flash(f"Password for {user.name} ({user.email}) has been successfully updated to the new value.", "success")
    return redirect(url_for("admin.user_detail", user_id=user_id))


@admin_bp.route("/users/<user_id>/toggle_ban", methods=["POST"])
def user_toggle_ban(user_id):
    """Toggles account suspension / ban for a user."""
    user = User.get_by_id(user_id)
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for("admin.users_list"))

    # Protect the Super Admin account
    if user.email.lower() == "palt51419@gmail.com":
        flash("Cannot suspend the Super Administrator account.", "danger")
        return redirect(url_for("admin.user_detail", user_id=user_id))

    reason = request.form.get("ban_reason", "").strip() or "Violation of campus conduct and safety guidelines."

    if user.is_banned:
        user.is_banned = False
        user.ban_reason = ""
        user.save()
        flash(f"Account for {user.name} has been reinstated and unbanned.", "success")
    else:
        user.is_banned = True
        user.ban_reason = reason
        user.save()
        flash(f"Account for {user.name} has been suspended ({reason}).", "warning")

    return redirect(url_for("admin.user_detail", user_id=user_id))


@admin_bp.route("/users/<user_id>/delete", methods=["POST"])
def user_delete(user_id):
    """Permanently purges a user and all related records from the platform."""
    user = User.get_by_id(user_id)
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for("admin.users_list"))

    if user.email.lower() == "palt51419@gmail.com":
        flash("Security Protection: The Super Admin account cannot be deleted.", "danger")
        return redirect(url_for("admin.user_detail", user_id=user_id))

    name = user.name
    email = user.email
    User.delete_cascading(user_id)

    flash(f"User {name} ({email}) and all their connections, messages, and swap requests were permanently deleted.", "success")
    return redirect(url_for("admin.users_list"))


# ==============================================================================
# 3. Global Skills Catalog Management
# ==============================================================================

@admin_bp.route("/skills")
def skills_list():
    """View and manage all skills in the platform's global directory."""
    db = get_db()
    skills = Skill.find_all()

    # Calculate statistics for each skill
    enriched = []
    for s in skills:
        teachers_count = db.users.count_documents({"teaching_skills.name": {"$regex": f"^{s.name}$", "$options": "i"}})
        learners_count = db.users.count_documents({"learning_skills.name": {"$regex": f"^{s.name}$", "$options": "i"}})
        enriched.append({
            "skill": s,
            "teachers_count": teachers_count,
            "learners_count": learners_count
        })

    return render_template("admin/skills.html", skills=enriched, total_count=len(enriched))


@admin_bp.route("/skills/add", methods=["POST"])
def skill_add():
    """Adds a new skill to the platform catalog without needing code edits."""
    name = request.form.get("name", "").strip()
    category = request.form.get("category", "General").strip()

    if not name:
        flash("Skill name is required.", "danger")
        return redirect(url_for("admin.skills_list"))

    existing = Skill.get_by_name(name)
    if existing:
        flash(f"The skill '{name}' already exists in the catalog.", "warning")
        return redirect(url_for("admin.skills_list"))

    Skill.create(name=name, category=category)
    flash(f"Successfully added '{name}' to the skills directory.", "success")
    return redirect(url_for("admin.skills_list"))


@admin_bp.route("/skills/<skill_id>/edit", methods=["POST"])
def skill_edit(skill_id):
    """Modifies an existing skill's name or category."""
    skill = Skill.get_by_id(skill_id)
    if not skill:
        flash("Skill not found.", "danger")
        return redirect(url_for("admin.skills_list"))

    name = request.form.get("name", "").strip()
    category = request.form.get("category", "General").strip()

    if not name:
        flash("Skill name cannot be empty.", "danger")
        return redirect(url_for("admin.skills_list"))

    db = get_db()
    db.skills.update_one({"_id": ObjectId(skill_id)}, {"$set": {"name": name, "category": category}})

    flash(f"Skill '{name}' updated successfully.", "success")
    return redirect(url_for("admin.skills_list"))


@admin_bp.route("/skills/<skill_id>/delete", methods=["POST"])
def skill_delete(skill_id):
    """Deletes a skill from the platform catalog."""
    db = get_db()
    db.skills.delete_one({"_id": ObjectId(skill_id)})
    flash("Skill removed from catalog.", "success")
    return redirect(url_for("admin.skills_list"))


# ==============================================================================
# 4. Connections & Network Moderation
# ==============================================================================

@admin_bp.route("/connections")
def connections_list():
    """Lists all active student-to-student connections with moderation tools."""
    db = get_db()
    conn_docs = list(db.connections.find().sort("created_at", -1).limit(100))

    connections = []
    for c in conn_docs:
        u1 = User.get_by_id(c.get("user1_id"))
        u2 = User.get_by_id(c.get("user2_id"))
        connections.append({
            "id": str(c["_id"]),
            "user1": u1,
            "user2": u2,
            "created_at": c.get("created_at")
        })

    return render_template("admin/connections.html", connections=connections, total_count=len(connections))


@admin_bp.route("/connections/<conn_id>/delete", methods=["POST"])
def connection_delete(conn_id):
    """Breaks / severs an unwanted or reported connection between two users."""
    db = get_db()
    db.connections.delete_one({"_id": ObjectId(conn_id)})
    flash("Connection was severed successfully.", "success")
    return redirect(url_for("admin.connections_list"))


# ==============================================================================
# 5. Direct Messages Moderation Log
# ==============================================================================

@admin_bp.route("/messages")
def messages_list():
    """Inspects recent platform chat messages for harassment or policy violation."""
    db = get_db()
    msg_docs = list(db.messages.find().sort("created_at", -1).limit(100))

    messages = []
    for m in msg_docs:
        sender = User.get_by_id(m.get("sender_id"))
        receiver = User.get_by_id(m.get("receiver_id"))
        messages.append({
            "id": str(m["_id"]),
            "sender": sender,
            "receiver": receiver,
            "content": m.get("content", ""),
            "created_at": m.get("created_at"),
            "is_read": m.get("is_read", False)
        })

    return render_template("admin/messages.html", messages=messages, total_count=len(messages))


@admin_bp.route("/messages/<msg_id>/delete", methods=["POST"])
def message_delete(msg_id):
    """Deletes an inappropriate message from the database."""
    db = get_db()
    db.messages.delete_one({"_id": ObjectId(msg_id)})
    flash("Message permanently removed from chat history.", "success")
    return redirect(url_for("admin.messages_list"))


# ==============================================================================
# 6. Dynamic System Settings (No Code Change Required)
# ==============================================================================

@admin_bp.route("/settings", methods=["GET", "POST"])
def settings_page():
    """View and update live platform settings directly in MongoDB."""
    if request.method == "POST":
        announcement_enabled = request.form.get("announcement_enabled") == "on"
        announcement_text = request.form.get("announcement_text", "").strip()
        allow_registrations = request.form.get("allow_registrations") == "on"
        maintenance_mode = request.form.get("maintenance_mode") == "on"
        welcome_xp = int(request.form.get("welcome_xp", 50))
        contact_email = request.form.get("contact_email", "Palt51419@gmail.com").strip()

        PlatformSettings.update_settings({
            "announcement_enabled": announcement_enabled,
            "announcement_text": announcement_text,
            "allow_registrations": allow_registrations,
            "maintenance_mode": maintenance_mode,
            "welcome_xp": welcome_xp,
            "contact_email": contact_email
        })

        flash("Platform settings saved and applied live across the application!", "success")
        return redirect(url_for("admin.settings_page"))

    current_settings = PlatformSettings.get_settings()
    return render_template("admin/settings.html", settings=current_settings)


# ==============================================================================
# 7. Course Management & Curriculum Administration
# ==============================================================================

@admin_bp.route("/courses")
def courses_list():
    """Admin Course Directory: Manage, edit, publish/draft courses and assignments."""
    db = get_db()
    courses = Course.find_all(sort=[("created_at", -1)])
    total_courses = len(courses)
    published_count = len([c for c in courses if c.is_published])
    total_enrollments = db.enrollments.count_documents({})
    total_certificates = db.certificates.count_documents({})

    return render_template(
        "admin/courses.html",
        courses=courses,
        total_courses=total_courses,
        published_count=published_count,
        total_enrollments=total_enrollments,
        total_certificates=total_certificates
    )


@admin_bp.route("/courses/new", methods=["GET", "POST"])
def course_new():
    """Create a new course with an accompanying practical project assignment."""
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        category = request.form.get("category", "Programming").strip()
        difficulty = request.form.get("difficulty", "Beginner").strip()
        duration = request.form.get("estimated_duration", "10 Hours").strip()
        instructor = request.form.get("instructor", "").strip()
        youtube_url = request.form.get("youtube_url", "").strip()
        thumbnail_url = request.form.get("thumbnail_url", "").strip()
        description = request.form.get("description", "").strip()
        raw_objectives = request.form.get("learning_objectives", "").strip()
        is_published = request.form.get("is_published") == "on"

        # Assignment details
        assignment_title = request.form.get("assignment_title", f"{title} — Final Project").strip()
        problem_statement = request.form.get("problem_statement", "").strip()
        raw_required = request.form.get("required_features", "").strip()
        raw_optional = request.form.get("optional_features", "").strip()
        tech_requirements = request.form.get("tech_requirements", "").strip()
        is_deployment_required = request.form.get("is_deployment_required") == "on"

        if not title or not youtube_url:
            flash("Please provide at least a course title and YouTube URL.", "danger")
            return render_template("admin/course_edit.html", course=None, assignment=None)

        objectives = [line.strip() for line in raw_objectives.splitlines() if line.strip()]
        required_features = [line.strip() for line in raw_required.splitlines() if line.strip()]
        optional_features = [line.strip() for line in raw_optional.splitlines() if line.strip()]

        course = Course({
            "title": title,
            "category": category,
            "difficulty": difficulty,
            "estimated_duration": duration,
            "instructor": instructor or "Curated Instructor",
            "youtube_url": youtube_url,
            "thumbnail_url": thumbnail_url,
            "description": description,
            "learning_objectives": objectives,
            "is_published": is_published,
            "created_at": datetime.now(timezone.utc)
        })
        course.save()

        evaluation_type = request.form.get("evaluation_type", "project_based").strip()
        try:
            passing_score = int(request.form.get("passing_score", 70))
        except (ValueError, TypeError):
            passing_score = 70

        quiz_json_raw = request.form.get("quiz_json", "").strip()
        quiz_data = {}
        if quiz_json_raw:
            try:
                quiz_data = json.loads(quiz_json_raw)
            except Exception as e:
                logger.warning(f"Error parsing quiz_json in course_new: {e}")

        if evaluation_type == "quiz_based":
            is_deployment_required = False

        assignment = Assignment({
            "course_id": str(course.id),
            "title": assignment_title,
            "short_description": f"Assessment quiz for {title}." if evaluation_type == "quiz_based" else f"Build and submit a functional project for {title}.",
            "problem_statement": problem_statement or (f"Complete the assessment to demonstrate understanding of {title}." if evaluation_type == "quiz_based" else f"Demonstrate practical competence in {title} by building a complete working application."),
            "required_features": required_features if evaluation_type != "quiz_based" else [],
            "optional_features": optional_features,
            "tech_requirements": tech_requirements,
            "evaluation_type": evaluation_type,
            "passing_score": passing_score,
            "is_deployment_required": is_deployment_required,
            "quiz_data": quiz_data,
            "is_published": True,
            "created_at": datetime.now(timezone.utc)
        })
        assignment.save()

        flash(f"Course '{course.title}' and assignment created successfully!", "success")
        return redirect(url_for("admin.courses_list"))

    return render_template("admin/course_edit.html", course=None, assignment=None)


@admin_bp.route("/courses/<course_id>/edit", methods=["GET", "POST"])
def course_edit(course_id):
    """Edit an existing course and its project assignment."""
    course = Course.get_by_id(course_id)
    if not course:
        flash("Course not found.", "danger")
        return redirect(url_for("admin.courses_list"))

    assignment = course.assignment

    if request.method == "POST":
        course.title = request.form.get("title", "").strip()
        course.category = request.form.get("category", "Programming").strip()
        course.difficulty = request.form.get("difficulty", "Beginner").strip()
        course.estimated_duration = request.form.get("estimated_duration", "10 Hours").strip()
        course.instructor = request.form.get("instructor", "").strip()
        course.youtube_url = request.form.get("youtube_url", "").strip()
        course.thumbnail_url = request.form.get("thumbnail_url", "").strip()
        course.description = request.form.get("description", "").strip()
        raw_objectives = request.form.get("learning_objectives", "").strip()
        course.learning_objectives = [line.strip() for line in raw_objectives.splitlines() if line.strip()]
        course.is_published = request.form.get("is_published") == "on"
        course.save()

        # Update assignment
        if not assignment:
            assignment = Assignment({"course_id": str(course.id)})

        assignment.title = request.form.get("assignment_title", f"{course.title} — Final Project").strip()
        assignment.problem_statement = request.form.get("problem_statement", "").strip()
        raw_required = request.form.get("required_features", "").strip()
        assignment.required_features = [line.strip() for line in raw_required.splitlines() if line.strip()]
        raw_optional = request.form.get("optional_features", "").strip()
        assignment.optional_features = [line.strip() for line in raw_optional.splitlines() if line.strip()]
        assignment.tech_requirements = request.form.get("tech_requirements", "").strip()
        assignment.is_deployment_required = request.form.get("is_deployment_required") == "on"
        if request.form.get("evaluation_type"):
            assignment.evaluation_type = request.form.get("evaluation_type").strip()
        if assignment.evaluation_type == "quiz_based":
            assignment.is_deployment_required = False
            
        quiz_json_raw = request.form.get("quiz_json", "").strip()
        if quiz_json_raw:
            try:
                parsed_quiz = json.loads(quiz_json_raw)
                assignment.quiz_data = parsed_quiz
                assignment._data["quiz_data"] = parsed_quiz
            except Exception as e:
                logger.warning(f"Error parsing quiz_json in course_edit: {e}")

        if request.form.get("passing_score"):
            try:
                assignment._data["passing_score"] = int(request.form.get("passing_score"))
            except (ValueError, TypeError):
                pass
        assignment.save()

        flash(f"Course '{course.title}' updated successfully!", "success")
        return redirect(url_for("admin.courses_list"))

    return render_template("admin/course_edit.html", course=course, assignment=assignment)


@admin_bp.route("/courses/<course_id>/toggle", methods=["POST"])
def course_toggle(course_id):
    """Quickly toggle course published / draft status."""
    course = Course.get_by_id(course_id)
    if not course:
        flash("Course not found.", "danger")
        return redirect(url_for("admin.courses_list"))

    course.is_published = not course.is_published
    course.save()
    status_str = "Published" if course.is_published else "Drafted"
    flash(f"Course '{course.title}' is now {status_str}.", "success")
    return redirect(url_for("admin.courses_list"))


@admin_bp.route("/courses/<course_id>/delete", methods=["GET", "POST"])
def course_delete(course_id):
    """Permanently delete a course and all associated milestone assignments, enrollments, and submissions."""
    db = get_db()
    course = Course.get_by_id(course_id)
    if not course:
        course = Course.get_by_slug(str(course_id).strip())

    if course:
        title = course.title
        course.delete()
        flash(f"Course '{title}' and all associated records were permanently deleted.", "success")
    else:
        # Direct fallback in MongoDB if model lookup missed
        obj_id = _to_obj_id(course_id)
        str_id = str(course_id).strip()
        c_doc = db.courses.find_one({
            "$or": [
                {"_id": obj_id},
                {"_id": str_id},
                {"slug": str_id}
            ]
        })
        if c_doc:
            title = c_doc.get("title", "Course")
            c_slug = c_doc.get("slug")
            c_real_id = str(c_doc["_id"])
            c_obj_id = c_doc["_id"]

            if c_slug:
                db.deleted_courses.update_one(
                    {"slug": c_slug},
                    {"$set": {
                        "slug": c_slug,
                        "course_id": c_real_id,
                        "deleted_at": datetime.now(timezone.utc)
                    }},
                    upsert=True
                )

            course_query = {"$or": [{"course_id": c_real_id}, {"course_id": c_obj_id}, {"course_id": c_slug}]}
            subs = list(db.submissions.find(course_query, {"_id": 1}))
            if subs:
                sub_ids = []
                for s in subs:
                    sub_ids.append(s["_id"])
                    sub_ids.append(str(s["_id"]))
                    sub_ids.append(_to_obj_id(s["_id"]))
                db.reviews.delete_many({"submission_id": {"$in": sub_ids}})

            db.submissions.delete_many(course_query)
            db.assignments.delete_many(course_query)
            db.enrollments.delete_many(course_query)
            db.certificates.delete_many(course_query)
            db.courses.delete_many({"$or": [{"_id": c_obj_id}, {"_id": c_real_id}, {"slug": c_slug}]})
            Course.invalidate_published_cache()
            flash(f"Course '{title}' and all associated records were permanently deleted.", "success")
        else:
            flash("Course not found or has already been permanently deleted.", "warning")

    return redirect(url_for("admin.courses_list"))


# ==============================================================================
# 8. Project Submissions & Review Queue
# ==============================================================================

@admin_bp.route("/submissions")
def submissions_list():
    """Admin Review Queue: Filter, inspect, and evaluate student project submissions."""
    db = get_db()
    status_filter = request.args.get("status", "all").strip()

    query = {}
    if status_filter != "all":
        query["status"] = status_filter

    submissions = Submission.find_all(query=query, sort=[("created_at", -1)])

    # Collect stats for filter tabs
    total_submissions = db.submissions.count_documents({})
    pending_count = db.submissions.count_documents({"status": Submission.STATUS_PENDING})
    changes_count = db.submissions.count_documents({"status": Submission.STATUS_CHANGES})
    rejected_count = db.submissions.count_documents({"status": Submission.STATUS_REJECTED})
    approved_count = db.submissions.count_documents({"status": Submission.STATUS_APPROVED})

    return render_template(
        "admin/submissions.html",
        submissions=submissions,
        status_filter=status_filter,
        total_submissions=total_submissions,
        pending_count=pending_count,
        changes_count=changes_count,
        rejected_count=rejected_count,
        approved_count=approved_count
    )


@admin_bp.route("/submissions/<submission_id>/review", methods=["GET", "POST"])
def submission_review(submission_id):
    """Detailed grading interface with rubric scorecard, feedback, and certificate issuance."""
    submission = Submission.get_by_id(submission_id)
    if not submission:
        flash("Submission not found.", "danger")
        return redirect(url_for("admin.submissions_list"))

    student = submission.user
    course = submission.course
    assignment = submission.assignment
    previous_review = submission.review

    if request.method == "POST":
        decision = request.form.get("decision", "").strip().lower()
        feedback = request.form.get("feedback", "").strip()

        if decision not in ["approved", "changes_requested", "rejected"]:
            flash("Invalid decision. Please select Approved, Changes Requested, or Rejected.", "danger")
            return redirect(url_for("admin.submission_review", submission_id=submission.id))

        if not feedback:
            flash("Please provide constructive feedback explaining your decision.", "danger")
            return redirect(url_for("admin.submission_review", submission_id=submission.id))

        # Collect scores: Quiz vs Project Rubric
        is_quiz_submission = getattr(submission, "is_quiz", False) or submission.evaluation_type == "quiz_based"
        if is_quiz_submission and submission.quiz_results:
            q_results = submission.quiz_results.get("questions", [])
            total_score = 0
            max_score = int(submission.quiz_results.get("total_marks", 100) or 100)
            scores = {}
            for q in q_results:
                q_id = q.get("question_id")
                manual_input = request.form.get(f"manual_score_{q_id}")
                if manual_input is not None and manual_input.strip() != "":
                    try:
                        awarded = float(manual_input)
                        q["awarded_marks"] = awarded
                        q["is_correct"] = (awarded == q.get("max_marks"))
                        q["needs_manual_review"] = False
                    except ValueError:
                        pass
                total_score += float(q.get("awarded_marks", 0))
                scores[q.get("question", f"Q_{q_id}")] = q.get("awarded_marks", 0)

            total_score = round(total_score, 2)
            percentage_score = int(round((total_score / max_score) * 100)) if max_score > 0 else int(total_score)
            submission.quiz_results["marks_obtained"] = total_score
            submission.quiz_results["percentage"] = percentage_score
            submission.quiz_results["requires_manual_review"] = any(q.get("needs_manual_review") for q in q_results)
            submission.quiz_results["is_passed"] = (percentage_score >= (getattr(assignment, "passing_score", 70) if assignment else 70))
        else:
            rubric = assignment.rubric if assignment else Assignment.DEFAULT_RUBRIC
            scores = {}
            total_score = 0
            max_score = 0
            for i, item in enumerate(rubric):
                criterion = item.get("criterion", f"Criterion {i+1}")
                max_pts = int(item.get("max_points", 25))
                max_score += max_pts
                try:
                    pts = int(request.form.get(f"score_{i}", max_pts))
                    pts = max(0, min(max_pts, pts))
                except (ValueError, TypeError):
                    pts = max_pts
                scores[criterion] = pts
                total_score += pts

            percentage_score = int(round((total_score / max_score) * 100)) if max_score > 0 else total_score

        passing_score = getattr(assignment, "passing_score", 70) if assignment else 70

        if decision == "approved" and percentage_score < passing_score:
            flash(f"Approval Failed: Awarded score of {percentage_score}% ({total_score}/{max_score} pts) does not meet the passing score requirement of {passing_score}%. Please adjust the scores or select 'Request Changes' / 'Reject'.", "danger")
            return redirect(url_for("admin.submission_review", submission_id=submission.id))

        # Save review
        review = Review({
            "submission_id": str(submission.id),
            "reviewer_id": str(current_user.id),
            "decision": decision,
            "scores": scores,
            "total_score": total_score,
            "max_score": max_score,
            "feedback": feedback,
            "created_at": datetime.now(timezone.utc)
        })
        review.save()

        # Update submission with score & status
        submission.status = decision
        submission.automated_score = percentage_score
        submission.reviewer_id = str(current_user.id)
        submission.review_feedback = feedback
        submission.reviewed_at = datetime.now(timezone.utc)
        submission.save()

        if decision == "approved":
            # Check if this course or capstone qualifies for Certificate issuance
            cert = Certificate.issue(student, course, assignment, submission)
            if cert:
                flash(f"🎉 Submission Approved with {percentage_score}%! Verified Certificate #{cert.certificate_id} has been officially issued to {student.name}.", "success")
            else:
                if assignment and assignment.is_final_capstone:
                    flash(f"⚠️ Capstone approved with {percentage_score}%, but certificate is withheld until student watches at least 80% of the lecture video.", "warning")
                else:
                    flash(f"🎉 Milestone {submission.step_number} Approved with {percentage_score}%! Milestone marked as passed and next milestone unlocked for {student.name}.", "success")
        elif decision == "changes_requested":
            flash(f"Changes requested for {student.name}'s submission ({percentage_score}%). Student notified with reviewer guidance on their dashboard.", "info")
        else:
            flash(f"Submission rejected with feedback ({percentage_score}%). Student may review requirements and resubmit.", "warning")

        return redirect(url_for("admin.submissions_list"))

    return render_template(
        "admin/submission_review.html",
        submission=submission,
        student=student,
        course=course,
        assignment=assignment,
        previous_review=previous_review
    )


# ==============================================================================
# 9. Storage Maintenance & Automated Cleanup
# ==============================================================================

@admin_bp.route("/maintenance/storage-clean", methods=["POST"])
def storage_clean():
    """Runs on-demand storage optimization: purges 7-day inactive users and orphaned records."""
    from services.storage_cleaner import run_storage_optimization
    try:
        days = int(request.form.get("days", 7))
    except (ValueError, TypeError):
        days = 7
    stats = run_storage_optimization(days=days)
    flash(
        f"🧹 Storage Optimization Complete! Purged {stats['purged_inactive_users']} inactive users (inactive >= {days} days) "
        f"and {stats['purged_orphaned_records']} orphaned records across all collections.",
        "success"
    )
    return redirect(url_for("admin.dashboard"))




# ==============================================================================
# 10. Interview Test Series Management
# ==============================================================================

@admin_bp.route("/test-series")
@admin_bp.route("/test-series/tests")
@admin_bp.route("/test-series", endpoint="test_series_list")
@admin_bp.route("/test-series/tests", endpoint="test_series_tests_list")
def test_series_tests_list():
    """Admin Test Series: View, create, and manage mock tests."""
    tests = TestDefinition.find_all()
    db = get_db()
    # Compute attempt metrics for each test
    test_metrics = {}
    for t in tests:
        attempts_count = db[TestAttempt.collection_name].count_documents({"test_id": t.id})
        completed_count = db[TestAttempt.collection_name].count_documents({"test_id": t.id, "status": TestAttempt.STATUS_COMPLETED})
        test_metrics[t.id] = {
            "attempts": attempts_count,
            "completed": completed_count,
            "questions_count": len(t.question_ids)
        }
    return render_template(
        "admin/test_series/tests_list.html",
        tests=tests,
        metrics=test_metrics
    )

@admin_bp.route("/test-series/tests/new", methods=["GET", "POST"])
def test_series_test_new():
    """Create a new mock test with configurable questions, duration, and focus loss thresholds."""
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        slug = request.form.get("slug", "").strip() or slugify(title)
        category = request.form.get("category", "Quantitative Aptitude").strip()
        difficulty = request.form.get("difficulty", "Beginner").strip()
        description = request.form.get("description", "").strip()
        duration_minutes = int(request.form.get("duration_minutes", 30))
        total_questions_count = int(request.form.get("total_questions_count", 30))
        passing_percentage = float(request.form.get("passing_percentage", 50.0))
        is_free = request.form.get("is_free") == "1"
        is_published = request.form.get("is_published") == "1"
        max_warnings = int(request.form.get("max_warnings", 3))
        selected_question_ids = request.form.getlist("question_ids")

        # Optional attached video resources
        video_title = request.form.get("video_title", "").strip()
        video_url = request.form.get("video_url", "").strip()
        video_resources = []
        if video_title and video_url:
            video_resources.append({
                "title": video_title,
                "youtube_url": video_url,
                "topic": category,
                "description": "Preparation video guide"
            })

        test = TestDefinition({
            "title": title,
            "slug": slug,
            "category": category,
            "difficulty": difficulty,
            "description": description,
            "duration_minutes": duration_minutes,
            "total_questions_count": total_questions_count or len(selected_question_ids),
            "passing_percentage": passing_percentage,
            "is_free": is_free,
            "is_published": is_published,
            "question_ids": selected_question_ids,
            "video_resources": video_resources,
            "focus_loss_policy": {
                "enabled": True,
                "max_warnings": max_warnings,
                "warning_cooldown_seconds": 5
            }
        }).save()

        flash(f"Test '{title}' created successfully!", "success")
        return redirect(url_for("admin.test_series_tests_list"))

    # GET: fetch questions for manual picker
    available_questions = Question.find_all(limit=100)
    return render_template(
        "admin/test_series/test_form.html",
        test=None,
        questions=available_questions
    )

@admin_bp.route("/test-series/tests/<test_id>/edit", methods=["GET", "POST"])
def test_series_test_edit(test_id):
    """Edit an existing mock test configuration."""
    test = TestDefinition.get_by_id(test_id)
    if not test:
        flash("Test not found.", "danger")
        return redirect(url_for("admin.test_series_tests_list"))

    if request.method == "POST":
        test.title = request.form.get("title", "").strip()
        test.slug = request.form.get("slug", "").strip() or slugify(test.title)
        test.category = request.form.get("category", test.category).strip()
        test.difficulty = request.form.get("difficulty", test.difficulty).strip()
        test.description = request.form.get("description", "").strip()
        test.duration_minutes = int(request.form.get("duration_minutes", test.duration_minutes))
        test.total_questions_count = int(request.form.get("total_questions_count", test.total_questions_count))
        test.passing_percentage = float(request.form.get("passing_percentage", test.passing_percentage))
        test.is_free = request.form.get("is_free") == "1"
        test.is_published = request.form.get("is_published") == "1"
        test.focus_loss_policy["max_warnings"] = int(request.form.get("max_warnings", 3))

        selected_qids = request.form.getlist("question_ids")
        if selected_qids:
            test.question_ids = selected_qids

        # Video update
        video_title = request.form.get("video_title", "").strip()
        video_url = request.form.get("video_url", "").strip()
        if video_title and video_url:
            test.video_resources = [{
                "title": video_title,
                "youtube_url": video_url,
                "topic": test.category,
                "description": "Preparation video guide"
            }]

        test.save()
        flash(f"Test '{test.title}' updated successfully!", "success")
        return redirect(url_for("admin.test_series_tests_list"))

    available_questions = Question.find_all(limit=150)
    return render_template(
        "admin/test_series/test_form.html",
        test=test,
        questions=available_questions
    )

@admin_bp.route("/test-series/tests/<test_id>/toggle", methods=["POST"])
def test_series_test_toggle(test_id):
    """Toggle publish status of a test."""
    test = TestDefinition.get_by_id(test_id)
    if not test:
        flash("Test not found.", "danger")
        return redirect(url_for("admin.test_series_tests_list"))

    test.is_published = not test.is_published
    test.save()
    status_str = "Published" if test.is_published else "Drafted"
    flash(f"Test '{test.title}' is now {status_str}.", "info")
    return redirect(url_for("admin.test_series_tests_list"))

@admin_bp.route("/test-series/tests/<test_id>/delete", methods=["POST"])
def test_series_test_delete(test_id):
    """Permanently deletes a test definition."""
    test = TestDefinition.get_by_id(test_id)
    if test:
        title = test.title
        test.delete()
        flash(f"Test '{title}' has been deleted.", "warning")
    return redirect(url_for("admin.test_series_tests_list"))

@admin_bp.route("/test-series/packs")
def test_series_packs_list():
    """Admin view for test packs and configurable pricing."""
    packs = TestPack.find_all()
    return render_template("admin/test_series/packs_list.html", packs=packs)

@admin_bp.route("/test-series/packs/<pack_id>/edit", methods=["POST"])
def test_series_pack_edit(pack_id):
    """Updates configurable pricing, status, and features of a test pack."""
    pack = TestPack.get_by_id(pack_id)
    if not pack:
        flash("Test pack not found.", "danger")
        return redirect(url_for("admin.test_series_packs_list"))

    try:
        pack.price_inr = int(request.form.get("price_inr", pack.price_inr))
        pack.is_free = (pack.price_inr == 0)
    except ValueError:
        pass
    pack.status = request.form.get("status", pack.status).strip()
    pack.badge_text = request.form.get("badge_text", pack.badge_text).strip()
    pack.short_description = request.form.get("short_description", pack.short_description).strip()
    pack.save()
    flash(f"Test pack '{pack.title}' updated (Price: ₹{pack.price_inr}, Status: {pack.status}).", "success")
    return redirect(url_for("admin.test_series_packs_list"))

@admin_bp.route("/test-series/questions")
def test_series_questions_list():
    """Question Bank Management: Filter, search, and add questions."""
    category = request.args.get("category", "").strip()
    difficulty = request.args.get("difficulty", "").strip()
    search = request.args.get("q", "").strip()

    query = {}
    if category:
        query["category"] = category
    if difficulty:
        query["difficulty"] = difficulty
    if search:
        query["question_text"] = {"$regex": search, "$options": "i"}

    questions = Question.find_all(query, limit=100)
    total_count = Question.count()

    return render_template(
        "admin/test_series/questions_list.html",
        questions=questions,
        total_count=total_count,
        selected_category=category,
        selected_difficulty=difficulty,
        search=search
    )

@admin_bp.route("/test-series/questions/new", methods=["GET", "POST"])
def test_series_question_new():
    """Add a new question with choices, code snippet, and explanation."""
    if request.method == "POST":
        q_text = request.form.get("question_text", "").strip()
        q_type = request.form.get("question_type", Question.TYPE_SINGLE_CHOICE)
        category = request.form.get("category", "Quantitative Aptitude").strip()
        subtopic = request.form.get("subtopic", "General").strip()
        difficulty = request.form.get("difficulty", "Beginner").strip()
        code_snippet = request.form.get("code_snippet", "").strip()
        language = request.form.get("language", "").strip()
        marks = float(request.form.get("marks", 1.0))
        negative_marks = float(request.form.get("negative_marks", 0.0))
        explanation = request.form.get("explanation", "").strip()

        # Parse options
        options = []
        for i in range(1, 5):
            opt_text = request.form.get(f"option_{i}", "").strip()
            if opt_text:
                options.append({"id": f"opt_{i}", "text": opt_text})

        correct_ans = request.form.getlist("correct_answers")

        Question({
            "question_text": q_text,
            "question_type": q_type,
            "category": category,
            "subtopic": subtopic,
            "difficulty": difficulty,
            "options": options,
            "correct_answers": correct_ans,
            "explanation": explanation,
            "code_snippet": code_snippet,
            "language": language,
            "marks": marks,
            "negative_marks": negative_marks,
            "is_published": True
        }).save()

        flash("Question added to question bank successfully!", "success")
        return redirect(url_for("admin.test_series_questions_list"))

    return render_template("admin/test_series/question_form.html", question=None)

@admin_bp.route("/test-series/questions/<question_id>/delete", methods=["POST"])
def test_series_question_delete(question_id):
    """Deletes a question from the question bank."""
    q = Question.get_by_id(question_id)
    if q:
        q.delete()
        flash("Question deleted from bank.", "info")
    return redirect(url_for("admin.test_series_questions_list"))

@admin_bp.route("/test-series/attempts")
def test_series_attempts_list():
    """Audit log of student test attempts, scores, and focus-loss violation records."""
    attempts = TestAttempt.find_all(limit=100)
    db = get_db()
    # Pre-fetch user names
    user_ids = list({_to_obj_id(a.user_id) for a in attempts if _to_obj_id(a.user_id)})
    user_map = {str(u["_id"]): u.get("name", "Student") for u in db[User.collection_name].find({"_id": {"$in": user_ids}})}

    return render_template(
        "admin/test_series/attempts_list.html",
        attempts=attempts,
        user_map=user_map
    )


# ==============================================================================
# 11. Automated Student Learning & Certificate Reminders
# ==============================================================================

@admin_bp.route("/reminders/trigger", methods=["GET", "POST"])
def reminders_trigger():
    """Manually triggers a scan and email dispatch for students with pending lectures or waiting certificates."""
    if request.method == "GET":
        return redirect(url_for("admin.settings_page"))

    force = request.form.get("force") == "1"

    def _bg_scan():
        try:
            from services.reminder_service import scan_and_send_student_reminders
            scan_and_send_student_reminders(force=force)
        except Exception as e:
            logger.error(f"Error triggering student reminders: {e}")

    threading.Thread(target=_bg_scan, daemon=True).start()
    flash(
        "Student Reminders scan launched in background! Eligible students are being processed asynchronously without slowing down the site.",
        "success"
    )
    return redirect(url_for("admin.settings_page"))


@admin_bp.route("/reminders/test-email", methods=["GET", "POST"])
def reminders_test_email():
    """Sends a sample test email to verify Gmail SMTP connection with skillrockk@gmail.com."""
    if request.method == "GET":
        return redirect(url_for("admin.settings_page"))

    recipient = (request.form.get("recipient") or current_user.email or "skillrockk@gmail.com").strip()

    def _bg_test():
        try:
            from services.reminder_service import build_reminder_email_content, _dispatch_smtp_email
            subject, html_body, text_body = build_reminder_email_content(
                student_name=getattr(current_user, "name", "Admin Test"),
                course_title="Artificial Intelligence and Machine Learning Fundamentals",
                course_slug="complete-aiml-job-ready-batch-introduction",
                reminder_type="certificate_waiting",
                watch_percent=85,
                resume_time="14:20"
            )
            success, msg = _dispatch_smtp_email(f"[TEST] {subject}", html_body, text_body, recipient)
            if not success:
                logger.info(f"[TEST EMAIL NOTE] {msg}")
        except Exception as e:
            logger.error(f"Error sending test email: {e}")

    threading.Thread(target=_bg_test, daemon=True).start()
    flash(
        f"Test reminder email dispatch initiated for {recipient}! If cloud host network restricts SMTP, simulated dispatch is safely recorded.",
        "info"
    )
    return redirect(url_for("admin.settings_page"))
