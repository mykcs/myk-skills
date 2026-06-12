---
name: lark-sheets
version: 1.2.0
description: "飞书电子表格：创建和操作电子表格。支持创建表格、创建/复制/删除/更新工作表、读写单元格、追加行数据、查找内容、导出文件。当用户需要创建电子表格、管理工作表、批量读写数据、在已知表格中查找内容、导出或下载表格时使用。若用户是想按名称或关键词搜索云空间里的表格文件，请改用 lark-drive 的 drive +search 先定位资源。"
metadata:
  requires:
    bins: ["lark-cli"]
  cliHelp: "lark-cli sheets --help"
---

# sheets (v3)

**CRITICAL — 开始前 MUST 先用 Read 工具读取 [`../lark-shared/SKILL.md`](../lark-shared/SKILL.md)，其中包含认证、权限处理**

## 快速决策
- 已知 spreadsheet URL / token 后，再进入 `sheets +info`、`sheets +read`、`sheets +find` 等对象内部操作。


📂 **核心概念** → see [`references/core-concepts.md`](references/core-concepts.md) (loaded on demand)

## Shortcuts（推荐优先使用）

Shortcut 是对常用操作的高级封装（`lark-cli sheets +<verb> [flags]`）。有 Shortcut 的操作优先使用。

### Spreadsheet Management

对应参考文档：[spreadsheet-management](references/lark-sheets-spreadsheet-management.md)

| Shortcut | 说明 |
|----------|------|
| [`+create`](references/lark-sheets-spreadsheet-management.md#create) | Create a spreadsheet (optional header row and initial data) |
| [`+info`](references/lark-sheets-spreadsheet-management.md#info) | View spreadsheet metadata and sheet information |
| [`+export`](references/lark-sheets-spreadsheet-management.md#export) | Export a spreadsheet (async task polling + optional download) |

### Sheet Management

对应参考文档：[sheet-management](references/lark-sheets-sheet-management.md)

| Shortcut | 说明 |
|----------|------|
| [`+create-sheet`](references/lark-sheets-sheet-management.md#create-sheet) | Create a sheet in an existing spreadsheet |
| [`+copy-sheet`](references/lark-sheets-sheet-management.md#copy-sheet) | Copy a sheet within a spreadsheet |
| [`+delete-sheet`](references/lark-sheets-sheet-management.md#delete-sheet) | Delete a sheet from a spreadsheet |
| [`+update-sheet`](references/lark-sheets-sheet-management.md#update-sheet) | Update sheet title, position, visibility, freeze, or protection |

### Cell Data

对应参考文档：[cell-data](references/lark-sheets-cell-data.md)

| Shortcut | 说明 |
|----------|------|
| [`+read`](references/lark-sheets-cell-data.md#read) | Read spreadsheet cell values |
| [`+write`](references/lark-sheets-cell-data.md#write) | Write to spreadsheet cells (overwrite mode) |
| [`+append`](references/lark-sheets-cell-data.md#append) | Append rows to a spreadsheet |
| [`+find`](references/lark-sheets-cell-data.md#find) | Find cells in a spreadsheet |
| [`+replace`](references/lark-sheets-cell-data.md#replace) | Find and replace cell values |

### Cell Style And Merge

对应参考文档：[cell-style-and-merge](references/lark-sheets-cell-style-and-merge.md)

| Shortcut | 说明 |
|----------|------|
| [`+set-style`](references/lark-sheets-cell-style-and-merge.md#set-style) | Set cell style for a range |
| [`+batch-set-style`](references/lark-sheets-cell-style-and-merge.md#batch-set-style) | Batch set cell styles for multiple ranges |
| [`+merge-cells`](references/lark-sheets-cell-style-and-merge.md#merge-cells) | Merge cells in a spreadsheet |
| [`+unmerge-cells`](references/lark-sheets-cell-style-and-merge.md#unmerge-cells) | Unmerge (split) cells in a spreadsheet |

### Cell Images

对应参考文档：[cell-images](references/lark-sheets-cell-images.md)

| Shortcut | 说明 |
|----------|------|
| [`+write-image`](references/lark-sheets-cell-images.md#write-image) | Write an image into a spreadsheet cell |

### Row Column Management

对应参考文档：[row-column-management](references/lark-sheets-row-column-management.md)

| Shortcut | 说明 |
|----------|------|
| [`+add-dimension`](references/lark-sheets-row-column-management.md#add-dimension) | Add rows or columns at the end of a sheet |
| [`+insert-dimension`](references/lark-sheets-row-column-management.md#insert-dimension) | Insert rows or columns at a specified position |
| [`+update-dimension`](references/lark-sheets-row-column-management.md#update-dimension) | Update row or column properties (visibility, size) |
| [`+move-dimension`](references/lark-sheets-row-column-management.md#move-dimension) | Move rows or columns to a new position |
| [`+delete-dimension`](references/lark-sheets-row-column-management.md#delete-dimension) | Delete rows or columns |

### Filter Views

对应参考文档：[filter-views](references/lark-sheets-filter-views.md)

| Shortcut | 说明 |
|----------|------|
| [`+create-filter-view`](references/lark-sheets-filter-views.md#create-filter-view) | Create a filter view |
| [`+update-filter-view`](references/lark-sheets-filter-views.md#update-filter-view) | Update a filter view |
| [`+list-filter-views`](references/lark-sheets-filter-views.md#list-filter-views) | List all filter views in a sheet |
| [`+get-filter-view`](references/lark-sheets-filter-views.md#get-filter-view) | Get a filter view by ID |
| [`+delete-filter-view`](references/lark-sheets-filter-views.md#delete-filter-view) | Delete a filter view |
| [`+create-filter-view-condition`](references/lark-sheets-filter-views.md#create-filter-view-condition) | Create a filter condition on a filter view |
| [`+update-filter-view-condition`](references/lark-sheets-filter-views.md#update-filter-view-condition) | Update a filter condition |
| [`+list-filter-view-conditions`](references/lark-sheets-filter-views.md#list-filter-view-conditions) | List all filter conditions of a filter view |
| [`+get-filter-view-condition`](references/lark-sheets-filter-views.md#get-filter-view-condition) | Get a filter condition by column |
| [`+delete-filter-view-condition`](references/lark-sheets-filter-views.md#delete-filter-view-condition) | Delete a filter condition |

### Dropdown

对应参考文档：[dropdown](references/lark-sheets-dropdown.md)

| Shortcut | 说明 |
|----------|------|
| [`+set-dropdown`](references/lark-sheets-dropdown.md#set-dropdown) | 设置下拉列表（`multipleValue` 写入的前置步骤） |
| [`+update-dropdown`](references/lark-sheets-dropdown.md#update-dropdown) | 更新下拉列表选项 |
| [`+get-dropdown`](references/lark-sheets-dropdown.md#get-dropdown) | 查询下拉列表配置 |
| [`+delete-dropdown`](references/lark-sheets-dropdown.md#delete-dropdown) | 删除下拉列表 |

### Float Images

对应参考文档：[float-images](references/lark-sheets-float-images.md)

| Shortcut | 说明 |
|----------|------|
| [`+media-upload`](references/lark-sheets-float-images.md#media-upload) | 上传本地图片素材，返回 `file_token`（供 `+create-float-image` 使用；>20MB 自动分片） |
| [`+create-float-image`](references/lark-sheets-float-images.md#create-float-image) | 创建浮动图片 |
| [`+update-float-image`](references/lark-sheets-float-images.md#update-float-image) | 更新浮动图片属性 |
| [`+get-float-image`](references/lark-sheets-float-images.md#get-float-image) | 获取浮动图片 |
| [`+list-float-images`](references/lark-sheets-float-images.md#list-float-images) | 查询所有浮动图片 |
| [`+delete-float-image`](references/lark-sheets-float-images.md#delete-float-image) | 删除浮动图片 |

### Formula

对应参考文档：[formula](references/lark-sheets-formula.md)

> 浮动图片相关的读接口只返回元数据（含 `float_image_token`），**不包含图片字节**。要读取图片内容，用 token 调 `lark-cli docs +media-preview --token "<float_image_token>" --output ./image.png`。


📂 **API Resources** → see [`references/api-resources.md`](references/api-resources.md) (loaded on demand)

## 权限表

| 方法 | 所需 scope |
|------|-----------|
| `spreadsheets.create` | `sheets:spreadsheet:create` |
| `spreadsheets.get` | `sheets:spreadsheet.meta:read` |
| `spreadsheets.patch` | `sheets:spreadsheet.meta:write_only` |
| `spreadsheet.sheet.filters.create` | `sheets:spreadsheet:write_only` |
| `spreadsheet.sheet.filters.delete` | `sheets:spreadsheet:write_only` |
| `spreadsheet.sheet.filters.get` | `sheets:spreadsheet:read` |
| `spreadsheet.sheet.filters.update` | `sheets:spreadsheet:write_only` |
| `spreadsheet.sheets.find` | `sheets:spreadsheet:read` |
| `spreadsheet.sheet.float_images.create` | `sheets:spreadsheet:write_only` |
| `spreadsheet.sheet.float_images.patch` | `sheets:spreadsheet:write_only` |
| `spreadsheet.sheet.float_images.get` | `sheets:spreadsheet:read` |
| `spreadsheet.sheet.float_images.query` | `sheets:spreadsheet:read` |
| `spreadsheet.sheet.float_images.delete` | `sheets:spreadsheet:write_only` |
