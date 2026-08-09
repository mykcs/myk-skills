"""Safety regressions for the CI-only Cloudflare Workers configuration."""

from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class CloudflareCiConfigTests(unittest.TestCase):
    def test_worker_has_no_public_routes(self) -> None:
        config = json.loads((ROOT / "wrangler.jsonc").read_text(encoding="utf-8"))
        self.assertEqual(config["name"], "myk-skills-validation")
        self.assertIs(config["workers_dev"], False)
        self.assertIs(config["preview_urls"], False)
        self.assertEqual(config["assets"]["directory"], "./cloudflare-dist")

    def test_cloudflare_build_installs_pinned_ci_dependencies(self) -> None:
        package = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
        scripts = package["scripts"]
        self.assertIn("pip install", scripts["cloudflare:build"])
        self.assertIn("requirements-ci.txt", scripts["cloudflare:build"])
        self.assertIn("scripts/cloudflare_build.py", scripts["cloudflare:build"])
        self.assertEqual(scripts["cloudflare:deploy"], "wrangler deploy")
        self.assertEqual(scripts["cloudflare:preview"], "wrangler versions upload")
        self.assertEqual(package["devDependencies"]["wrangler"], "4.114.0")

    def test_ci_python_dependencies_are_pinned(self) -> None:
        requirements = {
            line.strip()
            for line in (ROOT / "requirements-ci.txt").read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        }
        self.assertEqual(
            requirements,
            {"PyYAML==6.0.3", "shellcheck-py==0.11.0.1"},
        )
        self.assertEqual((ROOT / ".python-version").read_text(encoding="utf-8").strip(), "3.12")

    def test_generated_cloudflare_state_is_ignored(self) -> None:
        ignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
        self.assertIn(".wrangler/", ignore)
        self.assertIn("cloudflare-dist/", ignore)

    def test_build_assets_do_not_embed_repository_metadata(self) -> None:
        build = (ROOT / "scripts" / "cloudflare_build.py").read_text(encoding="utf-8")
        for forbidden in (
            "GITHUB_SHA",
            "GITHUB_REPOSITORY",
            "CF_PAGES_COMMIT_SHA",
            "CF_PAGES_BRANCH",
            "CLOUDFLARE_ACCOUNT_ID",
        ):
            self.assertNotIn(forbidden, build)
        self.assertIn('"status": "passed"', build)
        self.assertIn("scripts/ci_check.py", build)

    def test_github_actions_is_manual_fallback_only(self) -> None:
        workflow = (ROOT / ".github" / "workflows" / "rich-audit-ci.yml").read_text(
            encoding="utf-8"
        )
        trigger_block = workflow.split("\non:\n", 1)[1].split("\n\n", 1)[0]
        self.assertIn("workflow_dispatch:", trigger_block)
        self.assertNotIn("push:", trigger_block)
        self.assertNotIn("pull_request:", trigger_block)
        self.assertIn("python3 scripts/ci_check.py", workflow)
        self.assertIn("requirements-ci.txt", workflow)

    def test_required_check_policy_accounts_for_skipped_builds(self) -> None:
        policy = (ROOT / "docs" / "cloudflare-required-check-policy.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("do not configure", policy.lower())
        self.assertIn("global required status check", policy)
        self.assertIn("Build watch paths", policy)
        self.assertIn("exact latest head commit", policy)
        self.assertIn("Cloudflare Workers & Pages GitHub App", policy)
        self.assertIn("scripts/ci_check.py", policy)


if __name__ == "__main__":
    unittest.main(verbosity=2)
