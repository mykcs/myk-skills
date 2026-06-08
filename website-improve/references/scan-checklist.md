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
      href.includes('/#') ||
      href.match(/\.[a-z]{2,4}$/) ||
      href.startsWith('/osa/') ||
      href.startsWith('/GDKVM/')
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

### §2.7 hreflang 路径去重检查（Deja-Vu 防护）

> **触发历史**：2026-06-02 GDKVM (`Layout.astro:91-93`) 与 OSA (`Layout.astro:89-91`) **同一次三仓库审计中同时出现**同一类 bug — `new URL(\`/GDKVM/en${altPath}\`)` 把硬编码 base 与 `Astro.url.pathname` 已包含的 base 叠加，生成 `.../GDKVM/en/GDKVM/en/` 形式的 404 SEO 链接。

**检测脚本**（跑在 dist 上）：

```bash
# 抓所有 hreflang 链接，检查是否存在 base path 重复
node -e "
const fs = require('fs');
const path = require('path');
const glob = require('glob');

const BASE_PATTERNS = {
  mykcs: 'mykcs.github.io',
  gdkvm: 'GDKVM',
  osa: 'osa',
};

const files = glob.sync('dist/**/*.html');
const broken = [];

files.forEach(f => {
  const content = fs.readFileSync(f, 'utf-8');
  const re = /<link rel=\"alternate\" hreflang=\"[^\"]*\" href=\"([^\"]+)\"/g;
  let m;
  while ((m = re.exec(content)) !== null) {
    const url = m[1];
    Object.entries(BASE_PATTERNS).forEach(([repo, basePath]) => {
      // 检查 url 中是否出现 basePath 出现 ≥2 次（正常 1 次 = 在前缀位置）
      const matches = url.match(new RegExp(basePath.replace(/[.*+?^\${}()|[\\]\\\\]/g, '\\\\\$&'), 'g')) || [];
      if (matches.length > 1) {
        broken.push(\`\${f}: hreflang \${url} contains \${basePath} \${matches.length} times\`);
      }
    });
  }
});

if (broken.length) {
  console.log('=== HREFLANG BASE DUPLICATION ===');
  broken.forEach(b => console.log(b));
  process.exit(1);
} else {
  console.log('OK: no hreflang base duplication');
}
"
```

**推荐修复模式**（避免硬编码 base）：

```astro
{(() => {
  const baseUrl = import.meta.env.BASE_URL.replace(/\/$/, '');  // 'GDKVM' 或 'osa' 或 ''
  const altPath = Astro.url.pathname.replace(new RegExp(\`^\${baseUrl}/(en|zh)\`), '') || '/';
  return (
    <>
      <link rel=\"alternate\" hreflang=\"en\" href={new URL(\`\${baseUrl}/en\${altPath}\`, Astro.site).href} />
      <link rel=\"alternate\" hreflang=\"zh\" href={new URL(\`\${baseUrl}/zh\${altPath}\`, Astro.site).href} />
    </>
  );
})()}
```

**根因**：`Astro.url.pathname` 已包含 base 路径（如 `/GDKVM/en/poster/`），旧代码 `pathname.replace(/^\/(en|zh)/, '')` 只剥离 locale，**没有剥离 base**，再拼回 `/GDKVM/en${altPath}` 时就重复了。修复用 `import.meta.env.BASE_URL` 统一来源。

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

#### §4.6.1 已知限制 — yaml-language-server 中危（dev-only）

> 适用场景：`@astrojs/check` 传递依赖 `volar-service-yaml → yaml-language-server` 引入 5 个 medium Severity 漏洞。

**根因**：Astro 语言服务器（dev tooling）的传递依赖，非生产代码。

**通过标准**：
- 0 critical / high severity
- **medium severity 允许存在**（仅 devDependencies，不影响生产）
- CI 使用 `npm audit --audit-level=high` 或 `npm audit --omit=dev`

**修复路径**（优先级排序）：
1. **升级 `@astrojs/check`** — 问题已在 `@astrojs/language-server@2.16.5`（Volar services 0.0.70）中修复，升级到最新版即可消除警告
2. **CI 配置 `npm audit --omit=dev`** — 最简单正确做法，dev-only 漏洞不应出现在生产审计中（参考 Astro 官方 Issue #15303 + PR #15895）
3. **使用 `audit-ci --skip-dev`** — 需要细粒度控制时用此 wrapper

```bash
# CI 推荐：跳过 devDependencies 审计
npm audit --omit=dev

# 或：仅在高危时失败，medium 报告但不阻塞
npm audit --audit-level=high
```

**禁止**：为消除 dev-only medium 警告而移除 `@astrojs/check`（损失 TypeScript 类型检查）。

---

#### §4.6.2 已知限制 — set:html 渲染翻译文本中的 HTML（可接受）

> 适用场景：i18n 翻译 JSON 文件包含 `<strong>`、`<em>` 等 HTML 标签，使用 `set:html={t('key')}` 渲染。

**根因**：翻译 JSON 是**静态的、开发者可控的**，不属于用户输入。使用 `set:html` 渲染信任来源的 HTML 是安全的。

**安全判断标准**：
- 翻译文件在仓库中（`src/i18n/` 或 `public/locales/`）
- 无外部 CMS 或数据库注入的翻译内容
- 满足以上条件 → `set:html` 为**误报**，不是真正的安全风险

**通过标准**：
- **误报接受**，不修复
- 标记为 `/* TRUSTED: static JSON translation files */`
- 添加例外注释阻止误报告警（如 CI 配置 allowlist）

**推荐模式 — `<Fragment set:html={t('key')} />`**：
```astro
---
// Trusted: static JSON translation files, no user input
---
<Fragment set:html={t('hero.description')} />
<!-- 等价于 <span set:html={t('hero.description')} />，无额外 wrapper -->
```

**可选改进 — 类型安全的 markup 分离**：
```typescript
// src/i18n/utils.ts
export function thtml(key: string): string {
  return translations[currentLang][key]; // 明确标记为含 HTML 的翻译
}
```
```astro
<Fragment set:html={thtml('hero.description')} />
```

**参考**：
- Astro 官方 `set:html` 文档明确说明：信任来源的 HTML 可安全使用
- `astro-intl` 包的 `t.markup()` API 从类型层面分离 HTML 翻译

**禁止**：为消除此误报将 HTML 标签替换为纯文本（损害内容可读性）。

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

### §5.2 i18n Dead-Key Detection (Run 3 lesson, L13)

**问题**：多个 site 在 [en|zh].json 累积 dead keys, grep 显示 0 ref 但未删. Run 3 修复 GDKVM 2 个 (`home.venue`, `home.authors`); mykcs Run 1 已清 5 个. i18n dead-key 清理是 `sync-all-sites` 高频遗漏区 (per L13).

**检测命令**：
```bash
# 枚举所有 i18n content json files
for json in $(find src/content -name '*en.json' -o -name '*zh.json' 2>/dev/null); do
  echo "=== $json ==="
  # 用 jq 提取所有 scalar paths
  KEYS=$(jq -r 'paths(scalars) | join(".")' "$json" 2>/dev/null)
  for key in $KEYS; do
    # 跳过短 key (< 5 chars) + 跳过 "." 开头的 nested
    [ ${#key} -lt 5 ] && continue
    # 提取 leaf key name
    KEY_NAME=$(echo "$key" | awk -F. '{print $NF}')
    # 排除常见 content key (title, label, description 等)
    case "$KEY_NAME" in
      title|label|description|name|text|content|placeholder|heading|caption|alt) continue ;;
    esac
    # grep 全 src/ 找 ref files count (排除 self)
    COUNT=$(grep -rln "\b${KEY_NAME}\b" src/ --include="*.astro" --include="*.ts" --include="*.tsx" 2>/dev/null | grep -v "^${json}:\|/${json##*/}:" | wc -l | tr -d ' ')
    if [ "$COUNT" = "0" ]; then
      echo "DEAD_KEY: $json::$key"
    fi
  done
done
```

**输出格式**：
- `=== <file> ===` — 文件标识
- `DEAD_KEY: <file>::<key>` — dead key (0 ref in src/)
- 若全 file 无 dead key → 输出空 (但仍打印 `===` 分隔符)
- 总计: `DEAD_KEY_COUNT: <N>`

**修法**：删 dead key, **同时** en.json 和 zh.json 保持 sync. 走 bilingual sync protocol (per `~/.claude/memory/MEMORY.md` HOT FACTS).

**已知边界**：
- 不检查 `data-action`/`id` 等非语义 attribute
- 不检查 comment (TODO, FIXME)
- 不检查 dynamic `t(key)` 调用 (但 Phase 2 报出后必须 grep 验证 dynamic 也没用)

### §5.3 [lang]/404.astro 存在性检查 (Run 3 lesson, L13)

**问题**：双语 site 经常只有默认 `src/pages/404.astro`, 没有 `[lang]/404.astro`. 用户访问 `/zh/non-existent` 会 fall back 到英文 404, i18n 不一致. Run 3 修复 mykcs 加 `src/pages/[lang]/404.astro` (commit `2e5db38`). 已知 issue: CASE-WEBSITE-IMPROVE-MULTI-SITE-20260603 (双语 404.astro).

**检测命令**：
```bash
# 1. 是否双语 site?
HAS_EN=$(test -f src/content/homepage/en.json && echo "yes" || echo "no")
HAS_ZH=$(test -f src/content/homepage/zh.json && echo "yes" || echo "no")
if [ "$HAS_EN" = "yes" ] && [ "$HAS_ZH" = "yes" ]; then
  # 2. 双语 site, 检查 [lang]/404.astro
  if [ -f "src/pages/[lang]/404.astro" ]; then
    echo "I18N_404_OK"
    # 3. 验证含 locale 判断
    if grep -q "Astro.params.lang\|getStaticPaths" "src/pages/[lang]/404.astro"; then
      echo "I18N_404_LOCALE_AWARE"
    else
      echo "I18N_404_NOT_LOCALE_AWARE (warning: 文件存在但无 locale 判断)"
    fi
  else
    echo "I18N_404_MISSING (P1 issue: 用户访问 /zh/non-existent 会 fall back 英文 404)"
  fi
else
  echo "MONOLINGUAL (no check needed)"
fi
```

**输出格式**：
- `I18N_404_OK` — `[lang]/404.astro` 存在
- `I18N_404_LOCALE_AWARE` — 存在且含 locale 判断
- `I18N_404_NOT_LOCALE_AWARE` — 存在但无 locale 判断 (warning)
- `I18N_404_MISSING` — 不存在 (P1 issue)
- `MONOLINGUAL` — 非双语 site, 跳过

**修法**：
1. 复制 `src/pages/404.astro` → `src/pages/[lang]/404.astro`
2. 加 `Astro.params.lang` 判断 → 选对应语言文本
3. 加 `getStaticPaths` 返回 `[{params: {lang: 'en'}}, {params: {lang: 'zh'}}]`
4. Bilingual 翻译 404 标题/正文到 en/zh (走 bilingual sync protocol)
5. 验证: `npm run build` 后 `dist/en/404/index.html` + `dist/zh/404/index.html` 都生成

**参考实现**：mykcs Run 3 commit `2e5db38` (`feat(i18n): add bilingual 404 page for /en/404/ and /zh/404/`)

---

## §6. Agent-Check-Deps — 依赖检查

**对应 Agent**: Agent-Check-Deps

- [ ] 无未使用依赖：`zod`（空 collections）、`@fontsource/*`（无 import）、`@astrojs/compiler-rs`（未启用 rustCompiler）
- [ ] `@tailwindcss/postcss` → 已迁移到 `@tailwindcss/vite`
- [ ] `tailwind.config.mjs` + Tailwind v4 → v4 忽略此文件，主题写在 `global.css` 的 `@theme {}` 中
- [ ] `postcss.config.mjs` + Tailwind v4 + Vite → 已删除
- [ ] `@astrojs/tailwind` → 已迁移到 Tailwind v4 + `@tailwindcss/vite`
- [ ] **Tailwind v4 集成无冲突**：v4 只通过 `@tailwindcss/vite` + `vite.plugins`，**禁止**在 `integrations` 数组中同时使用 `tailwindcss()`（这会加载 v3 模式并导致 CSS 完全丢失）
- [ ] **@tailwindcss/vite 版本**：使用 v4.1.18（v4.3.0 有 tsconfigPaths bug）

```bash
# 1. 检查 @tailwindcss/vite 是否安装
grep -q "@tailwindcss/vite" package.json && echo "OK" || echo "MISSING"

# 2. 检查 tailwind.config.mjs 是否为 legacy（v4 忽略此文件）
grep -q "tailwind.config.mjs" && echo "LEGACY (ignored by v4)"

# 3. ⚠️ 检查 Tailwind v3/v4 集成冲突（CRITICAL）
# 如果 astro.config.mjs 的 integrations 数组中有 tailwindcss()，同时 vite.plugins 中也有 tailwindcss()，则会冲突
INTEGRATIONS_TAILWIND=$(grep -c "tailwindcss()" astro.config.mjs 2>/dev/null || echo "0")
VITE_TAILWIND=$(grep -c "tailwindcss()" astro.config.mjs 2>/dev/null || echo "0")
# 正确：只有 vite.plugins 中有 tailwindcss()
# 错误：integrations 和 vite.plugins 中都有
grep -n "integrations.*\[" astro.config.mjs | head -1
grep -n "tailwindcss()" astro.config.mjs

# 4. @tailwindcss/vite 版本检查
TAILWIND_VITE_VERSION=$(node -p "require('./node_modules/@tailwindcss/vite/package.json').version" 2>/dev/null || echo "unknown")
echo "@tailwindcss/vite version: $TAILWIND_VITE_VERSION"
# v4.3.0 有 tsconfigPaths bug，应降级到 4.1.18
```

**常见失败**：
- `integrations: [tailwindcss(), ...]` + `vite: { plugins: [tailwindcss()] }` → CSS 完全丢失
- `@tailwindcss/vite@4.3.0` → `tsconfigPaths` 错误，build 失败

---

## §6.1 Tailwind CSS 内联运行时验证（构建后必须执行）

> **CSS 完全丢失是最隐蔽的 bug**：build 成功、astro check 通过，但页面无样式。必须在 build 后验证 HTML 中是否真的包含了 Tailwind utilities CSS。

```bash
# 构建后验证（build 必须先完成）
python3 -c "
import re, sys, os

# 查找所有 HTML 文件
html_files = []
for root, dirs, files in os.walk('dist'):
    for f in files:
        if f.endswith('.html'):
            html_files.append(os.path.join(root, f))

missing_css = []
for html_path in html_files:
    with open(html_path) as f:
        html = f.read()
    # 检查是否有 Tailwind utilities CSS
    styles = re.findall(r'<style[^>]*>(.*?)</style>', html, re.DOTALL)
    has_tailwind = any('.bg-' in s or '.text-' in s or '.flex' in s for s in styles)
    if not has_tailwind and len(styles) > 1:  # 忽略只有 1 个 style 的简单页
        missing_css.append(html_path.replace('dist/', ''))

if missing_css:
    print('CSS_MISSING_IN:', ', '.join(missing_css[:5]))
    sys.exit(1)
else:
    print('CSS_INLINED_OK')
"
```

**Acceptance**：所有页面 HTML 中包含 Tailwind utilities CSS（`.bg-*`、`.text-*`、`.flex` 等）。

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

1. **jsDelivr semver tag redirect — Node.js undici 不跟随 301 重定向**：
   - `@v1` 和 `@v1.1.0` 均 301 重定向到 `raw.githubusercontent.com`
   - Node.js undici fetch 在 Astro build 图片优化阶段**不会跟随**该重定向
   - **症状**：`npm run build` 报错 `fetch failed` 或图片 404，但 curl 访问正常
   - **Fix**：
     1. 在 `astro.config.mjs` 的 `image.remotePatterns` 中添加 `{ protocol:'https', hostname:'raw.githubusercontent.com' }`
     2. 消费者端使用**精确 patch 版本**（`@v1.1.0`），不用 semver 范围（`@v1`）
     3. academic 仓库配置 `bump-version.yml` 自动递增 patch tag
   ```js
   // astro.config.mjs
   remotePatterns: [
     { protocol: 'https', hostname: 'cdn.jsdelivr.net' },
     { protocol: 'https', hostname: 'raw.githubusercontent.com' }, // 必须
   ],
   ```

2. **jsDelivr 新 tag 同步延迟**：刚 push 后访问 `@v1.0.0` 可能 502，改用短 commit hash（如 `@2d8a325`）立即可用

3. **Astro `<Image>` 需要 `remotePatterns`**：在 `astro.config.mjs` 中声明 `cdn.jsdelivr.net`

4. **构建时图片下载**：`npm run build` 时 Astro `<Image>` 会实际请求远程图片，URL 404/502 会直接报错中断 → build 通过 = 所有图片可访问

### CDN 版本策略 — 构建失败时的修复流程

**场景**：本地 `npm run build` 报错 `fetch failed`，但 `curl` 访问 URL 正常。

**根因**：jsDelivr semver tag 301 重定向到 `raw.githubusercontent.com`，undici 不跟随；或本地网络无法访问 `raw.githubusercontent.com`。

**三步修复流程**：

```
Step 1 — 添加 remotePatterns（必做）
   在 astro.config.mjs 中确保包含：
   { protocol:'https', hostname:'raw.githubusercontent.com' }

Step 2 — 尝试绕过 jsDelivr 重定向
   将所有 cdn.jsdelivr.net/gh/<org>/<repo>@<tag>/images
   替换为 raw.githubusercontent.com/<org>/<repo>/<commit-sha>/images

Step 3 — 本地网络不通时的回退策略
   如果 Step 2 仍然 fetch failed（本地 raw.githubusercontent.com 不通）：
   → 回退到 cdn.jsdelivr.net@v<tag>
   → commit + push，让 CI 验证（CI 网络通常可达）
   → build 产物由 CI 产出，本地只负责开发和 commit
```

**示例**（OSA 案例）：
```
# Step 2 替换
cdn.jsdelivr.net/gh/mykcs/academic@v1.1.0/images
  → raw.githubusercontent.com/mykcs/academic/84e996d75a811c8eb2758b3a74cd9615d3f5252f/images

# 如果本地 build 仍失败（网络不通），执行 Step 3
# 回退到 cdn.jsdelivr.net@v1.1.0，push 到 CI 验证
```

**commit SHA 获取方法**：
```bash
git ls-remote --tags https://github.com/<org>/<repo>.git 2>/dev/null | grep "<tag>"
# 输出如: 84e996d75a811c8eb2758b3a74cd9615d3f5252f  refs/tags/v1.1.0
```

**原则**：
- `remotePatterns` 配置正确 = 构建可在任何网络环境工作
- 优先 commit SHA（绕过重定向），其次 semver tag（依赖 CI 验证）
- 本地 build 失败不阻塞开发，push 后 CI 通过即可

### 迁移检查清单

- [ ] `grep -rn "academic/images" src/ public/` 确认所有引用已迁移
- [ ] `vendor/academic` submodule 指向带 tag 的 commit
- [ ] `npm run build` 通过且 dist/ 无残留绝对路径

---

## §12.2 CDN 图片加载模式 — OSA 模式（推荐）vs GDKVM 模式（不推荐）

> **触发条件**：审计涉及外部学术图片（`cdn.jsdelivr.net` / `raw.githubusercontent.com` / `<Image>` 组件）的项目。

### 两种模式对比

| 维度 | OSA 模式 ✅（推荐） | GDKVM 模式 ❌（不推荐） |
|------|-------------------|----------------------|
| **图片组件** | `<img>`（原生 HTML） | `<Image>`（Astro 组件） |
| **remotePatterns** | **不包含** `cdn.jsdelivr.net` | 包含 `cdn.jsdelivr.net` |
| **CDN URL** | `cdn.jsdelivr.net/gh/<org>/<repo>@v1.1.0/...` | `raw.githubusercontent.com/<org>/<repo>/<sha>/...` |
| **版本方式** | 语义化版本 tag（`@v1.1.0`） | Commit SHA（不可读、不可预期） |
| **CDN 边缘加速** | ✅ 有（全球边缘节点） | ❌ 无（直连 GitHub 源站） |
| **构建时图片验证** | ✅ 不触发（Astro 图片管线外） | ⚠️ 触发（需处理 301 重定向） |

### 为什么 OSA 模式更现代

**1. 语义化版本 vs Commit SHA 陷阱**
- OSA：`@v1.1.0` 可读、可预期、可管理，打新 tag 即可更新
- GDKVM：`<sha>` 不可读、不可预期，仓库更新后需手动逐个替换

**2. CDN 边缘加速 vs 直连源站**
- jsDelivr：全球边缘节点缓存，用户访问就近命中，延迟低
- raw.githubusercontent.com：无 CDN 层，在中国大陆等地区访问稳定性差

**3. 架构层面规避 vs 技术债妥协**
- OSA：用 `<img>` 代替 `<Image>` → 不进入 Astro 图片管线 → 从根本上规避 301 重定向问题
- GDKVM：加入 `remotePatterns` + `raw.githubusercontent.com` fallback → 以技术债换编译通过

### 检测命令

```bash
# 1. 检测当前项目使用的是哪种模式
echo "=== remotePatterns 配置 ==="
grep -A10 "remotePatterns" astro.config.mjs

echo ""
echo "=== 检测 <Image> 组件使用情况 ==="
grep -rn "<Image" src/ --include="*.astro" | head -10

echo ""
echo "=== 检测 <img> + jsDelivr 使用情况 ==="
grep -rn 'src="https://cdn.jsdelivr.net' src/ --include="*.astro" | head -10

echo ""
echo "=== 检测 raw.githubusercontent.com 使用情况 ==="
grep -rn "raw.githubusercontent.com" src/ --include="*.astro" | head -10
```

### 判断逻辑

```
IF 发现 <Image> 组件引用 cdn.jsdelivr.net
   THEN 标记为 GDKVM 模式（不推荐）
   AND 建议：替换为 <img> + jsDelivr 语义化版本

IF 发现 remotePatterns 包含 cdn.jsdelivr.net
   AND 项目使用 <Image> 组件
   THEN 这是中间态保守策略，不干净
   AND 建议：移除 cdn.jsdelivr.net from remotePatterns，改用 <img>

IF 发现 remotePatterns 不包含 cdn.jsdelivr.net
   AND 使用 <img> + jsDelivr 语义化版本
   THEN OSA 模式 ✅，通过
```

### OSA 模式修复流程（GDKVM → OSA）

```
Step 1 — 替换 <Image> 为 <img>
   搜索：grep -rn "<Image" src/ --include="*.astro"
   替换：将 <Image src={...} alt={...} /> 改为 <img src={...} alt={...} />

Step 2 — 更新 URL 为语义化版本
   将 raw.githubusercontent.com/<org>/<repo>/<sha>/
   替换为 cdn.jsdelivr.net/gh/<org>/<repo>@v<tag>/

Step 3 — 从 remotePatterns 移除 cdn.jsdelivr.net
   只保留：
   { protocol: 'https', hostname: 'mykcs.github.io' },
   { protocol: 'https', hostname: 'raw.githubusercontent.com' },

Step 4 — 验证构建
   npm run build && echo "OSA 模式迁移完成"
```

### 何时保留 GDKVM 模式（例外）

- 项目**必须**使用 `<Image>` 组件的响应式图片功能（自动 WebP、srcset）
- 此时使用 `raw.githubusercontent.com` 作为 fallback 可接受，但应在注释中说明原因
- 长期建议：迁移到真正的图片服务（Cloudinary、Imgix 等）

### Acceptance

- [ ] remotePatterns 中**不包含** `cdn.jsdelivr.net`（用 `<img>` 规避验证问题）
- [ ] 外部学术图片使用 `<img>` + `cdn.jsdelivr.net/@v<semver>/` 格式
- [ ] 版本 tag 为语义化版本（`v1.0.0`），非 commit SHA
- [ ] `npm run build` 通过，零 fetch failed 错误

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

## §14. Cross-Repo / Multi-Site Consistency Checks (2026-06-02)

> **触发条件**：审计 ≥2 个相关 repo，或在 `~/Repo/webs/` 矩阵下工作时
>
> **历史来源**：2026-06-02 5 仓扩展审计（mykcs + GDKVM + OSA + wangrui + academic）— 当日 3 仓审计（§0/§12-§16 in SKILL.md）的增量补强

### §14.1 Dead workflow lint

**模式**：`.github/workflows/*.yml` 中 `actions/checkout@*` 配置 `submodules: recursive`，但同一 repo 没有 `.gitmodules` 文件。

**触发场景**：消费者从 git submodule 迁移到 CDN（jsDelivr `@v1.x.y`）后，遗留的死 workflow。

**检测命令**（v3.3.0 self-resilient pattern，强制标准）：
```bash
# v3.3.0 hardening: line-anchored EOL-anchored pattern
# - 不会匹配 detection script 自身的 grep 字符串
# - 无需 basename skip 来自我排除
for yml in .github/workflows/*.yml; do
  [ -f "$yml" ] || continue
  if grep -qE '^[[:space:]]+submodules:[[:space:]]+recursive[[:space:]]*$' "$yml" 2>/dev/null; then
    if [ ! -f .gitmodules ] || ! grep -q '^\[submodule' .gitmodules 2>/dev/null; then
      echo "DEAD: $yml references submodules but no valid .gitmodules (file missing or has no [submodule] sections)"
    fi
  fi
done
```

**self-resilient pattern 强制规则**（per SKILL.md §32）：
- ✅ `^[[:space:]]+KEY:[[:space:]]+VALUE[[:space:]]*$` —— line-anchored + EOL-anchored
- ❌ 裸 `grep -q "PATTERN"` —— 匹配自身 / 注释 / 字符串字面量
- ❌ basename skip 唯一防御 —— 路径不匹配即失效

**真实命中（2026-06-02）**：
- mykcs.github.io: `.github/workflows/main.yml`（Sync Academic Submodule）→ 已删
- OSA: `.github/workflows/main.yml`（Sync Academic Submodule）→ 已删
- academic: `.github/workflows/update-sites.yml`（Sync Academic Submodule）→ 已删
- wangrui: 仍存在（按 P2 留待下次；当前 active main.yml 中无 submodules 引用）

**修复**：`git rm .github/workflows/<name>.yml && git commit -m "fix(ci): remove dead <Name> workflow"`

### §14.2 CDN ref mutable / pinned check

**模式**：`cdn.jsdelivr.net/gh/<owner>/<repo>@<mutable_ref>` 中的 ref 是可变的（`@main` / `@master` / `@HEAD` / `@latest`）。

**风险**：上游 ref 变 → 资源消失/破坏/行为改变。**不可逆**（CDN 有缓存，但 invalidate 不一定及时）。

**检测命令**：
```bash
grep -rE "cdn\.jsdelivr\.net/gh/[^@]+@(main|master|HEAD|latest)\b" \
  --include="*.astro" --include="*.ts" --include="*.tsx" --include="*.js" \
  --include="*.json" --include="*.md" .
```

**真实命中（2026-06-02）**：wangrui `astro/src/components/Favicon.astro` 用 `sprites-gallery@main` → 改为 `@15b1dcb`（同 SHA 已用于 `CVLayout.astro:111`，验证可工作）

**修复**：用 semver tag（`@v1.1.0`）或 commit SHA 替换 mutable ref。

### §14.3 Dead i18n key detection

**模式**：JSON 中的 key 没有被任何 `t('key')` / `i18n.t('key')` 调用使用。

**风险**：JSON 膨胀；维护负担（增减 keys 时双向同步成本高）；可能掩盖 dead code（key 看似用，实际只是被 import 链上一处 reference 引用）。

**检测命令**（per feature folder）：
```bash
for key in $(jq -r 'keys[]' src/content/<feature>/en.json 2>/dev/null); do
  grep -rE "t\(['\"]${key}['\"]\)|i18n\.t\(['\"]${key}['\"]\)" src/ 2>/dev/null | grep -q . || \
    echo "DEAD: key '${key}' not used in src/"
done
```

**真实命中（2026-06-02）**：
- GDKVM `src/i18n/{en,zh}.json`（218 行）整个文件未被 import → 整文件删除
- GDKVM `footer.langSwitch` key → 单 key 删除
- GDKVM `tool` JSON 8 keys（tab1, tab2, modelType, moe, dense, na, show, placeholder）只在被删的 orphan 文件中存在 → 随 orphan 文件一并删除
- wangrui `Masthead.astro:21` 局部 `const switchLabel`（不是 JSON key，但同 dead-code 模式）→ 删除
- OSA `langSwitchEn` / `og.locale` / `og.localeAlternate` keys → 标记删除（P3）

**注意**：JSON key 删除应在 bilingual-alignment 之后（先删 zh，再删 en 或反之），避免 i18n 暂时只剩单边。

### §14.4 CDN ref consistency (code vs docs)

**模式**：`.astro`/`.ts` 中的 CDN ref（如 `@v1.1.0`）与文档（`CONTEXT.md` / `CLAUDE.md`）中提到的 ref 不一致。

**风险**：开发者按文档操作 → 实际加载不同版本 → 调试困难。

**检测命令**：
```bash
# Find CDN refs in source
src_refs=$(grep -rEho "cdn\.jsdelivr\.net/gh/[^/]+/[^/@]+@[^/\")]+" \
  --include="*.astro" --include="*.ts" src/ 2>/dev/null | sed 's/.*@//' | sort -u)

# Find CDN refs in docs
doc_refs=$(grep -rEho "cdn\.jsdelivr\.net/gh/[^/]+/[^/@]+@[^/\) ]+" \
  --include="*.md" --include="*.mdx" . 2>/dev/null | sed 's/.*@//' | sort -u)

# Compare
diff <(echo "$src_refs") <(echo "$doc_refs")
```

**真实命中（2026-06-02）**：GDKVM `CONTEXT.md` 写 `@84e996d`（commit SHA），代码用 `@v1.1.0`（semver tag）→ 改 docs。

**修复**：以 source 为准（runtime 实际加载的）；更新 docs 同步。配合 §14.2 检测引用是否 mutable。

### §14.5 i18n defaultLocale 跨镜像一致性

**模式**：同 owner 的镜像站点（mykcs + wangrui）使用不同的 `defaultLocale`。

**风险**：访问两个站点的用户对「默认语言」的预期不一致。SEO 重复内容风险。

**检测**：
```bash
for site in ~/Repo/webs/active/*/ ~/Repo/webs/arch/*/; do
  config=$(find "$site" -maxdepth 3 -name "astro.config.*" 2>/dev/null | head -1)
  if [ -n "$config" ]; then
    echo "$(basename $site): $(grep -E "defaultLocale" "$config" 2>/dev/null | head -1)"
  fi
done
```

**真实命中（2026-06-02）**：wangrui arch uses `defaultLocale: 'zh'`（inverted），mykcs uses `'en'`。用户从 mykcs 切到 wangrui 期望默认 en，实际看到 zh。

**修复决策**：通常以 active 主站为准，arch 站同步。但这是**结构性变更**（影响所有 URL），需用户 sign-off。已 defer 为 P1。

### §14.6 Pre-audit working tree gate

**模式**：开始 audit 前，工作树已有 uncommitted 改动（特别是 ` D` 删除标记）。

**风险**：audit 结果可能基于错误的工作树状态。CI fresh-clone 与本地工作树不一致 → CI 通过但本地实际坏掉。

**真实命中（2026-06-02）**：academic repo 31 个 ` D` GDKVM 图像删除未提交。audit 阶段没意识到这是 P0 finding，fix 阶段才被 aggregator 标记（ACAD-P0-001）。

**修复流程**：
1. audit 启动前：`git status --porcelain` 必须为空
2. 除非用户显式声明这是 in-progress work
3. 如有 uncommitted work：明确分类为 (a) 已 staged 待 commit、(b) 误操作需丢弃、(c) 故意保留需 commit
4. (c) 类应在 audit 前 commit，避免污染 audit 上下文

### §14.7 Cross-repo owner double-verify (gh api)

> 触发：SKILL.md §31 升级（doc-sync 反向漂移防护）
> 来源：CASE-CROSS-REPO-OWNER-DRIFT-20260603

**模式**：doc / skill / 启动声明 引用 `<owner>/<repo>`，但该 owner/repo 在 GitHub 上 404（stale local config 误导）。

**风险**：stale git remote 不会因 GitHub 404 而 fail。本地 `git remote -v` 可无限期指向 404 URL。doc-sync agent 仅查 git config 不足以发现，audit agent 跑 `gh api` 才能拦截。

**真实命中（2026-06-03）**：
- mykcs/OSA: gh api 404（task 描述错把它当 canonical，实际 wangrui2025/osa 才是）
- 4 处 SKILL.md 替换 + 1 处 CLAUDE.md + 1 处 CASE-097 已污染
- 已 rollback（commit 0b550d5）

**检测命令**（gh api 双侧验证）：
```bash
# 对所有 active site 跑双侧验证
for repo in mykcs/mykcs.github.io wangrui2025/GDKVM wangrui2025/osa mykcs/OSA; do
  status=$(gh api "repos/$repo" -q '.full_name' 2>/dev/null)
  if [ -z "$status" ]; then
    echo "MISSING: $repo (gh api 404 — stale remote or wrong owner)"
  else
    echo "OK: $status"
  fi
done
```

**Acceptance**：
- 0 MISSING（无 stale remote）
- 任何 MISSING → CI fail，触发 §30 自进化协议

**集成到三仓 CI**（在 multi-site-checks.yml 加 step）：
```yaml
      - name: §14.7 Cross-repo owner double-verify
        run: |
          set -euo pipefail
          echo "::group::§14.7 Cross-repo owner double-verify"
          failed=0
          for repo in mykcs/mykcs.github.io wangrui2025/GDKVM wangrui2025/osa mykcs/OSA; do
            status=$(gh api "repos/$repo" -q '.full_name' 2>/dev/null || echo "")
            if [ -z "$status" ]; then
              echo "::error::MISSING: $repo (gh api 404 — stale remote or wrong owner)"
              failed=1
            else
              echo "✓ OK: $status"
            fi
          done
          echo "::endgroup::"
          exit $failed
```

**anti-pattern**（per SKILL.md §31）：
- ❌ `git remote -v 列出 = remote 存在` —— git config 可指向任意 URL 包括 404
- ❌ `task 描述 = 事实` —— 用户给的 owner 假设可能基于过时文档
- ❌ doc-sync 与 audit 验证深度不对等 —— 两类 agent 必须共享 §0 硬规则

---

## §15. Multi-Site Workflow Patterns (2026-06-02)

> 适用于使用 Workflow / multi-execute / team 等工具编排 N 个站点并行 audit 的场景
>
> **历史来源**：2026-06-02 5 仓并行 audit（mykcs + GDKVM + OSA + wangrui + academic）— 实际执行：11 agents / 648 tool uses / 844,747 subagent tokens / 30 min wall-clock

### §15.1 Schema extraction robustness (P0 trap)

**陷阱**：sub-agent 不传 `schema:` 时，return value 是 final text message。如果 orchestrator 用结构化字段过滤（如 `r.buildFinalStatus === 'pass'`），全部 fallback 为 `null` → 整个 phase 静默 skip。

**真实命中（2026-06-02）**：5-site audit 的 fix phase 5 agents 全部返回 text（无 schema），orchestrator 的 `pushable = fixResults.filter(r => r && r.buildFinalStatus === 'pass')` 过滤为 0 → push phase 跳过 → 14 commits 卡在本地未被 push。修复后由 orchestrator（main context）单独 push 14 commits 全部 PASS。

**修复（按优先级）**：
1. **始终给 sub-agent 传 `schema:`**（即使 minimal：仅 site / status / summary 三个字段）
2. 或：sub-agent 既写 `scan-{id}.json` 到磁盘，又返回 schema-validated 对象 → orchestrator 可读盘 fallback
3. 或：orchestrator 加 text fallback 解析（`r.summary.match(/build: (pass|fail)/)`）

**检测方法**（在 workflow result 上）：
```js
const empties = results.filter(r => r && Object.keys(r).length === 0).length
if (empties > 0) log(`⚠️ ${empties} sub-agents returned empty results — schema extraction failed`)
```

### §15.2 Push phase: `git pull --rebase` mandatory

**陷阱**：multi-site 编排下，多个 sessions / agents / 手动 push 可能先后发生。origin 可能在 pull 之后又有新 commit → `git push` 被 reject（non-fast-forward）。

**真实命中（2026-06-02）**：wangrui push 在第一轮被 reject，提示「一个仓库已向该引用进行了推送」。需 `git pull --rebase origin main && git push origin main` 才成功。

**修复**：push phase 的 agent prompt 强制要求 `git pull --rebase origin main`。在 orchestrator 的 PUSH_PROMPT 中显式写出。

**为什么不能用 smart-autopush.sh**：smart-autopush.sh 会在 pre-condition 不满足时 auto-commit（`git add -A`），对 academic 这种带 31 个 P0 deletions 的 repo 来说会污染 P0 finding。

### §15.3 限速 push 避免 GH Actions rate limit

**规则**：multi-site push 时，限制并发数 ≤ 2。

**理由**：GitHub Actions 免费账户 20 concurrent jobs，但同一 owner 的多 repo 同时 push + deploy 容易触发 GH 的 quota 警告（personal account 更敏感）。

**实现**：orchestrator 用 batch-of-2 + barrier + CI watch 模式：
```js
for (let i = 0; i < pushable.length; i += 2) {
  const batch = pushable.slice(i, i + 2)
  const results = await parallel(batch.map(s => () => pushAndWatch(s)))
  const failed = results.find(r => r?.ciStatus === 'failure')
  if (failed) {
    log('🚨 CI failed — STOPPING all remaining pushes per user directive')
    break
  }
}
```

### §15.4 CI failure interpretation

**陷阱**：CI 失败 ≠ 真实回归。某些 CI 失败是 EXPECTED signal（新加的 pre-flight guard 触发）。

**真实命中（2026-06-02）**：
- academic `validate-manifest.yml`（新加）失败 — 设计内行为，flag 了 P0-001（31 uncommitted GDKVM deletions + 2 dead image-map entries + 14 stale manifest entries）
- academic `Bump Version Tag` 同步成功（pre-bump guard 不触发，CI fresh-clone 看不到 local 31 deletions — 见 §15.5）

**修复流程**：
1. 看到 CI failure → 第一时间 `gh run view <id> --log-failed`
2. 区分："real regression" vs "expected signal" vs "transient infra issue"
3. real regression → halt 并报告
4. expected signal → 报告用户，标记为 design-intended（不阻塞后续 push）
5. transient → retry 一次，仍失败按 real regression 处理

### §15.5 Pre-bump guard 限制（CI fresh-clone 盲点）

**陷阱**：在 `.github/workflows/bump-version.yml` 加的 pre-bump guard 只看 `git status --porcelain`，但 CI runner 是 fresh-clone — 看不到 local working tree 状态。

**真实命中（2026-06-02）**：academic bump-version.yml 加的 pre-bump guard `git status --porcelain | grep '^ D'` 在 CI 上看到的是 fresh-clone（无 destructive deletions）→ 永远不触发。实际 31 个 deletions 在 `~/Repo/webs/academic` 的 local working tree，CI 看不到。

**修复（按推荐度）**：
- **方案 A**：在 `git push` 之前的 local pre-push hook 中跑 guard（推荐：拦截在最早阶段）
- **方案 B**：把 guard 改成 `git diff --name-only HEAD~1..HEAD | xargs -I {} bash -c 'test -f {} || echo MISSING: {}'`
- **方案 C**：要求所有 destructive ops 都先 commit（最严格，但 workflow 改动大）

**当前最佳实践**：方案 A — `~/.claude/scripts/pre-push-academic.sh` 加 guard，每次 `git push` 前跑。`smart-autopush.sh` 改造支持 hook 触发。

### §15.6 N-site 上限是 advisory（user 可 override）

**之前规则**：「3 个 agent 并行上限」（来自 2026-06-02 3 仓审计，§跨仓 audit 拆分策略）

**2026-06-02 5 仓审计推翻**：用户明确要求 5 仓并行「在 slowest-site time 内完成」。Audit 完成（11 agents / 648 tool uses / 844,747 tokens），但暴露 §15.1 (schema bug) — push phase 静默 skip。

**新规则（生效 2026-06-02 5-site audit 后）**：

| N | 推荐 | 必备条件 |
|---|------|----------|
| 1 | 直接用 Mode A | — |
| 2-3（默认）| 每仓 1 agent 跑全 phases | token 成本 vs 隔离价值平衡点 |
| 4-5（user override）| Workflow pipeline | orchestrator 显式声明 N + 全部 sub-agent 传 `schema:` + push rate-limited (≤2) + text fallback |
| 6+ | 拒绝，建议拆 2 个 session | context overflow 风险 |

**用户 override 触发条件**：用户显式说"5 仓并行"/"multi-site"/"N-site in slowest-time"。Orchestrator 必须 ask 一次确认 scope 后启动。

---

## §23. i18n switch URL — getRelativeLocaleUrl + prefixDefaultLocale:false 验证

> **触发条件**：`astro.config.mjs` 中 `i18n.prefixDefaultLocale: false`
>
> **历史来源**：2026-06-03 mykcs.github.io `Masthead.astro`（zh → en 切换跳到 `/en/` 但 en news_items 实际为 `/en/cv/` → 404）

### 检测

```bash
# 1. 读 astro.config.mjs 的 i18n 配置
grep -E "prefixDefaultLocale|defaultLocale" astro.config.mjs

# 2. 找所有 getRelativeLocaleUrl 调用
grep -rn "getRelativeLocaleUrl" src/ --include="*.astro" --include="*.ts"

# 3. 验证返回值在 dist 中存在
node -e "
const fs = require('fs');
const path = require('path');
const re = /href=\"([^\"]+)\"/g;
const files = require('glob').sync('dist/**/*.html');
const broken = [];

files.forEach(f => {
  const html = fs.readFileSync(f, 'utf-8');
  let m;
  while ((m = re.exec(html)) !== null) {
    const href = m[1];
    if (href.startsWith('http') || href.startsWith('#') || href.startsWith('mailto:')) continue;
    if (href.match(/\.[a-z]{2,4}$/)) continue;  // 静态资源
    const clean = href.replace(/\/$/, '');
    const candidates = [
      'dist' + clean,
      'dist' + clean + '/index.html',
    ];
    if (!candidates.some(c => fs.existsSync(c))) {
      broken.push(\`\${f} → \${href} NOT FOUND\`);
    }
  }
});

if (broken.length) {
  console.log('=== BROKEN I18N SWITCH URLS ===');
  broken.forEach(b => console.log(b));
  process.exit(1);
} else {
  console.log('OK: all i18n switch URLs resolve');
}
"
```

### 修复模式

```typescript
// 错
const switchUrl = getRelativeLocaleUrl(targetLocale, currentPath);
// prefixDefaultLocale:false 时返回 '/cv/'（无前缀）→ 404

// 对
const basePath = Astro.url.pathname.replace(/^\/(en|zh)\//, '/').replace(/^\/(en|zh)$/, '/') || '/';
const switchUrl = targetLocale === 'en'
  ? \`/en\${basePath === '/' ? '/' : basePath}\`
  : \`/zh\${basePath === '/' ? '/' : basePath}\`;
```

---

## §24. JSON-LD `set:html` 验证

> **触发条件**：项目使用 Schema.org `application/ld+json`
>
> **历史来源**：2026-06-03 GDKVM + OSA 同次审计中同时中招 — `<script define:vars={JSON}>{JSON.parse(structuredDataJson)}</script>` 不写 DOM

### 检测

```bash
# 1. 找所有 application/ld+json script
grep -rn 'application/ld+json' src/ --include="*.astro"

# 2. 验证不是 define:vars 模式（写死 = broken）
grep -rn 'application/ld+json' src/ --include="*.astro" | grep -E 'define:vars|JSON\.parse' && \
  echo "BROKEN: define:vars 模式不写 DOM" || echo "OK"

# 3. 验证 dist 中实际有 JSON 内容（不是空 script）
python3 -c "
import re, glob
broken = []
for f in glob.glob('dist/**/*.html', recursive=True):
    html = open(f).read()
    for m in re.finditer(r'<script type=\"application/ld\+json\"[^>]*>(.*?)</script>', html, re.DOTALL):
        body = m.group(1).strip()
        if not body or body == 'null' or len(body) < 5:
            broken.append(f'{f}: empty JSON-LD body')
        elif not body.startswith('{') and not body.startswith('['):
            broken.append(f'{f}: JSON-LD body not JSON: {body[:50]}')

if broken:
    print('=== BROKEN JSON-LD ===')
    for b in broken: print(b)
    exit(1)
else:
    print('OK: JSON-LD content present in all pages')
"
```

### 修复模式

```astro
<!-- 错 -->
<script type="application/ld+json" is:inline define:vars={{ structuredData }}>
  {JSON.parse(structuredDataJson)}
</script>

<!-- 对 -->
<script type="application/ld+json" set:html={structuredDataJson} />
```

---

## §25. Critters Cannot-Inline 检测

> **触发条件**：项目使用 `astro-critters` 集成
>
> **历史来源**：2026-06-03 mykcs.github.io build log 报 3 个 `Cannot inline file dist/{index,design/index,hello/index}.html!` 噪声（meta-refresh 跳转桩无 CSS）

### 检测

```bash
# build log 中 grep
npm run build 2>&1 | grep -i "cannot inline" | head -5
# 期望输出: 空（0 行）

# 如果有 1+ 行 → 需要 filter meta-refresh 桩
```

### 修复模式

```javascript
// astro.config.mjs
critters({
  Critters: {
    // Skip Astro's auto-generated meta-refresh redirect stubs
    prerender: (path) => !{
      'index.html': true,
      'design/index.html': true,
      'hello/index.html': true,
    }[path] === true,
  },
}),
```

**注意**：列出所有 meta-refresh 桩（grep `dist -name "*.html" -exec grep -l "http-equiv.*refresh" {} \;`）。

---

## §26. Asset 优化检测

> **触发条件**：`@fontsource/*` 字体 + `astro-pagefind` 集成 + 外部 CDN 静态资源

### §26.1 woff cleanup（节省 ~4MB）

```bash
# 检测 dist 中 woff 文件
find dist -name "*.woff" -exec ls -lh {} \;
# 期望: 空

# 检测 CSS @font-face 中引用 woff
grep -rn 'format("woff")' dist/ --include="*.css" --include="*.html" | head -5
# 期望: 空（删除 woff 时同时 strip CSS）
```

**修复模式**（build-pipeline.mjs `astro:build:done` hook）：

```javascript
function removeLegacyWoff(distDir) {
  const _astro = path.join(distDir, '_astro');
  if (!fs.existsSync(_astro)) return;
  for (const f of fs.readdirSync(_astro)) {
    if (f.endsWith('.woff')) {
      const p = path.join(_astro, f);
      console.log(`[woff-cleanup] Removed ${f} (${(fs.statSync(p).size / 1024 / 1024).toFixed(2)}MB)`);
      fs.unlinkSync(p);
    }
  }
  // 同时 strip CSS @font-face 声明
  const stripWoff = (filePath) => {
    if (!fs.existsSync(filePath)) return;
    const original = fs.readFileSync(filePath, 'utf-8');
    const stripped = original.replace(
      /,url\([^)]+\.woff[^)]*\) format\("woff"\)/g, ''
    );
    if (stripped !== original) fs.writeFileSync(filePath, stripped, 'utf-8');
  };
  // 遍历 dist 中所有 .css 和 .html
  // ...
}
```

### §26.2 pagefind cleanup（节省 ~732K）

```bash
# 检测 pagefind 资产
ls -d dist/pagefind/ 2>/dev/null
# 期望: 不存在

# 检测项目是否 import pagefind
grep -rn "pagefind" src/ --include="*.astro" --include="*.ts"
# 如果 dist/pagefind/ 存在但 src/ 无 import → 删除 dist/pagefind
```

### §26.3 translate.svg / icons 本地化

```bash
# 检测 cdn.jsdelivr.net 静态资源
grep -rn 'src="https://cdn.jsdelivr.net' src/ --include="*.astro"
# 期望: 0 个（除非学术资源库图片）

# 替代方案：local public/icons/translate.svg
ls public/icons/*.svg 2>/dev/null | head -5
```

---

## §27. Sitemap filter post-process workaround

> **触发条件**：`@astrojs/sitemap@3.7.x` 报 zod 验证错误
>
> **历史来源**：2026-06-03 GDKVM 实验 3 次（箭头函数 / function / async）filter option 全部 zod 失败

### 检测

```bash
# build log 中 grep zod 错误
npm run build 2>&1 | grep -i "zod\|invalid" | head -5

# 验证 sitemap-0.xml 包含 redirect 桩
test -f dist/sitemap-0.xml && \
  grep -oE '<loc>[^<]*</loc>' dist/sitemap-0.xml | \
  grep -E '/reprod/?$|GDKVM/$|osa/$' | head -5
# 期望: 空（无 redirect 桩）
```

### 修复模式（post-process）

```javascript
// build-pipeline.mjs astro:build:done hook
const sitemapFiles = ['sitemap-0.xml', 'sitemap-index.xml']
  .map(f => path.join(distDir, f))
  .filter(p => fs.existsSync(p));
for (const sf of sitemapFiles) {
  let xml = fs.readFileSync(sf, 'utf-8');
  xml = xml.replace(
    /<url>\s*<loc>https:\/\/wangrui2025\.github\.io\/GDKVM\/(?:(?:en|zh)\/)?reprod\/<\/loc>\s*<\/url>/g,
    ''
  );
  xml = xml.replace(
    /<url>\s*<loc>https:\/\/wangrui2025\.github\.io\/GDKVM\/<\/loc>\s*<\/url>/g,
    ''
  );
  fs.writeFileSync(sf, xml, 'utf-8');
}
```

---

## §28. 双语 [lang]/404.astro 验证

> **触发条件**：双语 i18n 项目（`/[lang]/*` 路由）

### 检测

```bash
# 1. 验证 [lang]/404.astro 存在
test -f "src/pages/[lang]/404.astro" && echo "OK" || echo "MISSING: [lang]/404.astro"

# 2. 验证 dist 中 locale-prefixed 404 存在
for locale in en zh; do
  test -f "dist/${locale}/404/index.html" && echo "OK: dist/${locale}/404/" || \
    echo "MISSING: dist/${locale}/404/"
done

# 3. 验证 lang switch 在 404 页可用
grep -l "switchUrl\|getRelativeLocaleUrl" src/pages/[lang]/404.astro && \
  grep "switchUrl\|getRelativeLocaleUrl" src/pages/[lang]/404.astro | head -3
```

### 修复模式

```astro
---
// src/pages/[lang]/404.astro
import Layout from '../../layouts/Layout.astro';
import { t } from '../../i18n';

export function getStaticPaths() {
  return [
    { params: { lang: 'en' } },
    { params: { lang: 'zh' } },
  ];
}

const { lang } = Astro.params;
---
<Layout lang={lang} title="404">
  <h1>404</h1>
  <p>{t(lang, '404.message')}</p>
  <a href={getRelativeLocaleUrl(lang === 'en' ? 'zh' : 'en', '/')}>
    {t(lang, '404.switchLang')}
  </a>
</Layout>
```

---

## §29. CI workflow 存在性 + 包管理匹配

> **触发条件**：所有 active 站

### 检测

```bash
# 1. 验证 .github/workflows 存在
ls .github/workflows/*.yml .github/workflows/*.yaml 2>/dev/null
# 期望: ≥ 1 个 workflow

# 2. 验证 workflow 包管理与 packageManager 字段一致
if grep -q '"packageManager".*"pnpm' package.json; then
  grep -L "pnpm/action-setup\|pnpm install" .github/workflows/*.yml
  # 期望: 空（无 workflow 用错的包管理）
fi

# 3. 验证 workflow 包含必需步骤
for f in .github/workflows/*.yml; do
  grep -q "actions/checkout" "$f" || echo "MISSING checkout: $f"
  grep -q "actions/setup-node" "$f" || echo "MISSING setup-node: $f"
  grep -q "upload-pages-artifact" "$f" || echo "MISSING upload-pages-artifact: $f"
done
```

### 修复模式

**无 CI 的站**（GDKVM 历史状态）：

```yaml
# .github/workflows/deploy.yml
name: Deploy Astro site to Pages
on:
  push:
    branches: [main]
  workflow_dispatch:

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

permissions:
  contents: read
  pages: write
  id-token: write

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-node@v5
        with:
          node-version: 24
          cache: 'pnpm'
      - run: pnpm install --frozen-lockfile
      - run: pnpm run build
        env:
          NODE_OPTIONS: --max-old-space-size=4096
      - uses: actions/configure-pages@v5
      - uses: actions/upload-pages-artifact@v5
        with:
          path: ./dist
  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - id: deployment
        uses: actions/deploy-pages@v4
```

**OSA 的 bug 修复**（npm → pnpm）：

```yaml
# ❌ 错：项目用 pnpm 但 workflow 用 npm
- run: npm ci
- run: npm run build

# ✅ 对：统一 pnpm
- uses: pnpm/action-setup@v6
- run: pnpm install --frozen-lockfile
- run: pnpm run build
```

---

## Workflow Reminder

**SCAN 工作流**：scan → fix → build-verify → commit

1. 运行检查，记录问题清单
2. 应用修复
3. 重新 `npm run build` 和 `npx astro check` 确认零错误
4. `git add -A` → `smart-autopush.sh` 提交（描述审计/修复内容）

**Multi-Site SCAN 工作流**（2026-06-02 起，详见 §15）：
1. Phase 1: 1 agent per site, scan-only (no push) — 全部传 `schema:`
2. Phase 2: 1 aggregator agent (barrier) — 写 UNIFIED-REPORT.md
3. Phase 3: 1 agent per site, P1+P2 fixes only — 全部传 `schema:`
4. Phase 4: push in batches of 2 — 每仓先 `git pull --rebase`
5. Phase 5: verify (final state check)
