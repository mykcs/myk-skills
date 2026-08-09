# Cloudflare Workers Builds validation

`myk-skills` uses GitHub as the source of truth. The target CI architecture is Cloudflare Workers Builds for routine pull-request and `main` validation, with GitHub Actions retained only as a manual fallback after Cloudflare has been proven on the latest PR head.

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

`scripts/ci_check.py` is the provider-neutral validation policy. Cloudflare and the eventual manual-only GitHub Actions fallback must call the same entrypoint rather than maintaining separate test definitions.

## Intended Cloudflare project settings

Create/connect a Worker project with:

- Git repository: `mykcs/myk-skills`
- Worker/project name: `myk-skills-validation`
- production branch: `main`
- builds for non-production branches: enabled
- root directory: `/`
- build command: `npm run cloudflare:build`
- production deploy command: `npm run cloudflare:deploy`
- non-production deploy command: `npm run cloudflare:preview`

Keep the Cloudflare GitHub App repository scope as narrow as practical.

## Public exposure safety

`wrangler.jsonc` intentionally sets:

```json
"workers_dev": false,
"preview_urls": false
```

Do not enable a public route merely to inspect CI output. Use Cloudflare build history plus the GitHub check/comment as evidence. Generated assets must not contain branch names, commit SHAs, repository URLs, account IDs, secrets, or build UUIDs.

## Migration gate

Do **not** disable the existing automatic GitHub workflow merely because these files exist.

The migration is complete only after all of the following are true:

1. the Cloudflare Worker is connected to `mykcs/myk-skills`;
2. non-production branch builds are enabled;
3. a pull request's latest head commit receives a successful Cloudflare build/check;
4. the exact observed Cloudflare check can be used as the merge gate where repository rules support it.

Only then should the existing GitHub Actions workflow be changed to `workflow_dispatch`-only fallback. This avoids a CI coverage gap during migration.

## Rollback

If Workers Builds becomes unavailable or unreliable, the manual GitHub Actions fallback can call the same `scripts/ci_check.py` entrypoint. If temporary automatic GitHub-hosted CI is required, restore `pull_request` / `push: main` triggers without forking validation logic.
