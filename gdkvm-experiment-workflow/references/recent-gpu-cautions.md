# Recent GPU usage cautions

Use this reference after [host-cases.md](host-cases.md) for GPU status, launch,
reservation, recovery, or capacity questions. It distills recent parent
`zju-server` operating changes; the parent policy wins, and every dated snapshot
must be rechecked live before use.

Authoritative sources: `/Users/myk/Claude/Projects/zju-server/docs/experiment-execution-policy.md`,
`/Users/myk/Claude/Projects/zju-server/docs/operations.md`, and
`/Users/myk/Claude/Projects/zju-server/docs/server-facts.md`.

## Status is not launch authority

- For a status-only “who is using GPU0–7?” query on `lyg2171`, prefer the single
  read-only `ssh wangrui_root gpu-who`; return the eight-row owner/workload table
  first. Use `gpu-who --details` only when requested or attribution is unresolved.
- Never answer a live status question from an old snapshot. A status result also
  does not reserve a GPU; launch still needs the current UUID, owner, occupancy,
  storage, output-collision, and contract checks.
- On `whs512`, follow the direct-host snapshot and ownership procedure in
  [rtx6-operations.md](rtx6-operations.md); do not assume `gpu-who` exists there.

## Authorization, holders, and shared capacity

- Standing project authorization is not an exclusive reservation. An ordinary
  launch needs an in-pool UUID that is live-idle at the point of use.
- A project-owned holder is allowed only when the active parent/project contract
  records the reservation. Acquire it only while the UUID is genuinely available;
  never kill, reset, restart, or preempt another workload to create a holder.
- Treat a verified holder bound to its UUID as `project-reserved`, verify the
  holder before handoff, remove only the project’s own holder immediately before
  launching the real workload, and record holder-release and launch timestamps.
  If launch fails before GPU acquisition, restore the holder only when the policy
  says it is safe and the reservation is still active.
- The remaining 5090 pool is shared first-come capacity. Coordinate voluntary
  release; an empty lock file or idle snapshot is not a reservation.

## Dynamic placement and topology

- For a homogeneous 5090 dynamic plan, `scripts/oe --gpus auto:N --wait` must
  resample the whole standing-pool candidate set. Busy cards reduce capacity;
  later-idle cards may backfill pending cells. Record backfill latency and any
  capacity-starvation event.
- UUIDs are physical identity and accounting evidence; indices are launch-time
  aliases only. A missing or replaced UUID is a topology/policy mismatch and
  fails closed. A retry/resume cannot migrate a running cell unless its contract
  explicitly permits migration.

## Namespace and control-plane boundaries

- In a namespace-limited view, nontrivial memory with no visible PID means
  `occupied / owner-unresolved`, not free, orphaned, or leaked. Zero utilization
  means only idle at that sample.
- `root@wangr-dev` is container root with Docker-daemon capability, not proof of
  physical-host root. Do not stop/restart/remove/rename or `docker exec` into
  sibling containers, run global Docker prune, use privileged/arbitrary mounts,
  or mutate daemon/driver/CUDA/SSH settings for an experiment.
- Never free capacity by killing, GPU-resetting, restarting, or preempting an
  external workload. If ownership cannot be established, leave the cell blocked.

## Evidence and qualification

- A runtime qualification is reusable only when the relevant runtime fingerprint
  matches. Recheck volatile GPU, disk, process, output, and network facts at each
  launch or handoff.
- Preserve the operator, contract/authorization basis, timestamped UUID snapshot,
  holder identity (if any), cell-to-UUID mapping, and blocked/lost-capacity reason.
