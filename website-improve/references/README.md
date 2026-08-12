# Website-improve references

Load references progressively; do not preload the whole directory.

For every change to a human-facing rendered web surface, first classify and apply [`human-thinking-web-expression.md`](./human-thinking-web-expression.md). It is the shared owner-preference source for representing human thought with semantic HTML while balancing information density and reading flow. A small edit may use `APPLY_LIGHT`; a broad change may use `APPLY_FULL`; backend-only work may be `NOT_APPLICABLE`.

For hosting, Preview, deployment-provider, build-budget, canonical-domain, or CI/CD architecture decisions, read [`deployment-platforms.md`](./deployment-platforms.md) first. Its provider-role map is the current shared decision rule: inspect the target repository's source/CI/Preview/Production/runtime/canonical-identity responsibilities before copying any sibling repository's provider topology.

For concurrent Agent branches/PRs and hosted-build budgeting, read [`parallel-agent-delivery.md`](./parallel-agent-delivery.md).

Task-specific references remain authoritative for their narrower subjects. Historical examples are evidence, not account-wide defaults.
