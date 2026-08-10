# Website-improve 3-role workflow — v4.2.0

This reference defines the active Planner → Executor → Verifier handoff for
`website-improve`. The three roles are independent and exchange JSON artifacts.

## Role boundaries

| Role | Owns | Must not own |
| --- | --- | --- |
| **Planner** | scope, assumptions, risk, completion criteria, verification targets, publication intent | source edits, final verdict |
| **Executor** | scoped edits, fresh first-party verification, blockers, session manifest | self-approval, automatic publication |
| **Verifier** | independent acceptance and evidence-derived PASS/FAIL | remediation, commits, pushes, deploys |

A single subagent must not impersonate all three roles.

## Planner → `plan.json`

Use modern mode for new active runs:

```bash
python3 ~/.claude/scripts/website-improve/plan_json_gen.py \
  --artifact-mode modern \
  --audit-target "<requested outcome>" \
  --sub-modes "<A,B,C,D as applicable>" \
  --sites "<task-scoped site identifiers>" \
  --expected-wall-clock <minutes> \
  --completion "<task-scoped criteria CSV>" \
  --verification-targets "<build,test,browser,curl,security,...>" \
  --publication-mode "<none|commit|push|pr|deploy|release>" \
  --session-manifest-required \
  --pre-flight "<assumptions/risk declaration>" \
  --out plan.json
```

The artifact field `4_sites` retains its historical name for compatibility, but the
modern schema accepts arbitrary task-scoped site identifiers. Do not force an
unrelated site into the historical four-site preset.

Planner rules:

- criteria describe the requested outcome, not fixed Git ceremony;
- `publication-mode none` is correct when publication is not requested;
- multi-site fan-out contains exactly the sites in scope;
- Planner does not edit files or manufacture evidence;
- routine reversible work proceeds autonomously after the declaration unless a real human-only boundary exists.

## Executor → `exec-log.json`

Executor reads the plan, edits only the intended scope, gathers fresh evidence, and
records blockers plus session isolation.

Example supporting files:

`verification.json`:

```json
[
  {
    "kind": "build",
    "status": "PASS",
    "command": "npm run build",
    "target": "basemodel",
    "evidence": "exit 0"
  }
]
```

`blockers.json`:

```json
[]
```

`session-manifest.json`:

```json
{
  "intentional_changes": ["src/pages/guide.astro"],
  "pre_existing_changes": []
}
```

Generate the modern executor handoff:

```bash
python3 ~/.claude/scripts/website-improve/exec_log_gen.py \
  --artifact-mode modern \
  --plan plan.json \
  --files-changed "src/pages/guide.astro:12:3" \
  --verification-file verification.json \
  --blockers-file blockers.json \
  --publication-state NOT_REQUESTED \
  --session-manifest-file session-manifest.json \
  --out exec-log.json
```

Modern Executor rules:

- `git_commits`, `smart_push_status`, and `decision_stream_entries` are legacy compatibility fields and are not synthesized;
- do not run `smart-autopush.sh` as an execution side effect;
- do not commit/push/deploy unless a separate requested publication lifecycle owns it;
- modification of package/lock/build config requires the project-owned install/build verification;
- blockers remain explicit instead of becoming hidden deferred work.

## Publication between execution and final acceptance

Publication is a separate lifecycle. If the plan requests `commit`, `push`, `pr`,
`deploy`, or `release`, hand the already execution-verified work to the repository's
canonical publication path.

Examples:

- `.claude` PR publication → canonical `/pr` after commits already exist;
- a Cloudflare-hosted site → use its current Git/Cloudflare publication contract;
- no requested publication → remain `NOT_REQUESTED` or `NOT_APPLICABLE`.

A requested publication that cannot be verified must become `BLOCKED`; it may not be
silently omitted to get a PASS.

## Verifier → Acceptance → `verdict.json`

Verifier independently converts the evidence into the modern Acceptance object.
Example successful no-publication task:

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

Then derive the final verdict:

```bash
python3 ~/.claude/scripts/website-improve/verdict_json_gen.py \
  --artifact-mode modern \
  --acceptance-file acceptance.json \
  --out verdict.json
```

PASS requires:

- scope `PASS`;
- execution evidence `PASS`;
- blockers `CLEAR`;
- publication `NOT_REQUESTED`, `NOT_APPLICABLE`, or `VERIFIED`;
- ownership `PASS` or `NOT_APPLICABLE`;
- session manifest `PASS`.

`publication = BLOCKED`, incomplete execution, hidden blockers, ownership failure, or
manifest failure all fail closed.

`--verdict` is only a compatibility assertion. It cannot turn failing evidence into
PASS.

## Scope-relevant verification

The historical four-site CI/curl workflow is still valid when all four historical
sites are actually in scope. It is not a universal requirement.

Examples:

- single `basemodel` visual improvement → build/browser evidence for `basemodel`;
- two-site sync → evidence for those two sites;
- explicit historical four-site sweep → verify all four;
- deployed header/robots/sitemap fix → add deployed-layer curl evidence;
- source-only non-publication task → do not invent deployed publication evidence.

See `4-site-ci-gate.md` for the detailed contextual rules.

## Failure and retry

If Verifier returns FAIL:

1. return the concrete failed acceptance dimensions and evidence to a fresh Executor pass;
2. repair/re-run the affected evidence;
3. invoke a fresh independent Verifier.

Do not make “two failures” itself a reason to stop and ask the user. Keep expanding the
solution space unless a genuine human-only boundary, irreversible/high-risk decision,
or unavailable external control plane requires the user.

## Memory promotion

Decision streams, cases, and ADRs are conditional durable-memory outputs. They are not
required merely because a website-improve run happened.

## Compatibility window

Legacy generator mode and historical fixtures remain supported while live callers are
migrated. Historical benchmark/case text may contain four-site/smart-push terminology;
it does not override this active workflow.
