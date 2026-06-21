# Changelog

> **本主页只保留 v0.11+ 当前 active 4 个版本 (v0.11.0 / v0.11.1 / v0.12.0 / v0.13.0)**. v0.4.0 ~ v0.10.0 7 个历史版本详细 changelog 已下沉到 [`CHANGELOG-archive.md`](CHANGELOG-archive.md) (2026-06-17 拆分). 触发 case: rich-audit v2.6.2+ skill_authoring_checker 检测主页 CHANGELOG.md 过长, 违反 SKILL.md 简洁原则.

## v0.13.0 changelog (2026-06-17)

**重大重构 (NEW)**: 5 h2 → 6 h2 (新增 §1.6 套磁准备清单, 替代 v0.5.0 旧 §1.4 套磁 h2) + 6 个新结构 (1.3.1 学术方向匹配度 / 1.4 A 顶会 10 + B 主题表 + C 趋势 / 1.5.3 P0/P1/P2 待补汇总 / 1.2 顶部 2xN 方向矩阵) + 主动 WebFetch 主页 + 3 个新硬要求 (v0.13.0 #1-#3) + 19 → 22 项 LLM 自检 (新增 Check 20 P0/P1/P2 + 21 主动 WebFetch + 22 1.6 套磁清单) + 模板整合 (report-template.md 583 → 470 行 v0.13.0 + output-contract.md 与 report-template.md 100% 一致) + paper-card 入口整合 (新建 paper-card-formats.md, 删 paper-card-v04.md + paper-card-v11.md 索引) + bin 脚本归档 (4 个 v0.4.0 legacy → bin/archive/v04-legacy/) + 无水印 (删 "整理人: claudecode teacher-report skill v0.5.0").

**触发 case**: 魏颖 wiki 套磁清理 (2026-06-17, claudecode 帮用户修了 12 项 patch) 暴露模板缺失. 详见 `references/report-template.md` §12 v0.13.0 变更日志.

**与 v0.12.0 关系**: 兼容. v0.12.0 4 章节必含 + Output Discipline 全部保留. v0.13.0 在 v0.12.0 基础上扩 §1.6 套磁清单 + §1.3.1 + §1.4 重组 + §1.2.1 主动 WebFetch. (v0.13.1 移除 §1.2 顶部 2xN 矩阵, 实际使用不实用.)

## v0.12.0 changelog (2026-06-12)

**去除《套磁与申请建议》section**. 6 h2 → 5 h2 (去掉 §1.4. 套磁与申请建议 + 3 个 h3 子章节: 1.4.1 套磁信 / 1.4.2 申请时间节点 / 1.4.3 风险点). 新章节结构: 1.1. 自评 (user-owned v0.9.0) / 1.2. 导师与课题组画像 / 1.3. 申博匹配度评估 / 1.4. 论文产出全景 / 1.5. 数据来源与说明. 触发 case: 用户 2026-06-12 显式说明「修改 skill 模板里去掉《套磁与申请建议》」. 现有 13 PIs wiki docx 中, 仅 2 个 doc (毛玉仁 / 高云君, v0.5.0+v0.9.0+ 模板) 含此 §1.4. 套磁 section — 这 2 个 doc 需 fix: 删 §1.4. + 后续 §1.5→§1.4 + §1.6→§1.5. 其余 13 doc (v0.9.0 之前 5-section 模板) 已无此 section, 不需 fix. Skill 模板 7 个文件同步 (SKILL.md + output-contract.md + audit-checklist.md + h3-mapping.md + user-owned.md + failure-handling.md + report-template.md). 18 → 19 项 LLM 自检 (Check 18: 5 h2 章节齐全不含套磁). 与 v0.5.0+v0.9.0 旧规则 (含 §1.4. 套磁) 冲突, 旧规则作废. 详见 `## 🚨 5 章节必含 (v0.12.0, 2026-06-12, 违反 = skill 协议破坏)` 硬要求.

## v0.11.1 changelog (2026-06-12)

**Output Discipline 范围扩展到 docx 内部**. v0.11.0 仅禁止 chat 输出 4 行元信息 preamble, 但实际 13 PIs 飞书 wiki docx 内部 12/13 都含同款 preamble callout (LLM 在生成 docx 时把元信息也写进 callout 了). v0.11.1 硬要求 LLM **不得**在 docx 内部生成 4 行元信息 callout: 「本报告: vX.X.X (升级自 vY.Y.Y, L? 数据已实际抓取) / 调研对象: ... / 招生匹配度: 🟡 ... / 论文产出: N 篇...」. 元信息正确存放点: docx §1 导师画像 + §2 申博匹配度 + §4 论文全景 + §5 数据来源, **不**用紧凑 4 行 callout 形式. 现有 13 PIs docx 12/13 已 F2 块级修删除 (本报告/调研对象/招生匹配度/论文产出 4 行 preamble callout), 详见 `## 🚨 Output Discipline 硬要求 (v0.11.0, 2026-06-11, 违反 = skill 协议破坏)` v0.11.1 扩展 subsection.

## v0.11.0 changelog (2026-06-11)

**Paper Card v0.11.0 完整版 + Output Discipline 双升级**. 2 大维度:

**(1) Paper card v0.11.0 完整版 (替代 v0.3.9 完整版, v0.4.0 紧凑版保留)**. 12 决策: (1) 版本定位 v0.11.0 完整版, (2) 标题 `<p>` 段落, (3) status 字段独立新行, (4) arXiv 可空 (`arXiv：暂无` 合法状态值), (5) 编号 `1.` 纯文本前缀, (6) inline 中文括号 `（大老板）（通讯）`, (7) Skill 顶层 v0.11.0 单一版本号 (去 11 文件版本号后缀), (8) status 严格 enum 8 值 (被拒/在投/R&R/已收/Camera Ready/已发表/Preprint/撤稿), (9) paper URL 7 种优先级 (OpenReview 优先 → arXiv/DOI/papers.cool/proceedings/journal/主页 PDF), (10) LLM 自检 17 → 22 (Check 18 status enum + 19 paper URL + 20 arXiv/paper 一致性 + 21 status/paper URL 联动 + 22 paper card 编号样式), (11) 强制迁移 14 wiki docx, (12) 写完整 case file. v0.11.0 paper card 与 v0.11.0 Output Discipline 独立维度, 叠加生效.

**(2) Output Discipline 硬要求**. 禁止 LLM 在 chat 输出 4 行元信息 preamble: 「本报告: vX.X.X ... / 调研对象: ... / 招生匹配度: 🟡 ... / 论文产出: N 篇...」. LLM 应直接调 `lark-cli docs +create` → 输出 docx URL. 元信息 (招生匹配度 / 论文产出数 / L? 数据源状态) 是 docx TL;DR callout 内容, **不应在 chat 复述**.

## v0.13.2 changelog (2026-06-17)

**Paper card 格式统一 v0.3.0 增强 (NEW)**: §1.4.A 顶会 10 paper card 格式从 v0.4.0 紧凑 (callout 4 行 metadata) **改为 v0.3.0 增强 (h3 + 12 行, 1 h3 含 arXiv inline + 4 行独立 taxonomy + 全作者中文括注 + 通讯作者独立行 + 发表 + arXiv 完整 URL + paperscool 完整 URL)**. 触发 case: 魏颖 wiki 1.4.A 顶会 10 篇 (2026-06-17, user 反馈 v0.4.0 紧凑格式不符合预期). 同步修 3 个文件:
- `references/report-template.md` §5.1 例子 (callout 改为 h3 + 12 行)
- `references/paper-card-formats.md` §1 决策树 + §7 v0.13.0 选型决策表 (1.4.A 顶会 10 改为 v0.3.0 增强)
- `SKILL.md` 描述 (含 v0.13.2 描述) + 改 1.4.A 描述

**v0.3.0 增强 12 行 paper card 格式** (per paper, 1 h3 + 11 p):
1. `<h3>N. {标题} [arXiv {id}]</h3>` — h3 标题含 arXiv inline
2. `<p>大领域: {D}</p>` — 4 行独立 taxonomy 第 1 行
3. `<p>中方向: {M}</p>` — 第 2 行
4. `<p>小任务: {T}</p>` — 第 3 行
5. `<p>子技术: {S}</p>` — 第 4 行
6. `<p>作者: {作者1}（{中文1}）, {作者2}（{中文2}）, ...</p>` — 全作者中文括注
7. `<p>通讯作者: {老师}（{老师中文}）</p>` — 独立行
8. `<p>发表: {venue} {year} ({role})</p>`
9. `<p>arXiv: <a href="https://arxiv.org/abs/{id}">https://arxiv.org/abs/{id}</a></p>` — 完整 URL
10. `<p>paperscool: <a href="https://papers.cool/arxiv/{id}">https://papers.cool/arxiv/{id}</a></p>` — 完整 URL

**与 v0.3.9 / v0.4.0 / v0.11.0 关系**:
- v0.3.0 增强: 6 行 + 4 行 taxonomy + 通讯作者行 (本版本)
- v0.4.0 紧凑: 7 行 (callout + inline 标记, 用于 1.4.B 主题表)
- v0.11.0 完整: 10 行 (status enum + arXiv 可空 + paper URL 优先级, 用于论文 ≤ 3 篇)
- v0.13.2 选型: 1.4.A 顶会 10 → v0.3.0 增强, 1.4.B 主题表 → v0.4.0 紧凑, 套磁信深度引用 → v0.11.0 完整

## v0.13.4 changelog (2026-06-17)

**arXiv 幻觉重大修复 (NEW, 违反 = skill 协议破坏)**: teacher-report skill 之前 (v0.5.0 → v0.13.2) 生成的 arXiv ID 中, **70+ 假 arXiv ID** (LLM 幻觉, 不存在 或 ID 真实但内容 LLM 编造). 魏颖 wiki 1.4.A 10 篇 audit 结果:
- 5 假 ID (404 NOT FOUND): #1 `22hBwIf7OC` / #2 `5U1rlpX68A` / #3 `gc8QAQfXv6` / #5 `TpD2aG1h0D` / #7 `iTTZFKrlGV`
- 1 ID 真内容假 (#9 `2206.04335` 实际是 "Learning to generate imaginary tasks" 而非 docx 编造的 "Adversarial Task Up-sampling")
- 3 真 (2406.01721 DuQuant / 2506.12597 Automatic Expert / 2311.06868 Concept-wise)
- 1 待补 (#10 Scalable Heterogeneous Translated Hashing)

1.4.B 5 主题 63 篇 arXiv 列全部 标 "待补" (LLM 编造 arXiv ID 严重, 不逐 verify 节省时间).

**主页 / 邮箱 verify 通过**:
- person.zju.edu.cn/yingwei 真 (魏颖-浙江大学个人主页, 百人计划研究员 + 博导)
- wei-ying.net 真 (CompLife Lab, 基座模型 + Agent)
- ying.wei@zju.edu.cn 真 (主页 metadata)

**新增 Check 23 arXiv URL verify 硬要求** (违反 = skill 协议破坏):
- 每个 arXiv ID 必跑 `WebFetch https://arxiv.org/abs/{id}` verify HTTP 200
- HTTP 200 还要 verify title 匹配 L1 byline (避免 ID 真但内容 LLM 编造)
- 失败标 "待补" + 删 href (不保留假链接)
- 必跑 `python3 scripts/check_arxiv_url.py --id {id}` 返回 0

**新脚本**: `scripts/check_arxiv_url.py` (1 脚本, 必跑)

**触发 case**: 魏颖 wiki 1.4.A 顶会 10 篇 (2026-06-17, user 反馈 "https://arxiv.org/abs/22hBwIf7OC 这些链接全是假的")

**修复 4 文档**:
- `references/output-contract.md` Check 23 加 arXiv URL verify 硬要求
- `references/report-template.md` §5.1 填表规则加 arXiv verify 步骤
- `references/paper-card-formats.md` 选型表加 arXiv verify 必跑
- `SKILL.md` description 加 v0.13.4 描述

## v0.13.5 changelog (2026-06-17)

**paper link 字段名 + fallback 硬要求 (NEW, 违反 = skill 协议破坏)**: 字段名 `arXiv：` → `paper link:`. Fallback 顺序: (1) arXiv ID 真 (YYMM.NNNNN 格式 + Check 23 verify HTTP 200) → `https://arxiv.org/abs/{id}`. (2) arXiv ID 假/无 → `https://openreview.net/forum?id={id}` (用 arXiv ID 拼). (3) OpenReview 也无 → `暂无`. 触发 case: 魏颖 wiki 1.4.A 顶会 10 篇 + 1.4.B 5 主题 63 篇 (2026-06-17, user 反馈 "arXiv 改为 paper link, 如果有 arxiv 就写上, 没有就找 openreview, 还是没有就写暂无"). 同步加 **Check 24 paper link fallback 硬要求** + 修改 1.4.A #1 (Plug-and-Play 22hBwIf7OC 假) → OpenReview URL, 1.4.A #4/#6/#8/#9 真 → arXiv URL, 1.4.A #10 无 arXiv → 暂无. 1.4.B 5 callout 63 行重写: 25 真 → arXiv, 36 假 → OpenReview. report-template.md §5.1 填表规则加 v0.13.5 paper link fallback 步骤. SKILL.md description 加 v0.13.5.

## v0.13.6 changelog (2026-06-17)

**§1.3 申博匹配度评估整块删除 (NEW)**: 6 章节必含 → 4 章节必含 + TL;DR (1.1/1.2/1.3 论文/1.4 数据/1.5 套磁). §1.3 申博匹配度评估 h2 + 1.3.1 学术方向匹配度 h3 + 1.3.2 团队氛围 h3 + 1.3.3 毕业要求 h3 整块删除 (73 block batch delete in 魏颖 wiki docx). 章节重编号: 原 1.4 论文全景 → 1.3, 原 1.5 数据来源 → 1.4, 原 1.6 套磁准备清单 → 1.5. 触发 case: 魏颖 wiki 1.3 段 (2026-06-17, user 反馈 "skill 去掉《1.3. 申博匹配度评估》这一整块内容"). 同步修 4 文件:
- `references/report-template.md` 5 章节必含 (line 19-29 6 → 4) + §4 1.3 整段删除 + 章节重编号 §5→§4 §6→§5 §7→§6
- `references/output-contract.md` 6 章节必含 → 5 章节必含 (4 必含 + TL;DR) + Check 18 重命名 §1.6 → §1.5 + §1.3 申博匹配度 完整章节必含段删除 + §1.3 论文产出全景 / §1.4 数据来源 / §1.5 套磁准备清单 段重写
- `references/paper-card-formats.md` 无修改 (1.3.1 仅在用户偏好列表, 不影响 1.4.A 选型决策)
- `SKILL.md` description 4 章节必含 + 加 v0.13.6 描述

**保留内容 (历史 changelog, 不删)**:
- v0.12.0 changelog 描述 "5 h2: 1.1/1.2/1.3/1.4/1.5" (line 14) — 当时 5 h2 含 1.3 申博匹配度, 1.6 套磁是 v0.13.0 加的, v0.13.6 再删 1.3 重排
- output-contract.md line 29 v0.13.6 移除 changelog 描述 (记录 1.3 删除历史)
