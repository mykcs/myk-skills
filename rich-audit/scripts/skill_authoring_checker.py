#!/usr/bin/env python3
"""
skill_authoring_checker.py - Rich-Audit v2.6.14 skill authoring best practices checker

Per code.claude.com/docs/en/skills (2026-06 spec):
  * "All fields are optional. Only description is recommended so Claude knows when to use the skill."
  * name: optional, defaults to directory name
  * description: recommended, truncated at 1,536 chars combined with when_to_use
  * allowed-tools / disallowed-tools: optional (CLI-only)

Per rich-audit Layer 3 Force-All-Search 2026-06-12 (原 Tri-Search 2026-06-11, 2026-06-12 重命名 v2.7): previous checker was overly strict — 691
findings (621 missing_field) were near-all false positives. Loosened thresholds:

  1. Frontmatter completeness:
     - Missing `description`            → MED  (per official spec: only recommended)
     - Missing `name`                   → LOW  (per official spec: defaults to dir name)
     - Missing optional `metadata.*` / `triggers` / `tags` / `license` → LOW (informational)
  2. Body length (≤ 200 lines per architecture-health threshold) → still flagged
  3. Description quality (≥ 20 chars) → still flagged
  4. Version semver (x.y.z) → still flagged (when version is present)

Output: JSON. Exit 0 clean, 1 findings.

Usage: python3 ~/.agents/skills/rich-audit/scripts/skill_authoring_checker.py
"""
import json
import re
import sys
from pathlib import Path

SKILLS_DIR = Path.home() / ".agents" / "skills"
VERSION = "1.1.0"

# Per Anthropic docs 2026-06: ALL frontmatter fields are optional.
# Only `description` is "recommended" — promote to MED, others to LOW.
RECOMMENDED_FIELDS_MED = ["description"]            # missing = MED
RECOMMENDED_FIELDS_LOW = ["name"]                    # missing = LOW (fallback to dir name)
INFORMATIONAL_FIELDS = ["metadata.version", "metadata.category", "triggers", "tags",
                        "user-invocable", "license"]  # missing = LOW (informational only)
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
        return [{"type": "missing_skill_md", "path": str(skill_dir.relative_to(SKILLS_DIR.parent)),
                 "severity": "medium"}]
    try:
        text = skill_md.read_text(errors="ignore")
    except OSError:
        return [{"type": "read_error", "path": str(skill_md), "severity": "low"}]
    rel = str(skill_dir.relative_to(SKILLS_DIR.parent))
    fm = parse_frontmatter(text)
    if fm is None:
        return [{"type": "missing_frontmatter", "path": rel, "severity": "medium"}]

    # description is RECOMMENDED per Anthropic spec → MED severity
    for field in RECOMMENDED_FIELDS_MED:
        if not fm.get(field):
            findings.append({
                "type": "missing_frontmatter_field",
                "path": rel,
                "field": field,
                "severity": "medium",
            })
    # name is optional (falls back to dir name) → LOW
    for field in RECOMMENDED_FIELDS_LOW:
        if not fm.get(field):
            findings.append({
                "type": "missing_frontmatter_field",
                "path": rel,
                "field": field,
                "severity": "low",
            })
    # other fields are informational only — kept but LOW severity
    for field in INFORMATIONAL_FIELDS:
        if not get_nested(fm, field):
            findings.append({
                "type": "missing_frontmatter_field",
                "path": rel,
                "field": field,
                "severity": "low",
            })

    desc = fm.get("description", "")
    if isinstance(desc, str) and len(desc.strip()) < MIN_DESC_CHARS:
        findings.append({
            "type": "description_too_short",
            "path": rel,
            "actual_chars": len(desc.strip()),
            "min_chars": MIN_DESC_CHARS,
            "severity": "medium",
        })
    version = get_nested(fm, "metadata.version")
    if version and isinstance(version, str) and not SEMVER_RE.match(version):
        findings.append({
            "type": "invalid_version",
            "path": rel,
            "version": version,
            "severity": "low",
        })
    triggers = fm.get("triggers")
    if triggers and isinstance(triggers, str):
        trigger_list = [t.strip() for t in triggers.split("\n") if t.strip()]
        if not trigger_list:
            findings.append({"type": "no_triggers", "path": rel, "severity": "low"})
    body_lines = text.count("\n")
    if body_lines > MAX_BODY_LINES:
        findings.append({
            "type": "body_too_long",
            "path": rel,
            "actual_lines": body_lines,
            "max_lines": MAX_BODY_LINES,
            "severity": "medium",
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
    by_severity: dict[str, int] = {}
    for f in all_findings:
        t = f.get("type", "unknown")
        by_type[t] = by_type.get(t, 0) + 1
        s = f.get("severity", "unknown")
        by_severity[s] = by_severity.get(s, 0) + 1
    result = {
        "tool": "skill_authoring_checker.py",
        "version": VERSION,
        "skills_scanned": skills_scanned,
        "findings": all_findings,
        "count": len(all_findings),
        "by_type": by_type,
        "by_severity": by_severity,
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if not all_findings else 1


if __name__ == "__main__":
    sys.exit(main())
