# 修复操作记录

## 修复 1: ClientRouter 移至 head（HIGH）
**文件**: `src/pages/index.astro`, `src/layouts/Layout.astro`
**问题**: `ClientRouter` 被放置在 body 区域，违反 Astro 官方文档要求。
**修复**:
- 在 `Layout.astro` 的 `<head>` 中添加 `<slot name="head" />`
- 在 `index.astro` 中使用 `<Fragment slot="head">` 将 `ClientRouter` 注入到 head 中
**验证**: 构建成功，生成的 HTML 中 `<script>` 标签位于 `<head>` 内。

## 修复 2: 移除 Image 组件多余的 `format` prop（MEDIUM）
**文件**: `src/components/Gallery.astro`
**问题**: 对本地导入的图片使用 `format="webp"` / `format="avif"` 是多余的，Astro 会自动优化。
**修复**: 移除 `format` 属性，保留 `width`, `height`, `alt`, `loading`。
**验证**: 构建成功，图片仍被优化为 webp 格式（Astro 默认行为）。

## 修复 3: 补充缺失的 assets 文件（BLOCKER）
**文件**: `src/assets/hero.png`
**问题**: `Gallery.astro` 引用了不存在的 `../assets/hero.png`，导致构建失败。
**修复**: 使用 Python 生成一个最小有效 PNG 文件放置到 `src/assets/hero.png`。
**验证**: 构建通过，图片优化流程正常执行。

## 未修复项
- **Tailwind v3 → v4 升级**: 用户未要求，且涉及较大变更（需移除 `@astrojs/tailwind` 集成）。
- **Content Collections 迁移**: 项目规模极小，`import.meta.glob` 当前写法可接受。
