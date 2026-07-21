# host-self-evolve changelog 历史归档 (v3.2.1 / v3.2.2 / v3.2.3)

> **拆分原因 (2026-07-21 立, per ADR-0078)**: SKILL.md frontmatter when_to_use 段 2236 chars 超 1536 cap, 触发 §C.3.3 v2.6.49 split-in-two 协议. 拆 3 段历史 changelog (v3.2.1 / v3.2.2 / v3.2.3) 到本文件, frontmatter when_to_use 仅保留当前 (v3.3.0 + v3.3.1).
> **SSOT**: 主 SKILL.md frontmatter when_to_use 段 (per ADR-0037 protocol-ssot-drift-audit-standard).

---

## v3.2.3 汇报极简化 (per ADR-0052 user-override, 2026-07-06)

- 跑完汇报长度 ≤ §Phase 1 段 (~80 行)
- 严格 1:1 复刻: 目的 + N 件事 (一句话 + 现状 + 干什么 + 验收) + 整体验收 (5 项)
- 删 v3.2.2 扩展: BLOCKED 段 / ⏱️ 段 / 任务后建议段 / 自检 emoji
- 反模式: ❌ 跑完汇报 > 80 行 (per ADR-0052 v3.2.3)

## v3.2.2 汇报格式 (per ADR-0051 user-override, 2026-07-06) — 已废弃

- 跑完汇报必走 §Phase 1 段同款大白话 (现状 + 干什么 + 验收, 不用 table markdown)
- 整体验收段必填 5 项 (path / commit / push / CI / owner)
- 反模式: ❌ 跑完汇报用 table markdown (per ADR-0051 v3.2.2 废弃)

## v3.2.1 default decision (per ADR-0050 user-override, 2026-07-06)

- Run 范围: 默认全套 (Phase 1.1 → 1.4), user 显式说"只跑 X" 才拆 sub-task
- 执行模式: 默认三段串行 (plan/execute/verify 物理隔离, per v2.6.59 + §C.3.7)
- AskUserQuestion 触发白名单 (以下才问): 不可逆操作 / framework config 改字段 / user 偏好变更 / user 显式说"立刻决策"
- 反模式: ❌ 跑 host-self-evolve 还问"Run 范围"/"执行模式" (per ADR-0050 v3.2.1)

---

## 联动

- 主 SKILL.md frontmatter when_to_use (1 行 pointer 到本文件)
- ADR-0050 / ADR-0051 / ADR-0052 (3 个 user-override 起源)
- ADR-0078 (本拆分触发 ADR)
- references/changelog.md (完整 v3.3.0 / v3.3.1 changelog)