import importlib.util
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

MODULE_PATH = Path(__file__).with_name("rich_audit.py")
spec = importlib.util.spec_from_file_location("rich_audit", MODULE_PATH)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class SecurityExclusionTests(unittest.TestCase):
    def test_runtime_copies_are_excluded_but_active_source_is_scanned(self):
        with tempfile.TemporaryDirectory() as d:
            home = Path(d)
            claude = home / ".claude"
            omc = home / ".omc"
            active = claude / "scripts" / "active.py"
            active.parent.mkdir(parents=True)
            secret = 'api_key="' + "A" * 40 + '"'
            active.write_text(secret)
            os.chmod(active, 0o777)
            active_json = claude / "api-keys.json"
            active_json.write_text('{"MINIMAX_API_KEY": "' + "B" * 48 + '"}')

            excluded = [
                claude / ".worktrees" / "x" / "copy.py",
                claude / ".venv" / "copy.py",
                claude / "session-env" / "session" / "copy.py",
                claude / "node_modules" / "copy.py",
                claude / "plugins" / "cache" / "copy.py",
                claude / "plugins" / "marketplaces" / "vendor" / "copy.py",
                omc / ".cache" / "copy.py",
                omc / "state" / "checkpoints" / "copy.json",
                omc / "state" / "sessions" / "copy.json",
            ]
            for path in excluded:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(secret)
                os.chmod(path, 0o777)

            with patch.object(audit, "HOME", home), \
                 patch.object(audit, "CLAUDE_DIR", claude), \
                 patch.object(audit, "OMC_DIR", omc):
                findings = audit.check_security({})

            files = [item["file"] for item in findings]
            self.assertIn(str(active), files)
            self.assertIn(str(active_json), files)
            for path in excluded:
                self.assertNotIn(str(path), files)


if __name__ == "__main__":
    unittest.main()
