"""Regression tests for the repository Makefile convenience wrapper."""

from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAKEFILE = ROOT / "Makefile"


class MakefileContractTests(unittest.TestCase):
    def test_makefile_delegates_validation_to_shared_entrypoint(self) -> None:
        text = MAKEFILE.read_text(encoding="utf-8")
        self.assertIn("PY ?= python3", text)
        self.assertIn("scripts/ci_check.py", text)
        self.assertIn("test: check", text)
        self.assertIn("ci: check", text)
        self.assertIn("npm run cloudflare:build", text)

    def test_makefile_does_not_reintroduce_stale_validation_policy(self) -> None:
        text = MAKEFILE.read_text(encoding="utf-8")
        for stale in (
            "SKILL := rich-audit",
            "Tri-Search Protocol",
            "unittest (10 tests)",
            "Running 7 detection scripts",
            "SCRIPTS_LIST :=",
        ):
            self.assertNotIn(stale, text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
