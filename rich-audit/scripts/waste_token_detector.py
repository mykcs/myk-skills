#!/usr/bin/env python3
"""
waste_token_detector.py - Rich-Audit v2.6.10 C: wasted context tokens detector

Per jarodtaylor gist (dead weight, conflicts, stale rules, wasted context tokens):
  1. Hot path heavy (> 1500 tokens, loaded every session)
  2. Skill too heavy (> 1500 tokens, loaded on demand)
  3. Stale hot path (> 30 days, not modified)

Output: JSON {tool, version, findings, count, by_type, total_hot_path_tokens}
Exit 0 clean, 1 findings.

Usage: python3 ~/.agents/skills/rich-audit/scripts/waste_token_detector.py
"""
import json
import re
import sys
import time
from pathlib import Path

CLAUDE_DIR = Path.home() / ".claude"
SKILLS_DIR = Path.home() / ".agents" / "skills"
VERSION = "1.0.0"
WARN_TOKENS = 1500
STALE_DAYS = 30

HOT_PATHS = [
    CLAUDE_DIR / "rules",
    CLAUDE_DIR / "memory",
    CLAUDE_DIR / "CLAUDE.md",
    CLAUDE_DIR / "CLAUDE.local.md",
]


def estimate_tokens(text: str) -> int:
    return len(text) // 4


def detect_hot_path_heavy() -> list[dict]:
    findings: list[dict] = []
    for p in HOT_PATHS:
        if p.is_file():
            try:
                tokens = estimate_tokens(p.read_text(errors="ignore"))
            except OSError:
                continue
            if tokens > WARN_TOKENS:
                findings.append({
                    "type": "hot_path_heavy",
                    "path": str(p.relative_to(CLAUDE_DIR.parent)),
                    "tokens": tokens,
                })
    return findings


def detect_skill_too_heavy() -> list[dict]:
    findings: list[dict] = []
    if not SKILLS_DIR.exists():
        return findings
    for skill_dir in SKILLS_DIR.iterdir():
        if not skill_dir.is_dir():
            continue
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            continue
        try:
            tokens = estimate_tokens(skill_md.read_text(errors="ignore"))
        except OSError:
            continue
        if tokens > WARN_TOKENS:
            findings.append({
                "type": "skill_too_heavy",
                "path": str(skill_dir.relative_to(SKILLS_DIR.parent)),
                "tokens": tokens,
            })
    return findings


def detect_stale_hot_path() -> list[dict]:
    findings: list[dict] = []
    rules_dir = CLAUDE_DIR / "rules"
    if not rules_dir.exists():
        return findings
    for p in rules_dir.glob("*.md"):
        try:
            age_days = (time.time() - p.stat().st_mtime) / 86400
        except OSError:
            continue
        if age_days > STALE_DAYS:
            findings.append({
                "type": "stale_hot_path",
                "path": str(p.relative_to(CLAUDE_DIR.parent)),
                "age_days": round(age_days, 1),
            })
    return findings


def main() -> int:
    findings: list[dict] = []
    findings.extend(detect_hot_path_heavy())
    findings.extend(detect_skill_too_heavy())
    findings.extend(detect_stale_hot_path())
    by_type: dict[str, int] = {}
    for f in findings:
        t = f.get("type", "unknown")
        by_type[t] = by_type.get(t, 0) + 1
    # total hot path tokens (rules + CLAUDE.md + memory)
    total_hot = 0
    rules_dir = CLAUDE_DIR / "rules"
    if rules_dir.exists():
        for p in rules_dir.glob("*.md"):
            try:
                total_hot += estimate_tokens(p.read_text(errors="ignore"))
            except OSError:
                continue
    for p in (CLAUDE_DIR / "CLAUDE.md", CLAUDE_DIR / "CLAUDE.local.md"):
        if p.exists():
            try:
                total_hot += estimate_tokens(p.read_text(errors="ignore"))
            except OSError:
                continue
    result = {
        "tool": "waste_token_detector.py",
        "version": VERSION,
        "findings": findings,
        "count": len(findings),
        "by_type": by_type,
        "total_hot_path_tokens": total_hot,
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    # v2.6.14 fix: exit 0 on successful execution. See dead_code_detector.py for rationale.
    return 0


if __name__ == "__main__":
    sys.exit(main())
