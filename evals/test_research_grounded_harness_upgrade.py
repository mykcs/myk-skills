"""Regression tests for research-grounded harness upgrade contracts."""

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
HARNESS_UPGRADE = REPO_ROOT / "harness-upgrade" / "SKILL.md"
CONTEXT_BUDGET = REPO_ROOT / "context-budget" / "SKILL.md"
VERIFY = REPO_ROOT / "verify" / "SKILL.md"


class ResearchGroundedHarnessUpgradeTests(unittest.TestCase):
    def test_harness_upgrade_requires_fresh_primary_research(self) -> None:
        text = HARNESS_UPGRADE.read_text(encoding="utf-8")
        self.assertIn("search the web before editing", text.lower())
        self.assertIn("recent primary research", text.lower())
        self.assertIn("disconfirming evidence", text.lower())
        self.assertIn("the research refresh again", text.lower())
        self.assertNotIn("gpt-5.6", text.lower())
        self.assertNotIn("claude opus 4.6", text.lower())

    def test_context_budget_is_not_a_self_referential_200k_shim(self) -> None:
        text = CONTEXT_BUDGET.read_text(encoding="utf-8")
        self.assertIn("HOT", text)
        self.assertIn("WARM", text)
        self.assertIn("COLD", text)
        self.assertIn("Just-in-time retrieval", text)
        self.assertIn("Structured state over transcript retention", text)
        self.assertIn("No invented context limit", text)
        self.assertNotIn("Assume a 200K context window", text)
        self.assertNotIn("Apply the `context-budget` skill", text)

    def test_verify_separates_infrastructure_from_implementation(self) -> None:
        text = VERIFY.read_text(encoding="utf-8")
        self.assertIn("Environment fingerprint", text)
        self.assertIn("IMPLEMENTATION", text)
        self.assertIn("POLICY_DRIFT", text)
        self.assertIn("INFRASTRUCTURE", text)
        self.assertIn("INSUFFICIENT_EVIDENCE", text)
        self.assertIn("High-impact verification portfolio", text)
        self.assertIn("unavailable/skipped hosted check", text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
