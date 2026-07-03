---
name: host-self-evolve
description: |
  本地主机 Claude Code 协调 + 自我进化 (v3.1.0 design philosophy): 提升 ~/.claude/ 跨层一致性 + §I.4 8 步循环 + N-tool fan-out internalize.
  5 Layer: Layer 0 5 commands gate / Layer 1 7 sub-task audit / Layer 2 cleanup orphan / Layer 3 N-tool fan-out / Layer A.2-A.4 5 字段自检 + 4 站 CI gate.
  触发词: 主机自升级, /host-self-evolve, self-evolve, 整理记忆, 协调 ~/.claude, 自我进化.
  必跑: memory-bench 50 题 (per §C.3.3) + 三段 sub-agent (v2.6.59) + 实测 wall-clock. 详见 [N-tool-search SSOT §1](~/.claude/rules/protocols/N-tool-search.md) + [changelog](references/changelog.md).
when_to_use: |
  Also trigger when self-evolve / skill evolve / host 升级 / 整理记忆 / claude 协调.
  sub-task 触发: frontmatter audit (15 fields / 1,536 cap) / shell unified check / memory-bench 50 题 (per §C.3.3).
  范围: ~/.claude/ + ~/.agents/skills/ 双仓.
  不适用: 单文件 typo / 文档微调 / 非 ~/.claude/ 项目 (用 website-improve).
  反模式: ❌ 标 PENDING 跳过 memory-bench / ❌ 写约束值当 wall-clock (per CASE-HOST-SELF-EVOLVE-V2-7-0) / ❌ 三段 sub-agent 物理隔离破坏 / ❌ 跑前不显示 🎯 banner / ❌ 跑完不写 ## ✅/## ❌/## 🔧 3 段. 完整见 [skill-authoring-best-practices.md](references/skill-authoring-best-practices.md).
license: MIT
metadata:
  version: "3.1.0"
  author: mykcs
  category: self-evolution
  changelog: "see references/changelog.md for v1.0.0-v3.1.0 history (v3.1.0 = 🎯 执行前 banner + ✅ 执行后 detailed 3 段 + §✅ 修没做到 协议, per user 2026-07-03 反馈)"
  tags: [self-evolution, claude, host, banner, fix-until-done]
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
