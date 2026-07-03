## §A.1 Layer 0: Verification Gate Pre-check (v2.6.19, 强制 · 不可跳过)

> **Why**: rich-audit 跑完口头报 "✅ 已 push" / "审计完成" 是典型 form violation (CASE-CONTENT2HTML-AUDIT-VERIFICATION-GATE-FAIL-20260621, 2026-06-21). Verification Gate 只能事后验证 ground truth, 不能事后编造. Layer 0 把 ground-truth 收集**前置**到 Pre-flight Declaration 之后, Layer 1 之前 — 任何 state drift 在 audit 启动前显式可见.
>
> **Trigger**: rich-audit 任何触发 (含 `rich审计` / `/rich-audit` / `进化` / `rich audit` / `自我升级` / `claude 审计` / `audit claude files`).
>
> **违反硬规则**: 跳过 Layer 0 直接进 Layer 1 = 等同把 verification gate 延后到 "✅ 已 push" 之后 = CASE-CONTENT2HTML-AUDIT-VERIFICATION-GATE-FAIL-20260621 重现.

### Layer 0 必跑 5 commands (per targeted repo)

**Pre-flight Declaration 输出目标文件夹后, 立即对每个 git repo 跑:**

```bash
# 1. Commit 真存在 (过去 1 周至少 1 commit)
git log --oneline -1

# 2. 5 commits 连续性 (sanity check: 是真仓, 不是空仓)
git log --oneline -5 | head -5

# 3. 0 uncommitted (避免 audit 期间被中断污染)
git status --short

# 4. Remote 对 (双账号隔离铁律: wangrui2025/* 禁止 push 到 mykcs)
git remote -v | head -2

# 5. CI 状态 (针对 active project repo, e.g. mykcs.github.io)
gh api repos/<owner>/<repo>/commits/HEAD/status 2>/dev/null | jq -r '.state // "NO_CI"'
```

### Layer 0 输出契约 (4 字段 per repo, 必填)

```text
╭─────────────────────────────────────────────────────────╮
│  Layer 0 Ground Truth Snapshot — <repo>                 │
│  path: <absolute-path>                                  │
│  remote: <owner>/<repo>                                │
│  1. head:   <hash> | <subject>                          │
│  2. recent: [<hash1>, <hash2>, ...]                     │
│  3. status: <clean | N uncommitted>                     │
│  4. remote_url: <url>                                  │
│  5. ci_state: <success | pending | failure | NO_CI>     │
╰─────────────────────────────────────────────────────────╯
```

**如果任何字段触发以下条件 → 阻塞 Layer 1, AskUserQuestion 询问 user**:

| 条件 | 含义 | 询问 |
|------|------|------|
| `head` empty | 仓为空 / 未初始化 | "此仓未初始化, audit 跳过?" |
| `status` ≥ 1 uncommitted | 改动未 commit | "有 uncommitted 改动, 先 commit 还是 audit 时忽略?" |
| `remote` 错 | 双账号污染 / wrong owner | "remote 是 X, 期望 Y, 切换?" |
| `ci_state` = failure | CI red | "CI 失败, audit 仍继续?" |
| `ci_state` = pending | CI running | "CI pending, 等还是先 audit?" |

### 反例 (禁止 — 这些就是 friction cluster 反复出现的 root cause)

```text
❌ "我开始 audit 了"  (跳过 Layer 0 → 不知道仓的 current state → 报"完成"时无 ground truth)
❌ "我 audit 完了, 报告如下..."  (Layer 1 跑完才看 git log → 形式违反 verification gate)
❌ "5 commits 已 push"  (口头声明, 没跑 git log -5 → CASE-CONTENT2HTML-AUDIT-VERIFICATION-GATE-FAIL-20260621 复现)
❌ 把 Layer 0 当 optional pre-check 跑一下就 skip → 违反 hard rule
```

### 正例 (强制)

```text
✅ "Layer 0 完成: 5 repos 全部 clean + remote 对 + CI green. 进入 Layer 1 审计..."
✅ "Layer 0 检测到 status 1 uncommitted, 阻塞 Layer 1, AskUserQuestion: commit 或 ignore?"
✅ "Layer 0 检测到 remote 是 wangrui2025, 期望 mykcs (双账号隔离), 阻塞, AskUserQuestion: 切换 remote 或 跳过此仓?"
✅ "Layer 0 完成: 写入 /tmp/rich-audit-L0-<run-id>.json, 包含 5 repos × 5 commands = 25 行 ground truth"
```

### Layer 0 实现位置

- **代码**: `scripts/verification_gate_precheck.py` (v2.6.19 新增, 必跑)
- **输出文件**: `/tmp/rich-audit-L0-<run-id>.json` (含 5 repos × 5 commands)
- **整合点**: Pre-flight Declaration 输出后, 调用此脚本, 5 commands 跑完才进 Layer 1

### Bonus test (v2.6.19)

**Bug 本质**: rich-audit 报"完成"无 ground truth (与 website-improve Mode A 报告"✅ 已 push" 同源)
**End-to-end command**: `python3 scripts/verification_gate_precheck.py --repos ~/.claude,~/.agents/skills,~/Repo/webs/active/mykcs.github.io`
- 旧代码预期: 0 ground truth captured, audit 跑完仍可能误报 "✅ 全部正常"
- 新代码预期: 25 行 ground truth (5 repos × 5 commands) 写入 `/tmp/rich-audit-L0-*.json`, audit 报告 reference 此文件
**Actual**: TBD (A/B test in Step 6)

---

