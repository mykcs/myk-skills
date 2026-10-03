"""Regression tests for the server-artifact-governance skill contract."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / "server-artifact-governance" / "SKILL.md"
ZJU = ROOT / "server-artifact-governance" / "references" / "zju-server.md"
EVALS = ROOT / "server-artifact-governance" / "evals" / "evals.json"


class TestServerArtifactGovernanceSkill(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.skill = SKILL.read_text(encoding="utf-8")
        cls.zju = ZJU.read_text(encoding="utf-8")
        cls.evals = json.loads(EVALS.read_text(encoding="utf-8"))

    def test_skill_version_is_v1_1(self) -> None:
        self.assertIn('version: "1.1.0"', self.skill)

    def test_four_gate_model_is_explicit_and_conjunctive(self) -> None:
        for marker in (
            "**OWNERSHIP**",
            "**RECOVERABILITY**",
            "**CURRENT USE / RETENTION**",
            "**EXACT SCOPE / AUTHORITY**",
            "These gates are conjunctive, not a score",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, self.skill)

    def test_common_project_names_are_not_ownership_proof(self) -> None:
        self.assertIn("What is not ownership evidence", self.skill)
        self.assertIn("OpenEVO, Evo, WebShop", self.skill)
        self.assertIn("Shared or unresolved ownership stays protected", self.skill)

    def test_upload_success_is_not_recovery_proof(self) -> None:
        self.assertIn("Separate upload from recovery proof", self.skill)
        self.assertIn("upload completed", self.skill)
        self.assertIn("immutable commit/revision/digest exists", self.skill)
        self.assertIn("A failed recovery gate leaves the local source in place", self.skill)

    def test_recent_use_and_analysis_hold_survive_remote_backup(self) -> None:
        self.assertIn("Remote recovery makes an object **eligible**", self.skill)
        self.assertIn("current analysis/retention hold", self.skill)
        self.assertIn("ANALYSIS HOLD", self.skill)

    def test_broad_cleanup_shortcuts_are_forbidden(self) -> None:
        for marker in (
            "no `docker system prune`",
            "no `docker image prune -a`",
            "no global HF cache sweep",
            "no workspace-wide `rm -rf`",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, self.skill)

    def test_precise_reclaim_and_physical_readback_are_required(self) -> None:
        self.assertIn("one-object transactions", self.skill)
        self.assertIn("exact paths/object IDs", self.skill)
        self.assertIn("logical bytes separately from observed physical `df` delta", self.skill)

    def test_hardlinks_do_not_count_as_physical_reclaim(self) -> None:
        for marker in (
            "Hardlinks, copy-on-write, deduplication, and physical reclaim",
            "group hardlinked paths by `(device, inode)`",
            "deleting one pathname can reclaim",
            "**0 physical bytes**",
            "Never sum per-path `st_blocks` across hardlinks",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, self.skill)

    def test_manifest_reclassification_invalidates_old_approval(self) -> None:
        for marker in (
            "retention/scientific re-review changes the candidate set",
            "treat the old approval as **superseded**",
            "new unique manifest",
            "must not silently authorize the revised semantic scope",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, self.skill)

    def test_critical_headroom_prefers_low_risk_exact_reclaim(self) -> None:
        for marker in (
            "Critical-headroom mode",
            "P3/rebuildable",
            "stop long recursive inventory/hash scans",
            "do not kill/preempt active science",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, self.skill)

    def test_concurrent_cleanup_and_control_plane_fail_closed(self) -> None:
        for marker in (
            "one cleanup writer at a time",
            "overlapping reclaim manifest",
            "least-privilege sidecar",
            "tool-safety denial",
            "tmpfs, permission changes",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, self.skill)

    def test_zju_adapter_routes_to_current_project_authority(self) -> None:
        for marker in (
            "mykcs/zju-server/AGENTS.md",
            "docs/storage-governance-agent-contract.md",
            "docs/storage-pressure-artifact-reclaim-sop.md",
            "docs/research-artifact-lifecycle.md",
            "docs/free-first-backup-policy.md",
            "docs/shared-filesystem-deletion-safety.md",
            "docs/rdc-sidecar-runbook.md",
            "docs/workspace-ownership-contract.md",
            "scripts/verify_remote_reclaim_gate.py",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, self.zju)
        self.assertIn("Current project files win if this reference becomes stale", self.zju)

    def test_recovery_disclosure_and_provider_state_are_separate(self) -> None:
        for marker in (
            "SERVER_ONLY -> REMOTE_BACKED_UP -> RECOVERY_VERIFIED",
            "disclosure_state: PRIVATE | EMBARGOED | PUBLIC | NEVER_PUBLIC",
            "provider_visibility: live observation, not policy authority",
            "Disaster recovery never grants publication authority",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, self.skill)

    def test_research_asset_lifecycle_bridge_exists(self) -> None:
        bridge = ROOT / "server-artifact-governance" / "references" / "research-asset-lifecycle.md"
        text = bridge.read_text(encoding="utf-8")
        for marker in (
            "mykcs/fuhuo_20260419",
            "Experiment Passport",
            "Passport Artifact DAG",
            "exact NOT_AUTHORIZED reclaim proposal",
            "W&B",
            "pointer",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, text)

    def test_evals_cover_name_collision_docker_and_hf_recovery(self) -> None:
        self.assertEqual(self.evals["skill_name"], "server-artifact-governance")
        prompts = "\n".join(case["prompt"] for case in self.evals["evals"])
        self.assertIn("大家都在做 Evo", prompts)
        self.assertIn("docker system df", prompts)
        self.assertIn("已经传到 Hugging Face", prompts)
        self.assertIn("同一个 inode", prompts)
        self.assertIn("重新检查", prompts)
        self.assertIn("另一个 Agent", prompts)
        self.assertIn("no live connection", prompts)


if __name__ == "__main__":
    unittest.main(verbosity=2)
