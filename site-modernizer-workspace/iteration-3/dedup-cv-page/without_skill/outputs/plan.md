# CV 页面去重执行计划

## 目标
- 清理重复的 CV 页面：`src/pages/cv.astro`（纯中文）与 `src/pages/[lang]/cv.astro`（双语）功能重复。
- 保留双语版本 `src/pages/[lang]/cv.astro`，删除纯中文版本 `src/pages/cv.astro`。
- 用户访问 `/cv/` 时自动 301 跳转到 `/zh/cv/`（默认语言为中文）。

## 现状分析

### 文件结构
```
src/pages/
├── cv.astro          ← 纯中文，硬编码 lang='zh'
├── cv/               ← 空目录（Astro 路由占位）
└── [lang]/
    └── cv.astro      ← 双语，支持 en/zh
```

### 关键配置（astro.config.mjs）
```js
i18n: {
  locales: ['en', 'zh'],
  defaultLocale: 'zh',
  prefixDefaultLocale: false,  // 默认语言不显示前缀
  routing: {
    prefixDefaultLocale: false,
  },
}
```

配置说明：`prefixDefaultLocale: false` 表示默认语言 `zh` 的页面既可以通过 `/cv/` 访问，也可以通过 `/zh/cv/` 访问。删除 `src/pages/cv.astro` 后，`/cv/` 路径将失去匹配，需要创建 redirect 规则。

## 执行步骤

### 步骤 1：删除重复文件
```bash
rm src/pages/cv.astro
```

### 步骤 2：清理空目录
```bash
rmdir src/pages/cv
```
（若目录非空则保留，视实际情况而定；当前为空目录，可直接删除。）

### 步骤 3：配置 Astro Redirect
在 `astro.config.mjs` 中添加 `redirects` 配置，将 `/cv/` 永久重定向到 `/zh/cv/`：

```js
export default defineConfig({
  output: 'static',
  integrations: [],
  i18n: {
    locales: ['en', 'zh'],
    defaultLocale: 'zh',
    prefixDefaultLocale: false,
    routing: {
      prefixDefaultLocale: false,
    },
  },
  // 新增：redirects 配置
  redirects: {
    '/cv': '/zh/cv',
    '/cv/': '/zh/cv/',
  },
  vite: {
    plugins: [tailwindcss()],
  },
});
```

> Astro 静态输出模式下，`redirects` 会生成 HTML meta refresh 文件（带 `<link rel="canonical">`），实现客户端跳转。对于永久重定向，Astro 在适配器部署时（如 Vercel/Netlify）可生成 301 规则；纯静态托管（GitHub Pages）则依赖 meta refresh。

### 步骤 4：验证构建
```bash
npm run build
```

检查 `dist/` 目录：
- 不存在 `dist/cv/index.html`（旧页面已删除）
- 存在 `dist/zh/cv/index.html`（双语页面正常生成）
- 存在 `dist/cv/index.html`（redirect 文件，内容含 `<meta http-equiv="refresh" content="0;url=/zh/cv/">`）

### 步骤 5：验证跳转
本地预览或检查生成的 redirect HTML：
```bash
cat dist/cv/index.html
```
预期内容包含：
```html
<meta http-equiv="refresh" content="0;url=/zh/cv/">
<link rel="canonical" href="/zh/cv/">
```

## 回滚方案
若出现问题，可随时从 Git 恢复：
```bash
git checkout -- src/pages/cv.astro
```
并移除 `astro.config.mjs` 中的 `redirects` 配置。

## 验收标准
- [ ] `src/pages/cv.astro` 已删除
- [ ] `src/pages/cv/` 空目录已清理
- [ ] `astro.config.mjs` 包含 `/cv` → `/zh/cv` 的 redirect 配置
- [ ] `npm run build` 成功，无报错
- [ ] `dist/cv/index.html` 为 redirect 文件，非原始 CV 内容
- [ ] `dist/zh/cv/index.html` 内容正常
