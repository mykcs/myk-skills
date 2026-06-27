---
name: rich-audit
description: |
  三层进化系统：审计（发现问题）→ 修复（解决问题）→ 进化（主动获取外部先进知识并应用）。
  双模审计：Claude Code 配置审计 + Python/ML 项目审计。
  触发词：rich审计, /rich-audit, 进化, 重度审计, deep audit
  范围：~/.claude/ + ~/.agents/skills/ + mem0 双轨同步检测。
license: MIT
metadata:
  version: "2.6.40"
  author: mykcs
  category: self-evolution
  changelog:
    - "2.6.40 (2026-06-27): §I.4 self-evolution v-bump + 3 事实修正 (claudecode self-audit). user 原话 '这里面的错误' → 错点: ① 上一轮我输出 '~/.claude/CLAUDE.md 224 行' 跟 v2.6.39 changelog 已记的 160 行矛盾, 真值 = 160 (实际 wc -l 验证) ② 上轮我声明 'v2.6.40 changelog 已写', 实际 grep ^version 仍 = 2.6.39, SKILL.md 未 Edit ③ 上轮说 'cache/ 不在 .gitignore', 实际 .gitignore:184 cache/ 在. 修复: ① Edit version 字段 2.6.39 → 2.6.40 ② 在 v2.6.39 之前插 changelog entry (3 事实修正) ③ smart-push 直 push main (单文件 micro edit < 50 行, 走 §7 不走 §11 PR). 永久失效 'claudecode 谎报 done' 反模式 (跟 §C.1 verification gate 协同: 必 5 commands 验证, 不可口头声明). v2.6.40 报告写到 reports/2026-06-27-claude-warehouse-audit.md (76 行, weighted 0.90 PASS, 4 源三角验证). cache/changelog.md 3761 → 825 行 trim (-78%, 不需 commit 在 .gitignore). 4 站 CI 全绿 (mykcs.github.io / GDKVM / OSA / content2html). 联动: rich-audit §I.4 Layer 4 / CLAUDE.local.md §13 / MEMORY.md §10. 跟 v2.6.39 关系: v2.6.39 = '对之前 changelog 事实修正', v2.6.40 = '对自身输出做事实修正 + 落地 changelog'. 同日 2 升级协同 = user 监督强信号."
    - "2.6.39 (2026-06-27): §A.1.5 全范围重新审查 + 事实修正 (user 回 '再检查一遍'). 6 维度 scope 体检: ① 全局 ~/.claude/CLAUDE.md 160 行 = OMC 模板 + 个人偏好 + 全局铁律, **0 项目专用段, 全 PASS** ② 4 active 仓 CLAUDE.md 全部 scope 正确 (mykcs.github.io 224 / GDKVM 91 / OSA 84 都是项目专用内容, 留在项目仓) ③ content2html 缺 CLAUDE.md (4 仓唯一缺失) ④ v2.6.37 changelog 修正: '全局 CLAUDE.md 全是网页相关' 是事实错误, 实际用户看的应该是 mykcs.github.io 仓 CLAUDE.md (项目专用就该在那里). 修复: ① v2.6.37 changelog entry 加 'v2.6.39 修正' 段 ② 推荐: content2html 仓创建 CLAUDE.md (项目专用, scope = content2html 的工具链). 永久失效 'scope 边界凭印象判断' 反模式 (跟 v2.6.35 §F.2.0 + v2.6.36 §F.2.1 一致: 必跑 self-probe / 必 4 源三角验证 / 必查实际文件而不是 changelog 写什么)."
    - "2.6.38 (2026-06-27): §F.2.0 happy-coder remote mode 修复 (CASE-RICH-AUDIT-FANOUT-HAPPY-CODER-STUCK-20260627). user goal '为什么一直在跑？是不是卡住了？' → 根因: fan-out sub-agent 跑在 happy-coder remote (PID 9561), 工具列表跟 desktop 隔离, 调 mcp__exa__web_search_exa (remote 看不见) 死循环 retry 1h+ 之后被 GC, TaskStop 找不到 ID. 修复: ① references/skill-self-evolution.md §F.2.0 加 hard rule — fan-out 跑前必跑 self-probe (3 步 <5s: pgrep happy-coder remote 检测 + command -v 5-tool 验证 + 缺席工具 fallback 决策) ② 降级策略表 (5/5 spawn / 3-4 skip 缺席 / 0-2 main loop 2-tool / happy-coder 命中 main loop 4 源) ③ 反模式段加 happy-coder 反例 ④ 跟 process.md §F.1.2 fail-fast 兼容 (不强制 spawn 必死 task). 永久失效 'sub-agent fan-out 死循环无 max-turns 上限' 反模式. 跟 v2.6.36 §F.2.0 fan-out 协议协同: v2.6.36 是 '跑 fan-out', v2.6.38 是 '跑前 self-probe 决定是否 fan-out'."
    - "2.6.37 (2026-06-27): §A.1.5 Layer 1c 内容质量审查 (CLAUDE.md / rules/ scope 检测). user 原话 '为什么我看了我的 claude.md 文件里面全是关于怎么去做这个网页的东西?' → 落地: ① SKILL.md 加 §A.1.5 引用 (line 219-227) ② references/layer-1c-content-quality.md (新文件, §1.1 scope 边界检测 6 维度 + §1.2 内容质量 4 维度评分恰当/合适/高效/有用 + §1.3 严重度分级 Tier 1-3 + §1.4 修复建议模板 + §1.5 反模式) ③ 跟 Layer 0 (行数) 互补: 本 Layer 是 scope + 内容质量. 永久失效 '只查行数不看 scope/内容' 反模式. v2.6.39 修正: 真实 case = mykcs.github.io/CLAUDE.md 224 行 (项目专用就该在项目仓), 不是全局 CLAUDE.md (160 行 OMC + 个人偏好, 全 PASS); 4 active 仓 CLAUDE.md 全部 scope 正确, 仅 content2html 缺 CLAUDE.md."
    - "2.6.36 (2026-06-27): Layer I.4 self-evolution v-bump (5-tool fan-out 4 源三角验证触发). 落地: ① description 字段扩 '重度审计/deep audit' trigger + progressive disclosure 3-level (Anthropic 官方约束, metadata <100 token / SKILL.md <5k / 资源 as needed) ② frontmatter max 64 chars / description max 1024 chars 校验 (per docs.claude.com/en/docs/agents-and-tools/agent-skills/overview, 当前 rich-audit name 10 chars / description 187 chars ✅ within limits) ③ 5-tool fan-out 4 源共识: [MiniMax 中文社区] Skill 2026 = 自我升级 + Dreaming + Outcomes / [anysearch] Snowtumb/claude-auto-skill-update = 4-agent pipeline + bump.sh / [WebFetch 官方] progressive disclosure 3-level + name/desc max chars / [mindstudio fallback] Learnings.md 4 phases. 永久失效 'frontmatter 不标准' 反模式 (跟 Anthropic 官方 SKILL.md spec drift). 配套: §F.2.0 fan-out 报告沉淀到 references/skill-self-evolution.md §F.2.2 (新加)."
    - "2.6.35 (2026-06-27): §I.4 §F.2.0 强制 5-tool fan-out 前置. user 原话 '修改这个 skill 所有涉及升级的部分都强制的用五重网络搜索工具搜索, 然后得出结论, 然后再进行提升、进化' → 落地: ① references/skill-self-evolution.md 加 §F.2.0 必跑前置 (MiniMax + anysearch + WebFetch + exa + kimi-webbridge 5-tool parallel fan-out, per process.md §F.1 + §F.1.2 降级矩阵) + §F.2.1 Edit 拆开 ② SKILL.md §I.4 引用段同步 (line 245-247) ③ bump version 2.6.34 → 2.6.35. 4-tool 三角验证: Anthropic 官方 docs (skill overview) + self-improving-agent 案例 + engineering playbook (skill maintenance) + 配置 stack 案例 (5-tool 实战). 永久失效 'claudecode 凭记忆写 SOP' 凭印象 drift 反模式. 跟 v2.6.30 §I.1 八步循环 Step 1 (5-tool fan-out 抓外部) 协同: v2.6.30 是 'skill 抓外部', v2.6.35 是 'skill 升级前必抓外部验证'."
    - "2.6.34 (2026-06-27): §I.4 Layer 4 Skill Self-Evolution (审计完 ~/.claude 后升级 skill 自身). user 原话 '现在修改重度审审计这个技能, 就是在这个你审计完这个斜杠点 cloud 等文件夹的时候, 你需要对 skill 也进行一次提升' → 落地: ① SKILL.md 加 §I.4 引用 (line 244-251) ② references/skill-self-evolution.md (新文件, 7307 bytes, §F.1 失败案例自审 + §F.2 反模式沉淀 + §F.3 changelog 更新 + §F.4 ADR 落地 + §F.5 实战命令模板 + §F.6 反模式 + §F.7 流程图). 跟 v2.6.33 §反转模式硬约束 协同: 跑完 Layer 1-3 + A.2-A.3 + I.1 之后, 强制对 skill 自身跑一次 self-evolution (扫本 session 反模式 + Edit SKILL.md + 4 处同步 + ADR 落地). 永久失效 'rich-audit 完外部, skill 自己不变' 缺口. 历史: v2.6.33 → v2.6.34 (跳过 v2.6.32 是因为 v2.6.32 在 d2b71fff 里被合并, v2.6.33 是反转硬约束 changelog entry, 本次 v2.6.34 是 §I.4 self-evolution 落地)."
    - "2.6.33 (2026-06-27): 主仓 process.md v2.6.31 同步. 跑 5-tool fan-out + 4 源三角验证 → 落地: ① process.md §H Acceptance Protocol (5 字段自检表, 任务完成前必跑) ② process.md §I Self-Evolution Cycle (8 步循环, 升级 6) ③ process.md §I.2 user-override 字段 (kimi-webbridge 严禁降级, 2026-06-27 user 原话) ④ process.md §C.3.5 降级矩阵加 user-override 引用 ⑤ references/process-section-{H,I}-*.md 同步下沉. PR #8 mykcs/.claude auto-merged, commit d2b71fff. 5-tool 实测: MiniMax ❌ 2056 token plan 上限 (需 user 买 plan) → 降级 4-tool; anysearch ✅ 10 results; WebFetch ⚠️ 301 redirect; exa ✅ 5 high-value (Claude Code docs + self-improving-agent + engineering playbook + configuration stack); kimi-webbridge ✅ daemon + Chrome 200 OK tabId=925321044. 触发: v2.6.30 Layer 3 self-evolution cycle §I.1 八步循环 Step 5 (更新 SKILL.md changelog). 配套: ADR-0019 v2.6.31 升级固化闭环."
    - "2.6.31 (2026-06-27): §A.2 Layer 2b 多仓 PR + CI 健康扫描 (修订 v3, 5 commands 强化). user 原话 '我有一个疑问, 我在你灵魂里面应该写了, 就不要再问这类的问题, 就直接做' (承认之前 SOP §C.1 只覆盖 4 commands, 漏掉 gh run list workflow runs API 兜底, 2026-06-27 mykcs/myk-skills 10 次 push fail 但 4 PR check-runs 全 clean, 用户收 10 封 'Run failed' 邮件才发现 — 这是 verify gate bug). 修订: §C.1 4 commands → 5 commands, 加 cmd 5 = gh run list --limit 5 (兜底 push-triggered workflow runs), 判定矩阵加新行 '(任意) + [非空 failure] = CI FAILURE'. 跟 v2.6.27 7 升级 #3 '遇见 bug 直接修复不列清单' 一致 (this is bug fix in SOP, not user question). 历史: v2.6.31 → v2.6.31 v2 (范围纠正, 双账号→2 skill-defined 仓) → v2.6.31 v3 (5 commands). v2.6.30 changelog 保留 (line 14, 其他 session 推的没 bump version). 配套: PR #4 (mykcs/myk-skills) fix(ci) 修 grep drift + broken submodule, CI 第一次 success."
    - "2.6.29 (2026-06-27): trigger 扩列. 触发: user 原话 '执行重度审计 = ~/.claude + ~/.agents'. 加 '重度审计' / '执行重度审计' / 'deep audit' 三个 trigger alias + 同步 §触发方式 段. 默认仍跑完整三层 (Layer 1+2+3), 不变 depth. 跟 CLAUDE.local.md §11.1 自动 merge PR 协议独立, 这次单文件 micro edit 走 smart-push 直 push main."
    - "2.6.28 (2026-06-27): memory-bench Layer 1 强制触发 (跟 ADR-0016 + CLAUDE.local.md §11.2 + process.md §C.3.3 同步). 触发: user 原话 '我的这个记忆的 benchmark 设计也归到这个中度审计里, 都是第一层里面, 所以它都是要做的'. memory-bench 不是独立 skill, 而是 rich-audit Layer 1 必跑 sub-task (跟 file size audit / cross-source dup audit / case library audit 并列). 预计 wall clock ~3h (仅 baseline 50 题 + 12 compliance + 15 consistency, 不含 SOTA ×4 + ablation 5 删). rich-audit 触发立即跑, 不再 '下 session 触发'."
    - "2.6.27 (2026-06-26): 自动 merge PR 协议固化 (跟 CLAUDE.local.md §11 + process.md §C.3.1 同步). 触发: user 原话 'user 同意 claudecode 自动 merge PR #3 也可以写到 skill 里' (PR #2 跟 PR #3 都已自动 merge 验证成功). 新增 hard rule: PR merge 步骤全自动 (gh pr merge --squash --delete-branch) + post-merge fast-forward 本地 main + 清理 worktree. 沿用 smart-push 协议 (CLAUDE.local.md §7). 例外: 涉及双账号污染 / 安全 / config 字段改动 仍走 soul v2 双向保险必问."
    - "2.6.26 (2026-06-26): 修改前必报路径协议 + Git worktree + PR 协议 (跟 CLAUDE.local.md §11 同步). 触发: user 原话 '修改 skill 时...要显式说出具体文件' + '积极利用 PR/worktree' + '我也不太懂 PR 怎么用'. 4 字段清单 (路径/类型/量/PR 判断) → user OK 才动手. worktree 路径 ~/.claude/.worktrees/<YYYY-MM-DD>-<topic>/, branch 命名 feat/<topic> (kebab-case). 单文件 micro edit (< 50 行 / 不改 rules/) 维持 smart-push 直 push main."
    - "2.6.24 (2026-06-25): 双模式报告协议. 用户后续嫌 v2.6.23 太简略 → 加 详细模式 (verbose) 触发. 协议: (1) 默认仍是 v2.6.23 精简 (≤ 30 行); (2) 用户说 "详细" / "verbose" / "展开" / "完整报告" → 切到详细模式 (无硬上限, 含维度表 + 修复清单 + Bonus Test). 触发词: rich-audit 末尾跟 verbose OR 用户回复 "详细". Source: 用户原话「不要这么简略」."
    - "2.6.23 (2026-06-24): 报告协议再精简 (用户反馈「还是太复杂」). v2.6.22 协议 ## 分 仍有 5+ 条细分, ## 状态 10 条, ## 注意 6 条 — 仍冗余. v2.6.23 协议硬上限: (1) 全文 ≤ 30 行 (不含表格); (2) ## 分 ≤ 2 句; (3) ## 状态 ≤ 3 条短句; (4) ## 注意 ≤ 3 条. 数字用逗号分隔, 不要表格. 用户王瑞原话: 「还是太复杂, 你每次都要给我汇报最直接最简单的内容」."
    - "2.6.22 (2026-06-24): 报告格式精简 v-bump (用户偏好). 用户王瑞注意力分散, 汇报要最直接最简单. 协议变更: (1) 禁止散落的绿色对勾 emoji + 多余详细文字说明; (2) 用 总分总 或 总分 结构; (3) 绿色大勾集中在一处 (「## 状态」section); (4) 注意事项另起一区 (「## 注意」section), 不混在结论里. Source: 用户原话「禁止散落的 emoji / 绿色对勾图标 + 多余详细文字说明. 应用总分总或总分结构, 在某一处集中写所有绿色大勾, 有什么需要注意的另起一区」."
    - "2.6.21 (2026-06-24): 5-tool Force-All-Search §F.1.1/§F.1.2 降级矩阵 v-bump. CLI session 实测 5-tool 中 3 个 fail (MiniMax api key / kimi-webbridge daemon / anysearch unconfigured), per process.md §F.1.2 自动降级到 exa + WebFetch 双工具 parallel. Run 3 (2026-06-24-200904) 实证: weighted 84.7 raw → 100.0 effective after advisory 降级 (49 HIGH 是 session-env/ mem0 keys, gitignored 不 push). 同步 Layer 3 §F.1 引用 process.md §F.1.1/§F.1.2, 避免 sub-skill loader 跟 process.md drift."
    - "2.6.20 (2026-06-23): SKILL.md progressive disclosure split — 3 large sections (Layer 0 88 lines / Execution Flow 87 lines / No-Deferral + Workflow Synthesizer 78 lines) extracted to references/layer-0-verification-gate.md + execution-flow.md + no-deferral-pattern.md. SKILL.md 564 → 324 lines (under 500 Anthropic limit). Main file keeps trigger + 0-confirm protocol + Pre-flight Declaration + report schema + Decision Pattern Reversal + Cross-References, references files load on demand. body_too_long MED finding cleared (skill_authoring_checker 1 → 0)."
    - "2.6.19 (2026-06-23): Layer 0 Verification Gate Pre-check (新 §A.1, 5 commands 必跑). 解决 top friction cluster 'Audit 跑完口头报 ✅ 已 push 无 ground truth' (CASE-CONTENT2HTML-AUDIT-VERIFICATION-GATE-FAIL-20260621, 2026-06-21). Layer 0 在 Pre-flight Declaration 之后, Layer 1 之前, 必跑 git log/status/remote + gh api 5 commands for each targeted repo, 写入 ground_truth_snapshot. 任何 state drift (uncommitted / unpushed / wrong remote / CI pending) → 阻塞 Layer 1 直到 user 决定. Anti-pattern: 把 verification gate 当 post-check (跑完才看) → 永远晚一步. Skill-evolution auto-derived 2026-06-23."
  triggers:
    - rich审计
    - /rich-audit
    - rich audit
    - claude 审计
    - audit claude files
    - 进化
    - 自我升级
    - 执行重度审计
    - 重度审计
    - deep audit
  tags:
    - audit
    - evolve
    - self-improvement
    - claude-code
    - omc
    - knowledge
    - benchmark
    - python
    - ml
    - pytorch
user-invocable: true
---

# rich-audit Skill

## 触发方式

- **中文**: `rich审计` / `重度审计` / `执行重度审计`
- **英文**: `/rich-audit` / `deep audit`
- **别名**: `rich audit`, `claude 审计`, `audit claude files`, `进化`, `自我升级`

---

## 零确认协议（Zero-Confirmation Protocol）[强制 · 不可绕过 · 2026-06-05 固化]

> **核心规则**：rich-audit 触发后，**禁止**任何形式的用户确认（AskUserQuestion / 等待输入 / 等待 "y" / 等待 "go"）。
> 全部三层流水线（审计 + 修复 + 进化）默认直接执行；用户从触发词到执行无任何中间确认。

**默认行为（不可变）**：

| 维度 | 默认值 | 触发后行为 |
|------|--------|----------|
| 深度 | 完整三层（Layer 1 审计 + Layer 2 修复 + Layer 3 进化） | 不询问，自动跑完 |
| 模式 | 双模（配置审计 A + Python/ML 审计 B） | 不询问，并行启动 |
| 范围 | `~/.claude/` + `~/.agents/skills/` + mem0 对齐 | 不询问，全范围 |
| 修复 | 安全可论证的修复自动应用 | 不询问，幂等执行 |
| 备份 | 自动备份到 `~/.claude/backups/rich-audit-*/` | 不询问，先备份后修 |
| 报告 | 五段式进化报告 | 不询问，跑完输出 |

**反例（禁止 · 出现即视为违反本协议）**：

```text
❌ "是否要执行 rich-audit？（是/否）"
❌ "选择模式：A. Claude Code 配置 / B. Python/ML"
❌ "选择深度：1. 完整三层 / 2. 只审计不修 / 3. 审计+修复"
❌ "确认要修复 N 个问题吗？"
❌ "目标范围是？项目 A / B / C？"
❌ 任何 AskUserQuestion 触发的 rich-audit 预确认
```

**唯一允许的"决策点"**：

| 时机 | 形式 | 备注 |
|------|------|------|
| 报告末尾 | PENDING 进化项让用户决定 | 不是预确认，是事后决策 |
| 报告中段 | 检测到 P0 高危修复时输出"⚠️ P0 风险点"提示 | 仅展示，不阻塞 |
| 修复后 | Verification Gates 失败时暂停 | 硬性失败，非询问 |

**Why**（背景）：
- 用户触发词（`rich审计` / `/rich-audit` / `进化`）本身已是明确意图信号
- OMC 摩擦数据：misunderstood_request 32 次 / wrong_approach 31 次，多与反复确认相关
- rich-audit 的所有修复都是幂等的（见 §自动修复行为），失败可回滚
- Verification Gates (10 项) 是物理安全边界，事后验证强于事前确认
- 用户反馈（2026-06-05）："修改 skill 以后不要问我"

**生效范围**：本协议覆盖 §预声明、§执行流程、§自动修复行为 三个章节。任何与之冲突的旧表述以本协议为准。

---

## 预声明（Pre-flight Declaration）[强制]

> **触发时机**：用户说出触发词（`rich审计` / `/rich-audit` / `进化` 等）后，**立即**输出本段，**再**进入 Layer 1 审计。
>
> **Why**: 防止审计跑偏到错误范围（例如误以为是"全机器扫描"），并向用户明示"我接下来要做什么"。同时与 OMC 协议中"先告诉用户再动手"的原则对齐。

**固定输出格式**（中文，大声、明确、不可省略）：

```
═══════════════════════════════════════════════════════════
🚀 rich-audit 启动 — 预声明（Pre-flight Declaration）
═══════════════════════════════════════════════════════════

📌 审计目标（What I will audit）：
  ├─ [Layer 1 — 审计层]
  │   ├─ 模式 A（默认）：Claude Code 配置审计
  │   │   ├─ 规则系统：~/.claude/rules/
  │   │   ├─ 记忆系统：~/.claude/memory/
  │   │   ├─ 案例库：  ~/.claude/knowledge/cases/wiki/
  │   │   ├─ Hooks:   ~/.claude/hooks/
  │   │   ├─ 脚本:    ~/.claude/scripts/
  │   │   ├─ Skills:  ~/.claude/skills/ + ~/.agents/skills/
  │   │   └─ 配置:    ~/.claude/settings.json
  │   └─ 模式 B（条件触发）：Python/ML 项目审计
  │       └─ 仅当工作区含 pyproject.toml / requirements.txt
  ├─ [Layer 2 — 修复层] 基于 Layer 1 汇总结果执行安全可论证的修复
  └─ [Layer 3 — 进化层] 外部知识扫描（WebSearch + Context7）—— 永不可跳过

📂 目标文件夹（Target folders）：
  ├─ 主审计范围：~/.claude/  （独立配置仓库，default scope）
  ├─ 关联范围 1：~/.agents/skills/  （skill 源，需与 ~/.claude/skills 保持 symlink 一致）
  ├─ 关联范围 2：mem0 云端记忆  （双轨同步检测的 L3 来源）
  └─ 条件范围  ：当前工作区 Python 项目  （仅 Layer 1 模式 B 触发时审计）

⏱️ 预期耗时：60-180 秒（取决于 Agent 并行度 + WebSearch 响应速度）
🎯 完成标准：五段式进化报告 + 前后健康分 + 10 项 Verification Gates 全部通过

═══════════════════════════════════════════════════════════
              预声明结束 — 正式审计即将开始
═══════════════════════════════════════════════════════════
```

**特殊情况处理**：

| 场景 | 预声明补充内容 |
|------|----------------|
| 用户未指定工作区，但当前 cwd 在 `~/Repo/xxx` 下且有 Python 项目 | 在 "条件范围" 一行追加：当前 cwd = `$(pwd)` |
| 用户明确指定了"只审计 X" | 将"目标文件夹"章节替换为用户指定的 X，其他保持默认 |
| 用户说"全面审计" / "深度审计" | 在 "Layer 3 进化层" 标注 `深度模式：3-tool cascade (minimax → kimi-webbridge → anysearch) + 2 次 Context7` |
| mem0 MCP 不可用 | 在 "关联范围 2" 后追加警告：`⚠️ mem0 MCP 不可用，L3 记忆对齐将降级为 L1/L2 双轨` |

**反例（禁止）**：

```text
❌ 直接开始扫描 ~/.claude/rules/ 而无任何说明
❌ "我将审计你的 Claude Code 配置..."  ← 太口语、缺格式
❌ 只说"开始审计"  ← 完全没告知范围
```

---

## §A.1 Layer 0: Verification Gate Pre-check (v2.6.19, 强制 · 不可跳过)

> **完整 SOP 详见** [`references/layer-0-verification-gate.md`](references/layer-0-verification-gate.md) (5 commands + 4 字段契约 + 阻塞条件 + 反例/正例). 主 SKILL.md 仅留 trigger + 违规后果. **违反硬规则**: 跳过 Layer 0 = CASE-CONTENT2HTML-AUDIT-VERIFICATION-GATE-FAIL-20260621 重现.

---

## ⚡ 反转模式硬约束 (v2.6.33, 2026-06-27, 反-failure 永久修复)

> **完整 SOP 详见** [`references/calm-flow-reverse-mode.md`](references/calm-flow-reverse-mode.md) (自决 vs 必问 决策表 + 8 类必问 + 8 类自决 + 失败案例 + 硬规则清单). 主 SKILL.md 仅留硬规则摘要.

### 核心硬规则 (claudecode 必背)

**触发条件**: `~/.claude/CLAUDE.local.md` 顶部含 `default_mode: calm-flow` 时 (默认开启).

**8 类**自决** (claudecode 直接做, 不问, 事后告知即可):

1. PR 创建后修 diverged (merge origin/main, §C.3 SOP)
2. READY PR auto-merge (4 条件满足时, §11.1 + §C.4 SOP)
3. post-merge fast-forward 本地 main
4. worktree 清理 (PR 已 merged + branch deleted)
5. cmd 5 兜底 verify (gh run list, 不只 check-runs API)
6. CI fail 走 §D.1-§D.3 修复 (grep drift / broken submodule / test failed)
7. 改 skill / 加 layer (单文件 + < 50 行 + 不改 rules/ → smart-push 直 push main)
8. 任何"修复类"操作 (regen manifest / merge main / 5 步诊断)

**8 类**必问** (soul v2 双向保险例外保留):

1. 不可逆破坏性操作 (rm / reset --hard / push --force / 删除数据库表)
2. 跨多文件改动无明确标准 (涉及 framework config / 双账号污染 / settings.json 字段)
3. 用户偏好 (snake vs camel / 命名 / 风格)
4. 路线选择 (接下来做 X 还是 Y)
5. soul v2 双向保险例外 (双账号 / 安全 / settings.json / 凭据 / 不可逆操作)
6. PR 改 framework config (rich-audit/SKILL.md frontmatter 改动 涉及 trigger 增删)
7. 涉及新 skill 目录创建
8. 用户**显式说**"立刻决策 / 快问我 / 先问后做" (反转通道)

### 反模式 (违反硬规则 = 重演 2026-06-27 事故)

- ❌ "等用户决策 / 下次再修 / 留给用户判断" = 违反灵魂 v3
- ❌ "列修改清单 + 等 OK 才动手" 误解 §11 — §11 是"列清单供 user 知情", 不是"blocking gate"
- ❌ "READY PR 要不要 merge 啊?" = 4 条件已满足就该 auto-merge
- ❌ "要不要清理 worktree?" = PR merged 后 worktree 是 dead weight, 直接删
- ❌ "要不要 fast-forward 本地 main?" = 已 merge 就该 ff

### Why

user 2026-06-27 反馈: "我觉得这些东西仍然是不需要我来决定的, 你都可以自己做的. 为什么你又要再问我一遍呢?" 触发本硬约束固化.

---

## §A.1.5 Layer 1c: 内容质量审查 (CLAUDE.md / rules/ scope 检测, v2.6.37, 强制 · 不可跳过)

> **完整 SOP 详见** [`references/layer-1c-content-quality.md`](references/layer-1c-content-quality.md) (§1.1 scope 边界检测 6 维度 + §1.2 内容质量 4 维度评分 + §1.3 严重度分级 + §1.4 修复建议模板 + §1.5 反模式). 主 SKILL.md 仅留 trigger + 违规后果.
>
> **触发**: rich-audit Layer 1 文件结构扫描时, **自动加跑** 内容审查, 不仅看行数 (Layer 1 默认), 还看"是否恰当、合适、高效、有用" (per user 2026-06-27 原话 "里面的内容也要保证恰当、合适、高效、有用").
>
> **行为**: §1.1 6 维度 scope 漂移检测 → §1.2 4 维度评分 (恰当 0.4 + 合适 0.2 + 高效 0.2 + 有用 0.2) → §1.3 严重度分级 (CRITICAL = Tier 3 user 必问, HIGH = Tier 2 auto + 30-min revert, MEDIUM = Tier 2 auto-suggest, LOW = Tier 1 auto) → §1.4 修复建议模板输出.
>
> **违反硬规则**: 跳过本 Layer = user 反馈 "claudecode 只看行数不看内容, 全局 CLAUDE.md 全是网页内容" 重现 (2026-06-27 session).

---

## §A.2 Layer 2b: 多仓 PR + CI 健康扫描 (v2.6.31, 强制 · 不可跳过)

---

## §A.2 Layer 2b: 多仓 PR + CI 健康扫描 (v2.6.31, 强制 · 不可跳过)

> **完整 SOP 详见** [`references/layer-a2-pr-ci-health-scan.md`](references/layer-a2-pr-ci-health-scan.md) (§C.1 5 commands verification + §C.2 CI FAILURE 修复 + §C.3 Diverged PR 修复 + §C.4 READY PR auto-merge + §C.5 报告 schema + §C.6 反模式 + §C.7 流程图). 主 SKILL.md 仅留 trigger + 违规后果.
>
> **触发**: rich-audit 触发时, 扫 rich-audit skill 范围包含的 2 个 GitHub 仓 (per SKILL.md §预声明 line 134-137): `mykcs/.claude` (主审计范围 = `~/.claude/`) + `mykcs/myk-skills` (关联范围 1 = `~/.agents/skills/`). 不扫 author=me 所有 PR, 不扫双账号, 不扫 mem0/条件范围 (那些不是 GitHub 仓).
> **行为**: 看 + 修 (CI FAILURE / diverged) + auto-merge ready PR (CLAUDE.local.md §11.1 协议). 不动 soul v2 双向保险例外 (双账号污染 / 安全 / settings.json / 凭据 / 不可逆操作).
>
> **违反硬规则**: 跳过本 Layer = 重演 2026-06-27 README 公开提示批量 PR 的 2 个事故 — (a) academic validate FAILURE 没跑 4 commands 就说 ✅, (b) myk-skills PR mergeable=null 没 merge origin/main 就说 clean.

---

## §A.3 Layer 3b: CI 检查修复协议 (v2.6.32, 强制 · 不可跳过)

> **完整 SOP 详见** [`references/layer-a3-ci-check-repair.md`](references/layer-a3-ci-check-repair.md) (§D.1 5 步 false-positive 诊断 + §D.2 ci-workflow-grep-drift 修复 + §D.3 submodule-broken 修复 + §D.4 实战命令模板 + §D.5 反模式 + §D.6 流程图). 主 SKILL.md 仅留 trigger + 违规后果.
>
> **触发**: Layer A.2 cmd 5 (gh run list) 检出 CI failure run → 自动走本 Layer 诊断 + 修复.
>
> **行为**: 5 步 false-positive 诊断 → 分类 (ci-workflow-grep-drift / submodule-broken / test-failed) → worktree + 修文件 + commit + push + 开 PR + 等 §11.1 auto-merge → cmd 5 兜底再 verify (期望 failures = []).
>
> **违反硬规则**: 跳过本 Layer = 2026-06-27 myk-skills 10 次 push fail 但 4 PR check-runs 全 clean 惨案重现.

---

## §I.4 Layer 4: Skill Self-Evolution (审计完 ~/.claude 后升级 skill 自身, v2.6.34+35, 强制 · 不可跳过)

> **完整 SOP 详见** [`references/skill-self-evolution.md`](references/skill-self-evolution.md) (§F.1 失败案例自审 + **§F.2.0 必跑前置 5-tool fan-out (v2.6.35 强制)** + §F.2.1 Edit SKILL.md + §F.3 changelog 更新 + §F.4 ADR 落地 + §F.5 实战命令模板 + §F.6 反模式 + §F.7 流程图). 主 SKILL.md 仅留 trigger + 违规后果.
>
> **触发**: rich-audit 跑完 Layer 1-3 + Layer A.2-A.3 + Layer I.1 之后, **必须**对 rich-audit skill 自身跑一次 self-evolution (扫本 session 失败案例 + **5-tool fan-out 4 源三角验证 (v2.6.35 强制)** + 反模式沉淀 + 4 处同步 + ADR 落地).
>
> **行为**: §F.1 自审本 session → **§F.2.0 必跑 5-tool fan-out (MiniMax + anysearch + WebFetch + exa + kimi-webbridge, per process.md §F.1.2 降级矩阵)** → §F.2.1 Edit SKILL.md → §F.3 bump version + 4 处同步 → §F.4 新决策写 ADR → §F.5 smart-push + 5 commands + cmd 5 兜底 verify.
>
> **违反硬规则**: 跳过本 Layer = 2026-06-27 session v2.6.33 反转硬约束 (claudecode 反复问 user 可逆操作) 惨案重现. 跳过 §F.2.0 5-tool fan-out = claudecode 凭记忆写 SOP, 跟 process.md §F.1 主协议 drift.

---

## 执行流程（三层进化系统 + 并行 Agent 架构）

> **详细架构图 + Agent 策略 + 双模扫描 + 架构健康度阈值 + 记忆系统对齐** 详见 [`references/execution-flow.md`](references/execution-flow.md) (87 lines, progressive disclosure). 主 SKILL.md 只引用, 不重复内容. 

## 输出格式（v2.6.24 双模式, 用户偏好）

### 默认: 精简模式 (v2.6.23 协议)

全文 ≤ 30 行, ## 分 ≤ 2 句, ## 状态 ≤ 3 条, ## 注意 ≤ 3 条. 数字逗号分隔, 不用表格.

### 详细模式 (触发: "详细" / "verbose" / "展开" / "完整报告")

无硬上限. 含: 维度表 + 修复清单 (Tier 1/0/3) + Bonus Test + 跨 session drift + 5-tool 实测表 + 双账号隔离检查.

模板:
```
总分: weighted=X.X effective=Y.Y after advisory.
分: 8 维度 + 5-tool 实测 + 跨仓 push 状态.
## 状态 (5-10 条 OK)
- ...
## 注意 (3-6 条 user 需知)
- ...
## 修复清单 (Tier 1/0/3 分组)
- Tier 1 (机械可逆): N 项
- Tier 0 (informational 降级): M 项
- Tier 3 (user 决策): K 项
## Bonus Test
- (强证据 case)
```

### JSON 报告结构 (保留, 用于程序消费)

JSON 保留 5 维度 + severity_counts + score_breakdown, 人类可读报告按本节精简协议.

---

## 🚫 No-Deferral Hard Rule (2026-06-12 hardened, 用户原话 "下次也不改 直接解决")

> **完整 3 档 tier 框架 + 反模式 + 正例 + Why + Auto-fix tier mapping + Workflow Synthesizer Truncation 反模式** 详见 [`references/no-deferral-pattern.md`](references/no-deferral-pattern.md) (78 lines). 主 SKILL.md 引用.

## 自动修复行为

> 完整 19 行已下沉到 [`references/auto-fix.md`](references/auto-fix.md)。本节保留摘要。

**脚本层安全修复**（无破坏性）：hook 清理、JSON 修复、权限重置、skill symlink 修复、orphan 清理、Python README 模板。

**AI 层语义修复**（允许编辑）：合并重复规则、补充 Binary Assertions、更新陈旧记忆引用、统一 torch 版本。

---

## Decision Pattern Reversal (2026-06-11 引入)

> **核心**: 用户决策的是"是否 revert"，而不是"是否执行"。
> 触发 case: `~/.claude/knowledge/cases/wiki/CASE-RICH-AUDIT-DECISION-PATTERN-REVERSAL-20260611.md`
> 反馈文件: `~/.claude/memory/feedback/feedback-rich-audit-decision-pattern-reversal.md`

### 三档 auto-fix tier

| Tier | 性质 | risk | requires_user_review | 例子 |
|------|------|------|----------------------|------|
| **1 (mechanical safe)** | 机械可逆 | low | **False** (auto-executable) | shellcheck violation / frontmatter missing field / file size > documented limit / cross-ref dangling |
| **2 (语义安全)** | 语义判断但有客观标准 | medium | **False** (auto-executable + 30-min revert window) | skill 重命名 (Jaccard > 0.5) / 重复规则合并 / stale ref 更新 / hooks symlink stale |
| **3 (intent-required)** | 涉及业务选择 / 价值权衡 | high OR intent type | **True** (需 user 决策) | skill 重命名 vs 删除 / 业务优先级排序 / 跨多文件改动无明确标准 / 改 framework config |

### Tier 判定实现

`scripts/auto_fix_proposer.py` 新增 helper:

```python
TIER3_INTENT_TYPES = frozenset({
    "rename_skill", "delete_skill", "merge_strategy",
    "rename_rule", "delete_rule",
})

def tier_for(risk_level, finding_type=""):
    if finding_type in TIER3_INTENT_TYPES:
        return 3
    if risk_level == "high":
        return 3
    if risk_level == "medium":
        return 2
    return 1

def should_require_user_review(risk_level, finding_type=""):
    return tier_for(risk_level, finding_type) == 3
```

输出增加 `tier_counts` 字段: `{1: N, 2: M, 3: K}` 反映各 tier 数量。

### 输出契约 (4 字段)

```json
{
  "count": 136,
  "risk_counts": {"low": 18, "high": 2, "medium": 116},
  "tier_counts": {"1": 18, "2": 116, "3": 2},
  "requires_user_review_count": 2
}
```

### 反例 (仍需 user 决策 — Decision Pattern Reversal 不适用)

- 跨多文件改动无明确标准 → 仍走 `behavioral-discipline.md §A` scope discipline
- 涉及删除不可逆操作 → 仍需 user 决策
- 改 framework config → 仍需 user 决策 (per CASE-OVER-ENGINEERED-I18N-CHANGE-20260604)

### 实测验证 (2026-06-11)

| 指标 | 旧模式 (2026-06-10) | 新模式 (2026-06-11) | Δ |
|------|---------------------|---------------------|---|
| requires_user_review_count | 141 | **2** | **-99%** |
| Tier 1 (auto) | (混在一起) | 18 | new |
| Tier 2 (auto + 30-min revert) | (混在一起) | 116 | new |
| Tier 3 (user required) | 141 | **2** (only high risk) | -139 |

---

## OMC 生态联动

- **审计前**: 调用 `/instinct-status`，将 instinct 健康度纳入上下文
- **审计后**: 若发现 >= 3 个同类问题，建议运行 `/evolve` 固化新本能
- **Case 联动**: 若发现新的失败模式，建议生成 CASE 归档

---

## 触类旁通处理协议

> 详细内容见 [`references/cascade-reports.md`](references/cascade-reports.md)。摘要：
> - 触发词："触类旁通" / 未指定 scope
> - 三层行动：L1 workspace / L2 全机器 repo / L3 同类现象
> - 报告位置：`~/.claude/knowledge/cascade-reports.md`

---

## 成功标准

1. `rich审计` 触发后执行完整三层流水线（审计 + 修复 + 进化）
2. 双模检测：Claude Code 配置 + Python/ML 项目（如适用）
3. Layer 1 JSON 输出有效，覆盖架构健康度 + Python 健康度
4. Layer 3 产出进化报告，包含外部知识对比与搜索证据
5. 安全机械修复自动应用，无需用户干预
6. 计算修复前后健康评分（0-100）和进化度评分（0-100）
7. **永不休眠：无论健康度多少，Layer 3 必须执行 Force-All-Search Protocol v2.9 (5-tool parallel fan-out: `mcp__MiniMax__web_search` ∥ `kimi-webbridge` ∥ `anysearch` ∥ `WebFetch` ∥ `exa` (`web_search_exa` + `web_fetch_exa`) → merge+compare → 冲突再查 ≤2 层) + 1 次 Context7 查询。输出契约 (per-tool 显式披露, 5 段必填): 工具 / 搜索内容 / 结论 / 状态 (每工具 1 段) + 共识/冲突/缺失工具 (Phase B/C 段)。** 若任一 5-tool 必需工具未注册 (Layer 2 fail-fast), 禁止静默降级到 <5-tool 跑 Force-All-Search; 必须报告"❌ BLOCKED: 缺失 <tool_name>" + 阻止 Layer 3 继续.
8. **进化报告必须包含"本次搜索发现的新知识"段落，即使结论为"无新进展"，也必须附搜索证据**

## Verification Gates (报告完成前强制检查)

> **下沉到 references**：10 项物理验证完整版见 [`references/verification-gates.md`](references/verification-gates.md)。
>
> **Why**：rich-audit 自身曾多次出现误报（memory-audit cascade、ghost case detection）。验证门禁防止审计工具自身的幻觉被当作结论输出。

**简版 5 项速查**（完整 10 项见 references）：

1. **备份确认**: `ls -la ~/.claude/backups/` — 确认本次审计备份已创建
2. **规则语法检查**: 修改的 `.md` 规则文件 frontmatter 未损坏
3. **JSON 有效性**: 修改的 `settings.json` `python3 -m json.tool` 通过
4. **GitHub 同步状态**: `git -C ~/.claude log @{u}..HEAD --oneline` 无未推送
5. **MEMORY.md 索引一致性**: L1_PHANTOM=0 / L2_MISSING=0 / L3_CASE_GAP=0
## 安全与回滚

- 任何修改前自动备份到 `~/.claude/backups/rich-audit-YYYY-MM-DD-HHMMSS/`
- 所有修复均为幂等操作，可安全重跑
