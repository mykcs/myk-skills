> 📌 This is a public repository. To make it private, navigate to **Settings → Danger Zone → Change repository visibility → Make private**. Visibility changes are reversible but may affect external links and forks.

# myk-skills

Claude Code skills for personal knowledge management, web development, and productivity automation.

## Architecture

```
~/.agents/skills/          ← git clone (source of truth, mykcs/myk-skills)
~/.claude/skills/          ← symlinks to ~/.agents/skills/<name>
```

**Rule**: All skills in `~/.claude/skills/` must be symlinks pointing to `~/.agents/skills/`. No real directories allowed.

## Skills

| Skill | Description |
|-------|-------------|
| `site-modernizer` | Static academic/personal website maintenance and upgrading |
| `rich-audit` | Multi-stage audit skill for code quality and modernization |
| `feishu-agent` | Feishu Bitable natural language CRUD operations |
| `grill-with-docs` | Repo audit with documentation coverage analysis |
| `record-case` | Structured case archiving from session learnings |
| `skill-creator` | Create new Claude Code skills from templates |
| `xlsx` | Excel file operations via Python |
| `pdf` | PDF generation and manipulation |
| `docx` | Word document operations |
| `pptx` | PowerPoint generation |
| `frontend-design` | Frontend UI/UX design and implementation |
| `canvas-design` | Canvas-based design and visualization |
| `publishing-astro-websites` | Astro website publishing workflow |
| `mcp-builder` | Build MCP servers and tools |
| `web-access` | Web search and fetch capabilities |
| `learn` | Learning and knowledge acquisition |
| `hello-world` | Example skill template |
| ... | [38 skills total] |

## Usage

```bash
# Install a new skill — create symlink
ln -s ~/.agents/skills/<name> ~/.claude/skills/<name>

# Check symlink status
ls -la ~/.claude/skills/
```

## Adding a New Skill

1. Add skill directory to `~/.agents/skills/<name>/`
2. Commit and push to `mykcs/myk-skills`
3. Create symlink: `ln -s ~/.agents/skills/<name> ~/.claude/skills/<name>`

## License

MIT
