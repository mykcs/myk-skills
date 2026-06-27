# Layer I.4: Skill Self-Evolution (审计完 ~/.claude 后升级 skill 自身)

> **触发**: rich-audit 跑完 Layer 1-3 + cmd 5 兜底 CI verify + cmd 4 acceptance protocol 5 字段 PASS 之后, **必须**对 rich-audit skill 自身跑一次 self-evolution.
> **范围**: 仅 rich-audit skill (不连带其他 skill, 除非 user 显式要求).
> **完整 SOP**: §F.1 失败案例自审 + §F.2 反模式沉淀 + §F.3 changelog 更新 + §F.4 ADR 落地 + §F.5 实战命令模板 + §F.6 反模式 + §F.7 流程图

## 为什么需要本 Layer (背景)

rich-audit 是"自我进化系统":

- **Layer 1-3**: 审计 + 修复 + 外部知识扫描 (跟 user 仓耦合)
- **Layer A.2-A.3**: PR/CI 健康扫描 + 修复 (跟 GitHub Actions 耦合)
- **Layer I.1 (v2.6.30 §I)**: external sources self-evolution (跑 5-tool fan-out 抓外部知识)

**缺口**: 跑完 rich-audit 后, **rich-audit skill 自身不升级**. user 2026-06-27 反馈:

> "现在修改重度审审计这个技能, 就是在这个你审计完这个斜杠点 cloud 等文件夹的时候, 你需要对 skill 也进行一次提升."

意思是: **审计完外部仓, 顺手审计自身**. 类似 IDE 的 "lint others + lint self".

---

## §F.1 失败案例自审 (post-audit, per session)

每次 rich-audit 跑完, **强制**自审本 session:

```bash
# 1. 扫本 session 的 failed / partial / repeated-ask 模式
decision-stream_file="$HOME/.claude/decision-stream/<session-id>.md"
test -f "$decision-stream_file" && {
  echo "=== self-decisions 本 session ==="
  cat "$decision-stream_file"
}

# 2. 扫本 session AskUserQuestion 调用 (claudecode 反复问 user 的硬证据)
echo "=== 本 session AskUserQuestion count ==="
# (看 transcript logs 里的 ToolUse 计数 AskUserQuestion tool)

# 3. 跟反转硬约束 (v2.6.33) 对照
#   - 8 类自决: 哪些做了? 哪些又问了?
#   - 8 类必问: 哪些真问了? 哪些该问没问?
#   - 5 类反模式: 哪些犯了?
```

**判定**: 如果发现 1+ 个新失败模式, 走 §F.2.

---

## §F.2 反模式沉淀 (新增到 SKILL.md, **v2.6.35 强化: 必先跑 5-tool fan-out**)

发现新反模式后, **必须**先跑 5-tool Force-All-Search (per process.md §F.1 + §F.1.2 降级矩阵), **得出结论后再 Edit SKILL.md 加新段**.

### §F.2.0 必跑前置: 5-tool parallel fan-out 兜底 (v2.6.35 NEW)

```bash
# 必跑 (跟 process.md §F.1 + references/force-all-search-protocol.md §F.1.2 同步)
echo "=== 5-tool fan-out (per §F.2.0 强制前置) ==="

# 1. MiniMax 中文语义搜索
mcp__MiniMax__web_search "Claude Code skill self-evolution anti-pattern $TOPIC"

# 2. kimi-webbridge Scholar 搜索
# (CLI session 不可达时降级 exa Scholar, per process.md §F.1.2)
echo "  - kimi-webbridge: ❌ CLI 不可达, 降级到 exa Scholar"

# 3. anysearch fallback
mcp__anysearch__web_search "Claude Code SKILL.md self-evolution best practices"

# 4. WebFetch 直接抓 (官方 doc / Anthropic blog)
WebFetch https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview "skill self-evolution best practices"

# 5. exa combo (search + fetch)
mcp__exa__web_search_exa "Claude Code skill maintenance evolution"
mcp__exa__web_fetch_exa <high-value URL>

# 输出契约 (per process.md §F.2: per-tool 1 段, 4 字段: 工具/搜索内容/结论/状态)
# 然后 Phase B: merge + compare 共识/冲突
# 然后 Phase C: 冲突再查 ≤2 层, 仍不收敛 → 报告 "未收敛" 降级人工
```

**为什么强制**: claudecode 凭记忆/训练数据写 SOP 容易 drift, 5-tool fan-out 提供 4 源三角验证 (Claude Code 官方 docs + self-improving-agent 论文 + engineering playbook + configuration stack 案例). **避免 v2.6.33 那种"claudecode 反复问 user" 反模式凭记忆想当然沉淀**.

### §F.2.1 Edit SKILL.md (5-tool fan-out 后)

5-tool 跑完 + 共识/冲突报告出来后, **才**动笔 Edit:

```bash
# 1. Edit SKILL.md 加反模式段 (用 Edit 工具, 跟 §A.3 平行)
# 模板:
#   ## §X.Y <反模式名> (<version>, <date>)
#   - 现象: <what happened>
#   - 根因: <why>
#   - 修复: <how>
#   - 反模式: <do not>

# 2. bump version (v2.6.33 → v2.6.34)
# 3. 加 changelog (跟 §E.5 4 处同步对齐)
# 4. 加 changelog 末尾 reference 到本文件 §F.2
```

**真实案例 (v2.6.33 永久修复)**:
- 现象: claudecode 在 PR merged 后还问"要不要清理 worktree"
- 根因: 误解灵魂 v3 反转模式, 把"bug fix 直接做"当成唯一自决类别
- 修复: 4 处同步反转硬约束 SOP
- 反模式: "可逆写操作包装成必问"

---

## §F.3 changelog 更新 (跟 v2.6.30 §I.1 Step 5 同步)

rich-audit v2.6.30 §I.1 八步循环 Step 5 是"更新 SKILL.md changelog". 本 Layer 在 §F.2 基础上, 必跑:

```bash
# 1. SKILL.md frontmatter version: 2.6.X → 2.6.X+1
# 2. SKILL.md changelog 数组最前面加新 entry
# 3. 同步到 4 处 (跟 v2.6.33 §E.5):
#    - SKILL.md frontmatter
#    - references/ (新建或更新)
#    - CLAUDE.local.md (新加 §X)
#    - MEMORY.md HOT FACTS (新加 §X)
```

**反模式**:
- ❌ 只 bump version 不加 changelog (drift 后失忆)
- ❌ 改了 SKILL.md 不同步 CLAUDE.local.md / MEMORY.md (4 处必同步, 任何 1 处改其他 3 处必改)
- ❌ changelog 写得太长 (>1 段应拆) 或太短 (<1 行查不到根因)

---

## §F.4 ADR 落地 (新决策必写)

发现新反模式 + 修复路径, **必须**写 ADR (`~/.claude/docs/adr/`):

```bash
# 1. 看现有 ADR 编号
ls $HOME/.claude/docs/adr/ | sort -V | tail -3

# 2. 新建 ADR-NNNN-<topic>.md
ADR_NEXT=$(($(ls $HOME/.claude/docs/adr/ | grep -oE '^[0-9]+' | sort -n | tail -1) + 1))
ADR_FILE="$HOME/.claude/docs/adr/${ADR_NEXT}-<topic>.md"

# 3. 用 record-case skill 模板填:
#   - 状态 / 决策 / 背景 / 备选方案 / 后果 / 实施步骤
```

**真实案例**: v2.6.33 反转硬约束 → ADR-0020 (待写, 本次 session 自决任务清单)

---

## §F.5 实战命令模板 (skill self-evolve 完整流程)

```bash
# 1. Post-audit 自审
echo "=== §F.1 自审 ==="
# (看 §F.1)

# 2. 若发现新反模式, 走 §F.2 (Edit SKILL.md)
# 3. bump version
# 4. add changelog
# 5. 4 处同步 (SKILL.md / references/ / CLAUDE.local.md / MEMORY.md)

# 6. smart-push 直 push main (跟 v2.6.33 §E.2 #7 一致)
git -C $HOME/.agents/skills add <changed files>
touch $HOME/.agents/skills/.smart-push-skip-review
$HOME/.claude/scripts/smart-push.sh $HOME/.agents/skills "<semantic msg>" done --strict-staging

# 7. 5 commands verify (cmd 1-4 + cmd 5 兜底)
git -C $HOME/.agents/skills log -1 --format="%h | %s"
git -C $HOME/.agents/skills log --oneline -5 | head -5
git -C $HOME/.agents/skills status --short
git -C $HOME/.agents/skills remote -v | head -2
gh api repos/mykcs/myk-skills/commits/HEAD/status

# 8. cmd 5 兜底 CI verify
gh run list --repo mykcs/myk-skills --limit 5 --json conclusion | python3 -c "
import json, sys
fails = [r for r in json.load(sys.stdin) if r.get('conclusion') == 'failure']
print('failures:', len(fails))
"
```

---

## §F.6 反模式 (claudecode 必避)

- ❌ **跑完 rich-audit 不自审** = 漏掉本 Layer, skill 永远不变
- ❌ **自审发现反模式但不落地** = "下次再升级" 违反 no-stuck 协议 (v2.6.30 §C.3.6)
- ❌ **只 bump version 不写 changelog** = 失忆, 下次审计会重复踩同一坑
- ❌ **改了 SKILL.md 不 4 处同步** = drift, 反转硬约束失效
- ❌ **加 ADR 不引用到 changelog** = 跟其他 case 脱节
- ❌ **写太抽象的 SOP** = 下次不知道做什么, 必须含命令模板 (per §F.5)

---

## §F.7 完整流程图

```
rich-audit 触发
    ↓
Layer 0: git/gh state pre-check (5 commands)
    ↓
Layer 1-3 (审计 + 修复 + 进化)
    ↓
Layer A.2 + A.3 (PR + CI 健康扫描 + 修复)
    ↓
Layer I.1 (v2.6.30): external sources self-evolution (5-tool fan-out)
    ↓
Layer I.4 (本文件): Skill Self-Evolution ← 新增
    ├─ §F.1 失败案例自审 (扫本 session 反复问 user / 假反模式)
    ├─ §F.2 反模式沉淀 (Edit SKILL.md 加新段)
    ├─ §F.3 changelog 更新 (bump version + 4 处同步)
    ├─ §F.4 ADR 落地 (新决策)
    ├─ §F.5 实战命令模板
    └─ §F.7 流程图闭环
    ↓
完成
```

---

## Cross-References

- v2.6.30 §I Self-Evolution Cycle (external sources): SKILL.md `## §I` + references/execution-flow.md
- v2.6.33 反转硬约束: [`calm-flow-reverse-mode.md`](calm-flow-reverse-mode.md)
- 5-tool Force-All-Search: [`force-all-search-protocol.md`](force-all-search-protocol.md) §F.1.1/§F.1.2
- §H Acceptance Protocol: process.md §H (5 字段自检表, 任务完成前必跑)
- §D CI 检查修复: [`layer-a3-ci-check-repair.md`](layer-a3-ci-check-repair.md)
- §A.2 PR 健康扫描: [`layer-a2-pr-ci-health-scan.md`](layer-a2-pr-ci-health-scan.md)
- 真实 case 2026-06-27: 本 session v2.6.33 反-failure 永久修复
- 真实 case 2026-06-21: CASE-CONTENT2HTML-AUDIT-VERIFICATION-GATE-FAIL (verify gate bug)
- 真实 case 2026-06-23: CASE-CLAUDECODE-DEFERRED-THEATER-RECURRENCE (反复问 user)