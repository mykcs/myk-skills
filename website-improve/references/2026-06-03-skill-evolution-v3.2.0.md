## Skill Evolution v3.2.0 — 2026-06-03 3 站 Mode A 跨站 bug 模式

> **本节来源**：2026-06-03 对 mykcs/mykcs.github.io、wangrui2025/GDKVM、wangrui2025/osa 同步执行 Mode A 后，**修复过程中**暴露的 5+ 跨站同模式 bug。每个规则对应 §23-§29。

### §23 — `getRelativeLocaleUrl` + `prefixDefaultLocale: false` 陷阱

**症状**：`prefixDefaultLocale: false` 时，`getRelativeLocaleUrl('en', '/cv/')` 返回 `/cv/`（默认 locale 不加 `/en/` 前缀），但实际 build 在 `/en/cv/` → 返回值指向不存在的文件，**Masthead 语言切换点 404**。

**修复模式**（手动构造带前缀 URL）：

```typescript
// ❌ 错：依赖 getRelativeLocaleUrl
const switchUrl = getRelativeLocaleUrl(targetLocale, currentPath);

// ✅ 对：手动拼前缀
const basePath = Astro.url.pathname.replace(/^\/(en|zh)\//, '/').replace(/^\/(en|zh)$/, '/') || '/';
const switchUrl = targetLocale === 'en'
  ? `/en${basePath === '/' ? '/' : basePath}`
  : `/zh${basePath === '/' ? '/' : basePath}`;
```

**检测**：scan-checklist §23 + Agent-Check-Buttons §2.6 强制验证 href 在 dist 中真实存在。

### §24 — JSON-LD 必须用 `set:html`，禁用 `<script define:vars>`

**症状**：`<script type="application/ld+json" is:inline define:vars={{ structuredData }}>{JSON.parse(structuredDataJson)}</script>` — Astro 把变量注入到 inline script 局部作用域，**不是**渲染 JSON-LD 的正确方式。Google 爬虫看不到任何 Schema.org。

**修复**：

```astro
<!-- ❌ 错 -->
<script type="application/ld+json" is:inline define:vars={{ structuredData }}>
  {JSON.parse(structuredDataJson)}
</script>

<!-- ✅ 对 -->
<script type="application/ld+json" set:html={structuredDataJson} />
```

**检测**：scan-checklist §24（dist HTML 中 `<script type="application/ld+json">` 内容必须 ≥ 1 个 JSON 对象）。

### §25 — Critters 必须 filter meta-refresh 桩

**症状**：`astro-critters` 报 `Cannot inline file dist/{index,design/index,hello/index}.html!` — 这些是 Astro 自动生成的 meta-refresh 跳转桩（278-330 字节，无 `<link rel="stylesheet">`，CSS 无内联意义）。Critters 报噪声但 build 通过。

**修复**：

```javascript
critters({
  Critters: {
    prerender: (path) => !{
      'index.html': true,
      'design/index.html': true,
      'hello/index.html': true,
    }[path] === true,
  },
}),
```

**检测**：scan-checklist §25 + build 后 grep `Cannot inline` 必为 0。

### §26 — Asset 优化：woff 4MB + pagefind 732K + translate.svg 本地化

**触发条件**：`@fontsource/*` 字体、`astro-pagefind` 集成、外部 CDN 静态资源。

**woff cleanup（节省 ~4MB）**：
- `@fontsource/noto-serif-sc` 同时打包 woff + woff2（woff 是 legacy IE/old Android 兜底，>97% 现代浏览器可省）
- 删 .woff 文件**必须同时 strip CSS @font-face 声明**，否则 HTML 引用 404
- 模式见 build-pipeline.mjs `removeLegacyWoff` 实现

**pagefind cleanup（节省 ~732K）**：
- `astro-pagefind` build 搜索索引，但无任何 UI 调用 = 死资产
- 模式：检测 dist/pagefind/ 存在但无 `import 'virtual:pagefind'` → 删整目录

**translate.svg / icons 本地化**：
- 每次页面渲染走 1 次 CDN round-trip
- `public/icons/*.svg` 本地化 + `<img src="/icons/translate.svg">` 替代 `src={cdnUrl}`

**检测**：scan-checklist §26 + `du -sh dist/pagefind dist/_astro/*.woff` 必为 0。

### §27 — Sitemap filter post-process workaround

**症状**：`@astrojs/sitemap@3.7.x` 把 `filter` option 用 zod 校验，**拒绝所有用户实现**（箭头函数、function 声明、async 全部失败）。3 种写法都试过。

**修复（workaround）**：放弃 `filter` option，改在 build-pipeline integration 的 `astro:build:done` 钩子里**后处理** `dist/sitemap-0.xml`：

```javascript
const xml = fs.readFileSync('dist/sitemap-0.xml', 'utf-8');
const cleaned = xml.replace(
  /<url>\s*<loc>https:\/\/<site>\/GDKVM\/(?:(?:en|zh)\/)?reprod\/<\/loc>\s*<\/url>/g,
  ''
);
fs.writeFileSync('dist/sitemap-0.xml', cleaned, 'utf-8');
```

**检测**：scan-checklist §27 + build 后 grep `<url>` 必不含 redirect 桩。

### §28 — 双语 [lang]/404.astro 必备

**症状**：项目只有 root `pages/404.astro`（单语）。在 `/en/...` 页面 404 后点 lang switch 跳到 `/zh/404/` → 仍 404（因为 root 404 不会重新生成 locale 版本）。

**修复**：
1. 删除 root `pages/404.astro`（保留 fallback 行为）
2. 新建 `pages/[lang]/404.astro`：

```astro
---
import Layout from '../../layouts/Layout.astro';
import { t } from '../../i18n';

export function getStaticPaths() {
  return [
    { params: { lang: 'en' } },
    { params: { lang: 'zh' } },
  ];
}
---
<Layout lang={Astro.params.lang}>
  <h1>404</h1>
  <p>{t(Astro.params.lang, '404.message')}</p>
</Layout>
```

**检测**：scan-checklist §28 + Agent-Check-Routing 必查 `dist/{en,zh}/404/index.html` 都存在。

### §29 — CI workflow 存在性 + 包管理匹配

**症状**：
- GDKVM **完全没 CI workflow** — audited 7 P0/P1 但无自动验证，下次改动立刻回退
- OSA `astro.yml` 用 **npm**，但项目实际用 pnpm → CI 装错包管理 → 缺 deps

**修复**：
- 无 CI 站：复制 `mykcs.github.io/.github/workflows/deploy.yml` 模板，调整 path
- CI 用错包管理：把 `npm install` 改为 `pnpm install --frozen-lockfile`，或用 `detect-package-manager` action

**检测**：scan-checklist §29 + Agent-Check-Build 必查 `.github/workflows/*.yml` 存在 + workflow 中包管理与 `packageManager` 字段一致。

### v3.2.0 增量（与 v3.0/v3.1 对比）

| 版本 | 来源 | 增量 |
|------|------|------|
| v3.0.0 | 2026-06-02 三仓 audit | §0/§12-§16 |
| v3.1.0 | 2026-06-02 同日 5-site audit | §17-§22 |
| **v3.2.0** | **2026-06-03 三站 Mode A 修复** | **§23-§29（执行层跨站 bug 模式）** |

### 已知跨仓约束（v3.2.0 追加）

| 约束 | 原因 | 适用 |
|------|------|------|
| **JSON-LD 渲染方式** | `set:html` 唯一正确路径 | 所有用 schema.org 的站 |
| **404 page 模板** | 双语站必须 `[lang]/404.astro` | GDKVM / OSA / mykcs |
| **asset 优化基线** | woff 4MB + pagefind 732K = 必删 | 所有 @fontsource/astro-pagefind 站 |
| **CI workflow 必备** | 无 CI = 审计装饰品 | 所有 active 站 |

---
