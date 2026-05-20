---
name: feishu-agent
description: 飞书 Bitable 持久化代理——自然语言 CRUD、URL 解析、schema 缓存、OAuth 自动映射
user-invocable: true
license: MIT
metadata:
  version: "1.0.0"
  author: mykcs
  category: integration
  triggers:
    - feishu
    - lark
    - bitable
    - 飞书
    - 多维表格
    - 豆仓
  trigger-patterns:
    - "/feishu"
    - "update feishu"
    - "lark-cli"
  tags:
    - feishu
    - lark
    - bitable
    - crud
---

# Feishu Agent Skill

## 用途

将飞书 Bitable 的重复摩擦（share-token vs record_id、OAuth scope、字段映射）封装为一次调用的持久化代理。支持自然语言增删改查、schema 缓存、URL 自动解析。

## 触发方式

- `/feishu <command>`
- 中文/英文关键词：`feishu`, `lark`, `bitable`, `飞书`, `多维表格`, `豆仓`

## 核心能力

### 1. URL 解析（resolve_url）

输入任意飞书 URL，自动解析为 `(app_token, table_id, record_id)`：

| URL 类型 | 示例 | 解析结果 |
|---------|------|---------|
| Wiki share | `https://xxx.feishu.cn/wiki/ABCdef` | share_token → obj_token → app_token |
| Bitable base | `https://xxx.feishu.cn/base/XYZ123` | app_token=XYZ123 |
| Bitable record | `.../base/XYZ123?table=tblAAA&view=vewBBB` | app_token, table_id, (可选)record_id |

**缓存**：解析结果写入 EverMem namespace `feishu-url-cache`，TTL 7 天。
> **降级策略**：若 EverMem MCP 不可用，跳过缓存直接解析，不阻塞操作。

### 2. Schema 内省与缓存

每个 base 的字段、类型、select/multi_select 选项枚举，首次查询后缓存到 EverMem namespace `feishu-schema-cache`。

```bash
# 获取 schema
lark-cli base field list --app-token <app_token> --table-id <table_id> --as user
```

### 3. 自然语言 CRUD

| 指令 | 行为 |
|------|------|
| `/feishu add <记录名称> with <字段>=<值>` | 查重 → 创建缺失选项 → 插入记录 |
| `/feishu update <记录名称> <字段> <值>` | 按名称查找 → PATCH 字段 |
| `/feishu list <表名> where <条件>` | 查询并格式化输出 |
| `/feishu delete <记录名称>` | 按名称查找 → 确认 → DELETE |

**示例（以咖啡豆数据库为例）**：
- `/feishu add bean konomi with notes floral,citrus`
- `/feishu update konomi roast-date 2026-05-08`
- `/feishu list beans where brand=月球`
- `/feishu delete konomi`

### 4. Upsert-First 写入

任何写入操作前，先按唯一字段（如"咖啡豆名称"）查询：

```bash
lark-cli base record list --app-token <app_token> --table-id <table_id> \
  --filter 'CurrentValue.[咖啡豆名称] = "konomi"' --as user
```

- 查到 → PATCH 更新
- 未查到 → 确认后 CREATE

### 5. OAuth Scope 自动映射

人类可读 scope 名 → lark-cli 标准 scope 名：

| 人类名称 | API scope |
|---------|-----------|
| 多维表格 | base |
| 文档 | docs / docx |
| 知识库 | wiki |
| 日历 | calendar |
| 任务 | task |

默认使用 `--recommend` 授权，覆盖常见 scope。遇 `permission_denied` 时提示重新授权。

## 执行流程

1. **解析 URL/token**：如果是 URL，走 resolve_url；如果已缓存，直接取缓存
2. **认证检查**：`lark-cli auth status` → 未登录则触发 `lark-cli auth login --recommend`
3. **Schema 检查**：无缓存则拉取 schema，缓存到 EverMem
4. **执行 CRUD**：按 Upsert-First 原则操作
5. **验证**：操作后读取记录确认写入成功
6. **归档**：如需，生成 case 记录到 `~/.claude/knowledge/cases/`

## 边界与限制

- **禁止裸 Create**：必须先查后写
- **Token 不外传**：`~/.lark-cli/` 内容不 cat 到对话
- **破坏性操作确认**：delete、字段删除、批量修改需用户确认
- **字段类型锁定**：不修改已有字段类型（修改字段类型 = 数据丢失，如需调整必须在飞书 UI 中操作）

## 回归测试

每次 skill 变更后运行（脚本不存在时跳过）：

```bash
# Test 1: URL 解析
[ -f ~/.claude/skills/feishu-agent/test_resolve_url.py ] && python3 ~/.claude/skills/feishu-agent/test_resolve_url.py || echo "SKIP: test_resolve_url.py not found"

# Test 2: Schema 缓存
[ -f ~/.claude/skills/feishu-agent/test_schema_cache.py ] && python3 ~/.claude/skills/feishu-agent/test_schema_cache.py || echo "SKIP: test_schema_cache.py not found"

# Test 3: Upsert 流程（dry-run）
[ -f ~/.claude/skills/feishu-agent/test_upsert_flow.py ] && python3 ~/.claude/skills/feishu-agent/test_upsert_flow.py --dry-run || echo "SKIP: test_upsert_flow.py not found"
```

## 依赖

- `lark-cli` 已安装且已 OAuth 授权
- EverMem MCP 可用（用于缓存）
- Python 3.10+（用于测试脚本）

## 相关规则

- `behavioral-feishu-lark-cli.md` — 飞书操作纪律
- `reference/lark-cli-user-auth-paradigm.md` — 用户身份授权模式
- `CASE-FEISHU-WIKI-BITABLE-OPERATIONS-20260503` — 完整踩坑记录
