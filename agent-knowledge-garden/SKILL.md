---
name: agent-knowledge-garden
description: >-
  Audit and maintain Agent-facing repository knowledge across long-lived projects: keep root instructions small, preserve one writable owner per fact, detect stale/current conflicts, repair docs/agents navigation, and update the account registry without forcing one technical architecture onto every repository.
when_to_use: >-
  Use for docs/agents cleanup, AGENTS.md/CLAUDE.md knowledge drift, cross-repository Agent onboarding, repository knowledge maps, stale handoffs, or account-wide Agent documentation audits. Do not use for ordinary product documentation that has no Agent-operational purpose.
metadata:
  version: "1.0.0"
  category: agent-knowledge
  owner: mykcs
---

# Agent Knowledge Garden

Maintain Agent knowledge as a **control system**, not a documentation dump.

## Objective

Optimize for the time from a fresh Agent entering a repository to its first correct, validated action.

Minimize:

- always-loaded context;
- discovery/tool calls;
- stale or contradictory guidance;
- duplicated writable policy;
- owner relay between tools;
- unverified completion claims.

## Canonical account surfaces

When accessible, read:

1. `mykcs/.agents/docs/agents/README.md` — account navigation contract;
2. `mykcs/.agents/docs/agents/KNOWLEDGE-ARCHITECTURE.md` — first-principles design;
3. `mykcs/.agents/docs/agents/repositories.json` — machine-readable long-lived repository registry.

If the `.agents` checkout is local, run:

```bash
npm run agent-docs:audit
```

The audit is read-only. If GitHub CLI access is unavailable, use the registry as the checklist and inspect repositories through the connected GitHub capability instead of asking the owner to relay file contents.

## Gardening loop

### 1. Discover

For each in-scope active repository:

- read root Agent/tool instruction files;
- read `docs/agents/README.md` and `LATEST.md` when present;
- inspect current policy/repository maps;
- refresh executable truth and live provider state for any claim that depends on them.

Do not begin from history unless the task is historical.

### 2. Classify knowledge

Classify each important statement as:

- **stable** — purpose, ownership, architectural principle;
- **current** — current workflow/layout/migration state;
- **live** — PR/deployment/quota/account/provider state;
- **historical** — rationale, incident evidence, superseded state.

Live claims must be refreshed. Historical claims must not masquerade as current instructions.

### 3. Resolve ownership

Apply one-fact-one-owner:

```text
shared user/cross-tool policy -> mykcs/.agents
shared reusable workflow      -> mykcs/myk-skills
Claude-native mechanics       -> mykcs/.claude
Codex-native mechanics        -> mykcs/.codex
host projection ownership     -> mykcs/dotfiles
project truth                 -> project repository
live provider state           -> provider
```

When duplicate writable copies exist, keep the canonical owner and replace consumers with a short pointer/import/summary where appropriate.

Do not make Claude and Codex structures symmetrical merely for appearance.

### 4. Reduce bootstrap context

Root `AGENTS.md` / `CLAUDE.md` should primarily route plus state non-negotiable invariants.

- target roughly 100-150 lines for a normal project router;
- treat ~200 lines as a review signal, not an absolute failure;
- move task/subtree-specific detail into current docs or path-scoped/nested instructions;
- do not split files if the split would be empty or harder to discover.

### 5. Repair current-vs-history structure

For larger/changing projects, prefer:

```text
docs/agents/README.md
docs/agents/LATEST.md
docs/agents/current/
docs/agents/history/
```

For a small stable project, `docs/agents/README.md` may contain the map and current facts directly.

Never create empty `LATEST.md`, `current/`, or `history/` solely to match another repository.

### 6. Promote enforceable rules

If the same prose constraint has failed repeatedly and can be detected mechanically, promote it into a test/linter/audit/schema. Keep prose as explanation, not the only enforcement mechanism.

### 7. Update registry selectively

Update `mykcs/.agents/docs/agents/repositories.json` only when a repository becomes a long-lived Agent work surface, changes lifecycle/role, changes expected entrypoints, or gains a useful mechanical drift check.

Do not register archives, datasets, caches, one-off experiments or snapshots merely to make the account look uniform.

### 8. Validate

After changes:

- re-read every changed Agent entrypoint;
- run repository-local validation appropriate to the changed repo;
- run `.agents` offline/online Agent-doc audit when available;
- verify links/paths and known-current markers;
- for website repositories, preserve their own deployment/build-budget rules and do not trigger hosted builds merely to validate documentation when the repository provides a cheaper/local path.

## Semantic review rule

A structural audit cannot prove semantic freshness.

When a warning concerns architecture, deployment, current provider configuration or product behavior, compare the documentation against code/config/tests and live provider evidence. Fix the stale canonical source; do not silence the warning by weakening the audit unless the audit itself is wrong.

## Completion

Report concisely:

- repositories changed;
- conflicts/drift removed;
- registry/audit result;
- any remaining live-state boundary that could not be verified;
- any newly discovered repeated failure that should become an executable invariant next time.
