---
name: feishu-agent
version: 1.1.0
description: "飞书 Bitable 自然语言代理：自然语言 CRUD、URL 解析、Schema 缓存、Upsert-First 写入。处理飞书多维表格的日常增删改查时调用。当用户用自然语言描述 Bitable 操作（如「往咖啡豆表里加一条」「更新 x 的价格」）时使用。"
metadata:
  requires:
    bins: ["lark-cli"]
  cliHelp: "lark-cli base --help"
---

# feishu-agent (v1.1)

> **前置条件：** 先阅读 [`../lark-shared/SKILL.md`](../lark-shared/SKILL.md)，其中包含认证、权限处理和安全规则。
> **执行前必做：** 执行任何 base 命令前，必须先确认 base token 和 table id，再按 Shortcuts 表格调用对应命令。

## 何时使用本 Skill

### 1.1 触发条件

以下场景应使用本 skill：

- 用户用自然语言操作飞书多维表格（"加一条记录""帮我查一下""更新某个值"）
- 用户给了一个飞书 Bitable 或 Wiki URL
- 用户提到 coffee bean / 咖啡豆 / 豆仓 等特定数据集的名称

以下场景不应使用本 skill：

- 用户直接说「用 lark-cli 操作 Base」或给出了完整的 lark-cli 命令 → 走 `lark-base` skill
- 用户要做字段设计、公式字段、跨表计算、数据分析 → 走 `lark-base` skill
- 用户只是查认证状态、切换身份 → 先读 `lark-shared`

### 1.2 与 lark-base 的分工

| 需求 | 用哪个 skill |
|------|-------------|
| 自然语言 CRUD（加/查/改/删记录） | `feishu-agent`（本 skill） |
| 给 URL / token，直接读写记录 | `feishu-agent`（本 skill） |
| 建表、改字段、视图管理、公式设计 | `lark-base` |
| 批量操作、数据分析、跨表计算 | `lark-base` |

---

## 核心概念

- **Base（多维表格）**：飞书多维表格，通过 `--app-token`（也叫 `base-token`）定位
- **Table（数据表）**：Base 内部的一张表，通过 `--table-id` 定位
- **Record（记录）**：表中的一行数据
- **Upsert-First**：写入前先查，存在则更新，不存在才创建。避免重复记录。

---

## Shortcuts（推荐优先使用）

| Shortcut | 适用场景 | 说明 |
|----------|---------|------|
| `+resolve` | 用户给了 URL | 解析飞书 URL → (app_token, table_id, record_id) |
| `+upsert` | 自然语言新增或更新记录 | 查重 → 存在则 PATCH，不存在则 CREATE |
| `+get` | 查询单条或多条记录 | 按条件筛选并格式化输出 |
| `+list` | 列出表内所有记录 | 适合数据量小（<100条）的表 |
| `+delete` | 删除记录 | 按名称查找 → 确认 → DELETE |

### `+resolve` — URL 解析

将飞书 URL 解析为 base 操作所需的 token 元组。

```bash
lark-cli wiki +node-get --token <wiki_url_or_token>
# 若返回 obj_type=bitable → 取 obj_token 作为 app_token
# 若直接是 base URL → app_token = URL 中的 /base/ 后那段
```

**支持的 URL 类型：**

| URL 类型 | 示例 | 解析结果 |
|---------|------|---------|
| Wiki 节点 | `https://xxx.feishu.cn/wiki/ABCdef` | `share_token → obj_token → app_token`（若 obj_type=bitable） |
| Bitable base | `https://xxx.feishu.cn/base/XYZ123` | `app_token = XYZ123` |
| Bitable 带参数 | `.../base/XYZ123?table=tblAAA&record=recBBB` | `app_token, table_id, record_id` |

解析完成后，将 `(app_token, table_id)` 记住，后续操作复用。

### `+upsert` — 新增或更新记录（Upsert-First）

**这是本 skill 最核心的操作。**

```
意图：往表里加一条 / 更新某条记录
输入：表名（或 URL）、记录名称字段值、字段=值 对
输出：操作结果（创建成功 / 更新成功 / 查不到记录）
```

**执行步骤：**

1. **确认 base token 和 table id** — 若用户只给了表名，先用 `+resolve` 从 URL 解析；若无 URL，尝试从已知信息推断
2. **拉取 schema**（首次操作或新 base）确认字段名和类型
3. **按唯一字段（如"名称""咖啡豆名称"）查重**
   ```bash
   lark-cli base record list \
     --app-token <app_token> --table-id <table_id> \
     --filter 'CurrentValue.[咖啡豆名称] = "konomi"' --as user
   ```
4. **分支处理**
   - **查到 → PATCH 更新**（只改提供的字段，保留其他字段）
   - **未查到 → CREATE 新记录**
5. **验证**：操作后读一条记录确认写入成功

**示例流程：**

用户：「往豆仓里加一条，豆子名称 konomi，产地 埃塞俄比亚，风味 floral,citrus」

```bash
# Step 1: 确认 token（假设已知 app_token=XYZ123, table_id=tblAAA）
# Step 2: 拉 schema（首次）
lark-cli base field list --app-token XYZ123 --table-id tblAAA --as user
# Step 3: 查重
lark-cli base record list \
  --app-token XYZ123 --table-id tblAAA \
  --filter 'CurrentValue.[豆子名称] = "konomi"' --as user
# Step 4a: 若未查到 → 创建
lark-cli base record create \
  --app-token XYZ123 --table-id tblAAA \
  --fields '{"豆子名称":"konomi","产地":"埃塞俄比亚","风味":"floral,citrus"}' --as user
# Step 4b: 若查到 → 更新（只 PATCH 提供了的字段）
lark-cli base record patch \
  --app-token XYZ123 --table-id tblAAA --record-id <existing_record_id> \
  --fields '{"产地":"埃塞俄比亚","风味":"floral,citrus"}' --as user
```

### `+get` — 查询记录

```bash
# 按条件查
lark-cli base record list \
  --app-token <app_token> --table-id <table_id> \
  --filter 'CurrentValue.[产地] = "埃塞俄比亚"' --as user

# 格式化输出（用 --format json 或直接读 JSON 贴给用户）
```

### `+list` — 列出所有记录

```bash
lark-cli base record list \
  --app-token <app_token> --table-id <table_id> --as user
```

> 适用于 100 条以内的小表。大表请用 `+get` 带 filter。

### `+delete` — 删除记录

```bash
# 先查 record_id
lark-cli base record list \
  --app-token <app_token> --table-id <table_id> \
  --filter 'CurrentValue.[豆子名称] = "konomi"' --as user

# 确认后再删（高风险操作，若 record 存在则提示用户确认）
lark-cli base record delete \
  --app-token <app_token> --table-id <table_id> \
  --record-id <record_id> --as user
```

---

## 自然语言意图路由

用户说话时，按以下规则路由：

| 用户意图 | 对应操作 |
|---------|---------|
| "加一条""新增""录入""添加" | `+upsert`（优先 CREATE） |
| "更新""改一下""修改" | `+upsert`（优先 PATCH） |
| "查一下""看看""有没有" | `+get` |
| "列出""全部""有哪些" | `+list` |
| "删掉""删除""移除" | `+delete` |

---

## 重要约束

- **禁止裸 Create**：所有写入必须先查重再决定 CREATE 或 PATCH
- **Token 不外传**：不把 token 值 cat/打印到对话中
- **破坏性操作（delete）必须确认**：向用户展示目标记录，征得同意后再执行
- **字段类型锁定**：不修改已有字段类型（修改字段类型 = 数据丢失）
- **验证延迟**：写入后等待 2 秒再读取验证（数据同步延迟）

---

## 依赖

- `lark-cli` 已安装且已完成 OAuth 授权（`--as user` 需要 `auth login`）
- 无 EverMem 依赖（降级：始终直接解析，不依赖缓存）
