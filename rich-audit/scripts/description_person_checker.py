#!/usr/bin/env python3
"""
description_person_checker.py - Rich-Audit v2.6.13 new detection dimension 1

Detects first/second-person pronouns in SKILL.md description field, per
Anthropic Skills Best Practices:
  "Always write in third person. The description is injected into the system
   prompt, and inconsistent point-of-view can cause discovery problems."

Reference: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices

Bad examples:
  - "I can help you process Excel files"   ❌
  - "You can use this to process..."        ❌
  - "我可以帮您处理表格"                       ❌

Good examples:
  - "Processes Excel files and generates reports"  ✅
  - "Extracts text from PDFs"                       ✅

Output: JSON to stdout. Exit 0 if clean, 1 if findings present.

Usage: python3 ~/.agents/skills/rich-audit/scripts/description_person_checker.py
"""
import json
import re
import sys
from pathlib import Path

SKILLS_DIRS = [
    Path.home() / ".agents" / "skills",
    Path.home() / ".claude" / "skills",
]

VERSION = "1.0.0"

# English first/second person pronouns (word-boundary).
# Avoid common false positives: "you" inside compound words, technical terms.
EN_PRONOUNS_RE = re.compile(
    r"\b(?:I|me|my|mine|myself|you|your|yours|yourself|we|us|our|ours|ourselves)\b",
    re.IGNORECASE,
)

# Chinese first/second person pronouns. 「我们」/「咱们」 included.
ZH_PRONOUNS_RE = re.compile(r"(?:我|我们|您|你|你们|咱|咱们)")

# Frontmatter parser: extract description field even if multi-line (`description: |`)
DESC_RE = re.compile(
    r"^description:\s*(\|[+-]?)?\s*\n?((?:.*?)(?=\n\w+:|\n---|\Z))",
    re.MULTILINE | re.DOTALL,
)


def extract_description(skill_md_text: str) -> str:
    """Extract YAML description field value, handling both inline and `|` block."""
    fm_match = re.match(r"^---\n(.*?)\n---", skill_md_text, re.DOTALL)
    if not fm_match:
        return ""
    fm = fm_match.group(1)
    # Find description: key
    desc_match = re.search(
        r"^description:\s*(\|[+-]?)?\s*\n?(.*?)(?=\n[a-zA-Z_-]+:|\Z)",
        fm,
        re.MULTILINE | re.DOTALL,
    )
    if not desc_match:
        return ""
    raw = desc_match.group(2).strip()
    # Strip leading "|" marker if any
    raw = re.sub(r"^\|[+-]?\s*\n?", "", raw)
    return raw.strip()


def check_skill(skill_dir: Path) -> dict | None:
    """Check one skill's description for pronoun violations. Return finding or None."""
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return None
    try:
        text = skill_md.read_text(errors="ignore")
    except OSError:
        return None
    description = extract_description(text)
    if not description:
        return None
    en_hits = EN_PRONOUNS_RE.findall(description)
    zh_hits = ZH_PRONOUNS_RE.findall(description)
    if not en_hits and not zh_hits:
        return None
    return {
        "type": "description_non_third_person",
        "path": str(skill_dir.relative_to(skill_dir.parent.parent)),
        "skill": skill_dir.name,
        "en_pronouns": sorted(set(en_hits)),
        "zh_pronouns": sorted(set(zh_hits)),
        "description_preview": description[:200],
        "severity": "recommended",
    }


def main() -> int:
    findings: list[dict] = []
    skills_scanned = 0
    seen_skill_dirs: set[Path] = set()
    for skills_dir in SKILLS_DIRS:
        if not skills_dir.exists():
            continue
        for skill_dir in skills_dir.iterdir():
            if not skill_dir.is_dir():
                continue
            # Resolve symlinks to avoid double-counting
            real = skill_dir.resolve()
            if real in seen_skill_dirs:
                continue
            seen_skill_dirs.add(real)
            skills_scanned += 1
            finding = check_skill(skill_dir)
            if finding:
                findings.append(finding)
    by_type: dict[str, int] = {}
    for f in findings:
        t = f.get("type", "unknown")
        by_type[t] = by_type.get(t, 0) + 1
    result = {
        "tool": "description_person_checker.py",
        "version": VERSION,
        "skills_scanned": skills_scanned,
        "findings": findings,
        "count": len(findings),
        "by_type": by_type,
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if not findings else 1


if __name__ == "__main__":
    sys.exit(main())
