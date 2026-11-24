"""
Code Execution Service for SkillRock Monthly Challenge Coding Arena.
Provides AST security validation, restricted subprocess execution, and automated test-case evaluation.
"""

import ast
import json
import logging
import subprocess
import sys
import time

logger = logging.getLogger(__name__)

# Forbidden modules and functions for untrusted code execution
FORBIDDEN_MODULES = {
    "os", "subprocess", "socket", "shutil", "pty", "pathlib", "ctypes",
    "threading", "multiprocessing", "signal", "tempfile", "posix", "nt",
    "_winapi", "msvcrt", "gc", "resource", "mmap", "builtins"
}

FORBIDDEN_SYS_ATTRS = {
    "exit", "_getframe", "modules", "settrace", "setprofile", "addaudithook"
}

FORBIDDEN_CALLS = {
    "eval", "exec", "open", "compile", "__import__", "globals", "locals",
    "getattr", "setattr", "delattr", "breakpoint", "memoryview", "exit", "quit"
}

MAX_EXECUTION_TIME_SECONDS = 5.0
MAX_OUTPUT_BYTES = 64 * 1024  # 64 KB


def validate_python_ast(code_str: str) -> tuple[bool, str]:
    """
    Statically analyzes code with Python's AST to catch prohibited modules or dangerous calls.
    Returns (is_safe, error_message).
    """
    try:
        tree = ast.parse(code_str)
    except SyntaxError as e:
        return False, f"Syntax Error on line {e.lineno}: {e.msg}"
    except Exception as e:
        return False, f"Parsing Error: {str(e)}"

    for node in ast.walk(tree):
        # Disallow forbidden imports (import os, etc.)
        if isinstance(node, ast.Import):
            for alias in node.names:
                root_mod = alias.name.split('.')[0]
                if root_mod in FORBIDDEN_MODULES:
                    return False, f"Security Violation: Import of '{alias.name}' is prohibited."

        # Disallow forbidden from-imports (from os import path, from sys import exit)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                root_mod = node.module.split('.')[0]
                if root_mod in FORBIDDEN_MODULES:
                    return False, f"Security Violation: Import from '{node.module}' is prohibited."
                if root_mod == "sys":
                    for alias in node.names:
                        if alias.name in FORBIDDEN_SYS_ATTRS:
                            return False, f"Security Violation: Import of 'sys.{alias.name}' is prohibited."

        # Disallow access to dangerous sys attributes (sys.exit, sys.modules)
        elif isinstance(node, ast.Attribute):
            if isinstance(node.value, ast.Name) and node.value.id == "sys":
                if node.attr in FORBIDDEN_SYS_ATTRS:
                    return False, f"Security Violation: Access to 'sys.{node.attr}' is prohibited."
            elif node.attr.startswith("__") and node.attr.endswith("__"):
                return False, f"Security Violation: Dunder attribute access '{node.attr}' is prohibited."

        # Disallow calls to dangerous builtins (eval(), exec(), open(), exit())
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                if node.func.id in FORBIDDEN_CALLS:
                    return False, f"Security Violation: Function call '{node.func.id}()' is prohibited."
            elif isinstance(node.func, ast.Attribute):
                if node.func.attr in FORBIDDEN_CALLS or (node.func.attr.startswith("__") and node.func.attr.endswith("__")):
                    return False, f"Security Violation: Attribute call '{node.func.attr}' is prohibited."

    return True, ""


def execute_python_code(code_str: str, stdin_input: str = "", timeout: float = MAX_EXECUTION_TIME_SECONDS) -> dict:
    """
    Runs Python code in an isolated subprocess with provided standard input.
    Enforces strict timeout and max output length.
    """
    is_safe, err_msg = validate_python_ast(code_str)
    if not is_safe:
        return {
            "success": False,
            "stdout": "",
            "stderr": err_msg,
            "exit_code": 1,
            "execution_time_ms": 0.0,
            "timed_out": False,
            "error_type": "SecurityViolation"
        }

    # Prepare execution payload
    # Note: validate_python_ast already statically verifies AST for forbidden calls and imports.
    harness = f"""
import sys

orig_import = __builtins__.__dict__["__import__"]
forbidden = {{"os", "subprocess", "socket", "shutil", "pty", "pathlib", "ctypes", "threading", "multiprocessing", "signal", "tempfile", "posix", "nt", "_winapi", "msvcrt", "gc", "resource", "mmap"}}

def safe_import(name, globals=None, locals=None, fromlist=(), level=0):
    root = name.split('.')[0]
    if root in forbidden:
        raise ImportError(f"Import of module '{{name}}' is prohibited")
    if root == "sys" and fromlist:
        for f in fromlist:
            if f in {{"exit", "_getframe", "modules", "settrace", "setprofile", "addaudithook"}}:
                raise ImportError(f"Import of 'sys.{{f}}' is prohibited")
    return orig_import(name, globals, locals, fromlist, level)

# Provide safe execution scope
safe_builtins = {{k: v for k, v in __builtins__.__dict__.items() if k not in ["open", "eval", "exec", "compile", "breakpoint"]}}
safe_builtins["__import__"] = safe_import

code_str = {repr(code_str)}
code_obj = compile(code_str, '<student_code>', 'exec')

global_ns = {{
    "__name__": "__main__",
    "__builtins__": safe_builtins,
    "sys": sys
}}

exec(code_obj, global_ns)
"""

    start_time = time.perf_counter()
    try:
        proc = subprocess.run(
            [sys.executable, "-I", "-c", harness],  # -I flags isolated mode (ignores PYTHONPATH and user site)
            input=stdin_input,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
        stdout = proc.stdout[:MAX_OUTPUT_BYTES]
        stderr = proc.stderr[:MAX_OUTPUT_BYTES]

        return {
            "success": proc.returncode == 0,
            "stdout": stdout,
            "stderr": stderr,
            "exit_code": proc.returncode,
            "execution_time_ms": elapsed_ms,
            "timed_out": False,
            "error_type": None if proc.returncode == 0 else "RuntimeError"
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Time Limit Exceeded (Timeout of {timeout}s exceeded)",
            "exit_code": -1,
            "execution_time_ms": round(timeout * 1000, 2),
            "timed_out": True,
            "error_type": "TimeLimitExceeded"
        }
    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Execution failed: {str(e)}",
            "exit_code": -1,
            "execution_time_ms": 0.0,
            "timed_out": False,
            "error_type": "SystemError"
        }


def evaluate_test_cases(code_str: str, test_cases: list[dict], language: str = "python") -> dict:
    """
    Evaluates code against a list of test cases.
    Each testcase dict should have:
    - input: string to provide on stdin
    - expected_output: string expected on stdout
    - is_hidden: bool (if True, input/expected_output will be masked in student response)
    """
    if language.lower() != "python":
        return {
            "success": False,
            "error": f"Language '{language}' is not currently configured. Supported language: Python.",
            "passed_count": 0,
            "total_count": len(test_cases),
            "all_passed": False,
            "results": []
        }

    is_safe, sec_err = validate_python_ast(code_str)
    if not is_safe:
        return {
            "success": False,
            "error": sec_err,
            "passed_count": 0,
            "total_count": len(test_cases),
            "all_passed": False,
            "results": []
        }

    results = []
    passed_count = 0

    for idx, tc in enumerate(test_cases):
        tc_input = str(tc.get("input", ""))
        expected_raw = str(tc.get("expected_output", ""))
        is_hidden = bool(tc.get("is_hidden", False))

        exec_res = execute_python_code(code_str, stdin_input=tc_input)

        actual_stdout = exec_res["stdout"].strip()
        expected_clean = expected_raw.strip()

        # Check equivalence (strip trailing whitespace and normalize CRLF)
        passed = (exec_res["success"] and actual_stdout.replace("\r\n", "\n") == expected_clean.replace("\r\n", "\n"))
        if passed:
            passed_count += 1

        result_item = {
            "test_case_id": idx + 1,
            "is_hidden": is_hidden,
            "passed": passed,
            "execution_time_ms": exec_res["execution_time_ms"],
            "timed_out": exec_res["timed_out"],
            "error": exec_res["stderr"] if not exec_res["success"] else None
        }

        if is_hidden:
            result_item["input"] = "[Hidden Test Case]"
            result_item["expected_output"] = "[Hidden Output]"
            result_item["actual_output"] = "[Hidden Output]" if not passed else actual_stdout
        else:
            result_item["input"] = tc_input
            result_item["expected_output"] = expected_clean
            result_item["actual_output"] = actual_stdout

        results.append(result_item)

    all_passed = (passed_count == len(test_cases)) and (len(test_cases) > 0)

    return {
        "success": True,
        "error": None,
        "passed_count": passed_count,
        "total_count": len(test_cases),
        "all_passed": all_passed,
        "results": results
    }
