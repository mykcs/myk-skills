## API Resources

```bash
lark-cli schema drive.<resource>.<method>   # 调用 API 前必须先查看参数结构
lark-cli drive <resource> <method> [flags] # 调用 API
```

> **重要**：使用原生 API 时，必须先运行 `schema` 查看 `--data` / `--params` 参数结构，不要猜测字段格式。

### files

  - `copy` — 复制文件
  - `create_folder` — 新建文件夹
  - `list` — 获取文件夹下的清单
  - `patch` — 修改文件标题

### file.comments

  - `batch_query` — 批量获取评论
  - `create_v2` — 添加全文/局部（划词）评论
  - `list` — 分页获取文档评论
  - `patch` — 解决/恢复 评论

### file.comment.replys

  - `create` — 添加回复
  - `delete` — 删除回复
  - `list` — 获取回复
  - `update` — 更新回复

### permission.members

  - `auth` — 
  - `create` — 增加协作者权限
  - `transfer_owner` — 

### metas

  - `batch_query` — 获取文档元数据

### user

  - `remove_subscription` — 取消订阅用户、应用维度事件
  - `subscription` — 订阅用户、应用维度事件（本次开放评论添加事件）
  - `subscription_status` — 查询用户、应用对指定事件的订阅状态

### file.statistics

  - `get` — 获取文件统计信息

### file.view_records

  - `list` — 获取文档的访问者记录

### file.comment.reply.reactions

  - `update_reaction` — 添加/删除 reaction
