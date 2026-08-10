"""Regression tests for the active website-improve v4.2.0 workflow contract.

These tests intentionally assert stable architecture markers instead of broad
substring bans across prose. Historical/anti-pattern documentation is allowed to
name retired behavior; the active contract must positively encode the modern
ownership and acceptance boundaries.
"""

from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / "website-improve" / "SKILL.md"
REFS = ROOT / "website-improve" / "references"
THREE_ROLE = REFS / "3-role-workflow.md"
CI_GATE = REFS / "4-site-ci-gate.md"
PER = REFS / "per-workflow-framework.md"
RECOVERY = REFS / "orchestrator-recovery.md"
CHECKLIST = REFS / "validation-checklist.md"
MODE_A = REFS / "mode-a.md"
MODE_D = REFS / "mode-d-multisite.md"
TRIGGERS = REFS / "triggers.md"
QUALITY = REFS / "quality-checks.md"


class TestModernAcceptanceWorkflow(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.skill = SKILL.read_text(encoding="utf-8")
        cls.three_role = THREE_ROLE.read_text(encoding="utf-8")
        cls.ci_gate = CI_GATE.read_text(encoding="utf-8")
        cls.per = PER.read_text(encoding="utf-8")
        cls.recovery = RECOVERY.read_text(encoding="utf-8")
        cls.checklist = CHECKLIST.read_text(encoding="utf-8")
        cls.mode_a = MODE_A.read_text(encoding="utf-8")
        cls.mode_d = MODE_D.read_text(encoding="utf-8")
        cls.triggers = TRIGGERS.read_text(encoding="utf-8")
        cls.quality = QUALITY.read_text(encoding="utf-8")

    def test_active_skill_uses_modern_artifact_contract(self) -> None:
        self.assertIn('version: "4.2.0"', self.skill)
        self.assertIn("--artifact-mode modern", self.skill)
        self.assertIn("--acceptance-file", self.skill)
        self.assertIn("--artifact-mode modern", self.three_role)
        self.assertIn("--acceptance-file", self.three_role)

    def test_roles_are_independent_and_verifier_is_read_only(self) -> None:
        self.assertIn("Planner → Executor → Verifier", self.skill)
        self.assertIn("The three roles are independent", self.skill)
        self.assertIn("Verifier is independent and read-only", self.skill)
        self.assertIn("Verifier remains read-only", self.three_role)

    def test_publication_is_separate_and_fail_closed(self) -> None:
        for state in ("NOT_REQUESTED", "NOT_APPLICABLE", "VERIFIED", "BLOCKED"):
            with self.subTest(state=state):
                self.assertIn(state, self.skill)
                self.assertIn(state, self.three_role)
        self.assertIn("Publication is separate from execution", self.skill)
        self.assertIn("`BLOCKED` fails the final verdict", self.ci_gate)

    def test_executor_and_recovery_do_not_own_publication(self) -> None:
        self.assertIn("does **not** automatically commit, push", self.skill)
        self.assertIn("does **not** grant permission to publish work automatically", self.recovery)
        self.assertIn("Publication is not recovery", self.recovery)
        self.assertIn("enter publication only when the plan explicitly requested it", self.recovery)

    def test_site_and_ci_scope_are_task_driven(self) -> None:
        self.assertIn("single unrelated site such as `basemodel`", self.ci_gate)
        self.assertIn("exactly the sites in scope", self.skill)
        self.assertIn("not the default scope", self.triggers.lower())
        self.assertIn("plan.verification_targets", self.mode_a)
        self.assertIn("不使用 GitHub Actions 的站点", self.mode_a)

    def test_mode_d_execution_is_publication_free_by_default(self) -> None:
        self.assertIn("publication_mode = none", self.mode_d)
        self.assertIn("does **not** automatically commit, push", self.mode_d)
        self.assertIn("publication is requested", self.mode_d)
        self.assertIn("not a mandatory Phase 4 output", self.mode_d)

    def test_quality_checks_match_the_changed_layer(self) -> None:
        self.assertIn("Planner selects the checks", self.quality)
        self.assertIn("requested outcome depends on", self.quality)
        self.assertIn("task-scoped v4.2.0 acceptance", self.quality)
        self.assertIn("`skipped`, missing, stale, queued, or unavailable checks are not PASS", self.quality)

    def test_memory_and_validation_contract_are_modern(self) -> None:
        self.assertIn("not mandatory for every PER task", self.per)
        self.assertIn("plan_json_gen.py --artifact-mode modern", self.checklist)
        self.assertIn("verdict_json_gen.py --artifact-mode modern --acceptance-file", self.checklist)
        self.assertIn("NOT_REQUESTED", self.checklist)
        self.assertIn("BLOCKED", self.checklist)


if __name__ == "__main__":
    unittest.main(verbosity=2)
