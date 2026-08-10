"""Regression tests for the active website-improve v4.2.0 workflow contract."""

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


class TestModernAcceptanceWorkflow(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.skill = SKILL.read_text(encoding="utf-8")
        cls.three_role = THREE_ROLE.read_text(encoding="utf-8")
        cls.ci_gate = CI_GATE.read_text(encoding="utf-8")
        cls.per = PER.read_text(encoding="utf-8")
        cls.recovery = RECOVERY.read_text(encoding="utf-8")
        cls.checklist = CHECKLIST.read_text(encoding="utf-8")

    def test_active_skill_is_v4_2_modern(self) -> None:
        self.assertIn('version: "4.2.0"', self.skill)
        self.assertIn("--artifact-mode modern", self.skill)
        self.assertIn("--acceptance-file", self.skill)

    def test_three_roles_remain_independent(self) -> None:
        for role in ("Planner", "Executor", "Verifier"):
            with self.subTest(role=role):
                self.assertIn(role, self.skill)
                self.assertIn(role, self.three_role)
        self.assertIn("The three roles are independent", self.skill)
        self.assertIn("Verifier is read-only", self.skill)

    def test_publication_is_conditional_acceptance(self) -> None:
        for state in ("NOT_REQUESTED", "NOT_APPLICABLE", "VERIFIED", "BLOCKED"):
            with self.subTest(state=state):
                self.assertIn(state, self.skill)
        self.assertIn("Publication is separate from execution", self.skill)
        self.assertIn("publication `VERIFIED` or `BLOCKED`", self.three_role)

    def test_executor_does_not_own_automatic_smart_push(self) -> None:
        self.assertNotIn("并自动 `smart-autopush.sh` 提交", self.skill)
        self.assertNotIn("按 plan 跑 audit、fix、smart-push", self.skill)
        self.assertIn("does **not** automatically commit, push", self.skill)
        self.assertIn("Publication is separate from execution", self.skill)

    def test_recovery_is_not_a_publication_takeover(self) -> None:
        self.assertIn("does **not** grant permission to publish work automatically", self.recovery)
        self.assertIn("Publication is not recovery", self.recovery)
        for stale_instruction in (
            "Step 2: 接管 push",
            "smart-push 试",
            "git pull --rebase origin main",
            "手动 raw `git push`",
        ):
            with self.subTest(stale_instruction=stale_instruction):
                self.assertNotIn(stale_instruction, self.recovery)

    def test_four_site_gate_is_scope_relevant_not_universal(self) -> None:
        self.assertIn("only when the requested task actually includes all four", self.ci_gate)
        self.assertIn("single unrelated site such as `basemodel`", self.ci_gate)
        self.assertNotIn("任何 website-improve run", self.ci_gate)
        self.assertNotIn("4 站 CI 必须全部", self.ci_gate)

    def test_fixed_five_git_fields_no_longer_define_completion(self) -> None:
        self.assertNotIn("5 字段自检全过", self.skill)
        self.assertNotIn("Verifier → User（PASS）：必须附 5 字段", self.per)
        self.assertIn("Do not create fixed path/commit/push/CI/owner rows", self.ci_gate)

    def test_memory_promotion_is_conditional(self) -> None:
        self.assertIn("promotion outputs", self.skill)
        self.assertIn("not mandatory for every PER task", self.per)
        self.assertNotIn("不写 case 文件 → self-evolution 协议违反", self.skill)

    def test_checklist_guards_modern_cli_contract(self) -> None:
        self.assertIn("plan_json_gen.py --artifact-mode modern", self.checklist)
        self.assertIn("verdict_json_gen.py --artifact-mode modern --acceptance-file", self.checklist)
        self.assertIn("single-site tasks verify that site only", self.checklist.lower())


if __name__ == "__main__":
    unittest.main(verbosity=2)
