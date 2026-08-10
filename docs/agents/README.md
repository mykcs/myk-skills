# Agent documentation

This is the stable Agent entrypoint for `mykcs/myk-skills`, the canonical repository for shared user skills consumed across Agent harnesses.

Do not treat every nested `SKILL.md` as an active user skill. The repository deliberately contains active top-level skills plus archives, benchmarks, plugin-owned skills and nested references.

## Read first

1. this file — ownership and repository map;
2. root `README.md` — human-facing repository purpose and installation/use guidance;
3. [`scripts/skill_inventory.py`](../../scripts/skill_inventory.py) — deterministic classification of all `SKILL.md` files;
4. [`scripts/ci_check.py`](../../scripts/ci_check.py) — repository validation gate, including inventory invariants;
5. the task-relevant top-level `<skill>/SKILL.md` — canonical workflow for that skill;
6. [`../agent-notes/README.md`](../agent-notes/README.md) — dated architecture/migration handoffs and verified invariants;
7. `shared/` and `reference/` only when the selected skill or task points there.

When available, account-wide collaboration preferences and the repository registry live in `~/.agents/AGENTS.md` and `~/.agents/docs/agents/README.md`.

## Ownership boundary

```text
mykcs/.agents        shared user/tool instructions and account navigation
mykcs/myk-skills     shared reusable skill semantics (this repository)
mykcs/.claude        Claude-native commands/hooks/rules/OMC adapters
mykcs/.codex         Codex-native config/hooks/system skills/plugins
```

A harness command may be a thin UX adapter for a skill owned here. In that case, workflow semantics belong in the skill and must not drift into a second writable command copy.

Codex `skills/.system/*` are platform/runtime-native capabilities. Never merge or replace them with a user skill from this repository solely because names overlap.

## Repository map

```text
<name>/SKILL.md          active top-level shared skill roots
shared/                  reusable references shared by multiple skills
reference/               reference material, not an active skill root by itself
docs/agent-notes/        dated Agent-facing architecture/migration notes
docs/agents/             stable repository orientation
scripts/skill_inventory.py deterministic skill inventory/classification
scripts/ci_check.py      validation/inventory invariants
requirements-ci.txt      CI/build dependencies
package.json             Cloudflare validation build entrypoints
_archive/ and fixtures   non-active historical/benchmark surfaces where present
```

Use the inventory tool rather than a hand-written skill count.

## Skill lifecycle rules

- **active**: top-level user-owned skill with canonical `SKILL.md`;
- **internal**: implementation/helper skill not intended as a public user entrypoint;
- **archive/reference/benchmark/plugin**: retained for evidence, evaluation or vendor/reference use and not counted as the active public surface;
- name collision is not proof of duplicate ownership; inspect lifecycle and owner first.

When adding or moving a skill, run the repository inventory/validation checks and update the owning documentation rather than editing consumer symlinks.

## Validation

Use the repository-provided checks rather than inventing an external CI contract:

```bash
python3 scripts/skill_inventory.py
python3 scripts/ci_check.py
```

For a changed skill, also run its task-specific tests/evals when present. A skill is not complete merely because the file exists; its trigger, workflow, references and validation path must remain coherent.

## Agent notes vs current truth

`docs/agent-notes/` contains durable handoffs such as harness CI cleanup and website-improve migration/acceptance work. These notes explain decisions and regressions, but current code/tests/inventory win if a dated note becomes stale.

Do not paste raw chat logs into Agent notes. Prefer decisions, invariants, known failures, rollback boundaries and links to concrete files/PRs/commits.

## Maintenance rule

Update this file when repository ownership, skill lifecycle classes, validation entrypoints or cross-harness boundaries change. Keep task-specific workflow truth inside the owning skill and keep dated migration detail in `docs/agent-notes/`.
