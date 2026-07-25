---
name: plugin-hook-drift-pre-check
description: |
  安装 / 卸载 / 更新 Claude Code plugin 之前的 drift 预检 SOP: enabledPlugins 状态核对、
  registry 滞后检测、worktree dirty block、4 维体检。当用户操作 plugin (install/uninstall/update)、
  或怀疑 plugin 状态漂移 (enabled false 误判) 时触发。
license: MIT
metadata:
  version: 2.2.0
  category: workflow
  author: mykcs
  migrated-from: ~/.claude/rules/plugin-hook-drift-pre-check.md (2026-07-25 rules 减重)
---

# 规则: plugin hook drift pre-check（plugin 升级跨大版本必跑 settings.json hook path 体检）

> **触发来源**: CASE-PRECOMPACT-HOOK-DEAD-PATH-PLUGIN-MISMATCH-20260716 (2026-07-16 立, /compact 被死链 hook 阻断) + CASE-MEM0-WRAPPER-PATH-STALE-20260624 (30 天前同类, threshold 满足 record-case §9 "≥2 次重复必升级为硬约束")
> **生效**: 任何 plugin uninstall / 大版本升级 / Claude Code 命令 hook 报错 / settings.json 改动 之前必跑体检
> **强制执行**: 暂不立 hook (per §C.3.6.1 no-stuck), 走 claudecode 自检 + §A.1 settings.json SOP 5 件套兜底

## 1. 触发条件 (5 类, any-of 命中 → 跑体检)

| # | 触发 | 检查方法 | 来源协议 |
|---|------|---------|---------|
| 1 | **plugin uninstall** | `cat ~/.claude/plugins/installed_plugins.json` 看是否少 entry | Claude Code plugin 设计缺陷 |
| 2 | **plugin 大版本升级** (跨 minor/major) | 比对 `installed_plugins.json` installPath version 段 | 同上 |
| 3 | **Claude Code 命令失败 + 错误信息含 hook name** (PreCompact/SessionStart/Stop 等) | `jq '.hooks.<event>' ~/.claude/settings.json` 列命令路径 | 本 case |
| 4 | **cache 目录仅含 `.disabled` 占位** | `ls ~/.claude/plugins/cache/<plugin>/` | CASE-MEM0-SLOW-HOOK-SEAL-20260715 |
| 5 | **settings.json 改动涉及 hooks 字段** | 改前必跑 §A.1 SOP + 本规则体检 | tooling §A.1 |

## 2. 体检 SOP (4 步, 必跑全)

### Step 1: 列出所有 hook event + 各自命令路径

```bash
jq '.hooks | keys[]' ~/.claude/settings.json
# 期望输出: "PreToolUse" / "PostToolUse" / "SessionStart" / "PreCompact" / ...

jq '.hooks.<event>[].command' ~/.claude/settings.json
# 对每个 event 列所有 hook command 字符串
```

### Step 2: 验证每条 command 路径真实存在

```bash
# 解析 command 字符串里的脚本路径 (jq + grep)
jq -r '.hooks.PreCompact[] | .command' ~/.claude/settings.json \
  | grep -oE '/[^\s]+\.(py|sh|js)' \
  | while read p; do
      test -f "$p" && echo "✅ $p" || echo "❌ DEAD-LINK: $p"
    done
```

### Step 3: 对比 installed_plugins.json 看 installPath 跟 hook path 是否一致

```bash
# 3.1 列出 installed plugin
jq -r '.plugins[] | "\(.name)@\(.version) -> \(.installPath)"' \
  ~/.claude/plugins/installed_plugins.json

# 3.2 比对 hook path 跟 installPath 是否同一 plugin/version
# 例: hook path 含 `mem0/0.2.0/`, installPath 含 `mem0/0.2.11/` → drift
```

### Step 4: 4 维结论判定 (drift vs in-sync)

| 维度 | in-sync 标志 | drift 标志 (BLOCKED) |
|------|------------|---------------------|
| 1. 路径存在 | `test -f <path>` ✅ | `❌ DEAD-LINK` |
| 2. version 一致 | hook path version == installed version | hook path version != installed version |
| 3. cache 目录 | `<plugin>/<version>/` 存在 | 仅 `.disabled` 占位 |
| 4. plugin 名一致 | hook path plugin name == installed plugin name | hook path plugin name 不在 installed |

**任一维度 drift → BLOCKED**, 走 §3 修复。

## 3. 修复路径 (4 选 1, 按 §C.3.6.1 no-stuck 选最稳)

### 方案 A: 选择性删 dead-link hook entry (推荐, per 本 case)

```bash
# 必先 Read 确认哪个 index 是 dead-link, 哪个是活 hook
jq '.hooks.PreCompact | length' ~/.claude/settings.json   # 期望 ≥ 2 才需要选删
jq '.hooks.PreCompact | to_entries[] | {idx: .key, cmd: .value.command}' ~/.claude/settings.json

# 假设 [0] 是 dead-link, [1] 是活 hook
jq 'del(.hooks.PreCompact[0])' ~/.claude/settings.json > /tmp/sn.json \
  && mv /tmp/sn.json ~/.claude/settings.json
```

**适用**: 多 hook 同 event, 部分 dead 部分活

### 方案 B: 全删整个 event hook (不推荐, 误伤活 hook)

```bash
jq 'del(.hooks.PreCompact)' ~/.claude/settings.json
```

**适用**: 该 event 全 dead, 无活 hook

### 方案 C: 改 path 凑合 (不推荐, 临时方案)

```bash
# 改 hardcode path 到新 version (0.2.0 → 0.2.11)
# ⚠️ 临时方案, 下次 plugin 升级再炸
jq '.hooks.PreCompact[0].command |= sub("0\.2\.0"; "0.2.11")' ~/.claude/settings.json
```

**适用**: 短期救火 (但要 commit + 标 "TODO: 长期治本改 fallback 链")

### 方案 D: 重新装 plugin 复活 hook (cost/benefit 高)

```bash
# 1. uninstall plugin
# 2. reinstall (走 plugin marketplace)
# 3. restart Claude Code
# 4. 5 字段自检 (commit/push/CI/owner/path) 2x
```

**适用**: plugin 功能真的需要 (但 mem0 等可走 L3 本地化方案, 不需要 PreCompact hook)

## 4. §A.1 settings.json SOP 5 件套 (必跑全, 任何方案 1-4 之后)

```bash
# 1. backup
TS=$(date +%Y%m%d-%H%M%S)
cp ~/.claude/settings.json ~/.claude/settings.json.backup.$TS

# 2. jq 修改
jq '<jq-expression>' ~/.claude/settings.json > /tmp/settings.new.json \
  && mv /tmp/settings.new.json ~/.claude/settings.json

# 3. JSON validate
python3 -c "import json; json.load(open('/Users/myk/.claude/settings.json'))"

# 4. diff check (linter 噪音分离)
bash ~/.claude/scripts/check-settings-json-diff.sh
# exit 0 = clean diff
# exit 1 = 含 linter signature, 拆 2 commit

# 5. atomic commit + push + 5 字段自检
cd ~/.claude
git add settings.json
git commit -m "fix(settings): <具体改动描述>"
git push origin main

# 5 字段验收
git log -1 --format="%h | %s"     # commit ✅
git log --oneline -5              # 5 commits ✅
git status --short                # 0 uncommitted (settings.json) ✅
git remote -v | head -2           # owner 一致 ✅
gh api repos/<owner>/<repo>/commits/HEAD/status   # CI green (或 pending if 无 GH Actions)
```

## 5. 5 IF...THEN 规则 (跟 record-case §9 + CASE-PRECOMPACT-HOOK-DEAD-PATH 同源)

1. **IF** plugin uninstall / 大版本升级 **THEN** 必跑本规则 §2 4 步体检, drift 即 BLOCKED
2. **IF** Claude Code 命令失败 + 错误信息含 hook name (PreCompact/SessionStart/Stop 等) **THEN** 必跑 §2 Step 2 `test -f <path>` 验证脚本存在, 缺失即 dead-link 走 §3 修复
3. **IF** cache 目录仅含 `.disabled` 占位 **THEN** 整 plugin 已禁用, 必删所有引用此 plugin 的 settings.json hook entry (per plugin 卸载不 cleanup 缺陷)
4. **IF** `jq '.hooks.<event> | length'` ≥ 2 **THEN** 必先 Read 索引定位 dead vs 活 hook, 走方案 A 选择性 `del(.hooks.<event>[<idx>])`, **不**全删 (避免误伤活 hook)
5. **IF** settings.json 改动涉及 hooks 字段 **THEN** 必走 §A.1 5 件套 (backup → jq → validate → diff check → atomic commit + push + 5 字段自检), **禁止**裸 Edit tool 改 (per settings.json SOP §A 硬规则 1-5)

## 6. 5 协议级反模式 (永久失效, 跟 record-case §6 同骨架)

1. ❌ "改 path 凑合 (0.2.0 → 0.2.11)" = 临时方案, 下次 plugin 升级再炸
2. ❌ "全删 event hook (`del(.hooks.PreCompact)`)" = 误伤活 hook (per 本 case vibe-island-bridge)
3. ❌ "假设 path 还对 (凭印象做事)" = 违反 §2 Step 2 `test -f` 实测
4. ❌ "裸 Edit tool 改 settings.json" = 违反 §A.1 5 件套 (per tooling §A.1 硬规则 #4)
5. ❌ "plugin 升级跨大版本不体检" = 违反本规则 §1 触发条件 #2

## 7. 联动 (cross-references)

- `~/.claude/rules/references/tooling-section-A-settings-json-sop.md` §A.1 硬规则 1-5 (5 件套)
- `~/.claude/rules/post-pr-merge-ff-verify-rule.md` §H (PR 合并后 ff verify + ahead/behind)
- `~/.claude/rules/protocols/5-field-acceptance.md` §H (5 字段自检表)
- `~/.claude/rules/cross-session-grep-mandatory.md` §1 (立新文件 / 改字段前 6 件套 grep)
- `~/.claude/docs/adr/0027-adr-namespace-resolution.md` (整数 slot 优先, 0058 = 本 rule ADR)
- `~/.claude/docs/adr/0058-plugin-hook-drift-pre-check.md` (本 rule ADR, 待立)
- `~/.claude/knowledge/cases/wiki/CASE-PRECOMPACT-HOOK-DEAD-PATH-PLUGIN-MISMATCH-20260716.md` (本 case)
- `~/.claude/knowledge/cases/wiki/CASE-MEM0-WRAPPER-PATH-STALE-20260624.md` (30 天前同类, 触发 record-case §9 升级阈值)
- `~/.claude/knowledge/cases/wiki/CASE-HOOK-EVENT-NAME-20260716.md` (同日同类, 不同根因 event 名 vs path drift)
- `~/.claude/knowledge/cases/wiki/CASE-MEM0-SLOW-HOOK-SEAL-20260715.md` (mem0 plugin 链路关联)
- `~/.claude/scripts/check-settings-json-diff.sh` (diff 校验 SOP §4 step 4)
- `~/.claude/plugins/installed_plugins.json` (plugin install 状态 SSOT)

## §8. 增量段 (v2.0+ 已搬 changelog-archive, 主文件不留)

> v2.0 (mem0 enabledPlugins false 误判) + v2.1 (plugin update registry 滞后 silent downgrade) + v2.2 (worktree dirty block + changelog discipline) 全部 4 CASE + 5 IF...THEN + 5 反模式 段已归档 [`rules/references/plugin-hook-drift-pre-check-changelog-archive.md`](rules/references/plugin-hook-drift-pre-check-changelog-archive.md). 触发场景: 30 天内同类第 4 次 mem0 plugin 链路 / CASE-OMC-PLUGIN-REGISTRY-DRIFT-20260720 / CASE-DOCTOR-PR-FF-ONLY-DIRTY-BLOCK-RECURRENCE-20260720 全部走 archive 查阅.

## 9. 历史 record

> **v2.2 (2026-07-20)**: 加 §8.3 v2.2 增量段 (per CASE-DOCTOR-PR-FF-ONLY-DIRTY-BLOCK-RECURRENCE-20260720 + changelog discipline). lesson A = 立 worktree 前必先 `git status --short` 列脏文件 + 5 IF...THEN + 5 反模式; lesson B = §8.x changelog 必走 changelog-archive, §9 仅留 pointer + 最近 1-2 条. 联动 process.md §C.3.1 (建议加第 0 步) + ADR-0071 plugin-update-registry-vs-tag-check. 完整 record 已归档 changelog-archive.
>
> **v2.1 (2026-07-20)**: 加 §8.2 plugin-update-registry-vs-tag-check 段 (per CASE-OMC-PLUGIN-REGISTRY-DRIFT-20260720, claude plugin update 字面 "updated from X to Y" 不可信 + registry stale silent downgrade 硬约束). 3 字段自检表 (registry / git tag / post-update installed) + 判定矩阵 4 态 + 手动 upgrade 3 步协议 + 5 IF...THEN + 5 反模式永久失效. 联动 ADR-0071 (整数 slot 0070 已占, 跳 0071).
>
> 完整历史 record (v1.0 / v2.0 / v2.1 / v2.2 立案) 已归档: `rules/references/plugin-hook-drift-pre-check-changelog-archive.md` (2026-07-19 v1.0/v2.0 立案, 2026-07-20 v2.1/v2.2 增量).