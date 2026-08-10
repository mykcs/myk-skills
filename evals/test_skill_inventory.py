from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.skill_inventory import inventory_repository


class SkillInventoryTests(unittest.TestCase):
    def test_classifies_active_archive_plugin_and_reference_skills(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            fixtures = {
                "alpha/SKILL.md": "---\nname: alpha\n---\n# Alpha\n",
                "_archive/old/SKILL.md": "---\nname: old\n---\n# Old\n",
                "plugins/demo/skills/plugin-skill/SKILL.md": "---\nname: plugin-skill\n---\n",
                "alpha/references/example/SKILL.md": "---\nname: example\n---\n",
            }
            for rel, text in fixtures.items():
                path = root / rel
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text, encoding="utf-8")

            payload = inventory_repository(root)
            by_path = {entry["path"]: entry for entry in payload["entries"]}

            self.assertTrue(by_path["alpha/SKILL.md"]["active"])
            self.assertEqual(by_path["_archive/old/SKILL.md"]["lifecycle"], "archive")
            self.assertEqual(
                by_path["plugins/demo/skills/plugin-skill/SKILL.md"]["lifecycle"],
                "plugin-owned",
            )
            self.assertEqual(
                by_path["alpha/references/example/SKILL.md"]["lifecycle"],
                "reference-copy",
            )
            self.assertEqual(payload["counts"]["active"], 1)
            self.assertEqual(payload["counts"]["total_skill_files"], 4)

    def test_reports_duplicate_active_frontmatter_names(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for directory in ("one", "two"):
                path = root / directory / "SKILL.md"
                path.parent.mkdir(parents=True)
                path.write_text("---\nname: shared-name\n---\n", encoding="utf-8")

            payload = inventory_repository(root)
            self.assertEqual(payload["duplicate_active_names"], ["shared-name"])


if __name__ == "__main__":
    unittest.main()
