"""Regression tests for verifier-pass2 public/internal routing."""

import unittest
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
SKILL_MD = SKILL_DIR / "SKILL.md"


class TestVerifierPass2InternalEntrypoint(unittest.TestCase):
    def test_direct_user_invocation_is_disabled(self) -> None:
        text = SKILL_MD.read_text(encoding="utf-8")
        self.assertIn("user-invocable: false", text)
        self.assertNotIn("user-invocable: true", text)

    def test_canonical_user_entrypoint_is_verify_pass2(self) -> None:
        text = SKILL_MD.read_text(encoding="utf-8")
        self.assertIn("Canonical user-facing entrypoint: `/verify pass2`", text)
        self.assertIn("internal implementation", text)

    def test_validation_only_limits_are_preserved(self) -> None:
        text = SKILL_MD.read_text(encoding="utf-8")
        self.assertIn("does **not** fix anything", text)
        self.assertIn("Do not chain more than 2 passes", text)
        self.assertIn("Default to `real: false` if uncertain", text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
