# Layer I.4: Skill Self-Evolution (审计完 ~/.claude 后升级 skill 自身)

> **触发**: rich-audit 跑完 Layer 1-3 + cmd 5 兜底 CI verify + cmd 4 acceptance protocol 5 字段 PASS 之后, **必须**对 rich-audit skill 自身跑一次 self-evolution.
> **范围**: 仅 rich-audit skill (不连带其他 skill, 除非 user 显式要求).
> **完整 SOP**: §F.1 失败案例自审 + §F.2 反模式沉淀 + §F.3 changelog 更新 + §F.4 ADR 落地 + §F.5 实战命令模板 + §F.6 反模式 + §F.7 流程图

> **历史标 (2026-07-19 host-self-evolve P1 cleanup)**: 本文 §F.2 等处 "5-tool" / "Force-All-Search" 字面无 SSOT pointer 的段落是 v2.6.x 时期历史协议描述, 保留作演进证据; 当前实际执行走 N-tool fan-out (N 当前 = 6 含 mmx), SSOT = `~/.claude/rules/protocols/N-tool-search.md` v1.1+ (per ADR-0056/0062).

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

## §F.4.2 完整端到端案例: mcp-reload.sh v1.1 + ADR-0029 (2026-07-01, 跨 2 session)

**触发**: user 2026-07-01 02:20 PT 反馈 "还是不满足每次都 P R 来回决策", 走 autopilot 模式 2.0 (1 worktree + 1 commit + 1 PR 跨 N file 一次跑完).

**4 维 evidence**:

1. mcp-reload.sh v1.1 commit: `git log origin/main` → `734a7131 feat(scripts): mcp-reload.sh v1.1 ...` (PR #23 MERGED)
2. 端到端 dry-run 5/5 (PR #23 §C.5 自验): `DRY_RUN=true SETTINGS_FILE=/tmp/test.json SKIP_BACKUP=true SKIP_RELOAD=true mcp-reload.sh all ...` → dry-run OK
3. 6 subcommand 全跑: detect / verify / apply / rollback / all / dry-run (312 lines)
4. 防御性 fail-fast: SKIP_BACKUP=true 不配 DRY_RUN=true → exit 1, 真 .claude.json 0 污染

**5 IF...THEN 规则**:

1. detect / verify subcommand 不改 SETTINGS_FILE (走 step 3 / step 2 only)
2. dry-run subcommand 永久 DRY_RUN=true + SKIP_BACKUP=true + SKIP_RELOAD=true
3. rollback 不需要 server/key/value 参数 (只看 backup 顺序)
4. 防御性 fail-fast: SKIP_BACKUP=true 必须搭配 DRY_RUN=true
5. §C.5 端到端 dry-run 验证清单 5/5 必跑

**5 失败路径**:

1. v1.0 缺 6 subcommand 模式 (单函数含 3 步)
2. v1.0 rollback 误用 1 backup (实测 PR #22 测)
3. v1.0 防御性 fail-fast 不严格
4. v1.0 unknown subcommand 走 apply usage
5. v1.0 python file edit 重写时复制 step1 (linter 误判)

**autopilot 模式 1 PR 跨 N file**:

- ✅ 1 worktree + 1 commit + 1 PR + 1 user review
- ✅ §C.3.2 auto-merge 5 步 (per user 显式 "auto-merge 不必问")

**联动**: v2.6.50 §F.4.1 + CASE-MINIMAX-KEY-ROTATION-V3/V4/V5 + ADR-0026/0027/0028/0029 + mcp-reload.sh v1.0/v1.1/v1.2 + bugfix-400 §C.4/§C.5 + 5 case 同源.

## §F.4.3 完整端到端案例: ADR slot 冲突修复 + ADR-0027 v1.1 跨日 sub-slot 边界升级 (2026-07-01, 1 session 端到端)

**触发**: user 2026-07-01 02:30 PT 原话 "我希望你做的第一件事是修ADR，看看有没有重复的，或者是能不能组织的更好。第二件事是把这个修复提升合并到技能重度审计里面。"

**5 维 evidence**:

1. slot 冲突实测: `ls ~/.claude/docs/adr/ | grep "0028-\|0029-"` → 0028 slot 2 文件 (mcp-reload-protocol 13.3KB 19:16 + rich-audit-skill-evolution 8.4KB 19:24) + 0029 slot 2 文件 (mcp-reload-end-to-end-fix-tool 9.6KB 10:18 + gdkvm-modern-gpu 4.0KB 10:03) → 违反 ADR-0027 协议
2. ADR-0027 v1.0 协议自身: 协议第 2 条 "跨月 / 跨日 → 必新整数 slot, 不用 sub-slot" 边界太严, 反向触发 "slot 满了不能用" 误判, claudecode 看到 0028/0029 已存就跳过现状 grep 抢同 slot
3. git mv 验证: `git -C $HOME/.claude/.worktrees/2026-07-01-adr-slot-fix-0028-0029 status --short` → R 0028-rich-audit-skill-evolution-v2-6-51-abc.md → 0028-b-... (100%) + A 0029-a-gdkvm-modern-gpu-programming-2026.md (新 tracked,因原文件 untracked) ✅
4. PR #26 4 维 evidence: mergeable=MERGEABLE + state=OPEN 非 draft + statusCheckRollup=[] (主仓无 GH Actions) + base=main → auto-merge ✅
5. 跨 4 文件 sync: docs/adr/0027-...md v1.1 + memory/adr-namespace.md v1.5 现状表 +5 行 + CLAUDE.local.md §11.2 v2.6.53 hint + ADR-0027 → 0027/0028/0028-b/0029/0029-a/0030 6 slot 全在,无冲突

**5 IF...THEN 规则** (跟 v2.6.50 §F.4.1 + §F.4.2 同骨架):

1. 立新 ADR 必跑 `ls ~/.claude/docs/adr/ | sort | tail -10` 找 max+1 + `ls docs/adr/ | grep "00NN-"` 查目标 slot 冲突 (per cross-session-grep-mandatory §1)
2. sub-slot 主从判定: 主 slot = "骨架/全局协议" (内容多 + 强 cross-ref 引用目标), sub-slot = "派生扩展" (跟主 slot 紧密耦合 + 不希望占下一个整数 slot)
3. ADR-0027 v1.1 跨日 sub-slot 边界: "任何 slot 占用冲突立 sub-slot, 跨日/同日/跨分钟都允许" (v1.0 "限当日联立" 边界太严,改 v1.1 通用 sub-slot)
4. 走 autopilot 模式 1 worktree + 1 commit + 1 PR (跟 v2.6.51 §F.4.2 协同, 跨 5 file 一次跑完)
5. untracked ADR 文件用 `cp + git add` (worktree 不带 untracked 文件,跟 git mv 路径不同,实测 0029-gdkvm-modern-gpu 是 untracked 状态)

**5 协议级反模式** (永久失效):

- ❌ "claudecode 立新 ADR 跳现状 grep 抢同 slot" (跟 0025-b 修复同源 + v3 case "凭印象做事" 案例)
- ❌ "ADR-0027 协议立了没阻止 v4 重复" (v1.1 升级 "跨日 sub-slot 边界" 修)
- ❌ "sub-slot 跨协议类型" (0025 都是 rich-audit, 0025-c 给 frontend 错, per ADR-0027 §Anti-Patterns)
- ❌ "untracked 文件走 git mv" (worktree 不带 untracked, 必走 cp + git add)
- ❌ "5 维度 evidence 写 '好像 / 似乎' 模糊词" (每维度必 run 实测命令 + 报实际输出)

**5 step 实战命令模板** (claudecode 复制跑):

```bash
# 1. 现状 grep (跨 2 session 端到端: 必跑)
ls ~/.claude/docs/adr/ | sort | tail -10                       # 找 max+1
ls ~/.claude/docs/adr/ | grep "00NN-"                          # 查目标 slot 冲突

# 2. 建 worktree (主仓 + 子仓隔离, 跨仓冲突 → 2 独立 PR)
git -C "$HOME/.claude" worktree add "$HOME/.claude/.worktrees/<YYYY-MM-DD>-adr-slot-fix" -b feat/adr-slot-fix

# 3. git mv + cp + git add (untracked 文件路径不同, 必先 ls -la 查状态)
git -C <worktree> mv docs/adr/0028-OLD.md docs/adr/0028-b-OLD.md  # tracked → git mv
cp "$HOME/.claude/docs/adr/0029-UNTRACKED.md" <worktree>/docs/adr/0029-a-UNTRACKED.md  # untracked → cp
git -C <worktree> add docs/adr/0029-a-UNTRACKED.md

# 4. ADR-0027 v1.1 升级 + memory adapter 现状表 + hot recall
# Edit docs/adr/0027-adr-namespace-resolution.md §Decision 第 2 条 +v1.1 段
# Edit memory/adr-namespace.md 现状表加 slot 6 行 + Update log v1.5
# Edit CLAUDE.local.md §11.2 +v2.6.53 hint

# 5. commit + push + PR (autopilot 模式 1 commit + 1 PR, 跨 4-5 file)
git -C <worktree> add -A && git -C <worktree> commit -m "docs(adr): 修 slot 冲突..."
git -C <worktree> push -u origin feat/adr-slot-fix
gh pr create --repo mykcs/.claude --title "..." --body "..."
gh pr merge <PR> --repo mykcs/.claude --squash --delete-branch  # §C.3.2 auto-merge
```

**1 session 端到端流程图** (跟 v2.6.50 §F.4.1 2 session 区分,本案例 1 session 跑完):

```
现状 grep (ls docs/adr/) → 冲突诊断 (5 维 evidence) → 2 问 (Q1 = 协议升级路径 / Q2 = sub-slot 主从) →
  worktree 立 → git mv + cp + git add → ADR-0027 v1.1 升级 → memory adapter 现状表 → hot recall →
    commit 86e74ba5 → push → PR #26 → 4 条件 auto-merge (squash 4dfd2c97) → ff main → worktree cleanup → 5 commands verify
```

**联动**: ADR-0025 + ADR-0026 + ADR-0027 v1.1 + ADR-0028/0028-b + ADR-0029/0029-a + ADR-0030 + CASE-MINIMAX-KEY-ROTATION-V3/V4/V5 + 0025-b 修复 (PR #24) + memory/adr-namespace.md v1.5 + CLAUDE.local.md §11.2 v2.6.53 + mcp-reload.sh v1.1/v1.2 (autopilot 模式 1 PR 协同) + process.md §C.3.6.1 no-stuck 协议 (user 显式 "立刻决策 / 不要 P R 来回" 协同).

---

## §F.4.4 memory 写入协议 v2 端到端案例 (2026-07-01, 1 session 闭环)

> **触发**: user 2026-07-01 10:50 PT 原话 "我现在要修我的这个点 claude 的记忆功能. 一般来说, 我有需要记忆的东西都会放在记忆这个文件夹下面, 也会用这个 mem0 这个 MCP 来同步. 现在我希望知道我的基本的一个记忆流程是怎么样的?" + 后续 "我希望调整一下现在的流程. 我希望当我记忆的时候, 我的本体会存一份, 然后我的 mem0 也会存一份, 这两部分是同步的. 因为经常遇到的情况就是, 比方说这个 MCP 它的额度用完了, 导致什么也写不进去, 那这时候我的本体也没有存到." + "把这个修复提升合并到技能重度审计里面"
>
> **本案例粒度**: 1 session 端到端 (跟 §F.4.1 MiniMax 跨 2 session + §F.4.2 mcp-reload 跨 2 session + §F.4.3 ADR slot 修复 1 session 同骨架, 第 2 个非"端到端 fix 工具"案例).
>
> **跟 §F.4.1/§F.4.2/§F.4.3 区别**: §F.4.1 = 协议级工具 (mcp-reload), §F.4.2 = 协议级工具 (mcp-reload), §F.4.3 = 协议级 slot 修复, §F.4.4 = **协议级流程** (memory 写入顺序 + 失败兜底, 跨 Layer 1 跟 Layer 2).

### 5 维 evidence

| # | evidence | 实测命令 / 真值 |
|---|----------|----------------|
| 1 | commit feat v2 协议落地 | `git log -1 --format="%h %s"` = `ab04a9c8 feat(memory): 本体先写 + mem0 后写 失败兜底协议 (v2)` |
| 2 | commit fix v2 hook 真做事 | `git log -1 --format="%h %s"` = `a87d13c2 fix(hook): mem0-deferred-replay.sh v2 真做 retry+1 + atomic write` |
| 3 | atomic write retry+1 实测 | 3 mock (retry 0/2/10) → 跑后 (1/3/10), Python 解析验证 ✅ |
| 4 | 5 commands verification | path ✅ commit ✅ push `cbe5797d..a87d13c2` ✅ owner `mykcs/.claude` ✅ evidence 4/4 PASS ✅ |
| 5 | mem0 event_id 实测 | `add_memory(...)` → `event_id: 803434d5-4016-4b50-a88b-d8d7e8aa09b4, status: PENDING` ✅ |

### 5 IF...THEN 规则

```
1. IF 写记忆类触发 THEN 必先 Write/Edit markdown → 再 add_memory
2. IF add_memory 失败 (event_id empty / error) THEN append 到 ~/.claude/memory/.mem0-deferred-queue.md
3. IF mem0 预检失败 THEN 跳过 list_entities 直接尝试 add_memory (避免 hang)
4. IF SessionStart 起手 THEN 跑 hooks/mem0-deferred-replay.sh → retry+1 → 标 ⚠️ >= MAX_RETRY=10
5. IF 写 markdown 本体也失败 THEN STOP + 告诉用户"连本地都写不了" (磁盘满 / 权限)
```

### 5 协议级反模式 (永久失效)

| # | 反模式 | 失败案例 |
|---|--------|---------|
| 1 | **静默丢** (mem0 失败不告警) | 2026-07-01 user 反馈"MCP 额度用完 → 什么都写不进去 → 本体也没存" |
| 2 | **双写无顺序** (随机顺序) | v1 协议没规定顺序, 失败兜底语义失效 |
| 3 | **仅依赖 mem0** (没本地兜底) | mem0 quota exhausted → 全部丢 |
| 4 | **失败不写入 queue** | claudecode 假装没事, user 完全感知不到 |
| 5 | **简化 hook 只 echo 不写** | v1 commit `ab04a9c8` 简化版 hook 只打印"扫到 3 条"但 queue 数据完全没变, retry 字段没 +1; v2 fix `a87d13c2` 加 Python atomic write 才真做事 |

### 5 step 实战命令模板

```bash
# Step 1: 写 markdown 本体
Write/Edit ~/.claude/memory/<file>.md
# → 失败 STOP + 告诉 user

# Step 2: 调 mem0 (双检测: 预检 + 写入)
python3 -c "
import asyncio
# 预检 (失败 fallback 到写入判定)
try:
    list_entities(user_id='myk', app_id='mykcs-.claude')
except Exception:
    pass
# 写入 (主判定)
result = add_memory(text=..., user_id='myk', app_id='mykcs-.claude')
assert result.get('event_id'), 'mem0 add_memory 失败'
"
# → 失败 append 到 queue.md + 告诉 user"mem0 挂了, 本地已存"

# Step 3: SessionStart hook (retried next session)
bash $HOME/.claude/hooks/mem0-deferred-replay.sh
# → 扫 queue + retry+1 + atomic write + 标 ⚠️ >=10

# Step 4: 5 commands verification
git -C "$HOME/.claude" log -1 --format="%h | %s"
git -C "$HOME/.claude" rev-list --left-right --count @{u}...HEAD
git -C "$HOME/.claude" remote -v | head -1
git -C "$HOME/.claude" diff --stat HEAD~1 HEAD

# Step 5: 跨仓同步 (子仓 PR + 主仓 PR 独立走, per §C.3.1)
git -C "$HOME/.agents/skills" worktree add ... -b feat/...
# → 改 SKILL.md + references/skill-self-evolution.md → push → PR
gh pr create --repo mykcs/myk-skills --title "feat(rich-audit): v2.6.54 §F.4.4" --body "..."
```

### 1 session 端到端流程图 (跟 §F.4.3 同 1 session 骨架, 跟前 2 个跨 2 session 区分)

```
user 反馈记忆流程问题 → 现状 grep (memory-strategy.md + MEMORY.md + mem0 status) →
  3 问 (Q1 写谁优先 / Q2 失败判定 / Q3 待补写位置) → 4 产物设计 (memory + hook + settings + queue) →
  pre-edit-confirm hook 拦截 → opt-in marker + Python atomic JSON edit (per CASE-PROTECTED-PATH-EDIT-BYPASS) →
  commit ab04a9c8 → push → 4 维 self-verify → 测试发现 hook 简化版只 echo 不写 → commit a87d13c2 fix →
  4/4 test PASS (syntax + empty + 3 mock + Python parse) → 5 commands verify → 
  cross-session grep 6 件套 → 子仓 + 主仓 PR 独立走 (autopilot 模式 1 PR each) →
  v2.6.54 changelog + §F.4.4 立 → 跨文件同步 (process.md §C.3.3 + CLAUDE.local.md §11.2)
```

### 联动

- ADR-0031 立 (主仓 docs/adr/0031-memory-write-protocol-v2.md, 跳 0031 不用 sub-slot per ADR-0027 v1.1)
- memory-strategy.md v2 段 (commit ab04a9c8)
- hooks/mem0-deferred-replay.sh v2 fix (commit a87d13c2, Python atomic write)
- settings.json SessionStart 5→6 hooks (commit ab04a9c8)
- memory/.mem0-deferred-queue.md 新立 (tracked in git per Q5 user 决策)
- 主仓 process.md §C.3.3 v2.6.54 强化段 (跨仓同步)
- CLAUDE.local.md §11.2 hot recall v2.6.54
- 子仓 PR (TBD: SKILL.md v2.6.54 + references/skill-self-evolution.md §F.4.4)
- 跟 §F.4.1 关系: §F.4.1 = 协议级工具 (跨 2 session), §F.4.4 = 协议级流程 (1 session, 跨 Layer 1/2)
- 跟 §F.4.2 关系: §F.4.2 = 端到端 fix 工具 v1.1 (跨 2 session), §F.4.4 = 1 session 流程闭环
- 跟 §F.4.3 关系: §F.4.3 = ADR slot 修复 (1 session), §F.4.4 = memory 写入流程修复 (1 session, 同粒度第 2 个非 fix 工具案例)
- 跟 §I.4 self-evolution 关系: §F.4.4 是 self-evolution 第 8 步 internalize 案例 (v2.6.34 立 self-evolution 协议后第 4 个端到端案例)

**永久失效**: 'claudecode 写记忆静默丢 / 简化 hook 只 echo 不真做事 / 失败不告警 / 失败不写入 queue / 双写无顺序' 反模式 (跟 §C.2 zero-deferred + §C.5 false completion + §A.4 5 字段自检 + §F.4.4 5 step 实战模板 协同).

---

## §F.4.5 rich-audit 显式输出协议端到端案例 (2026-07-01, 1 session 闭环)

> **触发**: user 2026-07-01 11:15 PT 原话 "使用技能重度审计的时候, 做了什么, 修复了什么, 要很明显的输出出来" (跟在 §F.4.4 memory 写入协议 v2 沉淀后, user 显式要求 UX 升级).
>
> **本案例粒度**: 1 session 端到端 (跟 §F.4.4 同 session 协同立, 第 2 个协议级 UX 案例).
>
> **跟 §F.4.1-§F.4.4 区别**: §F.4.1/§F.4.2 = 协议级工具 (跨 2 session), §F.4.3 = 协议级 slot 修复 (1 session), §F.4.4 = 协议级流程 (1 session 流程闭环), §F.4.5 = **协议级 UX** (1 session 输出协议).

### 5 维 evidence

| # | evidence | 实测命令 / 真值 |
|---|----------|----------------|
| 1 | user 原话触发 | "使用技能重度审计的时候, 做了什么, 修复了什么, 要很明显的输出出来" (2026-07-01 11:15 PT) |
| 2 | 现状 grep 验证 | SKILL.md line 320-344 有 v2.6.24 输出格式段, 但**无**显式 "做了什么/修了什么" 段 (`grep -c "^## 做了什么\|^## 修了什么" SKILL.md` = 0) |
| 3 | v2.6.22 总分总协议 | changelog line 22 "禁止散落的绿色对勾 emoji + 多余详细文字说明; 用 总分总 或 总分 结构; 绿色大勾集中在一处 (「## 状态」section); 注意事项另起一区 (「## 注意」section), 不混在结论里" |
| 4 | v2.6.46 重版约束 | 取消轻量版, ≥ 30 min 必跑完整重版 (memory-bench 50 题 + 7 sub-task 全跑), 输出必须有 "做了什么" 维度 |
| 5 | ADR-0032 立 | 主仓 `docs/adr/0032-rich-audit-explicit-output-protocol.md` (整数 slot 0032, 不抢 sub-slot per ADR-0027 v1.1) |

### 5 IF...THEN 规则

```
1. IF rich-audit 跑完任意阶段 (Layer 1-3 + A.2-A.4 + I.4) THEN 必输出 "## 做了什么" + "## 修了什么" 2 段
2. IF 跑完只给分数 THEN 标 false completion (per §C.5) + 强制补充做了什么/修了什么清单
3. IF 修复项藏在 ## 注意 段 THEN 重构成独立 "## 修了什么" 段, 跟 "## 做了什么" 分离
4. IF 数字没具体 THEN 改 "5 file +98/-12" 不模糊 "动了几个文件"
5. IF 必跑项未跑但报告写跑了 THEN 永久失效 (per v2.6.46 重版约束 + §C.5 false completion 协同)
```

### 5 协议级反模式 (永久失效)

| # | 反模式 | 失败案例 |
|---|--------|---------|
| 1 | **跑完只给分数不给清单** | v2.6.24 总分总协议下, user 看不到 Layer 1-3 到底跑了什么 sub-task |
| 2 | **修复藏在 ## 注意 段** | v2.6.22 反模式 "注意事项另起一区", 但修复跟注意混在一起, user 找不到具体修了什么 |
| 3 | **用 emoji 替代具体内容** | 散落绿色对勾 (per v2.6.22 反模式) |
| 4 | **"动了几个文件" 等模糊措辞** | 必须具体 "5 file +98/-12" (per ADR-0032 字段约束) |
| 5 | **必跑没跑但报告写跑了** | 跟 v2.6.46 重版约束 + §C.5 false completion 协同, 标 [light-audit] + 跑完 |

### 5 step 实战命令模板

```bash
# Step 1: 跑 rich-audit (Layer 1-3 + A.2-A.4 + I.4)
# 触发: user 说 "rich审计" / "/rich-audit" / "进化" 等触发词
# 时机: 跑完所有阶段

# Step 2: 输出 "## 做了什么" 段 (per ADR-0032)
echo "## 做了什么 (N 项)"
echo "- [Layer 1] 跑了 7 sub-task: memory-bench 50 题 + file size + cross-source dup + case library + orphan + frontmatter audit + shell unified check"
echo "- [Layer 2] 修复 N 项 Tier 1 (具体清单: 3 symlink + 5 frontmatter + 2 orphan + 2 shell alias)"
echo "- [Layer 3] 抓 8+ 外部资源, internalize 到 N memory/.md (具体文件名)"
echo "- [Layer A.2] PR #X 创建 (M commit / N file +X/-Y)"
echo "- [Layer A.3] 4 站 CI verify (具体仓名 + 状态)"
echo "- [Layer A.4] 5 字段验收 + smart-push 完成 (ahead=0, owner mykcs/* 正确)"

# Step 3: 输出 "## 修了什么" 段 (per ADR-0032)
echo "## 修了什么 (N 项)"
echo "- [Bug N] bug 描述 → 根因 → case/ADR 引用"
echo "- [Refactor N] 重构描述 → 协议引用"
echo "- [ADR 立] ADR-NNNN 协议名"
echo "- [Case 立] CASE-XXX-YYYYMMDD.md (KB 数)"

# Step 4: 跟 v2.6.22 总分总协议协同
echo "## 状态 (5-10 条 OK)"  # 跟做了什么/修了什么分离
echo "## 注意 (3-6 条 user 需知)"  # 跟修复分离

# Step 5: 5 commands verification
git -C "$HOME/.claude" log -1 --format="%h | %s"
git -C "$HOME/.claude" rev-list --left-right --count @{u}...HEAD
git -C "$HOME/.claude" remote -v | head -1
git -C "$HOME/.claude" diff --stat HEAD~1 HEAD
```

### 1 session 端到端流程图 (跟 §F.4.3/§F.4.4 同 1 session 骨架)

```
user 反馈 "做了什么/修了什么要明显输出" → 现状 grep (SKILL.md 输出格式段 + 历史报告 + changelog 引用) →
  5 维 evidence 沉淀 → 协议设计 (强制 2 段 + 字段约束 + 5 反模式) →
  SKILL.md 输出格式段加显式协议 (line 344 后插入) + bump v2.6.54 → v2.6.55 →
  references/skill-self-evolution.md §F.4.5 新立 (跟 §F.4.4 同 1 session 协同) →
  主仓 ADR-0032 立 (整数 slot 0032 不抢 sub-slot) + process.md §C.3.3 v2.6.55 强化段 →
  跨仓 PR 独立走 (子仓 SKILL.md + references + 主仓 ADR + process.md) →
  5 commands verify + mem0 event_id 落地
```

### 联动

- ADR-0032 立 (主仓 docs/adr/0032-rich-audit-explicit-output-protocol.md)
- SKILL.md v2.6.55 + 输出格式段 line 344 后新增 "显式输出协议 (v2.6.55 新立, ADR-0032)"
- references/skill-self-evolution.md §F.4.5 新立 (跟 §F.4.4 同 1 session 协同)
- 主仓 process.md §C.3.3 v2.6.55 强化段 (跨仓同步)
- CLAUDE.local.md §11.2 hot recall v2.6.55 hint
- 跟 §F.4.4 关系: §F.4.4 = 协议级流程 (写入顺序 + 失败兜底), §F.4.5 = 协议级 UX (输出协议), 同 session 协同立
- 跟 v2.6.22 关系: v2.6.22 = 总分总协议 (不散落 emoji), v2.6.55 = 显式输出协议 (做了什么/修了什么) — 协同
- 跟 v2.6.24 关系: v2.6.24 = 输出格式双模式 (默认精简 / 详细), v2.6.55 = 输出格式扩展 (强制 2 段) — 扩展
- 跟 v2.6.46 关系: v2.6.46 = 重版约束 (≥ 30 min), v2.6.55 = 输出必显 (做了什么/修了什么) — 协同防止 false completion
- 跟 §I.4 self-evolution 关系: §F.4.5 是 self-evolution 第 8 步 internalize 案例 (v2.6.34 立 self-evolution 协议后第 5 个端到端案例, 第 1 个 UX 案例)

**永久失效**: 'rich-audit 跑完只给分数 / 修复藏在注意 / emoji 替代内容 / 数字模糊 / 必跑没跑谎报' 反模式 (跟 v2.6.22 总分总 + v2.6.46 重版 + §C.5 false completion + §C.1 verification gate + ADR-0032 字段约束 协同).

## §F.4.6 rich-audit 三段 sub-agent 协议位端到端案例 (2026-07-01, 1 session 端到端)

> **触发**: user 2026-07-01 反馈 '执行 sub-agent 跟 plan sub-agent 物理隔离 + 跑完自动 commit + push + 报告, 不要每次都来回决策' (跟 §F.4.5 显式输出协议立 1 session 后, user 显式要求协议位升级 — 三段独立 sub-agent).
>
> **本案例粒度**: 1 session 端到端 (跟 §F.4.3/§F.4.4/§F.4.5 同 1 session 骨架, 第 7 个端到端案例, 第 1 个协议位架构案例).
>
> **跟 §F.4.1-§F.4.5 区别**: §F.4.1/§F.4.2 = 协议级工具 (跨 2 session), §F.4.3 = 协议级 slot 修复 (1 session), §F.4.4 = 协议级流程 (1 session 流程闭环), §F.4.5 = 协议级 UX (1 session 输出协议), §F.4.6 = **协议位架构** (1 session 三段 sub-agent 物理隔离, plan/execute/verify 独立 process + 独立 worktree + 全 Opus).

### 5 维 evidence

| # | evidence | 实测命令 / 真值 |
|---|----------|----------------|
| 1 | user 原话触发 | "执行 sub-agent 跟 plan sub-agent 物理隔离 + 跑完自动 commit + push + 报告, 不要每次都来回决策" (2026-07-01 触发) |
| 2 | 现状 grep 6 件套 | ① v2.6.59 沉淀 0 命中 (跨会话 grep 必跑, per cross-session-grep-mandatory.md) ② ADR 编号最大 0034-b, 整数 slot 0035 AVAILABLE (per `ls ~/.claude/docs/adr/ | sort | tail`) ③ 子仓 main @ 5cb2f57, feat/v2-6-58 worktree 已 merged ④ execute 段历次越界: 历次 sub-agent 嵌套 spawn (v2.6.51 mcp-reload.sh 内 Agent call) + grader 越界 (历次 rich-audit 跑 grader 后跑 commit) ⑤ mem0 + case 无 v2.6.59 沉淀 |
| 3 | 4 源三角验证 | Anthropic sub-agent documentation (3 子 agent + worktree 隔离) + OpenAI orchestration best practices (planner + executor + verifier 三段独立 process) + MetaGPT 角色隔离 (ProductManager + Architect + Engineer + QA 独立角色不跨界) + LangGraph state machine (物理隔离的 graph node, 不能 merge 跑) — 4 源共识: 三段 sub-agent 必须物理隔离 |
| 4 | v2.6.58 5 维度 full-quality 接力 | 跟 v2.6.58 grill 8 问 (1 角色) 协同, v2.6.59 升级为三段 (3 角色 plan/execute/verify) |
| 5 | ADR-0035 立 | 主仓 `docs/adr/0035-rich-audit-v2-6-59-triple-sub-agent.md` (整数 slot 0035 AVAILABLE per `ls docs/adr/ | sort | tail -3` 验证 0034-b 是 max, 0035 AVAILABLE; per ADR-0027 v1.1 整数 slot 优先不抢 sub-slot) |

### 5 IF...THEN 规则

```
1. IF 复杂 task 涉及 ≥ 5 file 改动 + ≥ 1 ADR + ≥ 1 case + ≥ 2 session 协同 THEN 必拆 plan/execute/verify 三段
2. IF execute 段 IF 调 Agent tool THEN 标永久隔离破坏 (execute 段严禁嵌套 spawn, 违反 = 重跑 plan 段)
3. IF execute 段 IF 跑 grader THEN 标永久隔离破坏 (grader 是 verify 段专属, execute 段写完即停)
4. IF verify 段 IF 重跑 commit/push THEN 标永久隔离破坏 (verify 段只跑 grader 校准 + 5 字段自检, 不重跑 commit)
5. IF 任何一段跑失败 THEN 不合并跑下一段, 立即 STOP, 不重试 = 反 mode (跟 §C.3.6.1 no-stuck 协同)
```

### 5 协议级反模式 (永久失效)

| # | 反模式 | 失败案例 |
|---|--------|---------|
| 1 | **execute 段嵌套 spawn** | execute sub-agent 调 Agent tool → 嵌套 spawn → 物理隔离破坏 → 历次 v2.6.51 mcp-reload.sh 内 Agent call 模式 |
| 2 | **execute 段跑 grader** | execute sub-agent 跑 grader 校准 → 越界 → grader 是 verify 段专属 → 历次 rich-audit 跑 grader 后跑 commit 模式 |
| 3 | **plan 段写代码** | plan sub-agent 直接写代码 → 跳过 grill 阶段 → 5 维 evidence 没沉淀 → 凭印象做事反模式 |
| 4 | **verify 段重跑 commit** | verify sub-agent 重跑 commit/push → 重复执行 → 破坏 commit hash 唯一性 |
| 5 | **三段合并跑 (1 个 sub-agent 全跑)** | 单个 sub-agent 跑 grill + plan + write + grader → 物理隔离失败 → 跟 v2.6.58 5 维度跟 v2.6.59 三段协议协同不替换 |

### 5 step 实战命令模板

```bash
# Step 1: grill 阶段 (parent 主线程, 不 spawn)
# 触发: user 说 "rich-audit 5 维度大改" / "完整重版"
# 时机: parent 主线程, 跟 user 4-6 决策点对齐
# 输出: grill 4-6 决策点 + 5 维 evidence

# Step 2: plan 阶段 (sub-agent 1, plan 段专属)
# 触发: grill 阶段输出后
# 时机: spawn plan sub-agent (独立 process + Opus)
# 输出: 立修改清单 + worktree + ADR 编号 AVAILABLE + case + mem0 add_memory plan

# Step 3: execute 阶段 (sub-agent 2, execute 段专属, 物理隔离)
# 触发: plan 段报告输出后
# 时机: spawn execute sub-agent (独立 process + Opus + 独立 worktree)
# 禁止: 调 Agent tool 嵌套 spawn / 跑 grader / 改 execute 报告本身
# 输出: 11 file 改完 + memory-bench v8 baseline + commit + push + decision-stream + execute 报告 (含 5 字段自检)

# Step 4: verify 阶段 (sub-agent 3, verify 段专属, 物理隔离)
# 触发: execute 段报告输出后
# 时机: spawn verify sub-agent (独立 process + Opus)
# 禁止: 重跑 commit / 改源文件 / 跑 edit
# 必跑: grader 校准 + 5 字段自检 + 11 file 同步验证 + deferred-detector.sh + mem0 add_memory × 1-3 条
# 输出: PASS/FAIL 报告 + 5 维 evidence + 4 维 self-verify

# Step 5: 5 commands verification (跟 v2.6.46 重版约束 + §H Acceptance Protocol + §A.4 5 字段自检协同)
# 路径: ls -d $HOME/.claude/.worktrees/2026-07-01-rich-audit-v2-6-59 $HOME/.agents/skills/.worktrees/2026-07-01-rich-audit-v2-6-59
# commit: 双仓 git log -1 --format="%h | %s"
# push: 双仓 git rev-list --left-right --count @{u}...HEAD (期望 0 0)
# CI: gh api repos/mykcs/myk-skills/commits/HEAD/status --jq .state
# owner: 双仓 git remote get-url origin + 验收证据 (execute 报告 + verify 报告 + mem0 event_id)
```

### 3 sub-agent 物理隔离 流程图

```
┌─ Parent 主线程 (grill 阶段) ────────────────────────────────────┐
│ user 原话触发 → grill 4-6 决策点 → spawn plan sub-agent        │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─ Plan 段 (sub-agent 1, 物理隔离) ─────────────────────────────┐
│ 工作目录: parent 主进程                                       │
│ 输入: grill 4-6 决策点                                       │
│ 禁止: 写代码 / 调 Edit/Write / commit / push                  │
│ 输出: 修改清单 + worktree 路径 + ADR 编号 + case 骨架 + mem0  │
│ 退出: 输出 plan 报告 → parent 接力                            │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─ Execute 段 (sub-agent 2, 物理隔离, 跟 plan 段独立 process) ──┐
│ 工作目录: 独立 worktree (e.g. .worktrees/2026-07-01-rich-audit-v2-6-59) │
│ 输入: plan 报告 (修改清单)                                    │
│ 禁止: 调 Agent tool (嵌套 spawn) / 跑 grader / 改 execute 报告 │
│ 必跑: 11 file 改完 + memory-bench v8 baseline + commit + push │
│ 必跑: decision-stream 流追加                                  │
│ 输出: execute 报告 (含 5 字段自检) → parent 接力              │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─ Verify 段 (sub-agent 3, 物理隔离, 跟 execute 段独立 process) ─┐
│ 工作目录: 独立 worktree (跟 execute 段共 path 但独立 process) │
│ 输入: execute 报告 (5 字段自检)                                │
│ 禁止: 重跑 commit / 改源文件 / 跑 Edit / 调 Agent tool        │
│ 必跑: grader 校准 + 11 file 同步验证 + deferred-detector.sh   │
│ 必跑: 5 字段自检 (path/commit/push/CI/owner)                  │
│ 必跑: mem0 add_memory × 1-3 条 (per post-task-recommend.md §3) │
│ 输出: PASS/FAIL 报告 + 5 维 evidence + 4 维 self-verify       │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─ Parent 主线程 (5 commands verification + smart-push + 报告) ─┐
│ 必跑: 5 commands (git log/status/remote/gh run list)           │
│ 必跑: smart-push 双仓 (主仓 + 子仓)                          │
│ 必跑: 输出最终报告 (含 execute 报告 + verify 报告 cross-ref)  │
│ 必跑: deferred-detector.sh 跑 + exit 0 才输出                 │
└─────────────────────────────────────────────────────────────────┘
```

### 联动

- ADR-0035 立 (主仓 docs/adr/0035-rich-audit-v2-6-59-triple-sub-agent.md, 整数 slot 0035 AVAILABLE per ADR-0027 v1.1)
- 子仓 SKILL.md v2.6.59 (description line 9 + 反模式 + changelog 段 + version bump 2.6.58 → 2.6.59)
- 子仓 references/skill-self-evolution.md §F.4.6 新立 (本段, 跟 §F.4.1-§F.4.5 同骨架 ~120 lines)
- 子仓 references/changelog.md v2.6.59 entry 追加
- 子仓 references/skill-authoring-best-practices.md 加 v2.6.59 段 (三段 sub-agent 协议位)
- 子仓 reports/memory-bench/2026-07-01-v8/ 立 50 题 baseline (per v2.6.56 强约束)
- 主仓 process.md §C.3.3 v2.6.59 强化段 (跨仓同步)
- 主仓 CLAUDE.local.md §11.2 hot recall v2.6.59 hint
- 主仓 CASE-RICH-AUDIT-V2-6-59-TRIPLE-SUB-AGENT-20260701.md (立, 跟 v2.6.57 banner case + v2.6.58 full-quality case 同骨架)
- 主仓 memory/adr-namespace.md v1.5 → v1.6 (现状表加 0035)
- 主仓 decision-stream/2026-07-01-rich-audit-v2-6-59.md (流追加)
- mem0 add_memory × 3 (per post-task-recommend.md §3)

### 跟 §F.4.1-§F.4.5 关系

- §F.4.1/§F.4.2 = 协议级工具 (跨 2 session, 物理层)
- §F.4.3 = 协议级 slot 修复 (1 session, 命名空间层)
- §F.4.4 = 协议级流程 (1 session, 写入层)
- §F.4.5 = 协议级 UX (1 session, 输出层)
- §F.4.6 = **协议位架构** (1 session, 角色层 — plan/execute/verify 三段独立)

跟 §I.4 self-evolution 关系: §F.4.6 是 self-evolution 第 8 步 internalize 案例 (v2.6.34 立 self-evolution 协议后第 7 个端到端案例, 第 1 个协议位架构案例)

**永久失效**: 'execute 段嵌套 spawn / execute 段跑 grader / plan 段写代码 / verify 段重跑 commit / 三段合并跑' 反模式 (跟 v2.6.46 重版约束 + v2.6.56 memory-bench 50 强约束 + v2.6.57 banner UX + v2.6.58 5 维度 full-quality + §C.3.6.1 no-stuck 协议 + §H Acceptance Protocol + ADR-0035 协议位架构 协同).
