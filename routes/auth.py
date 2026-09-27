"""
SkillSwap Campus — Authentication Routes
Includes real Google OAuth 2.0 and secure email login/registration.
Removes all fake demo accounts.
"""

import os
import logging
from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from models import User, PlatformSettings
from services.google_auth import (
    is_google_auth_configured,
    get_google_auth_flow,
    fetch_google_user_profile
)

logger = logging.getLogger(__name__)
auth_bp = Blueprint("auth", __name__)

# ==============================================================================
# Google OAuth 2.0 Authentication
# ==============================================================================

@auth_bp.route("/auth/google")
def google_login():
    """Initiates Google OAuth 2.0 login / sign up / account connection flow."""
    # Never redirect to login, register, or auth callback after authenticating
    raw_next = request.args.get("next") or request.referrer or ""
    if not raw_next or any(x in str(raw_next).lower() for x in ["login", "register", "auth"]):
        next_url = url_for("dashboard.dashboard")
    else:
        next_url = raw_next
    session["oauth_next"] = next_url

    if not is_google_auth_configured():
        flash(
            "Google Login is not configured yet. MANUAL CONFIGURATION REQUIRED: "
            "Please configure GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in your .env file. "
            "See GOOGLE_SETUP.md for complete step-by-step instructions.",
            "warning"
        )
        if current_user.is_authenticated:
            return redirect(next_url)
        return redirect(url_for("auth.login"))

    # If user is already authenticated, mark this session as an account linking flow
    if current_user.is_authenticated:
        session["linking_user_id"] = str(current_user.id)
    else:
        session.pop("linking_user_id", None)

    # Determine redirect URI (prefer explicitly configured or dynamically built)
    configured_redirect = os.getenv("GOOGLE_REDIRECT_URI", "").strip()
    if configured_redirect and "YOUR_" not in configured_redirect:
        redirect_uri = configured_redirect
    else:
        redirect_uri = url_for("auth.google_callback", _external=True)

    try:
        flow = get_google_auth_flow(redirect_uri)
        authorization_url, state = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
            prompt="consent"
        )
        session["oauth_state"] = state
        session["oauth_redirect_uri"] = redirect_uri
        return redirect(authorization_url)
    except Exception as e:
        logger.error(f"Error initiating Google OAuth: {e}")
        flash(f"Could not initiate Google Login: {str(e)}", "danger")
        if current_user.is_authenticated:
            return redirect(next_url)
        return redirect(url_for("auth.login"))


@auth_bp.route("/auth/google/callback")
def google_callback():
    """Callback endpoint for Google OAuth 2.0 (handles login and account linking)."""
    if not is_google_auth_configured():
        flash("Google Login is not configured yet.", "danger")
        return redirect(url_for("auth.login"))

    stored_state = session.get("oauth_state") or request.args.get("state")
    redirect_uri = session.get("oauth_redirect_uri") or os.getenv("GOOGLE_REDIRECT_URI", "").strip() or url_for("auth.google_callback", _external=True)
    next_url = session.pop("oauth_next", url_for("dashboard.dashboard"))
    if not next_url or any(x in str(next_url).lower() for x in ["login", "register", "auth"]):
        next_url = url_for("dashboard.dashboard")
    linking_user_id = session.pop("linking_user_id", None)

    try:
        flow = get_google_auth_flow(redirect_uri, state=stored_state)
        # Fetch tokens using the full authorization response URL
        flow.fetch_token(authorization_response=request.url)
        credentials = flow.credentials
    except Exception as e:
        logger.error(f"Google OAuth token exchange failed: {e}")
        flash(f"Google authentication was cancelled or failed ({str(e)}). Please try again.", "danger")
        return redirect(url_for("auth.login"))

    # Fetch user profile info from Google
    user_info = fetch_google_user_profile(credentials.token)
    if not user_info or "email" not in user_info:
        flash("Failed to retrieve your Google account profile. Please try again.", "danger")
        return redirect(url_for("auth.login"))

    email = user_info.get("email", "").strip().lower()
    name = user_info.get("name", "Student").strip()
    google_id = user_info.get("sub")
    picture = user_info.get("picture", "")

    # Handle Case 1: Existing logged-in student linking their Google account
    if linking_user_id:
        target_user = User.get_by_id(linking_user_id) or (current_user if current_user.is_authenticated else None)
        if target_user:
            target_user.google_id = google_id
            if picture and not target_user.google_picture:
                target_user.google_picture = picture
            target_user.google_access_token = credentials.token
            target_user.google_refresh_token = credentials.refresh_token or target_user.google_refresh_token
            if credentials.expiry:
                target_user.google_token_expiry = credentials.expiry
            target_user.save()
            flash("Your Google account has been connected successfully! Real Google Meet links will now be generated automatically for your sessions.", "success")
            return redirect(next_url)

    # Handle Case 2: Standard Google Login / Signup
    user = User.get_by_email(email)
    is_new_user = False

    if not user:
        user = User.create(
            email=email,
            name=name,
            google_id=google_id,
            google_picture=picture,
            google_access_token=credentials.token,
            google_refresh_token=credentials.refresh_token,
            google_token_expiry=credentials.expiry,
            college="",
            branch="",
            year="",
            bio="",
            xp=0,
            rating=0.0,
            rating_count=0
        )
        is_new_user = True
    else:
        # Update with newest tokens and Google profile info
        user.google_id = google_id
        if picture:
            user.google_picture = picture
        if credentials.token:
            user.google_access_token = credentials.token
        if credentials.refresh_token:
            user.google_refresh_token = credentials.refresh_token
        if credentials.expiry:
            user.google_token_expiry = credentials.expiry
        user.save()

    # Log in user with persistent remember cookie
    login_user(user, remember=True)

    if is_new_user or not user.college:
        flash(f"Welcome to Skill Rock, {user.name}! Please set your campus and skills to get started.", "success")
        return redirect(url_for("profile.edit_profile"))

    flash(f"Signed in as {user.name} via Google.", "success")
    return redirect(next_url)


# ==============================================================================
# Standard Campus Email / Password Authentication
# ==============================================================================

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.dashboard"))

    settings = PlatformSettings.get_settings()
    if not settings.get("allow_registrations", True):
        flash("New student registrations are currently paused by the platform administrator.", "warning")
        return render_template("register.html")

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        college = request.form.get("college", "").strip()
        branch = request.form.get("branch", "").strip()
        year = request.form.get("year", "").strip()

        if not all([name, email, password, college, branch, year]):
            flash("All fields are required to create your campus account.", "danger")
            return render_template("register.html", name=name, email=email, college=college, branch=branch, year=year)

        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "danger")
            return render_template("register.html", name=name, email=email, college=college, branch=branch, year=year)

        # Check duplicate user in MongoDB
        existing_user = User.get_by_email(email)
        if existing_user:
            flash("An account with this email already exists. Please log in.", "warning")
            return redirect(url_for("auth.login"))

        welcome_xp = int(settings.get("welcome_xp", 50))
        new_user = User.create(
            name=name,
            email=email,
            college=college,
            branch=branch,
            year=year,
            bio=f"Student at {college} studying {branch}.",
            xp=welcome_xp,
            rating=0.0,
            rating_count=0
        )
        new_user.set_password(password)
        new_user.save()

        login_user(new_user, remember=True)
        flash(f"Welcome to Skill Rock, {new_user.name}! Let's add your skills.", "success")
        return redirect(url_for("profile.profile"))

    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        if getattr(current_user, "is_admin", False):
            return redirect(url_for("admin.admin_dashboard"))
        return redirect(url_for("dashboard.dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Please enter both email and password.", "danger")
            return render_template("login.html", email=email)

        user = User.get_by_email(email)
        if not user or not user.check_password(password):
            flash("Invalid email or password. Please try again.", "danger")
            return render_template("login.html", email=email)

        if getattr(user, "is_banned", False):
            reason = getattr(user, "ban_reason", "") or "Terms violation or community guideline breach."
            flash(f"Your account has been suspended: {reason}. Contact Palt51419@gmail.com for assistance.", "danger")
            return render_template("login.html", email=email)

        login_user(user, remember=True)
        flash(f"Welcome back, {user.name}!", "success")
        raw_next = request.args.get("next")
        if not raw_next or any(x in str(raw_next).lower() for x in ["login", "register", "auth"]):
            if getattr(user, "is_admin", False):
                next_page = url_for("admin.admin_dashboard")
            else:
                next_page = url_for("dashboard.dashboard")
        else:
            next_page = raw_next
        return redirect(next_page)

    return render_template("login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been signed out.", "info")
    return redirect(url_for("index"))
