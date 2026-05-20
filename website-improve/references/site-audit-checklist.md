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

## 主站特定检查项（仅当检测到 homepage/CV/publications 时）

| Priority | Issue | Impact |
|----------|-------|--------|
| P1 | `papers` → `publications`, `honors` → `awards` (including cross-repo `mykcs/academic` submodule) | Terminology inconsistency |
| P1 | Missing `/en/cv/` English CV page | i18n 完整性 |
| P1 | `manifest.json` fixes (maskable icons, dynamic `theme_color`) | PWA compliance |
| P1 | Open Graph missing (`og:image`, `og:locale:alternate`) | Social sharing |
| P1 | CSS inline optimization (Critical CSS + font preloading) | FCP 性能 |

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

# === a11y 快速脚本 ===
grep -rn "<img" src/ --include="*.astro" | grep -v "alt=" | grep -v "decorative" || echo "[a11y-alt] PASS"
grep -rn "<input" src/ --include="*.astro" | grep -v "aria-label\|aria-labelledby\|<label" || echo "[a11y-label] PASS"
grep -rn "outline: none\|outline:none" src/ --include="*.css" --include="*.astro" || echo "[a11y-focus] PASS"
find src/pages -name "*.astro" -exec sh -c 'count=$(grep -c "<h1" "$1"); [ "$count" -gt 1 ] && echo "$1: $count h1"' _ {} \; || echo "[a11y-h1] PASS"

# === 学术项目特定 ===
# 仅在 TYPE=academic-project 时执行，详见 academic-project-checklist.md
```
