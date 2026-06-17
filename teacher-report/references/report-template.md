---
name: teacher-report-template
description: |
  飞书 docx v0.13.6 单一权威模板 (2026-06-17 重写). 4 章节必含 (1.1 自评 / 1.2 导师画像 / 1.3 论文全景 / 1.4 数据来源 / 1.5 套磁清单) + 1.3 A/B/C 论文重组 + P0/P1/P2 标签 + 主动 WebFetch 主页. 替代 v0.5.0 旧模板 (含 §1.4 套磁). 触发: 解决 output-contract.md 与原 report-template.md 互相矛盾问题.
---

# teacher-report 飞书 docx v0.13.6 模板

> **核心变更 (v0.13.6, 2026-06-17)**: 4 章节必含 (TL;DR + 1.1/1.2/1.3/1.4/1.5) + 1.3 A 顶会 10 / 1.3 B 主题表 / 1.3 C 趋势 + 1.4.3 P0/P1/P2 待补 + 1.5 套磁清单 + 主动 WebFetch 主页 + 无装饰 emoji + 长编号 h2 `1.X.` + 无水印.

## 章节骨架 (v0.13.6, 必含, 顺序固定)

```
<title>{学校} {老师}</title>
<TL;DR callout + grid>            ← 必含, 2 列布局 (不含 chat preamble)
<h2>1.1. 自评</h2>                ← user-owned v0.9.0, claudecode 禁止写入
  <p>[自评内容由用户填写 — claudecode 不得修改此章节, 除非用户明说]</p>
<h2>1.2. 导师与课题组画像</h2>
  <h3>1.2.1. 基本信息与学术身份</h3>    ← table 9 行 (姓名/职称/单位/行政职务/学术荣誉/学术兼职/研究方向/主页/邮箱) + 主动 WebFetch 主页
  <h3>1.2.2. 研究方向与近年课题</h3>    ← L1 + S2 抓取
  <h3>1.2.3. 招生偏好 [L7 社区来源]</h3>
  <h3>1.2.4. 培养模式 [L7 社区来源]</h3>
  <h3>1.2.5. 科研资源</h3>
<h2>1.3. 论文产出全景
  <callout> 数据快照 (论文数/时间跨度/主领域) </callout>
  <h3>1.3.A. 顶会代表作 (10 篇)</h3>     ← NEW v0.13.0: 按 oral/spotlight/BP 选
  <h3>1.3.B. 其他论文 (按 5-7 主题汇总表)</h3>  ← NEW v0.13.0
  <h3>1.3.C. 趋势分析 (近 3 年方向漂移)</h3>    ← NEW v0.13.0
<h2>1.4. 数据来源与说明</h2>
  <h3>1.4.1. L1-L4 论文类数据源</h3>
  <h3>1.4.2. L7 社区类数据源</h3>
  <h3>1.4.3. 🟥 P0/P1/P2 待补字段汇总</h3>      ← NEW v0.13.0: 单一路径, 全 doc 待补集中
<h2>1.5. 套磁准备清单 (基于 §1.1-§1.4 综合)</h2>   ← NEW v0.13.0: 替代 v0.5.0 旧 §1.4 套磁
  <h3>1.5.1. 24h 内必做的 5 件事</h3>
  <h3>1.5.2. 1v1 必问 5 题 (覆盖 §1.2.3 + §1.2.5 缺失字段)</h3>
  <h3>1.5.3. 发信时窗 + 邮件模板要点</h3>
  <h3>1.5.4. 备份计划 (若老师无名额 / 1v1 无回复)</h3>
```

> **🚨 h2/h3 顺序硬规则 (2026-06-10 加入, 来源: 邓舒敏 v0.3.5→v0.4.0 case)**
>
> **h2 必须在它 h3 子节之前出现**, 禁止 5 个 h2 集中在 doc 开头然后 body 全部接在后面. 视觉上每节是 `h2 + h3* + body*` 紧邻结构, 不是 `h2 h2 h2 h2 h2 + h3* + body*` 分离结构.
>
> 飞书 docx 渲染按 XML 物理顺序展示, 若 5 h2 集中开头, 视觉上 = 5 个空 § 标题连排, 然后 §5 body 突然出现, 看起来"§5 内容跑了 2 轮" + "重复一轮又一轮".
>
> **正确 XML 顺序 (LarkDoc v2)**: 严格按上面的章节骨架顺序, h2 后面紧跟其 h3 + body, 再到下一个 h2.
>
> **LLM 自检规则** (写完 docx 必跑):
> 1. `grep -c '<h2>' content` = 5 (1.1/1.2/1.3/1.4/1.5)
> 2. 顺序: 按 h2 编号 1.1→1.2→1.3→1.4→1.5 在 content 中必须按出现顺序, 每个 h2 紧邻其 h3 子节 (而非孤立)
> 3. 5 个 h2 不连续出现在 doc 前 5% 长度内

---

## 1. TL;DR callout 模板

```xml
<callout>
  <p><b>TL;DR 核心结论</b></p>
  <grid>
    <column width-ratio="0.500000">
      <p><b>招生匹配度</b>: 🟢 <b>高</b> (方向契合 × 论文产出稳定 × 杰青导师 × 双核带生)</p>
      <p><b>关键数字</b>: 近 3 年 <b>104 篇</b> | CCF-A ~65 | CCF-B ~15 | Nature/Cell 3 | 中文核心 ~8 | 投稿中 ~13</p>
      <p><b>作者位置</b>: <b>80% 论文为通讯/末位</b> = senior PI 挂名模式. ⚠️ 本人一作 = 0 → 实际带生高度疑为青年教师, 需邮件追问 1v1 安排.</p>
    </column>
    <column width-ratio="0.500000">
      <p><b>核心建议</b>: 直接套磁; 邮件引用 1.3.A 顶会 1-2 篇 + 用户方向桥接</p>
      <p><b>风险灯号</b>: 🟡 中 (方向变化快; 实际带生者不明; 名额紧张)</p>
      <p><b>下一步</b>: 邮件联系 + 1v1 问 5 题 (见 §1.5.2) + LinkedIn 找在读 PhD</p>
    </column>
  </grid>
</callout>
```

**填表规则**:
- 左列 3 行: 匹配度 / 关键数字 / 角色定位
- 右列 3 行: 核心建议 / 风险灯号 / 下一步
- 匹配度三档: 🟢 高 / 🟡 中 / 🔴 低
- 风险灯号三档: 🟢 低 / 🟡 中 / 🔴 高

**🚨 v0.11.0 Output Discipline**: TL;DR callout **只在 docx 内部**, chat 输出不重复. LLM 调 `lark-cli docs +create` 后直接输出 docx URL, 中间不输出"本报告/调研对象/招生匹配度/论文产出"4 行 preamble.

---

## 2. 1.1 自评 (user-owned)

```xml
<h2>1.1. 自评</h2>
<p>[自评内容由用户填写 — claudecode 不得修改此章节, 除非用户明说]</p>
<hr/>
```

**🚨 硬规则 (v0.9.0, 违反 = skill 协议破坏)**: claudecode 禁止往 §1.1 写入任何内容. 模板只放占位 + 警示文案. 整段自评由用户在飞书 web 端手填.

---

## 3. 1.2 导师与课题组画像

### 3.1 1.2.1 基本信息 table (v0.13.0 主动 WebFetch 主页)

```xml
<h3>1.2.1. 基本信息与学术身份</h3>
<table>
  <colgroup><col width="150"/><col width="330"/></colgroup>
  <thead>
    <tr><th><p>项目</p></th><th><p>内容</p></th></tr>
  </thead>
  <tbody>
    <tr><td><p>姓名</p></td><td><p>{中文名} ({Pinyin})</p></td></tr>
    <tr><td><p>职称</p></td><td><p>{职称} / 博士生导师 [来源: L1 主页 WebFetch 验证]</p></td></tr>
    <tr><td><p>单位</p></td><td><p>{学校} · {学院}</p></td></tr>
    <tr><td><p>行政职务</p></td><td><p>🟨 P1 待补 (1v1 问在读博士, 见 §1.4.3)</p></td></tr>
    <tr><td><p>学术荣誉</p></td><td><p>{国家XX计划 (年)} / {百人计划研究员} [来源: L1 + boshihoujob 验证]</p></td></tr>
    <tr><td><p>学术兼职</p></td><td><p>🟨 P1 待补 (1v1 问 / LinkedIn 查 alumni, 见 §1.4.3)</p></td></tr>
    <tr><td><p>研究方向</p></td><td><p>{3-5 个关键词, · 分隔} [来源: L1 主页 WebFetch 验证 {YYYY-MM-DD}]</p></td></tr>
    <tr><td><p>主页</p></td><td><p><a href="{主页URL}">{主页URL}</a> (外网镜像: <a href="{外网URL}">{外网URL}</a>)</p></td></tr>
    <tr><td><p>邮箱</p></td><td><p><a href="mailto:{邮箱}">{邮箱}</a></p></td></tr>
  </tbody>
</table>
```

**🚨 NEW v0.13.0 硬要求 (违反 = skill 协议破坏)**:
- 主页 URL **必须**由 LLM 主动调 `WebFetch <person.zju.edu.cn/{pinyin}>` 抓取, **禁止**留 ❓ 待补
- 邮箱 **必须**由 LLM 主动抓取, **禁止**留 ❓ 待补
- 抓取失败的字段, 留 🟨 P1 待补 + 抓取命令提示, **不**留 ❓
- 数据来源 URL 必填 + 抓取日期必填 (便于 audit)

### 3.2 1.2.2 研究方向与近年课题

```xml
<h3>1.2.2. 研究方向与近年课题</h3>
<p><b>核心方向</b>: {3-5 个关键词, · 分隔} [L1 主页]</p>
<p><b>子方向细分</b>:</p>
<ul>
  <li><b>{子方向1}</b>: {1 句话描述} [L1 主页 / S2 论文分类]</li>
  <li><b>{子方向2}</b>: {1 句话描述}</li>
</ul>
```

### 3.3 1.2.3 招生偏好 (L7 社区)

```xml
<h3>1.2.3. 招生偏好 [L7 社区来源]</h3>
<callout>
  <p><b>招生名额</b>: {博士每年 X 名} [社区-多源] / [社区-单源] / [🟥 P0 待补 (1v1 问, 见 §1.4.3)]</p>
  <p><b>竞争程度</b>: {申请/录取比 ≈ X:1} [社区来源] / [🟥 P0 待补 (参考 浙大CS 历年报录比)]</p>
  <p><b>本科背景偏好</b>: {偏好 985/211 / 卡本科层次 / 灵活} [社区-多源] / [L1 官网明示] / [🟨 P1 待补]</p>
  <p><b>研究方向偏好</b>: {强匹配 LLM/Agent/CV / 跨方向也收} [社区来源] / [🟥 P0 待补]</p>
  <p><b>推免/考博/申请-考核</b>: {以哪种为主, 时间节点} [官方时间]</p>
  <p><b>1v1 带生</b>: {导师亲自带 / 团队青年教师实际带} [社区来源] / [🟥 P0 待补 (套磁必问)]</p>
</callout>
<callout>
  <p><b>本节缺失字段</b>: 2027 Fall 招生名额, 实际带生者, 推免 vs 申请-考核比例</p>
  <p><b>建议补充路径</b>: 见 §1.4.3 待补字段汇总</p>
</callout>
```

### 3.4 1.2.4 培养模式 (L7 社区)

```xml
<h3>1.2.4. 培养模式 [L7 社区来源]</h3>
<callout>
  <p><b>指导频率</b>: {每周 1v1 meeting / 2 周 1 次 / 月度} [社区-多源] / [L1 主页] / [🟥 P0 待补]</p>
  <p><b>组会制度</b>: {每周组会, 学生轮流汇报 / 自由} [社区来源]</p>
  <p><b>放羊 vs push</b>: {低年级放羊 / 高年级 push} [社区来源] / [🟨 P1 待补]</p>
  <p><b>是否允许实习</b>: {允许业界 6-12 个月 / 不允许} [社区-多源] / [L1 主页] / [🟨 P1 待补]</p>
  <p><b>开题/中期/答辩节奏</b>: {博一开题, 博三中期, 博五答辩} [官方时间]</p>
  <p><b>寒暑假/节假日</b>: {正常放假 / 项目紧时无休} [社区来源]</p>
</callout>
<callout>
  <p><b>本节缺失字段</b>: 1v1 meeting 真实频率, push 程度, 实习政策灵活度</p>
  <p><b>建议补充路径</b>: 见 §1.4.3 待补字段汇总</p>
</callout>
```

### 3.5 1.2.5 科研资源

```xml
<h3>1.2.5. 科研资源</h3>
<table>
  <colgroup><col width="200"/><col width="500"/></colgroup>
  <thead><tr><th><p>维度</p></th><th><p>资源 / 说明</p></th></tr></thead>
  <tbody>
    <tr><td><p>GPU 算力</p></td><td><p>{A100 8卡/H100/课题组共享} [L1 主页] / [🟥 P0 待补 (1v1 问)]</p></td></tr>
    <tr><td><p>科研经费</p></td><td><p>{NSFC 面上/重点/杰青 + 横向项目} [L1 主页]</p></td></tr>
    <tr><td><p>数据集/设备</p></td><td><p>{领域数据集, 实验室设备} [L1 主页] / [🟨 P1 待补]</p></td></tr>
    <tr><td><p>海外合作/交流</p></td><td><p>{与 MIT/Stanford/NUS 联培} [L1 主页] / [🟨 P1 待补]</p></td></tr>
    <tr><td><p>业界实习</p></td><td><p>{MSRA/Google/字节 合作实习} [L1 主页] / [🟥 P0 待补]</p></td></tr>
    <tr><td><p>会议资助</p></td><td><p>{发表顶会全额资助 / 限额} [L1 主页] / [🟥 P0 待补]</p></td></tr>
  </tbody>
</table>
<callout>
  <p><b>本节缺失字段</b>: 实际 GPU 分配规则, 横向项目占比, 联培博士具体去向</p>
  <p><b>建议补充路径</b>: 见 §1.4.3 待补字段汇总</p>
</callout>
```


---

## 4. 1.3 论文产出全景 (NEW v0.13.0 A/B/C 重组)

### 4.0 数据快照 callout

```xml
<h2>1.3. 论文产出全景</h2>
<callout background-color="light-gray">
  <p><b>数据快照</b>: {YYYY-MM-DD} | <b>论文总数</b>: {N} | <b>时间跨度</b>: {year1-year2} | <b>主领域</b>: {top 3 方向}</p>
</callout>
```

### 4.1 1.3.A 顶会代表作 (10 篇, v0.3.0 增强格式)

```xml
<h3>1.3.A. 顶会代表作 (10 篇, 按 oral/spotlight/Best Paper 选)</h3>
<p><b>选稿标准</b>: ICLR/NeurIPS/ICML oral &gt; spotlight &gt; long talk &gt; Best Paper Finalist, 跨方向覆盖</p>
<h3>{N}. {论文标题 (verbatim)}</h3>
<p>大领域: {D}</p>
<p>中方向: {M}</p>
<p>小任务: {T}</p>
<p>子技术: {S}</p>
<p>作者: {作者1}（{中文1}）, {作者2}（{中文2}）, ..., {老师}（{老师中文}）</p>
<p>通讯作者: {老师}（{老师中文}）</p>
<p>发表: {venue} {year} ({oral/spotlight/long talk/BP Finalist})</p>
<p>paper link: <a href="{paper-url}">{paper-url}</a></p>
<p>paperscool: <a href="https://papers.cool/arxiv/{arxiv-id}">https://papers.cool/arxiv/{arxiv-id}</a></p>
<!-- 重复 10 次, 每篇 1 个 h3 + 10 p, 共 11 行 -->
```

**填表规则 (v0.3.0 增强硬要求 + v0.13.4 arXiv verify + v0.13.5 paper link fallback)**:
- 10 篇: 选 oral/spotlight/long talk/BP Finalist 优先, 跨方向覆盖 (持续学习/LLM/CV/AI4Science/迁移/元学习 等)
- 每篇 **11 行** (1 h3 标题 + 10 p): h3 标题**只**含编号+标题 (无 arXiv inline) + 4 行独立 taxonomy + 全作者中文括注 + 通讯作者独立行 + 发表 + paper link + paperscool 完整 URL
- **❌ 禁止** h3 含 `[arXiv xxx]` inline (v0.13.4 user 反馈, arXiv 移到独立 p 行)
- **❌ 禁止** callout 包裹 (用 h3 直挂, 不套 callout)
- **❌ 禁止** 1 行 4 项 taxonomy (必须 4 行独立 p 块, 与 output-contract Check 8 一致)
- **❌ 禁止** emoji="⭐" (v0.6.0 H2 无装饰 emoji 硬要求, paper h3 同样不装饰)
- **❌ 禁止** inline `<b>Ying Wei (通讯)</b>` (通讯作者独立行, 中文括注, 无 bold)
- **🔴 v0.13.5 paper link fallback 硬要求 (Check 24)**: 字段名 `arXiv：` → `paper link:`. Fallback 顺序: 1) arXiv ID 真 (YYMM.NNNNN 格式 + Check 23 verify HTTP 200) → `https://arxiv.org/abs/{id}`. 2) arXiv ID 假/无 → `https://openreview.net/forum?id={id}` (用 假 arXiv ID 拼). 3) OpenReview 也无 → `暂无`.
- **🔴 v0.13.4 必跑** `python3 scripts/check_arxiv_url.py --id {arxiv-id}` verify HTTP 200 + title 匹配 L1 byline (Check 23 硬要求). **LLM 禁止** 编造 arXiv ID (e.g. 22hBwIf7OC / TpD2aG1h0D). 失败标 "待补" + 删 href.
- 选稿标准在 h3 段落明示, 便于 audit

### 4.2 1.3.B 其他论文 (按 5-7 主题汇总表)

```xml
<h3>1.3.B. 其他论文 ({N} 篇, 按 5-7 主题汇总)</h3>
<callout>
  <p><b>B1. {主题1} (M 篇)</b> — 主题: {1 句话}</p>
  <table>
    <colgroup><col width="40"/><col width="380"/><col width="120"/><col width="180"/></colgroup>
    <thead>
      <tr><th>#</th><th>标题</th><th>会议/年份</th><th>arXiv</th></tr>
    </thead>
    <tbody>
      <tr><td>{编号}</td><td>{论文标题}</td><td>{venue} {year}</td><td><a href="https://arxiv.org/abs/{id}">{id}</a> / 暂无 / 待补</td></tr>
      <!-- M 行 -->
    </tbody>
  </table>
</callout>
<!-- 重复 5-7 个 callout, 每个主题一个 -->
```

**填表规则**:
- 主题数: 5-7 个 (按 §1.4 论文数 top 主题)
- 每个主题 1 个 callout, 内部 table 列出 M 行
- arXiv 列: link / 暂无 / 待补 三选一
- 主题归类按 中方向 (来自原 paper card)

### 4.3 1.3.C 趋势分析

```xml
<h3>1.3.C. 趋势分析 (近 3 年方向漂移)</h3>
<callout background-color="light-gray">
  <p><b>1. 方向漂移 (year1-year2 → year3-year4)</b>: {1-2 句, 早期 vs 当前主线}</p>
  <p><b>2. {当前主线} 强度</b>: {N 篇 oral, 是当前组最稳方向}</p>
  <p><b>3. {次主线} 占比</b>: {占比%, 与主方向关联}</p>
  <p><b>4. 国际合作网络</b>: {1 句, 通讯/合作单位}</p>
  <p><b>5. 顶会比例</b>: {N/N = 100%} 顶会 (含 IJCAI), 0 期刊主作, 0 workshop-only</p>
</callout>
```

**填表规则**:
- 5 个观察点必含 (方向漂移 / 主线强度 / 次主线占比 / 国际合作 / 顶会比例)
- 每点 1-2 句, 不写大段
- 套磁参考: 强调当前主线, 弱化早期

---

## 5. 1.4 数据来源与说明

### 5.1 1.4.1 L1-L4 论文类数据源

```xml
<h3>1.4.1. L1-L4 论文类数据源</h3>
<ul>
  <li><b>arXiv API</b>: {N} 篇全部验证 byline + Check 13 wiki_subject {N}/{N} 通过 ({YYYY-MM-DD} 抓取, 见 §1.3)</li>
  <li><b>个人主页</b>: ✅ <a href="{主页URL}">{主页URL}</a> (WebFetch 验证 {YYYY-MM-DD})</li>
  <li><b>检索时间</b>: {YYYY-MM-DD}</li>
  <li><b>覆盖范围</b>: {老师} {year1}-{year2} 全部代表论文 {N} 篇 ({10 顶会 + 63 主题分组}, 见 §1.3)</li>
</ul>
```

### 5.2 1.4.2 L7 社区类数据源

```xml
<h3>1.4.2. L7 社区类数据源</h3>
<ul>
  <li><b>mysupervisor.org</b>: 🟥 P0 待查 {N} 条评价 [L7 社区]</li>
  <li><b>学院 PDF</b>: 🟥 P0 待查 ({学校}{学院} 2026 招生意向信息表) [团队意向, 非官方计划]</li>
  <li><b>知乎/小红书</b>: 🟥 P0 待查 {N} 条 长文/单贴 [L7 社区]</li>
  <li><b>检索时间</b>: {YYYY-MM-DD}</li>
</ul>
```

### 5.3 1.4.3 P0/P1/P2 待补字段汇总 (NEW v0.13.0 单一路径)

```xml
<h3>1.4.3. 🟥 P0/P1/P2 待补字段汇总 (统一路径 §1.4.3)</h3>
<callout background-color="light-orange" emoji="❓">
  <p><b>本报告未确认的字段 (影响决策)</b>:</p>
  <ul>
    <li>🟥 P0 — {招生名额 — 1v1 问}</li>
    <li>🟥 P0 — {实际带生者 (1v1 vs 团队) — 1v1 问}</li>
    <li>🟥 P0 — {L7 招生偏好/培养模式/团队氛围/毕业去向 — 知乎/mysupervisor/LinkedIn 抓取}</li>
    <li>🟥 P0 — {L1 vs L7 矛盾说法 (套磁必问 onboarding 计划)}</li>
    <li>🟨 P1 — {行政职务 — 1v1 问}</li>
    <li>🟩 P2 — {学术兼职 — LinkedIn}</li>
  </ul>
  <p><b>建议补充路径</b>: 套磁时直接问导师 / 课题组在读博士 / mysupervisor 关注 + 提醒 / {学校}研招网 2026 年公告</p>
</callout>
```

**🚨 NEW v0.13.0 硬要求**:
- **统一路径**: 所有 ❓ 待补统一汇总到 §1.4.3, 其他章节末尾不再重复 "建议补充路径" (4 行 → 1 行 "见 §1.4.3")
- **P0/P1/P2 标签必填**:
  - 🟥 P0 = critical for decision (套磁必问 / 招生名额 / 实际带生者)
  - 🟨 P1 = important for ongoing eval (1v1 频率 / 实习政策 / 留校情况)
  - 🟩 P2 = nice-to-have (行政职务 / 学术兼职)
- **禁止** ❓ 单独使用 (v0.5.0 旧模板 ❓ 待补被 P0/P1/P2 替代)
- **禁止** ❌ ❎ 等其他占位符

---

## 6. 1.5 套磁准备清单 (NEW v0.13.0, 替代 v0.5.0 旧 §1.4 套磁)

```xml
<h2>1.5. 套磁准备清单 (基于 §1.1-§1.4 综合)</h2>
<h3>1.5.1. 24h 内必做的 5 件事</h3>
<ol>
  <li><b>精读 2 篇代表作</b>: 从 §1.3.A 顶会 10 篇选 2 篇 (推荐 {paper 1} + {paper 2}, 前者展示当前主线, 后者展示 {匹配点}). 读 Intro + Method + 实验细节, 准备 3 个 follow-up 问题.</li>
  <li><b>写 3 句话开场白</b>: (a) {1 句, 引用 1.2.2 方向 bridge paper} (b) {1 句, 用户经验桥接} (c) {1 句, 1v1 问 1 题}. 三句话必须基于 §1.2.2 方向 bridge + 用户自身背景.</li>
  <li><b>准备 CV 一页</b>: 英文 1 页 + 中文 1 页, 突出 {代表作 + 核心经验}. 1v1 邮件附件用 PDF 版.</li>
  <li><b>看 1 个 OpenReview 评论</b>: 在 OpenReview 翻 §1.3.A 顶会 1 篇的 reviewer 评分 + rebuttal, 找 1 个 reviewer 关心的细节问题.</li>
  <li><b>找到 1 个在读博士的 1v1 问 5 题</b>: 优先级: 1v1 邮件前必须找到 1 个 {老师}组在读 PhD 问 5 题 (见 §1.5.2). 找不到 → 套磁延后 3-5 天, 优先 LinkedIn 搜 "{老师} {学校} PhD student".</li>
</ol>
<h3>1.5.2. 1v1 必问 5 题 (覆盖 §1.2.3 + §1.2.5 缺失字段)</h3>
<ol>
  <li><b>Onboarding</b>: "博一前 6 个月谁 1v1 带我? 是您亲自带还是 senior PhD 带? 6 个月后是否切换独立课题?" (覆盖 §1.2.3 招生偏好)</li>
  <li><b>推免 vs 申请-考核</b>: "您组 2027 Fall 是推免直博 / 申请-考核 / 硕转博 哪条? 推免比例 vs 申请-考核比例?" (覆盖 §1.2.3 招生名额)</li>
  <li><b>方向 vs {用户方向 bridge}</b>: "我读了 {bridge paper 1} + {bridge paper 2}, 您组 {year1-year2 偏 X, year3-year4 偏 Y}. 当前组里 {用户方向} 是主线还是偏门? 我 {用户方向} 经验怎么接入?" (覆盖 §1.2.2 方向接入)</li>
  <li><b>延毕与转博</b>: "组内过去 3 年 PhD 实际延毕率多少? 推免直博生转博率 (硕转博) 大概多少? 在读博士中已经有几位?" (覆盖 §1.2.3 + §1.2.4 培养)</li>
  <li><b>实习与会议</b>: "是否允许博士期间去工业界实习 (如 阿里达摩院 / DeepSeek)? NeurIPS / ICLR / ICML 会议是否资助?" (覆盖 §1.2.4 + §1.2.5)</li>
</ol>
<h3>1.5.3. 发信时窗 + 邮件模板要点</h3>
<callout background-color="light-blue" emoji="📧">
  <p><b>发信时窗</b>:</p>
  <ul>
    <li><b>最佳</b>: 周二-周四 工作日 9:00-11:00 (招生办老师邮件习惯时段)</li>
    <li><b>次佳</b>: 周一上午 / 周五下午</li>
    <li><b>避免</b>: 周五晚 + 周末 + 节假日 (老师可能周末不查邮件)</li>
  </ul>
  <p><b>邮件结构 (基于 §1.2.2 方向 bridge)</b>:</p>
  <ol>
    <li>Subject: "Prospective PhD Applicant - {用户方向 1} + {用户方向 2} ({姓名} / {学校})"</li>
    <li>第 1 段 (3 句): 自我介绍 + 读 2 篇代表作 + 套磁切入主线 (引 §1.2.2)</li>
    <li>第 2 段 (3 句): 我的 {用户方向} 经验 + 如何接入您组 {主方向} 主线</li>
    <li>第 3 段 (1 句): 1v1 问 5 题里挑 1-2 个不敏感的先问 (如 #2 招生渠道)</li>
    <li>附件: CV (英文 1 页 PDF) + 代表作 PDF (选 1 篇自己最好的, 非 老师 paper)</li>
    <li>签名: 中文姓名 + 英文名 + 本科学校 + 硕士学校 + 联系方式 (Gmail + 微信 ID + 手机可选)</li>
  </ol>
</callout>
<h3>1.5.4. 备份计划 (若老师无名额 / 1v1 无回复)</h3>
<callout background-color="light-red" emoji="🔄">
  <p><b>Plan A (主) - {老师}正博</b>: 1v1 套磁成功 → 推免 / 申请-考核 → {year} Fall 入学</p>
  <p><b>Plan B - {老师}组 senior PhD 联培</b>: 若老师本人无名额, 找其组内 senior PhD ({5+ 名 oral 一作}) 做联培, 通过 senior PhD 引荐</p>
  <p><b>Plan C - 同方向其他 {学校} 老师</b>: 若 {老师}组不收, 转 {学校}{学院} 同方向 ({主方向}) 其他 PI, 如 {合作者} (与 {老师} 有合作 #{编号})</p>
  <p><b>Plan D - 跨校备份</b>: 同方向 ({主方向}) 港三所 / 清北 / 中科院自动化所 老师</p>
  <p><b>Plan E - 时间线</b>: {YYYY-MM} 之前必须 1v1 收到 1 个 positive 回复, 否则启动 Plan B/C/D. 套磁窗口只剩 {6-9 月 (申请-考核) + 9 月推免}.</p>
</callout>
```

**🚨 NEW v0.13.0 硬要求**:
- 1.5 是 v0.5.0 旧 §1.4 套磁的**替代**, 不是补充. 旧 v0.5.0 §1.4 套磁信 / 申请时间节点 / 风险点 **禁止**再写到 docx
- 1.5 套磁信是 chat 输出, **不**写到 docx h2 章节里 (v0.12.0 Output Discipline)
- 1.5 4 个子节必含, **禁止**只写 1.5.1 (24h 5 件事)
- 1.5.2 1v1 必问 5 题每题**必含** "覆盖 §X.Y" 标注, 便于 audit

---

## 8. 模板 footer (无水印 v0.13.6)

```xml
<hr/>
<p>文档生成时间: {YYYY-MM-DD} (v0.13.6 套磁就绪版 — 1.3 A/B/C 论文重组 + 1.4.3 P0/P1/P2 待补 + 1.5 套磁清单 + 主动 WebFetch 主页 + paper link fallback v0.13.5)</p>
<p>模板: <a href="https://github.com/mykcs/myk-skills/tree/main/teacher-report/references/report-template.md">teacher-report v0.13.6</a></p>
```

**🚨 NEW v0.13.6 硬要求**:
- **禁止** "整理人: claudecode teacher-report skill v0.5.0" 水印 (v0.5.0 旧模板残留)
- 改为版本号 + 关键变更 + 模板源 link
- 必含 v0.13.6 版本号 + 1.3 重组 / 1.4.3 / 1.5 / WebFetch / paper link fallback 5 个核心变更标签

---

## 9. 分块写入 (超长文档)

`docs +create` 单次 `--content` 体积有限制 (实测 ~30 blocks). 超长时 (尤其是 1.4 论文重组后):

1. **第 1 次**: `docs +create --content '<title>...</title><TL;DR>...</TL;DR><hr/>'`
2. **第 2 次**: `docs +update --command append --content '<h2>1.1. 自评</h2>...'`
3. **第 3-N 次**: 继续 append `1.2.1-1.2.5` / `1.3 数据快照 + 1.3.A + 1.3.B + 1.3.C` / `1.4.1-1.4.3` / `1.5.1-1.5.4`

每章 append 一段, 失败时只重传该段, 不要全量重传.

---

## 10. 视觉丰富度硬要求 (防止"全文字")

- TL;DR 必须 callout + grid, 不能纯文字
- 每个 h3 章节必须至少有 1 个 callout / table / grid 之一
- "核心观察 / 关键判断 / 风险点" 段落必须用 callout
- 论文精读用 callout, 不要写成大段叙述
- 表格用 `<table>` 块, **不要**用 markdown 表格 (飞书 v2 API 不渲染 markdown table)

---

## 11. 申博 wiki dashboard 摘要模板

**用途**: 每次跑完老师报告, **append 一段摘要**到"申博 wiki dashboard"主节点, 让 user 在一个地方看到所有候选老师.

```xml
<hr/>
<h3>申博候选: {学校} {老师} ({YYYY-MM-DD} 调研)</h3>
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
      <td><p>{🟢 高 / 🟡 中 / 🔴 低} ({1 行理由})</p></td>
      <td><p>{近 3 年论文数 / 顶会产出 / 本人一作}</p></td>
      <td><p>{行政岗 / 方向偏 / 招生名额 / 实际带生者}</p></td>
    </tr>
  </tbody>
</table>
<p><b>飞书 docx 全文</b>: <a href="{report_url}">{学校} {老师} (v0.13.6 套磁就绪版)</a></p>
<p><b>核心建议</b>: {1 行: 直接套磁 / 改推替代导师 / 暂缓}</p>
```

**填表规则**:
- 摘要 ≤ 5 行, user 扫一眼就懂要不要细读全文
- 飞书 docx 用 `<a href="...">` 链接, user 一键跳转
- "核心建议" 必含 1 个 actionable 决策
- 多个老师时, dashboard 持续 append, 自然形成"申博候选池"时序

**反例** (禁止):
- ❌ 摘要超过 5 行 — 失去 dashboard 一目了然的价值
- ❌ 不带飞书 docx 链接 — user 无法跳转看全文
- ❌ 缺"核心建议" — 摘要失去决策价值

---

## 12. v0.13.6 变更日志 (本次)

> **v0.13.6 (2026-06-17) 重大重构 (NEW)**: 4 章节必含 (TL;DR + 1.1/1.2/1.3/1.4/1.5) + §1.3 A/B/C 论文重组 + §1.4.3 P0/P1/P2 统一 + §1.5 套磁清单 + 主动 WebFetch 主页 + 无水印. 触发 case: 魏颖 wiki 套磁清理 (2026-06-17, claudecode 帮用户修了 12 项 patch) 暴露模板缺失.
>
> **5 个核心结构** (2026-06-17 v0.13.6, 5 → 5):
> 1. §1.2.1 主动 WebFetch 主页 — L1 主页 + 邮箱必抓, 禁止留 ❓
> 2. §1.3 A 顶会 10 + B 主题 5-7 表 + C 趋势分析
> 3. §1.4.3 P0/P1/P2 待补字段汇总 (统一路径, 单一 callout)
> 4. §1.5 套磁准备清单 (替代 v0.5.0 旧 §1.4 套磁)
> 5. v0.13.5 paper link fallback (Check 24, 字段名 arXiv: → paper link:, 3 档 fallback)
>
> **3 个硬要求升级**:
> - v0.13.6 #1: 主页/邮箱必须 WebFetch 主动抓, 失败留 P1 + 抓取命令提示 (不 ❓)
> - v0.13.6 #2: P0/P1/P2 标签必填, 单一路径 §1.4.3, 其他章节末尾 "见 §1.4.3" 一行
> - v0.13.6 #3: 删 "整理人: claudecode teacher-report skill v0.5.0" 水印, 改 v0.13.6 版本号 + 关键变更 + 模板源 link
>
> **与 v0.13.0 关系**: 重编号 + 删 1.3 申博匹配度评估整块. v0.13.6 在 v0.13.0 基础上重排 1.4 论文 → 1.3, 1.5 数据 → 1.4, 1.6 套磁 → 1.5, 并删 v0.13.0 §1.3 申博匹配度评估 (含 §1.3.1 学术方向匹配度 / §1.3.2 团队氛围 / §1.3.3 毕业要求) 整块 73 blocks.
>
> **L1 抓取规则升级**: L1 抓取失败时, 不留 ❓, 改留 🟨 P1 待补 + 抓取命令提示 + 数据源预期 URL 模板. 失败字段在 §1.4.3 汇总时标 🟨 P1.
