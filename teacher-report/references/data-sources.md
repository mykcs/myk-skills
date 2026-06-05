# Data Sources — 四级抓取细节

> Step 1 用。优先级 L1 → L2 → L3 → L4(实际跳过 Google Scholar,L2 改为 Semantic Scholar)。

## L1 — 学校/学院官网

**适用场景**: 拿老师中文姓名 + 学校 + 学院 → 拿基本信息、职称、行政职务、邮箱、研究方向。

**URL 模式(中英文大学各异,以下是常用模式)**:

| 学校 | URL 模式 | 备注 |
|------|---------|------|
| 浙江大学 | `person.zju.edu.cn/{pinyin}` | 大多数老师 |
| 浙江大学 | `mypage.zju.edu.cn/{pinyin}` | 部分老师(如汤斯亮) |
| 浙江大学 | `cs.zju.edu.cn/{year}/{month}/{name}` | 学院新闻页里的个人介绍 |
| 清华大学 | `iiis.tsinghua.edu.cn/{pinyin}` 或 `cs.tsinghua.edu.cn/info/{id}/{name}.htm` | 域名分散,先 `web_search` |
| 北京大学 | `ai.pku.edu.cn/{pinyin}.htm` 或 `eecs.pku.edu.cn` 教师列表 | 静态页,直接 `webfetch` |
| 复旦大学 | `faculty.fudan.edu.cn/{pinyin}` | |
| 上海交通大学 | `cs.sjtu.edu.cn/FacultyShow/{id}` 或 `faculty.sjtu.edu.cn/{pinyin}` | |

**抓取策略**:
1. 先 `webfetch` 拿静态 HTML;失败或明显是 SPA 框架(<div id="app"></div>),改 `playwright` MCP 的 `browser_navigate` + `browser_snapshot`
2. 提取字段: 中文姓名 / 职称 / 行政职务 / 邮箱 / 电话 / 研究方向关键词 / 代表性论文 5-10 篇
3. 找不到个人页时,fallback 到学院教师列表页 → grep 名字 → 拿该卡片内的信息

**失败兜底**:
- 抓不到主页 → 记录 `L1 失败原因:{原因}` → 跳 L2
- 抓到了但内容空洞(只一行"教授,博士生导师")→ 仍算 L1 部分成功,基本信息填表用,其他字段从 L2 补

## L2 — Semantic Scholar API

**适用场景**: 拿英文论文清单、h-index、合作者。**不依赖国内网络**。

**API**:

```bash
# 1. 搜作者 ID
curl "https://api.semanticscholar.org/graph/v1/author/search?query={name}&fields=name,affiliations,paperCount,hIndex,homepage,url"

# 2. 拿论文清单
curl "https://api.semanticscholar.org/graph/v1/author/{author_id}/papers?fields=title,year,venue,citationCount,authors,externalIds&limit=100"
```

**字段提取**:
- `paperCount`、`hIndex` → TL;DR "关键数字"
- 论文列表 → 论文全景章节
- `authors[*].name` → 合作者图谱(高频出现 = 学生)
- `externalIds.DOI` / `externalIds.ArXiv` → 套磁信引用

**rate limit**: 默认 100 RPS,实测偶尔 429 → 失败时 sleep 5s 重试 1 次。

**429 仍未恢复**: 跳 L3 DBLP。

## L3 — DBLP

**适用场景**: 论文 venue 标准化(给 CCF-A/B 标),补 L2 漏的 paper。

**API**:

```bash
# 1. 找 dblp pid
curl "https://dblp.org/search/author/api?q={name}&format=json"

# 2. 拿完整论文列表
curl "https://dblp.org/pid/{pid}.xml"
```

**字段提取**:
- `<year>` → 按年统计
- `<booktitle>` / `<journal>` → venue 名(CCF 等级需要本地映射表,见 `references/ccf-mapping.md` — **v0.1 暂不实现 CCF 映射**,报告里只写 venue 不写 CCF-A/B)
- 多个 pid 时 → 取 paperCount 最大的

**失败兜底**:
- DBLP 找不到 → L2 + 个人 L4 凑合
- DBLP 数据少(< 5 篇)→ 大概率名字错,Google 一下 `{name} {university}` 找正确英文名

## L4 — 个人主页 / 知乎 / 谷歌学术

**适用场景**: L1-L3 拿不到的信息(学生名单、研究亮点、跨学科合作)。

**方法**:
- `web_search` 关键词: `"{老师中文名}" "{学校}" 主页` / `"{老师中文名}" {university} site:github.io` / `"{老师中文名}" scholar`
- 命中后 `webfetch` 拉页面 → 提取学生 / 代表工作 / 简历

**注意**:
- 谷歌学术在国内不稳定,失败不重试
- 知乎答案不直接采信,只作为"该老师风评"线索

## ZJU 老师特别补充

- 个人主页 URL 模式见上表
- 学院教师列表: `https://www.cs.zju.edu.cn/jsjy/17474/list.htm`(教授)
- 学工新闻: `https://www.cs.zju.edu.cn/` → 按时间找

**经验**:
- 青年教师(AP/副研)优先在 `cs.zju.edu.cn` 找,老教师优先 `person.zju.edu.cn`
- 行政职务高的老师(院长/副院长)→ 必有独立主页,优先 L1
- 跨学科合作多的老师(法律 AI / 教育 AI)→ Google 搜 `{领域} 浙大 {老师名}`,新闻稿常含合作论文

## 数据合并规则

| 字段 | 优先级 |
|------|-------|
| 中文姓名 / 学校 | 用户输入(权威) |
| 职称 / 行政职务 | L1 > L4(以学校官网为准) |
| 邮箱 | L1 > L4(以个人主页为准;不要用 arXiv 论文猜) |
| h-index | L2(实时数据) > L1(可能过期) |
| 论文清单 | L2 + L3 取并集去重(按 DOI / 标题) |
| CCF 等级 | **v0.1 不实现,留 v0.2** |
| 学生名单 | L4 优先(从合著论文高频作者 + 主页"学生"页面) |

**冲突处理**: L1 与 L2 h-index 差 > 5 → 报告"5. 数据来源"注明两者差值,取 L2。
