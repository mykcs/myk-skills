"""Regression tests for the harness-audit skill entrypoint."""

import unittest
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
SKILL_MD = SKILL_DIR / "SKILL.md"
WRAPPER_COMMAND = "python3 ~/.claude/scripts/harness-audit-cp.py <scope> --format <text|json>"
DIRECT_MARKETPLACE_COMMAND = (
    "node ~/.claude/plugins/marketplaces/everything-claude-code/"
    "scripts/harness-audit.js"
)


class TestHarnessAuditEntrypoint(unittest.TestCase):
    def test_skill_file_exists_and_keeps_frontmatter(self) -> None:
        text = SKILL_MD.read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---\n"))
        self.assertIn("name: harness-audit", text)
        self.assertIn("description:", text)

    def test_skill_routes_through_control_plane_wrapper(self) -> None:
        text = SKILL_MD.read_text(encoding="utf-8")
        self.assertIn(WRAPPER_COMMAND, text)
        self.assertIn("--root <path>", text)

    def test_skill_does_not_hardcode_marketplace_execution(self) -> None:
        text = SKILL_MD.read_text(encoding="utf-8")
        self.assertNotIn(DIRECT_MARKETPLACE_COMMAND, text)
        self.assertIn("HARNESS_AUDIT_JS", text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
