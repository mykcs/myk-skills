# GDKVM experiment contract and evidence

Read this reference for a new phase, changed hypothesis, materially changed runtime path, or scientific recovery decision. Reuse the current project-owned contract when one already exists.

## Contract ownership

Store the active contract and result ledger in the GDKVM project’s versioned experiment area. Do not make `~/.claude/plans`, chat text, a case file, or this skill a second source of scientific truth.

The contract must be committed and pushed before formal task consumption. Hash the finalized machine-readable content and bind qualification, launch, and result receipts to that hash.

## Minimum fields

Use the repository’s schema when it exists. Otherwise cover this semantic minimum:

```yaml
schema: gdkvm.experiment-contract.v2
identity:
  campaign_id: <stable-id>
  repository: <remote>
  commit: <full-sha>
  protocol_hash: <hash-after-freeze>
science:
  question: <one falsifiable question>
  baseline: <exact config/evidence identity>
  arms: [<complete frozen set>]
  seeds: [<complete frozen set>]
  primary_metric: <name and extraction rule>
  decision_rule: <predeclared comparison>
  invalid_rules: [<infra/scientific validity rules>]
  retry_policy: <which invalid cells may retry and how many times>
  stop_rule: <success, futility, safety, and budget stops>
  claim_boundary: <what the run can and cannot establish>
runtime:
  fingerprint_inputs: [<trainer/evaluator/dependencies/model/data>]
  qualification_receipt: <matching PASS or pending>
resources:
  authorization_basis: <current policy or explicit owner record>
  authorized_gpu_uuids: [<UUIDs>]  # or a policy-defined candidate pool
  resource_assignment_mode: exact | dynamic-live-idle
  gpus_per_cell: <N>
  max_concurrent_cells: <N>
  gpu_hour_budget: <limit>
  cell_timeout_seconds: <limit>
execution:
  launcher: systemd-run-user
  unit_prefix: <collision-free prefix>
  cell_key_fields: [campaign_id, arm, seed, attempt]
  atomic_claim_root: <durable contract-owned path>
  fencing_lock: <host-supported per-cell exclusive lock>
  claim_initialization_grace_seconds: <bounded value>
  claim_reconcile_interval_seconds: <bounded value>
  output_root: <durable path>
  tracking_mode: online | offline | disabled
```

Do not copy the example’s field names if the repository already has an authoritative schema. Preserve the meaning and validate it with project code.

## Material-change test

A new label or session is not a material change. Re-freeze and requalify only to the degree required when changing trainer/evaluator behavior, model/data identity, dependencies affecting execution, treatment/config semantics, task/seed set, metric extraction, retry rules, budget, or claim boundary.

Changing only a report renderer, monitoring connection, evidence serialization, collision-free path, or another reward-blind wrapper can be an engineering repair when the frozen decision tree permits it. Preserve the failure and prove equivalence before exact resume.

## Planning and scheduler rules

- Research/design may explore alternatives before freeze; formal execution consumes only frozen arms and seeds.
- `exact` assignment binds each cell to preregistered UUIDs and fails closed if unavailable.
- `dynamic-live-idle` selects from the authorized candidate set at launch and records the chosen UUID. It must not widen the pool.
- Busy or owner-unresolved GPUs reduce capacity. They do not justify preemption, stale pinning, or extra cells.
- Parallelism is a resource parameter, not a scientific arm. Respect `gpus_per_cell`, `max_concurrent_cells`, and GPU-hour budget.
- Keep an already running cell on its gated UUID unless the recovery rule explicitly permits migration.
- Atomically claim each campaign/arm/seed/attempt in a shared durable root before launch. Persist `cell_key`, `protocol_hash`, deterministic unit, claimant token, timestamp, and claim state with atomic replacement.
- Hold the per-cell fencing lock across token/state CAS, final live gate, deterministic-unit launch, and `started | launch_failed` persistence. Orphan reconciliation takes the same lock, persists `orphaned`, and revokes the old token before a later attempt can be allocated.
- An existing claim always routes through bounded state/unit/ledger reconciliation, never a second launch. An orphaned claim is preserved as failed launch evidence; only the frozen retry policy may allocate a new attempt.

## Recovery decision tree

Continue automatically when all answers are yes:

1. Is the failure operational rather than a measured scientific outcome?
2. Does the repair keep treatment, data, evaluator, metric, retry semantics, budget, and claim boundary unchanged?
3. Does the contract authorize the retry/resume and remaining attempts?
4. Are runtime qualification and live resource gates valid for the resumed path?
5. Can the original failure and repair be preserved in the ledger?

Otherwise stop before more formal consumption and amend/re-freeze the contract or request the unresolved human decision.

## Result ledger

The ledger should let another agent reconstruct the run without reading chat history. Record:

- campaign/protocol hash and repository SHA;
- runtime fingerprint and qualification receipt;
- cell identity: arm, seed, attempt, claim metadata/state/token/fencing/orphan classification, unit, GPU UUID/index, timestamps, output path;
- launch gate and resource authority basis;
- completion status, validity classification, retry lineage, failure reason;
- raw metric source plus parsed primary/safety metrics;
- planned/started/completed/valid/invalid/missing denominators;
- resource use, stop-rule decision, supported and unsupported claims.

Do not overwrite historical attempts. A later successful retry does not erase the first failure.

## Verification questions

Before closeout, an independent verifier should be able to answer:

1. Did execution match the frozen arms, seeds, metric, decision rule, retry policy, and budget?
2. Can every reported value be traced to a raw artifact and exact runtime/source identity?
3. Are invalid, missing, and retried cells visible in the denominator?
4. Were only authorized, live-gated GPU UUIDs used?
5. Does the final claim stay inside the preregistered boundary?

If any answer is unknown, report it as unknown or blocked. Do not manufacture a PASS, case, ADR, or memory to fill the gap.
