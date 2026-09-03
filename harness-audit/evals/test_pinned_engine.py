"""Regression tests for the pinned harness-audit engine supply chain and CLI contract."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
ENGINE = SKILL_ROOT / "scripts" / "harness-audit.js"
UPSTREAM = SKILL_ROOT / "vendor" / "UPSTREAM.md"
LICENSE = SKILL_ROOT / "vendor" / "ECC-LICENSE"
EXPECTED_BLOB_SHA = "79bc57c84af5acbd24c5cc6a26da88f1a5bfc0fc"
EXPECTED_RUBRIC = "2026-03-30"
EXPECTED_CATEGORIES = {
    "Tool Coverage",
    "Context Efficiency",
    "Quality Gates",
    "Memory Persistence",
    "Eval Coverage",
    "Security Guardrails",
    "Cost Efficiency",
}


def git_blob_sha(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


class TestPinnedHarnessAuditEngine(unittest.TestCase):
    def test_engine_is_exact_pinned_upstream_blob(self) -> None:
        self.assertTrue(ENGINE.is_file())
        self.assertEqual(git_blob_sha(ENGINE.read_bytes()), EXPECTED_BLOB_SHA)

    def test_license_and_provenance_are_preserved(self) -> None:
        self.assertTrue(LICENSE.is_file())
        self.assertIn("MIT License", LICENSE.read_text(encoding="utf-8"))
        provenance = UPSTREAM.read_text(encoding="utf-8")
        self.assertIn("affaan-m/ECC", provenance)
        self.assertIn("da04a6e344e9a563fb04262ab6362bda07617178", provenance)
        self.assertIn(EXPECTED_BLOB_SHA, provenance)
        self.assertIn(EXPECTED_RUBRIC, provenance)

    def test_cli_is_root_aware_deterministic_and_seven_category(self) -> None:
        with tempfile.TemporaryDirectory(prefix="harness-audit-engine-") as tmp:
            root = Path(tmp) / "consumer"
            home = Path(tmp) / "home"
            root.mkdir()
            home.mkdir()
            (root / "package.json").write_text(
                json.dumps({"name": "harness-audit-fixture", "scripts": {}}),
                encoding="utf-8",
            )
            (root / ".gitignore").write_text("node_modules\n.env\n", encoding="utf-8")

            env = os.environ.copy()
            env["HOME"] = str(home)
            command = [
                "node",
                str(ENGINE),
                "repo",
                "--format",
                "json",
                "--root",
                str(root),
            ]
            first = subprocess.run(
                command,
                env=env,
                text=True,
                capture_output=True,
                check=True,
            )
            second = subprocess.run(
                command,
                env=env,
                text=True,
                capture_output=True,
                check=True,
            )

            self.assertEqual(first.stdout, second.stdout)
            report = json.loads(first.stdout)
            self.assertTrue(report["deterministic"])
            self.assertEqual(report["rubric_version"], EXPECTED_RUBRIC)
            self.assertEqual(report["target_mode"], "consumer")
            self.assertEqual(Path(report["root_dir"]).resolve(), root.resolve())
            self.assertEqual(set(report["categories"]), EXPECTED_CATEGORIES)
            self.assertEqual(len(report["categories"]), 7)


if __name__ == "__main__":
    unittest.main(verbosity=2)
