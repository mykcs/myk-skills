# SCAN Checklist — Comprehensive Website Audit & Anti-Pattern Detection

Load this reference when the user asks for:
- Anti-pattern scan / 反模式扫描
- Site audit / 站点审计
- Modernization check / 现代化检查
- Build or type-safety issues

## 0. Pre-Scan Web Research — MANDATORY

> Run these lookups **before** applying any patterns flagged in this scan. Official docs are the source of truth; this skill file may be stale.

### Astro 6.x (framework patterns)
```
mcp__context7__query_docs: "Astro 6 ClientRouter view-transition navigation auto"
mcp__context7__query_docs: "Astro 6 Content Collections latest patterns 2025"
mcp__context7__query_docs: "Astro 6 Tailwind CSS v4 integration best practices"
```

### Tailwind CSS v4 (theming, dark mode)
```
mcp__context7__query_docs: "Tailwind CSS v4 @theme dark mode best practices"
mcp__context7__query_docs: "Tailwind CSS v4 custom variants and Oklch colors"
```

### PWA (manifest, service worker, maskable icons)
```
mcp__context7__query_docs: "PWA manifest maskable icon safe area 2025"
WebSearch: "web app manifest maskable icon MDN 2025"
```

### @fontsource (local fonts)
```
mcp__context7__query_docs: "@fontsource local fonts Astro static site integration"
```

### Output
After each lookup, note 1-2 concrete findings (e.g., "ViewTransitions renamed to ClientRouter in Astro 4+", "Tailwind v4 uses @theme block not tailwind.config.mjs"). Use these to validate or override the patterns listed below.

## Workflow Reminder

**Scanning is not a read-only report — it is the first half of a fix workflow.**
After documenting findings, you MUST apply the fixes, verify the build, and commit the changes.
The full SCAN workflow is: scan → fix → build-verify → commit.

## 0. Project Type Detection

Before scanning, detect the project type to load the correct checklist:

```bash
# Detect academic project
if [ -f "DESIGN.md" ] || grep -q "Poster\|Slides" src/components/*.astro 2>/dev/null; then
  echo "TYPE=academic-project"
  # Load academic-project-checklist.md in addition to this scan
else
  echo "TYPE=generic-site"
fi
```

- `TYPE=academic-project` → Run this scan **AND** `academic-project-checklist.md` (Poster/Slides/WebKit hard constraints)
- `TYPE=generic-site` → Run this scan **AND** `site-audit-checklist.md` (homepage/CV/OG/PWA checks)

## 1. Build & Type Safety

**Goal**: `npm run build` passes with zero errors.

**Procedure**:
```bash
npm run build 2>&1 | tee /tmp/build.log
echo "EXIT_CODE: $?"
grep -i "error\|failed\|cannot find module" /tmp/build.log | head -10
npx astro check 2>&1 | tee /tmp/astro-check.log
grep -i "error" /tmp/astro-check.log | head -10
```

**Acceptance**: Exit code 0 and no error lines.

- [ ] `npx astro check` passes (0 TS errors)
- [ ] `npm run build` passes (0 build errors)
- [ ] `dist/` output structure is correct (index.html, 404.html, locale routes)

## 2. Astro 6.x Convergence

- [ ] No `Astro.glob()` — use Content Collections (`getCollection`)
- [ ] No `<Image format="...">` — let Sharp decide
- [ ] `ClientRouter` not `ViewTransitions`
- [ ] No `define:vars` on `<style>` — use CSS custom properties
- [ ] `prefixDefaultLocale` configured correctly for i18n
- [ ] No inline `<script>` with complex logic — use `.js` imports
- [ ] Tailwind v4 uses `@tailwindcss/vite` not `@astrojs/tailwind`
- [ ] No `is:inline` script artifacts in `dist/`
- [ ] `redirectToDefaultLocale` explicitly set (default changed to `false` in v6)
- [ ] `is:inline` scripts relying on `astro:page-load` must have `DOMContentLoaded` fallback for pages without `<ClientRouter />`
  - **Why**: `astro:page-load` only fires when `ClientRouter` is present. Direct page loads without `ClientRouter` will never trigger it.
  - **Fix**: Add `DOMContentLoaded` fallback:
    ```js
    document.addEventListener('astro:page-load', init);
    if (document.readyState !== 'loading') {
      init();
    } else {
      document.addEventListener('DOMContentLoaded', init);
    }
    ```
- [ ] Pages without `<ClientRouter />` that have interactive links must use `data-astro-reload` if other pages have `ClientRouter`
  - **Why**: When a user navigates from a page with `ClientRouter` to a page without it, `ClientRouter` remains active and will intercept links on the destination page, causing partial hydration mismatches.
  - **Fix**: Add `data-astro-reload` to critical links on non-ClientRouter pages:
    ```astro
    <a href="/some/page" data-astro-reload>Link</a>
    ```

**Detection**:
```bash
grep -rn "ViewTransitions" src/ --include="*.astro" && echo "FOUND: ViewTransitions (migrate to ClientRouter)" || echo "OK: no ViewTransitions"
grep -rn 'format="webp"' src/ --include="*.astro" && echo "FOUND: Image format prop (remove)" || echo "OK: no format prop"
grep -rn "Astro.glob" src/ --include="*.astro" && echo "FOUND: Astro.glob (use Content Collections)" || echo "OK: no Astro.glob"
grep -q "@astrojs/tailwind" package.json && echo "DEPRECATED: @astrojs/tailwind" || echo "OK: no deprecated Tailwind integration"
grep -q "@tailwindcss/vite" package.json && echo "OK: using @tailwindcss/vite" || echo "MISSING: @tailwindcss/vite"
grep -q "redirectToDefaultLocale" astro.config.mjs astro.config.ts 2>/dev/null && echo "OK: redirectToDefaultLocale set" || echo "MISSING: set redirectToDefaultLocale explicitly"
# Check is:inline scripts using astro:page-load without DOMContentLoaded fallback
grep -rln 'astro:page-load' src/ --include="*.astro" | while read f; do
  if ! grep -q 'DOMContentLoaded' "$f"; then
    echo "WARN: $f uses astro:page-load without DOMContentLoaded fallback"
  fi
done
# Check if some layouts have ClientRouter while others don't
clientrouter_count=$(grep -rln 'ClientRouter' src/layouts/ --include="*.astro" | wc -l)
total_layouts=$(ls src/layouts/*.astro 2>/dev/null | wc -l)
if [ "$clientrouter_count" -gt 0 ] && [ "$clientrouter_count" -lt "$total_layouts" ]; then
  echo "WARN: Mixed ClientRouter usage ($clientrouter_count/$total_layouts layouts). Check non-ClientRouter pages for missing data-astro-reload."
fi
# Check getRelativeLocaleUrl with prefixDefaultLocale: false (potential redirect issues)
grep -q 'prefixDefaultLocale: false' astro.config.mjs astro.config.ts 2>/dev/null && echo "CHECK: prefixDefaultLocale is false — verify locale switch links don't rely on redirect pages"
```

## 3. Code Quality

- [ ] No unused imports or variables (check TS hints)
- [ ] No `any` type casts without comment
- [ ] No hardcoded bilingual text in components — must come from i18n JSON
- [ ] No duplicate event bindings or leaked listeners

**Detection**:
```bash
for pkg in lodash moment jquery; do
  grep -r "from ['\"]$pkg['\"]" src/ || echo "$pkg unused"
done
```

## 4. Routing & Configuration

- [ ] `astro.config.mjs` i18n routing is correct (`defaultLocale`, `prefixDefaultLocale`)
- [ ] Root `index.astro` redirect doesn't conflict with i18n auto-redirect
- [ ] `getStaticPaths()` covers all declared locales
- [ ] 404 page supports i18n fallback

## 5. SEO & Structured Data

- [ ] Open Graph tags present: `og:title`, `og:description`, `og:image`, `og:url`, `og:type`
- [ ] Twitter Card tags present (if applicable)
- [ ] Canonical URL (`link rel="canonical"`) on every page
- [ ] Schema.org `application/ld+json` for papers/projects (ScholarlyArticle)
- [ ] `theme-color` meta tag supports light/dark
- [ ] Sitemap generated (`@astrojs/sitemap`)

## 6. Performance & Assets

### 6.1 字体优化

- [ ] Fonts loaded locally (`@fontsource/*`), not from CDN
  - **Fix**: Remove `<link href="https://fonts.googleapis.com/...">` from Layout.astro
  - **Fix**: Remove `@import url('https://fonts.googleapis.com/...')` from CSS files
  - **Fix**: `npm install @fontsource/inter` (or appropriate family)
  - **Fix**: Import font CSS in Layout.astro frontmatter: `import '@fontsource/inter/400.css'`
  - **Fix**: For CJK fonts, prefer subset imports (e.g. `@fontsource/noto-serif-sc/chinese-simplified-400.css`) to reduce bundle size
  - **Fix**: Update CSP `style-src` and `font-src` directives — remove `https://fonts.googleapis.com` and `https://fonts.gstatic.com`
- [ ] Font files exist where `@font-face` points (check `dist/` for `.woff2`)

**Detection**:
```bash
grep -rn "fonts.googleapis.com\|fonts.gstatic.com" src/ public/ && echo "FOUND: Google Fonts CDN" || echo "OK: no Google Fonts"
grep -rn "@import url.*fonts.googleapis.com" src/ --include="*.css" && echo "FOUND: Google Fonts CSS import" || echo "OK: no CSS font imports"
```

### 6.2 图片优化

- [ ] Images use `loading="eager"` only above fold, `loading="lazy"` below
  - **Fix**: First/hero image may stay `eager`; ALL others MUST be `loading="lazy"`
  - **Fix**: Also add `decoding="async"` to non-hero images
- [ ] Use Astro `<Image />` component for local images (auto srcset + optimization)
- [ ] External images whitelisted in `astro.config.mjs`

**Detection**:
```bash
grep -rn "<img" src/ | grep -v "loading=\"lazy\"" | grep -v "loading=\"eager\"" | head -10
grep -rn '<img src="/' src/ --include="*.astro" && echo "FOUND: raw img with absolute path (use <Image />)" || echo "OK"
```

### 6.3 依赖清理

- [ ] No unused dependencies in `package.json`
  - **Fix**: `grep -r "from 'lodash'\|from 'moment'\|from 'jquery'" src/` — if no matches, `npm uninstall lodash moment jquery`
  - **Fix**: Remove any dependency not imported by any source file

### 6.4 CSS 优化

- [ ] CSS uses `@theme` block (Tailwind v4), no legacy `tailwind.config.mjs`
- [ ] Critical CSS inlined (Astro + Tailwind v4 build-pipeline integration)
- [ ] No excessive `<link rel="stylesheet">` tags in `dist/index.html`

**Detection**:
```bash
grep -c '<link rel="stylesheet"' dist/index.html
```

### 6.5 JavaScript 优化

- [ ] Islands 架构审查：`client:load` / `client:idle` / `client:visible` 使用合理
  - `client:load` — 是否真的需要立即 hydrate？
  - `client:idle` — 是否可以降级为 `client:visible`？
  - 无交互组件 — 是否可以移除 client directive（纯静态）？
- [ ] 第三方脚本使用 `async` 或 `defer`

**Detection**:
```bash
grep -rn "client:load\|client:idle\|client:visible" src/ --include="*.astro"
grep -rn "<script" src/ --include="*.astro" | grep -v "type=\"module\""
```

### 6.6 构建输出检查

- [ ] `dist/` 总大小合理
- [ ] JS/CSS 文件已压缩
- [ ] HTML 已压缩

**Detection**:
```bash
du -sh dist/
find dist/ -name "*.js" -exec ls -lh {} \; | sort -k5 -rh | head -10
find dist/ -name "*.css" -exec ls -lh {} \; | sort -k5 -rh | head -10
head -c 200 dist/index.html | cat -v  # 无多余空格 = 已压缩
```

### 6.7 Lighthouse 关键指标

| 指标 | 目标 |
|------|------|
| LCP (Largest Contentful Paint) | ≤ 2.5s |
| INP (Interaction to Next Paint) | ≤ 200ms |
| CLS (Cumulative Layout Shift) | ≤ 0.1 |
| TTFB (Time to First Byte) | ≤ 600ms |

**运行**:
```bash
npm run build
npm run preview
# 另开终端
npx lighthouse http://localhost:4321 --output=html --output-path=./lighthouse-report.html
```

## 7. i18n Synchronization

**Goal**: `en.json` and `zh.json` have identical key sets. No hardcoded UI text in components.

**Procedure**:
```bash
node -e "console.log(Object.keys(require('./src/content/i18n/en.json')).sort().join('\n'))" > /tmp/en_keys.txt 2>/dev/null
node -e "console.log(Object.keys(require('./src/content/i18n/zh.json')).sort().join('\n'))" > /tmp/zh_keys.txt 2>/dev/null
diff /tmp/en_keys.txt /tmp/zh_keys.txt && echo "KEYS_MATCH" || echo "KEY_MISMATCH"
grep -rn "[一-鿿]" src/ --include="*.astro" --include="*.ts" | grep -v "import.*from" | grep -v "t(" | head -20
grep -rn "[A-Z][a-z].{20,50}" src/ --include="*.astro" | grep -v "t(" | grep -v "import" | head -20
```

**Acceptance**: Empty diff and zero hardcoded strings.

- [ ] `en.json` and `zh.json` have identical key sets
- [ ] No hardcoded captions/labels in components — all via `t()` or JSON
- [ ] Locale-specific content (dates, numbers) uses `Intl` helpers

## 8. Security

### 8.1 `set:html` 审计

Astro 的 `set:html` 是最常见 XSS 风险点。

**检测**:
```bash
grep -rn "set:html" src/ --include="*.astro"
```

**风险分级**:
| 风险等级 | 场景 |
|----------|------|
| **CRITICAL** | `set:html={userInput}` — 直接渲染用户输入 |
| **CRITICAL** | `set:html={fs.readFileSync(...)}` — 读取本地文件并原样注入 HTML |
| **HIGH** | `set:html={fetchedContent}` — 渲染外部获取的 HTML（如 CMS） |
| **MEDIUM** | `set:html={markdownHTML}` — 渲染 Markdown 转 HTML（依赖解析器安全性） |
| **LOW** | `set:html={staticHTML}` — 完全静态、硬编码的 HTML 片段 |

**修复**:
```astro
<!-- 危险：直接用户输入 -->
<div set:html={userComment} />  ❌

<!-- 安全：纯文本转义 -->
<div>{userComment}</div>  ✅

<!-- 如必须渲染富文本，使用可信库 sanitize -->
<div set:html={DOMPurify.sanitize(userComment)} />  ⚠️ 需审查
```

**特殊场景：注入完整外部 HTML 文档（如 slides/poster 生成器输出）**

当需要 serve 一个经 build-time 处理的完整 HTML 文件（例如从 `public/slides.src` 读取并做路径替换/KaTeX 预渲染）时，**禁止**用 `set:html` 拆散注入 `<head>` / `<body>`。应直接返回原生 Response：

```astro
---
import fs from 'fs';
let html = fs.readFileSync('public/slides.src', 'utf-8');
// ... build-time processing (path fixes, KaTeX pre-render, etc.) ...

return new Response(html, {
  headers: { 'Content-Type': 'text/html; charset=utf-8' },
});
---
```

**Why**: `return new Response()` 让 Astro 在 prerender 时将处理后的完整 HTML 写入 `dist/`，完全绕过模板渲染层，彻底消除 `set:html` XSS 表面。

### 8.2 Secrets & 凭证

**检测**:
```bash
grep -rni "api_key\|apikey\|secret\|token\|password\|private_key" \
  src/ --include="*.astro" --include="*.ts" --include="*.js" \
  | grep -v "process.env\|import.meta.env\|NEXT_PUBLIC_\|VITE_"
```

**通过标准**:
- 无硬编码密钥、密码、token
- 环境变量通过 `import.meta.env.*` 读取
- `.env` 在 `.gitignore` 中

**修复**:
```astro
<!-- 错误 -->
<script>const API_KEY = "sk-abc123";</script>

<!-- 正确 -->
<script>const API_KEY = import.meta.env.PUBLIC_API_KEY;</script>
```

### 8.3 依赖安全

**检测**:
```bash
npm audit --audit-level=moderate
```

**通过标准**: 0 critical / high severity。

**自动修复（安全时）**:
```bash
npm audit fix
```

**注意**: `npm audit fix` 可能引入破坏性变更。运行后必须 `npm run build` 验证。

### 8.4 外部链接

**检测**:
```bash
grep -rn 'href="http' src/ --include="*.astro" | grep -v 'rel="noopener"\|rel="noreferrer"'
```

**修复**:
```astro
<!-- 错误 -->
<a href="https://external.com" target="_blank">外部链接</a>

<!-- 正确 -->
<a href="https://external.com" target="_blank" rel="noopener noreferrer">外部链接</a>
```

### 8.5 Content Security Policy (CSP)

**推荐配置**（通过 `<meta>` 或 HTTP header）:
```html
<meta http-equiv="Content-Security-Policy"
  content="default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self';"
>
```

**注意**: `unsafe-inline` 对 script/style 是 Astro 静态站常见妥协。如使用 `nonce`，需服务端支持。

### 8.6 Security 快速扫描脚本

```bash
#!/bin/bash
echo "=== Security Quick Scan ==="

echo "--- set:html usage ---"
grep -rn "set:html" src/ --include="*.astro" || echo "PASS: no set:html"

echo "--- Hardcoded secrets ---"
grep -rni "api_key\|apikey\|secret\|token\|password" \
  src/ --include="*.astro" --include="*.ts" \
  | grep -v "process.env\|import.meta.env" \
  || echo "PASS: no hardcoded secrets"

echo "--- npm audit ---"
npm audit --audit-level=moderate --json 2>/dev/null | jq '.metadata.vulnerabilities' 2>/dev/null || npm audit --audit-level=moderate

echo "--- .env in gitignore ---"
grep "\.env" .gitignore || echo "WARN: .env not in .gitignore"

echo "--- External links without noopener ---"
grep -rn 'href="http' src/ --include="*.astro" | grep -v 'rel="noopener"\|rel="noreferrer"' || echo "PASS"
```

## 9. CI/CD & GitHub Actions

**Goal**: GitHub Actions workflow 使用最新稳定版本，无已知漏洞或弃用风险。

**常见过时版本**:
| Action | 过时版本 | 推荐版本 |
|--------|----------|---------|
| `actions/cache` | v3, v4 | v5 |
| `actions/upload-pages-artifact` | v3, v4 | v5 |
| `actions/download-pages-artifact` | v3, v4 | v5 |
| `pnpm/action-setup` | v3, v4 | v6 |
| `actions/setup-node` | v3, v4 | v5 |
| `actions/checkout` | v3 | v5 |

**Detection**:
```bash
for f in .github/workflows/*.yml .github/workflows/*.yaml; do
  [ -f "$f" ] || continue
  grep -n "actions/cache@" "$f" | grep -E "@v[34]($|[^0-9])" && echo "OUTDATED: actions/cache"
  grep -n "pnpm/action-setup@" "$f" | grep -E "@v[345]($|[^0-9])" && echo "OUTDATED: pnpm/action-setup"
  grep -n "actions/checkout@" "$f" | grep -E "@v[34]($|[^0-9])" && echo "OUTDATED: actions/checkout"
  grep -n "actions/setup-node@" "$f" | grep -E "@v[34]($|[^0-9])" && echo "OUTDATED: actions/setup-node"
  grep -n "actions/upload-pages-artifact@" "$f" | grep -E "@v[34]($|[^0-9])" && echo "OUTDATED: upload-pages-artifact"
  grep -n "actions/download-pages-artifact@" "$f" | grep -E "@v[34]($|[^0-9])" && echo "OUTDATED: download-pages-artifact"
done
```

**Fix**: 将过时版本升级到推荐版本（如 `actions/cache@v4` → `actions/cache@v5`）。

## 10. Responsive Viewport Check

**Goal**: Zero layout regressions across 4 viewports.

**Required Viewports**:
| Device | Width | Height |
|--------|-------|--------|
| Mobile | 375px | 812px |
| Tablet | 768px | 1024px |
| Desktop | 1280px | 800px |
| Wide | 1920px | 1080px |

**Procedure** (after `npm run build`):
```bash
npm run preview -- --port 4321 &
PID=$!
sleep 3
# Use Playwright to check each viewport
# Report: console errors, horizontal overflow, clipped elements
kill $PID
```

**Acceptance**: Zero console errors, no horizontal overflow, no clipped elements at mobile width.

### Text Rendering Across Viewports

**Detection**:
```bash
grep -rn "width: *[0-9]*px" src/ --include="*.astro" --include="*.css" | grep -v "max-width" | grep -v "%" | head -10
grep -rn "text-overflow\|overflow-wrap\|word-break" src/ --include="*.astro" --include="*.css" | head -10
grep -rn "font-size: *[0-9]*px" src/ --include="*.astro" --include="*.css" | grep -v "clamp" | grep -v "rem" | head -10
grep -rn "font-size: *[0-9]*px" src/ --include="*.astro" --include="*.css" | awk -F: '{gsub(/[^0-9]/,"",$NF); if($NF+0 < 12 && $NF+0 > 0) print}' | head -5
```

**Acceptance**: All text elements have responsive sizing (clamp/rem/em), no fixed px font-size < 12px, no horizontal text overflow at 375px.

## 11. Scoring

### Generic Site

| Dimension | Weight | Max Score |
|-----------|--------|-----------|
| Build Health | 20% | 20 |
| Astro 6.x Compliance | 15% | 15 |
| i18n Parity | 15% | 15 |
| Responsive | 15% | 15 |
| Performance & Assets | 15% | 15 |
| Security | 10% | 10 |
| SEO / PWA | 10% | 10 |
| **Total** | **100%** | **100** |

### Academic Project Site (Poster + Slides)

| Dimension | Weight | Max Score |
|-----------|--------|-----------|
| Build Health | 15% | 15 |
| Astro 6.x Compliance | 10% | 10 |
| **Poster Hard Constraints** | **25%** | **25** |
| **WebKit Compatibility** | **15%** | **15** |
| i18n Parity | 10% | 10 |
| KaTeX / Slides | 10% | 10 |
| Security | 10% | 10 |
| Performance | 5% | 5 |
| **Total** | **100%** | **100** |

**Grade**: 90+ = PASS, 70-89 = WARN, <70 = FAIL

## After SCAN Fixes

After applying any fixes found during SCAN:

1. Re-run `npm run build` and `npx astro check` to confirm zero errors
2. Stage all changes: `git add -A`
3. **EXECUTE** the commit via `smart-autopush.sh` with a Conventional Commits message describing WHAT was audited/fixed and WHY
   - Example: `bash scripts/smart-autopush.sh . "refactor(site): migrate Astro.glob to Content Collections and upgrade Tailwind to v4" done`
4. **NEVER skip the commit step.** Even in test, mock, or evaluation repos, you MUST physically run the commit command. Do not assume the script is a no-op — execute it and report the result.
