---
name: website-improve
description: |
  Evidence-first website improvement workflow (v4.3.0). Uses three independent
  Planner → Executor → Verifier roles for full runs, plus a proportional situational
  lens that makes every human-facing web change consider semantic HTML, mental models,
  information density, and reading flow without forcing heavyweight ceremony on tiny edits.
when_to_use: |
  Use for website audits, visual/UX improvements, Astro/site modernization,
  project pages, and multi-site fan-out. A tiny rendered-content edit still applies
  the shared web-expression lens, but it does not by itself force a full three-role
  run. Do not use the full workflow for unrelated backend bugs or documentation-only
  edits where the workflow overhead adds no value.
metadata:
  version: "4.3.0"
  author: mykcs
  category: web-development
  tags: [website, improve, multi-site, astro, workflow, semantic-html, information-architecture]
  changelog: |
    4.3.0 (2026-08-12): add the human-thinking web-expression situational lens.
    Every rendered web change is classified as APPLY_LIGHT, APPLY_FULL, or
    NOT_APPLICABLE; full website-improve runs retain independent three-role acceptance.
    4.2.0 (2026-08-10): migrate the active workflow to evidence-first modern
    acceptance. Preserve three independent roles; separate execution acceptance
    from conditional publication; remove automatic smart-push, universal four-site
    CI, fixed Git five-field completion, and mandatory per-task memory artifacts.
    4.1.1 (2026-07-25): progressive-disclosure reference split.
license: "MIT"
last_updated: "2026-08-12"
---

# website-improve v4.3.0

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

## 0. Situational human-thinking web-expression lens

Read [`references/human-thinking-web-expression.md`](references/human-thinking-web-expression.md)
whenever a task can change what a person sees or understands in a rendered webpage.
This includes a small request such as adding one fact, item, label, status, action, or
content block.

Classify the task before editing:

- `APPLY_LIGHT` — a small local rendered change. Decide the reader goal, mental
  relationship, semantic HTML form, density layer, flow impact, and proportional
  evidence. This does not by itself force plan/exec/verdict artifacts.
- `APPLY_FULL` — a route, feature, workflow, broad content journey, comparison,
  navigation system, or reusable visual grammar changes materially. Select the full
  project-approved workflow; when that is `website-improve`, all three roles run.
- `NOT_APPLICABLE` — no rendered human-facing consequence. State the reason and do
  not manufacture UI scope.

When this full skill is selected, Planner must encode the expression decision in the
pre-flight/completion/verification targets, Executor must implement it using semantic
HTML and the project design system, and Verifier must inspect the actual changed layer.
A decorative card grid, provider `READY` badge, or existing component file is not
reader acceptance.

## 1. Core acceptance model

Completion has two separate layers.

### Execution Acceptance

Every full run must prove:

1. **scope** — the requested website change/audit scope is satisfied;
2. **execution evidence** — fresh first-party evidence relevant to the change exists;
3. **blockers** — unresolved blockers are visible, never hidden;
4. **ownership/target** — the correct repo/site/account was operated on when applicable;
5. **session manifest** — intentional changes are separated from pre-existing changes;
6. **web expression** — reader goal, relationship, semantic form, density/flow, and
   changed-layer evidence are explicit when the task affects a rendered surface.

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

Use [`references/triggers.md`](references/triggers.md) for long-tail routing cues. The
web-expression disposition is evaluated before mode selection, but it never silently
adds sites or publication work.

## 3. Pre-flight and Planner

Planner owns assumptions, scope, risk decisions, verification targets, publication
intent, and the `APPLY_FULL` web-expression decision. It may proceed autonomously after
declaring material assumptions unless a genuine human-only boundary exists.

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
  --pre-flight "<assumptions, risk, reader goal, mental relationship, semantic HTML, density/flow decision>" \
  --out plan.json
```

Rules:

- `--sites` follows the actual task scope; it is not restricted to the historical four sites.
- `--completion` describes the requested result, not fixed Git/memory ceremony.
- `--publication-mode none` is correct when the user did not request publication.
- Planner must not edit source files or fabricate verification results.
- For `APPLY_FULL`, verification targets must prove the actual relationship/density
  outcome: source semantics alone are insufficient when layout or interaction matters.

## 4. Executor

Executor owns code/content changes and fresh execution evidence.

Executor must:

- read `plan.json` before editing;
- verify the repository/site target before writes;
- preserve pre-existing unrelated changes;
- make only scope-justified edits;
- use semantic HTML to encode order, hierarchy, comparison, evidence, state,
  topology, or decision structure when those relationships carry the meaning;
- preserve a coherent density ladder and surrounding page journey rather than
  optimizing one isolated block;
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

For semantic content changes, inspect heading order, native element choice, static
reading order, mobile order, local actions, evidence labels, and optional-depth
boundaries. JavaScript enhancement must not be the only source of primary meaning.

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

For concurrent branches/PRs or build-quota work, also load
[`references/parallel-agent-delivery.md`](references/parallel-agent-delivery.md).
Development may be parallel; publication is serialized through the project-approved
integration/release head.

## 6. Verifier

Verifier is independent and read-only. It inspects the plan, executor evidence,
current target state, and publication evidence when publication was requested.

For rendered surfaces, Verifier also checks that the chosen HTML actually communicates
the intended relationship, that density/flow remains coherent across affected routes
and states, and that evidence comes from the changed layer rather than a nearby proxy.

Verifier creates an Acceptance object such as:

```json
{
  "scope": "PASS",
  "execution_evidence": "PASS",
  "blockers": "CLEAR",
  "publication": "NOT_REQUESTED",
  "ownership": "PASS",
  "session_manifest": "PASS",
  "web_expression": "PASS"
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
rules. The important v4.3.0 interpretation is:

- CI belongs to acceptance only when CI is relevant to the scoped repo/publication contract;
- historical four-site CI fan-out applies only when those four sites are actually in scope;
- deployed-layer `curl` applies when deployed behavior must be proven;
- local source existence is not evidence that deployed behavior works;
- a skipped/missing/unavailable check is never silently converted to PASS;
- a provider deployment state is not a substitute for semantic/visual/interaction
  inspection when the requested outcome depends on those layers.

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

The owner preference in `human-thinking-web-expression.md` is already durable shared
knowledge. Projects should link it and add only local constraints; do not copy the full
policy into every repository or per-task memory file.

Historical case/benchmark files may describe legacy smart-push/four-site behavior;
they are historical evidence and do not override this active v4.3.0 skill.

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
- ❌ every small rendered edit is forced through heavyweight workflow ceremony
- ❌ “use HTML expressively” becomes decoration without semantic structure
- ❌ a dense card wall substitutes for hierarchy, sequence, comparison, evidence, or flow

## 11. References

Load only what the task needs:

- [`references/human-thinking-web-expression.md`](references/human-thinking-web-expression.md) — situational owner lens for semantic HTML, mental relationships, density, flow, and proportional evidence
- [`references/triggers.md`](references/triggers.md) — long-tail routing and expression disposition
- [`references/3-role-workflow.md`](references/3-role-workflow.md) — modern artifact handoff and role boundaries
- [`references/4-site-ci-gate.md`](references/4-site-ci-gate.md) — scope-relevant CI/deployed verification
- [`references/per-workflow-framework.md`](references/per-workflow-framework.md) — generic evidence-first PER framework
- [`references/orchestrator-recovery.md`](references/orchestrator-recovery.md) — fail-closed stall/recovery behavior
- [`references/quality-checks.md`](references/quality-checks.md) — audit/visual/template checks
- [`references/validation-checklist.md`](references/validation-checklist.md) — modern workflow validation checklist
- [`references/deployment-platforms.md`](references/deployment-platforms.md) — provider-role-first hosting decisions
- [`references/parallel-agent-delivery.md`](references/parallel-agent-delivery.md) — parallel worker PRs, serialized integration, and hosted-build budgets
- `references/mode-a.md`, `astro-build-guide.md`, `project-page-template.astro`, `mode-d-multisite.md` — task-specific execution details

The modern acceptance contract in `.claude/scripts/website-improve/` is the artifact
SSOT for full runs. The human-thinking web-expression lens is the semantic source for
all rendered changes. If a historical reference conflicts with this v4.3.0 active
workflow, prefer this file plus current generator/schema behavior and then repair the
stale live reference.
