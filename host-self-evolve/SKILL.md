---
name: host-self-evolve
description: |
  本地主机 Claude Code 协调 + 自我进化 (v3.2.0 design philosophy + Phase 1 阶段化): 提升 ~/.claude/ 跨层一致性 + §I.4 8 步循环 + N-tool fan-out internalize.
  5 Layer: Layer 0 5 commands gate / Layer 1 7 sub-task audit / Layer 2 cleanup orphan / Layer 3 N-tool fan-out / Layer A.2-A.4 5 字段自检 + 4 站 CI gate.
  触发词: 主机自升级, /host-self-evolve, self-evolve, 整理记忆, 协调 ~/.claude, 自我进化.
  必跑: 跑前 banner + §Phase 1 Life/Setup 段 (4 子模块 1.1 shell / 1.2 记忆 / 1.3 规则 / 1.4 自动化, per ADR-0041) + memory-bench 50 题 (per §C.3.3) + 三段 sub-agent (v2.6.59) + 实测 wall-clock. 详见 [N-tool-search SSOT §1](~/.claude/rules/protocols/N-tool-search.md) + [changelog](references/changelog.md).
when_to_use: |
  Also trigger when self-evolve / skill evolve / host 升级 / 整理记忆 / claude 协调.
  sub-task 触发: frontmatter audit (15 fields / 1,536 cap) / shell unified check / memory-bench 50 题 (per §C.3.3).
  范围: ~/.claude/ + ~/.agents/skills/ 双仓.
  不适用: 单文件 typo / 文档微调 / 非 ~/.claude/ 项目 (用 website-improve).
  反模式: ❌ 标 PENDING 跳过 memory-bench / ❌ 写约束值当 wall-clock (per CASE-HOST-SELF-EVOLVE-V2-7-0) / ❌ 三段 sub-agent 物理隔离破坏 / ❌ 跑前不显示 🎯 banner / ❌ 跑前 banner 后缺 §Phase 1 段 (per ADR-0041 v3.2.0) / ❌ 跑完不写 ## ✅/## ❌/## 🔧 3 段. 完整见 [skill-authoring-best-practices.md](references/skill-authoring-best-practices.md).
license: MIT
metadata:
  version: "3.2.0"
  author: mykcs
  category: self-evolution
  changelog: "see references/changelog.md for v1.0.0-v3.2.0 history (v3.2.0 = 🎯 banner + §Phase 1 Life/Setup 4 子模块总览嵌入, per user 2026-07-08 反馈 + ADR-0041)"
  tags: [self-evolution, claude, host, banner, fix-until-done, phase-1, life-setup]
---

# 主机自升级 Skill (host-self-evolve v3.0.0)

## 设计哲学 (design philosophy, v1.0 立)

本技能的**唯一目的**是提升本地主机的 `~/.claude/` 协调性能力, 配套持续自我进化机制:

### 维度 1: 协调性 (coordination)

`~/.claude/` 是一台**小型主机的配置仓库**, 跟代码仓无异。本技能像管代码一样管它:

| 协调层 | 关注 |
|--------|------|
| `CLAUDE.md` | 全局入口, 内容跨仓一致, 不超 200 行 |
| `CLAUDE.local.md` | 本机 hot recall 锚点, 关键 fact ≤ 5 字段自检 |
| `rules/` | 行为准则, path-scoped 减少 token 注入 |
| `memory/` | 用户偏好 + 案例 + ADR 索引 |
| `cases/wiki/` | 已知失败模式 + 5 IF...THEN 规则 |
| `skills/` | 子仓 symlink → `~/.agents/skills/`, source of truth 单点 |
| `scripts/` | 可执行工具 (cross-tool 验证) |
| `hooks/` | 自动化行为 (per settings.json) |

**协调硬指标**:
- ✅ 协议位 (N-tool-search / cross-session-grep / skill-self-evolution / reverse-mode / soul-protocol / 5-field-acceptance) 不散落, 改 1 行 anchor pointer 引用 SSOT
- ✅ frontmatter 15 字段 + 1,536 chars cap 全 SKILL.md 满足
- ✅ 双账号隔离 (mykcs/* vs wangrui2025/*) 永不出错
- ✅ case file 引用都命中, 0 orphan, 0 dangling cross-ref

### 维度 2: 自我进化 (self-evolution)

跟管代码一样, 配置仓也需要**持续改进**。8 步循环 (per §I.4):

1. 跑 N-tool fan-out (N 当前 = 6, per N-tool-search.md)
2. 抓 8+ 外部资源 highlights
3. internalize 关键洞见 → `~/.claude/memory/*.md` 或新建 memory
4. 更新 ADR (整数 slot 不抢 sub-slot, per ADR-0027 v1.1)
5. 更新 SKILL.md changelog (v3.0.0 → v3.1.0...)
6. commit + push (atomic commit + smart-push, 走 §11)
7. PR + auto-merge (per §C.3.2, 4 条件满足)
8. 5 commands verify + 第 6 字段 FF status + decision-stream

### 维度 3: wall-clock 诚实 (per CASE-HOST-SELF-EVOLVE-V2-7-0-WALL-CLOCK-FALSE-CLAIM)

**禁止写协议约束值当 wall-clock**。**禁止用"重版/重度/轻量/快速版"** 字眼诱导偷懒 (per CASE-HOST-SELF-EVOLVE-V2-7-0-NO-LIGHT-HEAVY-WORDS, 2026-07-03 立, v2.7 = 本次改名立条源)。

- ✅ time.start + time.end 实测 wall-clock
- ✅ 任务完成时长 = 协议要求的 wall-clock 时, 写实测值, 不写约束值
- ✅ 任务未跑够约束时长, 写 "< 实测 X, 约束 ≥ Y" + 立 case file + 不掩饰

## 触发方式 (中英文, 12 词)

| 中文 | 英文 |
|------|------|
| 主机自升级 | /host-self-evolve |
| 自我升级 | self-evolve |
| 整理记忆 | host evolve |
| claude 协调 | claude coord |
| 协调 ~/.claude | evolve claude |
| evolve 整体 | full self-evolve |

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
  - N-tool fan-out 抓 8+ 资源 internalize (per §I.4 8 步循环)
  - Layer A.4 5 字段自检表全过 (path / commit / push / CI / owner)
  - 三段 sub-agent 协议位 (plan / execute / verify 物理隔离, per v2.6.59)
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

---

## 🌱 Phase 1 — Life / Setup 段 (v3.2.0 立, 2026-07-08, per ADR-0041)

> **触发**: user 2026-07-08 反馈 "修改 skill 主机自升级, 我需要你把这个 skill 明显的分为几个阶段或者是几个模块. 我需要在这个第一阶段是生命或者是设置, 需要完整的输出出来, 我们要干什么". 跟 v3.1.0 banner UX 协同: banner 之后**必**输出本段 (不可跳, 违反 v3.2.0 §✅ 修没做到).
>
> **协议位**: host-self-evolve 跑前 banner 之后**必**先输出本段 (跟 v3.1.0 banner + ADR-0041 协同). 缺 = 违反 v3.2.0 硬约束.
>
> **🔴 硬规则 (per CASE-HOST-SELF-EVOLVE-V3-2-0-PHASE-1-MISSED-20260708, 2026-07-08 user 抓包立)**:
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
  - 用三段 sub-agent 跑 (计划 / 执行 / 验收 三个人独立)
  - 跑完输出 ## ✅ 做了 + ## ❌ 没做 + ## 🔧 修了 三段

═══════════════════════════════════════
banner 结束 — 立即接 Phase 1 段
═══════════════════════════════════════
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

  现状:
    - 4 hooks 协议位 (cross-session-grep / verify-before-act / post-pr-merge-ff-verify / protocol-violation-auto-detect)
    - 挂载在 ~/.claude/settings.json 的 PreToolUse / PostPRMerge / Stop 钩子位
    - 实施状态: 0 个真挂 (参考实现 ~/.omc/hooks/*.sh 写好了, user 没挂载)

  干什么:
    1. 摸底: grep -A 20 '"hooks"' ~/.claude/settings.json
    2. 比对参考实现 ~/.omc/hooks/* 4 个脚本
    3. 跟 user 确认是否挂 (framework config 改字段 必问)
    4. 挂载后跑 5 commands verify + 1 次实战触发验证
    5. 立 ADR-0042 (本机自动化挂载决策沉淀)

  验收:
    - 4 hooks 协议位 100% 挂载 (或 user 决策"参考实现就够" 走文档化)
    - settings.json diff ≤ 50 行
    - new ADR 立 (0042 整数 slot)


═══════════════════════════════════════
🚀 Phase 1 整体验收 (跑完 1.1 → 1.4 后必跑)
═══════════════════════════════════════

  - 5 fields acceptance (path / commit / push / CI / owner)
  - decision-stream 流追加 (per calm-flow §4)
  - mem0 add_memory × 1-3 条 (per post-task-recommend §3)
  - ADR 整数 slot 不抢 sub-slot (per ADR-0027 v1.1)
  - SKILL.md changelog 升 v3.2.X (本 run 沉淀)

═══════════════════════════════════════
``` 整理

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

═══════════════════════════════════════════════════════════

🚀 Phase 1 整体验收 (跑完 1.1 → 1.4 后必跑)
═══════════════════════════════════════════════════════════
  - 5 fields acceptance (path / commit / push / CI / owner)
  - decision-stream 流追加 (per calm-flow §4)
  - mem0 add_memory × 1-3 条 (per post-task-recommend §3)
  - ADR 整数 slot 不抢 sub-slot (per ADR-0027 v1.1)
  - SKILL.md changelog 升 v3.2.0 (本 run 沉淀)

═══════════════════════════════════════════════════════════
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
- 跟 v2.6.59 三段 sub-agent 协议位 (plan / execute / verify) 协同: Phase 1 跑前属于 plan 段
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

| # | 项 | Layer | 详情 |
|---|----|-------|------|
| 1 | <做了什么> | [Layer X] | <具体动作 + 数字> |
| 2 | <做了什么> | [Layer X] | <具体动作 + 数字> |
| ... | ... | ... | ... |

**小计**: N 项, 跨 [Layer X / Y / Z].

## ❌ 没做 (M 项)

| # | 项 | 原因 | 修法 (立即跑) |
|---|----|------|---------------|
| 1 | <没做到什么> | <为什么没做> | <具体修法, 含命令> |
| ... | ... | ... | ... |

**小计**: M 项, 必立即修 (per §✅ 修没做到 协议).

## 🔧 修了 (K 项) — 上面 ❌ 没做的修法跑完

| # | ❌ 没做 # | 修法 (跟上面) | 跑完实测 | 验收 |
|---|-----------|--------------|---------|------|
| 1 | 1 | <命令> | <输出> | ✅ / ❌ |
| ... | ... | ... | ... | ... |

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

| 修法类型 | 必跑 | 不可卸载给 user |
|---------|------|-----------------|
| ❌ 没做表任一项 | 立即跑修法 (单步 ≤ 5 min) | ❌ 写"下次再" / "留给 user" |
| ❌ 修法失败 | 重试 ≤ 3 次 (per §C.3.6.1 no-stuck) | ❌ 立即 STOP + AskUserQuestion |
| ❌ BLOCKED on X | 显式说明 + 触发条件 | ❌ 静默标 PENDING |
| ❌ 不可逆 / framework config / user 偏好 | AskUserQuestion (4 类必问) | ❌ 装作 know |
| ❌ 跑 ≥ 5 min 必问 user | AskUserQuestion (long-task 显式) | ❌ 默默做 |

**反模式 (永久失效)**:
- ❌ 跑完只给分数 ("完成 80%" 无 3 段)
- ❌ 修复藏在 ❌ 没做表里不显式 (违反 user 反馈 "非常详细、明显地输出")
- ❌ ❌ 没做 = 0 假装全做了 (实际 < 100%, false completion per §C.5)
- ❌ 写"下次再" / "留给 user" (违反 v3.1.0 §✅ 修没做到 协议)
- ❌ 跑完不跑 5 字段自检 (per §H Acceptance Protocol)

**联动**:
- 跟 v2.6.55 (做什么/修了什么, 短) 协同: v2.6.55 简化, v3.1.0 详 3 段
- 跟 v2.6.57 (banner, 跑前) 协同: 跑前 banner + 跑后 3 段 = 完整 UX
- 跟 v2.6.59 (三段 sub-agent) 协同: verify 段必跑 3 段 detailed 输出 (per §C.3.7)
- 跟 §C.3.6.1 (no-stuck) 协同: 修没做到失败 ≤ 3 次重试, 不循环
- 跟 §C.5 (false completion) 协同: ❌ 没做 = 0 才是真 done
- 跟 §H (Acceptance Protocol) 协同: 5 字段自检在 3 段后
