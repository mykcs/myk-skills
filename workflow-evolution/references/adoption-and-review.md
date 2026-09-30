# Adoption and on-demand review

Use this reference for a cross-workflow rollout or general review. Reuse existing owner
files and tools. These are lightweight fields and examples, not a new governance platform.

## Current shared owners to read

- [Knowledge architecture](https://github.com/mykcs/.agents/blob/main/docs/agents/KNOWLEDGE-ARCHITECTURE.md):
  one writable owner per fact, small routers, selective registry and current-vs-history boundaries.
- [Repository registry](https://github.com/mykcs/.agents/blob/main/docs/agents/repositories.json):
  discovery of long-lived work surfaces; it is not an instruction to mutate every listed repository.
- [Wish protocol](https://github.com/mykcs/.agents/blob/main/docs/agents/WISH_PROTOCOL.md):
  the shared project-intent lifecycle. Current guidance is project-scoped, not website-specific;
  a folder is appropriate when its lifecycle justifies it, while a small existing mission/WISH
  owner can also satisfy the role.
- [Dev protocol](https://github.com/mykcs/.agents/blob/main/docs/agents/DEV_PROTOCOL.md) and
  [CI standard](https://github.com/mykcs/.agents/blob/main/docs/agents/CI_STANDARD.md):
  shared development/acceptance semantics with local implementation and live provider owners.
  Current CI policy unifies semantics rather than vendors. Apply that established division without
  asking the user to restate it: each repository chooses the best implementation for its workload.
- [CI portfolio rollout](https://github.com/mykcs/.agents/blob/main/docs/agents/CI_PORTFOLIO_ROLLOUT.md):
  existing cross-repository CI progress owner. Refresh it and the relevant active work before
  starting parallel migration records.

Links and wording were checked on 2026-09-30. Reopen the current owners for a new run; this reference
does not freeze future policy, active PR state, provider identity or adoption counts.

For evidence and rule consolidation, also read:
- [RAW contract](https://github.com/mykcs/.agents/blob/main/docs/learning/schemas/RAW_RECORD.md):
  direct wording stays faithful; new interpretations do not rewrite old evidence
- [Derived knowledge](https://github.com/mykcs/.agents/blob/main/docs/learning/schemas/DERIVED_KNOWLEDGE.md):
  strengthen one mechanism with evidence and boundaries rather than duplicate near-synonym rules
- [ADR-0002](https://github.com/mykcs/.agents/blob/main/docs/adr/0002-project-authority-roles-no-pkg.md):
  extend current knowledge architecture; roles are not mandatory folders or another umbrella
- [ADR-0003](https://github.com/mykcs/.agents/blob/main/docs/adr/0003-cross-tool-conversation-learning-owner.md):
  central learning/evidence and project current truth have different owners
- [ADR-0004](https://github.com/mykcs/.agents/blob/main/docs/adr/0004-generalize-wish-folder-lifecycle.md):
  generalizes Wish folder scope while preserving optional, project-appropriate adoption

RAW answers what the owner said; ADR records why a durable decision was made; cases preserve
incident evidence; current rules/Dev explain present behavior. Reconcile local interpretation and
enforcement against central guidance while preserving each evidence role and historical provenance.

## The compact run contract

Resolve fields that matter for the current task:
- scope: selected standard/workflow and target repositories or consumer class
- purpose: user outcome and what must stay true
- standardization target: common semantics, file convention, implementation, provider, or a mix
- action authority: inspect / propose / local draft / PR / integrate / live migration, as granted
- trigger: on-demand general review or topical propagation of a proven improvement
- reporting: concise outcome, meaningful findings and decisions genuinely requiring the user
- progress owner: existing program/standard/project review record, if a durable record is useful

Use the user's instruction and current central standards to resolve fields before asking another
question. Implement authorized safe repairs; do not use the run contract as an approval ritual.
Missing authority for one action does not block independent applicability work or other safe fixes.

The skill contains no polling daemon, background subscription or hidden auto-migration loop.
Recurring invocation is only a future opt-in option through an external scheduler with explicitly
chosen cadence, scope, authority and notification destination; this draft creates no schedule.

## Applicability before copying

For each relevant consumer, answer:
1. Does it share the problem and invariants solved by this improvement?
2. Is the behavior already present under another valid owner or shape?
3. Can it inherit the shared contract directly, or does it need an adapter?
4. What local requirement requires a real exception?
5. What evidence would establish adoption, and what is the rollback route?

Useful compact record:
`consumer → current owner → applicability → intended delta/exception → proof → next action`

Possible applicability states:
- already aligned
- adoption candidate
- adapter needed
- justified exception
- out of scope
- evidence missing

Keep execution state separate: proposed, piloting, qualified, adopted, verified, blocked. A proposed
consumer row cannot count as adoption. Central documentation being merged proves nothing about
whether all intended consumers actually use it.

An exception needs a concrete local requirement, supporting evidence, owner and revisit condition.
"It is different" is not enough. Equally, identical filenames or providers are not inherently
better. Revisit exceptions after meaningful changes instead of giving every one a ceremonial expiry.

## Wish propagation example

A newly improved Wish lifecycle may apply across websites, tooling, research and infrastructure.
Extract its shared intent/routing/history behavior, then inspect each project's actual need.

A changing research program might benefit from the full folder. A stable utility might already
have a concise mission file serving the same role. A frozen dataset archive may be out of scope.
Apply the shared principle in the shape that best fits each project. If a future explicit request
changes the shared convention, update its canonical authority before propagating the new convention.

Verify that ordinary future tasks reach the correct current Wish and respect project-local science
and runtime truth. Merely creating four Markdown files does not prove usable adoption.

## CI propagation example

Read the central CI contract, then inspect each repository's validation, check identity, command,
provider and live authority. Follow the existing tiering rather than asking the user to choose a
universal provider or duplicating acceptance rules in this skill.

A portable Linux validator, native iOS qualification, scientific/GPU acceptance and a static
redirect can need different execution lanes. If consolidating providers is explicitly selected,
compare these constraints, current plans/costs/access and replacement coverage before cutover.

Qualify a representative target, then materially different target classes. Use negative controls:
a failing validator must fail the gate, a skipped run must not masquerade as execution, and
incorrect head/provider identity must not satisfy acceptance. Follow the existing CI standard
for exact-head qualification, authority transfer, rollback and predecessor retirement.

Do not start another progress ledger when the current CI portfolio rollout already owns the work.

## A proportional general review

Use change-aware discovery for broad scope, then inspect the highest-impact uncertainties in depth.
The baseline is the last verified design and adoption state, not a stale chat summary.

Look for:
- newly useful improvements not yet assessed for other workflows
- conflicting or duplicated shared/local rules and stale projections
- exceptions whose original reason no longer holds
- maintenance/security/support changes in actual dependencies
- shifts in user habits, environments, frequency or friction
- simpler native or mature upstream capabilities that now cover custom machinery
- previously accepted complexity that no longer buys useful behavior

Make coverage honest. For a portfolio review, name inspected surfaces and material gaps; do not
claim every repository was checked from one central document. Reuse a compact last-reviewed record
only when needed to maintain coverage across runs.

Carry forward still-relevant work instead of repeatedly proposing the same unchanged idea. Retain
the current design when it wins. Report a concise no-change outcome when that is the finding.
Do not fabricate improvements to justify another run.

## Rollout and stopping

For each selected change, define the acceptance outcome and a reversible path at the affected
boundary. Expand only after evidence supports the next consumer class and authorization covers it.
A change in semantics, live access, provider cost or risk may need a new decision.

Stop expansion on an unexplained regression, an unavailable necessary gate or a real authority
boundary. Preserve completed verified targets, state the narrow blocker, and continue independent
in-scope work. Do not declare the whole portfolio complete while relevant targets remain unknown.
