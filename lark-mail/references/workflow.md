## 典型工作流

1. **确认身份** — 首次操作邮箱前先调用 `lark-cli mail user_mailboxes profile --params '{"user_mailbox_id":"me"}'` 获取当前用户的真实邮箱地址（`primary_email_address`），不要通过系统用户名猜测。后续判断"发件人是否为用户本人"时以此地址为准。
2. **浏览** — `+triage` 查看收件箱摘要，获取 `message_id` / `thread_id`
3. **阅读** — `+message` 读单封邮件，`+thread` 读整个会话
4. **回复** — `+reply` / `+reply-all`（默认存草稿，加 `--confirm-send` 则立即发送）
5. **转发** — `+forward`（默认存草稿，加 `--confirm-send` 则立即发送）
6. **新邮件** — `+send` 存草稿（默认），加 `--confirm-send` 发送
7. **确认投递** — 立即发送后用 `send_status` 查询投递状态，定时发送后在预定时间后再查询；取消定时发送用 `cancel_scheduled_send`
8. **编辑草稿** — `+draft-edit` 修改已有草稿。正文编辑通过 `--patch-file`：回复/转发草稿用 `set_reply_body` op 保留引用区，普通草稿用 `set_body` op

对于所有发信场景，默认话术应偏向：
- 先创建草稿
- 若当前结果返回了草稿打开链接，直接把链接展示给用户
- 若用户需要，再继续帮他修改草稿或执行发送
- 若本次产出了草稿且不是直接发信，则优先展示草稿打开链接；若当前输出没有链接，则静默处理

### CRITICAL — 首次使用任何命令前先查 `-h`

无论是 Shortcut（`+triage`、`+send` 等）还是原生 API，**首次调用前必须先运行 `-h` 查看可用参数**，不要猜测参数名称：

```bash
# Shortcut
lark-cli mail +triage -h
lark-cli mail +send -h

# 原生 API（逐级查看）
lark-cli mail user_mailbox.messages -h
```

`-h` 输出即可用 flag 的权威来源。reference 文档中的参数表可辅助理解语义，但实际 flag 名称以 `-h` 为准。

### 收件人搜索：查找邮箱地址

当需要查找收件人邮箱地址时，使用联系人搜索接口。支持多种搜索方式，如：
- **按人名搜索**：如"给张三发邮件" → query="张三"
- **按邮箱关键词搜索**：如"发到 larkmail 的邮箱" → query="@larkmail"
- **按群名搜索**：如"发给项目群" → query="项目群"

```bash
lark-cli mail multi_entity search --as user --data '{"query":"<关键词>"}'
```

搜索结果包含多种实体类型：

| `type` 值 | `tag` 示例 | 说明 |
|-----------|-----------|------|
| `user` / `chatter` | `chatter` | 个人用户 |
| `enterprise_mail_group` | `mail_group` | 企业邮件组 |
| `chat` / `group` | `chat_group_tenant` / `chat_group_normal` | 群聊（有群邮件地址） |
| `external_contact` | `external_contact` | 外部联系人 |

**处理规则：**
1. 从结果中筛选有 `email` 字段的条目
2. 无论匹配数量多少，都必须列出候选项供用户确认后再使用（搜索是模糊匹配，单条结果不代表精确命中）。展示尽可能多的字段帮助用户区分：
   ```text
   找到以下匹配"张三"的结果：
   1. 张三 <zhangsan@example.com>
      类型：user | 部门：研发团队
   ---
   找到多个匹配"组"的结果，请选择：
   1. 团队邮件组 <team@example.com>
      类型：enterprise_mail_group | 标签：mail_group
   2. 项目群 <project@example.com>
      类型：chat | 成员数：50 | 标签：chat_group_normal
   3. 张群 <zhangqun@example.com>
      类型：user | 部门：研发团队 | 备注名：张群同学
   ```
   可用字段：`name`（名称）、`email`（邮箱）、`department`（部门）、`tag`（标签）、`display_name`（备注名）、`type`（实体类型）、`member_count`（成员数，群类型时展示）。字段为空时省略。
3. 若无匹配，告知用户未找到，建议换关键词或直接提供邮箱地址
4. 用户确认后，将 `email` 传入 compose shortcut 的 `--to` / `--cc` / `--bcc` 参数

**注意：** 用户直接提供完整邮箱地址时不需要搜索，直接使用即可。

### 命令选择：先判断邮件类型，再决定草稿还是发送

| 邮件类型 | 存草稿（不发送） | 直接发送 | 定时发送 |
|----------|-----------------|---------|----------|
| **新邮件** | `+send` 或 `+draft-create` | `+send --confirm-send` | `+send --confirm-send --send-time <unix_timestamp>` |
| **回复** | `+reply` 或 `+reply-all` | `+reply --confirm-send` 或 `+reply-all --confirm-send` | `+reply --confirm-send --send-time <unix_timestamp>` 或 `+reply-all --confirm-send --send-time <unix_timestamp>` |
| **转发** | `+forward` | `+forward --confirm-send` | `+forward --confirm-send --send-time <unix_timestamp>` |

- 有原邮件上下文 → 用 `+reply` / `+reply-all` / `+forward`（默认即草稿），**不要用 `+draft-create`**
- **发送前必须向用户确认收件人和内容；如有必要，可引导用户去飞书邮件里打开草稿查看详情；用户明确同意后才可执行发送或使用 `--confirm-send`**
- **发送后必须调用 `send_status` 确认投递状态**；定时发送（`--send-time`）在预定发送时间后再查询，取消定时发送用 `cancel_scheduled_send`（详见下方说明）

> **定时发送注意事项**：`--send-time` 必须与 `--confirm-send` 配合使用，不能单独使用。`send_time` 为 Unix 时间戳（秒），需至少为当前时间 + 5 分钟。

### 使用公共邮箱或别名（send_as）发信

当用户需要用非主账号地址发信时，使用 `--mailbox` 指定邮箱、`--from` 指定发件人地址。

- `--mailbox` 传邮箱地址（如 `shared@example.com` 或 `me`），可通过 `accessible_mailboxes` 查询可用值
- `--from` 传发信地址（别名、邮件组等），可通过 `send_as` 查询可用值

**查询可用邮箱和发信地址：**

```bash
# 查询可访问的邮箱（主邮箱 + 公共邮箱）
lark-cli mail user_mailboxes accessible_mailboxes --params '{"user_mailbox_id":"me"}'

# 查询某个邮箱的可用发信地址（主地址、别名、邮件组）
lark-cli mail user_mailbox.settings send_as --params '{"user_mailbox_id":"me"}'
```

**公共邮箱发信：**

```bash
# --mailbox 指定公共邮箱，From 头自动使用该邮箱地址
lark-cli mail +send --mailbox shared@example.com \
  --to bob@example.com --subject '通知' --body '<p>你好</p>'
```

**别名发信：**

```bash
# --mailbox 指定所属邮箱，--from 指定别名地址
lark-cli mail +send --mailbox me --from alias@example.com \
  --to bob@example.com --subject '测试' --body '<p>你好</p>'
```

不使用公共邮箱或别名时无需指定 `--mailbox`，行为与之前一致。

### 发送后确认投递状态

**立即发送（无 `--send-time`）**：邮件发送成功后（收到 `message_id`），**必须**调用 `send_status` API 查询投递状态并向用户报告：

```bash
lark-cli mail user_mailbox.messages send_status --params '{"user_mailbox_id":"me","message_id":"<发送返回的 message_id>"}'
```

返回每个收件人的投递状态（`status`）：1=正在投递, 2=投递失败重试, 3=退信, 4=投递成功, 5=待审批, 6=审批拒绝。向用户简要报告结果，如有异常状态（退信/审批拒绝）需重点提示。

**定时发送（指定了 `--send-time`）**：定时发送不会立即产生 `message_id`，`send_status` 在定时发送成功后会返回"待发送"状态，**不建议在定时发送后立即查询**。可在预定发送时间后再查询。如需取消定时发送：

```bash
lark-cli mail user_mailbox.drafts cancel_scheduled_send --params '{"user_mailbox_id":"me","draft_id":"<draft_id>"}'
```

**取消后邮件会变回草稿**，可继续编辑或在之后重新发送。

### 撤回邮件

发送成功后，若响应中包含 `recall_available: true`，说明该邮件支持撤回（24 小时内已投递的邮件）。

**撤回操作：**
```bash
lark-cli mail user_mailbox.sent_messages recall --as user \
  --params '{"user_mailbox_id":"me","message_id":"<message_id>"}'
```

- 返回 `recall_status: available` 表示撤回请求已受理（异步执行）
- 返回 `recall_status: unavailable` 表示不可撤回，`recall_restriction_reason` 说明原因

**查询撤回进度：**
```bash
lark-cli mail user_mailbox.sent_messages get_recall_detail --as user \
  --params '{"user_mailbox_id":"me","message_id":"<message_id>"}'
```

- `recall_status: in_progress` — 撤回进行中，可稍后再查
- `recall_status: done` — 撤回完成，查看 `recall_result`（`all_success` / `all_fail` / `some_fail`）和每个收件人的详情

**注意：** 撤回是异步操作，`recall` 返回成功仅表示请求已受理，实际结果需通过 `get_recall_detail` 查询。若响应中无 `recall_available` 字段，说明该邮件或应用不支持撤回，不要主动提及撤回。

### 正文格式：优先使用 HTML

撰写邮件正文时，**默认使用 HTML 格式**（body 内容会被自动检测）。仅当用户明确要求纯文本时，才使用 `--plain-text` 标志强制纯文本模式。

- HTML 支持粗体、列表、链接、段落等富文本排版，收件人阅读体验更好
- 所有发送类命令（`+send`、`+reply`、`+reply-all`、`+forward`、`+draft-create`）都支持自动检测 HTML，可通过 `--plain-text` 强制纯文本
- 纯文本仅适用于极简内容（如一句话回复 "收到"）

```bash
# ✅ 推荐：HTML 格式
lark-cli mail +send --to alice@example.com --subject '周报' \
  --body '<p>本周进展：</p><ul><li>完成 A 模块</li><li>修复 3 个 bug</li></ul>'

# ⚠️ 仅在内容极简时使用纯文本
lark-cli mail +reply --message-id <id> --body '收到，谢谢'
```

### 读取邮件：按需控制返回内容

`+message`、`+messages`、`+thread` 默认返回 HTML 正文（`--html=true`）。仅需确认操作结果（如验证标记已读、移动文件夹是否成功）时，用 `--html=false` 跳过 HTML 正文，只返回纯文本，显著减少 token 消耗。

输出默认为结构化 JSON，可直接读取，无需额外编码转换。

```bash
# ✅ 验证操作结果：不需要 HTML
lark-cli mail +message --message-id <id> --html=false

# ✅ 需要阅读完整内容：保持默认
lark-cli mail +message --message-id <id>
```


📂 **原生 API 调用规则** → see [`references/native-api-rules.md`](references/native-api-rules.md) (loaded on demand)
