# 初始代码库评估

## 项目概况

- **框架**: Astro v5 (package.json 声明 `^5.0.0`，实际安装 v6.3.2)
- **构建输出**: static
- **集成**: `@astrojs/tailwind` + Tailwind CSS v3
- **页面数量**: 1 页 (`src/pages/index.astro`)
- **组件数量**: 1 个 (`src/components/Gallery.astro`)
- **布局数量**: 1 个 (`src/layouts/Layout.astro`)

## 文件清单

```
src/
  components/
    Gallery.astro
  layouts/
    Layout.astro
  pages/
    index.astro
astro.config.mjs
package.json
```

## 初步观察

1. `Gallery.astro` 引用了 `../assets/hero.png`，但 `src/assets/` 目录不存在。
2. `index.astro` 使用了 `Astro.glob()`，该 API 在 Astro 5 中已标记为 deprecated。
3. `index.astro` 使用了 `ViewTransitions`，该组件在 Astro 6 中已被 `ClientRouter` 取代。
4. `index.astro` 在 `<html>` 标签内嵌套 `<Layout>`，这是反模式（Layout 应该包裹页面内容，而不是被放在 html 内部）。
5. `@astrojs/tailwind` + Tailwind v3 是旧组合，Astro 5.2+ 推荐 Tailwind v4 + `astro add tailwind`。
