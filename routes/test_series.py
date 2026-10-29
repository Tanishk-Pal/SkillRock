"""
SkillRock — Interview Test Series Routes & Assessment Controller
Handles public discovery, timed testing engine, autosaving responses,
focus-loss anti-cheating monitoring, and server-side evaluation.
"""

from datetime import datetime, timezone, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, abort
from flask_login import login_required, current_user
from models.test_series import Question, TestDefinition, TestPack, TestAttempt, UserEntitlement
from models.mongo import _to_obj_id

test_series_bp = Blueprint("test_series", __name__, url_prefix="/test-series")

def _finalize_attempt(attempt, test=None):
    """
    Server-side scoring engine: evaluates an attempt against the authoritative
    question bank, computing marks, topic breakdowns, and solutions.
    """
    if attempt.status in [TestAttempt.STATUS_COMPLETED, TestAttempt.STATUS_CANCELLED]:
        return attempt

    if not test:
        test = TestDefinition.get_by_id(attempt.test_id)
        if not test:
            attempt.status = TestAttempt.STATUS_TIMED_OUT
            attempt.save()
            return attempt

    questions = test.questions
    total_score = 0.0
    max_score = 0.0
    correct_count = 0
    incorrect_count = 0
    unanswered_count = 0
    topic_stats = {}
    question_results = []

    for q in questions:
        max_score += q.marks
        user_resp = attempt.responses.get(q.id, {}) or attempt.responses.get(str(q.id), {})
        user_ans = user_resp.get("answer") if isinstance(user_resp, dict) else user_resp

        # Category/topic tracking
        topic = q.subtopic or q.category or "General"
        if topic not in topic_stats:
            topic_stats[topic] = {"total": 0, "correct": 0, "marks": 0.0}
        topic_stats[topic]["total"] += 1

        is_correct = False
        is_answered = user_ans is not None and user_ans != "" and user_ans != []

        if not is_answered:
            unanswered_count += 1
            marks_awarded = 0.0
        else:
            # Check correctness based on question type
            if q.question_type == Question.TYPE_MULTIPLE_SELECT:
                user_set = set(user_ans) if isinstance(user_ans, list) else {str(user_ans)}
                correct_set = set(q.correct_answers)
                if user_set == correct_set:
                    is_correct = True
                    correct_count += 1
                    marks_awarded = q.marks
                else:
                    incorrect_count += 1
                    marks_awarded = -abs(q.negative_marks)
            else:
                val = user_ans[0] if (isinstance(user_ans, list) and len(user_ans) > 0) else user_ans
                user_str = str(val).strip().lower()
                correct_strs = [str(ca).strip().lower() for ca in q.correct_answers]
                if user_str in correct_strs:
                    is_correct = True
                    correct_count += 1
                    marks_awarded = q.marks
                else:
                    incorrect_count += 1
                    marks_awarded = -abs(q.negative_marks)

        if is_correct:
            topic_stats[topic]["correct"] += 1
            topic_stats[topic]["marks"] += marks_awarded

        total_score += marks_awarded

        # Record question result with full solution for review screen
        question_results.append({
            "question_id": q.id,
            "question_text": q.question_text,
            "question_type": q.question_type,
            "category": q.category,
            "subtopic": q.subtopic,
            "difficulty": q.difficulty,
            "options": q.options,
            "code_snippet": q.code_snippet,
            "language": q.language,
            "marks": q.marks,
            "negative_marks": q.negative_marks,
            "user_answer": user_ans,
            "correct_answers": q.correct_answers,
            "is_correct": is_correct,
            "marks_awarded": marks_awarded,
            "explanation": q.explanation
        })

    # Prevent negative overall test score
    final_score = max(0.0, round(total_score, 2))
    max_score = max(1.0, round(max_score, 2))
    percentage = round((final_score / max_score) * 100, 2)
    answered_total = correct_count + incorrect_count
    accuracy = round((correct_count / answered_total) * 100, 2) if answered_total > 0 else 0.0

    # Format topic breakdown percentages
    breakdown = {}
    for top, data in topic_stats.items():
        breakdown[top] = {
            "total": data["total"],
            "correct": data["correct"],
            "percentage": round((data["correct"] / data["total"]) * 100, 1) if data["total"] > 0 else 0.0
        }

    attempt.status = TestAttempt.STATUS_COMPLETED
    attempt.submitted_at = datetime.now(timezone.utc)
    started = attempt.started_at
    if started.tzinfo is None:
        started = started.replace(tzinfo=timezone.utc)
    attempt.time_taken_seconds = max(1, int((attempt.submitted_at - started).total_seconds()))
    attempt.score = final_score
    attempt.max_score = max_score
    attempt.percentage = percentage
    attempt.is_passed = percentage >= test.passing_percentage
    attempt.correct_count = correct_count
    attempt.incorrect_count = incorrect_count
    attempt.unanswered_count = unanswered_count
    attempt.accuracy_percentage = accuracy
    attempt.topic_breakdown = breakdown
    attempt.question_results = question_results
    attempt.save()
    return attempt


# -------------------------------------------------------------------------
# Public Discovery & Catalog
# -------------------------------------------------------------------------

@test_series_bp.route("/", strict_slashes=False)
@test_series_bp.route("", strict_slashes=False)
def landing():
    """
    Interview Test Series Landing Page.
    Search, filters, free tests, premium packs, and student attempt progress.
    """
    search_q = request.args.get("q", "").strip().lower()
    selected_category = request.args.get("category", "").strip()
    selected_difficulty = request.args.get("difficulty", "").strip()
    selected_price = request.args.get("price", "all").strip().lower()
    active_tab = request.args.get("tab", "all").strip().lower()

    # Query all published tests and test packs
    all_tests = TestDefinition.find_all({"is_published": True, "is_archived": False})
    all_packs = TestPack.find_all({"status": {"$in": [TestPack.STATUS_PUBLISHED, TestPack.STATUS_COMING_SOON]}})

    # Filter tests
    filtered_tests = []
    for t in all_tests:
        if search_q:
            match_title = search_q in t.title.lower()
            match_desc = search_q in t.description.lower()
            match_cat = search_q in t.category.lower()
            if not (match_title or match_desc or match_cat):
                continue
        if selected_category and t.category != selected_category:
            continue
        if selected_difficulty and t.difficulty != selected_difficulty:
            continue
        if selected_price == "free" and not t.is_free:
            continue
        if selected_price == "paid" and t.is_free:
            continue
        filtered_tests.append(t)

    # Student progress map (if authenticated)
    student_attempts = []
    user_test_stats = {}
    if current_user.is_authenticated and current_user.id:
        student_attempts = TestAttempt.find_by_user(current_user.id, limit=20)
        for att in student_attempts:
            tid = att.test_id
            if tid not in user_test_stats:
                user_test_stats[tid] = {
                    "attempts_count": 0,
                    "best_score": 0.0,
                    "best_percentage": 0.0,
                    "is_passed": False,
                    "latest_status": att.status,
                    "has_active": False,
                    "active_attempt_id": None
                }
            user_test_stats[tid]["attempts_count"] += 1
            if att.status == TestAttempt.STATUS_IN_PROGRESS:
                if not att.is_expired:
                    user_test_stats[tid]["has_active"] = True
                    user_test_stats[tid]["active_attempt_id"] = att.id
            if att.status == TestAttempt.STATUS_COMPLETED:
                if att.percentage > user_test_stats[tid]["best_percentage"]:
                    user_test_stats[tid]["best_percentage"] = att.percentage
                    user_test_stats[tid]["best_score"] = att.score
                if att.is_passed:
                    user_test_stats[tid]["is_passed"] = True

    categories = [
        "Quantitative Aptitude",
        "Logical Reasoning",
        "Programming Fundamentals",
        "Data Structures and Algorithms",
        "Coding and Output Prediction",
        "Database and SQL",
        "Computer Science Fundamentals",
        "Technical Interviews",
        "Company-Style Placement Preparation"
    ]

    return render_template(
        "test_series/landing.html",
        tests=filtered_tests,
        packs=all_packs,
        categories=categories,
        selected_category=selected_category,
        selected_difficulty=selected_difficulty,
        selected_price=selected_price,
        search_q=search_q,
        active_tab=active_tab,
        user_test_stats=user_test_stats,
        recent_attempts=student_attempts[:5]
    )


@test_series_bp.route("/packs/<pack_slug>")
def pack_detail(pack_slug):
    """Details of a curated Test Pack including included tests, topics, and video masterclasses."""
    pack = TestPack.get_by_slug(pack_slug)
    if not pack:
        flash("The requested test pack could not be found.", "warning")
        return redirect(url_for("test_series.landing"))

    tests = pack.tests
    return render_template("test_series/pack_detail.html", pack=pack, tests=tests)


@test_series_bp.route("/tests/<test_slug>")
def test_detail(test_slug):
    """
    Test Overview & Briefing Screen.
    Explains duration, question count, marking scheme, rules, and focus loss warnings.
    """
    test = TestDefinition.get_by_slug(test_slug)
    if not test or not test.is_published:
        flash("The requested test could not be found or is not yet published.", "warning")
        return redirect(url_for("test_series.landing"))

    active_attempt = None
    past_attempts = []
    has_access = False

    if current_user.is_authenticated and current_user.id:
        has_access = UserEntitlement.has_access_to_test(current_user, test)
        active_attempt = TestAttempt.get_active_attempt(current_user.id, test.id)
        if active_attempt and active_attempt.is_expired:
            _finalize_attempt(active_attempt, test)
            active_attempt = None
        past_attempts = [a for a in TestAttempt.find_by_user(current_user.id) if a.test_id == test.id]

    return render_template(
        "test_series/test_detail.html",
        test=test,
        active_attempt=active_attempt,
        past_attempts=past_attempts,
        has_access=has_access
    )


# -------------------------------------------------------------------------
# Timed Assessment Engine & Anti-Cheat APIs
# -------------------------------------------------------------------------

@test_series_bp.route("/tests/<test_slug>/start", methods=["POST"])
@login_required
def start_test(test_slug):
    """Starts or resumes an active timed test attempt."""
    test = TestDefinition.get_by_slug(test_slug)
    if not test or not test.is_published:
        flash("The requested test is not available.", "danger")
        return redirect(url_for("test_series.landing"))

    # Entitlement check
    if not UserEntitlement.has_access_to_test(current_user, test):
        flash("This test requires access to an Interview Test Pack. Purchases will be available soon.", "warning")
        return redirect(url_for("test_series.test_detail", test_slug=test.slug))

    # Check for active in-progress attempt
    active_attempt = TestAttempt.get_active_attempt(current_user.id, test.id)
    if active_attempt:
        if not active_attempt.is_expired:
            return redirect(url_for("test_series.exam_room", attempt_id=active_attempt.id))
        else:
            _finalize_attempt(active_attempt, test)

    # Initialize new attempt with authoritative server timestamps
    now = datetime.now(timezone.utc)
    deadline = now + timedelta(minutes=test.duration_minutes)

    questions = test.questions
    initial_responses = {}
    for q in questions:
        initial_responses[q.id] = {
            "answer": None,
            "marked_for_review": False,
            "saved_at": None
        }

    attempt = TestAttempt({
        "user_id": str(current_user.id),
        "test_id": test.id,
        "test_title": test.title,
        "test_slug": test.slug,
        "status": TestAttempt.STATUS_IN_PROGRESS,
        "started_at": now,
        "duration_minutes": test.duration_minutes,
        "deadline_at": deadline,
        "responses": initial_responses,
        "focus_loss_events": [],
        "warning_count": 0
    }).save()

    return redirect(url_for("test_series.exam_room", attempt_id=attempt.id))


@test_series_bp.route("/attempts/<attempt_id>")
@login_required
def exam_room(attempt_id):
    """
    Dedicated Timed Assessment Room.
    Serves sanitized question payloads, synchronized countdown timer, and question palette.
    """
    attempt = TestAttempt.get_by_id(attempt_id)
    if not attempt or (attempt.user_id != str(current_user.id) and not getattr(current_user, "is_admin", False)):
        flash("Test attempt not found or access unauthorized.", "danger")
        return redirect(url_for("test_series.landing"))

    test = TestDefinition.get_by_id(attempt.test_id)
    if not test:
        flash("Associated test definition was not found.", "danger")
        return redirect(url_for("test_series.landing"))

    # If already submitted or cancelled, redirect to result
    if attempt.status in [TestAttempt.STATUS_COMPLETED, TestAttempt.STATUS_CANCELLED]:
        return redirect(url_for("test_series.attempt_result", attempt_id=attempt.id))

    # Auto-finalize if time has expired
    if attempt.is_expired:
        _finalize_attempt(attempt, test)
        flash("Assessment time has elapsed. Your responses have been automatically submitted.", "info")
        return redirect(url_for("test_series.attempt_result", attempt_id=attempt.id))

    # Prepare sanitized questions: NEVER leak correct answers or explanations to active test client!
    questions = test.questions
    sanitized_questions = [q.to_dict(include_solutions=False) for q in questions]

    return render_template(
        "test_series/exam_room.html",
        attempt=attempt,
        test=test,
        questions=sanitized_questions,
        remaining_seconds=attempt.remaining_seconds
    )


@test_series_bp.route("/attempts/<attempt_id>/save-answer", methods=["POST"])
@login_required
def save_answer(attempt_id):
    """
    Continuous Auto-Save API.
    Saves student answer in real-time without resetting or trusting client timer.
    """
    attempt = TestAttempt.get_by_id(attempt_id)
    if not attempt or (attempt.user_id != str(current_user.id) and not getattr(current_user, "is_admin", False)):
        return jsonify({"success": False, "error": "Unauthorized"}), 403

    if attempt.status != TestAttempt.STATUS_IN_PROGRESS:
        return jsonify({"success": False, "error": f"Attempt is {attempt.status}."}), 400

    if attempt.is_expired:
        _finalize_attempt(attempt)
        return jsonify({
            "success": False,
            "expired": True,
            "redirect_url": url_for("test_series.attempt_result", attempt_id=attempt.id)
        }), 200

    data = request.get_json(silent=True) or {}
    qid = str(data.get("question_id", ""))
    answer = data.get("answer") if "answer" in data else data.get("selected_options")
    marked_for_review = bool(data.get("marked_for_review", False))

    if not qid:
        return jsonify({"success": False, "error": "Question ID required."}), 400

    now_iso = datetime.now(timezone.utc).isoformat()
    if not isinstance(attempt.responses, dict):
        attempt.responses = {}

    attempt.responses[qid] = {
        "answer": answer,
        "marked_for_review": marked_for_review,
        "saved_at": now_iso
    }
    attempt.save()

    return jsonify({
        "success": True,
        "question_id": qid,
        "saved_at": now_iso,
        "remaining_seconds": attempt.remaining_seconds
    })


@test_series_bp.route("/attempts/<attempt_id>/focus-loss", methods=["POST"])
@login_required
def record_focus_loss(attempt_id):
    """
    Anti-Cheat Focus-Loss Event Logger.
    Logs tab visibility/window blur with 5s cooldown debounce.
    Enforces maximum 3 warnings; 4th qualifying violation immediately cancels test.
    """
    attempt = TestAttempt.get_by_id(attempt_id)
    if not attempt or (attempt.user_id != str(current_user.id) and not getattr(current_user, "is_admin", False)):
        return jsonify({"success": False, "error": "Unauthorized"}), 403

    if attempt.status != TestAttempt.STATUS_IN_PROGRESS:
        return jsonify({"success": False, "error": "Attempt is not in progress."}), 400

    data = request.get_json(silent=True) or {}
    event_type = str(data.get("event_type", "visibility_hidden")).strip()
    reason = str(data.get("reason", "Student navigated away from test window.")).strip()

    recorded, warning_count, cancelled = attempt.add_focus_loss_event(event_type, reason)

    redirect_url = None
    if cancelled:
        redirect_url = url_for("test_series.attempt_result", attempt_id=attempt.id)

    return jsonify({
        "success": True,
        "recorded": recorded,
        "warning_count": warning_count,
        "cancelled": cancelled,
        "status": "cancelled" if cancelled else "warning",
        "cancellation_reason": attempt.cancellation_reason if cancelled else None,
        "redirect_url": redirect_url
    })


@test_series_bp.route("/attempts/<attempt_id>/submit", methods=["POST"])
@login_required
def submit_test(attempt_id):
    """
    Final Submission API.
    Idempotently evaluates answers and generates student result.
    """
    attempt = TestAttempt.get_by_id(attempt_id)
    if not attempt or (attempt.user_id != str(current_user.id) and not getattr(current_user, "is_admin", False)):
        return jsonify({"success": False, "error": "Unauthorized"}), 403

    # Idempotent handling: if already completed, return result redirect immediately
    if attempt.status == TestAttempt.STATUS_COMPLETED:
        return jsonify({
            "success": True,
            "redirect_url": url_for("test_series.attempt_result", attempt_id=attempt.id)
        })

    if attempt.status == TestAttempt.STATUS_CANCELLED:
        return jsonify({
            "success": False,
            "error": "This test was cancelled due to focus-loss limit violations and cannot be submitted."
        }), 400

    # Save any final payload passed in request
    data = request.get_json(silent=True) or {}
    final_responses = data.get("responses")
    if isinstance(final_responses, dict):
        for qid, val in final_responses.items():
            if isinstance(val, dict):
                attempt.responses[str(qid)] = val
            else:
                attempt.responses[str(qid)] = {
                    "answer": val,
                    "marked_for_review": False,
                    "saved_at": datetime.now(timezone.utc).isoformat()
                }

    # Evaluate attempt
    _finalize_attempt(attempt)

    return jsonify({
        "success": True,
        "redirect_url": url_for("test_series.attempt_result", attempt_id=attempt.id)
    })


# -------------------------------------------------------------------------
# Results, Performance Analysis & History
# -------------------------------------------------------------------------

@test_series_bp.route("/attempts/<attempt_id>/result")
@login_required
def attempt_result(attempt_id):
    """
    Test Results, Score Card & Solution Review Page.
    Shows score, accuracy, topic breakdown, actionable practice recommendations,
    and detailed step-by-step solutions (or cancellation explanation).
    """
    attempt = TestAttempt.get_by_id(attempt_id)
    if not attempt or (attempt.user_id != str(current_user.id) and not getattr(current_user, "is_admin", False)):
        flash("Attempt record not found or access denied.", "danger")
        return redirect(url_for("test_series.landing"))

    test = TestDefinition.get_by_id(attempt.test_id)

    # Compute recommended practice topics based on topics where score < 70%
    recommended_topics = []
    if attempt.status == TestAttempt.STATUS_COMPLETED and attempt.topic_breakdown:
        for topic, data in attempt.topic_breakdown.items():
            if data.get("percentage", 0.0) < 70.0:
                recommended_topics.append({
                    "topic": topic,
                    "percentage": data.get("percentage", 0.0),
                    "correct": data.get("correct", 0),
                    "total": data.get("total", 0)
                })
        recommended_topics.sort(key=lambda x: x["percentage"])

    return render_template(
        "test_series/result.html",
        attempt=attempt,
        test=test,
        recommended_topics=recommended_topics
    )


@test_series_bp.route("/my-attempts")
@login_required
def my_attempts():
    """Student's comprehensive test series attempt history and performance trends."""
    attempts = TestAttempt.find_by_user(current_user.id)
    return render_template("test_series/my_attempts.html", attempts=attempts)
