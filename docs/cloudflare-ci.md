# Cloudflare Workers Builds secondary validation

`myk-skills` uses GitHub as the source of truth and GitHub Actions as the canonical routine CI / merge gate. Cloudflare Workers Builds is retained temporarily as non-blocking secondary evidence during the cutover.

## Current architecture

```text
GitHub PR / main push
        |
        +--> GitHub Actions: Repository validation  [required]
        |       |
        |       +--> scripts/ci_check.py             [validation SSOT]
        |
        +--> Cloudflare Workers Builds              [secondary / optional]
                |
                +--> scripts/ci_check.py
```

Provider configuration must not duplicate validation logic. `scripts/ci_check.py` owns the repository policy.

## Repository-owned commands

```bash
python3 -m pip install -r requirements-ci.txt
python3 scripts/ci_check.py
npm run cloudflare:build
npm run cloudflare:deploy
npm run cloudflare:preview
```

## GitHub gate

`.github/workflows/rich-audit-ci.yml` runs on pull requests, pushes to `main`, and manual dispatch. The stable required check name is `Repository validation`. GitHub Actions references are pinned to immutable commit SHAs and maintained through GitHub-Actions Dependabot updates.

For merge-gate policy, see `docs/cloudflare-required-check-policy.md`.

## Retained Cloudflare project

The existing secondary project is:

- Git repository: `mykcs/myk-skills`
- Worker/project name: `myk-skills-validation`
- production branch: `main`
- root directory: `/`
- build command: `npm run cloudflare:build`
- production deploy command: `npm run cloudflare:deploy`
- non-production deploy command: `npm run cloudflare:preview`

The Worker is CI-only. `wrangler.jsonc` must keep `workers_dev=false` and `preview_urls=false`; do not create a public route merely to inspect CI output.

## Build watch paths

Cloudflare may keep the conservative secondary optimization:

```text
Include paths: *
Exclude paths: docs/*
```

This skip policy is exactly why Cloudflare must not be a global required GitHub check: a docs-only PR may legitimately have no Cloudflare status. GitHub's `Repository validation` still runs for every PR and is the actual required gate.

Do not broaden the Cloudflare exclusion to `*.md`: active skills use Markdown and can be behavior-bearing.

## Evidence boundary

GitHub repository state proves the source workflow and ruleset. Cloudflare Dashboard/API state is a separate provider plane. A document saying Cloudflare is configured does not prove the live provider setting.

## Transition history

Cloudflare became routine validation on 2026-08-09, when it solved the then-current hosted-CI requirement. On 2026-09-04 the authority moved back to GitHub Actions because this public repository can use standard GitHub-hosted runners without Actions-minute cost and GitHub can enforce one exact-head required check without Cloudflare's watch-path gap.

Historical notes remain preserved under `docs/agent-notes/` and `EVOLUTION_LOG.md`; do not rewrite them to pretend GitHub Actions was always the owner.

## Retirement / rollback

After the GitHub required gate is proven stable, the Cloudflare project can be retired as a separate provider operation. Until then it may continue producing secondary checks. If GitHub Actions has a service outage, do not silently weaken the ruleset; record the incident and use an explicit, bounded recovery decision.
