# Website-improve orchestrator recovery — v4.2.0

Recovery restores a valid execution/verification lane when a subagent or tool path
stalls. It does **not** grant permission to publish work automatically.

## 1. Principle

A stalled agent may already have useful work product. Preserve and inspect it before
throwing it away, but treat every completion claim as untrusted until independently
verified.

Recovery order:

1. inspect existing artifacts/work product;
2. identify intentional vs pre-existing changes;
3. determine which role stalled;
4. respawn/reassign that role or switch to another available tool path;
5. rerun affected verification evidence;
6. continue to independent Verifier acceptance;
7. enter publication only when the plan explicitly requested it.

## 2. Tool provisioning

Before assigning work, ensure the role has the tools actually needed for its task.
Do not hard-code one product-specific tool-loading mechanism as a universal contract;
use the current harness/tool discovery mechanism available to the runtime.

If a subagent starts with no usable tools:

- fail the assignment early;
- re-provision/reassign instead of letting it idle indefinitely;
- preserve the plan and existing evidence so another Executor can continue.

## 3. Detecting a stall

Use observable progress rather than wall-clock guesses when the runtime exposes it:

- tool calls/results;
- artifact modification time;
- workflow status;
- heartbeat/progress events;
- repository/worktree changes.

A long-running process is not automatically stalled, and a silent process is not
automatically healthy. Use the best available runtime evidence.

## 4. Work-product inspection

For a stalled Executor, inspect without publishing:

```bash
git status --short
git diff --check
git diff --stat
```

Where appropriate also inspect:

```bash
git diff
git log -1 --oneline
```

Do not assume an existing commit belongs to this task; compare against the session
manifest and current plan.

If the worktree includes unrelated pre-existing changes, keep them isolated. Do not
use blanket staging as a recovery shortcut.

## 5. Recovery actions by role

### Planner stalled

- reconstruct scope from the user request and existing plan draft;
- rerun Planner with the same task constraints;
- do not start edits until a valid modern plan exists.

### Executor stalled

- preserve verified useful edits;
- reject edits outside the plan;
- rerun missing/affected verification;
- create/update the modern exec log with blockers and session manifest;
- do not self-approve.

### Verifier stalled

- do not let Executor self-certify;
- spawn a fresh independent Verifier with plan + exec log + current evidence;
- Verifier remains read-only.

## 6. Publication is not recovery

The following are **not** generic recovery actions:

```text
git add -A
git commit --no-verify
git push origin main
smart-autopush.sh
```

Do not execute them merely because an Executor stalled.

If publication was requested and execution acceptance is complete, hand the verified
change to the repository's canonical publication lifecycle. That lifecycle owns its
own branch/commit/push/PR/deploy safety checks.

A stale/diverged branch should generally be rebuilt/replayed on latest main when that
is safer than rewriting shared history. Do not force-push just to make recovery fast.

## 7. Verification after recovery

Any recovered work invalidates evidence that could have been affected by the recovery.
Rerun the relevant checks and record fresh evidence before final Verifier acceptance.

Examples:

- source edit recovered → rerun build/test/lint that covers it;
- layout edit recovered → rerun browser/visual evidence;
- deployment requested → verify the published/deployed target after publication;
- multi-site recovery → rerun evidence for the affected scoped sites, not unrelated sites.

## 8. User escalation boundary

Do not make the user the fallback for ordinary tool/process failures.

Keep expanding the agent-accessible solution space unless blocked by a genuine
human-only boundary:

- login/authorization not available to connected tools;
- 2FA/CAPTCHA;
- physical-device action;
- irreversible or high-risk approval;
- an external control plane unavailable to all connected routes.

When such a boundary exists, report exactly what is blocked and what evidence already
passes. Do not call an unavailable check PASS.

## 9. Memory after recovery

A recovery incident becomes a case/ADR/memory entry only when it meets the current
memory-promotion threshold (reusable rule, recurring defect, durable architecture
change, etc.). Do not create a case file solely because a subagent stalled once.

## Permanent anti-patterns

- ❌ retrying a dead agent forever without inspecting work product
- ❌ abandoning usable work because one agent process died
- ❌ auto-committing/pushing stalled work
- ❌ bypassing the independent Verifier after recovery
- ❌ asking the user to perform agent-accessible diagnostics
- ❌ using old four-site recovery commands for a single-site task
