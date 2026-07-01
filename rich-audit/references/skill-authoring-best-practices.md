# Skill Authoring Best Practices (v2.6.7, 2026-06-10)

> ⚠️ [历史快照 2026-06-10] Tri-Search Protocol v2.6 已于 2026-06-12 重命名为 Force-All-Search Protocol v2.7; 本文档保留历史命名作为 audit trail.
> 来源: 4-tool Tri-Search 2026-06-10 找到的 v2.6.1 候选 D
> 对标: platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
> 检测: `scripts/skill_authoring_checker.py`

## 检查项 (per Claude API Docs)

### 1. Frontmatter 完整性
- ✅ `name` (必需)
- ✅ `description` (必需, 单行或 `|` 多行)
- ✅ `metadata.version` (必需, semver 格式)
- ✅ `metadata.category` (推荐)
- ✅ `triggers` (推荐, 至少 1 个)
- ✅ `tags` (推荐)
- ✅ `user-invocable` (推荐, true/false)
- ✅ `license` (推荐)

### 2. 命名规范
- "Use consistent naming patterns" (官方)
- 推荐: gerund 形式 (verb + -ing), e.g. `auditing`, `debugging`
- 现实: 现有 skill 多用 noun 或 noun-phrase (e.g. `rich-audit`, `website-improve`)
- **不强制**: 重命名会破坏 `triggers` 跟 slash command 引用

### 3. 简洁性 (Conciseness)
- "State what to do rather than narrate how or why"
- "Once a skill loads, its content stays in context across turns, so every line is a recurring token cost"
- 推荐: SKILL.md ≤ 200 行 (per `architecture-health` 阈值)
- 详细参考下沉到 `references/` 子目录

### 4. Body 结构
- Frontmatter 之后直接进 description / 触发词
- 复杂逻辑下沉到 references/ 或 scripts/
- 零确认协议 (if any) 写在显眼位置

## 检查命令 (Python script)

```bash
python3 ~/.agents/skills/rich-audit/scripts/skill_authoring_checker.py
```

输出 JSON: `{tool, version, skills_scanned, findings: [...], count, by_type}`

finding 类型:
- `missing_frontmatter_field`: 必需字段缺失
- `body_too_long`: SKILL.md > 200 行
- `no_triggers`: triggers 列表为空
- `description_too_short`: description < 20 chars
- `invalid_version`: version 不符合 semver

## 已知反例 (case 库)

- 大量 skill 没有 `metadata.version` (e.g. 部分历史 skill)
- 一些 skill 的 `description` 过短 (e.g. "test", "demo")

## 自动修复 (Level 分级)

- **Level 1 (机械)**: 列缺失字段清单, **不改**
- **Level 2 (提议)**: 提议补 frontmatter 模板, **用户确认**
- **Level 3 (应用)**: 真实补字段, **需用户授权**

## 互补关系

- 跟 `consistency-6d/5-frontmatter.md` 互补 (本文件专门针对 skills, 5-frontmatter 通用)
- 跟 `dead-code-orphan.md` 互补 (本文件看"字段完整性", dead-code 看"有没有人用")

## v2.6.59 段: 三段 sub-agent 协议位 (plan / execute / verify 物理隔离)

> **来源**: rich-audit v2.6.59 三段 sub-agent 协议位立 (跟 §F.4.6 端到端案例协同). 跨 skill 推广建议: 任何 complex task 涉及 ≥ 5 file 改动 + ≥ 1 ADR + ≥ 1 case + ≥ 2 session 协同 → 必拆三段 sub-agent.

### 协议位架构 (5 字段)

| 字段 | plan 段 | execute 段 | verify 段 |
|------|---------|------------|-----------|
| 工作目录 | parent 主进程 | 独立 worktree | 独立 worktree (跟 execute 共 path, 独立 process) |
| 输入 | grill 4-6 决策点 | plan 报告 (修改清单) | execute 报告 (5 字段自检) |
| 必跑 | 立修改清单 + worktree + ADR 编号 + case 骨架 + mem0 plan | 11 file 改完 + memory-bench baseline + commit + push + decision-stream | grader 校准 + 5 字段自检 + deferred-detector + mem0 add_memory × 1-3 |
| 禁止 | 写代码 / 调 Edit/Write / commit / push | 调 Agent tool 嵌套 spawn / 跑 grader / 改 execute 报告 | 重跑 commit / 改源文件 / 跑 Edit / 调 Agent tool |
| 输出 | plan 报告 | execute 报告 (含 5 字段自检) | PASS/FAIL 报告 (含 5 维 evidence + 4 维 self-verify) |

### 5 反模式 (永久失效)

1. **execute 段嵌套 spawn** → 物理隔离破坏
2. **execute 段跑 grader** → 越界
3. **plan 段写代码** → 跳过 grill 阶段
4. **verify 段重跑 commit** → 重复执行
5. **三段合并跑 (1 个 sub-agent 全跑)** → 物理隔离失败

### 跟 §I.4 self-evolution 关系

v2.6.59 §F.4.6 是 self-evolution 第 7 个端到端案例, 第 1 个协议位架构案例. 跟 v2.6.58 5 维度 full-quality (1 角色) 协同, v2.6.59 = 3 角色 plan/execute/verify.

**联动**: rich-audit/SKILL.md v2.6.59 + skill-self-evolution.md §F.4.6 + changelog.md + ADR-0035 + CASE-RICH-AUDIT-V2-6-59-TRIPLE-SUB-AGENT-20260701 + process.md §C.3.3 v2.6.59 强化段 + CLAUDE.local.md §11.2 hint.
