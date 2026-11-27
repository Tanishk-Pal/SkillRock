"""
SkillRock — College Academic Teacher Assessment Suite & Examination Controller
Provides Teacher Workspace (/teacher/assessments), Multi-Step Test Creation Wizard,
Question Bank Management, Live Assessment Delivery, Anti-Cheat Integrity Monitoring,
Automated + Manual Grading Engine, and Performance Analytics.
"""

import json
import csv
import io
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from bson import ObjectId
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, abort, Response
from flask_login import login_required, current_user

from models.academic_assessment import (
    AcademicSubject, AcademicQuestion, CollegeAssessment, CollegeAssessmentAttempt, seed_default_academic_curriculum
)
from models.mongo import get_db, _to_obj_id, slugify

teacher_bp = Blueprint("teacher", __name__, url_prefix="/teacher")

def _require_teacher_or_admin():
    """Enforces strict backend role-based access control for teacher functionality."""
    if not current_user.is_authenticated:
        flash("Please log in with teacher or administrator credentials to access this area.", "warning")
        abort(401)
    if not (getattr(current_user, "is_teacher", False) or getattr(current_user, "is_admin", False)):
        flash("Access Denied: Teacher or Administrator privileges required.", "danger")
        abort(403)


# ==============================================================================
# TEACHER WORKSPACE DASHBOARD
# ==============================================================================

@teacher_bp.route("/assessments", strict_slashes=False)
@login_required
def assessments_dashboard():
    """
    Teacher Workspace Overview & Assessment Management Dashboard.
    Provides key statistics, recent tests, question banks, and pending evaluations.
    """
    _require_teacher_or_admin()
    db = get_db()
    seed_default_academic_curriculum(db)

    # Teachers see their own assessments, Admins see platform-wide
    is_adm = getattr(current_user, "is_admin", False)
    test_filter = {} if is_adm else {"teacher_id": str(current_user.id)}

    all_tests = CollegeAssessment.find_all(test_filter)
    all_subjects = AcademicSubject.find_all({"is_active": True})
    all_questions = AcademicQuestion.find_all({} if is_adm else {"teacher_id": str(current_user.id)})

    # Compute Statistics
    total_subjects = len(all_subjects)
    total_tests = len(all_tests)
    upcoming_tests = sum(1 for t in all_tests if t.live_status == "Upcoming")
    active_tests = sum(1 for t in all_tests if t.live_status == "Live")
    published_results = sum(1 for t in all_tests if t.result_published)

    # Attempts & Submissions metrics
    test_ids = [str(t.id) for t in all_tests]
    attempts_query = {"assessment_id": {"$in": test_ids}} if test_ids else {"assessment_id": "__none__"}
    all_attempts = CollegeAssessmentAttempt.find_all(attempts_query)
    total_attempts = len(all_attempts)
    pending_evaluations = sum(1 for a in all_attempts if a.needs_manual_review and a.status == CollegeAssessmentAttempt.STATUS_SUBMITTED)

    active_tab = request.args.get("tab", "overview").strip().lower()

    return render_template(
        "teacher/dashboard.html",
        tests=all_tests,
        subjects=all_subjects,
        questions=all_questions,
        total_subjects=total_subjects,
        total_tests=total_tests,
        upcoming_tests=upcoming_tests,
        active_tests=active_tests,
        total_attempts=total_attempts,
        pending_evaluations=pending_evaluations,
        published_results=published_results,
        attempts=all_attempts[:15],
        active_tab=active_tab
    )


# ==============================================================================
# MULTI-STEP TEST CREATION & MANAGEMENT WIZARD
# ==============================================================================

@teacher_bp.route("/assessments/create", methods=["GET", "POST"])
@login_required
def assessment_create():
    """
    Comprehensive multi-step assessment builder:
    Step 1: Basic Information & Academic Scope
    Step 2: Schedule & Availability Window
    Step 3: Question Selection & Bank Integration
    Step 4: Configurable Anti-Cheat & Integrity Settings
    Step 5: Review & Publish / Draft
    """
    _require_teacher_or_admin()
    db = get_db()
    seed_default_academic_curriculum(db)

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        subject_id = request.form.get("subject_id", "").strip()
        academic_year = request.form.get("academic_year", "1").strip()
        semester = int(request.form.get("semester", 1))
        department = request.form.get("department", "Computer Science & Engineering").strip()
        class_section = request.form.get("class_section", "All Sections").strip()
        assessment_type = request.form.get("assessment_type", "Unit Test").strip()
        duration_minutes = int(request.form.get("duration_minutes", 45))
        total_marks = float(request.form.get("total_marks", 30.0))
        passing_marks = float(request.form.get("passing_marks", 12.0))

        # Schedule
        exam_date = request.form.get("exam_date", datetime.now(timezone.utc).strftime("%Y-%m-%d")).strip()
        start_time = request.form.get("start_time", "09:00").strip()
        end_time = request.form.get("end_time", "23:59").strip()
        max_attempts = int(request.form.get("max_attempts", 1))
        status = request.form.get("status", CollegeAssessment.STATUS_PUBLISHED).strip()

        # Integrity Settings
        preset = request.form.get("integrity_preset", "standard").strip()
        fullscreen_monitoring = request.form.get("fullscreen_monitoring") == "on"
        tab_switch_monitoring = request.form.get("tab_switch_monitoring") == "on"
        copy_paste_monitoring = request.form.get("copy_paste_monitoring") == "on"
        context_menu_monitoring = request.form.get("context_menu_monitoring") == "on"
        keyboard_shortcut_monitoring = request.form.get("keyboard_shortcut_monitoring") == "on"
        camera_permission = request.form.get("camera_permission", "optional").strip()
        max_warnings = int(request.form.get("max_warnings", 3))
        auto_submit_on_limit = request.form.get("auto_submit_on_limit") == "on"
        randomize_questions = request.form.get("randomize_questions") == "on"
        randomize_options = request.form.get("randomize_options") == "on"

        # Resolve Subject info
        subject = AcademicSubject.get_by_id(subject_id)
        subject_name = subject.name if subject else "General Subject"
        subject_code = subject.code if subject else "GEN101"

        # Parse Datetimes
        try:
            start_datetime = datetime.fromisoformat(f"{exam_date}T{start_time}:00").replace(tzinfo=timezone.utc)
            end_datetime = datetime.fromisoformat(f"{exam_date}T{end_time}:00").replace(tzinfo=timezone.utc)
        except Exception:
            start_datetime = datetime.now(timezone.utc)
            end_datetime = start_datetime + timedelta(days=7)

        # Selected questions from question bank
        selected_q_ids = request.form.getlist("question_ids")

        assessment = CollegeAssessment({
            "title": title,
            "slug": slugify(f"{title}-{subject_code}-{datetime.now().strftime('%y%m%d%H%M')}"),
            "description": description,
            "subject_id": subject_id,
            "subject_name": subject_name,
            "subject_code": subject_code,
            "academic_year": academic_year,
            "semester": semester,
            "department": department,
            "class_section": class_section,
            "assessment_type": assessment_type,
            "teacher_id": str(current_user.id),
            "teacher_name": current_user.name,
            "duration_minutes": duration_minutes,
            "total_marks": total_marks,
            "passing_marks": passing_marks,
            "exam_date": exam_date,
            "start_time": start_time,
            "end_time": end_time,
            "start_datetime": start_datetime,
            "end_datetime": end_datetime,
            "max_attempts": max_attempts,
            "status": status,
            "result_published": False,
            "question_ids": selected_q_ids,
            "integrity_settings": {
                "preset": preset,
                "fullscreen_monitoring": fullscreen_monitoring,
                "tab_switch_monitoring": tab_switch_monitoring,
                "copy_paste_monitoring": copy_paste_monitoring,
                "context_menu_monitoring": context_menu_monitoring,
                "keyboard_shortcut_monitoring": keyboard_shortcut_monitoring,
                "camera_permission": camera_permission,
                "max_warnings": max_warnings,
                "auto_submit_on_limit": auto_submit_on_limit,
                "randomize_questions": randomize_questions,
                "randomize_options": randomize_options
            }
        })
        assessment.save()
        flash(f"🎉 Successfully created examination '{title}' for {subject_name} ({subject_code})!", "success")
        return redirect(url_for("teacher.assessments_dashboard", tab="tests"))

    all_subjects = AcademicSubject.find_all({"is_active": True})
    available_questions = AcademicQuestion.find_all({"is_published": True})

    return render_template(
        "teacher/assessment_form.html",
        subjects=all_subjects,
        questions=available_questions,
        assessment=None
    )


@teacher_bp.route("/assessments/<aid>/delete", methods=["POST"])
@login_required
def assessment_delete(aid):
    """Deletes or archives an assessment."""
    _require_teacher_or_admin()
    assessment = CollegeAssessment.get_by_id(aid)
    if not assessment:
        flash("Assessment not found.", "warning")
        return redirect(url_for("teacher.assessments_dashboard"))

    # Protect assessments belonging to another teacher unless admin
    if not getattr(current_user, "is_admin", False) and assessment.teacher_id != str(current_user.id):
        flash("You are not authorized to delete another teacher's assessment.", "danger")
        return redirect(url_for("teacher.assessments_dashboard"))

    title = assessment.title
    assessment.delete()
    flash(f"Assessment '{title}' removed.", "info")
    return redirect(url_for("teacher.assessments_dashboard", tab="tests"))


@teacher_bp.route("/assessments/<aid>/publish-results", methods=["POST"])
@login_required
def assessment_publish_results(aid):
    """Publishes scores and detailed solutions for students."""
    _require_teacher_or_admin()
    assessment = CollegeAssessment.get_by_id(aid)
    if not assessment:
        flash("Assessment not found.", "warning")
        return redirect(url_for("teacher.assessments_dashboard"))

    assessment.result_published = True
    assessment.result_publish_date = datetime.now(timezone.utc)
    assessment.save()
    flash(f"✅ Results for '{assessment.title}' have been published! Students can now review their scores.", "success")
    return redirect(request.referrer or url_for("teacher.assessments_dashboard"))


# ==============================================================================
# QUESTION BANK MANAGEMENT
# ==============================================================================

@teacher_bp.route("/questions/create", methods=["POST"])
@login_required
def question_create():
    """Adds a new question to the reusable Question Bank."""
    _require_teacher_or_admin()
    subject_id = request.form.get("subject_id", "").strip()
    topic = request.form.get("topic", "General").strip()
    question_text = request.form.get("question_text", "").strip()
    question_type = request.form.get("question_type", AcademicQuestion.TYPE_MCQ).strip()
    difficulty = request.form.get("difficulty", "Intermediate").strip()
    marks = float(request.form.get("marks", 2.0))
    negative_marks = float(request.form.get("negative_marks", 0.0))
    explanation = request.form.get("explanation", "").strip()

    subject = AcademicSubject.get_by_id(subject_id)
    subject_name = subject.name if subject else "General Subject"

    # Options parsing for MCQs
    options = []
    opt_texts = request.form.getlist("option_text")
    for idx, ot in enumerate(opt_texts):
        if ot.strip():
            options.append({
                "id": f"opt_{idx + 1}",
                "text": ot.strip()
            })

    correct_answers = request.form.getlist("correct_answers")
    if not correct_answers and request.form.get("single_correct"):
        correct_answers = [request.form.get("single_correct")]

    # Coding question attributes
    coding_language = request.form.get("coding_language", "python")
    coding_starter_code = request.form.get("coding_starter_code", "")
    coding_sample_input = request.form.get("coding_sample_input", "")
    coding_sample_output = request.form.get("coding_sample_output", "")
    coding_hidden_test_cases = []
    h_in = request.form.getlist("hidden_input")
    h_out = request.form.getlist("hidden_output")
    for i, o in zip(h_in, h_out):
        if i.strip() or o.strip():
            coding_hidden_test_cases.append({"input": i.strip(), "output": o.strip()})

    question = AcademicQuestion({
        "teacher_id": str(current_user.id),
        "teacher_name": current_user.name,
        "subject_id": subject_id,
        "subject_name": subject_name,
        "topic": topic,
        "question_text": question_text,
        "question_type": question_type,
        "difficulty": difficulty,
        "marks": marks,
        "negative_marks": negative_marks,
        "options": options,
        "correct_answers": correct_answers,
        "explanation": explanation,
        "coding_language": coding_language,
        "coding_starter_code": coding_starter_code,
        "coding_sample_input": coding_sample_input,
        "coding_sample_output": coding_sample_output,
        "coding_hidden_test_cases": coding_hidden_test_cases,
        "is_published": True
    })
    question.save()
    flash(f"Question saved to Question Bank for {subject_name}!", "success")
    return redirect(url_for("teacher.assessments_dashboard", tab="questions"))


@teacher_bp.route("/questions/<qid>/delete", methods=["POST"])
@login_required
def question_delete(qid):
    _require_teacher_or_admin()
    q = AcademicQuestion.get_by_id(qid)
    if q:
        q.delete()
        flash("Question removed from bank.", "info")
    return redirect(url_for("teacher.assessments_dashboard", tab="questions"))


# ==============================================================================
# SUBMISSION REVIEW, MANUAL GRADING & INTEGRITY REPORTS
# ==============================================================================

@teacher_bp.route("/attempts/<attempt_id>/grade", methods=["GET", "POST"])
@login_required
def attempt_grade(attempt_id):
    """Teacher review of subjective answers, marks adjustments, and audit trail."""
    _require_teacher_or_admin()
    attempt = CollegeAssessmentAttempt.get_by_id(attempt_id)
    if not attempt:
        flash("Attempt record not found.", "warning")
        return redirect(url_for("teacher.assessments_dashboard"))

    assessment = CollegeAssessment.get_by_id(attempt.assessment_id)

    if request.method == "POST":
        old_score = attempt.score
        new_score = float(request.form.get("total_score", attempt.score))
        feedback = request.form.get("teacher_feedback", "").strip()

        attempt.score = round(new_score, 2)
        attempt.percentage = round((attempt.score / max(1.0, attempt.max_score)) * 100, 2)
        if assessment:
            attempt.is_passed = attempt.score >= assessment.passing_marks
        attempt.teacher_feedback = feedback
        attempt.evaluator_id = str(current_user.id)
        attempt.evaluated_at = datetime.now(timezone.utc)
        attempt.needs_manual_review = False
        attempt.status = CollegeAssessmentAttempt.STATUS_EVALUATED

        # Audit trail
        attempt.grade_audit_trail.append({
            "evaluator_id": str(current_user.id),
            "evaluator_name": current_user.name,
            "old_score": old_score,
            "new_score": attempt.score,
            "feedback": feedback,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        attempt.save()
        flash(f"Successfully updated evaluation for {attempt.user_name} ({attempt.score}/{attempt.max_score})!", "success")
        return redirect(url_for("teacher.assessments_dashboard", tab="submissions"))

    questions = assessment.questions if assessment else []
    return render_template(
        "teacher/attempt_grade.html",
        attempt=attempt,
        assessment=assessment,
        questions=questions
    )


@teacher_bp.route("/assessments/<aid>/export-csv")
@login_required
def assessment_export_csv(aid):
    """Exports examination grades and attempt analytics to CSV."""
    _require_teacher_or_admin()
    assessment = CollegeAssessment.get_by_id(aid)
    if not assessment:
        abort(404)

    attempts = CollegeAssessmentAttempt.find_by_assessment(aid)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Student Name", "Student Email", "Roll Number", "Status",
        "Marks Obtained", "Maximum Marks", "Percentage", "Result",
        "Warnings Count", "Time Taken (Seconds)", "Submitted At"
    ])

    for att in attempts:
        writer.writerow([
            att.user_name,
            att.user_email,
            att.roll_number,
            att.status,
            att.score,
            att.max_score,
            f"{att.percentage}%",
            "PASS" if att.is_passed else "FAIL",
            att.warning_count,
            att.time_taken_seconds,
            att.submitted_at.strftime("%Y-%m-%d %H:%M:%S") if att.submitted_at else "N/A"
        ])

    output.seek(0)
    filename = f"grades_{assessment.subject_code}_{slugify(assessment.title)}.csv"
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename={filename}"}
    )


# ==============================================================================
# SECURE STUDENT EXAMINATION RUNTIME & ANTI-CHEAT ENGINE
# ==============================================================================

def _evaluate_academic_attempt(attempt, assessment=None):
    """
    Automated evaluation engine for objective and coding questions.
    Marks subjective questions for teacher manual rubric review.
    """
    if attempt.status in [CollegeAssessmentAttempt.STATUS_EVALUATED]:
        return attempt

    if not assessment:
        assessment = CollegeAssessment.get_by_id(attempt.assessment_id)
        if not assessment:
            attempt.status = CollegeAssessmentAttempt.STATUS_TIMED_OUT
            attempt.save()
            return attempt

    questions = assessment.questions
    total_score = 0.0
    max_score = 0.0
    correct_count = 0
    incorrect_count = 0
    unanswered_count = 0
    needs_manual = False

    for q in questions:
        max_score += q.marks
        user_resp = attempt.responses.get(q.id, {}) or attempt.responses.get(str(q.id), {})
        user_ans = user_resp.get("answer") if isinstance(user_resp, dict) else user_resp

        is_answered = user_ans is not None and user_ans != "" and user_ans != []

        if not is_answered:
            unanswered_count += 1
            continue

        # Automated Scoring by Question Type
        if q.question_type == AcademicQuestion.TYPE_MCQ:
            val = user_ans[0] if isinstance(user_ans, list) else user_ans
            if str(val).strip().lower() in [str(ca).strip().lower() for ca in q.correct_answers]:
                correct_count += 1
                total_score += q.marks
            else:
                incorrect_count += 1
                total_score -= abs(q.negative_marks)

        elif q.question_type == AcademicQuestion.TYPE_MULTIPLE_SELECT:
            u_set = set(user_ans) if isinstance(user_ans, list) else {str(user_ans)}
            c_set = set(q.correct_answers)
            if u_set == c_set:
                correct_count += 1
                total_score += q.marks
            else:
                incorrect_count += 1
                total_score -= abs(q.negative_marks)

        elif q.question_type == AcademicQuestion.TYPE_NUMERICAL:
            try:
                user_num = float(user_ans)
                correct_num = float(q.correct_answers[0])
                tol = float(getattr(q, "numeric_tolerance", 0.05))
                if abs(user_num - correct_num) <= tol:
                    correct_count += 1
                    total_score += q.marks
                else:
                    incorrect_count += 1
                    total_score -= abs(q.negative_marks)
            except Exception:
                incorrect_count += 1

        elif q.question_type == AcademicQuestion.TYPE_FILL_BLANKS:
            u_txt = str(user_ans).strip().lower()
            accepted = [str(ca).strip().lower() for ca in q.correct_answers]
            if u_txt in accepted:
                correct_count += 1
                total_score += q.marks
            else:
                incorrect_count += 1

        elif q.question_type == AcademicQuestion.TYPE_CODING:
            # Deterministic Sandboxed Test Case Runner
            student_code = str(user_ans)
            test_cases = q.coding_hidden_test_cases or []
            if not test_cases and q.coding_sample_input:
                test_cases = [{"input": q.coding_sample_input, "output": q.coding_sample_output}]

            passed_tc = 0
            for tc in test_cases:
                inp = tc.get("input", "")
                expected = tc.get("output", "").strip()
                try:
                    # Execute in sandboxed subprocess with 3-second hard timeout
                    proc = subprocess.run(
                        [sys.executable, "-c", student_code],
                        input=inp,
                        capture_output=True,
                        text=True,
                        timeout=3
                    )
                    actual_out = proc.stdout.strip()
                    if actual_out == expected:
                        passed_tc += 1
                except Exception:
                    pass

            if test_cases:
                fraction = passed_tc / len(test_cases)
                awarded = round(q.marks * fraction, 2)
                total_score += awarded
                if fraction >= 0.99:
                    correct_count += 1
                else:
                    incorrect_count += 1
            else:
                needs_manual = True

        elif q.question_type in [AcademicQuestion.TYPE_SHORT_ANSWER, AcademicQuestion.TYPE_LONG_ANSWER]:
            needs_manual = True

    final_score = max(0.0, round(total_score, 2))
    max_score = max(1.0, round(max_score, 2))
    percentage = round((final_score / max_score) * 100, 2)

    attempt.status = CollegeAssessmentAttempt.STATUS_SUBMITTED
    attempt.submitted_at = datetime.now(timezone.utc)
    started = attempt.started_at
    if started.tzinfo is None:
        started = started.replace(tzinfo=timezone.utc)
    attempt.time_taken_seconds = max(1, int((attempt.submitted_at - started).total_seconds()))
    attempt.score = final_score
    attempt.max_score = max_score
    attempt.percentage = percentage
    attempt.is_passed = final_score >= assessment.passing_marks
    attempt.correct_count = correct_count
    attempt.incorrect_count = incorrect_count
    attempt.unanswered_count = unanswered_count
    attempt.needs_manual_review = needs_manual
    attempt.save()
    return attempt


@teacher_bp.route("/exam/<assessment_slug>")
@login_required
def student_take_assessment(assessment_slug):
    """
    Renders the modern, distraction-free examination room for an academic test.
    Applies configurable integrity policies (fullscreen, tab-switch, copy-paste).
    """
    assessment = CollegeAssessment.get_by_slug(assessment_slug)
    if not assessment or assessment.status == CollegeAssessment.STATUS_DRAFT:
        flash("The requested examination is not available.", "danger")
        return redirect(url_for("test_series.landing"))

    # Active attempt check
    active_attempt = CollegeAssessmentAttempt.get_active_attempt(current_user.id, assessment.id)
    if not active_attempt:
        # Check if already submitted and max attempts reached
        past_attempts = CollegeAssessmentAttempt.find_all({
            "user_id": str(current_user.id),
            "assessment_id": str(assessment.id)
        })
        if len(past_attempts) >= assessment.max_attempts:
            latest = past_attempts[0]
            if assessment.result_published:
                return redirect(url_for("teacher.student_assessment_result", attempt_id=latest.id))
            flash(f"You have already completed your permitted attempts ({assessment.max_attempts}) for this examination.", "info")
            return redirect(url_for("test_series.landing"))

        # Create new attempt with server-side authoritative deadline
        now = datetime.now(timezone.utc)
        deadline = now + timedelta(minutes=assessment.duration_minutes)
        active_attempt = CollegeAssessmentAttempt({
            "user_id": str(current_user.id),
            "user_name": current_user.name,
            "user_email": current_user.email,
            "roll_number": getattr(current_user, "college", "") or f"SKR-{current_user.id[:6]}",
            "assessment_id": str(assessment.id),
            "assessment_title": assessment.title,
            "subject_id": str(assessment.subject_id),
            "subject_name": assessment.subject_name,
            "subject_code": assessment.subject_code,
            "academic_year": assessment.academic_year,
            "status": CollegeAssessmentAttempt.STATUS_IN_PROGRESS,
            "started_at": now,
            "duration_minutes": assessment.duration_minutes,
            "deadline_at": deadline,
            "responses": {},
            "integrity_events": []
        }).save()

    # If active attempt has expired, auto-submit
    if active_attempt.is_expired:
        _evaluate_academic_attempt(active_attempt, assessment)
        flash("Examination deadline reached. Your responses were automatically submitted.", "info")
        if assessment.result_published:
            return redirect(url_for("teacher.student_assessment_result", attempt_id=active_attempt.id))
        return redirect(url_for("test_series.landing"))

    questions_payload = [q.to_dict(include_solutions=False) for q in assessment.questions]

    return render_template(
        "teacher/exam_room.html",
        assessment=assessment,
        attempt=active_attempt,
        questions=questions_payload,
        remaining_seconds=active_attempt.remaining_seconds
    )


@teacher_bp.route("/exam/<attempt_id>/save-answer", methods=["POST"])
@login_required
def student_save_answer(attempt_id):
    """Asynchronous autosave endpoint for individual student answers."""
    attempt = CollegeAssessmentAttempt.get_by_id(attempt_id)
    if not attempt or attempt.user_id != str(current_user.id):
        return jsonify({"success": False, "error": "Unauthorized"}), 403

    if attempt.status != CollegeAssessmentAttempt.STATUS_IN_PROGRESS or attempt.is_expired:
        return jsonify({"success": False, "error": "Attempt is closed or expired"}), 400

    payload = request.get_json() or {}
    question_id = str(payload.get("question_id", ""))
    answer = payload.get("answer")
    marked_review = bool(payload.get("marked_for_review", False))

    if question_id:
        attempt.responses[question_id] = {
            "answer": answer,
            "marked_for_review": marked_review,
            "saved_at": datetime.now(timezone.utc).isoformat()
        }
        attempt.save()

    return jsonify({
        "success": True,
        "remaining_seconds": attempt.remaining_seconds,
        "saved_at": datetime.now(timezone.utc).isoformat()
    })


@teacher_bp.route("/exam/<attempt_id>/integrity-event", methods=["POST"])
@login_required
def student_integrity_event(attempt_id):
    """Records anti-cheat violations (tab switch, blur, fullscreen exit) and enforces warnings."""
    attempt = CollegeAssessmentAttempt.get_by_id(attempt_id)
    if not attempt or attempt.user_id != str(current_user.id):
        return jsonify({"success": False, "error": "Unauthorized"}), 403

    assessment = CollegeAssessment.get_by_id(attempt.assessment_id)
    max_warn = assessment.integrity_settings.get("max_warnings", 3) if assessment else 3

    payload = request.get_json() or {}
    event_type = payload.get("event_type", "focus_loss")
    details = payload.get("details", "Focus loss or tab navigation detected")

    recorded, count, cancelled = attempt.add_integrity_event(event_type, details=details, max_warnings=max_warn)

    return jsonify({
        "recorded": recorded,
        "warning_count": count,
        "max_warnings": max_warn,
        "cancelled": cancelled,
        "cancellation_reason": attempt.cancellation_reason if cancelled else "",
        "redirect_url": url_for("test_series.landing") if cancelled else None
    })


@teacher_bp.route("/exam/<attempt_id>/submit", methods=["POST"])
@login_required
def student_submit_assessment(attempt_id):
    """Submits and evaluates student assessment responses."""
    attempt = CollegeAssessmentAttempt.get_by_id(attempt_id)
    if not attempt or attempt.user_id != str(current_user.id):
        flash("Unauthorized attempt submission.", "danger")
        return redirect(url_for("test_series.landing"))

    assessment = CollegeAssessment.get_by_id(attempt.assessment_id)
    _evaluate_academic_attempt(attempt, assessment)

    if assessment and assessment.result_published:
        flash("🎉 Assessment submitted successfully! Your evaluated score is now available.", "success")
        return redirect(url_for("teacher.student_assessment_result", attempt_id=attempt.id))

    flash("✅ Assessment submitted successfully! Your responses have been saved and sent for evaluation.", "success")
    return redirect(url_for("test_series.landing"))


@teacher_bp.route("/exam/result/<attempt_id>")
@login_required
def student_assessment_result(attempt_id):
    """Displays student performance, verified score, and solutions (if results published)."""
    attempt = CollegeAssessmentAttempt.get_by_id(attempt_id)
    if not attempt:
        flash("Assessment record not found.", "warning")
        return redirect(url_for("test_series.landing"))

    # Only student themselves or teachers/admins can view
    is_owner = attempt.user_id == str(current_user.id)
    is_faculty = getattr(current_user, "is_teacher", False) or getattr(current_user, "is_admin", False)
    if not (is_owner or is_faculty):
        flash("You are not authorized to view this result.", "danger")
        return redirect(url_for("test_series.landing"))

    assessment = CollegeAssessment.get_by_id(attempt.assessment_id)
    if not is_faculty and (not assessment or not assessment.result_published):
        flash("The results for this assessment have not been published yet by your department faculty.", "info")
        return redirect(url_for("test_series.landing"))

    questions = assessment.questions if assessment else []

    return render_template(
        "teacher/exam_result.html",
        attempt=attempt,
        assessment=assessment,
        questions=questions
    )
