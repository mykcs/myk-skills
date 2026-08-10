---
name: harness-upgrade
description: Research-grounded workflow for upgrading Claude/Codex/agent harnesses. Refreshes current runtime state, searches recent primary research and official vendor guidance before design changes, minimizes hot context and tool surface, and verifies upgrades with independent evidence.
version: "1.0.0"
author: "mykcs"
license: "MIT"
last_updated: "2026-08-11"
triggers:
  - harness upgrade
  - upgrade harness
  - modernize harness
  - improve harness
  - harness architecture
  - harness consolidation
  - agent harness upgrade
  - 升级 harness
  - harness 升级
  - 智能体框架升级
---

# harness-upgrade

This is the canonical cross-harness workflow for **changing the harness itself**. It is intentionally different from `harness-audit`, which is read-only scoring/inspection.

The core rule is:

> **Never treat the repository's current harness design as timeless. Before making a substantive harness change, refresh current runtime truth and search for recent primary research plus current official platform guidance.**

A harness upgrade is complete only when the new design is grounded in current evidence, mapped to an authoritative owner, implemented without unnecessary duplication, and verified against both behavior and infrastructure.

## 1. Mandatory research refresh

For any substantive change to agents, skills, commands, hooks, context/memory, orchestration, permissions, sandboxes, routing, verification, or shared instruction architecture:

1. **Refresh current state first** — read current `main`, active runtime config, mounted hooks, routing metadata, shared-skill ownership, and any machine-readable manifest. Do not design against a stale handoff.
2. **Search the web before editing** — use current official vendor documentation and recent primary research. Prefer sources published or materially updated within the last 12 months; include older foundational work only when still load-bearing.
3. **Use primary evidence** — official OpenAI/Anthropic/platform engineering or safety documentation, original papers/preprints, benchmark papers, and source repositories. Secondary summaries may help discovery but should not be the basis for architecture decisions when primary sources exist.
4. **Search for disconfirming evidence** — do not collect only papers that support the proposed change. Look for ablations, negative results, benchmark-noise findings, and deployment caveats.
5. **Record applicability, not just citations** — for each load-bearing source, state: finding, affected harness surface, why it applies here, and whether it changes the planned design.
6. **If research does not justify a change, keep the current design.** Research is a gate against stale assumptions, not a ritual that forces churn.

Minimum evidence for a high-impact harness change:

- at least one current first-party source for each affected platform/runtime whose behavior may have changed;
- at least one independent primary research source for any claimed general agent-design improvement;
- explicit note when evidence conflicts or is benchmark-specific.

## 2. Design defaults for frontier agents

Use these as hypotheses to test against current evidence, not as eternal laws.

### Keep the core loop simple

Prefer the harness-native execution loop, sandbox, approvals, shell/file tools, skills, compaction, tracing, and platform-native primitives over bespoke wrappers that duplicate them.

### Progressive disclosure over monolithic hot context

Keep always-loaded instructions small. Put detailed procedures in discoverable skills/protocols and load them just in time. Avoid preloading large archives, raw tool outputs, or every specialist instruction into every turn.

### Structured durable state over transcript hoarding

For long-running work, preserve compact structured state such as task goals, decisions, blockers, tested evidence, and next actions outside the active context. After compaction/session boundaries, resume from those artifacts rather than replaying the full trace.

### Minimize irrelevant tool/context exposure

Give an agent the tools and context required for its current role. Do not mirror every tool, hook, command, or skill across harnesses for symmetry. Prefer role-scoped or task-scoped discovery when the runtime supports it.

### Bounded autonomy

Optimize for high autonomy **inside explicit technical boundaries**. Use sandboxing/least privilege as the primary boundary and reserve synchronous review for boundary-crossing, destructive, security-sensitive, or otherwise high-impact actions. Prefer native approval/auto-review mechanisms over new ad-hoc prompt gates when available.

### Specialize only where specialization pays

Do not create multi-agent structure just because parallel agents exist. Use subagents/specialists when they reduce context interference, enable independent verification, or parallelize separable work. Keep one clear top-level orchestration owner.

## 3. Context-engineering upgrade gate

When changing instruction files, memory, tool routing, or compaction:

1. classify context as **hot** (must always be present), **warm** (discoverable/JIT), or **cold** (archive/forensic only);
2. move low-frequency detail out of hot context before rewriting it shorter in-place;
3. clear or summarize stale raw tool results when their exact bytes are no longer needed;
4. prefer file/path/identifier references that the agent can resolve on demand;
5. preserve high-value state through structured notes across compaction/session boundaries;
6. if practical, run a small before/after ablation on representative tasks and compare success, tool calls, latency/token use, and regressions.

Do not assume a fixed context-window size. Read current model/runtime capabilities when available; otherwise optimize relative waste rather than inventing a token limit.

## 4. Verification portfolio for harness changes

A high-impact harness upgrade should not depend on one fixed verifier or one benchmark. Verification must co-evolve with the generator and the harness.

Use a portfolio appropriate to the change:

- **Static/config checks** — schema, ownership, mounts, references, generated-vs-canonical boundaries.
- **Executable tests** — unit/integration/CLI tests that exercise the changed behavior.
- **Environment fingerprint** — record relevant OS/runtime/tool versions for hosted or benchmark validation so infrastructure drift is separable from product regressions.
- **Independent review** — a read-only verifier/reviewer context that did not author the implementation.
- **Intent evidence** — verify the actual user/acceptance goal, not only proxy tests.
- **Adversarial or pass-2 review** — when the change affects security, permissions, routing, publication, memory, or verification itself.

Classify failures explicitly as one of:

- implementation/regression;
- policy/ownership drift;
- infrastructure/environment failure;
- insufficient evidence / unverifiable boundary.

Never convert an unavailable hosted gate into PASS.

## 5. Safe change sequence

1. Refresh every affected repository/owner.
2. Build a current inventory of the changed surface and active callers/mounts.
3. Run the mandatory research refresh.
4. Write a short evidence-to-design delta: **keep / change / retire / test first**.
5. Make the smallest coherent reversible change at the canonical owner.
6. Add/extend machine invariants for load-bearing architecture decisions.
7. Verify locally/through available executable gates before publication.
8. Re-refresh `main` before merge and inspect concurrency overlap.
9. Merge shared semantics before thin consumer adapters when ordering matters.
10. Run post-merge verification; distinguish infrastructure failure from code failure.
11. Preserve a compact research/decision note only for substantive architecture changes. Do not create permanent memory artifacts for routine maintenance.

## 6. Output contract

For a substantive harness upgrade, return:

```text
HARNESS UPGRADE: COMPLETE | PARTIAL | BLOCKED

Current-state owners:
- <surface> -> <canonical owner>

Research refresh:
- As-of: <date>
- Primary sources: <n>
- Key deltas: <what changed our design>
- Disconfirming evidence: <what argued against change>

Changes:
- KEEP: ...
- CHANGE: ...
- RETIRE: ...
- DEFER/TEST FIRST: ...

Verification portfolio:
- Static/config: PASS|FAIL|N/A
- Executable: PASS|FAIL|N/A
- Environment fingerprint: captured|N/A
- Independent review: PASS|FAIL|N/A
- Hosted gate: PASS|FAIL|UNAVAILABLE|N/A

Remaining boundary:
- <only real unresolved human/runtime boundary>
```

## 7. Cross-harness ownership

- Shared upgrade workflow lives here in `myk-skills` / `~/.agents/skills`.
- Claude may add a short always-loaded trigger pointing here; it must not duplicate this full workflow.
- Codex should discover/use this shared skill through native skill routing; do not create a mirrored Claude-style command tree.
- Tool-native sandbox, approvals, hooks, plugins, system skills, compaction, and model routing remain owned by their respective harnesses.

## 8. Future-proofing rule

The concrete research cited in any one upgrade note is historical evidence, **not permanent policy**. On the next harness-upgrade request, run the research refresh again using the then-current date, models, platform capabilities, and primary literature.
