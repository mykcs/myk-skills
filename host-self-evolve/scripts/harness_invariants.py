#!/usr/bin/env python3
"""Check the host-level invariants shared by Claude Code and Codex.

This checker is deliberately read-only. It validates the architectural boundaries
owned by the shared harness control plane without modifying either consumer.

Usage:
  python3 harness_invariants.py
  python3 harness_invariants.py --home /tmp/fake-home

Exit status is 0 when all invariants hold, 1 when drift is found, and 2 when a
configuration file cannot be parsed.
"""
from __future__ import annotations

import argparse
import json
import sys
import tomllib
from pathlib import Path
from typing import Any

VERSION = "1.1.0"


def finding(kind: str, path: Path, detail: str) -> dict[str, str]:
    return {"type": kind, "path": str(path), "detail": detail}


def load_json(path: Path) -> tuple[dict[str, Any] | None, list[dict[str, str]]]:
    if not path.is_file():
        return None, [finding("config_missing", path, "required JSON config is missing")]
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return None, [finding("config_invalid", path, str(error))]
    if not isinstance(value, dict):
        return None, [finding("config_invalid", path, "top-level JSON value must be an object")]
    return value, []


def load_toml(path: Path) -> tuple[dict[str, Any] | None, list[dict[str, str]]]:
    if not path.is_file():
        return None, [finding("config_missing", path, "required TOML config is missing")]
    try:
        value = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as error:
        return None, [finding("config_invalid", path, str(error))]
    return value, []


def audit_codex(home: Path) -> list[dict[str, str]]:
    path = home / ".codex" / "config.toml"
    data, errors = load_toml(path)
    if data is None:
        return errors
    findings = list(errors)

    mcp = data.get("mcp_servers", {})
    if isinstance(mcp, dict) and "memory-1" in mcp:
        findings.append(finding(
            "codex_duplicate_memory_plane",
            path,
            "mcp_servers.memory-1 must stay removed; native Codex Memories is the only runtime memory plane",
        ))

    memories = data.get("memories", {})
    expected_memories = {
        "generate_memories": False,
        "use_memories": True,
        "disable_on_external_context": True,
    }
    for key, expected in expected_memories.items():
        actual = memories.get(key) if isinstance(memories, dict) else None
        if actual is not expected:
            findings.append(finding(
                "codex_memory_policy_drift",
                path,
                f"memories.{key} expected {expected!r}, got {actual!r}",
            ))

    if data.get("approval_policy") != "on-request":
        findings.append(finding(
            "codex_default_approval_drift",
            path,
            f"approval_policy expected 'on-request', got {data.get('approval_policy')!r}",
        ))
    if data.get("sandbox_mode") != "workspace-write":
        findings.append(finding(
            "codex_default_sandbox_drift",
            path,
            f"sandbox_mode expected 'workspace-write', got {data.get('sandbox_mode')!r}",
        ))

    workspace = data.get("sandbox_workspace_write", {})
    if not isinstance(workspace, dict) or workspace.get("network_access") is not True:
        findings.append(finding(
            "codex_workspace_network_drift",
            path,
            "sandbox_workspace_write.network_access must remain true for autonomous normal development",
        ))

    projects = data.get("projects", {})
    home_project = projects.get(str(home)) if isinstance(projects, dict) else None
    if isinstance(home_project, dict) and home_project.get("trust_level") == "trusted":
        findings.append(finding(
            "codex_home_trust_too_broad",
            path,
            f"catch-all trusted project for {home} must stay removed",
        ))

    profiles = data.get("profiles", {})
    full_access = profiles.get("full-access") if isinstance(profiles, dict) else None
    if not isinstance(full_access, dict) or (
        full_access.get("approval_policy") != "never"
        or full_access.get("sandbox_mode") != "danger-full-access"
    ):
        findings.append(finding(
            "codex_full_access_escape_hatch_drift",
            path,
            "profiles.full-access must preserve the explicit opt-in unrestricted escape hatch",
        ))
    return findings


def pretool_bash_commands(settings: dict[str, Any]) -> list[str]:
    commands: list[str] = []
    hooks = settings.get("hooks", {})
    groups = hooks.get("PreToolUse", []) if isinstance(hooks, dict) else []
    if not isinstance(groups, list):
        return commands
    for group in groups:
        if not isinstance(group, dict) or group.get("matcher") != "Bash":
            continue
        for hook in group.get("hooks", []):
            if isinstance(hook, dict) and isinstance(hook.get("command"), str):
                commands.append(hook["command"])
    return commands


def audit_claude(home: Path) -> list[dict[str, str]]:
    path = home / ".claude" / "settings.json"
    data, errors = load_json(path)
    if data is None:
        return errors
    findings = list(errors)

    permissions = data.get("permissions", {})
    if not isinstance(permissions, dict):
        permissions = {}
    if permissions.get("defaultMode") != "acceptEdits":
        findings.append(finding(
            "claude_default_mode_drift",
            path,
            f"permissions.defaultMode expected 'acceptEdits', got {permissions.get('defaultMode')!r}",
        ))

    allow = permissions.get("allow", [])
    allow = allow if isinstance(allow, list) else []
    blanket = sorted({rule for rule in allow if rule in {"Bash(*)", "Read(*)", "Write(*)", "Edit(*)"}})
    if blanket:
        findings.append(finding(
            "claude_blanket_permission_regression",
            path,
            f"blanket allow rules reintroduced: {blanket}",
        ))
    stale_memory = sorted(rule for rule in allow if isinstance(rule, str) and rule.startswith("mcp__memory"))
    if stale_memory:
        findings.append(finding(
            "claude_stale_memory_mcp_permission",
            path,
            f"retired memory MCP permission(s) reintroduced: {stale_memory}",
        ))
    stale_minimax = sorted(rule for rule in allow if isinstance(rule, str) and rule.startswith("mcp__MiniMax__"))
    if stale_minimax:
        findings.append(finding(
            "claude_retired_minimax_mcp_permission",
            path,
            f"MiniMax platform routing is mmx-CLI-only; retired MCP permission(s) reintroduced: {stale_minimax}",
        ))

    sandbox = data.get("sandbox", {})
    if not isinstance(sandbox, dict) or sandbox.get("enabled") is not True:
        findings.append(finding("claude_sandbox_disabled", path, "sandbox.enabled must remain true"))
    if not isinstance(sandbox, dict) or sandbox.get("autoAllowBashIfSandboxed") is not True:
        findings.append(finding(
            "claude_sandbox_autonomy_drift",
            path,
            "sandbox.autoAllowBashIfSandboxed must remain true",
        ))

    commands = pretool_bash_commands(data)
    combined = [command for command in commands if "combined-bash-guard.py" in command]
    if len(combined) != 1:
        findings.append(finding(
            "claude_bash_guard_mount_drift",
            path,
            f"expected exactly one combined-bash-guard.py PreToolUse[Bash] mount, got {len(combined)}",
        ))
    retired = [
        command for command in commands
        if "skills-symlink-guard.py" in command or "verify-lark-cli-data.py" in command
    ]
    if retired:
        findings.append(finding(
            "claude_retired_bash_guard_remounted",
            path,
            f"retired standalone guard(s) remounted: {retired}",
        ))
    return findings


def audit_shared_control_plane(home: Path) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    expected = {
        "shared_instruction_source_missing": home / ".agents" / "AGENTS.md",
        "projection_compiler_missing": home / ".agents" / "bin" / "compile-agent-instructions.sh",
        "claude_projection_missing": home / ".claude" / "CLAUDE.md",
        "codex_projection_missing": home / ".codex" / "AGENTS.md",
    }
    for kind, path in expected.items():
        if not path.exists():
            findings.append(finding(kind, path, "required shared-control-plane artifact is missing"))
    return findings


def audit_home(home: Path) -> list[dict[str, str]]:
    home = home.expanduser().resolve()
    return [
        *audit_shared_control_plane(home),
        *audit_claude(home),
        *audit_codex(home),
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--home", type=Path, default=Path.home(), help="home directory to audit")
    args = parser.parse_args()

    findings = audit_home(args.home)
    result = {
        "tool": "harness_invariants.py",
        "version": VERSION,
        "home": str(args.home.expanduser().resolve()),
        "ok": not findings,
        "count": len(findings),
        "findings": findings,
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if any(item["type"] == "config_invalid" for item in findings):
        return 2
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
