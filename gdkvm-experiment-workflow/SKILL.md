---
name: gdkvm-experiment-workflow
description: Orchestrate reproducible GDKVM experiments on the RTX6 GPU server from protocol freeze through launch, monitoring, recovery, verification, and evidence closeout. Use for GDKVM phase/sweep/long-run work or when deciding how to safely continue an existing GDKVM experiment; status-only GPU questions should remain read-only.
license: MIT
metadata:
  type: skill
  version: "2.0.0"
  updated: "2026-08-31"
  category: ml-experiment-orchestration
  source_of_truth:
    - "The active GDKVM repository protocol and current result ledger"
    - "The current host/account/GPU policy governing RTX6"
    - "references/rtx6-operations.md"
    - "references/experiment-contract.md"
  tags: [gdkvm, experiment, rtx6, hydra, torchrun, systemd-run, reproducibility]
  user_invocable: true
---

# GDKVM experiment workflow

Run GDKVM experiments as a resumable, evidence-bound program. The default is calm autonomy: reuse durable authorization and matching qualifications, recheck volatile state at use, and ask the user only at a real authority, destructive-action, visibility, or unresolved scientific-choice boundary.

## Route the request

- **Status / “谁在跑” / progress**: do read-only inspection and report evidence. Do not start, stop, retry, edit a protocol, or claim ownership from memory alone.
- **Resume / retry an existing run**: resolve the current frozen contract and ledger first. Continue only missing eligible work without changing its scientific semantics.
- **New phase / sweep / changed hypothesis**: read [references/experiment-contract.md](references/experiment-contract.md), freeze the decision rule and budget before looking at new outcomes, then commit and push the contract before formal consumption.
- **Any live RTX6 action**: read [references/rtx6-operations.md](references/rtx6-operations.md) immediately before acting. Host policy and live evidence override historical cases and examples.

The July 2026 phase plans, cases, and `gdkvm-train-launcher` are historical evidence. Reuse demonstrated invariants such as durable `systemd-run` supervision, but do not inherit plaintext credentials, fixed GPU indices, stale branches, fixed five-arm designs, or old approval gates.

## Operating model

### 1. Resolve current truth

Confirm the actual local repository, remote, branch, dirty state, and current protocol/result entrypoint. On RTX6, verify host identity, operator identity, repository SHA/dirty state, runtime identity, GPU index-to-UUID map, occupancy, disk, active units, output paths, and tracking mode.

Classify each prerequisite:

- **Immutable**: Git/config/data/model hashes; reuse exact evidence.
- **Runtime-fingerprint**: Python/Torch/CUDA/dependency/trainer/evaluator path; reuse a matching PASS qualification.
- **Live**: GPU occupancy, process/unit state, disk, output collisions, credentials/network; recheck at point of use.
- **Human-only**: missing resource authority, destructive/shared-resource action, visibility/release, or a scientific fork not resolved by the contract.

Do not turn a new session, phase label, retry, resume, or progress report into another approval or full-qualification gate.

### 2. Freeze or reuse the experiment contract

Prefer the project’s existing current protocol. Do not create a parallel plan merely because a new Agent session began.

A new or materially changed contract must bind the scientific question, baseline, arms, seeds, primary metric, decision rule, invalid-attempt rules, retry semantics, timeout, GPU-hour/attempt budget, stop rule, claim boundary, runtime fingerprint, resource authority, and output identity. Freeze it before outcome inspection and commit/push it before formal work.

Never assume a historical arm count, win ratio, or DICE threshold. Those are valid only when the current contract preregisters them.

### 3. Qualify the execution path

For a new or materially changed trainer/runtime/evaluator path:

1. Run applicable CPU/unit/config checks.
2. Run the smallest contract-required single-cell or single-GPU smoke.
3. Save a receipt binding the exact runtime fingerprint and test scope.
4. Scale only after PASS and only to the frozen matrix.

If the fingerprint matches a prior PASS, reuse it and run only the live gate. A monitor disconnect or SSH failure is not evidence that the remote workload failed; inspect the unit, PID, GPU UUID, output heartbeat, and durable artifacts before relaunching.

### 4. Gate and schedule GPUs

- GPU UUID is the durable identity; record the index mapping used by `CUDA_VISIBLE_DEVICES` at launch.
- Use only GPUs covered by the current resource authority. Connection access is not GPU authorization.
- Immediately before launch, perform the live gate in `references/rtx6-operations.md`. Nontrivial occupancy with unresolved ownership is blocked, not free.
- Never kill, reset, preempt, or enter another user’s process/container to obtain capacity.
- Concurrency follows the frozen resource mode, GPUs per cell, and live capacity. Do not hardcode sequential execution or opportunistically add arms/seeds because cards are idle.
- Once a cell is running on a gated GPU, keep it pinned unless the contract’s recovery rule explicitly permits migration.

### 5. Launch and supervise durably

Prepare code, config, output directory, deterministic cell/unit identity, and command before the final live gate. Atomically claim the exact campaign/arm/seed/attempt in the shared durable control root. Hold the contract-defined per-cell fencing lock across the final token/state check, live gate, `systemd-run`, and launch-state persistence. If a claim already exists, follow its fenced reconciliation/orphan path and never relaunch that attempt. Monitor with `systemctl`, `journalctl`, GPU telemetry, and output heartbeats.

Do not use `nohup`, `tmux`, `screen`, `ssh -f`, or a bare background process for formal long runs on RTX6. Stop only the exact project-owned unit, and only when the user request, frozen stop rule, or safe recovery path authorizes it; do not `kill <pid>` as routine control.

### 6. Recover without changing the science

Continue autonomously for reward-blind, semantics-preserving repairs: reconnect monitoring, fix evidence serialization, correct an output/path wrapper, use a contract-permitted tracking fallback, or exact-resume missing eligible cells within the frozen retry and budget rules.

Stop and re-freeze before changing an arm, seed set, data split, evaluator, primary metric, retry semantics, decision rule, budget, or claim boundary. Preserve failed attempts and reasons; never erase or relabel them to make the denominator look better.

### 7. Verify and close

Use an independent verification pass when delegation is available. Reconcile at least:

- planned / started / completed / valid / invalid / missing cells;
- per-cell Git/config/runtime/GPU UUID/unit/output identities;
- primary and safety metrics against the preregistered decision rule;
- retries, exclusions, time/GPU budget, and stop-rule execution;
- protocol, qualification, launch, and result evidence paths.

Completion is not scientific success. Report the supported claim, unsupported claim, and next decision separately. Update the project-owned protocol/result ledger; create a case, ADR, decision stream, or memory only when its own trigger is satisfied.

## Delegation

For a genuinely new or complex phase, separate planning, execution, and verification responsibilities. Planning freezes the contract; execution cannot widen it; verification must inspect raw evidence rather than approve the executor’s summary. These roles may be separate agents when available, but fixed model names and a mandatory three-agent ceremony are not part of the scientific protocol.

Independent read-only discovery may run in parallel. GPU cells run sequentially or concurrently only as allowed by the frozen matrix and current authorized live capacity.

## When to ask the user

Ask only when evidence cannot resolve one of these boundaries:

- no durable authority covers the requested GPU/job;
- a destructive or shared-resource mutation is required;
- the next step changes frozen science, retry semantics, or budget;
- repository/publication visibility or release scope changes;
- credentials, 2FA, CAPTCHA, or administrator action is required.

Do not ask merely to acknowledge a startup report, reuse a matching PASS, continue a permitted retry/resume, select among equivalent live-idle authorized GPUs, or perform read-only diagnosis.

## Completion report

Keep the final report short and concrete:

1. changed or executed work;
2. protocol/runtime/GPU UUID/unit/output identities;
3. verification result and supported scientific claim;
4. one-line risk or blocker;
5. next command only when real work remains.

Then add 1–3 actual pitfalls and 1–3 prevention actions. Never print secrets or invent missing evidence.
