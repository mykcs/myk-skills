---
name: confirm-edit
description: Confirm target repository and branch before multi-file edits
metadata:
  type: skill
  version: 1.0.0
version: "1.0.0"
author: "mykcs"
license: "MIT"
last_updated: "2026-07-19"
---

# confirm-edit

Confirm repository context before executing multi-file edits. Prevents wrong-repo iterations.

## 触发条件

**必须调用**：在以下操作前
- 跨 3+ 文件的批量 Edit
- 涉及 `~/Repo/webs/` 下任意站点的文件修改
- 涉及 `~/Repo/mykcs/` 下任意子目录的文件修改

**自动跳过**：单文件微调、已确认过的连续编辑

## 执行方式

用户手动调用：`/confirm-edit` 或 `confirm-edit`

或 AI 主动调用（建议语气）："确认目标仓库上下文 — ~/Repo/webs/active/mykcs.github.io/，等待确认后执行"

## 检查项

```bash
# 1. 目标仓库
git -C "$TARGET_REPO" remote get-url origin
git -C "$TARGET_REPO" branch --show-current
git -C "$TARGET_REPO" status --short

# 2. 未提交的更改
git -C "$TARGET_REPO" log @{u}..HEAD --oneline | wc -l

# 3. 与上游分歧
git -C "$TARGET_REPO" fetch origin
git -C "$TARGET_REPO" log HEAD..origin/main --oneline | wc -l
```

## 已知仓库映射

| 路径 | URL | 说明 |
|------|-----|------|
| `~/Repo/webs/active/mykcs.github.io/` | mykcs.github.io | 主站（活跃维护） |
| `~/Repo/webs/arch/wangrui2025.github.io/` | wangrui2025.github.io | 旧站（已重定向） |
| `~/Repo/mykcs/cc_switch/` | github.com/mykcs/cc_switch | CC 开关 |
| `~/.claude/` | github.com/mykcs/.claude | 全局配置 |

## 确认模板

```
> **确认操作目标**：`{TARGET_REPO}`
> - Remote: `{git_remote}`
> - Branch: `{git_branch}`
> - Uncommitted: `{N} changes`
> - Behind upstream: `{N} commits`

按 Enter 继续，或提供替代路径。
```
