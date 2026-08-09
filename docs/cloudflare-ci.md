# Cloudflare Workers Builds validation

`myk-skills` uses GitHub as the source of truth. Routine pull-request and `main` validation runs on Cloudflare Workers Builds. GitHub Actions is retained only as a manual fallback.

## Architecture

```text
GitHub branch / PR push
        |
        v
Cloudflare Workers Builds
        |
        +-- install pinned CI Python dependencies
        +-- validate active top-level SKILL.md files
        +-- run repository evals
        +-- run active-skill evals
        +-- preserve host-self-evolve compatibility checks
        |
        v
CI-only Worker version/deployment
(no workers.dev route, no preview URL)
        |
        v
Cloudflare GitHub check/comment
```

The Worker has no product, API, or backend responsibility. Static assets exist only because Workers Builds needs a deployable object after validation succeeds.

## Repository-owned commands

```bash
python3 -m pip install -r requirements-ci.txt
python3 scripts/ci_check.py
npm run cloudflare:build
npm run cloudflare:deploy
npm run cloudflare:preview
```

`scripts/ci_check.py` is the provider-neutral validation policy. Cloudflare and the manual-only GitHub Actions fallback call the same entrypoint rather than maintaining separate test definitions.

## Cloudflare project settings

The connected Worker project uses:

- Git repository: `mykcs/myk-skills`
- Worker/project name: `myk-skills-validation`
- production branch: `main`
- builds for non-production branches: enabled
- root directory: `/`
- build command: `npm run cloudflare:build`
- production deploy command: `npm run cloudflare:deploy`
- non-production deploy command: `npm run cloudflare:preview`

Keep the Cloudflare GitHub App repository scope as narrow as practical.

## Agent note: Pages 500-build quota vs Workers Builds

This section records a recurring operator concern so future agents do not make a destructive CI change based on the wrong Cloudflare quota.

### The concern

The operator was concerned that this repository might consume the Cloudflare Pages Free-plan allowance of 500 builds per month and asked whether the Cloudflare integration should be disabled or changed to avoid using that allowance.

### Current answer

As of 2026-08-09, this repository's CI project is **Cloudflare Workers Builds**, not Cloudflare Pages. These products have separate build limits:

- Cloudflare Pages Free: 500 builds per month.
- Cloudflare Workers Builds Free: 3,000 build-minutes per month.

Therefore, `myk-skills-validation` does **not** consume the Pages 500-build monthly allowance merely by running its Workers Builds validation. The relevant resource for this repository is Workers Builds build-minutes.

Official references:

- Workers Builds limits and pricing: <https://developers.cloudflare.com/workers/ci-cd/builds/limits-and-pricing/>
- Pages limits: <https://developers.cloudflare.com/pages/platform/limits/>

### Required agent behavior

For the specific concern about the Pages 500-build quota, the default action is **no action**. Do not disconnect `myk-skills-validation`, disable normal PR validation, or restore automatic GitHub Actions merely to protect the Pages build allowance.

Workers Builds currently provides the routine PR/main validation gate, while GitHub Actions is intentionally manual fallback only. Removing Workers Builds without first establishing an equivalent validated replacement would weaken the repository's safety gate.

If Workers Builds usage itself later becomes materially high, optimize that usage separately. Prefer Cloudflare **Build watch paths** to skip changes that cannot affect validation, rather than disabling CI globally. Cloudflare documents Workers Build watch paths here:

<https://developers.cloudflare.com/workers/ci-cd/builds/build-watch-paths/>

When adding exclusions, fail closed: do not exclude paths containing validation policy, active skills, tests/evals, dependency pins, Wrangler configuration, CI scripts, or other files whose changes should still be verified. Re-check current Cloudflare limits before making quota-driven decisions because plan limits can change over time.

## Public exposure safety

`wrangler.jsonc` intentionally sets:

```json
"workers_dev": false,
"preview_urls": false
```

Do not enable a public route merely to inspect CI output. Use Cloudflare build history plus the GitHub check/comment as evidence. Generated assets must not contain branch names, commit SHAs, repository URLs, account IDs, secrets, or build UUIDs.

## Migration status

Migration completed on 2026-08-09 after a real pull-request build succeeded for exact head commit `cc30e20515f4519b2c28fc67ca51730dda620680` on `myk-skills-validation`.

The steady-state policy is now:

1. GitHub remains the only code source and PR/history system.
2. Cloudflare Workers Builds runs routine validation for `main` and non-production branches.
3. `.github/workflows/rich-audit-ci.yml` is `workflow_dispatch`-only and is not part of normal push/PR execution.
4. Both Cloudflare and the manual GitHub fallback use `scripts/ci_check.py` as the validation SSOT.
5. If Cloudflare becomes unavailable, manually run the GitHub fallback; restore automatic GitHub triggers only as an explicit temporary rollback.

## Rollback

If Workers Builds becomes unavailable or unreliable, run the manual GitHub Actions fallback, which calls the same `scripts/ci_check.py` entrypoint. If temporary automatic GitHub-hosted CI is required, restore `pull_request` / `push: main` triggers without forking validation logic.
