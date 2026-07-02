# Daily Digest 输出 Schema (top 5 表格写入)

> **触发**: daily 浅扫完成 (5 source fan-out → dedup → 7 维 LLM judge), 必产出本格式 scored jsonl.
> **消费方**: `digest-publish.sh --mode=daily` 真写飞书 Bitable.

## scored jsonl 文件结构 (1 行 1 paper)

```json
{
  "arxiv_id": "2509.25123",
  "title": "Self-Evolving Agents: A Survey",
  "url": "https://arxiv.org/abs/2509.25123",
  "source": "arxiv",
  "authors": ["Wei Lab", "Zheng Wei"],
  "venue_score": 4,
  "author_score": 5,
  "code_score": 4,
  "dataset_score": 4,
  "number_score": 4,
  "citation_score": 3,
  "match_score": 5,
  "composite_score": 4.1,
  "caution_flag": "✅ 可引",
  "subareas": ["self-evolving", "multi-agent"],
  "summary": "<1-2 句中文翻译 + 关键 insight>",
  "fetched_at": "2026-07-02T08:00:00+08:00",
  "reason_to_care": "<1 句, 为什么您应该读>"
}
```

---

## daily 输出表格 (5 字段 view, Bitable 默认 view)

| # | Bitable 字段 | 来自 scored jsonl |
|---|---|---|
| 1 | title | `title` |
| 2 | url | `url` |
| 3 | source | `source` (SingleSelect) |
| 4 | composite_score | `composite_score` (Formula 自动算) |
| 5 | reason_to_care | `summary` (Text 多行) |

---

## top 5 选规则 (sorted by composite_score desc)

```bash
# digest-publish.sh 内部逻辑
jq -r '.[] | select(.composite_score >= 3) | .title' scored.jsonl \
  | head -5
```

**过滤条件** (per 7 维评分语义):
- composite_score >= 3 (慎引以上)
- source != "github" OR stars > 100 (GitHub 源过滤)
- subareas 至少 1 个跟 user 当前周关联

---

## 📊 daily 推送示例 (格式参考)

```markdown
# 🌅 2026-07-02 AI Daily Digest (Top 5)

📊 本日评分分布: 4.1 / 4.5 / 3.8 / 3.5 / 3.2 (top 5 平均 3.8)

| # | 标题 | 子方向 | 评分 | 来源 | 摘要 |
|---|------|--------|------|------|------|
| 1 | Self-Evolving Agents: A Survey | self-evolving / multi-agent | 4.1 ✅ | arXiv | 综述近 3 年奠基 paper, 5 代际演进... |
| 2 | Robin: lab-in-the-loop multi-agent | multi-agent / wet-loop | 4.0 ✅ | arXiv | FutureHouse ripasudil dAMD 案例... |
| 3 | Anthropic: Building effective agents | skill / agentic-protocol | 3.8 ✅ | blog-rss | 4 类 agent + 4 反模式... |
| 4 | HN: Show HN: paper-digest v2 launch | benchmark / tool | 3.5 ⚠️ | hn | 80 stars 开源, 借鉴 LLM-as-judge... |
| 5 | GitHub: awesome-self-evolving-agents trending | self-evolving / tool | 3.2 ⚠️ | github | 500+ stars 周增 100... |

🎯 user 视角: 1 篇综述 + 1 篇案例 + 1 篇方法 + 1 篇工具 + 1 篇社区趋势
```

---

## 🔧 digest-publish.sh 写表实现 (pseudo-code)

```bash
#!/bin/bash
MODE="${1:-daily}"
TOP_N=$([ "$MODE" = "daily" ] && echo 5 || echo 20)

# 1. 读 scored jsonl
PAPERS=$(jq -r ". | select(.composite_score >= 3)" scored.jsonl | sort -t, -k4 -nr | head -$TOP_N)

# 2. 写 Bitable Paper 表
echo "$PAPERS" | while read -r paper; do
    lark-cli base create_record --app_token "$BAPP_TOKEN" --table_id "$TABLE_ID_PAPER" --fields "$paper"
done

# 3. 更新 Weekly 表 (daily also writes to current Weekly.papers for aggregation)
if [ "$MODE" = "daily" ]; then
    WEEK_ID=$(date +%G-W%V)
    lark-cli base update_record --record_id "$WEEKLY_RECORD_ID" --fields '{"papers": [...]}'
fi
```

---

## 🔗 相关

- `~/.agents/skills/auto-feishu-digest/templates/weekly-digest.md` (深度版, 20 篇 + 周报附件)
- `~/.agents/skills/auto-feishu-digest/templates/feishu-bit-schema.md` (Bitable 字段定义)
- `~/.agents/skills/auto-feishu-digest/scripts/digest-publish.sh` (实现)
