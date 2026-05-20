# 反模式发现报告

## 发现 1: ClientRouter 放置在 body 中（HIGH）
**位置**: `src/pages/index.astro`
**问题**: `<ClientRouter />` 被放在 `<Layout>` 的 body 区域内，而不是 `<head>` 中。
**依据**: Astro 官方文档明确要求 ClientRouter 必须放在 `<head>` 元素内才能正常工作。
**当前代码**:
```astro
<Layout>
  <ClientRouter />
  <h1>Old Site</h1>
```

## 发现 2: Image 组件使用了不必要的 `format` prop（MEDIUM）
**位置**: `src/components/Gallery.astro`
**问题**: 对本地导入的图片使用 `format="webp"` 和 `format="avif"`。当 `src` 是本地导入的图片对象时，Astro 会自动处理格式，手动指定 format 是多余的，且可能导致意外行为。
**当前代码**:
```astro
<Image src={hero} format="webp" width={800} height={600} alt="Hero" />
<Image src={hero} format="avif" width={400} height={300} alt="Thumb" />
```

## 发现 3: Layout 缺少 viewport meta 标签（MEDIUM）
**位置**: `src/layouts/Layout.astro`
**问题**: `<head>` 中缺少 `<meta name="viewport" content="width=device-width, initial-scale=1">`，现代网站必备。

## 发现 4: import.meta.glob 访问 `url` 和 `frontmatter` 的方式（LOW）
**位置**: `src/pages/index.astro`
**问题**: 代码使用了 `p.url` 和 `p.frontmatter.title`。虽然这在 `eager: true` 模式下对 Markdown 文件有效，但更好的做法是使用类型安全的 Content Collections（Astro v2+ 推荐）。不过考虑到项目规模，这不算严重反模式。

## 发现 5: @astrojs/tailwind 集成与 Tailwind v3 的组合（INFO）
**位置**: `package.json`, `astro.config.mjs`
**问题**: 项目使用 `@astrojs/tailwind` + Tailwind v3。这不是错误，但 Astro 社区正在向 Tailwind v4 迁移，v4 不再需要 `@astrojs/tailwind` 集成。由于用户没有要求升级 Tailwind，暂不处理。
