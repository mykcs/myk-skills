---
name: devfleet
description: Orchestrates parallel Claude Code agents via Claude DevFleet — plans projects from natural language, dispatches agents in isolated worktrees, monitors progress, and reads structured reports.
---

# devfleet

> Migrated from `~/.claude/commands/devfleet.md` on 2026-06-15.
> Original slash command continues to work; this skill version supports auto-trigger by description keyword.

Orchestrate parallel Claude Code agents via Claude DevFleet. Each agent runs in an isolated git worktree with full tooling.

Requires the DevFleet MCP server: `claude mcp add devfleet --transport http http://localhost:18801/mcp`

## Flow

```
User describes project
  → plan_project(prompt) → mission DAG with dependencies
  → Show plan, get approval
  → dispatch_mission(M1) → Agent spawns in worktree
  → M1 completes → auto-merge → M2 auto-dispatches (depends_on M1)
  → M2 completes → auto-merge
  → get_report(M2) → files_changed, what_done, errors, next_steps
  → Report summary to user
```

## Workflow

1. **Plan the project** from the user's description:

```
mcp__devfleet__plan_project(prompt="<user's description>")
```

This returns a project with chained missions. Show the user:
- Project name and ID
- Each mission: title, type, dependencies
- The dependency DAG (which missions block which)

2. **Wait for user approval** before dispatching. Show the plan clearly.

3. **Dispatch the first mission** (the one with empty `depends_on`):

```
mcp__devfleet__dispatch_mission(mission_id="<first_mission_id>")
```

The remaining missions auto-dispatch as their dependencies complete (because `plan_project` creates them with `auto_dispatch=true`). When manually creating missions with `create_mission`, you must explicitly set `auto_dispatch=true` for this behavior.

4. **Monitor progress** — check what's running:

```
mcp__devfleet__get_dashboard()
```

Or check a specific mission:

```
mcp__devfleet__get_mission_status(mission_id="<id>")
```

Prefer polling with `get_mission_status` over `wait_for_mission` for long-running missions, so the user sees progress updates.

5. **Read the report** for each completed mission:

```
mcp__devfleet__get_report(mission_id="<mission_id>")
```

Call this for every mission that reached a terminal state. Reports contain: files_changed, what_done, what_open, what_tested, what_untested, next_steps, errors_encountered.

## All Available Tools

| Tool | Purpose |
|------|---------|
| `plan_project(prompt)` | AI breaks description into chained missions with `auto_dispatch=true` |
| `create_project(name, path?, description?)` | Create a project manually, returns `project_id` |
| `create_mission(project_id, title, prompt, depends_on?, auto_dispatch?)` | Add a mission. `depends_on` is a list of mission ID strings. |
| `dispatch_mission(mission_id, model?, max_turns?)` | Start an agent |
| `cancel_mission(mission_id)` | Stop a running agent |
| `wait_for_mission(mission_id, timeout_seconds?)` | Block until done (prefer polling for long tasks) |
| `get_mission_status(mission_id)` | Check progress without blocking |
| `get_report(mission_id)` | Read structured report |
| `get_dashboard()` | System overview |
| `list_projects()` | Browse projects |
| `list_missions(project_id, status?)` | List missions |

## Guidelines

- Always confirm the plan before dispatching unless the user said "go ahead"
- Include mission titles and IDs when reporting status
- If a mission fails, read its report to understand errors before retrying
- Agent concurrency is configurable (default: 3). Excess missions queue and auto-dispatch as slots free up. Check `get_dashboard()` for slot availability.
- Dependencies form a DAG — never create circular dependencies
- Each agent auto-merges its worktree on completion. If a merge conflict occurs, the changes remain on the worktree branch for manual resolution.

## Self-Heal on CI Failure (2026-06-24)

> 来源: 用户提的 meta-pattern "自治多站点 Fleet Operator" 显式要求"CI fail 时 spawn 子 agent 来自愈",原 §Guidelines line 93 只说"read report before retry",无 child-spawn 协议。

**触发**: `get_mission_status(mission_id)` 返回 `status=failed` 且 `errors_encountered` 含 CI / GitHub Actions / HTTP 5xx failure code。

**协议**:

1. **先 read 失败 mission 的 report** (`get_report(mission_id)`) 找具体 CI fail reason。
2. **不要直接 retry**: 同一 prompt retry = 同一输出,再次 fail 的概率高。违反 process.md §C.7 cascade-kill 反模式 ("重启一下就好了")。
3. **派生 child mission** 修复 root cause:
   ```
   mcp__devfleet__create_mission(
     project_id=<same_project_id>,
     title="self-heal: <mission_id> CI fail — <reason>",
     prompt="<original_prompt> + CI log first 30 lines + ask: 1) read CI log 2) identify root cause 3) apply minimal fix 4) re-run tests 5) commit to worktree branch",
     depends_on=[<original_mission_id>],
     auto_dispatch=true
   )
   ```
4. **child 完成后**: 检查 `get_report(child_id)` → `status=success` → 主 mission mark resolved via child report; `status=failed` → 进 step 5。
5. **循环上限**: self-heal chain max depth 3 (避免 infinite recursion 吃光 concurrency slot)。depth 3 仍 fail → AskUserQuestion 给用户,不静默 spawn 第 4 次。

**硬规则**:
- ❌ 同一 mission_id retry without derive child → 等于 "重启一下就好了",process.md §C.7 反模式
- ❌ child mission prompt 不附 CI log → child 看不到 root cause,会瞎猜 fix
- ❌ self-heal chain 没 max depth → 无限递归 spawn,占满 agent concurrency slot
- ✅ child mission 显式 `depends_on=<failed_mission_id>` → 串成 dependency chain,DevFleet DAG 不会 race
- ✅ max 3 次 self-heal → 失败后 AskUserQuestion,符合 process.md §C.2 zero-deferred

**反模式 (claudecode 历史踩过)**:
- 派生 child 但 prompt 不变 → child 走相同路径,fix 不了 root cause
- self-heal chain 没 max depth → 无限递归 (CASE-CODEX-MINIMAX-FISH-ORPHAN-CASCADE-20260622 同源问题)

## Shared State via /tmp/fleet-state.json (2026-06-24)

> 来源: 用户 meta-pattern "自治多站点 Fleet Operator" 显式提"通过共享 state 文件交换发现",原 SKILL.md 走 DevFleet MCP 内部 state,无 user-facing shared file 协议。

**触发**: 多 fleet operator / 第三方 monitor script 需要跨 session / 跨 agent 看到 fleet 状态 (e.g. CI dashboard / Slack notifier / 定时 cron check)。

**写协议 (POSIX atomic rename)**:

```bash
STATE_FILE=/tmp/fleet-state.json
TMP_FILE="${STATE_FILE}.tmp.$$"
cat > "$TMP_FILE" <<EOF
{
  "ts": "$(date -Iseconds)",
  "fleet_id": "<project_id>",
  "missions": {
    "<mission_id>": {
      "status": "<dispatched|running|success|failed>",
      "last_update": "<ISO 8601>",
      "agent_id": "<id>",
      "files_changed": <n>,
      "errors": []
    }
  }
}
EOF
mv "$TMP_FILE" "$STATE_FILE"   # POSIX rename(2) atomic, never truncate in-place
```

**频率**: 每个 mission 状态变更后立即 update (dispatched → running → success/failed),≤ 1 Hz (避免 race)。

**读协议 (concurrent-safe)**:

```bash
# Atomic read with file lock
flock -s /tmp/fleet-state.json.lock cat /tmp/fleet-state.json | jq '.missions'
```

**硬规则**:
- ❌ truncate `/tmp/fleet-state.json` in-place (`> file` / `echo > file`) → reader 拿到 partial JSON → parse error cascade
- ❌ 不用 `mv` 走 tmp file → POSIX rename 是 atomic,直接覆盖不是
- ❌ 跨 session 共享时不 lock → concurrent writer tear
- ❌ 把 state 写到 `~/.claude/state/fleet.json` → 跟 ~/.claude 是 git 仓冲突 + 权限问题
- ✅ 始终 write 到 `.tmp.<pid>` → `mv` 覆盖 → POSIX atomic rename guarantee
- ✅ monitor 用 `flock -s` 读 → 防止读到 partial write

**反模式**:
- 不用 jq 直接 cat + grep → 解析脆弱,字段顺序敏感
- 多个 writer 不做 PID 锁 → last-writer-wins,history 丢失

