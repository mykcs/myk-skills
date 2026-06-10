"""
test_detection_scripts.py - Smoke tests for the 3 detection scripts.

Verifies each script:
  1. Runs without crash (exit 0 or 1)
  2. Outputs valid JSON
  3. Has expected top-level keys

Run: python3 -m unittest ~/.agents/skills/rich-audit/scripts/test_detection_scripts.py -v
Or:  cd ~/.agents/skills/rich-audit && python3 -m unittest scripts.test_detection_scripts -v
"""
import json
import subprocess
import unittest
from pathlib import Path

SCRIPTS_DIR = Path.home() / ".agents" / "skills" / "rich-audit" / "scripts"


def _run_script(name: str, timeout: int = 60) -> dict:
    """Run a detection script and return parsed JSON output."""
    result = subprocess.run(
        ["python3", str(SCRIPTS_DIR / name)],
        capture_output=True, text=True, timeout=timeout,
    )
    assert result.returncode in (0, 1), (
        f"{name} crashed with exit {result.returncode}: {result.stderr[:200]}"
    )
    return json.loads(result.stdout)


class TestDeadCodeDetector(unittest.TestCase):
    def test_schema(self):
        data = _run_script("dead_code_detector.py")
        for key in ("tool", "version", "scope", "findings", "count", "by_type"):
            self.assertIn(key, data, f"missing key: {key}")
        self.assertEqual(data["count"], len(data["findings"]))
        self.assertEqual(
            data["count"],
            sum(data["by_type"].values()),
            "by_type sum should equal count",
        )

    def test_finding_types(self):
        data = _run_script("dead_code_detector.py")
        valid_types = {"orphan_case", "dead_hook", "dead_script", "orphan_skill", "error"}
        for f in data["findings"]:
            self.assertIn(f.get("type"), valid_types, f"unknown finding type: {f.get('type')}")


class TestCommandsToSkillsMigrator(unittest.TestCase):
    def test_schema(self):
        data = _run_script("commands_to_skills_migrator.py")
        for key in ("tool", "version", "migration_candidates", "skill_overlaps",
                    "migration_count", "overlap_count"):
            self.assertIn(key, data, f"missing key: {key}")
        self.assertEqual(data["migration_count"], len(data["migration_candidates"]))
        self.assertEqual(data["overlap_count"], len(data["skill_overlaps"]))


class TestLintRunner(unittest.TestCase):
    def test_schema(self):
        data = _run_script("lint_runner.py")
        for key in ("tool", "version", "scanned_sh", "scanned_py", "findings",
                    "count", "by_type"):
            self.assertIn(key, data, f"missing key: {key}")
        self.assertEqual(data["count"], len(data["findings"]))
        self.assertGreaterEqual(data["scanned_sh"] + data["scanned_py"], 1)

    def test_types_known(self):
        data = _run_script("lint_runner.py")
        valid_types = {"shellcheck", "py_compile", "error", "shellcheck_timeout",
                       "shellcheck_parse_error", "py_compile_timeout"}
        for f in data["findings"]:
            self.assertIn(f.get("type"), valid_types, f"unknown: {f.get('type')}")


class TestMemoryAuditRunner(unittest.TestCase):
    def test_schema(self):
        data = _run_script("memory_audit_runner.py")
        for key in ("tool", "version", "exit_code", "result_line",
                    "summary_pass", "missing_files_count"):
            self.assertIn(key, data, f"missing key: {key}")
        self.assertIsInstance(data["summary_pass"], bool)


if __name__ == "__main__":
    unittest.main()
