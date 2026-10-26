"""
Skill Rock — Learn & Build Blueprint
Core Learning Platform: Free curated video courses, real-world project assignments,
student submission workflow, project review tracking, and tamper-proof certificate generation.
"""

import re
import logging
from urllib.parse import urlparse
from datetime import datetime, timezone
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify,
    abort
)
from flask_login import login_required, current_user
from models import (
    get_db,
    User,
    Course,
    Assignment,
    Enrollment,
    Submission,
    Review,
    Certificate,
    extract_youtube_id,
    slugify
)

logger = logging.getLogger(__name__)

learning_bp = Blueprint("learning", __name__, url_prefix="/learning")


# ==============================================================================
# Helper Functions & URL Validation
# ==============================================================================

def is_valid_url(url):
    """Validates if a URL is well-formed with http/https scheme and a valid network domain."""
    if not url or not isinstance(url, str):
        return False
    url = url.strip()
    try:
        parsed = urlparse(url)
        return parsed.scheme in ["http", "https"] and bool(parsed.netloc) and ("." in parsed.netloc or parsed.hostname == "localhost")
    except Exception:
        return False


def is_valid_github_url(url):
    """Validates that a URL is a legitimate public GitHub repository link."""
    if not is_valid_url(url):
        return False
    pattern = r"^https?:\/\/(www\.)?github\.com\/[a-zA-Z0-9_\-\.]+\/[a-zA-Z0-9_\-\.]+(\/.*)?$"
    return bool(re.match(pattern, url.strip()))


# ==============================================================================
# Curated Study Interests (Bubble Selection for Students)
# ==============================================================================

AVAILABLE_INTERESTS = [
    {
        "id": "Programming",
        "name": "Programming",
        "icon": "code",
        "emoji": "💻",
        "description": "Python, C++, Java, Object-Oriented Design & Scripting"
    },
    {
        "id": "Web Development",
        "name": "Web Development",
        "icon": "globe",
        "emoji": "🌐",
        "description": "HTML5, CSS3, JavaScript ES6+, React & Full-Stack Apps"
    },
    {
        "id": "AI & Machine Learning",
        "name": "AI & Machine Learning",
        "icon": "cpu",
        "emoji": "🤖",
        "description": "Data Modeling, Neural Networks, Computer Vision & LLMs"
    },
    {
        "id": "Data Science",
        "name": "Data Science",
        "icon": "bar-chart-2",
        "emoji": "📊",
        "description": "SQL, Pandas, NumPy, Data Cleaning & Analytics Dashboards"
    },
    {
        "id": "Mobile App Development",
        "name": "Mobile Apps",
        "icon": "smartphone",
        "emoji": "📱",
        "description": "Flutter, Dart, Android & Cross-Platform Mobile Applications"
    },
    {
        "id": "Cloud & DevOps",
        "name": "Cloud & DevOps",
        "icon": "cloud",
        "emoji": "☁️",
        "description": "Docker, Linux, Production Deployments, CI/CD & Cloud APIs"
    },
    {
        "id": "Cybersecurity",
        "name": "Cybersecurity",
        "icon": "shield-check",
        "emoji": "🛡️",
        "description": "Network Security, Web Pentesting, Safe Auth & Defense"
    },
    {
        "id": "UI/UX Design",
        "name": "UI/UX Design",
        "icon": "layout",
        "emoji": "🎨",
        "description": "Figma, User Research, Wireframes, Responsive Design Systems"
    },
    {
        "id": "Database Engineering",
        "name": "Databases",
        "icon": "database",
        "emoji": "🗄️",
        "description": "PostgreSQL, MongoDB, Redis, Schema Design & Performance"
    },
    {
        "id": "Tech Fundamentals & DSA",
        "name": "Tech & DSA",
        "icon": "terminal",
        "emoji": "⚡",
        "description": "Data Structures, Algorithms, Problem Solving & System Design"
    }
]


# ==============================================================================
# 0. Student Study Interests Onboarding (Interactive Bubble Form)
# ==============================================================================

@learning_bp.route("/onboarding", methods=["GET", "POST"])
@learning_bp.route("/interests", methods=["GET", "POST"])
@login_required
def onboarding_interests():
    """
    Interactive bubble selection onboarding for student interests.
    Allows students to pick up to 3 topics (Programming, Web Dev, AI, etc.)
    that automatically personalize their course feed and project recommendations.
    """
    if request.method == "POST":
        if request.is_json:
            data = request.get_json() or {}
            selected = data.get("interests", [])
        else:
            selected = request.form.getlist("interests")
            if not selected and request.form.get("interests"):
                selected = [s.strip() for s in request.form.get("interests").split(",") if s.strip()]

        clean = [str(x).strip() for x in selected if str(x).strip()][:3]
        if not clean:
            if request.is_json:
                return jsonify({"success": False, "error": "Please select at least 1 study interest."}), 400
            flash("Please choose at least 1 topic to customize your learning journey.", "warning")
            return redirect(url_for("learning.onboarding_interests"))

        current_user.set_interests(clean)
        logger.info(f"Student {current_user.email} updated study interests: {clean}")

        if request.is_json:
            return jsonify({
                "success": True,
                "interests": clean,
                "redirect": url_for("learning.courses_list")
            })

        flash(f"Your learning journey is customized for: {', '.join(clean)}! Explore curated courses below.", "success")
        return redirect(url_for("learning.courses_list"))

    return render_template(
        "learning/onboarding_interests.html",
        available_interests=AVAILABLE_INTERESTS,
        user_interests=current_user.interests
    )


# ==============================================================================
# 1. Course Catalogue (Browse & Discover Free Courses)
# ==============================================================================

@learning_bp.route("")
@learning_bp.route("/")
@learning_bp.route("/courses")
def courses_list():
    """
    Public Course Catalogue.
    Allows students to browse curated free learning courses with category,
    difficulty, and search filtering. Personalizes ranking based on student's
    selected interest bubbles.
    """
    try:
        category = request.args.get("category", "").strip()
        difficulty = request.args.get("difficulty", "").strip()
        language = request.args.get("language", "").strip()
        search = request.args.get("q", "").strip()

        query = {"is_published": True}
        if category and category != "All":
            query["category"] = category
        if difficulty and difficulty != "All":
            query["difficulty"] = difficulty
        if language and language != "All":
            query["language"] = {"$regex": f"^{re.escape(language)}$", "$options": "i"}
        if search:
            safe_search = re.escape(search)
            query["$or"] = [
                {"title": {"$regex": safe_search, "$options": "i"}},
                {"description": {"$regex": safe_search, "$options": "i"}},
                {"category": {"$regex": safe_search, "$options": "i"}},
                {"instructor": {"$regex": safe_search, "$options": "i"}},
                {"language": {"$regex": safe_search, "$options": "i"}}
            ]

        if (not category or category == "All") and not difficulty and not language and not search:
            courses = Course.get_published_courses() or []
        else:
            courses = Course.find_all(query=query, sort=[("created_at", -1)]) or []
            if courses:
                course_ids = [str(c.id) for c in courses]
                asg_map = Assignment.get_by_courses(course_ids)
                for c in courses:
                    c._cached_assignment = asg_map.get(str(c.id))

        # Collect enrolled course IDs and certified course IDs for the logged-in user
        enrolled_course_ids = set()
        completed_course_ids = set()
        user_interests = []
        recommended_courses = []
        other_courses = []

        if current_user.is_authenticated:
            try:
                user_enrollments = Enrollment.find_by_user(current_user.id) or []
                for e in user_enrollments:
                    enrolled_course_ids.add(str(getattr(e, "course_id", "")))
                    if getattr(e, "status", "") == "completed":
                        completed_course_ids.add(str(getattr(e, "course_id", "")))
            except Exception as e_enr:
                logger.warning(f"Could not load enrollments for user {current_user.id}: {e_enr}")

            try:
                user_interests = [str(i).strip() for i in (current_user.interests or []) if str(i).strip()]
            except Exception as e_int:
                logger.warning(f"Could not read user interests: {e_int}")
                user_interests = []

        # Personalized Recommendation Algorithm:
        # If the user has selected interests and hasn't explicitly applied a narrow category filter,
        # partition courses into recommended (matching chosen interests) and others.
        if user_interests and (not category or category == "All") and not search:
            norm_interests = [str(i).lower() for i in user_interests if i]
            for c in courses:
                c_cat = str(getattr(c, "category", "") or "").lower()
                c_title = str(getattr(c, "title", "") or "").lower()
                # Check match against user's interest bubbles
                matched = any(
                    interest in c_cat or c_cat in interest or interest in c_title
                    for interest in norm_interests
                )
                if matched:
                    recommended_courses.append(c)
                else:
                    other_courses.append(c)
        else:
            other_courses = list(courses)

        # Distinct categories for filter pills (in-memory extraction when viewing all courses, avoiding remote roundtrip)
        available_categories = []
        try:
            if not category or category == "All":
                cat_set = set(str(getattr(c, "category", "")).strip() for c in courses if getattr(c, "category", None))
                available_categories = sorted(list(cat_set))
            if not available_categories:
                db = get_db()
                raw_cats = db.courses.distinct("category", {"is_published": True}) or []
                available_categories = [str(c).strip() for c in raw_cats if c and str(c).strip()]
        except Exception as e_cat:
            logger.warning(f"Could not fetch distinct categories: {e_cat}")
            available_categories = ["Programming", "Web Development", "AI & Machine Learning", "Data Science", "Mobile Apps"]

        return render_template(
            "learning/courses.html",
            courses=courses,
            recommended_courses=recommended_courses,
            other_courses=other_courses,
            user_interests=user_interests,
            available_interests=AVAILABLE_INTERESTS,
            selected_category=category,
            selected_difficulty=difficulty,
            selected_language=language,
            search_query=search,
            available_categories=available_categories,
            enrolled_course_ids=enrolled_course_ids,
            completed_course_ids=completed_course_ids,
            total_courses=len(courses)
        )
    except Exception as e:
        logger.exception(f"Unhandled error in courses_list: {e}")
        flash("An error occurred while loading the courses catalogue. Please refresh or try again.", "danger")
        return render_template(
            "learning/courses.html",
            courses=[],
            recommended_courses=[],
            other_courses=[],
            user_interests=[],
            available_interests=AVAILABLE_INTERESTS,
            selected_category="",
            selected_difficulty="",
            selected_language="",
            search_query="",
            available_categories=["Programming", "Web Development", "AI & Machine Learning", "Data Science"],
            enrolled_course_ids=set(),
            completed_course_ids=set(),
            total_courses=0
        )


# ==============================================================================
# 2. Course Details & Learning Player Page
# ==============================================================================

@learning_bp.route("/courses/<slug>")
def course_detail(slug):
    """
    Dedicated Course Page.
    Features YouTube video embed, course objectives, syllabus,
    practical project assignment briefing, and enrolment trigger.
    """
    course = Course.get_by_slug(slug)
    if not course:
        # Fallback check by MongoDB ObjectId
        course = Course.get_by_id(slug)
    if not course or (not course.is_published and not getattr(current_user, "is_admin", False)):
        flash("The requested course could not be found or is not yet published.", "warning")
        return redirect(url_for("learning.courses_list"))

    assignment = course.assignment
    enrollment = None
    submission = None
    certificate = None

    if current_user.is_authenticated:
        enrollment = Enrollment.get_by_user_course(current_user.id, course.id)
        if assignment:
            submission = Submission.get_latest(current_user.id, assignment.id)
        certificate = Certificate.get_by_user_course(current_user.id, course.id)

    return render_template(
        "learning/course_detail.html",
        course=course,
        assignment=assignment,
        enrollment=enrollment,
        submission=submission,
        certificate=certificate
    )


# ==============================================================================
# 3. Free Course Enrolment
# ==============================================================================

@learning_bp.route("/enrol/<course_id>", methods=["POST"])
@login_required
def enrol_course(course_id):
    """
    Free Enrolment Endpoint.
    Guarantees idempotency via unique compound index (user_id, course_id).
    """
    course = Course.get_by_id(course_id)
    if not course:
        flash("Course not found.", "danger")
        return redirect(url_for("learning.courses_list"))

    existing = Enrollment.get_by_user_course(current_user.id, course.id)
    if existing:
        flash(f"You are already enrolled in {course.title}.", "info")
        return redirect(url_for("learning.course_detail", slug=course.slug))

    enrollment = Enrollment({
        "user_id": str(current_user.id),
        "course_id": str(course.id),
        "status": "enrolled",
        "created_at": datetime.now(timezone.utc)
    })
    enrollment.save()

    flash(f"🎉 Enrolment successful! Welcome to '{course.title}'. Watch the course and build your project to earn your certificate.", "success")
    return redirect(url_for("learning.course_detail", slug=course.slug))


@learning_bp.route("/progress/save", methods=["POST"])
@login_required
def save_course_progress():
    """
    Saves student lecture watch progress for resume capability
    and validates the 80% course completion gate for project certification.
    """
    data = request.get_json(silent=True) or {}
    course_id = data.get("course_id")
    if not course_id:
        return jsonify({"success": False, "error": "course_id is required"}), 400

    course = Course.get_by_id(course_id)
    if not course:
        return jsonify({"success": False, "error": "Course not found"}), 404

    enrollment = Enrollment.get_by_user_course(current_user.id, course.id)
    if not enrollment:
        enrollment = Enrollment({
            "user_id": str(current_user.id),
            "course_id": str(course.id),
            "status": "in_progress",
            "created_at": datetime.now(timezone.utc)
        })

    try:
        watch_seconds = int(float(data.get("watch_seconds", 0)))
    except (ValueError, TypeError):
        watch_seconds = 0

    try:
        video_duration = int(float(data.get("video_duration", 0)))
    except (ValueError, TypeError):
        video_duration = 0

    stored_max = int(getattr(enrollment, "max_watch_seconds", 0) or 0)
    # Anti-skip guard: prevent client from jumping arbitrarily ahead to bypass 80% requirement
    if stored_max > 0 and not getattr(enrollment, "video_completed", False):
        if watch_seconds > stored_max + 30:
            # Clamp to allowed incremental playback
            watch_seconds = stored_max + 15

    if watch_seconds > 0:
        enrollment.watch_seconds = watch_seconds
        enrollment.max_watch_seconds = max(stored_max, watch_seconds)

    if video_duration > 0:
        enrollment.video_duration = video_duration

    if enrollment.video_duration > 0:
        pct = min(100, int(round((enrollment.max_watch_seconds / enrollment.video_duration) * 100)))
        enrollment.watch_percent = pct
        if pct >= 80:
            enrollment.video_completed = True

    if enrollment.status == "enrolled":
        enrollment.status = "in_progress"

    enrollment.save()

    return jsonify({
        "success": True,
        "watch_seconds": enrollment.watch_seconds,
        "max_watch_seconds": enrollment.max_watch_seconds,
        "video_duration": enrollment.video_duration,
        "watch_percent": enrollment.watch_percent,
        "video_completed": enrollment.video_completed,
        "formatted_resume_time": enrollment.formatted_resume_time
    })


# ==============================================================================
# 4. Student Hub: My Learning Dashboard
# ==============================================================================

@learning_bp.route("/my-learning")
@login_required
def my_learning():
    """
    Student's Personal Learning Command Center.
    Tracks enrolled courses, active project submissions, review feedback,
    and verified earned certificates.
    """
    try:
        enrollments = Enrollment.find_by_user(current_user.id) or []
        submissions = Submission.find_by_user(current_user.id) or []
        certificates = Certificate.find_by_user(current_user.id) or []

        # Attach courses and assignments to enrollments
        enrolled_items = []
        for enr in enrollments:
            try:
                crs = getattr(enr, "course", None)
                if crs:
                    asg = getattr(crs, "assignment", None)
                    sub = Submission.get_latest(current_user.id, asg.id) if asg else None
                    cert = Certificate.get_by_user_course(current_user.id, crs.id)
                    enrolled_items.append({
                        "enrollment": enr,
                        "course": crs,
                        "assignment": asg,
                        "submission": sub,
                        "certificate": cert
                    })
            except Exception as e_item:
                logger.warning(f"Error parsing enrollment item: {e_item}")

        # Attach certificate to submissions for safe template display
        for sub in submissions:
            try:
                sub.certificate = Certificate.get_by_user_course(current_user.id, getattr(sub, "course_id", None))
            except Exception:
                sub.certificate = None

        # Summary metrics
        total_enrolled = len(enrolled_items)
        total_completed = len([item for item in enrolled_items if getattr(item.get("enrollment"), "status", "") == "completed"])
        pending_submissions = len([s for s in submissions if getattr(s, "status", "") == Submission.STATUS_PENDING])
        total_certificates = len(certificates)

        return render_template(
            "learning/my_learning.html",
            enrolled_items=enrolled_items,
            submissions=submissions,
            certificates=certificates,
            Certificate=Certificate,
            total_enrolled=total_enrolled,
            total_completed=total_completed,
            pending_submissions=pending_submissions,
            total_certificates=total_certificates
        )
    except Exception as e:
        logger.exception(f"Unhandled error in my_learning: {e}")
        flash("Could not load your learning dashboard. Please browse available courses below.", "warning")
        return redirect(url_for("learning.courses_list"))


# ==============================================================================
# 5. Assignment Briefing Page
# ==============================================================================

@learning_bp.route("/assignment/<assignment_id>")
def assignment_detail(assignment_id):
    """
    Dedicated Assignment & Milestone Briefing.
    Displays problem statement, test cases, progressive milestone stepper,
    and requirements based on whether the step is automated or human-reviewed.
    """
    assignment = Assignment.get_by_id(assignment_id)
    if not assignment:
        flash("Milestone assignment not found.", "warning")
        return redirect(url_for("learning.courses_list"))

    course = assignment.course
    enrollment = None
    submission = None
    certificate = None
    all_milestones = []
    user_submissions = {}
    is_unlocked = True

    if course:
        all_milestones = Assignment.get_all_by_course(course.id)

    if current_user.is_authenticated and course:
        enrollment = Enrollment.get_by_user_course(current_user.id, course.id)
        submission = Submission.get_latest(current_user.id, assignment.id)
        certificate = Certificate.get_by_user_course(current_user.id, course.id)
        user_submissions = Submission.get_all_for_course(current_user.id, course.id)

        # Check progressive prerequisite lock
        step_num = getattr(assignment, "step_number", 1)
        if step_num > 1:
            is_unlocked = Submission.is_step_approved(current_user.id, course.id, step_num - 1)

    watch_pct = getattr(enrollment, "watch_percent", 0) if enrollment else 0
    is_lecture_qualified = (watch_pct >= 80) or getattr(current_user, "is_admin", False)

    return render_template(
        "learning/assignment_detail.html",
        assignment=assignment,
        course=course,
        all_milestones=all_milestones,
        user_submissions=user_submissions,
        enrollment=enrollment,
        submission=submission,
        certificate=certificate,
        is_unlocked=is_unlocked,
        is_lecture_qualified=is_lecture_qualified
    )


# ==============================================================================
# 6. Progressive Milestone Submission (Automated & Human Verified)
# ==============================================================================

@learning_bp.route("/submit/<assignment_id>", methods=["GET", "POST"])
@login_required
def submit_project(assignment_id):
    """
    Project & Milestone Submission Portal.
    - Interim Milestones: Evaluated automatically by Algorithmic or Dual-Engine AI evaluator.
    - Final Capstone: Validates GitHub repo + live deployment, strictly reviewed by human.
    """
    assignment = Assignment.get_by_id(assignment_id)
    if not assignment:
        flash("Milestone assignment not found.", "danger")
        return redirect(url_for("learning.courses_list"))

    course = assignment.course
    if not course:
        flash("Associated course not found.", "danger")
        return redirect(url_for("learning.courses_list"))

    # Auto-enrol student if they haven't enrolled yet
    enrollment = Enrollment.get_by_user_course(current_user.id, course.id)
    if not enrollment:
        enrollment = Enrollment({
            "user_id": str(current_user.id),
            "course_id": str(course.id),
            "status": "in_progress",
            "created_at": datetime.now(timezone.utc)
        })
        enrollment.save()

    # Prerequisite verification: cannot submit Milestone N without Milestone N-1 approved
    step_num = getattr(assignment, "step_number", 1)
    if step_num > 1:
        prev_approved = Submission.is_step_approved(current_user.id, course.id, step_num - 1)
        if not prev_approved:
            flash(f"🔒 Prerequisite Required: You must complete and pass Milestone {step_num - 1} before accessing Milestone {step_num}.", "warning")
            prev_asg = Assignment.get_by_course_and_step(course.id, step_num - 1)
            if prev_asg:
                return redirect(url_for("learning.assignment_detail", assignment_id=prev_asg.id))
            return redirect(url_for("learning.course_detail", slug=course.slug))

    existing_sub = Submission.get_latest(current_user.id, assignment.id)

    # If already approved
    if existing_sub and existing_sub.status == Submission.STATUS_APPROVED:
        flash(f"You have already passed Milestone {step_num}! Great job.", "success")
        next_asg = Assignment.get_by_course_and_step(course.id, step_num + 1)
        if next_asg:
            return redirect(url_for("learning.assignment_detail", assignment_id=next_asg.id))
        return redirect(url_for("learning.my_learning"))

    is_project = assignment.is_project_based
    is_capstone = assignment.is_final_capstone

    # For Final Capstone, verify 80% video lecture gate
    if is_capstone:
        watch_pct = getattr(enrollment, "watch_percent", 0)
        video_completed = getattr(enrollment, "video_completed", False) or (watch_pct >= 80)
        if not video_completed and not getattr(current_user, "is_admin", False):
            flash(f"Course Requirement: You must watch at least 80% of the course lecture video before submitting your capstone project for evaluation. Your current watch progress is {watch_pct}%.", "warning")
            return redirect(url_for("learning.course_detail", slug=course.slug))

    if request.method == "POST":
        # =====================================================================
        # PATH A: DEDICATED PROJECT-BASED ASSIGNMENT (GitHub + Live URL Review)
        # =====================================================================
        if is_project:
            title = request.form.get("title", "").strip() or assignment.title
            description = request.form.get("description", "").strip()
            github_url = request.form.get("github_url", "").strip()
            deployment_url = request.form.get("deployment_url", "").strip()
            tech_stack = request.form.get("tech_stack", "").strip()

            errors = []
            if not title:
                errors.append("Please enter a descriptive project title.")
            if not github_url:
                errors.append("Public GitHub repository URL is required.")
            elif not is_valid_github_url(github_url):
                errors.append("Please provide a valid GitHub repository URL (e.g., https://github.com/username/project-repo).")

            # Validate live deployment URL (required for all project-based assignments)
            if not deployment_url:
                errors.append("Live deployment URL (e.g. Render, Vercel, Netlify, GitHub Pages) is required for this project.")
            elif not is_valid_url(deployment_url):
                errors.append("Please provide a valid live deployment URL starting with http:// or https://")

            if not description or len(description) < 30:
                errors.append("Please provide a meaningful description of your project (at least 30 characters) explaining what you built.")

            if errors:
                for err in errors:
                    flash(err, "danger")
                return render_template(
                    "learning/submit_project.html",
                    assignment=assignment,
                    course=course,
                    submission=existing_sub,
                    form_data={
                        "title": title,
                        "description": description,
                        "github_url": github_url,
                        "deployment_url": deployment_url,
                        "tech_stack": tech_stack
                    }
                )

            # Security: enforce student ownership
            if existing_sub and str(existing_sub.user_id) != str(current_user.id):
                abort(403)

            if existing_sub:
                sub = existing_sub
                sub.title = title
                sub.description = description
                sub.github_url = github_url
                sub.deployment_url = deployment_url
                sub.tech_stack = tech_stack
                sub.evaluation_type = assignment.evaluation_type or Assignment.TYPE_PROJECT_BASED
                sub.status = Submission.STATUS_PENDING
                sub.reviewer_id = ""
                sub.review_feedback = ""
                sub.reviewed_at = None
                sub.save()
                flash("🚀 Project resubmission received! Your updated code and live deployment are now Under Review.", "success")
            else:
                sub = Submission({
                    "assignment_id": str(assignment.id),
                    "course_id": str(course.id),
                    "user_id": str(current_user.id),
                    "step_number": step_num,
                    "evaluation_type": assignment.evaluation_type or Assignment.TYPE_PROJECT_BASED,
                    "title": title,
                    "description": description,
                    "github_url": github_url,
                    "deployment_url": deployment_url,
                    "tech_stack": tech_stack,
                    "status": Submission.STATUS_PENDING,
                    "created_at": datetime.now(timezone.utc)
                })
                sub.save()
                flash("🚀 Project submitted successfully! Your submission is now Under Review by our evaluation team.", "success")

            if enrollment.status == "enrolled":
                enrollment.status = "in_progress"
                enrollment.save()

            return redirect(url_for("learning.assignment_detail", assignment_id=assignment.id))

        # =====================================================================
        # PATH B: ALGORITHMIC TEST RUNNER (Automated Python Unit Tests)
        # =====================================================================
        code_snippet = request.form.get("code_snippet", "").strip()
        student_notes = request.form.get("student_notes", "").strip()

        from services.assignment_evaluator import AssignmentEvaluator
        eval_result = AssignmentEvaluator.evaluate(assignment, code_snippet, student_notes)

        # Record or update submission
        if existing_sub:
            sub = existing_sub
            sub.code_snippet = code_snippet
            sub.description = student_notes
            sub.automated_score = eval_result["score"]
            sub.automated_feedback = eval_result["feedback"]
            sub.test_results = eval_result["test_results"]
            sub.status = Submission.STATUS_APPROVED if eval_result["decision"] == "approved" else Submission.STATUS_REJECTED
            sub.reviewed_at = datetime.now(timezone.utc)
            sub.reviewer_id = "automated_engine"
            sub.save()
        else:
            sub = Submission({
                "assignment_id": str(assignment.id),
                "course_id": str(course.id),
                "user_id": str(current_user.id),
                "title": f"Milestone {step_num}: {assignment.title}",
                "code_snippet": code_snippet,
                "description": student_notes,
                "step_number": step_num,
                "evaluation_type": getattr(assignment, "evaluation_type", Assignment.TYPE_ALGORITHMIC),
                "automated_score": eval_result["score"],
                "automated_feedback": eval_result["feedback"],
                "test_results": eval_result["test_results"],
                "status": Submission.STATUS_APPROVED if eval_result["decision"] == "approved" else Submission.STATUS_REJECTED,
                "reviewed_at": datetime.now(timezone.utc),
                "reviewer_id": "automated_engine",
                "created_at": datetime.now(timezone.utc)
            })
            sub.save()

        if eval_result["decision"] == "approved":
            flash(f"🎉 Milestone {step_num} Approved! Automated Score: {eval_result['score']}%. Next step unlocked!", "success")
            next_asg = Assignment.get_by_course_and_step(course.id, step_num + 1)
            if next_asg:
                return redirect(url_for("learning.assignment_detail", assignment_id=next_asg.id))
            return redirect(url_for("learning.course_detail", slug=course.slug))
        else:
            flash(f"⚠️ Milestone {step_num} Needs Revision (Score: {eval_result['score']}%). Review the diagnostic feedback below and try again.", "warning")
            return render_template(
                "learning/submit_project.html",
                assignment=assignment,
                course=course,
                submission=sub,
                eval_result=eval_result,
                form_data={"code_snippet": code_snippet, "student_notes": student_notes}
            )

    # GET request
    form_data = {}
    if existing_sub:
        form_data = {
            "title": existing_sub.title,
            "description": existing_sub.description,
            "github_url": existing_sub.github_url,
            "deployment_url": existing_sub.deployment_url,
            "tech_stack": existing_sub.tech_stack,
            "code_snippet": getattr(existing_sub, "code_snippet", ""),
            "student_notes": existing_sub.description
        }
    elif not is_project and getattr(assignment, "starter_code", ""):
        form_data = {
            "code_snippet": getattr(assignment, "starter_code", "")
        }

    return render_template(
        "learning/submit_project.html",
        assignment=assignment,
        course=course,
        submission=existing_sub,
        form_data=form_data
    )


@learning_bp.route("/api/evaluate-milestone/<assignment_id>", methods=["POST"])
@login_required
def api_evaluate_milestone(assignment_id):
    """
    Instant in-browser algorithmic/AI evaluation for intermediate milestones.
    Returns JSON results immediately with test case breakdown.
    """
    assignment = Assignment.get_by_id(assignment_id)
    if not assignment:
        return jsonify({"status": "error", "message": "Assignment not found"}), 404

    data = request.get_json(silent=True) or request.form
    code_snippet = (data.get("code_snippet") or "").strip()
    student_notes = (data.get("student_notes") or "").strip()

    from services.assignment_evaluator import AssignmentEvaluator
    eval_result = AssignmentEvaluator.evaluate(assignment, code_snippet, student_notes)

    # Save or update submission state
    sub = Submission.get_latest(current_user.id, assignment.id) or Submission({
        "assignment_id": str(assignment.id),
        "course_id": str(assignment.course_id),
        "user_id": str(current_user.id),
        "step_number": getattr(assignment, "step_number", 1),
        "evaluation_type": getattr(assignment, "evaluation_type", "algorithmic"),
        "created_at": datetime.now(timezone.utc)
    })
    sub.title = f"Milestone {getattr(assignment, 'step_number', 1)}: {assignment.title}"
    sub.code_snippet = code_snippet
    sub.description = student_notes
    sub.automated_score = eval_result["score"]
    sub.automated_feedback = eval_result["feedback"]
    sub.test_results = eval_result["test_results"]
    sub.status = Submission.STATUS_APPROVED if eval_result["decision"] == "approved" else Submission.STATUS_REJECTED
    sub.reviewed_at = datetime.now(timezone.utc)
    sub.reviewer_id = "automated_engine"
    sub.save()

    return jsonify({
        "status": "ok",
        "decision": eval_result["decision"],
        "score": eval_result["score"],
        "feedback": eval_result["feedback"],
        "test_results": eval_result["test_results"],
        "evaluator_type": eval_result.get("evaluator_type")
    })


# ==============================================================================
# 7. Official Certificate Presentation View
# ==============================================================================

@learning_bp.route("/certificate/<cert_id>")
@login_required
def view_certificate(cert_id):
    """
    Official Certificate Presentation View.
    Strictly protected: Only the student who earned this certificate or an administrator can access it.
    External visitors and recruiters must use the public verification route: /verify/<cert_id>.
    """
    certificate = Certificate.get_by_cert_id(cert_id)
    if not certificate:
        certificate = Certificate.get_by_id(cert_id)
    if not certificate:
        flash("Certificate record not found.", "warning")
        return redirect(url_for("learning.courses_list"))

    # Security: Verify that the current user is the owner of the certificate or an administrator
    if str(certificate.user_id) != str(current_user.id) and not getattr(current_user, "is_admin", False):
        flash("Access Denied: You are not authorized to view or download another student's certificate.", "danger")
        return redirect(url_for("learning.my_learning"))

    student = certificate.user
    course = certificate.course
    submission = certificate.submission

    return render_template(
        "learning/certificate.html",
        certificate=certificate,
        student=student,
        course=course,
        submission=submission
    )


# ==============================================================================
# 8. Public Certificate Verification Endpoint
# ==============================================================================

@learning_bp.route("/verify/<cert_id>")
def verify_certificate(cert_id):
    """
    Public Certificate Verification Portal.
    Allows recruiters, colleges, and peers to verify authenticity
    without exposing confidential student credentials.
    """
    certificate = Certificate.get_by_cert_id(cert_id)
    if not certificate:
        certificate = Certificate.get_by_id(cert_id)

    is_valid = certificate is not None
    return render_template(
        "verify_certificate.html",
        certificate=certificate,
        is_valid=is_valid,
        cert_id=cert_id
    )
