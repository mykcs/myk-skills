---
name: conversation-closeout
description: >-
  End-of-conversation knowledge closeout. Use when the user says the conversation is ending,
  wants lessons/preferences/memories/workflows preserved, asks to summarize and sediment what was
  learned, or wants reusable engineering experience written back so future work is faster. Sweep
  the accessible conversation for all reusable value, separate durable lessons from temporary
  state, preserve explicit owner feedback faithfully, deduplicate against existing knowledge,
  route each item to its real writable owner, strengthen project rules/tests/SOPs when behavior
  should change, validate the writeback, and finish with a compact ELI5 report. This is broader
  than record-case: it orchestrates the whole conversation and may delegate individual cases,
  rule consolidation, knowledge-topology repair, or fresh-Agent acceptance to neighboring skills.
when_to_use: >-
  Trigger for “对话结束了”, “收尾一下”, “总结并沉淀经验”, “把今天学到的留下来”, “这些踩坑以后还会遇到”,
  “把我的偏好/想法记下来”, “把可复用的东西都整理掉”, “conversation closeout”, or equivalent
  end-of-session intent across engineering, research, operations, design, content, governance,
  communication, or mixed work.
metadata:
  version: "1.0.0"
  category: knowledge-workflow
  owner: mykcs
---

# Conversation Closeout

Turn a finished conversation into durable future leverage.

The goal is not to write a chronological summary. The goal is:

Scan the whole accessible conversation for anything that would make the owner's next similar task
faster, safer, clearer, or less repetitive, then put each useful thing into its correct long-term
owner.

This includes more than explicit preferences. A closeout may capture recurring engineering
problems, failed approaches, reusable workflows, explicit owner corrections, project decisions,
research-method lessons, tool/provider behavior, repeated failure families, Agent-discovery
improvements, and “how we should work next time” patterns.

Be generous in candidate discovery and strict in what becomes durable.

## Ownership model

This Skill owns the closeout workflow. It does not own every destination.

Use one-fact-one-owner:

- cross-tool owner feedback / learned practice -> mykcs/.agents/docs/learning
- shared reusable workflow / Skill -> mykcs/myk-skills
- project current truth / SOP / test / config -> owning project repository
- Agent knowledge topology / routing -> owning project plus .agents router/registry when needed
- live provider/account/runtime state -> live provider/runtime, not durable prose
- tool-native config/memory candidate -> owning harness only when that surface is authoritative
- historical evidence -> historical/receipt/evidence owner; never rewrite as current truth

Relevant .agents learning contracts live under docs/learning/schemas:
- FEEDBACK_COVERAGE_LEDGER.md
- RAW_RECORD.md
- DERIVED_KNOWLEDGE.md
- FUTURE_TASK_RETRIEVAL_PROOF.md
- CLOSEOUT_RECEIPT.md

Current project/live authority outranks stale handoffs and memory.

## First principle: recover reusable value, not transcript bulk

The owner wants almost everything worth reusing preserved. That does not mean storing every
message.

For every candidate ask:

1. Will this plausibly matter again?
2. Would losing it cause repeated work, repeated correction, avoidable risk, or lost owner intent?
3. Is there a stable owner where it can be found next time?
4. Is the lesson supported by direct feedback or verified evidence?
5. Can it be stated with a useful boundary instead of overgeneralizing one incident?

If the answer is mostly no, keep it out of durable knowledge.

## Phase 0 — Resolve the closeout surface

Before writing anything:

1. identify the accessible conversation window;
2. identify affected repositories/projects/tools;
3. read current project/root Agent instructions;
4. read current .agents learning entrypoints/schemas when available;
5. inspect overlapping open PRs/branches before writes;
6. refresh live facts only when they materially affect a current-rule conclusion.

If only part of the conversation is available, say so. Never invent missing feedback.

If a predecessor closeout exists for the same conversation, do a delta closeout from the previous
boundary instead of re-ingesting the same material.

## Phase 1 — Build a reusable-value inventory

Scan the accessible conversation and identify every meaningful candidate.

### A. Direct owner signal

Look for corrections, explicit preferences, future-default language, acceptance/rejection,
“这个更像我 / 这样更好”, factual corrections, scope boundaries, and instructions about how
future Agents should work.

Preserve strong direct owner wording faithfully when it has reusable value.

Do not upgrade better into accepted, promising into canonical, or one local preference into a
global rule without evidence.

### B. Engineering / operational lesson

Look for non-obvious bugs/root causes, failed approaches, misleading green evidence,
environment/tool/provider quirks, recovery/fallback paths, race/concurrency issues,
CI/deployment/storage/runtime lessons, false-blocker risks, and steps that materially reduced
future work.

Prefer the mechanism over the literal symptom.

### C. Workflow / SOP improvement

Capture reusable sequences such as safer operation order, better debugging loops, handoff patterns,
verification strategies, or new acceptance workflows.

If reusable across tasks, prefer myk-skills over copied project-local prose.

### D. Decision / architecture rationale

Capture durable why when the conversation selected among alternatives and the choice will matter
again. Do not preserve every routine choice as an ADR.

### E. Project current truth

Identify facts future Agents need to act correctly: canonical path/owner/routing, experiment
contract, CI authority, runbook, source-of-truth location, or active project rule.

Write these back to the project, not only to learning memory.

### F. Research / evidence-handling lesson

Capture reusable methodology: evidence layers, contamination boundaries, fair-comparison rules,
protocol freezing, or what a result can/cannot prove.

Keep actual scientific results in their project/evidence owner.

### G. Communication / content / design preference

Capture explicit reusable owner judgment while preserving scope: tone, terminology, “sounds like
me”, information density, reader-first explanation, or design-reference interpretation.

Do not turn one surface-specific comment into a universal style law.

### H. Knowledge-system / Agent-routing lesson

Capture when future Agents struggled to find the right owner, or the real fix was routing rather
than more prose.

### I. Intentional non-learning

Explicitly classify notable things that should not become durable:

- transient PR/deployment/job status;
- temporary PID/container state;
- one-time provider outage;
- credentials/secrets;
- unverified speculation;
- pure emotional venting;
- already-owned facts that need no duplicate;
- incidental values unlikely to recur;
- stale implementation detail that belongs only in history.

A strong closeout proves what it refused to learn.

## Phase 2 — Coverage ledger: no silent loss

Create a compact coverage ledger for meaningful candidate units.

Each gets one primary disposition:
- ingest-new
- merge-existing
- project-writeback
- workflow-skill
- case
- decision
- fact-not-preference
- temporary-state
- superseded
- ambiguous-hold
- out-of-scope

Do not silently omit repeated owner corrections. Do not inflate counts by splitting every sentence.

If an unresolved ambiguous-hold affects a claimed broad lesson, do not claim full absorption.

## Phase 3 — Retrieve before creating

Before a new lesson/case/rule/Skill:

1. search existing .agents RAW/learned/project learning;
2. search the owning project's current docs/tests/SOPs;
3. search myk-skills for an existing workflow;
4. search relevant case/rule stores when they are real current owners;
5. inspect open PRs that may already change the same owner.

If the mechanism already exists, strengthen it, attach new evidence, and raise repeat/severity only
when justified. Do not create a synonym.

## Phase 4 — Route to the correct owner

Direct owner feedback:
Use .agents learning schemas. Preserve exact human wording as RAW when wording matters. Derived
interpretation stays outside RAW.

Engineering case:
If one incident deserves deep archival and record-case is the current owner for that environment,
delegate the single-case deep archive there. conversation-closeout remains the conversation-wide
orchestrator.

Shared workflow:
If the conversation created/refined a reusable workflow, update/create a Skill in myk-skills.
Use skill-creator when substantial Skill design/evaluation is required.

Rule-corpus cleanup:
Use rules-distill when existing rules need keep/consolidate/deprecate/move decisions.

Agent knowledge topology:
Use agent-knowledge-garden when fresh Agents cannot find the owner, current/history routing is
confused, or account/project Agent docs have drifted.

Project behavior:
If future behavior should actually change, update the natural project owner: code, test, schema,
linter/audit, Agent instruction, SOP/runbook, decision owner, experiment authority, or
CI/deployment guard.

A central lesson without project writeback is incomplete when the project still behaves wrongly.

## Phase 5 — Learn mechanism, scope, severity

For each durable lesson, preserve scope, mechanism, evidence, anti-overgeneralization boundary,
and project writeback/guard when relevant.

Useful repeat states:
- observed — one supported occurrence
- repeated — multiple supported occurrences
- hard — repeated/explicit enough that a pre-owner-review guard is justified

Hard means “check this mechanism”, not “ban the literal token everywhere”.

## Phase 6 — Promote machine-checkable lessons

When recurrence is mechanically detectable, prefer a test, linter, schema, audit, CI/deployment
check, freshness guard, authority-drift check, or runtime preflight.

Do not encode subjective judgment as brittle string tests.

Useful escalation:
- first useful incident -> learn the mechanism
- repeated incident -> strengthen shared/project rule
- repeated machine-checkable incident -> add a guard

## Phase 7 — Preserve history honestly

Never rewrite old evidence so it looks like today's policy existed in the past.

Keep historical record, current truth, and learned interpretation separate.

## Phase 8 — Prove future usability

Writing knowledge is not enough.

For each new/materially strengthened high-value lesson, run the .agents Future-Task Retrieval Proof.

When the lesson should change first-attempt behavior and the originating conversation knows too
much, use the shared fresh-agent-acceptance Skill.

Do not use same-context self-review as independent evidence.

## Phase 9 — Validate and integrate writeback

For every repository changed:

1. resolve current integration SHA;
2. use a topic branch;
3. avoid colliding with another active writer;
4. run repository-local validation;
5. refresh base before merge;
6. require the repository's live required checks;
7. merge only exact-head accepted work;
8. read back resulting main when current authority changed.

Do not weaken CI/rulesets merely to merge learning work.

If provider/permission blocks a nonessential writeback, preserve the strongest verified state and
report it honestly.

## Phase 10 — Closeout receipt

Create/update the .agents closeout receipt when conversation-learning is in scope.

It should prove source window, coverage, RAW refs, learned/strengthened lessons, intentional
non-learning, project writeback/guards, future-task proof, and validation/merge state.

The receipt is proof, not a prose diary.

## What not to do

Do not:
- dump the transcript into “memory”;
- save secrets/auth material;
- treat every temporary fact as durable;
- duplicate project current truth in learning files;
- create a new rule when one already exists;
- turn one local preference into a global law;
- call Agent inference “owner feedback”;
- rewrite history to match current policy;
- erase useful failed paths when they are the lesson;
- create a case/ADR/Skill merely for symmetry;
- claim “remembered” when the destination was not actually written/validated;
- claim full closeout when a material reusable lesson is still blocked.

## Relationship to neighboring Skills

- record-case — deep archive of one selected case; not the whole-conversation orchestrator.
- rules-distill — consolidate an existing rule corpus.
- agent-knowledge-garden — repair Agent-facing knowledge topology/routing.
- skill-creator — design/evaluate a reusable Skill discovered during closeout.
- fresh-agent-acceptance — stronger proof that behavior survives loss of source context.
- verify — repository/artifact correctness evidence.

Delegate when needed; do not duplicate their mechanics here.

## Completion standard

A closeout is complete only when:

- meaningful reusable candidates were accounted for;
- strong direct owner feedback was preserved faithfully when appropriate;
- reusable mechanisms were merged into existing knowledge rather than duplicated;
- project current behavior was updated where needed;
- repeated machine-checkable failures gained a guard or an explicit reason why not;
- high-value lessons have future-task reachability proof;
- stronger fresh-Agent proof was used when context advantage was material;
- changed repositories were validated and merged when authorized/possible;
- blocked writebacks are stated literally;
- the owner receives a compact summary, not another giant retrospective.

## Final owner-facing report

Keep it short and natural in Chinese. Answer:

1. 总结了什么？
2. 记住了什么？
3. 有没有重复犯错？
4. 还有没有 blocker？

If useful, add one line naming changed repositories/Skills.

Do not make the owner read the receipt to know whether closeout succeeded.
