# Scope-relevant CI and deployed verification — v4.2.0

This reference replaces the old interpretation that every website-improve run must
prove four historical sites, five Git fields, and deployed curl evidence.

The durable lesson from the old four-site incidents remains valid: **verify the layer
that can actually fail**. The scope of that verification is now derived from the plan.

## 1. When the historical four-site gate applies

Historical preset:

- `mykcs`
- `GDKVM`
- `OSA`
- `content2html`

Require evidence for all four only when the requested task actually includes all four,
for example an explicit four-site sweep, shared change that affects all four, or a
publication contract that requires all four.

Do not require four-site CI for:

- a single unrelated site such as `basemodel`;
- a two-site task whose scope names only two sites;
- local source work with no publication request unless CI is itself a declared execution target.

## 2. CI is contextual evidence, not a universal ceremony

For every scoped site/repository, determine the actual validation contract:

1. project-owned local/agent checks;
2. repository-required hosted checks when they exist;
3. native/platform checks when Linux/web CI cannot validate the changed behavior;
4. publication/deployment checks only when publication is requested/applicable.

A CI check is acceptable evidence only when it belongs to the current head/target and
has a terminal successful state. `skipped`, missing, unavailable, queued, or stale
checks are not silently upgraded to PASS.

If a repository deliberately does not use hosted PR CI, use its repository-owned
validation entrypoint instead of manufacturing a temporary PR just to obtain a hosted
badge.

## 3. Multi-site fan-out

For Mode D, construct the evidence set from exactly the sites in `plan.json`.

Example two-site plan:

```text
sites: [site-a, site-b]
verification_targets: [build, browser]
```

Both site-a and site-b must pass their planned build/browser evidence. The historical
other two sites are irrelevant unless the change actually affects them.

Example explicit historical full sweep:

```text
sites: [mykcs, GDKVM, OSA, content2html]
verification_targets: [build, ci]
```

All four now belong to scope, so all four must pass the relevant checks.

## 4. Lockfile/build safety

The old lockfile incident remains a valid hard rule for affected projects.

If Executor changes `package.json`, a package lockfile, or dependency/build config:

1. regenerate the lockfile with the project's package manager when needed;
2. run the project's clean/install consistency check when available (`npm ci`, equivalent lockfile check, etc.);
3. run the relevant build/test command;
4. record command + exit status in modern verification evidence.

Do not infer a valid lockfile from a textual package diff.

## 5. Deployed-layer verification

Local files are not proof of deployed behavior. Add live/deployed evidence when the
requested outcome depends on a deployed layer.

Typical triggers:

| Change | Useful deployed evidence |
| --- | --- |
| security headers / `_headers` | response headers from the real deployed host |
| `.well-known/*` | live HTTP status/content type/content |
| `robots.txt` | live content |
| manifest | live status/content |
| sitemap | live content/status |
| routing/redirects | browser or HTTP redirect chain |
| production UI fix | browser/runtime evidence on deployed target if deployment is in scope |

Do not require deployed curl for a source-only task whose plan explicitly has
publication `NOT_REQUESTED` and whose requested outcome is fully verifiable locally.

## 6. Ownership/target evidence

Ownership is part of modern Acceptance, but evidence should match the risk.

For Git publication or multi-account work, verify repository owner/remote/target before
writes and before publication. For a read-only or non-Git local task, ownership may be
`NOT_APPLICABLE`.

Do not create fixed path/commit/push/CI/owner rows merely to fill a legacy table.

## 7. Publication states

Final publication acceptance uses:

- `NOT_REQUESTED` — user/task did not request publication;
- `NOT_APPLICABLE` — publication does not apply;
- `VERIFIED` — requested publication completed and is evidenced;
- `BLOCKED` — publication was requested but cannot be verified/completed.

`BLOCKED` fails the final verdict. `NOT_REQUESTED` and `NOT_APPLICABLE` are not
failures when execution acceptance is otherwise complete.

## 8. Verifier checklist

Verifier asks:

- Is every site/repository in the plan covered by fresh relevant evidence?
- Are there any sites outside the plan being checked only because of historical habit?
- If CI is required, is it for the correct current head and terminal-successful?
- If deployed behavior is part of scope, was the deployed layer actually tested?
- If publication was requested, is it `VERIFIED` rather than assumed?
- Are target/owner boundaries proven where relevant?
- Does the session manifest distinguish intended from pre-existing changes?

Then encode those answers into the modern Acceptance object instead of a fixed legacy
five-field table.

## Permanent anti-patterns

- ❌ “four-site CI green” as a universal single-site completion rule
- ❌ missing/skipped CI reported as success
- ❌ local file existence treated as deployed proof
- ❌ fixed commit/push evidence required when publication was not requested
- ❌ another site's CI failure blocks a task that does not affect that site
- ❌ requested deployment marked PASS without deployed evidence
