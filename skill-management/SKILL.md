---
name: behavioral-skills-management
description: Skills 目录 symlink 矩阵 + git 同步规则（2026-06-01 重构）
metadata:
  type: convention
  project_id: myk
  source: CASE-SKILL-DIR-UNIFICATION-CONSOLIDATED
---

# Skills 管理规范

> 2026-06-01 重构后定型：所有 skill 必须在 `~/.agents/skills/` 维护，consumer 端用 symlink 读。

## Symlink 矩阵

| 路径 | 类型 | 说明 |
|------|------|------|
| `~/.agents/skills/` | git clone | Skills source of truth（`mykcs/myk-skills`），**所有 skill 必须在这里** |
| `~/.claude/skills/` | **directory symlink** | 整体 → `~/.agents/skills/`（Claude Code 读取） |
| `~/.mavis/skills/` | **directory symlink** | 整体 → `~/.agents/skills/`（mavis 读取） |

## 规则

- **新增 skill**：直接在 `~/.agents/skills/<name>/` 下创建 → `git add` + `git commit` + `git push`。新 skill 自动对两个 consumer 可见
- **修改 skill**：在 `~/.agents/skills/<name>/` 内修改并 push
- **禁止 `rm` / `unlink` `~/.claude/skills` 或 `~/.mavis/skills` 本身**——symlink 是只读视图入口，删了就看不到任何 skill
- **永远通过 `~/.agents/skills/` 写入**——不要在 `~/.claude/skills/<name>/` 里「临时改」（绕开 git = 下次 pull 丢失）
- **local-only skill 语义已废除**：所有 skill 必须 commit 进 git。机器特定的需求用 SKILL.md 内的 feature flag 或独立分支实现
- **维护脚本**：`~/.agents/skills/sync-skill/bin/sync-skill`（默认 verify-only，`--migrate` 显式）

## 验证命令

```bash
# 验证 symlink 完整性
readlink ~/.claude/skills  # 应输出 ~/.agents/skills
readlink ~/.mavis/skills   # 应输出 ~/.agents/skills

# 验证 .agents/skills 中每个 skill 都可见
for s in ~/.claude/skills/*/; do
  name=$(basename "$s")
  [ -d "$HOME/.agents/skills/$name" ] || echo "[MISSING] $name"
done
```

## 故障排查

- **Plugin 不刷新**：SKILL.md 文本是 live-reloaded；`hooks/`、`.mcp.json`、`agents/`、`output-styles/` 修改后需 `/reload-plugins`
- **Symlink 损坏**：参考 `~/.claude/knowledge/cases/wiki/CASE-SKILLS-SYMLINK-REGRESSION-20260602.md`
- **本地 skill 丢失**：可能因 `git pull` 冲突，运行 `sync-skill --migrate` 重建

## OMC 4.14.4 迁移窗口

- **OMX_ASK_\* → OMC_ASK_\***：硬 sunset **2026-06-30**（28 天）。`run-provider-advisor.js` 已带 deprecation warning。
- **Team MCP runtime 废弃**：`mcp__team__omc_run_team_*` 改用 CLI `omc team N:agent-type "task"`。详见本地 OMC 插件 `~/.claude/plugins/cache/omc/oh-my-claudecode/4.14.4/docs/MIGRATION.md`。
- **Native Team Worktree Mode**：worker 在独立 git worktree 中运行（opt-in）。
