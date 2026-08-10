# website-improve long-tail routing triggers — v4.2.0

This file is a routing aid for requests that do not directly name a sub-mode. It does
not override `website-improve/SKILL.md`, and it must not expand task scope merely
because a historical keyword appears.

## Mode A — check / improve

Typical terms:

- `improve site`, `check website`, `site check`, `audit site`, `health check`
- `upgrade`, `modernize`, `升级`, `重构`, `cleanup`, `清理`
- `anti-pattern scan`, `反模式扫描`
- `build fix`, `fix build`
- `architecture decision`, `ADR`
- `duplicate pages`, `redirect`, `重定向`

Route to Mode A for the site(s) actually named or resolved from context.

## Mode B — Astro/build

Typical terms:

- `astro`, `astro website`, `astro static site`
- `astro content collections`, `astro deployment`, `astro i18n`
- `starlight`, `mermaid`, build/dependency migration terms

Add Mode B when the target is Astro or the requested work materially touches the Astro
build/dependency layer. Do not run it just because historical website-improve defaults
used a broad sweep.

## Mode C — project page

Typical terms:

- project page / academic project page
- paper/project landing page
- research demo site

Add Mode C when the requested outcome is a project-page artifact.

## Mode D — multi-site

Typical terms:

- `fan out`, `parallel sites`, `并行部署`
- `sync all sites`, `multi-site`
- `parallel full audit`, `全量 fan-out`
- `4-site sweep`

Mode D scope is **the sites named/resolved by the request**.

`4-site sweep` is an explicit historical preset for:

- `mykcs`
- `GDKVM`
- `OSA`
- `content2html`

It is not the default scope for a generic `audit site` or `full sweep` request.

`full sweep` means “run the relevant website-improve capabilities across the resolved
scope”, not “force A+B+C+D and four historical sites regardless of relevance”. Planner
chooses sub-modes based on the actual task and technology stack.

## Routing precedence

1. explicit user scope and requested outcome;
2. current website-improve v4.2.0 skill contract;
3. these keyword hints;
4. fallback to Mode A for the resolved site(s).

Never let a keyword silently add a repository/site the user did not request and the
change does not affect.

## Publication and verification

Triggers select capabilities, not publication side effects.

- `deploy all` may imply publication/deployment intent and should be encoded by Planner;
- `audit all` does not automatically imply commit/push/deploy;
- hosted CI is used only when the scoped repository/publication contract calls for it;
- Verifier still derives modern Acceptance from task-scoped evidence.

## Historical note

Older versions of this file described `4-site sweep` as a default scope and `full
sweep` as mandatory A+B+C+D. Those semantics are retained only as history in Git; they
are not active v4.2.0 routing rules.
