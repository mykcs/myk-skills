# Research asset lifecycle bridge

This reference distills the reusable research-asset lifecycle used by the owner's fuhuo recovery
manual. It is not a copy of the website and does not replace project-specific Recovery/Disclosure,
Passport, Registry, publication, or deletion authorities.

Human-facing reference repository: `mykcs/fuhuo_20260419`

Current fuhuo pages to consult when that project context matters:

- `/docs/experiment-lifecycle` — the full science/run/asset/recovery sequence;
- `/docs/research-assets` — provider reconciliation, recovery/disclosure audit, fresh restore and
  exact reclaim proposal;
- `/docs/server-governance` — machine lifecycle and point-of-use deletion safety boundary.

## Durable model

### Recovery is a state machine, not a boolean

```text
SERVER_ONLY
-> REMOTE_BACKED_UP
-> RECOVERY_VERIFIED
```

- `SERVER_ONLY`: the valuable bytes are still dependent on the server.
- `REMOTE_BACKED_UP`: a remote copy exists, but the strongest recovery claim is not yet proven.
- `RECOVERY_VERIFIED`: immutable remote identity and the project's required readback/restore
  evidence are closed.

Do not skip from “upload succeeded” to `RECOVERY_VERIFIED`.

### Recovery and disclosure are orthogonal

A project may separately track:

```text
PRIVATE
EMBARGOED
PUBLIC
NEVER_PUBLIC
```

The desired disclosure state is not inferred from provider visibility. Provider visibility is live
evidence to reconcile against policy. Disaster recovery must never make unpublished research
public merely to simplify backup or verification.

### Route by semantic role

A common research split is:

```text
GitHub   -> code, config, Passport/Registry, manifests, receipts, small evidence, provenance
HF       -> checkpoint, adapter, model-derived state, large trajectory/data archives
GHCR/OCI -> runtime/container identity when exact runtime preservation matters
W&B      -> scalar history / charts / observability binding
pointer  -> unchanged upstream asset or project-defined no-new-binary state
```

The owning project decides the actual providers and namespaces.

### Identity graph stays with the scientific project

If the project has Experiment Passport, Experiment Registry, Server Run Passport, asset ledger or
Passport Artifact DAG, those are the identity owners. Server cleanup must update/reconcile them
rather than creating a parallel cleanup-only identity system.

### Reclaim is downstream of scientific closeout

For experiment-derived assets:

```text
seal/reconcile experiment
-> inventory assets by semantic role
-> establish recovery/disclosure state
-> immutable readback + size/content identity + required fresh restore
-> update project asset graph/ledger
-> exact NOT_AUTHORIZED reclaim proposal when that is the project contract
-> owner/current-policy approval
-> server point-of-use deletion gate
-> exact delete/thin + receipt
```

A recovery-safe object can still remain locally held for analysis, resume, rollback, comparison or
another explicit retention reason.

## Ownership boundary

The fuhuo website explains the human mental model and recovery journey. The shared
`server-artifact-governance` Skill owns reusable execution workflow. Target repositories/servers own
live paths, permissions, provider truth, scientific identity and destructive authority.

Do not fork any of these into another editable copy.
