---
name: fresh-agent-acceptance
description: >-
  Design and evaluate context-isolated behavioral acceptance tests for completed Agent-facing
  changes. Use whenever the user asks whether a fresh/new Agent would naturally do the right
  thing, wants a prompt to copy into brand-new windows, asks for a no-context/hidden/blind test,
  or wants to prove that AGENTS/docs/SOP/routing/authority changes actually changed first-attempt
  behavior without telling the tested Agent what changed. The workflow audits and repairs real
  entrypoints first, freezes a hidden rubric and authority snapshot, emits a realistic non-leading
  prompt for manual copy, and later grades every returned trial without changing the rubric.
when_to_use: >-
  Trigger for phrases such as “新开一个窗口测试”, “看看新 Agent 会不会自然做对”, “给我一个 prompt
  拿去不同窗口”, “无上下文验收”, “隐蔽验收”, “不要告诉它我们想测什么”, “blind/fresh-agent
  acceptance”, or equivalent intent after a workflow/rule/router has been completed.
metadata:
  version: "1.0.0"
  category: agent-evaluation
  owner: mykcs
---

# Fresh Agent Acceptance

Prove **behavioral transfer**, not merely that a rule exists.

The canonical acceptance semantics live in:

`mykcs/.agents/docs/learning/BLIND_FRESH_AGENT_ACCEPTANCE.md`

This skill is the thin execution surface. It must not become a second writable policy.

## What this workflow is really testing

The user normally wants to know:

> If the original conversation disappeared, would an ordinary fresh Agent encounter a realistic
> adjacent task and naturally make the right decisions from the current system?

That is stronger than:

- “can it find the Markdown?”;
- “can it repeat the new rule when asked about the rule?”;
- “does a reviewer think the docs look correct?”.

The evidence ladder is:

```text
rule exists
  -> current routing can expose it
  -> a fresh Agent naturally applies it
  -> independent fresh contexts converge on the same invariant
```

## Fresh means conversation-isolated, not bootstrap-free

A valid trial excludes the **source conversation and its hidden reasoning**.

Do **not** strip normal account/project bootstrap, repository `AGENTS.md`, current docs, connected
tools, or live provider access merely to make the Agent “more blank”. Those are part of the real
system being tested.

A same-context subagent is not strong fresh-Agent evidence when it can inherit the source
conversation, scratch state, or hidden rubric.

Preferred route:

1. this originating window prepares the packet;
2. the owner copies only the test prompt into a brand-new top-level window/tool;
3. that Agent works normally from current project/account capabilities;
4. the owner copies the returned result back here;
5. this window evaluates it against the already-frozen rubric.

## Phase A — Originating window prepares the test

### 1. Define the target behavior privately

Before writing the test prompt, identify:

- **behavior under test** — what should the next Agent do differently?
- **critical invariants** — what must be true for PASS?
- **acceptable variation** — what examples/evidence paths may differ?
- **hard fails** — what behavior proves the change did not transfer?
- **forbidden side effects** — what the trial must not mutate or consume?
- **evidence classes** — which current/live sources could support the answer?

Test behavior, not wording. A rule can be quoted correctly while the task is still handled wrong.

### 2. Audit the real entry path before testing

A black-box trial is useful only after the implementation is actually in place.

Inspect, as relevant:

- shared/account Agent routing;
- target repository root Agent entrypoint;
- current topic router/current authority;
- executable config/tests/guards;
- live provider/ruleset/runtime state;
- overlapping PRs or stale branches.

If a real routing/current-authority gap is found, fix and validate that gap **before** generating
the blind prompt when the task authority permits it.

Do not turn a known broken entrypoint into a test and then call the predictable failure “evidence”.

### 3. Choose the acceptance level

- **Level 0 — reachability:** ordinary future-task retrieval proof only.
- **Level 1 — blind single:** one genuinely fresh context.
- **Level 2 — blind replicated:** same frozen prompt in two or three independent fresh contexts.

Prefer Level 2 for repository front doors, shared cross-tool behavior, authority boundaries,
fallback/recovery behavior, or repeated expensive mistakes.

### 4. Freeze the tested world

Record the minimum state that can change the correct answer:

- target repository/ref/SHA;
- parent/shared authority SHA when relevant;
- live ruleset/provider/runtime identity when relevant.

For replicated trials, every trial belongs to the same set only while these answer-changing
authorities remain materially unchanged.

If the world changes, do not average old and new outputs together. Start a new trial set or
explicitly classify the comparison as non-replicated evidence.

This is the behavioral equivalent of exact-head testing.

### 5. Design an ordinary task, not an exam question

The test prompt should look like a small task the user might genuinely request.

Good patterns:

- inspect one old artifact and plan one new artifact;
- inspect one runtime mount and propose one new output;
- diagnose a small failure and decide whether another authorized route exists;
- inspect a tiny PR and report its actual merge requirement;
- compare one historical record with one current/live state.

Bad patterns:

- “What is our new rule?”;
- “Did yesterday’s fix work?”;
- “Read AGENTS.md and tell me the canonical path”;
- “Test whether Cloudflare/Mac/storage rule X is correct”.

The task should **need** the target behavior without naming it.

### 6. Use a contrastive witness when the behavior is a boundary

If the lesson says “X is correct here but wrong there”, include both sides naturally.

Examples:

- a historical record where the old path must remain unchanged **plus** a new output that must
  use the current path;
- a container-internal path where `/root` is legitimate **plus** a host-side destination where it
  is not;
- an old provider receipt that remains true **plus** a live merge-authority question;
- a preferred route failure **plus** another already-authorized fallback opportunity.

This catches mechanical keyword replacement and proves the Agent understands the boundary.

Do not add fake traps that no normal task would contain.

### 7. Prevent answer leakage

The fresh prompt should not name:

- the rule being tested;
- the file just edited;
- the implementation PR;
- the expected answer;
- the lesson ID;
- the hidden rubric;
- “exam”, “blind acceptance”, “did you learn”, or equivalent meta language.

It may name the real repository/product when a normal task would.

Leave source discovery to the fresh Agent unless a normal user task genuinely supplies a source.

### 8. Bound side effects

Default to read-only or simulated acceptance.

Useful wording:

- “不要真的创建，只告诉我会放哪里”;
- “不要运行模型/使用 GPU”;
- “只读检查当前状态”;
- “不要修改 provider/ruleset”.

A behavioral test grants no extra mutation authority.

### 9. Ask for compact task-shaped outputs

Return fields should reveal behavior without asking the Agent to explain the hidden lesson.

Example:

```text
sample=
historical_value=
planned_new_value=
runtime_source=
runtime_destination=
required_gate=
evidence_basis=
```

Different valid evidence paths are acceptable.

### 10. Freeze prompt and rubric before trials

Before the owner copies anything:

- freeze the exact prompt text;
- freeze the hidden invariant-level rubric;
- record the world snapshot;
- compute a prompt SHA-256 when a hashing tool is readily available.

Do not change the rubric after seeing an answer.

A materially changed prompt starts a new trial set.

## Required output from Phase A

Return exactly two clearly separated sections.

### COPY ONLY — FRESH AGENT PROMPT

This section must stand alone. It is the only section the owner copies into fresh windows.

It contains:

- realistic task;
- read-only/safety boundary when needed;
- compact return fields.

It does **not** contain the rubric or test rationale.

### KEEP HERE — HIDDEN RUBRIC

Record:

- packet/trial-set identity;
- tested behavior;
- frozen world snapshot;
- critical invariants;
- acceptable alternatives;
- hard-fail conditions;
- forbidden side effects;
- expected evidence classes;
- PASS / FAIL / INCONCLUSIVE / LEAKED rules;
- recommended trial count.

Do not instruct the owner to paste this section into the fresh context.

## Phase B — Evaluate returned fresh-Agent outputs

When the owner pastes one or more fresh-window results back:

### 1. Do not redesign the test after seeing results

Use the frozen rubric from Phase A.

If the exact rubric is unavailable, say the evaluation cannot be a valid pre-registered blind
verdict. Do not reconstruct a friendlier rubric from the outputs.

### 2. Recheck the tested world

If relevant repository/provider authority changed materially during the trial set, classify the
affected comparison as **INCONCLUSIVE** or start a new trial set.

Do not combine answers produced against different authorities as if they were replications.

### 3. Score semantics, not literal strings

For each trial, record every critical invariant:

```text
invariant=<name>  result=PASS|FAIL|UNKNOWN  evidence=<short reason>
```

Allow different:

- historical examples;
- files;
- launchers;
- evidence paths;
- wording.

What matters is the behavioral boundary.

### 4. Use four verdicts

- **PASS** — all critical invariants hold; evidence is sufficient; no forbidden behavior.
- **FAIL** — at least one critical invariant is violated.
- **INCONCLUSIVE** — required evidence was unavailable and the Agent honestly refused to guess,
  or the tested world changed materially.
- **LEAKED** — the prompt itself materially exposed the target answer/rule.

A LEAKED answer can be factually correct but cannot prove behavioral transfer.

### 5. Never cherry-pick replicated trials

Preserve every returned trial.

Strong replicated evidence is:

> different Agents choose different examples/evidence paths but converge on the same invariants.

One passing Agent does not erase another valid failure.

### 6. Diagnose failure before changing the prompt

Classify a failure as:

- **ROUTING** — Agent never reached the real current owner;
- **OWNER_TEXT** — reached it but the authority is ambiguous/misleading;
- **GUARD** — machine-checkable regression is not protected;
- **PROMPT_DESIGN** — task leaked, was artificial, or had unrelated ambiguity;
- **ACCESS** — fresh context could not access required current/private/live evidence.

Repair the real owner when the failure is ROUTING / OWNER_TEXT / GUARD.

Only rewrite the test when the problem is PROMPT_DESIGN.

After any material repair, start a new trial set. Do not recycle the old PASS/FAIL as proof of the
new system.

## First-principles anti-gaming rules

Never:

- paste the owner’s correction into the fresh prompt;
- name the exact changed file merely to force retrieval;
- add search keywords only so the right document appears;
- use the same conversation/subagent and call it independent;
- score only the best output;
- move the rubric after seeing results;
- require exact expected strings when multiple evidence paths are valid;
- run GPU/destructive/production actions merely to make the test realistic;
- strip normal project/global bootstrap that the real future Agent would have.

## Relation to other workflows

- `.agents FUTURE_TASK_RETRIEVAL_PROOF` asks whether the lesson is reachable.
- This skill asks whether the lesson **changes behavior without prompting the answer**.
- `verify` validates code/artifact correctness; it does not replace a fresh-context behavioral trial.
- Historical BaseModel cold-read/HPL machinery is evidence only; do not revive it as a second owner.
- `agent-knowledge-garden` may repair Agent-facing routing discovered by a failed trial.

## Short user-facing trigger

A user should not need to remember the SOP path. Natural language is enough, for example:

> 这件事做完了。帮我做一次 fresh-Agent 验收：先把该修的入口修好，然后给我一段不泄露
> 考点的真实任务 Prompt，我会复制到几个全新窗口；等我把结果贴回来后，你按事先冻结的
> 标准判定它到底有没有真的学会。

The skill should execute the workflow directly rather than asking the user to restate the protocol.
