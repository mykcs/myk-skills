# website-improve validation checklist — v4.2.0

Use this checklist to validate the **active workflow contract**, not historical
benchmark output.

## 1. Role independence

- [ ] Planner, Executor, and Verifier remain three distinct roles.
- [ ] Planner does not edit source files.
- [ ] Executor does not self-declare PASS.
- [ ] Verifier remains read-only and does not remediate its own findings.

## 2. Modern artifacts

- [ ] Planner uses `plan_json_gen.py --artifact-mode modern`.
- [ ] Plan records task-scoped site identifiers and completion criteria.
- [ ] Plan records verification targets.
- [ ] Plan records publication intent (`none|commit|push|pr|deploy|release`).
- [ ] Plan requires a session manifest for the active modern workflow.
- [ ] Executor uses `exec_log_gen.py --artifact-mode modern`.
- [ ] Executor records fresh verification runs and blockers.
- [ ] Executor records `publication_state` without owning publication as a side effect.
- [ ] Executor records intentional vs pre-existing changes in the session manifest.
- [ ] Verifier uses `verdict_json_gen.py --artifact-mode modern --acceptance-file ...`.

## 3. Publication separation

- [ ] Executor instructions do not automatically call `smart-autopush.sh`.
- [ ] Commit/push/PR/deploy/release occur only when the plan requests/applicably requires publication.
- [ ] Requested publication must be `VERIFIED` for final PASS; unresolved publication is `BLOCKED`.
- [ ] `NOT_REQUESTED` / `NOT_APPLICABLE` publication can pass when execution acceptance is complete.
- [ ] Recovery instructions do not use blanket `git add -A`, commit, or push as generic stall recovery.

## 4. Scope-relevant evidence

- [ ] Single-site tasks verify that site only unless a real shared dependency expands scope.
- [ ] Multi-site tasks verify every site actually named in scope.
- [ ] Historical four-site fan-out applies only when those four sites are in scope.
- [ ] Build/test/browser/curl/native evidence matches the changed layer.
- [ ] Deployed-layer evidence is required when deployed behavior/publication is part of the requested outcome.
- [ ] Missing/skipped/unavailable hosted checks are not described as PASS.

## 5. Build and dependency safety

- [ ] Package/lock/build-config edits regenerate/validate lockfiles as appropriate.
- [ ] Project-owned install/build/test commands pass after relevant config changes.
- [ ] Layout/interactive changes receive browser/visual evidence matching declared browser targets.
- [ ] Findings are based on actual evidence, not speculative “verify X” TODOs.

## 6. Session isolation and ownership

- [ ] Current repo/site target is resolved before writes.
- [ ] Intentional changes are separated from pre-existing changes.
- [ ] Multi-account Git publication verifies the intended owner/remote when relevant.
- [ ] A stale branch is not force-pushed over concurrent work merely to simplify merge history.

## 7. Memory promotion

- [ ] Case/decision-stream/ADR output is created only when current memory-promotion rules justify it.
- [ ] Historical benchmark/case text is not treated as active workflow SSOT.
- [ ] New active instructions do not require a case file for every task.

## 8. Failure handling

- [ ] Verifier FAIL returns concrete failed dimensions/evidence to Executor.
- [ ] A fresh independent Verifier checks remediation.
- [ ] The agent tries safe alternative routes before escalating ordinary tool failures.
- [ ] User intervention is reserved for genuine human-only boundaries or irreversible/high-risk approval.

## 9. Live-reference scan before release

Search active website-improve files (excluding historical benchmarks/cases) for stale
contract markers:

```bash
grep -R "smart-autopush\|--smart-push\|self_check_5_fields\|5 字段自检\|4 站 CI 全绿" \
  website-improve/SKILL.md website-improve/references website-improve/evals
```

Interpret matches semantically. An anti-pattern statement such as “do not run
smart-autopush automatically” is expected; an active instruction that makes it
mandatory is a regression.

Also confirm modern ownership markers exist:

```bash
grep -R -- "--artifact-mode modern\|--acceptance-file\|NOT_REQUESTED\|NOT_APPLICABLE\|VERIFIED\|BLOCKED" \
  website-improve/SKILL.md website-improve/references website-improve/evals
```

## 10. Repository validation

`myk-skills/scripts/ci_check.py` automatically discovers active skill eval suites.
Before merging a website-improve workflow change, run the repository-owned validation
entrypoint when an execution environment is available, or a narrowly justified focused
equivalent when the full environment is genuinely unavailable.

Do not create hosted-CI-only smoke PRs unless the repository's current merge contract
explicitly requires that provider evidence.
