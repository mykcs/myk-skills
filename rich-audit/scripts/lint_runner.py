#!/usr/bin/env python3
"""
lint_runner.py - Rich-Audit v2.6.3 lint runner

Runs (per user hard rule "shellcheck 必跑"):
  1. shellcheck on all .sh in ~/.claude/scripts/ and ~/.claude/hooks/
  2. python3 -m py_compile on all .py in same dirs

Output: JSON to stdout. Exit 0 if clean, 1 if findings.

Usage: python3 ~/.agents/skills/rich-audit/scripts/lint_runner.py
"""
import json
import subprocess
import sys
from pathlib import Path

CLAUDE_DIR = Path.home() / ".claude"
SCAN_DIRS = [CLAUDE_DIR / "scripts", CLAUDE_DIR / "hooks"]

VERSION = "1.0.0"


def run_shellcheck(shell_files: list[Path]) -> list[dict]:
    findings: list[dict] = []
    for sh in shell_files:
        try:
            result = subprocess.run(
                ["shellcheck", "--format=json", str(sh)],
                capture_output=True, text=True, timeout=30,
            )
        except FileNotFoundError:
            return [{"type": "error", "msg": "shellcheck not installed"}]
        except subprocess.TimeoutExpired:
            findings.append({"type": "shellcheck_timeout", "path": str(sh)})
            continue
        if result.returncode == 0:
            continue
        if not result.stdout.strip():
            continue
        try:
            issues = json.loads(result.stdout)
            for issue in issues:
                findings.append({
                    "type": "shellcheck",
                    "path": str(sh.relative_to(CLAUDE_DIR.parent)),
                    "line": issue.get("line"),
                    "col": issue.get("column"),
                    "code": issue.get("code"),
                    "level": issue.get("level"),
                    "message": (issue.get("message") or "")[:200],
                })
        except json.JSONDecodeError:
            findings.append({
                "type": "shellcheck_parse_error",
                "path": str(sh),
                "raw": result.stdout[:500],
            })
    return findings


def run_py_compile(py_files: list[Path]) -> list[dict]:
    findings: list[dict] = []
    for py in py_files:
        try:
            result = subprocess.run(
                ["python3", "-m", "py_compile", str(py)],
                capture_output=True, text=True, timeout=10,
            )
        except subprocess.TimeoutExpired:
            findings.append({"type": "py_compile_timeout", "path": str(py)})
            continue
        if result.returncode != 0:
            findings.append({
                "type": "py_compile",
                "path": str(py.relative_to(CLAUDE_DIR.parent)),
                "message": (result.stderr or result.stdout)[:300],
            })
    return findings


def main() -> int:
    shell_files: list[Path] = []
    py_files: list[Path] = []
    for d in SCAN_DIRS:
        if not d.exists():
            continue
        shell_files.extend(d.glob("*.sh"))
        py_files.extend(d.glob("*.py"))

    findings: list[dict] = []
    findings.extend(run_shellcheck(shell_files))
    findings.extend(run_py_compile(py_files))

    by_type: dict[str, int] = {}
    for f in findings:
        t = f.get("type", "unknown")
        by_type[t] = by_type.get(t, 0) + 1

    result = {
        "tool": "lint_runner.py",
        "version": VERSION,
        "scanned_sh": len(shell_files),
        "scanned_py": len(py_files),
        "findings": findings,
        "count": len(findings),
        "by_type": by_type,
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if not findings else 1


if __name__ == "__main__":
    sys.exit(main())
