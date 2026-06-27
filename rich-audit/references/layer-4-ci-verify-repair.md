# Layer 4: CI Verify + Repair 验证门 SOP (v2.6.31, 2026-06-27)

> **范围**: GitHub Actions CI + 跨仓 PR 工作树状态 + 修复 SOP（regen manifest / diverged merge / worktree cleanup）
> **触发**: rich-audit 触发的所有 sub-task PR（含 README 公开提示批量 PR / memory-bench 报告 PR / 跨仓修复 PR）
> **位置**: Layer 0 → Layer 1 → Layer 2 → Layer 3 → **Layer 4 (本文件)** → 完成
> **完整 4 commands + 修复 SOP + 反模式**

## 为什么需要 Layer 4 (背景)

rich-audit v2.6.19 引入 Layer 0 verification gate（commit 前 5 commands pre-check），解决了"口头报 ✅ 已 push 无 ground truth"反模式（CASE-CONTENT2HTML-AUDIT-VERIFICATION-GATE-FAIL-20260621）。

但 Layer 0 只覆盖 **commit 前** 的本地状态。**PR 创建后** 还需要：

1. **CI 状态 verify** — 跨仓 PR 的 GitHub Actions 是否真跑了 + 通过（academic validate-manifest 是案例）
2. **PR diverged 修复** — 当 origin/main 推进后，PR head 变 outdated → `mergeable=null`（myk-skills PR #3 是案例）
3. **asset size drift 修复** — README 改了 size → manifest 跟踪的 size 过期 → CI FAILURE（academic README size 1794→2018 是案例）

Layer 4 = **PR 创建后到 merge 前的验证门**，覆盖 Layer 0 覆盖不到的范围。

---

## §B.1 4 commands verification (per PR, post-creation)

每个 PR 创建后**必须**跑这 4 个 verify，全部 PASS 才算 PR 就绪：

```bash
# 1. PR state
gh api repos/<owner>/<repo>/pulls/<num> --jq '{state, draft, mergeable, mergeable_state}'

# 2. GitHub Actions checks (排除 Cursor IDE bot 干扰)
gh api repos/<owner>/<repo>/commits/<sha>/check-runs | jq '[.check_runs[] | select(.app.name != "Cursor" and .app.name != "Cursor Application") | {name, conclusion: (.conclusion // .status), app: .app.name}]'

# 3. Local worktree clean
git -C <worktree_dir> status --short   # 期望空

# 4. Commit exists locally
git -C <worktree_dir> log -1 --format="%h %s"   # 期望非空 + sha 跟 PR head 一致
```

**判定**：

| mergeable | mergeable_state | GH Actions | 判定 |
|-----------|----------------|------------|------|
| true | clean | success (or empty) | ✅ **PASS** — 可 merge |
| true | clean | (无 GA 配置) | ✅ **PASS** — 仓无 CI, PR clean 即 OK |
| null | unknown | (任意) | ⚠️ **DIVERGED** — 走 §B.3 修复 SOP |
| true | unstable / blocked / dirty | failure | 🚨 **CI FAILURE** — 走 §B.2 修复 SOP |
| false | blocked | (任意) | 🚨 **MERGE CONFLICT** — 走 §B.3 rebase/merge |

---

## §B.2 CI FAILURE 修复 SOP (academic validate-manifest 案例)

### 现象

```
[validate via GitHub Actions] conclusion=failure
```

GH Actions run 日志报错：
```
Manifest out of sync with working tree. Diff (manifest vs fresh):
Run 'python3 scripts/generate-manifest.py' to refresh.
##[error]Process completed with exit code 1.
```

### 根因（5 步 false-positive §C.6 诊断）

学术资源仓（`mykcs/academic` 等）的 `validate-manifest.yml` 工作流跑 `python3 scripts/generate-manifest.py --check`，比较 **manifest.json 跟踪的 asset size** 跟 **实际工作树文件 size**。

当 PR 改了 README.md 等被 manifest 跟踪的文件 → size 变化 → manifest 过期 → CI FAILURE。

**这是 design 行为**（academic 仓 design: README 作为学术资源引用，必须在 manifest 里），不是 CI bug。

### 5 步诊断（避免误判）

| Step | 假设 | 验证 | 结论 |
|------|------|------|------|
| 0 | base state 已坏 | `cd <main_worktree>; python3 scripts/generate-manifest.py --check` | exit 0 → base OK |
| 1 | 我的 PR 改坏了 | `git diff main...HEAD --stat` | 仅 README.md +N 行 → PR 没动 manifest |
| 2 | manifest 跟文件 size | 对比 manifest README.md size vs 实际 README.md size | size 不同 → 根因 |
| 3 | regen manifest | `python3 scripts/generate-manifest.py` 不带 `--check` | 写入新 manifest |
| 4 | verify fix | `python3 scripts/generate-manifest.py --check` | exit 0 → 修复 |

### 修复命令模板

```bash
cd <worktree_dir>
# 1. regen manifest
python3 scripts/generate-manifest.py
# 2. 验证 --check 通过
python3 scripts/generate-manifest.py --check; echo "exit: $?"   # 期望 0
# 3. commit fix
git add meta/manifest.json
git commit -m "fix(manifest): regenerate to include <file> size after <trigger>"
# 4. push
git push origin <branch>
# 5. 等 CI 重跑 (~30s) + verify
sleep 30
gh api repos/<owner>/<repo>/commits/<sha>/check-runs --jq '[.check_runs[] | .conclusion]' | grep -q "success" && echo "✅ FIXED" || echo "❌ STILL FAIL"
```

### 真实案例

**academic #1**: `c67f247` (README +224 bytes) → validate FAILURE → regen → `364ebd3` → validate SUCCESS ✅

---

## §B.3 Diverged PR 修复 SOP (myk-skills PR #3 案例)

### 现象

```
mergeable: null
mergeable_state: unknown
```

GH API 对比：
```
gh api repos/<owner>/<repo>/compare/main...<branch>
→ status=diverged, ahead_by=1, behind_by=2
```

### 根因

PR 创建后，`origin/main` 被其他 session / background agent 推进（rich-audit / memory-bench / 跨仓修复），PR head 变 outdated。GitHub 自动算不出能否 merge → mergeable=null。

### 修复命令模板（用 merge 不用 rebase，保留 PR commit 历史清晰）

```bash
cd <worktree_dir>
# 1. fetch 新 main
git fetch origin main
# 2. 预测冲突（看 main 改了哪些文件）
git diff --name-only origin/main HEAD
# 3. merge main 进 feat 分支
git merge --no-ff origin/main -m "merge: sync with main (N commits ahead) before final CI verify

Trigger: 4 PR CI re-verify 发现 <repo> PR mergeable=null
Root cause: remote main 推进了 N commits
PR branch 变成 diverged (X ahead, Y behind).

This merge brings PR up-to-date with main so mergeable_state=clean."
# 4. push 更新后的 PR head
git push origin <branch>
# 5. 等 GH API 缓存刷新 (~5s) + verify
sleep 5
gh api repos/<owner>/<repo>/pulls/<num> --jq '{sha: .head.sha, mergeable, mergeable_state}'
# 期望: mergeable=true, mergeable_state=clean, sha 跟本地 HEAD 一致
```

### 真实案例

**myk-skills #3**: `c67f247` (single commit) → diverged (1 ahead, 2 behind) → merge origin/main → `05171dd` → mergeable=true, clean ✅

---

## §B.4 Worktree cleanup (post-merge)

PR merge 后（按 CLAUDE.local.md §11.1 自动 merge 协议）：

```bash
# 1. fetch + fast-forward 本地 main
git -C <repo_dir> fetch origin main
git -C <repo_dir> merge --ff-only origin/main

# 2. 清理 worktree
git -C <repo_dir> worktree remove --force <worktree_dir>

# 3. 删除远端 feat branch (gh pr merge --delete-branch 已删, 但保险跑一次)
git -C <repo_dir> branch -d <branch>   # 本地分支清理
git push origin --delete <branch>      # 远端分支清理 (如未自动)

# 4. 5 commands verification (跟 Layer 0 同一组)
git -C <repo_dir> log -1 --format="%h | %s"
git -C <repo_dir> log --oneline -5 | head -5
git -C <repo_dir> status --short       # 期望空
git -C <repo_dir> remote -v | head -2
gh api repos/<owner>/<repo>/commits/HEAD/status
```

---

## §B.5 反模式 (claudecode 必避)

- ❌ **跳过 Layer 4 验证** = CASE-CONTENT2HTML-AUDIT-VERIFICATION-GATE-FAIL-20260621 重现（口头报 ✅ 无 ground truth）
- ❌ **CI FAILURE 立刻 revert PR** = 表面修复, 不解决根因（asset size 还会再漂）
- ❌ **Diverged 用 `git rebase -i`** = 丢失 PR commit 历史, 跟 merge commit 混乱
- ❌ **跑 manifest 检查不 regen** = 工作树跟 manifest 永远不同步
- ❌ **不读 CI 日志就猜根因** = 5 步 false-positive 协议 §C.6 必须按顺序跑
- ❌ **不排除 Cursor app 就说 CI status** = Cursor IDE bot 的 check 跟真 GH Actions 混在一起, 误导

---

## §B.6 触发场景 (Layer 4 必跑)

| 场景 | 触发频率 |
|------|---------|
| rich-audit 触发的 sub-task PR (README / manifest / skill refactor) | 每次 PR 创建 |
| myk-skills 仓的任意 PR | 每次 (rich-audit v2.6.28 memory-bench + §B.1) |
| 双账号 (mykcs + wangrui2025) 跨仓 PR | 每次 (CLAUDE.local.md §7 双账号隔离铁律) |
| 跨境 GH Actions runner 仓 (e.g. glados-checkin) | 每次 (CLAUDE.local.md §10.1 + 10.2) |

---

## §B.7 完整流程 (Layer 4 全套)

```
PR 创建后
    ↓
§B.1 4 commands verification
    ├─ ✅ PASS → PR 就绪, 等 merge
    ├─ ⚠️ DIVERGED → §B.3 修复 → 回到 §B.1
    └─ 🚨 CI FAILURE → §B.2 修复 → 回到 §B.1
    ↓
PR merge (§11.1 自动 merge 协议)
    ↓
§B.4 worktree cleanup
    ↓
5 commands final verification (跟 Layer 0 同)
    ↓
decision-stream 记录 (calm-flow §4 schema)
    ↓
完成
```

---

## Cross-References

- Layer 0 verification gate SOP → [`layer-0-verification-gate.md`](layer-0-verification-gate.md)
- 自动 merge PR 协议 → `~/.claude/CLAUDE.local.md` §11.1
- 5 commands verification 主源头 → `~/.claude/rules/process.md` §C 验证门
- Deja Vu Fix Protocol → `~/.claude/rules/process.md` §E
- Bonus Test Pattern → `~/.claude/rules/process.md` §D
- 学术 validate-manifest 失败案例 → `~/.claude/knowledge/cases/wiki/` (本次触发未单独建 case, 触发条件: 学术仓 PR 改了 README/asset)
- myk-skills diverged 案例 → 同上 (本次触发未单独建 case, 触发条件: 跨 PR 期间 origin/main 推进)