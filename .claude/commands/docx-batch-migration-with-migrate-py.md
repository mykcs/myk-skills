---
name: docx-batch-migration-with-migrate-py
description: Workflow command scaffold for docx-batch-migration-with-migrate-py in myk-skills.
allowed_tools: ["Bash", "Read", "Write", "Grep", "Glob"]
---

# /docx-batch-migration-with-migrate-py

Use this workflow when working on **docx-batch-migration-with-migrate-py** in `myk-skills`.

## Goal

Batch-migrate all paper cards in docx files to the new schema using bin/migrate.py, including OpenReview API integration, confidence heuristics, and optimized block replacement.

## Common Files

- `teacher-report/bin/migrate.py`
- `teacher-report/SKILL.md`
- `teacher-report/references/paper-card.md`
- `teacher-report/references/paper-entry.md`

## Suggested Sequence

1. Understand the current state and failure mode before editing.
2. Make the smallest coherent change that satisfies the workflow goal.
3. Run the most relevant verification for touched files.
4. Summarize what changed and what still needs review.

## Typical Commit Signals

- Implement or refine extract_paper_cards_from_doc logic to accurately identify paper card blocks.
- Integrate or update status detection heuristics and OpenReview API fallback in bin/migrate.py.
- Generate new DocxXML blocks for the upgraded paper card format.
- Optimize migration to use batch block_replace instead of multiple block_delete/block_insert calls.
- Run dry-run migration and audit results (migrated/skipped/failed).

## Notes

- Treat this as a scaffold, not a hard-coded script.
- Update the command if the workflow evolves materially.