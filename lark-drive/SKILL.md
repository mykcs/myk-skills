---
name: lark-drive
version: 1.0.0
description: "飞书云空间：管理云空间中的文件和文件夹。上传和下载文件、创建文件夹、复制/移动/删除文件、查看文件元数据、管理文档评论、管理文档权限、订阅用户评论变更事件、修改文件标题（docx、sheet、bitable、file、folder、wiki）；也负责把本地 Word/Markdown/Excel/CSV 以及 Base 快照（.base）导入为飞书在线云文档（docx、sheet、bitable）。当用户需要上传或下载文件、整理云空间目录、查看文件详情、管理评论、管理文档权限、修改文件标题、订阅用户评论变更事件，或要把本地文件导入成新版文档、电子表格、多维表格/Base 时使用。"
metadata:
  requires:
    bins: ["lark-cli"]
  cliHelp: "lark-cli drive --help"
---

# drive (v1)

**CRITICAL — 开始前 MUST 先用 Read 工具读取 [`../lark-shared/SKILL.md`](../lark-shared/SKILL.md)，其中包含认证、权限处理**

> **导入分流规则：** 如果用户要把本地 Excel / CSV / `.base` 快照导入成 Base / 多维表格 / bitable，必须优先使用 `lark-cli drive +import --type bitable`。不要先切到 `lark-base`；`lark-base` 只负责导入完成后的表内操作。

## 快速决策

- 用户要**搜文档 / Wiki / 电子表格 / 多维表格 / 云空间对象**，优先使用 `lark-cli drive +search`。自然语言里"最近我编辑过的"、"我创建的"（→ `--mine`，实为 owner 语义）、"最近一周我打开过的 xxx"、"某人 owner 的 docx" 等直接映射到扁平 flag，避免手写嵌套 JSON。
- 用户要把本地 `.xlsx` / `.csv` / `.base` 导入成 Base / 多维表格 / bitable，第一步必须使用 `lark-cli drive +import --type bitable`。
- 用户要把本地 `.md` / `.docx` / `.doc` / `.txt` / `.html` 导入成在线文档，使用 `lark-cli drive +import --type docx`。
- 用户要在 Drive 里上传、创建、读取、局部 patch 或覆盖更新**原生 `.md` 文件**（不是导入成 docx），切到 [`lark-markdown`](../lark-markdown/SKILL.md)。
- 用户要比较原生 `.md` 文件的**历史版本差异**，或比较远端 Markdown 与本地草稿，切到 [`lark-markdown`](../lark-markdown/SKILL.md) 的 `lark-cli markdown +diff`；需要版本号时先用 `drive +version-history`。
- 用户要查看、下载、回滚或删除文件的**历史版本**，使用 `drive +version-history`、`drive +version-get`、`drive +version-revert`、`drive +version-delete`；这组命令同时支持 `--as user` 和 `--as bot`，自动化场景优先 `--as bot`。
- 用户要把本地 `.xlsx` / `.xls` / `.csv` 导入成电子表格，使用 `lark-cli drive +import --type sheet`。
- 用户要在云空间里新建文件夹，优先使用 `lark-cli drive +create-folder`。
- 用户要把本地文件上传到知识库 / 文档库里的某个 wiki 节点下时，仍然使用 `lark-cli drive +upload --wiki-token <wiki_token>`；不要误切到 `wiki` 域命令。
- `lark-base` 只负责导入完成后的 Base 内部操作（表、字段、记录、视图），不要在“本地文件 -> Base”这一步提前切到 `lark-base`。

## 修改标题
- 使用 `drive files patch` 命令，通过new_title字段可以修改标题，支持 docx、sheet、bitable、file、wiki、folder 类型


📂 **核心概念** → see [`references/core-concepts.md`](references/core-concepts.md) (loaded on demand)


📂 **Shortcuts（推荐优先使用）** → see [`references/shortcuts.md`](references/shortcuts.md) (loaded on demand)

## 权限表

| 方法                                             | 所需 scope                          |
|------------------------------------------------|-----------------------------------|
| `files.copy`                                   | `docs:document:copy`              |
| `files.create_folder`                          | `space:folder:create`             |
| `files.list`                                   | `space:document:retrieve`         |
| `files.patch`                                  | `docx:document:write_only`        |
| `file.comments.batch_query`                    | `docs:document.comment:read`      |
| `file.comments.create_v2`                      | `docs:document.comment:create`    |
| `file.comments.list`                           | `docs:document.comment:read`      |
| `file.comments.patch`                          | `docs:document.comment:update`    |
| `file.comment.replys.create`                   | `docs:document.comment:create`    |
| `file.comment.replys.delete`                   | `docs:document.comment:delete`    |
| `file.comment.replys.list`                     | `docs:document.comment:read`      |
| `file.comment.replys.update`                   | `docs:document.comment:update`    |
| `permission.members.auth`                      | `docs:permission.member:auth`     |
| `permission.members.create`                    | `docs:permission.member:create`   |
| `permission.members.transfer_owner`            | `docs:permission.member:transfer` |
| `permission.public.get`                        | `docs:permission.setting:read`    |
| `permission.public.patch`                      | `docs:permission.setting:write_only` |
| `metas.batch_query`                            | `drive:drive.metadata:readonly`   |
| `user.remove_subscription`                     | `docs:event:subscribe`            |
| `user.subscription`                            | `docs:event:subscribe`            |
| `user.subscription_status`                     | `docs:event:subscribe`            |
| `file.statistics.get`                          | `drive:drive.metadata:readonly`   |
| `file.view_records.list`                       | `drive:file:view_record:readonly` |
| `file.comment.reply.reactions.update_reaction` | `docs:document.comment:create`    |
