#!/usr/bin/env python3
"""
commands_to_skills_migrator.py - Rich-Audit v2.6.2 commands→skills migration detector

Per code.claude.com/docs/en/skills: "Custom commands have been merged into skills"

Detects:
  1. Migration candidates (commands in ~/.claude/commands/*.md without matching skill)
  2. Skill trigger overlap (multiple skills sharing same trigger word)

Output: JSON to stdout. Exit 0 if clean, 1 if findings present.

Usage: python3 ~/.agents/skills/rich-audit/scripts/commands_to_skills_migrator.py
"""
import json
import re
import sys
from pathlib import Path

CLAUDE_DIR = Path.home() / ".claude"
COMMANDS_DIR = CLAUDE_DIR / "commands"
SKILLS_DIR = Path.home() / ".agents" / "skills"

VERSION = "1.0.0"


def detect_migration_candidates() -> list[dict]:
    if not COMMANDS_DIR.exists():
        return []
    candidates: list[dict] = []
    for cmd in COMMANDS_DIR.glob("*.md"):
        name = cmd.stem
        skill_path = SKILLS_DIR / name / "SKILL.md"
        if not skill_path.exists():
            try:
                body_lines = len(cmd.read_text(errors="ignore").splitlines())
            except OSError:
                body_lines = -1
            candidates.append({
                "type": "migration_candidate",
                "command": str(cmd.relative_to(CLAUDE_DIR)),
                "name": name,
                "body_lines": body_lines,
                "target_path": f"~/.agents/skills/{name}/SKILL.md",
            })
    return candidates


def parse_skill_meta(skill_dir: Path) -> dict | None:
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return None
    try:
        text = skill_md.read_text(errors="ignore")
    except OSError:
        return None
    fm_match = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not fm_match:
        return None
    fm = fm_match.group(1)
    triggers_block = re.findall(r"triggers:\s*\n((?:\s*-\s*.+\n)+)", fm)
    trigger_list: list[str] = []
    if triggers_block:
        trigger_list = [
            t.strip().lstrip("- ").strip()
            for t in triggers_block[0].split("\n")
            if t.strip()
        ]
    return {
        "name": skill_dir.name,
        "triggers": trigger_list,
    }


def detect_skill_overlap() -> list[dict]:
    if not SKILLS_DIR.exists():
        return []
    metas: list[dict] = []
    for skill_dir in SKILLS_DIR.iterdir():
        if not skill_dir.is_dir():
            continue
        meta = parse_skill_meta(skill_dir)
        if meta:
            metas.append(meta)
    overlaps: list[dict] = []
    for i, a in enumerate(metas):
        a_triggers = set(a["triggers"])
        if not a_triggers:
            continue
        for b in metas[i + 1:]:
            shared = a_triggers & set(b["triggers"])
            if shared:
                overlaps.append({
                    "type": "skill_overlap_triggers",
                    "skills": [a["name"], b["name"]],
                    "shared_triggers": sorted(shared),
                })
    return overlaps


def main() -> int:
    candidates = detect_migration_candidates()
    overlaps = detect_skill_overlap()
    result = {
        "tool": "commands_to_skills_migrator.py",
        "version": VERSION,
        "scope_commands": str(COMMANDS_DIR),
        "scope_skills": str(SKILLS_DIR),
        "migration_candidates": candidates,
        "skill_overlaps": overlaps,
        "migration_count": len(candidates),
        "overlap_count": len(overlaps),
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if not (candidates or overlaps) else 1


if __name__ == "__main__":
    sys.exit(main())
