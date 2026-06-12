## Workflow

> **这是演示文稿，不是文档。** 每页 slide 是独立的视觉画面，信息密度要低，排版要留白。

### Design Ideas

不要生成无设计感的幻灯片。纯白背景 + 标题 + bullets 只能作为极简临时稿，不能作为正式交付。

开始写 XML 前，先在 `slide_plan.json` 里确定 deck 级视觉策略：

- **主题化配色**：配色必须服务本次主题、行业和受众，不要默认蓝色商务风。如果把同一套颜色换到另一个完全不同主题仍然成立，说明配色不够具体。
- **主次比例**：选择 1 个主色承担约 60-70% 视觉权重，1-2 个辅助色承担结构和分区，1 个强调色只用于关键数字、结论或行动点。不要让所有颜色权重相同。
- **背景一致性**：先确定全 deck 的背景策略，默认保持同一明暗基调和底色体系；只有分节、转场或强调页才有意改变背景，并必须通过相同主色、纹理、边栏或 motif 让变化看起来属于同一套设计。无论深浅，都要保证正文、图标和线条对比充足。
- **统一 motif**：选择一个可复用视觉母题贯穿全文，例如粗侧边栏、圆形图标底、半出血图片区、编号节点、卡片左上角色块或大号数字。不要每页换一套装饰语言。

每页至少要有一个视觉元素：图片、图标、图表、表格、流程、对比结构、大号数字、示意图或由 shape 组成的抽象视觉。文本框本身不算主视觉。

可优先考虑这些页面形态：

- **双栏结构**：左文右图或左图右文，视觉区域占 35-45% 宽度。
- **图标行**：图标在色块或圆形底中，右侧是短标题和一句解释。
- **2x2 / 2x3 网格**：适合能力、模块、风险、行动项，每格内容保持同等层级。
- **半出血视觉**：图片或抽象形状占据左/右半屏，文字覆盖或贴边排布。
- **大数字卡片**：关键指标用 60-72pt 数字，下面配 10-14pt 标签。
- **对比列**：before/after、方案 A/B、问题/解法用左右并列，标题和基线严格对齐。
- **时间线/流程图**：步骤用节点和箭头表达，流程方向必须一眼可见。

字体和间距建议：

- 标题 36-44pt，关键结论可更大；正文 14-18pt；注释 10-12pt。
- 正文默认左对齐；只在封面、结尾或大号数字场景中使用居中。
- 页面边距至少 40px；内容块之间保持 24-40px 间距，并在同一 deck 内保持一致。
- 卡片内边距要真实留出空间，不要让文字贴边；对齐 shape 和文字时要考虑文本框 padding。

常见错误必须避免：

- 不要所有页面复用同一种标题 + 三 bullets 版式。
- 不要用低对比文字或低对比图标，例如浅灰字压在浅色背景上。
- 不要让装饰线穿过文字，或让页脚、来源、编号挤压主体内容。
- 不要把素材缺失表现为空白图片框；必须按 `fallback_if_missing` 生成 XML-native 视觉。
- 不要留下模板占位文案、示例公司名、示例日期或与用户主题无关的原模板内容。

### 创建方式选择

| 场景 | 推荐方式 |
|------|----------|
| 简单 XML（1-3 页、结构简单、几乎无复杂中文和特殊字符） | `slides +create --slides '[...]'` 一步创建 |
| 复杂 XML（多页、含中文、大段文本、复杂布局、嵌套引号、特殊字符较多） | **两步创建**：先 `slides +create` 创建空白 PPT，再用 `xml_presentation.slide create` 逐页添加 |
| 已有 PPT 继续追加或插入页面 | 使用 `xml_presentation.slide create`，必要时配合 `before_slide_id` |

> [!WARNING]
> `--slides '[...]'` 的风险点主要在 shell 参数传递，而不是单纯页数。即使只有 1 页，只要 XML 足够复杂，也建议使用两步创建法。

> [!IMPORTANT]
> `slides +create --slides` 底层会逐页创建，不是原子操作。中途失败时先记录 `xml_presentation_id`，回读确认当前状态，再继续修复或追加。

### 模板与脚本优先流程

模板细则见 [template-catalog.md](references/template-catalog.md)。主流程只记住：先 `search`，锁定后 `summarize`，需要骨架时才 `extract`；不要直接读取完整模板 XML 或照搬占位文案。

```bash
python3 skills/lark-slides/scripts/template_tool.py search --query "<用户需求原文>" --limit 3
python3 skills/lark-slides/scripts/template_tool.py summarize --template <template-id> --label <封面|目录|分节|内容|结尾>
python3 skills/lark-slides/scripts/template_tool.py extract --template <template-id> --label <页型> --out /tmp/template-slice.xml
```

```text
Step 1: 需求澄清 & 读取知识
  - 澄清主题、受众、页数、风格；模板需求按“模板与脚本优先流程”处理
  - 读取 xml-schema-quick-ref.md；新建 / 大幅改写时还要读取 planning-layer.md、visual-planning.md、asset-planning.md

Step 2: 生成大纲 → 用户确认 → 写入 slide_plan.json
  - 生成结构化大纲供用户确认；如使用模板，标明基于哪个模板改写
  - 新建 / 大幅改写必须先创建目录并写入 `.lark-slides/plan/<deck-or-task-id>/slide_plan.json`
  - plan 字段、路径命名、模板边界和 `asset_need` 结构按 planning-layer.md / asset-planning.md 执行

Step 3: 按 slide_plan.json 生成 XML → 创建
  - 逐页消费 plan：key_message 定主结论，layout_type 定几何，visual_focus 定主视觉，text_density 定文本量
  - 缺少真实素材时必须用 `fallback_if_missing` 生成 XML-native 兜底视觉；不要留空
  - 创建方式按“创建方式选择”判断；图片、复杂 XML、转义和 3350001 排查按 lark-slides-create.md、media-upload.md、troubleshooting.md 执行

Step 4: 审查 & 交付
  - 创建完成后，必须用 xml_presentations.get 读取全文 XML，并按 validation-checklist.md 做显式验证记录，包括 XML 文本重叠检查
  - 失败或部分成功按 troubleshooting.md 处理；局部问题优先用 `+replace-slide` 修正
  - 没问题 → 交付：告知用户演示文稿 ID 和访问方式
```

### jq 命令模板（编辑已有 PPT 时使用）

新建 PPT 推荐用 `+create --slides`。以下 jq 模板适用于向已有演示文稿追加页面的场景，可以避免手动转义双引号：

```bash
# 追加到末尾
lark-cli slides xml_presentation.slide create \
  --as user \
  --params '{"xml_presentation_id":"YOUR_ID"}' \
  --data "$(jq -n --arg content '<slide xmlns="http://www.larkoffice.com/sml/2.0">
  <style><fill><fillColor color="BACKGROUND_COLOR"/></fill></style>
  <data>
    在这里放置 shape、line、table、chart 等元素
  </data>
</slide>' '{slide:{content:$content}}')"

# 插到指定页之前：before_slide_id 必须在 --data body 里，与 slide 同级
# ⚠️ 不要把 before_slide_id 写进 --params —— CLI 会当未知 query 参数静默下发，服务端忽略，新页跑到末尾
lark-cli slides xml_presentation.slide create \
  --as user \
  --params '{"xml_presentation_id":"YOUR_ID"}' \
  --data "$(jq -n --arg content '<slide ...>...</slide>' --arg before 'TARGET_SLIDE_ID' \
    '{slide:{content:$content}, before_slide_id:$before}')"
```

> 渐变色必须使用 `rgba()` 格式并带百分比停靠点，如 `linear-gradient(135deg,rgba(15,23,42,1) 0%,rgba(56,97,140,1) 100%)`。使用 `rgb()` 或省略停靠点会导致服务端回退为白色。

### 大纲模板

生成大纲时使用以下格式，交给用户确认：

```text
[PPT 标题] — [定位描述]，面向 [目标受众]

模板：[未使用模板 / <category>/<template>.xml（推荐原因）]

页面结构（N 页）：
1. 封面页：[标题文案]
2. [页面主题]：[要点1]、[要点2]、[要点3]
3. [页面主题]：[要点描述]
...
N. 结尾页：[结尾文案]

风格：[配色方案]，[排版风格]
```
