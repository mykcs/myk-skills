"""Regression tests for the platform-neutral repository CI entrypoint."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CI_CHECK = ROOT / "scripts" / "ci_check.py"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ci_check = load_module(CI_CHECK, "myk_ci_check")


class CiCheckRegressionTests(unittest.TestCase):
    def _repo_fixture(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        (root / "scripts").mkdir()
        return tmp, root

    def test_active_skill_discovery_is_top_level_and_excludes_hidden_archive(self) -> None:
        _, root = self._repo_fixture()
        for name in ("alpha", "beta", "_archive", ".cache"):
            skill = root / name
            skill.mkdir()
            (skill / "SKILL.md").write_text("---\nname: sample\n---\n", encoding="utf-8")
        (root / "docs").mkdir()

        self.assertEqual(
            [path.name for path in ci_check.active_skill_dirs(root)],
            ["alpha", "beta"],
        )

    def test_skill_eval_discovery_only_returns_test_directories(self) -> None:
        _, root = self._repo_fixture()
        alpha = root / "alpha"
        beta = root / "beta"
        for skill in (alpha, beta):
            skill.mkdir()
            (skill / "SKILL.md").write_text("---\nname: sample\n---\n", encoding="utf-8")
        (alpha / "evals").mkdir()
        (alpha / "evals" / "test_alpha.py").write_text("", encoding="utf-8")
        (beta / "evals").mkdir()
        (beta / "evals" / "notes.md").write_text("not a test\n", encoding="utf-8")

        self.assertEqual(ci_check.skill_eval_dirs(root), [alpha / "evals"])

    def test_prepare_host_ci_home_recreates_legacy_stub_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            ci_check.prepare_host_ci_home(home)
            self.assertTrue((home / ".claude" / "memory" / "MEMORY.md").is_file())
            self.assertTrue((home / ".claude" / "scripts" / "stub.sh").is_file())
            self.assertTrue((home / ".claude" / "commands" / "stub-cmd.md").is_file())
            skill_md = home / ".agents" / "skills" / "stub-skill" / "SKILL.md"
            self.assertIn("name: stub-skill", skill_md.read_text(encoding="utf-8"))

    def test_host_modernization_reports_missing_contracts(self) -> None:
        _, root = self._repo_fixture()
        host = root / "host-self-evolve"
        (host / "references" / "consistency-6d").mkdir(parents=True)
        (host / "scripts").mkdir()
        (host / "SKILL.md").write_text("# no marker\n", encoding="utf-8")

        failures = ci_check.check_host_modernization(root)
        self.assertTrue(any("PER Workflow" in failure for failure in failures))
        self.assertTrue(any("consistency-6d/1" in failure for failure in failures))
        self.assertTrue(any("dead_code_detector.py" in failure for failure in failures))

    def test_parse_tool_json_checks_tool_identity(self) -> None:
        good = subprocess.CompletedProcess(
            args=["tool"], returncode=0, stdout=json.dumps({"tool": "demo.py"}), stderr=""
        )
        self.assertEqual(ci_check.parse_tool_json(good, "demo.py")["tool"], "demo.py")

        bad = subprocess.CompletedProcess(
            args=["tool"], returncode=0, stdout=json.dumps({"tool": "other.py"}), stderr=""
        )
        with self.assertRaises(RuntimeError):
            ci_check.parse_tool_json(bad, "demo.py")

    def test_current_host_modernization_contract_is_present(self) -> None:
        self.assertEqual(ci_check.check_host_modernization(ROOT), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
