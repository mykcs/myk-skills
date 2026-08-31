# GPU host cases and routing

This is a routing reference, not a resource-authorization list. Read it before live work when the user names `whs512`, `rtx6`, `lyg2171`, `wangr-dev`, or “4×3090/8×5090”. Verify the resolved host and operator identity live; dated facts below are evidence, not current availability.

## Case A — `whs512` = RTX6 = 4×RTX 3090

**Use for:** GDKVM Hydra/TorchRun work on the direct RTX6 server.

- The user-facing host label is `whs512`; historical verified identity is `rtx6` at `172.31.71.202`.
- Historical login evidence mentions `RuiWang2024` through the macOS Keychain item
  `gdkvm-202-sshpass`; never print or store its secret. Current Agents must use
  the parent-approved root/operator path for host-side Git, staging, supervision,
  and tests. The historical user/key path is not a normal fallback; if root
  access is unavailable, stop and re-qualify rather than silently selecting it.
- Read [rtx6-operations.md](rtx6-operations.md) for historical connection and
  supervision evidence, while treating current parent policy and live identity
  as authoritative.
- Hardware observed on 2026-08-11: four NVIDIA GeForce RTX 3090 devices, 24,576 MiB each.
- Historical GDKVM checkout: `/data/wr2024/Repo/code_modern_v3`; typical runtime shape is Hydra + `torchrun`, supervised by the user systemd manager.
- A historical 0/1 split and another user’s old 2/3 ownership are not current authorization. Resolve exact allowed GPU UUIDs from the active host/project contract and perform the immediate two-sample live gate.
- If the direct host, account, key fingerprint, runtime, or GPU topology differs, stop and re-qualify the relevant path. Do not silently fall through to the 5090 workflow.

Read [rtx6-operations.md](rtx6-operations.md) for secure connection, snapshot, UUID mapping, live gate, systemd supervision, monitor-disconnect recovery, and per-cell claim fencing.

## Case B — `lyg2171` daemon label → `wangrui_root` → `root@wangr-dev` (8×RTX 5090)

**Use for:** OpenEvo/WebShop or other experiments governed by the ZJU parent server contract.

- `lyg2171` is the observed Docker daemon/server name, not the interactive shell hostname. The current preferred SSH alias is `wangrui_root`, expected to reach `root@wangr-dev` inside the `dev-wangr` control container.
- Dated hardware evidence records eight NVIDIA GeForce RTX 5090 devices, 32,607 MiB each. GPU UUID, occupancy, and owner state must be checked live at launch.
- Parent authority is `/Users/myk/Claude/Projects/zju-server/docs/experiment-execution-policy.md`; access and identity details are in `/Users/myk/Claude/Projects/zju-server/docs/access.md`. Read those before any server mutation or OpenEvo launch.
- The canonical OpenEvo launcher is the project’s `scripts/oe` and its current campaign/launch-gate contracts. New homogeneous-5090 work normally uses `dynamic-live-idle`; cells record the UUID selected at launch.
- `root@wangr-dev` is container root with Docker-daemon capability, not verified physical-host root. Docker visibility does not authorize sibling-container mutation. Never kill/reset/preempt another workload.
- OpenEvo standing authorization and project-owned holder semantics apply only under the current parent policy and project contract. They do not authorize `whs512`/RTX6 and do not turn an idle snapshot into a reservation.

Read the parent policy and the active project campaign/current-state docs for UUID pool, holder state, runtime qualification, W&B mode, and formal task-consumption authority. Do not copy the RTX6 `RuiWang2024`, `/data/wr2024/Repo/code_modern_v3`, Hydra, or 3090 assumptions into this case.

## Shared routing and stop rules

1. Resolve the label to a live hostname, SSH alias, operator, and GPU model before launch.
2. If the resolved identity does not match the selected case, stop; do not “try the other server” with the same command.
3. Keep scientific contract, runtime qualification, and GPU authorization host-scoped. A passing 3090 path is not a 5090 qualification, and 5090 standing authorization is not RTX6 authority.
4. Preserve UUIDs as identity and indices only as launch-time aliases; recheck occupancy/owner at use.
5. Treat these cases as reusable operational patterns, not permission to reveal credentials, alter host infrastructure, or mutate shared workloads.
