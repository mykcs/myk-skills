"""Regression tests for the repository skill validator baseline."""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ROOT_VALIDATOR = ROOT / "scripts" / "quick_validate.py"
CANONICAL_VALIDATOR = ROOT / "skill-creator" / "scripts" / "quick_validate.py"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


root_validator = load_module(ROOT_VALIDATOR, "repo_quick_validate")
canonical_validator = load_module(CANONICAL_VALIDATOR, "canonical_quick_validate")


class QuickValidateRegressionTests(unittest.TestCase):
    def _make_skill(self, text: str) -> Path:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        skill_dir = Path(tmp.name) / "sample-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(text, encoding="utf-8")
        return skill_dir

    def test_current_verifier_pass2_schema_is_accepted(self) -> None:
        valid, message = root_validator.validate_skill(ROOT / "verifier-pass2")
        self.assertTrue(valid, message)

    def test_current_host_self_evolve_schema_is_accepted(self) -> None:
        valid, message = root_validator.validate_skill(ROOT / "host-self-evolve")
        self.assertTrue(valid, message)

    def test_documented_fields_and_extension_fields_are_allowed(self) -> None:
        skill_dir = self._make_skill(
            """---\n"
            "name: sample-skill\n"
            "description: Sample skill used for validator regression coverage.\n"
            "when_to_use: Use for validator regression tests.\n"
            "user-invocable: false\n"
            "disable-model-invocation: true\n"
            "allowed-tools: [Read, Grep]\n"
            "metadata:\n"
            "  version: 1.0.0\n"
            "tags: [validation, regression]\n"
            "author: mykcs\n"
            "custom-extension-field: accepted\n"
            "---\n"
            "# Sample\n"
            """
        )
        valid, message = canonical_validator.validate_skill(skill_dir)
        self.assertTrue(valid, message)

    def test_empty_frontmatter_is_structurally_valid(self) -> None:
        skill_dir = self._make_skill("---\n---\n# Fallback description paragraph\n")
        valid, message = canonical_validator.validate_skill(skill_dir)
        self.assertTrue(valid, message)

    def test_invalid_boolean_field_fails_closed(self) -> None:
        skill_dir = self._make_skill(
            "---\nname: sample-skill\nuser-invocable: sometimes\n---\n# Sample\n"
        )
        valid, message = canonical_validator.validate_skill(skill_dir)
        self.assertFalse(valid)
        self.assertIn("YAML boolean", message)

    def test_invalid_name_fails_closed(self) -> None:
        skill_dir = self._make_skill("---\nname: Sample_Skill\n---\n# Sample\n")
        valid, message = canonical_validator.validate_skill(skill_dir)
        self.assertFalse(valid)
        self.assertIn("lowercase letters", message)

    def test_malformed_yaml_fails_closed(self) -> None:
        skill_dir = self._make_skill("---\nname: [broken\n---\n# Sample\n")
        valid, message = canonical_validator.validate_skill(skill_dir)
        self.assertFalse(valid)
        self.assertIn("Invalid YAML", message)

    def test_root_entrypoint_delegates_to_canonical_validator(self) -> None:
        skill_dir = self._make_skill("---\nname: sample-skill\n---\n# Sample\n")
        self.assertEqual(
            root_validator.validate_skill(skill_dir),
            canonical_validator.validate_skill(skill_dir),
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
