---
name: fresh-agent-acceptance
description: >-
  Black-box acceptance for completed work when the originating conversation may have a context
  advantage. Use whenever the user says they fixed/built/changed something but is not sure it is
  really solved for a fresh Agent, wants a short prompt to copy into brand-new windows, wants a
  no-context/hidden test, or explicitly does not want the tested Agent told what changed. Infer the
  real success behavior from the current conversation, verify the target is in the state intended
  for testing, freeze a hidden rubric, generate a normal-looking non-leading task, and later grade
  all returned fresh-window results against that original rubric.
when_to_use: >-
  Trigger for phrases such as “新开窗口测一下”, “看看新 Agent 会不会自然做对”, “给我一个 prompt
  拿去几个新窗口”, “无上下文/黑盒/隐蔽验收”, “不要告诉它我们改了什么”, “我不确定是不是真的
  修好了”, or equivalent intent after completing code, docs, configuration, workflow, research,
  product, infrastructure, or Agent-facing work.
metadata:
  version: "1.1.0"
  category: agent-evaluation
  owner: mykcs
---

# Fresh Agent Acceptance

Use a fresh Agent to test whether completed work **really survives loss of the source conversation**.

The problem is epistemic: the originating window helped create/fix the thing, so it already knows
what changed, where to look, what the intended answer is, and which awkward details to ignore.
That context advantage can make a weak implementation look finished.

The real question is:

> **Can a fresh Agent handle a normal downstream task correctly without being told what we changed?**

This is a shared reusable workflow. Project/local truth still belongs to the project, artifact,
runtime, product, or live provider being tested. The `.agents` learning system may reference this
Skill when a conversation closeout needs stronger behavioral evidence.

This workflow can test code, docs, configuration, websites, CI/deployment, research procedures,
recovery flows, artifact placement, or Agent-facing behavior. Do not force every case into
“routing/authority” language.

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

### 1. Infer and freeze the real success behavior

From the current conversation, privately identify:

- what was just changed/fixed/built;
- what a future Agent would need to accomplish for us to say it really works;
- what this originating window knows that a fresh Agent would not;
- critical invariants, acceptable variation, hard fails, forbidden side effects, and useful evidence.

Test the downstream behavior, not a sentence the fresh Agent should recite.

### 2. Check the thing being tested

Inspect the strongest current evidence for the completed work:

- the actual artifact/code/docs/config;
- the normal user or Agent path;
- relevant runtime/live state;
- executable tests/guards when they exist.

If you find an obvious unfinished defect and the current task authorizes repairing it, repair and
validate it before designing the black-box trial.

If repair is outside current authority, report that boundary instead of designing a test around a
known-broken state.

Do not assume this means “audit Agent entrypoints”. Check whatever surfaces actually determine the
behavior the user just changed.

### 3. Choose the acceptance level

- **Level 0 — reachability:** ordinary future-task retrieval proof only.
- **Level 1 — blind single:** one genuinely fresh context.
- **Level 2 — blind replicated:** same frozen prompt in two or three independent fresh contexts.

Prefer Level 2 for important, ambiguous, shared, or expensive-to-get-wrong changes.

### 4. Freeze the tested world

Record only the state that can materially change the correct answer, for example:

- repository/ref/SHA;
- deployed artifact/version;
- dataset/config revision;
- ruleset/provider/runtime identity when relevant.

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

Classify the primary failure as:

- **TARGET_DEFECT** — the completed thing is actually incomplete or wrong;
- **DISCOVERY** — it works, but a fresh Agent/user cannot naturally find or use it;
- **INTERPRETATION** — the right surface is found but remains ambiguous;
- **GUARD** — a machine-checkable regression can recur without protection;
- **PROMPT_DESIGN** — the black-box task itself leaked, was artificial, or had unrelated ambiguity;
- **ACCESS_ENVIRONMENT** — the fresh context lacked required capability/current evidence.

Fix the real target for the first four classes.

Rewrite the test only for **PROMPT_DESIGN**.

After any material repair, start a new trial set. Do not recycle old PASS/FAIL as proof of the new
system.

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

## Relation to neighboring skills

These workflows are complementary, not aliases:

- **`skill-creator`** owns creating/improving a Skill and controlled with-skill vs baseline/old-skill
  evaluation. Use `fresh-agent-acceptance` only when the later question is whether a completed
  Skill/system survives loss of the originating conversation in normal use.
- **`verify`** owns build/test/security/adversarial implementation evidence. It may be part of
  Phase A's target check, but a same-context verifier is not a substitute for a fresh-window
  black-box trial.
- **`healer-cannot-self-heal`** owns session/sub-problem triage when the current conversation is
  itself drifting or untrustworthy. It diagnoses the session; it does not certify a completed
  repair. After a repair, this Skill can test downstream behavior in fresh contexts.
- **`harness-upgrade`** owns research, design, implementation, and the normal verification
  portfolio for harness changes. Add this Skill when source-conversation context advantage itself
  is part of the acceptance risk.
- **`website-improve`** owns website-specific Planner → Executor → Verifier delivery. Use this
  Skill only for the separate question of fresh-context behavioral transfer.

Do not merge these workflows merely because they all use words such as “independent”, “fresh”, or
“verification”. Their tested object and evidence model are different.

## Relation to other workflows

- `verify` checks whether an artifact/build/test is correct.
- `fresh-agent-acceptance` checks whether the completed result still works when the source
  conversation disappears.
- `.agents` Future-Task Retrieval Proof checks whether learned guidance is reachable; it may use
  this Skill when behavioral evidence is valuable.
- Historical BaseModel cold-read/HPL machinery is evidence only; do not revive it as a second owner.

## Natural trigger

A user should not need to remember the implementation details. For example:

> 这个东西我刚做完，但这个窗口知道太多背景。帮我做一次 fresh-Agent 黑盒验收，给我一个
> 不泄露考点的短 Prompt，我会发给几个新窗口；结果回来后按你现在先定好的标准一起判断。

Infer the rest from the current conversation rather than asking the user to restate what changed.
