# RTX6 operations for GDKVM

Read this reference immediately before any live RTX6 inspection or mutation. It records the operating shape, not permanent resource ownership.

## Known profile and authority boundary

Last confirmed from this Mac on 2026-08-11:

- host `rtx6` / `172.31.71.202`;
- login `RuiWang2024`;
- four RTX 3090 GPUs;
- GDKVM checkout historically at `/data/wr2024/Repo/code_modern_v3`;
- long runs survive SSH through the user systemd manager.

These are discovery hints. Re-verify them live. Historical GPU 0/1 use and GPU 2/3 ownership are not current authorization. Obtain the permitted GPU set from the current project/host policy or versioned experiment contract; if none exists, GPU launch needs human authority.

## Secure connection

The password belongs only in macOS Keychain service `gdkvm-202-sshpass`, account `RuiWang2024@172.31.71.202`. Never place it in a prompt, file, note, process argument, or log.

```bash
SSHPASS="$(security find-generic-password \
  -s 'gdkvm-202-sshpass' \
  -a 'RuiWang2024@172.31.71.202' -w)" \
sshpass -e ssh \
  -o ConnectTimeout=10 \
  -o StrictHostKeyChecking=yes \
  RuiWang2024@172.31.71.202
```

If host-key verification fails or changes, stop and verify the fingerprint with the administrator. Do not switch off strict checking. A timeout is connectivity evidence only; it says nothing about remote job state.

## Read-only startup snapshot

Collect one timestamped snapshot before changing code or consuming GPUs. Do not print secret environment values.

```bash
hostname
whoami
date --iso-8601=seconds
git -C /data/wr2024/Repo/code_modern_v3 status --short --branch
git -C /data/wr2024/Repo/code_modern_v3 log -1 --format='%H %s'
loginctl show-user RuiWang2024 -p Linger
nvidia-smi --query-gpu=index,uuid,name,memory.total,memory.used,utilization.gpu \
  --format=csv,noheader
nvidia-smi --query-compute-apps=gpu_uuid,pid,process_name,used_memory \
  --format=csv,noheader
systemctl --user list-units --type=service --state=running,failed \
  --no-pager --no-legend
df -h /data/wr2024/Repo/code_modern_v3
```

Also capture the exact Python executable, Python/Torch/CUDA versions, Hydra config identity, trainer/evaluator hashes, output root, and tracking mode required by the contract. Treat a dirty checkout as a reproducibility warning; formal work must bind the exact effective source or use a clean contract-owned checkout.

Before GPU consumption, show a concise startup report with the campaign purpose and scientific question, frozen-contract/gate status, Git SHA/branch/dirty state, host/operator, runtime fingerprint and qualification receipt, visible GPU UUID snapshot, authorized GPU set or pool, output root, and tracking identity/mode. This report is observability, not an acknowledgement gate; continue automatically unless it reveals a real authority, safety, protocol, resource, or reproducibility blocker.

If `Linger=no`, do not silently change host account configuration. Use an already-authorized host procedure or request the required administrator/owner action.

## GPU live gate

1. Resolve the contract-authorized GPU UUIDs or candidate set.
2. Sample index, UUID, memory, utilization, and compute applications.
3. Attribute visible PIDs with read-only process metadata when needed.
4. Wait briefly and sample again immediately before launch.
5. Select only UUIDs that remain authorized and live-idle, unless the current host policy defines another explicit handoff mechanism.

Fail closed when memory is nontrivial but the process/owner cannot be resolved. Zero utilization means idle at the sample time, not free or reserved. Index is only a launch-time alias; preserve the UUID-to-index map in the receipt.

Do not use a stale snapshot, old phase record, unit name, or user memory as resource ownership proof. Never obtain capacity by killing, resetting, preempting, stopping, or entering another user’s workload.

## Durable launch

Derive one deterministic cell key and unit name from the frozen identity, for example:

```text
cell key: <campaign>:<arm>:<seed>:<attempt>
unit:     gdkvm-<campaign>-<arm>-s<seed>-a<attempt>
```

Before the final live gate, atomically create a claim directory for that cell key under a shared durable control root visible to every executor. The winner immediately atomically persists claim metadata containing `cell_key`, `protocol_hash`, deterministic `unit`, a unique non-secret `claimant_token`, `created_at`, and `state=claimed`.

Use a host-supported per-cell exclusive fencing lock on a filesystem with verified cross-executor locking semantics. The claimant must hold that lock while it:

1. atomically compare-and-swaps `claimed → launching`, conditional on the same claimant token and protocol hash and on `state != orphaned`;
2. performs the final live GPU gate;
3. invokes `systemd-run` for the deterministic unit; and
4. atomically persists `started` or `launch_failed` before releasing the lock.

If the lock or atomic-replace semantics are not reliable on the chosen control filesystem, fail closed. A late claimant whose token/state CAS fails must not launch.

If creation reports that the claim exists, never launch that attempt and never delete/reuse its claim. Read the claim, verify cell/protocol identity, query the deterministic unit, journal, output, and ledger, then:

- for missing metadata within the contract’s initialization grace, or `claimed` / `launching`, wait a bounded interval and reconcile again; do not declare orphaned while the fencing lock is held;
- for `started`, recover monitoring or final reconciliation;
- for `launch_failed`, preserve the failure and apply the frozen retry policy;
- after the grace period, acquire the same fencing lock, recheck token/state plus deterministic unit/process/output/ledger absence, then atomically persist `state=orphaned` and revoke/fence the old token; do not resurrect the same attempt.

Only after the fenced orphan state is durable may the frozen retry policy allocate the next attempt, with remaining budget and lineage to the prior claim. This makes executor loss a visible failed/orphaned launch rather than a duplicate scientific cell.

The actual command must come from the frozen contract. A typical multi-rank shape is:

```bash
systemd-run --user \
  --unit='<unique-unit>' \
  --working-directory=/data/wr2024/Repo/code_modern_v3 \
  --setenv=CUDA_VISIBLE_DEVICES='<live-gated-index-list>' \
  --setenv=PYTHONPATH=/data/wr2024/Repo/code_modern_v3 \
  --setenv=HYDRA_FULL_ERROR=1 \
  --setenv=OMP_NUM_THREADS=1 \
  --property=RuntimeMaxSec='<contract-timeout-seconds>' \
  /home/RuiWang2024/.local/bin/uv run torchrun \
    --standalone \
    --nproc_per_node='<gpus-per-cell>' \
    /data/wr2024/Repo/code_modern_v3/train.py \
    --config-path=/data/wr2024/Repo/code_modern_v3/config \
    --config-name='<frozen-config-name>' \
    hydra.run.dir='<collision-free-output-dir>'
```

Verify the actual `uv`, Python, `torchrun`, and Triton paths before using the example. Keep Hydra configs inside the repository config tree so relative defaults resolve. Do not invent overrides after the contract is frozen.

Do not add `--wait` merely to keep a run alive. The systemd service supplies durability. A scheduler may wait on the exact unit state before dispatching another cell when the contract requires sequential execution.

After launch, persist `state=started` while still holding the fencing lock and record the cell key/claimant token, timestamp, unit, PID, selected UUIDs/indices, command/config identity, source SHA, output path, and initial heartbeat.

## Monitoring and stop

```bash
systemctl --user status '<unit>' --no-pager
journalctl --user -u '<unit>' --no-pager
nvidia-smi --query-gpu=index,uuid,memory.used,utilization.gpu --format=csv,noheader
```

Use `rg` on retrieved logs when available to extract the contract’s metric and error patterns. Preserve the raw journal/output path; a truncated metric tail is a progress view, not the result ledger.

If monitoring disconnects, reconnect and inspect unit state, PID, UUID, journal, and output heartbeat before relaunching. If the exact project-owned unit must stop under an authorized stop/recovery rule:

```bash
systemctl --user stop '<unit>'
```

Then verify the unit, processes, GPU state, checkpoint/output integrity, and ledger update. Do not use a PID kill as routine control.

## Tracking and network

If the contract uses W&B or another online tracker, probe its fixed non-secret identity at most once per execution epoch. Persist the result. Use offline fallback only when the frozen contract permits it; observability failure must not silently change scientific semantics.
