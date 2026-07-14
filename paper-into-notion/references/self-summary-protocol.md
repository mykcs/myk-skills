# Skill 跑完自我总结协议 (4 段模板 + mem0 quota fallback)

> 起源: 2026-07-14 user 原话 "修改技能，每次运行完，要对这次任务的经验教训进行总结" (触发 paper-into-notion v2.2 → v2.3 升级)
> 配套: `scripts/skill-self-summary.sh` (独立可跑) / `~/.claude/CLAUDE.local.md` §self-summary-protocol 段 (hot recall)
> 案例: CASE-PAPER-INTO-NOTION-V2-3-SELF-SUMMARY-20260714
> ADR: ADR-0057-e

---

## §1. 4 段模板 (per post-task-recommend §2 硬规则)

**触发条件** (满足任一就必跑):
- skill 升级 commit 后
- skill 跨 db 搬 / 跨 session 任务完成
- 任何 build + deploy + config 改动完成
- user 显式说 "总结" / "回顾" / "沉淀"

**输出格式** (严格 4 段, 灵魂 v3/v4/v5/v6 自检):

```markdown
## 任务后建议

### 这次踩坑 (1-3 条)
- [踩坑现象] — 根因 / 当时为什么没识别
- 例: "改了 3 次才定位到 ADR-0027 v1.0 sub-slot 边界" — 根因: 没先 grep 现状

### 未来怎么避 (1-3 条)
- [可执行的避坑动作] — 为什么能避
- 例: "立新 ADR 前必跑 §3 现状 grep 6 件套" — per cross-session-grep-mandatory.md §1
```

**灵魂 v3 自检 (per post-task-recommend §6)**:
- ✅ 1 段 ≤ 15 行
- ✅ 1 问 ≤ 1 个 (如需)
- ✅ 字母选项必翻译
- ✅ 不用 "显然 / 你懂的 / 复杂协议名"
- ✅ 列表 ≤ 5 项, 表格 ≤ 5 列
- ✅ 开头 ≤ 3 句 (现状+进展+下一步)
- ✅ **没有 "可推迟事项功能段"** (per v3 反向证据)

**灵魂 v6 自检 (per post-task-recommend §6 v3 清理)**:
- ❌ 不能写 "3 件 follow-up" / "next step" / "下次 session 顺手做"
- ❌ 不能写可推迟事项功能段 (任何变体)
- ✅ 能顺手做的可自决事项必立即自决 (install / commit / 跑 e2e test / 立 case file)

## §2. mem0 quota fallback 决策树 (per CASE-MEM0-QUOTA-FALLBACK-LOCAL-20260714)

**mem0 quota 限制**: 10000 events / billing period (monthly), 撞墙返 400 `Usage quota exceeded`, 等下月自动重置。

```
跑 add_memory
  │
  ├─ 成功 → ✅ 沉淀完成
  │
  └─ 返 400 quota exceeded → 立即跑 3 步 fallback (不反问 user, 不重试)
      ├─ Step 1: 写本地 case file (per ~/.claude/knowledge/cases/wiki/CASE-*.md)
      ├─ Step 2: append CLAUDE.local.md §self-summary-{date} 段 (hot recall 强制入口)
      └─ Step 3: append decision-stream (per calm-flow §4, session 结束保留)
```

**反模式 (永久失效)**:
- ❌ "add_memory 失败等下月" — 浪费 17 天, 跨 session 失忆
- ❌ "add_memory 失败反问 user 要不要 add" — 甩锅, 违反 §C.3.6.1 no-stuck
- ❌ "add_memory 失败重试 3+ 次" — 浪费 session 时间
- ❌ "summary 落 chat 不落本地" — 跨 session 找不到 (§C.2 deferred theater)

**CLAUDE.local.md hot recall 强制入口**:
- SessionStart 自动注入, 跟 mem0 同等效果
- 不依赖 quota, 不依赖 mem0 服务可用
- 限制: 需手动改文件 (git 仓, tracked, 不是 .gitignore)

## §3. decision-stream append schema (per calm-flow §4)

**文件位置**: `~/.claude/decision-stream/<session-id>.md`

**append 格式** (YAML-like record):

```yaml
- ts: 2026-07-14T15:30:00+08:00    # 时刻 (ISO 8601 + timezone)
  type: auto-decide                  # auto-decide | must-ask
  content: "skill-self-summary: paper-into-notion 跑完自我总结"
  decision: "做了什么=... | 修了什么=... | 踩坑=... | 避坑=..."
  impact: "skill 跑完经验教训跨 session 沉淀 (本地 case + CLAUDE.local.md + decision-stream)"
  reversible: true                   # 可逆性 (写文件 + commit + push, 都可 git revert)
  risk: low                          # low | medium | high
  reason: "per post-task-recommend §2 硬规则 + user 2026-07-14 原话"
```

**限制** (per calm-flow §9):
- session 隔离: 决策流不跨 session 聚合
- 切到不同 session = 不同流
- session 结束保留 (不删, 累计历史)

## §4. 案例: paper-into-notion v2.0 → v2.1 → v2.2 → v2.3 4 次升级自我总结

| 版本 | 跑完时点 | 总结方式 | 4 段内容 |
|---|---|---|---|
| v2.0 | 2026-07-14 12:00 | 手动补 (反协议) | description split + 触发词扩 15+ |
| v2.1 | 2026-07-14 14:00 | 手动补 (反协议) | 跨 db 搬 schema 4 踩坑 (信任 docs / strip id / property name / workspace archive) |
| v2.2 | 2026-07-14 15:00 | 手动补 (反协议) | Notion URL 解读 + 修哪一部分 4 决路径 + 6 残留踩坑 |
| v2.3 | 2026-07-14 16:00 | **自动跑** (per skill-self-summary.sh) | skill 跑完自我总结协议 + mem0 quota fallback 3 步 |

**v2.3 立条时** (per CASE-PAPER-INTO-NOTION-V2-3-SELF-SUMMARY-20260714):

### 这次踩坑 (3 条)
1. 4 次升级 + 1 次跨 db 搬都没自动总结, user 显式触发 (反协议, per post-task-recommend §2 硬规则)
2. mem0 add_memory 撞墙后没立即 fallback, 反问 user "要不要 add" 浪费 1 轮 (违反 §C.3.6.1 no-stuck)
3. 总结协议没指定"必须写文件路径", 默认 user 复制粘贴 = 卸给 user (违反 post-task-recommend §2 灵魂 v6)

### 未来怎么避 (3 条)
1. skill 跑完必跑 skill-self-summary.sh (4 段 + mem0 fallback 3 步), 不可省, 不可推迟
2. add_memory 撞墙立即 3 步 fallback (本地 case + CLAUDE.local.md + decision-stream), 不反问
3. skill 升级 commit 必含 CHANGELOG.md + 自我总结 case file, 缺失则 pre-commit 拦截

## §5. 联动引用

- 起源 case: CASE-PAPER-INTO-NOTION-V2-3-SELF-SUMMARY-20260714
- ADR: ADR-0057-e (v2.3 升级) / ADR-0027 (v1.1 sub-slot) / ADR-0054 (Notion 严格层)
- 配套 script: `scripts/skill-self-summary.sh` (独立可跑, 跨 skill 通用)
- 协议: post-task-recommend §2 (4 段模板) + §6 (v3 反向证据, 不可推迟事项) / calm-flow §4 (decision-stream schema) / CASE-MEM0-QUOTA-FALLBACK-LOCAL-20260714 (mem0 quota fallback 决策树) / §C.3.6.1 no-stuck (撞墙立即 fallback) / §C.2 deferred theater (反模式)
- 工具: `mcp__plugin_mem0_mem0__add_memory` (10000/billing period) / `~/.claude/CLAUDE.local.md` (SessionStart hot recall 注入) / `~/.claude/decision-stream/<session-id>.md` (session 结束保留) / `~/.claude/knowledge/cases/wiki/` (永久 case 归档)
- 主 skill: SKILL.md v2.3 (frontmatter 4 字段全合规 + 触发词 24 + 反模式 19)
- mem0 官方: https://app.mem0.ai/dashboard/billing (quota 用量查询入口)
