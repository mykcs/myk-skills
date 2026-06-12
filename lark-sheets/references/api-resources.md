## API Resources

```bash
lark-cli schema sheets.<resource>.<method>   # 调用 API 前必须先查看参数结构
lark-cli sheets <resource> <method> [flags] # 调用 API
```

> **重要**：使用原生 API 时，必须先运行 `schema` 查看 `--data` / `--params` 参数结构，不要猜测字段格式。

### spreadsheets

  - `create` — 创建电子表格
  - `get` — 获取电子表格信息
  - `patch` — 修改电子表格属性

### spreadsheet.sheet.filters

  - `create` — 创建筛选
  - `delete` — 删除筛选
  - `get` — 获取筛选
  - `update` — 更新筛选

### spreadsheet.sheets

  - `find` — 查找单元格

### spreadsheet.sheet.float_images

  - `create` — 创建浮动图片
  - `patch` — 更新浮动图片
  - `get` — 获取浮动图片
  - `query` — 查询所有浮动图片
  - `delete` — 删除浮动图片
