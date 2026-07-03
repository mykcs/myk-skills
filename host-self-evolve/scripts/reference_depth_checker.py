#!/usr/bin/env python3
"""
reference_depth_checker.py - Rich-Audit v2.6.13 new detection dimension 3

Detects nested reference depth > 1 in SKILL.md, per Anthropic best practices:
  "Keep references one level deep from SKILL.md. All reference files should
   link directly from SKILL.md to ensure Claude reads complete files when needed."

Reference: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices

Bad example (2 levels deep):
  SKILL.md → advanced.md → details.md  ❌

Good example (1 level):
  SKILL.md → advanced.md (terminal)    ✅
  SKILL.md → reference.md (terminal)   ✅

Output: JSON to stdout. Exit 0 if clean, 1 if findings present.

Usage: python3 ~/.agents/skills/rich-audit/scripts/reference_depth_checker.py
"""
import json
import re
import sys
from pathlib import Path

SKILLS_DIRS = [
    Path.home() / ".agents" / "skills",
    Path.home() / ".claude" / "skills",
]

VERSION = "1.0.1"  # v1.0.1: skip sibling cross-links (ref2 in level1 set)

# Match markdown links to relative .md files inside same skill dir.
# Excludes external URLs (http/https) and absolute paths (/...).
MD_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)#:]+\.md)\)")


def find_internal_md_links(file_path: Path, skill_root: Path) -> set[Path]:
    """Return set of .md files referenced from `file_path` inside `skill_root`."""
    try:
        text = file_path.read_text(errors="ignore")
    except OSError:
        return set()
    refs: set[Path] = set()
    for _, link in MD_LINK_RE.findall(text):
        # Skip external / absolute / parent-escape links
        if link.startswith(("http://", "https://", "/", "../")):
            continue
        # Resolve relative to file_path's dir
        target = (file_path.parent / link).resolve()
        try:
            # Must stay inside skill root
            target.relative_to(skill_root.resolve())
        except ValueError:
            continue
        if target.suffix == ".md" and target.exists() and target != file_path:
            refs.add(target)
    return refs


def check_skill(skill_dir: Path) -> list[dict]:
    """Check skill: SKILL.md → level-1 refs → must NOT contain further .md refs.

    v1.0.1: skip findings where level-2 target is ALSO directly linked from
    SKILL.md (sibling cross-link, not true depth-2 nesting).
    """
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return []
    findings: list[dict] = []
    skill_root = skill_dir.resolve()
    # Level 1: refs from SKILL.md
    level1 = find_internal_md_links(skill_md, skill_dir)
    for ref1 in level1:
        # Level 2: refs from level-1 file
        level2 = find_internal_md_links(ref1, skill_dir)
        for ref2 in level2:
            # Skip if ref2 is also a direct SKILL.md link (sibling, not nested)
            if ref2 in level1:
                continue
            findings.append({
                "type": "reference_depth_exceeded",
                "skill": skill_dir.name,
                "from_level1": str(ref1.relative_to(skill_root)),
                "to_level2": str(ref2.relative_to(skill_root)),
                "depth": 2,
                "severity": "recommended",
                "fix": "Move level-2 ref to a direct SKILL.md link, or inline its content",
            })
    return findings


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
            real = skill_dir.resolve()
            if real in seen_skill_dirs:
                continue
            seen_skill_dirs.add(real)
            skills_scanned += 1
            findings.extend(check_skill(skill_dir))
    by_type: dict[str, int] = {}
    for f in findings:
        t = f.get("type", "unknown")
        by_type[t] = by_type.get(t, 0) + 1
    result = {
        "tool": "reference_depth_checker.py",
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
