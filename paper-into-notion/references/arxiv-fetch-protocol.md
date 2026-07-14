# arxiv-fetch-protocol.md — arXiv API + ElementTree 解析协议

> **核心约束**: 1 req / 3s rate limit (arXiv 官方)
> **重试策略**: 3 次失败 → exit 1, 不写 fallback record (per Q4 自修复)

---

## §1 API endpoint

```
GET https://export.arxiv.org/api/query?id_list=<ID>&max_results=1
```

**参数**:
| 参数 | 说明 | 必填? |
|---|---|---|
| `id_list` | arXiv ID (e.g. `1706.03762` 或 `cs.AI/0612345`) | ✅ |
| `max_results` | 返回最大条目数 | 推荐 1 (单 ID 查询) |
| `start` / `max_results` | 分页 (本次不用) | ❌ |

---

## §2 返回格式 (Atom XML)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <id>http://arxiv.org/abs/1706.03762v7</id>
    <title>Attention Is All You Need</title>
    <summary>The dominant sequence transduction models...</summary>
    <author><name>A. Vaswani</name></author>
    <author><name>N. Shazeer</name></author>
    ...
    <published>2017-06-12T17:57:34Z</published>
    <updated>2023-08-02T11:13:45Z</updated>
    <category term="cs.CL" />
    <link href="http://arxiv.org/abs/1706.03762v7" rel="alternate" type="text/html"/>
  </entry>
</feed>
```

**ElementTree 解析路径**:
```python
ns = {'atom': 'http://www.w3.org/2005/Atom'}
root = ET.fromstring(response_text)
entry = root.find('atom:entry', ns)
title = entry.find('atom:title', ns).text
authors = [a.find('atom:name', ns).text for a in entry.findall('atom:author', ns)]
abstract = entry.find('atom:summary', ns).text
```

---

## §3 rate limit + 重试

### §3.1 arXiv 官方约束

> arXiv API 没有公开的 rate limit 文档, 但实测 1 req / 3s 是软约束 (per 多次 burst 测试)

### §3.2 重试策略 (per Q4)

```bash
for i in 1 2 3; do
  RESPONSE=$(curl -fsSLG "$URL" 2>/dev/null) && break
  sleep ${ARXIV_RATE_LIMIT_SEC:-3}
done

# 3 次失败 → exit 1 (per Q4: 不写 fallback record)
[ -z "$RESPONSE" ] && { echo "❌ arXiv 抓取失败 (3 次重试)" >&2; exit 1; }
```

### §3.3 429 Too Many Requests 处理

如果 burst 多次请求, arXiv 会返 429:
```bash
# 检测 429
if echo "$RESPONSE" | grep -q "429 Too Many Requests"; then
  sleep 10  # 等更久
  # 重试
fi
```

**为什么 sleep 10s**: arXiv 没公开文档, 实测 10s 通常够 (vs 3s 默认不够)

---

## §4 错误处理

| 错误 | 处理 |
|---|---|
| 网络 timeout | curl `-fsSLG`, 自动 retry 3 次 |
| arXiv ID 不存在 | Atom XML 无 `<entry>`, ElementTree `.find('atom:entry', ns)` 返 None |
| arXiv rate limit (429) | sleep 10s, 重试 |
| ElementTree parse error | 跳过 entry, 报错 |
| 3 次重试都失败 | exit 1, 不写 fallback (per Q4) |

---

## §5 已知 arXiv ID pattern

| Pattern | 例 |
|---|---|
| Old (pre-2007) | `cs.AI/0612345` (带 category 前缀) |
| New (2007+) | `1706.03762` (YYMM.NNNNN) |
| 带 version | `1706.03762v7` (queries 自动 ignore v 后缀) |

**regex 提取**:
```bash
# 提取 ID from URL
URL="https://arxiv.org/abs/1706.03762"
ID=$(echo "$URL" | grep -oE '[0-9]{4}\.[0-9]{4,5}' | head -1)
# → 1706.03762
```

---

## §6 与 Notion 字段映射

| arXiv 字段 | Notion 字段 | 自动填? |
|---|---|---|
| `<title>` | 页面 (title) | ✅ |
| `<author>` × N | (Notion schema 暂不支持, 后填) | ❌ |
| `<summary>` | (放 rich_text 亮点) | ❌ 后填 |
| `<published>` | (放 paper card "date") | ❌ 后填 |
| `<category>` | (放 multi_select 知识点) | ❌ 后填 |
| `<link rel="alternate">` | (放 paper card "Code/Link") | ❌ 后填 |

**paper-into-notion skill 只填 Notion 3 auto 字段** (页面 / 状态 / 模态类型), 其他 arXiv 信息由 user 在 Notion UI 后填, 或由 weekly-report-phd skill 输出 paper card.

---

## §7 反模式

| # | 反模式 | 真因 | 正确做法 |
|---|---|---|---|
| 1 | arXiv 抓失败写 fallback record (per Q4) | "留空也比没 record 好" | exit 1 + 报错, skill 必自修复 (per Q4) |
| 2 | 用 URL 当 title (fallback) | 偷懒 | arXiv 必须抓真 title, 其他模态才用 URL 当 fallback |
| 3 | 不 retry 一次失败就 exit | 短暂网络抖动 | 重试 3 次 + sleep 3s |
| 4 | 解析失败返回 partial JSON | LLM 拿到 partial data 写错 | exit 1, 不写 partial |
| 5 | 没设 User-Agent 被 arXiv 拒 | arXiv 偏好 UA | curl 加 `-H "User-Agent: paper-into-notion/1.0"` (实测可选) |