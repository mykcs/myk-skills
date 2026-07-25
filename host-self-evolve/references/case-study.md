## 🔁 实战案例沉淀段 (per ADR-0056 + CASE-N-TOOL-DRIFT-CLEANUP-20260713, 2026-07-13 立)

> **目的**: host-self-evolve 跑过 1 次后, 必沉淀 "检查→修复→沉淀→复用" 全流程实战, 后续 run 直接复用, 不重跑.

### 案例 1: N-tool 协议位 drift 全面清理 (per ADR-0056, 2026-07-13)

**触发**: user 问 "把我这个主机所有的 claude 记忆、规则、灵魂所有的搜索工具协议都列出来. 然后去看他们是否都执行同一组的协议". claudecode 跑 4 维 audit (主仓 + 子仓 + 4 active 仓 + mem0), 发现 **6 P0 字面散落 + 20 P1 旧名残留 + 110+ P2 历史档案** = 协议位字面定义跟 SSOT 不一致 (漏 mmx 第 6 工具).

**5 件事 (一句话 + 现状 + 干什么 + 验收)**:

| #   | 一句话                                                             | 现状                               | 干什么                                                                                                                                                                                 | 验收                                                      |
| --- | ------------------------------------------------------------------ | ---------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------- |
| 1   | **6 件套 grep 现状** (cross-session-grep §1)                       | 立 ADR 前必跑                      | 扫 `~/.claude/` + `~/.agents/skills/` 4 维, 命中已有沉淀 (ADR-0054/0055/CASE-SEARCH/CASE-META)                                                                                         | ✅ 6 件命中, 走引用路径                                   |
| 2   | **AskUserQuestion 拍板路线**                                       | 路线分叉 + ≥3 候选 + user 显式拍板 | 给 4 选项 (A 全清 / B 只 P0 / C 只删旧副 SSOT / D 保持现状), user 选 **A + 整数 slot 0056 + worktree feat/n-tool-drift-cleanup**                                                       | ✅ A + 0056 + worktree 名 3 件                            |
| 3   | **§C.3.1 worktree 立**                                             | 不可逆 + multi-file                | `git worktree add .claude/worktrees/n-tool-drift -b feat/n-tool-drift-cleanup` 基于 main HEAD b090e9db                                                                                 | ✅ worktree 立, working dir 干净                          |
| 4   | **改 N file (worktree 绝对路径)**                                  | worktree 模式                      | 主仓 4 file (process.md §C.3.5/§C.3.6/§F + 3 references) + 子仓 2 file (loop-engineering + 子仓副 SSOT redirect) + 3 沉淀 (ADR-0056 + CASE + decision-stream) = 9 file 改              | ✅ 6 改 + 3 立 = 9 file                                   |
| 5   | **commit + push + PR + ff verify + worktree cleanup + 5 字段自检** | 闭环前必跑                         | 主仓 commit 0985d1d5 + b9aaa973 → PR #53 squash merged → ahead/behind 0/0 (rebase origin/main 修复 silent fail) → worktree removed; 子仓 commit 6e5f350 → push main → ahead/behind 0/0 | ✅ 2 PR merged + 2 仓 ahead/behind 0/0 + worktree cleanup |

**整体验收 (5 项)**:

| #   | 字段   | 验收标准                               | 实际                                            |
| --- | ------ | -------------------------------------- | ----------------------------------------------- |
| 1   | path   | 主仓 ~/.claude + 子仓 ~/.agents/skills | ✅ 2 仓                                         |
| 2   | commit | git log -1 有新 commit                 | ✅ 主仓 9897e9ea (PR #53 squash) + 子仓 6e5f350 |
| 3   | push   | ahead/behind 0/0                       | ✅ 双仓 0/0                                     |
| 4   | CI     | gh api .../commits/HEAD/status green   | ✅ pending (新 commit, GitHub Actions 待跑)     |
| 5   | owner  | mykcs/.claude + mykcs/myk-skills       | ✅ 双账号隔离正确                               |

**踩坑 (必沉淀)**: **gh pr merge stdout 空 ≠ 成功** (per ADR-0026 必读 body 协议位). 修法: 必跑 `gh pr view --json state` 实测 + post-pr-merge-ff-verify.sh hook 兜底. 本 case silent fail 后 hook 检测到 ahead/behind 1/1 diverged, §C.6 5 步诊断发现 ahead 是 user prep hook 自动 commit (auto-feishu-digest case, 跟 N-tool drift 无关), `git rebase origin/main` 修复.

**未来复用 (下次跑前必跑)**:

- 任何协议位散落 audit → 走本案例骨架 (6 件套 grep → AskUserQuestion → worktree → 改 N file → commit+push+PR+ff+cleanup+5 字段)
- 必跑 `post-pr-merge-ff-verify.sh` hook (per `~/.claude/rules/post-pr-merge-ff-verify-rule.md`) 防 gh PR 谎报
- 必跑 `gh pr view --json state` 实测 (per ADR-0026) 不要信 stdout 空
- §C.6 5 步 false-positive 诊断 protocol: ahead/bebehind diverged 必先看 ahead 是谁 (prep hook 自动 commit vs N-tool drift 相关)

**联动**: §20 8 步管道 (per ADR-0055) + §C.3.1 worktree + §C.3.2 PR auto-merge + post-pr-merge-ff-verify hook + §H 5 字段自检 + ADR-0056 + CASE-N-TOOL-DRIFT-CLEANUP-20260713
