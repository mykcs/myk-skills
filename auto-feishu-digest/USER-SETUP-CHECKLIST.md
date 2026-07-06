# User-Side Setup Checklist — auto-feishu-digest MVP (待您配 LARK_APP_SECRET)

> **状态**: v0.1.8 (2026-07-06) — LARK_APP_ID + BAPP_TOKEN 已从 ~/.zshrc 搬到 `.env`,自动 source,不用每次手动 export。
> **skill**: `~/.agents/skills/auto-feishu-digest v0.1.8` (commit 待 push)
> **剩 1 项**: 替换 `LARK_APP_SECRET` 占位符 → 跑 `--verify` 全 ✅ → claudecode 跑 A4
> **核心改动**: `.env` 跟 skill 走 (per user 反馈 "不能我每次跑一遍 skill 都重新配一次")
> **验证脚本**: `bash ~/.agents/skills/auto-feishu-digest/scripts/digest-publish.sh --verify`
> **下一步**: 您把 LARK_APP_SECRET 替换真值 → 跑 --verify 7 全 ✅ → 回 "env 配好", claudecode 跑 A4

---

## Step 0: 为什么有 .env (per v0.1.8)

**之前 (v0.1.0-1.7)**: 7 env 全放 `~/.zshrc`,每次新 shell 要 `source ~/.zshrc`,换电脑 / 重装就丢,**鱼 bash zsh 行为分裂**。
**v0.1.8 起**: 7 env 放 `~/.agents/skills/auto-feishu-digest/.env` (跟 skill 走),3 个 .sh 脚本顶部自动 `set -a; . ../.env; set +a`。**好处**:
- 不用每次手动 export
- 换电脑直接拷 .env 就跑
- 不污染公共 shell source (`~/.zshrc` 保留)
- Secret 跟 skill 走,`mykcs/myk-skills` 仓 `.gitignore` 已含 `.env`,**不会被 push 泄漏**

---

## Step 1: 建飞书应用 + 自有权限 (5 min)

| # | 操作 | URL | 备注 |
|---|---|---|---|
| 1.1 | 打开飞书开放平台 | https://open.feishu.cn/app | 推荐 Chrome / Edge |
| 1.2 | 创建企业自建应用 | "创建企业自建应用" | 名字: `AI Daily Digest` |
| 1.3 | 添加机器人能力 | "应用功能 → 机器人" | 必加, 才能发消息 |
| 1.4 | 添加权限 scope | "权限管理 → API 权限" | 必须勾选 4 个: ① `bitable:app` ② `bitable:app:readonly` ③ `bitable:app:write` ④ `bitable:app:create` |
| 1.5 | 发布应用 | "版本管理与发布 → 创建版本" | 老板/管理员审批, 个人应用可自审 |
| 1.6 | 拿 2 个凭证 | "应用功能 → 凭证与基础信息" | **App ID** (cli_xxx) + **App Secret** (xxx) |

**勾选的 4 个 scope 作用**:

| Scope | 干啥 |
|---|---|
| `bitable:app` | 读写表格元数据 |
| `bitable:app:readonly` | 只读 table list / record list |
| `bitable:app:write` | 写 record / 改 record |
| `bitable:app:create` | 新建 record (不只是改) |

---

## Step 2: 建 Bitable base + 拆 4 表 (10 min)

| # | 操作 | 命名 |
|---|---|---|
| 2.1 | 打开飞书多维表格 | https://feishu.cn/base |
| 2.2 | 新建空白 base | 名字: **AI Daily Digest** (weiying 主用) |
| 2.3 | 复制 4 表结构 | 复制 [`templates/feishu-bit-schema.md`](~/.agents/skills/auto-feishu-digest/templates/feishu-bit-schema.md) §表 1-4 字段定义到 base |
| 2.4 | 建表 1: Paper (主表) | 25 字段 (per schema §表 1), 推荐先建这张, 跟 Auto Number + Created Time 一起 |
| 2.5 | 建表 2: Author | 8 字段 (per schema §表 2), DuplexLink 反向自动到 Paper |
| 2.6 | 建表 3: Venue | 6 字段 (per schema §表 3), DuplexLink 反向自动到 Paper |
| 2.7 | 建表 4: Weekly | 10 字段 (per schema §表 4), DuplexLink 反向自动到 Paper |
| 2.8 | 拿 5 个 ID | Base URL + 4 个 table_id |

**怎么拿 base URL + 4 table_id**:

```text
1. 打开新建的 base, URL 形如: https://feishu.cn/base/AbCdEfGhiJkLmN
   ↑ 这一段 (base ID) = BAPP_TOKEN

2. 打开 Paper 表, URL 形如: https://feishu.cn/base/AbCdEfGhiJkLmN?table=tblXXX
   ↑ 这一段 (table ID) = TABLE_ID_PAPER

3. 同样方法拿 Author / Venue / Weekly 3 个 table ID
```

---

## Step 3: 替换 LARK_APP_SECRET 占位符 (1 min)

v0.1.8 起,env 跟 skill 走。打开:

```bash
vim ~/.agents/skills/auto-feishu-digest/.env
```

把 `LARK_APP_SECRET="REPLACE_WITH_YOUR_APP_SECRET_HERE"` 那一行替换成真值 (从飞书 App "应用功能 → 凭证与基础信息" 拿)。

**已自动填好的 (从 zshrc 搬来,无需重配)**:
- LARK_APP_ID (跟 `~/.zshrc` 一致)
- BAPP_TOKEN (跟 `~/.zshrc` 一致)
- 4 TABLE_ID (Paper / Author / Venue / Weekly)

**用户替换 1 项**: LARK_APP_SECRET

**`~/.zshrc` 那 2 行 export 保留不动** (per user 2026-07-06 决策 "保留 zshrc 不动"),`.env` 为准, 鱼 bash 自动 source, zsh 走 zshrc (重复定义不冲突)。

---

## Step 4: 验证 (30 sec)

```bash
bash ~/.agents/skills/auto-feishu-digest/scripts/digest-publish.sh --verify
```

**期望输出 (全 ✅)**:

```
[1] 检查环境变量:
  ✅ LARK_APP_ID 已设
  ✅ LARK_APP_SECRET 已设
  ✅ BAPP_TOKEN 已设
  ✅ TABLE_ID_PAPER 已设
  ✅ TABLE_ID_AUTHOR 已设
  ✅ TABLE_ID_VENUE 已设
  ✅ TABLE_ID_WEEKLY 已设

[2] 检查 Bitable 可读:
  ✅ lark-cli 已装

[3] 检查 scored jsonl 缓存目录:
  ✅ /Users/myk/.cache/digest 存在
```

**任何一个 ❌ → 检查 Step 1-3, 一定要 source 重载后再跑**。

---

## Step 5: 回 "env 配好" → claudecode 跑 A4

您回我 "env 配好", claudecode 立即跑:

```bash
# 1. 真 collect (5 source fan-out, ~10 min)
bash ~/.agents/skills/auto-feishu-digest/scripts/digest-collect.sh --source=all

# 2. 真 score (5-min opus-as-judge, ~5 min)
bash ~/.agents/skills/auto-feishu-digest/scripts/digest-score.sh

# 3. 真 publish (写 Bitable 4 表, ~1 min)
bash ~/.agents/skills/auto-feishu-digest/scripts/digest-publish.sh --mode=daily --dry-run  # 先 dry-run
bash ~/.agents/skills/auto-feishu-digest/scripts/digest-publish.sh --mode=daily             # 真写
```

**v0.1.8 起不用 `source ~/.zshrc` 重载 env** — 3 个 .sh 脚本顶部自动 `.env`,任何 shell (fish / bash / zsh) 跑都生效。

5 字段验收 + case file 立到 `~/.claude/knowledge/cases/wiki/CASE-AUTO-FEISHU-DIGEST-MVP-RUN1-<date>.md`

---

## ❓ 3 个常见坑 (提前避)

### 坑 1: scope 加错

**症状**: publish 真写时报 `99991663 Missing scope`

**原因**: App 加 scope 但没发布版本, 或者加了 `bitable:app` 却没勾 `bitable:app:write`

**修复**: 回 Step 1.5 确保版本已发布, Step 1.4 4 个 scope 全勾

### 坑 2: 4 table 拆错顺序

**症状**: Paper 表创完, Author / Venue DuplexLink 找不到 table_id

**修复**: 必须先建 Paper 表 (主表), 再建 Author / Venue / Weekly (附属表 DuplexLink → Paper), 否则反向关联断

### 坑 3: env 写错 shell

**症状**: `--verify` 输出 "未设"

**原因**: 没 `source ~/.zshrc` 重载, 或者写到 `~/.bash_profile` 但用的是 zsh

**修复**: 看您 shell 是 zsh (macOS 默认) 还是 bash, 改对应文件 + source

---

## 🔗 资源

- 飞书应用申请: https://open.feishu.cn/app
- 飞书 Bitable 帮助: https://www.feishu.cn/hc/zh-CN/articles/0000013660003895
- lark-cli 文档: `lark-cli --help` (本机已装)
- skill 完整文档: `~/.agents/skills/auto-feishu-digest/SKILL.md`
- Case 立条: `~/.claude/knowledge/cases/wiki/CASE-AUTO-FEISHU-DIGEST-MVP-20260702.md`

---

## ⏱ 时间估算

| Step | 时间 |
|---|---|
| Step 1 (App + 4 scope) | 5-10 min |
| Step 2 (Bitable 4 表) | 8-12 min |
| Step 3 (shell env) | 1 min |
| Step 4 (verify) | 30 sec |
| Step 5 (claudecode run A4) | 15-20 min (含真 5-source fan-out + LLM judge) |

**总用户时间**: ~15 min (首次), 后续 daily 自动跑不用动。

---

**估计您跑下来 ≈ 15 min + 回 "env 配好" + 等我 15-20 min 跑 A4 真闭环 + 5 字段验收 + 立 case**。
