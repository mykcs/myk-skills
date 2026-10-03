---
name: server-artifact-governance
description: >-
  Organize and reclaim space on authorized research/ML servers without losing scientific value or
  touching other users' assets. Use when the owner asks to 整理服务器, 清理 checkpoint/adapter/run,
  腾空间, 迁移/归档科研资产, 清理大型文件, audit storage, or decide what can be deleted. Resolve the
  target server's current authority first, then perform read-only inventory, prove ownership,
  current use and retention intent, establish exact recoverability or rebuildability, archive safe
  candidates, produce an exact reclaim manifest, execute only currently authorized precise cleanup,
  and verify physical reclaim. Never infer ownership from project-name similarity or broad paths,
  never equate upload success with recoverability, and never use broad prune as a shortcut.
when_to_use: >-
  Trigger for “整理服务器”, “再清理一批 checkpoint”, “服务器空间不够”, “哪些大型文件可以删”,
  “把不用的 run/model/archive 搬到云端再删”, “清理旧实验”, “腾磁盘空间”, “server cleanup”,
  “storage reclaim”, “archive old checkpoints”, or equivalent authorized research-server asset
  governance work.
metadata:
  version: "1.2.1"
  category: operations-recovery
  owner: mykcs
triggers:
  - 整理服务器
  - 清理服务器
  - 清理 checkpoint
  - 清理 Checkpoint
  - 腾空间
  - 大型文件清理
  - 科研资产归档
  - 旧实验整理
  - server cleanup
  - storage reclaim
  - artifact cleanup
---

# Server Artifact Governance

Use this workflow to turn a research server from an accidental archive into a **safe working set**:
keep what current work needs, preserve scientifically valuable history off-server, and reclaim only
objects whose ownership, liveness, retention intent, and recovery story are actually closed.

The goal is **not** “delete as much as possible”. The goal is:

> Recover space without losing science, breaking active work, crossing another user's boundary, or
> creating recovery claims that have not been proven.

This Skill owns the reusable **workflow**. The target repository/server owns current paths,
accounts, deletion authority, lifecycle classes, provider destinations, live experiment state,
and machine-specific guards.

For the user's ZJU research server, load
[references/zju-server.md](references/zju-server.md) after this router.

For experiment-derived scientific assets, also use
[references/research-asset-lifecycle.md](references/research-asset-lifecycle.md). It distills the
recovery/disclosure/asset-routing model used by the owner's fuhuo recovery manual without turning
that website into a second execution-policy owner.

## Non-negotiable four-gate model

For any scientifically meaningful local object, local destructive removal requires all applicable
gates to be true at the action boundary:

1. **OWNERSHIP** — prove the user/project has disposition authority over the exact object.
2. **RECOVERABILITY** — prove the exact scientific bytes are recoverable off-server, or prove the
   target policy explicitly classifies the object as non-scientific/rebuildable where exact bytes
   do not matter.
3. **CURRENT USE / RETENTION** — prove it is not active, not a resume dependency, not under current
   analysis/rollback hold, and not otherwise intentionally retained.
4. **EXACT SCOPE / AUTHORITY** — mutate only the exact currently authorized object set under the
   target project's current deletion policy.

These gates are conjunctive, not a score. One unknown gate means HOLD.

## Keep recovery, disclosure, and live provider state separate

For project-owned scientific assets, track at least three independent dimensions when the owning
project supports them:

```text
recovery_state: SERVER_ONLY -> REMOTE_BACKED_UP -> RECOVERY_VERIFIED
disclosure_state: PRIVATE | EMBARGOED | PUBLIC | NEVER_PUBLIC
provider_visibility: live observation, not policy authority
```

Only evidence moves `recovery_state`. A successful upload may justify `REMOTE_BACKED_UP`; it does
not become `RECOVERY_VERIFIED` until the target project's immutable identity/readback/restore
requirements pass.

Disaster recovery never grants publication authority. A private recovery copy may be fully
`RECOVERY_VERIFIED`; a public provider object may still violate the project's disclosure state.
Capacity pressure must not silently change visibility, licensing, canonical namespace, or research
publication intent.

When the project maintains `recoverability_class`, Passport/Registry, asset ledger, or an Artifact
DAG, update those existing owners rather than inventing a second inventory.

### What is not ownership evidence

Never upgrade ownership merely because:

- the directory/repository/project name contains OpenEVO, Evo, WebShop, or another shared project;
- everyone on the server works on similar experiments;
- a path sits below one familiar workspace;
- Unix owner is `root`;
- an image/tag/container has a familiar prefix;
- the current Agent previously managed or inspected the object.

Distinguish source/workspace lineage, human/project disposition authority, and runtime caller.
Shared or unresolved ownership stays protected.

## Phase 0 — Resolve current authority before scanning

Before a large inventory or mutation:

1. identify the exact server / namespace / filesystem whose capacity matters;
2. read that project's current Agent/router and storage/lifecycle/recovery authorities;
3. inspect current open worklines, cleanup manifests/receipts, and active operators when concurrent
   work could collide; treat one exact object set as having one cleanup writer at a time;
4. classify the current user request:
   - inventory only;
   - archive/recovery only;
   - reclaim proposal;
   - exact authorized deletion;
5. preserve stricter current project rules over this Skill.

Do not use an old closeout, memory, cached provider state, or previous chat approval as current live
truth when the relevant fact can change.

If another Agent/workline already owns an overlapping reclaim manifest or is actively archiving,
hashing, or deleting the same exact objects, do not become a second writer. Reconcile the current
ledger/receipt and work as a read-only sidecar or switch to a non-overlapping candidate set.

## Phase 1 — Read-only inventory first

Start bounded. Read-only does not mean unbounded.

Collect only enough evidence to find the real space owners and build a useful candidate set:

- current absolute time/timezone;
- `df`/filesystem capacity and inode state for the backing filesystem that matters;
- bounded top-level allocated sizes for the user's real workspace/data roots;
- active containers and their relevant bind mounts;
- active processes/controllers and exact path references needed for liveness decisions;
- current experiment/run state relevant to large assets;
- model/run/checkpoint/cache/archive candidates above a useful size threshold;
- remote Git/HF/OCI/upstream evidence already known for those candidates.

When `df` and a namespace-local `du` disagree, resolve mount/backing-filesystem/container namespace
boundaries before blaming Docker or assuming hidden data is somebody else's. Bind capacity evidence to
the filesystem that actually backs the candidate: deleting a GalaxyFS object cannot be validated by
watching root-overlay `df /`, and deleting an overlay object cannot be validated from GalaxyFS `df`.

Avoid broad recursive `find`, `du`, hashing, or cross-user process crawling when a narrower query
answers the decision.

### Critical-headroom mode

When the backing filesystem is close to ENOSPC, change the **order of work**, not the safety gates:

- sample current `df`/write trend with a short bounded check so urgency is real rather than assumed;
- stop long recursive inventory/hash scans that are not needed for the next decision;
- prefer already-proven, project-owned **P3/rebuildable** caches, temporary environments, derived
  arrays, duplicate staging copies, or provider-native caches whose exact bytes are not scientific
  authority, when current project authorization permits their cleanup;
- prefer provider/tool-native cache cleanup for rebuildable caches when it is narrower and more
  auditable than raw directory deletion;
- do not stage new large archives on the same nearly-full filesystem merely to prepare a cleanup;
- do not kill/preempt active science, widen permissions, or weaken recovery/approval gates just to
  create headroom.

The first goal is to restore a small safe operating margin with the lowest-risk exact object, then
continue normal governance.

## Phase 2 — Build an exact candidate ledger

Every candidate must be individually identifiable. At minimum capture:

```text
candidate_id
captured_at
exact_path_or_object_id
kind
size_bytes
filesystem_or_device
inode
nlink
allocated_blocks_or_bytes
ownership_evidence
scientific_role
active_process_refs
active_container_refs
config_resume_refs
recent_use_or_hold
source_git_or_run_identity
local_content_identity
remote_or_rebuild_source
immutable_remote_revision_or_digest
remote_content_identity
fresh_restore_or_reload_evidence
expected_reclaim_bytes
physical_reclaim_basis
reclaim_uncertainty
decision
reason
```

Do not make a directory-level delete decision from its top-level owner alone when descendants,
mounts, worktrees, mixed UIDs, or active references can differ.

### Hardlinks, copy-on-write, deduplication, and physical reclaim

Byte identity is a **scientific/content** fact, not automatically a **capacity** fact.

Before advertising reclaim from local duplicates:

1. inspect filesystem/device, inode, link count and allocated blocks/bytes where the filesystem
   exposes them;
2. group hardlinked paths by `(device, inode)` before summing allocated space;
3. if `nlink > 1` and another link to that inode will remain, deleting one pathname can reclaim
   **0 physical bytes** for that inode even though the logical pathname is hundreds of GB;
4. distinct inodes may still share CoW/deduplicated backend blocks, so equal hashes or apparent
   logical duplicates do not guarantee equal physical reclaim;
5. keep `logical_deleted_bytes`, `unique_allocated_bytes`, `expected_physical_reclaim`, and
   observed before/after `df` as separate fields.

Never sum per-path `st_blocks` across hardlinks as if every pathname owned distinct blocks.

## Phase 3 — Classify by independent dimensions

Do not begin with one `keep/delete` bit.

Resolve independently:

- ownership/disposition authority;
- liveness/current references;
- scientific uniqueness/value;
- recent/near-term use and explicit holds;
- exact recoverability vs functional rebuildability;
- restore/rebuild cost;
- local physical cost;
- deletion authority for this exact task.

Use the target project's current lifecycle labels when they exist. If no project taxonomy exists,
present a small human-readable projection such as:

- **ACTIVE / HOLD** — in use or needed locally;
- **ANALYSIS HOLD** — not running but current scientific analysis/rollback needs it;
- **ARCHIVE THEN RECLAIM** — scientifically valuable, cold-storage candidate;
- **REBUILDABLE** — exact historical bytes are not required and an immutable rebuild source exists;
- **SHARED / UNKNOWN** — ownership or reference graph unresolved; do not touch.

The labels are presentation, not the safety mechanism.

## Phase 4 — Route assets to the right recovery owner

Use one-fact-one-owner:

- **GitHub** — code, manifests, configs, provenance, hashes, receipts, recovery instructions;
- **Hugging Face / scientific object store** — checkpoints, adapters, model-derived state, large
  trajectories/data archives when policy allows;
- **OCI/GHCR** — complete runtime images when exact runtime preservation is needed;
- **W&B / observability service** — scalar history, charts and telemetry bindings only when the
  project uses them; observability is not the scientific asset authority;
- **pointer** — unchanged upstream/base assets or project-defined no-new-binary states where a
  durable immutable pointer is the truthful artifact;
- **pinned upstream** — rebuildable/downloadable external models/data when immutable identity is
  sufficient;
- **no archive** — explicitly non-scientific temporary/cache data that target policy says can be
  rebuilt and whose exact bytes do not matter.

Do not upload secrets, credentials, private keys, runner credentials, unapproved public data, or
unlicensed material.

Do not create a new long-term recovery destination merely because the preferred provider quota is
full. A fallback destination must be allowed by current project/retention policy and remain
discoverable later.

## Phase 5 — Separate upload from recovery proof

`upload started`, `upload completed`, bytes-sent counters, CAS/Xet/LFS pre-upload success, and
“the page opens” are not recovery proof.

For scientifically meaningful bytes, close the transaction with evidence appropriate to the
provider and target policy:

```text
local exact identity
    -> remote path/object exists
    -> immutable commit/revision/digest exists
    -> remote size/content identity matches
    -> fresh read/download/reload evidence when required
    -> durable receipt points both directions
```

Treat provider quota, commit API, network, and client cache/state as separate failure layers.
If a client reports failure after transferring bytes, inspect the actual remote tree/revision before
retrying. If a new repository is used, do not assume pre-upload/cache state from another repository
proves blobs are committed there.

A failed recovery gate leaves the local source in place.

## Phase 6 — Current-use and liveness gate immediately before reclaim

Remote recovery makes an object **eligible** for local thinning; it does not make it disposable.

Before destructive action, refresh:

- open file descriptors / relevant process references;
- container mounts;
- cwd/argv/config/resume pointers;
- controllers/supervisors or next-stage reacquisition;
- current experiment/analysis/rollback holds;
- exact local identity if the object could have changed since archive verification.

If a liveness check finds one of this workflow's own stale diagnostic/upload processes, do not
silently ignore it. Identify it, stop/finish only that known process when authorized, then rerun the
same gate. Unknown references remain a blocker.

## Phase 7 — Reconcile scientific identity before a reclaim proposal

When the large object belongs to an experiment/research lifecycle, reclaim starts only after the
experiment-side identity is coherent enough to explain what the object is.

Use the owning project's existing sequence, which commonly looks like:

```text
seal / reconcile terminal experiment state
-> route code / evidence / model-derived state / runtime / observability
-> verify immutable recovery evidence
-> update Registry / Passport / asset ledger / Artifact DAG when those exist
-> exact reclaim proposal
-> current deletion-authorization gate
-> point-of-use liveness/identity recheck
-> exact local thinning + receipt
```

Do not manufacture a checkpoint merely to make an archive look complete. If the owning project
defines a pointer/no-update representation, preserve that truthful state instead.

## Phase 8 — Produce the owner-facing reclaim proposal

Before any destructive action that the target policy requires the owner to approve, produce from
one snapshot:

### ELI5 summary

Answer first:

1. how much physical space is currently available;
2. whether current important work is at near-term risk of filling the filesystem;
3. the biggest safe candidates and their approximate reclaim;
4. which important assets are explicitly protected this round;
5. what exact action still needs authorization, if any.

### Technical evidence

For each candidate include:

- exact object/path;
- bytes;
- ownership evidence;
- active refs;
- scientific role/retention state;
- remote/rebuild identity;
- restore evidence;
- expected physical reclaim and uncertainty;
- exact proposed action.

If the target policy uses a versioned deletion manifest, create it with a non-authorized initial
state and bind approval to the exact version/object identities.

If a later retention/scientific re-review changes the candidate set, protected set, retention class,
or keep/delete boundary, treat the old approval as **superseded** even when surviving paths/hashes
are unchanged. Issue a new unique manifest in its non-authorized initial state and obtain whatever
fresh approval the current project policy requires. A previously approved larger/sibling manifest
must not silently authorize the revised semantic scope.

Do not ask the user to repeat an approval already given for the exact current manifest. Do not
reinterpret a broad historical “整理服务器” instruction as approval for a newly discovered
destructive set when current policy requires exact approval.

## Phase 9 — Execute precise reclaim only inside current authority

When the exact action is authorized:

1. rerun the live/identity gates;
2. use exact paths/object IDs — no unreviewed glob expansion;
3. process a small batch at a time;
4. under critical disk pressure, prefer **one-object transactions**:
   archive -> immutable verify -> exact prune -> `df` readback -> next object;
5. record before/after physical filesystem availability on the **same backing-filesystem probe path** as the candidate set, and preserve enough mount/device identity to prove both samples refer to that same filesystem;
6. preserve active experiments, protected models, controllers, CI, and shared resources;
7. stop on drift rather than expanding the deletion set.

### Concurrent-writer and control-plane failures

Immediately before mutation, refresh the exact manifest/receipt namespace or other current project
coordination surface. If another workline has superseded the manifest or owns overlapping exact
objects, stop that object set and reconcile rather than racing two cleanup writers.

If the primary SSH/RDC/tool route fails, treat that as a control-plane route failure, not permission
to widen a least-privilege sidecar or change file ownership. Consult the target project's current
recovery authority and use an already-authorized independent control plane when one exists. Ask for
physical/manual intervention only at a genuine authentication, physical, safety, or unknown-risk
boundary.

A tool-safety denial on an irreversible primitive is also not permission to disguise the same
destructive action through tmpfs, permission changes, a different shell, or another equivalent
route. Use a project-supported executor/reversible placement path when legitimately available, or
stop with the exact blocker.

Never use broad cleanup as a shortcut:

- no `docker system prune`;
- no `docker image prune -a`;
- no global volume/network prune;
- no global HF cache sweep;
- no workspace-wide `rm -rf`;
- no “delete everything older than N days” policy;
- no deletion of sibling-user/shared/owner-unresolved assets.

### Git worktrees and code

A clean working tree is not remote-recoverability proof. Prove the exact HEAD/dirty state is
recoverable. Use Git worktree-aware removal for linked worktrees rather than raw directory deletion.

For **temporary Git sandboxes / negative fixtures / verifier clones** whose current HEAD contains
local-only synthetic commits, do not collapse "clean" into "safe to delete". If current project
policy classifies the sandbox as rebuildable/non-scientific and the exact final tree matters only
for reproducing the fixture, an accepted compaction form is:

```text
reachable immutable base commit
+ binary-capable patch from base -> local HEAD
+ commit metadata / fixture identity
+ task-local qualification or result metadata when relevant
+ durable hashes for the recovery pack
+ fresh replay check on a clean checkout of the base
```

The recovery pack must live outside the ephemeral delete root and be materially smaller than the
sandbox it replaces. Verify the base is actually retrievable from the current authoritative remote;
do not preserve a patch against another local-only parent and call that remote recovery.

Dirty or untracked worktrees are **HOLD by default**. Do not silently flatten unique uncommitted
state into a "rebuildable" label. Capturing dirty state requires an explicit stronger recovery plan
that preserves the exact files/diffs and passes its own restore/replay gate.

This compaction pattern is for disposable test/qualification sandboxes. It is not a replacement for
preserving canonical project history, scientific source authority, or branches whose commit graph
itself is the artifact.

### Docker

Shared-daemon `reclaimable` is an observation, not an ownership/deletion list. Separate container
writable layers from shared image layers and prove exact object provenance/reference state.

## Phase 10 — Verify actual reclaim and system health

After each meaningful batch:

- re-read physical filesystem availability on the candidate set's same backing filesystem, not a default `/` chosen by habit;
- record exact deleted/thinned objects;
- report logical bytes separately from observed physical `df` delta;
- check protected/active workloads remain healthy;
- clean temporary upload/archive staging created by this workflow when safe;
- preserve recovery receipts and immutable identities;
- record unexpected changes or concurrent-write uncertainty.

If logical deletion succeeds but physical free space does not increase as expected, first verify that
the pre/post samples were taken from the candidate's **same backing filesystem**. A zero delta on a
different mount is a measurement error, not evidence for surviving hardlinks. Once the measurement
target is proven correct, check at least: remaining hardlinks/link count, deleted-but-open file
descriptors, shared/CoW/deduplicated storage, and concurrent writes. If the historical pre-delete
sample targeted the wrong filesystem, do not invent an exact physical-reclaim value after the fact. Do not respond by deleting more scientifically valuable objects merely to
make the original reclaim estimate come true.

On a shared filesystem, do not attribute the entire session-level `df` delta to this workflow if
other users/processes can write concurrently.

## Phase 11 — Closeout

A complete run reports:

- what was inventoried;
- what was kept and why;
- what was archived and where;
- what exact recovery proof passed;
- what was deleted/thinned;
- logical vs observed physical reclaim;
- current free space;
- protected active/analysis assets still present;
- unresolved HOLDs/blockers;
- durable project receipt/writeback when the project requires one.

Do not turn dated free-space values, PIDs, provider incidents, or one run's exact candidate list into
standing policy.

## Fail-closed conditions

Stop destructive progress for the affected object when any of these is unresolved:

- ownership/disposition authority;
- another user's/shared object boundary;
- current liveness or resume dependency;
- current analysis/retention hold;
- scientific exact-byte recovery;
- secret/license/visibility decision;
- target repository/provider identity;
- immutable revision/digest;
- local object drift after verification;
- a newer overlapping cleanup writer/manifest that supersedes the current object set;
- exact deletion authority required by current project policy.

A blocker for one object does not block independent safe inventory/archive work on other objects.

## Output style

Default to concise Chinese for this owner's server work:

- first paragraph: current risk / reclaimed or reclaimable amount / protected items;
- then one compact candidate table or list;
- explain only the evidence needed for a decision;
- preserve exact hashes/paths/revisions in receipts or technical detail, not in the opening ELI5.

When the user asks “继续”, continue from durable receipts/current authority rather than restarting the
whole inventory blindly.

When a real execution exposes a reusable workflow failure or a safer recovery pattern, feed that
mechanism back into this Skill's contract/evals after the operational task reaches a safe boundary.
Do not leave a reusable lesson only in one conversation receipt when future cleanup Agents should
benefit from it.
