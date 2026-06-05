---
name: sync-all-sites
description: 跨 3-5 个 Astro 站点的并行 audit + fix + deploy 编排
metadata:
  type: skill
  version: 1.0.0
  author: myk
  source: insights-friction-2026-06-03
  requires: [website-improve, context-verify.sh, gh-api-push.sh]
---

# /sync-all-sites — 多站点并行同步

> 适用：mykcs.github.io / GDKVM / OSA / Academic / wangrui2025(arch) 等 Astro 站点
> 来源：insights 2026-06-03 — 用户 5-9 parallel agent runs 显著提升 session 完成度

## 触发

```bash
/sync-all-sites [scope=audit|fix|deploy|full] [sites=mykcs,GDKVM,OSA]
```

默认：`scope=full`, `sites=mykcs,GDKVM,OSA`

## 4 阶段协议

### Phase 1: 验仓（必须先做，不能跳过）

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

**abort 条件**：
- 任何站点 `git status` 非空（uncommitted changes）→ 提示用户提交
- 任何站点 `git log HEAD..origin/main` 有新 commit → 提示 `git pull --rebase`

### Phase 2: 并行 audit（3-5 agent）

```text
For each site, launch 1 Agent with this prompt:

You are auditing <SITE_REPO> for SEO/accessibility/i18n/CI/build issues.

**EVIDENCE-BASED AUDIT (强制)**：
每个 issue 必须给出 grep/curl/ls 的实际命令输出，**禁止报"verify X" / "check Y" / "should audit Z"**。
- ❌ BAD: `{"fix": "verify if Google Sans is configured"}`
- ✅ GOOD: `{"fix": "Google Sans fallback — global.css:7 'was Google Sans' comment", "evidence": "grep -n 'Google_Sans\\|Google Sans' src/ 2>/dev/null | head -5"}`

**DEAD-CODE PROOF 协议**：
- 报"dead i18n key"前必须 `grep -rn '<key>' src/` 显示 0 matches
- 报"unused font"前必须 `grep -rn 'fontfile' src/ --include="*.astro"` 显示 0 imports
- 报"unused file"前必须 `grep -rn 'filename' src/` 显示 0 references
- **找不到 = 不存在，不算 dead**

Output JSON schema:
{
  "site": "<name>",
  "score": 0-100,
  "issues": [
    {"severity": "P0|P1|P2", "type": "seo|a11y|i18n|build|ci|security", "file": "path", "fix": "concrete action", "evidence": "grep/curl/ls output snippet"}
  ]
}

**No `deferred` field** — 报出来就是要 fix 的，看不到 grep 证据的不报。

Use the website-improve skill (v3.3+) for the audit protocol.
Do NOT make any edits — read-only mode.
Report back as a single JSON block.
```

**barrier**：等所有 agent 返回后聚合。

### Phase 3: 并行 fix（仅 P0 + P1）

```text
Filter issues by severity ∈ {P0, P1}.
Group by site. Launch 1 Agent per site with this prompt:

Apply the following fixes to <SITE_REPO>:
<issue list>

For each fix:
1. Show the diff
2. Run the relevant build/test command
3. Commit with conventional commit message
4. Push via gh-api-push.sh (not raw git push)

Do NOT touch issues not in this list. (scope discipline)
Do NOT mark done until build passes.
```

**barrier**：所有 agent 返回后聚合。

### Phase 4: CI gate + case 记录

```bash
# Wait for all CI runs to settle
for site in $SITES; do
  echo "=== $site CI ==="
  gh run list --repo <OWNER>/<REPO> --limit 3 --json status,conclusion,name
done

# If any failed, do NOT mark done — list in deferred items
```

**Case file** (强制):
```bash
CASE_PATH=~/.claude/knowledge/cases/CASE-SYNC-ALL-SITES-$(date +%Y%m%d).md
cat > "$CASE_PATH" <<EOF
# sync-all-sites run $(date -Iseconds)

## Sites synced
- $SITES

## Audit scores
<JSON aggregate>

## Fixes applied
<list>

## CI status
<list>

## Action items (当场执行 — no deferred)
- [x] DONE: <item> (commit <hash>, ci green)
- [ ] BLOCKED on <X>: <item> — trigger: <user runs Y / CI shows Z>
- [ ] NEEDS USER INPUT: <question> (use AskUserQuestion inline, not in this list)

## Lessons
<bullet list — only lessons learned, no follow-up TODOs>
EOF
```

## Output contract

```markdown
# sync-all-sites report

## Sites
- mykcs: score=98, fixes=3, ci=green ✅
- GDKVM: score=87, fixes=12, ci=green ✅
- OSA:   score=92, fixes=5, ci=green ✅

## Total commits
N

## Case file
~/.claude/knowledge/cases/CASE-SYNC-ALL-SITES-YYYYMMDD.md
```

**禁用的输出段**（2026-06-05 规则硬化）：
- ❌ `## Deferred items (next run)` 列表
- ❌ `## P2 (out of scope this run)` 段落
- ❌ `## Followup` / `## TODO next session` / `## Carried over` 任何形式
- ❌ 案例文件"Lessons"段里出现"待做" / "建议改" / "应该审计" 的 follow-up 项

**未完成项的唯一合法出口**：
1. 当场 commit + push（"已完成 N 项" 写入 case）
2. `AskUserQuestion` 立即问用户（不静默 defer）
3. 标 `BLOCKED on <X>` 并写明触发条件（"等用户跑 X 命令" / "等 CI 跑完确认 Y"）

## 硬规则

- ❌ 跳过 Phase 1 验仓 → 禁止进入 Phase 2
- ❌ Phase 3 编辑未被 issue 列表覆盖的文件 → scope creep
- ❌ 任何 CI red 时声明"完成" → verification gate 违反
- ❌ 不写 case 文件 → self-evolution 协议违反
- ❌ 输出报告含 "Deferred items" 段 → 零容忍
- ❌ audit 报"verify X 是否存在"式推测 → 必须 grep/curl 给出证据
- ✅ 任何 abort 条件触发时立即停，不重试

## 已知反模式

- **快速通道**：跳过 Phase 1 直接派 agent → 改错仓（已发生 4+ 次）
- **silent skip**：CI red 不报"未完成"
- **全量 auto-apply**：把 P2 也一起 fix → scope creep
- **不写 case**：跑完不沉淀 → 下次跑同样的问题
- **deferred theater**（2026-06-05 新增）：用"Deferred items"段把没做的事写得很整齐，假装在管理 follow-up → 实际等于不做的合法化包装
- **speculative audit**（2026-06-05 新增）：audit 报"verify X" / "check Y" / "should audit Z" → 不是审计，是 todo list。审计必须 grep/curl 给出具体证据（`grep -rEn 'pattern' src/` 输出行号 / `curl -sI <url>` 输出状态码 / `ls -la <file>` 输出大小）。**无证据 = 不存在**
- **fake dead code**（2026-06-05 新增）：报"5 个 dead i18n keys"但其中 3 个根本不在 i18n 文件里（不是 dead，是从未存在）→ 删除前必须 grep 证明 dead，否则就是数据捏造

## 与其他 skill 的关系

- `website-improve` — Phase 2/3 的 audit 协议来自此 skill
- `confirm-edit` — Phase 1 的"验仓"在每个 site 复用
- `context-verify.sh` — Phase 1 验仓的底层工具
- `gh-api-push.sh` — Phase 3 push 走此脚本避免 timeout

## v1.0.0 已知限制

- 不处理 monorepo（每个 site 必须是独立 git 仓）
- 不处理"某站点需要不同的 base branch"（默认 main）
- 不处理"某站点有手动 hold"（用户需在调用前告知）
