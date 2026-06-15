---
name: lark-mail-api-resources
description: "飞书邮箱 API Resources + 权限表 速查。仅在需要查找原生 API 路径或对应 scope 时引用。"
---

# lark-mail API Resources 速查

> 从 `lark-mail/SKILL.md` 拆出，避免主 SKILL.md 超过 500 行 hot-path token 限制。

## API Resources

```bash
lark-cli schema mail.<resource>.<method>   # 调用 API 前必须先查看参数结构
lark-cli mail <resource> <method> [flags] # 调用 API
```

> **重要**：使用原生 API 时，必须先运行 `schema` 查看 `--data` / `--params` 参数结构，不要猜测字段格式。

### multi_entity

  - `search` — 适用于写信联系人搜索

### user_mailboxes

  - `accessible_mailboxes` — 列出可访问的邮箱
  - `profile` — 获取用户邮箱信息
  - `search` — 搜索邮件

### user_mailbox.drafts

  - `cancel_scheduled_send` — 取消定时发送
  - `create` — 创建草稿
  - `delete` — 删除草稿
  - `get` — 获取草稿内容
  - `list` — 列出草稿列表
  - `send` — 发送草稿
  - `update` — 更新草稿

### user_mailbox.event

  - `subscribe` — 订阅事件
  - `subscription` — 获取订阅状态
  - `unsubscribe` — 取消订阅

### user_mailbox.folders

  - `create` — 创建邮箱文件夹
  - `delete` — 删除邮箱文件夹
  - `get` — 获取邮箱文件夹信息
  - `list` — 列出邮箱文件夹
  - `patch` — 修改邮箱文件夹

### user_mailbox.labels

  - `create` — 创建标签
  - `delete` — 删除标签
  - `get` — 获取标签信息
  - `list` — 列出标签
  - `patch` — 更新标签

### user_mailbox.mail_contacts

  - `create` — 创建邮箱联系人
  - `delete` — 删除邮箱联系人
  - `list` — 列出邮箱联系人
  - `patch` — 修改邮箱联系人信息

### user_mailbox.message.attachments

  - `download_url` — 获取附件下载链接

### user_mailbox.messages

  - `batch_get` — 批量获取邮件详情
  - `batch_modify` — 批量修改邮件
  - `batch_trash` — 批量删除邮件
  - `get` — 获取邮件详情
  - `list` — 列出邮件
  - `modify` — 修改邮件
  - `send_status` — 查询邮件发送状态
  - `trash` — 删除邮件

### user_mailbox.rules

  - `create` — 创建收信规则
  - `delete` — 删除收信规则
  - `list` — 列出收信规则
  - `reorder` — 对收信规则进行排序
  - `update` — 更新收信规则

### user_mailbox.sent_messages

  - `get_recall_detail` — 查询邮件撤回进度
  - `recall` — 撤回已发送的邮件

### user_mailbox.settings

  - `send_as` — 列出可发信邮箱

### user_mailbox.template.attachments

  - `download_url` — 获取模板附件下载链接

### user_mailbox.templates

  - `create` — 创建个人邮件模板
  - `delete` — 删除指定邮件模板
  - `get` — 获取指定邮件模板详情
  - `list` — 列出指定邮箱下的全部个人邮件模板（不分页，仅返回 id 与 name）
  - `update` — 全量替换指定邮件模板内容

### user_mailbox.threads

  - `batch_modify` — 批量修改邮件会话
  - `batch_trash` — 批量删除邮件会话
  - `get` — 获取邮件会话详情
  - `list` — 列出邮件会话
  - `modify` — 修改邮件会话
  - `trash` — 删除邮件会话

## 权限表

| 方法 | 所需 scope |
|------|-----------|
| `multi_entity.search` | `mail:user_mailbox:readonly` |
| `user_mailboxes.accessible_mailboxes` | `mail:user_mailbox:readonly` |
| `user_mailboxes.profile` | `mail:user_mailbox:readonly` |
| `user_mailboxes.search` | `mail:user_mailbox.message:readonly` |
| `user_mailbox.drafts.cancel_scheduled_send` | `mail:user_mailbox.message:send` |
| `user_mailbox.drafts.create` | `mail:user_mailbox.message:modify` |
| `user_mailbox.drafts.delete` | `mail:user_mailbox.message:modify` |
| `user_mailbox.drafts.get` | `mail:user_mailbox.message:readonly` |
| `user_mailbox.drafts.list` | `mail:user_mailbox.message:readonly` |
| `user_mailbox.drafts.send` | `mail:user_mailbox.message:send` |
| `user_mailbox.drafts.update` | `mail:user_mailbox.message:modify` |
| `user_mailbox.event.subscribe` | `mail:event` |
| `user_mailbox.event.subscription` | `mail:event` |
| `user_mailbox.event.unsubscribe` | `mail:event` |
| `user_mailbox.folders.create` | `mail:user_mailbox.folder:write` |
| `user_mailbox.folders.delete` | `mail:user_mailbox.folder:write` |
| `user_mailbox.folders.get` | `mail:user_mailbox.folder:read` |
| `user_mailbox.folders.list` | `mail:user_mailbox.folder:read` |
| `user_mailbox.folders.patch` | `mail:user_mailbox.folder:write` |
| `user_mailbox.labels.create` | `mail:user_mailbox.message:modify` |
| `user_mailbox.labels.delete` | `mail:user_mailbox.message:modify` |
| `user_mailbox.labels.get` | `mail:user_mailbox.message:modify` |
| `user_mailbox.labels.list` | `mail:user_mailbox.message:modify` |
| `user_mailbox.labels.patch` | `mail:user_mailbox.message:modify` |
| `user_mailbox.mail_contacts.create` | `mail:user_mailbox.mail_contact:write` |
| `user_mailbox.mail_contacts.delete` | `mail:user_mailbox.mail_contact:write` |
| `user_mailbox.mail_contacts.list` | `mail:user_mailbox.mail_contact:read` |
| `user_mailbox.mail_contacts.patch` | `mail:user_mailbox.mail_contact:write` |
| `user_mailbox.message.attachments.download_url` | `mail:user_mailbox.message.body:read` |
| `user_mailbox.messages.batch_get` | `mail:user_mailbox.message:readonly` |
| `user_mailbox.messages.batch_modify` | `mail:user_mailbox.message:modify` |
| `user_mailbox.messages.batch_trash` | `mail:user_mailbox.message:modify` |
| `user_mailbox.messages.get` | `mail:user_mailbox.message:readonly` |
| `user_mailbox.messages.list` | `mail:user_mailbox.message:readonly` |
| `user_mailbox.messages.modify` | `mail:user_mailbox.message:modify` |
| `user_mailbox.messages.send_status` | `mail:user_mailbox.message:readonly` |
| `user_mailbox.messages.trash` | `mail:user_mailbox.message:modify` |
| `user_mailbox.rules.create` | `mail:user_mailbox.rule:write` |
| `user_mailbox.rules.delete` | `mail:user_mailbox.rule:write` |
| `user_mailbox.rules.list` | `mail:user_mailbox.rule:read` |
| `user_mailbox.rules.reorder` | `mail:user_mailbox.rule:write` |
| `user_mailbox.rules.update` | `mail:user_mailbox.rule:write` |
| `user_mailbox.sent_messages.get_recall_detail` | `mail:user_mailbox.message:readonly` |
| `user_mailbox.sent_messages.recall` | `mail:user_mailbox.message:modify` |
| `user_mailbox.settings.send_as` | `mail:user_mailbox:readonly` |
| `user_mailbox.template.attachments.download_url` | `mail:user_mailbox.message:readonly` |
| `user_mailbox.templates.create` | `mail:user_mailbox.message:modify` |
| `user_mailbox.templates.delete` | `mail:user_mailbox.message:modify` |
| `user_mailbox.templates.get` | `mail:user_mailbox.message:modify` |
| `user_mailbox.templates.list` | `mail:user_mailbox.message:modify` |
| `user_mailbox.templates.update` | `mail:user_mailbox.message:modify` |
| `user_mailbox.threads.batch_modify` | `mail:user_mailbox.message:modify` |
| `user_mailbox.threads.batch_trash` | `mail:user_mailbox.message:modify` |
| `user_mailbox.threads.get` | `mail:user_mailbox.message:readonly` |
| `user_mailbox.threads.list` | `mail:user_mailbox.message:readonly` |
| `user_mailbox.threads.modify` | `mail:user_mailbox.message:modify` |
| `user_mailbox.threads.trash` | `mail:user_mailbox.message:modify` |
