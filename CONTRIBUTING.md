# Contributing to myk-skills

## Skill Structure

Each skill lives in its own directory under the repository root and must contain:

```
skill-name/
├── SKILL.md          # Required: skill definition with YAML frontmatter
├── references/       # Optional: supporting reference documents
├── [other files]    # Optional: templates, scripts, etc.
```

### SKILL.md Frontmatter

```yaml
---
name: skill-name
description: One-line description of when to use this skill
license: MIT
author: mykcs
metadata:
  version: "1.0.0"
  category: [evaluation|development|automation|...]
  tags: [relevant, tags]
triggers:
  - trigger-word-1
  - trigger-word-2
---
```

Required frontmatter fields: `name`, `description`, `license`, `author`, `metadata.tags`, `triggers`

## Adding a New Skill

1. Create a directory under the repository root
2. Add `SKILL.md` with proper frontmatter
3. Add reference documents to `references/` if applicable
4. Submit a PR with the new skill

## Reference Document Organization

Reference documents (.md) should live inside the skill that uses them, not at the repository root. Use a `references/` subdirectory within the skill directory.

## Python Code

Python code in `core/` must:
- Import all functions used (no bare `pow()` — use `**` operator or `math.pow()`)
- Have docstrings for all public functions
- Be compatible with Python 3.10+

## Commit Convention

```
<type>(<scope>): <description>

Types: fix, feat, refactor, docs, chore
Scope: P0 (critical), Phase2, Phase3, or skill name
```
