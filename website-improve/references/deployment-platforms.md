# Deployment architecture for website work — choose roles before providers

Last reviewed: **2026-08-11**

This reference is for `website-improve` tasks that touch Preview, hosting, CI/CD, canonical domains, or release architecture. Do not use an account-wide vendor recipe as a substitute for inspecting the target repository.

## Core rule

**Map provider roles first; choose or remove providers second.**

Before proposing Vercel, Cloudflare, GitHub Pages, Netlify, or another host, identify the target repository's current responsibilities:

| Role | Questions |
| --- | --- |
| Source / history | Where are canonical code, branches, PRs and releases? |
| Validation / CI | Which provider actually runs blocking checks, and what platform-specific checks remain elsewhere? |
| Preview / review | Is a public/exact-head Preview actually needed? Which current provider can supply it? |
| Production | Which host serves the real product? What rollback exists? |
| Runtime / API | Are there Functions, Workers, cron, storage, auth or other non-static requirements? |
| Product identity | Which hostname/base path/canonical URLs are externally visible and indexable? |

A provider should normally own at least one **distinct, justified role**. Add a provider only when it fills a demonstrated missing role or deliberately replaces another. Avoid a third routine provider merely for symmetry or account-wide consistency.

## Decision principles

1. **Keep a working provider when the original pain was orchestration, not the provider itself.** If excessive Preview builds were the problem, moving Preview elsewhere may solve the problem without moving Production.
2. **Provider-hosted domains are product identity.** Moving away from `*.pages.dev`, `*.vercel.app`, `*.github.io`, or a repository subpath can require canonical/SEO/redirect/external-link migration.
3. **Preview and Production are separate evidence layers.** Build success or provider `READY` is not proof that the requested routes/visuals were inspected; Preview acceptance is not proof Production changed.
4. **Exact-head evidence matters.** If `main` moves after a Preview passes, compare the branch again and revalidate when the intervening changes affect the same contract.
5. **Do not optimize one quota by blindly moving pressure into another.** GitHub Actions usage, Vercel deployments/build execution, Cloudflare Pages Builds, and Cloudflare Workers Builds are different resource pools.
6. **Batch coherent edits.** Avoid trigger-only commits and rapid push loops that manufacture hosted builds.
7. **Re-check current first-party docs.** Provider pricing, quotas, promotion behavior and runtime capabilities change; dated project notes are hypotheses when current limits materially affect the decision.

## Reference examples, not templates

### `mykcs/basemodel`

Current recommended steady state after the 2026-08-11 audit:

```text
GitHub = source
Vercel = ordinary PR / branch Preview
Cloudflare Pages = Production at basemodel.pages.dev
```

The Cloudflare Workers Static Assets shadow was successfully validated but Production cutover is paused. The original problem was Cloudflare Preview/build-budget consumption; Vercel solved that Preview role without requiring a Production-host migration.

### `mykcs/mykcs.github.io`

Different topology, intentionally:

```text
GitHub Pages = canonical/indexable Production
Cloudflare Pages = noindex mirror/review + scoped /api/scholar runtime
```

Adding Vercel only for Preview would create a third provider without replacing an existing required role, so the `basemodel` topology should not be copied mechanically.

### `mykcs/content2html`

GitHub Pages currently satisfies Production and canonical identity at `/content2html`. No second provider is justified until a concrete Preview/runtime/hosting problem appears.

### Non-website repositories

Cloudflare may be CI or runtime rather than hosting. For example, an iOS repository can legitimately use Workers Builds as portable CI while Xcode remains the native validation surface; a scheduled Worker product can legitimately use Cloudflare as both runtime and validation. Website Preview guidance does not apply to those roles.

## Vercel guidance

Vercel is strong for Git-connected exact-head Preview and build feedback, but do not add it automatically.

Use it when public/Agent-visible Preview is a real missing role and its extra provider ownership is justified. Keep Production disabled there when another provider intentionally owns Production. Treat Preview protection/share-link behavior and build limits as live provider facts to verify when material.

Do not assume promoting a normal Preview means “zero additional build”; verify the current Vercel promotion/deployment model when build-count optimization is part of the task.

## Cloudflare guidance

Distinguish Cloudflare products and roles:

- **Pages** — static/site hosting with Pages-specific Git build quotas and `pages.dev` identity;
- **Workers Static Assets** — Workers deployment/runtime model, useful when Workers-native behavior or a host migration is actually justified;
- **Workers Builds** — CI/build service whose resource accounting is different from Pages Builds;
- **Direct Upload** — a deployment mechanism, not an account-wide Preview policy.

Do not say a Direct Upload or Workers Build is “free” merely because it does not consume Pages' Git-build counter. Report the resource/evidence layer actually used.

## GitHub Pages guidance

GitHub Pages remains a good choice for simple static sites, especially when `github.io` identity or repository base paths are intentional product contracts. Do not add a second host solely to make all repositories look alike.

If a public PR Preview becomes a repeated bottleneck, evaluate current preview options then and measure whether the second provider removes enough friction to justify itself.

## Migration / simplification checklist

When adding or removing a provider:

```text
read project Agent/current docs + executable config + live provider state
-> inspect overlapping PRs
-> map provider roles and canonical identity
-> state the measured problem
-> choose the smallest role change
-> preserve provider-neutral build/validation
-> create reversible non-production evidence when needed
-> verify exact head + affected routes/runtime/SEO/headers
-> define rollback
-> explicit Production/canonical cutover
-> verify Production
-> retire old infrastructure only after independent proof
```

Do not combine a framework migration, custom-domain migration and provider migration unless the product actually requires them together.

## Completion evidence

Report separately:

- repository/local Gate;
- hosted build provider and result;
- Preview URL and whether affected routes were actually inspected;
- branch/PR/exact-head state;
- Production changed yes/no/unknown;
- Production verification;
- quota/build-counter claims only when authoritative provider evidence exists.
