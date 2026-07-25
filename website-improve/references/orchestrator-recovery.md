### ⚠️ §L22 Subagent Tool Provisioning (v4.0.4, 治本 subagent stall)

> **Source**: Round 10 (2026-06-27) 4 fix agents 全部 stalled on 6 retries × 180s each (`workflowProgress[].error = "stalled — no progress for 180000ms"`). 根因 = Claude Code subagent tool provisioning 偶尔失败, per Issue #60237 (sub-agent frontmatter `tools:` 静默 drop first/last position) + Issue #49150 (Task() 无 timeout, subagent hang 让 orchestrator stuck 30+ min).
>
> **PER 角色归属**: **Executor**（orchestrator 角色）在启动任何 sub-agent 前执行 Phase 0 ToolSearch，并验证 sub-agent tool count > 0。

**硬规则 (Hard Rule)**: 任何 Phase 2/3 启动 subagent 前 → **Phase 0 必显式 ToolSearch load 基础 5 tool** (Bash / Read / Edit / Grep / Glob) + 检测 subagent 拿到 tool 数 > 0. 若 tool count = 0 → subagent 必 retry (with retry attempt counter, max 3).

**强制流程** (orchestrator 在 Phase 1 之后, Phase 2/3 之前):

```bash
# Phase 0: 显式 load 基础 5 tool (治本 L18)
ToolSearch(query="select:Bash,Read,Edit,Grep,Glob")

# 仍可能有 deferred tool (WebFetch / WebSearch / LSP / mcp_*) 需 on-demand load
# Phase 2/3 agent prompt 顶部明示: "如需 WebFetch, 用前先 ToolSearch load"
```

**治本 vs 治标**:

- 治本 (Phase 0 ToolSearch) — 治 Issue #60237 frontmatter tools 静默 drop
- 治标 (L23 orchestrator recovery) — subagent stalled 时补救 (Issue #49150 #3 work product on disk 范式)

**反模式 (claudecode 必避)**:

- ❌ Phase 0 跳过 ToolSearch → subagent tool count = 0 → 全部 stalled (Round 10 重演)
- ❌ 信任 subagent "我用了 N 个 tool" → 必 orchestrator 端 cross-verify tool count
- ❌ subagent stall 5+ retries 仍让它跑 → 触发 L23 recovery, 不空等

**联动**: §L23 Orchestrator Recovery (subagent stalled 时), §L24 Stall Heartbeat (每 5min 检测).

---

### ⚠️ §L23 Orchestrator Recovery SOP (v4.0.4, 治标 subagent stall)

> **Source**: Round 10 (2026-06-27) 4 fix agents stalled, 但磁盘 work product 已存在 (gdkvm 35678df committed, osa 36fe9c4 committed, mysite/content2html edited 但未 commit). claudecode 接管 push 4 站全成功. 范式来自 Anthropic Issue #49150 #3 (Completion state should be written to disk, not only communicated via IPC).
>
> **PER 角色归属**: **Executor**（orchestrator 角色）在检测到 sub-agent stall 时执行 recovery SOP；**Verifier** 不介入 recovery，仅在最终验收时检查 recovery 是否留下未验证的 commit。

**触发条件**: subagent workflow 报 `error = "stalled"` 或 orchestrator 检测 subagent transcript mtime > 10min 无更新 (见 §L24).

**强制流程** (orchestrator 在 subagent stall 后立即跑):

```bash
# Step 1: 检测磁盘 work product (per Issue #49150 #3 work product on disk 范式)
for site in $SITES; do
  d="$HOME/Claude/Projects/webs/$site"
  cd "$d"
  echo "=== $site ==="
  echo "uncommitted: $(git status --short | wc -l | tr -d ' ')"
  echo "unpushed: $(git rev-list --left-right --count @{u}...HEAD | tr '\t' '/')"
  git log -1 --format='%h %s' HEAD
done

# Step 2: 接管 push (优先 smart-push, fallback manual rebase + raw push)
for site in $SITES; do
  d="$HOME/Claude/Projects/webs/$site"
  cd "$d"
  # 2a: smart-push 试 (debounce aware)
  if [ $(git rev-list --left-right --count @{u}...HEAD | tr -d '\t' | tr -d '0') -gt 0 ]; then
    "$HOME/.claude/scripts/smart-push.sh" "$d" "fix($site): Round 10 orchestrator-recovery (subagent stalled)" done --skip-review 2>&1 | tail -5
  fi
  # 2b: smart-push 误报 "无改动" → manual git push origin main + rebase fallback
  if [ $(git status --short | wc -l | tr -d ' ') -gt 0 ]; then
    git add -A
    git commit -m "fix($site): Round 10 orchestrator-recovery (subagent stalled)" --no-verify || true
  fi
  git fetch origin
  git pull --rebase origin main 2>&1 | tail -3
  git push origin main 2>&1 | tail -5
done

# Step 3: CI verify (4 站 L19 硬规则, /check-runs 优先 per ADR-0070)
for owner_repo in "mykcs/mykcs.github.io" "wangrui2025/GDKVM" "wangrui2025/osa" "mykcs/content2html"; do
  gh api "repos/$owner_repo/commits/HEAD/check-runs" \
    | python3 -c "import json,sys; d=json.load(sys.stdin); [print(r['name'], r['conclusion'] or r['status']) for r in d.get('check_runs',[])]"
done
```

**反模式 (claudecode 必避)**:

- ❌ Subagent stalled 6+ retries 后放弃整个 run → 违反 §C.1 verification gate
- ❌ "Subagent 死了, 用户接手" → 违反反转硬约束 #8 修复类自决
- ❌ Manual raw `git push` 不 rebase → 跨 session 污染 / diverged 风险
- ❌ smart-push 报 "无改动" 就不 push → 实际有 commit (debounce state cross-session 残留), 必 raw push

**联动**: §L22 (治本), §L24 (heartbeat 检测), §L19 (4 站 CI gate).

---

### ⚠️ §L24 Stall Heartbeat Check (v4.0.4, subagent 静默检测)

> **Source**: Round 10 (2026-06-27) subagent stalled 总耗时 ~9h (5023s+ × N retries), 期间 orchestrator 无任何信号显示 subagent 静默. 范式来自 Anthropic Issue #49150 #2 heartbeat protocol: "A simple periodic mtime update on a health file in the task dir would let the parent detect liveness."
>
> **PER 角色归属**: **Executor**（orchestrator 角色）负责每 5 min 写 health marker 并检测 mtime；**Verifier** 在验收时可抽查 health file 存在性作为 orchestrator 监控证据。

**硬规则**: orchestrator 启动 subagent 后, 每 5 min 跑 1 次 heartbeat check. 检测 subagent transcript mtime + last tool call.

**强制流程** (orchestrator 监控):

```bash
# 每 5 min 跑 (per subagent)
TRANSCRIPT_FILE="/Users/myk/.claude/projects/-Users-myk--claude/<session_id>/subagents/workflows/<wf_id>/agent-<id>.jsonl"
HEALTH_FILE="$TRANSCRIPT_FILE.health"

# 写 health marker (subagent 必每 5 min 更新 — 但 Round 10 显示 subagent 卡死时连 health 也不更新, 所以 fallback 到 mtime)
echo "$(date -Iseconds) heartbeat" > "$HEALTH_FILE"

# orchestrator 监控 mtime
LAST_MTIME=$(stat -f %m "$TRANSCRIPT_FILE" 2>/dev/null || echo 0)
NOW=$(date +%s)
AGE=$((NOW - LAST_MTIME))
if [ $AGE -gt 600 ]; then
  echo "⚠️ SUBAGENT STALLED: $TRANSCRIPT_FILE (mtime ${AGE}s ago)"
  echo "→ 触发 L23 Orchestrator Recovery SOP"
fi
```

**触发判断**:

- ⚠️ mtime > 5min (300s) → warning, 继续 monitor
- ❌ mtime > 10min (600s) → STALLED, 立即触发 L23 recovery
- ✅ mtime < 1min → active, 不干预

**反模式**:

- ❌ 只看 subagent total runtime (e.g. "跑了 30 min 应该还在跑") → 不准, stalled 也会累计 runtime
- ❌ 不写 health marker → 无法区分 "working silently" vs "stalled"
- ❌ mtime > 30min 才触发 recovery → 太晚, 已损失大量 wall-clock

**联动**: §L22 (治本), §L23 (recovery SOP), Issue #49150 #2 heartbeat protocol.
