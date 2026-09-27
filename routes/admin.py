"""
SkillSwap Campus — Master Administration Suite
Comprehensive administrative dashboard, user control, profile management,
password reset, database inspection, and dynamic system settings.
"""

import os
import sys
import platform
import logging
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
from models import (
    get_db,
    User,
    Skill,
    Connection,
    SwapRequest,
    Session,
    Message,
    PlatformSettings
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
        return redirect(url_for("dashboard.dashboard"))


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

    # Pre-calculate counts for each user (connections, messages)
    enriched_users = []
    for u in users:
        conn_count = Connection.count({"$or": [{"user1_id": u.id}, {"user2_id": u.id}]})
        has_local_password = bool(u.password_hash)
        has_google = bool(u.google_id or u.google_access_token)
        enriched_users.append({
            "user": u,
            "connections_count": conn_count,
            "has_local_password": has_local_password,
            "has_google": has_google
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

    return render_template(
        "admin/user_detail.html",
        target_user=user,
        connections=connections,
        messages=messages,
        hash_algorithm=hash_algorithm,
        hash_preview=hash_preview
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
