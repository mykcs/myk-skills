# Contributing to myk-skills

## Skill Structure

Each active top-level skill lives in its own directory under the repository root and must contain a `SKILL.md` file:

```text
skill-name/
├── SKILL.md          # Required: skill definition
├── references/       # Optional: supporting reference documents
├── evals/            # Optional: skill-specific regression tests
└── [other files]     # Optional: templates, scripts, assets, etc.
```

## `SKILL.md` Frontmatter

A skill may use YAML frontmatter at the top of `SKILL.md`. The repository validator follows the current Claude Code skill contract: documented frontmatter fields are optional, `description` is recommended for discoverability, and repository-specific extension fields are allowed.

Example:

```yaml
---
name: skill-name
description: Explain what the skill does and when it should be used.
when_to_use: Use when the request matches this skill's scope.
user-invocable: true
disable-model-invocation: false
allowed-tools:
  - Read
  - Grep
metadata:
  version: "1.0.0"
  tags:
    - example
---
```

The canonical repository validator is `skill-creator/scripts/quick_validate.py`; the root entrypoint `scripts/quick_validate.py` delegates to it. Validation intentionally fails closed on malformed YAML and invalid field types, but it does not maintain a stale fixed allowlist of extension fields.

Current validated field rules include:

- `name`, when present, must be a non-empty kebab-case string of at most 64 characters.
- `description`, `when_to_use`, `argument-hint`, and `model`, when present, must be strings.
- `user-invocable` and `disable-model-invocation`, when present, must be YAML booleans.
- `allowed-tools` and `arguments`, when present, must be a string or a list of strings.
- `metadata`, when present, must be a mapping.
- Additional extension fields are permitted unless a more specific skill-level contract says otherwise.

Do not describe repository conventions such as `author`, `license`, `tags`, or custom trigger metadata as Claude Code runtime requirements unless the runtime specification actually requires them.

## Adding or Updating a Skill

1. Create or update the skill directory under the repository root.
2. Keep `SKILL.md` narrowly scoped and structurally valid.
3. Put supporting documents under the skill's `references/` directory when practical.
4. Add `evals/test_*.py` regression coverage for behavior or contracts that are easy to regress.
5. Run the provider-neutral repository validation before merging:

```bash
python3 -m pip install -r requirements-ci.txt
python3 scripts/ci_check.py
```

Routine pull-request and `main` validation runs through Cloudflare Workers Builds. GitHub Actions is retained only as a manual fallback; both providers call the same `scripts/ci_check.py` policy entrypoint.

## Reference Document Organization

Reference documents should normally live inside the skill that uses them, under a `references/` subdirectory, rather than accumulating at repository root.

## Python Code

Repository CI is pinned to Python 3.12. Python code that participates in repository validation should therefore run cleanly on Python 3.12. If an individual skill intentionally supports a wider Python range, document and test that range within the skill instead of treating the repository CI version as its public compatibility promise.

Public Python functions should have useful docstrings, imports should be explicit, and detection/validation tools should produce stable machine-readable contracts when other tests depend on them.

## Validation and CI

`scripts/ci_check.py` is the single source of truth for repository validation. It currently covers:

- structural validation of active top-level `SKILL.md` files;
- root regression tests under `evals/`;
- active skill `evals/test_*.py` suites;
- preserved `host-self-evolve` compatibility and modernization checks.

Do not duplicate these checks into provider-specific CI configuration. Provider configuration should invoke the shared entrypoint instead.

## Commit Convention

Prefer concise conventional commit subjects:

```text
<type>(<scope>): <description>
```

Common types include `fix`, `feat`, `refactor`, `docs`, `test`, `build`, and `chore`. Use a scope that identifies the affected skill or subsystem when it adds useful context.
