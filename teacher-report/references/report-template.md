# 报告模板 — 飞书 Docx v2 XML Schema

> 基于吴飞样本(2026-06-02 报告)抽出的结构骨架。LLM 按此 schema 把抓到的数据填入,生成完整 XML,再调 `lark-cli docs +create` 写入。

## 章节骨架(必含,顺序固定)

```
<title>{学校} {老师}</title>
<TL;DR callout + grid>          ← 必含,2 列布局
<hr/>
<h2>👤 1. 导师与课题组画像</h2>
  <h3>基本信息</h3>             ← 必含,table
  <h3>课题组定位</h3>            ← 必含,callout
  <h3>关键人物图谱</h3>          ← 可选,table
<hr/>
<h2>📊 2. 申博匹配度评估</h2>
  <h3>方向契合度总览</h3>       ← 必含,grid of callouts
  <h3>最相关 10 篇论文精读</h3> ← 必含,10 个子段
  <h3>方向分布与趋势</h3>       ← 必含,table + callout
<hr/>
<h2>✉️ 3. 套磁与行动建议</h2>
  <h3>推荐邮件草稿</h3>         ← 必含,callout
  <h3>需要确认的关键问题</h3>   ← 必含,bullet
  <h3>风险点</h3>              ← 必含,callout
<hr/>
<h2>📚 4. 论文产出全景(按年)</h2>
  <h3>4.1 2026 / 4.2 2025 / 4.3 2024 / ...</h3>  ← 按年倒序,table
<hr/>
<h2>ℹ️ 5. 数据来源与说明</h2>   ← 必含
```

## 1. TL;DR callout 模板

```xml
<callout emoji="🎯">
  <p><b>TL;DR 核心结论</b></p>
  <grid>
    <column width-ratio="0.500000">
      <p><b>招生匹配度</b>：🟢 <b>高</b>（方向契合 × 论文产出稳定 × 杰青导师 × 双核带生）</p>
      <p><b>关键数字</b>：近 3 年 <b>104 篇</b>｜CCF-A ~65 ｜ CCF-B ~15 ｜ Nature/Cell 3 ｜ 中文核心 ~8 ｜ 投稿中 ~13</p>
      <p><b>作者位置</b>：<b>80% 论文为通讯/末位</b> = senior PI 挂名模式(≠ 实际带生)。⚠️ 本人一作 = 0 → 实际带生高度疑为青年教师(况琨/张圣宇),需邮件追问 1v1 安排。</p>
    </column>
    <column width-ratio="0.500000">
      <p><b>核心建议</b>：直接套磁吴飞；邮件引用《OS Agents》综述 + WorldEdit / InfiGUI-R1</p>
      <p><b>风险灯号</b>：🟡 中（方向变化快；况琨可能为指导者；名额紧张）</p>
      <p><b>下一步</b>：邮件联系吴飞（cc 况琨），调研 2027 Fall 招生政策</p>
    </column>
  </grid>
</callout>
```

**填表规则**:
- 左列 3 行: 匹配度 / 关键数字 / 角色定位
- 右列 3 行: 核心建议 / 风险灯号 / 下一步
- 匹配度三档: 🟢 高 / 🟡 中 / 🔴 低
- 风险灯号三档: 🟢 低 / 🟡 中 / 🔴 高

## 2. 基本信息 table 模板

```xml
<h3>{老师}{职称}基本信息</h3>
<table>
  <colgroup><col/><col/></colgroup>
  <thead>
    <tr><th vertical-align="top"><p>项目</p></th><th vertical-align="top"><p>内容</p></th></tr>
  </thead>
  <tbody>
    <tr><td vertical-align="top"><p>姓名</p></td><td vertical-align="top"><p>{中文名}（{Pinyin}）</p></td></tr>
    <tr><td vertical-align="top"><p>职称</p></td><td vertical-align="top"><p>{学校}{职称}、博士生导师</p></td></tr>
    <tr><td vertical-align="top"><p>行政职务</p></td><td vertical-align="top"><p>{...}</p></td></tr>
    <tr><td vertical-align="top"><p>学术荣誉</p></td><td vertical-align="top"><p>国家杰出青年科学基金获得者（{年}）、...</p></td></tr>
    <tr><td vertical-align="top"><p>学术兼职</p></td><td vertical-align="top"><p>{...}</p></td></tr>
    <tr><td vertical-align="top"><p>研究方向</p></td><td vertical-align="top"><p>{3-5 个关键词，用、分隔}</p></td></tr>
    <tr><td vertical-align="top"><p>学术服务</p></td><td vertical-align="top"><p>{会议} 领域主席（Area Chair）</p></td></tr>
  </tbody>
</table>
```

## 3. 课题组定位 callout 模板

```xml
<callout emoji="👥">
  <p><b>"{老师}-{合著者}"双核心模式</b></p>
  <ul>
    <li><b>{老师}</b>：大方向、政策资源、跨学科合作</li>
    <li><b>{合著者}</b>：技术方向把控、学生日常指导、顶会论文主力产出</li>
  </ul>
</callout>
```

如果**没有明显的双核**,改成单段文字描述,不要硬塞双核。

**⚠️ 反模式(必须避免)**:如果导师本人是末位/通讯 PI、实际带生者高度疑为青年教师,**禁止**把这种情况包装成"X-Y 双核心"或"X-Y-Z 三核心"callout —— 那是把"学生代笔"美化成"团队结构"。

正确做法:在 callout 末尾用 **⚠️** 单独标一行:
> "实际带生者高度疑似 X / Y / Z,导师时间投入 < 50%,需邮件确认 1v1 带生安排。"

## 4. 方向契合度 grid 模板

```xml
<grid>
  <column width-ratio="0.250000">
    <callout emoji="🤖">
      <p><b>{方向 A}（{年}-{年}）</b></p>
      <p>{1-2 篇代表论文}</p>
      <p>→ 对应你的"{用户方向}"兴趣</p>
    </callout>
  </column>
  <column width-ratio="0.250000">
    <callout emoji="🎨">
      <p><b>{方向 B}</b></p>
      <p>...</p>
    </callout>
  </column>
  <!-- 2-4 个 column 均可,根据老师方向数量 -->
</grid>
```

## 5. 论文精读子段模板(每个论文一段)

```xml
<h4>({N}) {方向分组}（{数量} 篇）</h4>
<p><b>① {论文标题} ({venue} {year}) {⭐}</b></p>
<ul>
  <li><b>类型</b>：{Survey/原创研究/Benchmark}</li>
  <li><b>{老师}角色</b>：{末位/通讯/无/合作}</li>
  <li><b>核心贡献</b>：{一句话}</li>
  <li><b>与你关联</b>：{与用户方向的连接点}</li>
  <li><b>技术关键词</b>：{5 个英文关键词，逗号分隔}</li>
</ul>
```

**🚨 论文精读硬规则(违反 = skill 协议破坏)**:

1. **禁止作者列表** — 论文标题后**只接 `(venue year)`**,**省略**所有作者姓名 / et al. / Kun Kuang* / 通讯标记。吴飞原模板不显示作者(读者关注的是论文本身,不是作者)。

2. **venue 必须是 venue 名** — `NeurIPS 2025` / `ACL 2025` / `KDD 2026` / `ICLR 2026` / `arXiv preprint` / `ACM Computing Surveys` / `TPAMI` / `Cell Patterns` 等。**禁止**用 arXiv ID(`arXiv 2410.15319` ❌) / DOI / 通讯邮箱 / 期刊缩写作为 venue。

3. **状态标记** 在 `(venue year)` 之后空一格:
   - `⭐` = 重点关注
   - `📝` = 投稿中(submitted)
   - `⚠️` = 撤稿/被拒(withdrawn/desk-rejected)
   - `🆕` = 最新发表
   - 例:`② InfiGUI-R1: Advancing Multimodal GUI Agents from Reactive Actors to Deliberative Reasoners (ICLR 2026 Submitted) ⭐ 📝`

4. **5 字段必含 + 顺序固定**:
   - 类型(Survey / 原创研究 / Benchmark)
   - {老师}角色(末位/通讯/无/合作)
   - 核心贡献(一句话,不超 30 字)
   - 与你关联(具体到论文技术点 + 用户方向连接,**禁止**"高度契合"等空话)
   - 技术关键词(**5 个**英文逗号分隔,不是 6 个、不是中文)

5. **套磁可引用度自检** — 每篇论文精读写完后,问自己:"如果我在套磁信中引用这篇论文,我能不能**只读这两行 + 5 字段**就理解它?" 不行就改。

**反例**(我跑况琨时犯的错,以后禁止):
- ❌ `① Causality for Large Language Models(Anpeng Wu, Kun Kuang*, Minqin Zhu, et al., arXiv 2410.15319, 2024) ⭐` — 加了作者列表 + arxiv id 当 venue
- ✅ `① Causality for Large Language Models (arXiv preprint 2024) ⭐` — 完整标题 + venue 名 + 年份

**状态标记约定**:
- `⭐` = 重点关注
- `📝` = 投稿中(submitted)
- `⚠️` = 撤稿/被拒(withdrawn/desk-rejected)
- `🆕` = 最新发表

## 6. 方向分布 table 模板

```xml
<h3>大方向分布（近 3 年）</h3>
<table>
  <colgroup><col/><col/><col/></colgroup>
  <thead>
    <tr>
      <th><p>方向</p></th>
      <th><p>论文数</p></th>
      <th><p>占比</p></th>
    </tr>
  </thead>
  <tbody>
    <tr><td><p>{方向 A}</p></td><td><p>{N}</p></td><td><p>{X%}</p></td></tr>
    ...
  </tbody>
</table>
```

## 7. 套磁邮件 callout 模板

```xml
<callout emoji="💌">
  <p>建议在邮件中明确提及以下 1-2 篇论文，展示你对他课题组最新工作的了解：</p>
  <p><b>"我仔细阅读了您课题组近期在 {venue} {year} 发表的《{论文标题}》，对其中提出的 {技术点} 印象深刻。{与用户方向连接}。"</b></p>
</callout>
```

## 8. 风险点 callout 模板

```xml
<callout emoji="⚠️">
  <ul>
    <li><b>{风险类型}</b>：{具体描述}</li>
    <li><b>{风险类型 2}</b>：{...}</li>
  </ul>
</callout>
```

## 9. 数据来源章节模板

**强制**:必须在 §5 顶部放一个 ⚠️ callout 集中列出**所有 🟡 待验证字段**,让用户一眼看到决策盲区。数据缺口分散在其他章节(论文全景/行政任职/风险点)也要回收到这里。

```xml
<h2>ℹ️ 五、数据来源与说明</h2>
<callout emoji="⚠️">
  <p><b>本报告未确认的字段(影响决策)</b></p>
  <ul>
    <li>❌ {2027 Fall 招生名额 — 主页无明示,需邮件问}</li>
    <li>❌ {实际带生者(本人 vs X / Y / Z) — 仅从合著频率推断}</li>
    <li>❌ {学生名单 / 毕业去向 — 主页未公开}</li>
    <li>❌ {2024/2025 完整论文清单 — L2/L3 数据源受限时}</li>
    <li>❌ {其他未确认字段}</li>
  </ul>
</callout>
<ul>
  <li><b>主要来源</b>：{L1-L4 数据源}</li>
  <li><b>检索时间</b>：{YYYY-MM-DD}</li>
  <li><b>覆盖范围</b>：{时间窗口} 期间以 {老师} 为作者的全部可检索论文</li>
  <li><b>局限性</b>：{部分 ICLR 2026 投稿论文状态为 Submitted/Withdrawn，已如实标注；部分作者学生身份基于机构归属和合作频率推断}</li>
</ul>
<hr/>
<p>文档生成时间：{YYYY-MM-DD}</p>
<p>整理人：Mavis teacher-report skill</p>
```

## 分块写入(超长文档)

`docs +create` 单次 `--content` 体积有限制(实测 ~30 blocks)。超长时:

1. **第 1 次**:`docs +create --content '<title>...</title><TL;DR>...</TL;DR><hr/>'`
2. **第 2-N 次**:`docs +update --command append --content '<h2>...</h2>...'` 逐章节追加

每章 append 一段,失败时只重传该段,不要全量重传。

## 视觉丰富度硬要求(防止"全文字")

- TL;DR 必须 callout + grid,不能纯文字
- 每个 h3 章节必须至少有 1 个 callout / table / grid 之一
- "核心观察 / 关键判断 / 风险点" 段落必须用 callout(💡/⚠️ emoji)
- 论文精读用列表 + 加粗,不要写成大段叙述
- 表格用 `<table>` 块,**不要**用 markdown 表格(飞书 v2 API 不渲染 markdown table)

## 11. 申博 wiki dashboard 摘要模板

**用途**:每次跑完老师报告,**append 一段摘要**到"申博 wiki dashboard"主节点,让 user 在一个地方看到所有候选老师。

```xml
<hr/>
<h3>🎓 申博候选:{学校} {老师}({YYYY-MM-DD} 调研)</h3>
<table>
  <colgroup><col/><col/><col/></colgroup>
  <thead>
    <tr>
      <th><p>匹配度</p></th>
      <th><p>关键数字</p></th>
      <th><p>主风险</p></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><p>{🟢 高 / 🟡 中 / 🔴 低}({1 行理由})</p></td>
      <td><p>{近 3 年论文数 / 顶会产出 / 本人一作} </p></td>
      <td><p>{行政岗 / 方向偏 / 招生名额 / 实际带生者 等}</p></td>
    </tr>
  </tbody>
</table>
<p><b>飞书 docx 全文</b>:<a href="{report_url}">{学校} {老师}(v0.2.3 精细化报告)</a></p>
<p><b>核心建议</b>:{1 行:直接套磁 / 改推替代导师 / 暂缓}</p>
```

**填表规则**:
- 摘要 ≤ 5 行,user 扫一眼就懂要不要细读全文
- 飞书 docx 用 `<a href="...">` 链接,user 一键跳转
- "核心建议" 必含 1 个 actionable 决策
- 多个老师时,dashboard 持续 append,自然形成"申博候选池"时序

**反例**(禁止):
- ❌ 摘要超过 5 行 — 失去 dashboard 一目了然的价值
- ❌ 不带飞书 docx 链接 — user 无法跳转看全文
- ❌ 缺"核心建议" — 摘要失去决策价值
