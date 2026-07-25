---
name: disable-truth-sop
description: |
  反"假完成" SOP: per-edit verify 4 维 (jq assertion / readback / 禁 heuristic 当 ground truth /
  禁 git status 单源)。当排查 agent 谎报 done/all green、settings 改动验证、
  或需要写后必断言的场景时触发。
license: MIT
metadata:
  version: 1.0.0
  category: workflow
  author: mykcs
  migrated-from: ~/.claude/rules/disable-truth-sop.md (2026-07-25 rules 减重)
---

---
name: disable-truth-sop
description: 任何 enable/disable/配文件改动 (禁用 MCP / 启 auto mode / 加 allow rule / 改 enabledPlugins) 必走 4 维 disable-truth SOP：路径真实 + jq semantic assertion + mktemp + atomic mv 后 readback。禁止凭报告 / 凭假设 / 凭 jq 退出码当绿。3 CASE 同源 (2026-07-25 doctor cleanup execute false-green + filesystem 路径假设 + MiniMax mcpServers 写坏)。
metadata:
  type: rule
  category: self-verify
  status: enforced
  created: 2026-07-25
  related:
    - CASE-DOCTOR-CLEANUP-EXECUTE-FALSE-GREEN-20260725
    - claudecode-verify-before-act.md (4 维 self-verify 通用协议)
    - tooling.md §A.1 (settings.json SOP 5 件套 — backup/jq/validate/diff check/atomic commit)
    - tooling.md §A.6 #8 (改 env 字段 3 scope grep + 跨 session 实测 — 同根 30 天 5 次 case)
    - hook-payload-ground-truth.md (hook payload 必实测不假设)
---

# 规则: disable-truth SOP (禁 / 配改动必 jq `-e` 语义断言 + readback)

> **触发**: 任何对 settings.json / settings.local.json / .claude.json / .mcp.json / installed_plugins.json 的 enable / disable / 配置改动 (含但不限于 禁 skill / 禁 plugin / 禁 MCP / 提 defaultMode / 加 allow rule / 改 env var)
> **生效**: 改前后必走 4 维 disable-truth SOP，禁止 jq empty 退出 0 当绿、禁止凭 execute 段报告当过

## 1. 起源 case (3 同源, 2026-07-25)

| case | 表面症状 | 真因 (jq / 报告层谎报) | 误信来源 |
|------|---------|--------------------|---------|
| CASE-DOCTOR-CLEANUP-EXECUTE-FALSE-GREEN-20260725 | execute 段报"5 字段自检全过"但 jq 实测返 false | jq empty 退出 0 ≠ 期望值在场 | execute 段自检 grep 词 + 写入字段长度够 = "通过" |
| CASE-DOCTOR-CLEANUP-FILESYSTEM-PATH-ASSUMPTION-20260725 | filesystem 路径假设为 `~/.mcp.json`, 实测为空 `{}`, filesystem 根本未启用 | 体检摘要推断 + execute 段沿用同假设 | doctor 体检时未 grep 真值 |
| CASE-DOCTOR-CLEANUP-MINIMAX-MCP-MERGE-BROKEN-20260725 | jq `(. + {MiniMax: true})` merge 把 mcpServers.MiniMax object 内容清成 null | jq `+` 在已存在 key 上重写 = 清旧值 | 仅验 merge 退出码, 不验 mcpServers keys 数量与各 value type |

**共同反模式**: "jq 没报错 = 已生效" / "execute 报 PASS = 已生效" / "disable no-op 听起来稳 → 加双重保险" → 违反 claudecode-verify-before-act.md §1 反模式根因 (凭印象做事)

## 2. 触发条件 (4 类动作必跑 disable-truth SOP)

| # | 动作 | 真值源 | 失败现象 |
|---|------|--------|---------|
| 1 | 禁 / 启 skill | `settings.json.skillOverrides` | skill name 拼错 / 字段类型错 (string "off" vs boolean false) |
| 2 | 禁 / 启 plugin | `settings.json.enabledPlugins` + `installed_plugins.json` keys | plugin `<name>@<marketplace>` 拼错 (ecc vs everything-claude-code) |
| 3 | 禁 / 启 MCP server (user / project / local scope 任意) | `~/.claude.json` + `~/.mcp.json` + `.claude/settings.local.json.disabledMcpjsonServers` 三 scope grep | scope 路径错 + jq merge 写坏 mcpServers 真值 |
| 4 | 改 permissions.defaultMode / permissions.allow | `settings.json` + `.claude/settings.local.json` (per-project) | type 错 (string vs enum) / 漏配 cascade 覆盖 |

## 3. 4 维 disable-truth SOP (必跑全)

### 维度 1: 路径真实 (改前 grep 找真 path)

```bash
# 改前必跑：列真实配置所在文件 + 内容
grep -rli "<name>" ~/.claude/ 2>/dev/null
echo "--- 真值 ---"
jq '.mcpServers | keys' ~/.claude.json 2>/dev/null
jq '.mcpServers | keys' ~/.mcp.json 2>/dev/null
jq '.enabledPlugins | keys' ~/.claude/settings.json
jq '.skillOverrides | keys' ~/.claude/settings.json 2>/dev/null
```

**判定**: grep 0 hit → 该 key 根本没启用，**禁止凭空 jq 加 disabledMcpServers 等做 no-op** (per CASE-FILESYSTEM-20260725)。

### 维度 2: jq semantic assertion (改后必 `-e`)

```bash
# 任何 disable / enable 改完必跑 jq -e 实测期望值在位 + 类型对
jq -e '.enabledPlugins["everything-claude-code@everything-claude-code"] == false' settings.json
jq -e '.skillOverrides["algorithmic-art"] == "off"' settings.json
jq -e '.permissions.defaultMode == "auto"' settings.json
jq -e '.disabledMcpServers.MiniMax == true' .claude.json
jq -e '.projects["/Users/myk"].disabledMcpServers | index("filesystem") != null' .claude.json

# 反例: jq empty / jq . permissions.allow|length 都验的是结构存在 ≠ 期望值在场
# ✅ 必跑 jq -e '期望 == 实测', 失败 false 立即 STOP
```

### 维度 3: mktemp + jq --slurpfile 合并 (改前准备)

```bash
TS=$(date -u +%Y%m%d-%H%M%S)
cp ~/.claude/settings.json ~/.claude/settings.json.backup.disabletruth-${TS}
mktemp /tmp/st_disabletruth.XXXXXX.json
# 想要的 final state 写 mktemp 文件（不是 echo 拼 shell arg）
jq -n '{"enabledPlugins": {...}}' > /tmp/st_disabletruth.XXXXXX.json
jq --slurpfile n /tmp/st_disabletruth.XXXXXX.json \
   '.enabledPlugins = $n[0].enabledPlugins' \
   settings.json > /tmp/settings.merged.XXXXXX.json
jq empty /tmp/settings.merged.XXXXXX.json && echo "VALID"
```

### 维度 4: atomic mv + jq readback (改后 read 真值)

```bash
mv /tmp/settings.merged.XXXXXX.json settings.json
# 必跑 readback 不依赖写入时 jq 退出码
jq -e '<期望>' settings.json   # 维度 2 完整重跑
# 关键: 改动是否污染邻居 key
jq 'keys' settings.json        # 看原本 keys 还在不在
jq '.enabledPlugins | keys | length' settings.json  # 数量级 sanity
```

## 4. 5 IF...THEN 规则

1. **IF** 任何 disable / enable / addPermission 改动 **THEN** 必跑 4 维 SOP (路径真实 + jq assertion + mktemp + readback)
2. **IF** grep 找不到真值源 **THEN** 立即 STOP，**禁止** jq 加 disabled* 字段做 no-op (反例: filesystem 不存在却被双重保险)
3. **IF** jq `+` merge 操作 enable/disable map **THEN** 先 `setpath / with_entries` 精确路径改，**禁**用 `(. + {k: v})` 在已存在 key 上重写 (反例: MiniMax mcpServers object 被清成 null)
4. **IF** execute 段报告"全部 PASS"但读回 jq 返 false **THEN** 立即 STOP 主进程 commit + 抓 execute 段 transcript journal 重独立断言 (反例: execute 段 5 字段自检全绿但 jq 实测 2/6 假绿)
5. **IF** 改动跨 3 文件 + plugin key + mcpServers key 同步 **THEN** 跑前必先 `jq 'keys' <每个 file>` 列 ground truth，改后必 jq '-e' 逐字段断言

## 5. 7 协议级反模式 (永久失效)

1. ❌ "jq empty 退出 0 = 已生效" (违反 jq semantic assertion 维度 2)
2. ❌ "execute 段报 PASS = 已生效" (违反 readback 维度 4)
3. ❌ "grep 找不到 = 应该禁用 + 加字段防漏" (违反路径真实维度 1 + no-op 反模式)
4. ❌ "jq `(. + {k: v})` 合并 = 安全" (破坏已存在 key 真值，违反维度 3 + mktemp)
5. ❌ "settings-sop 5 件套跑过 = 已生效" (差 jq semantic assertion 这一步)
6. ❌ "plugin key 错位但对象 value = false 是对的" (错 key 不影响目标 plugin，等于没禁)
7. ❌ "smart-push 报 '无有效改动跳过' = 不需要 push" (smart-push heuristic ≠ 你的 ground truth)

## 6. 联动 (cross-references)

- `~/.claude/rules/claudecode-verify-before-act.md` §3 4 维 self-verify (通用协议, disable-truth 是其 settings 维度特化)
- `~/.claude/rules/tooling.md` §A.1 settings.json SOP 5 件套 (backup + jq + validate + diff check + atomic commit)
- `~/.claude/rules/tooling.md` §A.6 #8 改 env 字段 3 scope grep (同根 30 天 5 次 case, 跟 MiniMax 同源)
- `~/.claude/rules/hook-payload-ground-truth.md` (hook payload 必实测, 同 ground truth 哲学)
- `~/.claude/knowledge/cases/wiki/CASE-DOCTOR-CLEANUP-EXECUTE-FALSE-GREEN-20260725.md` (本 rule 起源 case)
- `~/.claude/knowledge/cases/wiki/CASE-MINIMAX-PAYGO-FALSE-REMOVAL-20260721.md` (30 天前同源, MINIMAX_PAYGO_API_KEY 字段误删)
- `~/.claude/knowledge/cases/wiki/CASE-SETTINGS-AUTH-401-WRITE-RULE-20260721.md` (settings.json 写保护硬约束)
- `~/.claude/docs/adr/0081-disable-truth-sop.md` (本 rule ADR, 待立)

## 7. 历史 record

- **2026-07-25 v1.0 立**: per CASE-DOCTOR-CLEANUP-EXECUTE-FALSE-GREEN-20260725, 3 同源 case 硬化。claudecode-verify-before-act 通用协议基础上加 settings 维度特化：4 维 SOP (路径真实 + jq `-e` 语义断言 + mktemp + readback) + 7 反模式永久失效。联动 CASE-MINIMAX-PAYGO-FALSE-REMOVAL-20260721 (30 天同源第 5 次触发 record-case §9 升级阈值) + ADR-0081 (整数 slot 0081 AVAILABLE per `ls ~/.claude/docs/adr/ | sort | tail -1` 验证)。

