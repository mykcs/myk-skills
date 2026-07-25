---
name: gdkvm-train-launcher
description: GDKVM 训练启动 skill（2026-06-30 立, v1.0）— 在六号服务器（202/rtx6, 172.31.71.202）跑 hydra + torchrun 双卡训练。一行连接 + systemd-run 启动 + journalctl 监控 + GPU/CUDA 0,1 隔离 + loginctl Linger 必备 + hydra config 必须在 config/ 目录。触发场景：用户说「六号服务器」「202 (rtx6)」「两张卡」「GDKVM 训练」「code_modern_v3」「systemd-run 启动」时必读。
when_to_use: |
  触发: 六号服务器 / 202 (rtx6) / 172.31.71.202 / GDKVM 训练 / code_modern_v3 / 两张卡 / systemd-run 启动.
  硬约束: 禁 nohup/tmux/screen 必须 systemd-run --user; GPU 只用 0,1; loginctl Linger 必备; hydra config 在 config/ 目录.
  不适用: 其他服务器训练 / 推理部署 / 非 hydra+torchrun 任务.
metadata:
  type: skill
  version: 1.0
  created: 2026-06-30
  source_of_truth: ~/.claude/memory/connect-202-gpu.md (87 行, 2026-06-08 立)
version: "1.0.0"
author: "mykcs"
license: "MIT"
last_updated: "2026-07-19"
---

# gdkvm-train-launcher (v1.0)

> **一句话**：在 202 (rtx6) 用两张卡跑 GDKVM hydra 训练，所有 `nohup/tmux/screen` 都不行，**必须** `systemd-run --user`。

---

## §1. 服务器身份（"六号服务器 = 202 = rtx6"）

| 维度 | 值 |
|------|-----|
| 内部名 | rtx6 / 六号服务器 |
| IP | `172.31.71.202` |
| 用户 | `RuiWang2024` |
| 密码 | `2024RWang@CV++` |
| GPU | RTX 3090 × 4（平时 2 卡可用） |
| 代码根 | `/data/wr2024/Repo/code_modern_v3/` |
| 分支 | `kimi_repair_20260227` |
| venv | `/data/wr2024/Repo/code_modern_v3/.venv/` |

**冲突注意**：user.md profile 写 `172.31.71.132`，**实际**是 `.202`（2026-06-30 claudecode 实测 user 确认）。如未来再启新笔记，以本表为准。

---

## §2. 一行连接

```bash
sshpass -p '2024RWang@CV++' ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=accept-new RuiWang2024@172.31.71.202
```

**前置**：本机 `brew install sshpass`（macOS）或 `apt install sshpass`（Linux）。

---

## §3. GPU 硬约束：只用 0,1

| GPU 编号 | 归属 | 能否用 |
|---------|------|--------|
| 0 | RuiWang2024 | ✅ |
| 1 | RuiWang2024 | ✅ |
| 2 | GuanhaoWu (UID 1044) | ❌ 绝对不能用 |
| 3 | GuanhaoWu (UID 1044) | ❌ 绝对不能用 |

**所有启动命令必带**：`--setenv=CUDA_VISIBLE_DEVICES=0,1` + `--nproc_per_node=2`。漏掉 → 任务跑到别人卡上，可能被 kill 也可能污染别人实验。

---

## §4. 启动训练（systemd-run + Linger 必备）

### 4.1 一次性 enable-linger（已启用跳过）

```bash
ssh RuiWang2024@172.31.71.202 "loginctl show-user RuiWang2024 | grep Linger"
# 期望输出：Linger=yes
# 没开 → ssh 内跑：loginctl enable-linger RuiWang2024
```

### 4.2 启动 smoke 训练（50 iter 验证）

```bash
ssh RuiWang2024@172.31.71.202 << 'EOF'
cd /data/wr2024/Repo/code_modern_v3
systemd-run --user --unit=my_smoke \
  --working-directory=/data/wr2024/Repo/code_modern_v3 \
  --setenv=PATH=/data/wr2024/Repo/code_modern_v3/.venv/bin:/usr/bin:/bin \
  --setenv=CUDA_VISIBLE_DEVICES=0,1 \
  -- /data/wr2024/Repo/code_modern_v3/.venv/bin/torchrun \
    --standalone --nproc_per_node=2 \
    /data/wr2024/Repo/code_modern_v3/train.py \
    --config-path=config --config-name=config_smoke_50
EOF
```

### 4.3 启动正式训练

```bash
ssh RuiWang2024@172.31.71.202 << 'EOF'
cd /data/wr2024/Repo/code_modern_v3
systemd-run --user --unit=my_phase \
  --working-directory=/data/wr2024/Repo/code_modern_v3 \
  --setenv=PATH=/data/wr2024/Repo/code_modern_v3/.venv/bin:/usr/bin:/bin \
  --setenv=CUDA_VISIBLE_DEVICES=0,1 \
  -- /data/wr2024/Repo/code_modern_v3/.venv/bin/torchrun \
    --standalone --nproc_per_node=2 \
    /data/wr2024/Repo/code_modern_v3/train.py
EOF
```

**Unit 命名约定**：`my_<task>` 小写无空格（`my_phase` / `my_smoke` / `my_lr_warmup`）。

---

## §5. 监控

### 5.1 训练 log（journalctl，不是 /tmp/*.log）

```bash
ssh RuiWang2024@172.31.71.202 "journalctl --user -u my_phase -f"
```

### 5.2 看 DICE 指标（关键产物）

```bash
ssh RuiWang2024@172.31.71.202 "journalctl --user -u my_phase --no-pager | grep 'DICE=' | tail -10"
```

### 5.3 看 GPU 利用率

```bash
ssh RuiWang2024@172.31.71.202 "nvidia-smi --query-gpu=0,1,memory.used,utilization.gpu --format=csv,noheader"
```

### 5.4 看 Unit 状态

```bash
ssh RuiWang2024@172.31.71.202 "systemctl --user status my_phase --no-pager"
```

---

## §6. 停掉

```bash
ssh RuiWang2024@172.31.71.202 "systemctl --user stop my_phase"
```

**不要** `kill <pid>` — systemd-run 的 transient unit，stop 才是正确路径。

---

## §7. 关键约束（踩过的坑）

| 坑 | 解决 |
|----|------|
| GPU 2,3 是 GuanhaoWu 的 | 只用 `CUDA_VISIBLE_DEVICES=0,1` |
| `nohup` / `setsid` / `tmux` / `screen` / `crontab` / `ssh -f` / `at` 全部失败（SSH 退出被 logind cull） | **必须用 `systemd-run --user --unit=`** |
| `Linger=no` → user session 子进程被杀 | `loginctl enable-linger RuiWang2024`（一次性） |
| hydra `+train.num_iterations=50` 在 systemd-run 命令行解析失败 | 改用 config 副本 + `--config-path=config --config-name=config_smoke_50` |
| hydra `defaults: - model: base` 找不到 model/base.yaml | config 副本必须放 `config/` 目录，不能放 `/tmp/` |
| rtx1_23 已作废（2026-06-03 MCE 故障）| 不要 ssh `172.31.71.23`，所有实验都在 202 上 |

---

## §8. 历史背景

| 时间 | 事件 | 影响 |
|------|------|------|
| 2026-02-27 | branch `kimi_repair_20260227` 创建 | GDKVM 主代码库分支 |
| 2026-06-03 | rtx1_23 MCE 硬件故障 | 永久迁移到 202 (rtx6) |
| 2026-06-08 | rtx1_23 标 deprecated | claudecode 笔记固化 |
| 2026-06-08 | connect-202-gpu.md 87 行记下 systemd-run + Linger 必跑模式 | 沉淀方法论 |
| 2026-06-30 | 立 gdkvm-train-launcher skill (v1.0) | 笔记 → 结构化 skill |

---

## §9. 相关 case / 引用

| 文件 | 内容 |
|------|------|
| `~/.claude/memory/connect-202-gpu.md` | 本 skill 的 source of truth（87 行） |
| `~/.claude/memory/rtx1-23-deprecated.md` | rtx1_23 作废背景 |
| `~/.claude/knowledge/cases/wiki/CASE-RTX1-MCE-HARDWARE-FAILURE-20260603.md` | MCE 故障详细 |
| `~/.claude/knowledge/cases/wiki/CASE-GPU-DETACH-FAIL-20260608.md` | GPU detach 失败模式 |
| `~/.claude/knowledge/cases/wiki/CASE-GPU-DETACH-LOGIND-20260608.md` | logind cull 子进程 |
| `~/.agents/skills/website-improve/SKILL.md` | GDKVM 网站（非训练） |

---

## §10. 反模式（claudecode 必避）

- ❌ `nohup python train.py &` → SSH 退出被杀
- ❌ `tmux new -d "python train.py"` → 同上
- ❌ 不带 `CUDA_VISIBLE_DEVICES=0,1` → 跑别人卡上
- ❌ `kill <torchrun pid>` → 应该 `systemctl --user stop my_<task>`
- ❌ 把 hydra config 放 `/tmp/` → 找不到 model/base.yaml
- ❌ 改 rtx1_23 上代码 → rtx1_23 已作废
- ❌ 漏 enable-linger → systemd-run 启动后 SSH 退出被杀
- ❌ 不写 commit 就跑训练 → 代码跟配置不同步