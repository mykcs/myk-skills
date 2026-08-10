# website-improve modern acceptance closure — 2026-08-10

> Agent-facing operational snapshot. Refresh current `main`, PRs, and provider state before acting. Current code/tests are the live SSOT when they disagree with this note.

## Landed result

PR #107 migrated the active `website-improve` skill from legacy v4.1.1 completion semantics to evidence-first v4.2.0.

- merge commit: `b3b7bb03f913f796a12381045dcab157d60b7e69`
- active skill: `website-improve/SKILL.md`
- regression: `website-improve/evals/test_modern_acceptance_workflow.py`
- Cloudflare exact-head validation: `4f2ecf4c8e0f6d7658e4d571b9c74ed9d97dd7e5` → `Deployment successful`

Post-merge reads confirmed:

- `SKILL.md` is v4.2.0 on `main`;
- the modern regression is active on `main` and does not retain the temporary diagnostic `@unittest.skip`.

## Active architecture

Preserve these boundaries:

1. Planner, Executor, and Verifier are independent roles.
2. Verifier is read-only and does not remediate/commit/push/deploy.
3. New active artifacts use `--artifact-mode modern`.
4. Verifier uses `--acceptance-file`; caller-provided verdicts cannot override evidence.
5. Execution Acceptance is separate from Publication Acceptance.
6. Publication states are `NOT_REQUESTED`, `NOT_APPLICABLE`, `VERIFIED`, `BLOCKED`.
7. Executor does not automatically `smart-autopush`, commit, push, open PRs, or deploy.
8. Recovery restores execution/verification lanes but does not take over publication.
9. Durable case/ADR/decision-stream output is conditional memory promotion, not universal per-task ceremony.

## Task-scoped site and CI semantics

The historical four-site set (`mykcs`, `GDKVM`, `OSA`, `content2html`) remains a supported explicit multi-site preset, not the definition of every website task.

- single `basemodel` task → verify `basemodel` and any genuine shared dependencies;
- two-site task → verify those two sites;
- explicit historical four-site sweep → verify all four;
- hosted CI is evidence only when the current repository/publication contract uses it;
- missing/skipped/stale/unavailable CI is never PASS;
- deployed-layer checks are required when the requested outcome depends on deployed behavior.

The `.claude` artifact layer was also corrected so modern `plan.json` can contain arbitrary non-empty task-scoped site identifiers while retaining the historical field name `4_sites` for compatibility. That landed in `.claude` PR #226 (`4f80f7f9290f45eaf241fe6414f937c9672a9969`).

## Live references migrated

The v4.2 migration updated the active contract across:

- `website-improve/SKILL.md`
- `references/3-role-workflow.md`
- `references/4-site-ci-gate.md`
- `references/per-workflow-framework.md`
- `references/orchestrator-recovery.md`
- `references/validation-checklist.md`
- `references/mode-a.md`
- `references/mode-d-multisite.md`
- `references/triggers.md`
- `references/quality-checks.md`

`scan-checklist.md`, benchmark reports, evolution history, and historical cases may still name older providers/four-site/smart-push behavior. Treat them as detailed/historical material; active routing and acceptance come from v4.2.0 plus current generator/schema behavior.

## Regression lesson: test semantics, not prose

During migration, new tests initially failed because they asserted exact natural-language wording or broad substring absence. A diagnostic head with only the new regression skipped passed the full Cloudflare gate, proving the production migration itself was healthy.

The regression was then rewritten to assert stable architecture markers instead of banning words across explanatory prose. This repeats an earlier harness lesson: documentation may legitimately mention retired/forbidden behavior; tests should distinguish active semantics from comments/history/examples.

Do not reintroduce broad raw-substring bans over Markdown as a safety contract unless the literal text itself is the behavior being tested.

## Stale PR cleanup completed in the same audit

Clearly superseded/risky old PRs were closed rather than left as future merge traps:

- `.claude` #140 — obsolete harness-audit soft retirement;
- `.claude` #136 — stale settings/doctor branch based on old staging base;
- `.claude` #105 — old universal 5+1/four-site completion assumptions;
- `myk-skills` #48 — old per-skill frontmatter fix superseded by repository-wide active-skill validation;
- `myk-skills` #71 — stale 708-file skill retirement/move based on old doctor snapshot;
- `myk-skills` #37 — old paper-into-notion v3.x branch superseded by current v4.7.

Other old PRs were not closed merely to reduce the count when they may still contain independent work. Review them separately against current `main` before deciding.

## Compatibility window

Do not remove the legacy website-improve generator mode yet.

- `.claude/scripts/website-improve/test_3role_e2e.sh` remains a legacy compatibility fixture.
- Legacy artifact fields remain accepted for transitional callers.
- Historical cases/decision streams are not live callers.

Remove compatibility only after a fresh live-consumer scan proves no active caller depends on it.

## Safe next work

There is no remaining required “modern verdict → active skill migration” dependency; that chain is complete.

Future work should be driven by a concrete live defect or a verified live legacy consumer, not by the old handoff sequence. Before any new cleanup:

1. refresh both `.claude/main` and `myk-skills/main`;
2. search active callers, excluding historical cases/benchmarks;
3. preserve the three-role and conditional-publication boundaries;
4. run the repository's current validation contract for the exact head;
5. never revive stale PRs/aliases simply because older notes mention them.
