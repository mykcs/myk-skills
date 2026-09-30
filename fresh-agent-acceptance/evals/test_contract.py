"""Regression tests for the fresh-agent-acceptance skill contract."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / "fresh-agent-acceptance" / "SKILL.md"
EVALS = ROOT / "fresh-agent-acceptance" / "evals" / "evals.json"


class TestFreshAgentAcceptanceSkill(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.skill = SKILL.read_text(encoding="utf-8")
        cls.evals = json.loads(EVALS.read_text(encoding="utf-8"))

    def test_skill_is_general_black_box_workflow(self) -> None:
        self.assertIn("Use a fresh Agent to test whether completed work", self.skill)
        self.assertIn("The problem is epistemic", self.skill)
        self.assertIn("code, docs, configuration, websites", self.skill)
        self.assertIn("Do not force every case into", self.skill)

    def test_fresh_context_is_conversation_isolated_not_bootstrap_free(self) -> None:
        self.assertIn("conversation-isolated, not bootstrap-free", self.skill.lower())
        self.assertIn("Do **not** strip normal account/project bootstrap", self.skill)
        self.assertIn("same-context subagent is not strong fresh-Agent evidence", self.skill)

    def test_originator_infers_success_and_checks_actual_target(self) -> None:
        self.assertIn("Infer and freeze the real success behavior", self.skill)
        self.assertIn("what was just changed/fixed/built", self.skill)
        self.assertIn("Check the thing being tested", self.skill)
        self.assertIn("Do not assume this means", self.skill)

    def test_prompt_design_is_non_leading_and_contrastive(self) -> None:
        self.assertIn("Design an ordinary task, not an exam question", self.skill)
        self.assertIn("Use a contrastive witness", self.skill)
        self.assertIn("Prevent answer leakage", self.skill)
        self.assertIn("The task should **need** the target behavior without naming it", self.skill)
        self.assertIn("Do not add fake traps", self.skill)

    def test_replicated_trials_freeze_prompt_rubric_and_world(self) -> None:
        self.assertIn("Freeze the tested world", self.skill)
        self.assertIn("behavioral equivalent of exact-head testing", self.skill)
        self.assertIn("Freeze prompt and rubric before trials", self.skill)
        self.assertIn("materially changed prompt starts a new trial set", self.skill)
        self.assertIn("do not average old and new outputs together", self.skill.lower())

    def test_phase_a_output_separates_prompt_from_hidden_rubric(self) -> None:
        self.assertIn("COPY ONLY — FRESH AGENT PROMPT", self.skill)
        self.assertIn("KEEP HERE — HIDDEN RUBRIC", self.skill)
        self.assertIn("It is the only section the owner copies", self.skill)
        self.assertIn("Do not instruct the owner to paste this section", self.skill)

    def test_evaluator_does_not_move_rubric_or_cherry_pick(self) -> None:
        self.assertIn("Do not redesign the test after seeing results", self.skill)
        self.assertIn("Never cherry-pick replicated trials", self.skill)
        self.assertIn("Score semantics, not literal strings", self.skill)
        for verdict in ("PASS", "FAIL", "INCONCLUSIVE", "LEAKED"):
            self.assertIn(verdict, self.skill)

    def test_failure_diagnosis_is_domain_general(self) -> None:
        for failure_class in (
            "TARGET_DEFECT",
            "DISCOVERY",
            "INTERPRETATION",
            "GUARD",
            "PROMPT_DESIGN",
            "ACCESS_ENVIRONMENT",
        ):
            with self.subTest(failure_class=failure_class):
                self.assertIn(f"**{failure_class}**", self.skill)
        self.assertIn("Fix the real target for the first four classes", self.skill)
        self.assertIn("Rewrite the test only for **PROMPT_DESIGN**", self.skill)

    def test_skill_defaults_to_read_only_acceptance(self) -> None:
        self.assertIn("Default to read-only or simulated acceptance", self.skill)
        self.assertIn("A behavioral test grants no extra mutation authority", self.skill)
        self.assertIn("run GPU/destructive/production actions", self.skill)

    def test_eval_suite_covers_originator_and_evaluator_modes(self) -> None:
        self.assertEqual(self.evals["skill"], "fresh-agent-acceptance")
        self.assertEqual(self.evals["version"], "1.1.0")
        by_id = {case["id"]: case for case in self.evals["cases"]}
        self.assertEqual(
            set(by_id),
            {
                "originator-general-completed-work",
                "originator-contrastive-boundary",
                "evaluator-replicated-results",
            },
        )
        self.assertTrue(
            by_id["originator-general-completed-work"]["expected"]["infers_target_from_conversation"]
        )
        self.assertFalse(
            by_id["originator-general-completed-work"]["expected"]["prompt_reveals_change"]
        )
        self.assertTrue(
            by_id["originator-contrastive-boundary"]["expected"]["contrastive_boundary_witness"]
        )
        self.assertFalse(
            by_id["evaluator-replicated-results"]["expected"]["rubric_rewritten_after_outputs"]
        )
        self.assertEqual(
            by_id["evaluator-replicated-results"]["expected"]["honest_access_gap_may_be"],
            "INCONCLUSIVE",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
