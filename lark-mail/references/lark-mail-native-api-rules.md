---
name: lark-mail-native-api-rules
description: "飞书邮箱原生 API 调用规则与示例。仅在 Shortcut 未覆盖、必须使用原生 API 时引用。"
---

# lark-mail 原生 API 调用规则

> 从 `lark-mail/SKILL.md` 拆出，避免主 SKILL.md 超过 500 行 hot-path token 限制。

## 何时使用原生 API

没有 Shortcut 覆盖的操作才使用原生 API。调用步骤以本节为准（API Resources 章节见 `references/lark-mail-api-resources.md`）。

## Step 1 — 用 `-h` 确定要调用的 API（必须，不可跳过）

先通过 `-h` 逐级查看可用命令，确定正确的 `<resource>` 和 `<method>`：

```bash
# 第一级：查看 mail 下所有资源
lark-cli mail -h

# 第二级：查看某个资源下所有方法
lark-cli mail user_mailbox.messages -h
```

`-h` 输出的就是可执行的命令格式（空格分隔）。**不要跳过此步直接查 schema，不要猜测命令名称。**

## Step 2 — 查 schema，获取参数定义

确定 `<resource>` 和 `<method>` 后，查 schema 了解参数：

```bash
lark-cli schema mail.<resource>.<method>
# 例如：lark-cli schema mail.user_mailbox.messages.modify_message
```

> **⚠️ 注意**：① 必须精确到 method 级别，禁止查 resource 级别（如 `lark-cli schema mail.user_mailbox.messages`，输出 78K）。② schema 路径用 `.` 分隔（`mail.user_mailbox.messages.modify_message`），但 CLI 命令在 resource 和 method 之间用**空格**（`lark-cli mail user_mailbox.messages modify_message`），不要混淆。

schema 输出是 JSON，包含两个关键部分：

| schema JSON 字段 | CLI 标志 | 含义 |
|---|---|---|
| `parameters`（每个字段有 `location`） | `--params '{...}'` | URL 路径参数 (`location:"path"`) 和查询参数 (`location:"query"`) |
| `requestBody` | `--data '{...}'` | 请求体（仅 POST / PUT / PATCH / DELETE 有） |

**速记：schema 中有 `location` 字段的 → `--params`；在 `requestBody` 下的 → `--data`。二者绝对不能混放。** path 参数和 query 参数统一放 `--params`，CLI 自动把 path 参数填入 URL。

## Step 3 — 构造命令

按 Step 2 的映射规则，拼接命令：

```
lark-cli mail <resource> <method> --params '{...}' [--data '{...}']
```

## 示例

**GET — 只有 `--params`**（`parameters` 中有 path + query，无 `requestBody`）：

```bash
# schema 中：user_mailbox_id (path, required), page_size (query, required), folder_id (query, optional)
lark-cli mail user_mailbox.messages list \
  --params '{"user_mailbox_id":"me","page_size":20,"folder_id":"INBOX"}'
```

**POST — `--params` + `--data`**（`parameters` 中有 path，`requestBody` 有 body 字段）：

```bash
# schema 中：parameters → user_mailbox_id (path, required)
#            requestBody → name (required), parent_folder_id (required)
lark-cli mail user_mailbox.folders create \
  --params '{"user_mailbox_id":"me"}' \
  --data '{"name":"newsletter","parent_folder_id":"0"}'
```

## 常用约定

- `user_mailbox_id` 几乎所有邮箱 API 都需要，一般传 `"me"` 代表当前用户
- 列表接口支持 `--page-all` 自动翻页，无需手动处理 `page_token`
