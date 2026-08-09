#!/usr/bin/env python3
"""Platform-neutral validation entrypoint for myk-skills.

This script is intentionally independent of GitHub Actions and Cloudflare. It
collects the repository checks that both environments can call later, so CI
providers do not become the source of validation policy.
"""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from types import ModuleType
from typing import Sequence


ROOT = Path(__file__).resolve().parents[1]
ROOT_EVALS = ROOT / "evals"
HOST_REQUIRED_SCRIPTS = (
    "dead_code_detector.py",
    "commands_to_skills_migrator.py",
    "lint_runner.py",
    "memory_audit_runner.py",
    "skill_authoring_checker.py",
    "skill_overlap_enhancer.py",
    "waste_token_detector.py",
    "auto_fix_proposer.py",
)


def _load_module(path: Path, name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load Python module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def active_skill_dirs(root: Path = ROOT) -> list[Path]:
    """Return active top-level skill directories in deterministic order."""
    return sorted(
        (
            path
            for path in root.iterdir()
            if path.is_dir()
            and not path.name.startswith((".", "_"))
            and (path / "SKILL.md").is_file()
        ),
        key=lambda path: path.name,
    )


def skill_eval_dirs(root: Path = ROOT) -> list[Path]:
    """Return active skill eval directories that contain unittest files."""
    result: list[Path] = []
    for skill_dir in active_skill_dirs(root):
        eval_dir = skill_dir / "evals"
        if eval_dir.is_dir() and any(eval_dir.glob("test_*.py")):
            result.append(eval_dir)
    return result


def validate_active_skills(root: Path = ROOT) -> list[str]:
    """Validate every active top-level SKILL.md and return failure messages."""
    validator = _load_module(root / "scripts" / "quick_validate.py", "myk_repo_quick_validate")
    failures: list[str] = []
    for skill_dir in active_skill_dirs(root):
        valid, message = validator.validate_skill(skill_dir)
        if not valid:
            failures.append(f"{skill_dir.name}: {message}")
    return failures


def run_command(
    command: Sequence[str],
    *,
    cwd: Path = ROOT,
    env: dict[str, str] | None = None,
    capture_output: bool = False,
) -> subprocess.CompletedProcess[str]:
    """Run one check and fail immediately if the command exits non-zero."""
    print(f"$ {' '.join(command)}")
    return subprocess.run(
        list(command),
        cwd=cwd,
        env=env,
        text=True,
        capture_output=capture_output,
        check=True,
    )


def parse_tool_json(result: subprocess.CompletedProcess[str], expected_tool: str) -> dict:
    """Parse a smoke-check JSON payload and verify its tool identity."""
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"{expected_tool} did not emit valid JSON") from exc
    if payload.get("tool") != expected_tool:
        raise RuntimeError(
            f"Expected tool {expected_tool!r}, got {payload.get('tool')!r}"
        )
    return payload


def prepare_host_ci_home(home: Path) -> None:
    """Reproduce the minimal HOME fixture used by the legacy host CI."""
    claude = home / ".claude"
    (claude / "knowledge" / "cases" / "wiki").mkdir(parents=True)
    (claude / "knowledge" / "cases" / "wiki" / "README.md").write_text(
        "# CI stub\n", encoding="utf-8"
    )
    for name in ("hooks", "scripts", "rules", "memory", "commands"):
        (claude / name).mkdir(parents=True, exist_ok=True)
    (claude / "memory" / "MEMORY.md").write_text("# CI stub\n", encoding="utf-8")
    stub_sh = claude / "scripts" / "stub.sh"
    stub_sh.write_text('#!/bin/bash\necho "stub"\n', encoding="utf-8")
    stub_sh.chmod(0o755)
    (claude / "commands" / "stub-cmd.md").write_text(
        "# stub command\n", encoding="utf-8"
    )

    stub_skill = home / ".agents" / "skills" / "stub-skill"
    stub_skill.mkdir(parents=True)
    (stub_skill / "SKILL.md").write_text(
        "---\n"
        "name: stub-skill\n"
        "description: Stub skill for CI testing with a third-person description.\n"
        "metadata:\n"
        '  version: "1.0.0"\n'
        "---\n"
        "# Stub Skill\n"
        "CI stub for detection-script smoke tests.\n",
        encoding="utf-8",
    )


def check_host_modernization(root: Path = ROOT) -> list[str]:
    """Preserve the file/protocol assertions from the legacy GitHub workflow."""
    host = root / "host-self-evolve"
    failures: list[str] = []
    skill_md = host / "SKILL.md"
    if not skill_md.is_file() or "PER Workflow" not in skill_md.read_text(encoding="utf-8"):
        failures.append("host-self-evolve/SKILL.md: PER Workflow marker missing")

    consistency = host / "references" / "consistency-6d"
    for number in range(1, 7):
        if not list(consistency.glob(f"{number}-*.md")):
            failures.append(f"host-self-evolve consistency-6d/{number}-*.md missing")

    for script_name in HOST_REQUIRED_SCRIPTS:
        if not (host / "scripts" / script_name).is_file():
            failures.append(f"host-self-evolve/scripts/{script_name} missing")
    return failures


def run_unittest_dir(test_dir: Path, *, cwd: Path = ROOT, env: dict[str, str] | None = None) -> None:
    if not test_dir.is_dir() or not any(test_dir.glob("test_*.py")):
        return
    run_command(
        [sys.executable, "-m", "unittest", "discover", str(test_dir), "-p", "test_*.py", "-v"],
        cwd=cwd,
        env=env,
    )


def run_host_self_evolve_checks(root: Path = ROOT) -> None:
    """Run the substantive checks currently owned by rich-audit-ci.yml."""
    host = root / "host-self-evolve"
    failures = check_host_modernization(root)
    if failures:
        raise RuntimeError("Host modernization checks failed:\n- " + "\n- ".join(failures))

    with tempfile.TemporaryDirectory(prefix="myk-skills-ci-home-") as tmp:
        home = Path(tmp)
        prepare_host_ci_home(home)
        env = os.environ.copy()
        env["HOME"] = str(home)

        run_command(
            [sys.executable, "-m", "unittest", "scripts.test_detection_scripts", "-v"],
            cwd=host,
            env=env,
        )
        dead_code = run_command(
            [sys.executable, "scripts/dead_code_detector.py"],
            cwd=host,
            env=env,
            capture_output=True,
        )
        parse_tool_json(dead_code, "dead_code_detector.py")

        lint = run_command(
            [sys.executable, "scripts/lint_runner.py"],
            cwd=host,
            env=env,
            capture_output=True,
        )
        parse_tool_json(lint, "lint_runner.py")


def main() -> int:
    print("== myk-skills validation ==")

    print("\n[1/4] Validate active SKILL.md files")
    failures = validate_active_skills(ROOT)
    if failures:
        print("Active skill validation failed:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    print(f"Validated {len(active_skill_dirs(ROOT))} active top-level skills")

    print("\n[2/4] Run repository evals")
    run_unittest_dir(ROOT_EVALS, cwd=ROOT)

    print("\n[3/4] Run active skill evals")
    eval_dirs = skill_eval_dirs(ROOT)
    for eval_dir in eval_dirs:
        print(f"-- {eval_dir.relative_to(ROOT)}")
        run_unittest_dir(eval_dir, cwd=ROOT)
    print(f"Ran {len(eval_dirs)} active skill eval suites")

    print("\n[4/4] Preserve host-self-evolve CI checks")
    run_host_self_evolve_checks(ROOT)

    print("\nPASS: myk-skills validation complete")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, RuntimeError, subprocess.CalledProcessError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        sys.exit(1)
