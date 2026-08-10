#!/usr/bin/env python3
"""Deterministic inventory for every SKILL.md in myk-skills.

The inventory deliberately separates active top-level skills from archives,
benchmark fixtures, plugin-owned skills, and nested reference copies so a raw
recursive count is never mistaken for the active runtime surface.
"""

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class SkillEntry:
    path: str
    name: str
    lifecycle: str
    owner: str
    active: bool


def _read_frontmatter_name(path: Path) -> str:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.parent.name

    if not text.startswith("---\n"):
        return path.parent.name

    for line in text.splitlines()[1:]:
        if line.strip() == "---":
            break
        if line.startswith("name:"):
            value = line.split(":", 1)[1].strip().strip('"\'')
            return value or path.parent.name
    return path.parent.name


def classify_skill(root: Path, skill_md: Path) -> SkillEntry:
    rel = skill_md.relative_to(root)
    parts = rel.parts
    lowered = tuple(part.lower() for part in parts)

    active = (
        len(parts) == 2
        and parts[-1] == "SKILL.md"
        and not parts[0].startswith((".", "_"))
    )

    if active:
        lifecycle = "active"
        owner = "shared-skill-ssot"
    elif any(part.startswith("_archive") or part == "archive" for part in lowered):
        lifecycle = "archive"
        owner = "historical"
    elif any(part.startswith(".deprecated") or "deprecated" in part for part in lowered):
        lifecycle = "deprecated-reference"
        owner = "historical"
    elif "benchmarks" in lowered:
        lifecycle = "benchmark-fixture"
        owner = "benchmark"
    elif "plugins" in lowered:
        lifecycle = "plugin-owned"
        owner = "plugin"
    elif "references" in lowered or "reference" in lowered:
        lifecycle = "reference-copy"
        owner = "parent-skill"
    else:
        lifecycle = "nested-skill"
        owner = "nested"

    return SkillEntry(
        path=rel.as_posix(),
        name=_read_frontmatter_name(skill_md),
        lifecycle=lifecycle,
        owner=owner,
        active=active,
    )


def inventory_repository(root: Path = ROOT) -> dict:
    entries = [
        classify_skill(root, path)
        for path in sorted(root.rglob("SKILL.md"), key=lambda p: p.as_posix())
    ]

    counts: dict[str, int] = {}
    for entry in entries:
        counts[entry.lifecycle] = counts.get(entry.lifecycle, 0) + 1

    active_names = [entry.name for entry in entries if entry.active]
    duplicate_active_names = sorted(
        name for name in set(active_names) if active_names.count(name) > 1
    )

    return {
        "schema_version": 1,
        "root": ".",
        "rules": {
            "active": "top-level <name>/SKILL.md where <name> does not begin with . or _",
            "archive": "paths under _archive/archive",
            "benchmark_fixture": "paths under benchmarks",
            "plugin_owned": "paths under plugins",
            "reference_copy": "nested paths under reference/references",
        },
        "counts": {
            "total_skill_files": len(entries),
            "active": sum(1 for entry in entries if entry.active),
            **dict(sorted(counts.items())),
        },
        "duplicate_active_names": duplicate_active_names,
        "entries": [asdict(entry) for entry in entries],
    }


def render_text(payload: dict) -> str:
    counts = payload["counts"]
    lines = [
        "myk-skills inventory",
        f"total SKILL.md: {counts['total_skill_files']}",
        f"active top-level: {counts['active']}",
    ]
    for lifecycle, count in counts.items():
        if lifecycle in {"total_skill_files", "active"}:
            continue
        lines.append(f"{lifecycle}: {count}")

    duplicates = payload["duplicate_active_names"]
    lines.append(
        "duplicate active names: " + (", ".join(duplicates) if duplicates else "none")
    )
    lines.append("")
    lines.append("Active skills:")
    for entry in payload["entries"]:
        if entry["active"]:
            lines.append(f"- {entry['name']}: {entry['path']}")
    return "\n".join(lines)


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--format", choices=("json", "text"), default="json")
    parser.add_argument("--output", type=Path, help="Write output to a file instead of stdout")
    parser.add_argument(
        "--fail-on-duplicate-active-name",
        action="store_true",
        help="Return non-zero when two active top-level skills declare the same name",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)

    root = args.root.resolve()
    payload = inventory_repository(root)
    rendered = (
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=False) + "\n"
        if args.format == "json"
        else render_text(payload) + "\n"
    )

    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")

    if args.fail_on_duplicate_active_name and payload["duplicate_active_names"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
