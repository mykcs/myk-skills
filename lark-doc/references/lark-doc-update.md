
# docs +update（更新飞书云文档）

> **前置条件（MUST READ）：** 生成文档内容前，必须先用 Read 工具读取以下文件，缺一不可：
> 1. [`../lark-shared/SKILL.md`](../../lark-shared/SKILL.md) — 认证、全局参数和安全规则
> 2. [`lark-doc-xml.md`](lark-doc-xml.md) — XML 语法规则（使用 Markdown 格式时改读 [`lark-doc-md.md`](lark-doc-md.md)）
> 3. [`lark-doc-style.md`](style/lark-doc-style.md) — 排版指南（元素选择、丰富度规则、颜色语义）
> 4. [`lark-doc-update-workflow.md`](style/lark-doc-update-workflow.md) — 改写增强工作流（Code-Act Loop、并行执行策略）
>
> **未读完以上文件就生成内容会导致格式错误或样式不达标。**

通过八种指令精确更新飞书云文档。支持字符串级别和 block 级别的操作。

> **⚠️ 格式选择规则：**
> - **局部精修**（`str_replace` / `block_insert_after` / `block_replace` / `block_delete` / `block_move_after`）：优先使用 XML（默认）。XML 能稳定表达 block 结构和样式，精准编辑更可控；不要因为 Markdown 写起来更简单就自行切换。
> - **整段写入**（`append` / `overwrite`）：XML 和 Markdown 都可以。用户提供 `.md` 本地文件或明确要求 Markdown 时直接用 Markdown；否则默认 XML。
>
> **Markdown 局限 & block ID 前提：** Markdown 不携带 block ID，也无样式（颜色、对齐、callout 等）。需要按 block ID 定位（`block_*` 指令的 `--block-id`）时，先 `docs +fetch --api-version v2 --detail with-ids` **配合 `--scope`（`outline` / `range` / `keyword` / `section`）局部获取**目标段落，不要全量 fetch。拿到 block ID 后 `--content` 仍可用 Markdown，只是写入内容不带样式。

## 参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `--api-version` | 是 | 固定传 `v2` |
| `--doc` | 是 | 文档 URL 或 token |
| `--command` | 是 | 操作指令（见下方指令速查表） |
| `--doc-format` | 否 | 内容格式：`xml`（默认，始终优先使用）\| `markdown`（仅用户明确要求时） |
| `--content` | 视指令 | 写入内容（`str_replace` 传空字符串可实现删除） |
| `--pattern` | 视指令 | 匹配文本（str_replace） |
| `--block-id` | 视指令 | 目标 block ID（block_* 操作）,-1 表示末尾 |
| `--src-block-ids` | 视指令 | 源 block ID（逗号分隔），用于 block_copy_insert_after / block_move_after |
| `--revision-id` | 否 | 基准版本号，-1 = 最新（默认 `-1`） |

## 指令速查表

| 指令 | 说明 | 必需参数 |
|------|------|----------|
| `str_replace` | 全文文本查找替换（replacement 支持富文本标签；`--content` 传空字符串即为删除） | `--pattern` `--content` |
| `block_insert_after` | 在指定 block 之后插入新内容 | `--block-id` `--content` |
| `block_copy_insert_after` | 复制源 block 并插入到锚点之后（源块不变） | `--block-id` `--src-block-ids` |
| `block_replace` | 替换指定 block（同一 block 仅限一次） | `--block-id` `--content` |
| `block_delete` | 删除指定 block（逗号分隔可批量） | `--block-id` |
| `overwrite` | ⚠️ 清空文档后全文重写（可能丢失图片、评论） | `--content` |
| `append` | 在文档末尾追加内容（等价于 `block_insert_after --block-id -1`） | `--content` |
| `block_move_after` | 移动已有 block 到指定位置 | `--block-id` + (`--content` 或 `--src-block-ids`) |

## 指令示例

### str_replace — 全文文本替换

> **匹配范围：**
> - **XML 模式（默认）**：`--pattern` 只支持**行内匹配**，不能跨 block / 跨段落匹配。涉及整段或多 block 的改动，请改用 `block_replace`。
> - **Markdown 模式**（`--doc-format markdown`）：`--pattern` 同时支持**行内和跨行匹配**，可以用多行字符串匹配并替换一整段内容。
>   - 还支持**`前缀...后缀` 省略号语法**：用 `...`（三个英文句点）串联起始与结束片段，匹配从前缀到后缀之间的全部内容（含中间被省略部分）。适合一段很长、但首尾特征明显的文本，避免把整段都塞进 `--pattern`。
>   - 前缀、后缀本身仍遵循 Markdown 转义规则；省略号中间的内容**会被替换**为 `--content` 的完整文本，不会被保留。

```bash
# 简单文本替换
lark-cli docs +update --api-version v2 --doc "<doc_id>" --command str_replace \
  --pattern "张三" --content "李四"

# 替换为富文本（加粗 + 链接）
lark-cli docs +update --api-version v2 --doc "<doc_id>" --command str_replace \
  --pattern "旧链接" --content '<b>新链接</b> <a href="https://example.com">点击查看</a>'

# 仅当用户明确要求时才使用 Markdown
lark-cli docs +update --api-version v2 --doc "<doc_id>" --command str_replace \
  --doc-format markdown --pattern "旧内容" --content "新内容"

# Markdown 模式下支持跨行匹配（--pattern 与 --content 都需要真实换行；"..."/'...' 里的 \n 是字面量）
# 多行内容推荐 heredoc 或 --content @file.md，避免 shell 转义踩坑
lark-cli docs +update --api-version v2 --doc "<doc_id>" --command str_replace \
  --doc-format markdown \
  --pattern "$(printf '## 旧标题\n\n第一段原文\n\n第二段原文')" \
  --content - <<'EOF'
## 新标题

改写后的第一段

改写后的第二段
EOF

# Markdown 模式下使用 `前缀...后缀` 省略号匹配首尾特征明显的大段内容
# 下例会把「## 旧标题」到「结束语。」之间的所有内容整体替换
lark-cli docs +update --api-version v2 --doc "<doc_id>" --command str_replace \
  --doc-format markdown \
  --pattern "## 旧标题...结束语。" \
  --content - <<'EOF'
## 新标题

重写后的正文...

新的结束语。
EOF

# 删除文本：--content 传空字符串即可
lark-cli docs +update --api-version v2 --doc "<doc_id>" --command str_replace \
  --pattern "废弃的内容" --content ""
```

### block_insert_after — 在指定 block 之后插入

```bash
lark-cli docs +update --api-version v2 --doc "<doc_id>" --command block_insert_after \
  --block-id "目标 block_id" \
  --content '<h2>新章节</h2><ul><li>要点 1</li><li>要点 2</li></ul>'
```

### block_replace — 替换指定 block

```bash
lark-cli docs +update --api-version v2 --doc "<doc_id>" --command block_replace \
  --block-id "目标 block_id" \
  --content '<p>替换后的段落内容</p>'
```

### block_delete — 删除指定 block

```bash
lark-cli docs +update --api-version v2 --doc "<doc_id>" --command block_delete \
  --block-id "目标 block_id"
```

### overwrite — 全文覆盖

```bash
lark-cli docs +update --api-version v2 --doc "<doc_id>" --command overwrite \
  --content '<title>全新文档</title><h1>概述</h1><p>新的内容</p>'
```

> ⚠️ 会清空文档后重写，可能丢失图片、评论等。仅在需要完全重建文档时使用。

### append — 在文档末尾追加

```bash
lark-cli docs +update --api-version v2 --doc "<doc_id>" --command append \
  --content '<h2>新增章节</h2><p>追加的内容</p>'
```

> 等价于 `block_insert_after --block-id -1`，无需先获取 block ID。

### block_copy_insert_after — 复制块并插入

将一个或多个源块复制到锚点块之后，源块保持不变。`--src-block-ids` 为逗号分隔的源块 ID，按顺序依次插入到锚点之后。

```bash
# 复制多个块（按顺序插入：anchor → a → b → c）
lark-cli docs +update --api-version v2 --doc "<doc_id>" --command block_copy_insert_after \
  --block-id "锚点 block_id" \
  --src-block-ids "block_a,block_b,block_c"
```

### block_move_after — 移动已有 block

将文档中已有的 block 移动到指定锚点之后。使用 `--src-block-ids` 指定要移动的块 ID，无需 `--content`。

```bash
# 移动到页面末尾
lark-cli docs +update --api-version v2 --doc "<doc_id>" --command block_move_after \
  --block-id "-1表示末尾，page_id表示开头，blk" \
  --src-block-ids "block_a,block_b"
```

## 返回值

```json
{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "revision_id": 13,
      "new_blocks": [
        { "block_id": "blkcnXXXX", "block_type": "whiteboard", "block_token": "boardXXXX" }
      ]
    },
    "result": "success",
    "updated_blocks_count": 3,
    "warnings": []
  }
}
```

| 字段 | 说明 |
|------|------|
| `result` | `success` \| `partial_success` \| `failed` |
| `updated_blocks_count` | 实际更新的 block 数量 |
| `warnings` | 警告信息列表 |
| `document.new_blocks` | 本次操作新增的 block 列表（如画板）。`block_id` 可用于后续精确编辑；`block_token` 是资源块 token（如画板）可交给 `lark-whiteboard` 等 skill 继续操作 |

## 典型工作流

### 精确 block 级更新

1. **获取文档内容和 block ID**：
   ```bash
   lark-cli docs +fetch --api-version v2 --doc "<doc_id>" --detail with-ids
   ```

2. **定位目标 block**：从返回的 XML 中找到要修改的 block 及其 `id` 属性

3. **执行更新**：
   ```bash
   # 替换特定 block
   lark-cli docs +update --api-version v2 --doc "<doc_id>" --command block_replace \
     --block-id "blkcnXXXX" --content "<p>新内容</p>"

   # 在某 block 后插入
   lark-cli docs +update --api-version v2 --doc "<doc_id>" --command block_insert_after \
     --block-id "blkcnXXXX" --content "<h2>追加的章节</h2>"
   ```

### 简单文本替换

不需要 block ID，直接匹配替换：

```bash
lark-cli docs +update --api-version v2 --doc "<doc_id>" --command str_replace \
  --pattern "v1.0" --content "v2.0"
```

## 画板处理

> **`docs +update` 不能直接编辑已有画板的内容。** 本命令只能**新增**画板块；要修改已有画板，先用 `docs +fetch --api-version v2` 取到 `<whiteboard token="...">`，再按 [`lark-doc-whiteboard.md`](lark-doc-whiteboard.md) 启动 SubAgent 读取 [`lark-whiteboard`](../../lark-whiteboard/SKILL.md) 并写入。

画板的语法选型与插入示例见 [`lark-doc-style.md`](style/lark-doc-style.md) 的「画板语法与插入」章节。

## 最佳实践

- **精确操作优于全文覆盖**：使用 `block_replace`/`block_insert_after` 精确修改，避免 `overwrite` 全文覆盖
- **str_replace 的匹配范围取决于格式**：
  - **XML 模式（默认）**：`--pattern` 只支持**行内**匹配，不支持跨行 / 跨 block。段落、整块或容器级（列表、表格、分栏、引用块等）改动请改用 `block_replace` 指定 block_id 重建。
  - **Markdown 模式**（`--doc-format markdown`）：`--pattern` 同时支持**行内和跨行**匹配，还支持 `前缀...后缀` 省略号语法（用 `...` 串联首尾片段匹配一大段内容），可以一次替换多行文本；但仍建议优先按最小片段匹配，跨 block 容器级重写仍优先用 `block_replace`，避免副作用。
- **保护不可重建的内容**：图片、画板、电子表格等以 token 形式存储，替换时避开这些 block
- **str_replace 的 replacement 支持富文本**：可以用行内标签 `<b>`、`<a>`、`<cite>`、`<latex>` 等替换普通文本为富文本
- **同一 block 只能被 replace 一次**：多次修改同一 block 请合并为一次 block_replace
- **block_delete 支持批量**：用逗号分隔多个 block_id 一次删除
- **复杂结构重组**：将多个段落转换为 grid / table 等复杂布局时，分步操作比 overwrite 更安全：
  1. 用 `block_insert_after` 在目标位置插入新的富文本结构
  2. 用 `block_delete` 批量删除旧的 block
  3. 这样可以保留文档中其他不相关的内容（图片、评论等）
- **视觉丰富度**：插入或替换内容时，同样遵循 [`lark-doc-style.md`](style/lark-doc-style.md) 中的样式指南，主动使用结构化 block

## 踩坑与陷阱（实战经验，2026-06 验证）

> 这些是反复踩过的坑，写新流程前请先扫一遍。

### 1. `--content @<filepath>` 必须用相对路径

```
# ❌ 报错：invalid file path "..." --file must be a relative path
lark-cli docs +update --content @/Users/myk/.../foo.md

# ✅ 先 cd 到目标目录，用相对路径
cd /Users/myk/.mavis/sessions/<sid>/workspace
lark-cli docs +update --content @./foo.md
```

**原因**：`--content @file` 形式启用了 sandbox-style path resolution，绝对路径会被拒绝。

### 2. `block_replace` 同一 block 只能调用一次（静默失败）

```bash
# 第一次：ok ✓
lark-cli docs +update ... --command block_replace --block-id "X" --content "A"

# 第二次：仍返回 "ok": true 但 "result": "failed" —— 看起来成功实际没动
lark-cli docs +update ... --command block_replace --block-id "X" --content "B"
```

**应对**：每次修改前重新 `docs +fetch` 拿最新 block_id，不要靠记忆中的旧 id。第二次修改用新 block_id（同一逻辑位置重建出来的 cell 会有新 id）。

### 3. `str_replace` 在 markdown 模式不能写 XML/HTML 标签

```bash
# ❌ 标签被转义成字面量
--pattern "Genomic...</p></td><td></td>"
--content "Genomic...</p></td><td><p>2022.10</p></td>"
# 实际写入：<p>2022.10</p> 变成 &lt;p&gt;2022.10&lt;/p&gt; 文本
```

**应对**：
- 想插纯文本 → 直接用文本
- 想插段落 → 改用 `block_insert_after` 走 XML 模式
- 改表格 cell → 用 `前缀...后缀` 省略号语法绕开空 cell 匹配问题

### 4. markdown 模式支持 `前缀...后缀` 省略号语法

```bash
# 跨多 cell 匹配并整体替换
lark-cli docs +update --command str_replace --doc-format markdown \
  --pattern '论文标题...会议/期刊' \
  --content '论文标题</p></td><td><p>2024</p></td><td><p>会议/期刊'
```

省略号 `...` 中间内容**完全替换**为 `--content`，不会被保留。适合处理表格内连续多 cell。

### 5. 飞书 H1 vs H2 vs title 的关系

- Markdown 的 `# 一级标题` **会变成文档唯一 `<title>`**（不进入 body），不会出现在 `outline` 里
- body 实际从 H2 开始
- 飞书对 H2 里的 `1.` `2.` `3.` 等数字格式会**自动识别**为编号列表，但**仅在编辑器里实时输入时**触发；用 API str_replace 写入的 `1.` 是纯文本，不会自动激活编号 UI
- 想真用编号功能 → 在 Feishu 编辑器里手动把光标放在标题前敲 `1. ` 触发智能编号

### 6. 表格空 cell 无法用 str_replace 匹配

```xml
<td></td>  <!-- 空格也算不到字符 -->
```

**应对**：
- 用 `前缀...后缀` 省略号语法跨越空 cell
- 或用 `block_replace` 直接对 `<td>` 内部 `<p>` 操作（注意 1 次性限制）
- 或 str_replace 整行内容（包括前后 cell 作锚点）

### 7. 复杂结构（callout / grid）的子块用 `block_insert_after` 走 XML 模式

```bash
# 想要 callout，必须 --doc-format xml（默认），不能 markdown
lark-cli docs +update --command block_insert_after --block-id "X" \
  --content '<callout emoji="💡"><p>高亮框</p></callout>'
```

markdown 模式下的 `<callout>` `<grid>` 不会渲染，会被转义为字面量。

### 8. `str_replace` 不识别 `<p id="...">` block id 限定符（2026-06-11 case 验证）

**症状**: pattern 看起来 unique (`<p id="doxcnXYZ">旧文本</p>`) 但实际匹配了**所有** `旧文本` 实例。
**根因**: str_replace 在 lark 序列化层做纯文本匹配，`<p id="...">` 限定符被剥除, 只比较 inner text。
**典型反例**: 文档模板里 `❓ 待补` 出现 25+ 次，用 `<p id="X">❓ 待补</p>` 限定看似唯一, 实际触发 25 处全文替换, 1 次操作污染 23 个 block (XCkgdqmKSoSyiBxM9FYcbYLjnkb 实测)。
**应对**:
- 表格 cell / callout 子块 → 改用 `block_replace --block-id <id>` (API 层寻址, 不走文本匹配)
- str_replace 只用于**全文唯一**的纯文本 (标题、版本号、url 等)
- 改前 `grep` 计数目标字符串在文档中出现次数, > 1 即有风险
- 改后**立即** `docs +fetch --scope section/range` 验证, 不要相信 `result: success`

### 9. `block_insert_after` 多块 content 含 callout 静默吞并（2026-06-11 case 验证）

**症状**: `--content '<li>...</li>...<li>...</li><callout>...</callout>'` (5 块混合) 实际只插入 4 li, callout 丢失。
**根因**: callout 带 `emoji` / `background-color` / `border-color` 属性, 在多块 content 上下文中被静默跳过; `result: success` 仍返回, 不报错。
**应对**:
- callout **必须单独一次** `block_insert_after`, 与其他 block 分开调用
- 插入后**立即** `docs +fetch --scope range` 跨过目标位置验证
- 不要相信 `result: success` — 这只表示请求被接受, 不表示全部 block 都插入
- 如果要插入 li + callout, 先插 li (单独 call), 再插 callout (单独 call)

### 10. 验证脚本

```bash
# ~/.claude/scripts/lark-doc-update-verify.sh
# 用法: lark-doc-update-verify.sh <doc_id> <start_block> <end_block> <expected_string>
DOC=$1
START=$2
END=$3
EXPECTED=$4
lark-cli docs +fetch --api-version v2 --doc "$DOC" \
  --scope range --start-block-id "$START" --end-block-id "$END" \
  --detail with-ids | grep -q "$EXPECTED" \
  || { echo "VERIFY FAIL: '$EXPECTED' not found in range"; exit 1; }
echo "VERIFY OK"
```

### 11. `docs +fetch` 3380003 不可靠, 必须 `wiki +node-list` 二次确认 (2026-06-12 case 验证)

**症状**: `docs +fetch --doc <token>` 返 `{"ok": false, "error": {"code": 3380003, "message": "Document page has been deleted"}}`. claudecode 误判为 cascade delete 灾难, 实际是 lark 内部 doc aliasing.

**根因**: 飞书 wiki 节点可对应多个 docx token (aliased). URL 拿到的 token 跟真实存储 docx 是**两个不同 docx**. lark 通过 wiki 名称匹配做 aliasing, `docs +update` 写入和 `docs +fetch` 读出可能用不同 token. 一旦其中之一失效, 3380003 出现.

**典型反例**: 删除 dashboard (`drive +delete`) 后, dashboard 树里的 docx token 返 3380003, 但申博 space 里的同名 doc (`XPwod9uB6oCU8NxUCh0c59b4nyf`) 仍完好. claudecode 误判 cascade 灾难, 用户指引后才意识到.

**应对**:
- **删除前**: `lark-cli wiki +node-list --space-id <X>` 列空间全部节点, 确认 target 是顶级 (parent_node_token = "") vs 子节点
- **删除后**: 看到 3380003 不立刻 = 灾难. 必须 `wiki +node-list` 二次确认空间结构
- **首选 `wiki +node-delete` 替代 `drive +delete`**: 前者明确 wiki 树层级, 有 polling 提示, 错误信息可读
- **用 `drive +inspect --url` 拿 canonical token**: 不能凭 URL + 1 次 fetch 推断 docx token
- **验证脚本 fallback** (v2 升级): `lark-doc-update-verify.sh` 自动 `wiki +node-list` 跨 space 搜; exit 4 = 找到了, exit 3 = 真的丢了

### 12. 飞书 wiki 树 parent-children cascade 风险, dashboard 删除触发 children 失效 (2026-06-12 case 验证)

**症状**: `lark-cli drive +delete --file-token <dashboard_docx> --type docx --yes` 返 `{"deleted": true, "file_token": "..."}`. 看似只删 dashboard, 实际触发 wiki 树 parent-children cascade, dashboard **子节点** 全部失效.

**根因**: 飞书 wiki 是树结构, parent 节点 docx 删除 = 关联的 children wiki 节点全部失效. `drive +delete` 不提示 cascade 风险, 不区分 docx vs wiki node.

**典型反例**: 用户授权删除 dashboard (申博候选调研), dashboard 树里的子节点 docx 全部返 3380003. claudecode 误报"cascading delete 灾难"给用户, 实际申博 space 顶级节点 (独立树) 未受影响, 数据 0 损失.

**应对**:
- **删除 wiki 节点前必跑 `wiki +node-list` 列 children**: `lark-cli wiki +node-list --parent-node-token <target>` 列出 target 下所有子节点
- **首选 `wiki +node-delete` 替代 `drive +delete`**: 前者明确 wiki 树层级, polling 提示 cascade 范围; 后者直接删底层 docx, cascade 行为不透明
- **删除前用 `--dry-run` 预览**: `lark-cli drive +delete --dry-run` 打印完整请求, 但不阻止 cascade
- **删完立即 `wiki +node-list --space-id` 二次验证**: 空间顶级 vs 子节点 状态

## 参考


- [`lark-doc-update-workflow.md`](style/lark-doc-update-workflow.md) — 改写增强工作流（Code-Act Loop、并行执行策略）
- [`lark-doc-style.md`](style/lark-doc-style.md) — 文档样式指南（元素选择 + 丰富度规则 + 颜色语义）
- [`lark-doc-xml.md`](lark-doc-xml.md) — XML 语法规范
- [`lark-doc-fetch.md`](lark-doc-fetch.md) — 获取文档
- [`lark-doc-create.md`](lark-doc-create.md) — 创建文档
- [`lark-doc-media-insert.md`](lark-doc-media-insert.md) — 插入图片/文件到文档
- [`../../lark-shared/SKILL.md`](../../lark-shared/SKILL.md) — 认证和全局参数
