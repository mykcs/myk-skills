---
name: host-self-evolve
description: |
  本地主机 Claude Code 协调 + 自我进化 (v1.0 design philosophy): 提升 ~/.claude/ 跨层一致性 (CLAUDE.md / rules/ / memory/ / skills/ / cases/) + 持续自我进化 (§I.4 8 步循环 + N-tool fan-out internalize).
  5 Layer: Layer 0 5 commands gate / Layer 1 7 sub-task audit / Layer 2 cleanup orphan / Layer 3 N-tool fan-out / Layer A.2-A.4 5 字段自检 + 4 站 CI gate.
  触发词: 主机自升级, /host-self-evolve, self-evolve, 整理记忆, 协调 ~/.claude, 自我进化.
  必跑: memory-bench 50 题 (per §C.3.3) + 三段 sub-agent 物理隔离 (v2.6.59) + 跑完实测 wall-clock. 详见 [N-tool-search SSOT §1](~/.claude/rules/protocols/N-tool-search.md) + [changelog](references/changelog.md).
when_to_use: |
  Also trigger when self-evolve / skill evolve / host 升级 / 整理记忆 / claude 协调.
  sub-task 触发: frontmatter audit (15 fields / 1,536 cap) / shell unified check (3 shell 配置 + plugin) / memory-bench 50 题 (per §C.3.3).
  范围: ~/.claude/ + ~/.agents/skills/ 双仓 + Python/ML.
  不适用: 单文件 typo / 文档微调 / 非 ~/.claude/ 项目 (用 website-improve).
  反模式: ❌ 标 PENDING 跳过 memory-bench / ❌ 写协议约束值当 wall-clock (per CASE-HOST-SELF-EVOLVE-V2-7-0-WALL-CLOCK-FALSE-CLAIM) / ❌ 三段 sub-agent 物理隔离破坏. 完整见 [skill-authoring-best-practices.md](references/skill-authoring-best-practices.md).
license: MIT
metadata:
  version: "3.0.0"
  author: mykcs
  category: self-evolution
  changelog: "see references/changelog.md for v1.0.0-v3.0.0 history (v3.0.0 = rename + design philosophy 立)"
  tags: [self-evolution, claude, host]
---

# 主机自升级 Skill (host-self-evolve v3.0.0)

## 设计哲学 (design philosophy, v1.0 立)

本技能的**唯一目的**是提升本地主机的 `~/.claude/` 协调性能力, 配套持续自我进化机制:

### 维度 1: 协调性 (coordination)

`~/.claude/` 是一台**小型主机的配置仓库**, 跟代码仓无异。本技能像管代码一样管它:

| 协调层 | 关注 |
|--------|------|
| `CLAUDE.md` | 全局入口, 内容跨仓一致, 不超 200 行 |
| `CLAUDE.local.md` | 本机 hot recall 锚点, 关键 fact ≤ 5 字段自检 |
| `rules/` | 行为准则, path-scoped 减少 token 注入 |
| `memory/` | 用户偏好 + 案例 + ADR 索引 |
| `cases/wiki/` | 已知失败模式 + 5 IF...THEN 规则 |
| `skills/` | 子仓 symlink → `~/.agents/skills/`, source of truth 单点 |
| `scripts/` | 可执行工具 (cross-tool 验证) |
| `hooks/` | 自动化行为 (per settings.json) |

**协调硬指标**:
- ✅ 协议位 (N-tool-search / cross-session-grep / skill-self-evolution / reverse-mode / soul-protocol / 5-field-acceptance) 不散落, 改 1 行 anchor pointer 引用 SSOT
- ✅ frontmatter 15 字段 + 1,536 chars cap 全 SKILL.md 满足
- ✅ 双账号隔离 (mykcs/* vs wangrui2025/*) 永不出错
- ✅ case file 引用都命中, 0 orphan, 0 dangling cross-ref

### 维度 2: 自我进化 (self-evolution)

跟管代码一样, 配置仓也需要**持续改进**。8 步循环 (per §I.4):

1. 跑 N-tool fan-out (N 当前 = 6, per N-tool-search.md)
2. 抓 8+ 外部资源 highlights
3. internalize 关键洞见 → `~/.claude/memory/*.md` 或新建 memory
4. 更新 ADR (整数 slot 不抢 sub-slot, per ADR-0027 v1.1)
5. 更新 SKILL.md changelog (v3.0.0 → v3.1.0...)
6. commit + push (atomic commit + smart-push, 走 §11)
7. PR + auto-merge (per §C.3.2, 4 条件满足)
8. 5 commands verify + 第 6 字段 FF status + decision-stream

### 维度 3: wall-clock 诚实 (per CASE-HOST-SELF-EVOLVE-V2-7-0-WALL-CLOCK-FALSE-CLAIM)

**禁止写协议约束值当 wall-clock**。**禁止用"重版/重度/轻量/快速版"** 字眼诱导偷懒 (per CASE-HOST-SELF-EVOLVE-V2-7-0-NO-LIGHT-HEAVY-WORDS, 2026-07-03 立, v2.7 = 本次改名立条源)。

- ✅ time.start + time.end 实测 wall-clock
- ✅ 任务完成时长 = 协议要求的 wall-clock 时, 写实测值, 不写约束值
- ✅ 任务未跑够约束时长, 写 "< 实测 X, 约束 ≥ Y" + 立 case file + 不掩饰

## 触发方式 (中英文, 12 词)

| 中文 | 英文 |
|------|------|
| 主机自升级 | /host-self-evolve |
| 自我升级 | self-evolve |
| 整理记忆 | host evolve |
| claude 协调 | claude coord |
| 协调 ~/.claude | evolve claude |
| evolve 整体 | full self-evolve |

> **不适用** (灵魂 v6 anti-trigger, 跟 frontmatter when_to_use 协同): 单文件 typo / 文档微调 / 非 ~/.claude/ 项目 (用 website-improve) / 用户说 "我就要个快速版" (拒绝, 走 §F 自决协议位)。
