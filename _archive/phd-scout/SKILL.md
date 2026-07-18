---
name: phd-scout
description: |
  PhD Advisor Intelligence Gatherer — 申博情报搜集系统。自动抓取清北复交浙 AI/LLM/Agent 方向导师信息，判定危险信号，写入飞书。
  Use this skill whenever the user asks to find, scout, research, or gather information about PhD advisors or mentors in Chinese universities (清华/北大/复旦/上交/浙大), especially for AI/ML/LLM/Agent research directions. This includes requests like "查找清北复交浙的 Agent 方向老师", "调研某个老师的论文和学生", "更新飞书里的导师信息", "批量抓取导师数据". Explicitly trigger when user mentions 导师/老师/PI/博导 followed by university names or AI research topics.
兼容性: Python 3.10+, aiohttp, requests, playwright, openai
---

# PhD Scout — 申博情报搜集系统

## 核心职责

对单一老师执行五级穷尽搜索，输出结构化 JSON，并调用 feishu-agent 写入飞书。

## 铁律

1. **每次只处理一位老师**。不要试图批量优化。
2. **五级 fallback 必须走完才能放弃**，每步失败必须记录具体原因。
3. **方向判定**：先关键词初筛，边界案例调用 Kimi API 二审（仅当标题/摘要完全不包含任何初筛关键词时）。
4. **危险信号严格按规则判定**，不得擅自降级。
5. **飞书写入时，若老师已存在，触发审计模式**，不要覆盖追加型字段。

## 五级搜索 SOP（严格执行）

对每位老师，按以下顺序尝试，每步失败后记录原因再进入下一步：

| 级别 | 数据源 | 失败处理 |
|------|--------|----------|
| L1 | 学校/学院官网 (Playwright 动态加载) | 记录原因 → L2 |
| L2 | Google Scholar (scholarly 库) | **可接受失败**，记录原因 → L3 |
| L3 | Semantic Scholar API | 记录原因 → L4 |
| L4 | DBLP | 记录原因 → L5 |
| L5 | 小红书/知乎 | **手动模式**，输出 `[需手动补充]` |

**L2 失败不重试**：L2 (Google Scholar) 在中国大陆网络环境下不稳定，属预期失败，直接进入 L3。

## 方向判定

### 关键词库（初筛）

**一级词**（命中即相关）：LLM, large language model, agent, multi-agent, tool learning, tool use, reasoning, chain-of-thought, in-context learning, prompt engineering, dialogue system, conversational AI, foundation model, instruction tuning, alignment

**二级词**（相关但非核心）：reinforcement learning, reward model, pre-training, fine-tuning, model compression, knowledge distillation

### Kimi API 二审规则

**仅当论文标题和摘要完全不包含任何一级词时**才调用 Kimi API 二审。降低 API 调用成本。

## 行政等级标准化（三轨体系）

| 学术轨 | 行政轨 | 人才轨 |
|--------|--------|--------|
| AP（助理教授） | 系主任 | 四青（青千/优青/青拔/青长） |
| Associate（副教授） | 副院长 | 杰青/长江 |
| Full（教授） | 院长 | 更高（千人/院士） |
| Chair（讲席） | 校级 | |
| Academician（院士） | | |

## 危险信号判定

| 信号 | 条件 |
|------|------|
| 🔴 红灯 | L1~L4 全部失败（信息黑洞） |
| 🟡 黄灯 | L1 成功，但近3年可验证论文数为 0，或方向匹配论文数为 0 |
| 🟢 绿灯 | 其他情况 |

**注意**：信号只能变好（黄→绿），不能自动变差（绿→黄/红）。变差时标记"有更新待审"。

## 输出格式

```json
{
  "name": "姓名",
  "university": "学校",
  "school": "学院",
  "raw_title": "原始头衔",
  "standardized_ranks": ["Associate", "副院长"],
  "research_tags": ["LLM", "Agent"],
  "recent_papers": [
    {"title": "...", "year": 2024, "venue": "ICCV", "citations": 50}
  ],
  "h_index": 38,
  "h_index_log": ["2026-05-20: 38"],
  "students": [
    {"name": "...", "period": "2021-2025", "status": "in_progress"}
  ],
  "collaborators": [
    {"name": "...", "affiliation": "清华", "co_paper_count": 3}
  ],
  "signal": "green",
  "abandon_reason": null,
  "confidence": 4,
  "fullness_score": 5,
  "tags": ["#高活跃", "#方向精准"]
}
```

## 审计规则（老师已存在时）

- **论文列表**：与新论文取并集，去重追加
- **h-index**：若数值变化，更新字段并追加 `h_index_log`
- **学生列表**：合并去重，更新状态
- **危险信号**：绿→黄/红 时，改为标记"有更新待审"，不自动改灯
- **行政职务变化**：自动更新，追加变更日志

## 飞书写入（lark-cli）

### Schema 自适应（核心规则）

**当目标表与标准 schema 不匹配时**，按以下流程处理，不要硬编码字段名：

1. **探测阶段**：用 `lark-cli base +field-list` 读取目标表的真实字段名和类型
2. **映射阶段**：按字段语义建立配对（姓名→name，学院→school，职称→title，等）
3. **补齐阶段**：如果目标表缺少 phd-scout 标准输出中的字段，不写入；只写能匹配上的字段
4. **记录阶段**：在执行报告中标注哪些字段无法映射（`unmapped_fields`）

**lark-cli 版本差异大**：`+record-list` 的 `--filter` flag 在 1.0.44+ 才支持，1.0.19 不支持。直接用 Python 遍历过滤（见 `src/writers/lark_writer.py:_find_by_name`）。

**响应格式**：`data.data[i]` 是值的数组（按 `data.fields` 顺序），与 `data.record_id_list[i]` 下标对齐。

### 字段语义映射优先级

按以下顺序尝试匹配（语义优先，非名称优先）：

| 语义角色 | 可能的字段名模式 | 映射到标准字段 |
|---------|----------------|--------------|
| 导师姓名 | 姓名、name、导师、老师 | `name` |
| 学校 | 大学、university、学校 | `university` |
| 学院 | 学院、school、系 | `school` |
| 职称 | 职称、title、职务、职级 | `raw_title` |
| 研究方向 | 研究方向、方向、tags、research | `research_tags` |
| 联系状态 | 联系状态、状态、contact | `contact_status` |
| 推荐优先级 | 推荐优先级、优先级、priority | `priority` |
| 方向匹配度 | 方向匹配度、匹配度 | `direction_score` |
| 近3年文章 | 近3年文章、论文、papers | `recent_papers` |
| 邮箱 | 邮箱、email、mail | `email` |
| 主页 | 主页、url、link、website | `homepage` |
| 备注 | 备注、notes、note | `notes` |

## 飞书 wiki 节点命名规范（v1, 2026-06-11）

> **所有调研老师在飞书 wiki 中创建/重命名节点时，必须遵守此规范。** 来源：2026-06-11 14:30 与用户确认 + ZJU AI 学院官方教师名录（ai.zju.edu.cn 师资队伍 - 人工智能理论与系统研究所）校核。

### 节点 title 格式

**「姓名 学院」**（例：「吴飞 人工智能学院」、「张圣宇 计算机科学与技术学院」）。

- **禁止**旧格式「浙江大学 X (English Name)」（如「浙江大学 吴飞 (Fei Wu)」）
- **禁止**简写（如「吴飞 AI」、「吴飞 人工智能」）
- 学院名必须是**完整标准名**（「人工智能学院」/「计算机科学与技术学院」/「软件学院」等）

### 学院归属（13 位 ZJU 老师校核后）

| 老师 | 学院 | 老师 | 学院 |
|------|------|------|------|
| 吴飞 | 人工智能学院 | 张圣宇 | 计算机科学与技术学院 |
| 况琨 | 人工智能学院 | 沈春华 | 计算机科学与技术学院 |
| 肖俊 | 人工智能学院 | 周晓巍 | 计算机科学与技术学院 |
| 赵洲 | 人工智能学院 | 刘忠鑫 | 计算机科学与技术学院 |
| 郑小林 | 人工智能学院 | | |
| 邓舒敏 | 人工智能学院 | | |
| 魏颖 | 人工智能学院 | | |
| 汤斯亮 | 人工智能学院 | | |
| 刘泽民 | 人工智能学院 | | |

> **注**：汤斯亮、魏颖、刘忠鑫 3 位归属最初被 claudecode 误判（基于 DBLP/学校招聘广告等二手源），**已由用户纠正**。ZJU AI 学院官方教师名录是 ground truth 校核源。**任何未来新增老师，请用 `person.zju.edu.cn/{pinyin}` 或 ai.zju.edu.cn/cs.zju.edu.cn 官方源核实学院归属**。

### school 字段硬编码（bitable record / queue JSONL）

- **必须**用"学院"完整名称（如"人工智能学院"、"计算机科学与技术学院"）
- **不用**"系"简写（"计算机系"已废弃）
- queue/zju_ai_queue.jsonl 等输入数据**必须**用此格式

### 创建 wiki 节点的标准流程

```bash
# 1. 用 lark-cli 创建新节点
lark-cli wiki +node-create \
  --parent-node-token "<主页面 node_token>" \
  --title "姓名 学院"  # 严格按"姓名 学院"格式

# 2. 写入 docx 内容
lark-cli docs +update --api-version v2 \
  --doc "<新 obj_token>" \
  --command overwrite \
  --content @<local.xml>

# 3. 在主页面"飞书 wiki 全文"等链接中用新 URL
```

### 修改现有节点 title（重要：飞书 API 限制）

飞书 OpenAPI **不提供 wiki nodes.update 方法**（lark-cli v1.0.50 验证 PATCH/PUT 都 404）。要修改节点 title 只能：
1. **删除旧节点** + 重建（URL/node_token 会变）— 高风险
2. 仅修改 docx 内部 `<title>` 标签（`docs +update --command str_replace`）— 飞书 UI 仍显示旧 node title

**推荐**：新增调研节点时直接用新格式；旧节点需要重命名时走"删+重建"流程。

### 灾难教训（2026-06-11）

1. **keyword-fetch-then-overwrite 灾难** — 用 `--scope keyword` fetch 拿到 287 字节截断内容，overwrite 把主页面破坏。**overwrite 前必须用默认 scope (整篇) fetch，且长度 > 1KB 才安全**。
2. **飞书 create 后鬼影节点 race condition** — 13 次 create 之后，list 缓存/异步机制产生 13 个**空白同名鬼影节点**（obj_token 新建但从未写入内容，`obj_edit_time == obj_create_time`）。**清理脚本**：`find_ghosts.py` 按 content < 5KB 判定 + `+node-delete` 全部删除。

## kimi-webbridge 抓取 ZJU 老师

**ZJU 个人主页 URL 模式**：
- `person.zju.edu.cn/{pinyin}` — 大多数老师（杨易、赵洲、宋明黎等）
- `mypage.zju.edu.cn/{pinyin}` — 部分老师（汤斯亮）
- `kunkuang.github.io` — 个人独立网站

**WebBridge session 管理**：用 `session: "zju-agent"` 隔离，结束后 `close_session`。

**抓取策略**：先 snapshot 拿基本信息，再 click "个人简介" 展开详情。无详情页时取页面静态文本。

## 错误处理

| 错误类型 | 处理方式 |
|----------|----------|
| 飞书 API 429/500/鉴权失败 | **立即停止**，打印 `🚨 FATAL`，不继续 |
| 行级字段超限 | 截断至上限，标记 `[截断]`，继续下一条 |
| L1-L4 单级失败 | 记录原因，进入下一级，不重试超过2次 |
| lark-cli 命令失败 | 查 `lark-cli --version` + `--help` 确认版本支持情况 |

## 执行命令

> **注意**：`main.py` 在 skill 目录的 `phd-scout/` 子目录中，不是 skill 根目录。

```bash
cd ~/.mavis/skills/phd-scout/phd-scout

# 单个老师
python3 main.py --mode single --name "张三" --university "清华" --school "计算机系"

# 批量处理
python3 main.py --mode batch --input ../queue/teachers.jsonl --report

# 审计已有记录
python3 main.py --mode audit --base-id <base_token> --table-id <table_id>

# 刷新表格（读取表中老师 → 五级抓取 → 回写）
python3 main.py --mode refresh --base-id <base_token> --table-id <table_id>
```

## 学生去向推断算法

从近5年合著者中筛选"学生"：
1. 同单位（非目标老师课题组的排除）
2. 非通讯作者
3. 高频出现（2+ 篇合作论文）
4. 毕业时间：从论文时间线推断

去向分类：在研 / 毕业-学术界 / 毕业-工业界 / 去向不明

## 项目结构

```
phd-scout/
├── main.py                      # CLI 入口
├── requirements.txt             # 依赖
├── config/
│   ├── universities.json       # 清北复交浙学院 URL
│   ├── keywords.json          # 方向关键词库
│   └── rank_mapping.json      # 行政等级映射
├── src/
│   ├── orchestrator.py        # 主循环
│   ├── auditor.py            # 审计合并逻辑
│   ├── fetchers/             # 五级数据源
│   │   ├── university.py     # L1
│   │   ├── scholar.py        # L2
│   │   ├── semantic_scholar.py # L3
│   │   ├── dblp.py          # L4
│   │   └── social.py         # L5
│   ├── analyzer/             # 分析器
│   │   ├── direction.py      # 关键词 + Kimi 二审
│   │   ├── rank_standardize.py
│   │   └── student_tracker.py
│   └── writers/
│       └── lark_writer.py    # 飞书写入
├── queue/                     # 待处理队列（JSONL）
└── output/{errors,reports}   # 错误和报告
```
