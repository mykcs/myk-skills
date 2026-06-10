#!/usr/bin/env python3
"""
skill_authoring_checker.py - Rich-Audit v2.6.7 skill authoring best practices checker

Per platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices:
  1. Frontmatter completeness (name / description / metadata.version / triggers / tags)
  2. Body length (≤ 200 lines per architecture-health threshold)
  3. Description quality (≥ 20 chars)
  4. Version semver (x.y.z)

Output: JSON. Exit 0 clean, 1 findings.

Usage: python3 ~/.agents/skills/rich-audit/scripts/skill_authoring_checker.py
"""
import json
import re
import sys
from pathlib import Path

SKILLS_DIR = Path.home() / ".agents" / "skills"
VERSION = "1.0.0"

REQUIRED_FIELDS = ["name", "description"]
RECOMMENDED_FIELDS = ["metadata.version", "metadata.category", "triggers", "tags",
                       "user-invocable", "license"]
MAX_BODY_LINES = 200
MIN_DESC_CHARS = 20
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+")


def parse_frontmatter(text: str) -> dict | None:
    m = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return None
    fm: dict = {}
    current_key = None
    for line in m.group(1).split("\n"):
        if re.match(r"^[a-zA-Z_][a-zA-Z0-9_.]*:", line):
            key, _, val = line.partition(":")
            val = val.strip()
            if val == "":
                current_key = key
                fm[key] = None
            else:
                current_key = None
                if val.startswith("|") or val.startswith(">"):
                    fm[key] = val
                else:
                    fm[key] = val.strip('"').strip("'")
        elif line.startswith("  ") and current_key:
            # continuation of list / block
            fm[current_key] = (fm.get(current_key) or "") + "\n" + line.strip()
    return fm


def get_nested(d: dict, dotted_key: str):
    cur = d
    for k in dotted_key.split("."):
        if not isinstance(cur, dict) or k not in cur:
            return None
        cur = cur[k]
    return cur


def check_skill(skill_dir: Path) -> list[dict]:
    findings: list[dict] = []
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return [{"type": "missing_skill_md", "path": str(skill_dir.relative_to(SKILLS_DIR.parent))}]
    try:
        text = skill_md.read_text(errors="ignore")
    except OSError:
        return [{"type": "read_error", "path": str(skill_md)}]
    rel = str(skill_dir.relative_to(SKILLS_DIR.parent))
    fm = parse_frontmatter(text)
    if fm is None:
        return [{"type": "missing_frontmatter", "path": rel}]
    for field in REQUIRED_FIELDS:
        if not fm.get(field):
            findings.append({
                "type": "missing_frontmatter_field",
                "path": rel,
                "field": field,
                "severity": "required",
            })
    for field in RECOMMENDED_FIELDS:
        if not get_nested(fm, field):
            findings.append({
                "type": "missing_frontmatter_field",
                "path": rel,
                "field": field,
                "severity": "recommended",
            })
    desc = fm.get("description", "")
    if isinstance(desc, str) and len(desc.strip()) < MIN_DESC_CHARS:
        findings.append({
            "type": "description_too_short",
            "path": rel,
            "actual_chars": len(desc.strip()),
            "min_chars": MIN_DESC_CHARS,
        })
    version = get_nested(fm, "metadata.version")
    if version and isinstance(version, str) and not SEMVER_RE.match(version):
        findings.append({
            "type": "invalid_version",
            "path": rel,
            "version": version,
        })
    triggers = fm.get("triggers")
    if triggers and isinstance(triggers, str):
        trigger_list = [t.strip() for t in triggers.split("\n") if t.strip()]
        if not trigger_list:
            findings.append({"type": "no_triggers", "path": rel})
    body_lines = text.count("\n")
    if body_lines > MAX_BODY_LINES:
        findings.append({
            "type": "body_too_long",
            "path": rel,
            "actual_lines": body_lines,
            "max_lines": MAX_BODY_LINES,
        })
    return findings


def main() -> int:
    if not SKILLS_DIR.exists():
        print(json.dumps({"error": f"skills dir not found: {SKILLS_DIR}"}))
        return 1
    all_findings: list[dict] = []
    skills_scanned = 0
    for skill_dir in SKILLS_DIR.iterdir():
        if not skill_dir.is_dir():
            continue
        skills_scanned += 1
        all_findings.extend(check_skill(skill_dir))
    by_type: dict[str, int] = {}
    for f in all_findings:
        t = f.get("type", "unknown")
        by_type[t] = by_type.get(t, 0) + 1
    result = {
        "tool": "skill_authoring_checker.py",
        "version": VERSION,
        "skills_scanned": skills_scanned,
        "findings": all_findings,
        "count": len(all_findings),
        "by_type": by_type,
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if not all_findings else 1


if __name__ == "__main__":
    sys.exit(main())
