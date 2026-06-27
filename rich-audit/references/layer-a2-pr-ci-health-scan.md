# Layer A.2: 多仓 PR + CI 健康扫描 (v2.6.31, 2026-06-27)

> **范围**: 跨 mykcs + wangrui2025 双账号, 扫所有 `gh pr list --author @me --state open` 的 PR, 跑 4 commands verify + 修复 CI FAILURE / diverged + auto-merge ready PR.
> **触发**: rich-audit 触发时（v2.6.30 5 升级固化的 'bug 立即修' 协议自动包含本 Layer）
> **完整 SOP**: 4 commands verification + §C.2 CI 修复 + §C.3 diverged 修复 + §C.4 auto-merge + §C.5 报告 schema + §C.6 反模式

## 为什么需要本 Layer (背景)

rich-audit v2.6.19 引入 Layer 0 verification gate (commit 前 5 commands pre-check), 解决"口头报 ✅ 已 push 无 ground truth"反模式.

但 Layer 0 只覆盖 **commit 前** 的本地状态. **跨仓 PR 创建后** 需要新 Layer:

1. **PR 健康度 verify** — 跨仓 PR 的 mergeable / state / CI status 是不是干净的 (academic validate / myk-skills diverged 是案例)
2. **CI FAILURE 修复** — 学术仓 validate-manifest 失败时 regen manifest 修
3. **diverged PR 修复** — origin/main 推进后 PR head outdated 时 merge main
4. **ready PR auto-merge** — mergeable=true + state=clean + GH Actions success 的 PR 按 §11.1 协议自动 merge

本 Layer = **PR 创建后到 merge 前的健康扫描 + 修复 + 自动 merge**.

---

## §C.1 4 commands verification (per PR, post-creation)

每个 PR 创建后**必须**跑这 4 个 verify, 全部 PASS 才算 PR 就绪:

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

**判定矩阵**:

| mergeable | mergeable_state | GH Actions | 判定 |
|-----------|----------------|------------|------|
| true | clean | success (or empty) | ✅ **READY** — 可 auto-merge (§C.4) |
| true | clean | (无 GA 配置) | ✅ **READY** — 仓无 CI, PR clean 即 OK |
| null | unknown | (任意) | ⚠️ **DIVERGED** — 走 §C.3 修复 SOP |
| true | unstable / blocked / dirty | failure | 🚨 **CI FAILURE** — 走 §C.2 修复 SOP |
| false | blocked | (任意) | 🚨 **MERGE CONFLICT** — 走 §C.3 rebase/merge |

---

## §C.2 CI FAILURE 修复 SOP (academic validate-manifest 案例)

### 现象

```
[validate via GitHub Actions] conclusion=failure
```

GH Actions run 日志报错:
```
Manifest out of sync with working tree. Diff (manifest vs fresh):
Run 'python3 scripts/generate-manifest.py' to refresh.
##[error]Process completed with exit code 1.
```

### 根因 (5 步 false-positive §C.6 诊断)

学术资源仓 (`mykcs/academic` 等) 的 `validate-manifest.yml` 工作流跑 `python3 scripts/generate-manifest.py --check`, 比较 **manifest.json 跟踪的 asset size** 跟 **实际工作树文件 size**.

当 PR 改了 README.md 等被 manifest 跟踪的文件 → size 变化 → manifest 过期 → CI FAILURE.

**这是 design 行为** (academic 仓 design: README 作为学术资源引用, 必须在 manifest 里), 不是 CI bug.

### 5 步诊断 (避免误判)

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

## §C.3 Diverged PR 修复 SOP (myk-skills PR #3 案例)

### 现象

```
mergeable: null
mergeable_state: unknown
```

GH API 对比:
```
gh api repos/<owner>/<repo>/compare/main...<branch>
→ status=diverged, ahead_by=1, behind_by=2
```

### 根因

PR 创建后, `origin/main` 被其他 session / background agent 推进 (rich-audit / memory-bench / 跨仓修复), PR head 变 outdated. GitHub 自动算不出能否 merge → mergeable=null.

### 修复命令模板 (用 merge 不用 rebase, 保留 PR commit 历史清晰)

```bash
cd <worktree_dir>
# 1. fetch 新 main
git fetch origin main
# 2. 预测冲突 (看 main 改了哪些文件)
git diff --name-only origin/main HEAD
# 3. merge main 进 feat 分支
git merge --no-ff origin/main -m "merge: sync with main (N commits ahead) before final CI verify

Trigger: 多仓 PR CI 健康扫描发现 <repo> PR mergeable=null
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

## §C.4 READY PR auto-merge SOP (CLAUDE.local.md §11.1 协议)

### 触发条件

只有当 PR 满足**所有 4 个 READY 条件**时才 auto-merge:

1. `mergeable == true`
2. `mergeable_state == clean`
3. GitHub Actions **全部 success** (或仓无 GA 配置)
4. PR 不涉及 soul v2 双向保险例外:
   - ❌ 双账号污染 (wangrui2025/* → mykcs)
   - ❌ 安全 / 凭据 / settings.json 字段
   - ❌ 用户偏好 / 命名 / 风格
   - ❌ 不可逆 main 影响 (push --force / reset --hard)

### 命令模板 (5 步)

```bash
# 1. merge (squash + delete-branch 自动)
gh pr merge <PR_NUMBER> --repo <owner>/<repo> --squash --delete-branch

# 2. fetch origin main + fast-forward 本地
git -C "$HOME/.claude" fetch origin main
git -C "$HOME/.claude" merge --ff-only origin/main

# 3. 清理 worktree
git -C "$HOME/.claude" worktree remove --force "$HOME/.claude/.worktrees/<YYYY-MM-DD>-<topic>"

# 4. 5 commands verification
git -C "$HOME/.claude" log -1 --format="%h | %s"
git -C "$HOME/.claude" log --oneline -5 | head -5
git -C "$HOME/.claude" status --short
git -C "$HOME/.claude" remote -v | head -2

# 5. decision-stream 追加 (calm-flow §4 schema)
```

### 真实案例

本次 README 公开提示批量 PR (4 PR) 在 CI 全 clean 后即可走本 SOP:
- mykcs/myk-skills #3
- mykcs/academic #1
- mykcs/content2html #1
- mykcs/5-Day_Generative_AI_Intensive #1

---

## §C.5 报告 schema (rich-audit 集成格式)

### 精简模式 (默认, ≤ 30 行)

```
总分: <X> ready / <Y> diverged / <Z> ci-failure / <W> auto-merged
## 状态
- ✅ 4 PR ready (myk-skills #3 / academic #1 / content2html #1 / 5-Day #1)
- ✅ 1 PR auto-merged (academic #1)
## 注意
- <N> PR diverged: <repo> <#num> (已 merge main 修复)
- <M> PR ci-failure: <repo> <#num> (已 regen manifest 修复)
```

### 详细模式 (verbose 触发)

```
完整 4 仓 × 4 维表 (PR / mergeable / state / GA checks / 修复记录 / auto-merge status)
```

---

## §C.6 反模式 (claudecode 必避)

- ❌ **跳过本 Layer** = 重演 2026-06-27 README 公开提示批量 PR 的 2 个事故 — (a) academic validate FAILURE 没跑 4 commands 就说 ✅, (b) myk-skills PR mergeable=null 没 merge origin/main 就说 clean
- ❌ **CI FAILURE 立刻 revert PR** = 表面修复, 不解决根因 (asset size 还会再漂)
- ❌ **Diverged 用 `git rebase -i`** = 丢失 PR commit 历史, 跟 merge commit 混乱
- ❌ **不读 CI 日志就猜根因** = 5 步 false-positive 协议 §C.6 必须按顺序跑
- ❌ **不排除 Cursor app 就说 CI status** = Cursor IDE bot 的 check 跟真 GH Actions 混在一起, 误导
- ❌ **auto-merge 不走 §11.1 例外检查** = 可能误 merge 安全 / settings.json / 凭据类 PR

---

## §C.7 完整流程图

```
rich-audit 触发
    ↓
Layer 0: git/gh state pre-check (5 commands)
    ↓
Layer 1-3 (审计 + 修复 + 进化)
    ↓
Layer A.2 (本文件) — 多仓 PR + CI 健康扫描
    ├─ 扫 gh pr list --author @me --state open
    ├─ 对每个 PR 跑 §C.1 4 commands
    ├─ 分类: READY / DIVERGED / CI-FAILURE / MERGE-CONFLICT
    ├─ 修复 (§C.2 / §C.3) 或 auto-merge (§C.4)
    └─ 输出报告 (§C.5)
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
- 5 步 false-positive 诊断 → `~/.claude/rules/process.md` §C.6
- 双账号隔离铁律 → `~/.claude/CLAUDE.local.md` HOT FACTS §2 + §7
- 真实案例: README 公开提示批量 PR (4 PR, 2026-06-27) → `~/.claude/decision-stream/2026-06-27-readme-batch-pr/`
