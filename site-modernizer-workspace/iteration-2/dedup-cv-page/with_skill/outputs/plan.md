# 清理重复 CV 页面执行计划

## 目标

- 删除纯中文页面 `src/pages/cv.astro`
- 保留双语页面 `src/pages/[lang]/cv.astro`
- 用户访问 `/cv/` 时自动跳转到 `/zh/cv/`

## 现状分析

### 文件清单

| 文件 | 作用 |
|------|------|
| `src/pages/cv.astro` | 纯中文 CV，硬编码 `lang = 'zh'` |
| `src/pages/[lang]/cv.astro` | 双语 CV，支持 `en` 和 `zh` |
| `src/components/CvContent.astro` | CV 内容组件，接收 `lang` props |
| `src/layouts/Layout.astro` | 布局组件，接收 `lang` props |
| `astro.config.mjs` | Astro 配置，当前 `prefixDefaultLocale: false` |

### 关键配置现状

```js
// astro.config.mjs
i18n: {
  locales: ['en', 'zh'],
  defaultLocale: 'zh',
  prefixDefaultLocale: false,
  routing: {
    prefixDefaultLocale: false,
  },
}
```

当前配置下：
- `/cv/` → 由 `src/pages/cv.astro` 生成（纯中文）
- `/zh/cv/` → 由 `src/pages/[lang]/cv.astro` 生成（中文）
- `/en/cv/` → 由 `src/pages/[lang]/cv.astro` 生成（英文）

## 方案选型

Astro 的 `redirects` 配置可以将旧路由映射到新路由。对于静态导出站点，它会生成带有 `<meta http-equiv="refresh">` 的 HTML 文件。

**注意**：Astro 文档明确指出，redirects 的优先级低于同名的实际页面文件。因此如果 `src/pages/cv.astro` 存在，`/cv/` 的 redirect 不会生效。必须先删除该文件。

## 执行步骤

### Step 1: 删除重复页面

```bash
rm src/pages/cv.astro
```

### Step 2: 添加 redirect 配置

编辑 `astro.config.mjs`，在 `defineConfig` 中添加 `redirects`：

```js
import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';

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
  redirects: {
    '/cv': '/zh/cv',
    '/cv/': '/zh/cv/',
  },
  vite: {
    plugins: [tailwindcss()],
  },
});
```

### Step 3: 验证构建

```bash
npm run build
```

### Step 4: 验证输出

检查 `dist/` 目录：

```bash
ls -la dist/cv.html        # 应存在，且包含 meta refresh 跳转
ls -la dist/zh/cv.html     # 应存在
ls -la dist/en/cv.html     # 应存在
```

确认 `dist/cv.html` 中包含：

```html
<meta http-equiv="refresh" content="0;url=/zh/cv/">
```

### Step 5: 验证预览（可选）

```bash
npm run preview
```

用浏览器或 curl 访问 `http://localhost:4321/cv/`，确认 302/200 跳转到 `/zh/cv/`。

## 风险与边界

| 风险 | 缓解措施 |
|------|---------|
| 其他页面有链接指向 `/cv/` | 无需修改，redirect 会自动处理 |
| SEO 影响 | Astro 静态 redirect 使用 meta refresh，搜索引擎会跟随跳转 |
| `/cv` 和 `/cv/` 尾部斜杠 | 同时配置两条 redirect，覆盖两种情况 |
| `prefixDefaultLocale: false` 不变 | 保持现有行为，仅增加 redirect，不改动 i18n 路由策略 |

## 验收标准

- [ ] `src/pages/cv.astro` 已删除
- [ ] `astro.config.mjs` 已添加 `/cv` → `/zh/cv` redirect
- [ ] `npm run build` 成功
- [ ] `dist/cv.html` 存在且包含 meta refresh 到 `/zh/cv/`
- [ ] `dist/zh/cv.html` 和 `dist/en/cv.html` 正常生成
