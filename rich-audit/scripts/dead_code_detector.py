#!/usr/bin/env python3
"""
dead_code_detector.py - Rich-Audit v2.6.2 dead code / orphan detector

Detects:
  1. orphan case files (CASE-*.md in wiki/ not referenced anywhere in ~/.claude/)
  2. dead hooks (*.py in hooks/ not referenced in settings.json)
  3. dead scripts (*.sh in scripts/ not referenced in settings.json or sourced by other scripts)
  4. orphan skills (skills with no triggers or never referenced)

Output: JSON to stdout. Exit 0 if clean, 1 if findings present.

Usage: python3 ~/.agents/skills/rich-audit/scripts/dead_code_detector.py
"""
import json
import re
import sys
from pathlib import Path

CLAUDE_DIR = Path.home() / ".claude"
SKILLS_DIR = Path.home() / ".agents" / "skills"
WIKI_DIR = CLAUDE_DIR / "knowledge" / "cases" / "wiki"

VERSION = "1.0.0"


def find_referenced_cases() -> set[str]:
    referenced: set[str] = set()
    pattern = re.compile(r"CASE-[A-Z0-9_-]+")
    for md in CLAUDE_DIR.rglob("*.md"):
        try:
            text = md.read_text(errors="ignore")
        except OSError:
            continue
        for m in pattern.findall(text):
            referenced.add(m + ".md")
    return referenced


def detect_orphan_cases() -> list[dict]:
    if not WIKI_DIR.exists():
        return []
    referenced = find_referenced_cases()
    orphans = [p for p in WIKI_DIR.glob("CASE-*.md") if p.name not in referenced]
    return [
        {"type": "orphan_case", "path": str(p.relative_to(CLAUDE_DIR.parent))}
        for p in orphans
    ]


def detect_dead_hooks() -> list[dict]:
    settings_path = CLAUDE_DIR / "settings.json"
    if not settings_path.exists():
        return []
    try:
        settings = json.loads(settings_path.read_text())
    except json.JSONDecodeError:
        return [{"type": "error", "msg": "settings.json invalid JSON"}]
    referenced: set[str] = set()
    for event_group in (settings.get("hooks") or {}).values():
        for entry in event_group or []:
            for h in (entry.get("hooks") or []):
                cmd = h.get("command", "")
                if "/" in cmd:
                    referenced.add(Path(cmd).name)
    hooks_dir = CLAUDE_DIR / "hooks"
    if not hooks_dir.exists():
        return []
    dead = [p for p in hooks_dir.glob("*.py") if p.name not in referenced]
    return [
        {"type": "dead_hook", "path": str(p.relative_to(CLAUDE_DIR.parent))}
        for p in dead
    ]


def detect_dead_scripts() -> list[dict]:
    scripts_dir = CLAUDE_DIR / "scripts"
    if not scripts_dir.exists():
        return []
    settings_path = CLAUDE_DIR / "settings.json"
    referenced: set[str] = set()
    if settings_path.exists():
        try:
            settings = json.loads(settings_path.read_text())
            hooks = settings.get("hooks") or {}
            for entry_list in hooks.values():
                for entry in entry_list or []:
                    for h in (entry.get("hooks") or []):
                        cmd = h.get("command", "")
                        if "/" in cmd:
                            referenced.add(Path(cmd).name)
            status = settings.get("statusLine")
            if isinstance(status, dict) and "command" in status:
                referenced.add(Path(status["command"]).name)
        except json.JSONDecodeError:
            pass
    # cross-script sourcing
    for sh in scripts_dir.glob("*.sh"):
        try:
            text = sh.read_text(errors="ignore")
        except OSError:
            continue
        for m in re.findall(r"(?:source|\.)\s+([^\s|&;]+\.sh)", text):
            if "/" not in m:
                referenced.add(Path(m).name)
    dead = [
        p for p in scripts_dir.glob("*.sh")
        if p.name not in referenced and not p.name.startswith("_")
    ]
    return [
        {"type": "dead_script", "path": str(p.relative_to(CLAUDE_DIR.parent))}
        for p in dead
    ]


def detect_orphan_skills() -> list[dict]:
    if not SKILLS_DIR.exists():
        return []
    orphans: list[dict] = []
    for skill_dir in SKILLS_DIR.iterdir():
        if not skill_dir.is_dir():
            continue
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            continue
        try:
            text = skill_md.read_text(errors="ignore")
        except OSError:
            continue
        fm_match = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
        if not fm_match:
            continue
        fm = fm_match.group(1)
        triggers = re.findall(r"triggers:\s*\n((?:\s*-\s*.+\n)+)", fm)
        if not triggers:
            orphans.append({
                "type": "orphan_skill",
                "path": str(skill_dir.relative_to(SKILLS_DIR.parent)),
                "reason": "no triggers declared",
            })
    return orphans


def main() -> int:
    findings: list[dict] = []
    findings.extend(detect_orphan_cases())
    findings.extend(detect_dead_hooks())
    findings.extend(detect_dead_scripts())
    findings.extend(detect_orphan_skills())
    by_type: dict[str, int] = {}
    for f in findings:
        t = f.get("type", "unknown")
        by_type[t] = by_type.get(t, 0) + 1
    result = {
        "tool": "dead_code_detector.py",
        "version": VERSION,
        "scope": str(CLAUDE_DIR),
        "findings": findings,
        "count": len(findings),
        "by_type": by_type,
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if not findings else 1


if __name__ == "__main__":
    sys.exit(main())
