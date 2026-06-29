# Layer A.4: CI 全绿验收标准 (v2.6.45, 2026-06-29)

> **触发**: user 2026-06-29 原话 "把《CI 全绿》这个标准加入 skill 里面". 跟 website-improve §L26 (v4.0.5) + process.md §H Acceptance Protocol + §C.3.7 4 站 CI gate 全部同步.
>
> **source-of-truth split**:
> - SKILL.md §A.4 (主入口, 5 字段自检表 + 判定矩阵 + 联动)
> - 本文件 (references/layer-a4-ci-green.md, 详细 SOP + 实战命令模板 + 反模式 + Round 案例)

---

## §A.4.1 为什么 CI 全绿是验收标准 (不是 nice-to-have)

**反例 (2026-06-27 myk-skills 惨案)**: claudecode 跑 push 10 次 fail, 但本地 `git status` 4 PR check-runs 全 clean → 误以为 "all green" → 实际 CI 在跑但因 fork PR 不能 trigger, 后续 PR merge 触发 → 4 个站炸. 这是 §C.1 verification gate 形式违反 + §C.5 "build-pass theater" 反模式.

**根因**: claudecode 凭印象 / 局部 cmd 验证 / 不跑全 5 字段自检 → 谎报 done.

**修复**: 本 Layer 把 "CI 全绿" 固化为 **5 字段硬规则**, 任何 rich-audit run (含重度审计) 末段必跑, 缺一不可. 跟 website-improve §L26 (5 字段自检表) + process.md §H (5 字段自检表) 跨 skill 一致.

---

## §A.4.2 5 字段自检表 (rich-audit 重度审计特化版)

> 注: 跟 website-improve §L26 同源, 但字段 1+2+4 因 rich-audit 范围 (主仓 + 子仓, 不是 4 网站) 简化.

| # | 字段 | 验收标准 | 验证命令 |
|---|------|---------|---------|
| 1 | **path** | 审计目标文件绝对路径已输出 | `ls -d ~/.claude/ ~/.agents/skills/` |
| 2 | **commit** | 双仓 (主仓 + 子仓) `git log -1` 都有新 commit (or 显式标 "no fix needed" + 上次 commit hash) | `git -C $HOME/.claude log -1 --format='%h %s' && git -C $HOME/.agents/skills log -1 --format='%h %s'` |
| 3 | **push** | 双仓 `git rev-list --count @{u}..HEAD` 都 = 0 | `git -C $HOME/.claude rev-list --count @{u}..HEAD && git -C $HOME/.agents/skills rev-list --count @{u}..HEAD` |
| 4 | **CI** | 子仓 HEAD CI conclusion=success (主仓无 GH Actions, 仅 git status verify) | `gh api repos/mykcs/myk-skills/commits/HEAD/status --jq .state` |
| 5 | **owner 隔离 + 验收证据** | owner 正确 (mykcs/.claude + mykcs/myk-skills, 不交叉到 wangrui2025) + 1+ 行可执行命令证据 (5 commands / 5-tool fan-out / push commit hash / smart-push output) | `git -C $HOME/.claude remote get-url origin` + 子任务证据 |

---

## §A.4.3 实战命令模板 (rich-audit 重度审计末段必跑)

```bash
echo "=== §A.4.2 5 字段自检表 ==="
# 字段 1: path
ls -d ~/.claude/ ~/.agents/skills/ && echo "✅ 字段 1: path"

# 字段 2: commit
echo "--- 主仓 HEAD ---"
git -C $HOME/.claude log -1 --format='%h | %s'
echo "--- 子仓 HEAD ---"
git -C $HOME/.agents/skills log -1 --format='%h | %s'

# 字段 3: push 双重验证 (v2.6.42 协议)
echo "--- 主仓 push status ---"
git -C $HOME/.claude rev-list --count @{u}..HEAD
git -C $HOME/.claude rev-list --count HEAD..@{u}
echo "--- 子仓 push status ---"
git -C $HOME/.agents/skills rev-list --count @{u}..HEAD
git -C $HOME/.agents/skills rev-list --count HEAD..@{u}

# 字段 4: CI
echo "--- 子仓 HEAD CI ---"
gh api repos/mykcs/myk-skills/commits/$(git -C $HOME/.agents/skills rev-parse HEAD)/status --jq '.state'

# 字段 5: owner 隔离 + 证据
echo "--- 双仓 remote ---"
git -C $HOME/.claude remote get-url origin
git -C $HOME/.agents/skills remote get-url origin
# expected: github.com/mykcs/.claude.git + github.com/mykcs/myk-skills (不交叉 wangrui2025)
```

**判定** (跟 §A.4 判定矩阵同步):
- ✅ 5/5 全过 = "CI 全绿 ✅"
- ❌ 1+ red = "BLOCKED on `<field>`: `<reason>`" → 走 §A.3 修复

---

## §A.4.4 反模式 (claudecode 必避)

| 反模式 | 违反字段 | 真实 case |
|--------|---------|---------|
| ❌ "git push 后说 done" | push (字段 3) | v2.6.40 教训: smart-push 跳 push 阶段, 本地 commit 仍 ahead, status -sb 显示 [领先 1]. 修复: 必跑 `git rev-list --count @{u}..HEAD = 0` 双重验证 |
| ❌ "4 站 CI success = CI 全绿" | CI (字段 4) | rich-audit 不跑 4 网站, 但 site-modernizer 类 run 触发 4 站. 重度审计 #1-#5 跑完必须 §A.4 5 字段自检 |
| ❌ "改完没跑 build/test" | 验收证据 (字段 5) | v2.6.40 教训: claudecode 凭印象 "should be OK", 无可执行命令证据. 修复: 1+ 行 build/test/curl/grep 输出 |
| ❌ "5 字段 OK 但 owner 错" | owner (字段 5) | 双账号污染 4+ 次历史教训, mykcs 仓推到 wangrui2025 或反之. 修复: `remote get-url origin` 必跑 |
| ❌ "5 字段 OK 但缺 Layer 0-3 证据" | 验收证据 (字段 5) | 跟 §H 5 字段硬规则协同: 缺 Layer 0-3 子任务证据 = 形式通过, 实质无效 |
| ❌ "用 emoji ✅ 替代 5 字段自检表" | 全部 | 跟 §H 反模式同源: emoji 不是证据 |

---

## §A.4.5 实战 Round 案例 (重度审计 #5 = 2026-06-29)

```
| 字段 | 验证 |
|---|---|
| path | ~/.claude/ (1b98dc83) + ~/.agents/skills/ (98d33fa) ✅ |
| commit | 主仓 1b98dc83 Round 15 + 子仓 98d33fa v2.6.43 amend ✅ |
| push | 主仓 0/0 + 子仓 0/0 ✅ (v2.6.42 push 谎报协议生效) |
| CI | 子仓 98d33fa conclusion=success ✅ (28360574985 failure → rerun success) |
| owner | mykcs/.claude + mykcs/myk-skills ✅ 0 污染 |
| 验收证据 | 5 commands × 5-tool fan-out × smart-push output × gh run list ✅ |
→ "✅ CI 全绿" (5/5 字段)
```

---

## §A.4.6 联动

- **§A.2 Layer 2b** PR + CI 健康扫描 (前置: 跑 cmd 5 检 CI status)
- **§A.3 Layer 3b** CI 检查修复协议 (修复路径: 1+ 字段 red 时触发)
- **§I.4 Layer 4** Skill Self-Evolution (后置: CI 全绿 ✅ 后触发 §I.4 self-evolution cycle)
- **website-improve §L26** (v4.0.5) — 跨 skill 一致性, 5 字段自检表同源
- **process.md §H** Acceptance Protocol — 主仓 process.md 同步源
- **process.md §C.3.7** 4 站 CI 全绿硬规则 — site-modernizer 类 run 触发
- **CLAUDE.local.md §15** 4 站 CI 全绿 hot recall — user 强制记忆锚点
- **CASE-MULTI-SITE-FULL-AUDIT-V4-20260627** Round 10-15 完整 6 轮 timeline — 反例 + 修复案例
- **references/external-highlights-2026-06-27.md** + **external-highlights-2026-06-29.md** — 5-tool fan-out 8+ 资源

---

## §A.4.7 历史

- **2026-06-29 v2.6.45**: 立 (user 显式触发). 跟 website-improve §L26 (v4.0.5 同步立) 跨 skill 一致性落地.
- **2026-06-27 v2.6.40**: 反模式沉淀 — claudecode 谎报 done (跨 4 字段). 修复: 5 commands verify 必跑.
- **2026-06-22**: 主仓 process.md §H Acceptance Protocol 立 (5 字段自检表骨架).
- **2026-06-27 myk-skills 惨案**: 10 次 push fail + 4 PR check-runs 全 clean 谎报 done. 修复: §A.4 5 字段自检表.