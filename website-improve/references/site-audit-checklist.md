# Site Audit Checklist

Derived from real-world audits of academic personal homepages and project pages.

**Scope**: 通用网站 + 主站特定检查。学术项目页（Poster/Slides）的专用检查见 `academic-project-checklist.md`。

---

## 项目类型检测（运行时）

进入审计后，先检测项目类型：

```bash
# 检测是否为学术项目页
if [ -f "DESIGN.md" ] || grep -q "Poster\|Slides" src/components/*.astro 2>/dev/null; then
  echo "TYPE=academic-project"
else
  echo "TYPE=generic-site"
fi
```

- `TYPE=academic-project` → 同时加载 `academic-project-checklist.md`
- `TYPE=generic-site` → 仅执行本清单 + 通用扫描

---

## Pre-Audit Web Research

> **MANDATORY.** Validate current best practices before auditing.

```
mcp__context7__query_docs: "Astro academic personal homepage best practices 2025"
mcp__context7__query_docs: "PWA maskable icon manifest specification 2025"
mcp__context7__query_docs: "Open Graph image size recommendation Twitter LinkedIn 2025"
WebSearch: "academic personal homepage SEO best practices 2025"
```

---

## 通用检查项（所有项目）

| Priority | Issue | Impact |
|----------|-------|--------|
| P0 | `npx astro check` 0 errors | Build health |
| P0 | `npm run build` 0 errors | Deploy blocker |
| P1 | 无重复页面（如 `/cv.astro` + `/[lang]/cv.astro`） | Routing 冲突 |
| P1 | 无 `Astro.glob` / `ViewTransitions` 等废弃 API | Astro 6.x 合规 |
| P1 | `set:html` 审计 + secrets 扫描 | 安全红线 |
| P1 | a11y 合规（详见下方） | WCAG 2.2 AA |
| P1 | **暗黑模式功能正常** | 用户体验 |
| P1 | **中英文切换功能正常** | i18n 完整性 |
| P1 | **学术资产已库化**（本地图片迁移至 `mykcs/academic` CDN） | 资产治理 |
| P2 | **显示正常**（无布局溢出、无 FOUC） | 视觉质量 |
| P2 | **功能正常**（交互元素可点击、无 JS 错误） | 交互完整性 |
| P2 | 未使用依赖清理 | 构建体积 |
| P2 | 图片懒加载策略 | LCP 优化 |

### a11y 详细检查项

| # | 检查项 | 命令 | 通过标准 |
|---|--------|------|----------|
| 1 | 图片 alt | `grep -rn "<img" src/ --include="*.astro" \| grep -v "alt=" \| grep -v "decorative"` | 无结果 |
| 2 | Input label | `grep -rn "<input" src/ --include="*.astro" \| grep -v "aria-label\\|aria-labelledby\\|<label"` | 无结果 |
| 3 | Focus 可见 | `grep -rn "outline: none\\|outline:none" src/ --include="*.css" --include="*.astro"` | 无结果，或有 `:focus-visible` 恢复 |
| 4 | 语义化标题 | `grep -rn "<h1" src/pages/ --include="*.astro" \| wc -l` | 每页 1 个 |
| 5 | lang 属性 | `grep -rn '<html lang=' src/layouts/ --include="*.astro"` | 存在且正确 |
| 6 | 对比度 | DevTools Lighthouse Accessibility 或 WebAIM Contrast Checker | 正常文本 ≥ 4.5:1，大文本 ≥ 3:1 |
| 7 | 地标元素 | `<header>`, `<nav>`, `<main>`, `<footer>` 使用正确 | 无裸 `<div class="header">` |

---

## 新增功能检查项（通用）

> 以下检查项由运行时 Agent 执行，需输出明确的 PASS/FAIL 判定。

### 1. 暗黑模式功能正常

| 子项 | 检测命令 / 方法 | 通过标准 |
|------|----------------|----------|
| Toggle 存在 | `grep -rn "theme-toggle\|dark.*toggle\|ThemeToggle" src/ --include="*.astro"` | 至少一处 |
| localStorage 持久化 | 人工验证：切暗色 → 刷新 → 仍为暗色 | 状态保持 |
| 无 FOUC | Playwright 截图首帧 / 人工刷新观察 | 无可见闪烁 |
| meta theme-color 同步 | `grep -rn "theme-color" src/ --include="*.astro"` | 暗色/亮色分别对应 `#111827` / `#ffffff`（或项目定义值） |
| 系统偏好监听 | `grep -rn "matchMedia.*prefers-color-scheme" src/` | 存在且正确处理（可选） |

**修复指引**：
- Toggle 使用 `data-action="theme-toggle"` + 事件委托，禁止 `__xxxDelegated` 守卫
- 主题脚本允许 `is:inline`（唯一例外：FOUC 防护脚本）
- `theme-color` meta 标签必须与当前主题同步更新

### 2. 中英文切换功能正常

| 子项 | 检测命令 / 方法 | 通过标准 |
|------|----------------|----------|
| Lang switcher 存在 | `grep -rn "lang.*switch\|lang.*toggle\|language.*switch" src/ --include="*.astro" -i` 或组件名匹配 | 至少一处 |
| 路由结构 | `ls src/pages/[lang]/` 或 `astro.config.mjs` i18n 配置 | 存在 `/zh/` 或等效中文路由 |
| URL 构建规范 | `grep -rn 'getRelativeLocaleUrl' src/ --include="*.astro" --include="*.ts"` | 所有跨语言链接使用 `getRelativeLocaleUrl(locale, path)`，禁止字符串拼接 `${BASE_URL}` |
| 内容对等 | `diff <(jq 'keys' src/content/homepage/en.json) <(jq 'keys' src/content/homepage/zh.json)` | 键集合一致（允许顺序不同） |
| 切换后页面可用 | Playwright / 人工点击验证 | 切换语言后当前页面有对应翻译版本，无 404 |

**修复指引**：
- 字符串拼接 URL → `getRelativeLocaleUrl`
- 缺失翻译键 → 同步补充 `en.json` / `zh.json`
- 条件渲染 `lang === 'zh' ? '中文' : 'English'` → 统一使用 `t('key')`

### 3. 学术资产已库化

| 子项 | 检测命令 / 方法 | 通过标准 |
|------|----------------|----------|
| 无本地 paper 目录 | `ls src/assets/paper/ public/paper/ public/assets/images/*.png 2>/dev/null` | 不存在（或为空） |
| 无本地学术图片 import | `grep -rn "from.*assets.*paper\|from.*assets.*images" src/ --include="*.astro" --include="*.ts"` | 无结果 |
| CDN 引用正确 | `grep -rn "cdn.jsdelivr.net/gh/mykcs/academic" src/ public/ --include="*.astro" --include="*.html" --include="*.ts"` | 所有学术图片使用该前缀 |
| 混合引用标记 | `grep -rn "vendor/academic" src/ --include="*.astro" --include="*.ts"` | 若存在，标记为 INFO（主站允许构建时 import，项目页必须全 CDN） |

**修复指引**：
- 本地图片迁移到 `mykcs/academic` 仓库 `images/` 目录
- 引用路径统一替换为 `https://cdn.jsdelivr.net/gh/mykcs/academic@main/images/<filename>`
- 主站混合模式（`vendor/academic` 构建时 import + `image-map.json` 运行时 URL）可保留，但需确认 `vendor/academic` submodule 已更新

### 4. 显示正常（无布局溢出、无 FOUC）

| 子项 | 检测命令 / 方法 | 通过标准 |
|------|----------------|----------|
| 构建产物存在 | `ls dist/` | 成功生成 |
| 无全局 CSS 缺失 | `grep -r "@tailwindcss" dist/ || grep -r 'class="[^"]*bg-[^"]*"' dist/ | head -5` | Tailwind utility 已打入 |
| 无布局溢出 | Playwright 全页截图 + 人工检查 / 或 `document.documentElement.scrollWidth === window.innerWidth` | 无水平滚动条 |
| 无 FOUC | Playwright 首帧截图：字体、颜色、布局无可见跳变 | 首帧即最终样式 |
| 响应式验证 | Playwright 375px / 768px / 1440px 三端截图 | 无元素重叠、截断、错位 |

**修复指引**：
- FOUC → 检查 CSS 是否内联到 `<head>`；Tailwind v4 + Vite 需确认 `global.css` 被正确导入
- 溢出 → 检查 `vw` 单位、fixed 定位元素、未换行长文本
- 响应式 → 检查 `max-w-*`、`overflow-x-hidden`、图片 `max-width: 100%`

### 5. 功能正常（交互元素可点击、无 JS 错误）

| 子项 | 检测命令 / 方法 | 通过标准 |
|------|----------------|----------|
| 控制台无报错 | Playwright `page.on('pageerror', ...)` / 人工 DevTools Console | 0 error（warning 不计） |
| 主题 toggle 可点击 | Playwright 点击 + 截图对比 | body class 变化 / 样式切换 |
| 语言切换可点击 | Playwright 点击 + URL 断言 | 路由跳转正确 |
| 外部链接有效 | `grep -rn 'href="http' src/ --include="*.astro"` → 抽样 `curl -I` | HTTP 200 / 301 / 302 |
| 打印功能（如有） | 人工 `Ctrl+P` 或 Playwright `page.pdf()` | 布局完整、无截断 |

**修复指引**：
- JS 错误 → 按堆栈定位修复；常见：null 引用、重复事件监听、未定义变量
- 点击无响应 → 检查事件委托绑定、`data-action` 属性、`<a>` 标签 `href`
- 外部 404 → 更新链接或移除

---

## 主站特定检查项（仅当检测到 homepage/CV/publications 时）

| Priority | Issue | Impact |
|----------|-------|--------|
| P1 | `papers` → `publications`, `honors` → `awards` (including cross-repo `mykcs/academic` submodule) | Terminology inconsistency |
| P1 | Missing `/en/cv/` English CV page | i18n 完整性 |
| P1 | `manifest.json` fixes (maskable icons, dynamic `theme_color`) | PWA compliance |
| P1 | Open Graph missing (`og:image`, `og:locale:alternate`) | Social sharing |
| P1 | CSS inline optimization (Critical CSS + font preloading) | FCP 性能 |
| P2 | Google Fonts CDN usage (should migrate to `@fontsource/*`) | Privacy + offline support |

---

## 学术项目页特定检查项（摘要）

> **完整检查项见 `academic-project-checklist.md`。以下为摘要。**

| Priority | Issue | Impact |
|----------|-------|--------|
| P0 | Poster 4 列 `scrollHeight === clientHeight`（无溢出） | 布局崩坏 |
| P0 | WebKit 兼容性（flex+grid+img 硬规则） | Safari/iOS 裁切 |
| P1 | KaTeX 公式渲染可用性 + 预渲染策略 | 内容可读性 |
| P1 | Slides zoom/print 控制功能正常 | 交互完整性 |
| P1 | DESIGN.md 存在且与代码一致 | 文档一致性 |
| P2 | 学术资产 `/academic/images/` 引用可用 | 外链健康 |

---

## Detection Commands

```bash
# === 项目类型检测 ===
[ -f "DESIGN.md" ] && echo "[DESIGN.md] found" || echo "[DESIGN.md] MISSING"
grep -l "Poster\|Slides" src/components/*.astro 2>/dev/null && echo "[Academic components] found" || echo "[Academic components] none"

# === 通用检查 ===
# 重复页面
ls src/pages/cv.astro src/pages/[lang]/cv.astro 2>/dev/null && echo "DUPLICATE_PAGES found" || echo "DUPLICATE_PAGES ok"

# 废弃 API
grep -rn "Astro.glob\|ViewTransitions" src/ --include="*.astro" && echo "DEPRECATED_API found" || echo "DEPRECATED_API ok"

# === 主站特定 ===
# 术语一致性（仅在主站执行）
grep -rn "papers\|honors" src/ content/ --include="*.json" --include="*.ts" --include="*.astro" && echo "LEGACY_TERMS found" || echo "LEGACY_TERMS ok"

# manifest.json 健康
cat public/manifest.json 2>/dev/null | jq '.icons[] | select(.purpose | contains("maskable") | not)' 2>/dev/null && echo "MASKABLE_ICONS missing" || echo "MASKABLE_ICONS ok"

# Open Graph
grep -rn 'og:image\|og:locale' src/layouts/ src/pages/ && echo "OG_TAGS found" || echo "OG_TAGS missing"

# Google Fonts CDN (should migrate to @fontsource)
grep -rn "fonts.googleapis.com\|fonts.gstatic.com" src/ public/ --include="*.astro" --include="*.css" && echo "GOOGLE_FONTS found" || echo "GOOGLE_FONTS ok"

# === a11y 快速脚本 ===
grep -rn "<img" src/ --include="*.astro" | grep -v "alt=" | grep -v "decorative" || echo "[a11y-alt] PASS"
grep -rn "<input" src/ --include="*.astro" | grep -v "aria-label\|aria-labelledby\|<label" || echo "[a11y-label] PASS"
grep -rn "outline: none\|outline:none" src/ --include="*.css" --include="*.astro" || echo "[a11y-focus] PASS"
find src/pages -name "*.astro" -exec sh -c 'count=$(grep -c "<h1" "$1"); [ "$count" -gt 1 ] && echo "$1: $count h1"' _ {} \; || echo "[a11y-h1] PASS"

# === 学术项目特定 ===
# 仅在 TYPE=academic-project 时执行，详见 academic-project-checklist.md
```
