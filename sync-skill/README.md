# sync-skill

Maintain directory symlinks from skill consumers (`~/.claude/skills`, `~/.mavis/skills`) to the source of truth (`~/.agents/skills`).

## Why

Previously, each skill needed a manual symlink in `~/.claude/skills/`. This led to:

- Forgetting to add symlinks for new skills
- ~50 symlinks to maintain by hand
- A `phd-scout` real directory that broke the "no real dirs" rule

The directory-symlink pattern (used by `~/.mavis/skills` from the start) avoids all three.

## Usage

```bash
# Default: verify only (safe, can be called by agents)
sync-skill

# See what migration would do
sync-skill --migrate --dry-run

# Migrate: convert from per-skill to directory symlink
sync-skill --migrate

# Migrate + push to remote
sync-skill --migrate --push

# Roll back
sync-skill --restore
```

## Design

- **Default is verify-only**: safe to call from agents, CI, hooks
- **Destructive operations require explicit flag**
- **Uncommitted changes abort migration**: refuses to mix with in-progress work
- **No automatic push**: `git push` only with `--push`
- **Backups preserved**: targets renamed to `.bak.<timestamp>`, never deleted in place
- **Local-only skills preserved**: real dirs in target are moved to source and committed

## Files

- `SKILL.md` — LLM agent interface
- `bin/sync-skill` — main script
- `README.md` — this file
