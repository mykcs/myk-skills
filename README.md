# myk-skills

Shared user-level skills for the Claude Code and Codex harnesses.

## Architecture

```text
mykcs/myk-skills
        ↓ clone / checkout
~/.agents/skills/          ← canonical writable skill source
        ↓ consumer links / native routing
~/.claude/skills/          ← Claude consumer surface
Codex shared-skill routing ← Codex consumer surface
```

**Ownership rule:** shared skill semantics are edited in this repository only. Consumer links/adapters are not independent sources of truth.

Harness-native/system skills are separate. In particular, Codex `.system` skills are platform-owned and must not be merged into this repository merely because a name overlaps (for example `skill-creator`).

## Complete inventory

Do not maintain a hand-written skill count in this README. The repository contains active skills, archives, benchmark fixtures, plugin-owned skills, and nested reference copies; recursively counting `SKILL.md` files without lifecycle classification is misleading.

Generate a deterministic complete inventory with:

```bash
python3 scripts/skill_inventory.py --format text
python3 scripts/skill_inventory.py --format json
```

The inventory classifies every `SKILL.md` as one of:

- `active` — top-level `<name>/SKILL.md`, the shared runtime surface;
- `archive` / `deprecated-reference` — historical evidence only;
- `benchmark-fixture` — evaluation/benchmark material;
- `plugin-owned` — plugin-local skill surface;
- `reference-copy` / `nested-skill` — nested implementation/reference material.

Use `--fail-on-duplicate-active-name` in validation when duplicate active frontmatter names must fail the check.

## Verification ownership

Reusable workflows belong in shared skills. Harness-native command syntax should be a thin adapter rather than a copied implementation. For example:

- shared `verify` owns verification semantics; Claude `/verify` delegates to it;
- shared `docs` owns documentation lookup semantics; Claude `/docs` delegates to it;
- `harness-audit` owns its pinned engine while the Claude command remains a control-plane entry adapter.

## Adding or changing a skill

1. Edit/add the canonical top-level skill directory in this repository.
2. Run `python3 scripts/skill_inventory.py --format text --fail-on-duplicate-active-name`.
3. Run the repository validation entrypoint (`python3 scripts/ci_check.py`).
4. Update consumer symlinks/routing only when needed; do not create a second real skill tree under `.claude` or `.codex`.

## Validation policy

Validation is provider-neutral and local-first. `scripts/ci_check.py` is the repository validation entrypoint; GitHub Actions or Cloudflare may call it, but they are not the source of validation policy.

## License

MIT
