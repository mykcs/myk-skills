# Weekly Digest 输出 Schema (top 20 + 周报附件)

> **触发**: weekly 深扫 (周日 20:00 CST 跑, 7 天池子 + 7 维评分 + 跨子方向串联).
> **消费方**: `digest-publish.sh --mode=weekly` 写 Bitable + 周报 md 附件.

## scored jsonl 文件结构 (跟 daily 同, 但覆盖 7 天)

```json
{
  "arxiv_id": "2509.25123",
  "title": "...",
  "fetched_at": "...",
  "rank_in_week": 1,
  "weekly_trend": "rising|stable|declining",
  ...
}
```

---

## top 20 选规则

1. **primary sort**: composite_score desc (跟 daily 同)
2. **secondary sort**: weekly_trend (rising 优先) + subarea diversity (≤ 3 篇/子方向, 覆盖广)
3. **filter**:
   - composite_score >= 3
   - source != github OR stars > 200
   - 至少有 1 个 user 长期关心的 subarea

---

## 周报 md 文件结构

```markdown
# Weekly AI Digest — 2026 Week 27 (2026-06-29 至 2026-07-05)

> **生成**: 2026-07-05 20:00 CST
> **覆盖**: 7 days × 5 sources × dedup → 87 candidates → top 20
> **聚合**: subarea 分布 / 综合评分分布 / 慎引数量

---

## §1 Top 5 (本周最值得读的 5 篇)

[自动从 daily top 5 取 7 天最高分]

| # | 标题 | 子方向 | 综合分 | 来源 |
|---|------|--------|--------|------|
| 1 | Self-Evolving Agents: A Survey | self-evolving | 4.1 | arXiv |
| 2 | Robin | multi-agent | 4.0 | arXiv |
| 3 | Kosmos | multi-agent | 3.9 | arXiv |
| 4 | Anthropic: Building effective agents | agentic-protocol | 3.8 | blog |
| 5 | PaperSorter 0.3 | benchmark | 3.6 | github |

---

## §2 子方向全景 (本周 7 个 subarea 覆盖 + 评分)

| subarea | paper 数 | 综合分 avg | 状态 |
|---------|---------|-----------|------|
| self-evolving | 5 | 4.0 | 🔥 爆发期 |
| multi-agent | 4 | 3.8 | 📈 上升 |
| benchmark | 3 | 3.5 | 📊 稳定 |
| skill | 3 | 3.4 | 📊 稳定 |
| failure | 2 | 3.7 | 📈 上升 |
| reasoning | 2 | 3.2 | ➖ 待跟进 |
| tool | 1 | 3.0 | 🆕 新出 |

---

## §3 慎引清单 (≤ 3 分, 通常 2-3 篇)

| 标题 | 综合分 | 风险点 |
|------|--------|--------|
| AutoLLM v0.5 | 2.5 | 老模型 + 不维护 |
| HN 转载某个 stat | 2.0 | 非原始来源 |

---

## §4 待补 / 真读 pending (本周 pending 数量)

| 标题 | 风险点 |
|------|--------|
| Robin 完整 50 页 | 周末读 |
| Kosmos 完整 60 页 | 真读校准 |

---

## §5 本周新出现的 trend (跟上周对比)

- **rising**: failure 模式 (Hidden Pitfalls + Hartmann)
- **declining**: pure benchmark (被 7 维评分把 venue 权重降低)
- **new**: "agentic foundation model" (Sakana v2 + Andrew White)

---

## §6 来源 stat (本周 fan-out 抓源成功率)

| source | 抓取 | 去重后 | 通过率 |
|--------|------|--------|--------|
| arxiv | 35 | 28 | 80% |
| venue (NIPS/ICML) | 8 | 8 | 100% |
| blog-rss | 12 | 10 | 83% |
| hn | 22 | 11 | 50% (过滤掉 joke) |
| github | 15 | 3 | 20% (过滤掉小项目) |
| **汇总** | **92** | **60** | **65%** |

---

## 📎 附件

- **周报 md URL**: <github.com/mykcs/weiying20260624/blob/main/weekly/2026-W27.md>
- **Bitable Weekly record**: <link to Weekly.papers>
- **scored jsonl**: `~/.cache/digest/scored-2026-W27.jsonl`
```

---

## weekly 输出表格 (Bitable 视图)

| # | 字段 | 值来源 |
|---|---|---|
| 1 | week_id | `2026-W27` |
| 2 | period | range (start_date + end_date) |
| 3 | theme | 周最强 subarea |
| 4 | papers | DuplexLink (20 篇) |
| 5 | report_md_url | github URL (auto-generated) |
| 6 | fetch_count | 92 (raw 抓取数) |
| 7 | top_paper_score | max(composite_score) = 4.1 |
| 8 | digest_status | published |
| 9 | published_date | 写表时间 |

---

## 周报 md 仓库策略

- 推荐位置: `weiying20260624/weekly/<week-id>.md`
- 跟 paper_note 一起 version control
- 1 行 `git add weekly/ && git commit -m "weekly: 2026-W27 digest (87 candidates, 20 top)"` 即可

---

## 🔧 digest-publish.sh --mode=weekly 实现 (pseudo-code)

```bash
#!/bin/bash
MODE="${1:-weekly}"

# 1. 跑 scored-7d.jsonl (过去 7 天 score 全部 paper)
jq -r 'select(.fetched_at > (now - 7*86400))' scored.jsonl > scored-7d.jsonl

# 2. 选 top 20 (composite + subarea diversity)
TOP=$(jq -r '. | sort_by(-.composite_score) | .[0:20]' scored-7d.jsonl)

# 3. 生成周报 md (per 上面 schema)
cat > weekly/2026-W27.md <<EOF
# Weekly AI Digest — 2026 Week 27
...
EOF

# 4. 写 Bitable Weekly 表 + 关联 Paper 表
lark-cli base create_record --table_id "$TABLE_ID_WEEKLY" --fields "{week_id, period, papers: ...}"

# 5. git push 周报 md
git add weekly/ && git commit -m "weekly: $week_id digest" && git push
```

---

## 🔗 相关

- `~/.agents/skills/auto-feishu-digest/templates/daily-digest.md` (浅版)
- `~/.agents/skills/auto-feishu-digest/SKILL.md` §双轨
- `~/.agents/skills/auto-feishu-digest/scripts/digest-publish.sh` (实现)
