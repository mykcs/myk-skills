# Parallel Agent delivery, PR integration, and hosted-build budgets

Last reviewed: **2026-08-12**

Use this reference when two or more ChatGPT/Codex conversations, coding Agents, branches, or pull requests are working on the same website or release window. It complements the provider-role workflow in `deployment-platforms.md`; it does not replace project-specific repository policy or live provider state.

## Core rule

**Development may be parallel; publication is serialized.**

The default topology is:

```text
latest main
├─ worker branch A -> Draft PR A ┐
├─ worker branch B -> Draft PR B ├─> integration/release branch -> one integration PR -> main
└─ worker branch C -> Draft PR C ┘
                                                            -> project-owned Production path
```

A worker PR is a reviewable change unit. An integration PR is the accepted combined release head. Do not merge every worker PR into `main` merely because each one is individually mergeable.

## Worker-conversation contract

Each worker conversation should:

1. start from the latest intended base and record its base SHA;
2. own one narrow scope and inspect relevant open PRs before editing;
3. avoid unrelated refactors and shared-file churn;
4. prefer one atomic multi-file commit/ref update over sequential remote file writes;
5. run the strongest available non-hosted validation before the first push;
6. create a Draft PR rather than merging to `main`;
7. report changed files, tests, shared surfaces, dependencies and likely overlap;
8. avoid production deployment and unnecessary hosted Preview requests.

A worker PR may receive provider validation when the repository automatically triggers it. That consumption must be counted honestly; Draft status does not make a provider build disappear.

## Integration-conversation contract

A fresh integration conversation should:

1. refresh `main`, live provider state and the candidate PR list;
2. inspect each candidate's base/head SHA, diff, changed files, checks and dependencies;
3. classify overlap before combining work;
4. select only accepted, coherent changes for the release batch;
5. create one integration/release branch from the current intended base;
6. integrate by merge/cherry-pick/reapplication according to repository policy while preserving authorship and review traceability;
7. resolve conflicts on the integration branch rather than asking the owner to relay patches between chats;
8. run combined validation on the exact integration head;
9. create at most the project-approved hosted Preview/deployment evidence;
10. merge/update `main` once for the accepted batch;
11. mark worker PRs as merged, superseded or still pending with explicit links and reasons.

Do not combine unrelated or unaccepted work only to reduce build count. Reviewability, rollback and ownership remain requirements.

## Conflict classes

GitHub's text merge result is necessary but not sufficient. Check all four classes:

| Conflict class | Typical examples | Required response |
|---|---|---|
| Textual | same lines, delete/modify, rename/modify | resolve the Git conflict explicitly |
| Structural / semantic | layout wrapper changes break theme selectors; overflow clips menus | run the combined UI/runtime path |
| Dependency / generated | package manifest, lockfile, generated schema/assets | regenerate once from the integrated source |
| Provider / release | `vercel.json`, workflows, Build Watch, canonical URLs | re-evaluate trigger count and release ownership |

A clean Git merge does not prove the combined product is correct.

## Hosted-build budget truth

Opening a third conversation does **not** retroactively combine or erase builds already created by earlier pushes.

Provider consumption is determined by facts such as:

- how many new commit SHAs/ref updates were pushed;
- which branches and paths the provider watches;
- whether ignored/skipped deployments are still created or counted by that provider;
- whether Preview and Production are separate builds;
- whether promotion reuses an existing production artifact or rebuilds;
- whether the repository has provider-side branch controls, ignore commands or manual deployment gates.

Verify time-sensitive quota and promotion behavior from current first-party provider documentation and live project settings when it affects the decision. Never infer the remaining quota from repository text alone.

## Default budget modes

Choose the smallest mode that proves the requested result and matches project policy.

### Mode A — no hosted deployment

Use for documentation-only changes, local/Agent-verifiable policy edits, or repositories whose provider rules intentionally exclude the changed paths.

```text
worker checks -> integration checks -> source PR
hosted Preview/Production = none
```

### Mode B — one final Preview plus one Production update

Use when exact hosted behavior must be reviewed before release.

```text
worker branches stay unhosted or minimally hosted
-> combined integration head
-> one exact-head Preview
-> acceptance
-> one main update / Production build
```

### Mode C — one staged production artifact plus promotion

Use only when the chosen provider and project policy support a staged production deployment that can be promoted without rebuilding, and current provider behavior has been verified.

Do not generalize this mode to every Vercel/Cloudflare/GitHub Pages project. A normal Preview-to-Production path may create a second build.

## GitHub connector write discipline

When a connector must change several files on a provider-watched branch, prefer one Git data transaction:

```text
create blobs
-> create one tree from the current base tree
-> create one commit
-> update the branch ref once
```

Do not write five files through five sequential Contents API commits when one atomic tree commit is available. Branch creation alone is not proof that a hosted build was avoided; inspect provider behavior when material.

## Project-level adaptation

Each project should keep only a thin adaptation that states:

- which branches/providers trigger builds;
- whether worker PRs receive hosted validation;
- which files/paths are excluded;
- the integration branch naming convention;
- the exact combined Gate;
- the accepted Preview/Production budget;
- provider-specific exceptions and rollback.

Do not copy one project's Vercel, Cloudflare Pages, Workers Builds or GitHub Pages topology into another repository.

## Completion report

Report the release batch as separate evidence:

```text
candidate PRs inspected
candidate PRs accepted / deferred / superseded
conflict classes checked and resolutions
worker ref updates and hosted provider triggers when known
integration branch/head SHA
combined Gate/build result
hosted Preview/deployment count and states when authoritative evidence exists
main updates
Production changed yes/no/unknown
worker PR disposition and rollback path
```

A single integration PR is not proof of a single provider build. A provider `READY` badge is not proof that combined routes, themes, layouts or runtime behavior were actually inspected.
