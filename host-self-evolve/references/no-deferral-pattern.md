## 🚫 No-Deferral Hard Rule (2026-06-12 hardened, 用户原话 "下次也不改 直接解决")

> **历史标 (2026-07-14 ADR-0056 cleanup)**: 下方历史段若提 "5-tool" 是 v2.6.18 时期描述; 实际跑 N-tool (N 当前 = 6, per [~/.claude/rules/protocols/N-tool-search.md](https://example.invalid/~/.claude/rules/protocols/N-tool-search.md) v1.1.2). 保留旧字面作 audit trail.

**禁止任何形式的 "剩余 LOW 项 / 下次 audit 会改善" 的尾部短语.** 这种短语是 theater — 下次 audit 也不会自动改善, 因为没人在中间动它.

### 强制流程

任何 audit 报告中检测到的项 **必须** 走以下三档之一, 没有第四档:

| Tier | 行动 | 不能 |
|------|------|------|
| **解决** | 当场 fix (Tier 1/2/可推荐 Tier 3 per `feedback-auto-recommend-not-ask`) | 不能"留到下次" |
| **降级到非 finding** | 改阈值 / 加 allowlist / 改用 informational summary (不入 health score) | 不能写"虽然 LOW 但下次会自动改善" |
| **真不可处理** | 写到 `must_fix_before_completion` 阻塞 audit 完成 + AskUserQuestion | 不能静默列入 "remaining items" |

### 反例 (禁止)

```text
❌ "剩余 LOW 项: cases 索引部分老条目 / hook 系统已 2 真 orphan 出清 / settings env 漂移. 下次 rich-audit 应直接收到改善的分数"
❌ "These 405 informational LOW findings will resolve over time as skills are updated"
❌ "Recommended: next audit will pick up the cleanup"
❌ "## Remaining items (next session)" / "## Out of scope this run"
```

### 正例 (强制)

```text
✅ "原 405 LOW informational → patched skill_authoring_checker v2.6.16 默认不报 (改阈值, 降级到非 finding). 当前 finding count: 28 MED + 0 LOW."
✅ "Cases 索引经 grep 实证 — 全部 7-20 处引用, 不是 stale, 是 load-bearing. 已校正 audit 误判. Score 维度 'knowledge_cases' raw=62→90."
✅ "env drift MED finding → 用户已固化 feedback-env-drift-accepted, audit 默认跳过. 不再 emit."
```

### Why

- "下次会改善" = scope creep + 责任 dump (没人在 audit 之间专门动 LOW 项)
- 与 `~/.claude/rules/behavioral-process.md §C` "禁止 Deferred items 列表 (零容忍)" 对齐
- 与 `~/.claude/memory/feedback/feedback-auto-recommend-not-ask.md` (2026-06-12) 对齐: 能解决就解决, 不能就阻塞
- audit 工具的诚信 = 当前状态的诚实快照; 报"下次会改善" = 拿未来对赌掩盖当前 (典型 build-pass theater 变种)

### Auto-fix tier mapping (post-2026-06-12)

| Finding 类型 | 默认 tier | 不能做的事 |
|------------|----------|------------|
| 405 LOW informational (metadata.version etc missing) | Tier 0 — 不入 findings | 不能"标 LOW 然后 defer" |
| LOW false positive (cases load-bearing, hook 假 orphan) | Tier 0 — 修阈值/allowlist | 不能"标 LOW 然后 defer" |
| LOW 真问题, claudecode 能修 | Tier 1 自动执行 | 不能"标 LOW 然后 defer" |
| LOW 真问题, 用户偏好接受 | Tier 0 + 写 feedback | 不能"标 LOW 然后 defer" |
| LOW 真问题, 用户必须决策 | Tier 3 阻塞 + AskUserQuestion | 不能"标 LOW 然后 defer" |

---

## ⚠️ Workflow Synthesizer Truncation 反模式 (2026-06-12 hardened)

任何 rich-audit-style workflow 在 final-report 装配阶段, **禁止** 用 `JSON.stringify(multiAgentResults).slice(0, N)` 截断多 agent 输出. 截断会让装配器产生 "tool missing" / "无 disclosure block" 类**幻觉**.

**反例**: `wf_80569fec-62b` (CASE-RICH-AUDIT-WORKFLOW-SYNTHESIZER-TRUNCATION-20260612):
- 5 个 FAS tool segments (总 ~40KB) 序列化后被 `.slice(0, 8000)` 截到只剩前 1-2 个完整披露
- 装配器报 "3/5 tools missing disclosure" → 触发 Layer 2 fail-fast 假警报
- 实际 5 个 jsonl 全部 `stop=end_turn` + 都有 StructuredOutput ✅

**正确做法 (任选)**:
1. **File swap**: `Bash` 写入 `/tmp/rich-audit-<run-id>-<phase>.json`, 装配器 prompt 引用文件路径 + 让它 Read 完整
2. **Pre-summarize**: 每个 agent segment 在传给装配器前压到 ≤500 字符
3. **Truncation aware**: 显式告诉装配器 `"slice 了到 N 字节, full size 是 M, 缺失的看 /tmp/xxx.json"`

**诊断协议** (装配器报 "tool missing" 时):
```bash
# 第一步: 不要相信装配器, 先看 transcript
for jsonl in $WF_DIR/agent-*.jsonl; do
  stop=$(tail -1 "$jsonl" | python3 -c "import json,sys; print(json.loads(sys.stdin.read()).get('message',{}).get('stop_reason','?'))")
  has_so=$(grep -c "StructuredOutput" "$jsonl")
  echo "$jsonl: stop=$stop StructuredOutput=$has_so"
done
# 若全部 stop=end_turn + StructuredOutput≥1 → 100% 装配器 truncation bug, 不要修 L3 协议
```

**Force-All-Search Skills 验证**: kimi-webbridge / anysearch 在 workflow subagent 上下文**完全可用** (通过 Skill tool). 不需要 fallback 到 direct MCP. 但 anysearch 自己会 fallback (这是它内部容错, 与 Skill 加载无关).

---
