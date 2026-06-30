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

### §F.2.0 必跑前置: 5-tool parallel fan-out 兜底 (v2.6.35 NEW, v2.6.37 修 happy-coder remote mode)

**⚠️ v2.6.37 修复 (CASE-RICH-AUDIT-FANOUT-HAPPY-CODER-STUCK-20260627)**: fan-out 跑在 happy-coder remote mode (PID 9561) 时, 工具列表跟 desktop session 隔离, 调 `mcp__exa__web_search_exa` 这种 sub-agent 看不见的工具会**死循环 retry 1h+** (agent 没 max-turns 上限 + no timeout), 最后被 harness GC 掉但 task ID 丢失 → TaskStop 找不到.

**硬规则 — fan-out 跑前必跑 self-probe** (3 步, <5s):

```bash
# Step 1: 检测是否在 happy-coder remote mode
if pgrep -lf "happy-coder" | grep -q "remote"; then
  echo "⚠️ happy-coder remote mode detected → 走 main loop 兜底, 不 spawn sub-agent"
  echo "理由: remote 跟 desktop 工具列表隔离, fan-out sub-agent 会死循环 retry 不存在的工具"
  # 改用 main loop 直接跑 (WebFetch + MiniMax + anysearch + mindstudio 4 源替代)
  exit 0  # 跳过 sub-agent fan-out
fi

# Step 2: 验证 5-tool 实际可见
for tool in "mcp__MiniMax__web_search" "mcp__anysearch__web_search" "WebFetch" "mcp__exa__web_search_exa" "kimi-webbridge"; do
  command -v "$tool" 2>/dev/null >/dev/null && echo "✅ $tool" || echo "⚠️ $tool MISSING"
done

# Step 3: 工具全缺 → 走 main loop + 跳过 sub-agent (避免 spawn 一个必死 task)
```

**降级策略 (按可见工具数)**:

| 可见工具数 | 行为 |
|----------|------|
| 5/5 | spawn sub-agent 跑完整 fan-out |
| 3-4/5 | spawn sub-agent 但 skip 缺席工具 (per process.md §F.1.2) |
| 0-2/5 | **不走 sub-agent**, main loop 跑 WebFetch + anysearch 2-tool 兜底 |
| happy-coder remote 命中 | **不走 sub-agent**, main loop 跑 4 源 (WebFetch + MiniMax + anysearch + mindstudio fallback) |

**反模式 (claudecode 必避)**:
- ❌ happy-coder remote 模式下 spawn fan-out sub-agent → 1h+ 死循环后被 GC (本 case 反例)
- ❌ 跳过 self-probe 直接 spawn → 同上
- ❌ 缺席工具 retry 而不是 fallback → 跟 process.md §F.1.2 fail-fast (Layer 2) 兼容, 不强制 spawn 必死 task

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

### §F.2.2 4 源共识沉淀模板 (v2.6.36 立)

§F.2.0 5-tool 跑完, merge + compare 报告出来后, **把 4 源共识/冲突写到 SKILL.md changelog** (而不是只 bump version). 模板:

```
### 5-tool fan-out 4 源三角验证

| 维度 | [源 1] | [源 2] | [源 3] | [源 4] | 共识 |
|------|--------|--------|--------|--------|------|
| [关键洞见 1] | ✅ | ✅ | ✅ | ✅ | 高 confidence |
| [关键洞见 2] | ✅ | ✅ | ❌ | ✅ | 单源 (可接受) |
| [关键洞见 3] | ⚠️ | ⚠️ | ⚠️ | ⚠️ | 未收敛 → 降级人工 |

### 关键洞见 (供 §F.2.1 SKILL.md 升级用)

1. **Anthropic 官方 progressive disclosure** = SKILL.md frontmatter 必须含 name + description (max 64/1024 chars)
2. **[源 2 案例]** = [模式 + 优势 + 适用场景]
3. **[源 4 pattern]** = [Learnings.md / 版本管理 / drift detection]
```

**真实案例 (v2.6.36)**: 本次 rich-audit session 跑完, 4 源 (MiniMax + anysearch + WebFetch + mindstudio fallback) 共识 = progressive disclosure 3-level 官方约束 + Snowtumb/auto-skill-update bump.sh 模式. 落地到 SKILL.md v2.6.36 frontmatter description + trigger 列表.
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

### §F.4.1 完整端到端案例: MiniMax key rotation v3 → v4 (2026-06-30, 跨 2 session)

**触发**: user 原话 "修复 mcp__MiniMax__web_search 仍 2049 (key 失效, 跳过)" — mcp 工具返 2049 invalid api key, claudecode 误判 stale snapshot, 实际服务端物理失效.

**§F.1 失败案例自审** (4 维 evidence + 5 失败路径):

| Evidence | 工具 | 判定 |
|----------|------|------|
| 直 curl 老 key | `curl -X POST .../v1/text/chatcompletion_v2` | 2049 (服务端拒) ❌ |
| 新 key 直 curl | 同上 | 200 + Pong! ✅ |
| mcp__MiniMax__web_search | 上一条 session (46186) | 2049 (snapshot 永久, v3 假设) |
| mcp__MiniMax__web_search | 新 session (本 session) | 10 results (status_code 0, v4 实测 reload ✅) |
| .claude.json | grep -o key | 119 chars 新 key 真值 |

**5 失败路径** (claudecode 凭印象做事):
1. mem0 filter 格式错 2 次 (`{AND: [...]}` 嵌套)
2. curl `-w "%{http_code}"` 仅看 HTTP 200, 误判 body 2049
3. cross-session-grep 6 件套**立前跳过** (立 case 后才跑, 顺序错)
4. Bash 调 `mcp__MiniMax__web_search` (误把 mcp 工具当 bash 命令)
5. v3 假设 "mcp 端点 snapshot 永久 / 跨 session 不行" — 错, 实测 mcp 进程 per-session respawn, 跨 session (新 session 启动) = mcp respawn = reload 立即生效

**§F.2 反模式沉淀**:

- ❌ `curl -s -o /dev/null -w "%{http_code}\n"` 单查 HTTP status (MiniMax 业务 status_code 嵌 body `base_resp.status_code`)
- ❌ 改 .claude.json mcpServers env 后误判 mcp reload 时机 (同 session 内部不 reload, 跨 session 自动 reload)
- ❌ 立 case 假设 "永久 / 硬约束" 跑 Read + 实测 (v3 §硬约束 段错位)
- ❌ 跨 protocol 链路 (mcp / HTTP / shell) 不三路并行 verify
- ❌ 修订 v3 原文代替 v4 增量修正 (违反 case library 不可变性)

**§F.3 changelog 更新** (4 file 同步):

| 文件 | 改动 | 详情 |
|------|------|------|
| `~/.claude/knowledge/cases/wiki/CASE-MINIMAX-KEY-ROTATION-V3-20260630.md` | 新立 | 195 lines / 4 失败路径 / 5 IF...THEN / 1 协议级反模式 |
| `~/.claude/knowledge/cases/wiki/CASE-MINIMAX-KEY-ROTATION-V4-20260630.md` | 新立 (v4 增量) | 244 lines / 4 维 evidence / 5 IF...THEN / 2 协议级反模式 / v3 §硬约束 修正 |
| `~/.claude/docs/adr/0026-curl-body-vs-status-code.md` | 新立 | 117 lines / HTTP 200 ≠ 业务成功 / MiniMax 5 字段 (0/2049/1004/1008/1033) |
| `~/.claude/docs/adr/0027-adr-namespace-resolution.md` | 新立 | 127 lines / 整数 slot 00NN + sub-slot 00NN-a/b (max 2) + 跳号 0014-0015 保留 |
| `~/.claude/CLAUDE.local.md §9` | 改 | mcp__MiniMax__web_search 行 v3 → v4 假设错位修正 |
| `~/.claude/CLAUDE.local.md §18` | 改 | verify-before-act 4 维 (file 存在 / path 正确 / 内容匹配 / 改动范围 ≤ 预期) — v3 v4 双重 verify |
| `~/.claude/rules/process.md §A.1.5` | 改 | 加 ADR-0026 反模式 + 外部 API call 必读 body 协议 |
| `~/.claude/memory/api-status-codes.md` | 新立 (adapter) | 150 lines / provider MiniMax / Anthropic / OpenAI / Gemini / OpenRouter |
| `~/.claude/memory/adr-namespace.md` | 新立 (adapter) | 113 lines / 整数 slot + sub-slot + 跳号 保留 |
| `~/.claude/decision-stream/2026-06-30-minimax-key-rotation-v3-abc-closure.md` | 新立 | 12 decisions / 4387 → 6406 bytes |
| `~/.claude/backups/.claude.json.pre-minimax-rotate-v3-1782814337.json` | 新立 (备份) | 48133 bytes (atomic edit 前) |

**§F.4 ADR 落地** (3 个 ADR 跨子仓 + 主仓):

- **ADR-0026 curl body vs status_code**: 跟 v3 case 同源, 4 case 同源沉淀 (CASE-MINIMAX-KEY-ROTATION-V3 + CASE-FORCE-ALL-SEARCH-REALITY-ALIGNMENT-20260624 + CASE-RICH-AUDIT-A.1.5-SCOPE-FACT-CHECK-20260627 + CASE-PROTECTED-PATH-EDIT-BYPASS-20260627)
- **ADR-0027 ADR 命名空间规约**: 跟 v2.6.47 frontmatter audit 同模式 (现状 grep 6 件套 必跑), 立新 ADR 必跑 `ls ~/.claude/docs/adr/ | sort | tail -10`
- **ADR-0028 (备选)**: mcp reload 协议沉淀 (v4 case §"立 mcp reload 协议 3 步" 待立), 跨 session lifecycle 强耦合

**§F.5 实战命令模板** (端到端 5 步, **本案例**完整流程):

```bash
# Step 1: 诊断 (直 curl 物理可达, 跑 mcp 工具)
curl -s -X POST "https://api.minimaxi.com/v1/text/chatcompletion_v2" \
  -H "Authorization: Bearer $OLD_KEY" \
  -d '{"model":"MiniMax-Text-01","messages":[{"role":"user","content":"ping"}]}' | head -c 300

# Step 2: 4 维 self-verify per CLAUDE.local.md §18 (改 .claude.json 前)
cp -p ~/.claude.json ~/.claude/backups/.claude.json.pre-minimax-rotate-vN-$(date +%s).json
python3 -c "import json, pathlib; p=pathlib.Path.home()/'.claude.json'; d=json.loads(p.read_text()); d['mcpServers']['MiniMax']['env']['MINIMAX_API_KEY']='$NEW_KEY'; t=p.with_suffix('.tmp'); t.write_text(json.dumps(d,indent=2)); t.rename(p)"

# Step 3: 验证 (直 curl 物理可达, 不依赖 mcp 协议)
curl -s -X POST "https://api.minimaxi.com/v1/text/chatcompletion_v2" \
  -H "Authorization: Bearer $NEW_KEY" \
  -d '{"model":"MiniMax-Text-01","messages":[{"role":"user","content":"ping"}]}' | head -c 200

# Step 4: 立 case + ADR + cross-file sync (走 PR + worktree, per §11)
git -C "$HOME/.claude" worktree add "$HOME/.claude/.worktrees/2026-06-30-minimax-key-rotation-vN" -b feat/minimax-key-rotation-vN main
# ... 改 file + commit + push + gh pr create ...

# Step 5: decision-stream 落地 (per calm-flow §4 schema)
echo "decision-stream file 落地 (12 decisions, per calm-flow §4)"
```

**§F.6 反模式** (本案例新增 5 类, 跟 v2.6.43 跨期沉淀):

- ❌ 误把 mcp 端点 "snapshot 永久" 假设写进 case (跟 v3 假设错位同源)
- ❌ 改 .claude.json mcpServers env 后, 误判 mcp reload 时机
- ❌ 立 case 假设 "永久 / 硬约束" 跑 Read + 实测 (v3 §硬约束 段错位)
- ❌ 跨 protocol 链路 (mcp / HTTP / shell) 不三路并行 verify
- ❌ 修订 v3 原文代替 v4 增量修正 (违反 case library 不可变性)

**§F.7 完整流程图** (本案例 + 跨 2 session 演进):

```
Session A (v3 立, 22:30 PT)
  ├─ mcp__MiniMax__web_search 返 2049 (v3 假设: snapshot 永久)
  ├─ 直 curl 老 key 返 2049 (server-side invalid)
  ├─ user 提供新 key → atomic edit .claude.json
  ├─ 立 CASE-MINIMAX-KEY-ROTATION-V3 (195 lines, 4 失败路径 + 5 IF...THEN)
  ├─ 立 ADR-0026 (117 lines, curl body vs status_code)
  ├─ 立 ADR-0027 (127 lines, namespace rule)
  ├─ 4 file sync: CLAUDE.local.md §9 + §18 + process.md §A.1.5 + memory 2 adapter
  ├─ 3 PR (PR #12 #13 #14) all merged
  └─ decision-stream 12 decisions 落地

[user session restart]

Session B (v4 实测, 23:10 PT)
  ├─ mcp__MiniMax__web_search 返 10 results (v4 实测: mcp respawn 自动 reload)
  ├─ 直 curl 新 key 返 200 + Pong! (跟 mcp 协议无关, 物理可达)
  ├─ mcp__anysearch__web_search 返 2 results (chardet 修复生效)
  ├─ 立 CASE-MINIMAX-KEY-ROTATION-V4 (244 lines, 4 维 evidence + 5 IF...THEN + 2 协议级反模式)
  ├─ CLAUDE.local.md §9 改 v3 假设错位修正
  ├─ PR #16 merged (commit 2b47161c → d66969ed)
  └─ 立 §F.4.1 本案例段 (v2.6.50 bump) ← 当前 step

[合并整套修复方法到 rich-audit skill]
```

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