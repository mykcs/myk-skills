"""Regression tests for contributor-facing repository contracts."""

from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRIBUTING = ROOT / "CONTRIBUTING.md"


class ContributingContractTests(unittest.TestCase):
    def test_skill_frontmatter_guidance_matches_repository_validator(self) -> None:
        text = CONTRIBUTING.read_text(encoding="utf-8")
        self.assertIn("documented frontmatter fields are optional", text)
        self.assertIn("`description` is recommended", text)
        self.assertIn("extension fields are allowed", text)
        self.assertNotIn("Required frontmatter fields:", text)

    def test_contributing_points_to_shared_validation_entrypoint(self) -> None:
        text = CONTRIBUTING.read_text(encoding="utf-8")
        self.assertIn("python3 scripts/ci_check.py", text)
        self.assertIn("single source of truth", text)
        self.assertIn("Python 3.12", text)
        self.assertNotIn("Python 3.10+", text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
