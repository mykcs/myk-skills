---
name: curl
description: Curated curl examples and managed-agents HTTP integration guide. Use when debugging API calls, exploring HTTP behavior, or working with managed LLM agents.
when_to_use: curl examples, managed-agents API calls, HTTP debugging
version: "1.0.0"
author: "mykcs"
license: "MIT"
last_updated: "2026-07-19"
---

# Curl Skill

Curated curl usage examples and managed-agents HTTP integration reference.

## What's in this skill

- `examples.md` — Practical curl examples (auth, headers, multipart, retries)
- `managed-agents.md` — HTTP integration patterns for managed LLM agents

## When to use

- Debugging API calls from terminal
- Quick HTTP exploration of a service
- Configuring managed-agent HTTP clients

## Note

This skill supplements Claude Code's built-in WebFetch with terminal-based
HTTP examples. For complex workflows, prefer Bash with `curl -sS` + `jq`.
