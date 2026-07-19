---
name: model-route
description: Recommends the best model tier (haiku, sonnet, opus) for a task by complexity and budget, with a fallback model if the first attempt fails.
version: "1.0.0"
author: "mykcs"
license: "MIT"
last_updated: "2026-07-19"
---


> Migrated from `~/.claude/commands/model-route.md` on 2026-06-15.
> Original slash command continues to work; this skill version supports auto-trigger by description keyword.

Recommend the best model tier for the current task by complexity and budget.

## Usage

`/model-route [task-description] [--budget low|med|high]`

## Routing Heuristic

- `haiku`: deterministic, low-risk mechanical changes
- `sonnet`: default for implementation and refactors
- `opus`: architecture, deep review, ambiguous requirements

## Required Output

- recommended model
- confidence level
- why this model fits
- fallback model if first attempt fails

## Arguments

$ARGUMENTS:
- `[task-description]` optional free-text
- `--budget low|med|high` optional
