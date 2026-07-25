## 🔍 N-tool 协议位 audit 子任务 (per ADR-0056 + user 2026-07-13 拍板, 2026-07-13 立 + 2026-07-14 扩展)

> **触发 (user 原话 2026-07-13)**: "把我这个主机所有的 claude 记忆、规则、灵魂所有的搜索工具协议都列出来. 然后去看他们是否都执行同一组的协议, 就是我规定的 N 重网络搜索工具协议". claudecode 跑 host-self-evolve 时, **必**跑本子任务 (硬约束, 不可跳, 不依赖 user 重复指令).
>
> **目的**: 自动检测协议位字面散落 + 实际执行层 (5/6 vs 6/6) drift, 防止 SSOT 收口后子协议位漂移. **不止审计字面, 必修复到全机 active 入口都直指 SSOT** (per §20 8 步管道).
>
> **协议位**: 主 SSOT = `~/.claude/rules/protocols/N-tool-search.md` v1.1.2 (N 当前 = 6 = MiniMax + kimi-webbridge + anysearch + WebFetch + exa + mmx). claudecode 必跑 4 路盘点 + 4 维 audit, 命中 drift 走 §20 8 步管道 + 立 ADR (整数 slot).

### §1 4 路盘点协议 (新增, 2026-07-14 立, per CASE-META-PROTOCOL-MODIFICATION-PIPELINE-20260713 实战)

**触发**: 任何 host-self-evolve 跑前必跑本段, 跟 4 维 audit 并列, **不跳过**. 4 路盘点 = 列全机所有 "Claude 记忆/规则/灵魂/搜索工具协议" 入口 + 判定 active vs 历史 + 收口状态.

| #   | 维度                  | 范围                                                                                                                                                   | 关键判定                                                                                                                                                         |
| --- | --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | **记忆/灵魂层**       | `~/.claude/memory/` + `~/.claude/MEMORY.md` + `~/.claude/CLAUDE.local.md` § HOT FACTS + `~/.mem0/` 本地 config/log                                     | active 入口 (auto-memory 加载 / SessionStart 注入 / 远端 mem0 索引) 必须直指 SSOT; 旧"5-tool" / "Force-All-Search" 字面必须补 N-tool pointer + 历史标            |
| 2   | **规则/协议层**       | `~/.claude/rules/**` + `~/.claude/docs/adr/**` + `~/.claude/CLAUDE.md` + `~/.claude/CLAUDE.local.md`                                                   | SSOT 唯一性 + 全仓 active 规则引用同一 SSOT + protocols/README 死链 0 + 副 SSOT redirect 完整                                                                    |
| 3   | **skills/项目入口层** | `~/.agents/skills/*/SKILL.md` + `~/.agents/skills/*/references/` + 4 active 项目仓 `CLAUDE.md` (mysite / GDKVM / OSA / content2html 或 academic)       | skills description 顶部直指 SSOT + 子仓 protocol/references/ 含历史标不裸 5-tool + 项目仓 CLAUDE.md 至少 1 行 N-tool pointer                                     |
| 4   | **实际执行层**        | `~/.claude/settings.json` mcpServers + `~/.claude.json` mcpServers + 实际 Claude session 内可用工具列表 (区分物理 daemon/CLI 存在 vs session 路由可达) | N 个工具并行 fan-out 有 orchestrator 或强提示词约束; 缺工具走 §3 降级矩阵; 当前 session 路由可达 ≥ N-1 (kimi-webbridge 是已知 weakest link, 仅作 Layer 2 弱约束) |

### §2 4 维 audit 协议 (per ADR-0056 §1.1)

| #   | 维度                      | 跑法                                                                                                               | 期望命中                   |
| --- | ------------------------- | ------------------------------------------------------------------------------------------------------------------ | -------------------------- |
| 1   | **主仓 grep**             | `grep -rE "5-tool\|5-tool-search" ~/.claude/{rules,protocols,memory,docs,knowledge/cases,decision-stream}/`        | 0 命中 (字面) + 历史段除外 |
| 2   | **子仓 grep**             | `grep -rE "5-tool\|5-tool-search" ~/.agents/skills/*/SKILL.md ~/.agents/skills/*/references/`                      | 0 命中 (字面)              |
| 3   | **active 仓 grep**        | `grep -rE "5-tool\|5-tool-search" ~/Repo/webs/{active,academic}/` 或 `~/Claude/Projects/webs/` (per user 实际路径) | 0 命中 (跟 N-tool 无关)    |
| 4   | **N-tool pointer verify** | `grep -rE "N-tool-search\.md" ~/.claude/rules/` + `~/.claude/rules/protocols/N-tool-search.md` 存在 + 版本 v1.1+   | ≥ 1 (主 SSOT 必存)         |

> **路径例外**: 第 3 维跑路径 per user 实际配置, 旧 `~/Repo/webs/{active,academic}/` 跟新 `~/Claude/Projects/webs/` 都接受 (per v3.2.3 §Path Validation).

### §3 判定分支

| 命中                                             | 严重度 | 修法                                                                 |
| ------------------------------------------------ | ------ | -------------------------------------------------------------------- |
| 主仓/子仓 5-tool 字面 + 协议位段落               | 🔴 P0  | 走 §20 8 步管道 + 立 ADR (整数 slot)                                 |
| 主仓/子仓 5-tool 字面 + changelog/历史段         | ⚪ P2  | 不动 (历史演进证据)                                                  |
| 主仓/子仓 5-tool 字面 + 反模式段落               | ⚪ P2  | 不动 (反模式说明)                                                    |
| 副 SSOT 整篇 v2.9 协议位                         | 🔴 P0  | 整篇 redirect → N-tool-search.md v1.1.2                              |
| 协议位列 < 6 工具 (漏 mmx)                       | 🔴 P0  | 1 行补 mmx → 完整协议位                                              |
| N-tool-search.md 不存在 / 版本 < v1.1            | 🔴 P0  | 立即 git restore 或升级 (丢失主 SSOT)                                |
| 当前 session 路由 < N (缺 kimi-webbridge)        | 🟡 P1  | 报告 "⚠️ N-tool 降级到 M-tool" + 引导 user 跑 §20 路径, 不 fail-fast |
| SSOT 内部歧义 (exa '最后兜底' / §3.1 工具计数错) | 🟡 P1  | 立 v1.x.y patch (per §9 changelog), 跨 5 仓 sync                     |

### §4 修复 SOP (新增, 2026-07-14, 实战提炼自本次 cleanup run)

**触发**: §2 4 维 audit 命中 ≥1 🔴 P0 或 §3 §1 4 路盘点发现 active 入口 drift.

**完整 8 步管道** (per ADR-0055 + ADR-0056, claudecode 可复制):

1. **6 件套 grep** (`ls docs/adr/ | sort | tail` + 命中已有沉淀) — 立新 ADR / 改字段 / 加 layer / 立 skill 前必跑 (per `cross-session-grep-mandatory.md` §1)
2. **AskUserQuestion 拍板路线** (灵魂 v4 字母选项 + 1 行人话翻译) — 路线分叉 + ≥3 候选 + user 显式拍板; **必问 4 项**: (a) 修复范围 (主仓 / 主仓+子仓 / 主仓+子仓+4 项目仓); (b) 硬检查脚本挂 settings.json 还是只交付; (c) case/ADR 历史文件策略 (补 pointer vs 删除); (d) PR 协议 (worktree+auto-merge vs 直 push)
3. **§C.3.1 worktree** (`git worktree add` + 新分支) — 不可逆 + multi-file; **所有后续 Edit/Write 用 worktree 绝对路径** (关键陷阱! 避免绕过 worktree 隔离)
4. **改 N file** (主仓 + 子仓 + 项目仓, 视用户路线决策) — 13 file + 1 script (本次实战数); 策略 = 补 1 行 N-tool pointer + 历史标, 不删历史实现 (保留 audit trail)
5. **protected path 走 Python 4 维 self-verify** (`open() + replace() + write()` + 4 维 assert) — CLAUDE.md / settings.json / hooks/ 修改前必跑 (per `claudecode-verify-before-act.md` §5)
6. **commit + push + PR** (`git push -u origin feat/<topic>` + `gh pr create --head feat/<topic> --base main`) — worktree 内完成; PR body 写明 ADR 联动 + 反向证据
7. **gh pr merge --squash --delete-branch + ff-only + worktree cleanup** — PR merged 后必跑 (per `post-pr-merge-ff-verify-rule.md`); 5 字段自检表 (path / commit / push / CI / owner) + ahead/behind 0/0 验证 (防 gh PR 谎报)
8. **5 字段自检表** (per `protocols/5-field-acceptance.md` SSOT) — path 真存在 / commit hash / push ff=0/0 / CI green / owner 隔离 + drift check `bash scripts/check-n-tool-drift.sh` ✅ ALL PASS

### §5 drift check 脚本交付 (新增, 2026-07-14 实战)

**位置**: `~/.claude/scripts/check-n-tool-drift.sh` v1.0 (主仓 commit `d94fa91b`).

**功能**: 4 维验证, exit 0 = PASS, exit 1 = violation, exit 2 = SSOT 缺失 BLOCKED.

```bash
bash ~/.claude/scripts/check-n-tool-drift.sh  # 默认扫 ~/.claude/
bash ~/.claude/scripts/check-n-tool-drift.sh /path/to/repo  # 扫指定仓
```

**交付策略** (per user 拍板): 不挂 settings.json, 仅交付可执行脚本 + 文档. 用户后续可手动挂 UserPromptSubmit hook.

### §6 5 IF...THEN 触发规则

1. **IF** user 触发 host-self-evolve **THEN** 本子任务 §1 4 路盘点 + §2 4 维 audit 必跑 (per v3.2.3 硬约束, 不依赖 user 重复指令)
2. **IF** §2 audit 命中 🔴 P0 字面散落 **THEN** 走 §4 修复 SOP 立新 ADR (整数 slot 不抢 sub-slot, per ADR-0027 v1.1)
3. **IF** §1 盘点发现 active 入口 drift (hot facts / process / memory / skills / project) **THEN** §4 步骤 2 必先 AskUserQuestion 拍板 4 项, 不静默定路线
4. **IF** 命中副 SSOT 整篇 **THEN** 整篇 redirect (不只改 1 行, per §3 修法 + §6 反模式 #3)
5. **IF** N-tool-search.md 缺失 / 版本 < v1.1 **THEN** git restore + 立 ADR 立条 (per ADR-0037 散落审计)

### §7 7 协议级反模式 (永久失效, 2026-07-14 扩到 7)

1. ❌ 跑 host-self-evolve 不跑 N-tool audit 子任务 = 字面 drift 漏检 (per v3.2.3 硬约束)
2. ❌ 命中 5-tool 字面残留但没走 §20 8 步管道 = 违反 ADR-0055/0056
3. ❌ 副 SSOT 只改 1 行不整篇 redirect = 残留误导
4. ❌ audit grep 只看主仓不看子仓/active 仓 = 跨仓协议位分裂
5. ❌ 命中 P0 不立 ADR 直接 commit = 跳 ADR-0027 v1.1 整数 slot 优先
6. ❌ N-tool 协议位扩展 (加 N+1 工具) 不跑 audit = 字面散落源头
7. ❌ **§4 修复 SOP 跳步骤 (尤其 AskUserQuestion 拍板路线 + §20 8 步管道) = 违反 ADR-0055 元规则修改 8 步管道**

### §8 联动

- ADR-0056 (本子任务起源 ADR, 整数 slot 0056)
- CASE-N-TOOL-DRIFT-CLEANUP-20260713 + CASE-META-PROTOCOL-MODIFICATION-PIPELINE-20260713 (本子任务 + 修复 SOP 起源 case)
- §20 8 步管道 (per ADR-0055) — 命中 P0 必走, 不可跳步骤
- SSOT = `~/.claude/rules/protocols/N-tool-search.md` v1.1.2 (主权威)
- 副 SSOT (已作废) = `process-section-F-force-all-search.md` + 子仓 `force-all-search-protocol.md` (redirect)
- drift check 脚本 = `~/.claude/scripts/check-n-tool-drift.sh` v1.0 (per §5)

### §9 实战案例 (2026-07-14 立)

- 2026-07-13 主仓 run: 4 路盘点 (memory/规则/skills/运行) + 独立 verifier + case 补扫 → FAIL (active 不统一), 走 §20 8 步管道收口 13 file + 1 script → PR #54 MERGED
- 2026-07-14 子仓 run: 8 file 收口 → PR #24 MERGED
- 2026-07-14 项目仓 run: 3 项目仓 CLAUDE.md 各 +1 行 pointer → PR #2/#4/#2 MERGED

---

## 📋 §Layer 1.0 — N-tool 协议位 drift audit 协议 (per ADR-0056, 2026-07-13 立)

> **协议位**: host-self-evolve 跑前 banner 之后**必**跑本协议 (跟 banner Layer 1.0 + 实战案例沉淀段 line 194-231 + CASE-N-TOOL-DRIFT-CLEANUP-20260713 协同). 缺 = 违反 ADR-0056 硬约束.
>
> **目的**: 任何 web 搜索 / 信息查证协议位 (N-tool-search.md v1.1) **字面**必须一致, 不允许散落. 主仓 + 子仓 + active 仓 4 维 grep 必跑.

### 4 维 audit 协议 (per §20 SSOT 原则 + ADR-0056 §1.1)

**Step 1**: 主仓 grep (N-tool / 5-tool / Force-All-Search 协议位残留)

```bash
grep -rE "5-tool|5 tool|Force-All-Search|N-tool-search\.md|web_search|MiniMax|kimi-webbridge|anysearch|mmx" \
  ~/.claude/rules/ ~/.claude/protocols/ ~/.claude/memory/ \
  ~/.claude/CLAUDE.md ~/.claude/CLAUDE.local.md 2>/dev/null
```

**Step 2**: 子仓 grep (子仓 skill 协议位引用)

```bash
grep -rE "5-tool|5 tool|N-tool-search\.md|MiniMax|kimi-webbridge|anysearch|mmx" \
  ~/.agents/skills/ 2>/dev/null
```

**Step 3**: 4 active 仓 grep (跨仓协议位一致性)

```bash
for d in ~/Repo/webs/active/mykcs.github.io ~/Repo/webs/active/GDKVM \
         ~/Repo/webs/active/OSA ~/Repo/webs/active/content2html; do
  if [ -d "$d" ]; then
    grep -rln "5-tool\|N-tool-search\.md\|网络搜索" "$d" 2>/dev/null
  fi
done
```

**Step 4**: 副 SSOT 验证 (确保 N-tool-search.md v1.1 是**唯一**权威)

```bash
test -f ~/.claude/rules/protocols/N-tool-search.md && echo "✅ 主 SSOT 存在"
# 副 SSOT 必须 redirect header (不字面复述协议位)
test -f ~/.claude/rules/references/process-section-F-force-all-search.md
test -f ~/.agents/skills/host-self-evolve/references/force-all-search-protocol.md
```

### 判定分支 (IF...THEN, 必跑)

- **IF** Step 1-4 命中 "5-tool-search.md" 旧文件名 OR 字面 5 工具 (不含 mmx 第 6 工具) **THEN** 🔴 **P0 字面散落** → 走 §20 8 步管道修 (per ADR-0055)
- **IF** 命中 "5-tool" / "Force-All-Search" 但已 pointer SSOT **THEN** 🟡 P1 旧名残留 → 批量 1 行替换, 1 PR 1 commit
- **IF** 命中 docs/adr/ / knowledge/cases/ / decision-stream/ **THEN** ⚪ P2 历史档案 → 永久反映协议演进史, 不修
- **IF** Step 4 副 SSOT 字面复述协议位 (非 redirect) **THEN** 🔴 P0 整篇 redirect
- **IF** 4 active 仓命中 **THEN** 🔴 跨仓污染, 走 §20 + 双账号铁律隔离 (per ADR-0054)

### §20 8 步管道触发 (P0 命中时, per ADR-0055)

1. 6 件套 grep 现状 (`ls docs/adr/ | sort | tail` + 命中已有沉淀)
2. AskUserQuestion 拍板路线 (A 全清 / B 只 P0 / C 只删旧副 SSOT / D 保持现状)
3. §C.3.1 worktree (`git worktree add` + 新分支)
4. 改 N file (Write tool 用 worktree 绝对路径)
5. protected path 走 Python 4 维 self-verify (per §18)
6. commit + push + PR (主仓 + 子仓 2 PR, 跨仓协议位 100% 一致)
7. gh pr merge --squash --delete-branch + ff-only + worktree cleanup
8. §H 5 字段自检表 (path / commit / push / CI / owner)

### 输出格式 (协议位统一, per ADR-0056)

```
═══════════════════════════════════════════════════════════
🔍 Layer 1.0 N-tool 协议位 drift audit (per ADR-0056)
═══════════════════════════════════════════════════════════

[Step 1 主仓] P0=0 P1=N P2=M (历史档案)
[Step 2 子仓] P0=0 P1=N P2=M
[Step 3 4 active 仓] 0 命中 (跨仓协议位一致)
[Step 4 副 SSOT] 主仓 redirect ✅ + 子仓 redirect ✅

🎯 判定:
  ├─ P0 命中 = 0 → 协议位字面 100% 一致, 不修
  ├─ P1 命中 = N → 批量 1 行替换, 1 PR 1 commit (可选, 可 P2 follow-up)
  └─ P2 命中 = M → 永久反映协议演进史, 不修 (合规)

═══════════════════════════════════════════════════════════
```

### 反模式 (永久失效, 7 条)

1. ❌ 跑 host-self-evolve 不跑 Layer 1.0 audit = 字面 drift 漏检 (per ADR-0056)
2. ❌ 命中 P0 不走 §20 8 步管道 = 违反 ADR-0055/0056
3. ❌ 副 SSOT 只改 1 行不整篇 redirect = 残留误导
4. ❌ audit 只看主仓不看子仓/active 仓 = 跨仓协议位分裂
5. ❌ 命中 P0 不立 ADR 直接 commit = 跳 ADR-0027 v1.1 整数 slot 优先
6. ❌ N-tool 协议位扩展 (加 N+1 工具) 不跑 audit = 字面散落源头
7. ❌ 协议位修复失败不跑 `gh pr view --json state` 兜底 (per ADR-0026 + post-pr-merge-ff-verify-rule.md)

### 联动

- ADR-0056 (本子任务起源 ADR, 整数 slot 0056)
- CASE-N-TOOL-DRIFT-CLEANUP-20260713 (本子任务起源 case)
- §20 8 步管道 (per ADR-0055) — 命中 P0 必走
- SSOT = `~/.claude/rules/protocols/N-tool-search.md` v1.1 (主权威)
- 副 SSOT (已作废) = `process-section-F-force-all-search.md` + 子仓 `force-all-search-protocol.md` (redirect)
- §I.4 self-evolution 8 步循环 (per rich-audit v2.6.34) — Layer 1.0 audit 是 step 1 协议位扩展
- post-pr-merge-ff-verify-rule.md (§C.3.7 + ADR-0026 必读 body)
