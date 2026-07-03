> ⚠️ [历史快照] 本报告/文档中 "Tri-Search Protocol v2.6" 已于 2026-06-12 重命名为 "Force-All-Search Protocol v2.7"; 保留原命名作为 audit trail.
# 1. 术语一致性 (Terminology Consistency)

> Consistency 父维度 20% → 子维度 1: ~3-4%

## 检查对象

- `~/.claude/settings.json` (env, hooks 描述字符串)
- `~/.claude/CLAUDE.md` + `~/.claude/CLAUDE.local.md`
- `~/.claude/memory/MEMORY.md` (🔥 HOT FACTS, Identity, Patterns, Feedback, Cases)
- `~/.claude/memory/identity-first-person.md` 等专题 memory
- `~/.claude/rules/*.md` (4 个 behavioral + 6 个语言特定)
- `~/.agents/skills/*/SKILL.md` 描述

## 检查命令

```bash
# 提取所有 md/json 中的关键词频次
rg -o '\b(behavioral|行为|行为护栏|behavioral-?discipline|behavioral-?process|behavioral-?core|behavioral-?output|consistency|一致性|统一)\b' \
  ~/.claude/{rules,memory,CLAUDE.md,CLAUDE.local.md,settings.json} 2>/dev/null | \
  awk -F: '{print $2}' | sort | uniq -c | sort -rn
```

或 AI 语义检测: 把 4 类文件中关于"行为规则"的描述全部摘出来, 比对是否指同一概念.

## 已知不一致 (案例)

- "behavioral" vs "行为" vs "BAM" (拼音) vs "行为护栏" — 同一概念 4 种叫法
- "Tri-Search Protocol" vs "3-tool cascade" vs "4-tool parallel" — 协议多版本
- "consistency" vs "统一" vs "一致" — 父维度命名漂移

## 自动修复

- **Level 1 (机械)**: 把"行为"统一替换为"behavioral" 在非 behavioral-*.md 文件
- **Level 2 (AI 语义)**: 检测到术语不一致时, 提示用户确认标准名, 一次性全文替换
