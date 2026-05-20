# Astro 反模式扫描报告

## 项目信息
- 路径: `/Users/myk/.claude/skills/site-modernizer-workspace/iteration-18/anti-pattern-scan/with_skill/mock-repo`
- Astro 版本: ^5.0.0
- 扫描日期: 2026-05-15

## 发现的问题与修复

### 1. `Astro.glob()` 已废弃 (P0)
- **位置**: `src/pages/index.astro:5`
- **问题**: `Astro.glob('./posts/*.md')` 在 Astro 5+ 中已废弃，构建报错 `AstroGlobNoMatch`
- **修复**: 迁移到 Content Collections
  - 创建 `src/content.config.ts` 定义 posts collection schema
  - 创建 `src/content/posts/hello.md` 和 `another.md` 样例内容
  - 使用 `getCollection('posts')` 替代 `Astro.glob`
  - 新增 `src/pages/posts/[slug].astro` 动态路由渲染文章

### 2. `ViewTransitions` 已废弃 (P0)
- **位置**: `src/pages/index.astro:3,11`
- **问题**: `import { ViewTransitions } from 'astro:transitions'` 在 Astro 4+ 中已废弃
- **修复**: 替换为 `ClientRouter`

### 3. `<Image format="...">` 反模式 (P1)
- **位置**: `src/components/Gallery.astro:7,8`
- **问题**: 显式指定 `format="webp"` / `format="avif"` 会覆盖 Sharp 自动优化
- **修复**: 移除 `format` 属性，让 Astro 5+ 的 Sharp 集成自动决定最佳格式
- **附加**: 为缩略图添加 `loading="lazy" decoding="async"`

### 4. `define:vars` 在 `<style>` 上 (P1)
- **位置**: `src/pages/index.astro:21`
- **问题**: `<style define:vars={{ themeColor }}>` 是旧模式，Astro 6 推荐直接用 CSS 自定义属性或静态值
- **修复**: 将 `themeColor` 内联为静态 `#3b82f6`

## 验证结果

| 检查项 | 状态 |
|--------|------|
| `npm run build` | 通过 (0 errors) |
| `npx astro check` | 通过 (0 errors, 0 warnings, 0 hints) |
| 构建输出 | `/index.html`, `/posts/hello/index.html`, `/posts/another/index.html` |

## 提交记录

```
d81dd6e refactor(site): migrate Astro.glob to Content Collections, replace ViewTransitions with ClientRouter, remove Image format props, fix define:vars anti-pattern
```

## 文件变更摘要

| 文件 | 操作 |
|------|------|
| `src/pages/index.astro` | 修改: Astro.glob → getCollection, ViewTransitions → ClientRouter, 移除 define:vars |
| `src/components/Gallery.astro` | 修改: 移除 format 属性, 添加 lazy loading |
| `src/content.config.ts` | 新增: Content Collection schema |
| `src/content/posts/hello.md` | 新增: 样例文章 |
| `src/content/posts/another.md` | 新增: 样例文章 |
| `src/pages/posts/[slug].astro` | 新增: 文章详情页路由 |
| `.gitignore` | 新增: 排除 node_modules, .astro, dist |
