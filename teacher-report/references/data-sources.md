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
| 中国科学院 | `people.cas.cn/...` 或 `{lab}.cas.cn/...` 或 `ia.cas.cn/yjsjy/dsfc/` | 自动化所/计算所/软件所等子站各异,先 `web_search "{name} 中科院"` |
| 南京大学 | `cs.nju.edu.cn/people/{pinyin}.htm` 或 `lamda.nju.edu.cn/{pinyin}` | LAMDA 等实验室有独立子站 |
| 中国科学技术大学 | `staff.ustc.edu.cn/~{pinyin}/` 或 `cs.ustc.edu.cn/.../{name}.htm` | 老教师多在 staff 子域 |
| 香港中文大学 | `cse.cuhk.edu.hk/~{pinyin}/` | |
| 香港科技大学 | `cse.hkust.edu.hk/~{pinyin}/` | |
| Stanford | `cs.stanford.edu/people/{pinyin}` 或 `web.stanford.edu/~{pinyin}/` | 老教师多在 web 子域 |
| MIT CSAIL | `people.csail.mit.edu/{pinyin}/` | 缺人脸主页时试 CSAIL People |
| MIT EECS | `www.eecs.mit.edu/people/{pinyin}` | |
| UC Berkeley | `people.eecs.berkeley.edu/~{pinyin}/` 或 `bair.berkeley.edu/people/{pinyin}/` | BAIR / EECS 双路径 |
| CMU | `www.cs.cmu.edu/~{pinyin}/` | 多学院(MLD/LTI/HCII),先 web_search 定位学院 |
| Caltech | `www.cms.caltech.edu/people/{pinyin}` 或 `thesis.library.caltech.edu` 找学生反推 | CMS / EE 跨系 |

**抓取策略**:
1. **先 `webfetch` 拿静态 HTML**;失败或明显是 SPA 框架(`<div id="app"></div>` 标记或 `<script>` 渲染),改 `playwright` MCP 的 `browser_navigate` + `browser_snapshot`
2. 提取字段: 中文姓名 / 职称 / 行政职务 / 邮箱 / 电话 / 研究方向关键词 / 代表性论文 5-10 篇
3. 找不到个人页时,fallback 到学院教师列表页 → grep 名字 → 拿该卡片内的信息
4. **英文大学**常常没有静态 HTML,直接走 `web_search` + L4(个人主页 / Google Scholar / DBLP 拿基本信息)

**失败兜底**:
- 抓不到主页 → 记录 `L1 失败原因:{原因}` → 跳 L2
- 抓到了但内容空洞(只一行"Professor, PhD Advisor")→ 仍算 L1 部分成功,基本信息填表用,其他字段从 L2 补

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

## 关键词库(PhD 方向匹配)

> v0.2.6 新增(2026-06-05)。User 当前 PhD 方向是 **CV + medical imaging (echocardiography video segmentation, OSA, GDKVM)** + **LLM/Coding Agent** 双轨。

**用户方向 (myk, 2026-06-05)**:
- CV/medical imaging:echocardiography, cardiac MRI, ultrasound, video segmentation, semi-supervised, domain adaptation
- LLM/Agent:Large Language Model, agent, multi-agent, tool use, reasoning, prompt engineering, code generation, RAG
- 跨方向 medical LLM:Medical LLM, clinical NLP, medical VQA, Med-PaLM-style

**匹配判定**(v0.2.6 简化版):
- **🟢 高匹配**:老师研究方向与用户任一方向 ≥ 2 个近 3 年论文重叠
- **🟡 中匹配**:1 个重叠,或方向相邻(如"医学影像"与"医学 LLM"相邻)
- **🔴 低匹配**:0 重叠,方向无关(例如纯 NLP 老师 vs 用户 CV 方向)

**禁止在报告中估算匹配度** — 必须基于 L2 抓到的近 3 年论文关键词聚类,精确给到方向-方向,而不是"大致相关"。

## CCF mapping (deferred, v0.2 待实现)

> **状态**:**v0.1 不实现 CCF-A/B 标注**。LLM 估算的 "CCF-A 65" 不可信(把 ICLR submitted 当 CCF-A、把 Nature 子刊当 Nature、把 ACM Computing Surveys 当 CCF-A 等反例)。

**v0.2 实现方案**:
1. 维护 `references/ccf-mapping.json` 静态表(DBLP venue → CCF 等级),定期从 https://www.ccf.org.cn/Academic_Evaluation/By_category/ 同步
2. LLM-prompt.md §2 改:`{DBLP venue} → ccftable[venue] → CCF-{A|B|C|null}` 精确查询
3. 报告中 CCF 等级只从这张表出,LLM 不参与判断

**v0.1 临时处理**:报告**只写 venue 名**(NeurIPS / ICLR / TPAMI),**不写 CCF-A/B**。**禁止** LLM 自行标 CCF-A/B(违反 = skill 协议破坏)。
