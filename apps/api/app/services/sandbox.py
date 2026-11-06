"""Restricted local Python sandbox for implement tasks.

Not a hardened multi-tenant isolator — AST-blocks dangerous imports and enforces
timeouts. Production should eventually move to Firecracker/gVisor.
"""

from __future__ import annotations

import ast
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from app.core.config import get_settings

BLOCKED_MODULES = {
    "os",
    "sys",
    "subprocess",
    "socket",
    "pathlib",
    "shutil",
    "ctypes",
    "importlib",
    "multiprocessing",
    "threading",
    "http",
    "urllib",
    "requests",
    "httpx",
    "ftplib",
    "pickle",
    "builtins",
}


class SandboxError(Exception):
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(message)


def _assert_safe(code: str) -> None:
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        raise SandboxError("syntax_error", f"Syntax error: {exc}") from exc

    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            names: list[str] = []
            if isinstance(node, ast.Import):
                names = [a.name.split(".")[0] for a in node.names]
            elif node.module:
                names = [node.module.split(".")[0]]
            for name in names:
                if name in BLOCKED_MODULES:
                    raise SandboxError("blocked_import", f"Import of '{name}' is not allowed in sandbox")
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id == "__builtins__":
            raise SandboxError("blocked_attr", "Access to __builtins__ is not allowed")
        if isinstance(node, ast.Name) and node.id in {"__import__", "eval", "exec", "compile", "open"}:
            raise SandboxError("blocked_name", f"Use of '{node.id}' is not allowed")
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in {"eval", "exec", "open"}:
            raise SandboxError("blocked_call", f"Call to '{node.func.id}' is not allowed")


def run_python_tests(*, user_code: str, tests: list[dict[str, Any]]) -> dict[str, Any]:
    settings = get_settings()
    if not settings.sandbox_enabled:
        raise SandboxError("sandbox_disabled", "Code sandbox is disabled")

    _assert_safe(user_code)
    for t in tests:
        _assert_safe(str(t.get("setup", "")))
        _assert_safe(f"print({t.get('expression', 'None')})")

    harness_lines = [
        "RESULTS = []",
        user_code,
        "",
    ]
    for i, t in enumerate(tests):
        setup = t.get("setup") or ""
        expr = t.get("expression") or "None"
        expected = t.get("expected")
        harness_lines.append(setup)
        harness_lines.append("try:")
        harness_lines.append(f"    _got = {expr}")
        harness_lines.append(f"    _exp = {expected!r}")
        harness_lines.append("    _ok = _got == _exp")
        harness_lines.append(f"    RESULTS.append({{'i': {i}, 'ok': _ok, 'got': repr(_got), 'expected': repr(_exp)}})")
        harness_lines.append("except Exception as _e:")
        harness_lines.append(f"    RESULTS.append({{'i': {i}, 'ok': False, 'error': type(_e).__name__ + ': ' + str(_e)}})")
    harness_lines.append("import json")
    harness_lines.append("print('__MT_RESULTS__' + json.dumps(RESULTS))")
    harness = "\n".join(harness_lines)

    with tempfile.TemporaryDirectory(prefix="mt-sandbox-") as tmp:
        path = Path(tmp) / "solution.py"
        path.write_text(harness, encoding="utf-8")
        try:
            proc = subprocess.run(
                [sys.executable, "-I", "-S", str(path)],
                capture_output=True,
                text=True,
                timeout=settings.sandbox_timeout_seconds,
                cwd=tmp,
                env={"PYTHONPATH": "", "PYTHONDONTWRITEBYTECODE": "1"},
            )
        except subprocess.TimeoutExpired as exc:
            raise SandboxError("timeout", f"Execution exceeded {settings.sandbox_timeout_seconds}s") from exc

    stdout = (proc.stdout or "")[: settings.sandbox_max_output_chars]
    stderr = (proc.stderr or "")[: settings.sandbox_max_output_chars]
    results: list[dict[str, Any]] = []
    for line in stdout.splitlines():
        if line.startswith("__MT_RESULTS__"):
            import json

            try:
                results = json.loads(line[len("__MT_RESULTS__") :])
            except json.JSONDecodeError:
                results = []
            break

    passed = sum(1 for r in results if r.get("ok"))
    total = len(tests)
    return {
        "exit_code": proc.returncode,
        "stdout": stdout,
        "stderr": stderr,
        "tests_passed": passed,
        "tests_total": total,
        "results": results,
        "passed": passed == total and total > 0 and proc.returncode == 0,
    }
