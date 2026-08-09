# Agent Handoff — myk-skills harness / CI cleanup

Date: 2026-08-10
Repository: `mykcs/myk-skills`
Audience: future coding agents, repository maintenance agents, and CI/migration agents

## Executive state

The repository has completed the cleanup of the main historical CI / harness technical debt discussed in the 2026-08-09/10 maintenance thread.

Current architecture:

```text
GitHub repository / PRs
        |
        v
Cloudflare Workers Builds        <- routine PR + main validation
        |
        v
scripts/ci_check.py              <- validation policy SSOT
        ^
        |
manual GitHub Actions fallback   <- workflow_dispatch only
```

GitHub remains the source of truth for code/history/PRs. Cloudflare Workers Builds is the normal CI executor. GitHub Actions must not silently return to routine push/PR execution.

## Core invariants

### 1. Validation has one policy source

`scripts/ci_check.py` is the provider-neutral validation policy single source of truth.

Cloudflare and the manual GitHub Actions fallback invoke the same repository validation entrypoint. Do not copy validation rules into provider-specific workflow files or convenience scripts.

### 2. GitHub Actions is manual fallback only

`.github/workflows/rich-audit-ci.yml` is intentionally `workflow_dispatch`-only.

Do not restore automatic `push` / `pull_request` triggers merely because Cloudflare is temporarily inconvenient. If Cloudflare has an outage, use the manual fallback first; restoring automatic Actions is an explicit temporary rollback decision.

### 3. Exact latest-head Cloudflare gate

For any PR that triggers Workers Builds, merge only after Cloudflare succeeds for the **exact latest PR head commit**.

A green result for an older head is invalid after a new push. Agents must compare the Cloudflare-reported commit with the current PR head before merging.

### 4. Cloudflare is CI-only

Project / Worker name: `myk-skills-validation`.

Repository-owned configuration keeps:

- `workers_dev: false`
- `preview_urls: false`
- generated assets under `cloudflare-dist/`

Do not expose a public Worker route merely to inspect CI output.

### 5. Build watch paths and required checks are coupled

Repository desired-state Build watch policy:

```text
Include: *
Exclude: docs/*
```

The `docs/*` exclusion is intentionally narrow. Do **not** broaden it to `*.md` because active skills use Markdown (`SKILL.md` and references) as behavior-bearing input.

Because Cloudflare documents that a project skipped by Build watch paths does not generate a GitHub check run, **do not configure `myk-skills-validation` as a global required GitHub status check while any PR can be skipped by watch paths**.

Otherwise a docs-only PR can wait forever for a required check that Cloudflare intentionally never creates.

The detailed policy is in `docs/cloudflare-required-check-policy.md`.

If a future migration wants a GitHub-enforced required Cloudflare check, first remove every skip-capable watch-path exclusion, prove that docs-only and non-doc PRs both receive a check on their exact latest heads, then configure the Ruleset/branch protection and test that pending/failure actually blocks merge.

## Skill validator contract

The stale repository contributor guidance was corrected.

Current contract:

- every active top-level skill has a `SKILL.md`;
- `SKILL.md` starts with a YAML frontmatter block between `---` markers;
- documented frontmatter fields are optional;
- `description` is recommended for discoverability;
- repository-specific extension fields are allowed;
- malformed/missing frontmatter, malformed YAML, and invalid field types fail closed;
- the validator must not reintroduce a stale fixed allowlist of extension fields.

Canonical implementation:

- `skill-creator/scripts/quick_validate.py`
- root `scripts/quick_validate.py` delegates to the canonical implementation.

`CONTRIBUTING.md` is now aligned with this contract and Python 3.12 repository CI.

## Makefile cleanup

The old root Makefile was a second, stale CI policy. It hard-coded `rich-audit`, detector lists, Tri-Search checks, and a fixed test count.

That duplication was removed.

The root `Makefile` is now intentionally only a thin convenience wrapper around shared repository commands:

- `make check` -> `python3 scripts/ci_check.py`
- `make test` -> alias of `check`
- `make ci` -> alias of `check`
- `make cloudflare-build` -> repository Cloudflare build adapter
- `make clean` -> generated validation state only

Do not move validation semantics back into the Makefile.

## Verified runtime behavior

Two controlled smoke tests were used to distinguish desired-state documentation from actual Cloudflare behavior.

### Non-doc / host-self-evolve smoke

Temporary PR #103 changed only `host-self-evolve/.cloudflare-watch-smoke`.

Exact latest head:

`eacffda99ce5ec6969fa154d34d22f3a95782d59`

Observed result:

- Cloudflare Workers Builds started normally.
- `myk-skills-validation` completed successfully.
- PR was closed without merge; temporary smoke content did not reach `main`.

This proves that `host-self-evolve/**` is not stably excluded by the active watch-path behavior.

### Docs-only smoke

Temporary PR #105 changed only `docs/.cloudflare-watch-smoke.md`.

Exact latest head:

`9277b3537bf2ea5c54cf4a6c96e20ba221e12153`

Observed behavior:

- no Cloudflare PR check/comment appeared beyond the normal startup window seen on the paired non-doc smoke;
- this is consistent with Cloudflare's documented behavior for Build watch-path skips;
- PR was closed without merge; temporary smoke content did not reach `main`.

Treat this as behavioral evidence for the intended `docs/*` exclusion, while still remembering that Dashboard configuration is external runtime state.

### About PR #100's `Deployment skipped`

PR #100 (`host-self-evolve/**` changes) previously received a Cloudflare `Deployment skipped` result. Do not infer from that single historical event that `host-self-evolve/**` is excluded.

The controlled PR #103 smoke, kept open long enough for Cloudflare to process the latest head, triggered and passed successfully. Therefore the earlier skip should be treated as an isolated/cancellation/timing artifact unless future controlled tests prove otherwise.

## Completed cleanup PRs / evidence trail

### PR #98 — contributor contract cleanup

Purpose:

- remove stale required-frontmatter claims;
- align contributor docs with the canonical validator;
- align repository CI guidance with Python 3.12 and `scripts/ci_check.py`;
- add anti-regression tests.

Exact validated head before merge:

`6c84085489ea8b47309641fc131d0bd909c840ed`

Merge commit:

`aeddca6d1f22cf90dc6fcc1e3fcae98d6aaedd34`

### PR #99 — Makefile cleanup

Purpose:

- remove the stale `rich-audit` / Tri-Search / fixed-test-count policy from the Makefile;
- make the Makefile a thin wrapper around CI SSOT;
- add anti-regression tests.

Exact validated head before merge:

`b45324b2fbc7bd8a36cd9b2060b858681d0c41f4`

Merge commit:

`98ef3c94ee9af5c50d50e0514036c56b91d179b7`

### PR #102 — required-check policy

Purpose:

- resolve the conflict between Cloudflare Build watch-path skips and GitHub global required checks;
- codify exact-latest-head behavior;
- add policy regression coverage.

Exact validated head before merge:

`1a82c6c11f0470081cadf1b00413e3c8d55d0468`

Merge commit:

`f4a2be510d7a93303317420f43cfd50a82d7e293`

## Cloudflare repository configuration

Relevant source-controlled files:

- `.python-version` -> Python 3.12
- `requirements-ci.txt` -> pinned Python CI dependencies
- `package.json` -> Cloudflare check/build/deploy/preview commands
- `wrangler.jsonc` -> CI-only Worker configuration
- `scripts/cloudflare_build.py` -> runs repository validation, then emits metadata-minimized CI assets
- `docs/cloudflare-ci.md` -> architecture and Cloudflare operational guidance
- `docs/cloudflare-required-check-policy.md` -> GitHub required-check / watch-path policy

Current command model:

```text
cloudflare:check   -> python3 scripts/ci_check.py
cloudflare:build   -> install pinned CI deps + scripts/cloudflare_build.py
cloudflare:deploy  -> wrangler deploy
cloudflare:preview -> wrangler versions upload
```

## Agent behavior rules

When modifying this repository:

1. Start from current `main`; do not validate a stale base if `main` advanced concurrently.
2. Keep each architecture cleanup focused. If `main` moves during a high-risk change, rebuild/rebase onto current `main` before final validation.
3. For PRs that should build, require Cloudflare success on the exact latest head.
4. Never accept a Cloudflare success tied to an older PR head.
5. Do not restore routine GitHub Actions without an explicit rollback decision.
6. Do not create a second validation policy in Makefile, workflow YAML, or provider configuration.
7. Do not broaden Cloudflare docs exclusions to all Markdown.
8. Do not globally require the Cloudflare GitHub check while skip-capable Build watch paths exist.
9. Distinguish source-controlled desired state from live Cloudflare Dashboard / GitHub Ruleset state. A document is not proof of the external setting.
10. Use controlled temporary PRs for provider behavior tests, and close them without merge when the probe file is not product/repository content.

## Known observability boundary

The repository connector can observe GitHub code, PRs, comments, and Cloudflare's GitHub-visible bot results. It does not necessarily expose live Cloudflare Dashboard form values or GitHub Ruleset administration state.

Do not claim a runtime setting is verified unless it is proven by:

- authenticated provider API/UI access, or
- an observable controlled behavior test that directly exercises the setting.

## What is considered complete

The historical cleanup items from this thread are considered complete:

- contributor/frontmatter guidance drift: resolved;
- stale Makefile validation policy: resolved;
- Cloudflare required-check design ambiguity: resolved and documented;
- non-doc Cloudflare trigger behavior: controlled smoke passed;
- docs-only watch-path behavior: controlled smoke consistent with intended skip;
- automatic GitHub Actions regression: guarded; workflow remains manual fallback only.

Future work should treat these as established baselines unless new evidence proves the architecture should change.
