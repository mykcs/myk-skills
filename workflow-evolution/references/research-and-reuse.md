# Research and reuse decisions

Use this reference for source selection and uncertain replacement boundaries. The examples are
decision patterns, not package mandates or a standing inventory of the user's repositories.

## Primary-source starting points

Start with the sources relevant to the changed surface. These publishers are a useful research
set, not a required reading circuit or an authority above the user's goal.

- **OpenAI:** [Harness engineering](https://openai.com/index/harness-engineering/) gives a
  first-party account of agent-facing engineering. Follow links to current platform documentation
  for supported capabilities rather than treating an internal team's setup as a product contract.
- **Anthropic:** [Engineering](https://www.anthropic.com/engineering) covers harnesses, tools,
  context and evaluation. Check article updates: [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)
  now notes that its tooling landscape changed and points to [Managed Agents](https://www.anthropic.com/engineering/managed-agents).
  Extract the mechanism and check whether its assumptions match the current runtime.
- **Kimi / Moonshot:** [Kimi Research](https://www.kimi.com/en/blog/) links the team's technical
  reports and projects. Follow the original report/repository for methods and limitations; a model
  benchmark is not proof that its surrounding orchestration fits this project.
- **MiniMax:** [MiniMax Agent engineering retrospective](https://www.minimax.io/news/minimax-agent-what-we-learned-while-building-in-2025)
  is a first-party account of agent-building experience. Verify any proposed implementation against
  current official documentation or source, and separate measured behavior from product direction.
- **Apple Developer:** [News](https://developer.apple.com/news/) leads to current release notes,
  samples, APIs and platform guidance. Apply that evidence to the relevant Apple surface; do not
  import an Apple-specific architecture or visual convention into unrelated projects by analogy.

Links last checked for this draft on 2026-09-30. The date is provenance, not a claim of future
currency. Reopen load-bearing sources when making a new decision.

## Match the evidence to the claim

- Actual adoption: inspect target code, imports/callers, config, lockfiles, tests and deployment.
- Supported API or runtime behavior: use current official docs, release notes and the version
  actually installed; check implementation or run a focused probe when ambiguity matters.
- Candidate maturity: examine license, security/support policy, releases, tests, unresolved relevant
  issues, maintainer responses and compatible versions. Stars/downloads are discovery signals.
- Engineering improvement: read the original article/paper, method and limitations; seek counter-
  evidence and compare against the project's baseline. Marketing numbers are not local results.
- User fit: cite current user instructions or relevant repeated behavior. Separate preference,
  temporary circumstance, hard requirement and your own inference.

Freshness depends on what can invalidate the claim. A current release note may override old API
advice; an older benchmark may remain decisive if workload and hardware have not changed. Record
the source's actual publication/update date separately from your access date. Do not invent dates.

For each consequential candidate, a compact evidence row is enough:

`responsibility → current baseline → candidate/version → evidence and caveat → decision/test`

Pin versions or commits for experiments. If research is inconclusive, say which specific fact
would decide the choice. Do not hide missing support behind a long bibliography.

## Reuse at the right layer

### Already adopted does not mean missing

If a project already has orchestration pilots or a browser/test/schema stack, inspect their active
scope first. Reuse or complete an existing integration where appropriate. Do not introduce the same
framework as a new discovery or count a historical pilot as production adoption.

### Standard engine plus local semantics

A standard schema validator can be valuable as a CI-only differential oracle before becoming a
runtime dependency. First compare dialect, unknown-keyword behavior, reference resolution/offline
constraints, formats, non-finite numbers, equality and canonicalization. Scientific identities,
hashes and metric semantics may remain local authority. "Both validate JSON" does not establish
drop-in compatibility.

Property-based tools can generate and shrink inputs or event sequences while project tests keep
the actual invariants. The generator does not decide what scientific or operational correctness
means.

### Similar names can hide different responsibilities

A workflow SDK's replay API may check workflow-history compatibility. A scientific receipt replay
may reconstruct results or verify provenance. Reuse the SDK's supported replay for its domain
without deleting a different replay mechanism merely because both are called "replay".

### Replace a scanner without losing its scope

A mature secret scanner may reduce handwritten pattern maintenance, yet its default exclusions
may skip files the old scanner covered, such as SVGs or lockfiles. Build synthetic positive and
negative fixtures, compare file coverage and redacted output, and preserve repository-specific
rules where needed. Inspect current maintainer policy: feature-complete with security patches is
different from abandoned, and neither automatically proves fitness for evolving threat coverage.
Never put real secrets in an evaluation fixture.

### Add a common check without erasing domain checks

An accessibility engine inside an existing browser-test suite can cover common accessibility
failures. It does not replace geometry, interaction, scientific-reader comprehension or project-
specific content rules. Verify which contrast or keyboard checks overlap before removing them.

### Keeping a small component can be rational

A short, tested link checker may be cheaper to maintain than adopting a larger tool with new
configuration and CI installation. A benchmarked memory-mapped numeric format may still fit better
than a newer container format. Compare real coverage/workload and total cost, then keep the current
choice if it wins. Revisit when an observed requirement or dependency assumption changes.

## A discriminating experiment

For a replacement, capture only what is needed to answer the decision:

- baseline/candidate identity and representative fixture or workload;
- invariants and positive/negative controls at the exact boundary;
- expected benefit and acceptable regression limits justified by the task;
- relevant environment and raw observations;
- adoption, rejection and rollback/stop conditions.

A failed candidate is useful evidence. Fix the implementation only within authorized scope; do not
relax the invariant, remove inconvenient cases, or select only favorable runs to make adoption win.
When results depend on live services or stochastic models, distinguish repeatable evidence from
noise and report the uncertainty instead of inventing a significance threshold.
