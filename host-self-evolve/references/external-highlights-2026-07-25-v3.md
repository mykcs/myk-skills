# External Highlights — 2026-07-25 (v3 memory-bench, host-self-evolve Layer 3 N-tool fan-out)

> **来源**: Layer 3 N-tool parallel fan-out (N=6, per [N-tool-search.md v1.1.3](../../rules/protocols/N-tool-search.md)). 实际跑 4/6 工具: mmx (5 results) + anysearch (10 results) + exa (2 deep-fetches) + WebFetch (1 page). MiniMax 返 2049 (per ADR-0026 必读 body 协议位, 已知 key rotation 状态, 降级不影响主流程) + kimi-webbridge daemon 不可达 (Layer 2 弱约束已知, 跳过不 fail-fast).

## 8+ Highlights (新洞见, 经 grep 比对 / 未沉淀过)

### 1. Claude Code 7 层 memory 架构 (luyao618 源码解读, GitHub)

- **来源**: https://github.com/luyao618/Claude-Code-Source-Study/blob/main/docs-en/31-memory-subsystem-overview.md
- **关键洞见**: Claude Code 内置 7 层 memory (CLAUDE.md / Auto Memory memdir / Background ExtractMemories / Session Memory / Agent Memory / Relevant Memories on-demand / Auto Dream consolidation).
- **应用**: host-self-evolve 跑后**只更新 MEMORY.md 索引**; extractMemories 跑 background (post-response) — 我们没 background agent, 改用 `auto-feishu-digest` daily/weekly 双轨模拟.
- **跟现状对比**: 已有 `~/.claude/memory/MEMORY.md` (200 行硬顶) + `~/.claude/CLAUDE.local.md` hot recall + 自建 memory-strategy. 缺 "Relevant Memories on-demand" 跟 "Auto Dream 24h consolidation" — **观察项 v3.4 立条建议**.

### 2. Evo-Memory / EvoMemBench (Google DeepMind + UIUC, 2025-12)

- **来源**: https://arxiv.org/abs/2511.20857 + https://arxiv.org/html/2605.18421
- **关键洞见**: 静态 conversational memory → sequential task streams 自我进化 memory; ReMem pipeline = action → think → memory refine.
- **应用**: memory-bench 50 题可考虑加 "task stream evolution" 类型 (跨 session 改动记忆后 Q 改判), 当前题库 v0.2.1 已加 memory_architecture_post_mem0 5 题 (Q046-Q050).
- **跟现状对比**: 题库 v0.2.1 反映 mem0 已封存 + 本地 fallback 架构 (CLAUDE.local.md §19); 跟 Evo-Memory 思路一致 (本地化 + 自我进化).

### 3. mem0 2026 State of AI Agent Memory 报告

- **来源**: https://mem0.ai/blog/state-of-ai-agent-memory-2026
- **关键洞见**: 5 大开放挑战 = temporal abstraction at scale / cross-session structure (evolve not overwrite) / application-level eval framework / privacy & consent / cross-session identity resolution.
- **应用**: host-self-evolve 题目中"记忆改写而非覆盖"原则已隐含 (memory-strategy v2 §F.4.4 本体优先 + 索引化).
- **跟现状对比**: 我们做法 = 文件优先 + CLAUDE.local.md 索引; mem0 报告提的"评测框架"= 我们 memory-bench 50 题 (跟 Evo-Memory 目标一致).

### 4. Eight Phases of Remembering — Claude Code 8 阶段 memory 生命周期 (Mandar Karhade, mem0 团队)

- **来源**: https://ai.gopubby.com/eight-phases-of-remembering-how-claude-code-actually-built-memory-c7d1488f77b5
- **关键洞见**: Phase 5 = handleStopHooks() 跑后**3 个 background agents** fire-and-forget: extractMemories + sessionMemory + autoDream. 互斥 = main agent 写 memory 时, extractMemories 跳过 (hasMemoryWritesSince cursor).
- **应用**: 我们 `auto-feishu-digest` daily/weekly = autoDream 简化版 (cron 触发 + 索引刷新). extractMemories 互斥 = 写 memory 时停 background = 我们的 "host-self-evolve 跑后, 不重复自增 changelog" 逻辑.
- **跟现状对比**: 阶段 5 互斥 cursor = §C.2 zero-deferred + §C.6 5 步 false-positive 诊断的同根: "不要做 2 次同一件事".

### 5. How Claude Code Remembers And Forgets (DEV.to)

- **来源**: https://dev.to/oldeucryptoboi/how-claude-code-remembers-and-forgets-the-memory-and-persistence-architecture-55bd
- **关键洞见**: 5 大持久层 (CLAUDE.md / auto-memory dir / background extractor / compaction / raw session transcripts). Compaction = lossy + 破坏性. Transcript search = "last resort" (raw text grep, 慢).
- **应用**: 我们 compaction 没启用 (Claude Code 默认行为, 但我们 200K context + plan 阶段不依赖). 实际: host-self-evolve 走 "compaction 之前 Save session + 重开", 跟 Karpathy LLM Wiki 思路一致 (raw + wiki + schema 三层).
- **跟现状对比**: 缺 transcript search = 我们缺 §H Acceptance Protocol 的 "5 commands" 自动 grep 协议外的事后审计. **观察项**: 考虑 `~/.claude/decision-stream/` 追加 grep helper (per case-index-archive 已有).

### 6. Claude Code 官方 memory 文档 (Anthropic, code.claude.com)

- **来源**: https://code.claude.com/docs/en/memory
- **关键洞见**: Auto memory 默认 on, 项目级 scope (per git repo root). MEMORY.md 加载限制 = 200 行 OR 25KB. Topic files 按需读.
- **应用**: **官方一致** — 我们 MEMORY.md 已 47 行, 留 153 行缓冲, 跟官方 200 行硬顶兼容.
- **跟现状对比**: MEMORY.md 当前 47 行 ✅; 4 个分文件 (MEMORY-cases-active / MEMORY-feedback / MEMORY-cross-cutting / MEMORY-weiying-notion-MASTER) 充当 topic files = 跟官方模式 1:1.

### 7. Karpathy LLM Wiki + Ian Paterson memory 架构 8 规则

- **来源**: https://ianlpaterson.com/blog/claude-code-memory-architecture/
- **关键洞见**: 8 规则 = ① 文件经索引可发现 ② lesson 带日期 ③ write target 固定 schema ④ cron 必预算 + 失败告警 ⑤ 索引必 staleness 检测 ⑥ 事实唯一 canonical ⑦ 文件适配加载机制 ⑧ (没列).
- **应用**: 我们 host-self-evolve 跑后看: ① MEMORY.md 索引 ② 案例 30 天滚动 ③ case-index-archive schema ④ auto-feishu-digest quota budget ⑤ check-n-tool-drift ⑥ MEMORY.md 单一权威 ⑦ 200 行 cap ⑧ ?
- **跟现状对比**: 4/7 规则已立 (索引 + date-stamp + canonical + cap); 缺 staleness detector 跟 cron budget alert = **观察项 v3.4 立条建议**.

### 8. EvoArena (2026) — environment evolution benchmark

- **来源**: https://arxiv.org/html/2606.13681v2
- **关键洞见**: agents 在 evolving environments (terminal / code / user prefs) 准确率仅 39.6%. "persistent env evolution" 是个独立能力.
- **应用**: host-self-evolve 3.3.x changelog 反映 rules/SSOT/sub-slot 多版本变迁 — 跟 EvoArena 同根: environment evolves 速度 > agent adaptation 速度. 我们的解 = 强 user override (per v3.2.1) + 整数 slot 优先 (per ADR-0027 v1.1).
- **跟现状对比**: 我们 host-self-evolve 跑 1 次 / day = 不算 persistent env evolution, 跟 EvoArena 解法不同 (它是 build agent 我们是 maintain 仓).

## 已知沉淀 (历史, 不重列)

- rich-audit v2.6.30-59 changelog
- host-self-evolve v3.3.3 (上一 run) external-highlights-2026-07-25 (b4ac2224)
- EvoMemBench 引用 (per mem0.md + memory/external-highlights-2026-07-19.md)

## 协议位 (强制)

- N-tool-search.md v1.1.3 SSOT (per ADR-0056) — 协议位字面 100% 一致
- 4/6 工具跑通 = N-tool **降级到 4-tool (缺失 MiniMax + kimi-webbridge)**, per §3.1 row 6
- mmx 必跑 (v1.1.3 硬约束) ✅ — quota 81% remaining, 实测 5+ results
- 5 字段自检: mmx version 1.0.16 OK, search functional, organic 返回 ≥5
