#!/usr/bin/env python3
"""Run repository validation and emit metadata-minimized Cloudflare assets.

The Worker is CI-only. Public workers.dev and preview URLs are disabled; these
assets only provide a deployable object after the repository checks succeed.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "cloudflare-dist"


def main() -> int:
    result = subprocess.run(
        [sys.executable, "scripts/ci_check.py"],
        cwd=ROOT,
        check=False,
    )
    if result.returncode != 0:
        return result.returncode

    OUTPUT.mkdir(parents=True, exist_ok=True)
    report = {
        "status": "passed",
        "validation": "myk-skills repository checks",
        "checks": [
            "active top-level SKILL.md structural validation",
            "repository and active-skill Python regression evals",
            "host-self-evolve compatibility and modernization checks",
        ],
    }
    (OUTPUT / "status.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (OUTPUT / "robots.txt").write_text("User-agent: *\nDisallow: /\n", encoding="utf-8")
    (OUTPUT / "index.html").write_text(
        "<!doctype html><html><head><meta charset='utf-8'>"
        "<meta name='robots' content='noindex,nofollow'>"
        "<title>myk-skills validation</title></head>"
        "<body><main><h1>myk-skills validation passed</h1>"
        "<p>Repository skill checks and regression evals passed.</p>"
        "</main></body></html>\n",
        encoding="utf-8",
    )
    print("Generated Cloudflare validation assets in cloudflare-dist/", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
