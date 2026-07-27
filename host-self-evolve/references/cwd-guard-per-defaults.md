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

| PER 角色     | 在 host-self-evolve 中负责                                                                                                            | 产出 artifact                   |
| ------------ | ------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------- |
| **Planner**  | 输出 🎯 banner + 🌱 Phase 1 (Life/Setup) 段; 将 Layer 0-3 拆成可执行任务; 识别风险并决定 scope (默认全套 / 只跑 X)                    | `plan.json` / `plan.md`         |
| **Executor** | 跑 Layer 0 (5 commands gate) → Layer 1 (7 sub-tasks, 含 N-tool 协议位 audit) → Layer 2 (cleanup orphan) → Layer 3 (N-tool fan-out)    | `exec-log.json` / `exec-log.md` |
| **Verifier** | 跑 Layer A 5/6 字段自检 (path / cwd / commit / push / CI / owner) + memory-bench score gate + 4 站 CI gate; FAIL 则打回 Executor 重做 | `verdict.json` / `verdict.md`   |

### Layer → PER 归属

| Layer                | PER 归属          | 说明                           |
| -------------------- | ----------------- | ------------------------------ |
| Phase 1 (Life/Setup) | **Planner 输出**  | 跑前必输协议位, 属于 plan 阶段 |
| Layer 0-3            | **Executor 任务** | 实际执行摸底/修复/进化         |
| Layer A              | **Verifier 任务** | 验收与自检, 与执行物理隔离     |

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
>
> 1. "修改 skill 以后不许问这个问题, 直接全套"
> 2. "修改 skill 以后不许问这个问题, 直接三段串行"
>    **协议位**: host-self-evolve v3.2.1+ 跑前**不再问** "Run 范围" + "执行模式" 2 类决策, 默认走自决路径

**默认决策 (per ADR-0050 user-override)**:

- ✅ **Run 范围**: 默认全套 (Phase 1.1 → 1.4), user 显式说"只跑 X" 才拆 sub-task
- ✅ **执行模式**: 默认三段串行 (plan / execute / verify 物理隔离, per v2.6.59 + §C.3.7)
- ✅ **遗留 dirty 改动收口 (v3.2.6 新增, per user 2026-07-17 拍板)**: 摸底 Layer 0 发现工作树有未提交改动 (M / ?? untracked, 上个 session 收尾残留) → **默认纳入本轮一起收口, 不再 AskUserQuestion "怎么处理遗留改动"**. user 原话 "这批遗留改动本来就是这次自升级要处理的, 直接纳入本轮一起收口, 不要再停下来问". 例外: 遗留改动里含 4 类必问白名单 (framework config / user 偏好 / 不可逆 / user 显式说) 时, 仅对该子项走 AskUserQuestion, 其余 dirty 项照常纳入.
- ✅ **跑完摸底默认继续跑剩余 sub-task (v3.2.7 新增, per user 2026-07-18 拍板)**: 跑完单次摸底收口后**默认继续跑剩余 sub-task** (Phase 1.2 / 1.3 + Layer 1-3), **不再 AskUserQuestion "要不要继续"**. user 原话 "修改技能以后，不要出现这个情况，都是默认继续跑". 跟 v3.2.6 user-override 同根因, 跑后不主动停下问 user. 4 类必问白名单保留 (不可逆 / framework config / user 偏好 / user 显式说).
- ✅ **memory-bench 50 题必跑 (v3.2.8 新增, per user 2026-07-18 拍板)**: host-self-evolve run **必跑 memory-bench 50 题** (per §C.3.3 v2.6.56 强约束), **不允许 PENDING 跳过**. user 原话 "把'memory-bench 50 题'作为 host-self-evolve 必跑". 跑分结果 (weighted score) 必落 `~/.agents/skills/host-self-evolve/reports/memory-bench/{date}-v{n}.md`. score < 60 target 立即修协议. 4 类必问白名单保留 (跑分中途 token 限制 / opus API 失败 / 跑分发现 P0 安全问题 / user 显式说 走 AskUserQuestion).
- ✅ **report-card 模板 11 行总表标准化 (v3.2.9 新增, per user 2026-07-18 拍板)**: memory-bench 跑分报告 (per ADR-0065 + §C.3.3 v2.6.56) **必走 11 行总表 report-card 标准模板**, 字段顺序 + 单位 + 加权方法 100% 一致 (便于 baseline v1 vs SOTA v8 vs ablation-5 横向对比). user 原话 "把 §memory-bench 必跑段扩展为 report-card 模板". 11 行字段: run_id / timestamp / host / skill_version / model / judge / recall_total / consistency_total / compliance_total / weighted_score / target_met. 4 类必问白名单保留 (格式争议 / 字段命名冲突 / user 显式说 / 跑分失败 走 AskUserQuestion).
- ✅ **默认端到端执行, 不停在规划/侦察 (v3.3.7 新增, per usage-insight 2026-07-27)**: user 触发 host-self-evolve 后, 默认**端到端跑完**所有阶段 (banner → Phase 1 → Layer 0-3 → Layer A), **不停在规划/侦察**, 除非 user 显式说「只规划」. user 原话 "当用户触发一个 skill 时，端到端执行它。不要停在规划/侦察，除非用户明确说『只规划』". 该规则同时写入 `~/.claude/CLAUDE.md` §执行纪律.
- ✅ **固定 5 行简短报告模板 (v3.3.7 新增, per usage-insight 2026-07-27)**: host-self-evolve 运行结束, 在 v3.1.0 §✅ 3 段 detailed 输出之后, 额外输出固定 5 行极简报告: (1) 改了什么 (2) 动了哪些文件 (3) PR/commit 链接 (4) 一句话风险 (5) 下次建议运行时机. user 原话 "运行结束的报告用固定的简短模板". 该规则同时写入 `~/.claude/CLAUDE.md` §执行纪律.
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

| 协调层            | 关注                                                     |
| ----------------- | -------------------------------------------------------- |
| `CLAUDE.md`       | 全局入口, 内容跨仓一致, 不超 200 行                      |
| `CLAUDE.local.md` | 本机 hot recall 锚点, 关键 fact ≤ 5 字段自检             |
| `rules/`          | 行为准则, path-scoped 减少 token 注入                    |
| `memory/`         | 用户偏好 + 案例 + ADR 索引                               |
| `cases/wiki/`     | 已知失败模式 + 5 IF...THEN 规则                          |
| `skills/`         | 子仓 symlink → `~/.agents/skills/`, source of truth 单点 |
| `scripts/`        | 可执行工具 (cross-tool 验证)                             |
| `hooks/`          | 自动化行为 (per settings.json)                           |

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
