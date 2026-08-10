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
        cls.live = "\n".join(
            [
                cls.skill,
                cls.three_role,
                cls.ci_gate,
                cls.per,
                cls.recovery,
                cls.checklist,
                cls.mode_a,
                cls.mode_d,
                cls.triggers,
                cls.quality,
            ]
        )

    def test_active_skill_uses_modern_artifact_contract(self) -> None:
        self.assertIn('version: "4.2.0"', self.skill)
        self.assertIn("--artifact-mode modern", self.skill)
        self.assertIn("--artifact-mode modern", self.three_role)
        self.assertIn("--acceptance-file", self.skill)
        self.assertIn("--acceptance-file", self.three_role)

    def test_three_roles_remain_explicit_and_verifier_read_only(self) -> None:
        for role in ("Planner", "Executor", "Verifier"):
            with self.subTest(role=role):
                self.assertIn(role, self.skill)
                self.assertIn(role, self.three_role)
        self.assertIn("read-only", self.skill.lower())
        self.assertIn("read-only", self.three_role.lower())

    def test_publication_states_are_modern_and_conditional(self) -> None:
        for state in ("NOT_REQUESTED", "NOT_APPLICABLE", "VERIFIED", "BLOCKED"):
            with self.subTest(state=state):
                self.assertIn(state, self.skill)
                self.assertIn(state, self.three_role)
        self.assertIn("publication-mode none", self.skill)
        self.assertIn("publication_mode = none", self.mode_d)

    def test_legacy_publication_ownership_does_not_return(self) -> None:
        forbidden = (
            "并自动 `smart-autopush.sh` 提交",
            "按 plan 跑 audit、fix、smart-push",
            "Push via autopush.sh",
            "Step 2: 接管 push",
            "smart-push 试",
            "手动 raw `git push`",
        )
        for marker in forbidden:
            with self.subTest(marker=marker):
                self.assertNotIn(marker, self.live)

    def test_four_site_and_five_field_rules_are_not_universal(self) -> None:
        for marker in (
            "4 站 CI 必须全部",
            "4 active sites (mykcs/GDKVM/OSA/content2html) 必须 CI 全 green",
            "5 字段自检全过",
            "Verifier → User（PASS）：必须附 5 字段",
        ):
            with self.subTest(marker=marker):
                self.assertNotIn(marker, self.live)
        self.assertIn("basemodel", self.ci_gate)
        self.assertIn("path/commit/push/CI/owner", self.ci_gate)

    def test_mode_a_is_repository_aware(self) -> None:
        self.assertIn("plan.verification_targets", self.mode_a)
        self.assertIn("GitHub Actions", self.mode_a)
        self.assertNotIn("BUILD_PASS → TYPECHECK_PASS → CI_PASS", self.mode_a)

    def test_mode_d_execution_does_not_require_user_ok_or_case_file(self) -> None:
        for marker in (
            "等用户回 OK",
            "Case file** (强制)",
        ):
            with self.subTest(marker=marker):
                self.assertNotIn(marker, self.mode_d)
        self.assertIn("publication_mode = none", self.mode_d)
        self.assertIn("modern", self.mode_d.lower())

    def test_trigger_routing_does_not_expand_scope_by_default(self) -> None:
        self.assertIn("task scope", self.triggers.lower())
        self.assertIn("not the default scope", self.triggers.lower())
        self.assertNotIn("4 站同时 sweep (default scope)", self.triggers)

    def test_quality_checks_are_contextual_evidence(self) -> None:
        self.assertIn("requested outcome depends on", self.quality)
        self.assertIn("not mandatory for every", self.quality.lower())
        self.assertNotIn("任何 audit 必跑", self.quality)

    def test_memory_promotion_is_conditional(self) -> None:
        self.assertNotIn("不写 case 文件 → self-evolution 协议违反", self.live)
        self.assertIn("promotion", self.skill.lower())
        self.assertIn("not mandatory", self.per.lower())

    def test_validation_checklist_tracks_modern_cli(self) -> None:
        self.assertIn("plan_json_gen.py --artifact-mode modern", self.checklist)
        self.assertIn("verdict_json_gen.py --artifact-mode modern --acceptance-file", self.checklist)
        self.assertIn("NOT_REQUESTED", self.checklist)
        self.assertIn("BLOCKED", self.checklist)


if __name__ == "__main__":
    unittest.main(verbosity=2)
