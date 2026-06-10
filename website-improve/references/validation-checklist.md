# website-improve Validation Checklist (v3.7.0+ 拆分)

> **来源**: 从 SKILL.md v3.6.0 (2026-06-09) 拆分（v3.7.0 progressive disclosure refactor, 2026-06-10）。
> **目的**: §跨 § 引用 / §验证清单 / §Case 引用 3 节从 SKILL.md 抽到本文件，按需加载。
> **加载时机**: 多站点 fan-out 上线前对照 / 排查 §33-§35 规则关联 / 升级 v3.7.0+ 后回看 case 引用。

---

## 跨 § 引用 (Cross-Section References)

- **§33 ASI 防御** 关联 workflow 工具 `parallel()` 语法 (§17 §18 现有约束)
- **§34 Autopush fallback** 关联 §18 push rebase 保护 — 兜底链路是 [rebase protection → autopush → direct push]
- **§35 Fix agent cleanup** 关联 §15 Deja-Vu Gate — 同一类 working-tree 残留 30 天内第二次出现需走硬化规则

---

## 验证清单 (v3.6.0 上线后强制)

- [ ] 所有现存 workflow scripts 跑 `node --check` + ASI scan (`grep -B1 -A1 'SITES\.map.*$\n({' *.mjs`)
- [ ] smart-push.sh 加 `git status --porcelain` 兜底 (或 fix agent 强制走 §34 fallback 协议)
- [ ] 3 仓 fix agent prompt 模板注入 §35 cleanup 协议 (下一轮 fan-out 验证)
- [ ] 下一轮 multi-site fan-out 跑完后查 working tree, 0 dirty 视为通过

---

## Case 引用

- `~/.claude/knowledge/cases/wiki/CASE-MULTI-SITE-IMPROVE-20260609.md` — 触发本次升级的完整 case
- `~/.claude/scripts/multi-site-improve-20260609.mjs` — 已应用 §33 ASI 修复 (executed `;` after first SITES.map)
