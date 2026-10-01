---
name: workflow-evolution
description: >-
  Evolve engineering workflows, CI/resource usage, Agent harnesses and host control planes.
  Use for workflow evolution, broad modernization, CI quota/cost reassessment, cross-project
  adoption, harness upgrades or host self-evolution. Refresh authority and changing assumptions,
  complete safe authorized repairs, and verify integration. Not for a narrow bug fix, single-PR
  status check, closeout-only request or fresh-window acceptance alone.
metadata:
  version: "2.1.0"
  category: workflow-evolution
  owner: mykcs
triggers:
  - workflow evolution
  - evolve workflow
  - development system review
  - harness upgrade
  - harness evolution
  - host self evolve
  - host-self-evolve
  - 主机自升级
  - 自我进化
  - 智能体框架升级
---

# Workflow Evolution

This is the single active evolution workflow for the user's engineering system. It absorbs the
former `harness-upgrade` and `host-self-evolve` workflow semantics while keeping their historical
evidence and still-useful host tools available as cold implementation/history material.

The workflow is intentionally **heavy in coverage, light in hot context**. Start from this router
and load only the mode-specific references needed for the run.

## Select the mode

- **Cross-repository propagation / governance migration / general review** → read
  [adoption-and-review.md](references/adoption-and-review.md).
- **Agent harness, skills, prompts, hooks, context/memory, orchestration, sandbox or verification**
  → also read [harness-evolution.md](references/harness-evolution.md).
- **Local Mac/host control planes, shell/runtime, ~/.agents, ~/.claude, ~/.codex, hooks, skills,
  local CI/recovery or host drift** → also read
  [host-local-evolution.md](references/host-local-evolution.md).
- **CI modernization, free-tier/quota pressure, runners, trigger waste or provider reassessment**
  → read [ci-modernization.md](references/ci-modernization.md).
- **Any run that can safely repair findings** → apply
  [safe-autonomy.md](references/safe-autonomy.md).
- **Replacement / upstream-tool / research choice** → read
  [research-and-reuse.md](references/research-and-reuse.md).

A general "run Workflow evolution" request means inspect all materially relevant modes, but still
use progressive disclosure rather than loading every archive and reference. Include a change-aware
CI/resource screen in a general run when the scoped targets have validation or deployment lanes;
CI_NONE can be an aligned result. A topical request stays topical.

## Default: safe autonomous repair

Invoking this workflow authorizes **safe, understood, reversible, in-scope engineering repairs**.
Do not stop at an audit or proposal when the change can be made safely with available authority.

Make the change, run the affected checks, fix failures caused by the change, refresh moving state,
and continue until acceptance. Do not repeatedly ask for approval for ordinary repository edits,
tests, reversible configuration/routing repairs, documentation ownership fixes, or PR/merge work
that is already inside the user's authorized workflow and protected by existing gates.

Stop only at a real boundary: destructive deletion without existing authorization, credentials or
secret handling that needs user input, spending, visibility/license change, production cutover,
irreversible external action, unresolved scientific identity/semantics, unresolved ownership, or
an active-writer conflict that cannot be integrated safely. A blocked action does not block
independent safe work.

Safety is a boundary, not a reason to be passive.

## Central authority, local adaptation

Read current `.agents` knowledge architecture and relevant shared standards first. **`.agents`
owns central normative semantics; this skill owns evolution execution.** Project repositories own
their local product/scientific facts, implementation, tests, runtime and live provider truth.

Prefer one writable owner per shared fact. Use thin consumers/adapters and project-appropriate
shapes. Do not force identical folders, providers, hooks or CI lanes merely for symmetry.

Preserve RAW wording, ADR rationale, cases and historical receipts. Evolve current rules and
enforcement without rewriting history to make today's policy look timeless.

## Start from current truth

Before writing:

1. refresh the current default branch, relevant live provider/runtime and central owner;
2. inspect open PRs/active writers touching the same surfaces;
3. reuse the existing registry, progress owner, caller graph and project routers;
4. distinguish shared semantics, local implementation, executable/live truth and evidence/history;
5. continue an existing valid rollout instead of opening a competing program.

Tool memory and prior conversation summaries are candidate context, not current authority.

## One execution loop

For each selected finding, resolve **owner → violated invariant or wasted work → smallest useful
repair → proof → integration/read-back**. Compare the existing design against the alternative;
record the expected user benefit and what evidence would disprove it before implementation.

Separate independent read-only discovery from writes; keep one writer per mutable workline and
serialize provider cutovers/publication. Refresh head/base and automatic release side effects before
remote writes. Existing specific approval remains valid; a new publication effect needs authority.
After a tool failure, follow the current `.agents` engineering-completion protocol and authorized
fallbacks. Continue independent work when one action is blocked; retain bounded scope and coverage.

## Close a central-to-consumer governance migration

For Agent routing, Wish/Dev lifecycle, CI ownership, knowledge architecture or another shared
semantic migration:

1. **Change the canonical owner first.**
2. **Audit consumers and registry coverage**, including likely governed repositories missing from
   the registry.
3. Classify real consumer drift, justified exceptions, active-writer blockers, provider failures
   and stale auditor/registry expectations before changing anything.
4. **Never contaminate a correct project with obsolete wording** just to satisfy an old marker.
5. Repair the owning semantic route: stale links, missing routers, misused lifecycle directories,
   registry blind spots, executable guards or audit logic.
6. **Keep hot routers small without deleting load-bearing discovery**; search tests/callers before
   removing startup-visible markers.
7. **Treat the auditor as part of the system.** Update its expectations when the architecture
   changes instead of freezing the previous design.
8. Respect every repository's exact-head/current-base merge gate and distinguish implementation
   failure from infrastructure/provider failure.
9. After integration, run a **latest-main re-audit**.

Completion means **zero unexplained findings**: each scoped target is verified aligned, a justified
exception, or an explicit blocker. A central rule plus one green pilot is not portfolio completion;
a green audit obtained by weakening checks is not completion either.

## General evolution review

Review both what should spread and what should disappear. Look for duplicated owners, stale
instructions, dead compatibility layers, repeated user effort, unnecessary approvals, obsolete
harness assumptions, weak machine guards, unsupported custom machinery and mature/native
capabilities that now cover the same responsibility.

Prioritize by owner effort saved, recurrence, risk, leverage and number of genuinely applicable
consumers. Compare **keep / adopt / adapt / build narrowly / simplify-retire / test first**.

Do not time-box a heavy evolution run to a conversational convenience threshold. The stopping rule
is acceptance or a real boundary, not elapsed time. At the same time, do not manufacture work:
a well-supported no-change result is valid.

For substantive harness/platform changes, the current research refresh in
[harness-evolution.md](references/harness-evolution.md) is mandatory. For ordinary known-safe
consumer repairs, do not turn research into ceremony.

## Verification

Match verification to the changed layer:

- static/config/ownership and reference checks;
- executable unit/integration/CLI tests;
- current provider/ruleset/exact-head evidence;
- environment fingerprint when runtime drift matters;
- independent/pass-2 review for consequential changes;
- fresh-Agent acceptance when source-conversation context advantage is part of the risk.

Classify failures as implementation/regression, policy/ownership drift, infrastructure/environment,
or insufficient evidence. An unavailable/skipped hosted check never becomes PASS.
When a test fails, first establish the invariant it measures. Shared-runner startup/wall time is
not a probe's execution budget: use deterministic contract checks plus real bounded integration
checks where appropriate. Preserve negative controls; neither blindly retry nor weaken a gate to
obtain green evidence.

For a portfolio run, re-read latest integrated state after merges. Do not report "all complete"
from pre-merge snapshots.

## Neighboring workflows

- `harness-audit` remains a read-only deterministic scorecard; it does not own evolution.
- `agent-knowledge-garden` specializes in knowledge-topology discovery/routing and may supply
  findings to this workflow.
- `skill-creator` owns authoring mechanics and controlled skill-development evaluations.
- `verify` / `verifier-pass2` own focused verification evidence.
- `conversation-closeout` owns conversation-wide learning capture.
- `fresh-agent-acceptance` owns conversation-isolated behavioral transfer tests.

The former active skills `harness-upgrade` and `host-self-evolve` were absorbed into this
workflow on 2026-10-01. Their old SKILL documents are historical evidence, not competing current
instructions.

## Finish with the actual outcome

Give a compact outcome: scope/owner; **KEEP / CHANGE / RETIRE / TEST FIRST** decisions that matter;
actual verification and integrated state; remaining **BLOCKERS** and the smallest next action.
Omit empty categories and explain approval effects in plain language. Distinguish reviewed,
proposed, piloted, adopted and integrated states. Link existing owners instead of creating another
permanent ledger for a one-off run.
