#!/usr/bin/env python3
"""
skill_overlap_enhancer.py - Rich-Audit v2.6.10 B: skill overlap strengthened

Per github.com/scottholdren/skill-audit (skill-audit patterns):
  1. Trigger overlap (已有, 在 commands_to_skills_migrator.py)
  2. Trigger prefix overlap (v2.6.10 新)
  3. Description noun overlap via Jaccard (v2.6.10 新)

Output: JSON {tool, version, skills_scanned, findings, count, by_type}
Exit 0 clean, 1 findings.

Usage: python3 ~/.agents/skills/rich-audit/scripts/skill_overlap_enhancer.py
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

SKILLS_DIR = Path.home() / ".agents" / "skills"
VERSION = "1.0.0"
MIN_DESC_OVERLAP = 0.3
MIN_PREFIX_COUNT = 3
NOUNS_RE = re.compile(r"\b[a-z]{4,}\b")  # 4+ 字母词当 noun proxy


def jaccard(a: set, b: set) -> float:
    union = a | b
    return len(a & b) / len(union) if union else 0.0


def get_description_nouns(text: str) -> set[str]:
    fm_match = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not fm_match:
        return set()
    desc_match = re.search(r"description:\s*\|?\s*\n?((?:\s+.+\n?)+)", fm_match.group(1))
    if not desc_match:
        return set()
    return set(NOUNS_RE.findall(desc_match.group(1).lower()))


def detect_prefix_overlap() -> list[dict]:
    prefixes: Counter = Counter()
    for skill_dir in SKILLS_DIR.iterdir():
        if not skill_dir.is_dir():
            continue
        parts = skill_dir.name.split("-")
        for prefix in parts[:-1]:
            if prefix:
                prefixes[prefix] += 1
    return [
        {"type": "trigger_prefix_overlap", "prefix": p, "count": c}
        for p, c in prefixes.most_common() if c >= MIN_PREFIX_COUNT
    ]


def detect_description_overlap() -> list[dict]:
    skill_nouns: dict[str, set[str]] = {}
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
        nouns = get_description_nouns(text)
        if nouns:
            skill_nouns[skill_dir.name] = nouns
    overlaps: list[dict] = []
    names = list(skill_nouns.keys())
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            sim = jaccard(skill_nouns[a], skill_nouns[b])
            if sim >= MIN_DESC_OVERLAP:
                shared = skill_nouns[a] & skill_nouns[b]
                overlaps.append({
                    "type": "description_overlap",
                    "skills": [a, b],
                    "jaccard": round(sim, 3),
                    "shared_nouns": sorted(shared)[:10],
                })
    return overlaps


def main() -> int:
    if not SKILLS_DIR.exists():
        print(json.dumps({"error": f"skills dir not found: {SKILLS_DIR}"}))
        return 1
    findings: list[dict] = []
    findings.extend(detect_prefix_overlap())
    findings.extend(detect_description_overlap())
    skills_scanned = sum(1 for d in SKILLS_DIR.iterdir() if d.is_dir())
    by_type: dict[str, int] = {}
    for f in findings:
        t = f.get("type", "unknown")
        by_type[t] = by_type.get(t, 0) + 1
    result = {
        "tool": "skill_overlap_enhancer.py",
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
