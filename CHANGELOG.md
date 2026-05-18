# Changelog

All notable changes to this skill repository are documented here.

## [1.0.0] - 2026-05-18

### Added

- `agents/SKILL.md` - Agent skill definition (analyzer, comparator, grader)
- `docs/adr/` - ADR storage directory
- `core/references/` - Core library references (15 files)
- `web-access/references/` - Web access references (cdp-api, web)
- `frontend-design/references/` - Frontend design references
- `publishing-astro-websites/references/` - Publishing references
- `rich-audit/references/` - Audit references
- `pdf/references/` - PDF references (forms, advanced-reference)
- `pptx/references/` - PPTX references (editing, html-template)

### Fixed

- `.claude-plugin/` ownership统一为 mykcs
- `core/easing.py` bare `pow()` 替换为 `**` 运算符
- `LICENSE` copyright 统一为 mykcs

### Refactored

- `ADR-FORMAT.md` → `docs/ADR-FORMAT.md`
- `CONTEXT-FORMAT.md` → `docs/CONTEXT-FORMAT.md`
- Root-level orphan docs consolidated into skill directories
- `references/` directory flattened into respective skill `references/` subdirs

### Removed

- `SKILL.md` from repository root (moved to `xlsx/SKILL.md`)
