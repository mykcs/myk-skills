#!/usr/bin/env python3
"""
waste_token_detector.py - host harness wasted-context detector

Host harness checks (dead weight, conflicts, stale rules, wasted context tokens):
  1. Hot path heavy (> 3000 estimated tokens, loaded every session)
  2. Skill too heavy (> 3000 estimated tokens, loaded on demand)
  3. Stale hot path (> 30 days, not modified)

Output: JSON {tool, version, findings, count, by_type, total_hot_path_tokens}
Exit 0 after a successful audit; findings are informational JSON records.

Usage: python3 ~/.agents/skills/host-self-evolve/scripts/waste_token_detector.py
"""
import json
import re
import subprocess
import sys
import time
from pathlib import Path

CLAUDE_DIR = Path.home() / ".claude"
AGENTS_DIR = Path.home() / ".agents"
CODEX_DIR = Path.home() / ".codex"
KIMI_DIR = Path.home() / ".kimi-code"
SKILLS_DIR = Path.home() / ".agents" / "skills"
PLUGIN_MANIFEST = SKILLS_DIR / ".claude-plugin" / "plugin.json"
PROJECTION_COMPILER = AGENTS_DIR / "bin" / "compile-agent-instructions.sh"
VERSION = "1.1.0"
# v1.0.1 (2026-06-12): per official Claude Code docs, SKILL.md body < 500 lines
# (≈ 3000 tokens for prose markdown). Was 1500 (over-strict by 50%).
# For skills still > 3000 tokens, recommend progressive disclosure (move detail
# sections to references/ subfolder).
WARN_TOKENS = 3000
STALE_DAYS = 30

HOT_PATHS = [
    CLAUDE_DIR / "rules",
    CLAUDE_DIR / "CLAUDE.md",
    CLAUDE_DIR / "CLAUDE.local.md",
    CLAUDE_DIR / "hot-facts.md",
]


def estimate_tokens(text: str) -> int:
    return len(text) // 4


def frontmatter_block(text: str) -> str:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return ""
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            return "\n".join(lines[1:index])
    return ""


def frontmatter_text_field(block: str, field: str) -> str:
    lines = block.splitlines()
    prefix = f"{field}:"
    for index, line in enumerate(lines):
        if not line.startswith(prefix):
            continue
        value = line[len(prefix):].strip()
        if value not in {"|", ">"}:
            return value.strip("'\"")
        collected: list[str] = []
        for child in lines[index + 1:]:
            if child and not child[0].isspace():
                break
            collected.append(child.strip())
        return " ".join(part for part in collected if part)
    return ""


def iter_active_skill_files():
    if not SKILLS_DIR.exists():
        return
    for skill_dir in SKILLS_DIR.iterdir():
        skill_md = skill_dir / "SKILL.md"
        if skill_dir.is_dir() and skill_md.is_file():
            yield skill_md


def iter_cold_skill_files():
    for bucket in (SKILLS_DIR / "_archive", SKILLS_DIR / "_disabled"):
        if bucket.exists():
            yield from bucket.rglob("SKILL.md")


def skill_listing_inventory() -> dict:
    active_files = list(iter_active_skill_files())
    cold_files = list(iter_cold_skill_files())

    def listing_chars(paths: list[Path]) -> int:
        total = 0
        for path in paths:
            text = path.read_text(errors="ignore")
            block = frontmatter_block(text)
            total += len(frontmatter_text_field(block, "description"))
            total += len(frontmatter_text_field(block, "when_to_use"))
        return total

    manual_only = 0
    for path in active_files:
        block = frontmatter_block(path.read_text(errors="ignore"))
        if re.search(r"^disable-model-invocation:\s*true\s*$", block, re.MULTILINE):
            manual_only += 1

    active_chars = listing_chars(active_files)
    cold_chars = listing_chars(cold_files)
    return {
        "active_count": len(active_files),
        "active_description_chars": active_chars,
        "active_description_tokens_estimate": estimate_tokens("x" * active_chars),
        "manual_only_count": manual_only,
        "cold_count": len(cold_files),
        "cold_description_chars": cold_chars,
    }


def instruction_projection_tokens() -> dict[str, int]:
    consumers = {
        "source": AGENTS_DIR / "AGENTS.md",
        "claude": CLAUDE_DIR / "CLAUDE.md",
        "codex": CODEX_DIR / "AGENTS.md",
        "kimi": KIMI_DIR / "AGENTS.md",
    }
    result: dict[str, int] = {}
    for name, path in consumers.items():
        if path.exists():
            result[name] = estimate_tokens(path.read_text(errors="ignore"))
    return result


def is_path_scoped(text: str) -> bool:
    """Match Claude rule frontmatter, not nested metadata.paths fields."""
    block = frontmatter_block(text)
    return bool(re.search(r"^paths:\s*", block, flags=re.MULTILINE))


def iter_rule_files():
    rules_dir = CLAUDE_DIR / "rules"
    if not rules_dir.exists():
        return
    yield from (p for p in rules_dir.rglob("*.md") if p.is_file())


def iter_resident_rule_files():
    yield from (p for p in iter_rule_files() if not is_path_scoped(p.read_text(errors="ignore")))


def detect_hot_path_heavy() -> list[dict]:
    findings: list[dict] = []
    for p in HOT_PATHS:
        candidates = iter_resident_rule_files() if p == CLAUDE_DIR / "rules" else [p]
        for candidate in candidates:
            if not candidate.is_file():
                continue
            try:
                tokens = estimate_tokens(candidate.read_text(errors="ignore"))
            except OSError:
                continue
            if tokens > WARN_TOKENS:
                findings.append({
                    "type": "hot_path_heavy",
                    "path": str(candidate.relative_to(CLAUDE_DIR.parent)),
                    "tokens": tokens,
                })
    return findings


def detect_skill_too_heavy() -> list[dict]:
    findings: list[dict] = []
    if not SKILLS_DIR.exists():
        return findings
    for skill_dir in SKILLS_DIR.iterdir():
        if not skill_dir.is_dir():
            continue
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            continue
        try:
            tokens = estimate_tokens(skill_md.read_text(errors="ignore"))
        except OSError:
            continue
        if tokens > WARN_TOKENS:
            findings.append({
                "type": "skill_too_heavy",
                "path": str(skill_dir.relative_to(SKILLS_DIR.parent)),
                "tokens": tokens,
            })
    return findings


def detect_cross_tool_instruction_leak() -> list[dict]:
    findings: list[dict] = []
    consumers = {
        CLAUDE_DIR / "CLAUDE.md": ("Codex 专属", "Kimi 专属"),
        CODEX_DIR / "AGENTS.md": ("Claude Code 专属", "Kimi 专属"),
        KIMI_DIR / "AGENTS.md": ("Claude Code 专属", "Codex 专属"),
    }
    for path, forbidden in consumers.items():
        if not path.exists():
            continue
        text = path.read_text(errors="ignore")
        leaked = [heading for heading in forbidden if heading in text]
        if leaked:
            findings.append({
                "type": "cross_tool_instruction_leak",
                "path": str(path),
                "sections": leaked,
            })
    return findings


def detect_plugin_skill_scope_broad() -> list[dict]:
    if not PLUGIN_MANIFEST.exists():
        return []
    try:
        manifest = json.loads(PLUGIN_MANIFEST.read_text())
    except (OSError, json.JSONDecodeError):
        return [{"type": "plugin_manifest_invalid", "path": str(PLUGIN_MANIFEST)}]
    configured = manifest.get("skills")
    if configured == "./":
        return [{
            "type": "plugin_skill_scope_broad",
            "path": str(PLUGIN_MANIFEST),
            "detail": "plugin recursively exposes archive and disabled skills",
        }]
    if not isinstance(configured, list):
        return [{
            "type": "plugin_skill_scope_invalid",
            "path": str(PLUGIN_MANIFEST),
            "detail": "skills must be an explicit directory list",
        }]
    active = {path.parent.name for path in iter_active_skill_files()}
    exposed = {
        entry.removeprefix("./").rstrip("/")
        for entry in configured
        if isinstance(entry, str)
    }
    missing = sorted(active - exposed)
    extra = sorted(exposed - active)
    if missing or extra or len(exposed) != len(configured):
        return [{
            "type": "plugin_skill_scope_drift",
            "path": str(PLUGIN_MANIFEST),
            "missing": missing,
            "extra": extra,
        }]
    return []


def detect_instruction_projection_stale() -> list[dict]:
    if not PROJECTION_COMPILER.is_file():
        return [{
            "type": "instruction_projection_compiler_missing",
            "path": str(PROJECTION_COMPILER),
        }]
    try:
        result = subprocess.run(
            [str(PROJECTION_COMPILER), "--check"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        return [{
            "type": "instruction_projection_check_failed",
            "path": str(PROJECTION_COMPILER),
            "detail": str(error),
        }]
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()[:500]
        return [{
            "type": "instruction_projection_stale",
            "path": str(AGENTS_DIR / "AGENTS.md"),
            "detail": detail,
        }]
    return []


def detect_stale_hot_path() -> list[dict]:
    findings: list[dict] = []
    for p in iter_resident_rule_files():
        try:
            age_days = (time.time() - p.stat().st_mtime) / 86400
        except OSError:
            continue
        if age_days > STALE_DAYS:
            findings.append({
                "type": "stale_hot_path",
                "path": str(p.relative_to(CLAUDE_DIR.parent)),
                "age_days": round(age_days, 1),
            })
    return findings


def main() -> int:
    findings: list[dict] = []
    findings.extend(detect_hot_path_heavy())
    findings.extend(detect_skill_too_heavy())
    findings.extend(detect_stale_hot_path())
    findings.extend(detect_cross_tool_instruction_leak())
    findings.extend(detect_plugin_skill_scope_broad())
    findings.extend(detect_instruction_projection_stale())
    by_type: dict[str, int] = {}
    for f in findings:
        t = f.get("type", "unknown")
        by_type[t] = by_type.get(t, 0) + 1
    # total hot path tokens (resident rules + Claude projection)
    total_hot = 0
    for p in iter_resident_rule_files():
        try:
            total_hot += estimate_tokens(p.read_text(errors="ignore"))
        except OSError:
            continue
    for p in (CLAUDE_DIR / "CLAUDE.md", CLAUDE_DIR / "CLAUDE.local.md", CLAUDE_DIR / "hot-facts.md"):
        if p.exists():
            try:
                total_hot += estimate_tokens(p.read_text(errors="ignore"))
            except OSError:
                continue
    result = {
        "tool": "waste_token_detector.py",
        "version": VERSION,
        "findings": findings,
        "count": len(findings),
        "by_type": by_type,
        "total_hot_path_tokens": total_hot,
        "instruction_projection_tokens": instruction_projection_tokens(),
        "skill_listing": skill_listing_inventory(),
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    # v2.6.14 fix: exit 0 on successful execution. See dead_code_detector.py for rationale.
    return 0


if __name__ == "__main__":
    sys.exit(main())
