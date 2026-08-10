# Mode D — Multi-site orchestration v4.2.0

Mode D coordinates website-improve across **two or more task-scoped sites**. It keeps
the useful fan-out/barrier pattern from the historical sync-all-sites workflow while
removing universal publication and four-site assumptions.

## Trigger

Use Mode D when the user explicitly asks for multi-site work or the resolved plan
contains 2+ sites, for example:

- “sync these three sites”
- “audit site-a + site-b”
- “fan out across all four historical sites”
- a shared change demonstrably affects multiple sites

The historical preset `mykcs,GDKVM,OSA,content2html` remains available for an explicit
full sweep. It is not the default scope for unrelated website requests.

## Planner

Planner resolves the exact site set and writes a modern plan:

```bash
python3 ~/.claude/scripts/website-improve/plan_json_gen.py \
  --artifact-mode modern \
  --audit-target "<multi-site requested outcome>" \
  --sub-modes "A,D" \
  --sites "site-a,site-b" \
  --expected-wall-clock <minutes> \
  --completion "<task-scoped criteria CSV>" \
  --verification-targets "<build,browser,ci,curl,... as applicable>" \
  --publication-mode "<none|commit|push|pr|deploy|release>" \
  --session-manifest-required \
  --out plan.json
```

Pre-flight declares assumptions, ownership risks, and publication intent, then routine
reversible execution may continue autonomously. Do not stop for a ceremonial user
“OK” unless a genuine human-only/high-risk boundary exists.

## Phase 1 — Target isolation

For each scoped site:

- resolve the actual repository/path/owner;
- inspect current branch/worktree state;
- distinguish pre-existing changes from this task;
- do not assume historical local paths or GitHub owners are still correct;
- do not require a clean worktree by destroying/stashing unrelated user work.

If a site is inaccessible, record a blocker and continue other independent safe work
where possible.

## Phase 2 — Parallel read-only audit

One audit lane per scoped site may run in parallel. Each finding must contain concrete
first-party evidence. “Verify X”, “check Y”, or “should audit Z” is not a finding.

Useful audit result shape:

```json
{
  "site": "site-a",
  "issues": [
    {
      "severity": "P1",
      "type": "a11y",
      "file": "src/pages/index.astro",
      "problem": "navigation label missing",
      "evidence": "exact source/runtime evidence"
    }
  ]
}
```

Do not edit during the audit lane.

## Phase 3 — Executor fan-out

After findings are accepted into scope, assign one Executor lane per site. Executor:

1. reads the shared modern plan;
2. edits only accepted issues/improvements for that site;
3. runs the site's planned verification targets;
4. records blockers instead of silently deferring failures;
5. records the session manifest;
6. writes/merges evidence into the modern executor handoff.

Executor does **not** automatically commit, push, open a PR, or deploy. Multi-site
parallelism does not change publication ownership.

Package/lock/build configuration edits must still pass the project-owned clean
install/build checks described in `4-site-ci-gate.md`.

## Barrier

Wait until every scoped Executor lane is in a terminal evidence state:

- `PASS` execution evidence; or
- explicit `BLOCKED` / `INCOMPLETE` with reason.

Do not call the multi-site execution complete while one scoped site is silently
pending.

## Publication

If `publication_mode = none`, no site is committed/pushed merely because Mode D ran.

If publication is requested:

1. establish execution acceptance first;
2. route each verified site through its canonical Git/deploy lifecycle;
3. preserve owner/repository isolation;
4. avoid force-pushing stale/diverged branches when clean replay/rebase-safe recovery is available;
5. record final publication as `VERIFIED` or `BLOCKED` per scoped site/overall plan.

Do not use a generic `autopush.sh` or `smart-autopush.sh` takeover as the Mode D
publication mechanism.

## Phase 4 — Independent verification

Verifier checks **the sites in the plan**, not an unrelated fixed set.

Examples:

- two-site task → both sites require planned evidence;
- historical four-site full sweep → all four are in scope and must pass;
- a site with requested deployment → deployed evidence is required;
- source-only no-publication task → do not fabricate hosted CI/deploy evidence.

Build/CI/browser/curl evidence follows `4-site-ci-gate.md` and the current repository
contracts.

Final Acceptance uses:

```json
{
  "scope": "PASS|FAIL",
  "execution_evidence": "PASS|FAIL|BLOCKED|INCOMPLETE",
  "blockers": "CLEAR|BLOCKED",
  "publication": "NOT_REQUESTED|NOT_APPLICABLE|VERIFIED|BLOCKED",
  "ownership": "PASS|FAIL|NOT_APPLICABLE",
  "session_manifest": "PASS|FAIL"
}
```

Then `verdict_json_gen.py --artifact-mode modern --acceptance-file ...` derives the
verdict.

## Agent-output recovery

Do not make a particular final-message JSON wrapper a reason to discard valid work.
If an agent response is malformed:

- inspect the actual repository/artifacts/tool output;
- request/reconstruct the missing structured handoff;
- rerun affected verification;
- preserve independent Verifier acceptance.

Formatting recovery does not grant permission to commit/push.

## User escalation

Do not send ordinary multi-site conflicts back to the user as an information-shuttle
step. Continue autonomously across safe independent sites and switch tools/agents as
needed.

Escalate only for a genuine human-only boundary, unavailable external control plane,
or irreversible/high-risk decision.

## Memory

A multi-site case file or ADR is created only if the incident meets the current memory
promotion threshold. It is not a mandatory Phase 4 output.

## Permanent anti-patterns

- ❌ defaulting every website task to the historical four sites
- ❌ waiting for user “OK” before routine reversible fan-out
- ❌ fix agents committing/pushing as part of execution
- ❌ fixed four-site CI for a two-site task
- ❌ mandatory case file after every fan-out
- ❌ dropping a scoped site without recording it as blocked/incomplete
- ❌ Verifier editing a failed site itself
