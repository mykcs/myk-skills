---
name: 0001-consolidate-orphan-reference-documents
created: 2026-05-18
status: accepted
---

# Consolidate Orphan Reference Documents into Skill Directories

## Context

The repository had 20+ reference documents at the repository root level and in a `references/` directory that had no `SKILL.md` association. Claude Code's skill loading mechanism only recognizes directories with `SKILL.md` files, so these documents were "orphaned" — invisible to the skill system despite being high-quality content.

Additionally, the root directory contained 28 document files, creating significant cognitive load for anyone navigating the repository.

## Decision

Move all orphan reference documents into the skill directory they belong to, under a `references/` subdirectory. Create `SKILL.md` for agent directories that lacked one.

### Migration Map

| Document | Target Directory |
|----------|-----------------|
| `forms.md`, `reference.md` | `pdf/references/` |
| `editing.md`, `html-template.md` | `pptx/references/` |
| `astro-modernization-checklist.md` | `publishing-astro-websites/references/` |
| `audit-patterns.md`, `project-page-audit-checklist.md` | `rich-audit/references/` |
| `frontend-checklist.md` | `frontend-design/references/` |
| `cdp-api.md`, `web.md` | `web-access/references/` |
| `advanced-patterns.md`, `benchmarks.md`, etc. (15 files) | `core/references/` |
| `ADR-FORMAT.md`, `CONTEXT-FORMAT.md` | `docs/` |
| `agents/analyzer.md`, `grader.md` | (wrapped in `agents/SKILL.md`) |

## Consequences

**Positive:**
- All reference documents now discoverable via skill directory structure
- Root directory reduced from 28 files to minimal set
- Clear ownership of each document

**Negative:**
- Existing links to these documents from external sources will break
- Users who bookmarked old paths need to update

## Alternatives Considered

1. **Keep flat structure with README index** — Rejected because it doesn't integrate with Claude Code's skill loading mechanism
2. **Merge all references into a single `references/` SKILL** — Rejected because references serve different skills and should be co-located
