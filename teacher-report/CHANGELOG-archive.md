# teacher-report CHANGELOG Archive (v0.4.0 ~ v0.10.0)

> **历史 changelog**: v0.4.0 → v0.10.0 7 个版本详细 changelog 已下沉到本文件. 主页 CHANGELOG.md 只保留 v0.11+ 当前 active 4 个版本 (v0.11.0 / v0.11.1 / v0.12.0 / v0.13.0). 触发 case: rich-audit v2.6.2+ skill_authoring_checker 检测主页 CHANGELOG.md 过长 (11 个版本历史), 违反 SKILL.md 简洁原则.

---

## v0.10.0 changelog (2026-06-11)

**中文名字符级 typo 硬要求**. Check 17: 老师姓名必须与 L1-L4 权威来源字符级匹配. 触发 case: 邓舒敏 (Shumin Deng) 文档 28 处中文名 typo 「邓**舒**敏 (shū)」→ 实际正确「邓**淑**敏 (shú)」. 同音不同义 LLM auto-generate typo, 之前 v0.2.9 反幻觉规则只校验 OpenReview/arXiv 字段正确性, 不校验中文姓名字符级. 17 项 LLM 自检 (16 v0.9.0 + Check 17 中文名字符). 同音/形近字 typo 启发式列表 (28 pairs, 含 舒/淑/青/清/振/震 等) 已写入 `scripts/check_chinese_name.py`. push wiki 前必跑 `python3 scripts/check_chinese_name.py --wiki-scan`, 返回 0 才算合规.

## v0.9.0 changelog (2026-06-11)

**Progressive disclosure 进一步拆分 (rich-audit 触发)**. 595 → 168 lines (-72%). 7 新 reference files: anti-hallucination-rules.md (53) + paper-set-diff-rules.md (65) + h3-mapping.md (67) + inputs-and-mode.md (40) + output-contract.md (45) + audit-mode-output.md (35) + failure-handling.md (25). main SKILL.md 仅保留概述 + 索引 + v0.7.0/v0.8.0 硬要求引用. 触发 case: rich-audit v2.6.2+ skill_authoring_checker 检测 teacher-report/SKILL.md 超 500 行限制 (Anthropic SKILL.md 最佳实践), 违反 documented guideline.

## v0.8.0 changelog (2026-06-11)

**深度+1 编号重构**. h2 = `1.X.` (5 章 → 1.1./1.2./1.3./1.4./1.5.), h3 章节 = `1.X.Y.` (原 1.1./2.1./3.2./5.3. → 1.1.1./1.2.1./1.3.2./1.5.3.). paper card h3 (N. Title) 不变. 13 docs × 5 h2 + 11-12 h3 = 65 + 144 = 209 段统一清理 (申博 wiki P49mwGQU0iEh9CkXbCTcC418nPb). **16 项 LLM 自检 (15 v0.7.0 + Check 16 深度+1 编号)**. 与 v0.2.5 (`h2=1.`) + v0.7.0 (`h3=1.1.`) 旧规则均冲突, 全部作废.

## v0.7.0 changelog (2026-06-11)

**H1-H4 编号标题 dot 后缀硬要求** (`1.1` → `1.1.`, `1.1.1` → `1.1.1.`, `1` → `1.`). 13 docs × 11-12 H3 = 144 段统一清理 (申博 wiki P49mwGQU0iEh9CkXbCTcC418nPb). **15 项 LLM 自检 (14 v0.6.0 + Check 15 编号 dot 后缀)**. 与 v0.2.5 旧规则 (`h3 = 1.1` 无 dot) 冲突, 旧规则作废.

## v0.6.0 changelog (2026-06-11)

**H2 标题去装饰性 emoji 硬要求** (来源 13 docs × 5 H2 = 65 段统一清理, 申博 wiki P49mwGQU0iEh9CkXbCTcC418nPb). 14 项 LLM 自检 (新增 Check 14: H2 标题无装饰性 emoji). 装饰性 emoji 集合: 👤📊✉📚📖🎯ℹ 等图标类; 保留 ✅❌⚠⭐🟢🟡🔴 等状态/信号类 (allowlist).

## v0.5.0 changelog (2026-06-10)

**申博实操 8 h3 字段新增** (招生偏好/培养模式/科研资源/团队氛围/毕业去向/申请时间节点 等). 5 h2 框架保留, 在 §1/§2/§3 内部叠加 8 新 h3, 总 h3 2 → 12. 数据源扩 L7 (mysupervisor.org 浙大CS 213 位 + 16 评价/PI + 知乎 + 小红书 + 学院 PDF), L7 字段用 [社区来源] 标签与 L1 区分. **v0.5.0 模板包含 §1.4 套磁与申请建议 h2 (套磁信/申请时间节点/风险点)**, 此 h2 在 v0.12.0 移除 (替换为 §1.6 套磁准备清单).

## v0.4.0 changelog (2026-06-10)

**Progressive disclosure refactor (Anthropic SKILL.md 500-line best practice)**. 1300 → 435 lines (-67%). 3 reference files: url-validation-rules.md (277) + paper-entry.md (233) + output-schema.md (413). v0.3.9 paper card demoted to reference (legacy), v0.4.0 紧凑 promoted to default. 13 项 LLM 自检强化 (新增 Check 13 Wiki Subject Author Verification).
