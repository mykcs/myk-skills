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
