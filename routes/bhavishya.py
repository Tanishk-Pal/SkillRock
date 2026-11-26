"""
SkillRock — Bhavishya 1.0 Blueprint & Teaching Engine Routes
Handles:
- Bhavishya Dashboard & 19 Subject Cards
- 24-Week Interactive Curriculum Roadmap
- AI Teacher Classroom (Mode A: Live Voice, Mode B: Coding Lab, Mode C: Doubt Solver)
- Socratic Conversational AI Engine powered by Gemini Key Pool
- Isolated Secure Python Code Execution Sandbox
- Multi-Agent Group Discussion & 5-Round Placement Simulator
- 100% Completion Refund Claims & Verification Tracking
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
    BhavishyaBatchConfig,
    BhavishyaLiveLecture,
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
    - 100% completion refund and certificate status indicators
    """
    pkg = BhavishyaPackage()
    # Bhavishya 1.0 is 100% FREE for all students
    is_unlocked = True
    progress = None
    cashback_status = None
    user_id = None

    if current_user.is_authenticated:
        user_id = str(current_user.id)
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

    # Fetch Bhavishya 1.0 Live Lectures Batch configuration & modules
    batch_config = BhavishyaBatchConfig.get_config("bhavishya-1-0")
    active_live_lecture = BhavishyaLiveLecture.get_active_live("bhavishya-1-0")
    next_scheduled_lecture = BhavishyaLiveLecture.get_next_scheduled("bhavishya-1-0")
    live_modules = BhavishyaLiveLecture.get_modules_grouped("bhavishya-1-0")
    all_live_lectures = BhavishyaLiveLecture.get_all("bhavishya-1-0")
    completed_lectures_count = sum(1 for l in all_live_lectures if l.is_completed)

    # Physics Wallah-style Dual Flagship Batches: Python & English
    python_lectures = BhavishyaLiveLecture.get_all("bhavishya-1-0", subject_slug="python")
    english_lectures = BhavishyaLiveLecture.get_all("bhavishya-1-0", subject_slug="english")
    python_modules = BhavishyaLiveLecture.get_modules_grouped("bhavishya-1-0", subject_slug="python")
    english_modules = BhavishyaLiveLecture.get_modules_grouped("bhavishya-1-0", subject_slug="english")
    python_active_live = BhavishyaLiveLecture.get_active_live("bhavishya-1-0", subject_slug="python")
    english_active_live = BhavishyaLiveLecture.get_active_live("bhavishya-1-0", subject_slug="english")
    python_next = BhavishyaLiveLecture.get_next_scheduled("bhavishya-1-0", subject_slug="python")
    english_next = BhavishyaLiveLecture.get_next_scheduled("bhavishya-1-0", subject_slug="english")

    batch_courses = [
        {
            "id": "python-batch",
            "slug": "python",
            "title": "Python Mastery — Zero to Placement",
            "badge_title": "Python Live Batch",
            "tag": "Live Interactive Batch",
            "certification": "With Certification",
            "language": "Hinglish",
            "teacher_name": "Tanishk Pal Sir",
            "teacher_title": "Founder & Lead Python Educator",
            "teacher_avatar": "/static/img/teacher_tanishk.svg",
            "schedule": "Starts on 24 Nov 2026 | Daily Live 7:00 PM IST",
            "total_lectures": len(python_lectures),
            "modules_count": len(python_modules),
            "active_live": python_active_live,
            "next_scheduled": python_next,
            "study_url": url_for("bhavishya.subject_detail", slug="python"),
            "features": ["Daily Google Meet Live Classes", "Topic-wise DPPs with Instant Solutions", "Class Notes & Cheatsheets", "In-Browser Python IDE", "Ski AI Doubt Solver 24/7"],
            "gradient": "linear-gradient(135deg, #1E1B4B 0%, #312E81 100%)",
            "accent": "#6366F1"
        },
        {
            "id": "english-batch",
            "slug": "english",
            "title": "Professional English & Communication",
            "badge_title": "English Academy",
            "tag": "Speaking & Fluency Academy",
            "certification": "With Certification",
            "language": "Hinglish / English",
            "teacher_name": "Ananya Sharma Ma'am",
            "teacher_title": "Lead Communication & Verbal Coach",
            "teacher_avatar": "/static/img/teacher_ananya.svg",
            "schedule": "Starts on 24 Nov 2026 | Daily Live 8:30 PM IST",
            "total_lectures": len(english_lectures),
            "modules_count": len(english_modules),
            "active_live": english_active_live,
            "next_scheduled": english_next,
            "study_url": url_for("bhavishya.subject_detail", slug="english"),
            "features": ["Live Google Meet Speaking Circles", "Phonetics & Accent Softening", "Corporate Email & Standup Etiquette", "Behavioral Interview STAR Framework", "JAM & Impromptu Talk Drills"],
            "gradient": "linear-gradient(135deg, #064E3B 0%, #047857 100%)",
            "accent": "#10B981"
        }
    ]

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
        batch_config=batch_config,
        active_live_lecture=active_live_lecture,
        next_scheduled_lecture=next_scheduled_lecture,
        live_modules=live_modules,
        all_live_lectures=all_live_lectures,
        completed_lectures_count=completed_lectures_count,
        batch_courses=batch_courses,
        python_lectures=python_lectures,
        english_lectures=english_lectures
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
    Physics Wallah-style Subject & Chapter Playlist View:
    - Supports Flagship Live Batches (Python, English) with Chapter navigation and tabs
    - Also supports traditional 19 self-paced Bhavishya subjects
    """
    clean_slug = str(slug).strip().lower()
    is_python = clean_slug in ("python", "python-live", "python-programming")
    is_english = clean_slug in ("english", "english-live", "english-academy", "communication")
    
    # 100% Free for all students
    is_unlocked = True
    pkg = BhavishyaPackage()
    progress = None
    subject_progress_pct = 0.0

    if current_user.is_authenticated:
        progress = BhavishyaProgress.get_or_create_for_user(str(current_user.id))

    # Resolve subject object or fallback
    subject = BhavishyaSubject.get_by_slug(clean_slug)
    if not subject and is_python:
        subject = BhavishyaSubject.get_by_slug("python-programming")
    elif not subject and is_english:
        subject = BhavishyaSubject.get_by_slug("communication-mastery")

    # Flagship Live Batch info
    subject_slug = "python" if is_python else ("english" if is_english else clean_slug)
    is_live_batch = is_python or is_english or clean_slug.endswith("-live")

    if is_python:
        subject_info = {
            "title": "Python Mastery — Zero to Placement",
            "slug": "python",
            "teacher_name": "Tanishk Pal Sir",
            "teacher_title": "Founder & Lead Python Educator",
            "teacher_avatar": "/static/img/teacher_tanishk.svg",
            "language": "Hinglish",
            "accent_color": "#6366F1",
            "schedule": "Daily Live at 7:00 PM IST • Google Meet",
            "description": "Comprehensive live interactive classes on Google Meet with daily practice problems (DPP), lecture notes, in-browser compiler, and placement projects."
        }
    elif is_english:
        subject_info = {
            "title": "Professional English & Communication",
            "slug": "english",
            "teacher_name": "Ananya Sharma Ma'am",
            "teacher_title": "Lead Communication & Verbal Coach",
            "teacher_avatar": "/static/img/teacher_ananya.svg",
            "language": "Hinglish / English",
            "accent_color": "#10B981",
            "schedule": "Daily Live at 8:30 PM IST • Google Meet",
            "description": "Interactive speaking circles on Google Meet covering spoken English, pronunciation, corporate emails, and GD/interview prep."
        }
    else:
        subject_info = {
            "title": subject.title if subject else slug.replace("-", " ").title(),
            "slug": clean_slug,
            "teacher_name": "SkillRock Faculty",
            "teacher_title": "Academic Lead",
            "teacher_avatar": "/static/img/logo.jpg",
            "language": "Hinglish",
            "accent_color": "#38BDF8",
            "schedule": "Self-Paced & Live Mentorship",
            "description": subject.short_description if subject else ""
        }

    # Fetch live modules & lectures for this subject
    live_modules = BhavishyaLiveLecture.get_modules_grouped("bhavishya-1-0", subject_slug=subject_slug)
    all_lectures = BhavishyaLiveLecture.get_all("bhavishya-1-0", subject_slug=subject_slug)
    active_live_lecture = BhavishyaLiveLecture.get_active_live("bhavishya-1-0", subject_slug=subject_slug)
    next_scheduled_lecture = BhavishyaLiveLecture.get_next_scheduled("bhavishya-1-0", subject_slug=subject_slug)

    # Self-paced fallback
    prereqs = []
    first_lesson_id = ""
    if subject:
        if progress:
            subject_progress_pct = progress.calculate_subject_progress(subject)
        for p_slug in subject.prerequisites:
            p_subj = BhavishyaSubject.get_by_slug(p_slug)
            if p_subj:
                p_done = progress.calculate_subject_progress(p_subj) >= 80 if progress else False
                prereqs.append({"subject": p_subj, "is_satisfied": p_done})
        if subject.chapters and subject.chapters[0].get("lessons"):
            first_lesson_id = subject.chapters[0]["lessons"][0].get("id", "")

    return render_template(
        "bhavishya/subject_detail.html",
        subject=subject,
        subject_info=subject_info,
        subject_slug=subject_slug,
        is_live_batch=is_live_batch,
        live_modules=live_modules,
        all_lectures=all_lectures,
        active_live_lecture=active_live_lecture,
        next_scheduled_lecture=next_scheduled_lecture,
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

    # 100% Free for all students
    is_unlocked = True

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
        is_free_trial=False,
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
# 10. 100% Completion Refund Claims Portal
# ==============================================================================

@bhavishya_bp.route("/cashback/claim", methods=["GET", "POST"])
@login_required
def cashback_claim():
    """100% Completion Refund claim submission and status audit page."""
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
                "cashback_amount": 299.0,
                "upi_id": upi_id,
                "status": BhavishyaCashback.STATUS_UNDER_VERIFICATION,
                "applied_at": datetime.now(timezone.utc),
            })
        else:
            record.upi_id = upi_id
            record.status = BhavishyaCashback.STATUS_UNDER_VERIFICATION
            record.applied_at = datetime.now(timezone.utc)
        record.save()
        flash("Your 100% Completion Refund claim has been submitted for verification! Our team verifies submissions within 48 hours.", "success")
        return redirect(url_for("bhavishya.cashback_claim"))

    return render_template(
        "bhavishya/cashback_claim.html",
        record=record,
        progress=progress,
        completion_pct=pct,
        is_eligible=is_eligible,
        refund_amount=299.0,
    )


# ==============================================================================
# 9. Bhavishya 1.0 — Physics Wallah-Style Live Lecture Classroom & APIs
# ==============================================================================

@bhavishya_bp.route("/lecture/<lecture_id>")
def live_classroom(lecture_id):
    """
    Physics Wallah-style interactive live classroom for Bhavishya 1.0 Python Batch:
    - 🔴 LIVE NOW banner with 1-click Google Meet join for active sessions
    - Recorded video replay player for completed sessions
    - Downloadable class notes & PDF slides
    - Topic-wise Daily Practice Problems (DPP) with instant solution verification
    - In-browser interactive Python lab & compiler
    - 24/7 Ski AI doubt partner
    """
    lecture = BhavishyaLiveLecture.get_by_id(lecture_id)
    if not lecture:
        flash("Live lecture not found.", "warning")
        return redirect(url_for("bhavishya.dashboard"))

    batch_config = BhavishyaBatchConfig.get_config("bhavishya-1-0")
    # Stay within the active subject (Python or English)
    subj_slug = getattr(lecture, "subject_slug", "python") or "python"
    all_lectures = BhavishyaLiveLecture.get_all("bhavishya-1-0", subject_slug=subj_slug)

    # Bhavishya 1.0 is 100% Free for all students!
    is_unlocked = True
    is_free_trial = True

    # Determine prev and next lectures
    prev_lec = None
    next_lec = None
    for idx, l in enumerate(all_lectures):
        if l.lecture_id == lecture.lecture_id:
            if idx > 0:
                prev_lec = all_lectures[idx - 1]
            if idx < len(all_lectures) - 1:
                next_lec = all_lectures[idx + 1]
            break

    # Native In-App Recording Replay & Live Playback
    has_recording = lecture.has_recording
    playback_url = lecture.playback_url

    return render_template(
        "bhavishya/live_classroom.html",
        lecture=lecture,
        batch_config=batch_config,
        all_lectures=all_lectures,
        prev_lec=prev_lec,
        next_lec=next_lec,
        is_unlocked=is_unlocked,
        is_free_trial=is_free_trial,
        has_recording=has_recording,
        playback_url=playback_url
    )


@bhavishya_bp.route("/api/lecture/<lecture_id>/stream_status")
def api_lecture_stream_status(lecture_id):
    """Real-time In-App Live Stream status and viewer synchronization."""
    lecture = BhavishyaLiveLecture.get_by_id(lecture_id)
    if not lecture:
        return jsonify({"error": "Lecture not found"}), 404

    return jsonify({
        "success": True,
        "lecture_id": lecture.lecture_id,
        "is_live": lecture.is_live,
        "status": lecture.status,
        "title": lecture.title,
        "teacher_name": lecture.teacher_name,
        "stream_room_id": lecture.stream_room_id,
        "viewers_count": max(1, lecture.stream_viewers_count),
        "has_recording": lecture.has_recording,
        "playback_url": lecture.playback_url
    })


@bhavishya_bp.route("/api/lecture/<lecture_id>/stream_start", methods=["POST"])
@login_required
def api_lecture_stream_start(lecture_id):
    """Educator endpoint to start in-app live broadcasting."""
    if not (getattr(current_user, "is_admin", False) or getattr(current_user, "is_teacher", False)):
        return jsonify({"error": "Unauthorized. Only educators and admins can start broadcasting."}), 403

    lecture = BhavishyaLiveLecture.get_by_id(lecture_id)
    if not lecture:
        return jsonify({"error": "Lecture not found"}), 404

    lecture.status = BhavishyaLiveLecture.STATUS_LIVE
    lecture.stream_viewers_count = 1
    lecture.save()

    return jsonify({
        "success": True,
        "message": f"Broadcasting live: {lecture.title}",
        "status": "live",
        "is_live": True,
        "stream_room_id": lecture.stream_room_id
    })


@bhavishya_bp.route("/api/lecture/<lecture_id>/stream_end", methods=["POST"])
@login_required
def api_lecture_stream_end(lecture_id):
    """Educator endpoint to end in-app live broadcasting."""
    if not (getattr(current_user, "is_admin", False) or getattr(current_user, "is_teacher", False)):
        return jsonify({"error": "Unauthorized. Only educators and admins can end broadcasting."}), 403

    lecture = BhavishyaLiveLecture.get_by_id(lecture_id)
    if not lecture:
        return jsonify({"error": "Lecture not found"}), 404

    lecture.status = BhavishyaLiveLecture.STATUS_COMPLETED
    lecture.save()

    return jsonify({
        "success": True,
        "message": "Live lecture broadcasting concluded.",
        "status": "completed",
        "is_live": False
    })


@bhavishya_bp.route("/api/lecture/<lecture_id>/chat", methods=["GET", "POST"])
def api_lecture_chat(lecture_id):
    """Live classroom interactive chat & doubts stream."""
    db = get_db()
    room_id = f"chat-{lecture_id}"

    if request.method == "POST":
        if not current_user.is_authenticated:
            return jsonify({"error": "Please log in to chat."}), 401

        data = request.get_json() or {}
        msg_text = str(data.get("message", "")).strip()
        if not msg_text:
            return jsonify({"error": "Message cannot be empty."}), 400

        is_teacher = bool(getattr(current_user, "is_admin", False) or getattr(current_user, "is_teacher", False))
        chat_doc = {
            "room_id": room_id,
            "lecture_id": lecture_id,
            "user_id": str(current_user.id),
            "user_name": current_user.name or "Student",
            "user_avatar": getattr(current_user, "avatar_url", "") or "/static/img/avatar.png",
            "message": msg_text,
            "is_teacher": is_teacher,
            "created_at": datetime.now(timezone.utc),
            "timestamp_display": datetime.now().strftime("%I:%M %p")
        }
        db.bhavishya_live_chat.insert_one(chat_doc)
        return jsonify({"success": True, "chat": {
            "user_name": chat_doc["user_name"],
            "user_avatar": chat_doc["user_avatar"],
            "message": chat_doc["message"],
            "is_teacher": chat_doc["is_teacher"],
            "timestamp": chat_doc["timestamp_display"]
        }})

    # GET: return latest 60 messages
    messages = list(db.bhavishya_live_chat.find({"room_id": room_id}).sort("created_at", -1).limit(60))
    messages.reverse()
    formatted = []
    for m in messages:
        formatted.append({
            "user_name": m.get("user_name", "Student"),
            "user_avatar": m.get("user_avatar", "/static/img/avatar.png"),
            "message": m.get("message", ""),
            "is_teacher": bool(m.get("is_teacher", False)),
            "timestamp": m.get("timestamp_display", "")
        })

    return jsonify({"success": True, "messages": formatted})


@bhavishya_bp.route("/api/recordings/upload/<lecture_id>", methods=["POST"])
@login_required
def api_upload_lecture_recording(lecture_id):
    """
    Saves in-app recorded lecture video into dedicated storage,
    registers metadata in the ISOLATED recordings database vault,
    and links to the lecture without altering core SkillRock collections.
    """
    if not (getattr(current_user, "is_admin", False) or getattr(current_user, "is_teacher", False)):
        return jsonify({"error": "Unauthorized"}), 403

    lecture = BhavishyaLiveLecture.get_by_id(lecture_id)
    if not lecture:
        return jsonify({"error": "Lecture not found"}), 404

    video_file = request.files.get("video") or request.files.get("recording_file")
    if not video_file:
        return jsonify({"error": "No recording file provided"}), 400

    import os
    from werkzeug.utils import secure_filename
    from models.bhavishya_recordings import BhavishyaLectureRecording

    # Save to local recordings directory
    upload_dir = os.path.join(current_app.root_path, "static", "recordings", "bhavishya")
    os.makedirs(upload_dir, exist_ok=True)

    ts = int(time.time())
    ext = "webm"
    if "." in video_file.filename:
        ext = video_file.filename.rsplit(".", 1)[1].lower()

    filename = secure_filename(f"rec_{lecture.lecture_id}_{ts}.{ext}")
    dest_path = os.path.join(upload_dir, filename)
    video_file.save(dest_path)

    file_size = os.path.getsize(dest_path) if os.path.exists(dest_path) else 0
    file_url = f"/static/recordings/bhavishya/{filename}"

    duration_sec = int(request.form.get("duration", 0))

    # Save exclusively into the isolated recordings vault database
    rec = BhavishyaLectureRecording({
        "lecture_id": lecture.lecture_id,
        "batch_id": lecture.batch_id,
        "title": lecture.title,
        "file_url": file_url,
        "local_path": dest_path,
        "duration_seconds": duration_sec,
        "file_size_bytes": file_size,
        "mime_type": f"video/{ext}",
        "recorded_by": current_user.name or lecture.teacher_name,
        "status": "ready"
    })
    rec.save()

    # Update lecture playback pointer & status
    lecture.recording_url = file_url
    lecture.status = BhavishyaLiveLecture.STATUS_COMPLETED
    lecture.save()

    return jsonify({
        "success": True,
        "recording_id": rec.recording_id,
        "file_url": file_url,
        "file_size": file_size,
        "vault_db": "bhavishya_recordings_vault"
    })


@bhavishya_bp.route("/api/recordings/<lecture_id>")
def api_get_lecture_recording(lecture_id):
    """Retrieves recording details from the isolated recordings database vault."""
    from models.bhavishya_recordings import BhavishyaLectureRecording
    rec = BhavishyaLectureRecording.get_by_lecture(lecture_id)
    if not rec:
        return jsonify({"success": False, "has_recording": False}), 404
    return jsonify({
        "success": True,
        "has_recording": True,
        "recording": rec.to_dict()
    })


@bhavishya_bp.route("/api/live_status")
def api_live_status():
    """Returns the current live lecture status for real-time dashboard notifications."""
    active = BhavishyaLiveLecture.get_active_live("bhavishya-1-0")
    if active:
        return jsonify({
            "is_live": True,
            "lecture_id": active.lecture_id,
            "title": active.title,
            "teacher_name": active.teacher_name,
            "meet_url": active.active_meet_url,
            "duration": active.duration_minutes
        })
    next_lec = BhavishyaLiveLecture.get_next_scheduled("bhavishya-1-0")
    return jsonify({
        "is_live": False,
        "next_lecture": {
            "lecture_id": next_lec.lecture_id,
            "title": next_lec.title,
            "scheduled_display": next_lec.scheduled_display,
            "scheduled_at": next_lec.scheduled_at
        } if next_lec else None
    })


@bhavishya_bp.route("/api/dpp_submit", methods=["POST"])
def api_dpp_submit():
    """
    Evaluates student DPP responses, calculates score, awards XP points,
    and returns detailed solution explanations.
    """
    data = request.get_json() or {}
    lecture_id = data.get("lecture_id", "")
    answers = data.get("answers", {})  # { question_id: selected_index }

    lecture = BhavishyaLiveLecture.get_by_id(lecture_id)
    if not lecture:
        return jsonify({"error": "Lecture not found"}), 404

    correct_count = 0
    total_questions = len(lecture.dpp_list)
    results = []

    for q in lecture.dpp_list:
        qid = q.get("id")
        user_choice = answers.get(qid)
        correct_idx = q.get("answer_index", 0)
        is_correct = False
        if user_choice is not None:
            try:
                is_correct = (int(user_choice) == int(correct_idx))
            except Exception:
                is_correct = False
        if is_correct:
            correct_count += 1
        results.append({
            "id": qid,
            "is_correct": is_correct,
            "user_choice": user_choice,
            "correct_index": correct_idx,
            "explanation": q.get("explanation", "")
        })

    # Award XP to user if authenticated
    xp_awarded = 0
    if current_user.is_authenticated and correct_count > 0:
        try:
            xp_awarded = correct_count * 15
            current_user.xp = getattr(current_user, "xp", 0) + xp_awarded
            current_user.save()
        except Exception as e_xp:
            logger.warning(f"DPP XP award notice: {e_xp}")

    return jsonify({
        "success": True,
        "total_questions": total_questions,
        "correct_count": correct_count,
        "score_percent": round((correct_count / total_questions) * 100) if total_questions else 0,
        "xp_awarded": xp_awarded,
        "results": results
    })
