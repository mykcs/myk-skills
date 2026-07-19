---
name: sync-skill
description: Maintain directory symlinks from ~/.claude/skills and ~/.mavis/skills to ~/.agents/skills (source of truth). Use when ~/.claude/skills is in the legacy per-skill symlink state, or to verify the symlinks are correctly set up after a fresh machine setup. Safe to invoke by agents in verify-only mode.
version: "1.0.0"
author: "mykcs"
license: "MIT"
last_updated: "2026-07-19"
---

<what-to-do>

Maintain the directory symlink structure for skill consumers.

Three modes:
- **verify (default)**: Check that `~/.claude/skills` and `~/.mavis/skills` are directory symlinks pointing to `~/.agents/skills`. Exits 0 if OK, non-zero if migration is needed. Safe to call from agents, CI, or pre-commit hooks.
- **--migrate**: Convert from the legacy per-skill symlink pattern to directory symlinks. Backs up existing paths as `.bak.<timestamp>`. Moves any local-only skills (real directories, not symlinks) into the source repo and commits them. Refuses to run if the source repo has uncommitted changes.
- **--restore**: Roll back from the most recent `.bak` of each target.

Default mode is safe to invoke. The destructive operations (`--migrate`, `--restore`) require explicit opt-in.

</what-to-do>

<supporting-info>

## Architecture

- **Source of truth**: `~/.agents/skills/` (git clone of `mykcs/myk-skills`)
- **Consumers**: `~/.claude/skills` (Claude Code) and `~/.mavis/skills` (Mavis) — both directory symlinks to source

## Migration contract (--migrate)

Pre-conditions (any failure → abort):
1. `~/.agents/skills/` exists and is a git repo
2. `~/.agents/skills/` has no uncommitted changes (`git status` clean)
3. Target paths exist in a migratable state (real directory with per-skill symlinks, missing, or wrong symlink)

Steps:
1. Detect non-symlink entries in each target (e.g., local-only skills like `phd-scout`)
2. For each, `mv` into `~/.agents/skills/<name>/`, `git add`, `git commit` (default msg: `chore(skills): migrate <name> from local-only`)
3. `mv` each target to `<target>.bak.<timestamp>`
4. `ln -s ~/.agents/skills <target>`
5. Run verify mode to confirm

Post-conditions:
- Both consumers are directory symlinks to source
- Source repo has new commits for any migrated local-only skills
- `.bak.<timestamp>` directories exist for rollback (manual cleanup)

## Flags

| Flag | Effect |
|------|--------|
| `--migrate` | Perform migration (destructive) |
| `--restore` | Roll back from .bak |
| `--dry-run` | With --migrate: show what would happen, don't change |
| `--push` | With --migrate: also `git push` source to remote |
| `--message=MSG` | With --migrate: custom commit message |
| `--source=PATH` | Override source path (default `~/.agents/skills`) |
| `--target=PATH` | Override target (comma-separated, default claude + mavis) |
| `-h`, `--help` | Show usage |

## Safety guarantees

- **Default is verify-only**: no filesystem changes without explicit flag
- **Uncommitted changes abort**: refuses to mix migration with in-progress work
- **No automatic push**: `git push` only happens with explicit `--push`
- **Backup always**: target is renamed to `.bak.<timestamp>`, never deleted in place
- **Local-only skills preserved**: real directories in target are moved (not lost) and committed

</supporting-info>
