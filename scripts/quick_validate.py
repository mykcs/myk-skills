#!/usr/bin/env python3
"""Repository entrypoint for the canonical skill quick validator.

The implementation lives with ``skill-creator`` so authoring and repository CI
use one validator instead of maintaining two copies that can drift apart.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from typing import Any


CANONICAL_VALIDATOR = (
    Path(__file__).resolve().parents[1] / "skill-creator" / "scripts" / "quick_validate.py"
)


def _load_canonical() -> ModuleType:
    spec = importlib.util.spec_from_file_location("myk_skill_quick_validate", CANONICAL_VALIDATOR)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load canonical validator: {CANONICAL_VALIDATOR}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_CANONICAL = _load_canonical()
validate_skill = _CANONICAL.validate_skill


def main(argv: list[str] | None = None) -> int:
    return _CANONICAL.main(sys.argv[1:] if argv is None else argv)


if __name__ == "__main__":
    sys.exit(main())
