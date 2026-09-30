---
name: workflow-evolution
description: >-
  Evolve the user's engineering system across repositories and workflows: spread proven useful
  improvements such as Wish, CI and shared rules to applicable consumers, and on demand
  reassess whether current development practices remain modern, elegant, simple and
  suited to actual use. Resolve canonical owners, adoption gaps, stale/conflicting rules, mature
  upstream alternatives, justified exceptions and staged verification. Use for cross-project
  adoption or general workflow reassessment, applying live central .agents guidance to local
  reality and completing authorized safe repairs. Not a routine bug fix, status check,
  closeout-only request or fresh-window acceptance alone.
metadata:
  version: "1.1.0"
  category: workflow-evolution
  owner: mykcs
---

# Workflow Evolution

Help useful improvements compound across the user's work, then revisit the system as needs and
technology change. A solution fixed in one place should benefit other places where it genuinely
applies, without multiplying conflicting rules or forcing every project into the same shape.

Optimize for **modern, elegant, simple, and suited to actual use**:
- Modern: use current, supported capabilities when they improve the real job.
- Elegant: give each responsibility one clear owner and make the parts work coherently together.
- Simple: reduce owner effort, duplicate machinery and maintenance without losing needed behavior.
- User-fit: serve the original Wish and observed working needs, not fashion or an imagined user.

Use two entry modes: **topical propagation** of an improvement/principle, or **general review** of
the development system. Both run on demand from a short invocation. Repeating the invocation
later is supported; it does not create a schedule. Finding nothing worth changing is valid.

## Central authority, local adaptation

Read the current .agents knowledge architecture and relevant shared standards first. **.agents is
the single central normative authority**; this skill is its execution workflow, not a parallel
standard. Each repository selects the best local implementation from central guidance and its own
requirements. Link live owners instead of copying editable policy into every repository or skill.

Use first principles to question the current method when evidence supports a better one. Existing
folder shapes, rules and engineering habits are not goals in themselves. Central principles may
evolve through their real owner; factual/scientific truth and safety boundaries remain protected.

## Resolve the run's scope

Recover the current user goal, affected standard/workflow, intended consumers and action authority.
Use the existing repository registry, caller graph and current project routers rather than invent
a second account inventory. Explicitly scoped repositories count even if absent from a registry.

Resolve common semantics versus local implementation from current central standards; do not ask
the user to redesign that established relationship. Check only genuinely unresolved consequential
choices or boundaries. The current CI standard already permits workload-specific providers; the
Wish standard already permits a suitable local shape.

For an invocation authorizing safe repairs, carry out high-confidence reversible improvements in
scope rather than stop at an audit. Respect actual access, required confirmations and active writers.
If a particular action needs a decision, continue independent discovery and other authorized fixes.
A skill file is not itself permission to expand scope or cross security/production boundaries.

## Find actual owners and current baseline

Read current shared standards and relevant local Wish/Dev, executable configuration, tests and
live owners. Refresh active branches/PRs before writing. Existing pilots or ongoing rollout work
may already solve part of the problem; coordinate with their owner rather than start a duplicate.

Separate these layers:
- **Shared semantics:** one canonical standard or reusable skill
- **Consumers:** thin references, generated projections, adapters or configuration as needed
- **Local truth:** project decisions, science/product invariants, code, runtime and live provider
- **Evidence/history:** why a rule was adopted and what happened, not a competing policy

Identify stale, conflicting or duplicated rules by comparing scope and authority with actual
behavior. Repair the owner or routing when authorized; adding another reminder is not a repair.
Preserve RAW wording, historical ADR rationale and case evidence. Reconcile current interpretations
and rules rather than rewriting history. Treat tool memory as candidate context, not policy.

Trace evidence to a useful central principle, then test its local implications. Prefer one bounded
principle covering a family of confident cases over endlessly appending incident-specific rules.
Use deterministic audits for mechanical drift and capable model judgment for semantic fit; neither
file-presence checks nor arbitrary scores establish that a repository adopted the principle well.

For Wish and CI changes, start from the existing owners linked in
[adoption-and-review.md](references/adoption-and-review.md). Do not create another Wish lifecycle,
CI acceptance contract, portfolio progress record or ruleset authority inside this skill.

## Close a central-to-consumer governance migration

When a run changes shared semantics such as Agent routing, Wish/Dev lifecycle, CI ownership,
knowledge architecture, or another account-level convention, treat the work as a **closed
migration loop**, not a central-doc edit.

1. **Change the canonical owner first.** Put the new shared semantic rule in its existing central
   owner before teaching consumers. Preserve historical rationale through superseding ADRs or
   history; do not rewrite old evidence as if the earlier rule never existed.
2. **Audit consumers and registry coverage.** Check current default branches for registered
   long-lived consumers, then detect likely governed repositories that the registry itself missed.
   Absence from the registry is a possible registry defect, not proof that the repository is out
   of scope. Classify applicability before creating folders or machinery.
3. **Classify every finding before repairing it.** Separate real consumer drift from stale
   auditor/registry expectations, justified local exceptions, active-writer conflicts, and
   provider/infrastructure failures. Never contaminate a correct project with obsolete wording
   merely to make an old audit marker green.
4. **Repair the semantic route, not only the symptom.** Fix stale owner links, missing routers,
   misused lifecycle directories, registry blind spots and machine guards at the layer that owns
   them. Preserve valid local shapes; a shared lifecycle does not imply mandatory symmetry.
5. **Keep hot routers small without deleting load-bearing discovery.** Before slimming a root
   Agent/bootstrap file, search tests, callers and machine invariants for startup-visible markers.
   Move detail to scoped owners, but retain compact pointers or exact contract phrases that
   downstream behavior genuinely depends on.
6. **Treat the auditor as part of the system.** A mechanical audit can be stale too. After the
   shared semantic rule changes, update its required paths, references, discovery logic and
   expected markers so it detects current drift instead of preserving the previous architecture.
7. **Respect each repository's real merge gate.** Distinguish application/test failure from
   provider outage, billing/quota, stale-head evidence or missing status propagation. Do not weaken
   rules to get green; use the repository's qualified fallback or required exact-head path.
8. **Re-run from latest integrated state.** After consumer and audit fixes merge, refresh central
   `main` and perform the portfolio audit again. Completion means **zero unexplained findings**:
   every scoped target is verified aligned, a justified exception, or an explicit blocker. When
   the audit is designed as exhaustive for that portfolio, zero errors and zero warnings is the
   strongest clean closeout; do not hide residual warnings simply to report success.

Useful rollout order:

```text
central semantic owner
-> consumer applicability + registry discovery
-> consumer repairs
-> auditor / machine-guard repair
-> exact-head merges
-> latest-main portfolio re-audit
```

A central rule plus a green pilot is not portfolio completion. A green portfolio audit that was
made green by weakening checks or copying obsolete text is also not completion.

## Propagate a proven improvement

1. **Extract the reusable part.** State the problem solved, invariant/contract improved, evidence
   that it works and conditions where it applies. Separate common behavior from incidental folder
   layout, provider, language or scientific assumptions in the source project.
2. **Audit applicability.** Classify relevant consumers as already aligned, adoption candidate,
   adapter needed, justified exception, out of scope or evidence missing. Missing evidence is not
   an exception. Do not assume all repositories need the same machinery.
3. **Choose the shared boundary.** Prefer the existing central owner plus thin consumers and local
   adapters. Apply the principle, not a source project's incidental shape. Do not turn shared CI
   guidance into one-provider migration or Wish guidance into mandatory empty folders.
4. **Qualify a small adoption.** For consequential changes, use a representative pilot and prove
   the shared contract, local invariants, negative cases and rollback before expanding. Small safe
   pointer fixes need no elaborate program. Cover materially different consumer classes before
   claiming a pilot generalizes to them.
5. **Roll out within authority.** Reuse active worklines, refresh target state and make the smallest
   coherent consumer changes. Keep the old route recoverable until the new one qualifies. Stop
   expansion on unexplained regressions or violated invariants; diagnose rather than waive them.
6. **Verify adoption.** Test the actual consumer entry path and behavior, not just file presence.
   Follow each repository's exact-head/current-base acceptance and live migration rules. Report
   per-target verified state and exceptions; one passing pilot is not portfolio completion.

Feed reusable evidence back into the existing central principle when it reveals a real gap, with
traceable provenance and a boundary. Keep scientific/runtime facts in their project. Do not create
a central rule from one incidental local difference or recapture the entire conversation here.

Treat a repair as autonomous only when its scope and semantics are understood, local invariants
are preserved, it is reversible with a known recovery path, no active writer is being overwritten,
and the applicable checks can establish the result. Required confirmation for security, credentials,
destructive data operations, spending or production changes still applies. Generic simplification
does not authorize deleting RAW, ADRs, cases, user data or historical evidence.

For multi-session work, reuse the standard's existing progress owner. Keep a compact adoption
record: target, current owner, applicability, intended change, verification and next action.
For an exception, record reason, evidence, local owner and a condition for revisiting it. Do not
create a new database or permanent register for a small one-off change.

## Reassess the system on demand

Read the last relevant review/rollout state when present, then refresh facts that can change the
decision. Look for meaningful changes in user workflow, friction, models/platforms, upstream support,
integration costs, failures and applicability. Check whether exceptions still hold and whether
copied rules have drifted or become unnecessary.

Select work by expected owner effort saved, recurrence, risk and number of genuinely applicable
consumers. Use change-aware discovery plus targeted deep review; do not load every memory, rule
or case into every run. Inspect all relevant consumers in the requested scope or identify the
coverage gap honestly. Continue an existing useful rollout instead of proposing it again.

Review both **what to spread** and **what to simplify, replace or retire**. Search existing/native
capabilities and mature GitHub solutions before building common infrastructure. Consult primary
engineering sources from OpenAI, Anthropic, Kimi, MiniMax and Apple Developer where relevant.
Read [research-and-reuse.md](references/research-and-reuse.md) for credibility, currentness and
replacement boundaries; do not require every publisher on every run.

Compare meaningful candidates with keeping the current solution. Consider goal/semantic fit,
actual habits, compatibility, maintenance/license, total migration and operating cost, ownership
and reversibility. Distinguish explicit current preferences from inferred or historical habits.
Old habits may change; newest and most popular are not automatically better.

Choose **keep, adopt, adapt, build narrowly, simplify/retire, or test first**. For uncertainty, use
the smallest authorized experiment that can decide it: baseline, representative workload, positive
and negative controls, expected benefit and stop/rollback condition. Preserve domain-specific truth;
a standard validator, replay engine or scanner may not cover every custom responsibility.

Prioritize user benefit and cross-workflow leverage over cosmetic uniformity. Reviews need not
manufacture PRs, rules or tool changes. Continue authorized improvements to acceptance; distinguish
proposals from implementation. A semantic rule change still belongs in its existing canonical owner.

## Stop when the requested outcome is established

Finish when scoped consumers are verified aligned, repaired and checked, or carry a justified
exception/explicit blocker. For a general review, finish the selected authorized improvements and
state any uninspected scope. Do not invent more work or retry an unchanged no-op to keep evolving.

The default is one on-demand run with a concise outcome. A future recurring schedule is opt-in and
external to this skill; none is implied or created. See
[adoption-and-review.md](references/adoption-and-review.md) for a compact run contract and adoption
record when the work genuinely needs one.

## Relationships with existing workflows

- This skill owns cross-workflow selection, applicability, adoption orchestration and reassessment.
  It does not become the semantic owner of standards it propagates.
- [harness-upgrade](../harness-upgrade/SKILL.md) owns substantive harness research requirements,
  design, implementation and normal verification. Pass it the selected change and applicability
  evidence rather than copying its workflow or relaxing its gates.
- [agent-knowledge-garden](../agent-knowledge-garden/SKILL.md) owns knowledge-topology discovery,
  routing and drift repair. Reuse its audits when those are the actual work.
- [skill-creator](../skill-creator/SKILL.md) owns authoring and controlled skill-development tests;
  [verify](../verify/SKILL.md) and repository tests own correctness evidence.
- [conversation-closeout](../conversation-closeout/SKILL.md) captures conversation-wide lessons
  and routes writeback when closeout is in scope. Its outputs can seed adoption/review candidates;
  do not duplicate its ledgers, RAW or receipt semantics here.
- [fresh-agent-acceptance](../fresh-agent-acceptance/SKILL.md) owns the separate post-completion
  question of whether behavior survives source-context loss. Use its actual isolation and frozen
  rubric when that risk matters; same-context self-review is not that proof.

Resolve sibling skills through the current shared catalog or canonical mykcs/myk-skills repository
if paths are unavailable. Keep shared standards in .agents, reusable workflows in myk-skills, local
truth in its project/live owner and historical evidence in its evidence owner.

## Finish with the outcome

Explain what improved or should improve, where it applies, what intentionally stays different,
what was actually verified, and what remains blocked or awaits a decision. Distinguish reviewed,
proposed, piloted, adopted and integrated states. Link the existing owner for details.
Unchanged reviews need no new ADRs, rules, receipts or Wish/Dev generation.
