---
name: quality-gate
description: Runs the ECC quality pipeline (formatter, lint, type checks) on a file or directory on demand, with optional --fix and --strict flags.
---


> Migrated from `~/.claude/commands/quality-gate.md` on 2026-06-15.
> Original slash command continues to work; this skill version supports auto-trigger by description keyword.

Run the ECC quality pipeline on demand for a file or project scope.

## Usage

`/quality-gate [path|.] [--fix] [--strict]`

- default target: current directory (`.`)
- `--fix`: allow auto-format/fix where configured
- `--strict`: fail on warnings where supported

## Pipeline

1. Detect language/tooling for target.
2. Run formatter checks.
3. Run lint/type checks when available.
4. Produce a concise remediation list.

## Notes

This command mirrors hook behavior but is operator-invoked.

## Arguments

$ARGUMENTS:
- `[path|.]` optional target path
- `--fix` optional
- `--strict` optional
