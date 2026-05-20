# Academic Project Page Checklist

> 针对学术海报（Poster）+ 幻灯片（Slides）项目的专用审计清单。
> 适用项目：OSA、GDKVM 等论文宣传页。

---

## 0. DESIGN.md 存在性与一致性

**检测：**
```bash
[ -f "DESIGN.md" ] && echo "FOUND" || echo "MISSING"
```

**规则：**
- 若无 DESIGN.md → **自动创建模板**（见下方），标记为 P0 建议人工填充
- 若有 DESIGN.md → 检查代码是否遵守其中的硬约束（字号、高度、颜色等）

**自动创建模板（当 DESIGN.md 缺失时）：**
```markdown
# {Project} Poster 排版设计规范

## 1. 物理尺寸
| 属性 | 值 |
|------|-----|
| 总尺寸 | 84in × 42in |
| Header 高度 | 8in |
| Content 高度 | 32in（硬约束，不可突破） |
| Footer 高度 | 2in |
| 列数 | 4 列等宽 |

## 2. 硬约束
- Content 区域高度 = 32in
- 每列 `scrollHeight` 必须等于 `clientHeight`（无溢出）
- 图片 `max-height: 6in`
- Grid track 高度用 `minmax(0, 1fr)` 替代固定值

## 3. WebKit 兼容性
- `.column` 必须设置 `min-height: 0`
- `.column-inner` 作为 flex 容器必须包裹在 `.column`（grid item）内部
- Grid cell 内的 `<img>` 必须显式 `display: block` + `max-width/height: 100%`

## 4. 修改 checklist
1. [ ] `npm run build` 通过（0 errors）
2. [ ] 4 列 `scrollHeight === clientHeight`
3. [ ] `maxFigureHeight <= 576px`（6in）
4. [ ] WebKit 截图无溢出
```

---

## 1. Poster 布局硬约束

### 1.1 高度约束

**检测：**
```bash
# 检查 Poster.astro 中的高度定义
grep -n "32in\|content.*height\|min-height\|max-height" src/components/Poster.astro
```

**通过标准：**
- Content 区域高度严格等于 32in（或等效 px，如 3072px @ 96dpi）
- 任何增加内容高度的改动必须通过压缩其他区域补偿

### 1.2 列溢出检测

**检测（Playwright）：**
```javascript
// 每列 scrollHeight 必须等于 clientHeight
const columns = await page.locator('.column').all();
for (const col of columns) {
  const sh = await col.evaluate(el => el.scrollHeight);
  const ch = await col.evaluate(el => el.clientHeight);
  if (sh > ch) console.error(`OVERFLOW: col scrollHeight=${sh} > clientHeight=${ch}`);
}
```

**通过标准：** 4 列均 `scrollHeight === clientHeight`

### 1.3 图片大小约束

**检测：**
```bash
grep -n "max-height.*6in\|576px" src/components/Poster.astro
```

**通过标准：**
```css
.figure img {
  max-height: 6in;  /* 或 576px */
}
```

### 1.4 弹性压缩

**检测：**
```bash
grep -n "flex:.*auto\|min-height:.*0" src/components/Poster.astro
```

**通过标准：**
```css
.section {
  flex: 1 1 auto;
  min-height: 0;  /* 允许 section 被压缩 */
}
```

---

## 2. WebKit 兼容性（Safari / iOS）

> 来源：`~/.claude/rules/css-layout-cross-browser.md`

### 2.1 Flex + Grid 层级隔离

**规则：** flex parent 与 grid child 之间必须有一层 `display: block` 的 wrapper。

**检测：**
```bash
grep -n "display:.*flex" src/components/Poster.astro
grep -n "display:.*grid" src/components/Poster.astro
# 检查 grid item 是否直接就是 flex container
```

### 2.2 Grid Cell 内的 Image Block 化

**检测：**
```bash
grep -A5 "\.column.*img\|\.figure.*img\|grid-cell.*img" src/components/Poster.astro
```

**通过标准：**
```css
.grid-cell img,
.column img {
  display: block;
  width: 100%;
  height: 100%;
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  margin: 0;
}
```

### 2.3 Grid Track 高度

**检测：**
```bash
grep -n "grid-template-rows" src/components/Poster.astro
```

**通过标准：**
```css
/* ❌ 禁止固定 px */
/* grid-template-rows: 320px 260px; */

/* ✅ 必须使用 minmax(0, ...) */
grid-template-rows: minmax(0, 320px) minmax(0, 260px);
```

### 2.4 Playwright 双端验证

**必须同时验证：**
- Chromium（桌面端 viewport）
- WebKit/Safari（移动端 viewport，或 Playwright `webkit` 浏览器）

**检测：**
```bash
# Playwright 截图对比
npx playwright test --project=chromium --project=webkit
```

---

## 3. KaTeX 公式渲染

### 3.1 CDN 可用性

**检测：**
```bash
grep -n "katex" src/components/*.astro src/layouts/*.astro
```

**评估：**
- KaTeX CSS/JS 是否从 CDN 加载？
- 如果是，是否有本地 fallback？
- 公式是否在 SSR/构建时预渲染？还是客户端渲染？

### 3.2 公式块大小

**检测：**
```bash
grep -n "formula-box\|\.formula" src/components/Poster.astro
```

**通过标准（若 DESIGN.md 定义）：**
```css
.formula-box {
  font-size: 28pt;    /* 不可超过 30pt */
  padding: 0.05in;    /* 不可超过 0.08in */
}
```

---

## 4. Slides 检查

### 4.1 页面结构

**检测：**
```bash
cat src/pages/[lang]/slides.astro 2>/dev/null || cat src/pages/slides.astro
```

**通过标准：**
- 全屏 iframe 或等效布局
- 包含 zoom/print 控制按钮
- 支持键盘导航（左右箭头、空格）

### 4.2 响应式与打印

**检测：**
```bash
grep -n "@media print\|zoom\|scale\|transform" src/components/*.astro src/pages/*.astro
```

**通过标准：**
- 打印样式正确（无截断、背景色保留）
- Zoom 控制不破坏布局

---

## 5. 学术资产引用

### 5.1 图片路径可用性

**检测：**
```bash
grep -rn '"/academic/images/' src/ --include="*.astro" --include="*.ts" --include="*.json"
```

**通过标准：**
- 所有 `/academic/images/...` 路径对应的图片在 `wangrui2025.github.io/academic/` 上可访问
- 无 404 引用

### 5.2 跨域与 CORS

**评估：**
- 学术资产从主站跨域加载，确认无 CORS 问题
- 如有需要，`<img crossorigin="anonymous">` 或等价处理

---

## 6. 评分权重（学术项目页）

在 `scan-checklist.md` 通用评分基础上，学术项目页调整：

| 维度 | 权重 | 说明 |
|------|------|------|
| Build Health | 15% | |
| Astro 6.x Compliance | 10% | |
| **Poster 硬约束** | **25%** | 高度、列溢出、图片大小 |
| **WebKit 兼容性** | **15%** | 双端验证 |
| i18n Parity | 10% | en/zh 内容对等 |
| KaTeX / Slides | 10% | 公式渲染、幻灯片功能 |
| Security | 10% | |
| Performance | 5% | |

---

## 7. 修改后验证

任何涉及 Poster/Slides 的修改，发布前必须：

1. [ ] `npm run build` 通过（0 errors）
2. [ ] 4 列 `scrollHeight === clientHeight`（Playwright）
3. [ ] `maxFigureHeight <= 576px`（6in）
4. [ ] WebKit 截图无溢出（Playwright webkit）
5. [ ] KaTeX 公式渲染正常（Chromium + WebKit）
6. [ ] Slides zoom/print 控制正常
