## 并行 Agent 策略

> **下沉到 references**：完整 108 行已迁出（含 3 个 Layer Agent 启动模板 + 8 维度加权模型）。
> 详见 [`references/agent-strategy.md`](references/agent-strategy.md)

**核心原则**：无依赖关系的任务必须并行启动 Agent，缩短总耗时；有依赖关系的任务必须顺序执行。

**3 个并行域**：
- **Layer 1 双模并行**: `Agent-Audit-A`（配置）+ `Agent-Audit-C`（Python/ML）同时启动
- **Layer 3 多源并行**: `Agent-Evolve-1/2/3`（配置/ML/文档）同时启动
- **Layer 2 子任务并行**: `Agent-Fix-Rules/Memory/Skills/Python` 按文件类型并行

**8 维度加权模型**：architecture 25% + integrity 30% + security 20% + consistency 20% + github_sync 5% + timeliness 5% + redundancy 5% + performance 5%。

**Consistency 父维度展开 (v2.6, 2026-06-10)**:
父维度 20% 拆为 6 个子维度, 详见 [`references/consistency-6d/`](references/consistency-6d/):

| # | 子维度 | 文件 |
|---|------|------|
| 1 | 术语一致性 | [`1-terminology.md`](references/consistency-6d/1-terminology.md) |
| 2 | 交叉引用完整性 | [`2-cross-references.md`](references/consistency-6d/2-cross-references.md) |
| 3 | 规则冲突检测 | [`3-rule-conflicts.md`](references/consistency-6d/3-rule-conflicts.md) |
| 4 | 索引/指针有效性 | [`4-index-validity.md`](references/consistency-6d/4-index-validity.md) |
| 5 | 格式/前置元数据 | [`5-frontmatter.md`](references/consistency-6d/5-frontmatter.md) |
| 6 | 优先级与作用域 | [`6-priority-scope.md`](references/consistency-6d/6-priority-scope.md) |

**审计覆盖扩展 (v2.6.1, 2026-06-10)**: 2 个新检测维度, 跟 consistency-6d 互补
- **Dead Code / Orphan** → [`dead-code-orphan.md`](references/dead-code-orphan.md)
- **Commands → Skills Migration** → [`commands-to-skills-migration.md`](references/commands-to-skills-migration.md)

**Layer 3 进化层约束**：每次 `rich审计` 都必须执行外部扫描（禁止以"分数已经很高"为由跳过 WebSearch / Context7）。

**Force-All-Search Protocol v2.9 (2026-06-12 升级, 输出契约 per-tool 显式披露; 加 exa 为第 5 工具; 替换旧 Tri-Search v2.6)**:

5-tool **parallel fan-out** → merge + compare → 冲突再查 (≤2 层递归) → 输出契约

| Phase | 工具 | 角色 |
|-------|------|------|
| **A. Parallel Fan-out** | `mcp__MiniMax__web_search` ∥ `kimi-webbridge` ∥ `anysearch` ∥ `WebFetch` ∥ `exa` (`mcp__exa__web_search_exa` + `mcp__exa__web_fetch_exa`) | 5 路独立采信, 同 query (exa = combo search+fetch) |
| **B. Merge + Compare** | (内部) | 共识 (高 confidence) / 冲突 (需溯源) |
| **C. Conflict Resolve** | Phase A 递归, ≤2 层 | 冲突项再查; 仍不收敛 → 报告"未收敛"降级人工 |

**输出契约 (per-tool 显式披露, v2.9)**: 每个工具独立 1 段 (工具 / 搜索内容 / 结论 / 状态) + 共识 / 冲突 / 缺失工具分段; 5 工具**必须**全部披露, 缺/降级也要写 1 段 (状态字段标 ⚠️/❌), 不能只给合并结论. 完整模板见 [`references/force-all-search-protocol.md`](references/force-all-search-protocol.md).

**Why 5 tools**: 5 维并行 = (a) redundancy (1 tool 挂掉不影响) + (b) depth (kimi-webbridge 抓单源抓不到) + (c) cross-validation (anysearch 验证 minimax) + (d) direct fetch (WebFetch 读 top URL 全文) + **(e) algorithm/index diversity (exa 跟 MiniMax/anysearch 不重叠, 兜底独立算法/索引)**. 比 4-tool 多了 exa 这一维, 防"搜到但算法单一"假性多样.

**降级 (两层)**:
- **Layer 1 (已注册但暂不可用)**: HTTP 4xx/5xx / rate limit / timeout → 用同源工具替代, 报告标注"⚠️ <tool> <code> → <fallback>"; exa 是 combo 工具, 整体降级
- **Layer 2 (未注册 / MCP server 缺席)**: **fail-fast** — 拒绝执行 Force-All-Search, 报告"❌ BLOCKED: 缺失 N 个工具". 唯一例外: 用户显式说"接受降级"
- 完整协议 (含 5-tool 必需清单 + 检测方法) 见 [`references/force-all-search-protocol.md`](references/force-all-search-protocol.md)

---
