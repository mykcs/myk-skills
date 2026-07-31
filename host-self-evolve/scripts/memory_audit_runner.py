#!/usr/bin/env python3
"""
memory_audit_runner.py - Rich-Audit Layer 1 memory-audit.sh wrapper

Runs ~/.claude/scripts/memory-audit.sh, captures output, returns JSON.

Output: JSON {tool, version, exit_code, result_line, summary_pass,
            missing_files_count, raw_output}

Usage: python3 ~/.agents/skills/rich-audit/scripts/memory_audit_runner.py

v2.0.0 (2026-06-26): 版本号 bump, 跟 rich-audit 主线 v2.6.25 对齐.
  不改主逻辑, 维持 8 个 caller 兼容. (memory-bench 双脚本体系已于 2026-07-31 硬删, 本脚本保留作独立 memory audit 工具).
"""
import json
import re
import subprocess
import sys
from pathlib import Path

MEMORY_AUDIT_SCRIPT = Path.home() / ".claude" / "scripts" / "memory-audit.sh"
VERSION = "2.0.0"


def main() -> int:
    if not MEMORY_AUDIT_SCRIPT.exists():
        result = {
            "tool": "memory_audit_runner.py",
            "version": VERSION,
            "error": f"memory-audit.sh not found at {MEMORY_AUDIT_SCRIPT}",
        }
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 1

    proc = subprocess.run(
        ["bash", str(MEMORY_AUDIT_SCRIPT)],
        capture_output=True, text=True, timeout=60,
    )
    raw = proc.stdout

    result_match = re.search(r"=== Result ===\s*\n\s*([^\n]+)", raw)
    result_line = result_match.group(1).strip() if result_match else ""
    summary_pass = "✅" in result_line and "consistent" in result_line.lower()

    missing_section = re.search(
        r"--- Referenced in MEMORY.md but missing ---\s*\n([\s\S]+?)(?=\n---|\n===|$)",
        raw,
    )
    missing_count = 0
    if missing_section and "❌" in missing_section.group(1):
        missing_count = len(re.findall(r"^\s+❌", missing_section.group(1), re.MULTILINE))

    result = {
        "tool": "memory_audit_runner.py",
        "version": VERSION,
        "exit_code": proc.returncode,
        "result_line": result_line,
        "summary_pass": summary_pass,
        "missing_files_count": missing_count,
        "raw_output": raw,
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    # v2.6.14 fix: exit code reflects whether the wrapper ran successfully, NOT
    # whether the audit passed. Audit verdict lives in JSON `summary_pass` field.
    # Rationale: same Unix convention as the other 7 scripts. Callers use
    # `summary_pass` to gate on audit results, `exit_code` to detect broken runs.
    if proc.returncode != 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
