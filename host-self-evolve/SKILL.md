---
name: host-self-evolve
description: |
  本地主机 Claude Code 协调 + 自我进化 (v3.3.1 cross-reference + v3.3.0 PER Workflow): 提升 ~/.claude/ 跨层一致性 + §I.4 8 步循环 + N-tool fan-out internalize.
  5 Layer: Layer 0 5 commands gate / Layer 1 7 sub-task audit / Layer 2 cleanup orphan / Layer 3 N-tool fan-out / Layer A.2-A.4 5 字段自检 + 4 站 CI gate.
  触发词: 主机自升级, /host-self-evolve, self-evolve, 整理记忆, 协调 ~/.claude, 自我进化.
  必跑: §cwd-guard (v3.2.5/ADR-0059) + §doctor-check (v3.3.5) + banner + §Phase 1 (ADR-0041) + §memory-bench 50 题 (ADR-0065) + PER Workflow (v2.6.59/§C.3.7) + 实测 wall-clock.
  🆕 v3.3.1 cross-reference 5 维 (per ADR-0078): CSS → [CLAUDE.local.md §6.1](~/.claude/CLAUDE.local.md) | smart-push → [MEMORY.md §7](~/.claude/memory/MEMORY.md) | calm-flow → [soul.md §3](~/.claude/rules/soul.md) | N-tool → [N-tool-search.md](~/.claude/rules/protocols/N-tool-search.md) | auto-commit → [ADR-0063](~/.claude/docs/adr/0063-claudecode-auto-commit-policy.md).
when_to_use: |
  Also trigger when self-evolve / skill evolve / host 升级 / 整理记忆 / claude 协调.
  sub-task 触发: frontmatter audit / shell unified check / memory-bench 50 题 / N-tool 协议位 audit (per ADR-0056). 详见 references/per-workflow-framework.md.
  范围: ~/.claude/ + ~/.agents/skills/ 双仓. 不适用: 单文件 typo / 文档微调.
  反模式: ❌ PENDING 跳过 memory-bench / ❌ 写约束值当 wall-clock / ❌ 三段 sub-agent 物理隔离破坏 / ❌ 跑前不显示 🎯 banner / ❌ 跑完不写 ✅/❌/🔧 3 段 / ❌ 跑完汇报 > 80 行 / ❌ 跨域规则不引 SSOT (v3.3.1). 历史 → [archive](references/changelog-v3-2-1-3-archive.md).
license: MIT
metadata:
  version: "3.3.6"
  author: mykcs
  category: self-evolution
  changelog: "v3.3.6 (2026-07-26): 本 run @ Kimi Work 实跑收口 5 件事 — check-doctor-cleanup.sh 死变量 $LOCAL_CLAUDE 复活 (check 6/7/9/10 从假死到 8/8 ✅) + 7 rules frontmatter 补齐 (rules-health HIGH 5→0, 4 stub paths=self 落实自声明按需加载) + CLAUDE.md 22:11 0 字节截断应急 git 恢复 (属组 staff, 外部写入者未锁定) + Layer 2 七个根目录 .bak → backups/ + Layer 3 fan-out 12 highlights internalize. memory-bench 降级跑分 (deterministic-keyword-judge, 非官方 50 session + opus-judge) recall 22.5/50 (题库 v0.2.1 引用改名前 CLAUDE.local.md = staleness P1 派单) + consistency 4/6 + compliance 12/12 + normalized 72.4 ✅ target_met. v3.3.4 (2026-07-25): body 拆 4 references/ 1 层深 (per Anthropic best-practices + deep-research P0 #3). SKILL.md body 1014 → ~360 行 (< 500 cap). references/cwd-guard-per-defaults.md (§cwd-guard + PER + default decision + 汇报极简化 + 设计哲学) + references/memory-bench-protocol.md (memory-bench 必跑 + report-card 模板) + references/n-tool-drift-audit.md (N-tool 协议位 audit §1-§9 + §Layer 1.0) + references/case-study.md (实战案例沉淀). 触发不变. v3.3.3 (2026-07-25): 本 run @ Kimi Work 实跑收口 5 件事 — Layer 0 主仓 push 67f80059 + Layer 1.0 audit 子仓 PR #72 MERGED 50f1f6b + Layer 3 fan-out 12 highlights + memory-bench v0.2.0 recall 44/50 + consistency 15/15 + compliance 12/12 + normalized 95.8 ✅. v3.3.2 (2026-07-24): 本 run 实跑收口 4 件事 — CLAUDE.local.md §6.1 CSS var context 专题瘦身 + inject-hot-facts.sh v1.1 mtime 缓存修复 + settings.json dirty 走 worktree feat/settings-json-cleanup PR #107 + Layer 1.0 N-tool drift audit 4 维 grep P0=0. memory-bench v1. v3.3.1 (2026-07-22): 🆕 cross-reference 5 维 (per ADR-0078). v3.3.0 (2026-07-19): PER Workflow 统一抽象. v3.2.5 (2026-07-17): 🔒 cwd-guard 硬约束段 (per ADR-0059). v3.2.4 (2026-07-14): 🔍 N-tool 协议位 audit 子任务扩展 (per ADR-0056). 详见 references/changelog.md."
  tags:
    [
      self-evolution,
      claude,
      host,
      banner,
      fix-until-done,
      phase-1,
      life-setup,
      v3.2.1,
      default-decision,
      adr-0050,
      v3.2.2-deprecated,
      v3.2.3,
      report-minimal,
      phase-1-style,
      adr-0051-deprecated,
      adr-0052,
      v3.2.4,
      n-tool-audit-fix-sop,
      adr-0056,
      meta-protocol-pipeline,
      v3.2.5,
      cwd-guard,
      adr-0059,
      deja-vu-fix,
      per-workflow,
      v3.3.0,
      cross-reference-5d,
      adr-0078,
      v3.3.1,
      run-2026-07-24,
      adr-0065,
      v3.3.2,
      run-2026-07-25,
      v3.3.3,
      body-split-references,
      v3.3.4,
      doctor-check,
    ]
version: "1.0.0"
author: "mykcs"
last_updated: "2026-07-25"
triggers:
  - host-self-evolve
  - /host-self-evolve
  - self-evolve
  - 主机自升级
  - 整理记忆
  - 协调 ~/.claude
  - 自我进化

---

# 主机自升级 Skill (host-self-evolve v3.3.5)

> **v3.3.4 body 拆 4 references/** (per Anthropic best-practices + deep-research P0 #3): SKILL.md body 1014 → ~360 行. 引用 1 层深, 禁嵌套.

| references/ 段              | 内容                                                                                                 | 引用原因                                   |
| --------------------------- | ---------------------------------------------------------------------------------------------------- | ------------------------------------------ |
| `cwd-guard-per-defaults.md` | §cwd-guard (v3.2.5) + PER Workflow (v3.3.0) + v3.2.1 default decision + v3.2.3 汇报极简化 + 设计哲学 | 配置/默认决策段, 不常跑前必读              |
| `memory-bench-protocol.md`  | v3.2.8 memory-bench 必跑 + v3.2.9 report-card 11 行总表模板                                          | 跑分协议位, 跑分时才需要                   |
| `n-tool-drift-audit.md`     | N-tool 协议位 audit §1-§9 + §Layer 1.0 + §20 8 步管道 + 4 维 audit                                   | 协议位散落检测, 跑 host-self-evolve 时按需 |
| `case-study.md`             | 实战案例沉淀 (N-tool drift cleanup 5 件事 + 5 字段验收 + 踩坑 + 未来复用)                            | 历史案例, 复用参考                         |

---

## 🩺 §doctor-check 段 (v3.3.4 立, 2026-07-25, per Kimi Work session 体检修复实战)

> **触发**: 2026-07-25 Kimi Work session 修复链 — ① check-doctor-cleanup.sh 主流程曾是**死代码** (游离 `exit 0` + 内嵌 Python 字面换行语法错, 自创立起 8 项 check 从未实跑) ② 21:16 settings.json 出现 **0 字节 backup 对** (CC 自身备份例程被并发 doctor session 打断, 非本地脚本 bug, 属组 myk:wheel 异常).
>
> **协议位**: host-self-evolve 摸底阶段 (§cwd-guard 通过后 / Layer 1 开始前) **必跑** `bash ~/.claude/scripts/check-doctor-cleanup.sh`, 10 项 check (1/2/3/4/5/6/7/9/10, 8 跳过) 全 ✅ / ℹ️ 才继续; 任何 ⚠️ / ❌ 项先收口派单, 不带病进 Layer 1.

**10 项 check 一览** (SSOT = 脚本本身, 此处只列 anchor):

| # | 检查项 | 健康线 |
|---|--------|--------|
| 1 | 3 MCP 90 天 0 调用 | 全 disabled |
| 2 | CLAUDE.local.md dedup | 仅 1 份 |
| 3 | process.md chars | < 40K |
| 4 | stale §self-summary | 无 >7 天段 |
| 5 | SessionStart slow hooks | 无 timeout |
| 6 | context heavy (v3.3.5 增强) | references/protocols 无 paths 漏网=0 + 常驻 ~10K tokens (2026-07-26 减重后基线) |
| 7 | version currency | CLI 在 PATH |
| 9 | 频繁 deny | < 50 |
| 10 | **settings.json 完整性** (v3.3.4 新增) | JSON 有效 + 属组 staff + 无 0 字节 backup 残留 |

**脚本维护硬规则 (per 本次修复教训, 改 check-doctor-cleanup.sh 后必跑 3 件套)**:

1. `bash -n` 语法过 + `shellcheck -x` clean (含 info 级)
2. 全程冒烟 `bash check-doctor-cleanup.sh` exit 0 且无 stderr
3. **pipefail 3 脚枪写法** (set -euo pipefail 下必守):
   - `{ grep -r ... || true; } | wc -l` (grep 无匹配 exit 1 会杀脚本)
   - `grep -c ... || true` (grep -c 必出计数, 不要再 `| head -1`, `|| echo 0` 会造成双行)
   - `[ -f x ] && VAR=$(...)` 脚枪改 if-form (文件缺失即静默退出)

**反模式 (永久失效, 4 条)**:

1. ❌ 体检脚本自身带病 = 假绿源头 (游离 exit 0 让 8 项 check 死代码躺了 10 天无人发现)
2. ❌ 0 字节 backup 当 "已备份" = 比没备份更危险 (假安全感, 2026-07-25 21:16 实例)
3. ❌ settings.json 属组非 staff 不追查 = 外部工具截断式写入的信号被忽略
4. ❌ 改脚本只过 bash -n 不过 shellcheck + 冒烟 = pipefail 雷上线才炸

**联动**: §cwd-guard (跑前守卫, 本段是其兄弟段) + `rules/shared-file-write-freshness.md` (多 agent 并发写 settings 协议) + skill `disable-truth-sop` (写后必断言) + 主仓 commits 57e794bb (pipefail 排雷) / 93f7f656 (check 10 立) / ecffa304 (死代码复活)

**历史 record**:
- 2026-07-25 v3.3.4: 立 (per Kimi Work session — hooks shellcheck 修复链 + doctor 体检复活 + 0 字节 backup 根因调查收口, user 指令 "把这个检查修复合并进主机自升级")

---

- 2026-07-26 v3.3.5: check 6 增强 + §context-budget-fix 立 (per user "把这个检查修复加到主机自升级"). check 6 从'求和所有 rules'改成'揪 references/protocols 无顶层 paths 漏网'; 起源 rules 减重 91.4k→17k memory (主仓 PR #119/#120/#122/#123).

### §context-budget-fix (check 6 报 ⚠️ 时的修复 SOP, v3.3.5 立)

check 6 报 "N 个 references/protocols 无顶层 paths" → 逐个加**顶层** `paths:` 让其从常驻改按需加载。

**机制** (per code.claude.com/docs/en/memory + 2026-07-26 本机实证):

- rules/*.md 有**顶层** `paths:` (跟 name/description 平级, **不能**嵌 metadata) → 只在 Read 匹配文件时加载
- 无 paths → session 启动无条件常驻
- 实证: `process-a-workflow.md` (有 paths) 不在 /context; 无 paths 的全在

**修复映射 (按父规则继承 scope)**:

| 文件前缀 | 顶层 paths |
| --- | --- |
| `process-*` | 代码+配置+SKILL (同 process.md) |
| `tooling-*` | CSS/settings/kimi/skills |
| `language-stack-{cpp,go,php}` | 对应语言后缀 |
| `typescript-*` / `bugfix-400-*` | TS/JS / fix脚本+settings |
| `soul-*` | `~/.claude/rules/soul.md` + `references/soul-*.md` |
| `*-changelog-archive.md` | 只 scope 自己 (纯历史, ≈永不自动加载) |
| `protocols/*` | `~/.claude/rules/**` + `protocols/**` + skills (directive 在常驻 CLAUDE.md) |

**硬规则**:

1. ❌ 别 scope 写时安全闸门规则, **除非**它有 hook 兜底 (verify-before-act→`pre-verify-act.py`; cross-session-grep→`pre-skill-protocol.sh`) — 否则 Read 触发 ≠ Write 触发, 悄悄失效
2. ❌ `soul.md` / `calm-flow.md` 是核心行为规则, 保持常驻不 scope
3. ✅ 改完必**重启 claude + /context** 实测 (本 session 改的规则本 session 命中 scope 仍加载, 测不准)
4. ✅ 无 frontmatter 的文件新建 `---` 块含 `name:` + `paths:`; 有的则插顶层 paths (per rules 减重工程 §20 规范)

---
## 触发方式 (中英文, 12 词)

| 中文                     | 英文                   |
| ------------------------ | ---------------------- |
| 主机自升级               | /host-self-evolve      |
| 自我升级                 | self-evolve            |
| 整理记忆                 | host evolve            |
| claude 协调              | claude coord           |
| 协调 ~/.claude           | evolve claude          |
| evolve 整体              | full self-evolve       |
| **N-tool 协议位 audit**  | **N-tool audit**       |
| **4 路盘点 N-tool 收口** | **N-tool unify audit** |

> **不适用** (灵魂 v6 anti-trigger, 跟 frontmatter when_to_use 协同): 单文件 typo / 文档微调 / 非 ~/.claude/ 项目 (用 website-improve) / 用户说 "我就要个快速版" (拒绝, 走 §F 自决协议位)。

---

## 🎯 执行前 banner 段 (v3.1.0 立, 2026-07-03)

> **触发**: user 2026-07-03 反馈 "放到这个技能以后, 如果我执行它, 必须很明显地输出接下来要检查什么事情, 检查哪些、提升哪些、修复哪些". 跟 v2.6.55 (做什么/修了什么, 跑完 UX) + v2.6.57 (banner UX, 跑前 UX) 协同.
>
> **协议位**: host-self-evolve 跑前**必**先输出本段 (跟 frontmatter when_to_use + 触发词协同). 缺 = 违反 v3.1.0 硬约束.

**强制输出格式** (跟 v2.6.48 / v2.6.57 banner 同格式, 大横幅 + 5 字段):

```
═══════════════════════════════════════════════════════════
🎯 host-self-evolve v3.1.0 <本次跑主题 / 触发词>
═══════════════════════════════════════════════════════════

🔍 检查什么 (What I will check):
  ├─ [Layer 0] 5 commands gate (git status / log / remote / ahead-behind / CI)
  ├─ [Layer 1] 7 sub-task audit (file size / cross-source dup / case library / orphan / frontmatter / shell unified / memory-bench 50 题)
  ├─ [Layer 1.0] **N-tool 协议位 drift audit** (per ADR-0056, 2026-07-13 立, 强制必跑 — 详见 references/n-tool-drift-audit.md)
  ├─ [Layer 2] cleanup orphan (孤文件 / 断链 / 死代码)
  ├─ [Layer 3] N-tool fan-out (N 当前 = 6, per N-tool-search.md)
  └─ [Layer A] 5 字段自检 (path / commit / push / CI / owner) + §C.3.7 4 站 CI gate

🔧 修复什么 (What I will fix):
  ├─ Layer 0-3 跑出来的 critical (FAIL exit 2, 必修)
  ├─ Layer A 5 字段自检 fail 项 (必修)
  └─ memory-bench < 60 target 立即修协议 (per §C.3.3 v2.6.56)

🚀 提升什么 (What I will improve):
  ├─ 新洞见 internalize 到 ~/.claude/memory/*.md (per §I.4 step 3)
  ├─ ADR 整数 slot 不抢 sub-slot (per ADR-0027 v1.1)
  ├─ SKILL.md changelog 升 v3.1.X
  └─ sub-skill / references/ 增量文档化 (跟 references/changelog.md 同步)

⏱️ 预期 wall clock: ≥ 30 min (实测, 不写约束值, per CASE-HOST-SELF-EVOLVE-V2-7-0-WALL-CLOCK-FALSE-CLAIM)

✅ 完成标准:
  - 7 sub-task 全跑通 (含 memory-bench 50 题, 不允许 PENDING 跳过 per §C.3.3 v2.6.56)
  - **Layer 1.0 N-tool 协议位 drift audit 全跑通** (4 维 grep + 命中 P0 走 §20 8 步管道修, 不允许 PENDING 跳过)
  - N-tool fan-out 抓 8+ 资源 internalize (per §I.4 8 步循环)
  - Layer A.4 5 字段自检表全过 (path / commit / push / CI / owner)
  - PER Workflow 协议位 (plan / execute / verify 物理隔离, per references/per-workflow-framework.md)
  - 跑完必输出 ## ✅ 做了 (N 项) + ## ❌ 没做 (M 项) + ## 🔧 修了 (K 项) 3 段 (per v3.1.0 §✅ 执行后段)
  - ❌ 没做项 = 立即修, 不卸载给 user (per §✅ 修没做到 协议)

═══════════════════════════════════════════════════════════
                  banner 结束 — 正式自升级即将开始
═══════════════════════════════════════════════════════════
```

**字段约束**:

- 标题 `🎯 host-self-evolve v3.1.0 <主题>` 1 行 ≤ 60 chars
- 横幅 `═══...═══` 上下两行包围
- 5 字段必填 (检查 / 修复 / 提升 / 预期 wall clock / 完成标准)
- 数字具体 ("7 sub-task" / "5-tool" / "8+ 资源" / "≥ 30 min 实测")

**反模式 (永久失效)**:

- ❌ 跑前不显示 🎯 banner 段
- ❌ banner 缺 5 字段任一
- ❌ banner 数字模糊 ("一些" / "几个")
- ❌ 预期 wall clock 写约束值 (per CASE-HOST-SELF-EVOLVE-V2-7-0-WALL-CLOCK-FALSE-CLAIM)
- ❌ 主题字段缺 (banner 跑前 user 不知道要干嘛)
- ❌ **banner 缺 Layer 1.0 N-tool 协议位 drift audit** (字面 drift 漏检, 协议级必跑)

---


## 🌱 Phase 1 — Life / Setup 段 (v3.2.0 立, 2026-07-08, per ADR-0041)

> **触发**: user 2026-07-08 反馈 "修改 skill 主机自升级, 我需要你把这个 skill 明显的分为几个阶段或者是几个模块. 我需要在这个第一阶段是生命或者是设置, 需要完整的输出出来, 我们要干什么". 跟 v3.1.0 banner UX 协同: banner 之后**必**输出本段 (不可跳, 违反 v3.2.0 §✅ 修没做到).
>
> **协议位**: host-self-evolve 跑前 banner 之后**必**先输出本段 (跟 v3.1.0 banner + ADR-0041 协同). 缺 = 违反 v3.2.0 硬约束.
>
> **🔴 硬规则 (per CASE-HOST-SELF-EVOLVE-V3-2-0-PHASE-1-MISSED-20260708, 2026-07-08 user 抓包立)**:
>
> - 跑 banner 段 (v3.1.0) → **立即**接 §Phase 1 段 (v3.2.0) → 然后才跑 Layer 0-3 摸底
> - **不可跳** §Phase 1 段直接进 Layer 0-3 摸底
> - **不可自决**"先跑 7 sub-task 再补 §Phase 1 段" (违反"banner 之后立即")
> - **不可混** Phase 1.1-1.4 摸底 (Layer 0-3 子任务) 跟 §Phase 1 段 (跑前必输协议位 output), 2 个独立硬约束
> - claudecode 把"必"降级成"可选" = false completion (per §C.5 + 灵魂 v6 §6 self-verify)
> - 跑完**必**灵魂 v6 self-verify: `grep -E "🌱 Phase 1" <output>` 期望 ≥ 1 命中, 0 命中 = 违反 v3.2.0 硬约束, 立即 abort 改写

**强制输出格式**:

```
🎯 host-self-evolve v3.2.0 — 主机自升级
═══════════════════════════════════════

🔍 检查什么

  - Layer 0: 跑 5 个 git 命令 (查提交历史 / 当前改了什么 / 远程地址 / 跟远程差几条 / 线上是否绿)
  - Layer 1: 跑 7 项体检 (文件大小 / 重复内容 / 案例库 / 孤儿文件 / SKILL.md 头 / shell 配置 / 记忆题库 50 题)
  - Layer 2: 清掉没用的文件 / 断链 / 死代码
  - Layer 3: 上网查资料 (用 6 个搜索工具并行)
  - Layer A: 检查路径/提交/推送/线上绿灯/归属 5 项 + 4 个站点线上是否都绿

🔧 修复什么

  - Layer 0-3 跑出来标红的关键项 (FAIL 必须修)
  - Layer A 5 项里有哪项没过
  - 记忆题库 50 题分数 < 60 → 立刻改协议

🚀 提升什么

  - 新学到的东西写进本地记忆文件
  - 立新的 ADR (用整数编号,不抢 sub-slot)
  - SKILL.md 版本号往上提一档
  - 子 skill / 参考文档 增量补完

⏱️ 预计要多久: 至少 30 分钟 (写实测值,别写最低要求)

✅ 完成标准

  - 7 项体检全跑通 (含记忆题库 50 题, 不能跳过)
  - 上网查到 8 条以上资料并写进记忆
  - Layer A 5 项检查全过
  - 用 PER Workflow 跑 (计划 / 执行 / 验收 三个人独立)
  - 跑完输出 ## ✅ 做了 + ## ❌ 没做 + ## 🔧 修了 三段

══════════════════════
banner 结束 — 立即接 Phase 1 段
══════════════════════
```

```
🌱 Phase 1 — Setup (设置) — 完整说明
═══════════════════════════════════════

🎯 目的

  把本机 ~/.claude/ + ~/.agents/skills/ 这台"小主机"先从
  "能跑" 升级到 "稳跑 + 自我知道怎么跑"。后面 4 个子模块是
  地基, 地基不稳, 后面盖楼 (审计 / 进化 / 沉淀) 全是危楼。

───────────────────────────────────────
🧩 4 个子模块 — 第一批要干的活
───────────────────────────────────────


📦 Phase 1.1 — BASH / FISH / ZSH 整理

  一句话: 把本机 3 个 shell 配置拉到统一基线 (per shell-unify-checklist v1.1)

  现状:
    - fish 4.6.0 (主用, 严格统一)
    - bash 3.2.57 (claudecode 进程用, 严格统一)
    - zsh 5.9 (macOS 自带, 放松维护)

  干什么:
    1. 5 探测摸底 (LoginShell / 进程 shell / 3 shell 版本 / config 文件 / 公共源)
    2. 跑 shell-unified-check.py (Layer 1.4 orphan + 跨 shell dup)
    3. 手动 diff fish 跟 bash (真实 login shell 跑命令)
    4. 单源 grep (7 env var + 3 function 期望 1-2 命中)
    5. 修复: 抽公共源 ~/.config/shell-common/ 12 文件
    6. 5 commands 验收

  验收:
    - 12 公共源文件就位
    - 3 shell config 引用公共源 (loader.sh/fish)
    - 重复 key 检查 0 (除 env.sh + env.fish 双语版本)
    - shell-unified-check.py exit 0 (或 expected exit 1 zsh 放松)


───────────────────────────────────────


🧠 Phase 1.2 — 记忆整理

  一句话: 把本机所有"记忆" (MEMORY.md / mem0 / CLAUDE.local.md) 拉到统一基线

  干什么 (3 子层):

    A. MEMORY.md 索引化
       - 现状: MEMORY.md 200+ 行, 含 hot facts + feedback + cases + cross-cutting, 散落
       - 目标: 拆 4 文件 (MEMORY-index.md / MEMORY-feedback.md / MEMORY-cases-active.md / MEMORY-cross-cutting.md)
       - 验收: MEMORY.md ≤ 50 行, 全部子文件带 frontmatter + 互链

    B. mem0 cleanup (quota 1000/1000 满, reset 2026-08-01)
       - 现状: mem0 配额耗尽, 暂不可搜不可写
       - 目标: 跑 mem0 memory-reviewer 删过期 / 重复 memory
       - 验收: mem0 健康, quota < 80%, 关键决策可搜回

    C. CLAUDE.local.md hot facts 收紧 (321 行 → ≤ 250 行)
       - 现状: §5.1 / §5.2 / §6.1 / §7.1 / §8.1 / §10.1 ... 各 section 引用文件, 部分重复
       - 目标: 全 hot facts 走 SSOT 1 行 pointer 引用
       - 验收: CLAUDE.local.md ≤ 250 行, 0 内容重复


───────────────────────────────────────


📐 Phase 1.3 — 规则整理

  一句话: rules/ 8 文件 path-scoped + 0 散落 + 全 SSOT 引用

  现状:
    - 8 个 active rule 文件 (universal / process / typescript / python / language-stack / bugfix-400 / tooling / shell-unify / cross-session-grep / post-pr-merge-ff-verify)
    - 6 个 protocols/ SSOT v0.1 草案 (2026-07-02 立)
    - 散落位: 75 files drift (skill-self-evolution) + 41+ files 5 字段自检

  干什么:
    1. 跑 shell-unified-check.py Layer 1.4 (orphan audit)
    2. 跑 N-tool-search.md §1 6-tool 抓 8+ 外部资源
    3. cross-session-grep.md §1 6 件套 grep
    4. 跟 6 个 protocols/ SSOT 路径对比, 标散落位
    5. 修法: 改 1 行 anchor pointer (per §A.4.2 #4 path-scoped)
    6. 立 ADR-0041 (本 run 协调性 fix 沉淀, 整数 slot)

  验收:
    - 6 SSOT 全部 ≤ 200 行
    - 散落位 75 → 0
    - new ADR 立 (0041 整数 slot)


───────────────────────────────────────


⚙️ Phase 1.4 — 本机自带自动化整理

  一句话: 把 ~/.claude/hooks/ + scripts/ + settings.json 4 hooks 协议位 整理

  现状 (per CLAUDE.local.md §18 + rules/protocol-violation-auto-detect.md §4):
    - 4 hooks 协议位 (cross-session-grep / verify-before-act / post-pr-merge-ff-verify / protocol-violation-auto-detect)
    - 挂载在 ~/.claude/settings.json 的 PreToolUse / PostPRMerge / Stop 钩子位
    - 实施状态: 0 个真挂 (参考实现 ~/.omc/hooks/*.sh 写好了, user 没挂载)

  干什么 (SOP per ADR-0026 + ADR-0039 + §18):
    1. 摸底: `grep -A 20 '"hooks"' ~/.claude/settings.json` 看实际挂载数
    2. 比对参考实现 ~/.omc/hooks/* 4 个脚本 (per protocol-violation-auto-detect.md §4)
    3. 跟 user 确认是否挂 (灵魂 v3 §3: framework config 改字段 必问)
    4. 挂载后跑 5 commands verify + 1 次实战触发验证
    5. 立 ADR-0042 (本机自动化挂载决策沉淀)

  验收:
    - 4 hooks 协议位 100% 挂载 (或 user 决策"参考实现就够" 走文档化)
    - settings.json diff ≤ 50 行 (per tooling-section-A §A.2 触发式决策表)
    - new ADR 立 (0042 整数 slot)


═══════════════════════
🚀 Phase 1 整体验收 (跑完 1.1 → 1.4 后必跑)
═══════════════════════════════════════
  - 5 fields acceptance (path / commit / push / CI / owner)
  - decision-stream 流追加 (per calm-flow §4)
  - mem0 add_memory × 1-3 条 (per post-task-recommend §3)
  - ADR 整数 slot 不抢 sub-slot (per ADR-0027 v1.1)
  - SKILL.md changelog 升 v3.2.X (本 run 沉淀)

═══════════════════════════════════════
```

**字段约束** (跟 v3.1.0 banner §字段约束 协同):

- 标题 `🌱 Phase 1 — Life / Setup` 1 行 ≤ 60 chars
- 横幅 `═══...═══` 上下两行包围
- 4 子模块必填 (1.1 shell / 1.2 记忆 / 1.3 规则 / 1.4 自动化)
- 整体验收必填 (5 fields + decision-stream + mem0 + ADR + changelog)
- 数字具体 ("12 公共源文件" / "75 files drift" / "≥ 30 min 实测")

**§Phase 1 协议位硬规则**:

- IF user 触发「主机自升级」/ self-evolve / 整理记忆 / claude 协调 / 协调 ~/.claude / 自我进化
- AND banner 段跑完
- THEN **必**接本 §Phase 1 段 (banner 之后, Layer 0-3 之前)
- AND 4 子模块描述必完整 (一句话 + 现状 + 干什么 + 验收)

**反模式 (永久失效)**:

- ❌ 跑前只输出 banner 5 字段, 缺 §Phase 1 段 (违反 ADR-0041 v3.2.0)
- ❌ Phase 1 段输出后跳过 Layer 0-3 (违反 §I.4 8 步循环)
- ❌ Phase 1 4 子模块拆 4 个独立 skill (违反 host-self-evolve 主 skill 协调定位)
- ❌ Phase 1 跑完不跑整体验收 (违反 §H Acceptance Protocol 5 字段自检表)
- ❌ banner 写 wall clock = "30 min" 约束值 (违反 CASE-HOST-SELF-EVOLVE-V2-7-0-WALL-CLOCK-FALSE-CLAIM)

**联动**:

- 跟 v3.1.0 banner UX (跑前) 协同: banner → §Phase 1 → Layer 0-3 顺序固定
- 跟 v3.1.0 ✅ 执行后 3 段 detailed (跑后) 协同: §Phase 1 → Layer 0-3 → 3 段 detailed
- 跟 v2.6.46 wall-clock 改名实测硬约束协同: Phase 1 段含 wall clock 字段必填实测值
- 跟 PER Workflow (plan / execute / verify) 协同: Phase 1 跑前属于 plan 段
- 跟 ADR-0041 协同: 本段是 ADR-0041 §协议位架构图 的 SKILL.md 落地
- 跟 shell-unify-checklist v1.1 §2 4 步 SOP 协同: Phase 1.1 主入口
- 跟 memory-strategy.md v2 §F.4.4 协同: Phase 1.2 主入口
- 跟 rules-distill skill 协同: Phase 1.3 主入口
- 跟 protocol-violation-auto-detect §4 4 hooks 协议位 协同: Phase 1.4 主入口

**历史 record**:

- 2026-07-08 v3.2.0 立 (user 2026-07-08 反馈 + ADR-0041, 整数 slot 0041 AVAILABLE)

---

## ✅ 执行后 detailed 输出段 (v3.1.0 立, 2026-07-03)

> **触发**: user 2026-07-03 反馈 "等这一块功能运行完以后, 要非常详细、明显地输出哪些东西做到了, 哪些东西没做到. 如果没有做到的话, 就修复它, 并且做到". 跟 v2.6.55 协同 (v2.6.55 短, 本段详).
>
> **协议位**: host-self-evolve 跑完**必**先输出 3 段 (`✅ 做了` + `❌ 没做` + `🔧 修了`), 不可省. ❌ 没做项 = **必立即修** (per §✅ 修没做到 协议), 修完再进 §H 5 字段自检 + 报告.

**强制输出格式** (3 段 + 1 汇总):

```markdown
## ✅ 做了 (N 项)

| #   | 项         | Layer     | 详情              |
| --- | ---------- | --------- | ----------------- |
| 1   | <做了什么> | [Layer X] | <具体动作 + 数字> |
| 2   | <做了什么> | [Layer X] | <具体动作 + 数字> |
| ... | ...        | ...       | ...               |

**小计**: N 项, 跨 [Layer X / Y / Z].

## ❌ 没做 (M 项)

| #   | 项           | 原因         | 修法 (立即跑)      |
| --- | ------------ | ------------ | ------------------ |
| 1   | <没做到什么> | <为什么没做> | <具体修法, 含命令> |
| ... | ...          | ...          | ...                |

**小计**: M 项, 必立即修 (per §✅ 修没做到 协议).

## 🔧 修了 (K 项) — 上面 ❌ 没做的修法跑完

| #   | ❌ 没做 # | 修法 (跟上面) | 跑完实测 | 验收    |
| --- | --------- | ------------- | -------- | ------- |
| 1   | 1         | <命令>        | <输出>   | ✅ / ❌ |
| ... | ...       | ...           | ...      | ...     |

**小计**: K 项修完, M-K 项仍未修 (写明原因 + BLOCKED 条件).

## ⏱️ 实测 wall clock + 5 字段自检

- ⏱️ 实测 wall clock: <X> min (vs 预期 ≥ Y, 差/超 Z)
- 1. path: ✅ / ❌ <file>
- 2. commit: ✅ / ❌ <hash | msg>
- 3. push: ✅ / ❌ ahead/behind
- 4. CI: ✅ / ❌ <state>
- 5. owner: ✅ / ❌ <mykcs / wangrui2025>
```

**字段约束**:

- 3 段必填, 缺 = 违反 v3.1.0 硬约束
- 数字具体 ("3 file +12/-5" / "2 case 立")
- ❌ 没做表写"原因" + "修法" 双字段 (user 看得懂, 跟"未做"对立)
- 🔧 修了表回链 ❌ 没做表 # 字段 (对得上)
- ⏱️ wall clock 必填实测值 (per CASE-HOST-SELF-EVOLVE-V2-7-0-WALL-CLOCK-FALSE-CLAIM)

**§✅ 修没做到 协议 (v3.1.0 立, 2026-07-03)**:

| 修法类型                                 | 必跑                                | 不可卸载给 user                |
| ---------------------------------------- | ----------------------------------- | ------------------------------ |
| ❌ 没做表任一项                          | 立即跑修法 (单步 ≤ 5 min)           | ❌ 写"下次再" / "留给 user"    |
| ❌ 修法失败                              | 重试 ≤ 3 次 (per §C.3.6.1 no-stuck) | ❌ 立即 STOP + AskUserQuestion |
| ❌ BLOCKED on X                          | 显式说明 + 触发条件                 | ❌ 静默标 PENDING              |
| ❌ 不可逆 / framework config / user 偏好 | AskUserQuestion (4 类必问)          | ❌ 装作 know                   |
| ❌ 跑 ≥ 5 min 必问 user                  | AskUserQuestion (long-task 显式)    | ❌ 默默做                      |

**反模式 (永久失效)**:

- ❌ 跑完只给分数 ("完成 80%" 无 3 段)
- ❌ 修复藏在 ❌ 没做表里不显式 (违反 user 反馈 "非常详细、明显地输出")
- ❌ ❌ 没做 = 0 假装全做了 (实际 < 100%, false completion per §C.5)
- ❌ 写"下次再" / "留给 user" (违反 v3.1.0 §✅ 修没做到 协议)
- ❌ 跑完不跑 5 字段自检 (per §H Acceptance Protocol)

**联动**:

- 跟 v2.6.55 (做什么/修了什么, 短) 协同: v2.6.55 简化, v3.1.0 详 3 段
- 跟 v2.6.57 (banner, 跑前) 协同: 跑前 banner + 跑后 3 段 = 完整 UX
- 跟 PER Workflow 协同: verify 段必跑 3 段 detailed 输出 (per §C.3.7)
- 跟 §C.3.6.1 (no-stuck) 协同: 修没做到失败 ≤ 3 次重试, 不循环
- 跟 §C.5 (false completion) 协同: ❌ 没做 = 0 才是真 done
- 跟 §H (Acceptance Protocol) 协同: 5 字段自检在 3 段后
