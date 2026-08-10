---
name: website-improve
description: |
  Evidence-first website improvement workflow (v4.2.0). Uses three independent
  Planner → Executor → Verifier roles, task-scoped modern artifacts, conditional
  publication, and scope-relevant build/browser/deployed verification. Multi-site
  fan-out is supported without making four-site CI or Git publication universal.
when_to_use: |
  Use for website audits, visual/UX improvements, Astro/site modernization,
  project pages, and multi-site fan-out. Do not use for unrelated bugs or tiny
  documentation-only edits where the workflow overhead adds no value.
metadata:
  version: "4.2.0"
  author: mykcs
  category: web-development
  tags: [website, improve, multi-site, astro, workflow]
  changelog: |
    4.2.0 (2026-08-10): migrate the active workflow to evidence-first modern
    acceptance. Preserve three independent roles; separate execution acceptance
    from conditional publication; remove automatic smart-push, universal four-site
    CI, fixed Git five-field completion, and mandatory per-task memory artifacts.
    4.1.1 (2026-07-25): progressive-disclosure reference split.
license: "MIT"
last_updated: "2026-08-10"
---

# website-improve v4.2.0

`website-improve` is a three-role website improvement workflow:

```text
Planner → Executor → Verifier
```

The three roles are independent. The Planner does not edit. The Executor does not
self-approve. The Verifier is read-only and does not fix failures.

The default artifact path is the **modern** website-improve contract implemented by:

- `~/.claude/scripts/website-improve/plan_json_gen.py`
- `~/.claude/scripts/website-improve/exec_log_gen.py`
- `~/.claude/scripts/website-improve/verdict_json_gen.py`
- `~/.claude/scripts/website-improve/schemas.py`

Legacy generator mode remains available for compatibility with historical callers,
but this active skill must not generate new legacy workflows by default.

## 1. Core acceptance model

Completion has two separate layers.

### Execution Acceptance

Every run must prove:

1. **scope** — the requested website change/audit scope is satisfied;
2. **execution evidence** — fresh first-party evidence relevant to the change exists;
3. **blockers** — unresolved blockers are visible, never hidden;
4. **ownership/target** — the correct repo/site/account was operated on when applicable;
5. **session manifest** — intentional changes are separated from pre-existing changes.

### Publication Acceptance

Commit, push, PR, deploy, and release evidence is required **only when publication is
requested or necessary for the user's requested outcome**.

Publication state is one of:

- `NOT_REQUESTED`
- `NOT_APPLICABLE`
- `VERIFIED`
- `BLOCKED`

Do not manufacture Git history, hosted CI, deployment, case files, or durable memory
merely to make a completion table look full.

## 2. Scope routing

Sub-modes remain useful capabilities, not universal mandatory phases.

| Sub-mode | Use when | Default scope |
| --- | --- | --- |
| **A — Check + Improve** | normal website audit/improvement | requested site(s) |
| **B — Astro Build** | target is Astro or build/dependency work is relevant | requested Astro repo(s) |
| **C — Project Page** | project page / academic project intent | requested project site |
| **D — Multi-Site Fan-out** | user requests multiple sites, sync/fan-out, or scope contains 2+ sites | exactly the sites in scope |

The historical four-site set (`mykcs`, `GDKVM`, `OSA`, `content2html`) remains a
supported multi-site preset. It is **not** a universal validation requirement for an
unrelated single-site task such as `basemodel`.

When the user explicitly requests the historical full sweep, all four sites are in
scope and each must receive the scope-relevant evidence defined in the plan.

## 3. Pre-flight and Planner

Planner owns assumptions, scope, risk decisions, verification targets, and
publication intent. It may proceed autonomously after declaring material assumptions
unless a genuine human-only boundary exists.

Do not ask the user to approve routine reversible steps merely because the workflow
has a Planner stage.

Generate the plan in modern mode:

```bash
python3 ~/.claude/scripts/website-improve/plan_json_gen.py \
  --artifact-mode modern \
  --audit-target "<requested outcome>" \
  --sub-modes "<A,B,C,D as applicable>" \
  --sites "<task-scoped site/repo identifiers>" \
  --expected-wall-clock <minutes> \
  --completion "<task-scoped acceptance criteria CSV>" \
  --verification-targets "<build,test,browser,curl,security,...>" \
  --publication-mode "<none|commit|push|pr|deploy|release>" \
  --session-manifest-required \
  --pre-flight "<assumptions and risk declaration>" \
  --out plan.json
```

Rules:

- `--sites` follows the actual task scope; it is not restricted to the historical four sites.
- `--completion` describes the requested result, not fixed Git/memory ceremony.
- `--publication-mode none` is correct when the user did not request publication.
- Planner must not edit source files or fabricate verification results.

## 4. Executor

Executor owns code/content changes and fresh execution evidence.

Executor must:

- read `plan.json` before editing;
- verify the repository/site target before writes;
- preserve pre-existing unrelated changes;
- make only scope-justified edits;
- run the verification targets named in the plan;
- record blockers instead of silently deferring them;
- record a session manifest;
- write a modern `exec-log.json`.

Executor does **not** automatically commit, push, open a PR, deploy, or create durable
memory just because code execution is complete.

Example modern executor artifact generation:

```bash
python3 ~/.claude/scripts/website-improve/exec_log_gen.py \
  --artifact-mode modern \
  --plan plan.json \
  --files-changed "<path:add:del,...>" \
  --verification-file verification.json \
  --blockers-file blockers.json \
  --publication-state NOT_REQUESTED \
  --session-manifest-file session-manifest.json \
  --out exec-log.json
```

`git_commits`, `smart_push_status`, and `decision_stream_entries` are legacy
compatibility fields. Do not populate them in modern mode unless a transitional
caller explicitly requires them.

### Build safety

If `package.json` / lockfiles / build configuration are changed, regenerate the
relevant lockfile and run the project-owned install/build checks before claiming the
build is healthy. Never infer build success from a small diff.

For layout/CSS/interactive changes, use browser/visual evidence appropriate to the
actual compatibility target. Do not require WebKit merely because an old checklist
said so if the task has a different declared browser target; likewise do not skip it
when Safari/WebKit compatibility is part of scope.

## 5. Publication lifecycle

Publication is separate from execution.

If the plan requests publication, the orchestrator hands the already-verified change
to the canonical Git/deploy lifecycle. For `.claude` Git publication, `/pr` is the
canonical PR surface and operates on already-created commits. Other repositories may
have their own publication contract.

Do not:

- run `smart-autopush.sh` automatically as an Executor side effect;
- `git add -A` / commit / push because a subagent stalled;
- force-push to make a stale branch current;
- treat an unavailable/skipped hosted check as PASS.

After requested publication, final acceptance must mark publication `VERIFIED` or
`BLOCKED`. `BLOCKED` cannot produce a PASS verdict.

## 6. Verifier

Verifier is independent and read-only. It inspects the plan, executor evidence,
current target state, and publication evidence when publication was requested.

Verifier creates an Acceptance object such as:

```json
{
  "scope": "PASS",
  "execution_evidence": "PASS",
  "blockers": "CLEAR",
  "publication": "NOT_REQUESTED",
  "ownership": "PASS",
  "session_manifest": "PASS"
}
```

Then derive the verdict:

```bash
python3 ~/.claude/scripts/website-improve/verdict_json_gen.py \
  --artifact-mode modern \
  --acceptance-file acceptance.json \
  --out verdict.json
```

`--verdict` is assertion-only. It cannot override contradictory evidence.

Verifier returns FAIL when evidence is insufficient. Remediation goes back to a fresh
Executor pass; Verifier does not patch the files itself.

## 7. Scope-relevant CI and deployed verification

Read [`references/4-site-ci-gate.md`](references/4-site-ci-gate.md) for the detailed
rules. The important v4.2.0 interpretation is:

- CI belongs to acceptance only when CI is relevant to the scoped repo/publication contract;
- historical four-site CI fan-out applies only when those four sites are actually in scope;
- deployed-layer `curl` applies when deployed behavior must be proven;
- local source existence is not evidence that deployed behavior works;
- a skipped/missing/unavailable check is never silently converted to PASS.

## 8. Recovery

Read [`references/orchestrator-recovery.md`](references/orchestrator-recovery.md).

Recovery means preserving work product and restoring a valid execution/verification
lane. It does not grant permission to auto-publish.

If an agent stalls:

1. inspect existing work product and session manifest;
2. verify what actually changed;
3. respawn/reassign the appropriate role or continue via an available tool path;
4. rerun affected execution evidence;
5. only enter publication if the plan requested it.

Escalate to the user only for a genuine human-only boundary: login/authorization,
2FA/CAPTCHA, physical-device action, irreversible/high-risk approval, or a control
plane unavailable to every connected agent tool.

## 9. Memory and cases

Decision streams, case files, ADRs, and durable memory are **promotion outputs**, not
universal per-task side effects. Create/update them only when the current memory
promotion rules say the information is durable enough to preserve.

Historical case/benchmark files may describe legacy smart-push/four-site behavior;
they are historical evidence and do not override this active v4.2.0 skill.

## 10. Permanent anti-patterns

- ❌ one agent acts as Planner + Executor + Verifier
- ❌ Executor self-declares PASS
- ❌ Verifier edits files to make its own verdict pass
- ❌ fixed `commit/push/CI/owner` fields define every task's completion
- ❌ four-site CI is required for an unrelated single-site task
- ❌ Executor automatically smart-pushes after every edit
- ❌ recovery commits/pushes stalled work without publication intent
- ❌ durable case/decision-stream output is mandatory for every run
- ❌ missing/skipped CI is called green
- ❌ a failed verification is hidden as a deferred follow-up

## 11. References

Load only what the task needs:

- [`references/3-role-workflow.md`](references/3-role-workflow.md) — modern artifact handoff and role boundaries
- [`references/4-site-ci-gate.md`](references/4-site-ci-gate.md) — scope-relevant CI/deployed verification
- [`references/per-workflow-framework.md`](references/per-workflow-framework.md) — generic evidence-first PER framework
- [`references/orchestrator-recovery.md`](references/orchestrator-recovery.md) — fail-closed stall/recovery behavior
- [`references/quality-checks.md`](references/quality-checks.md) — audit/visual/template checks
- [`references/validation-checklist.md`](references/validation-checklist.md) — modern workflow validation checklist
- `references/mode-a.md`, `astro-build-guide.md`, `project-page-template.astro`, `mode-d-multisite.md` — task-specific execution details

The modern acceptance contract in `.claude/scripts/website-improve/` is the artifact
SSOT. If a historical reference conflicts with this v4.2.0 active workflow, prefer
this file plus the current generator/schema behavior and then repair the stale live
reference.
