### ⚠️ §L27 3-Role Workflow (v4.0.7, 强制, 适用所有 sub-mode)

> **Source**: user 2026-07-01 原话 "修改 skill website improve 这个 skill 要有工作流，使用 Workflow 这个功能。不管是 skill 还是 workflow，要有计划者、执行者、检查验收者，这三个独立的。subagent 的，要分开。"

**架构 (3 独立 sub-agent + Workflow tool + SKILL.md 手册, 双层)**:

| 角色         | OMC agent                 | Model | 责任                                                                   |
| ------------ | ------------------------- | ----- | ---------------------------------------------------------------------- |
| **planner**  | oh-my-claudecode:planner  | Opus  | §L21 pre-flight + 4 站 scan plan + 风险决策 + 写 plan.json             |
| **executor** | oh-my-claudecode:executor | Opus  | git apply + smart-push.sh + decision-stream + 写 exec-log.json         |
| **verifier** | oh-my-claudecode:verifier | Opus  | 4 站 CI curl + 5 字段自检 + PASS/FAIL verdict + reject → executor 重做 |

> 通用 PER 规则（handoff / anti-patterns / 失败处理）见 SKILL.md 顶部 `## PER Workflow` 段落。本段只保留 website-improve 特有的角色分配与 JSON schema 示例。

**JSON artifact schema 必跑**（per plan / exec-log / verdict 各自 schema）:

```bash
# planner → plan.json (per ~/.claude/scripts/website-improve/plan_json_gen.py)
python3 ~/.claude/scripts/website-improve/plan_json_gen.py \
  --audit-target "<本次目标>" \
  --sub-modes "A,B,D" \
  --sites "GDKVM,OSA,mykcs,content2html" \
  --expected-wall-clock 45 \
  --completion "4 站 CI green,5 字段自检全过,decision-stream 全 append,case file 沉淀" \
  --pre-flight "<7 段 pre-flight 声明>" \
  --out plan.json

# executor → exec-log.json (per exec_log_gen.py)
python3 ~/.claude/scripts/website-improve/exec_log_gen.py \
  --plan plan.json \
  --files-changed "<path:N:M,path:N:M>" \
  --git-commits "<site:sha:msg,site:sha:msg>" \
  --smart-push "<status:site,status:site>" \
  --decision-stream-file "<JSON 数组 file>" \
  --out exec-log.json

# verifier → verdict.json (per verdict_json_gen.py)
python3 ~/.claude/scripts/website-improve/verdict_json_gen.py \
  --verdict PASS \
  --ci-gdkvm green --ci-mykcs green --ci-osa green --ci-content2html green \
  --sc-path PASS --sc-commit PASS --sc-push PASS --sc-ci PASS --sc-owner PASS \
  --dl-gdkvm PASS --dl-mykcs PASS --dl-osa PASS --dl-content2html PASS \
  --out verdict.json
```

**§L21 Pre-flight 默认反转 (PR #6 兼容)**:

- planner 输 7 段 pre-flight（audit trail）→ **直接进 executor**（不 user 等 OK，per v4.0.6 §L21 默认反转模式 + PR #6 merged commit f702ba8）
- 跟 PR #6 v4.0.6 §L21 默认反转模式 100% 兼容

**§L19/L25/L26 verifier 必跑**:

- **§L19**: 4 站 CI（mykcs/GDKVM/OSA/content2html）任一 red → verifier reject 整轮
- **§L25**: 4 站 curl live URL（不只 source grep）
- **§L26**: 5 字段自检表（path / commit / push / CI / owner 隔离 + 验收证据, per process.md §H Acceptance Protocol）

**e2e test 必跑 (跟 §C.5 验证门 + §D Bonus Test 协同)**:

```bash
# 10 case 端到端测试: 6 PASS + 4 FAIL 验证 schemas.py + 3 gen 脚本不退化
PATH=$HOME/.claude/scripts/website-improve/.venv/bin:$PATH \
  bash ~/.claude/scripts/website-improve/test_3role_e2e.sh
# 期望: PASS: 10 / FAIL: 0, rc=0
```

**触发式决策**:

- IF user 触发 website-improve → orchestrator 必 spawn 3 sub-agent（planner → executor → verifier），**不允许单 sub-agent 跑**
- IF 任一 sub-agent stall → §L23 Recovery（保留）
- IF verifier FAIL → executor 重做整轮（user 2026-07-01 选 A）
- IF verifier FAIL 2 次 → AskUserQuestion 拍板（no-stuck §C.3.6.1）
- IF 3 role workflow 跟 PR #6 §L21 默认反转冲突 → 以 PR #6 为准（默认反转优先，PR #6 merged commit f702ba8）

**反模式 (website-improve 特有, v4.0.7)**:

- ❌ 跳过 §L22 ToolSearch 让 sub-agent 0 tool uses
- ❌ plan.json / exec-log.json / verdict.json 写完不校验（fail-fast 缺失）
- 通用 PER 反模式（1 个 sub-agent 跑 3 角色 / executor 自标 done / verifier FAIL 仍 ship / 口头传话）见 SKILL.md 顶部 `## PER Workflow`。

**联动**:

- **§A.6 Verifier Self-Test Protocol**（v3.10.0 强制）— 升级为独立 verifier sub-agent（3 角色第 3 个）
- **§A.5 Multi-Round Audit Protocol**（v3.9.0 强制）— 每次 round 都跑 1 次完整 3-role（planner → executor → verifier）
- **§A.7 Template Consistency Check**（v3.10.0 强制）— 跟 3-role 协同不替换
- **§L19** 4 站 CI 全绿硬规则 — verifier 必跑
- **§L20** fix-validate-build — executor 改 package.json 后必 npm install + 二次 build
- **§L21** Pre-flight Declaration（v4.0.6 默认反转, PR #6 merged）— planner 输 7 段 pre-flight 兼容
- **§L22** Subagent Tool Provisioning（v4.0.4 治本 subagent stall）— 3 sub-agent 各自跑 Phase 0 ToolSearch
- **§L23** Orchestrator Recovery SOP（v4.0.4 治标 subagent stall）— 任一 sub-agent stall 触发
- **§L24** Stall Heartbeat Check（v4.0.4 subagent 静默检测）— 3 sub-agent 都受 5min heartbeat
- **§L25** Deployed-Layer Verify Protocol（v4.0.4 Round 11 P0/P1 regression 治本）— verifier 必跑 4 站 curl
- **§L26** CI 全绿验收标准（v4.0.5, per process.md §H Acceptance Protocol）— verifier 5 字段自检表
- **process.md §C.5** false completion — 任何 3-role run 必跑完所有阶段才能声明 done
- **process.md §C.3.6.1** no-stuck — 失败任一环立即 STOP + 降级或 AskUserQuestion
- **process.md §H** Acceptance Protocol — verifier self_check_5_fields 字段直接对应
- **CLAUDE.local.md §15** 4 站 CI 全绿 hot recall — verifier 必跑
- **CLAUDE.local.md §11.2** v2.6.57 banner UX 协同 (跟 PR #6 §L21 默认反转 UX 一致)
- **calm-flow.md §5** 卡片墙 — 3-role 决策摘要
- **post-task-recommend.md v0.2** 灵魂 v6 协议 — claudecode 顺手做的必自决（v0.2 永久失效反模式）
- **decision-stream/2026-07-01-website-improve-3role-design.md**（本 session design 草稿）
- **decision-stream/2026-07-01-website-improve-pr6-merge-rebase.md**（PR #6 merge 决策）
- **CASE-WEBSITE-IMPROVE-3ROLE-WORKFLOW-20260701**（立, 跟本段联动）
- **CASE-POST-TASK-RECOMMEND-20260701**（灵魂 v6 v0.2 协议联动）
- **CASE-SOUL-V6-4-VIOLATIONS-20260701**（4 类违反修复, 跟 §L27 反模式清单同源）
- **CASE-RICH-AUDIT-V2-6-59-TRIPLE-SUB-AGENT-20260701**（rich-audit v2.6.59 三段 sub-agent 协议位, 跟 §L27 3 角色架构同源）

**案例沉淀**:

- CASE-WEBSITE-IMPROVE-3ROLE-WORKFLOW-20260701 (立, 跟本段协同)
- CASE-POST-TASK-RECOMMEND-20260701 (灵魂 v6 v0.2 协议联动)
- CASE-SOUL-V6-4-VIOLATIONS-20260701 (4 类违反修复, 跟 §L27 反模式清单同源)
- CASE-RICH-AUDIT-V2-6-59-TRIPLE-SUB-AGENT-20260701 (rich-audit v2.6.59 三段 sub-agent 协议位, 跟 §L27 3 角色架构同源)

**Ref**:

- ~/.agents/skills/website-improve/SKILL.md (本文件)
- ~/.claude/decision-stream/2026-07-01-website-improve-3role-design.md
- ~/.claude/scripts/website-improve/README.md
- ~/.claude/rules/post-task-recommend.md v0.2
- ~/.claude/rules/process.md §C.3.6 §H §C.5
- ~/.claude/CLAUDE.local.md §15 §11.2 §12
