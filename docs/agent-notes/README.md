# Agent Notes

This directory contains durable, agent-facing handoffs for repository architecture, migration decisions, operational constraints, and verified invariants.

Use these notes as **orientation**, not as a substitute for executable tests or live provider state. When a note conflicts with current code, tests, Cloudflare/GitHub runtime state, or newer dated guidance, verify the current state before changing behavior.

## Current notes

- [`2026-08-10-harness-ci-cleanup.md`](./2026-08-10-harness-ci-cleanup.md) — current `myk-skills` validation architecture, Cloudflare/GitHub CI split, exact-head merge gate, validator contract, Makefile cleanup, Build watch-path behavior, and anti-regression guidance.

## Maintenance rules

- Prefer one focused note per completed architecture/migration thread.
- Record decisions, invariants, verified behavior, and rollback boundaries; do not paste raw chat transcripts.
- Link concrete repository files, PRs, and commits when they are part of the evidence trail.
- Distinguish **repository desired state** from **live provider configuration**. Source-controlled docs cannot prove current Cloudflare Dashboard or GitHub Ruleset state.
- Update or supersede stale notes rather than layering contradictory instructions indefinitely.
