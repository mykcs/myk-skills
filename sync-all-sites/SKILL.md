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

Output JSON schema:
{
  "site": "<name>",
  "score": 0-100,
  "issues": [
    {"severity": "P0|P1|P2", "type": "seo|a11y|i18n|build|ci|security", "file": "path", "fix": "concrete action"}
  ],
  "deferred": []
}

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

## Deferred items
<list>

## Lessons
<bullet list>
EOF
```

## Output contract

```markdown
# sync-all-sites report

## Sites
- mykcs: score=98, fixes=3, ci=green ✅
- GDKVM: score=87, fixes=12, ci=green ✅
- OSA:   score=92, fixes=5, ci=red ❌ (see deferred)

## Total commits
N

## Deferred items (next run)
- [ ] OSA: <issue>

## Case file
~/.claude/knowledge/cases/CASE-SYNC-ALL-SITES-YYYYMMDD.md
```

## 硬规则

- ❌ 跳过 Phase 1 验仓 → 禁止进入 Phase 2
- ❌ Phase 3 编辑未被 issue 列表覆盖的文件 → scope creep
- ❌ 任何 CI red 时声明"完成" → verification gate 违反
- ❌ 不写 case 文件 → self-evolution 协议违反
- ✅ 任何 abort 条件触发时立即停，不重试

## 已知反模式

- **快速通道**：跳过 Phase 1 直接派 agent → 改错仓（已发生 4+ 次）
- **silent skip**：CI red 不报"未完成"
- **全量 auto-apply**：把 P2 也一起 fix → scope creep
- **不写 case**：跑完不沉淀 → 下次跑同样的问题

## 与其他 skill 的关系

- `website-improve` — Phase 2/3 的 audit 协议来自此 skill
- `confirm-edit` — Phase 1 的"验仓"在每个 site 复用
- `context-verify.sh` — Phase 1 验仓的底层工具
- `gh-api-push.sh` — Phase 3 push 走此脚本避免 timeout

## v1.0.0 已知限制

- 不处理 monorepo（每个 site 必须是独立 git 仓）
- 不处理"某站点需要不同的 base branch"（默认 main）
- 不处理"某站点有手动 hold"（用户需在调用前告知）
