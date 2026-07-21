---
name: host-self-evolve
description: |
  本地主机 Claude Code 协调 + 自我进化 (v3.3.1 cross-reference + v3.3.0 PER Workflow): 提升 ~/.claude/ 跨层一致性 + §I.4 8 步循环 + N-tool fan-out internalize.
  5 Layer: Layer 0 5 commands gate / Layer 1 7 sub-task audit / Layer 2 cleanup orphan / Layer 3 N-tool fan-out / Layer A.2-A.4 5 字段自检 + 4 站 CI gate.
  触发词: 主机自升级, /host-self-evolve, self-evolve, 整理记忆, 协调 ~/.claude, 自我进化.
  必跑: §cwd-guard (v3.2.5/ADR-0059) + banner + §Phase 1 (ADR-0041) + §memory-bench 50 题 (ADR-0065) + PER Workflow (v2.6.59/§C.3.7) + 实测 wall-clock.
  🆕 v3.3.1 cross-reference 5 维 (per ADR-0078): CSS → [CLAUDE.local.md §6.1](~/.claude/CLAUDE.local.md) | smart-push → [MEMORY.md §7](~/.claude/memory/MEMORY.md) | calm-flow → [soul.md §3](~/.claude/rules/soul.md) | N-tool → [N-tool-search.md](~/.claude/rules/protocols/N-tool-search.md) | auto-commit → [ADR-0063](~/.claude/docs/adr/0063-claudecode-auto-commit-policy.md).
when_to_use: |
  Also trigger when self-evolve / skill evolve / host 升级 / 整理记忆 / claude 协调.
  sub-task 触发: frontmatter audit / shell unified check / memory-bench 50 题 / N-tool 协议位 audit (per ADR-0056). 详见 references/per-workflow-framework.md.
  范围: ~/.claude/ + ~/.agents/skills/ 双仓. 不适用: 单文件 typo / 文档微调.
  反模式: ❌ PENDING 跳过 memory-bench / ❌ 写约束值当 wall-clock / ❌ 三段 sub-agent 物理隔离破坏 / ❌ 跑前不显示 🎯 banner / ❌ 跑完不写 ✅/❌/🔧 3 段 / ❌ 跑完汇报 > 80 行 / ❌ 跨域规则不引 SSOT (v3.3.1). 历史 → [archive](references/changelog-v3-2-1-3-archive.md).
license: MIT
metadata:
  version: "3.3.0"
  author: mykcs
  category: self-evolution
  changelog: "v3.3.0 (2026-07-19): PER Workflow 统一抽象；新增 PER Workflow 总览节；Layer 0-3/A 明确归属 Executor/Verifier。 v3.2.5 (2026-07-17): 🔒 cwd-guard 硬约束段 (per ADR-0059 + CASE-HOST-SELF-EVOLVE-CWD-DRIFT-20260717, §E Deja Vu Fix 第 2 次触发). 跑前第 1 行必跑 `pwd` 验证 cwd = ~/.claude 或 ~/.claude/.worktrees/<branch>/, 不通过 STOP + AskUserQuestion 拍板 A 切主仓 / B 切子仓. 5 字段自检升级 6 字段 (加 cwd). 联动: ADR-0059 + case + §A.4.1 #1 + §A.4.2 #4 + §H Acceptance Protocol + CASE-PATH-DRIFT-20260714 (同类源). v3.2.4 (2026-07-14): 🔍 N-tool 协议位 audit 子任务扩展 (per ADR-0056 + CASE-META-PROTOCOL-MODIFICATION-PIPELINE-20260713 实战). 加 §1 4 路盘点协议 (记忆/灵魂 + 规则/协议 + skills/项目入口 + 实际执行层), §4 8 步修复 SOP (6 件套 grep + AskUserQuestion 拍板 4 项 + worktree + 改 N file + Python 4 维 self-verify + commit + push + PR + gh pr merge + ff + cleanup + 5 字段自检), §5 drift check 脚本交付 (主仓 commit d94fa91b, 不挂 settings.json), §6 5 IF...THEN 触发规则 + §7 7 协议级反模式扩 1 项 (跳 §20 8 步管道). 触发词 + 触发方式补 N-tool audit + 4 路盘点; user 原话 2026-07-13 '把我这个主机所有的 claude 记忆、规则、灵魂所有的搜索工具协议都列出来. 然后去看他们是否都执行同一组的协议'. 详见 references/changelog.md."
  tags: [self-evolution, claude, host, banner, fix-until-done, phase-1, life-setup, v3.2.1, default-decision, adr-0050, v3.2.2-deprecated, v3.2.3, report-minimal, phase-1-style, adr-0051-deprecated, adr-0052, v3.2.4, n-tool-audit-fix-sop, adr-0056, meta-protocol-pipeline, v3.2.5, cwd-guard, adr-0059, deja-vu-fix, per-workflow, v3.3.0]
version: "1.0.0"
author: "mykcs"
last_updated: "2026-07-19"
---

# 主机自升级 Skill (host-self-evolve v3.3.0)

## 🔒 §cwd-guard 段 (v3.2.5 立, 2026-07-17, per ADR-0059 + §E Deja Vu Fix Protocol)

> **触发**: CASE-HOST-SELF-EVOLVE-CWD-DRIFT-20260717 (本 run 摸底阶段 cwd drift, 第 2 次同类 30 天阈值到硬约束, 跟 CASE-PATH-DRIFT-20260714 同根因)
>
> **协议位**: host-self-evolve v3.2.5+ 跑前**必跑** cwd 验证硬规则, 不通过则**立即 STOP + AskUserQuestion**, 不继续执行 Layer 0-3 摸底.

**硬规则 (5 条, per ADR-0059 §2.1)**:

1. **Rule 1**: 跑前第 1 行命令必跑 cwd 验证:
   ```bash
   pwd  # 期望: /Users/myk/.claude (主仓) 或 /Users/myk/.claude/.worktrees/<branch>/ (worktree 模式)
   ```

2. **Rule 2**: pwd 输出 ≠ `/Users/myk/.claude` AND ≠ `/Users/myk/.claude/.worktrees/*` → 立即 STOP + AskUserQuestion 拍板 2 选项:
   - **A**: `cd ~/.claude && pwd` 切主仓 (推荐, 99% case)
   - **B**: user 显式说"跑子仓 X" 才切子仓

3. **Rule 3**: pwd 输出 = `/Users/myk/.claude/.worktrees/<branch>/` → 算合规 (worktree 模式), 继续.

4. **Rule 4**: 后续所有 `git status` / `git log` / `git remote` / `git rev-list` 命令**禁用** `git -C` 强切, 改直接 `git status` 走 cwd (因为 cwd 已合规). 避免主仓 / 子仓 / worktree 混层.

5. **Rule 5**: §H 5 字段自检表升级 6 字段 (path / cwd / commit / push / CI / owner), cwd 字段必填 `~/.claude` 主仓绝对路径, 不填子仓 / worktree / 项目仓路径.

**反模式 (永久失效, 5 条, per ADR-0059 §2.3)**:

1. ❌ host-self-evolve 跑前不 verify cwd = 摸底混层 (本 case 真因)
2. ❌ 5 字段自检用 `git -C ~/.claude` 强切主仓就够了 = 不够, 摸底阶段已混层
3. ❌ 跑完汇报不察觉 cwd 错 = 跑完自检缺 cwd 字段
4. ❌ cwd drift 当单次 bug 修, 不立 §E Deja Vu = 同类会再出现
5. ❌ 立 ADR 不 grep 现状 6 件套 = 重复劳动

**联动**: ADR-0059 (本段协议位) + CASE-HOST-SELF-EVOLVE-CWD-DRIFT-20260717 (本段起源) + CASE-PATH-DRIFT-20260714 (同类源) + §E Deja Vu Fix Protocol (per `rules/process.md` §E) + §A.4.1 #1 Repository Context Verification + §A.4.2 #4 Path Validation + §H Acceptance Protocol 5 字段 → 6 字段升级

**历史 record**:
- 2026-07-17 v3.2.5: 立 (per ADR-0059 + CASE-HOST-SELF-EVOLVE-CWD-DRIFT-20260717 + §E Deja Vu Fix Protocol 第 2 次触发 + 整数 slot 0059)

---

## 🔁 PER Workflow 总览 (v3.3.0 立, per references/per-workflow-framework.md)

> **来源**: 本技能统一采用 `~/.agents/skills/website-improve/references/per-workflow-framework.md` 的 Plan → Execute → Verify (PER) 三段抽象。
> **协议位**: host-self-evolve v3.3.0+ 把原先"三段 sub-agent (plan/execute/verify)"提升为**具名 PER Workflow**, 角色/产物/反模式全部对齐框架, 不另起炉灶。

### PER 与 host-self-evolve 的映射

| PER 角色 | 在 host-self-evolve 中负责 | 产出 artifact |
|----------|---------------------------|---------------|
| **Planner** | 输出 🎯 banner + 🌱 Phase 1 (Life/Setup) 段; 将 Layer 0-3 拆成可执行任务; 识别风险并决定 scope (默认全套 / 只跑 X) | `plan.json` / `plan.md` |
| **Executor** | 跑 Layer 0 (5 commands gate) → Layer 1 (7 sub-tasks, 含 N-tool 协议位 audit) → Layer 2 (cleanup orphan) → Layer 3 (N-tool fan-out) | `exec-log.json` / `exec-log.md` |
| **Verifier** | 跑 Layer A 5/6 字段自检 (path / cwd / commit / push / CI / owner) + memory-bench score gate + 4 站 CI gate; FAIL 则打回 Executor 重做 | `verdict.json` / `verdict.md` |

### Layer → PER 归属

| Layer | PER 归属 | 说明 |
|-------|----------|------|
| Phase 1 (Life/Setup) | **Planner 输出** | 跑前必输协议位, 属于 plan 阶段 |
| Layer 0-3 | **Executor 任务** | 实际执行摸底/修复/进化 |
| Layer A | **Verifier 任务** | 验收与自检, 与执行物理隔离 |

### 核心反模式 (从 PER 框架引入, 永久失效)

1. ❌ **1 个 sub-agent 跑完 3 角色**
2. ❌ **Executor 自己标 done**
3. ❌ **Verifier FAIL 还强行 ship**

> 完整 6 条反模式见 `references/per-workflow-framework.md` §反模式。

**联动**:
- `references/per-workflow-framework.md` (SSOT)
- v3.1.0 banner 段 / v3.2.0 Phase 1 段 (Planner 产出)
- v3.2.1 default decision 段 (Planner scope/risk 决策, user-override, 不变)
- Layer 0-3 详细协议 (Executor 执行范围)
- v3.2.8 memory-bench 必跑段 + v3.2.9 report-card 模板段 (Verifier 验收项)

---

## 🎯 v3.2.1 default decision 段 (2026-07-10 立, per ADR-0050)

> **触发**: user 2026-07-10 主机自升级 run 拍板原话 (2 段):
>   1. "修改 skill 以后不许问这个问题, 直接全套"
>   2. "修改 skill 以后不许问这个问题, 直接三段串行"
> **协议位**: host-self-evolve v3.2.1+ 跑前**不再问** "Run 范围" + "执行模式" 2 类决策, 默认走自决路径

**默认决策 (per ADR-0050 user-override)**:
- ✅ **Run 范围**: 默认全套 (Phase 1.1 → 1.4), user 显式说"只跑 X" 才拆 sub-task
- ✅ **执行模式**: 默认三段串行 (plan / execute / verify 物理隔离, per v2.6.59 + §C.3.7)
- ✅ **遗留 dirty 改动收口 (v3.2.6 新增, per user 2026-07-17 拍板)**: 摸底 Layer 0 发现工作树有未提交改动 (M / ?? untracked, 上个 session 收尾残留) → **默认纳入本轮一起收口, 不再 AskUserQuestion "怎么处理遗留改动"**. user 原话 "这批遗留改动本来就是这次自升级要处理的, 直接纳入本轮一起收口, 不要再停下来问". 例外: 遗留改动里含 4 类必问白名单 (framework config / user 偏好 / 不可逆 / user 显式说) 时, 仅对该子项走 AskUserQuestion, 其余 dirty 项照常纳入.
- ✅ **跑完摸底默认继续跑剩余 sub-task (v3.2.7 新增, per user 2026-07-18 拍板)**: 跑完单次摸底收口后**默认继续跑剩余 sub-task** (Phase 1.2 / 1.3 + Layer 1-3), **不再 AskUserQuestion "要不要继续"**. user 原话 "修改技能以后，不要出现这个情况，都是默认继续跑". 跟 v3.2.6 user-override 同根因, 跑后不主动停下问 user. 4 类必问白名单保留 (不可逆 / framework config / user 偏好 / user 显式说).
- ✅ **memory-bench 50 题必跑 (v3.2.8 新增, per user 2026-07-18 拍板)**: host-self-evolve run **必跑 memory-bench 50 题** (per §C.3.3 v2.6.56 强约束), **不允许 PENDING 跳过**. user 原话 "把'memory-bench 50 题'作为 host-self-evolve 必跑". 跑分结果 (weighted score) 必落 `~/.agents/skills/host-self-evolve/reports/memory-bench/{date}-v{n}.md`. score < 60 target 立即修协议. 4 类必问白名单保留 (跑分中途 token 限制 / opus API 失败 / 跑分发现 P0 安全问题 / user 显式说 走 AskUserQuestion).
- ✅ **report-card 模板 11 行总表标准化 (v3.2.9 新增, per user 2026-07-18 拍板)**: memory-bench 跑分报告 (per ADR-0065 + §C.3.3 v2.6.56) **必走 11 行总表 report-card 标准模板**, 字段顺序 + 单位 + 加权方法 100% 一致 (便于 baseline v1 vs SOTA v8 vs ablation-5 横向对比). user 原话 "把 §memory-bench 必跑段扩展为 report-card 模板". 11 行字段: run_id / timestamp / host / skill_version / model / judge / recall_total / consistency_total / compliance_total / weighted_score / target_met. 4 类必问白名单保留 (格式争议 / 字段命名冲突 / user 显式说 / 跑分失败 走 AskUserQuestion).
- ✅ **判定流程**:
  1. user 触发 host-self-evolve → 立即加载 v3.2.0 banner 段 + v3.2.0 Phase 1 段 + v3.2.1 default decision 段 (本段)
  2. **不再 AskUserQuestion** "Run 范围" + "执行模式" 2 类问题
  3. 默认跑全套 + 三段串行, 走 execute 段
  4. user 在跑中显式说"只跑 X" → 立即切单 sub-task, 不停 run
  5. 跑完按 v3.1.0 §✅ 3 段 detailed 输出 (✅ 做了 / ❌ 没做 / 🔧 修了)

**保留 AskUserQuestion 触发白名单** (硬约束 + user override 协同, 跟 calm-flow §6 反转模式 4 类硬约束对齐):
1. **不可逆操作**: rm / push main / reset hard / 删数据库表
2. **framework config 改字段**: settings.json / hooks 挂载 / SKILL.md frontmatter
3. **user 偏好变更**: 命名 / 风格 / 路线选择 / user 哲学
4. **user 显式说**: "立刻决策 / 快问我 / 先问后做 / 不要自决"

**反模式 (永久失效, 6 条, per ADR-0050 §5)**:
1. ❌ 跑 host-self-evolve 还问 "Run 范围" / "执行模式" = 违反 user-override
2. ❌ 跑全套后假装"只跑 X" (实跑全部但报告说"我没跑完") = 违反 §C.5 false completion
3. ❌ 拆三段 sub-agent 后用 1 个 agent 跑完 = 违反 §C.3.7 物理隔离硬约束
4. ❌ user 显式说"只跑 X" 还跑全套 = 违反 user override 优先级
5. ❌ 把本段"不再问"推广到所有 AskUserQuestion = 违反 4 类必问硬约束保留
6. ❌ 跑完不输出 v3.1.0 §✅ 3 段 detailed = 违反 v3.1.0 硬约束
7. ❌ 摸底 Layer 0 发现工作树 dirty 就停下问 "怎么处理遗留改动" = 违反 v3.2.6 user-override (直接纳入本轮收口)
8. ❌ 跑完单次摸底收口后 AskUserQuestion "要不要继续跑 Layer 1-3" = 违反 v3.2.7 user-override (默认继续跑剩余 sub-task, per ADR-0064)
9. ❌ host-self-evolve 跑分 PENDING 跳过 memory-bench 50 题 = 违反 v3.2.8 user-override (memory-bench 必跑不跳过, per ADR-0065)
10. ❌ memory-bench 跑分报告缺 11 行总表任一字段 / 字段顺序错乱 / score 用百分制 / target_met 不填 = 违反 v3.2.9 report-card 模板 (per ADR-0066)

**联动**:
- 跟 v3.1.0 banner UX (跑前) + v3.2.0 Phase 1 段 (跑前) 协同: 三段顺序 = banner → Phase 1 → v3.2.1 default decision → execute
- 跟 v3.1.0 §✅ 3 段 detailed (跑后) 协同: 本段跑前决策 + v3.1.0 跑后报告 = 完整 UX
- 跟 ADR-0050 v1.0 (整数 slot 0050) 协同: 本段是 ADR-0050 §3 SKILL.md 改动清单落地
- 跟 calm-flow §6 反转模式协同: 4 类必问硬约束保留 = calm-flow 反转触发
- 跟 §C.3.7 三段 sub-agent 协议位统一协议 (v2.6.60) 协同: 本段默认触发协议位执行
- 跟 CASE-HOST-SELF-EVOLVE-PHASE-1-LIFE-SETUP-20260708 协同: 本段立条源 (user 反馈触发)

**历史 record**:
- 2026-07-10 v3.2.1: 立 (ADR-0050 整数 slot 0050 + user-override 落点 + 本段嵌入 SKILL.md)
- 2026-07-17 v3.2.6: 加第 3 条默认决策 (遗留 dirty 改动纳入本轮收口, 不再问) + 反模式 #7 (per user 2026-07-17 拍板)
- 2026-07-18 v3.2.7: 加第 4 条默认决策 (跑完摸底默认继续跑剩余 sub-task, 不再问) + 反模式 #8 (per user 2026-07-18 拍板 + ADR-0064 整数 slot)
- 2026-07-18 v3.2.8: 加第 5 条默认决策 (memory-bench 50 题必跑, 不允许 PENDING 跳过) + 反模式 #9 (per user 2026-07-18 拍板 + ADR-0065 整数 slot)
- 2026-07-18 v3.2.9: 加第 6 条默认决策 (memory-bench 跑分报告 11 行总表 report-card 模板标准化) + 反模式 #10 (per user 2026-07-18 拍板 + ADR-0066 整数 slot)

---

## 🎯 v3.2.9 report-card 模板段 (2026-07-18 立, per ADR-0066)

> **触发**: user 2026-07-18 拍板 "把 §memory-bench 必跑段扩展为 report-card 模板 (跑分报告 11 行总表标准化)". 跟 §C.3.3 v2.6.56 强约束 + §H 5 字段自检 + ADR-0016 memory-bench 归属决策 协同.
>
> **协议位**: memory-bench 跑分报告 (per ADR-0065 + §C.3.3 v2.6.56) **必走 11 行总表 report-card 标准模板**, 字段顺序 + 单位 + 加权方法 100% 一致.

**11 行总表标准模板**:

| # | 字段 | 格式 | 单位 |
|---|------|------|------|
| 1 | run_id | `memory-bench-{YYYY-MM-DD}-v{n}` | string |
| 2 | timestamp | ISO 8601 + timezone | string |
| 3 | host | `mykcs/{local-path}` | string |
| 4 | skill_version | `v{X.Y.Z}` | semver |
| 5 | model | `claude-{sonnet\|opus\|haiku}` + version | string |
| 6 | judge | `opus-as-judge` + version | string |
| 7 | recall_total | N/50 (sum) | 整数 |
| 8 | consistency_total | N/15 (sum) | 整数 |
| 9 | compliance_total | N/12 (sum) | 整数 |
| 10 | weighted_score | `0.0 - 2.0` 5 级 (opus-as-judge) | float |
| 11 | target_met | `✅ ≥ 60 / ❌ < 60` | boolean |

**模板示例** (per §C.3.3 v2.6.56 实战):

```markdown
| # | 字段 | 值 |
|---|------|-----|
| 1 | run_id | memory-bench-2026-07-18-v1 |
| 2 | timestamp | 2026-07-18T15:30:00+08:00 |
| 3 | host | mykcs@/Users/myk/.claude |
| 4 | skill_version | v3.2.9 |
| 5 | model | sonnet 4.6 |
| 6 | judge | opus-as-judge v4.5 |
| 7 | recall_total | 42/50 |
| 8 | consistency_total | 13/15 |
| 9 | compliance_total | 11/12 |
| 10 | weighted_score | 0.93 |
| 11 | target_met | ✅ ≥ 60 |
```

**失败处理** (per §C.3.6.1 no-stuck 协同):
- 跑分报告缺 11 行总表任一字段 → 报告无效, 立即重跑
- 跑分报告字段顺序错乱 → 报告无效, 立即重排
- weighted_score 用百分制 (0-100) 而非 5 级 (0-2.0) → 报告无效, 立即改回
- target_met 字段不填 / 填 "YES" / 填 "是" → 报告无效, 必用 ✅/❌
- score < 60 target + 11 行总表完整 → 走 §v3.2.8 立即修协议

**横向对比协议** (per §C.3.3 v2.6.56 baseline compare):
- baseline v1 vs SOTA v8 vs ablation-5: 11 行总表字段顺序 100% 一致才能对比
- weighted_score 差异 ≥ 0.1 = 实质改善 (跨版本提交决策依据)
- target_met ❌ → 不接受新版本 (除非 user 显式 override)

**反模式 (永久失效, 5 条, per ADR-0066 §4)**:
1. ❌ 跑分报告缺 11 行总表任一字段 = 违反 v3.2.9 段
2. ❌ 跑分报告字段顺序错乱 (e.g. recall_total 在 consistency_total 前) = 违反 report-card 模板
3. ❌ weighted_score 用百分制 (0-100) 而非 5 级 (0-2.0) = 违反 §C.3.3 v2.6.56
4. ❌ target_met 字段不填 / 填 "YES" / 填 "是" = 违反 report-card 模板 (必用 ✅/❌)
5. ❌ 跑分报告跑通后不跟 baseline / SOTA 横向对比 = 违反 §C.3.3 v2.6.56 baseline compare

**联动**:
- 跟 ADR-0065 (memory-bench 必跑) 协同 — 本 ADR 立 report-card 模板 = 必跑段的下一步标准化
- 跟 §C.3.3 v2.6.56 (memory-bench 强约束) + §C.3.3 v2.6.46 (重版约束) 协同
- 跟 ADR-0016 (memory-bench into rich-audit, 归属决策) 协同
- 跟 §C.3.6.1 no-stuck 协议 协同
- 跟 §H Acceptance Protocol (5 字段自检 → 7 字段新增 row 7 format) 协同

**历史 record**:
- 2026-07-18 v3.2.9: 立 (per user 2026-07-18 拍板 "把 §memory-bench 必跑段扩展为 report-card 模板" + ADR-0066 整数 slot 0066)

---

## 🎯 v3.2.8 memory-bench 必跑段 (2026-07-18 立, per ADR-0065)

> **触发**: user 2026-07-18 原话 "把'memory-bench 50 题'作为 host-self-evolve 必跑". 跟 §C.3.3 v2.6.56 强约束 + §C.3.3 v2.6.46 重版约束 + §C.3.6.1 no-stuck + §H 5 字段自检 协同.
>
> **协议位**: host-self-evolve v3.2.8+ run **必跑 memory-bench 50 题** (per §C.3.3 v2.6.56), **不允许 PENDING 跳过**, 跑分结果 (weighted score) 必落 `~/.agents/skills/host-self-evolve/reports/memory-bench/{date}-v{n}.md`.

**跑分流程** (per §C.3.3, 7 步):

| Step | 行为 | 输出 |
|------|------|------|
| 1 | 读 `~/.agents/skills/host-self-evolve/references/memory-bench-50q-sample.json` | 50 题题库 |
| 2 | 50 题拆 50 个 sonnet session, 每题独立 (防前后题污染) | 50 session 报告 |
| 3 | opus-as-judge 评分 (5 级: 0 / 0.5 / 1.0 / 1.5 / 2.0) | 评分报告 |
| 4 | 15 consistency 跨源 grep + opus-judge 语义 | consistency 报告 |
| 5 | 12 compliance 触发场景, 跑对应 hook/script | compliance 报告 |
| 6 | 4 metric 加权求和 → total score | total score |
| 7 | 写 11 行总表到 `~/.agents/skills/host-self-evolve/reports/memory-bench/{date}-v{n}.md` | 报告文件 |

**失败处理** (per §C.3.6.1 no-stuck 协同):
- 跑分中途 token 限制 / opus API 失败 → 暂停 + 报告 user + AskUserQuestion (走 4 类必问白名单)
- 跑分发现 P0 安全问题 → 立即停止 + 报告 user
- 跑分时间长 (3h) → 拆多 session, 进度写 decision-stream

**score < 60 target** → 立即修协议 (per §C.3.3 v2.6.56 强约束).

**反模式 (永久失效, 5 条, per ADR-0065 §4)**:
1. ❌ host-self-evolve 跑分 PENDING 跳过 memory-bench 50 题 = 违反 v3.2.8 段
2. ❌ 跑分报告不写 weighted total score / 不写 11 行总表 = 违反 §C.3.3 v2.6.56 强约束
3. ❌ 跑分中途 token 限制不报 user 不 AskUserQuestion = 违反 §C.3.6.1 no-stuck
4. ❌ 跑分 score < 60 target 不立即修协议 = 违反 §C.3.3 v2.6.56
5. ❌ 跑分报告写到非 `~/.agents/skills/host-self-evolve/reports/memory-bench/` 路径 = 违反 §C.3.3 路径规约

**联动**:
- 跟 §C.3.3 v2.6.56 强约束 + §C.3.3 v2.6.46 重版约束 协同
- 跟 ADR-0016 (memory-bench into rich-audit, user 立的归属决策) 协同
- 跟 ADR-0065 (本 ADR, 整数 slot 0065) 协同
- 跟 §C.3.6.1 no-stuck 协议 协同
- 跟 §H Acceptance Protocol 5 字段自检表 (新增第 6 字段: score) 协同

**历史 record**:
- 2026-07-18 v3.2.8: 立 (per user 2026-07-18 拍板 "把 memory-bench 50 题作为 host-self-evolve 必跑" + ADR-0065 整数 slot 0065)

---

## 🎯 v3.2.3 汇报极简化段 (2026-07-10 立, per ADR-0052)

> **触发**: user 反馈 "还是不够还是不够整洁, 完全模仿 §Phase 1 段格式就好了"
> **协议位**: host-self-evolve v3.2.3+ 跑完汇报 ≤ §Phase 1 段同长度 (~80 行), 严格 1:1 复刻

**骨架** (跟 §Phase 1 段 1:1, 见 §Phase 1 段):

```
🌱 Run Summary — <主题> — 完整说明
═══════════════════════════════════════

🎯 目的

  <一句话, ≤ 3 行>

───────────────────────────────────────
🧩 <N> 件事 — 清单
───────────────────────────────────────

📦 <事项 1>

  一句话: <本事项目的, ≤ 1 行>

  现状:
    - <事实 1>
    - <事实 2>

  干什么:
    1. <动作 1>
    2. <动作 2>

  验收:
    - <验收 1>
    - <验收 2>

═══════════════════════════════════════
🚀 整体验收
═══════════════════════════════════════

  - path: <文件路径>
  - commit: <hash | msg>
  - push: ahead/behind 0 0
  - CI: <state>
  - owner: <mykcs / wangrui2025>
```

**字段约束**:
- 总长度 ≤ 80 行 (跟 §Phase 1 段同)
- 不写 BLOCKED 段 (走 AskUserQuestion, 不在汇报)
- 不写 ⏱️ wall clock 段 (灵魂 v6 自检机制已立, 不重报)
- 不写任务后建议段 (post-task-recommend v3 清理后, 走 mem0 自动沉淀)
- 不用 emoji (✅❌🔧) 替代内容

**反模式 (永久失效, 6 条)**:
1. ❌ 跑完汇报 > 80 行
2. ❌ 跑完汇报含 BLOCKED 段
3. ❌ 跑完汇报含 ⏱️ wall clock 段
4. ❌ 跑完汇报含任务后建议段
5. ❌ 跑完汇报含自检 emoji (✅❌🔧)
6. ❌ 跑完汇报堆 "联动 cross-references" 段

**联动**: v3.2.2 §汇报格式段 废弃 (太复杂), v3.2.3 取代 (极简); ADR-0051 v3.2.2 废弃, ADR-0052 v3.2.3 立

**历史 record**:
- 2026-07-10 v3.2.3: 立 (ADR-0052 整数 slot 0052 + user-override 2 次反馈 + 跑完汇报极简化 ≤ 80 行)

---

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

## 🔁 实战案例沉淀段 (per ADR-0056 + CASE-N-TOOL-DRIFT-CLEANUP-20260713, 2026-07-13 立)

> **目的**: host-self-evolve 跑过 1 次后, 必沉淀 "检查→修复→沉淀→复用" 全流程实战, 后续 run 直接复用, 不重跑.

### 案例 1: N-tool 协议位 drift 全面清理 (per ADR-0056, 2026-07-13)

**触发**: user 问 "把我这个主机所有的 claude 记忆、规则、灵魂所有的搜索工具协议都列出来. 然后去看他们是否都执行同一组的协议". claudecode 跑 4 维 audit (主仓 + 子仓 + 4 active 仓 + mem0), 发现 **6 P0 字面散落 + 20 P1 旧名残留 + 110+ P2 历史档案** = 协议位字面定义跟 SSOT 不一致 (漏 mmx 第 6 工具).

**5 件事 (一句话 + 现状 + 干什么 + 验收)**:

| # | 一句话 | 现状 | 干什么 | 验收 |
|---|--------|------|--------|------|
| 1 | **6 件套 grep 现状** (cross-session-grep §1) | 立 ADR 前必跑 | 扫 `~/.claude/` + `~/.agents/skills/` 4 维, 命中已有沉淀 (ADR-0054/0055/CASE-SEARCH/CASE-META) | ✅ 6 件命中, 走引用路径 |
| 2 | **AskUserQuestion 拍板路线** | 路线分叉 + ≥3 候选 + user 显式拍板 | 给 4 选项 (A 全清 / B 只 P0 / C 只删旧副 SSOT / D 保持现状), user 选 **A + 整数 slot 0056 + worktree feat/n-tool-drift-cleanup** | ✅ A + 0056 + worktree 名 3 件 |
| 3 | **§C.3.1 worktree 立** | 不可逆 + multi-file | `git worktree add .claude/worktrees/n-tool-drift -b feat/n-tool-drift-cleanup` 基于 main HEAD b090e9db | ✅ worktree 立, working dir 干净 |
| 4 | **改 N file (worktree 绝对路径)** | worktree 模式 | 主仓 4 file (process.md §C.3.5/§C.3.6/§F + 3 references) + 子仓 2 file (loop-engineering + 子仓副 SSOT redirect) + 3 沉淀 (ADR-0056 + CASE + decision-stream) = 9 file 改 | ✅ 6 改 + 3 立 = 9 file |
| 5 | **commit + push + PR + ff verify + worktree cleanup + 5 字段自检** | 闭环前必跑 | 主仓 commit 0985d1d5 + b9aaa973 → PR #53 squash merged → ahead/behind 0/0 (rebase origin/main 修复 silent fail) → worktree removed; 子仓 commit 6e5f350 → push main → ahead/behind 0/0 | ✅ 2 PR merged + 2 仓 ahead/behind 0/0 + worktree cleanup |

**整体验收 (5 项)**:

| # | 字段 | 验收标准 | 实际 |
|---|------|---------|------|
| 1 | path | 主仓 ~/.claude + 子仓 ~/.agents/skills | ✅ 2 仓 |
| 2 | commit | git log -1 有新 commit | ✅ 主仓 9897e9ea (PR #53 squash) + 子仓 6e5f350 |
| 3 | push | ahead/behind 0/0 | ✅ 双仓 0/0 |
| 4 | CI | gh api .../commits/HEAD/status green | ✅ pending (新 commit, GitHub Actions 待跑) |
| 5 | owner | mykcs/.claude + mykcs/myk-skills | ✅ 双账号隔离正确 |

**踩坑 (必沉淀)**: **gh pr merge stdout 空 ≠ 成功** (per ADR-0026 必读 body 协议位). 修法: 必跑 `gh pr view --json state` 实测 + post-pr-merge-ff-verify.sh hook 兜底. 本 case silent fail 后 hook 检测到 ahead/behind 1/1 diverged, §C.6 5 步诊断发现 ahead 是 user prep hook 自动 commit (auto-feishu-digest case, 跟 N-tool drift 无关), `git rebase origin/main` 修复.

**未来复用 (下次跑前必跑)**:
- 任何协议位散落 audit → 走本案例骨架 (6 件套 grep → AskUserQuestion → worktree → 改 N file → commit+push+PR+ff+cleanup+5 字段)
- 必跑 `post-pr-merge-ff-verify.sh` hook (per `~/.claude/rules/post-pr-merge-ff-verify-rule.md`) 防 gh PR 谎报
- 必跑 `gh pr view --json state` 实测 (per ADR-0026) 不要信 stdout 空
- §C.6 5 步 false-positive 诊断 protocol: ahead/bebehind diverged 必先看 ahead 是谁 (prep hook 自动 commit vs N-tool drift 相关)

**联动**: §20 8 步管道 (per ADR-0055) + §C.3.1 worktree + §C.3.2 PR auto-merge + post-pr-merge-ff-verify hook + §H 5 字段自检 + ADR-0056 + CASE-N-TOOL-DRIFT-CLEANUP-20260713

## 🔍 N-tool 协议位 audit 子任务 (per ADR-0056 + user 2026-07-13 拍板, 2026-07-13 立 + 2026-07-14 扩展)

> **触发 (user 原话 2026-07-13)**: "把我这个主机所有的 claude 记忆、规则、灵魂所有的搜索工具协议都列出来. 然后去看他们是否都执行同一组的协议, 就是我规定的 N 重网络搜索工具协议". claudecode 跑 host-self-evolve 时, **必**跑本子任务 (硬约束, 不可跳, 不依赖 user 重复指令).
>
> **目的**: 自动检测协议位字面散落 + 实际执行层 (5/6 vs 6/6) drift, 防止 SSOT 收口后子协议位漂移. **不止审计字面, 必修复到全机 active 入口都直指 SSOT** (per §20 8 步管道).
>
> **协议位**: 主 SSOT = `~/.claude/rules/protocols/N-tool-search.md` v1.1.2 (N 当前 = 6 = MiniMax + kimi-webbridge + anysearch + WebFetch + exa + mmx). claudecode 必跑 4 路盘点 + 4 维 audit, 命中 drift 走 §20 8 步管道 + 立 ADR (整数 slot).

### §1 4 路盘点协议 (新增, 2026-07-14 立, per CASE-META-PROTOCOL-MODIFICATION-PIPELINE-20260713 实战)

**触发**: 任何 host-self-evolve 跑前必跑本段, 跟 4 维 audit 并列, **不跳过**. 4 路盘点 = 列全机所有 "Claude 记忆/规则/灵魂/搜索工具协议" 入口 + 判定 active vs 历史 + 收口状态.

| # | 维度 | 范围 | 关键判定 |
|---|------|------|---------|
| 1 | **记忆/灵魂层** | `~/.claude/memory/` + `~/.claude/MEMORY.md` + `~/.claude/CLAUDE.local.md` § HOT FACTS + `~/.mem0/` 本地 config/log | active 入口 (auto-memory 加载 / SessionStart 注入 / 远端 mem0 索引) 必须直指 SSOT; 旧"5-tool" / "Force-All-Search" 字面必须补 N-tool pointer + 历史标 |
| 2 | **规则/协议层** | `~/.claude/rules/**` + `~/.claude/docs/adr/**` + `~/.claude/CLAUDE.md` + `~/.claude/CLAUDE.local.md` | SSOT 唯一性 + 全仓 active 规则引用同一 SSOT + protocols/README 死链 0 + 副 SSOT redirect 完整 |
| 3 | **skills/项目入口层** | `~/.agents/skills/*/SKILL.md` + `~/.agents/skills/*/references/` + 4 active 项目仓 `CLAUDE.md` (mysite / GDKVM / OSA / content2html 或 academic) | skills description 顶部直指 SSOT + 子仓 protocol/references/ 含历史标不裸 5-tool + 项目仓 CLAUDE.md 至少 1 行 N-tool pointer |
| 4 | **实际执行层** | `~/.claude/settings.json` mcpServers + `~/.claude.json` mcpServers + 实际 Claude session 内可用工具列表 (区分物理 daemon/CLI 存在 vs session 路由可达) | N 个工具并行 fan-out 有 orchestrator 或强提示词约束; 缺工具走 §3 降级矩阵; 当前 session 路由可达 ≥ N-1 (kimi-webbridge 是已知 weakest link, 仅作 Layer 2 弱约束) |

### §2 4 维 audit 协议 (per ADR-0056 §1.1)

| # | 维度 | 跑法 | 期望命中 |
|---|------|------|---------|
| 1 | **主仓 grep** | `grep -rE "5-tool\|5-tool-search" ~/.claude/{rules,protocols,memory,docs,knowledge/cases,decision-stream}/` | 0 命中 (字面) + 历史段除外 |
| 2 | **子仓 grep** | `grep -rE "5-tool\|5-tool-search" ~/.agents/skills/*/SKILL.md ~/.agents/skills/*/references/` | 0 命中 (字面) |
| 3 | **active 仓 grep** | `grep -rE "5-tool\|5-tool-search" ~/Repo/webs/{active,academic}/` 或 `~/Claude/Projects/webs/` (per user 实际路径) | 0 命中 (跟 N-tool 无关) |
| 4 | **N-tool pointer verify** | `grep -rE "N-tool-search\.md" ~/.claude/rules/` + `~/.claude/rules/protocols/N-tool-search.md` 存在 + 版本 v1.1+ | ≥ 1 (主 SSOT 必存) |

> **路径例外**: 第 3 维跑路径 per user 实际配置, 旧 `~/Repo/webs/{active,academic}/` 跟新 `~/Claude/Projects/webs/` 都接受 (per v3.2.3 §Path Validation).

### §3 判定分支

| 命中 | 严重度 | 修法 |
|------|-------|------|
| 主仓/子仓 5-tool 字面 + 协议位段落 | 🔴 P0 | 走 §20 8 步管道 + 立 ADR (整数 slot) |
| 主仓/子仓 5-tool 字面 + changelog/历史段 | ⚪ P2 | 不动 (历史演进证据) |
| 主仓/子仓 5-tool 字面 + 反模式段落 | ⚪ P2 | 不动 (反模式说明) |
| 副 SSOT 整篇 v2.9 协议位 | 🔴 P0 | 整篇 redirect → N-tool-search.md v1.1.2 |
| 协议位列 < 6 工具 (漏 mmx) | 🔴 P0 | 1 行补 mmx → 完整协议位 |
| N-tool-search.md 不存在 / 版本 < v1.1 | 🔴 P0 | 立即 git restore 或升级 (丢失主 SSOT) |
| 当前 session 路由 < N (缺 kimi-webbridge) | 🟡 P1 | 报告 "⚠️ N-tool 降级到 M-tool" + 引导 user 跑 §20 路径, 不 fail-fast |
| SSOT 内部歧义 (exa '最后兜底' / §3.1 工具计数错) | 🟡 P1 | 立 v1.x.y patch (per §9 changelog), 跨 5 仓 sync |

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

## 触发方式 (中英文, 12 词)

| 中文 | 英文 |
|------|------|
| 主机自升级 | /host-self-evolve |
| 自我升级 | self-evolve |
| 整理记忆 | host evolve |
| claude 协调 | claude coord |
| 协调 ~/.claude | evolve claude |
| evolve 整体 | full self-evolve |
| **N-tool 协议位 audit** | **N-tool audit** |
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
  ├─ [Layer 1.0] **N-tool 协议位 drift audit** (per ADR-0056, 2026-07-13 立, 强制必跑 — 见下文 §Layer 1.0 N-tool 协议位 drift audit 协议)
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
  - 用 PER Workflow 跑 (计划 / 执行 / 验收 三个人独立)
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
- 跟 PER Workflow 协同: verify 段必跑 3 段 detailed 输出 (per §C.3.7)
- 跟 §C.3.6.1 (no-stuck) 协同: 修没做到失败 ≤ 3 次重试, 不循环
- 跟 §C.5 (false completion) 协同: ❌ 没做 = 0 才是真 done
- 跟 §H (Acceptance Protocol) 协同: 5 字段自检在 3 段后
