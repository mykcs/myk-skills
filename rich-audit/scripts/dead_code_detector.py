#!/usr/bin/env python3
"""
dead_code_detector.py - Rich-Audit v2.6.13 dead code / orphan detector

Detects:
  1. orphan case files (CASE-*.md in wiki/ not referenced anywhere in ~/.claude/)
  2. dead hooks (*.py in hooks/ not referenced in settings.json)
  3. dead scripts (*.sh in scripts/ not referenced in settings.json or sourced by other scripts)
  4. orphan skills (skills with no triggers or never referenced)

Output: JSON to stdout. Exit 0 if clean, 1 if findings present.

Usage: python3 ~/.agents/skills/rich-audit/scripts/dead_code_detector.py

v2.6.13 fixes (2026-06-11, per CASE-RICH-AUDIT-DETECTION-SCHEMA-BUG-20260611):
  - Case regex now matches lowercase letters (was [A-Z0-9_-]+ → [A-Za-z0-9_-]+).
    Fixes 9+ false orphan_case findings (e.g. CASE-098-usage-report-verification).
  - Hook/script command parsing now splits compound commands (&&/||/;/|) and
    extracts ALL .py/.sh tokens, not just Path(cmd).name of the full string.
    Fixes 17+ false dead_script findings (e.g. smart-push.sh, memory-audit.sh,
    skills-symlink-restore.py were all reported as dead despite being referenced
    in SessionStart compound hook commands).
"""
import json
import re
import sys
from pathlib import Path

CLAUDE_DIR = Path.home() / ".claude"
SKILLS_DIR = Path.home() / ".agents" / "skills"
WIKI_DIR = CLAUDE_DIR / "knowledge" / "cases" / "wiki"

VERSION = "1.2.0"  # v2.6.13 fixes

# v2.6.13: split compound shell commands on &&, ||, ;, | (single pipe)
_COMPOUND_SPLIT_RE = re.compile(r"\s*(?:&&|\|\||;|\|)\s*")
# v2.6.13: extract .py/.sh file tokens from a (sub-)command
_SCRIPT_TOKEN_RE = re.compile(r"(?:^|[\s'\"=])([^\s'\"=|&;]+\.(?:py|sh|mjs|js|ts))\b")


def extract_script_names(cmd: str) -> set[str]:
    """v2.6.13: parse compound shell command, return ALL referenced script basenames.

    Handles cases like:
      "python3 ~/.claude/hooks/a.py && python3 ~/.claude/hooks/b.py"
      "bash X.sh; bash Y.sh || true"
      "exec --flag=~/.claude/scripts/foo.sh -v"
    """
    found: set[str] = set()
    for sub in _COMPOUND_SPLIT_RE.split(cmd):
        # Match each .py/.sh path-like token in the sub-command.
        for match in _SCRIPT_TOKEN_RE.finditer(" " + sub):
            token = match.group(1)
            try:
                found.add(Path(token).name)
            except (ValueError, OSError):
                continue
    return found


def find_referenced_cases() -> set[str]:
    referenced: set[str] = set()
    # v2.6.13: include lowercase letters in CASE pattern
    # File names contain mixed case e.g. CASE-098-usage-report-verification-20260527.md
    pattern = re.compile(r"CASE-[A-Za-z0-9_-]+")
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


def _collect_settings_referenced() -> set[str]:
    """v2.6.13: shared helper to collect script names from settings.json hooks + statusLine."""
    settings_path = CLAUDE_DIR / "settings.json"
    referenced: set[str] = set()
    if not settings_path.exists():
        return referenced
    try:
        settings = json.loads(settings_path.read_text())
    except json.JSONDecodeError:
        return referenced
    for event_group in (settings.get("hooks") or {}).values():
        for entry in event_group or []:
            for h in (entry.get("hooks") or []):
                cmd = h.get("command", "")
                if cmd:
                    referenced.update(extract_script_names(cmd))
    status = settings.get("statusLine")
    if isinstance(status, dict) and "command" in status:
        referenced.update(extract_script_names(status.get("command", "")))
    return referenced


def _collect_md_referenced_scripts() -> set[str]:
    """v2.6.13: scan ~/.claude/**.md + ~/.agents/skills/**.md for script basenames.

    Scripts referenced inside case files, SKILL.md, or README.md should NOT be
    reported as dead. Excludes backups/ and archive-*/ subdirectories.
    """
    referenced: set[str] = set()
    pattern = re.compile(r"\b([a-zA-Z][\w-]+\.(?:sh|py))\b")
    for base in (CLAUDE_DIR, SKILLS_DIR):
        if not base.exists():
            continue
        for md in base.rglob("*.md"):
            parts = md.parts
            # Skip backup / archive directories
            if any(p.startswith("backups") or p.startswith("archive-") for p in parts):
                continue
            try:
                text = md.read_text(errors="ignore")
            except OSError:
                continue
            for m in pattern.findall(text):
                referenced.add(m)
    return referenced


def _collect_script_sourced() -> set[str]:
    """v2.6.13: scan all .sh files for sourced/invoked siblings."""
    referenced: set[str] = set()
    scripts_dir = CLAUDE_DIR / "scripts"
    if not scripts_dir.exists():
        return referenced
    invoke_re = re.compile(r"(?:source|\.|bash|sh|python3?)\s+([^\s|&;]+\.(?:sh|py))")
    for sh in scripts_dir.rglob("*.sh"):
        try:
            text = sh.read_text(errors="ignore")
        except OSError:
            continue
        for m in invoke_re.findall(text):
            referenced.add(Path(m).name)
    return referenced


def detect_dead_hooks() -> list[dict]:
    hooks_dir = CLAUDE_DIR / "hooks"
    if not hooks_dir.exists():
        return []
    referenced = _collect_settings_referenced()
    referenced |= _collect_md_referenced_scripts()
    dead = [p for p in hooks_dir.glob("*.py") if p.name not in referenced]
    return [
        {"type": "dead_hook", "path": str(p.relative_to(CLAUDE_DIR.parent))}
        for p in dead
    ]


def detect_dead_scripts() -> list[dict]:
    scripts_dir = CLAUDE_DIR / "scripts"
    if not scripts_dir.exists():
        return []
    referenced = _collect_settings_referenced()
    referenced |= _collect_md_referenced_scripts()
    referenced |= _collect_script_sourced()
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
            skill_name = skill_dir.name
            # v1.2.0 (2026-06-12): skip loaded-by-name skills (no triggers needed).
            # Was causing 64 false positive orphan_skill findings.
            if skill_name in LOADED_BY_NAME_SKILLS:
                continue
            orphans.append({
                "type": "orphan_skill",
                "path": str(skill_dir.relative_to(SKILLS_DIR.parent)),
                "reason": "no triggers declared",
            })
    return orphans


# v1.2.0 (2026-06-12): skills loaded by name (Skill tool) rather than trigger.
# These don't need `triggers:` frontmatter. Identified by being referenced in
# CLAUDE.md, MEMORY.md, or other skill files. Kept manual for now.
LOADED_BY_NAME_SKILLS: set[str] = {
    "rich-audit", "session-chapter", "healer-cannot-self-heal",
    "persona-check", "skill-management", "sync-skill",
    "skill-create", "skill-evolution", "learned",
    "omc-reference", "anysearch", "kimi-webbridge",
    "web-access", "agent-reach", "agents", "algorithmic-art",
    "backup-claude-settings", "brand-guidelines", "canvas-design",
    "claude-api", "claude-skill-docx-batch", "confirm-edit",
    "curl", "doc-coauthoring", "docx", "eval-viewer", "feishu-agent",
    "find-skills", "frontend-design", "frontend-slides", "grill-me",
    "grill-with-docs", "internal-comms", "lark-approval",
    "lark-attendance", "lark-base", "lark-calendar", "lark-contact",
    "lark-doc", "lark-drive", "lark-event", "lark-im", "lark-mail",
    "lark-minutes", "lark-okr", "lark-openapi-explorer", "lark-shared",
    "lark-sheets", "lark-skill-maker", "lark-slides", "lark-task",
    "lark-vc", "lark-whiteboard", "lark-wiki", "lark-workflow-meeting-summary",
    "lark-workflow-standup-report", "learn", "learn-eval", "mcp-builder",
    "pdf", "phd-scout", "pptx", "record-case", "skill-health",
    "slack-gif-creator", "teacher-report", "theme-factory",
    "verifier-pass2", "web-artifacts-builder", "web-design-engineer",
    "webapp-testing", "website-improve", "xiao-de", "xlsx",
    # v1.2.1 (2026-06-15): additional loaded-by-name skills confirmed in repo
    "lark-markdown", "lark-vc-agent", "skill-creator", "lark-apps",
    "parallel-fix-explorer",
}


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
    # v2.6.14 fix: exit 0 on successful execution regardless of findings.
    # Findings count is in JSON `count` field; callers must check that, not exit code.
    # Rationale: Unix exit code = "did the tool run successfully?", not "did it find problems?".
    # Previous `return 0 if not findings else 1` broke `cmd && echo OK` pipelines.
    return 0


if __name__ == "__main__":
    sys.exit(main())
