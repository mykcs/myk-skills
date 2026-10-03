"""Check the installable skill contract and evaluation fixtures, not behavioral quality."""

import json
from pathlib import Path
import re
import unittest

import yaml


SKILL = Path(__file__).resolve().parents[1]


class WorkflowEvolutionContractTests(unittest.TestCase):
    def test_identity_and_ui_are_consistent(self):
        text = (SKILL / "SKILL.md").read_text()
        metadata = yaml.safe_load(text.split("---", 2)[1])
        self.assertEqual(metadata["name"], SKILL.name)
        self.assertTrue(metadata["description"].strip())
        payload = json.loads((SKILL / "evals/evals.json").read_text())
        self.assertEqual(metadata["metadata"]["version"], payload["version"])
        ui = yaml.safe_load((SKILL / "agents/openai.yaml").read_text())
        self.assertIn("$" + metadata["name"], ui["interface"]["default_prompt"])
        self.assertTrue(ui.get("policy", {}).get("allow_implicit_invocation", True))

    def test_references_resolve(self):
        for path in [SKILL / "SKILL.md", *sorted((SKILL / "references").glob("*.md"))]:
            for target in re.findall(r"\]\(([^)]+)\)", path.read_text()):
                if target.startswith(("https://", "http://", "#")):
                    continue
                with self.subTest(source=str(path), target=target):
                    self.assertTrue((path.parent / target.split("#", 1)[0]).is_file())

    def test_central_migration_loop_is_closed_and_non_gaming(self):
        text = (SKILL / "SKILL.md").read_text()
        reference = (SKILL / "references/adoption-and-review.md").read_text()
        for marker in [
            "Change the canonical owner first",
            "Audit consumers and registry coverage",
            "Never contaminate a correct project with obsolete wording",
            "Keep hot routers small without deleting load-bearing discovery",
            "Treat the auditor as part of the system",
            "zero unexplained findings",
            "latest-main re-audit",
        ]:
            self.assertIn(marker, text + "\n" + reference)

        payload = json.loads((SKILL / "evals/evals.json").read_text())
        case = next(case for case in payload["evals"] if case["id"] == 19)
        self.assertTrue(case["should_trigger"])
        self.assertIn("stale auditor expectations", case["expected_output"])
        self.assertIn("machine-tested startup discovery", case["expected_output"])

    def test_v2_absorbs_harness_and_host_with_safe_autonomy(self):
        text = (SKILL / "SKILL.md").read_text()
        for marker in [
            "single active evolution workflow",
            "safe autonomous repair",
            "Safety is a boundary, not a reason to be passive",
            "harness-evolution.md",
            "host-local-evolution.md",
            "former active skills `harness-upgrade` and `host-self-evolve` were absorbed",
        ]:
            self.assertIn(marker, text)

        harness = (SKILL / "references/harness-evolution.md").read_text()
        for marker in [
            "search the web before editing",
            "recent primary research",
            "disconfirming evidence",
            "the research refresh again",
            "progressive disclosure",
        ]:
            self.assertIn(marker.lower(), harness.lower())

        host = (SKILL / "references/host-local-evolution.md").read_text()
        self.assertIn("legacy implementation/evidence", host)
        self.assertIn("Do **not** preserve these as mandatory current behavior", host)

        safe = (SKILL / "references/safe-autonomy.md").read_text()
        self.assertIn("Proceed without another approval", safe)
        self.assertIn("Real stop/approval boundaries", safe)

        buoyancy = (SKILL / "references/knowledge-buoyancy.md").read_text()
        for marker in [
            "Knowledge buoyancy / 知识沉浮",
            "Parse cold evidence",
            "Promotion rules",
            "Demotion rules",
            "evidence stays deep",
        ]:
            self.assertIn(marker.lower(), buoyancy.lower())

        repo_root = SKILL.parents[0]
        self.assertFalse((repo_root / "harness-upgrade" / "SKILL.md").exists())
        self.assertFalse((repo_root / "host-self-evolve" / "SKILL.md").exists())
        self.assertTrue((repo_root / "_archive" / "harness-upgrade" / "SKILL.md").is_file())
        self.assertTrue((repo_root / "_archive" / "host-self-evolve" / "SKILL.md").is_file())
        self.assertIn("knowledge-buoyancy.md", text)
        self.assertIn("case/receipt distillation", text)

    def test_evaluation_fixtures_are_complete_and_balanced(self):
        payload = json.loads((SKILL / "evals/evals.json").read_text())
        self.assertEqual(payload["skill_name"], SKILL.name)
        cases = payload["evals"]
        self.assertEqual(len({case["id"] for case in cases}), len(cases))
        self.assertTrue(any(case["should_trigger"] for case in cases))
        self.assertTrue(any(not case["should_trigger"] for case in cases))
        for case in cases:
            with self.subTest(case=case["id"]):
                self.assertIsInstance(case["should_trigger"], bool)
                self.assertTrue(case["prompt"].strip())
                self.assertTrue(case["expected_output"].strip())
                self.assertTrue(case["assertions"])
                self.assertTrue(all(isinstance(item, str) and item.strip() for item in case["assertions"]))


if __name__ == "__main__":
    unittest.main()
