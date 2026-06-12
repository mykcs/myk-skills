---
name: lark-base
version: 1.2.1
description: "当需要用 lark-cli 操作飞书多维表格（Base）时调用：搜索 Base、建表、字段管理、记录读写、记录分享链接、视图配置、历史查询，以及角色/表单/仪表盘管理/工作流；也适用于把旧的 +table / +field / +record 写法改成当前命令写法。涉及字段设计、公式字段、查找引用、跨表计算、行级派生指标、数据分析需求时也必须使用本 skill。"
metadata:
  requires:
    bins: ["lark-cli"]
  cliHelp: "lark-cli base --help"
---

# base

> **前置条件：** 先阅读 [`../lark-shared/SKILL.md`](../lark-shared/SKILL.md)。
> **执行前必做：** 执行任何 `base` 命令前，必须先阅读对应命令的 reference 文档，再调用命令。
> **查询类任务必做：** 涉及筛选、排序、Top/Bottom N、聚合、多表关联、查询后写入或判断全局结论时，必须先阅读 [`references/lark-base-data-analysis-sop.md`](references/lark-base-data-analysis-sop.md)，再选择 `record / view / data-query` 路径。
> **命名约定：** Base 业务命令仅使用 `lark-cli base +...` 形式；解析 Wiki 链接使用 `lark-cli wiki +node-get`。
> **分流规则：** 如果用户要“把本地文件导入成 Base / 多维表格 / bitable”，第一步不是 `base`，而是 `lark-cli drive +import --type bitable`；导入完成后再回到 `lark-cli base +...` 做表内操作。

## 1. 何时使用本 Skill

### 1.1 触发条件

以下场景应使用本 skill：

- 用户明确要操作飞书多维表格 / Base。
- 用户要建表、改表、查表、删表，或管理字段、记录、视图。
- 用户要做公式字段、lookup 字段、派生指标、跨表计算。
- 用户要做临时统计、聚合分析、比较排序、求最值。
- 用户要管理 workflow、dashboard、表单、角色权限。
- 用户给出 `/base/{token}` 链接。
- 用户给出 `/wiki/{token}` 链接，且最终解析为 `bitable`。
- 用户要把旧的 Base 聚合式写法改成当前原子命令写法，例如把旧 `+table / +field / +record / +view / +history / +workspace` 改写成当前命令。

以下场景不应使用本 skill：

- 用户只是做认证、初始化配置、切换 `--as user/bot`、处理 scope。此时先读 `../lark-shared/SKILL.md`。
- 用户只是泛化地讨论“数据分析 / 字段设计”，但并不在 Base 场景中。不要因为提到“统计 / 公式 / lookup”就误触发。

### 1.2 前置约束

1. 先阅读 [`../lark-shared/SKILL.md`](../lark-shared/SKILL.md)。
2. Base 业务命令仅使用 `lark-cli base +...` 形式的 shortcut 命令。
3. 如果输入是 Wiki 链接或 Wiki token，并且用户想读取/操作其中的 Base，先执行 `lark-cli wiki +node-get --token <wiki_url_or_token>`；当返回 `data.obj_type=bitable` 时，把 `data.obj_token` 当作 `--base-token`。不要把 URL 里的 `/wiki/{token}` 当成 Base token。
4. 定位到命令后，先读该命令对应的 reference，再执行命令。
5. 如果用户要把本地 Excel / CSV / `.base` 快照导入成 Base / 多维表格 / bitable，第一步不是 `base`，而是 `lark-cli drive +import --type bitable`；导入完成后再回到 `lark-cli base +...` 做表内操作。
6. 不要在 Base 场景改走 `lark-cli api /open-apis/bitable/v1/...`。
7. 如果用户只给 Base 名称、关键词，或说“帮我找一个多维表格”，先通过 `lark-cli drive +search --query <keyword> --doc-types bitable` 搜索 Base / 多维表格资源；拿到 Base URL 后再使用本 skill 的 `base +...` 命令。复杂搜索再读 [`../lark-drive/references/lark-drive-search.md`](../lark-drive/references/lark-drive-search.md)：标题精确匹配、限定 owner（`--mine` / `--creator-ids`，owner 语义非"最初创建人"）/群/文件夹/时间范围、只搜标题/评论、分页/全量搜索。


📂 **2. 模块与命令导航** → see [`references/modules-commands.md`](references/modules-commands.md) (loaded on demand)

## 3. 多维表格通用知识

飞书多维表格英文名是 `Base`，曾用名 `Bitable`；因此旧文档、返回字段、参数名或错误信息里出现 `bitable` 多属历史兼容，不代表应改用另一套命令体系。

### 3.1 字段分类与可写性

| 字段类型 | 含义 | 能否直接作为 `+record-upsert / +record-batch-create / +record-batch-update` 写入目标 | 说明 |
|----------|------|-----------------------------------------------------------|------|
| 存储字段 | 真实存用户输入的数据 | 可以 | 常见如文本、数字、日期、单选、多选、人员、关联 |
| 附件字段 | 存储文件附件 | 不应直接按普通字段写 | 上传附件走 `+record-upload-attachment`；下载附件走 `+record-download-attachment`；删除附件走 `+record-remove-attachment` |
| 地理位置字段 | 存储坐标并由平台解析地址 | 可以 | 写入必须使用 `{lng,lat}`；读取、筛选和转文本等场景使用 `full_address` 字符串；只有公式能访问坐标 |
| 系统字段 | 平台自动维护 | 不可以 | 常见如创建时间、更新时间、创建人、修改人、自动编号 |
| `formula` 字段 | 通过表达式计算 | 不可以 | 只读字段 |
| `lookup` 字段 | 通过跨表规则查找引用 | 不可以 | 只读字段 |

### 3.2 任务选路心智模型

| 用户诉求 | 优先方案 | 不要误走 |
|---------|----------|----------|
| 一次性分析 / 临时统计 | `+data-query` | 不要用 `+record-list` / `+record-search` 拉全量后手算 |
| 要把结果长期显示在表里 | `formula` 字段 | 不要只给一次性手工分析结果 |
| 用户明确要求 lookup，或天然是固定查找配置 | `lookup` 字段 | 不要默认先上 lookup；先判断 formula 是否更合适 |
| 读取原始记录明细 / 关键词检索 / 导出 | `+record-search / +record-list / +record-get` | 不要拿 `+data-query` 当取数命令 |
| 上传附件到记录 | `+record-upload-attachment` | 不要用 `+record-upsert` / `+record-batch-*` 伪造附件值 |
| 下载记录里的附件文件 | `+record-download-attachment --record-id <record_id> --output <dir>`，可加 `--file-token <file_token>` 只下指定附件 | Base 附件必须用这个命令下载；用其他下载入口可能失败 |
| 写入地理位置 | `+record-upsert` / `+record-batch-*` 传 `{lng,lat}` | 不要把纯地址文本当成 CellValue |
| 基于视图做筛选读取 | `+view-set-filter` + `+record-list` | 不要跳过视图筛选直接猜条件 |
| 本地 Excel / CSV / `.base` 导入为 Base | `lark-cli drive +import --type bitable` | 不要误走 `+base-create`、`+table-create` 或 `+record-upsert` |

### 3.3 查询执行契约

涉及查询、统计或判断结论时，先阅读 [`references/lark-base-data-analysis-sop.md`](references/lark-base-data-analysis-sop.md)，并遵守以下高优先级规则：

1. `+record-list` 默认页、固定 `--limit` 和本地 `jq` 只能证明已读取范围内的事实，不能直接支撑全局最值、全量计数、Top/Bottom N、异常识别或分组结论。
2. 能由 Base 表达的筛选、排序、投影、聚合、分组和限制，应在 Base 云端查询服务中执行；不要先拉明细到本地上下文再手工筛选排序。
3. `has_more=true` 或等价分页信号表示当前结果不是全量；除非用户只要样例/前 N 条，不能基于该页回答全局问题。
4. 多表查询必须先确认关系字段和连接键；link 单元格里的 `record_id` 是关系键，不是用户可读答案。
5. 最终答案必须能追溯到真实表、真实字段、查询范围、筛选/排序/聚合条件和必要的连接键。

### 3.4 表名、字段名与表达式引用

1. 表名、字段名必须精确匹配真实返回，来源应是 `+table-list / +table-get / +field-list`。
2. 不要凭自然语言猜名称，不要自行改写用户口述中的表名、字段名。
3. `formula / lookup / data-query / workflow` 中出现的名称同样必须精确匹配；表达式引用、where 条件、DSL 字段名、workflow 配置都遵守同一规则。
4. 跨表场景必须额外读取目标表结构，不能只看当前表。

### 3.5 Token 与链接

这是高优先级章节。只要用户输入里出现链接、token，或报错涉及 `baseToken` / `wiki_token` / `obj_token`，都应优先回到这里检查。

| 输入类型 | 正确处理方式 | 说明 |
|---------|--------------|------|
| 直接 Base 链接 `/base/{token}` | 直接提取 token 作为 `--base-token` | 不要把完整 URL 直接作为 `--base-token` |
| Wiki 链接 `/wiki/{token}` | 先用下方 fast path 解析 `data.obj_token` | 不要把 `wiki_token` 直接当 `--base-token`；如果这一步失败，再看 [`lark-wiki-node-get.md`](../lark-wiki/references/lark-wiki-node-get.md) |
| URL 中的 `?table={id}` | 先按前缀判断对象类型 | `tbl` 开头表示数据表 `table-id`，可作为 `--table-id`；`blk` 开头表示仪表盘 `dashboard-ID`；`wkf` 开头表示 `workflow-ID`；`ldx` 开头表示内嵌文档，不要一律当成 `--table-id` |
| URL 中的 `?view={id}` | 提取为 `--view-id` | 适合直接定位视图 |

Wiki Base fast path:

```bash
BASE_TOKEN="$(lark-cli wiki +node-get --as user --token "<wiki_url_or_token>" --jq '.data | select(.obj_type == "bitable") | .obj_token')"
```

| `lark-cli wiki +node-get` 返回的 `data.obj_type` | 后续路线 | 说明 |
|-----------------------------------------------|----------|------|
| `bitable` | 优先走 `lark-cli base +...` | 如果 shortcut 不覆盖，再用 `lark-cli base <resource> <method>`；不要改走 `lark-cli api /open-apis/bitable/v1/...` |
| `docx` | 转到文档 / Drive 相关 skill | 不继续使用本 skill 的 Base 命令 |
| `sheet` | 转到 Sheets 相关 skill | 不继续使用本 skill 的 Base 命令 |
| `slides` | 转到 Drive 相关 skill | 不继续使用本 skill 的 Base 命令 |
| `mindnote` | 转到 Drive 相关 skill | 不继续使用本 skill 的 Base 命令 |

### 3.6 身份选择与权限降级策略

多维表格通常属于用户的个人或团队资源。**默认应优先使用 `--as user`（用户身份）执行所有 Base 操作**，始终显式指定身份。

- **`--as user`（推荐）**：以当前登录用户身份操作其有权访问的 Base。执行前先完成用户授权：

```bash
lark-cli auth login --domain base
```

- **`--as bot`（降级）**：仅当 user 身份权限不足、且 bot 身份确实拥有目标 Base 的访问权限时，才降级使用。bot 看不到用户私有资源，行为以应用身份执行。

**执行规则**：

1. 所有操作默认先用 `--as user`。
2. 若 user 身份返回权限错误，先判断是否为**不可重试错误码**（如 `91403`）。若是，**立即停止**，不做任何重试或降级，直接按 `lark-shared` 权限不足处理流程引导用户解决。
3. 非不可重试错误码时，检查错误响应中是否包含 `permission_violations` / `hint` 等提权引导信息：
   - **有提权引导**：按 `lark-shared` 权限不足处理流程，先引导用户完成 user 身份提权（`auth login --scope`）；确认提权成功后，以 `--as user` 重试。
   - **无提权引导**（如资源级无访问权限、非 scope 不足）：切换到 `--as bot` 重试**一次**。
4. 若 bot 身份仍然返回权限错误，**立即停止重试**，根据错误响应按 `lark-shared` 流程引导用户解决（引导去开发者后台开通 scope 或确认资源访问权限）。
5. 只有在用户明确要求"用应用身份 / bot 身份操作"，才跳过 user 直接使用 `--as bot`。

## 4. 执行规则

### 4.1 标准执行顺序

1. 先判断任务属于哪个模块，选对命令族。
2. 如果用户给了链接，先解析 token，不要把 wiki token、完整 URL 或其他对象 ID 误当成 `base_token`。
3. 如果是查询类任务，先判断问题范围，阅读 data analysis SOP，再决定使用 `record / view / data-query`。
4. 先拿结构，再写命令，避免猜表名、字段名、表达式引用。
5. 定位到命令后，先读对应 reference，再执行命令。
6. 执行命令，并按返回结果判断下一步。
7. 回复时返回关键结果和后续可继续操作的信息，方便 agent 链式执行下一步。

### 4.2 不可违反规则

1. 先拿结构，再写命令；至少先拿当前表结构，跨表时还要拿目标表结构。
2. 不要猜表名、字段名、表达式引用，一律以真实返回为准。
3. 只使用原子命令；不要回退到旧的聚合式 `+table / +field / +record / +view / +history / +workspace`。
4. 写记录前先读字段结构；先 `+field-list`，再按 [`lark-base-cell-value.md`](references/lark-base-cell-value.md) 构造 CellValue。
5. 写字段前先看字段属性规范；先读 `lark-base-shortcut-field-properties.md`，再构造 `+field-create / +field-update` 的 JSON。
6. 只写可写字段；系统字段、附件字段、`formula`、`lookup` 默认不作为普通记录写入目标。
7. 聚合分析与取数分流；统计走 `+data-query`，关键词检索走 `+record-search`，明细走 `+record-list / +record-get`。
8. 筛选查询按视图能力执行；先用 `+view-set-filter` 配置筛选，再结合 `+record-list` 读取。
9. 全局查询不得基于默认分页、小 `--limit` 或未证明全量的本地 `jq` 结果下结论。
10. Base 场景不要改走裸 API，不要切去 `lark-cli api /open-apis/bitable/v1/...`。
11. 统一使用 `--base-token`。
12. workflow 场景先读 schema，不要凭自然语言猜 `type`。
13. dashboard 场景先读 guide；提到图表、看板、block 就先进入 dashboard 模块。
14. formula / lookup 场景先读 guide；没读 guide 前不要直接创建或更新。

### 4.3 并发、分页与批量限制

- `+table-list / +field-list / +record-list / +view-list / +record-history-list / +role-list / +dashboard-list / +dashboard-block-list / +workflow-list` 禁止并发调用，只能串行执行。
- `+record-list` 分页时，`--limit` 最大 `200`；先拉首批并检查 `has_more`，只有用户明确需要更多数据时再继续翻页。
- 批量写入时，单批不超过 `200` 条。
- 连续写入同一表时，必须串行写入，批次间延迟 `0.5–1` 秒。

### 4.4 确认与回复规则

- 视图重命名时，用户已明确“把哪个视图改成什么名字”时，`+view-rename` 直接执行即可。
- 更新字段或删除记录 / 字段 / 表时，如果用户已经明确目标，`+field-update / +record-delete / +field-delete / +table-delete` 可直接执行，并带 `--yes`。
- 删除目标仍有歧义时，先用 `+record-get / +field-get / +table-get` 或相应 list 命令确认。
- `+base-create / +base-copy` 成功后，回复中必须主动返回新 Base 的标识信息；若结果带可访问链接，也应一并返回。
- 若 Base 由 bot 身份创建或复制，shortcut 会自动尝试为当前 CLI 用户补授 `full_access`，并在输出中返回 `permission_grant`；agent 不需要再手动编排单独授权。owner 转移必须单独确认，禁止擅自执行。

## 5. 常见错误与恢复

| 错误 / 现象 | 含义 | 恢复动作 |
|-------------|------|----------|
| `1254064` | 日期格式错误 | 传 `YYYY-MM-DD HH:mm:ss` 字符串，不要写相对时间 |
| `1254068` | 超链接格式错误 | `"https://example.com"` 或 `"[文本](https://example.com)"` |
| `1254066` | 人员字段错误 | `[{ "id": "ou_xxx" }]` |
| `1254045` | 字段名不存在 | 检查字段名（含空格、大小写） |
| `1254015` | 字段值类型不匹配 | 先 `+field-list`，再按类型构造 |
| `param baseToken is invalid` / `base_token invalid` | 把 wiki token、workspace token 或其他 token 当成了 `base_token` | 如果输入来自 `/wiki/...`，先用 `lark-cli wiki +node-get --token <wiki_url_or_token>` 取真实 `data.obj_token`；当 `data.obj_type=bitable` 时，用 `data.obj_token` 作为 `--base-token` 重试，不要改走 `bitable/v1` |
| `not found` 且用户给的是 wiki 链接 | 常见于把 wiki token 当成 base token | 优先回退检查 wiki 解析，而不是改走 `bitable/v1` |
| formula / lookup 创建失败 | 指南未读或结构不合法 | 先读 `formula-field-guide.md` / `lookup-field-guide.md`，再按 guide 重建请求 |
| `ignored_fields` / `READONLY` | 只读字段被当成可写字段，常见于系统字段、formula、lookup | 移除只读字段，只写存储字段；计算结果交给 formula / lookup / 系统字段自动产出 |
| `1254104` | 批量超 200 条 | 分批调用 |
| `1254291` | 并发写冲突 | 串行写入 + 批次间延迟 |
| `91403` | 无权限访问该 Base | **不要重试**。按 `lark-shared` 权限不足处理流程引导用户解决权限问题 |
