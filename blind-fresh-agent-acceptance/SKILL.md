---
name: blind-fresh-agent-acceptance
description: >-
  Design and evaluate a context-isolated behavioral black-box test for a completed
  Agent-facing change. Use whenever the user asks whether a fix/rule/router/skill
  really makes a brand-new Agent naturally do the right thing, asks for a prompt
  to paste into a fresh/no-context window, wants a hidden/blind acceptance test,
  wants the same prompt tried in several independent Agent windows, or says not
  to reveal what was changed or what is being tested.
when_to_use: >-
  Trigger for fresh-Agent acceptance, no-context validation, hidden behavioral
  tests, black-box Agent evals, “给我一段复制到新窗口的 prompt”, “不要告诉新窗口我们改了什么”,
  and post-change tests of repository routing, authority, fallback, storage,
  runtime, CI/provider, or other first-attempt Agent behavior. Do not use this
  merely for ordinary code review or unit testing when no fresh-Agent behavior
  is being tested.
metadata:
  version: "1.0.0"
  category: agent-evaluation
  owner: mykcs
---

# Blind Fresh-Agent Acceptance

Turn a completed Agent-facing change into a realistic **behavioral black-box test**.

The goal is not to make a fresh Agent recite the new rule. The goal is to see whether
it naturally behaves correctly on an ordinary adjacent task **without being told what
changed**.

## Canonical contract

Read the current canonical SOP from `mykcs/.agents/main` before designing a trial:

`docs/learning/BLIND_FRESH_AGENT_ACCEPTANCE.md`

The `.agents` contract owns PASS/FAIL semantics, proof levels, receipt fields, and
learning-system boundaries. This Skill owns only the **execution workflow**.

If that canonical path is not yet present on current `.agents/main`, do not treat an
open PR copy as account-wide authority. A staged SOP/Skill rollout may continue, but
report that the shared protocol is not yet landed.

## Acceptance chain

```text
rule/change exists
  -> a fresh Agent can discover the real owner through normal routing
  -> a fresh Agent naturally applies the behavior in a realistic task
```

## Workflow

### 1. Freeze the hidden hypothesis first

Before writing the test prompt, privately record:

- critical invariants;
- acceptable alternatives;
- hard-fail behavior;
- evidence classes that count;
- forbidden side effects;
- what would make the trial inconclusive.

Do not expose this rubric to the tested Agent.

### 2. Audit the real entry path before testing

Inspect the surfaces a fresh Agent should encounter naturally:

- project/root Agent instructions;
- current topic router or handoff;
- executable owner/config/test when relevant;
- live provider/ruleset/runtime state when the answer depends on it.

If a real routing or authority gap exists, repair it first with the normal project
workflow and validation. Do not make the prompt more leading to compensate for a
broken discovery path.

### 3. Design a realistic adjacent task

The prompt should look like normal work, not an exam.

Useful task shapes:

- inspect one old artifact and plan one new successor output;
- compare one historical path with one current runtime path;
- diagnose a small provider/CI state and state the next safe action;
- locate one current asset and one implementation detail;
- prepare a tiny read-only preflight.

Do not tell the tested Agent:

- what changed;
- what rule is being tested;
- which file was just edited;
- the expected answer;
- the hidden rubric;
- to “verify our fix”.

Let it decide what to inspect.

### 4. Use a contrastive witness for boundary rules

If the lesson is a boundary rather than a simple replacement, put **both sides** into
the same realistic task.

Examples:

- a historical value where the old spelling remains correct + a new value that must
  use today’s canonical rule;
- a container-internal path where `/root` is legitimate + a host-side path where it is not;
- an old provider receipt that remains historically true + a live merge-authority value
  that must come from current state.

This distinguishes real transfer from blanket keyword substitution.

### 5. Bound side effects

Default to read-only or simulated work:

- do not run the model;
- do not allocate GPU;
- do not mutate production/provider state;
- do not create the proposed output.

A blind test grants no extra authority.

### 6. Freeze the trial packet and tested world

Record:

- exact prompt text;
- prompt SHA-256 when tooling is available;
- target repository/ref;
- other current-owner/live identities that can materially change the answer;
- hidden rubric.

For replicated trials, use the **same prompt and same relevant authority surface**.
If `main`, a parent policy, or live merge authority changes materially between trials,
start a new trial set instead of mixing results.

### 7. Return two physically separate sections

Always produce:

## COPY TO FRESH AGENT

Only the realistic task and compact return contract.

Fields should expose task semantics, not the hidden lesson, for example:

```text
sample=
historical_value=
planned_new_value=
runtime_source=
runtime_destination=
required_gate=
evidence_basis=
```

## KEEP HIDDEN — EVALUATOR RUBRIC

Include:

- tested behavior;
- critical invariants;
- acceptable variation;
- hard-fail conditions;
- forbidden side effects;
- evidence expectations;
- PASS / FAIL / INCONCLUSIVE / LEAKED rules;
- frozen refs/state.

Tell the user to copy **only** the first section.

### 8. Use genuinely fresh contexts

Preferred route:

1. source window creates the packet;
2. user manually copies only the blind prompt;
3. a new ChatGPT/Codex/Claude/Kimi context performs the task;
4. user pastes the unedited result back;
5. source/evaluator window scores it against the frozen rubric.

A same-context subagent is not fresh evidence when it can inherit source conversation,
scratch state, or hidden rubric.

For repository front-door, cross-tool, authority, or expensive repeated-failure
changes, prefer **2–3 independent fresh contexts**.

### 9. Grade semantics, not strings

Different Agents may choose different samples, files, or evidence paths and still PASS.

Strong replicated evidence is:

> different valid evidence paths converge on the same invariant-level behavior.

Use the canonical verdicts:

- `PASS` — all critical invariants hold;
- `FAIL` — a critical invariant is violated;
- `INCONCLUSIVE` — required evidence is unavailable and the Agent does not guess;
- `LEAKED` — the prompt materially revealed the answer/tested rule.

Never cherry-pick only the passing Agent.

### 10. Repair the system, not the score

If a trial fails, classify it as:

- routing failure;
- owner-text/relationship failure;
- executable guard failure;
- prompt-design failure;
- capability/access failure.

If a real project gap is found, repair the real owner/route/guard and start a **new
trial set**. Do not edit the rubric after seeing the answer and do not add search
keywords merely to force retrieval.

## Output contract

When creating a blind fresh-Agent test, return:

1. **Audit result** — what was checked/fixed before testing.
2. **COPY TO FRESH AGENT** — the only text to paste elsewhere.
3. **KEEP HIDDEN — EVALUATOR RUBRIC** — frozen scoring criteria.
4. **Trial metadata** — target refs/state and prompt hash when available.

When trial outputs come back, keep the original rubric and report:

```text
TRIAL 1: PASS|FAIL|INCONCLUSIVE|LEAKED
TRIAL 2: ...
TRIAL 3: ...
SET VERDICT: ...
DISAGREEMENT: ...
REAL SYSTEM GAP FOUND: yes|no
NEXT ACTION: ...
```

## Anti-patterns

Do not:

- turn the prompt into a quiz about the rule;
- name the exact current file merely to force retrieval;
- copy the owner correction into the prompt;
- use irrelevant keywords to trigger retrieval;
- run destructive/GPU/production actions for realism;
- change the prompt between replicas and call them one set;
- mix trials from materially different `main`/ruleset states;
- score literal wording instead of semantic boundaries;
- call a same-context self-review independent;
- re-create the retired BaseModel HPL / Gold Pair / Preference Brief control plane.

## Related skills

- `agent-knowledge-garden` repairs Agent-facing knowledge architecture.
- `verify` owns ordinary build/test/security/review evidence.
- This Skill is for the narrower question: **does fresh-Agent behavior transfer without
  prompt leakage?**
