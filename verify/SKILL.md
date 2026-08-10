---
name: verify
description: Canonical cross-harness verification workflow for build/type/lint/test/security checks, targeted quality gates, adversarial review, and pass-2 finding validation.
version: "1.1.0"
author: "mykcs"
license: "MIT"
last_updated: "2026-08-10"
triggers:
  - verify
  - /verify
  - run verification
  - build check
  - pre-commit check
  - pre-flight check
  - quality gate
  - adversarial verify
  - pass-2 verify
---

# verify

This skill is the canonical verification **workflow** shared across harnesses. Harness-native commands may provide convenient syntax, but they should delegate here instead of maintaining a second verification policy.

Verification is evidence gathering. It must not silently become an implementation, remediation, commit, push, or merge workflow.

## Modes

- `full` (default): complete repository verification.
- `quick`: build + type checks only.
- `pre-commit`: commit-relevant checks for the current diff.
- `pre-pr`: full verification plus security-sensitive checks.
- `quality [path|.] [--fix] [--strict]`: targeted formatter/lint/type quality gate.
- `adversarial [scope]`: two independent read-only reviewers; both must pass.
- `pass2 [findings]`: adversarial validation of findings that already exist.

## Full verification sequence

Run repository-appropriate checks in this order, skipping only checks that genuinely do not exist for the project and reporting them as `N/A`:

1. **Build** — run the project build command. If build failure prevents later checks from being meaningful, report and stop.
2. **Types** — run the project type checker when available.
3. **Lint / format** — run configured lint and formatter checks.
4. **Tests** — run the relevant automated test suite and report pass/fail counts; report coverage only when the project actually produces it.
5. **Security / secret scan** — inspect the changed scope or repository with the project's configured scanner(s) when available; never invent scanner coverage.
6. **Debug-log audit** — inspect project-appropriate debug logging (`console.log`, equivalents) when that is a repository policy.
7. **Git state** — report uncommitted changes and the exact diff scope being verified.

Do not assume every repository is TypeScript/Node. Detect the project's real tooling from version-controlled configuration and scripts.

## Quick mode

`quick` runs only the minimum build/type checks that exist for the repository. If the project has no type checker, report `Types: N/A` rather than substituting an unrelated check.

## Pre-commit mode

Prefer checks scoped to the current uncommitted diff when the underlying tooling supports safe scoping. The result is a commit-readiness signal only; this mode does not create the commit.

## Pre-PR mode

Run the full suite plus security-sensitive checks relevant to the change: secrets, dependency/config risk, unsafe generated artifacts, and repository-specific release gates. Do not claim security coverage beyond the tools actually executed.

## Quality mode

`quality [path|.] [--fix] [--strict]`

1. Determine the target path (default `.`) and its actual language/tooling.
2. Run formatter checks for the target.
3. Run lint and type checks when available and safely scopeable.
4. `--fix` permits only the formatter/linter fixes those tools normally perform; it does not authorize unrelated remediation.
5. `--strict` treats warnings as failures when the underlying tooling supports warning thresholds.
6. Return a concise PASS/FAIL report with the exact tools and target used.

Quality mode replaces legacy standalone `quality-gate` semantics. Harness adapters should route that old intent here rather than duplicating the policy.

## Adversarial mode

`adversarial [file-or-glob | description]`

This is an independent verification gate, not an implementation loop.

1. Define the review scope from the supplied path/description or current diff.
2. Build an objective rubric covering correctness, security, error handling, completeness, internal consistency, regressions, and relevant domain-specific checks.
3. Run two independent read-only reviewer contexts. Prefer materially different reviewer capabilities when available, but do not hard-code provider/model names in the shared skill.
4. Require structured per-criterion evidence from both reviewers.
5. PASS only if both reviewers pass. Any fail returns consolidated findings.
6. Do not edit files, remediate, commit, push, merge, or retry after fixing inside the same verification run.

This mode replaces legacy standalone `santa-loop` verification semantics.

## Pass-2 mode

`pass2 [findings-or-review-source]`

This mode validates findings that already exist. It is not a first-pass code review.

For each finding:

1. Re-read the cited source with fresh context.
2. Reproduce the claimed failure mode when practical.
3. Check for false positives and alternative explanations.
4. Assess regression risk and whether the finding is actionable.
5. Return `real: true|false`, confidence, evidence, and a suggested action.
6. Default to `real: false` when evidence is insufficient.

When the `verifier-pass2` skill is available, it is the internal implementation for this mode. Do not chain an unbounded third/fourth review pass.

## Cross-harness ownership

- Shared verification semantics live here in `myk-skills` / `~/.agents/skills`.
- Claude slash commands such as `/verify` are UX adapters only.
- Codex may invoke the same skill directly or through its native skill routing; do not create a mirrored command tree merely for symmetry.
- Harness-native sandboxes, approval policies, hooks, and model routing remain owned by their harness and are not duplicated here.

## Output contract

Use this shape, adapting fields to `N/A` when a check does not exist:

```text
VERIFICATION: PASS | FAIL

Scope:    <path/diff/repository>
Build:    OK | FAIL | N/A
Types:    OK | <n> errors | N/A
Lint:     OK | <n> issues | N/A
Tests:    <passed>/<total> | FAIL | N/A
Security: OK | <n> findings | N/A
Logs:     OK | <n> findings | N/A

Ready for commit/PR: YES | NO | N/A
```

For `quality`, include target and whether `--fix` was used.
For `adversarial`, include both reviewer verdicts and agreement/disagreement.
For `pass2`, clearly separate confirmed findings from rejected/uncertain findings.

A PASS must be backed by checks actually executed or evidence actually inspected. Never infer PASS from the absence of output.
