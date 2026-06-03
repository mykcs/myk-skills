# Skill Evolution Log

Records every v-bump from `/skill-evolution` (auto) or manual change.

Format: `<ts> | <skill> | v<old>→v<new> | reason | M=<before> M'=<after>`

## 2026-06-03 — Initial setup

This file was created as part of the `/skill-evolution` v1.0.0 bootstrap.
The skill itself + cron stub at `~/.claude/scripts/run-skill-evolution.sh`
were added in the same change set.

Pending: actual evolution runs require the user to invoke
`/skill-evolution` interactively in a Claude session (the cron stub
only logs a reminder).
