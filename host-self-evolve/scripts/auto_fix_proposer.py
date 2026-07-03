#!/usr/bin/env python3
"""
auto_fix_proposer.py - Rich-Audit v2.6.11 auto-fix Level 2 proposer

Per scope discipline: NOT auto-applied. Generates fix proposals only.

Input:  findings JSON via stdin OR --input <file>
Output: JSON {tool, version, proposals, count, requires_user_review_count}

For each finding type, generates a proposal with:
  - risk_level: high / medium / low
  - requires_user_review: bool
  - proposed_change: human-readable description
  - before / after: file path or content snippet

Usage:
  python3 dead_code_detector.py | python3 auto_fix_proposer.py
  python3 auto_fix_proposer.py --input findings.json
"""
import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

VERSION = "1.0.0"
ARCHIVE_PREFIX = "archive-" + datetime.now().strftime("%Y-%m-%d")

# Tier 3 (intent-required): always needs user review regardless of risk
TIER3_INTENT_TYPES = frozenset({
    "rename_skill", "delete_skill", "merge_strategy",
    "rename_rule", "delete_rule",
})


def tier_for(risk_level: str, finding_type: str = "") -> int:
    """Determine tier from risk + finding type.

    Tier 1: low risk, mechanical safe (auto-executable)
    Tier 2: medium risk, 语义安全 (auto-executable + 30-min revert window)
    Tier 3: high risk OR intent-required type (needs user review)
    """
    if finding_type in TIER3_INTENT_TYPES:
        return 3
    if risk_level == "high":
        return 3
    if risk_level == "medium":
        return 2
    return 1  # low or unknown


def should_require_user_review(risk_level: str, finding_type: str = "") -> bool:
    """Decision Pattern Reversal (2026-06-11): ONLY Tier 3 requires user review.

    See CASE-RICH-AUDIT-DECISION-PATTERN-REVERSAL-20260611.
    """
    return tier_for(risk_level, finding_type) == 3


def propose_dead_hook(f: dict) -> dict:
    path = f.get("path", "<unknown>")
    return {
        "type": "dead_hook",
        "risk_level": "high",
        "requires_user_review": True,
        "proposed_change": (
            f"从 ~/.claude/settings.json 删除对 {path} 的 hook 引用; "
            f"如确认无用, 删除文件 {path} 本身"
        ),
        "before": f"(hook entry in settings.json for {path})",
        "after": "(removed from settings.json)",
        "manual_steps": [
            f"1. 编辑 ~/.claude/settings.json, 找到对 {path} 的 hook 引用, 整段删除",
            f"2. 如果确认永久不用, 跑 `rm {path}`",
            f"3. 跑 python3 ~/.agents/skills/rich-audit/scripts/dead_code_detector.py 重新验证",
        ],
    }


def propose_dead_script(f: dict) -> dict:
    path = f.get("path", "<unknown>")
    return {
        "type": "dead_script",
        "risk_level": "medium",
        "requires_user_review": True,
        "proposed_change": f"把 {path} 移到 ~/.claude/{ARCHIVE_PREFIX}/{path} (软删除)",
        "before": f"~/.claude/{path}",
        "after": f"~/.claude/{ARCHIVE_PREFIX}/{path}",
        "manual_steps": [
            f"1. mkdir -p ~/.claude/{ARCHIVE_PREFIX}/",
            f"2. mv ~/.claude/{path} ~/.claude/{ARCHIVE_PREFIX}/{path}",
            f"3. (30 天后如仍无人用) 永久删除",
        ],
    }


def propose_orphan_case(f: dict) -> dict:
    path = f.get("path", "<unknown>")
    return {
        "type": "orphan_case",
        "risk_level": "low",
        "requires_user_review": True,
        "proposed_change": f"在 case 文件头部加 'ARCHIVED: <reason>' 标记, 不删除",
        "before": f"{path}",
        "after": f"{path}  (with 'ARCHIVED:' prefix in first line)",
        "manual_steps": [
            f"1. 编辑 {path}",
            f"2. 在 frontmatter 之后第一行加: '> ARCHIVED: not referenced in MEMORY.md as of 2026-06-10'",
            f"3. 不要删, 留作历史",
        ],
    }


def propose_orphan_skill(f: dict) -> dict:
    path = f.get("path", "<unknown>")
    return {
        "type": "orphan_skill",
        "risk_level": "medium",
        "requires_user_review": True,
        "proposed_change": f"给 {path} 的 SKILL.md frontmatter 加 'archived: true', 标记不再主动触发",
        "before": f"{path}/SKILL.md  (no archived field)",
        "after": f"{path}/SKILL.md  (with metadata.archived: true)",
        "manual_steps": [
            f"1. 编辑 {path}/SKILL.md",
            f"2. 在 frontmatter 加 metadata.archived: true",
            f"3. 触发词仍然存在, 但 skill 自己声明不主动 invoke",
        ],
    }


def propose_shellcheck(f: dict) -> dict:
    code = f.get("code", "")
    path = f.get("path", "<unknown>")
    line = f.get("line", 0)
    msg = f.get("message", "")
    sc_fix = {
        "SC2016": "single quote 不展开表达式, 改用 double quote",
        "SC2001": "sed 替换, 考虑用 bash 参数展开 ${var//pattern/repl}",
        "SC2086": "变量没加引号, 加双引号",
        "SC2034": "变量赋值但未使用, 删或加 export 标记使用",
        "SC2015": "A && B || C 模式, 改用 if/then/else",
        "SC2012": "ls | grep 模式, 改用 find 或 globs",
    }
    return {
        "type": "shellcheck",
        "risk_level": "low",
        "requires_user_review": True,
        "proposed_change": f"修 {path}:{line} 的 SC{code} ({sc_fix.get(code, msg)})",
        "before": f"{path}:{line}  ({msg})",
        "after": f"修 quote / 改用参数展开 / 改用 find, 等",
        "manual_steps": [
            f"1. 编辑 {path}",
            f"2. 跳到 L{line}, 按 SC{code} 文档修",
            f"3. 跑 shellcheck {path} 验证",
        ],
    }


def propose_missing_frontmatter_field(f: dict) -> dict:
    field = f.get("field", "<unknown>")
    severity = f.get("severity", "recommended")
    path = f.get("path", "<unknown>")
    defaults = {
        "metadata.version": "0.1.0",
        "metadata.category": "utilities",
        "triggers": "['/skill-name']",
        "tags": "[]",
        "user-invocable": "true",
        "license": "MIT",
    }
    default = defaults.get(field, "<TODO>")
    return {
        "type": "missing_frontmatter_field",
        "risk_level": "low" if severity == "recommended" else "medium",
        "requires_user_review": True,
        "proposed_change": f"给 {path} 的 SKILL.md frontmatter 加 {field}: {default}",
        "before": f"# {path}  (missing {field})",
        "after": f"# {path}  (with {field}: {default})",
        "manual_steps": [
            f"1. 编辑 {path}/SKILL.md",
            f"2. 在 frontmatter 加: {field}: {default}",
            f"3. 跑 python3 ~/.agents/skills/rich-audit/scripts/skill_authoring_checker.py 验证",
        ],
    }


PROPOSERS = {
    "dead_hook": propose_dead_hook,
    "dead_script": propose_dead_script,
    "orphan_case": propose_orphan_case,
    "orphan_skill": propose_orphan_skill,
    "shellcheck": propose_shellcheck,
    "missing_frontmatter_field": propose_missing_frontmatter_field,
}



def enrich_proposal(p: dict) -> dict:
    """Post-process: set tier + requires_user_review based on type + risk_level.

    Replaces hardcoded requires_user_review with tier-based logic.
    Decision Pattern Reversal (2026-06-11).
    """
    rl = p.get("risk_level", "unknown")
    pt = p.get("type", "")
    p["tier"] = tier_for(rl, pt)
    p["requires_user_review"] = should_require_user_review(rl, pt)
    return p


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", help="findings JSON file (default: stdin)")
    args = parser.parse_args()

    if args.input:
        data = json.loads(Path(args.input).read_text())
    else:
        data = json.loads(sys.stdin.read())

    findings = data.get("findings", [])
    proposals: list[dict] = []
    for f in findings:
        ftype = f.get("type", "")
        proposer = PROPOSERS.get(ftype)
        if proposer:
            proposals.append(enrich_proposal(proposer(f)))
        else:
            proposals.append(enrich_proposal({
                "type": ftype,
                "risk_level": "unknown",
                "requires_user_review": True,
                "proposed_change": f"无提议器: 需手动处理 {ftype}",
                "before": str(f),
                "after": "(manual)",
                "manual_steps": ["(no automated proposal)"],
            }))

    risk_counts: dict[str, int] = {}
    tier_counts: dict[int, int] = {1: 0, 2: 0, 3: 0}
    for p in proposals:
        rl = p.get("risk_level", "unknown")
        risk_counts[rl] = risk_counts.get(rl, 0) + 1
        t = p.get("tier", 0)
        tier_counts[t] = tier_counts.get(t, 0) + 1

    result = {
        "tool": "auto_fix_proposer.py",
        "version": VERSION,
        "proposals": proposals,
        "count": len(proposals),
        "risk_counts": risk_counts,
        "tier_counts": tier_counts,
        "requires_user_review_count": sum(1 for p in proposals if p.get("requires_user_review")),
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    # v2.6.14 fix: exit 0 on successful execution. See dead_code_detector.py for rationale.
    return 0


if __name__ == "__main__":
    sys.exit(main())
