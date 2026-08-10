# Website-improve quality checks — v4.2.0

This reference preserves useful high-signal audit techniques without making every
historical check mandatory for every website task. Planner selects the checks that
match the requested scope and changed layer; Executor records the resulting evidence;
Verifier decides whether that evidence satisfies modern Acceptance.

## 1. Repeat-audit / regression comparison

Repeated audits benefit from comparing against prior evidence, but a `/tmp` snapshot is
not a universal completion artifact.

Use a prior snapshot/report when:

- the user explicitly asks “再检查一遍” / compare with the last audit;
- a prior structured audit exists and regression/progress comparison is useful;
- the same site has recurring findings that need trend evidence.

If no prior snapshot exists, run the current evidence-based audit without fabricating
one just to satisfy a historical rule. Durable audit history should follow current
memory/case promotion policy rather than an unconditional `/tmp` convention.

Useful comparison output:

- newly introduced findings;
- resolved findings;
- unchanged unresolved findings;
- stale findings whose underlying evidence no longer reproduces.

Do not treat an empty text diff alone as proof that the site is globally clean; the
current audit still needs scope-relevant execution evidence.

## 2. Deployed behavior checks

Source grep is not proof of deployed behavior **when the requested outcome depends on
the deployed layer**.

Use live HTTP/browser evidence for changes such as:

- response/security headers;
- redirects/routing;
- `robots.txt`, sitemap, manifest, `.well-known/*`;
- production-only rendering/asset behavior;
- a requested deployment/release.

Do not require deployed curl for a source-only task with publication `NOT_REQUESTED`
when the requested outcome is fully verifiable locally.

## 3. Dependency/security evidence

When dependency or vulnerability work is in scope:

- use the project's current package manager and lockfile;
- use the authoritative registry/advisory source appropriate to the ecosystem;
- distinguish runtime vs dev-only risk;
- record the command/source used so a Verifier can reproduce the claim.

Historical npm registry workarounds are examples, not universal commands for every
site.

## 4. Verifier self-test

When the workflow changes or introduces a custom verifier/detector, test the verifier
itself against known states when practical:

1. a known-good/PASS sample;
2. a known-bad/FAIL sample.

This is especially important for threshold-based visual/content detectors where a
poor absolute threshold can create systematic false positives or false negatives.

Do not require a synthetic mutation test for every ordinary website edit when the
Verifier logic itself has not changed.

## 5. Template consistency

For collections of pages/slides/components that intentionally share a template, verify
that the shared structural/visual contract has not drifted.

Useful evidence may include:

- component/template source reuse;
- element/class counts where they have semantic meaning;
- snapshot/visual comparison across representative pages;
- shared helper/import structure;
- browser evidence for typography/spacing/overflow.

Do not compare unrelated page types merely because they live in the same repository.

## 6. Browser and visual evidence

For layout/CSS/interactive changes:

- verify the actual breakpoints/states affected by the task;
- include mobile/desktop evidence when responsive behavior is part of scope;
- include Safari/WebKit only when it is a declared compatibility target or the defect is browser-specific;
- verify overlap, overflow, clipping, unreadable text, broken controls, and relevant focus/hover/open states.

A source diff by itself is insufficient for a visual claim.

## 7. Content / SEO / a11y / i18n

Choose checks based on the changed surface:

- SEO: title/description/canonical/OG/structured data when relevant;
- a11y: labels, semantics, contrast, keyboard/focus, reduced motion as relevant;
- i18n: language parity, route correctness, hreflang/switching when localized content is in scope;
- content accuracy: factual/source validation when the task depends on current external facts.

Do not produce a finding solely because a historical checklist contains an item that
the current project intentionally does not implement.

## 8. Build / type / CI

Use the current repository's own contract:

- build/typecheck/lint/test commands actually defined by the project;
- hosted CI only when the repository uses/requires it;
- native/platform validation when web/Linux CI cannot cover the changed behavior.

`skipped`, missing, stale, queued, or unavailable checks are not PASS.

## 9. Evidence rule

Every reported defect or PASS claim should have evidence proportionate to the claim.
Examples:

- dead code → zero-reference/source proof;
- build health → current build exit/result;
- visual fix → browser/screenshot/runtime evidence;
- deployment fix → current deployed/live evidence;
- publication → current target/commit/deploy evidence.

Avoid findings phrased only as “verify X”, “check Y”, or “should audit Z”. If the
necessary evidence is obtainable by the agent, obtain it before reporting a finding.

## 10. Relationship to modern Acceptance

These checks feed execution evidence. They do not redefine final completion.

Final modern Acceptance remains:

- scope;
- execution evidence;
- blockers;
- conditional publication;
- ownership/target where applicable;
- session manifest.

Historical hard rules remain useful as incident lessons, but they no longer override
task-scoped v4.2.0 acceptance.
