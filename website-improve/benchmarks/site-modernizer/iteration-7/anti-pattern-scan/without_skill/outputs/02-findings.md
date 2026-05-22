# 反模式与过时写法发现

## P0 - 构建失败级

### 1. `Astro.glob()` 已废弃
- **位置**: `src/pages/index.astro:5`
- **问题**: `const posts = await Astro.glob('./posts/*.md');`
- **影响**: Astro 5 中 deprecated，Astro 6 中已移除；当前构建直接报错 `AstroGlobNoMatch`
- **修复**: 替换为 `Object.values(import.meta.glob('./posts/*.md', { eager: true }))`

### 2. `ViewTransitions` 已移除
- **位置**: `src/pages/index.astro:3, 11`
- **问题**: `import { ViewTransitions } from 'astro:transitions';` + `<ViewTransitions />`
- **影响**: Astro 6 中已完全移除，替换为 `ClientRouter`
- **修复**: 改为 `import { ClientRouter } from 'astro:transitions';` + `<ClientRouter />`

### 3. Layout 嵌套在 `<html>` 内部
- **位置**: `src/pages/index.astro:9-18`
- **问题**: 页面自己写了 `<html>` 并在其中放 `<Layout>`，而 `Layout.astro` 本身已经包含 `<!DOCTYPE html>` 和 `<html>` 标签
- **影响**: 产生嵌套 `<html>` 标签，HTML 结构非法
- **修复**: 移除页面中的 `<html>`/`<head>`，让 `<Layout>` 作为根元素包裹内容

## P1 - 警告级

### 4. `format` prop 在 `<Image>` 上已废弃
- **位置**: `src/components/Gallery.astro:7-8`
- **问题**: `<Image src={hero} format="webp" ... />` 和 `format="avif"`
- **影响**: Astro Image 组件不再支持 `format` prop，格式由内部自动处理
- **修复**: 移除 `format` 属性

### 5. `@astrojs/tailwind` + Tailwind v3 组合过时
- **位置**: `package.json`
- **问题**: 使用 `@astrojs/tailwind` 集成和 `tailwindcss@3`
- **影响**: Astro 5.2+ 官方推荐 Tailwind v4，使用 `@tailwindcss/vite` 插件，不再需要 `@astrojs/tailwind`
- **修复**: 升级到 Tailwind v4 并移除 `@astrojs/tailwind`

## P2 - 建议级

### 6. 引用的图片资源不存在
- **位置**: `src/components/Gallery.astro:3`
- **问题**: `import hero from '../assets/hero.png';` 但 `src/assets/` 目录不存在
- **影响**: 构建时若该组件被使用会报错；当前未被 `index.astro` 引用所以未触发
- **修复**: 补充图片资源或移除该组件引用

## 修复优先级总结

| 优先级 | 问题 | 文件 |
|--------|------|------|
| P0 | Astro.glob() deprecated | `src/pages/index.astro` |
| P0 | ViewTransitions 已移除 | `src/pages/index.astro` |
| P0 | Layout 嵌套在 html 内 | `src/pages/index.astro` |
| P1 | Image format prop 废弃 | `src/components/Gallery.astro` |
| P1 | Tailwind v3 组合过时 | `package.json` |
| P2 | 图片资源缺失 | `src/components/Gallery.astro` |
