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
