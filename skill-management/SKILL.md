---
name: behavioral-skills-management
description: Skills 目录 symlink 矩阵 + git 同步规则（2026-06-01 重构）
metadata:
  type: convention
  project_id: myk
  source: CASE-SKILL-DIR-UNIFICATION-CONSOLIDATED
version: "1.0.0"
author: "mykcs"
license: "MIT"
last_updated: "2026-07-19"
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

- ✅ **OMX_ASK_\* / OMX_TEAM_WORKER 全面替换（2026-06-02 提前 28 天完成）**：
  - `~/.claude/omc/scripts/run-provider-advisor.js`：删除 `OMX_ASK_ORIGINAL_TASK` alias 常量 + 读取分支
  - `~/.claude/hooks/pre-tool-use.mjs` + template：删除 `OMX_TEAM_WORKER` fallback
  - 剩余 3 处 OMX 字符串为解释性注释
- ⏳ **Team MCP runtime 废弃**：`mcp__team__omc_run_team_*` 改用 CLI `omc team N:agent-type "task"`。CLI 已可用（`/opt/homebrew/bin/omc`），无需等 OMC 5.0。
- **Native Team Worktree Mode**：worker 在独立 git worktree 中运行（opt-in，env `OMC_TEAM_WORKTREE_MODE=detached|branch`）。

## `omc team` CLI 即用参考

**基本语法**：`omc team [N:agent-type[:role]] [options] "<task>"`

| 模式 | 命令 | 说明 |
|------|------|------|
| 同构 N-worker | `omc team 3:claude "fix failing tests"` | 3 个 Claude worker 并行 |
| 角色化 | `omc team 2:codex:architect "design auth"` | 2 个 codex worker，role=architect |
| 异构 provider | `omc team 1:codex,1:gemini "compare"` | 1 codex + 1 gemini |
| 新窗口 | `omc team 2:codex "review" --new-window` | 每个 worker 独立 tmux 窗口 |
| 禁分解 | `omc team 2:claude "..." --no-decompose` | 整段作为单一 worker scope |

**管理子命令**：
- `omc team status <name>` — 查看 team 状态
- `omc team shutdown <name> [--force]` — 关闭 team
- `omc team api <op> --input '<json>'` — 编程式交互（send-message 等）

**Worktree 隔离**：env `OMC_TEAM_WORKTREE_MODE=detached` 让每个 worker 在 `.omc/team/<name>/worktrees/<worker>/` 独立工作。

**典型工作流**（rich-audit Layer 2 修复时使用）：
```bash
# 启动 3 个 worker 并行修不同 PENDING 项
omc team 3:claude "fix 5 PENDING items from rich-audit report"

# 异步查询状态
sleep 60 && omc team status fix-rich-audit

# 完成后关闭
omc team shutdown fix-rich-audit
```
