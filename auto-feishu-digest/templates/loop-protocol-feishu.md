# Loop Protocol — Auto Feishu Digest MVP (启动 checklist)

> **触发**: 第一次跑 auto-feishu-digest skill 时, 复制本协议填 4 配置.
> **不用每次都填**: 1 次配好, 后续 cron + claudecode 自动跑.

## 4 必填配置 (前置)

| # | 配置 | 默认 | 说明 |
|---|---|---|---|
| 1 | **LARK_APP_ID** | `<需 user 提供>` | 飞书应用 App ID |
| 2 | **LARK_APP_SECRET** | `<需 user 提供>` | 飞书应用 App Secret |
| 3 | **BAPP_TOKEN** | `<需 user 提供>` | 飞书 Bitable Base 的 app_token (URL 中 `/base/` 后) |
| 4 | **TABLE_ID_<N>** | 4 个 (paper / author / venue / weekly) | 每个 Bitable 表 ID |

**获取路径**:

```bash
# 1. 创建飞书应用: https://open.feishu.cn/app
#    (跟内容管理 CLI 应用区分, 这是新 app, scope: bitable:app + bitable:app:readonly + bitable:app:write)

# 2. 创建 Bitable base (https://feishu.cn/base)
#    推荐命名: AI Daily Digest (weiying 主用), URL 形如 feishu.cn/base/AbCdEfGhiJkLmN

# 3. 拆 4 表 (per templates/feishu-bit-schema.md)
#    Paper / Author / Venue / Weekly

# 4. 用 templates/feishu-bit-schema.md 字段定义填, 4 表全设 DuplexLink

# 5. 把 4 个 table_id 抄写到 ~/.zshrc / ~/.bash_profile
export LARK_APP_ID="cli_xxx"
export LARK_APP_SECRET="xxx"
export BAPP_TOKEN="AbCdEfGhiJkLmN"
export TABLE_ID_PAPER="tblXXX1"
export TABLE_ID_AUTHOR="tblXXX2"
export TABLE_ID_VENUE="tblXXX3"
export TABLE_ID_WEEKLY="tblXXX4"

# 6. verify
bash ~/.agents/skills/auto-feishu-digest/scripts/digest-publish.sh --verify
```

---

## 跑通路径 (5 步)

| Step | 脚本 | 输入 | 输出 | 时间 |
|---|---|---|---|---|
| 1 | `digest-collect.sh --source=arxiv` | (无, 自动跑) | `~/.cache/digest/arxiv-<date>.jsonl` | 2-3 min |
| 2 | `digest-collect.sh --source=all` (5 源) | 5 source | 5 jsonl | 10-15 min |
| 3 | `digest-score.sh --in=*.jsonl` | 5 jsonl | `scored-<date>.jsonl` + dedup | 5-10 min |
| 4 | `digest-publish.sh --in=scored-<date>.jsonl --mode=daily` | scored | 写 Bitable top 5 | 1-2 min |
| 5 | `digest-publish.sh --mode=weekly` (周日晚跑) | scored 7d | top 20 + 周报附件 | 2-3 min |

**总 wall clock**: 12-20 min (daily) / 20-30 min (weekly)

---

## cron 配置 (推荐)

```bash
# crontab -e
# daily 08:00 CST (UTC+8, system tz)
0 8 * * * bash ~/.agents/skills/auto-feishu-digest/scripts/digest-collect.sh --source=all && bash ~/.agents/skills/auto-feishu-digest/scripts/digest-score.sh && bash ~/.agents/skills/auto-feishu-digest/scripts/digest-publish.sh --mode=daily >> ~/.cache/digest/log/daily.log 2>&1

# weekly 周日 20:00 CST
0 20 * * 0 bash ~/.agents/skills/auto-feishu-digest/scripts/digest-publish.sh --mode=weekly >> ~/.cache/digest/log/weekly.log 2>&1
```

**不依赖 cron 替代方案** (claudecode 触发):

- 在 daily journal 文件 `~/.claude/journal/<date>.md` 顶部加 trigger marker
- SessionStart hook 检测 marker → 自动跑 pipeline
- 推荐 (跟 weiying overnight-loop.sh 模式协同)

---

## 验收 (5 字段)

| # | 字段 | 验证 |
|---|---|---|
| 1 | path | `ls ~/.agents/skills/auto-feishu-digest/` |
| 2 | env | `env \| grep -E "LARK_\|BAPP_\|TABLE_ID_"` |
| 3 | 抓源 | `bash digest-collect.sh --source=arxiv --dry-run` (返回 200) |
| 4 | 评分 | `bash digest-score.sh --dry-run` |
| 5 | 写表 | `bash digest-publish.sh --verify` (Bitable 4 表可读) |

---

## 🔗 相关

- `~/.agents/skills/auto-feishu-digest/SKILL.md` §架构 + 双轨
- `~/.agents/skills/auto-feishu-digest/templates/feishu-bit-schema.md` 4 表字段定义
- `~/.agents/skills/auto-feishu-digest/templates/daily-digest.md` daily 输出 schema
- `~/.agents/skills/auto-feishu-digest/templates/weekly-digest.md` weekly 输出 schema
