#!/usr/bin/env python3
"""Validate one Claude Code skill's ``SKILL.md`` structure.

This validator intentionally follows the current Claude Code skill contract:
frontmatter fields are optional, ``description`` is recommended, and extension
fields are allowed. It rejects structural/type errors that can make a skill
unusable instead of enforcing a stale repository-specific allowlist.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

import yaml


FRONTMATTER_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|\Z)", re.DOTALL)
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
BOOLEAN_FIELDS = ("user-invocable", "disable-model-invocation")
TEXT_FIELDS = ("description", "when_to_use", "argument-hint", "model")
STRING_OR_LIST_FIELDS = ("allowed-tools", "arguments")


def _parse_frontmatter(content: str) -> tuple[bool, dict[str, Any] | None, str]:
    if not content.startswith("---"):
        return False, None, "No YAML frontmatter found"

    match = FRONTMATTER_RE.match(content)
    if not match:
        return False, None, "Invalid frontmatter format"

    try:
        parsed = yaml.safe_load(match.group(1))
    except yaml.YAMLError as exc:
        return False, None, f"Invalid YAML in frontmatter: {exc}"

    # All documented fields are optional, so an empty frontmatter block is a
    # valid empty mapping rather than a missing-required-fields error.
    if parsed is None:
        parsed = {}
    if not isinstance(parsed, dict):
        return False, None, "Frontmatter must be a YAML dictionary"

    return True, parsed, ""


def _validate_optional_fields(frontmatter: dict[str, Any]) -> tuple[bool, str]:
    if "name" in frontmatter:
        name = frontmatter["name"]
        if not isinstance(name, str):
            return False, f"Name must be a string, got {type(name).__name__}"
        name = name.strip()
        if not name:
            return False, "Name cannot be empty when provided"
        if len(name) > 64:
            return False, f"Name is too long ({len(name)} characters). Maximum is 64 characters."
        if not NAME_RE.fullmatch(name):
            return False, (
                f"Name '{name}' must contain only lowercase letters, digits, and single hyphens, "
                "and cannot start or end with a hyphen"
            )

    for field in TEXT_FIELDS:
        if field in frontmatter and not isinstance(frontmatter[field], str):
            return False, f"{field} must be a string when provided"

    for field in BOOLEAN_FIELDS:
        if field in frontmatter and not isinstance(frontmatter[field], bool):
            return False, f"{field} must be a YAML boolean when provided"

    for field in STRING_OR_LIST_FIELDS:
        if field not in frontmatter:
            continue
        value = frontmatter[field]
        if not isinstance(value, (str, list)):
            return False, f"{field} must be a string or YAML list when provided"
        if isinstance(value, list) and not all(isinstance(item, str) for item in value):
            return False, f"{field} list entries must all be strings"

    if "metadata" in frontmatter and not isinstance(frontmatter["metadata"], dict):
        return False, "metadata must be a YAML dictionary when provided"

    return True, "Skill structure is valid!"


def validate_skill(skill_path: str | Path) -> tuple[bool, str]:
    """Validate a skill directory without imposing repository-only schema fields."""
    skill_path = Path(skill_path)
    skill_md = skill_path / "SKILL.md"
    if not skill_md.is_file():
        return False, "SKILL.md not found"

    try:
        content = skill_md.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        return False, f"Unable to read SKILL.md: {exc}"

    ok, frontmatter, message = _parse_frontmatter(content)
    if not ok or frontmatter is None:
        return False, message

    return _validate_optional_fields(frontmatter)


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        print("Usage: python quick_validate.py <skill_directory>")
        return 2

    valid, message = validate_skill(argv[0])
    print(message)
    return 0 if valid else 1


if __name__ == "__main__":
    sys.exit(main())
