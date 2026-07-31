---
name: post-pr-merge-ff-verify
description: |
  PR 合并 (gh pr merge) 之后必跑的 fast-forward verify SOP: ahead/behind 检查、
  local-only commits 兜底、reset --mixed 撤回路径。当用户合并 PR、提到 ff verify、
  ahead/behind 不为 0 0、或需要撤回本地 merge commit 时触发。
license: MIT
metadata:
  version: 1.0.0
  category: workflow
  author: mykcs
  migrated-from: ~/.claude/rules/post-pr-merge-ff-verify-rule.md (2026-07-25 rules 减重)
triggers:
  - ff verify
  - post pr merge
  - /post-pr-merge-ff-verify
  - PR 合并后 verify
  - ahead/behind check
  - gh pr merge verify
when_to_use: |
  ff verify / post merge / ahead-behind / 撤回
---

# 规则: PR 合并后强制 FF 验证协议 (post-pr-merge-ff-verify)

> **触发来源**: CASE-RICH-AUDIT-V2-6-60-PARALLEL-VS-SERIAL-20260702 (2026-07-02 立, 3 次反复触发 v2.6.58/59/60 同源 gh PR 谎报反模式, 满足 record-case 协议 ≥ 2 次必须升级为硬约束条件)
> **生效**: 任何 `gh pr merge` 完成后必跑 `~/.omc/hooks/post-pr-merge-ff-verify.sh <repo>` 兜底
> **强制执行**: hook `PostToolUse[matcher="Bash"]` 自动跑 (per §3.2 hook 实现, 跟 gh pr merge case 过滤), command 字符串含 `gh pr merge` 才真触发脚本
> **⚠️ 已知约束 (per §10)**: Claude Code 无 `PostPRMerge` 事件, 旧版用 `hooks.PostPRMerge` 整段静默失效 (per CASE-HOOK-EVENT-NAME-20260716). 必须走 PostToolUse + Bash matcher + inline case 过滤.

## 1. 触发条件 (v2.6.60 立, 跟 v2.6.58/59 同源 PR 谎报反模式协同固化)

**触发场景** (any-of):
- ✅ `gh pr merge <PR_NUMBER>` 执行后
- ✅ `gh pr merge --squash --delete-branch` 执行后
- ✅ `gh pr merge --auto` 状态变更后
- ✅ 任何 PR 合并操作 (走 §11.1 auto-merge 4 条件)
- ✅ 任何 commit hash 已被 GitHub API 标 MERGED 后

**失败症状** (跟 v2.6.58/59/60 同源反模式):
- gh 返 "was already merged" 但本地 main 找不到 commit (ahead/behind 1 0 落后)
- gh 返 "merged" 但 origin/main 未推进 (PR merged 但 ff 未到本地)
- gh 返 "merged" 但 ahead/behind 不为 0 0 (本地有 commit 未推 / 本地落后 origin)

## 2. 强制执行流程 (per §3 hook 实现)

**Step 1**: PR 合并后, 必跑 hook:
```bash
bash ~/.omc/hooks/post-pr-merge-ff-verify.sh <repo_path>
# repo_path = $HOME/.claude 或 $HOME/.agents/skills
```

**Step 2**: 检查 hook 退出码:
- **exit 0** (FF status ✅ in sync): 走 Step 4
- **exit 1** (FF status ⚠️ 落后): 走 Step 3 修复
- **exit 2** (FF status ❌ diverged): 走 §C.6 5 步 false-positive 诊断

**Step 3** (hook exit 1 修复):
```bash
# 落后修复 (PR merged 但本地 main 落后 origin/main)
git -C "<repo_path>" fetch origin main
git -C "<repo_path>" merge --ff-only origin/main
# 验证
bash ~/.omc/hooks/post-pr-merge-ff-verify.sh <repo_path>
# 期望 exit 0
```

**Step 4** (后续动作):
- 走 worktree 清理 (per §11.1 + §C.3.6)
- 跑 5 字段自检 (path/commit/push/CI/owner) + 第 6 字段 FF status (per v2.6.60 §C.3.7)
- decision-stream 流追加 (per calm-flow §4)

## 3. hook 实现 (`~/.omc/hooks/post-pr-merge-ff-verify.sh` v2.0)

> **位置**: `~/.omc/hooks/post-pr-merge-ff-verify.sh` (148 lines bash, v2.0 完整 source)
> **⚠️ v2.0 真相 (2026-07-26 立 CASE 修正)**: v2.0 完整 source 在 `~/.omc/` 独立 git 仓库活着 (commit 7cec24a, 2026-07-21, `feat(hooks): post-pr-merge-ff-verify.sh v2.0 + reset-helper.sh v1.0`). CASE-FF-VERIFY-SCRIPT-LOST-20260726 误判为失踪, 实为 v2.0 没 checkout 到 .omc/hooks/ working tree. v3.0 缩水版已撤回, v2.0 完整 source (148 行, 4 维自检 + 3 选 1 diverged 恢复 + 5 IF...THEN 决策矩阵 + 4 反模式) 重新挂载
> **退出码**: 0 = in sync / 1 = 落后需 ff / 2 = diverged
> **触发机制**: 通过 `~/.claude/settings.json` 的 `hooks.PostToolUse[matcher="Bash"]` inline 过滤 `gh pr merge` 子串, 命中后 background 跑本脚本 (per §3.2)

**4 维自检** (per v2.6.60 §C.3.7):
1. path: `test -d <repo_path> && echo ✅`
2. fetch: `git -C <repo_path> fetch origin main 2>&1 | tail -1`
3. ahead/behind: `git -C <repo_path> rev-list --left-right --count @{u}...HEAD`
4. FF status: 解析 ahead/behind 输出 → exit 0/1/2

## 3.2 挂载 (settings.json PostToolUse[Bash] inline, 2026-07-25 迁移)

> **⚠️ 历史**: v1.0 (2026-07-02) 用 `hooks.PostPRMerge`, 2026-07-16 启动日志报 `Unknown hook event "PostPRMerge" was ignored` → 整段静默失效 (per CASE-HOOK-EVENT-NAME-20260716). v3 (2026-07-25) 迁移到 PostToolUse + Bash matcher. v2.0 脚本 (2026-07-21 commit 7cec24a) 完整存活在 .omc 独立 git 仓, working tree 未 checkout 历史误判为失踪.

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "/bin/sh -c 'cmd=\"$CLAUDE_TOOL_INPUT_COMMAND\"; case \"$cmd\" in *gh\\ pr\\ merge*) bash \"$HOME/.omc/hooks/post-pr-merge-ff-verify.sh\" \"$HOME/.claude\" >/dev/null 2>&1 &;; esac; exit 0'"
          }
        ]
      }
    ]
  }
}
```

**3 维自检** (per `claudecode-verify-before-act.md` §4 IF #5 + `tooling §A.6 #2`):
1. **event 白名单**: `jq '.hooks | keys' ~/.claude/settings.json` → 14 个合法 event (Notification/PermissionRequest/PostToolUse/PostToolUseFailure/PreCompact/PreToolUse/SessionEnd/SessionStart/Stop/StopFailure/SubagentStart/SubagentStop/TaskCompleted/UserPromptSubmit), **不**含 PostPRMerge ✅
2. **matcher 工具名**: matcher = `"Bash"`, 只匹配 Bash 工具, 不匹配 Edit/Write
3. **case 过滤命令**: command 字符串内含 `case "$cmd" in *gh\ pr\ merge*)`, 命中 `gh pr merge` 才 background 跑脚本. 不命中 → 立即 exit 0, 0 副作用

**生效条件**: 改完 settings.json 必重启 Claude Code (hooks 在 session start 时固化)

## 4. 5 IF...THEN 规则 (跟 v2.6.60 case 段 8.5 协同)

1. **IF** `gh pr merge` 完成 **THEN** 必跑 `~/.omc/hooks/post-pr-merge-ff-verify.sh <repo>` 兜底
2. **IF** hook 跑出 ahead/behind 1 0 落后 **THEN** 必跑 `git merge --ff-only origin/main` 修复, 不依赖 gh 报告
3. **IF** hook 跑出 ahead/behind diverged **THEN** 跑 §C.6 5 步 false-positive 诊断
4. **IF** hook 跑通 exit 0 **THEN** 走 5 字段自检第 6 字段 FF status (per v2.6.60 §C.3.7)
5. **IF** PR merged 但 hook 跑不通 (exit 2) **THEN** 立即 STOP + AskUserQuestion (跟 §C.3.6.1 no-stuck 协同)

## 5. 5 协议级反模式 (永久失效, 跟 v2.6.60 case 段 8.6 协同)

- ❌ 依赖 gh PR merged 报告不跑实测 (per v2.6.58/59/60 三次反复)
- ❌ PR 合并后不跑 hook 兜底 (违反本协议 step 1)
- ❌ ahead/behind 1 0 落后不 ff 修复 (违反本协议 step 3)
- ❌ hook exit 2 diverged 强行 retry 3+ 次 (违反 §C.3.6.1 no-stuck)
- ❌ 5 字段自检缺第 6 字段 FF status (违反 v2.6.60 §C.3.7)

## 6. 跨规则协同 (跟其他 hook 协议位)

- **cross-session-grep-mandatory.md §3** (第 1 个 hook 协议位, PreToolUse + 6 件套 grep 防空白起点)
- **claudecode-verify-before-act.md §5** (第 2 个 hook 协议位, PreToolUse + 4 维 self-verify 防凭印象做事)
- **post-pr-merge-ff-verify-rule.md** (本协议, 第 3 个 hook 协议位, **PostToolUse[Bash] + gh pr merge case 过滤** + ahead/behind 兜底防 gh PR 谎报)
- **3 个 hook 协议位协同**: 立新文件前 6 件套 grep + 改 protected path 前 4 维 self-verify + PR 合并后 ahead/behind 兜底

## 7. 历史 record

- **2026-07-25 v1.1 立**: 加 §3.2 (PostToolUse[Bash] 挂载) + §10 (已知约束段, Claude Code 无 PostPRMerge 事件) + §6 联动更新. 触发: CASE-HOOK-EVENT-NAME-20260716 + 用户 2026-07-25 显式确认 "顺手改规则文档". 联动: hooks/README.md row 3 + ADR-0047 superseded 注解.
- 2026-07-02: 立 (CASE-RICH-AUDIT-V2-6-60-PARALLEL-VS-SERIAL-20260702 触发, 3 次反复 v2.6.58/59/60 同源反模式, 满足 record-case 协议 ≥ 2 次必须升级为硬约束条件)
- 联动: ADR-0036 (整数 slot 0036 立, §C.3.7 跨 skill 统一协议) + v2.6.60 case 段 8.1/8.4/8.5/8.6/8.7 + process.md §C.3.7 (主仓协议位)

## 8. 相关

- CASE-RICH-AUDIT-V2-6-60-PARALLEL-VS-SERIAL-20260702 (2026-07-02, 4 维对比 + hook v1.0 实战验证)
- ADR-0036-rich-audit-v2-6-60-cross-skill-protocol (整数 slot 0036, §C.3.7 跨 skill 统一协议)
- v2.6.58 / v2.6.59 / v2.6.60 三段 sub-agent 协议位 (Plan Opus / Execute Opus / Verify Opus, 物理隔离)
- cross-session-grep-mandatory.md §3 (第 1 个 hook 协议位)
- claudecode-verify-before-act.md §5 (第 2 个 hook 协议位)
- process.md §C.3.7 跨 skill 统一协议 + §C.3.6.1 no-stuck + §C.6 5 步 false-positive 诊断
- universal.md §A.4.1 硬规则 + §A.4.3 反模式
- CASE-HOOK-EVENT-NAME-20260716 (PostPRMerge 死链 case, 触发本协议 v1.1 升级)
- ADR-0074 §A.6 #2 (3 维 jq 白名单交叉验证硬约束, 跟本协议 §3.2 协同)

## 10. 已知约束 (Claude Code 无 PostPRMerge 事件, 必走 PostToolUse + Bash matcher)

> **立条**: 2026-07-25 per CASE-HOOK-EVENT-NAME-20260716 (用户启动日志报 `Unknown hook event "PostPRMerge" was ignored`, 整段 hook 静默失效)
> **目的**: 防下个 session 再把 hook 挂到不存在的 event 名

**Claude Code 27 个 hook event (权威白名单)**:
PreToolUse / PostToolUse / PostToolUseFailure / PostToolBatch / Notification / UserPromptSubmit / UserPromptExpansion / SessionStart / SessionEnd / Stop / StopFailure / SubagentStart / SubagentStop / PreCompact / PostCompact / PermissionRequest / PermissionDenied / Setup / TeammateIdle / TaskCreated / TaskCompleted / Elicitation / ElicitationResult / ConfigChange / WorktreeCreate / WorktreeRemove / InstructionsLoaded / CwdChanged / FileChanged / DirectoryAdded / MessageDisplay

**❌ 不存在的 event** (跟 PR merge 相关, 但 Claude Code 没原生支持):
- `PostPRMerge` ← 用户曾经挂, 静默失效 (本次 v1.1 修)
- `PreMerge` / `OnPRMerged` / `PRMerged` / 类似命名猜测 ← 都**不**存在

**✅ 正确挂法** (per §3.2):
```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "/bin/sh -c 'cmd=\"$CLAUDE_TOOL_INPUT_COMMAND\"; case \"$cmd\" in *gh\\ pr\\ merge*) bash \"$HOME/.omc/hooks/post-pr-merge-ff-verify.sh\" \"$HOME/.claude\" >/dev/null 2>&1 &;; esac; exit 0'"
          }
        ]
      }
    ]
  }
}
```

**3 维自检** (per `claudecode-verify-before-act.md` §4 IF #5 + `tooling §A.6 #2`):
1. event 名在 27 白名单内 ✅
2. matcher 匹配工具名 (Bash/Edit/Write 等), 不是命令字符串
3. 命令字符串过滤靠 hook 脚本内 `case "$cmd" in *<pattern>*)` 模式

**反模式 (永久失效)**:
- ❌ "猜 event 名 (PreMerge / OnPRMerged / PRMerged)" → 全部不在白名单, 整段丢弃
- ❌ "保留 `hooks.PostPRMerge` 反正无害" → 启动日志持续报错 + 误导用户以为 hook 在工作
- ❌ "改 hook event 名凑对" → 协议位是白名单约束, 不能凑
- ❌ "matcher 写命令字符串 (e.g. `\"Bash(gh pr merge)\"`)" → matcher 协议位只匹配工具名, 命令过滤靠脚本内 case

**联动**:
- CASE-HOOK-EVENT-NAME-20260716 (本约束起源 case)
- ADR-0074 §A.6 #2 (3 维 jq 白名单交叉验证硬约束)
- tooling §A.1 settings.json SOP 5 件套 (backup → jq → validate → diff check → atomic commit)
- claudecode-verify-before-act.md §4 IF #5 (改 settings.json hook event 必跑白名单验证)
