# Cloudflare required-check policy

This document resolves the GitHub merge-gate policy for `myk-skills-validation`.

## Decision

While Cloudflare Workers Builds is allowed to skip any pull request through **Build watch paths** (currently the repository desired state excludes `docs/*`), **do not configure the `myk-skills-validation` Cloudflare check run as a global required status check in a GitHub Ruleset or branch-protection rule**.

This is deliberate, not a missing migration step.

Cloudflare documents that a project skipped by Build watch paths does not generate a GitHub check run. A globally required GitHub check must be satisfied on the pull request's latest commit. Combining those two settings would leave a docs-only pull request waiting for a check that Cloudflare intentionally never creates.

## Steady-state merge gate

- For every pull request whose changes trigger Workers Builds, require a successful Cloudflare result for the **exact latest head commit** before merging.
- A successful Cloudflare result for an older commit never satisfies the gate after a new push.
- Docs-only pull requests may intentionally have no Cloudflare check when the `docs/*` Build watch-path exclusion is active.
- `.github/workflows/rich-audit-ci.yml` remains a manual emergency fallback and must not become a second automatic required check.
- `scripts/ci_check.py` remains the validation policy single source of truth.

## When a global required check becomes valid

A future migration may make Cloudflare a GitHub-enforced required check, but only after all of the following are completed in order:

1. Remove every Cloudflare Build watch-path exclusion that can suppress a pull-request build, so every PR head is guaranteed to create the Cloudflare check run.
2. Verify with both a docs-only PR and a non-doc PR that Cloudflare creates a check run on each exact latest head.
3. Identify the exact GitHub check-run context and pin its expected source to the **Cloudflare Workers & Pages GitHub App** when GitHub exposes that option.
4. Configure the repository Ruleset / branch protection to require that exact check.
5. Verify that an intentionally pending or failing Cloudflare build blocks merging and that a successful latest-head build unblocks it.
6. Update this policy and the repository regression tests in the same gated change.

Do not enable a required check first and hope skipped builds will satisfy it.

## Runtime configuration observability

GitHub Rulesets and Cloudflare Build watch paths are account-level runtime settings, not source-controlled files. Repository documentation records the intended architecture; it is not proof of the live dashboard state.

When an authenticated GitHub administration API/UI capability is available, verify that no global required `myk-skills-validation` check is configured while skip paths remain enabled. If such a rule is found, treat it as configuration drift: the default resolution is to remove the global requirement and preserve the conservative `docs/*` build exclusion. Removing the exclusion and moving to a fully required check is a separate architecture change that must follow the migration sequence above.

## References

- Cloudflare Workers GitHub integration: https://developers.cloudflare.com/workers/ci-cd/builds/git-integration/github-integration/
- Cloudflare Workers Build watch paths: https://developers.cloudflare.com/workers/ci-cd/builds/build-watch-paths/
- GitHub required status checks troubleshooting: https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/troubleshooting-required-status-checks
