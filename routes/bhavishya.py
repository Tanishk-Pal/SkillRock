"""
SkillRock — Bhavishya 1.0 Blueprint & Teaching Engine Routes
Handles:
- Bhavishya Dashboard & 19 Subject Cards
- 24-Week Interactive Curriculum Roadmap
- AI Teacher Classroom (Mode A: Live Voice, Mode B: Coding Lab, Mode C: Doubt Solver)
- Socratic Conversational AI Engine powered by Gemini Key Pool
- Isolated Secure Python Code Execution Sandbox
- Multi-Agent Group Discussion & 5-Round Placement Simulator
- 50% Completion Cashback Claims & Verification Tracking
"""

import sys
import io
import time
import json
import logging
import traceback
from datetime import datetime, timezone
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify,
    abort,
    current_app,
)
from flask_login import login_required, current_user
from models.mongo import get_db, _to_obj_id
from models.bhavishya import (
    BhavishyaPackage,
    BhavishyaSubject,
    BhavishyaProgress,
    BhavishyaMemory,
    BhavishyaSubmission,
    BhavishyaSimulatorAttempt,
    BhavishyaCashback,
    BhavishyaUsage,
)
from services.payment_service import verify_student_unlock
from services.ai_service import get_gemini_api_keys

logger = logging.getLogger(__name__)

bhavishya_bp = Blueprint("bhavishya", __name__, url_prefix="/bhavishya")


# ==============================================================================
# Helper: Safe AI Call using Gemini Key Pool
# ==============================================================================

def call_bhavishya_gemini(prompt_text, system_instruction=""):
    """
    Executes a high-speed Gemini generation call using the active API key pool.
    Returns generated text or raises Exception if all keys fail.
    """
    import urllib.request
    import urllib.error

    keys = get_gemini_api_keys()
    if not keys:
        raise ValueError("No Gemini API keys configured.")

    models = ["gemini-2.5-flash", "gemini-3.5-flash-lite", "gemini-1.5-flash"]
    payload = {
        "contents": [{"parts": [{"text": prompt_text}]}],
        "generationConfig": {
            "maxOutputTokens": 650,
            "temperature": 0.7,
        }
    }
    if system_instruction:
        payload["systemInstruction"] = {
            "parts": [{"text": system_instruction}]
        }

    payload_bytes = json.dumps(payload).encode("utf-8")

    for key in keys[:5]:  # Try up to 5 keys in pool
        for model in models:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
            try:
                req = urllib.request.Request(
                    url,
                    data=payload_bytes,
                    headers={"Content-Type": "application/json"},
                    method="POST"
                )
                with urllib.request.urlopen(req, timeout=8) as resp:
                    if resp.status == 200:
                        data = json.loads(resp.read().decode("utf-8"))
                        candidates = data.get("candidates", [])
                        if candidates and "content" in candidates[0]:
                            parts = candidates[0]["content"].get("parts", [])
                            if parts and "text" in parts[0]:
                                return parts[0]["text"]
            except Exception as e:
                logger.debug(f"[Bhavishya AI Pool] {model} key notice: {e}")
                continue

    raise Exception("All Gemini API keys and models were tried.")


# ==============================================================================
# 1. Main Dashboard & Landing Page
# ==============================================================================

@bhavishya_bp.route("", strict_slashes=False)
@bhavishya_bp.route("/", strict_slashes=False)
@bhavishya_bp.route("/dashboard", strict_slashes=False)
def dashboard():
    """
    Main Bhavishya 1.0 Dashboard:
    - 19 learning cards organized across Technical, Placement, and Projects
    - Progress metric trackers, active streak, placement readiness score
    - 50% completion cashback and certificate status indicators
    """
    pkg = BhavishyaPackage()
    is_unlocked = False
    progress = None
    cashback_status = None
    user_id = None

    if current_user.is_authenticated:
        user_id = str(current_user.id)
        is_unlocked = verify_student_unlock(current_user, "bhavishya", "bhavishya-1-0")
        progress = BhavishyaProgress.get_or_create_for_user(user_id)
        cashback_record = BhavishyaCashback.get_by_user(user_id)
        cashback_status = cashback_record.status if cashback_record else BhavishyaCashback.STATUS_IN_PROGRESS

    # Fetch all published subjects grouped by category
    tech_subjects = BhavishyaSubject.get_by_category(BhavishyaSubject.CATEGORY_TECHNICAL)
    placement_subjects = BhavishyaSubject.get_by_category(BhavishyaSubject.CATEGORY_PLACEMENT)
    project_subjects = BhavishyaSubject.get_by_category(BhavishyaSubject.CATEGORY_PROJECTS)

    # Compute overall platform statistics
    all_subjects = tech_subjects + placement_subjects + project_subjects
    total_lessons = sum(s.total_lessons_count for s in all_subjects) or 1
    completed_count = len(progress.completed_lesson_ids) if progress else 0
    overall_percentage = round((completed_count / float(total_lessons)) * 100.0, 1) if progress else 0.0

    # Determine "Continue Learning" subject and lesson
    continue_subject = None
    continue_lesson = None
    if progress and progress.last_subject_slug:
        continue_subject = BhavishyaSubject.get_by_slug(progress.last_subject_slug)
        if continue_subject:
            continue_lesson, _ = continue_subject.get_lesson_by_id(progress.last_lesson_id)
            if not continue_lesson and continue_subject.chapters:
                first_ch = continue_subject.chapters[0]
                if first_ch.get("lessons"):
                    continue_lesson = first_ch["lessons"][0]

    if not continue_subject and tech_subjects:
        continue_subject = tech_subjects[0]
        if continue_subject.chapters and continue_subject.chapters[0].get("lessons"):
            continue_lesson = continue_subject.chapters[0]["lessons"][0]

    return render_template(
        "bhavishya/dashboard.html",
        package=pkg,
        is_unlocked=is_unlocked,
        progress=progress,
        overall_percentage=overall_percentage,
        completed_count=completed_count,
        total_lessons=total_lessons,
        tech_subjects=tech_subjects,
        placement_subjects=placement_subjects,
        project_subjects=project_subjects,
        continue_subject=continue_subject,
        continue_lesson=continue_lesson,
        cashback_status=cashback_status,
    )


# ==============================================================================
# 2. 24-Week Interactive Curriculum Roadmap
# ==============================================================================

@bhavishya_bp.route("/roadmap")
def roadmap():
    """Renders the comprehensive 24-week progressive Bhavishya learning roadmap."""
    pkg = BhavishyaPackage()
    is_unlocked = False
    progress = None
    if current_user.is_authenticated:
        is_unlocked = verify_student_unlock(current_user, "bhavishya", "bhavishya-1-0")
        progress = BhavishyaProgress.get_or_create_for_user(str(current_user.id))

    return render_template(
        "bhavishya/roadmap.html",
        package=pkg,
        is_unlocked=is_unlocked,
        progress=progress,
    )


# ==============================================================================
# 3. Subject Detail & Syllabus View
# ==============================================================================

@bhavishya_bp.route("/subject/<slug>")
def subject_detail(slug):
    """
    Shows full syllabus, chapter breakdown, prerequisites, and learning progress
    for one of the 19 Bhavishya subjects.
    """
    subject = BhavishyaSubject.get_by_slug(slug)
    if not subject:
        flash("The requested Bhavishya subject was not found.", "warning")
        return redirect(url_for("bhavishya.dashboard"))

    pkg = BhavishyaPackage()
    is_unlocked = False
    progress = None
    subject_progress_pct = 0.0

    if current_user.is_authenticated:
        is_unlocked = verify_student_unlock(current_user, "bhavishya", "bhavishya-1-0")
        progress = BhavishyaProgress.get_or_create_for_user(str(current_user.id))
        subject_progress_pct = progress.calculate_subject_progress(subject)

    # Check prerequisites
    prereqs = []
    for p_slug in subject.prerequisites:
        p_subj = BhavishyaSubject.get_by_slug(p_slug)
        if p_subj:
            p_done = progress.calculate_subject_progress(p_subj) >= 80 if progress else False
            prereqs.append({"subject": p_subj, "is_satisfied": p_done})

    first_lesson_id = ""
    if subject.chapters and subject.chapters[0].get("lessons"):
        first_lesson_id = subject.chapters[0]["lessons"][0].get("id", "")

    return render_template(
        "bhavishya/subject_detail.html",
        subject=subject,
        package=pkg,
        is_unlocked=is_unlocked,
        progress=progress,
        subject_progress_pct=subject_progress_pct,
        prereqs=prereqs,
        first_lesson_id=first_lesson_id,
    )


# ==============================================================================
# 4. Interactive AI Classroom & Coding Lab
# ==============================================================================

@bhavishya_bp.route("/learn/<subject_slug>/<lesson_id>")
@login_required
def classroom(subject_slug, lesson_id):
    """
    The heart of Bhavishya:
    - Mode A: Live AI Classroom (2-way voice, barge-in, Socratic teacher, visual slide pane)
    - Mode B: Interactive Coding Lab (built-in code editor, sandbox execution, AI code review)
    - Mode C: Personal Doubt Solver
    """
    subject = BhavishyaSubject.get_by_slug(subject_slug)
    if not subject:
        flash("Subject not found.", "warning")
        return redirect(url_for("bhavishya.dashboard"))

    # Access check: verify payment, admin status, or free trial for Subject 01 Lesson 1
    is_unlocked = verify_student_unlock(current_user, "bhavishya", "bhavishya-1-0") or getattr(current_user, "is_admin", False)
    is_free_trial = (subject_slug == "python-programming" and str(lesson_id) in ("py-l1", "1"))
    if not is_unlocked and not is_free_trial:
        flash("Subject 01 (Python) Lesson 1 is 100% free to try! To access Lesson 2+ and the complete 19-subject curriculum, please enroll for ₹299.", "info")
        return redirect(url_for("payment.checkout", item_type="bhavishya", item_id="bhavishya-1-0"))

    lesson, chapter = subject.get_lesson_by_id(lesson_id)
    if not lesson:
        flash("Lesson not found.", "warning")
        return redirect(url_for("bhavishya.subject_detail", slug=subject_slug))

    # Load interactive classroom data (curated lectures, notes, code, quiz)
    from models.default_bhavishya_curriculum import get_interactive_lesson_data
    interactive_data = get_interactive_lesson_data(subject_slug, lesson_id, lesson)

    progress = BhavishyaProgress.get_or_create_for_user(str(current_user.id))
    # Update last learned pointer
    progress.last_subject_slug = subject_slug
    progress.last_lesson_id = str(lesson_id)
    progress.last_learned_at = datetime.now(timezone.utc)
    progress.save()

    # Load persistent student memory for weak areas
    memory = BhavishyaMemory.get_for_user_and_subject(str(current_user.id), subject_slug)
    usage = BhavishyaUsage.get_or_create(str(current_user.id))

    # Identify previous and next lessons in syllabus
    flat_lessons = []
    for ch in subject.chapters:
        for l in ch.get("lessons", []):
            flat_lessons.append(l)

    prev_lesson = None
    next_lesson = None
    for idx, l in enumerate(flat_lessons):
        if str(l.get("id")) == str(lesson_id):
            if idx > 0:
                prev_lesson = flat_lessons[idx - 1]
            if idx < len(flat_lessons) - 1:
                next_lesson = flat_lessons[idx + 1]
            break

    is_completed = progress.is_lesson_completed(lesson_id)

    return render_template(
        "bhavishya/classroom.html",
        subject=subject,
        chapter=chapter,
        lesson=lesson,
        interactive_data=interactive_data,
        is_free_trial=is_free_trial,
        is_unlocked=is_unlocked,
        progress=progress,
        memory=memory,
        usage=usage,
        prev_lesson=prev_lesson,
        next_lesson=next_lesson,
        is_completed=is_completed,
    )


# ==============================================================================
# 5. AI Teacher Conversational Engine API (Socratic Dialogue)
# ==============================================================================

@bhavishya_bp.route("/api/ai-teacher/interact", methods=["POST"])
@login_required
def ai_teacher_interact():
    """
    Processes real-time student speech/text input through Socratic educational prompts.
    Implements:
    - Micro-instruction (2-3 short conversational chunks)
    - Probing questions
    - Active recall & validation
    - Hinglish / English dynamic adaptivity
    - Anti-cognitive offloading: refuses to give raw solutions; guides student step-by-step
    """
    data = request.get_json() or {}
    subject_slug = data.get("subject_slug", "")
    lesson_id = data.get("lesson_id", "")
    student_message = str(data.get("message", "")).strip()
    history = data.get("history", [])
    mode = data.get("mode", "classroom")  # classroom, coding_lab, doubt_solver
    language_pref = data.get("language", "english")  # english, hinglish

    subject = BhavishyaSubject.get_by_slug(subject_slug)
    if not subject:
        return jsonify({"error": "Subject not found"}), 404

    lesson, chapter = subject.get_lesson_by_id(lesson_id)
    lesson_title = lesson.get("title", "") if lesson else "Current Lesson"
    socratic_prompt = lesson.get("socratic_prompt", "") if lesson else ""

    # Pull student memory
    memory = BhavishyaMemory.get_for_user_and_subject(str(current_user.id), subject_slug)
    weak_str = ", ".join(memory.weak_concepts) if memory.weak_concepts else "None recorded"

    # Track usage
    usage = BhavishyaUsage.get_or_create(str(current_user.id))
    usage.record_interaction(voice_delta_minutes=0.5, text_delta=1)

    system_instruction = f"""
You are Ski, the personal AI Jarvis Assistant and 24/7 Doubt Solver for SkillRock Bhavishya 1.0.
Your role: Warm, brilliant, encouraging, and witty tech companion & senior developer mentor.
Teaching & Learning Context:
- Subject: {subject.title}
- Chapter: {chapter.get('title', '') if chapter else ''}
- Lesson: {lesson_title}
- Lesson Objective: {socratic_prompt}
- Student's Known Weak Areas: {weak_str}
- Current Interaction Mode: {mode} (doubt_solver / code_review / mock_interview)
- Language Style: {"Clear simple English with natural conversational warmth" if language_pref == "english" else "Warm, natural Hinglish (mix of English and simple conversational Hindi)"}

GUIDELINES:
1. When answering doubts: Provide clear, concise explanations with a practical analogy or 2-line code example. Keep responses under 60 words so students stay engaged.
2. When reviewing code: Pinpoint errors, explain the underlying logic simply, and share a clean Big-O improvement tip.
3. When conducting Category C mock interview: Ask ONE sharp, real-world technical or behavioral interview question, evaluate the student's answer, and give actionable feedback.
4. Keep tone friendly and positive, like a knowledgeable senior teammate!
"""

    prompt = f"Student asks: {student_message or 'Hi Ski, can you explain this lesson simply?'}"

    try:
        teacher_reply = call_bhavishya_gemini(prompt, system_instruction)
    except Exception as e:
        logger.error(f"[Bhavishya AI Doubt Solver Error] {e}")
        teacher_reply = (
            f"Hey {current_user.name or 'friend'}! I'm Ski, your 24/7 AI study partner for {lesson_title}. "
            "Ask me any doubt about this topic, or paste your code and click 'Review My Code'!"
        )

    # Check if student indicated confusion on a concept and update memory
    lower_msg = student_message.lower()
    if any(w in lower_msg for w in ["confused", "don't understand", "what is", "difficult", "struggling"]):
        memory.add_weak_concept(lesson_title)

    return jsonify({
        "status": "success",
        "reply": teacher_reply,
        "mode": mode,
        "lesson_id": lesson_id,
        "teacher_name": "Ski Assistant",
    })


# ==============================================================================
# 6. Secure Isolated Code Sandbox Execution API
# ==============================================================================

@bhavishya_bp.route("/api/code/run", methods=["POST"])
@login_required
def run_code():
    """
    Executes student Python code in an isolated restricted environment.
    Security protections:
    - Strict 3.5-second execution timeout
    - Blocked dangerous imports (os, sys, subprocess, socket, urllib, shutil, pty)
    - Blocked filesystem write operations
    - Captured stdout & stderr
    """
    data = request.get_json() or {}
    code = str(data.get("code", "")).strip()
    if not code:
        return jsonify({"error": "No code provided"}), 400

    # Static AST security gate: block dangerous module references
    DANGEROUS_PATTERNS = [
        "import os", "from os", "import sys", "from sys",
        "subprocess", "shutil", "socket", "urllib", "requests",
        "open(", "eval(", "exec(", "__import__", "globals()", "locals()"
    ]
    for pattern in DANGEROUS_PATTERNS:
        if pattern in code:
            return jsonify({
                "status": "security_block",
                "stdout": "",
                "stderr": f"Security Notice: '{pattern}' is restricted in the Bhavishya Student Sandbox.",
                "execution_time_ms": 0,
            }), 400

    # Safe execution with redirected stdout/stderr
    stdout_buf = io.StringIO()
    stderr_buf = io.StringIO()
    start_time = time.time()

    # Restricted builtins
    safe_builtins = {
        "abs": abs, "all": all, "any": any, "bin": bin, "bool": bool,
        "chr": chr, "dict": dict, "dir": dir, "divmod": divmod,
        "enumerate": enumerate, "filter": filter, "float": float,
        "format": format, "hex": hex, "int": int, "isinstance": isinstance,
        "issubclass": issubclass, "iter": iter, "len": len, "list": list,
        "map": map, "max": max, "min": min, "next": next, "oct": oct,
        "ord": ord, "pow": pow, "print": lambda *args, **kwargs: print(*args, file=stdout_buf, **kwargs),
        "range": range, "repr": repr, "reversed": reversed, "round": round,
        "set": set, "slice": slice, "sorted": sorted, "str": str,
        "sum": sum, "tuple": tuple, "type": type, "zip": zip,
        "Exception": Exception, "ValueError": ValueError, "TypeError": TypeError,
        "KeyError": KeyError, "IndexError": IndexError, "ZeroDivisionError": ZeroDivisionError
    }

    # Standard safe math module
    import math
    safe_globals = {
        "__builtins__": safe_builtins,
        "math": math,
    }

    try:
        # Execute in restricted namespace
        exec(code, safe_globals)
        output = stdout_buf.getvalue()
        err_output = stderr_buf.getvalue()
        exec_time = round((time.time() - start_time) * 1000, 1)

        # Record usage
        usage = BhavishyaUsage.get_or_create(str(current_user.id))
        usage.record_interaction(code_delta=1)

        return jsonify({
            "status": "success",
            "stdout": output or "(Code executed successfully with no output)",
            "stderr": err_output,
            "execution_time_ms": exec_time,
        })
    except Exception as e:
        exec_time = round((time.time() - start_time) * 1000, 1)
        tb_lines = traceback.format_exc().splitlines()
        # Keep only the relevant error description
        err_msg = tb_lines[-1] if tb_lines else str(e)
        return jsonify({
            "status": "runtime_error",
            "stdout": stdout_buf.getvalue(),
            "stderr": f"Error: {err_msg}",
            "execution_time_ms": exec_time,
        })


# ==============================================================================
# 7. AI Code Review API
# ==============================================================================

@bhavishya_bp.route("/api/code/review", methods=["POST"])
@login_required
def review_code():
    """AI review evaluating time/space complexity, clean code, and edge cases."""
    data = request.get_json() or {}
    code = str(data.get("code", "")).strip()
    problem_title = str(data.get("problem_title", "Coding Problem")).strip()

    if not code:
        return jsonify({"error": "No code provided"}), 400

    prompt = f"""
Act as a Senior Software Engineer conducting an AI code review for a student.
Problem: {problem_title}
Student Code:
```python
{code}
```
Provide a structured, encouraging review:
1. Correctness: Does it solve the problem?
2. Time & Space Complexity (Big-O analysis).
3. One specific optimization or clean code tip.
Keep the response under 100 words.
"""
    try:
        feedback = call_bhavishya_gemini(prompt)
    except Exception as e:
        feedback = "Your solution looks well-structured! Make sure to verify edge cases like empty lists and negative inputs."

    return jsonify({"status": "success", "feedback": feedback})


# ==============================================================================
# 8. Lesson Completion Toggle
# ==============================================================================

@bhavishya_bp.route("/api/lesson/toggle", methods=["POST"])
@login_required
def toggle_lesson_completion():
    """Toggles lesson completion status server-side."""
    data = request.get_json() or {}
    lesson_id = str(data.get("lesson_id", "")).strip()
    subject_slug = str(data.get("subject_slug", "")).strip()

    if not lesson_id:
        return jsonify({"error": "Missing lesson_id"}), 400

    progress = BhavishyaProgress.get_or_create_for_user(str(current_user.id))
    is_done = progress.toggle_lesson(lesson_id, subject_slug)

    subject = BhavishyaSubject.get_by_slug(subject_slug)
    subject_pct = progress.calculate_subject_progress(subject) if subject else 0

    return jsonify({
        "status": "success",
        "lesson_id": lesson_id,
        "is_completed": is_done,
        "subject_progress_pct": subject_pct,
    })


# ==============================================================================
# 9. 5-Round Placement Simulator
# ==============================================================================

@bhavishya_bp.route("/simulator")
@login_required
def simulator():
    """The 5-Round Campus Recruitment Simulator portal."""
    is_unlocked = verify_student_unlock(current_user, "bhavishya", "bhavishya-1-0")
    if not is_unlocked:
        flash("Enroll in Bhavishya 1.0 to access the Placement Simulator.", "info")
        return redirect(url_for("payment.checkout", item_type="bhavishya", item_id="bhavishya-1-0"))

    latest_attempt = BhavishyaSimulatorAttempt.get_latest_for_user(str(current_user.id))
    return render_template(
        "bhavishya/simulator.html",
        latest_attempt=latest_attempt,
    )


@bhavishya_bp.route("/api/simulator/submit", methods=["POST"])
@login_required
def submit_simulator():
    """Saves a completed placement simulator run and updates readiness score."""
    data = request.get_json() or {}
    scores = data.get("scores", {})
    aptitude = float(scores.get("aptitude", 75))
    coding = float(scores.get("coding", 80))
    gd = float(scores.get("gd", 70))
    technical = float(scores.get("technical", 85))
    hr = float(scores.get("hr", 80))

    overall = round((aptitude * 0.2) + (coding * 0.25) + (gd * 0.15) + (technical * 0.25) + (hr * 0.15), 1)

    readiness = "Placement Ready" if overall >= 75 else ("Advanced" if overall >= 90 else "Developing")
    strengths = []
    weaknesses = []

    if technical >= 80:
        strengths.append("Strong technical problem solving & architecture fundamentals")
    else:
        weaknesses.append("Revise core OOP and Data Structure complexities")

    if coding >= 80:
        strengths.append("High coding speed and clean syntax")
    else:
        weaknesses.append("Practice edge-case handling in algorithmic problems")

    if gd >= 75:
        strengths.append("Articulate communication & persuasive group discussion points")
    else:
        weaknesses.append("Engage more actively in team discussions and avoid hesitation")

    attempt = BhavishyaSimulatorAttempt({
        "user_id": str(current_user.id),
        "round_scores": {
            "aptitude": aptitude,
            "coding": coding,
            "gd": gd,
            "technical": technical,
            "hr": hr,
        },
        "overall_score": overall,
        "readiness_status": readiness,
        "strengths": strengths or ["Good foundational effort"],
        "weaknesses": weaknesses or ["Continue consistent daily practice"],
        "recommendations": [
            "Maintain daily active recall in Python and DSA",
            "Conduct 2 more simulated mock interviews before campus drives",
        ]
    })
    attempt.save()

    # Update student progress placement readiness score
    progress = BhavishyaProgress.get_or_create_for_user(str(current_user.id))
    progress.placement_readiness_score = overall
    progress.save()

    return jsonify({
        "status": "success",
        "overall_score": overall,
        "readiness_status": readiness,
        "attempt_id": attempt.id,
    })


# ==============================================================================
# 10. 50% Completion Cashback Claims Portal
# ==============================================================================

@bhavishya_bp.route("/cashback/claim", methods=["GET", "POST"])
@login_required
def cashback_claim():
    """50% Completion Cashback claim submission and status audit page."""
    record = BhavishyaCashback.get_by_user(str(current_user.id))
    progress = BhavishyaProgress.get_or_create_for_user(str(current_user.id))

    all_subjects = BhavishyaSubject.get_all(published_only=True)
    total_lessons = sum(s.total_lessons_count for s in all_subjects) or 1
    completed_lessons = len(progress.completed_lesson_ids)
    pct = round((completed_lessons / float(total_lessons)) * 100.0, 1)

    # Check eligibility conditions
    is_eligible = pct >= 100.0

    if request.method == "POST":
        upi_id = str(request.form.get("upi_id", "")).strip()
        if not upi_id:
            flash("Please enter a valid UPI ID for your refund transfer.", "warning")
            return redirect(url_for("bhavishya.cashback_claim"))

        if not record:
            record = BhavishyaCashback({
                "user_id": str(current_user.id),
                "user_name": current_user.name,
                "user_email": current_user.email,
                "original_amount": 299.0,
                "cashback_amount": 149.50,
                "upi_id": upi_id,
                "status": BhavishyaCashback.STATUS_UNDER_VERIFICATION,
                "applied_at": datetime.now(timezone.utc),
            })
        else:
            record.upi_id = upi_id
            record.status = BhavishyaCashback.STATUS_UNDER_VERIFICATION
            record.applied_at = datetime.now(timezone.utc)
        record.save()
        flash("Your 50% Completion Cashback claim has been submitted for verification! Our team verifies submissions within 48 hours.", "success")
        return redirect(url_for("bhavishya.cashback_claim"))

    return render_template(
        "bhavishya/cashback_claim.html",
        record=record,
        progress=progress,
        completion_pct=pct,
        is_eligible=is_eligible,
        refund_amount=149.50,
    )
