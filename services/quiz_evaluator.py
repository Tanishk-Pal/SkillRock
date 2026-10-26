"""
SkillRock Quiz Evaluator Service
Provides secure sanitization of quiz data (preventing answer leaks to clients)
and server-side evaluation, scoring, partial credit, and status determination.
"""

import copy
import random
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


def sanitize_for_student(quiz_data: Dict[str, Any], shuffle_questions: bool = False, shuffle_options: bool = False) -> Dict[str, Any]:
    """
    Sanitizes quiz questions for student clients.
    Completely removes correct answers, answer keys, accepted strings, and explanations.
    """
    if not isinstance(quiz_data, dict):
        return {"questions": [], "time_limit_minutes": 0, "max_attempts": 3}

    sanitized = {
        "time_limit_minutes": int(quiz_data.get("time_limit_minutes", 0) or 0),
        "max_attempts": int(quiz_data.get("max_attempts", 3) or 3),
        "allow_review_answers": bool(quiz_data.get("allow_review_answers", True)),
        "show_immediate_results": bool(quiz_data.get("show_immediate_results", True)),
        "total_marks": int(quiz_data.get("total_marks", 0) or 0),
        "questions": []
    }

    raw_questions = quiz_data.get("questions", []) or []
    questions_copy = copy.deepcopy(raw_questions)

    if shuffle_questions or quiz_data.get("shuffle_questions"):
        random.shuffle(questions_copy)

    total_marks = 0
    for idx, q in enumerate(questions_copy):
        q_id = str(q.get("id") or f"q_{idx + 1}")
        q_type = str(q.get("type", "single_choice")).lower()
        marks = int(q.get("marks", 1) or 1)
        total_marks += marks

        options = []
        raw_options = q.get("options", []) or []
        for o_idx, opt in enumerate(raw_options):
            if isinstance(opt, dict):
                opt_id = str(opt.get("id") or f"opt_{o_idx + 1}")
                opt_text = str(opt.get("text", "")).strip()
            else:
                opt_id = f"opt_{o_idx + 1}"
                opt_text = str(opt).strip()
            options.append({"id": opt_id, "text": opt_text})

        if shuffle_options or quiz_data.get("shuffle_options"):
            random.shuffle(options)

        sanitized_q = {
            "id": q_id,
            "order": idx + 1,
            "type": q_type,
            "question": str(q.get("question", "")).strip(),
            "marks": marks,
            "options": options,
            "placeholder": str(q.get("placeholder", "")).strip()
        }
        sanitized["questions"].append(sanitized_q)

    sanitized["total_marks"] = total_marks if total_marks > 0 else len(sanitized["questions"])
    return sanitized


def evaluate_quiz_submission(
    quiz_data: Dict[str, Any],
    submitted_answers: Dict[str, Any],
    passing_score: int = 70
) -> Dict[str, Any]:
    """
    Evaluates student quiz answers against official answer keys on the server.
    Calculates marks, partial credit for multiple select, fuzzy matching for short answers,
    and returns question-level breakdown and outcome status.
    """
    raw_questions = quiz_data.get("questions", []) if isinstance(quiz_data, dict) else []
    
    total_quiz_marks = 0
    total_awarded_marks = 0.0
    question_breakdowns = []
    requires_manual_review = False

    for idx, q in enumerate(raw_questions):
        q_id = str(q.get("id") or f"q_{idx + 1}")
        q_type = str(q.get("type", "single_choice")).lower()
        q_marks = int(q.get("marks", 1) or 1)
        total_quiz_marks += q_marks

        explanation = str(q.get("explanation", "")).strip()
        correct_option_ids = [str(cid).strip() for cid in q.get("correct_option_ids", []) if cid]
        accepted_answers = [str(a).strip() for a in q.get("accepted_answers", []) if str(a).strip()]
        case_sensitive = bool(q.get("case_sensitive", False))
        manual_review_flag = bool(q.get("requires_manual_review", False))

        # Retrieve student answer
        student_ans = submitted_answers.get(q_id)
        awarded_marks = 0.0
        is_correct = False
        needs_review_for_this = False

        if q_type == "single_choice":
            ans_str = str(student_ans or "").strip()
            if correct_option_ids and ans_str in correct_option_ids:
                awarded_marks = float(q_marks)
                is_correct = True
            elif not correct_option_ids and str(q.get("correct_answer", "")).strip() == ans_str:
                awarded_marks = float(q_marks)
                is_correct = True

        elif q_type == "true_false":
            ans_str = str(student_ans or "").strip().lower()
            correct_val = ""
            if correct_option_ids:
                correct_val = correct_option_ids[0].lower()
            else:
                correct_val = str(q.get("correct_answer", "")).strip().lower()

            # Normalize "true"/"false"
            norm_student = "true" if ans_str in ["true", "t", "1", "yes"] else ("false" if ans_str in ["false", "f", "0", "no"] else ans_str)
            norm_correct = "true" if correct_val in ["true", "t", "1", "yes"] else ("false" if correct_val in ["false", "f", "0", "no"] else correct_val)

            if norm_student and norm_student == norm_correct:
                awarded_marks = float(q_marks)
                is_correct = True

        elif q_type == "multiple_select":
            # List of option IDs selected by student
            if isinstance(student_ans, list):
                chosen_set = {str(x).strip() for x in student_ans if str(x).strip()}
            elif student_ans:
                chosen_set = {str(student_ans).strip()}
            else:
                chosen_set = set()

            correct_set = set(correct_option_ids)
            if not correct_set and q.get("correct_options"):
                correct_set = {str(x).strip() for x in q.get("correct_options", [])}

            if chosen_set == correct_set and correct_set:
                awarded_marks = float(q_marks)
                is_correct = True
            elif correct_set:
                # Proportional partial credit: (correct_picked - incorrect_picked) / total_correct
                correct_picked = len(chosen_set & correct_set)
                incorrect_picked = len(chosen_set - correct_set)
                net = max(0, correct_picked - incorrect_picked)
                fraction = net / float(len(correct_set))
                awarded_marks = round(fraction * q_marks, 2)
                is_correct = (awarded_marks == float(q_marks))

        elif q_type == "short_answer":
            ans_str = str(student_ans or "").strip()
            matched = False

            if accepted_answers:
                for target in accepted_answers:
                    if case_sensitive:
                        if ans_str == target:
                            matched = True
                            break
                    else:
                        if ans_str.lower() == target.lower():
                            matched = True
                            break

            if matched:
                awarded_marks = float(q_marks)
                is_correct = True
            elif manual_review_flag:
                # Routed for human review
                needs_review_for_this = True
                requires_manual_review = True
                awarded_marks = 0.0
                is_correct = False
            else:
                awarded_marks = 0.0
                is_correct = False

        total_awarded_marks += awarded_marks

        # Build options map for displaying text in review
        options_map = {}
        for opt in (q.get("options", []) or []):
            if isinstance(opt, dict):
                options_map[str(opt.get("id"))] = str(opt.get("text", ""))

        question_breakdowns.append({
            "question_id": q_id,
            "type": q_type,
            "question": str(q.get("question", "")),
            "max_marks": q_marks,
            "awarded_marks": awarded_marks,
            "is_correct": is_correct,
            "student_answer": student_ans,
            "correct_option_ids": correct_option_ids,
            "accepted_answers": accepted_answers,
            "options_map": options_map,
            "explanation": explanation,
            "needs_manual_review": needs_review_for_this
        })

    # Total score calculation
    effective_total = total_quiz_marks if total_quiz_marks > 0 else 100
    percentage = round((total_awarded_marks / effective_total) * 100, 1)
    is_passed = (percentage >= passing_score) and not requires_manual_review

    if requires_manual_review:
        status = "pending_review"
    elif is_passed:
        status = "approved"
    else:
        status = "rejected"

    return {
        "total_marks": effective_total,
        "marks_obtained": round(total_awarded_marks, 2),
        "percentage": percentage,
        "passing_score": passing_score,
        "is_passed": is_passed,
        "status": status,
        "requires_manual_review": requires_manual_review,
        "questions": question_breakdowns
    }
