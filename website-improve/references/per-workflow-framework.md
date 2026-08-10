# PER workflow framework — evidence-first v2

PER means **Plan → Execute → Verify**. It is a general workflow pattern for complex
skills that benefit from independent acceptance.

## 1. Roles

| Role | Owns | Does not own |
| --- | --- | --- |
| **Planner** | intent, scope, assumptions, risks, acceptance criteria, verification targets, publication intent | implementation, final PASS |
| **Executor** | scoped implementation, fresh first-party evidence, blockers, session manifest | self-approval, implicit publication |
| **Verifier** | independent evidence review and PASS/FAIL | remediation, publication side effects |

The roles exchange artifacts. A single agent must not silently collapse all three
roles for workflows that declare PER independence.

## 2. Execution acceptance vs publication acceptance

Execution completion is not the same thing as Git/deployment publication.

### Execution Acceptance

A task should prove:

- requested scope is satisfied;
- execution evidence is fresh and relevant;
- blockers are visible;
- target/ownership is correct where applicable;
- intentional changes are isolated from pre-existing changes.

### Publication Acceptance

Commit/push/PR/deploy/release evidence is required only when publication is requested
or necessary for the requested outcome.

Allowed publication states:

- `NOT_REQUESTED`
- `NOT_APPLICABLE`
- `VERIFIED`
- `BLOCKED`

Do not manufacture a commit, push, CI run, deployment, or memory artifact just to fill
a universal acceptance form.

## 3. Planner artifact

A modern website-improve plan includes task-scoped criteria plus explicit publication
intent and verification targets.

Illustrative shape:

```json
{
  "audit_target": "improve basemodel guide layout",
  "sub_modes": ["A"],
  "4_sites": ["basemodel"],
  "risk_decisions": [],
  "expected_wall_clock_min": 20,
  "completion_criteria": [
    "build passes",
    "desktop and mobile layout evidence shows no overlap"
  ],
  "pre_flight_declaration": "single-site visual improvement",
  "publication_requested": false,
  "publication_mode": "none",
  "verification_targets": ["build", "browser"],
  "session_manifest_required": true
}
```

`4_sites` is a historical compatibility field name; modern values are task-scoped
site identifiers rather than a fixed four-site enum.

## 4. Executor artifact

A modern executor handoff records work and evidence, not mandatory publication:

```json
{
  "plan_hash": "sha256:<...>",
  "files_changed": [
    {"path": "src/pages/guide.astro", "lines_added": 12, "lines_removed": 3}
  ],
  "verification_runs": [
    {
      "kind": "build",
      "status": "PASS",
      "command": "npm run build",
      "evidence": "exit 0"
    }
  ],
  "blockers": [],
  "publication_state": "NOT_REQUESTED",
  "session_manifest": {
    "intentional_changes": ["src/pages/guide.astro"],
    "pre_existing_changes": []
  }
}
```

Legacy `git_commits`, `smart_push_status`, and `decision_stream_entries` may remain
accepted by compatibility schemas, but modern active workflows do not synthesize them.

## 5. Verifier artifact

Verifier expresses the final acceptance dimensions:

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

A final verdict is derived from evidence; a caller-provided PASS must never override a
failed dimension.

## 6. Publication lifecycle

When publication is requested:

1. execution acceptance is established first;
2. the orchestrator routes the verified change to the repository's canonical Git or deploy lifecycle;
3. requested publication is evidenced as `VERIFIED` or `BLOCKED`;
4. final Verifier acceptance includes that publication state.

Executor ownership of implementation does not imply ownership of `git add`, commit,
push, PR creation, deployment, or release.

## 7. Failure handling

Verifier FAIL returns concrete failed dimensions and reproduction evidence to a fresh
Executor pass. The agent should keep trying alternative safe approaches while the
problem is agent-resolvable.

Ask the user only when a genuine human-only boundary exists, such as authorization,
2FA/CAPTCHA, physical-device action, irreversible/high-risk approval, or a control
plane inaccessible to every available tool.

A fixed retry count by itself is not a reason to offload the problem to the user.

## 8. Recovery

Agent/process recovery preserves work product and restores a valid execution lane. It
must not automatically publish stalled work.

- inspect current artifacts/worktree;
- distinguish intentional and pre-existing changes;
- rerun affected evidence;
- respawn/reassign Executor as needed;
- enter publication only if the plan requested it.

## 9. Memory promotion

Decision streams, case files, and ADRs are durable-memory outputs governed by memory
promotion rules. They are conditional, not mandatory for every PER task.

## 10. Evidence quality

Evidence must match the claim:

- source/build claims → local/project-owned checks;
- browser/UI claims → browser/runtime evidence;
- deployed claims → deployed/live evidence;
- native-platform claims → native-platform evidence;
- publication claims → current publication target evidence.

Unavailable, skipped, stale, or unrelated evidence is not PASS.

## 11. Website-improve mapping

| Role | website-improve v4.2.0 |
| --- | --- |
| Planner | modern plan, task-scoped sites/criteria, verification targets, publication intent |
| Executor | audit/fix + fresh evidence + blockers + session manifest |
| Verifier | modern Acceptance + evidence-derived verdict |

Historical four-site fan-out remains a supported scope when requested; it is no longer
the definition of every website task.
