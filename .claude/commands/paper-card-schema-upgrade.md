---
name: paper-card-schema-upgrade
description: Workflow command scaffold for paper-card-schema-upgrade in myk-skills.
allowed_tools: ["Bash", "Read", "Write", "Grep", "Glob"]
---

# /paper-card-schema-upgrade

Use this workflow when working on **paper-card-schema-upgrade** in `myk-skills`.

## Goal

Upgrade the paper card format across documentation, templates, and migration scripts to a new version (e.g., v0.3.9 → v0.11.0), including new fields, enums, and LLM checks.

## Common Files

- `teacher-report/SKILL.md`
- `teacher-report/references/paper-card.md`
- `teacher-report/references/paper-entry.md`
- `teacher-report/bin/migrate.py`

## Suggested Sequence

1. Understand the current state and failure mode before editing.
2. Make the smallest coherent change that satisfies the workflow goal.
3. Run the most relevant verification for touched files.
4. Summarize what changed and what still needs review.

## Typical Commit Signals

- Update SKILL.md with new changelog, description, and section headers for the new version.
- Rewrite or extend references/paper-card.md to include new frontmatter, relationship sections, and usage guidance.
- Rewrite or extend references/paper-entry.md to add new template fields, enums, and detailed instructions.
- Update bin/migrate.py header docstring to document new migration logic and fields.
- Implement or update migration logic in bin/migrate.py to handle new fields, enums, and LLM checks.

## Notes

- Treat this as a scaffold, not a hard-coded script.
- Update the command if the workflow evolves materially.