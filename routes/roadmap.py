"""
SkillRock — Career Roadmap Blueprint
Handles roadmap catalog, syllabus detail, student enrollment, interactive 20-week dashboard,
embedded video lecture player with timestamp offsets, project & capstone submissions,
verified certificate issuance, and the 50% Completion Cashback transparency tracker.
"""

from datetime import datetime, timezone, timedelta
import re
import hashlib
import uuid
import logging

from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    request,
    jsonify,
    abort
)
from flask_login import login_required, current_user

from models.roadmap import (
    RoadmapPackage,
    RoadmapProgress,
    RoadmapSubmission,
    RoadmapCashback
)
from models.mongo import get_db, Certificate
from services.payment_service import (
    verify_student_unlock,
    grant_student_access,
    get_item_by_type_and_id
)

logger = logging.getLogger(__name__)

roadmap_bp = Blueprint("roadmap", __name__, url_prefix="/roadmaps")


def _get_linear_lessons_list(pkg):
    """Returns a flat ordered list of (phase, week, lesson) tuples for navigation."""
    ordered = []
    for p in pkg.phases:
        for w in p.get("weeks", []):
            for l in w.get("lessons", []):
                ordered.append((p, w, l))
    return ordered


@roadmap_bp.route("")
@roadmap_bp.route("/")
def catalog():
    """
    Public Career Roadmaps Catalog.
    Displays all published roadmaps with duration, phases, projects count,
    technologies, career outcomes, and 50% Completion Cashback guarantees.
    """
    packages = RoadmapPackage.get_all(published_only=True)
    
    # Attach enrollment status if user logged in
    enrolled_slugs = set()
    user_progress_map = {}
    if current_user.is_authenticated:
        for p in packages:
            if verify_student_unlock(current_user, "roadmap", str(p.id)):
                enrolled_slugs.add(p.slug)
                prog = RoadmapProgress.get_user_progress(current_user.id, p.slug)
                if prog:
                    user_progress_map[p.slug] = prog.calculate_completion_percentage(p.total_lessons_count)

    return render_template(
        "roadmap/index.html",
        packages=packages,
        enrolled_slugs=enrolled_slugs,
        user_progress_map=user_progress_map,
    )


@roadmap_bp.route("/<slug>")
def detail(slug):
    """
    Roadmap Landing & Syllabus Overview Page.
    Shows the full 5-phase, 20-week learning structure, weekly milestones,
    hands-on projects, capstone preview, and 50% completion cashback conditions.
    """
    pkg = RoadmapPackage.get_by_slug(slug)
    if not pkg or (not pkg.is_published and not getattr(current_user, "is_admin", False)):
        abort(404)

    is_enrolled = False
    progress = None
    completion_pct = 0
    if current_user.is_authenticated:
        is_enrolled = verify_student_unlock(current_user, "roadmap", str(pkg.id))
        if is_enrolled:
            progress = RoadmapProgress.get_user_progress(current_user.id, pkg.slug)
            if progress:
                completion_pct = progress.calculate_completion_percentage(pkg.total_lessons_count)

    return render_template(
        "roadmap/detail.html",
        roadmap=pkg,
        is_enrolled=is_enrolled,
        progress=progress,
        completion_pct=completion_pct,
    )


@roadmap_bp.route("/<slug>/enroll", methods=["POST"])
@login_required
def enroll(slug):
    """
    Enrolls the current student into the roadmap.
    - If free -> grants access and forwards to dashboard.
    - If paid -> redirects to Razorpay checkout.
    - If already unlocked -> forwards to dashboard directly.
    """
    pkg = RoadmapPackage.get_by_slug(slug)
    if not pkg:
        abort(404)

    if verify_student_unlock(current_user, "roadmap", str(pkg.id)):
        flash(f"You already have active access to {pkg.title}!", "info")
        return redirect(url_for("roadmap.dashboard", slug=pkg.slug))

    if not pkg.is_paid or pkg.price <= 0:
        grant_student_access(
            user_id=str(current_user.id),
            item_type="roadmap",
            item_id=str(pkg.id),
            granted_by="system_free",
            amount=0.0
        )
        flash(f"🎉 Enrolled in {pkg.title}! Your learning journey has started.", "success")
        return redirect(url_for("roadmap.dashboard", slug=pkg.slug))

    # Paid roadmap -> Route to unified checkout
    ref_code = request.form.get("srid") or request.args.get("srid") or request.args.get("ref")
    checkout_url = url_for("payment.checkout", item_type="roadmap", item_id=pkg.slug)
    if ref_code:
        checkout_url += f"?srid={ref_code}"
    return redirect(checkout_url)


@roadmap_bp.route("/<slug>/dashboard")
@login_required
def dashboard(slug):
    """
    Interactive Student Roadmap Dashboard.
    Tracks overall 20-week completion %, weekly milestones, next actionable lesson,
    project submission statuses, and cashback countdown.
    """
    pkg = RoadmapPackage.get_by_slug(slug)
    if not pkg:
        abort(404)

    if not verify_student_unlock(current_user, "roadmap", str(pkg.id)):
        flash("Please enroll in this Career Roadmap to access the dashboard and course material.", "warning")
        return redirect(url_for("roadmap.detail", slug=pkg.slug))

    progress = RoadmapProgress.get_user_progress(current_user.id, pkg.slug)
    if not progress:
        # Auto-initialize progress for unlocked student
        progress = RoadmapProgress({
            "user_id": str(current_user.id),
            "roadmap_slug": pkg.slug,
            "cashback_percentage_enrolled": pkg.cashback_percentage,
        })
        progress.save()

    total_lessons = pkg.total_lessons_count
    completed_count = len(progress.completed_lesson_ids)
    completion_pct = progress.calculate_completion_percentage(total_lessons)

    # Find the next incomplete lesson to recommend
    next_lesson = None
    next_week = None
    ordered_lessons = _get_linear_lessons_list(pkg)
    for p, w, l in ordered_lessons:
        if l.get("id") not in progress.completed_lesson_ids:
            next_lesson = l
            next_week = w
            break

    # If all lessons completed, default next_lesson to first lesson
    if not next_lesson and ordered_lessons:
        _, next_week, next_lesson = ordered_lessons[0]

    # Submissions
    submissions = RoadmapSubmission.get_user_submissions(current_user.id, pkg.slug)
    submissions_by_project = {s.project_id: s for s in submissions}
    capstone_submission = submissions_by_project.get(pkg.capstone.get("id")) if pkg.capstone else None
    capstone_approved = capstone_submission is not None and capstone_submission.status == RoadmapSubmission.STATUS_APPROVED

    # Deadline & Cashback metrics
    deadline_date = progress.started_at + timedelta(days=pkg.completion_deadline_days)
    now_utc = datetime.now(timezone.utc)
    if deadline_date.tzinfo is None:
        deadline_date = deadline_date.replace(tzinfo=timezone.utc)
    
    days_left = max(0, (deadline_date - now_utc).days)
    is_deadline_passed = now_utc > deadline_date

    cashback_record = RoadmapCashback.get_by_user_and_roadmap(current_user.id, pkg.slug)

    # Check Certificate status
    certificate = Certificate.get_by_user_course(current_user.id, pkg.slug)

    return render_template(
        "roadmap/dashboard.html",
        roadmap=pkg,
        progress=progress,
        total_lessons=total_lessons,
        completed_count=completed_count,
        completion_pct=completion_pct,
        next_lesson=next_lesson,
        next_week=next_week,
        submissions_by_project=submissions_by_project,
        capstone_submission=capstone_submission,
        capstone_approved=capstone_approved,
        deadline_date=deadline_date,
        days_left=days_left,
        is_deadline_passed=is_deadline_passed,
        cashback_record=cashback_record,
        certificate=certificate,
    )


@roadmap_bp.route("/<slug>/learn/<int:week_num>/<lesson_id>")
@login_required
def learn(slug, week_num, lesson_id):
    """
    Embedded Video Lecture & Learning Workspace.
    Embeds verified YouTube chapters with exact start timestamps,
    learning objectives, structured references, and server-side completion tracking.
    """
    pkg = RoadmapPackage.get_by_slug(slug)
    if not pkg:
        abort(404)

    if not verify_student_unlock(current_user, "roadmap", str(pkg.id)):
        flash("Please enroll to access lectures.", "warning")
        return redirect(url_for("roadmap.detail", slug=pkg.slug))

    lesson, week, phase = pkg.get_lesson_by_id(lesson_id)
    if not lesson or not week:
        abort(404)

    progress = RoadmapProgress.get_user_progress(current_user.id, pkg.slug)
    if not progress:
        progress = RoadmapProgress({"user_id": str(current_user.id), "roadmap_slug": pkg.slug})
        progress.save()

    # Determine linear previous and next lessons
    ordered_lessons = _get_linear_lessons_list(pkg)
    prev_item = None
    next_item = None
    current_idx = -1
    for idx, (p, w, l) in enumerate(ordered_lessons):
        if l.get("id") == str(lesson_id):
            current_idx = idx
            break

    if current_idx > 0:
        prev_item = ordered_lessons[current_idx - 1]
    if current_idx >= 0 and current_idx < len(ordered_lessons) - 1:
        next_item = ordered_lessons[current_idx + 1]

    # Update student's current_week bookmark
    if progress.current_week < week_num:
        progress.current_week = week_num
        progress.save()

    is_completed = progress.is_lesson_completed(lesson_id)
    total_lessons = pkg.total_lessons_count
    completion_pct = progress.calculate_completion_percentage(total_lessons)

    return render_template(
        "roadmap/learn.html",
        roadmap=pkg,
        current_phase=phase,
        current_week=week,
        current_lesson=lesson,
        prev_item=prev_item,
        next_item=next_item,
        progress=progress,
        is_completed=is_completed,
        completion_pct=completion_pct,
    )


@roadmap_bp.route("/<slug>/progress/toggle-lesson", methods=["POST"])
@login_required
def toggle_lesson(slug):
    """
    Server-Side Lesson Completion Toggle.
    Validates user access, toggles lesson in completed_lesson_ids set,
    persists in MongoDB, and returns JSON with new percentage.
    """
    pkg = RoadmapPackage.get_by_slug(slug)
    if not pkg:
        return jsonify({"success": False, "error": "Roadmap not found"}), 404

    if not verify_student_unlock(current_user, "roadmap", str(pkg.id)):
        return jsonify({"success": False, "error": "Access denied"}), 403

    data = request.get_json(silent=True) or request.form
    lesson_id = str(data.get("lesson_id", "")).strip()
    if not lesson_id:
        return jsonify({"success": False, "error": "Lesson ID required"}), 400

    lesson, week, phase = pkg.get_lesson_by_id(lesson_id)
    if not lesson:
        return jsonify({"success": False, "error": "Invalid lesson ID"}), 404

    progress = RoadmapProgress.get_user_progress(current_user.id, pkg.slug)
    if not progress:
        progress = RoadmapProgress({"user_id": str(current_user.id), "roadmap_slug": pkg.slug})

    is_now_completed = progress.toggle_lesson(lesson_id)
    total_lessons = pkg.total_lessons_count
    completion_pct = progress.calculate_completion_percentage(total_lessons)

    if completion_pct >= 100.0 and progress.completion_status != "completed":
        progress.completion_status = "completed"
        progress.completed_at = datetime.now(timezone.utc)
        progress.save()

    return jsonify({
        "success": True,
        "lesson_id": lesson_id,
        "is_completed": is_now_completed,
        "completed_count": len(progress.completed_lesson_ids),
        "total_count": total_lessons,
        "completion_pct": completion_pct,
    })


@roadmap_bp.route("/<slug>/projects")
@login_required
def projects_hub(slug):
    """
    Projects & Capstone Evaluation Hub.
    Displays all 4 phase projects and the final Capstone project with
    submission links, rubric criteria, evaluation statuses, and reviewer notes.
    """
    pkg = RoadmapPackage.get_by_slug(slug)
    if not pkg:
        abort(404)

    if not verify_student_unlock(current_user, "roadmap", str(pkg.id)):
        flash("Please enroll to view project assignments.", "warning")
        return redirect(url_for("roadmap.detail", slug=pkg.slug))

    submissions = RoadmapSubmission.get_user_submissions(current_user.id, pkg.slug)
    submissions_by_project = {s.project_id: s for s in submissions}

    return render_template(
        "roadmap/projects.html",
        roadmap=pkg,
        submissions_by_project=submissions_by_project,
        capstone=pkg.capstone,
    )


@roadmap_bp.route("/<slug>/projects/<project_id>/submit", methods=["POST"])
@login_required
def submit_project(slug, project_id):
    """
    Submits a project repository and live deployment for evaluator review.
    Validates GitHub URL format and Capstone live demo requirements.
    """
    pkg = RoadmapPackage.get_by_slug(slug)
    if not pkg:
        abort(404)

    if not verify_student_unlock(current_user, "roadmap", str(pkg.id)):
        abort(403)

    proj, is_capstone = pkg.get_project_by_id(project_id)
    if not proj:
        flash("Invalid project assignment selected.", "danger")
        return redirect(url_for("roadmap.projects_hub", slug=pkg.slug))

    github_url = request.form.get("github_url", "").strip()
    deployment_url = request.form.get("deployment_url", "").strip()
    notes = request.form.get("notes", "").strip()

    # URL Validation
    if not github_url or "github.com" not in github_url.lower():
        flash("Please provide a valid GitHub repository URL (e.g., https://github.com/username/repo).", "danger")
        return redirect(url_for("roadmap.projects_hub", slug=pkg.slug))

    if is_capstone and not deployment_url:
        flash("The Final Capstone project requires a live cloud deployment link (Vercel, Render, Netlify, etc.).", "danger")
        return redirect(url_for("roadmap.projects_hub", slug=pkg.slug))

    existing = RoadmapSubmission.get_by_user_and_project(current_user.id, pkg.slug, project_id)
    sub = existing or RoadmapSubmission({
        "user_id": str(current_user.id),
        "user_name": getattr(current_user, "name", "Student"),
        "user_email": getattr(current_user, "email", ""),
        "roadmap_slug": pkg.slug,
        "project_id": str(project_id),
        "project_title": proj.get("title", "Project"),
        "is_capstone": is_capstone,
    })

    sub.github_url = github_url
    sub.deployment_url = deployment_url
    sub.notes = notes
    sub.status = RoadmapSubmission.STATUS_PENDING
    sub.submitted_at = datetime.now(timezone.utc)
    sub.admin_feedback = ""
    sub.save()

    flash(f"🎉 '{proj.get('title')}' submitted successfully! Our evaluation team will review your code against rubrics.", "success")
    return redirect(url_for("roadmap.projects_hub", slug=pkg.slug))


@roadmap_bp.route("/<slug>/cashback")
@login_required
def cashback_tracker(slug):
    """
    50% Completion Cashback Tracker & Eligibility Portal.
    Clearly breaks down the 4 mandatory criteria:
    1. 100% of 20-week lessons marked complete.
    2. All 4 phase projects submitted.
    3. Final Capstone project approved by SkillRock evaluators.
    4. Completed within the completion deadline window.
    """
    pkg = RoadmapPackage.get_by_slug(slug)
    if not pkg:
        abort(404)

    if not verify_student_unlock(current_user, "roadmap", str(pkg.id)):
        flash("Please enroll to view the cashback tracker.", "warning")
        return redirect(url_for("roadmap.detail", slug=pkg.slug))

    progress = RoadmapProgress.get_user_progress(current_user.id, pkg.slug)
    if not progress:
        progress = RoadmapProgress({"user_id": str(current_user.id), "roadmap_slug": pkg.slug})
        progress.save()

    total_lessons = pkg.total_lessons_count
    completed_lessons = len(progress.completed_lesson_ids)
    completion_pct = progress.calculate_completion_percentage(total_lessons)

    # Phase projects check
    submissions = RoadmapSubmission.get_user_submissions(current_user.id, pkg.slug)
    submissions_by_project = {s.project_id: s for s in submissions}
    
    phase_projects_submitted = all(
        p.get("id") in submissions_by_project for p in pkg.projects
    )

    capstone_sub = submissions_by_project.get(pkg.capstone.get("id")) if pkg.capstone else None
    capstone_approved = capstone_sub is not None and capstone_sub.status == RoadmapSubmission.STATUS_APPROVED

    # Deadline check
    deadline_date = progress.started_at + timedelta(days=pkg.completion_deadline_days)
    now_utc = datetime.now(timezone.utc)
    if deadline_date.tzinfo is None:
        deadline_date = deadline_date.replace(tzinfo=timezone.utc)
    is_within_deadline = now_utc <= deadline_date
    days_left = max(0, (deadline_date - now_utc).days)

    # Paid check
    is_paid_student = progress.amount_paid > 0
    cashback_amount = round(progress.amount_paid * (pkg.cashback_percentage / 100.0), 2)

    is_eligible = (
        pkg.cashback_enabled
        and is_paid_student
        and completion_pct >= 100.0
        and phase_projects_submitted
        and capstone_approved
        and is_within_deadline
    )

    cashback_record = RoadmapCashback.get_by_user_and_roadmap(current_user.id, pkg.slug)

    return render_template(
        "roadmap/cashback.html",
        roadmap=pkg,
        progress=progress,
        completion_pct=completion_pct,
        completed_lessons=completed_lessons,
        total_lessons=total_lessons,
        phase_projects_submitted=phase_projects_submitted,
        capstone_approved=capstone_approved,
        capstone_sub=capstone_sub,
        deadline_date=deadline_date,
        is_within_deadline=is_within_deadline,
        days_left=days_left,
        is_paid_student=is_paid_student,
        cashback_amount=cashback_amount,
        is_eligible=is_eligible,
        cashback_record=cashback_record,
    )


@roadmap_bp.route("/<slug>/cashback/request", methods=["POST"])
@login_required
def request_cashback(slug):
    """
    Claims 50% Completion Cashback.
    Enforces strict server-side validation against all 4 completion criteria:
    - 100% lessons
    - Phase projects submitted
    - Capstone approved
    - Within deadline
    - Anti-duplicate idempotency
    """
    pkg = RoadmapPackage.get_by_slug(slug)
    if not pkg:
        abort(404)

    if not verify_student_unlock(current_user, "roadmap", str(pkg.id)):
        abort(403)

    if not pkg.cashback_enabled:
        flash("Cashback is not enabled for this program.", "danger")
        return redirect(url_for("roadmap.cashback_tracker", slug=pkg.slug))

    progress = RoadmapProgress.get_user_progress(current_user.id, pkg.slug)
    if not progress or progress.amount_paid <= 0:
        flash("Cashback is only applicable to paid enrollments.", "danger")
        return redirect(url_for("roadmap.cashback_tracker", slug=pkg.slug))

    # Existing request check
    existing = RoadmapCashback.get_by_user_and_roadmap(current_user.id, pkg.slug)
    if existing and existing.review_status in (
        RoadmapCashback.STATUS_PENDING_REVIEW,
        RoadmapCashback.STATUS_APPROVED,
        RoadmapCashback.STATUS_PROCESSED
    ):
        flash("You have already submitted a cashback request for this roadmap. Our team is processing it.", "info")
        return redirect(url_for("roadmap.cashback_tracker", slug=pkg.slug))

    # Check 1: 100% lessons
    if progress.calculate_completion_percentage(pkg.total_lessons_count) < 100.0:
        flash("You must complete 100% of all 20-week lessons to qualify for cashback.", "danger")
        return redirect(url_for("roadmap.cashback_tracker", slug=pkg.slug))

    # Check 2: All phase projects submitted
    submissions = RoadmapSubmission.get_user_submissions(current_user.id, pkg.slug)
    submissions_by_project = {s.project_id: s for s in submissions}
    if not all(p.get("id") in submissions_by_project for p in pkg.projects):
        flash("You must submit all phase projects before claiming cashback.", "danger")
        return redirect(url_for("roadmap.cashback_tracker", slug=pkg.slug))

    # Check 3: Capstone approved
    capstone_sub = submissions_by_project.get(pkg.capstone.get("id")) if pkg.capstone else None
    if not capstone_sub or capstone_sub.status != RoadmapSubmission.STATUS_APPROVED:
        flash("Your Final Capstone project must be evaluated and approved by SkillRock evaluators to qualify for cashback.", "danger")
        return redirect(url_for("roadmap.cashback_tracker", slug=pkg.slug))

    # Check 4: Deadline check
    deadline_date = progress.started_at + timedelta(days=pkg.completion_deadline_days)
    now_utc = datetime.now(timezone.utc)
    if deadline_date.tzinfo is None:
        deadline_date = deadline_date.replace(tzinfo=timezone.utc)
    if now_utc > deadline_date:
        flash("The completion deadline window for cashback has passed.", "danger")
        return redirect(url_for("roadmap.cashback_tracker", slug=pkg.slug))

    cashback_amount = round(progress.amount_paid * (pkg.cashback_percentage / 100.0), 2)
    req = existing or RoadmapCashback({
        "user_id": str(current_user.id),
        "user_name": getattr(current_user, "name", "Student"),
        "user_email": getattr(current_user, "email", ""),
        "roadmap_slug": pkg.slug,
        "roadmap_title": pkg.title,
        "original_payment_id": progress.payment_id,
        "original_amount": progress.amount_paid,
        "cashback_percentage": pkg.cashback_percentage,
        "cashback_amount": cashback_amount,
    })

    req.eligibility_status = RoadmapCashback.STATUS_ELIGIBLE
    req.review_status = RoadmapCashback.STATUS_PENDING_REVIEW
    req.refund_status = "none"
    req.requested_at = now_utc
    req.add_audit_entry(
        action="cashback_requested",
        by=f"student:{current_user.id}",
        note=f"Requested ₹{cashback_amount} (50% of ₹{progress.amount_paid}) after fulfilling all 4 criteria."
    )
    req.save()

    flash(f"🎉 50% Completion Cashback Claim (₹{cashback_amount}) submitted successfully! Our financial team will review and process your refund.", "success")
    return redirect(url_for("roadmap.cashback_tracker", slug=pkg.slug))


@roadmap_bp.route("/<slug>/certificate")
@login_required
def certificate_view(slug):
    """
    Verified Certificate of Completion for Career Roadmap.
    Requires 100% lessons completed and an approved Capstone project.
    Generates a cryptographically verified credential with legal name locking.
    """
    pkg = RoadmapPackage.get_by_slug(slug)
    if not pkg:
        abort(404)

    if not verify_student_unlock(current_user, "roadmap", str(pkg.id)):
        flash("Access denied.", "danger")
        return redirect(url_for("roadmap.detail", slug=pkg.slug))

    progress = RoadmapProgress.get_user_progress(current_user.id, pkg.slug)
    submissions = RoadmapSubmission.get_user_submissions(current_user.id, pkg.slug)
    submissions_by_project = {s.project_id: s for s in submissions}
    capstone_sub = submissions_by_project.get(pkg.capstone.get("id")) if pkg.capstone else None
    capstone_approved = capstone_sub is not None and capstone_sub.status == RoadmapSubmission.STATUS_APPROVED

    is_complete = progress and progress.calculate_completion_percentage(pkg.total_lessons_count) >= 100.0 and capstone_approved

    if not is_complete:
        flash("To earn your verified Certificate of Completion, complete all 20 weeks of lectures and have your Capstone project approved.", "warning")
        return redirect(url_for("roadmap.dashboard", slug=pkg.slug))

    # Issue or retrieve certificate
    cert = Certificate.get_by_user_course(current_user.id, pkg.slug)
    if not cert:
        cert_id = Certificate.generate_cert_id()
        now = datetime.now(timezone.utc)
        clean_name = getattr(current_user, "name", "SkillRock Graduate")
        raw_hash = f"{cert_id}:{current_user.id}:{pkg.slug}:{clean_name}:{now.isoformat()}"
        verification_hash = hashlib.sha256(raw_hash.encode("utf-8")).hexdigest()[:24]

        cert = Certificate({
            "certificate_id": cert_id,
            "user_id": str(current_user.id),
            "user_name": clean_name,
            "user_email": getattr(current_user, "email", ""),
            "course_id": pkg.slug,
            "course_title": f"{pkg.title} — Career Roadmap",
            "submission_id": str(capstone_sub.id) if capstone_sub else "",
            "issued_at": now,
            "verification_hash": verification_hash,
            "name_locked": False,
        })
        cert.save()
        logger.info(f"[ROADMAP CERTIFICATE ISSUED] Certificate {cert_id} for user {current_user.id} ({pkg.slug})")

    verification_url = url_for("learning.verify_certificate", cert_id=cert.certificate_id, _external=True)

    return render_template(
        "roadmap/certificate.html",
        roadmap=pkg,
        certificate=cert,
        verification_url=verification_url,
    )
