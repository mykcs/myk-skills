# Force-All-Search Protocol v2.9 (历史副 SSOT, 已 redirect 到主 SSOT N-tool-search.md v1.1)

> **⚠️ 本文件已作废** (per ADR-0056, 2026-07-13 立)
>
> **历史**: 本文件原是 Force-All-Search Protocol v2.9 (2026-06-12 立) 副 SSOT, 2026-07-13 ADR-0056 全面清理后作废.
>
> **现在**: 本文件**仅保留 redirect header + 历史归档**, 不再复述协议位 (per §20 SSOT 原则, 反模式 #5: 字面协议位散落).
>
> **完整协议位** (N 工具 / 顺序 / 降级矩阵 / 触发场景 / 反模式 / 可达性矩阵) 见主 SSOT:
> - 主仓: [`~/.claude/rules/protocols/N-tool-search.md`](../../../../../.claude/rules/protocols/N-tool-search.md) v1.1
> - (跨仓路径解析: 主仓 `~/.claude/` 跟子仓 `~/.agents/skills/` 是 sibling 目录)

---

## 历史归档 (per ADR-0037 protocol-ssot-drift-audit-standard §5)

**v2.9 (2026-06-12)**: Force-All-Search Protocol v2.9 = 5 工具 (mcp__MiniMax__web_search ∥ kimi-webbridge ∥ anysearch ∥ WebFetch ∥ exa). 共 5 工具, 缺 mmx 第 6 工具.

**v1.0 (2026-07-03)**: 改名 `5-tool-search.md`, 128+ 散落位改 1 行 pointer.

**v1.1 (2026-07-03)**: 加 mmx 第 6 工具 + 抽象协议名 `N-tool` (N 当前 = 6, 未来可扩), 改名 `N-tool-search.md`.

**v1.1.1 (2026-07-03)**: 撤 mmx-mcp-shim, mmx 恢复单形式 (per ADR-0038 v1.1.1 patch).

**v2.9.2 (2026-07-13 ADR-0056)**: 本文件 (子仓副 SSOT) + 主仓副 SSOT (`~/.claude/rules/references/process-section-F-force-all-search.md`) 一起作废, redirect 到主 SSOT `N-tool-search.md` v1.1.

---

## 反模式 (永久失效, 5 条)

1. ❌ 引用本文件当 N-tool 协议位 = 字面散落 (per §20 反模式 #5)
2. ❌ 引用 `5-tool-search.md` = 文件名已弃用, 必用 `N-tool-search.md`
3. ❌ 引用 `Force-All-Search Protocol v2.9` 当主协议 = v2.9 已是历史, N-tool v1.1 才是当前
4. ❌ 假设 N = 5 写死数字 = 违反 N-tool 抽象 (per N-tool-search.md §9 v1.1 changelog)
5. ❌ 在其他文件复述 6 工具顺序 = 必引用 SSOT §1, 不复制

---

## Cross-references (历史追溯)

- 主 SSOT: `~/.claude/rules/protocols/N-tool-search.md` v1.1
- 起源 ADR: `~/.claude/docs/adr/0022-5-tool-mandatory.md` (v2.9 必跑条款, HIGHEST PRIORITY)
- 顺序 ADR: `~/.claude/docs/adr/0025-rich-audit-5-tool-order-alignment.md`
- kimi-webbridge: `~/.claude/docs/adr/0030-kimi-webbridge-protocol-position-reversal.md`
- SSOT 起源: `~/.claude/docs/adr/0037-protocol-ssot-drift-audit-standard.md`
- N-tool 重命名: `~/.claude/docs/adr/0038-b-n-tool-search-v1.1.md`
- mmx 形式修正: `~/.claude/docs/adr/0038-b-n-tool-search-v1.1.md` v1.1.1 patch
- Drift 清理: `~/.claude/docs/adr/0056-n-tool-drift-cleanup.md` (本文件作废的 ADR)
- 起源 case: `~/.claude/knowledge/cases/wiki/CASE-SEARCH-TOOL-PROTOCOL-DRIFT-20260702.md`
- N-tool v1.1 case: `~/.claude/knowledge/cases/wiki/CASE-N-TOOL-MMX-DOUBLE-FORM-MISJUDGMENT-20260713.md`
- mmx 双形式 case: `~/.claude/knowledge/cases/wiki/CASE-N-TOOL-MMX-DOUBLE-FORM-MISJUDGMENT-20260713.md`

---

## 历史 record

- 2026-06-10: 立 v2.6 Tri-Search Protocol (3-tool)
- 2026-06-12: v2.7 Force-All-Search Protocol (4-tool)
- 2026-06-12: v2.8 (5-tool 加 exa)
- 2026-06-12: v2.9 (per-tool 显式披露)
- 2026-06-29: v2.9.2 (降级矩阵)
- 2026-07-03: 改名 5-tool-search.md v1.0
- 2026-07-03: 改名 N-tool-search.md v1.1 (加 mmx)
- 2026-07-03: v1.1.1 patch (撤 mmx-mcp-shim)
- **2026-07-13: ADR-0056 立, 本文件作废, redirect 到 N-tool-search.md v1.1** (本 redirect header 写入)
