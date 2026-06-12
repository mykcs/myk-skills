# Force-All-Search Protocol v2.7 (2026-06-12)

> 来源: `~/.agents/skills/rich-audit/SKILL.md` v2.7 Layer 3
> 全局化: `~/.claude/rules/behavioral-process-forceallsearch.md`
> 输出契约: 工具 / 搜索内容 / 结论 (3 字段必填; Layer 2 fail-fast 时加 缺失工具)
> 重命名历史: v2.6 "Tri-Search Protocol" (2026-06-10) → v2.7 "Force-All-Search Protocol" (2026-06-12); 数字 tri(=3) 误导, 实际是 4-tool.

## Phase A: 4-way Parallel Fan-out

| 工具 | 角色 | 优势 | 局限 |
|------|------|------|------|
| `mcp__MiniMax__web_search` | primary, fast API | 大批量 query | 无浏览器 |
| `kimi-webbridge` | real browser | 抓登录/动态/issue 评论 | 慢, 需 daemon running |
| `anysearch` | cross-validate | 多源, 23 垂直域 | API key 限流 |
| `WebFetch` | direct URL fetch | 读单 URL 全文 | 需已知 URL |

## Phase B: Merge + Compare

- **共识** (≥3 源一致): 高 confidence, 直接采纳
- **冲突** (≥1 源不一致): 入 Phase C 溯源
- **数据缺口** (某工具 502/error): 不算冲突, 标注"降级"

## Phase C: Conflict Resolve (递归 ≤2 层)

1. 对冲突项用 4 工具再 fan-out 一次
2. 仍冲突 → 报告"未收敛", 降级人工
3. hard cap 2 层防无限递归

## 降级矩阵（两层）

> **核心区分**: Layer 1 = 工具已注册但暂不可用 (HTTP 4xx/5xx, rate limit, timeout) → 降级继续
>                  Layer 2 = 工具未注册 (MCP server 缺席) → **fail-fast**

### Layer 1: 已注册但暂不可用

| 不可用 | 替代 | 报告标注 |
|--------|------|----------|
| kimi-webbridge 502 | WebFetch 抓 GitHub / docs URL | `⚠️ kimi-webbridge 502 → WebFetch` |
| minimax 4xx | anysearch 替代 | `⚠️ minimax 4xx → anysearch` |
| anysearch rate limit | minimax 替代 | `⚠️ anysearch rate-limited → minimax` |
| WebFetch 404 | 跳过, 报告"URL 不可达" | `⚠️ WebFetch 404, URL 跳过` |

### Layer 2: 未注册 (MCP server 缺席)

| 场景 | 行为 | 报告 |
|------|------|------|
| 缺 1 个工具 | **fail-fast** — 拒绝执行 Force-All-Search | `❌ BLOCKED: 缺失 <tool_name> (MCP server 未注册). 请安装 MCP server 或调整 spec.` |
| 缺 ≥ 2 个工具 | **fail-fast** + 列出全部缺失 | `❌ BLOCKED: 缺失 N 个工具 [<tool1>, <tool2>, ...]. 4-tool 三角测量失效.` |

**Why Layer 2 不降级**（设计意图 "强制全用 + 交叉验证" 的硬约束）:
- 4-tool parallel fan-out 设计 = redundancy + depth + cross-validation + direct fetch **4 维并行**
- 缺 1 维 = 失去该维度兜底 (e.g. 缺 kimi-webbridge = 无 real browser 抓登录/动态页)
- 缺 2+ 维 = 三角测量失效, "强制全用 + 交叉验证" 设计意图被违反
- 静默降级到 2-tool (e.g. minimax + exa) = **"假性 full coverage"**, 输出看起来 ≥3 工具, 实际只有 1 维 cross-validate, 失去 4 维安全网
- **唯一例外**: 用户显式说"接受降级" (e.g. "用 minimax+exa 跑就行") → 才走 Layer 1 同源替代路径

**检测方法**: 启动 Phase A 前必须枚举 `available_tools` (MCP 注册表), 对照 4-tool 必需清单:
- `mcp__MiniMax__web_search` ✓
- `kimi-webbridge` (MCP skill 注册名: `kimi-webbridge`) ✓
- `anysearch` (MCP skill 注册名: `anysearch`) ✓
- `WebFetch` (Claude Code 内置 tool) ✓

缺任意一个 → 走 Layer 2 路径.

## 输出模板

```
工具: [mcp__MiniMax__web_search | kimi-webbridge | anysearch | WebFetch]
搜索内容: [query 或 URL]
结论: [1-2 句总结]
缺失工具: [Layer 2 fail-fast 时必填, e.g. "kimi-webbridge, anysearch (未注册)"]
```

## Why 4 tools (而非 1 / 3)

- **1 tool**: Run 1 (2026-06-08) 单源 WebSearch 400 error + incomplete coverage
- **3 tools (旧 cascade)**: 缺 URL 全文验证层, 易"搜到但没读"
- **4 tools (新)**: 三角测量 = redundancy + depth + cross-validation + direct fetch
- **< 4 tools (降级)**: 失去"强制全用 + 交叉验证" 设计意图, 走 Layer 2 fail-fast

## 重命名历史

| 版本 | 日期 | 名称 | 备注 |
|------|------|------|------|
| v2.6 | 2026-06-10 | Tri-Search Protocol | 数字 tri(=3) 误导实际 4-tool |
| **v2.7** | **2026-06-12** | **Force-All-Search Protocol** | 反映"强制全用 + 交叉验证" 设计意图; 同步拆降级矩阵为 Layer 1/2 |
