# 高级触发词（Advanced Triggers）

> 本文件存放 paper-into-notion 的进阶 / skill-evolution / cross-db / 协议位触发词。
> 核心 URL→Notion 触发词保留在 `SKILL.md` frontmatter `when_to_use`。

## Skill 自我进化与总结

- "skill 跑完自我总结"
- "任务后总结"
- "skill 经验教训内化"
- "skill 自我升级"
- "skill 改 CLAUDE.md 后直接生效"

对应实现：
- `scripts/skill-self-summary.sh` — 4 段总结 + mem0 quota fallback 3 步
- `references/self-summary-protocol.md` — 4 段模板 + fallback 决策树
- `references/self-evolution-loop.md` — 4/5 步闭环（总结 → 内化 → commit → bump → subagent FAIL 反馈）

## Cross-DB / Schema 迁移

- "跨 db 搬 schema"
- "跨 db 同步"
- "跨 db 搬运行记录"
- "Notion URL 解读"
- "Notion schema 变更"
- "Notion cross-db 搬"
- "Notion property 改名"
- "Notion multi-db schema"

对应实现：
- `scripts/add-property.sh` — PATCH /v1/data_sources/{id} 加 property
- `templates/cross-db-migrate-payload.md` — 跨 db strip id 规则
- `references/notion-schema-migration.md` — Notion 2025 API model + 4 错误码
- `references/notion-url-parse.md` — URL 4 类 + id 提取 + 4 决路径
- `templates/notion-fix-cheatsheet.md` — 4 类常见问题 + 1 跳决策树

## 协议位与字面 drift 修复

- "**skill 子句 grep 修复**"
- "**skill 字面 drift 修复**"
- "**skill ask window 守卫**"
- "**用户 ADHD 节奏 + ask window**"

对应实现：
- `scripts/skill-self-summary.sh` Step 0 ask window 守卫
- `references/self-evolution-loop.md` §0 4 条件表
- 跨 skill 协议位必跑 sub-check，注释与实装字面一致

## 外部联动

- `weekly-report-phd` v0.7+ 跑周报时 paper card 联动
- `teacher-report` 写 paper card 给老师（**不走**本 skill，用 teacher-report）

## v-bump 与验证协议

- v-bump 自动触发：反模式 ≥ 4 / 流程变化 ≥ 1 / 触发词变化 ≥ 1 / hot recall 新增段，任一满足即触发
- spawn subagent 验证前必 `git pull + ff main`
- 3 dirty file 走 v-bump 闭环
- skill introspect cache stale：`NOTION_INTROSPECT=false` 守卫，改 db 后 `rm .introspect-cache.json`
