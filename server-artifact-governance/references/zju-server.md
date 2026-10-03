# ZJU server adapter

This reference is a **thin routing adapter** for the user's current ZJU research server. It does not
own server policy and must not be treated as a frozen copy of current facts.

Repository: `mykcs/zju-server`

## Read path

For “整理服务器 / 清理 checkpoint / 腾空间 / 科研资产归档” on this server:

1. read current `mykcs/zju-server/AGENTS.md`;
2. read current `docs/storage-governance-agent-contract.md`;
3. read current `docs/storage-pressure-artifact-reclaim-sop.md`;
4. read current `docs/research-artifact-lifecycle.md`;
5. read current `docs/free-first-backup-policy.md`;
6. read current `docs/shared-filesystem-deletion-safety.md` when file deletion/ownership matters;
7. use current `scripts/verify_remote_reclaim_gate.py` for scientific source removal when the
   project route requires it;
8. if cleanup control-plane access or UID/permission boundaries matter, read current
   `docs/rdc-sidecar-runbook.md` and `docs/workspace-ownership-contract.md`; do not widen the
   least-privilege RDC sidecar merely to make cleanup easier;
9. for OpenEVO scientific assets, also read the current artifact/publication/experiment-tracking
   authority in `mykcs/openevo-experiment`.

Current project files win if this reference becomes stale.

## Stable interpretation

- The shared server is multi-user; common OpenEVO/Evo naming is **not** personal ownership proof.
- Namespace `root`, project path names, Docker tags, and historical management are not enough to
  authorize another object's deletion.
- Scientific local deletion requires current ownership/liveness/retention plus exact off-server
  recoverability under the project gate.
- “Uploaded” is not the same as `REMOTE_VERIFIED_EXACT`.
- Current analysis/experiment holds keep an exact-remote asset local.
- Broad Docker/HF/workspace pruning is not a substitute for exact-object decisions.
- If a retention re-review changes candidate/protected classification or the effective delete set,
  the prior exact-manifest approval is superseded; follow the current SOP and create a new
  non-authorized manifest rather than inheriting the older approval.
- For duplicate-path capacity estimates, inspect inode/link/allocation identity before claiming
  physical reclaim. A hardlink alias can have large logical size and still reclaim zero physical
  bytes while another link remains.

## Authorization routing

This shared Skill never widens zju-server deletion authority.

For capacity-pressure cleanup, follow the **current** zju-server reclaim SOP's deletion-authorization
gate. If it requires an exact versioned manifest to be shown and approved, stop there until that
exact approval exists. If a later project policy changes that rule, follow the newer current
authority rather than preserving this sentence as a historical approval requirement.

An already-approved exact current manifest should not be re-asked merely because the Agent/session
changed. But if the semantic scope changes after a renewed scientific/retention review, the old
manifest is no longer the exact current manifest and its approval must not be inherited.

If the Mac/RDC/SSH control route fails during cleanup, keep the server sidecar's least-privilege
boundary intact. Consult the current owning recovery/control-plane authority instead of broadening
RDC permissions or changing workspace ownership as a shortcut.

## Live facts that must never be copied from old receipts

Always re-read:

- free space/inodes and backing filesystem;
- active runs/processes/containers/mounts;
- current protected models/checkpoints;
- current HF/GitHub/OCI destinations and quotas;
- current remote revisions/digests;
- current analysis/rollback intent;
- current authorization state for the exact reclaim manifest;
- current overlapping cleanup manifests/receipts or active writer ownership;
- inode/link/allocation identity when reclaim depends on duplicate/hardlink accounting.

Dated closeouts and conversation memory are evidence/history, not live truth.
