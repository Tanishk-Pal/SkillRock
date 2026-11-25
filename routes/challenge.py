"""
Monthly Challenge Blueprint for SkillRock.
Provides public catalog, detailed landing experience, 28-day student command center (9 tabs),
interactive practice, interview prep, LeetCode-style coding sandbox, 50-MCQ assessment,
certificate issuance, and 100% refund claim management.
"""

from datetime import datetime, timezone
import json
import logging
import random
import re
import secrets
from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required

from models.challenge import (
    AssessmentAttempt,
    AssessmentQuestion,
    ChallengeAssignmentSubmission,
    ChallengeEnrollment,
    CodingProblem,
    InterviewQuestion,
    MonthlyChallenge,
    PracticalAssignment,
    PracticeQuestion,
    RefundClaim,
)
from models.default_challenge_data import ensure_default_monthly_challenge
from services.code_execution_service import evaluate_test_cases, execute_python_code
from services.payment_service import get_db, verify_student_unlock

logger = logging.getLogger(__name__)

challenge_bp = Blueprint("challenge", __name__)


def _get_challenge_or_404(slug_or_id: str) -> MonthlyChallenge:
    """Retrieves MonthlyChallenge by slug or ID, auto-seeding default if empty."""
    ch = MonthlyChallenge.get_by_slug(slug_or_id) or MonthlyChallenge.get_by_id(slug_or_id)
    if not ch:
        # Attempt to seed default challenge if none exists
        ensure_default_monthly_challenge()
        ch = MonthlyChallenge.get_by_slug(slug_or_id) or MonthlyChallenge.get_by_id(slug_or_id)
    if not ch:
        abort(404)
    return ch


# ==============================================================================
# 1. Public Catalog & Detail Pages
# ==============================================================================

@challenge_bp.route("/challenges")
@challenge_bp.route("/challenge")
def catalog():
    """
    SkillRock Monthly Challenge Catalog.
    Displays available monthly challenges using SkillRock's signature course-card visual language.
    """
    ensure_default_monthly_challenge()
    challenges = MonthlyChallenge.get_all_active()

    user_enrollments = {}
    if current_user.is_authenticated:
        enrs = ChallengeEnrollment.get_user_all(str(current_user.id))
        for e in enrs:
            user_enrollments[e.challenge_slug] = e

    return render_template(
        "challenge/index.html",
        challenges=challenges,
        user_enrollments=user_enrollments,
    )


@challenge_bp.route("/challenge/<slug>")
def detail(slug):
    """
    Comprehensive Monthly Challenge landing experience.
    Features: Hero (₹499 CTA, 28-day countdown, outcomes, refund guarantee),
    'What You Will Get' 8-card grid, 6-module curriculum outline, and refund criteria terms.
    """
    challenge = _get_challenge_or_404(slug)

    is_enrolled = False
    enrollment = None
    if current_user.is_authenticated:
        enrollment = ChallengeEnrollment.get_user_enrollment(str(current_user.id), challenge.slug)
        if enrollment:
            is_enrolled = True
        elif verify_student_unlock(current_user, "challenge", str(challenge.id)):
            # If unlocked via payment but enrollment doc not yet saved
            enrollment = ChallengeEnrollment.get_or_create(
                user_id=str(current_user.id),
                challenge_id=str(challenge.id),
                challenge_slug=challenge.slug,
                amount_paid=float(challenge.price or 499.0)
            )
            is_enrolled = True

    return render_template(
        "challenge/detail.html",
        challenge=challenge,
        is_enrolled=is_enrolled,
        enrollment=enrollment,
    )


# ==============================================================================
# 2. Student 28-Day Command Center Dashboard (9 Tabs)
# ==============================================================================

@challenge_bp.route("/challenge/<slug>/dashboard")
@login_required
def dashboard(slug):
    """
    The 28-Day Student Command Center for enrolled learners.
    Hosts 9 distinct tabs:
    1. Overview (Countdown & milestone tracker)
    2. Learn (6 YouTube modules with completion checkboxes)
    3. Practice Arena (MCQs with explanations & scoring)
    4. Interview Preparation (placement questions with status filters)
    5. Coding Arena (LeetCode split-screen runner)
    6. Practical Assignment (Problem statement & submission portal)
    7. Final Assessment (50 MCQs, 2 attempts, >=80% pass threshold)
    8. SkillRock Certificate (preview, verify ID, download)
    9. 100% Refund (automated criteria validator, UPI claim form, status tracker)
    """
    challenge = _get_challenge_or_404(slug)
    user_id = str(current_user.id)

    enrollment = ChallengeEnrollment.get_user_enrollment(user_id, challenge.slug)
    if not enrollment:
        # Check if user has active payment unlock or is admin
        if verify_student_unlock(current_user, "challenge", str(challenge.id)) or current_user.is_admin:
            enrollment = ChallengeEnrollment.get_or_create(
                user_id=user_id,
                challenge_id=str(challenge.id),
                challenge_slug=challenge.slug,
                amount_paid=float(challenge.price or 499.0)
            )
        else:
            flash("You must be enrolled to access the Monthly Challenge Dashboard.", "warning")
            return redirect(url_for("challenge.detail", slug=challenge.slug))

    # Load interactive content collections
    practice_questions = PracticeQuestion.get_by_challenge(challenge.slug)
    interview_questions = InterviewQuestion.get_by_challenge(challenge.slug)
    coding_problems = CodingProblem.get_by_challenge(challenge.slug)
    assignment = PracticalAssignment.get_by_challenge(challenge.slug)
    assignment_submission = ChallengeAssignmentSubmission.get_user_submission(user_id, challenge.slug)
    assessment_attempts = AssessmentAttempt.get_user_attempts(user_id, challenge.slug)
    refund_claim = RefundClaim.get_by_user_challenge(user_id, challenge.slug)

    # 28-day countdown and progress calculations
    metrics = enrollment.get_countdown_metrics(challenge.duration_days)
    progress_stats = enrollment.calculate_progress(
        total_modules=len(challenge.modules),
        total_practice=len(practice_questions),
        total_interviews=len(interview_questions),
        total_coding=len(coding_problems),
        has_assignment_submitted=bool(assignment_submission and assignment_submission.status in ("submitted", "approved")),
        assessment_passed=enrollment.assessment_passed,
    )

    # Automated 7-condition refund eligibility check
    refund_check = enrollment.evaluate_refund_eligibility(
        total_modules=len(challenge.modules),
        total_practice=len(practice_questions),
        total_interviews=len(interview_questions),
        total_coding=len(coding_problems),
        assignment_submission_status=assignment_submission.status if assignment_submission else None,
        duration_days=challenge.duration_days,
    )

    active_tab = request.args.get("tab", "overview")

    return render_template(
        "challenge/dashboard.html",
        challenge=challenge,
        enrollment=enrollment,
        metrics=metrics,
        progress_stats=progress_stats,
        refund_check=refund_check,
        practice_questions=practice_questions,
        interview_questions=interview_questions,
        coding_problems=coding_problems,
        assignment=assignment,
        assignment_submission=assignment_submission,
        assessment_attempts=assessment_attempts,
        refund_claim=refund_claim,
        active_tab=active_tab,
    )


# ==============================================================================
# 3. Interactive APIs for Dashboard Tabs
# ==============================================================================

@challenge_bp.route("/challenge/<slug>/module/toggle", methods=["POST"])
@login_required
def toggle_module(slug):
    """Marks a module as completed or in-progress."""
    challenge = _get_challenge_or_404(slug)
    enrollment = ChallengeEnrollment.get_user_enrollment(str(current_user.id), challenge.slug)
    if not enrollment:
        return jsonify({"success": False, "error": "Not enrolled"}), 403

    data = request.get_json(silent=True) or {}
    module_id = int(data.get("module_id", 0))
    completed = bool(data.get("completed", True))

    current_completed = set(enrollment.modules_completed)
    if completed:
        current_completed.add(module_id)
    else:
        current_completed.discard(module_id)

    enrollment.modules_completed = sorted(list(current_completed))
    enrollment.save()

    return jsonify({
        "success": True,
        "modules_completed": enrollment.modules_completed,
        "completed_count": len(enrollment.modules_completed),
        "total_modules": len(challenge.modules),
    })


@challenge_bp.route("/challenge/<slug>/practice/submit", methods=["POST"])
@login_required
def submit_practice(slug):
    """Evaluates an MCQ in the Practice Arena and returns instant explanation."""
    challenge = _get_challenge_or_404(slug)
    enrollment = ChallengeEnrollment.get_user_enrollment(str(current_user.id), challenge.slug)
    if not enrollment:
        return jsonify({"success": False, "error": "Not enrolled"}), 403

    data = request.get_json(silent=True) or {}
    question_id = str(data.get("question_id", ""))
    selected_option = int(data.get("selected_option", -1))

    q = PracticeQuestion.get_by_id(question_id)
    if not q or q.challenge_slug != challenge.slug:
        return jsonify({"success": False, "error": "Question not found"}), 404

    is_correct = (selected_option == q.correct_option)

    # Update enrollment scores and attempt history
    enrollment.practice_scores[str(q.order_index)] = {
        "selected": selected_option,
        "is_correct": is_correct,
        "submitted_at": datetime.now(timezone.utc).isoformat(),
    }
    enrollment.save()

    return jsonify({
        "success": True,
        "is_correct": is_correct,
        "correct_option": q.correct_option,
        "explanation": q.explanation,
    })


@challenge_bp.route("/challenge/<slug>/interview/status", methods=["POST"])
@login_required
def update_interview_status(slug):
    """Updates interview preparation question status: not_started, practising, completed."""
    challenge = _get_challenge_or_404(slug)
    enrollment = ChallengeEnrollment.get_user_enrollment(str(current_user.id), challenge.slug)
    if not enrollment:
        return jsonify({"success": False, "error": "Not enrolled"}), 403

    data = request.get_json(silent=True) or {}
    question_id = str(data.get("question_id", ""))
    status = str(data.get("status", "completed")).lower()
    if status not in ("not_started", "practising", "completed"):
        status = "completed"

    q = InterviewQuestion.get_by_id(question_id)
    if not q or q.challenge_slug != challenge.slug:
        return jsonify({"success": False, "error": "Question not found"}), 404

    enrollment.interview_prep_status[str(q.order_index)] = status
    enrollment.save()

    return jsonify({
        "success": True,
        "question_id": question_id,
        "status": status,
    })


@challenge_bp.route("/challenge/<slug>/coding/run", methods=["POST"])
@login_required
def run_coding_code(slug):
    """Runs code in the Coding Arena against sample test cases or custom input."""
    challenge = _get_challenge_or_404(slug)
    enrollment = ChallengeEnrollment.get_user_enrollment(str(current_user.id), challenge.slug)
    if not enrollment:
        return jsonify({"success": False, "error": "Not enrolled"}), 403

    data = request.get_json(silent=True) or {}
    problem_id = str(data.get("problem_id", ""))
    code = str(data.get("code", "")).strip()
    custom_input = data.get("custom_input", None)

    prob = CodingProblem.get_by_id(problem_id)
    if not prob or prob.challenge_slug != challenge.slug:
        return jsonify({"success": False, "error": "Coding problem not found"}), 404

    if not code:
        return jsonify({"success": False, "error": "Code cannot be empty"}), 400

    # Custom input single run
    if custom_input is not None:
        exec_res = execute_python_code(code, stdin_input=str(custom_input))
        return jsonify({
            "success": True,
            "custom_run": True,
            "stdout": exec_res["stdout"],
            "stderr": exec_res["stderr"],
            "execution_time_ms": exec_res["execution_time_ms"],
            "passed": exec_res["success"],
        })

    # Run only sample visible test cases
    sample_cases = [tc for tc in prob.test_cases if not tc.get("is_hidden", False)]
    eval_res = evaluate_test_cases(code, sample_cases, language=prob.language)
    return jsonify(eval_res)


@challenge_bp.route("/challenge/<slug>/coding/submit", methods=["POST"])
@login_required
def submit_coding_problem(slug):
    """Evaluates code against ALL test cases (sample and hidden) and saves problem solve status."""
    challenge = _get_challenge_or_404(slug)
    enrollment = ChallengeEnrollment.get_user_enrollment(str(current_user.id), challenge.slug)
    if not enrollment:
        return jsonify({"success": False, "error": "Not enrolled"}), 403

    data = request.get_json(silent=True) or {}
    problem_id = str(data.get("problem_id", ""))
    code = str(data.get("code", "")).strip()

    prob = CodingProblem.get_by_id(problem_id)
    if not prob or prob.challenge_slug != challenge.slug:
        return jsonify({"success": False, "error": "Coding problem not found"}), 404

    if not code:
        return jsonify({"success": False, "error": "Code cannot be empty"}), 400

    eval_res = evaluate_test_cases(code, prob.test_cases, language=prob.language)

    if eval_res.get("all_passed"):
        if prob.slug not in enrollment.coding_problems_solved:
            enrollment.coding_problems_solved.append(prob.slug)
            enrollment.save()

    return jsonify({
        "success": True,
        "all_passed": eval_res.get("all_passed", False),
        "passed_count": eval_res.get("passed_count", 0),
        "total_count": eval_res.get("total_count", 0),
        "results": eval_res.get("results", []),
        "error": eval_res.get("error"),
        "solved_problems": enrollment.coding_problems_solved,
    })


@challenge_bp.route("/challenge/<slug>/assignment/submit", methods=["POST"])
@login_required
def submit_assignment(slug):
    """Submits practical project assignment for mentor/admin rubric review."""
    challenge = _get_challenge_or_404(slug)
    enrollment = ChallengeEnrollment.get_user_enrollment(str(current_user.id), challenge.slug)
    if not enrollment:
        flash("You must be enrolled to submit the practical assignment.", "danger")
        return redirect(url_for("challenge.detail", slug=challenge.slug))

    github_url = request.form.get("github_repo_url", "").strip()
    live_url = request.form.get("live_demo_url", "").strip()
    notes = request.form.get("submission_notes", "").strip()

    if not github_url and not live_url:
        flash("Please provide at least a GitHub repository or live deployment URL.", "warning")
        return redirect(url_for("challenge.dashboard", slug=challenge.slug, tab="assignment"))

    assignment = PracticalAssignment.get_by_challenge(challenge.slug)

    submission = ChallengeAssignmentSubmission({
        "user_id": str(current_user.id),
        "challenge_slug": challenge.slug,
        "assignment_id": str(assignment.id) if assignment else "",
        "github_repo_url": github_url,
        "live_demo_url": live_url,
        "submission_notes": notes,
        "status": "submitted",
        "submitted_at": datetime.now(timezone.utc),
    })
    submission.save()

    enrollment.assignment_status = "submitted"
    enrollment.save()

    flash("Practical assignment submitted successfully! Your submission is queued for rubric review.", "success")
    return redirect(url_for("challenge.dashboard", slug=challenge.slug, tab="assignment"))


@challenge_bp.route("/challenge/<slug>/assessment/start", methods=["POST"])
@login_required
def start_assessment(slug):
    """
    Initializes a timed 50-MCQ Final Assessment attempt.
    Enforces maximum of 2 attempts. Returns questions with sanitized choices (no correct answers).
    """
    challenge = _get_challenge_or_404(slug)
    enrollment = ChallengeEnrollment.get_user_enrollment(str(current_user.id), challenge.slug)
    if not enrollment:
        return jsonify({"success": False, "error": "Not enrolled"}), 403

    attempts = AssessmentAttempt.get_user_attempts(str(current_user.id), challenge.slug)
    if len(attempts) >= 2:
        return jsonify({
            "success": False,
            "error": "You have exhausted your maximum limit of 2 attempts for this assessment."
        }), 400

    # Fetch assessment questions and randomize
    all_questions = AssessmentQuestion.get_by_challenge(challenge.slug)
    if not all_questions or len(all_questions) < 10:
        return jsonify({
            "success": False,
            "error": "The 50-question assessment question bank is currently being prepared."
        }), 503

    # Shuffle question order deterministically or randomly for this attempt
    shuffled_questions = list(all_questions)
    random.shuffle(shuffled_questions)
    # Take up to 50 questions
    assessment_set = shuffled_questions[:50]

    attempt = AssessmentAttempt({
        "user_id": str(current_user.id),
        "challenge_slug": challenge.slug,
        "attempt_number": len(attempts) + 1,
        "total_questions": len(assessment_set),
        "started_at": datetime.now(timezone.utc),
        "question_ids": [str(q.id) for q in assessment_set],
    })
    attempt.save()

    # Sanitize questions for student client (exclude correct_option)
    client_questions = []
    for idx, q in enumerate(assessment_set):
        client_questions.append({
            "id": str(q.id),
            "order_index": idx + 1,
            "question_text": q.question_text,
            "options": q.options,
            "topic": q.topic,
        })

    return jsonify({
        "success": True,
        "attempt_id": str(attempt.id),
        "attempt_number": attempt.attempt_number,
        "total_questions": len(client_questions),
        "time_limit_minutes": 60,
        "questions": client_questions,
    })


@challenge_bp.route("/challenge/<slug>/assessment/submit", methods=["POST"])
@login_required
def submit_assessment(slug):
    """
    Evaluates student answers for the 50 MCQs.
    Pass threshold: >= 80% (40 out of 50 correct).
    Automatically issues verified Certificate ID upon passing!
    """
    challenge = _get_challenge_or_404(slug)
    enrollment = ChallengeEnrollment.get_user_enrollment(str(current_user.id), challenge.slug)
    if not enrollment:
        return jsonify({"success": False, "error": "Not enrolled"}), 403

    data = request.get_json(silent=True) or {}
    attempt_id = str(data.get("attempt_id", ""))
    student_answers = data.get("answers", {})  # { "question_id": selected_option_int }

    attempt = AssessmentAttempt.get_by_id(attempt_id)
    if not attempt or attempt.user_id != str(current_user.id):
        return jsonify({"success": False, "error": "Invalid assessment attempt"}), 404

    if attempt.completed_at:
        return jsonify({"success": False, "error": "Attempt has already been submitted"}), 400

    # Grade strictly against database questions
    score = 0
    total_q = len(attempt.question_ids) or 50
    db = get_db()
    for q_id_str in attempt.question_ids:
        q = AssessmentQuestion.get_by_id(q_id_str)
        if q:
            student_choice = student_answers.get(q_id_str)
            if student_choice is not None and int(student_choice) == q.correct_option:
                score += 1

    percentage = round((score / max(total_q, 1)) * 100, 1)
    passed = (percentage >= 80.0)

    attempt.score = score
    attempt.total_questions = total_q
    attempt.percentage = percentage
    attempt.passed = passed
    attempt.student_answers = {k: int(v) for k, v in student_answers.items() if v is not None}
    attempt.completed_at = datetime.now(timezone.utc)
    attempt.save()

    # Update enrollment status
    if passed:
        enrollment.assessment_passed = True
        enrollment.assessment_score = score
        # Generate Certificate ID if not present
        if not enrollment.certificate_id:
            cert_random = secrets.token_hex(3).upper()
            enrollment.certificate_id = f"SR-MCH-{datetime.now(timezone.utc).strftime('%Y%m')}-{cert_random}"
            enrollment.certificate_issued_at = datetime.now(timezone.utc)
        enrollment.save()

        # Persist corresponding Certificate in db.certificates primary ledger
        try:
            from models.mongo import Certificate
            existing_cert = Certificate.get_by_cert_id(enrollment.certificate_id)
            if not existing_cert:
                cert_record = Certificate.build_challenge_certificate(
                    enrollment,
                    challenge=challenge,
                    user=current_user,
                )
                if cert_record:
                    cert_record.save()
        except Exception as e:
            logger.error(f"Error persisting challenge certificate ledger record: {e}")
    else:
        # Check if user passed previously
        past_attempts = AssessmentAttempt.get_user_attempts(str(current_user.id), challenge.slug)
        if any(a.passed for a in past_attempts):
            enrollment.assessment_passed = True
            enrollment.save()

    return jsonify({
        "success": True,
        "score": score,
        "total_questions": total_q,
        "percentage": percentage,
        "passed": passed,
        "certificate_id": enrollment.certificate_id if passed else None,
        "pass_threshold_percentage": 80.0,
    })


# ==============================================================================
# 4. Verified Certificate
# ==============================================================================

@challenge_bp.route("/challenge/<slug>/certificate")
@login_required
def view_certificate(slug):
    """Displays the official SkillRock Certificate of Completion with verification ID."""
    challenge = _get_challenge_or_404(slug)
    enrollment = ChallengeEnrollment.get_user_enrollment(str(current_user.id), challenge.slug)
    if not enrollment or not enrollment.certificate_id:
        flash("Certificate is only issued after completing all challenge requirements and passing the assessment.", "warning")
        return redirect(url_for("challenge.dashboard", slug=challenge.slug, tab="certificate"))

    site_url = current_app.config.get("SITE_URL", "https://skillrock.in").rstrip("/")
    if request.host.startswith("localhost") or request.host.startswith("127.0.0.1"):
        verification_url = url_for("learning.verify_certificate", cert_id=enrollment.certificate_id, _external=True)
    else:
        verification_url = f"{site_url}/verify/{enrollment.certificate_id}"

    return render_template(
        "challenge/certificate.html",
        challenge=challenge,
        enrollment=enrollment,
        user=current_user,
        verification_url=verification_url,
    )


# ==============================================================================
# 5. 100% Refund Claim Management
# ==============================================================================

@challenge_bp.route("/challenge/<slug>/refund/claim", methods=["POST"])
@login_required
def submit_refund_claim(slug):
    """
    Submits a 100% Refund Claim.
    Enforces strict server-side evaluation of all 7 published conditions.
    Never accepts claims unless all 7 conditions are genuinely fulfilled.
    Dispatches notification to skillrockk@gmail.com and admin console.
    """
    challenge = _get_challenge_or_404(slug)
    user_id = str(current_user.id)
    enrollment = ChallengeEnrollment.get_user_enrollment(user_id, challenge.slug)
    if not enrollment:
        return jsonify({"success": False, "error": "Not enrolled"}), 403

    # Check for existing claim
    existing_claim = RefundClaim.get_by_user_challenge(user_id, challenge.slug)
    if existing_claim and existing_claim.status in ("pending", "approved"):
        return jsonify({
            "success": False,
            "error": f"You already have an active refund claim in status '{existing_claim.status.upper()}'."
        }), 400

    # Fetch context to evaluate the 7 criteria strictly
    practice_questions = PracticeQuestion.get_by_challenge(challenge.slug)
    interview_questions = InterviewQuestion.get_by_challenge(challenge.slug)
    coding_problems = CodingProblem.get_by_challenge(challenge.slug)
    assignment_sub = ChallengeAssignmentSubmission.get_user_submission(user_id, challenge.slug)

    eval_result = enrollment.evaluate_refund_eligibility(
        total_modules=len(challenge.modules),
        total_practice=len(practice_questions),
        total_interviews=len(interview_questions),
        total_coding=len(coding_problems),
        assignment_submission_status=assignment_sub.status if assignment_sub else None,
        duration_days=challenge.duration_days,
    )

    if not eval_result["all_eligible"]:
        unmet = [c["condition"] for c in eval_result["criteria"] if not c["fulfilled"]]
        return jsonify({
            "success": False,
            "error": f"Incomplete requirements for 100% refund. Unmet conditions: {', '.join(unmet)}",
            "criteria": eval_result["criteria"],
        }), 400

    data = request.get_json(silent=True) or request.form.to_dict() or {}
    upi_id = str(data.get("upi_id", "")).strip()
    account_name = str(data.get("account_holder_name", "")).strip()
    phone = str(data.get("phone_number", "")).strip()

    if not upi_id or "@" not in upi_id:
        return jsonify({"success": False, "error": "Please provide a valid UPI ID (e.g. name@okhdfcbank)."}), 400

    claim = RefundClaim({
        "user_id": user_id,
        "challenge_slug": challenge.slug,
        "amount": float(enrollment.amount_paid or challenge.price or 499.0),
        "upi_id": upi_id,
        "account_holder_name": account_name or getattr(current_user, "name", "Student"),
        "phone_number": phone or getattr(current_user, "phone", ""),
        "status": "pending",
        "criteria_snapshot": eval_result["criteria"],
        "submitted_at": datetime.now(timezone.utc),
    })
    claim.save()

    # Update enrollment refund claim status
    enrollment.refund_status = "claimed"
    enrollment.save()

    # Non-blocking email alert to platform administrative email: skillrockk@gmail.com
    try:
        from services.email_service import send_email
        subject = f"🔔 [SkillRock 100% Refund Claim] {current_user.name} — ₹{claim.amount:.0f}"
        body = f"""
New 100% Monthly Challenge Refund Claim Received:

Student Name: {current_user.name}
Student Email: {current_user.email}
Challenge: {challenge.title}
Enrolled Amount: ₹{claim.amount:.0f}
UPI ID: {claim.upi_id}
Account Name: {claim.account_holder_name}
Claim Reference: {claim.claim_id}
Submitted At: {claim.submitted_at.strftime('%Y-%m-%d %H:%M:%S UTC')}

All 7 required challenge conditions were verified by SkillRock backend:
- 100% Modules Completed: Yes
- 100% Practice Arena Questions: Yes
- 100% Interview Prep Completed: Yes
- 100% Coding Arena Problems: Yes
- Practical Assignment Submitted: Yes
- Final 50-MCQ Assessment Passed (>=80%): Yes
- Within 28-Day Deadline: Yes

Review and process this payout at:
https://skillrock.in/admin/challenges/refunds
"""
        send_email("skillrockk@gmail.com", subject, body)
    except Exception as e:
        logger.info(f"Refund notification dispatch notice: {e}")

    return jsonify({
        "success": True,
        "message": "Your 100% refund claim has been submitted! Our accounts team will review and credit your UPI within 3-5 business days.",
        "claim_id": claim.claim_id,
        "status": "pending",
    })
