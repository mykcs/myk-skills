# Tri-Search Protocol v2.6 (2026-06-10)

> 来源: `~/.agents/skills/rich-audit/SKILL.md` v2.6 Layer 3
> 全局化: `~/.claude/rules/behavioral-process.md` §E
> 输出契约: 工具 / 搜索内容 / 结论 (3 字段必填)

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

## 降级矩阵

| 不可用 | 替代 |
|--------|------|
| kimi-webbridge 502 | WebFetch 抓 GitHub / docs URL |
| minimax 4xx | anysearch 替代 |
| anysearch rate limit | minimax 替代 |
| WebFetch 404 | 跳过, 报告"URL 不可达" |

## 输出模板

```
工具: [mcp__MiniMax__web_search | kimi-webbridge | anysearch | WebFetch]
搜索内容: [query 或 URL]
结论: [1-2 句总结]
```

## Why 4 tools (而非 1 / 3)

- **1 tool**: Run 1 (2026-06-08) 单源 WebSearch 400 error + incomplete coverage
- **3 tools (旧 cascade)**: 缺 URL 全文验证层, 易"搜到但没读"
- **4 tools (新)**: 三角测量 = redundancy + depth + cross-validation + direct fetch
