#!/usr/bin/env python3
"""
skill_authoring_checker.py - Rich-Audit v2.6.16 skill authoring best practices checker

Per code.claude.com/docs/en/skills (2026-06 spec):
  * "All fields are optional. Only description is recommended so Claude knows when to use the skill."
  * name: optional, defaults to directory name
  * description: recommended, truncated at 1,536 chars combined with when_to_use
  * allowed-tools / disallowed-tools: optional (CLI-only)

Per rich-audit Layer 3 Force-All-Search 2026-06-12 + user feedback "下次也不改 直接解决"
(CASE-RICH-AUDIT-DEEP-20260612 follow-up):

v2.6.16 (2026-06-12) noise reduction:
  - INFORMATIONAL_FIELDS missing findings (metadata.*, triggers, tags, license)
    are NO LONGER emitted by default (was producing 405 LOW noise across 95 skills).
  - Pass --include-informational to opt-in (e.g. for skill authoring review session).
  - This reflects user-confirmed convention: optional fields are TRULY optional.
    Reporting them as findings (even at LOW) inflated audit health score impact +
    created "next audit will improve" theater that never materialized.

Output: JSON. Exit 0 clean, 1 findings.

Usage:
  python3 ~/.agents/skills/rich-audit/scripts/skill_authoring_checker.py
  python3 ~/.agents/skills/rich-audit/scripts/skill_authoring_checker.py --include-informational
"""
import argparse
import json
import re
import sys
from pathlib import Path

SKILLS_DIR = Path.home() / ".agents" / "skills"
VERSION = "1.1.2"

# Per Anthropic docs 2026-06: ALL frontmatter fields are optional.
# Only `description` is "recommended" — promote to MED, others to LOW.
RECOMMENDED_FIELDS_MED = ["description"]            # missing = MED
RECOMMENDED_FIELDS_LOW = ["name"]                    # missing = LOW (fallback to dir name)
# v2.6.16: INFORMATIONAL_FIELDS no longer emitted by default — see docstring.
INFORMATIONAL_FIELDS = ["metadata.version", "metadata.category", "triggers", "tags",
                        "user-invocable", "license"]
# Per platform.claude.com best-practices: SKILL.md body < 500 lines recommended.
# v2.6.15 (2026-06-12): aligned 200→500 (was over-strict by 60% vs official docs).
MAX_BODY_LINES = 500
MIN_DESC_CHARS = 20
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+")

# v2.6.15 (2026-06-12): nested skill subdirectories that intentionally
# do NOT have a top-level SKILL.md (they contain their own sub-skills).
# Was causing 22 false positive `missing_skill_md` findings.
NESTED_SKILL_DIRS: set[str] = {
    "go", "core", "python", "plugins", "references", "typescript",
    "java", "shared", "docs", "php", "cpp", "kotlin", "golang",
    "settings", "code-review", "skills", "scripts", "utils",
    # Repo / docs / assets dirs that are not skills themselves
    ".git", ".github", ".omc", ".claude-plugin",
    "assets", "examples", "reference", "themes", "templates",
    "csharp", "ruby",
}


def parse_frontmatter(text: str) -> dict | None:
    m = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return None
    fm: dict = {}
    current_key = None
    block_mode = False  # True when inside a '|' or '>' YAML block scalar
    for raw_line in m.group(1).split("\n"):
        line = raw_line.rstrip()
        key_match = re.match(r"^([a-zA-Z_][a-zA-Z0-9_.]*):\s*(.*)$", line)
        if key_match:
            key, val = key_match.group(1), key_match.group(2).strip()
            current_key = key
            block_mode = False
            if val == "":
                fm[key] = None
            elif val.startswith("|") or val.startswith(">"):
                fm[key] = ""
                block_mode = True
            else:
                fm[key] = val.strip('"').strip("'")
        elif block_mode and current_key is not None:
            # Continue the block scalar, preserving line breaks roughly
            fm[current_key] = (fm.get(current_key) or "") + "\n" + line
        elif line.startswith("  ") and current_key is not None and fm.get(current_key) is None:
            # Nested mapping under a key with no value, e.g. metadata:\n  version: ...
            nested_match = re.match(r"^\s+([a-zA-Z_][a-zA-Z0-9_.]*):\s*(.*)$", line)
            if nested_match:
                nested_key, nested_val = nested_match.group(1), nested_match.group(2).strip()
                full_key = f"{current_key}.{nested_key}"
                if nested_val == "":
                    fm[full_key] = None
                elif nested_val.startswith("|") or nested_val.startswith(">"):
                    fm[full_key] = ""
                    block_mode = True
                    current_key = full_key
                else:
                    fm[full_key] = nested_val.strip('"').strip("'")
    return fm


def get_nested(d: dict, dotted_key: str):
    cur = d
    for k in dotted_key.split("."):
        if not isinstance(cur, dict) or k not in cur:
            return None
        cur = cur[k]
    return cur


def check_skill(skill_dir: Path, include_informational: bool = False) -> list[dict]:
    findings: list[dict] = []
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        rel = str(skill_dir.relative_to(SKILLS_DIR.parent))
        # v2.6.15: skip nested skill subdirs (they contain sub-skills, not a SKILL.md)
        skill_name = skill_dir.name
        if skill_name in NESTED_SKILL_DIRS:
            return []
        return [{"type": "missing_skill_md", "path": rel,
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
    # v2.6.16: informational fields ONLY when explicitly requested.
    # Default audit run treats their absence as zero noise (per user feedback 2026-06-12).
    if include_informational:
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
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--include-informational", action="store_true",
                        help="Include missing INFORMATIONAL_FIELDS (metadata.*/triggers/tags/license) as LOW findings. "
                             "Off by default (v2.6.16): they are truly optional per Anthropic spec.")
    args = parser.parse_args()

    if not SKILLS_DIR.exists():
        print(json.dumps({"error": f"skills dir not found: {SKILLS_DIR}"}))
        return 1
    all_findings: list[dict] = []
    skills_scanned = 0
    for skill_dir in SKILLS_DIR.iterdir():
        if not skill_dir.is_dir():
            continue
        skills_scanned += 1
        all_findings.extend(check_skill(skill_dir, include_informational=args.include_informational))
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
        "include_informational": args.include_informational,
        "findings": all_findings,
        "count": len(all_findings),
        "by_type": by_type,
        "by_severity": by_severity,
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    # v2.6.14 fix: exit 0 on successful execution. See dead_code_detector.py for rationale.
    return 0


if __name__ == "__main__":
    sys.exit(main())
