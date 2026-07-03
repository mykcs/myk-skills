# Layer A.3: CI 检查修复协议 (v2.6.32, 2026-06-27)

> **范围**: rich-audit skill 范围内的 2 个 GitHub 仓 (`mykcs/.claude` + `mykcs/myk-skills`) 出现 CI workflow failure 时, **自动诊断 + 修复 + 跑通 + 报告**.
> **触发**: Layer 2b §C.1 cmd 5 兜底 (gh run list) 检出 failure run → 走本 Layer.
> **完整 SOP**: §D.1 5 步 false-positive 诊断 + §D.2 ci-workflow-grep-drift 修复 + §D.3 submodule-broken 修复 + §D.4 实战命令模板 + §D.5 反模式 + §D.6 流程图

## 为什么需要本 Layer (背景)

v2.6.31 加 Layer 2b (§A.2) PR + CI 健康扫描后, cmd 5 兜底会暴露历史 + 当前 CI failure. **问题**: 之前 v2.6.30 时代, 任何 rich-audit 改 SKILL.md 都会触发 main 上 rich-audit-ci workflow fail, 因为:

1. **ci-workflow-grep-drift** — workflow 期望字面字符串 (e.g. "Tri-Search Protocol v2.6") 在 SKILL.md, 但版本演进后该字符串被改名为新版本特征 (e.g. "§A.2 Layer 2b"). workflow 不更新, SKILL.md 改了 → CI fail.
2. **submodule-broken** — `.worktrees/...` 这种 worktree 路径被错误地当 submodule commit (160000 mode), 缺 .gitmodules URL 配置. actions/checkout 跑 `git submodule foreach` 找不到 URL → fatal exit 128 → 后续 step 全部 skip.

**这两个根因导致 2026-06-27 mykcs/myk-skills 10 次连续 push fail** 但 PR check-runs API 全 clean — user 收 10 封 "Run failed" 邮件才发现.

本 Layer = **把"CI fail → 找到根因 → 修复 → push → CI success"流程固化**, 避免再人工查 log.

---

## §D.1 5 步 false-positive 诊断协议 (CI 必跑)

按 process.md §C.6 5 步诊断, 但**对 CI 场景定制**:

| Step | 假设 | 验证方法 | 结论 |
|------|------|----------|------|
| 0 | base state 已坏? | `git -C <main_worktree> status --short` 空 + last CI run 在 < 1h 内跑过 | base 干净 → 继续诊断 |
| 1 | workflow 文件本身有问题? | `gh api repos/<owner>/<repo>/contents/.github/workflows/<name>.yml` 看 grep 字符串 | drift → 走 §D.2 |
| 2 | 仓结构 (submodule/symlink) 阻塞? | `git -C <repo> ls-files --stage \| grep 160000` 看 submodule 引用 | broken → 走 §D.3 |
| 3 | 是 test 失败 (而不是 setup 失败)? | 看 CI log "##[error]Process completed with exit code 1" 前后 step 名 | setup 失败 → 走 §D.2/§D.3; test 失败 → 走 SOP §C.2 (CI FAILURE 修复) |
| 4 | 多个修改叠加是元凶? | 改完 1 个修 → push → 看 run 1 → 若仍 fail → revert + 改下个 | 多改叠加 → 拆 commit |
| 5 | CI workflow 本身需要更新? | 看 workflow git log (e.g. `.github/workflows/rich-audit-ci.yml` 最后修改时间) | 跟 SKILL.md 演进 drift → workflow 也要更新 |

**反模式**:
- ❌ 看 CI 报红就改 SKILL.md 加 grep 字符串 (无效字符串不解决问题)
- ❌ Skip Step 0, 直接 revert commit → 浪费 5 步
- ❌ 没看 log 就猜是 setup 失败还是 test 失败 → 走错修复路径

---

## §D.2 ci-workflow-grep-drift 修复 (SOP + 实战)

### 现象

CI log 显示:
```
##[group]Run if ! grep -q "<old_string>" <file>; then
##[group]Run if ! grep -q "<old_string>" <file>; then
❌ <old_string> not in <file>
##[error]Process completed with exit code 1.
```

### 根因

`.github/workflows/<name>.yml` 的某 step 用 `grep -q "<字符串>"` 验证 SKILL.md/CHANGELOG.md 含特定字面字符串. **该字符串跟实际 skill 演进 drift 了** (典型 v2.6.20 时代 → v2.6.31 时代, 字符串从 "Tri-Search Protocol v2.6" 改成 "§A.2 Layer 2b").

### 修法 (3 选 1, 按风险)

| 选项 | 改动 | 风险 | 适用 |
|------|------|------|------|
| A. workflow grep 字符串改成新特征 | 改 workflow 文件 | low (CI check 同步) | 字符串改过名字但实际内容已存在 (推荐) |
| B. 删 grep 检查 | 删整个 step | medium (失去检查) | grep 已无意义 (如旧 layer 弃用) |
| C. SKILL.md 加旧字符串当 placeholder | 改 SKILL.md | high (污染文档) | **反模式, 不推荐** |

### 实战命令模板 (Option A)

```bash
# 1. 看远端 workflow 哪个 grep 字符串 fail
gh run view <run_id> --repo <owner>/<repo> --log-failed 2>&1 | grep "❌.*not in"

# 2. fetch + 建 worktree
cd <repo>
git fetch origin main
WORKTREE_DIR="$HOME/.claude/.worktrees/$(date +%Y-%m-%d)-ci-grep-drift"
git worktree add "$WORKTREE_DIR" -b "fix/ci-grep-drift-$(date +%Y-%m-%d)" origin/main

# 3. 改 workflow grep 字符串 (用 Python 替换, 安全)
cd "$WORKTREE_DIR"
python3 -c "
old = 'grep -q \"<old_string>\"'
new = 'grep -q \"<new_string>\"'
with open('.github/workflows/<name>.yml') as f: c = f.read()
c = c.replace(old, new)
with open('.github/workflows/<name>.yml', 'w') as f: f.write(c)
"

# 4. commit + push + 开 PR
git add .github/workflows/<name>.yml
git -c user.name='myk' -c user.email='...' commit -m "fix(ci): update workflow grep to current skill feature name"
git push -u origin fix/ci-grep-drift-...
gh pr create --repo <owner>/<repo> --title "fix(ci): grep drift repair" --body "..."

# 5. 等 CI 重跑 (~30s) + verify
sleep 30
gh api "repos/<owner>/<repo>/commits/<sha>/check-runs" --jq '[.check_runs[] | select(.app.name != "Cursor" and .app.name != "Cursor Application") | {name, conclusion}]'
```

### 真实案例 (mykcs/myk-skills, 2026-06-27)

- 旧 grep: `"Tri-Search Protocol v2.6"`
- 新 grep: `"§A.2 Layer 2b"` (v2.6.31 实际功能名)
- 修复 commit: `0397bfe` → merge commit `ad2f380` → main tip 立即生效

---

## §D.3 submodule-broken 修复 (SOP + 实战)

### 现象

CI log 显示:
```
fatal: No url found for submodule path '<path>' in .gitmodules
##[warning]The process '/usr/bin/git' failed with exit code 128
```

**所有后续 step 被 skip**, 即使其他 step 没问题.

### 根因

某个目录被错误地 commit 成 `160000` mode (submodule 引用), 指向某 commit hash, 但**`.gitmodules` 文件没有这个 submodule 的 URL 配置**. actions/checkout 跑 `git submodule foreach` 时 fatal.

**典型来源**: 误把 `git worktree add` 出来的路径 commit 进去 (worktree 路径在父仓里看起来像 submodule, 但没 .gitmodules 配置).

### 修法

```bash
# 1. 验证 submodule 确实 broken
cd <repo>
git ls-files --stage | grep 160000   # 列出所有 submodule 引用

# 2. fetch + 建 worktree
git fetch origin main
WORKTREE_DIR="$HOME/.claude/.worktrees/$(date +%Y-%m-%d)-remove-broken-submodule"
git worktree add "$WORKTREE_DIR" -b "fix/remove-broken-submodule-$(date +%Y-%m-%d)" origin/main

# 3. 从 index 删 submodule 引用 (git rm --cached 不删 worktree 物理目录)
cd "$WORKTREE_DIR"
git rm --cached <broken-submodule-path>   # 例: .worktrees/2026-06-27-xxx

# 4. 如果有遗留空目录, 用 rmdir 删 (git 不追踪空目录, 不影响)
[ -d <broken-submodule-path> ] && rmdir <broken-submodule-path> 2>/dev/null || true

# 5. 验证 cleanup
git ls-files --stage | grep 160000   # 期望空

# 6. commit + push + 开 PR
git add -A
git -c user.name='myk' -c user.email='...' commit -m "fix(ci): remove broken submodule reference (was blocking actions/checkout)"
git push -u origin fix/remove-broken-submodule-...
gh pr create --repo <owner>/<repo> --title "fix(ci): remove broken submodule" --body "..."

# 7. 等 CI 重跑 + verify
```

### 真实案例 (mykcs/myk-skills, 2026-06-27)

- 坏 submodule: `.worktrees/2026-06-27-readme-public-notice`
- 修复: `git rm --cached` 删 160000 引用
- 跟 §D.2 grep drift 修复**合并到同一个 PR #4** (commit `0397bfe`)

---

## §D.4 实战完整命令模板 (CI fail → 修复闭环)

```bash
# Phase 1: 检出 (用 Layer 2b cmd 5 兜底)
gh run list --repo <owner>/<repo> --limit 5 --json databaseId,conclusion,name,event,headBranch,createdAt | jq '[.[] | select(.conclusion == "failure")]'
FAIL_RUN_ID=$(<上面输出的 databaseId 第一个>)

# Phase 2: 5 步 false-positive 诊断
gh run view $FAIL_RUN_ID --repo <owner>/<repo> --log-failed | grep -A 2 "##\[error\]"
# → 找到 step 名 (e.g. "Verify Tri-Search Protocol v2.6 in SKILL.md")
# → 找到 error 模式 (e.g. "fatal: No url found" / "❌ not in" / "test failed")

# Phase 3: 分类 (走哪条修复路径)
if grep -q "❌.*not in" <(gh run view $FAIL_RUN_ID --log-failed); then
  echo "→ §D.2 ci-workflow-grep-drift"
elif grep -q "fatal: No url found for submodule" <(gh run view $FAIL_RUN_ID --log-failed); then
  echo "→ §D.3 submodule-broken"
elif grep -q "##\[error\]Process completed with exit code 1" <(gh run view $FAIL_RUN_ID --log-failed) && ! grep -q "fatal\|❌" <(gh run view $FAIL_RUN_ID --log-failed); then
  echo "→ SOP §C.2 (CI FAILURE 修复, 不是 workflow 本身问题, 是 test 失败)"
fi

# Phase 4: 修复 (按 Phase 3 分类走 §D.2 或 §D.3)

# Phase 5: 闭环 verify (PR merge 后, cmd 5 兜底 必返 [])
gh run list --repo <owner>/<repo> --limit 5 --json conclusion | jq '[.[] | select(.conclusion == "failure")] | length'
# 期望: 0 (新 push 都 success)
```

---

## §D.5 反模式 (claudecode 必避)

- ❌ **CI fail 立刻看 PR check-runs** = 跟 Layer 2b cmd 2 一样盲点, PR check-runs 不覆盖 push-triggered workflow. **必跑 cmd 5 = `gh run list`**.
- ❌ **CI fail 不看 log 直接猜** = 猜"是 test 失败"或"setup 失败"走错修复路径, 浪费时间
- ❌ **改 SKILL.md 加 grep 字符串当 placeholder** = 污染文档, 失去 CI check 意义 (Option C 反模式)
- ❌ **只改 workflow 不 merge PR** = 修复永远不生效 (2026-06-27 myk-skills 真实案例: PR #4 没 merge 之前, 修 grep 失败邮件继续来)
- ❌ **`git rm --cached` 后不 rmdir** = 空目录残留可能再次被 commit (虽然 git 不追踪, 但 .worktrees/ 这种路径被其他 process 看到会混乱)
- ❌ **改 .gitmodules 而不是删 submodule** = 创造新配置项, 错上加错. 应该是**直接删 submodule 引用**, 不补 URL

---

## §D.6 完整流程图

```
rich-audit 触发
    ↓
Layer 0: git/gh state pre-check (5 commands)
    ↓
Layer 1-3 (审计 + 修复 + 进化)
    ↓
Layer A.2 (§A.2) — PR + CI 健康扫描
    ├─ cmd 5 兜底: gh run list --limit 5
    ├─ 若检出 failure → 触发 Layer A.3 (本文件)
    ↓
Layer A.3 (本文件) — CI 检查修复
    ├─ 5 步 false-positive 诊断 (§D.1)
    ├─ 分类:
    │   ├─ ci-workflow-grep-drift → §D.2 修 workflow 文件
    │   ├─ submodule-broken       → §D.3 删 submodule 引用
    │   └─ test failed            → 走 SOP §C.2 (Layer 2b 既有)
    ├─ 修复 (worktree + commit + PR + 等 CI)
    ├─ Auto-merge ready PR (§11.1)
    └─ cmd 5 兜底再 verify: failures = []
    ↓
完成
```

---

## Cross-References

- Layer A.2 (上游, 触发本 Layer): [`layer-a2-pr-ci-health-scan.md`](layer-a2-pr-ci-health-scan.md) §C.1 cmd 5
- 5 commands verification SOP: §C.1 (mergeable + state + check-runs + worktree + `gh run list`)
- Auto-merge PR 协议 → `~/.claude/CLAUDE.local.md` §11.1
- 5 步 false-positive 诊断 → `~/.claude/rules/process.md` §C.6
- Real case 2026-06-27: mykcs/myk-skills `rich-audit-ci.yml` 10 次 push fail → PR #4 (`0397bfe` → merge `ad2f380`)
- Real case 2026-06-21: CASE-CONTENT2HTML-AUDIT-VERIFICATION-GATE-FAIL (verify gate 形式违反, 实质修复正确)
