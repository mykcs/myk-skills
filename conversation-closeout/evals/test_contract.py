"""Regression tests for the conversation-closeout skill contract."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / "conversation-closeout" / "SKILL.md"
EVALS = ROOT / "conversation-closeout" / "evals" / "evals.json"


class TestConversationCloseoutSkill(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.skill = SKILL.read_text(encoding="utf-8")
        cls.evals = json.loads(EVALS.read_text(encoding="utf-8"))

    def test_is_whole_conversation_orchestrator_not_summary(self) -> None:
        self.assertIn("not to write a chronological summary", self.skill)
        self.assertIn("whole accessible conversation", self.skill)
        self.assertIn("Be generous in candidate discovery", self.skill)
        self.assertIn("strict in what becomes durable", self.skill)

    def test_routes_to_one_fact_one_owner(self) -> None:
        for marker in (
            "cross-tool owner feedback / learned practice",
            "shared reusable workflow / Skill",
            "project current truth / SOP / test / config",
            "live provider/account/runtime state",
            "historical evidence",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, self.skill)

    def test_discovers_both_owner_feedback_and_engineering_lessons(self) -> None:
        self.assertIn("Direct owner signal", self.skill)
        self.assertIn("Engineering / operational lesson", self.skill)
        self.assertIn("Workflow / SOP improvement", self.skill)
        self.assertIn("Research / evidence-handling lesson", self.skill)
        self.assertIn("Communication / content / design preference", self.skill)

    def test_has_explicit_non_learning_filter(self) -> None:
        self.assertIn("Intentional non-learning", self.skill)
        for marker in (
            "transient PR/deployment/job status",
            "temporary PID/container state",
            "credentials/secrets",
            "unverified speculation",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, self.skill)

    def test_retrieve_before_create_and_strengthen_existing(self) -> None:
        self.assertIn("Retrieve before creating", self.skill)
        self.assertIn("Do not create a synonym", self.skill)
        self.assertIn("strengthen it", self.skill)

    def test_repeated_machine_checkable_failures_promote_to_guards(self) -> None:
        self.assertIn("Promote machine-checkable lessons", self.skill)
        self.assertIn("repeated machine-checkable incident -> add a guard", self.skill)
        self.assertIn("Do not encode subjective judgment as brittle string tests", self.skill)

    def test_neighboring_skills_have_narrow_roles(self) -> None:
        for marker in (
            "record-case",
            "rules-distill",
            "agent-knowledge-garden",
            "skill-creator",
            "fresh-agent-acceptance",
            "verify",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, self.skill)
        self.assertIn("not the whole-conversation orchestrator", self.skill)

    def test_future_usability_is_required(self) -> None:
        self.assertIn("Prove future usability", self.skill)
        self.assertIn("Future-Task Retrieval Proof", self.skill)
        self.assertIn("fresh-agent-acceptance", self.skill)
        self.assertIn("Do not use same-context self-review as independent evidence", self.skill)

    def test_final_report_matches_owner_facing_contract(self) -> None:
        for marker in (
            "总结了什么？",
            "记住了什么？",
            "有没有重复犯错？",
            "还有没有 blocker？",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, self.skill)

    def test_eval_suite_covers_filter_dedup_and_future_proof(self) -> None:
        self.assertEqual(self.evals["skill"], "conversation-closeout")
        self.assertEqual(self.evals["version"], "1.0.0")
        by_id = {case["id"]: case for case in self.evals["cases"]}
        self.assertEqual(
            set(by_id),
            {
                "mixed-value-sweep",
                "deduplicate-and-escalate",
                "workflow-and-future-proof",
            },
        )
        self.assertFalse(
            by_id["mixed-value-sweep"]["expected"]["temporary_pid_not_promoted"] is False
        )
        self.assertFalse(
            by_id["deduplicate-and-escalate"]["expected"]["duplicate_lesson_created"]
        )
        self.assertTrue(
            by_id["workflow-and-future-proof"]["expected"]["fresh_agent_acceptance_when_context_advantage_material"]
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
