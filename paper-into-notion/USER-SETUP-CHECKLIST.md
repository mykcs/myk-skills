# User-Side Setup Checklist — paper-into-notion v1.0 (无 token 配, 走 ntn CLI keychain)

> **状态**: v1.0 (2026-07-13) — ntn CLI 已走 macOS keychain, **不需要** 手动配 token / API key
> **skill**: `~/.agents/skills/paper-into-notion v1.0` (commit 待 push, ADR-0057)
> **核心改动**: 5 步 setup 全是 verify 类 (无手动 export), 跟 weekly-report-phd 同 keychain 流程

---

## Step 0: 为什么无 token 配 (per weekly-report-phd §C.3)

**之前 (v0.x 假设)**: user 每次跑要 `export NOTION_TOKEN=xxx`, 换电脑 / 重装就丢
**v1.0 起**: 走 ntn 0.18.1 CLI + macOS keychain 自动 auth, **没有任何 token env**
- 装 ntn CLI (`brew install notion-terminal` 或 `pip install notion-terminal`)
- `ntn login` 一次 → macOS keychain 持久存
- 后续跑 paper-into-notion.sh 自动读 keychain
- **不污染公共 shell source** (`~/.zshrc` 不动)

---

## Step 1: 装 ntn CLI (1 min)

```bash
# macOS
brew install notion-terminal

# 或 Python pip
pip install notion-terminal
```

期望: `ntn --version` → `ntn 0.18.1` 或更新

---

## Step 2: ntn login (1 min, 一次)

```bash
ntn login
# 期望: 浏览器跳 OAuth 页面 → 选 workspace "zju_wy" → 授权 mykcs01@163.com bot
# 期望输出: "✅ Authenticated as mykcs01@163.com in workspace zju_wy"
```

**没看到 "zju_wy" workspace** → user 找 admin 加 bot 到 workspace

---

## Step 3: 拿 Notion data source ID (2 min)

如果 user 已经知道 `data source ID = 398fedee-6267-80d6-92e5-000b54d8821e` → 跳过

否则:
```bash
# 1. 打开 https://www.notion.so/zju_wy/论文-<database_id>
#    URL 那段 32 位 hex = database_id
# 2. ntn 列 data sources (新版 API 必走 data source)
ntn api --method GET "/v1/databases/$DATABASE_ID" -H "Notion-Version: 2026-03-11"
# 期望: JSON 含 data_sources[].id 字段, 第一个 = data_source_id
```

---

## Step 4: 验证 (30 sec, 全 ✅ 期望)

```bash
bash ~/.agents/skills/paper-into-notion/scripts/paper-into-notion.sh --verify
```

**期望输出 (全 ✅)**:
```
[1] ntn CLI 安装: ✅ ntn 0.18.1
[2] ntn whoami: ✅ mykcs01@163.com @ zju_wy
[3] Notion-Version: ✅ 2026-03-11
[4] Data Source ID: ✅ 398fedee-6267-80d6-92e5-000b54d8821e
[5] 5 pattern 模态: ✅ arxiv / 公众号 / 博客 / Twitter / 其他
[6] arXiv API: ✅ export.arxiv.org 200 OK
[7] multi_select 保护 grader: ✅ PASS
```

任何一个 ❌ → 检查 Step 1-3, 重新 login 后再跑

---

## Step 5: 真跑一次 (1 min)

```bash
bash ~/.agents/skills/paper-into-notion/scripts/paper-into-notion.sh https://arxiv.org/abs/1706.03762

# 期望:
# ✅ record_id: xxx-xxx-xxx
# ✅ page_url: https://www.notion.so/...
# ✅ 3 字段填对 (页面=Attention Is All You Need, 状态=未开始, 模态类型=arXiv)
# ✅ multi_select 保护: 教育类型=[], 标签=[], 关键词=[] (新建 page 全空, 符合预期)
```

**回 "跑通" 给 claudecode** → 5 字段验收 + case 立到 `~/.claude/knowledge/cases/wiki/CASE-PAPER-INTO-NOTION-SKILL-V1-20260713.md`

---

## ❓ 3 个常见坑

### 坑 1: ntn login 找不到 workspace "zju_wy"
**症状**: login 后 `ntn whoami` 返的不是 mykcs01@163.com
**修复**: 检查 OAuth 授权的邮箱, 跟 Notion workspace owner 一致

### 坑 2: data source ID 错
**症状**: query 返 404 "data source not found"
**修复**: 走 Step 3 重新拿 ID, 写入 .env

### 坑 3: arXiv rate limit
**症状**: arxiv-fetch.sh 重试 3 次都失败 (per Q4)
**修复**: sleep 10s 再跑 (实测 rate limit 1 req/3s 是软约束, 但 5s 内多次 burst 会被拒)

---

## 🔗 资源

- ntn CLI 文档: `ntn --help` (本机已装或 Step 1 装)
- Notion API 文档: https://developers.notion.com/reference/intro
- arXiv API 文档: https://arxiv.org/help/api
- skill 完整文档: `~/.agents/skills/paper-into-notion/SKILL.md`
- 配套 weekly-report-phd skill: `~/.agents/skills/weekly-report-phd/SKILL.md` (ntn 0.18.1 用法)

---

## ⏱ 时间估算

| Step | 时间 |
|---|---|
| Step 1 (ntn install) | 1 min |
| Step 2 (ntn login) | 1 min |
| Step 3 (data source ID) | 2 min |
| Step 4 (verify) | 30 sec |
| Step 5 (真跑一次) | 1 min |

**总用户时间**: ~5 min (首次), 后续跑 skill 不用动。