## 2. 模块与命令导航

本章按“先选模块，再选命令”的方式组织。先判断用户目标属于哪个大模块，再进入对应子模块，按要求阅读 reference 后执行命令。

### 2.1 模块地图

| 大模块 | 处理什么问题 | 包含的小模块 / 能力 |
|------|-------------|-------------------|
| Base 模块 | 管理 Base 本体，或从链接进入 Base 场景 | `base-create / base-get / base-copy`，Base / Wiki 链接解析 |
| 表与数据模块 | 管理 Base 内部结构与日常数据操作 | `table / field / record / view` |
| 公式 / Lookup 模块 | 处理派生字段、条件判断、跨表计算、固定查找引用 | `formula / lookup` 字段创建与更新 |
| 数据分析模块 | 做一次性筛选、分组、聚合分析 | `data-query` |
| Workflow 模块 | 管理自动化流程 | `workflow-list / get / create / update / enable / disable` |
| Dashboard 模块 | 管理仪表盘和图表组件 | `dashboard-* / dashboard-block-*` |
| 表单模块 | 管理表单和表单题目 | `form-* / form-questions-*` |
| 权限与角色模块 | 管理高级权限和自定义角色 | `advperm-* / role-*` |

### 2.2 Base 模块

用于管理 Base 本体，或从用户给出的链接进入后续 Base 操作。  
模块索引：[`references/lark-base-workspace.md`](references/lark-base-workspace.md)

| 命令 | 用途 / 何时使用 | 必读 reference | 路由提醒 |
|------|------------------|----------------|----------|
| `lark-cli drive +search --query <keyword> --doc-types bitable` | 按名称、关键词查找 Base / 多维表格 / bitable | 复杂搜索再读 [`../lark-drive/references/lark-drive-search.md`](../lark-drive/references/lark-drive-search.md) | 先定位资源，再回到 `base +...` 操作表内数据 |
| `+base-create` | 创建新的 Base | [`lark-base-base-create.md`](references/lark-base-base-create.md)、[`lark-base-workspace.md`](references/lark-base-workspace.md) | 写入操作；执行前先读 reference；`--folder-token`、`--time-zone` 都是可选项 |
| `+base-get` | 获取 Base 信息 | [`lark-base-base-get.md`](references/lark-base-base-get.md)、[`lark-base-workspace.md`](references/lark-base-workspace.md) | 适合确认 Base 本体信息，不替代表/字段结构读取 |
| `+base-copy` | 复制已有 Base | [`lark-base-base-copy.md`](references/lark-base-base-copy.md)、[`lark-base-workspace.md`](references/lark-base-workspace.md) | 写入操作；执行前先读 reference；复制成功后应主动返回新 Base 标识信息 |

### 2.3 表与数据模块

这是最常用的大模块，包含 `table / field / record / view` 四类子模块。  
补充示例：[`references/examples.md`](references/examples.md)，适合需要串联 table / record / view 完整操作链路时再读。

#### 2.3.1 Table 子模块

子模块索引：[`references/lark-base-table.md`](references/lark-base-table.md)

| 命令 | 用途 / 何时使用 | 必读 reference | 路由提醒 |
|------|------------------|----------------|----------|
| `+table-list / +table-get` | 列出数据表，或获取单个表详情 | [`lark-base-table-list.md`](references/lark-base-table-list.md)、[`lark-base-table-get.md`](references/lark-base-table-get.md) | `+table-list` 只能串行执行；`+table-get` 适合删除/修改前确认目标 |
| `+table-create / +table-update / +table-delete` | 创建、更新或删除数据表 | [`lark-base-table-create.md`](references/lark-base-table-create.md)、[`lark-base-table-update.md`](references/lark-base-table-update.md)、[`lark-base-table-delete.md`](references/lark-base-table-delete.md) | 创建适合一次性建表；更新前先确认目标表；删除时用户已明确目标可直接执行并带 `--yes` |

#### 2.3.2 Field 子模块

普通字段管理走这里；如果字段类型是 `formula` 或 `lookup`，转到下方“公式 / Lookup 模块”。  
子模块索引：[`references/lark-base-field.md`](references/lark-base-field.md)

| 命令 | 用途 / 何时使用 | 必读 reference | 路由提醒 |
|------|------------------|----------------|----------|
| `+field-list / +field-get` | 列出字段结构，或获取单个字段详情 | [`lark-base-field-list.md`](references/lark-base-field-list.md)、[`lark-base-field-get.md`](references/lark-base-field-get.md) | 写记录、写字段、做分析前常先读 `+field-list`；`+field-list` 只能串行执行；`+field-get` 适合删除/更新前确认目标 |
| `+field-create / +field-update / +field-delete` | 创建、更新或删除普通字段 | [`lark-base-field-create.md`](references/lark-base-field-create.md)、[`lark-base-field-update.md`](references/lark-base-field-update.md)、[`lark-base-field-delete.md`](references/lark-base-field-delete.md)、[`lark-base-shortcut-field-properties.md`](references/lark-base-shortcut-field-properties.md) | 写字段前先看字段属性规范；如果涉及类型转换，直接按 `+field-update` 中的字段类型变更规则执行，只在安全白名单内考虑原地转换；如果类型是 `formula / lookup`，先转去读对应 guide；更新或删除时用户已明确目标可直接执行并带 `--yes` |
| `+field-search-options` | 查询字段可选项 | [`lark-base-field-search-options.md`](references/lark-base-field-search-options.md) | 适合单选/多选等选项型字段 |

#### 2.3.3 Record 子模块

子模块索引：[`references/lark-base-record.md`](references/lark-base-record.md)、[`references/lark-base-history.md`](references/lark-base-history.md)

| 命令 | 用途 / 何时使用 | 必读 reference | 路由提醒 |
|------|------------------|----------------|----------|
| `+record-search / +record-list / +record-get` | 按关键词检索记录、读取记录明细 / 分页导出，或按 ID 获取一条或多条记录 | [`lark-base-data-analysis-sop.md`](references/lark-base-data-analysis-sop.md) | 记录读取统一先读 data analysis SOP：已知 `record_id` 用 `+record-get`；明确关键词用 `+record-search`；普通明细用 `+record-list`；明确筛选 / 排序 / Top N 用临时视图投影后 `+record-list --view-id`；统计聚合才分流到 `+data-query`；`+record-get` 支持重复 `--record-id` 或 `--json` 读取多条记录 |
| `+record-upsert / +record-batch-create / +record-batch-update` | 创建、更新或批量写入记录 | [`lark-base-record-upsert.md`](references/lark-base-record-upsert.md)、[`lark-base-record-batch-create.md`](references/lark-base-record-batch-create.md)、[`lark-base-record-batch-update.md`](references/lark-base-record-batch-update.md)、[`lark-base-cell-value.md`](references/lark-base-cell-value.md) | 写前先 `+field-list`；只写存储字段；`+record-batch-update` 为同值更新（同一 patch 应用到多条记录）；批量单次不超过 `200` 条；附件不要走这里 |
| `+record-upload-attachment` | 给已有记录上传一个或多个附件 | 看 `lark-cli base +record-upload-attachment --help` | 附件上传专用链路，不要用 `+record-upsert` / `+record-batch-*` 伪造附件值；不支持 `--name` |
| `+record-download-attachment` | 下载一个或多个 Base 附件到本地 | 看 `lark-cli base +record-download-attachment --help` | Base 附件必须用这个命令下载；用其他下载入口可能失败 |
| `+record-remove-attachment` | 删除附件字段里的一个或多个附件 | 看 `lark-cli base +record-remove-attachment --help` | 删除操作；确认目标后带 `--yes` |
| `+record-delete` | 删除一条或多条记录 | [`lark-base-record-delete.md`](references/lark-base-record-delete.md) | 删除多条时重复传 `--record-id` 指定多个记录；用户已明确目标可直接执行并带 `--yes` |
| `+record-history-list` | 查询指定记录的变更历史 | [`lark-base-record-history-list.md`](references/lark-base-record-history-list.md) | 按 `table-id + record-id` 查询，不支持整表扫描；`+record-history-list` 只能串行执行 |
| `+record-share-link-create` | 为一条或多条记录生成分享链接 | [`lark-base-record-share-link-create.md`](references/lark-base-record-share-link-create.md) | 单次最多 100 条；重复 record_id 会自动去重；适合分享单条记录或批量分享场景 |

#### 2.3.4 View 子模块

子模块索引：[`references/lark-base-view.md`](references/lark-base-view.md)

| 命令 | 用途 / 何时使用 | 必读 reference | 路由提醒 |
|------|------------------|----------------|----------|
| `+view-list / +view-get` | 列出视图，或获取视图详情 | [`lark-base-view-list.md`](references/lark-base-view-list.md)、[`lark-base-view-get.md`](references/lark-base-view-get.md) | `+view-list` 只能串行执行；`+view-get` 适合查看已有视图配置 |
| `+view-create / +view-delete / +view-rename` | 创建、删除或重命名视图 | [`lark-base-view-create.md`](references/lark-base-view-create.md)、[`lark-base-view-delete.md`](references/lark-base-view-delete.md)、[`lark-base-view-rename.md`](references/lark-base-view-rename.md) | 创建前先确认表和视图类型；删除前先确认目标；用户已明确新名字时可直接重命名 |
| `+view-get-filter / +view-set-filter` | 读取或配置筛选条件 | [`lark-base-view-get-filter.md`](references/lark-base-view-get-filter.md)、[`lark-base-view-set-filter.md`](references/lark-base-view-set-filter.md)、[`lark-base-data-analysis-sop.md`](references/lark-base-data-analysis-sop.md) | 常与 `+record-list` 组合，用于按视图筛选读取 |
| `+view-get-sort / +view-set-sort` | 读取或配置排序 | [`lark-base-view-get-sort.md`](references/lark-base-view-get-sort.md)、[`lark-base-view-set-sort.md`](references/lark-base-view-set-sort.md) | 字段名必须来自真实结构 |
| `+view-get-group / +view-set-group` | 读取或配置分组 | [`lark-base-view-get-group.md`](references/lark-base-view-get-group.md)、[`lark-base-view-set-group.md`](references/lark-base-view-set-group.md) | 字段名必须来自真实结构 |
| `+view-get-visible-fields / +view-set-visible-fields` | 读取或配置视图可见字段 | [`lark-base-view-get-visible-fields.md`](references/lark-base-view-get-visible-fields.md)、[`lark-base-view-set-visible-fields.md`](references/lark-base-view-set-visible-fields.md) | 用于控制视图中的字段顺序与可见性；字段名必须来自真实结构 |
| `+view-get-card / +view-set-card` | 读取或配置卡片视图 | [`lark-base-view-get-card.md`](references/lark-base-view-get-card.md)、[`lark-base-view-set-card.md`](references/lark-base-view-set-card.md) | 适合卡片展示场景 |
| `+view-get-timebar / +view-set-timebar` | 读取或配置时间轴视图 | [`lark-base-view-get-timebar.md`](references/lark-base-view-get-timebar.md)、[`lark-base-view-set-timebar.md`](references/lark-base-view-set-timebar.md) | 适合时间线展示场景 |

### 2.4 公式 / Lookup 模块

只要用户诉求涉及派生指标、条件判断、文本处理、日期差、跨表计算、跨表筛选后取值，都要先判断是否进入本模块。

默认优先考虑 `formula`：适合常规计算、条件判断、文本处理、日期差、跨表聚合，以及需要长期显示在表里的派生结果。  
只有当用户明确要求 `lookup`，或场景天然符合 `from / select / where / aggregate` 这种固定查找建模时，再使用 `lookup`。

| 命令 | 用途 / 何时使用 | 必读 reference | 路由提醒 |
|------|------------------|----------------|----------|
| `+field-create`（`type=formula`） | 创建公式字段 | [`formula-field-guide.md`](references/formula-field-guide.md)、[`lark-base-field-create.md`](references/lark-base-field-create.md)、[`lark-base-shortcut-field-properties.md`](references/lark-base-shortcut-field-properties.md) | 没读 guide 前不要直接创建 |
| `+field-update`（`type=formula`） | 更新公式字段 | [`formula-field-guide.md`](references/formula-field-guide.md)、[`lark-base-field-update.md`](references/lark-base-field-update.md)、[`lark-base-shortcut-field-properties.md`](references/lark-base-shortcut-field-properties.md) | 先拿当前表结构 |
| `+field-create`（`type=lookup`） | 创建 lookup 字段 | [`lookup-field-guide.md`](references/lookup-field-guide.md)、[`lark-base-field-create.md`](references/lark-base-field-create.md)、[`lark-base-shortcut-field-properties.md`](references/lark-base-shortcut-field-properties.md) | 没读 guide 前不要直接创建 |
| `+field-update`（`type=lookup`） | 更新 lookup 字段 | [`lookup-field-guide.md`](references/lookup-field-guide.md)、[`lark-base-field-update.md`](references/lark-base-field-update.md)、[`lark-base-shortcut-field-properties.md`](references/lark-base-shortcut-field-properties.md) | 跨表时还要拿目标表结构 |

### 2.5 数据分析模块

用于一次性分析和临时聚合查询。用户要的是“这次算出来的结果”，而不是把结果沉淀成字段时，优先进入本模块。

进入本模块前先确认几件事：

- `+data-query` 只做聚合查询（分组、过滤、排序、聚合计算），不用于列出原始记录或逐条明细。
- 调用者必须是目标多维表格的管理员，拥有目标多维表格的 FA（Full Access / 完全访问权限），否则会返回权限错误。
- `+data-query` 只支持白名单字段类型；`formula`、`lookup`、附件、系统字段、关联等字段不能用于 `dimensions / measures / filters / sort`。

| 命令 | 用途 / 何时使用 | 必读 reference | 路由提醒 |
|------|------------------|----------------|----------|
| `+data-query` | 做分组统计、SUM / AVG / COUNT / MAX / MIN、条件筛选后的聚合分析 | [`lark-base-data-query.md`](references/lark-base-data-query.md) | 字段名必须精确匹配真实字段名；不要用 `+record-list` / `+record-search` 拉全量再手算；`+data-query` 不返回原始记录；使用前先确认权限和字段类型是否受支持 |

### 2.6 Workflow 模块

这是高约束模块。执行任何 workflow 命令前，都必须先读对应命令文档和 schema。  
模块索引：[`references/lark-base-workflow.md`](references/lark-base-workflow.md)

| 命令 | 用途 / 何时使用 | 必读 reference | 路由提醒 |
|------|------------------|----------------|----------|
| `+workflow-list / +workflow-get` | 列出 workflow，或获取完整 workflow 结构 | [`lark-base-workflow-list.md`](references/lark-base-workflow-list.md)、[`lark-base-workflow-get.md`](references/lark-base-workflow-get.md)、[`lark-base-workflow-schema.md`](references/lark-base-workflow-schema.md) | `+workflow-list` 只返回摘要且只能串行执行；需要完整结构时用 `+workflow-get` |
| `+workflow-create / +workflow-update` | 创建或更新 workflow | [`lark-base-workflow-create.md`](references/lark-base-workflow-create.md)、[`lark-base-workflow-update.md`](references/lark-base-workflow-update.md)、[`lark-base-workflow-schema.md`](references/lark-base-workflow-schema.md) | 先读 schema；禁止凭自然语言猜 `type`；先确认真实表名和字段名 |
| `+workflow-enable / +workflow-disable` | 启用或停用 workflow | [`lark-base-workflow-enable.md`](references/lark-base-workflow-enable.md)、[`lark-base-workflow-disable.md`](references/lark-base-workflow-disable.md)、[`lark-base-workflow-schema.md`](references/lark-base-workflow-schema.md) | 启用或停用前先确认目标 workflow；`workflow_id` 与 `table_id` 需按前缀区分 |

### 2.7 Dashboard 模块

当用户提到“仪表盘、dashboard、数据看板、图表、可视化、block、组件、添加组件、创建图表”等关键词时，进入本模块，并先阅读 [`lark-base-dashboard.md`](references/lark-base-dashboard.md)。

| 命令 | 用途 / 何时使用 | 必读 reference | 路由提醒 |
|------|------------------|----------------|----------|
| `+dashboard-list / +dashboard-get` | 列出仪表盘，或获取仪表盘详情 | [`lark-base-dashboard-list.md`](references/lark-base-dashboard-list.md)、[`lark-base-dashboard-get.md`](references/lark-base-dashboard-get.md)、[`lark-base-dashboard.md`](references/lark-base-dashboard.md) | 进入仪表盘语义后先读 guide；`+dashboard-list` 只能串行执行 |
| `+dashboard-create / +dashboard-update / +dashboard-delete` | 创建、更新或删除仪表盘 | [`lark-base-dashboard-create.md`](references/lark-base-dashboard-create.md)、[`lark-base-dashboard-update.md`](references/lark-base-dashboard-update.md)、[`lark-base-dashboard-delete.md`](references/lark-base-dashboard-delete.md)、[`lark-base-dashboard.md`](references/lark-base-dashboard.md) | 创建前先明确看板目标和展示场景；更新前先读取当前配置；删除前先确认目标 |
| `+dashboard-block-list / +dashboard-block-get` | 列出图表组件，或获取单个 block 详情 | [`lark-base-dashboard-block-list.md`](references/lark-base-dashboard-block-list.md)、[`lark-base-dashboard-block-get.md`](references/lark-base-dashboard-block-get.md)、[`lark-base-dashboard.md`](references/lark-base-dashboard.md)、[`dashboard-block-data-config.md`](references/dashboard-block-data-config.md) | `+dashboard-block-list` 只能串行执行；查看配置细节时读 block config 文档 |
| `+dashboard-block-create / +dashboard-block-update / +dashboard-block-delete` | 创建、更新或删除图表组件 | [`lark-base-dashboard-block-create.md`](references/lark-base-dashboard-block-create.md)、[`lark-base-dashboard-block-update.md`](references/lark-base-dashboard-block-update.md)、[`lark-base-dashboard-block-delete.md`](references/lark-base-dashboard-block-delete.md)、[`lark-base-dashboard.md`](references/lark-base-dashboard.md)、[`dashboard-block-data-config.md`](references/dashboard-block-data-config.md) | 涉及 `data_config`、图表类型、filter 时要读 block config 文档；删除前先确认目标 |

### 2.8 表单模块

用于管理表单本体和表单题目。  
模块索引：[`references/lark-base-form.md`](references/lark-base-form.md)、[`references/lark-base-form-questions.md`](references/lark-base-form-questions.md)  
表单问题相关操作依赖 `form-id`；具体获取方式见 `form-list` 和 `form-create` 的 reference。

| 命令 | 用途 / 何时使用 | 必读 reference | 路由提醒 |
|------|------------------|----------------|----------|
| `+form-list / +form-get` | 列出表单，或获取单个表单 | [`lark-base-form-list.md`](references/lark-base-form-list.md)、[`lark-base-form-get.md`](references/lark-base-form-get.md) | `+form-list` 可用来获取 `form-id`；`+form-get` 适合查看已有表单配置 |
| `+form-detail` | 通过表单分享链接获取表单详情（含题目列表、字段类型、校验规则） | [`lark-base-form-detail.md`](references/lark-base-form-detail.md) | 只读；仅需 `--share-token`（从分享链接提取），不需要 base-token/table-id/form-id；返回的 `questions` 可直接用于 `+form-submit` 构造参数 |
| `+form-submit` | 通过表单分享链接填写并提交表单（支持普通字段 + 附件上传） | [`lark-base-form-submit.md`](references/lark-base-form-submit.md) | 写入操作；仅支持 share_token 模式；**当 `--json` 包含 attachments 时必须额外提供 `--base-token`**（附件上传到 Base Drive Media 需要）；附件通过 `--json.attachments` 传入本地路径，CLI 自动并行上传 |
| `+form-create / +form-update / +form-delete` | 创建、更新或删除表单 | [`lark-base-form-create.md`](references/lark-base-form-create.md)、[`lark-base-form-update.md`](references/lark-base-form-update.md)、[`lark-base-form-delete.md`](references/lark-base-form-delete.md) | 创建后可继续进入表单问题相关操作；更新或删除前先确认目标表单 |
| `+form-questions-list` | 列出表单题目 | [`lark-base-form-questions-list.md`](references/lark-base-form-questions-list.md) | 适合查看已有题目结构 |
| `+form-questions-create / +form-questions-update / +form-questions-delete` | 创建、更新或删除题目 | [`lark-base-form-questions-create.md`](references/lark-base-form-questions-create.md)、[`lark-base-form-questions-update.md`](references/lark-base-form-questions-update.md)、[`lark-base-form-questions-delete.md`](references/lark-base-form-questions-delete.md) | 先确认 `form-id`；更新或删除前先确认题目目标 |

### 2.9 权限与角色模块

用于启用高级权限，以及管理 Base 自定义角色。  
涉及 `+advperm-enable / +advperm-disable / +role-*` 时，操作用户必须为 Base 管理员，否则会返回权限错误。

| 命令 | 用途 / 何时使用 | 必读 reference | 路由提醒 |
|------|------------------|----------------|----------|
| `+advperm-enable / +advperm-disable` | 启用或停用高级权限 | [`lark-base-advperm-enable.md`](references/lark-base-advperm-enable.md)、[`lark-base-advperm-disable.md`](references/lark-base-advperm-disable.md) | 管理角色前必须先启用；停用是高风险操作，会使已有自定义角色失效 |
| `+role-list / +role-get` | 列出角色，或获取角色详情 | [`lark-base-role-list.md`](references/lark-base-role-list.md)、[`lark-base-role-get.md`](references/lark-base-role-get.md)、[`role-config.md`](references/role-config.md) | `+role-list` 只能串行执行；`+role-get` 适合查看完整权限配置 |
| `+role-create / +role-update / +role-delete` | 创建、更新或删除角色 | [`lark-base-role-create.md`](references/lark-base-role-create.md)、[`lark-base-role-update.md`](references/lark-base-role-update.md)、[`lark-base-role-delete.md`](references/lark-base-role-delete.md)、[`role-config.md`](references/role-config.md) | `+role-create` 仅支持 `custom_role`；`+role-update` 采用 Delta Merge，`role_name` 和 `role_type` 即使不改也必须传当前值；`+role-delete` 不可逆 |
