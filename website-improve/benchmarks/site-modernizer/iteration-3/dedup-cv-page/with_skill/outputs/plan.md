# CV 页面去重执行计划

## 目标

清理重复的 CV 页面，保留双语版本，让访问 `/cv/` 的用户自动跳转到 `/zh/cv/`。

## 现状分析

- `src/pages/cv.astro`：纯中文版本，硬编码 `lang = 'zh'`，功能已被 `[lang]/cv.astro` 覆盖。
- `src/pages/[lang]/cv.astro`：双语版本，支持 `en` 和 `zh`，通过 `getStaticPaths` 生成 `/en/cv/` 和 `/zh/cv/`。
- Astro i18n 配置：`defaultLocale: 'zh'`, `prefixDefaultLocale: false`，因此 `/cv/` 和 `/zh/cv/` 理论上都指向中文内容，但 `/cv/` 是由 `cv.astro` 生成的独立页面，存在重复。

## 执行步骤

### 1. 删除重复页面

```bash
rm /Users/myk/.claude/skills/site-modernizer-workspace/iteration-2/dedup-cv-page/mock-repo/src/pages/cv.astro
```

### 2. 创建重定向页面

在 `src/pages/cv.astro` 位置新建一个重定向页面，将 `/cv/` 的请求 301 跳转到 `/zh/cv/`。

Astro 静态输出模式下，使用 `<meta http-equiv="refresh">` 实现客户端重定向：

```astro
---
// src/pages/cv.astro
// Redirect /cv/ -> /zh/cv/
---
<!doctype html>
<html lang="zh">
  <head>
    <meta charset="utf-8" />
    <meta http-equiv="refresh" content="0;url=/zh/cv/" />
    <link rel="canonical" href="/zh/cv/" />
    <title>Redirecting...</title>
  </head>
  <body>
    <p>Redirecting to <a href="/zh/cv/">/zh/cv/</a>...</p>
  </body>
</html>
```

### 3. 验证构建输出

```bash
cd /Users/myk/.claude/skills/site-modernizer-workspace/iteration-2/dedup-cv-page/mock-repo
npm run build
```

验证 `dist/cv.html` 存在且包含重定向标签，同时 `dist/zh/cv/index.html` 和 `dist/en/cv/index.html` 内容正确。

### 4. 清理空目录（如有）

```bash
rmdir /Users/myk/.claude/skills/site-modernizer-workspace/iteration-2/dedup-cv-page/mock-repo/src/pages/cv 2>/dev/null || true
```

## 验收标准

- [ ] `src/pages/cv.astro` 已替换为重定向页面，原纯中文内容已删除。
- [ ] `src/pages/[lang]/cv.astro` 保持不动，继续生成 `/en/cv/` 和 `/zh/cv/`。
- [ ] `npm run build` 成功，无报错。
- [ ] `dist/cv.html` 包含 `<meta http-equiv="refresh" content="0;url=/zh/cv/">`。
- [ ] `dist/zh/cv/index.html` 和 `dist/en/cv/index.html` 内容正确，未被破坏。
