---
name: lark-slides
version: 1.0.0
description: "飞书幻灯片：创建和编辑幻灯片。创建演示文稿、读取幻灯片内容、管理幻灯片页面（创建、删除、读取、局部替换）。当用户需要创建或编辑幻灯片、读取或修改单个页面时使用。当用户给出 doubao.com 的 /slides/ URL/token 时，也应直接使用本 skill，不要因为域名不是飞书而回退到 WebFetch；路由依据是 URL 路径模式和 token，而不是域名。不负责：云文档内容编辑（走 lark-doc）、云文档里的独立画板对象（走 lark-whiteboard，注意 slide 内嵌的流程图/架构图仍属本 skill）、上传或下载普通文件（走 lark-drive）。"
metadata:
  requires:
    bins: ["lark-cli"]
  cliHelp: "lark-cli slides --help"
---

# slides (v1)

## Quick Reference

| 用户需求 | 优先动作 | 关键文档 / 命令 |
|----------|----------|-----------------|
| 新建 PPT | 先规划 `slide_plan.json`，再按复杂度选择一步或两步创建 | `planning-layer.md`、`visual-planning.md`、`asset-planning.md`、`slides +create` |
| 大幅改写页面 | 先回读现有 XML，写入新 plan，再替换或重建相关页面 | `xml_presentations.get`、`+replace-slide`、`lark-slides-edit-workflows.md` |
| 编辑单个标题、文本块、图片或局部元素 | 优先块级替换/插入，不改页序 | `slides +replace-slide`、`lark-slides-replace-slide.md` |
| 读取或分析已有 PPT | 解析 slides/wiki token，回读全文或单页 XML，保存 `xml_presentation_id`、`slide_id`、`revision_id` | `xml_presentations.get`、`xml_presentation.slide.get` |
| 上传或使用图片 | 先上传为 `file_token`，禁止直接写 http(s) 外链 | `slides +media-upload`，或 `+create --slides` 的 `@./path` 占位符 |
| 在 slide 中绘制柱/条/折线/面积/雷达/饼等有数据序列的图表 | 使用原生 `<chart>` 元素 | `xml-schema-quick-ref.md` |
| 在 slide 中绘制流程图、时序图、架构图、散点图、漏斗图或装饰图案 | 必须先用 Read 工具读取参考文档，再生成 `<whiteboard>` 元素 | [`lark-slides-whiteboard.md`](references/lark-slides-whiteboard.md) |
| 使用语义图标 | 先检索 IconPark，再写 `<icon iconType="...">` | `iconpark_tool.py search → resolve`、`iconpark.md` |
| 用户提到模板、主题、版式 | 先检索模板，再摘要，必要时裁切骨架 | `template_tool.py search → summarize → extract` |
| 创建失败、空白页、3350001、布局异常 | 先回读状态，再按排障清单修复，不假设原操作原子成功 | `troubleshooting.md`、`validation-checklist.md` |

**CRITICAL — 开始前 MUST 先用 Read 工具读取 [`../lark-shared/SKILL.md`](../lark-shared/SKILL.md)，认证、权限和全局参数均以 lark-shared 为准。**

**CRITICAL — 生成任何 XML 之前，MUST 先用 Read 工具读取 [xml-schema-quick-ref.md](references/xml-schema-quick-ref.md)，禁止凭记忆猜测 XML 结构。**

**CRITICAL — 新建演示文稿或大幅改写页面时，MUST 先生成 `.lark-slides/plan/<deck-or-task-id>/slide_plan.json`，再生成 XML。先创建对应目录，规划层规则和中间产物生命周期见 [planning-layer.md](references/planning-layer.md)。仅替换一个标题、插入一个块等小型已有页编辑可豁免。**

**CRITICAL — 新建演示文稿或大幅改写页面时，生成 XML 前 MUST 读取 [visual-planning.md](references/visual-planning.md)，确保 `layout_type`、`visual_focus`、`text_density` 实际改变页面几何、主视觉和文本量。**

**CRITICAL — 新建演示文稿或大幅改写页面时，规划 `asset_need` MUST 遵循 [asset-planning.md](references/asset-planning.md)：只做元数据规划，必须有 `fallback_if_missing`，不得要求真实搜索、下载或上传素材。**

**CRITICAL — 创建或大幅改写后，MUST 按 [validation-checklist.md](references/validation-checklist.md) 做显式验证：回读全文 XML、核对页数和关键元素、检查空白/破损页、明显溢出、布局风险；XML 语法和文本重叠静态检查优先使用 [`scripts/xml_text_overlap_lint.py`](scripts/xml_text_overlap_lint.py)。**

**CRITICAL — 创建前自检或失败排障时，MUST 按 [troubleshooting.md](references/troubleshooting.md) 检查 XML 转义、结构、shell 截断、图片 token、3350001 和布局风险。**

**CRITICAL — 如果用户提到“模板”“套用模板”“参考某种主题/风格/版式”，或用户需求明显落在已有场景模板内（如工作汇报、产品介绍、商业计划书、培训、晋升汇报等），MUST 先用 [`scripts/template_tool.py`](scripts/template_tool.py) 的 `search` 做模板检索；默认给出 2-3 个最匹配模板候选供用户选择。锁定模板后用 `summarize` 获取主题和布局摘要；只有需要布局骨架时才用 `extract` 裁切目标页型 XML。不要直接读取完整模板 XML。**

> [!NOTE]
> `scripts/template_tool.py` 需要 Python 3。`references/template-index.json` 是脚本缓存/轻量路由索引，不是默认给 agent 阅读的文档；`assets/templates/*.xml` 是机器资源，只应通过脚本摘要或裁切，不要全文读取。

**CRITICAL — 使用模板生成或改写页面时，MUST 先 `summarize` 目标页型；只有需要具体布局骨架时才 `extract`。**

**编辑已有幻灯片页面**：优先用 [`+replace-slide`](references/lark-slides-replace-slide.md)（块级替换/插入，不动页序）；选择 action 和完整读-改-写流程见 [`lark-slides-edit-workflows.md`](references/lark-slides-edit-workflows.md)。

## 身份选择

飞书幻灯片通常是用户自己的内容资源。**默认应优先显式使用 `--as user`（用户身份）执行 slides 相关操作**，始终显式指定身份。

- **`--as user`（推荐）**：以当前登录用户身份创建、读取、管理演示文稿。执行前先完成用户授权：

```bash
lark-cli auth login --domain slides
```

- **`--as bot`**：仅在用户明确要求以应用身份操作，或需要让 bot 持有/创建资源时使用。使用 bot 身份时，要额外确认 bot 是否真的有目标演示文稿的访问权限。

**执行规则**：

1. 创建、读取、增删 slide、按用户给出的链接继续编辑已有 PPT，默认都先用 `--as user`。
2. 如果出现权限不足，先检查当前是否误用了 bot 身份；不要默认回退到 bot。
3. 只有在用户明确要求"用应用身份 / bot 身份操作"，或当前工作流就是 bot 创建资源后再做协作授权时，才切换到 `--as bot`。

## 执行前必做

> **重要**：`references/slides_xml_schema_definition.xml` 是此 skill 唯一正确的 XML 协议来源；其他 md 仅是对它和 CLI schema 的摘要。

高频只读：

- [xml-schema-quick-ref.md](references/xml-schema-quick-ref.md)
- [planning-layer.md](references/planning-layer.md)（新建 / 大幅改写）
- [visual-planning.md](references/visual-planning.md)（新建 / 大幅改写）
- [asset-planning.md](references/asset-planning.md)（新建 / 大幅改写）
- [validation-checklist.md](references/validation-checklist.md)（创建 / 大幅改写后）

按需再读：

- 创建：[`lark-slides-create.md`](references/lark-slides-create.md)
- 编辑：[`lark-slides-edit-workflows.md`](references/lark-slides-edit-workflows.md)、[`lark-slides-replace-slide.md`](references/lark-slides-replace-slide.md)
- 图片：[`lark-slides-media-upload.md`](references/lark-slides-media-upload.md)
- 流程图 / 时序图 / 架构图 / 装饰图案：[`lark-slides-whiteboard.md`](references/lark-slides-whiteboard.md)
- 图标：[`iconpark.md`](references/iconpark.md)、[`scripts/iconpark_tool.py`](scripts/iconpark_tool.py)
- 模板：[`template-catalog.md`](references/template-catalog.md)、[`scripts/template_tool.py`](scripts/template_tool.py)
- 排障：[`troubleshooting.md`](references/troubleshooting.md)
- 完整协议：[`slides_xml_schema_definition.xml`](references/slides_xml_schema_definition.xml)

## Workflow

> 已下沉到 `references/lark-slides-workflow-templates.md`（创建方式选择、模板与脚本优先流程、jq 命令模板、大纲模板）。

设计视觉策略见 `references/lark-slides-design-guide.md`。

## 核心概念

### URL 格式与 Token

| URL 格式 | 示例 | Token 类型 | 处理方式 |
|----------|------|-----------|----------|
| `/slides/` | `https://example.larkoffice.com/slides/xxxxxxxxxxxxx` | `xml_presentation_id` | URL 路径中的 token 直接作为 `xml_presentation_id` 使用 |
| `/wiki/` | `https://example.larkoffice.com/wiki/wikcnxxxxxxxxx` | `wiki_token` | ⚠️ **不能直接使用**，需要先查询获取真实的 `obj_token` |

> `+replace-slide` 和 `+media-upload` shortcut 会自动解析以上两种 URL；直接调用原生 API 时仍需手动解析 wiki 链接。

### Wiki 链接特殊处理（关键！）

知识库链接（`/wiki/TOKEN`）不能直接当 `xml_presentation_id`。直接调用原生 API 前，先查询 wiki 节点，确认 `node.obj_type == "slides"`，再用 `node.obj_token` 作为真实 presentation ID。

```bash
lark-cli wiki spaces get_node --as user --params '{"token":"wiki_token"}'
```

Shortcut `+replace-slide` 和 `+media-upload` 会自动解析 `/wiki/` URL；手动调用 `xml_presentations.*` / `xml_presentation.slide.*` 时才需要自己做这一步。

### 资源关系

```text
Wiki Space (知识空间)
└── Wiki Node (知识库节点, obj_type: slides)
    └── obj_token → xml_presentation_id

Slides (演示文稿)
├── xml_presentation_id (演示文稿唯一标识)
├── revision_id (版本号)
└── Slide (幻灯片页面)
    └── slide_id (页面唯一标识)
```

## Shortcuts 与 API

Shortcut 是对常用操作的高级封装（`lark-cli slides +<verb> [flags]`）。有 Shortcut 的操作优先使用。

| Shortcut | 说明 |
|----------|------|
| [`+create`](references/lark-slides-create.md) | 创建 PPT（可选 `--slides` 一步添加页面，支持 `<img src="@./local.png">` 占位符自动上传） |
| [`+media-upload`](references/lark-slides-media-upload.md) | 上传本地图片到指定演示文稿，返回 `file_token`（用作 `<img src="...">`），最大 20 MB |
| [`+replace-slide`](references/lark-slides-replace-slide.md) | 对已有幻灯片页面进行块级替换/插入（`block_replace` / `block_insert`），自动注入 id 和 `<content/>`，不改变页序 |

没有 Shortcut 覆盖时使用原生 API。高频资源：`xml_presentations.get` 读取全文；`xml_presentation.slide.create/delete/get/replace` 管理单页。

```bash
lark-cli schema slides.<resource>.<method>   # 调用 API 前必须先查看参数结构
lark-cli slides <resource> <method> [flags] # 调用 API
```

> **重要**：使用原生 API 时，必须先运行 `schema` 查看 `--data` / `--params` 参数结构，不要猜测字段格式。

## 核心规则

1. **先规划再写 XML**：新建演示文稿或大幅改写页面时，必须先写入 `.lark-slides/plan/<deck-or-task-id>/slide_plan.json`；模板、风格和大纲只能作为规划输入，不能绕过规划层
2. **创建流程**：简单短 XML（1-3 页、结构简单、特殊字符少）可用 `slides +create --slides '[...]'` 一步创建；复杂内容、含图片/中文大段文本/嵌套引号/较多特殊字符，或超过 10 页时，默认先 `slides +create` 创建空白 PPT，再用 `xml_presentation.slide.create` 逐页添加
3. **`<slide>` 直接子元素只有 `<style>`、`<data>`、`<note>`**：文本和图形必须放在 `<data>` 内
4. **文本通过 `<content>` 表达**：必须用 `<content><p>...</p></content>`，不能把文字直接写在 shape 内
5. **保存关键 ID**：后续操作需要 `xml_presentation_id`、`slide_id`、`revision_id`
6. **删除谨慎**：删除操作不可逆，且至少保留一页幻灯片
7. **编辑已有页面优先块级替换**：修改单个 shape/img 用 `+replace-slide`（`block_replace` / `block_insert`），不要整页重建；只有需要替换整页结构时才用 `slide.delete` + `slide.create`
8. **`<img src>` 只能用上传到飞书 drive 的 `file_token`，禁止使用 http(s) 外链 URL**：飞书 slides 渲染端不会代理外链图片，外链 src 在 PPT 里通常不显示或显示破图。流程必须是「先把图存到本地 → 用 `slides +media-upload` 上传或 `+create --slides` 的 `@./path` 占位符自动上传 → 拿 `file_token` 写进 `<img src>`」。如果用户给了网图链接，先 `curl`/下载到 CWD 内再走上传流程，不要直接把外链 URL 塞进 `src`。**图片最大 20 MB**（slides upload API 不支持分片上传）。

> **注意**：如果 md 内容与 `slides_xml_schema_definition.xml` 或 `lark-cli schema slides.<resource>.<method>` 输出不一致，以后两者为准。