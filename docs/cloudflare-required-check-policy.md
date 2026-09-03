# CI required-check policy

This document defines the merge-gate boundary between GitHub Actions and the retained Cloudflare Workers Builds integration.

## Decision

**GitHub Actions is the canonical required CI provider for `myk-skills`.**

The `Repository validation` check from `.github/workflows/rich-audit-ci.yml` must run on every pull request and must be required by the `main` ruleset. The same workflow also validates pushes to `main` and remains manually dispatchable for recovery testing.

Cloudflare Workers Builds is secondary, non-blocking evidence during the cutover. Do **not** configure `Workers Builds: myk-skills-validation` as a required status check while Build watch paths can intentionally skip `docs/*`.

## Why the authority moved back to GitHub

- `myk-skills` is public, so standard GitHub-hosted runners are free for this repository.
- GitHub can require its own exact-head check on every pull request without a second provider's skip semantics.
- `scripts/ci_check.py` remains the validation SSOT, so changing providers does not change validation semantics.
- Cloudflare can be retired later without creating a merge-gate gap.

## Steady-state merge gate

1. Changes to `main` arrive through a pull request.
2. `Repository validation` runs on the exact latest PR head.
3. The GitHub ruleset requires that check to pass before merge.
4. Review threads must be resolved.
5. Cloudflare status is informational and cannot override a failed or missing GitHub required check.

A successful check for an older commit never satisfies the gate after the PR head changes.

## Provider boundary

`scripts/ci_check.py` is the only validation-policy owner. Provider configuration may invoke it, but must not fork the test definition.

Cloudflare Build watch paths and project settings remain account-level state. Repository documentation records the intended secondary configuration; it is not proof of live Dashboard state.

## Retirement rule

The Cloudflare validation project may be disconnected once GitHub's required gate has been observed passing on normal PRs and `main` pushes and no unique Cloudflare-only evidence is needed. Retiring Cloudflare must not change `scripts/ci_check.py` or weaken the GitHub ruleset.
