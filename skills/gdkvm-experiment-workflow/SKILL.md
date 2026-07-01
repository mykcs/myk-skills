---
name: gdkvm-experiment-workflow
description: |
  GDKVM 实验 long-task 全循环 skill (v1.0, 2026-07-01 立) — 封装"连接 202 服务器 → 跑 hydra+torchrun → 设计实验 → 沉淀 case"完整闭环. 3 角色 subagent 严格串行 (Planner opus → Executor sonnet → Verifier sonnet), 失败任一环立即 STOP + AskUserQuestion 重新设计. 5 方向 sweep 内部 Executor sequential 排队 (GuanhaoWu 抢卡约束). 触发: "GDKVM 实验 / 跑 phase6 / 5 方向 sweep / phase5 long-run / 设计下一阶段实验 / 实验结果沉淀".
when_to_use: |
  触发: (1) user 说 GDKVM + 实验/phase/sweep/long-run/训练启动/服务器跑/DICE 数字; (2) user 拍板"开始 phase N"或"5 方向 sweep"; (3) plan v3.2 §修缮过程 5 方向任一进入执行阶段; (4) 实验结果出来后 user 说"沉淀/case/记录". 不适用: 单文件微调 / 文档更新 / 跑前问询 / 跟 GDKVM 仓无关的实验. 反模式: ❌ 失败不 STOP 继续下一环 / ❌ Executor 并行 5 方向 (GuanhaoWu 抢卡) / ❌ 跑完不沉淀 case / ❌ 跨 phase 复用 plan 不重审.
license: MIT
metadata:
  type: skill
  version: "1.0"
  created: "2026-07-01"
  category: ml-experiment-orchestration
  source_of_truth:
    - "~/.claude/plans/git-history-commit-rippling-gizmo.md (v3.2, 388 行)"
    - "~/.agents/skills/gdkvm-train-launcher/SKILL.md (v1.0, 189 行)"
    - "~/.claude/knowledge/cases/wiki/CASE-GDKVM-SERVER-ONBOARDING-20260701.md (167 行)"
  triggers:
    - "GDKVM 实验"
    - "跑 phase N"
    - "5 方向 sweep"
    - "long-run"
    - "设计下一阶段实验"
    - "实验结果沉淀"
  tags: [gdkvm, experiment, workflow, subagent-orchestration, hydra, torchrun, systemd-run, rtx6, case-archiving]
  user_invocable: true
  protocol_refs:
    - "process.md §A.3 (Feature Implementation Workflow)"
    - "process.md §B.1 (Plan Review Gate)"
    - "process.md §C.5 (false completion 反模式)"
    - "process.md §C.3.6 (no-stuck 协议)"
    - "process.md §H (Acceptance Protocol 5 字段)"
    - "rich-audit v2.6.55 (显式输出协议)"
    - "rich-audit v2.6.57 (启动 banner 段协议)"
---

# gdkvm-experiment-workflow (v1.0)

═══════════════════════════════════════════════════════════
🎯 gdkvm-experiment-workflow v1.0 <本次实验主题>
═══════════════════════════════════════════════════════════

📌 目标 (What I will orchestrate):
  ├─ [Planner] opus subagent 写 plan file (借鉴 plan v3.2 5 方向 + scorecard + Go/No-Go gate)
  ├─ [Executor] sonnet subagent 启训练 (复用 gdkvm-train-launcher sshpass + systemd-run + journalctl)
  └─ [Verifier] sonnet subagent 验收 (跑 8 步 SESSION START checklist + DICE grep + 5 件沉淀物)

⏱️ 预期 wall clock: 1 phase ≈ 4-6h (5 方向 long-run × 50-100 min/direction + 8 步 checklist + 沉淀物)
🎯 完成标准:
  - 3 subagent 严格串行 (不循环, per 物理卡约束)
  - 5 方向 sweep 内部 Executor sequential 排队 (GuanhaoWu 抢卡约束)
  - 失败任一环立即 STOP + AskUserQuestion 重新设计 (per process.md §B.1 + §C.3.6)
  - 跑完必输出 ## 做了什么 + ## 修了什么 2 段 (per v2.6.55 显式输出协议)
  - §H 5 字段自检表 + GDKVM 5 特化字段 (8 步 checklist / 5 方向 DICE / Go-No-Go gate / 15 反模式 / 5 件沉淀物)

═══════════════════════════════════════════════════════════
              banner 结束 — 正式实验循环即将开始
═══════════════════════════════════════════════════════════

## §1. 角色定义 (3 subagent 严格串行, 不循环)

### 1.1 Planner (opus, oh-my-claudecode:planner)

- **职责**: 战略规划 + interview workflow. 读 plan v3.2 + 现状, 设计 phase N 实验方案.
- **输入**: 3 source of truth (plan v3.2 / gdkvm-train-launcher v1.0 / server-onboarding case) + user 当前需求
- **输出**: `~/.claude/plans/gdkvm-<phase>-<YYYYMMDD>.md` (~388 行, 借鉴 plan v3.2 骨架)
  - 5 方向 + N 改动 + scorecard + Go/No-Go gate + 沉淀物清单
- **失败处理**: 立即 STOP, AskUserQuestion 重新设计 (per §B.1 Plan Review Gate)
- **关键能力**: 借鉴 rich-audit §I.6 capture 段 + 3 路并行调研 (plan v3.2 + server 端 8 步 checklist + 5-tool fan-out)

### 1.2 Executor (sonnet, oh-my-claudecode:executor)

- **职责**: focused task executor. 连 server + 启训练 + 监控 + 收 GPU.
- **输入**: Planner 产物 plan_path_abs + 5 方向 direction_set
- **输出**: journalctl 实时监控 + nvidia-smi GPU 利用率 + 训练 service 状态
- **失败处理**: 立即 STOP, 上报 Verifier 改设计 (per §C.3.6 no-stuck)
- **关键能力**: **复用 gdkvm-train-launcher v1.0 backend** (sshpass + systemd-run --wait + journalctl + systemctl --user stop)
- **5 方向 sequential 排队**: 不并行, GuanhaoWu 抢卡约束

### 1.3 Verifier (sonnet, oh-my-claudecode:verifier)

- **职责**: evidence-based completion. 跑 8 步 SESSION START checklist + DICE grep + Go/No-Go gate.
- **输入**: Planner plan + Executor logs (journalctl 截断 + GPU 利用率)
- **输出**: `~/.claude/knowledge/cases/wiki/CASE-GDKVM-<phase>-<YYYYMMDD>.md` + decision-stream
  - 5 件沉淀物 (per §7)
- **失败处理**: 写 BLOCKED decision-stream, AskUserQuestion 重设计
- **关键能力**: 借鉴 server-onboarding case 8 步 checklist + 15 反模式自检 + 5 方向 DICE delta 判定

### 1.4 串行协议 (不循环)

- **Planner → Executor → Verifier** 严格顺序, 阻塞前一个 → 后一个
- **不循环** (跟 ultraqa 区别): GDKVM 物理卡约束 retry 风险高, 失败走 AskUserQuestion 不重试
- **失败 STOP**: 任一环失败 → 立即停止后续环, 上报 user 重新设计

## §2. Planner 模板 (借鉴 plan v3.2)

### 2.1 plan 骨架 (5 段标准结构)

```markdown
# GDKVM phase N 计划 (v1.0, <YYYY-MM-DD HH:MM CST>)

> **状态**: v<X.Y>, <日期>
> **目标**: <一句话 phase 目标>
> **触发**: <user 原话 / 计划关键词>

## Context (为什么做)
<为什么这个 phase + 跟前 phase 关系 + 期望产出>

## 关键设计
### 5 方向 (B/C/D/E/F)
- 方向 X — <技术> (commit XXXXXX) ⭐ <优先级>
  - Why: <理论依据>
  - 改动: <文件>: <行数>
  - 预期: <DICE delta> / <wall delta>

## Scorecard (量化目标, phase gate 用)
| 指标 | baseline (R10) | 目标 (5 方向) | 验证 |
|------|----------------|----------------|------|
| Test DICE @ iter 3000 | 0.9380 | ≥ 0.94 | server smoke 跑完看 |

## 风险表
| 风险 | 缓解 |

## Go/No-Go gate
- ≥ 4/5 方向 Test DICE +0.001~+0.005 → ACCEPT, 写 case + 推 5 方向合并
- 2/5 反退 → revert + 找根因
- 全部反退 → 重新设计

## 沉淀文件 (5 件)
1. plan (本文件)
2. case (Verifier 阶段沉淀)
3. decision-stream (calm-flow §4 schema)
4. ADR (整数 slot NNNN)
5. memory (source-of-truth)
```

### 2.2 必填字段

- phase 号 + 日期 + server 环境快照 (8 步 checklist 缩略版)
- 5 方向每方向 1 段 (假设/命令/验收/反模式)
- Go/No-Go gate 必填 ≥ 4/5 ACCEPT 阈值

### 2.3 AskUserQuestion 强制点 (per §B.1)

- 5 方向接受哪几个
- 单方向 timeout 上限 (物理卡约束)
- 是否允许并行卡 (默认否, GuanhaoWu 抢卡约束)

## §3. Executor 模板 (复用 gdkvm-train-launcher v1.0)

### 3.1 sshpass 一行连接 (from gdkvm-train-launcher §2)

```bash
SSHPASS="$(security find-generic-password -s 'gdkvm-202-sshpass' -a 'RuiWang2024@172.31.71.202' -w)" \
  sshpass -e ssh -o StrictHostKeyChecking=no RuiWang2024@172.31.71.202
```

### 3.2 8 步 SESSION START checklist 必跑 (per server-onboarding case)

```bash
ssh RuiWang2024@172.31.71.202 '
echo "=== 1. git HEAD 跟 mac 一致 ==="
git -C /data/wr2024/Repo/code_modern_v3 log -1 --format="%h | %s"

echo "=== 2. git status clean ==="
git -C /data/wr2024/Repo/code_modern_v3 status --short --branch

echo "=== 3. Linger=yes ==="
loginctl show-user RuiWang2024 | grep Linger

echo "=== 4. GPU 0,1 空闲 ==="
nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv,noheader

echo "=== 5. 无 stale units ==="
systemctl --user list-units "gdkvm-p5lr-*.service" --state=failed --no-pager --no-legend

echo "=== 6. triton binary 在 ==="
ls /data/wr2024/Repo/code_modern_v3/.venv/lib/python3.12/site-packages/triton/backends/nvidia/bin/

echo "=== 7. torch 2.6.0+cu124 ==="
uv run python -c "import torch; print(torch.__version__, torch.cuda.is_available())"

echo "=== 8. GPU 跟 mac 端一致 ==="
nvidia-smi --query-gpu=name --format=csv,noheader
'
```

**任一 FAIL** → 立即 STOP, AskUserQuestion 重新设计 (违反 §C.3.6 no-stuck)

### 3.3 systemd-run 启训练 (必带 `--wait` 串行 + `CUDA_VISIBLE_DEVICES=0,1`)

```bash
ssh RuiWang2024@172.31.71.202 "
cd /data/wr2024/Repo/code_modern_v3
systemctl --user reset-failed gdkvm-p5lr-*.service
systemd-run --user --unit=gdkvm-p5lr-<dir> --wait \
  --setenv=CUDA_VISIBLE_DEVICES=0,1 \
  --setenv=PYTHONPATH=/data/wr2024/Repo/code_modern_v3 \
  --setenv=HYDRA_FULL_ERROR=1 \
  --setenv=OMP_NUM_THREADS=1 \
  --setenv=NCCL_IB_DISABLE=1 \
  --setenv=TORCH_NCCL_BLOCKING_WAIT=1 \
  --setenv=TORCH_NCCL_ASYNC_ERROR_HANDLING=1 \
  --setenv=UV_LINK_MODE=copy \
  --working-directory=/data/wr2024/Repo/code_modern_v3 \
  --setenv=PATH=/home/RuiWang2024/.local/bin/uv:\$PATH \
  --property=MemoryHigh=40G \
  /home/RuiWang2024/.local/bin/uv run torchrun --standalone --nproc_per_node=2 \
    /data/wr2024/Repo/code_modern_v3/train.py \
    --config-path=/data/wr2024/Repo/code_modern_v3/config \
    --config-name=config_<x> \
    main_training.num_iterations=<iters> \
    hydra.run.dir=/data/wr2024/Repo/code_modern_v3/outputs/phase<X>_longrun/gdkvm-p5lr-<dir>_<NOW> \
    main_training.ema_decay=<X> \
    main_training.accum_steps=<N> \
    ddp.bucket_cap_mb=50
"
```

### 3.4 journalctl 监控

```bash
ssh RuiWang2024@172.31.71.202 "
journalctl --user -u gdkvm-p5lr-<dir> --no-pager | grep -E 'DICE=|Test DICE=|Val DICE=' | tail -10
"
```

### 3.5 nvidia-smi GPU 利用率

```bash
ssh RuiWang2024@172.31.71.202 "
nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv,noheader
"
```

### 3.6 停训练 (必 `systemctl --user stop`, 不 `kill <pid>`)

```bash
ssh RuiWang2024@172.31.71.202 "
systemctl --user stop gdkvm-p5lr-<dir>.service
"
```

### 3.7 5 方向 Executor 内部 sequential 排队

```bash
for dir in d e b f c; do  # 不并行, GuanhaoWu 抢卡约束
  run_unit gdkvm-p5lr-$dir config_<x> <iters> "<extra>"
done
```

### 3.8 失败处理

- 任一方向 fail → 立即 STOP, AskUserQuestion 重设计 (per §C.3.6 no-stuck)
- 不重试 (GPU 抢卡 retry 风险高, per ultraqa 区别)

## §4. Verifier 模板 (借鉴 server-onboarding case)

### 4.1 重跑 8 步 SESSION START checklist 验证

```bash
ssh RuiWang2024@172.31.71.202 '
echo "=== 8 步 checklist ==="
<跟 §3.2 同 8 步>
'
```

### 4.2 DICE grep (从 journalctl 抓 Test DICE)

```bash
ssh RuiWang2024@172.31.71.202 "
journalctl --user -u gdkvm-p5lr-<dir> --no-pager | grep -E 'Test DICE=' | tail -5
"
```

### 4.3 Go/No-Go gate (跟 plan §Scorecard 对齐)

```markdown
- DICE ≥ baseline → ACCEPT
- DICE < baseline → BLOCKED
- 4/5 ACCEPT → 写 case + 推 5 方向合并
- 2/5 反退 → revert + 找根因
- 全部反退 → 重新设计
```

### 4.4 5 件沉淀物 (per §7)

### 4.5 反模式条款 (15 项) 验证, 跑过即勾选

## §5. 完整循环 (Plan → Execute → Verify → 沉淀)

```
Step 1: Planner subagent → plan file
  ↓ (per §B.1 user review + AskUserQuestion gate)
Step 2: Executor subagent (5 方向 sequential 内部排队) → journalctl log
  ↓ (per §C.3.6 no-stuck, 失败 STOP)
Step 3: Verifier subagent → case file + decision-stream
  ↓ (per §H Acceptance Protocol)
Phase end: §H 5 字段自检表 + GDKVM 5 特化字段
  ↓ (per CLAUDE.local.md §灵魂 v6)
任务后建议 (post-task-recommend.md): 3 段 (踩坑 / 避坑 / follow-up)
```

## §6. 15 反模式 (永久失效, claudecode 必背)

| # | 反模式 | IF...THEN | 来源 |
|---|--------|-----------|------|
| 1 | ❌ 假设 server 端有 `.venv/bin/torchrun` | **THEN** 必 `uv run torchrun` | launcher §1 |
| 2 | ❌ `systemd-run` 默认并行抢 GPU | **THEN** 必加 `--wait` 串行 | launcher §1 |
| 3 | ❌ 重启前不清 stale units | **THEN** 必 `systemctl --user reset-failed` | launcher §1 |
| 4 | ❌ 看到 `status=1/FAILURE` 立刻推断"代码错" | **THEN** 必 `journalctl` 找真因 | launcher §1 |
| 5 | ❌ 跑前不 `uv sync` | **THEN** 必 verify triton binary 在 | launcher §1 |
| 6 | ❌ `nohup / ssh -f / tmux / screen` | **THEN** 必 `systemd-run --user` | launcher §1 |
| 7 | ❌ 不带 `CUDA_VISIBLE_DEVICES=0,1` | **THEN** 必带 (GuanhaoWu 抢卡 2,3) | launcher §1 |
| 8 | ❌ `kill <pid>` 停训练 | **THEN** 必 `systemctl --user stop` | launcher §1 |
| 9 | ❌ 改 rtx1_23 (已作废 2026-06-03 MCE) | **THEN** 必用 202 (rtx6) | onboarding case |
| 10 | ❌ 不看 server 真实环境 | **THEN** 必 `which torchrun + which python3 + journalctl` | onboarding case |
| 11 | ❌ 不写 commit 就跑训练 | **THEN** 必 code + config 同步 (git push 前) | onboarding case |
| 12 | ❌ hydra config 放 `/tmp/` | **THEN** 必放 `config/` 目录 | onboarding case |
| 13 | ❌ 跳 8 步 SESSION START checklist | **THEN** 必跑全 8 步 (3.2 段) | onboarding case |
| 14 | ❌ DICE 反退立刻 revert | **THEN** 必先看 journalctl 找根因 (per plan v3.2 §反模式) | plan v3.2 |
| 15 | ❌ 跑完不沉淀 case | **THEN** 必 Verifier 阶段写 5 件沉淀物 (per §7) | plan v3.2 + 灵魂 v6 |

## §7. 5 件沉淀物 (Phase 闭环)

| # | 类型 | 路径 | 模板源 | 时机 |
|---|------|------|--------|------|
| 1 | plan | `~/.claude/plans/gdkvm-<phase>-<YYYYMMDD>.md` | git-history-commit-rippling-gizmo.md v3.2 (388 行) | Planner 输出 |
| 2 | case | `~/.claude/knowledge/cases/wiki/CASE-GDKVM-<phase>-<YYYYMMDD>.md` | CASE-GDKVM-SERVER-ONBOARDING-20260701.md (167 行) | Verifier 输出 |
| 3 | decision-stream | `~/.claude/decision-stream/2026-07-01-gdkvm-<phase>-<key>.md` | calm-flow §4 schema | Executor / Verifier 决策点 |
| 4 | ADR | `~/.claude/docs/adr/<NNNN>-gdkvm-<topic>-<YYYY>.md` | adr-template | 架构决策时 |
| 5 | memory | `~/.claude/memory/gdkvm-<topic>-<YYYY>.md` | connect-202-gpu.md (87 行结构) | Phase 收尾 |

**字段约束**:
- ADR 走整数 slot (per ADR-0027 v1.1 sub-slot 规则, 不抢 0030 sub-slot)
- decision-stream 走 calm-flow §4 YAML schema (ts / type / content / decision / impact / reversible / risk)
- case 走 server-onboarding case 骨架 (Finding + 8 步 checklist + 5 反模式 + 1 成功路径 + 历史 record)
- memory 走 connect-202-gpu 87 行结构 (5 维 evidence + 5 IF...THEN 规则)

## §8. 联动文件清单

### 上游模板 (不修改, 仅 Read)

| 类型 | 文件 | 用途 |
|------|------|------|
| Planner 模板 | `~/.claude/plans/git-history-commit-rippling-gizmo.md` (v3.2, 388 行) | 5 方向 + scorecard + Go/No-Go gate |
| Executor backend | `~/.agents/skills/gdkvm-train-launcher/SKILL.md` (v1.0, 189 行) | sshpass + systemd-run + journalctl |
| Verifier 模板 | `~/.claude/knowledge/cases/wiki/CASE-GDKVM-SERVER-ONBOARDING-20260701.md` (167 行) | 8 步 SESSION START checklist + 5 反模式 |

### 主仓协议 (Read + 引用)

| 文件 | 段 | 用途 |
|------|---|------|
| `~/.claude/rules/process.md` | §A.3 / §B.1 / §C.5 / §C.3.6 / §H / **§X.1** | 流程 + 验收 + Plan Review + no-stuck + 跨 skill 引用 |
| `~/.claude/CLAUDE.local.md` | §11.6 (v2.6.58 hint) | hot recall 本 skill |
| `~/.claude/memory/MEMORY.md` | §G gdkvm 段 | 索引入口 |
| `~/.claude/CLAUDE.md` | §Repo Confirmation + 4 站 + 双账号铁律 | 范围纪律 |

### OMC subagent (Task tool 调用)

| 角色 | subagent_type | model |
|------|---------------|-------|
| Planner | `oh-my-claudecode:planner` | opus |
| Executor | `oh-my-claudecode:executor` | sonnet |
| Verifier | `oh-my-claudecode:verifier` | sonnet |

## §9. 验收协议 (per §H + GDKVM 实验类特化)

### 9.1 universal §H 5 字段自检表 (per process.md §H)

| # | 字段 | 验收标准 | GDKVM 实验类适配 |
|---|------|---------|------------------|
| 1 | path | 5 件沉淀物绝对路径已输出 | 1+2+3+4+5 全列 |
| 2 | commit | `git log -1` 主仓 + 子仓双仓有 commit | 双仓独立 PR |
| 3 | push | `git rev-list --count @{u}..HEAD = 0` (主仓 + 子仓双验) | 双仓双跑 |
| 4 | CI | N/A (训练类, 走 §G.5 universal evidence 替代) | journalctl DICE grep 替代 |
| 5 | owner 隔离 + 验收证据 | owner 正确 + 1+ 行可执行命令 | 双账号铁律 + 5 commands verification |

### 9.2 GDKVM 实验类特化字段 (Phase end 必跑)

| # | 字段 | 验收标准 |
|---|------|---------|
| 6 | 8 步 checklist | 重跑 8 步 SESSION START, 全过 (1-8 勾选) |
| 7 | 5 方向 DICE | 每方向 `journalctl ... | grep 'DICE=' | tail -1` 输出 |
| 8 | Go/No-Go gate | 每方向判定 ACCEPT/BLOCKED, 跟 plan scorecard 对齐 |
| 9 | 15 反模式 | 反模式自检表全勾 (1-15) |
| 10 | 5 件沉淀物 | 1-5 全在, 路径列出 |

### 9.3 验收协议触发时机

- ✅ Phase end (5 方向全跑完 + Verifier ACCEPT)
- ✅ Phase 中途失败 (Executor BLOCKED)
- ✅ user 拍板 "开始 phase N"
- ✅ Phase closeout ADR 写入前

### 9.4 反模式 (验收阶段永久失效)

- ❌ Verifier 写 case 缺 8 步 checklist evidence (字段 6 跳)
- ❌ 5 方向 DICE 数字只报 1 个汇总, 缺单方向明细 (字段 7 跳)
- ❌ Go/No-Go gate 走 "感觉 OK" (字段 8 跳)
- ❌ 15 反模式自检表只跑 5 个 onboarding 来源 (字段 9 跳)
- ❌ 沉淀物只写 case 不写 ADR + memory (字段 10 跳)

## 任务后建议 (per 灵魂 v6 + post-task-recommend.md)

跑完任一 phase 后必给 3 段结构化建议:

1. **这次踩坑 (1-3 条)**: [踩坑现象] — 根因 / 当时为什么没识别
2. **未来怎么避 (1-3 条)**: [可执行的避坑动作] — 为什么能避
3. **3 件 follow-up**: 立即做的小事 / 需要 user 拍板的中事 / 下次 session 顺手的优化

+ mem0 add_memory 1-3 条/交互 (per post-task-recommend.md §3)

## Cross-ref

- **上游调研**: `~/.claude/plans/git-history-commit-rippling-gizmo.md` (本文件 v3.2 + 阶段 5 完整 388 行 + 新立 §gdkvm-experiment-workflow plan 段)
- **主仓协同**: process.md §X.1 (跨 skill 引用段) + CLAUDE.local.md §11.6 (v2.6.58 hot recall) + MEMORY.md §G (索引入口)
- **Executor backend**: gdkvm-train-launcher SKILL.md v1.0 (189 行)
- **Verifier 模板**: CASE-GDKVM-SERVER-ONBOARDING-20260701.md (167 行)
- **联动协议**: process.md §A.3 / §B.1 / §C.5 / §C.3.6 / §H + rich-audit v2.6.55 / v2.6.57 + post-task-recommend.md

## 历史 record

- 2026-07-01 18:21 CST: 立 v1.0 (user 拍板 3 subagent 串行 + Executor 复用 gdkvm-train-launcher + 双仓独立 PR)