---
name: workflow-evolution
description: >-
  Heavy on-demand evolution of the user's engineering system across repositories, Agent harnesses,
  and local host/control planes. Use for workflow evolution, cross-project standard adoption,
  harness upgrades, host self-evolution, or broad modernization/reassessment. Refresh current
  authority, research changing platform assumptions when relevant, directly complete safe
  authorized reversible improvements, and verify the integrated result. Not for a routine narrow
  bug fix, status check, closeout-only request, or fresh-window acceptance alone.
metadata:
  version: "2.0.0"
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
- **Any run that can safely repair findings** → apply
  [safe-autonomy.md](references/safe-autonomy.md).
- **Replacement / upstream-tool / research choice** → read
  [research-and-reuse.md](references/research-and-reuse.md).

A general "run Workflow evolution" request means inspect all materially relevant modes, but still
use progressive disclosure rather than loading every archive and reference.

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

Report:

- **KEEP** — current choices that still win;
- **CHANGE** — integrated improvements and their owners;
- **RETIRE** — superseded skills/rules/tools/worklines;
- **TEST FIRST** — uncertainties that still need discriminating evidence;
- **VERIFICATION** — what actually passed and on which current state;
- **BLOCKERS** — only real remaining boundaries.

Distinguish reviewed, proposed, piloted, adopted and integrated states. Link existing owners instead
of creating another permanent ledger for a one-off run.
