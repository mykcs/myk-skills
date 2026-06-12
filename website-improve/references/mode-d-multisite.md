## 模式 D: Multi-Site 编排 (2026-06-08 吞并自 sync-all-sites v1.1.0)

> **适用**：mykcs.github.io / GDKVM / OSA / Academic / wangrui2025(arch) 等 Astro 站点
> **来源**：insights 2026-06-03 — 用户 5-9 parallel agent runs 显著提升 session 完成度
> **吞并决策**：2026-06-08 (CASE-MERGE-SYNC-ALL-SITES-20260608) — 减少 skill 分散, 单一入口更易调用

**适用场景**: 用户要求"在 N 个站点上同时部署 N 个 agent"/"sync all sites"/"fan-out"/"deploy all"。Wall-clock = 最慢站点时长, 通常 10-15 min for 3 sites。

**与 Mode A 关系**: 每个 per-site agent 内部用 Mode A 协议 (Check → Fix → Improve → Verify)。Mode D 是 multi-site 编排层, 负责 4-phase 同步 (验仓/audit/fix/CI)。

### 触发

```bash
# 直接说触发词即可
"sync all sites" / "fan-out 3 sites" / "audit all" / "deploy all" / "multi-site"
"同时在 N 个站点部署 N 个 agent" / "并行 audit" / "3 个独立审计会话变成一次协调操作"
```

默认 scope: `mykcs, GDKVM, OSA` (3 个 active Astro 站). User 可 override scope 指定 sites.

### 4 阶段协议

#### Phase 0: 工具预加载 (L18 硬化, 2026-06-08 Run 4 验证 — 治本 subagent tool loading bug)

> **Run 4 发现**: GDKVM agent 0 tool uses. 错误信息: "SubagentStart hook did not provide working tools to begin audit. Deferred tool schemas (WebFetch, WebSearch, etc.) require ToolSearch loading before use." mykcs + OSA 同时跑 66 + 44 tool uses, 正常. 根因: General-purpose subagent tool provisioning 偶尔失败 (SubagentStart hook 漏 inject 某些 tool schema).

**强制流程** (orchestrator 在 Phase 1 之前必须跑):

```bash
# 1. 显式 load 基础 5 tool (确保 subagent 拿到 schemas)
ToolSearch(query="select:Bash,Read,Edit,Grep,Glob")
```

**为什么**: SubagentStart hook 偶尔漏 inject tool schemas. 预加载是治本方案 — 显式 load 后所有后续 subagent 都能拿到基础 5 tool.

**注意**: 仍可能有其他 deferred tool (WebFetch / WebSearch / LSP / mcp_*) 需 on-demand load. Phase 2 agent prompt 需明确 "如需 WebFetch, 用前先 ToolSearch load".

#### Phase 1: 验仓 (必须先做, 不能跳过)

```bash
# 对每个目标站点：
for site in $SITES; do
  case "$site" in
    mykcs)   repo=~/Repo/webs/active/mykcs.github.io ;;
    GDKVM)   repo=~/Repo/webs/active/GDKVM ;;
    OSA)     repo=~/Repo/webs/active/OSA ;;
    *)       echo "Unknown site: $site"; exit 1 ;;
  esac
  cd "$repo" || exit 1
  echo "=== $site ==="
  git remote -v
  git status --short
  git log @{u}..HEAD --oneline | wc -l
done
```

**abort 条件**:
- 任何站点 `git status` 非空 (uncommitted changes) → 提示用户提交
- 任何站点 `git log HEAD..origin/main` 有新 commit → 提示 `git pull --rebase`

#### Phase 2: 并行 audit (N agent, N = site count)

```text
For each site, launch 1 Agent with this prompt:

You are auditing <SITE_REPO> for SEO/accessibility/i18n/CI/build issues.

**EVIDENCE-BASED AUDIT (强制)**:
每个 issue 必须给出 grep/curl/ls 的实际命令输出, **禁止报"verify X" / "check Y" / "should audit Z"**。
- ❌ BAD: {"fix": "verify if Google Sans is configured"}
- ✅ GOOD: {"fix": "Google Sans fallback — global.css:7 'was Google Sans' comment", "evidence": "grep -n 'Google_Sans\\|Google Sans' src/ 2>/dev/null | head -5"}

**DEAD-CODE PROOF 协议**:
- 报"dead i18n key"前必须 `grep -rn '<key>' src/` 显示 0 matches
- 报"unused font"前必须 `grep -rn 'fontfile' src/ --include="*.astro"` 显示 0 imports
- 报"unused file"前必须 `grep -rn 'filename' src/` 显示 0 references
- **找不到 = 不存在, 不算 dead**

**L14 FINAL MESSAGE PROTOCOL (mandatory, orchestrator 会 grep 验证 JSON 合法性)**:
- 你的 final message MUST 是 EXACTLY 一个 JSON block matching 上面的 schema
- Wrap in ` ```json ... ``` ` 三反引号
- NO prose / NO "Task complete" / NO acknowledgments / NO preamble / NO postamble
- 任何非 JSON 内容 (含 ack / 解释 / "Subagent acknowledged" / "Acknowledged") → orchestrator 拒收, 整个 run 失败, Phase 2/3 需重做
- 验证方式: orchestrator 评分前会 `grep -q '"site":' <output>` + `python3 -c "import json; json.loads(...)"` 双层 check

Output JSON schema:
{
  "site": "<name>",
  "score": 0-100,
  "issues": [
    {"severity": "P0|P1|P2", "type": "seo|a11y|i18n|build|ci|security", "file": "path", "fix": "concrete action", "evidence": "grep/curl/ls output snippet"}
  ]
}

**No `deferred` field** — 报出来就是要 fix 的, 看不到 grep 证据的不报。

Use the website-improve skill (Mode A) for the audit protocol.
Do NOT make any edits — read-only mode.
Report back as a single JSON block.
```

**barrier**: 等所有 agent 返回后聚合。

#### Phase 3: 并行 fix (仅 P0 + P1)

```text
Filter issues by severity ∈ {P0, P1}.
Group by site. Launch 1 Agent per site with this prompt:

Apply the following fixes to <SITE_REPO>:
<issue list>

For each fix:
1. Show the diff
2. Run the relevant build/test command
3. Commit with conventional commit message
4. Push via autopush.sh (not raw git push)

Do NOT touch issues not in this list. (scope discipline)
Do NOT mark done until build passes.

**L14 FINAL MESSAGE PROTOCOL (mandatory)**:
- 你的 final message MUST 是 EXACTLY 一个 JSON block:
{
  "site": "<name>",
  "p0_fixed": <count>,
  "p1_fixed": <count>,
  "p2_deferred": <count>,
  "commits": ["<hash1>: <msg1>", "<hash2>: <msg2>"],
  "ci_status": "green|red|pending|unknown",
  "evidence_blocking": "<reason if not all P0/P1 fixed, else empty>"
}
- Wrap in ` ```json ... ``` ` 三反引号
- NO prose / NO "Task complete" / NO acknowledgments / NO preamble / NO postamble
- 任何非 JSON 内容 → orchestrator 拒收
- 验证方式同 Phase 2 (grep + python3 json.loads)
```

**barrier**: 所有 agent 返回后聚合。

#### Phase 4: CI gate + case 记录

```bash
# Wait for all CI runs to settle
for site in $SITES; do
  echo "=== $site CI ==="
  gh run list --repo <OWNER>/<REPO> --limit 3 --json status,conclusion,name
done
```

**Case file** (强制):
```bash
CASE_PATH=~/.claude/knowledge/cases/CASE-SYNC-ALL-SITES-$(date +%Y%m%d).md
```

### L17 Orchestrator Fallback (Agent ack → 自动 follow-up, 2026-06-08 Run 4 验证)

> **Run 4 发现**: L14 enforcement 2/3 success. 即便 prompt 顶部硬性要求 JSON, 仍有 ~33% agent 返 plain text ack (e.g. OSA "OSA Run 4 audit complete."). L14 内化非 100% 有效.

**强制流程** (orchestrator 在收到 agent final message 后, Phase 2/3 barrier 之前):

1. **验证 L14 compliance**:
   ```bash
   # 双层 check: JSON 存在 + 合法
   grep -q '"site":' <agent_output> && \
   python3 -c "import json; json.loads(<agent_output_with_fences>)"
   ```
2. **L14 失败时**: 自动 `SendMessage(to=<agent_id>, message="L14 violation detected. Please resend your final message as a single JSON block matching the schema, wrapped in \`\`\`json fences. NO other text. NO acknowledgments.")` 一次
3. **二次失败**: 不再 retry, 改用 `git log + gh run list` 重建证据链 (Run 3 fallback 模式). 在 evidence_blocking 字段标注 `"L17 fallback applied: agent returned plain text after 1 retry"`.

**为什么**: L14 prompt 内化非 100% 有效. Orchestrator 端兜底是必要的. 与 Run 3 mykcs agent 行为同款 (那次也用 SendMessage 救场). **不要让 plain-text 失败导致整 run 失败** — 用 fallback 重建即可.

### Output contract (strict 4-section)

```markdown
# sync-all-sites report
