# SCAN Checklist — Comprehensive Website Audit & Anti-Pattern Detection

> 此文件是 website-improve skill 的详细检查参考手册。
> 每个 Agent 在 SKILL.md 中有对应章节索引（§1 = Agent-Check-Build，§2 = Agent-Check-Buttons 等）。

## Pre-Scan Research — MANDATORY

> 在应用任何模式之前，先查官方文档确认当前最佳实践。此文件可能有过期内容。

```
mcp__context7__query_docs: "Astro 6 ClientRouter view-transition navigation auto"
mcp__context7__query_docs: "Astro 6 Content Collections latest patterns 2025"
mcp__context7__query_docs: "Astro 6 Tailwind CSS v4 integration best practices"
mcp__context7__query_docs: "Tailwind CSS v4 @theme dark mode best practices"
mcp__context7__query_docs: "Tailwind CSS v4 custom variants and Oklch colors"
mcp__context7__query_docs: "PWA manifest maskable icon safe area 2025"
mcp__context7__query_docs: "@fontsource local fonts Astro static site integration"
```

---

## §1. Agent-Check-Build — 构建与类型安全

**对应 Agent**: Agent-Check-Build

**Goal**: `npm run build` passes with zero errors.

```bash
npm run build 2>&1 | tee /tmp/build.log; echo "EXIT_CODE: $?"
grep -i "error\|failed\|cannot find module" /tmp/build.log | head -10
npx astro check 2>&1 | tee /tmp/astro-check.log
grep -i "error" /tmp/astro-check.log | head -10
```

- [ ] `npx astro check` passes (0 TS errors)
- [ ] `npm run build` passes (0 build errors)
- [ ] `dist/` output structure is correct (index.html, 404.html, locale routes exist at expected paths)
- [ ] **i18n switch URLs in built HTML 指向实际存在的文件**（见 §9.1）
- [ ] GitHub Actions 最近 3 次运行全部 success
- [ ] 无 Node.js 20 弃用警告（`actions/cache@v4`、`pnpm/action-setup@v4/v5` 需升级）
- [ ] `.github/workflows/*.yml` 使用推荐版本（checkout@v6, setup-node@v5, upload-pages-artifact@v5）

---

## §2. Agent-Check-Buttons — 按钮功能完整性

**对应 Agent**: Agent-Check-Buttons

> **按钮功能损坏是最隐蔽的 bug**，用户必须点击才能发现错误。

### §2.1 `[data-action]` 事件委托按钮

```bash
# 收集所有 data-action 值
grep -rhn 'data-action=' src/ --include="*.astro" | grep -o 'data-action="[^"]*"'

# 收集所有事件监听器
grep -rhn "data-action\|closest\(" src/ --include="*.astro" | grep -E "addEventListener|closest"
```

**常见失败**：监听器处理 `[data-action="print-cv"]` 但按钮是 `data-action="export-pdf"`

### §2.2 下载链接文件存在性

```bash
# 列出所有指向 public/ 内文件的链接
grep -rhn 'href="/[^"]*\.\(pdf\|html\|png\|jpg\|svg\|zip\)"' src/ --include="*.astro"

# 验证文件存在（public/ 在 build 时复制到 dist/）
for path in $(grep -roh 'href="/[^"]*\.\(pdf\|html\)"' src/ --include="*.astro" | sed 's/href="//;s/"$//'); do
  if [ ! -f "public/$path" ]; then
    echo "MISSING: public/$path"
  else
    echo "OK: public/$path"
  fi
done
```

**常见失败**：href 指向 `/cv/cv-zh.pdf` 但文件不存在（404）

### §2.3 `<button onclick>` 函数定义

```bash
grep -rhn 'onclick=' src/ --include="*.astro" | grep -oE 'onclick="[^"]+' | sed 's/onclick="//'
# 验证函数是否在同文件 <script> 或 import 的 .js 中定义
```

**常见失败**：`onclick="downloadPDF()"` 但函数未定义

### §2.4 外部链接状态

```bash
grep -ro 'href="https://[^"]*"' src/ --include="*.astro" | sed 's/href="//;s/"$//' | sort -u | while read url; do
  status=$(curl -sI -o /dev/null -w "%{http_code}" "$url")
  [ "$status" = "200" ] || [ "$status" = "301" ] || [ "$status" = "302" ] && echo "OK $status: $url" || echo "BROKEN $status: $url"
done
```

### §2.5 锚点链接目标

```bash
grep -ro 'href="#[^"]*"' src/ --include="*.astro" | sed 's/href="//;s/"$//' | sort -u
# 在对应页面检查 id 是否存在
```

### §2.6 导航/切换按钮 URL 验证（CRITICAL）

> **最隐蔽的按钮 bug**：按钮存在、处理器正常，但 href 指向不存在的路径。build 成功、astro check 通过，但用户点击无效。
> 典型场景：语言切换、页面跳转按钮。

```bash
# 构建（必须先 build 才能检查 dist）
npm run build > /dev/null 2>&1

# 扫描 dist/**/*.html 中的 href（排除外部链接和静态资源）
node -e "
const fs = require('fs');
const path = require('path');
const glob = require('glob');

const files = glob.sync('dist/**/*.html');
const results = [];

files.forEach(f => {
  const content = fs.readFileSync(f, 'utf-8');
  // 匹配渲染后的 HTML 中的 href 属性（literal quote 包裹的路径）
  const hrefRegex = /href=\"([^\"]+)\"/g;
  let m;
  while ((m = hrefRegex.exec(content)) !== null) {
    const href = m[1];
    // 排除外部链接、特殊协议、锚点、静态资源文件
    if (
      href.startsWith('http') ||
      href.startsWith('//') ||
      href.startsWith('mailto:') ||
      href.startsWith('tel:') ||
      href.startsWith('#') ||
      href.match(/\.[a-z]{2,4}$/)
    ) continue;
    results.push({ file: f.replace('dist/', ''), href });
  }
});

console.log(JSON.stringify(results));
" > /tmp/button_hrefs.json

# 验证每个 href 在 dist 中实际存在
node -e "
const fs = require('fs');
const data = JSON.parse(fs.readFileSync('/tmp/button_hrefs.json', 'utf-8'));
const dist = process.cwd() + '/dist';
let broken = [];

data.forEach(({ file, href }) => {
  const clean = href.replace(/\\/\$/, '');
  const candidates = [
    dist + clean,
    dist + clean + '/index.html'
  ];
  const exists = candidates.some(c => fs.existsSync(c));
  if (!exists) {
    broken.push('BROKEN: ' + file + ' -> ' + href + ' (NOT FOUND in dist)');
  }
});

if (broken.length) {
  console.log('=== BROKEN NAV BUTTON HREFS ===');
  broken.forEach(b => console.log(b));
  process.exit(1);
} else {
  console.log('All nav button URLs OK: ' + data.length + ' checked');
}
"
```

**常见失败**：
- 语言切换 `<a href="/cv/">` 但 dist 中 `/cv/` 不存在（实际在 `/en/cv/`）
- 导航链接 `<a href="/projects">` 少了 trailing slash，dist 中只有 `/projects/index.html`
- i18n `getRelativeLocaleUrl` 返回无前缀路径如 `/cv/`，但实际 build 在 `/en/cv/` 和 `/zh/cv/`

**Acceptance**：所有带 href 的导航按钮/链接，href 在 dist 中对应文件或目录存在。

### 报告模板

```json
{
  "data_action_buttons": [{ "file": "", "action": "", "handler_found": true|false }],
  "download_links": [{ "file": "", "href": "", "exists": true|false }],
  "external_links": [{ "file": "", "href": "", "status": 200 }],
  "onclick_functions": [],
  "anchor_links": [],
  "nav_button_urls": [{ "file": "", "href": "", "exists": true|false }]
}
```

**Acceptance**：所有 data-action 有监听器、所有下载文件存在、所有 onclick 函数已定义、所有外部链接返回 200/301/302、所有锚点目标存在、所有导航按钮 URL 在 dist 中存在。

---

## §3. Agent-Check-CodeQuality — GitHub 高星模板对照

**对应 Agent**: Agent-Check-CodeQuality

> 用 GitHub 高星 Astro 个人站点作为参照系，对比当前站点的代码质量差距。

### 参考模板

| 仓库 | Stars | 核心参考价值 |
|------|-------|------------|
| `maxpou/maxpou.fr` | 11+ | ThemeToggle 模式、Dark mode CSS 变体、print CSS |
| `lowmess/lowmess.com` | 224+ | `@media print` 完整 CSS、nav/footer 隐藏、黑色文字打印 |
| `siduck/quickcv` | 238+ | `window.print()` 流程、PDF 生成按钮 |
| `goulvenclech/goulven-clech.dev` | 7+ | PrintButton 组件拆分 |
| `ArielFalcon/portfolio` | 50+ | `print:hidden` Tailwind 工具类 |

### 对比维度

**1. 组件行数**：单组件是否 ≤ 300 行？
```bash
for f in src/components/*.astro src/layouts/*.astro; do
  lines=$(wc -l < "$f")
  [ "$lines" -gt 300 ] && echo "LARGE: $f ($lines lines)"
done
```

**2. 事件处理模式**：是否使用事件委托而非大量 inline onclick？
```bash
inline=$(grep -c "onclick=" src/ --include="*.astro" -r || true)
delegated=$(grep -c "addEventListener.*closest" src/ --include="*.astro" -r || true)
echo "Inline onclick: $inline, Delegated: $delegated"
```

**3. Dark mode 实现**：是否在 `<html>` 上切换 class？
```bash
grep -n "classList.toggle\|classList.add.*dark" src/ --include="*.astro" -r | head -5
```

**4. Print CSS**：是否有 `@media print` 块？
```bash
grep -c "@media print" src/ --include="*.astro" -r
grep -n "nav\|footer\|button" src/styles/*.css | grep "@media print" | head -10
```

**5. i18n 完整性**：是否所有文本通过翻译函数获取？
```bash
grep -rn "[一-鿿]" src/ --include="*.astro" | grep -v "t(" | grep -v "import" | head -10
```

### 质量评分

- **9-10**：组件 ≤ 300 行，事件委托，完整 print CSS，i18n 完整
- **7-8**：有少量 monolith 组件，print CSS 基本可用
- **5-6**：有大量 inline onclick，缺少 print CSS
- **<5**：架构混乱，需要重构

---

## §4. Agent-Check-Code — 反模式与安全检查

**对应 Agent**: Agent-Check-Code

### §4.1 Astro 6.x Convergence

- [ ] 无 `Astro.glob()` → 使用 Content Collections（`getCollection`）
- [ ] 无 `<Image format="...">` → 让 Sharp 自动决定
- [ ] `ClientRouter` 而非 `ViewTransitions`
- [ ] 无 `define:vars` on `<style>` → 使用 CSS 自定义属性
- [ ] `prefixDefaultLocale` 正确配置
- [ ] 无 inline `<script>` 复杂逻辑 → 使用 `.js` imports
- [ ] Tailwind v4 使用 `@tailwindcss/vite` 而非 `@astrojs/tailwind`
- [ ] 无 `is:inline` script 残留
- [ ] `redirectToDefaultLocale` 显式设置（v6 默认 false）
- [ ] `is:inline` 脚本使用 `astro:page-load` 时必须有 `DOMContentLoaded` fallback
- [ ] 无 ClientRouter 的页面如有交互链接，需加 `data-astro-reload`
- [ ] 强制亮色页面必须在 `astro:after-swap` 和 `astro:page-load` 两处都做 cleanup
- [ ] 强制亮色页面 ThemeToggle 必须在 init 和 click handler 两处移除 `.dark`
- [ ] 强制亮色页面按钮需要显式非透明背景（避免依赖 `dark:` 变体）
- [ ] locale 切换 URL 必须**验证指向实际存在的路径**（`prefixDefaultLocale: false` 时 `getRelativeLocaleUrl` 返回无前缀路径如 `/cv/`，需确认 dist 中 `/cv/` 或对应 locale 路径真实存在）
- [ ] `prefixDefaultLocale: false` 的 i18n 项目，**禁止盲目相信 `getRelativeLocaleUrl` 返回值**作为 switch URL

**Detection**:
```bash
grep -rn "ViewTransitions" src/ --include="*.astro" && echo "FOUND" || echo "OK"
grep -rn 'format="webp"' src/ --include="*.astro" && echo "FOUND" || echo "OK"
grep -rn "Astro.glob" src/ --include="*.astro" && echo "FOUND" || echo "OK"
grep -q "@astrojs/tailwind" package.json && echo "DEPRECATED" || echo "OK"
# astro:page-load without DOMContentLoaded fallback
grep -rln 'astro:page-load' src/ --include="*.astro" | while read f; do
  grep -q 'DOMContentLoaded' "$f" || echo "WARN: $f"
done
# Mixed ClientRouter usage
clientrouter_count=$(grep -rln 'ClientRouter' src/layouts/ --include="*.astro" | wc -l)
total_layouts=$(ls src/layouts/*.astro 2>/dev/null | wc -l)
[ "$clientrouter_count" -gt 0 ] && [ "$clientrouter_count" -lt "$total_layouts" ] && echo "WARN: mixed ClientRouter"
```

### §4.2 代码质量

- [ ] 无未使用的 imports 或变量
- [ ] 无 `any` 类型断言（无注释情况下）
- [ ] 组件中无非硬编码双语文本（必须来自 i18n JSON）
- [ ] 无重复事件绑定或泄漏监听器

```bash
for pkg in lodash moment jquery; do
  grep -r "from ['\"]$pkg['\"]" src/ || echo "$pkg unused"
done
```

### §4.3 安全 — set:html XSS

| 风险等级 | 场景 |
|----------|------|
| **CRITICAL** | `set:html={userInput}` — 直接渲染用户输入 |
| **CRITICAL** | `set:html={fs.readFileSync(...)}` — 读取本地文件并原样注入 |
| **HIGH** | `set:html={fetchedContent}` — 渲染外部 HTML |
| **MEDIUM** | `set:html={markdownHTML}` — 渲染 Markdown 转 HTML |
| **LOW** | `set:html={staticHTML}` — 完全静态硬编码 HTML |

```bash
grep -rn "set:html" src/ --include="*.astro"
```

### §4.4 安全 — Secrets

```bash
grep -rni "api_key\|apikey\|secret\|token\|password\|private_key" \
  src/ --include="*.astro" --include="*.ts" --include="*.js" \
  | grep -v "process.env\|import.meta.env\|NEXT_PUBLIC_\|VITE_"
```

### §4.5 安全 — 外部链接

```bash
grep -rn 'href="http' src/ --include="*.astro" | grep -v 'rel="noopener"\|rel="noreferrer"'
```

### §4.6 安全 — npm audit

```bash
npm audit --audit-level=moderate
# 通过标准：0 critical / high severity
```

---

## §5. Agent-Check-Content — SEO 与内容

**对应 Agent**: Agent-Check-Content

- [ ] `og:title`, `og:description`, `og:image`, `og:url`, `og:type` 完整
- [ ] Twitter Card tags（适用时）
- [ ] Canonical URL（每页）
- [ ] Schema.org `application/ld+json`（论文/项目用 ScholarlyArticle）
- [ ] `theme-color` meta tag 支持 light/dark
- [ ] Sitemap 生成（`@astrojs/sitemap`）
- [ ] en.json / zh.json 键值对等
- [ ] 无断链

```bash
node -e "console.log(Object.keys(require('./src/content/homepage/en.json')).sort().join('\n'))" > /tmp/en_keys.txt
node -e "console.log(Object.keys(require('./src/content/homepage/zh.json')).sort().join('\n'))" > /tmp/zh_keys.txt
diff /tmp/en_keys.txt /tmp/zh_keys.txt && echo "KEYS_MATCH" || echo "KEY_MISMATCH"
```

### §5.1 i18n Content Parity — 验证方法论（教训驱动）

**陷阱**：用 regex 提取 built HTML 文本做中英对比时，HTML 结构差异会导致误报。
例如：中英文 period 分别用 `<span>A</span><span>B</span>` 和 `<span>A - B</span>` 渲染相同文本，
`re.sub(r'<[^>]+>', ' ', html)` 会得到 `"A  B"` vs `"A - B"——但浏览器渲染完全一致。

**正确做法**：

1. **首选**：直接对比数据源 JSON — 从源数据验证，不依赖渲染结构
   ```python
   # 比较 JSON 源值，不比较 HTML 渲染文本
   with open('dist/en/cv/index.html') as f: en = f.read()
   with open('dist/zh/cv/index.html') as f: zh = f.read()
   # 不要 re.sub('<[^>]+>', ...) 提取文本做对比
   # 改为：直接提取 JSON 源数据中的值比较
   ```

2. **次选**：如果必须比较渲染结果，用 innerText 而非 regex
   ```javascript
   // Playwright 获取实际渲染文本
   await page.locator('.cv-page').innerText()
   ```

3. **禁止**：用 `re.sub(r'<[^>]+>', ' ', html)` 提取文本来对比中英文内容

**适用场景**：EN/ZH 双语页面的所有内容对比（CV、论文、About 等）

---

## §6. Agent-Check-Deps — 依赖检查

**对应 Agent**: Agent-Check-Deps

- [ ] 无未使用依赖：`zod`（空 collections）、`@fontsource/*`（无 import）、`@astrojs/compiler-rs`（未启用 rustCompiler）
- [ ] `@tailwindcss/postcss` → 已迁移到 `@tailwindcss/vite`
- [ ] `tailwind.config.mjs` + Tailwind v4 → v4 忽略此文件，主题写在 `global.css` 的 `@theme {}` 中
- [ ] `postcss.config.mjs` + Tailwind v4 + Vite → 已删除
- [ ] `@astrojs/tailwind` → 已迁移到 Tailwind v4 + `@tailwindcss/vite`

```bash
grep -q "@tailwindcss/vite" package.json && echo "OK" || echo "MISSING"
grep -q "tailwind.config.mjs" && echo "LEGACY (ignored by v4)"
```

---

## §7. Agent-Check-CV — CV 页面深度检查

**对应 Agent**: Agent-Check-CV

> **主站（mykcs.github.io）必须执行**。CSS specificity 冲突无法通过静态检查发现，必须 Playwright + `getComputedStyle` 验证。

```bash
# 1. Check CSS specificity
grep -n "\.cv-page.*cv-paper-author" src/styles/cv.css
grep -n "\.cv-paper-author" src/styles/cv.css | grep -v "\.cv-page"

# 2. Check conflicting rule
grep -n "\.cv-page.*text-text-secondary" src/styles/cv.css

# 3. Playwright verification (after build)
npm run preview -- --port 4321 &
sleep 3
node -e "
const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('http://127.0.0.1:4321/zh/cv/');
  const selfAuthor = await page.\$('.cv-paper-author-self');
  if (selfAuthor) console.log('Self:', await selfAuthor.evaluate(el => getComputedStyle(el).color));
  const otherAuthor = await page.\$('.cv-paper-author-other');
  if (otherAuthor) console.log('Other:', await otherAuthor.evaluate(el => getComputedStyle(el).color));
  await browser.close();
})();
"
```

**Acceptance**：
- `.cv-paper-author-self` → `rgb(0, 0, 0)` 或 `#000`
- `.cv-paper-author-other` → `rgb(136, 136, 136)` 或 `#888`
- `.cv-page .cv-paper-author-other` specificity ≥ `.cv-page .text-text-secondary`

**常见失败**：`.cv-paper-author-other { color: #888 }` 无 `.cv-page` 前缀 → 被 `.cv-page .text-text-secondary { color: #000 !important; }` 覆盖

---

## §8. Performance & Assets

### §8.1 字体优化

- [ ] Fonts 本地加载（`@fontsource/*`），不从 CDN
- [ ] Font 文件存在于 `@font-face` 指向的位置（检查 `dist/` 中的 `.woff2`）

```bash
grep -rn "fonts.googleapis.com\|fonts.gstatic.com" src/ public/ && echo "FOUND CDN" || echo "OK"
```

### §8.2 图片优化

- [ ] 首屏图片 `loading="eager"`，非首屏 `loading="lazy" decoding="async"`
- [ ] 本地图片使用 Astro `<Image />` 组件
- [ ] 外部图片已在 `astro.config.mjs` 中 whitelist

```bash
grep -rn "<img" src/ | grep -v "loading=\"lazy\"" | grep -v "loading=\"eager\"" | head -10
```

### §8.3 CSS 优化

- [ ] CSS 使用 `@theme` 块（Tailwind v4），无遗留 `tailwind.config.mjs`
- [ ] 关键 CSS 已内联（Astro + Tailwind v4 build-pipeline）
- [ ] `dist/index.html` 中无过多 `<link rel="stylesheet">` 标签

```bash
grep -c '<link rel="stylesheet"' dist/index.html
```

### §8.4 JavaScript 优化

- [ ] Islands 架构合理使用 `client:load` / `client:idle` / `client:visible`
- [ ] 第三方脚本使用 `async` 或 `defer`

```bash
grep -rn "client:load\|client:idle\|client:visible" src/ --include="*.astro"
```

### §8.5 构建输出

- [ ] `dist/` 总大小合理
- [ ] JS/CSS/HTML 已压缩

```bash
du -sh dist/
find dist/ -name "*.js" -exec ls -lh {} \; | sort -k5 -rh | head -10
```

---

## §9. Routing & Redirects

- [ ] `public/` 下无手写 HTML 重定向文件（用 `_redirects` 统一处理）
- [ ] `_redirects` 使用标准格式：`/source/*  /target/:splat  301`
- [ ] **i18n switch URL 不与 redirect 冲突**

### §9.1 i18n Switch URL 验证（CRITICAL for CV/i18n sites）

> `getRelativeLocaleUrl` 在 `prefixDefaultLocale: false` 时返回无前缀路径（如 `/cv/`），但实际页面可能构建在 `/en/cv/`、`/zh/cv/`。**build 成功不代表 switch URL 正确**。

```bash
# 1. 构建后，检查所有 locale switch href 是否指向实际存在的文件
BUILD_DIR="dist"
for locale in en zh; do
  for page in "" "cv" "slides"; do
    target="$BUILD_DIR/${locale}/${page}"
    if [ -d "$target" ] || [ -f "$target/index.html" ]; then
      # 找到了 locale 页面，检查其 switch URL
      index="$BUILD_DIR/${locale}/${page}/index.html"
      if [ -f "$index" ]; then
        switch_urls=$(grep -oPo 'href="[^"]*"(?=[^>]*data-astro-reload|切换语言|Switch Language)' "$index" 2>/dev/null | sed 's/href="//;s/"$//')
        for surl in $switch_urls; do
          # 解析相对路径 → 绝对路径
          abs_url=$(node -e "
            const u = new URL('$surl', 'https://example.com');
            console.log(u.pathname);
          ")
          target_file="$BUILD_DIR${abs_url}"
          if [ -f "$target_file" ] || [ -d "$target_file" ]; then
            echo "OK: $locale/${page} → $surl exists"
          else
            echo "BROKEN_SWITCH: $locale/${page} → $surl (NOT FOUND at $target_file)"
          fi
        done
      fi
    fi
  done
done
```

**常见失败**：
- `/zh/cv/` 的 switch URL 是 `/cv/`，但 `/cv/` 不存在（实际在 `/en/cv/`）
- `/cv/` 被 redirect 到 `/zh/cv`，导致切换按钮失效

**修复**：
- `prefixDefaultLocale: false` 时，`getRelativeLocaleUrl` 返回无前缀路径，**必须手动拼接实际路径**
- 正确做法：`const switchUrl = targetLang === 'en' ? '/en/cv/' : '/zh/cv/'`
- 禁止依赖 `getRelativeLocaleUrl` 返回值来判断实际 URL 结构

### §9.2 Redirect 冲突检测

```bash
# 检查 redirect 是否与 i18n switch URL 冲突
REDIRECTS_FILE="dist/_redirects"
if [ -f "$REDIRECTS_FILE" ]; then
  # 提取所有 redirect source 路径
  redirect_sources=$(grep -oE '^/[^ ]+' "$REDIRECTS_FILE" | sed 's/\*$//' | sort -u)
  # 提取所有 locale switch href
  switch_hrefs=$(grep -roh 'href="/[^"]*/"' dist/ --include="*.html" | grep -v "href=\"/_\|href=\"/fonts\|href=\"/images" | sed 's/href="//g;s/"$//' | sort -u)
  for href in $switch_hrefs; do
    for redir in $redirect_sources; do
      # 检查 redirect source 是否是 switch href 的前缀
      echo "$href" | grep -q "^$redir" && echo "CONFLICT: switch href=$href 被 redirect $redir 截断"
    done
  done
fi
```

**Acceptance**：所有 locale switch URL 指向 dist 中实际存在的文件；redirect 不截断 switch URL。

```bash
find public -name "*.html" -not -path "public/_astro/*" | while read f; do
  grep -q "http-equiv.*refresh\|window.location" "$f" && echo "REDIRECT_FILE: $f"
done
```

---

## §10. Responsive Viewport Check

**Goal**: 4 个 viewport 零布局回归。

| Device | Width | Height |
|--------|-------|--------|
| Mobile | 375px | 812px |
| Tablet | 768px | 1024px |
| Desktop | 1280px | 800px |
| Wide | 1920px | 1080px |

```bash
npm run preview -- --port 4321 &
sleep 3
# Playwright 检查每个 viewport
# 报告：console errors、水平溢出、被裁剪元素
kill $!
```

**Acceptance**：零 console error、无水平溢出、375px 宽度下无文字溢出。

---

## §11. CI/CD & GitHub Actions

**Goal**: workflow 使用最新稳定版本，消除所有 Annotations 警告。

| Action | 过时版本 | 推荐版本 |
|--------|----------|---------|
| `actions/cache` | v3, v4 | **v5** |
| `actions/upload-pages-artifact` | v3, v4 | **v5** |
| `actions/download-pages-artifact` | v3, v4 | **v5** |
| `pnpm/action-setup` | v3-v5 | **v6** |
| `actions/setup-node` | v3, v4 | v5 |
| `actions/checkout` | v3 | v5 |

```bash
for f in .github/workflows/*.yml .github/workflows/*.yaml; do
  [ -f "$f" ] || continue
  grep -n "actions/cache@" "$f" | grep -E "@v[34] " && echo "OUTDATED: $f"
  grep -n "pnpm/action-setup@" "$f" | grep -E "@v[345] " && echo "OUTDATED: $f"
done
grep -rn "FORCE_JAVASCRIPT_ACTIONS_TO_NODE24" .github/workflows/ && echo "WORKAROUND_FOUND" || echo "OK"
```

---

## §12. Academic Asset Library — 学术资产库化

> 适用于使用 `mykcs/academic` 管理学术图片的项目。

### 三阶段工作流

**阶段 1** — academic 仓库自动 tag：
- 添加 `.github/workflows/bump-version.yml`，每次 push 到 main 自动递增 patch tag
- 消费者统一引用：`cdn.jsdelivr.net/gh/mykcs/academic@<tag>/images/...`

**阶段 2** — 消费者项目迁移：
- 扫描本地学术资产：`grep -rn "academic/images" src/ public/`
- 替换 `@main` 或裸 `/academic/images/` 为带 tag 的 jsDelivr URL
- 删除本地副本

**阶段 3** — 统一路径管理模块：
```typescript
// src/constants/assets.ts
export const ACADEMIC_VERSION = 'v1.0.0';
export const ACADEMIC_BASE = `https://cdn.jsdelivr.net/gh/mykcs/academic@${ACADEMIC_VERSION}/images`;
export function academicImage(path: string): string {
  return `${ACADEMIC_BASE}/${path}`;
}
```

### 已知问题

1. **jsDelivr 新 tag 同步延迟**：刚 push 后访问 `@v1.0.0` 可能 502，改用短 commit hash（如 `@2d8a325`）立即可用
2. **Astro `<Image>` 需要 `remotePatterns`**：在 `astro.config.mjs` 中声明 `cdn.jsdelivr.net`
3. **构建时图片下载**：`npm run build` 时 Astro `<Image>` 会实际请求远程图片，URL 404/502 会直接报错中断 → build 通过 = 所有图片可访问

### 迁移检查清单

- [ ] `grep -rn "academic/images" src/ public/` 确认所有引用已迁移
- [ ] `vendor/academic` submodule 指向带 tag 的 commit
- [ ] `npm run build` 通过且 dist/ 无残留绝对路径

---

## §13. Scoring — 评分标准

### Generic Site

| Dimension | Weight | Max |
|-----------|--------|-----|
| Build Health | 20% | 20 |
| Astro 6.x Compliance | 15% | 15 |
| i18n Parity | 15% | 15 |
| Responsive | 15% | 15 |
| Performance & Assets | 15% | 15 |
| Security | 10% | 10 |
| SEO / PWA | 10% | 10 |
| **Total** | **100%** | **100** |

### Academic Project Site (Poster + Slides)

| Dimension | Weight | Max |
|-----------|--------|-----|
| Build Health | 15% | 15 |
| Astro 6.x Compliance | 10% | 10 |
| **Poster Hard Constraints** | **25%** | **25** |
| **WebKit Compatibility** | **15%** | **15** |
| i18n Parity | 10% | 10 |
| KaTeX / Slides | 10% | 10 |
| Security | 10% | 10 |
| Performance | 5% | 5 |
| **Total** | **100%** | **100** |

### Academic Personal Homepage (主站 with CV)

| Dimension | Weight | Max |
|-----------|--------|-----|
| Build Health | 15% | 15 |
| Astro 6.x Compliance | 10% | 10 |
| **CV Page Visual Rendering** | **20%** | **20** |
| **CSS Specificity Correctness** | **15%** | **15** |
| i18n Parity | 10% | 10 |
| Responsive | 10% | 10 |
| Performance & Assets | 10% | 10 |
| Security | 10% | 10 |
| **Total** | **100%** | **100** |

**Grade**: 90+ = PASS, 70-89 = WARN, <70 = FAIL

---

## Workflow Reminder

**SCAN 工作流**：scan → fix → build-verify → commit

1. 运行检查，记录问题清单
2. 应用修复
3. 重新 `npm run build` 和 `npx astro check` 确认零错误
4. `git add -A` → `smart-autopush.sh` 提交（描述审计/修复内容）
