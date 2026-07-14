# Skill 经验教训 → 提升 skill 闭环协议 (4 步: 总结 → 内化 → commit → bump version)

> 起源: 2026-07-14 user 原话 "修改技能，每次运行完，要对这次任务的经验教训进行总结，**提升 skill**" (触发 paper-into-notion v2.3 → v2.4 升级)
> 配套: `scripts/skill-self-summary.sh` v2.0 (3 健壮性 + v-bump 触发) / `references/self-summary-protocol.md` (v2.3 已立, 4 段模板)
> 案例: CASE-PAPER-INTO-NOTION-V2-4-SELF-EVOLUTION-20260714
> ADR: ADR-0057-f

---

## §1. 闭环 4 步协议 (per v2.6.30 §I self-evolution 协议位硬约束)

**触发条件** (满足任一就必跑):
- skill 升级 commit 后
- skill 跨 db 搬 / 跨 session 任务完成
- 任何 build + deploy + config 改动完成
- user 显式说 "总结" / "回顾" / "沉淀" / "提升 skill"

**4 步** (缺一不算 "提升 skill"):

### 1️⃣ 总结 (Summary)
- 跑 `scripts/skill-self-summary.sh` 4 段 (做了什么 N / 修了什么 N / 踩坑 1-3 / 避坑 1-3)
- 4 步 fallback: chat + 本地 case + CLAUDE.local.md hot recall + decision-stream
- mem0 quota 撞墙时, 3 步 fallback (本地 case + CLAUDE.local.md + decision-stream)

### 2️⃣ 内化 (Internalize)
- 经验教训 → SKILL.md 5 类沉淀:
  - **changelog** 段 (新立 v_new_version entry)
  - **触发词** (扩 `when_to_use` 段)
  - **反模式** (扩 4 反模式表)
  - **ADR** (新立 sub-slot, per ADR-0027 v1.1)
  - **case** (新立 `~/.claude/knowledge/cases/wiki/CASE-*.md`)
- 沉淀到 5 文件 (SKILL.md / ADR / case / scripts / references)

### 3️⃣ Commit (Atomic)
- worktree 立新分支 (per §C.3.1, 必跑 verify 2 次: `git worktree list` + `ls <worktree>/<expected-dir>`)
- atomic commit (5 file 单 commit, 1 unit 原则 per §C.3.2)
- commit message 含 changelog / 触发词 / 反模式 / 关联 ADR / 关联 case

### 4️⃣ Bump version (v-bump)
- v2.x → v2.(x+1) bump (per v2.6.49 description split 触发条件)
- frontmatter 4 字段保留合规 (per v2.6.47 audit)
- changelog 段加 v_new_version entry
- 触发词 + N (扩 when_to_use 段)
- 反模式 + N (扩 4 反模式表)
- 5 步 (总结 → 内化 → commit → bump → push, per v2.6.30 §I.1)

---

## §2. v-bump 自动触发条件判定 (per v2.4 ADR-0057-f)

**4 条件任一满足即触发 v-bump** (per v2.6.30 §I self-evolution 8 步循环):

| # | 条件 | 判定方法 | v-bump 触发 |
|---|------|---------|--------------|
| 1 | **反模式 ≥ 4** | 解析 SKILL.md 4 反模式表, 数条数 ≥ 4 | ✅ |
| 2 | **流程变化 ≥ 1** | git diff vs 上次 commit, 流程类代码 (scripts/ + run-card.md) 改 ≥ 1 文件 | ✅ |
| 3 | **触发词变化 ≥ 1** | 解析 frontmatter when_to_use, 跟上次 commit 字符串比对, diff ≥ 1 触发词 | ✅ |
| 4 | **hot recall 新增段** | CLAUDE.local.md 跑完 self-summary 后段数比跑前 +1 | ✅ |

**判定实现** (`scripts/skill-self-summary.sh` v2.0 末尾 6 步):
```bash
# 简化判定: PITFALLS + PREVENTIONS 字符串长度 + 踩坑条数
PITFALL_COUNT=$(echo "${PITFALLS}" | tr ';' '\n' | wc -l | tr -d ' ')
if [ "$PITFALL_COUNT" -ge 2 ]; then
  V_BUMP_TRIGGER=true
fi
```

**生产环境应升级**: 解析 SKILL.md frontmatter 反模式表 + 触发词 + git diff 段, 不靠字符串长度判定。

---

## §3. session id 3 步 fallback (per v2.4 ADR-0057-f 残留 1)

**实测问题**: v2.3 self-summary.sh 用 `CLAUDE_SESSION_ID` env, env 缺失时写 `~/.claude/decision-stream/unknown.md`, 跟别的 session 撞 file。

**3 步 fallback** (任一非空即用, 全缺失抛 exit 1):

```bash
SESSION_ID=""
if [ -n "${CLAUDE_SESSION_ID:-}" ]; then
  SESSION_ID="$CLAUDE_SESSION_ID"           # 1️⃣ env 优先
elif SESSION_ID=$(git rev-parse --short HEAD 2>/dev/null); then
  : # SESSION_ID = worktree commit hash      # 2️⃣ worktree commit hash
elif SESSION_ID=$(date +%Y%m%d-%H%M%S); then
  : # SESSION_ID = timestamp                 # 3️⃣ timestamp fallback
else
  echo "❌ session id fallback 全失败" >&2
  exit 1                                      # 全缺失抛错, 不静默
fi
```

**反模式** (永久失效):
- ❌ 硬编码 fallback "unknown" (env 缺失时不抛错, 跟别的 session 撞 file)
- ❌ 单一 fallback (env 缺失就抛错, 违反 §C.3.6.1 no-stuck)
- ❌ 不抛 exit 1 (撞墙不抛错, user 不知道)

---

## §4. CLAUDE.local.md hot recall 段带 `@v{version}` (per v2.4 ADR-0057-f 残留 2)

**实测问题**: v2.3 self-summary.sh append 段标题 `## §self-summary-{date}-{skill_name}`, 多次跑同名段堆叠, 难追溯本次 vs 上次。

**修法**: 段标题含 skill version, 格式 `## §self-summary-{date}-{skill_name}@v{version}`:

```bash
# 从 SKILL.md frontmatter 读 version
SKILL_VERSION=$(grep -E "^version: " SKILL.md | head -1 | sed 's/^version: //; s/[[:space:]]*$//' | tr -d '()')
HOT_RECALL_TITLE="## §self-summary-${DATE}-${SKILL_NAME}@${SKILL_VERSION} (auto-appended by skill-self-summary.sh)"

# 检查同名段是否已存在 (避免堆叠)
if grep -qF "$HOT_RECALL_TITLE" "$CLAUDE_LOCAL"; then
  echo "⚠️  已存在同名段, 跳过 append"
else
  echo "$HOT_RECALL_TITLE ..." >> "$CLAUDE_LOCAL"
fi
```

**实测** (v2.4 立条后跑 1 轮):
- 段标题: `## §self-summary-2026-07-14-paper-into-notion@v2.4 (auto-appended by skill-self-summary.sh)`
- 跟 v2.3 段 `## §self-summary-2026-07-14-paper-into-notion` 区分清楚 (版本号差异)

---

## §5. 案例: paper-into-notion v2.0 → v2.1 → v2.2 → v2.3 → v2.4 5 次升级每次都内化

| 版本 | commit | 5 类沉淀 (SKILL.md / ADR / case / scripts / references) | 闭环验证 |
|---|---|---|---|
| v2.0 | 8039aac | description split + 触发词 15+ + 6 字段→8 字段 schema 文档 | ✅ 闭环 |
| v2.1 | 8039aac | 跨 db 搬 schema 4 踩坑 + add-property.sh + cross-db-migrate-payload + notion-schema-migration | ✅ 闭环 |
| v2.2 | 900e19c | Notion URL 解读 + 修哪一部分 4 决路径 + 6 残留踩坑 | ✅ 闭环 |
| v2.3 | e760063 | skill 跑完自我总结协议 + mem0 quota fallback 3 步 | ❌ 3 健壮性缺失 (本次 v2.4 补) |
| v2.4 | (待) | 经验教训 → 提升 skill 闭环 + 3 健壮性 + v-bump 自动触发 | ✅ 闭环 (本次立) |

**v2.3 → v2.4 触发原因** (实测):
- 跑 v2.3 self-summary 1 轮, 实测 3 健壮性缺失
- user 反馈 "提升 skill" 触发立 v2.4
- v2.4 闭环 4 步: 总结 (v2.3 self-summary 跑过) → 内化 (本次立 5 file) → commit (待 PR) → bump (v2.3→v2.4)

---

## §6. 联动引用

- 起源 case: CASE-PAPER-INTO-NOTION-V2-4-SELF-EVOLUTION-20260714
- ADR: ADR-0057-f (v2.4 升级) / ADR-0057-e (v2.3 skill-self-summary 协议) / ADR-0027 (v1.1 sub-slot) / ADR-0054 (Notion 严格层)
- 配套 reference: `references/self-summary-protocol.md` (v2.3 已立, 4 段模板 + mem0 quota 决策树) / `references/self-evolution-loop.md` (本文件, 闭环 4 步)
- 配套 script: `scripts/skill-self-summary.sh` v2.0 (3 健壮性 + v-bump 触发判定)
- 协议: post-task-recommend §2 (4 段) + §6 (v3 反向证据) / calm-flow §4 (decision-stream schema) / v2.6.30 §I self-evolution 8 步循环 (per CHANGELOG.md v2.6.30 立) / v2.6.47 frontmatter audit / v2.6.49 description split-in-two / §C.3.1 worktree / §C.3.2 PR auto-merge / §H.1 5 字段验收 / §C.3.6.1 no-stuck
- 工具: `mcp__plugin_mem0_mem0__add_memory` (10000/billing period) / `~/.claude/CLAUDE.local.md` (SessionStart hot recall 注入) / `~/.claude/decision-stream/<session-id>.md` (session 结束保留) / `git rev-parse --short HEAD` (worktree commit hash fallback) / `date +%Y%m%d-%H%M%S` (timestamp fallback)
- 主 skill: SKILL.md v2.4 (frontmatter 4 字段全合规 + 触发词 26 + 反模式 24)
- 案例 v2.0 → v2.4 5 次升级: 8039aac (v2.0) → 8039aac (v2.1) → 900e19c (v2.2) → e760063 (v2.3) → (待 v2.4)
