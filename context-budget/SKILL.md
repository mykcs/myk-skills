---
name: context-budget
description: Cross-harness context-engineering workflow for reducing hot-context waste, improving just-in-time retrieval, preserving structured long-horizon state, and detecting context/tool overload without assuming a fixed context-window size.
version: "2.0.0"
author: "mykcs"
license: "MIT"
last_updated: "2026-08-11"
triggers:
  - context-budget
  - /context-budget
  - optimize context
  - context window
  - context engineering
  - context compaction
  - context pruning
  - 上下文优化
  - 上下文工程
  - context truncation
---

# context-budget

This skill is the canonical shared context-engineering workflow. Harness-native commands such as Claude's `/context-budget` are compatibility/UX adapters and must delegate here rather than carrying a second policy.

The objective is **not** to make every instruction shorter. It is to maximize the usefulness of the context that is actually hot at each step while preserving durable state outside the active window.

## Core principles

1. **Progressive disclosure** — keep always-loaded instructions small; load detailed skills, protocols, references, and code only when relevant.
2. **Just-in-time retrieval** — prefer stable identifiers such as paths, symbols, URLs, query names, and artifact IDs that the agent can resolve when needed instead of preloading full content.
3. **Structured state over transcript retention** — preserve goals, decisions, blockers, verification evidence, and next actions in compact durable notes/artifacts; do not rely on replaying the whole conversation.
4. **Compaction-aware design** — assume long-running agents may compact/reset context. Important state must survive in explicit artifacts, not only in prose several turns back.
5. **Tool-result hygiene** — raw tool results are usually temporary. Once their exact bytes are no longer needed, clear, summarize, or replace them with references/evidence records.
6. **Role-scoped context and tools** — specialists should receive the context/tool surface required for their role, not the entire harness catalog.
7. **No invented context limit** — read the current model/runtime window when available. If it is unknown, optimize relative waste and retrieval quality rather than assuming 200K or another fixed number.

## Workflow

### 1. Inventory the active context surface

Classify loaded/discoverable material into:

- **HOT** — must be present in most turns: short durable policy, current user goal, critical safety/ownership boundaries.
- **WARM** — should be discoverable just in time: skills, detailed SOPs, specialist prompts, project docs, tool schemas, recent structured notes.
- **COLD** — archive/forensic material: old cases, completed plans, stale run logs, historical research snapshots, deprecated instructions.

Include, where applicable:

- `AGENTS.md` / `CLAUDE.md` / system instructions;
- active rules/protocols;
- skills and skill metadata;
- command adapters;
- agent routing metadata and specialist prompts;
- MCP/plugin/tool schemas exposed to the model;
- memory/handoff/session notes;
- repeated raw tool results or copied documentation.

### 2. Detect high-value problems

Flag:

- duplicated semantics in multiple hot files;
- generated projections treated as independent policy;
- large always-loaded detail that can become a JIT skill/reference;
- stale provider/model/tool names in shared policy;
- archive/case/run material being loaded as current instruction;
- raw tool responses retained long after use;
- repeated full-file reads where identifiers or targeted retrieval would work;
- too many irrelevant tools/skills exposed to a specialist;
- context that will be lost across compaction because no structured state artifact exists;
- self-referential shims or adapters that point back to themselves instead of a canonical workflow.

### 3. Prioritize by expected value

Rank fixes using:

```text
priority = expected reliability gain + context savings + retrieval clarity - migration risk
```

Prefer structural savings over cosmetic shortening:

1. move cold material out of hot context;
2. convert reusable detail into JIT skills/references;
3. deduplicate semantics at the canonical owner;
4. summarize/clear stale tool results;
5. scope tools/context by role;
6. only then micro-optimize wording.

### 4. Design compaction/resume state

For long-horizon work, maintain a compact state artifact containing only what a fresh agent/session needs:

```text
Goal
Current owner/scope
Decisions already made
Files/artifacts changed
Verification evidence
Known blockers/risks
Next concrete actions
```

Do not copy the whole transcript into this artifact. It is a resume contract, not a diary.

### 5. Validate changes

When practical, compare before/after on representative tasks. Measure at least the dimensions that matter for the change:

- task success / correctness;
- context or token usage when observable;
- tool-call count and irrelevant calls;
- latency/runtime;
- retrieval precision/recall or missed context;
- regressions after compaction/session restart.

A smaller prompt is not automatically better if it reduces correctness or makes retrieval brittle.

## Optional arguments

- `--verbose` — include the full inventory and rationale.
- `--hot-only` — focus on always-loaded context.
- `--role <name>` — inspect the context/tool surface for one agent role.
- `--resume-state` — focus on long-horizon compaction/session handoff.

## Output contract

```text
CONTEXT ENGINEERING REPORT

Window/runtime: <detected value | unknown>
Hot context:     <main surfaces>
Warm/JIT:        <main surfaces>
Cold/archive:    <main surfaces>

Top issues:
1. <issue> — <why it matters>
2. ...

Recommended moves:
- KEEP HOT: ...
- MOVE TO JIT: ...
- SUMMARIZE/CLEAR: ...
- ARCHIVE/COLD: ...
- SCOPE BY ROLE: ...

Compaction/resume risk: LOW | MEDIUM | HIGH
Validation plan: <before/after evidence>
```

## Cross-harness ownership

- Shared context-engineering semantics live here.
- Claude/Codex native compaction, memory, context-editing, and tool-discovery mechanisms stay native; use them rather than emulating them in shared prose when possible.
- Always-loaded shared instructions should contain short durable policy and pointers, not a copy of this full workflow.
