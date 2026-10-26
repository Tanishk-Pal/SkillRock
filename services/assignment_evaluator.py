"""
SkillRock — Automated Assignment Evaluation Engine
Supports:
1. Deterministic Algorithmic Evaluation (Test case runner, syntax verification, input/output assertions)
2. Dual-Engine Evaluation (Algorithmic test runner + SkillBot AI / Gemini analysis)
"""

import ast
import json
import logging
import re
import sys
import time
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

# Safe execution builtins for running algorithmic unit tests
SAFE_BUILTINS = {
    "abs": abs,
    "all": all,
    "any": any,
    "bool": bool,
    "dict": dict,
    "enumerate": enumerate,
    "filter": filter,
    "float": float,
    "int": int,
    "isinstance": isinstance,
    "len": len,
    "list": list,
    "map": map,
    "max": max,
    "min": min,
    "pow": pow,
    "range": range,
    "reversed": reversed,
    "round": round,
    "set": set,
    "sorted": sorted,
    "str": str,
    "sum": sum,
    "tuple": tuple,
    "zip": zip,
    "True": True,
    "False": False,
    "None": None,
}


class AssignmentEvaluator:
    """
    Automated evaluation service for intermediate milestone assignments.
    """

    @classmethod
    def evaluate(cls, assignment, code_snippet: str, student_notes: str = "") -> Dict[str, Any]:
        """
        Main entry point for evaluating an assignment submission.
        Determines whether to run Algorithmic or Dual-Engine evaluation.
        """
        code = (code_snippet or "").strip()
        if not code:
            return {
                "decision": "rejected",
                "score": 0,
                "feedback": "No code was provided. Please write or paste your solution before submitting.",
                "test_results": [],
                "evaluator_type": getattr(assignment, "evaluation_type", "algorithmic")
            }

        eval_type = getattr(assignment, "evaluation_type", "algorithmic")

        # 1. First run deterministic algorithmic / test-case assertions
        algo_result = cls.evaluate_algorithmic(assignment, code)

        # If pure algorithmic mode, return immediately
        if eval_type == "algorithmic":
            return algo_result

        # 2. If dual-engine mode and code has basic syntax validity, run SkillBot AI enhancement
        if eval_type == "ai_dual":
            return cls.evaluate_ai_dual(assignment, code, algo_result, student_notes)

        # Default fallback
        return algo_result

    @classmethod
    def evaluate_algorithmic(cls, assignment, code: str) -> Dict[str, Any]:
        """
        Executes strict syntax analysis and test-case assertions.
        """
        test_results = []
        test_cases = getattr(assignment, "test_cases", []) or []
        required_keywords = getattr(assignment, "required_keywords", []) or []
        function_name = getattr(assignment, "target_function_name", "solution")

        # Step 1: Syntax Validation via AST
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return {
                "decision": "rejected",
                "score": 15,
                "feedback": f"Syntax Error on line {e.lineno}: {e.msg}. Please fix syntax before re-evaluating.",
                "test_results": [{"name": "Syntax Validation", "passed": False, "details": str(e)}],
                "evaluator_type": "algorithmic"
            }

        # Step 2: Check required keywords / structural concepts if specified
        missing_keywords = []
        for kw in required_keywords:
            if not re.search(r"\b" + re.escape(kw) + r"\b", code):
                missing_keywords.append(kw)

        if missing_keywords:
            test_results.append({
                "name": "Concept / Keyword Check",
                "passed": False,
                "details": f"Missing required concepts or declarations: {', '.join(missing_keywords)}"
            })

        # Step 3: Run Test Cases in a restricted namespace
        local_scope = {}
        global_scope = {"__builtins__": SAFE_BUILTINS}

        exec_success = False
        try:
            # Compile and execute code definition in restricted namespace
            byte_code = compile(tree, filename="<student_code>", mode="exec")
            exec(byte_code, global_scope, local_scope)
            exec_success = True
        except Exception as e:
            return {
                "decision": "rejected",
                "score": 25,
                "feedback": f"Runtime error during script execution: {type(e).__name__} - {str(e)}",
                "test_results": [{"name": "Execution Check", "passed": False, "details": str(e)}],
                "evaluator_type": "algorithmic"
            }

        # Locate target function or class
        target_func = local_scope.get(function_name) or global_scope.get(function_name)
        if not target_func and test_cases:
            # Look for any callable function defined in local_scope
            callable_funcs = [v for k, v in local_scope.items() if callable(v) and not k.startswith("_")]
            if callable_funcs:
                target_func = callable_funcs[0]

        passed_tests = 0
        total_tests = len(test_cases)

        if total_tests > 0 and target_func:
            for idx, tc in enumerate(test_cases, 1):
                tc_name = tc.get("name", f"Test Case {idx}")
                tc_input = tc.get("input")
                expected = tc.get("expected")

                try:
                    # Safely parse tc_input if it's a string representation of tuple/list
                    raw_input = tc_input
                    parsed_input = raw_input
                    if isinstance(raw_input, str):
                        raw_str = raw_input.strip()
                        if (raw_str.startswith("(") and raw_str.endswith(")")) or (raw_str.startswith("[") and raw_str.endswith("]")):
                            try:
                                parsed_input = ast.literal_eval(raw_str)
                            except Exception:
                                parsed_input = raw_input

                    # Execute with appropriate argument unpacking
                    if isinstance(parsed_input, tuple):
                        actual = target_func(*parsed_input)
                    elif isinstance(parsed_input, list):
                        try:
                            import inspect
                            sig = inspect.signature(target_func)
                            if len(sig.parameters) > 1 and len(sig.parameters) == len(parsed_input):
                                actual = target_func(*parsed_input)
                            else:
                                actual = target_func(parsed_input)
                        except Exception:
                            try:
                                actual = target_func(parsed_input)
                            except TypeError:
                                actual = target_func(*parsed_input)
                    elif parsed_input is not None:
                        actual = target_func(parsed_input)
                    else:
                        actual = target_func()

                    # Resilient comparison with expected
                    exp_val = expected
                    if isinstance(expected, str):
                        try:
                            exp_val = ast.literal_eval(expected.strip())
                        except Exception:
                            exp_val = expected

                    is_match = False
                    if actual == exp_val or actual == expected:
                        is_match = True
                    elif str(actual).strip() == str(expected).strip() or str(actual).strip() == str(exp_val).strip():
                        is_match = True
                    elif isinstance(actual, bool) and str(actual).lower() == str(expected).lower():
                        is_match = True

                    if is_match:
                        passed_tests += 1
                        test_results.append({
                            "name": tc_name,
                            "passed": True,
                            "status": "pass",
                            "expected": str(expected),
                            "actual": str(actual),
                            "details": f"Passed. Input: {tc_input} ➔ Output: {actual}"
                        })
                    else:
                        test_results.append({
                            "name": tc_name,
                            "passed": False,
                            "status": "fail",
                            "expected": str(expected),
                            "actual": str(actual),
                            "details": f"Failed. Input: {tc_input} | Expected: {expected} | Received: {actual}"
                        })
                except Exception as ex:
                    test_results.append({
                        "name": tc_name,
                        "passed": False,
                        "status": "fail",
                        "expected": str(expected),
                        "actual": "Error",
                        "error": f"{type(ex).__name__}: {str(ex)}",
                        "details": f"Error during test: {type(ex).__name__}: {str(ex)}"
                    })
        elif total_tests == 0:
            # If no explicit test cases defined, code execution + syntax validation passes
            passed_tests = 1
            total_tests = 1
            test_results.append({
                "name": "Code Structure & Execution Check",
                "passed": True,
                "details": "Code parsed cleanly with no runtime errors."
            })
        else:
            test_results.append({
                "name": "Target Function Definition",
                "passed": False,
                "details": f"Could not find function '{function_name}'. Please define it as required."
            })

        # Calculate score
        if total_tests > 0:
            pct = int((passed_tests / total_tests) * 100)
        else:
            pct = 100 if exec_success else 0

        if missing_keywords:
            pct = max(0, pct - (len(missing_keywords) * 15))

        is_approved = (pct >= 80 and not missing_keywords)

        if is_approved:
            feedback = f"✅ All algorithmic tests passed! ({passed_tests}/{total_tests} test cases passed). Excellent logic and execution."
        else:
            feedback = f"⚠️ Test cases failed ({passed_tests}/{total_tests} passed). Please review the test diagnostics below and fix edge cases."

        return {
            "decision": "approved" if is_approved else "rejected",
            "score": pct,
            "feedback": feedback,
            "test_results": test_results,
            "evaluator_type": "algorithmic"
        }

    @classmethod
    def evaluate_ai_dual(cls, assignment, code: str, algo_result: Dict[str, Any], student_notes: str = "") -> Dict[str, Any]:
        """
        Combines deterministic test runner results with SkillBot AI (Gemini)
        for qualitative review (code cleanlines, edge cases, naming, security).
        """
        from services.ai_service import is_gemini_configured, execute_fast_gemini_rest

        if not is_gemini_configured():
            logger.info("[Evaluator] Gemini API not configured; using deterministic algorithmic score.")
            algo_result["evaluator_type"] = "ai_dual (algorithmic fallback)"
            return algo_result

        problem_title = getattr(assignment, "title", "Programming Assignment")
        problem_desc = getattr(assignment, "problem_statement", getattr(assignment, "short_description", ""))
        tech_reqs = getattr(assignment, "tech_requirements", "")

        test_summary = f"{algo_result.get('score', 0)}% score on deterministic unit tests. Tests: {json.dumps(algo_result.get('test_results', []))}"

        prompt = f"""
You are the SkillRock Automated Code Evaluator. Evaluate this student submission for an online course assignment.

ASSIGNMENT TITLE: {problem_title}
PROBLEM STATEMENT: {problem_desc}
REQUIREMENTS: {tech_reqs}

AUTOMATED UNIT TEST RESULTS:
{test_summary}

STUDENT SUBMITTED CODE:
```
{code[:3000]}
```

STUDENT NOTES: {student_notes[:400] if student_notes else "None"}

Evaluate the submission on:
1. Correctness & logic
2. Clean code conventions & modularity
3. Edge case handling

Respond ONLY with valid JSON in this exact structure:
{{
  "decision": "approved" or "rejected",
  "score": integer between 0 and 100,
  "strengths": ["point 1", "point 2"],
  "improvements": ["point 1", "point 2"],
  "feedback": "2-3 concise, constructive sentences explaining the grading decision and advice."
}}
"""
        system_instruction = "You are an expert computer science grader. Be fair, encouraging, and accurate. Approve submissions that solve the core problem correctly (score >= 75). Reject with clear guidance if incomplete or broken."

        try:
            ai_resp = execute_fast_gemini_rest(prompt, system_instruction=system_instruction)
            # Extract JSON block
            raw = ai_resp.strip()
            match = re.search(r"\{.*\}", raw, re.DOTALL)
            if match:
                parsed = json.loads(match.group(0))
                decision = parsed.get("decision", "rejected").lower()
                ai_score = int(parsed.get("score", 70))
                feedback = parsed.get("feedback", "")
                strengths = parsed.get("strengths", [])
                improvements = parsed.get("improvements", [])

                # Blend algorithmic score with AI score (50% algorithmic, 50% AI)
                blended_score = int((algo_result.get("score", 0) * 0.5) + (ai_score * 0.5))

                # If algorithmic tests completely failed, cannot approve
                if algo_result.get("score", 0) < 50:
                    decision = "rejected"
                    blended_score = min(blended_score, 55)

                final_decision = "approved" if (decision == "approved" and blended_score >= 75) else "rejected"

                feedback_full = feedback
                if strengths:
                    feedback_full += "\n\n🌟 Strengths:\n• " + "\n• ".join(strengths)
                if improvements:
                    feedback_full += "\n\n💡 Suggestions for Improvement:\n• " + "\n• ".join(improvements)

                return {
                    "decision": final_decision,
                    "score": blended_score,
                    "feedback": feedback_full,
                    "test_results": algo_result.get("test_results", []),
                    "evaluator_type": "ai_dual"
                }
        except Exception as e:
            logger.warning(f"[Evaluator] Gemini AI evaluation error ({e}); falling back to algorithmic result.")

        algo_result["evaluator_type"] = "ai_dual (fallback)"
        return algo_result
