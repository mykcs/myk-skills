# Knowledge buoyancy / 知识沉浮

Use this mode when the owner asks to reorganize instructions/rules by importance, slim hot context,
distill cases/receipts/incidents, or run a broad Workflow evolution review where knowledge entropy
is part of the problem.

The semantic owner is the current
[.agents Knowledge Architecture](https://github.com/mykcs/.agents/blob/main/docs/agents/KNOWLEDGE-ARCHITECTURE.md).
This reference owns the **review/repair procedure**, not a second hierarchy definition.

## Goal

Make the system easier to enter and harder to misunderstand:

- high-consequence, stable, first-action guidance floats toward routers/current owners;
- task/domain guidance stays discoverable but on-demand;
- reusable mechanisms are extracted from evidence;
- cases/RAW/receipts/history sink as preserved evidence rather than competing current instructions;
- stale/superseded detail loses retrieval prominence without rewriting history.

“Float” means **earlier retrieval**, not “more morally important”. A severe historical incident can
remain cold after its reusable lesson is promoted.

## 1. Resolve current owners before moving anything

Read the root/project router and current knowledge architecture first. Identify:
- HOT entrypoints injected or routinely read;
- WARM current standards/protocols/owners;
- COOL derived/deeper reference;
- COLD RAW/receipts/cases/history/dated audits/rollouts.

Do not infer importance from file age, size, title, or directory depth alone. Verify whether the
content still owns current behavior, merely explains it, or only proves that something happened.
## 2. Parse cold evidence before deciding it is “just a case”

For each materially relevant case/RAW/receipt/incident cluster:

1. identify the visible symptom and underlying mechanism;
2. search current shared/project learned knowledge for an existing stable owner;
3. search the project current owner/guard for already-enforced behavior;
4. classify the result:
   - already parsed / no action;
   - strengthen existing learned mechanism;
   - promote new bounded learned mechanism;
   - write back to current owner/guard;
   - intentional non-promotion (one-off/live/speculative/evidence-only);
5. preserve evidence links and anti-overgeneralization boundaries.

Do **not** create one rule per case. Repeated evidence strengthens one mechanism.
Do **not** delete the case merely because its conclusion was extracted.

## 3. Promotion rules — what should float

Promote only when the next-higher layer needs the information to improve future first action.

Strong signals:
- independent recurrence across cases/projects;
- high cost of omission: security, data loss, scientific validity, publication/authority mistakes;
- stable semantics, not live values;
- broad applicability within a clear scope;
- one clear writable owner;
- machine-checkable invariant suitable for a test/audit.

Typical path:

```text
case / RAW / receipt
-> derived shared/project practice
-> current protocol / standard / guard
-> thin HOT router only if nearly every matching task needs it immediately
```

A rule does not jump directly from one incident to HOT merely because the incident was severe.
## 4. Demotion rules — what should sink

Demote retrieval prominence when information is:
- provider/UI/command detail from one incident;
- exact IDs, SHAs, quotas, PIDs or other volatile state;
- a completed rollout whose current rule exists elsewhere;
- an obsolete draft/implementation plan;
- duplicated explanation already owned by a stronger current source;
- historical rationale needed for audit/reconstruction, not normal execution.

Demotion normally means:
- remove from top-level/start-here routing;
- move under a Historical/Archive/Evidence section or history path when safe;
- replace duplicate semantics with a short pointer to the writable owner;
- keep Git/RAW/case provenance intact.

Do not mass-move files just to make directory depth look tidy. Physical relocation is justified only
when link/caller impact is bounded and the semantic owner is clear.

## 5. Router and owner checks

A healthy result should satisfy:

- HOT routers are compact and contain only non-negotiable invariants + routing;
- no HOT router asks ordinary work to start from RAW/receipts/cases;
- current owner pages separate current guidance from dated evidence;
- stable repeated/high-consequence mechanisms in cases are represented in learned/current owners;
- one fact has one writable owner;
- large current files are reviewed for cohesion, but line count alone never forces a split;
- executable invariants are tests/audits where practical.

Use repository-native audit tooling when available. For `mykcs/.agents`, run
`python3 scripts/knowledge_buoyancy_audit.py --strict` plus ordinary repository validation.
## 6. Acceptance and reporting

Report four things, compactly:

1. **Floated** — mechanisms/rules promoted upward and why.
2. **Sunk** — completed/superseded/detail surfaces demoted from routine discovery.
3. **Parsed evidence** — case/receipt clusters now linked to a derived/current owner.
4. **Still cold / unresolved** — evidence intentionally left cold, active-writer conflicts, or
   promotion candidates owned by another current PR.

A successful pass may legitimately leave many COLD files. **Evidence stays deep; conclusions
surface.** The target is not a low file count; it is low ambiguity and low
time-to-correct-first-action.

## Research basis and boundary

Current first-party guidance supports the underlying pattern:
- OpenAI's harness-engineering account argues for a small map instead of one giant instruction
  manual, structured repository knowledge, progressive disclosure and recurring garbage collection.
- Anthropic's Agent Skills guidance similarly treats progressive disclosure as layered loading:
  metadata first, then the core skill, then supporting files only as needed.

These sources support the architecture principle, not a universal numeric threshold or a claim that
every repository should use identical folders. Refresh current sources when a substantive harness
change depends on platform behavior.
