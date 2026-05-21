---
name: backup-claude-settings
description: |
  Backup Claude Code settings.json and .claude.json to a GitHub repository with timestamped filenames.
  Automatically detects the active API provider (Kimi, MiniMax, Anthropic, etc.) from
  ANTHROPIC_BASE_URL and uses it as the filename prefix. Commits and pushes immediately.
  Includes mandatory diff audit against the previous backup (cross-date) and generates an audit log.
license: MIT
metadata:
  version: 1.3.0
  category: utility
  author: mykcs
  triggers:
    - backup settings
    - backup claude settings
    - backup settings.json
    - 备份 setting
    - 备份 settings
    - 备份 claude 配置
  tags:
    - backup
    - claude-code
    - settings
    - git
---

# Backup Claude Settings

一键备份 `~/.claude/settings.json` 和 `.claude.json` 到 GitHub 仓库，自动根据当前 API 提供商命名。
每次备份后**强制对比审计**，与上一次同 provider 备份进行 diff，生成审计日志。

## 调用方式（重要）

由于本 skill 涉及 **git commit + push** 副作用，根据安全规则设置了 `disable-model-invocation: true`，**不能通过 `/backup-claude-settings` 调用**。

**正确用法**：直接对 Agent 说：
> "备份我的 Claude 配置" / "backup claude settings" / "备份 settings"

Agent 收到指令后会手动执行底层脚本，而非通过 Skill 工具自动触发。

## 备份目标

| 文件 | 来源 | 备份命名 |
|------|------|---------|
| `settings.json` | `~/.claude/settings.json` | `{provider}-YYYYMMDD-HHMM.json` |
| `.claude.json` (global) | `~/.claude/.claude.json` | `claude-json-global-YYYYMMDD-HHMM.json` |
| `.claude.json` (project) | `~/.claude.json` | `claude-json-project-YYYYMMDD-HHMM.json` |

## API 提供商检测

从 `settings.json` 中的 `ANTHROPIC_BASE_URL` 提取域名前缀作为文件名前缀：

- `https://api.kimi.com/coding/` → `kimi-20260428-1111.json`
- `https://api.minimax.chat/` → `minimax-20260428-1111.json`
- `https://api.anthropic.com/` → `anthropic-20260428-1111.json`

## 快速使用

```bash
# 常规备份（必须能找到上一次同 provider 备份，否则中止）
bash ~/.claude/scripts/backup-settings.sh

# 首次备份（显式声明无历史状态）
bash ~/.claude/scripts/backup-settings.sh --force-first
```

> **脚本不存在时**：Skill 被调用后，若 `~/.claude/scripts/backup-settings.sh` 不存在，Agent 应先检查 `~/.claude/scripts/` 下是否有同名脚本，若无则告知用户需要创建备份脚本或改用手动备份。

## 执行流程（不可跳过任何步骤）

1. **检测 API 提供商**：正则提取域名前缀，确定文件名前缀
2. **执行备份**：生成 JSON 文件到日期目录
3. **强制对比审计** `[BLOCKING]`：
   - 必须找到上一次同 provider 备份（跨日期目录回溯，不限于同一天）
   - 必须执行 diff，无论是否有变化
   - 无变化时显式输出：`✅ 与上一次备份（文件名）对比：无差异`
   - 有变化时输出 diff 前 60 行，并写入审计日志
   - 无法找到上一次备份时，**中止流程并 exit 1**，禁止静默假设为首次备份
   - 仅当传入 `--force-first` 参数时，跳过阻断并声明为基准状态
4. **权限配置备份**：同时备份全局和项目级 `.claude.json`
5. **提交与推送**：git add + commit + push（失败自动重试 3 次）
6. **完成声明限制**：
   - 禁止说"备份完成"而不提及 diff 结果和审计日志路径
   - 禁止说"无变化"而不指明对比的上一次备份文件名
   - 禁止用"您的提醒让我发现"等推卸责任的表述

## 惩罚机制

- 跳过步骤 3 或未能展示 diff 结果 = 操作无效，必须重新执行
- 无法找到历史备份但未使用 `--force-first` 时静默继续 = 操作无效
- 审计日志未生成 = 操作无效

## 功能特性

1. **通用 API 检测**：正则提取域名前缀，支持任意 API 提供商，不限于硬编码列表
2. **防重复覆盖**：同一分钟内重复运行会自动追加秒级后缀（如 `kimi-20260428-1111-45.json`）
3. **跨日期 Diff 对比**：备份后自动打印与上一次同 provider 备份的差异，支持跨日期目录回溯，对比输出保留前 60 行
4. **审计日志强制落盘**：每次备份生成 `audit-diff-YYYYMMDD-HHMM.log`，diff 结果必须写入文件
5. **首次备份阻断**：找不到历史备份时默认 exit 1，必须用 `--force-first` 显式声明
6. **权限配置备份**：同时备份全局 `~/.claude/.claude.json` 和项目级 `~/.claude.json`
7. **Push 重试**：网络失败时自动重试 3 次
8. **恢复流程**（路径为示例，请根据实际备份仓库替换）：

```bash
# 先确认备份仓库位置（通常为 ~/Repo/mykcs/ 下的对应仓库）
cd ~/Repo/mykcs/
ls

# 从备份恢复 settings.json（将 {provider} 替换为实际前缀）
cp {backup-repo}/YYYY-MM-DD/{provider}-YYYYMMDD-HHMM.json ~/.claude/settings.json

# 从备份恢复 .claude.json
cp {backup-repo}/YYYY-MM-DD/claude-json-global-YYYYMMDD-HHMM.json ~/.claude/.claude.json
```

## 约定

- 每次备份立即 `git push`，不累积
- 历史文件保留原前缀，不改名（记录当时使用的 API）
- commit message 包含 provider 信息：`backup(kimi): Claude settings 2026-04-28 11:11`
- 审计日志随备份文件一起提交，不可遗漏
