"""Regression tests for scripts/harness_invariants.py."""
from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "harness_invariants.py"
SPEC = importlib.util.spec_from_file_location("harness_invariants", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def write(path: Path, text: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def healthy_home(root: Path) -> None:
    write(root / ".agents" / "AGENTS.md", "# shared\n")
    write(root / ".agents" / "bin" / "compile-agent-instructions.sh", "#!/bin/sh\n")
    write(root / ".claude" / "CLAUDE.md", "# claude projection\n")
    write(root / ".codex" / "AGENTS.md", "# codex projection\n")

    claude = {
        "permissions": {
            "defaultMode": "acceptEdits",
            "allow": ["mcp__context7__*"],
        },
        "sandbox": {
            "enabled": True,
            "autoAllowBashIfSandboxed": True,
        },
        "hooks": {
            "PreToolUse": [
                {
                    "matcher": "Bash",
                    "hooks": [
                        {
                            "type": "command",
                            "command": "python3 ~/.claude/hooks/combined-bash-guard.py",
                        }
                    ],
                }
            ]
        },
    }
    write(root / ".claude" / "settings.json", json.dumps(claude))

    codex = '''approval_policy = "on-request"
sandbox_mode = "workspace-write"

[sandbox_workspace_write]
network_access = true

[memories]
generate_memories = false
use_memories = true
disable_on_external_context = true

[profiles.full-access]
approval_policy = "never"
sandbox_mode = "danger-full-access"
'''
    write(root / ".codex" / "config.toml", codex)


def finding_types(home: Path) -> set[str]:
    return {item["type"] for item in MODULE.audit_home(home)}


class HarnessInvariantTests(unittest.TestCase):
    def test_healthy_control_plane_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            home = Path(temp)
            healthy_home(home)
            self.assertEqual(MODULE.audit_home(home), [])

    def test_codex_regressions_are_detected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            home = Path(temp)
            healthy_home(home)
            codex = f'''approval_policy = "never"
sandbox_mode = "danger-full-access"

[mcp_servers.memory-1]
command = "npx"

[sandbox_workspace_write]
network_access = false

[projects."{home}"]
trust_level = "trusted"

[memories]
generate_memories = true
use_memories = true
disable_on_external_context = false
'''
            write(home / ".codex" / "config.toml", codex)
            types = finding_types(home)
            self.assertTrue({
                "codex_duplicate_memory_plane",
                "codex_memory_policy_drift",
                "codex_default_approval_drift",
                "codex_default_sandbox_drift",
                "codex_workspace_network_drift",
                "codex_home_trust_too_broad",
                "codex_full_access_escape_hatch_drift",
            }.issubset(types))

    def test_claude_regressions_are_detected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            home = Path(temp)
            healthy_home(home)
            settings = json.loads((home / ".claude" / "settings.json").read_text())
            settings["permissions"]["defaultMode"] = "default"
            settings["permissions"]["allow"] = [
                "Bash(*)",
                "mcp__memory__*",
                "mcp__MiniMax__*",
            ]
            settings["sandbox"] = {"enabled": False, "autoAllowBashIfSandboxed": False}
            settings["hooks"]["PreToolUse"][0]["hooks"].append({
                "type": "command",
                "command": "python3 ~/.claude/hooks/skills-symlink-guard.py",
            })
            write(home / ".claude" / "settings.json", json.dumps(settings))
            types = finding_types(home)
            self.assertTrue({
                "claude_default_mode_drift",
                "claude_blanket_permission_regression",
                "claude_stale_memory_mcp_permission",
                "claude_retired_minimax_mcp_permission",
                "claude_sandbox_disabled",
                "claude_sandbox_autonomy_drift",
                "claude_retired_bash_guard_remounted",
            }.issubset(types))

    def test_missing_shared_control_plane_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            home = Path(temp)
            healthy_home(home)
            (home / ".agents" / "AGENTS.md").unlink()
            (home / ".agents" / "bin" / "compile-agent-instructions.sh").unlink()
            types = finding_types(home)
            self.assertIn("shared_instruction_source_missing", types)
            self.assertIn("projection_compiler_missing", types)


if __name__ == "__main__":
    unittest.main(verbosity=2)
