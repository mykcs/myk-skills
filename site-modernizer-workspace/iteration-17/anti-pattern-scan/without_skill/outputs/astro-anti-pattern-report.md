# Astro 反模式扫描与修复报告

**项目**: mock-anti-pattern-site  
**扫描日期**: 2026-05-15  
**Astro 版本**: ^5.0.0  
**来源**: Context7 /withastro/docs (官方文档)

---

## 发现清单

| # | 文件 | 反模式 | 严重度 | 状态 |
|---|------|--------|--------|------|
| 1 | `src/pages/index.astro` | `Astro.glob()` 已废弃 (v5 起废弃，v6 移除) | HIGH | 已修复 |
| 2 | `src/pages/index.astro` | `<ViewTransitions />` 已废弃 (v5 起废弃，v6 移除) | HIGH | 已修复 |
| 3 | `src/components/Gallery.astro` | `<Image format="..." />` 的 `format` 不是有效 prop | MED | 已修复 |
| 4 | `src/components/Gallery.astro` | 同一图片用 `format` 区分多格式，应使用 `<Picture>` | MED | 已修复 |
| 5 | `src/pages/index.astro` | `<html>` 根元素包裹 `<Layout>`，结构倒置 | LOW | 已修复 |
| 6 | `package.json` | `@astrojs/tailwind` + `tailwindcss@3` 为旧版组合 | INFO | 建议升级 |

---

## 详细说明与修复

### 1. `Astro.glob()` 废弃 (HIGH)

**位置**: `src/pages/index.astro:5`

**旧代码**:
```astro
const posts = await Astro.glob('./posts/*.md');
```

**问题**: Astro 5.0 起 `Astro.glob()` 被废弃，Astro 6.0 彻底移除。官方推荐 `import.meta.glob()`。

**修复后**:
```astro
const posts = Object.values(import.meta.glob('./posts/*.md', { eager: true }));
```

> 注意: `import.meta.glob()` 返回对象而非 Promise，需用 `Object.values()` 转数组。

---

### 2. `<ViewTransitions />` 废弃 (HIGH)

**位置**: `src/pages/index.astro:3, 11`

**旧代码**:
```astro
import { ViewTransitions } from 'astro:transitions';
<ViewTransitions />
```

**问题**: Astro 5.0 起 `<ViewTransitions>` 被废弃，Astro 6.0 彻底移除，替换为 `<ClientRouter>`。

**修复后**:
```astro
import { ClientRouter } from 'astro:transitions';
<ClientRouter />
```

---

### 3. `<Image>` 的 `format` prop 无效 (MED)

**位置**: `src/components/Gallery.astro:7-8`

**旧代码**:
```astro
<Image src={hero} format="webp" width={800} height={600} alt="Hero" />
<Image src={hero} format="avif" width={400} height={300} alt="Thumb" />
```

**问题**: Astro 内置 `Image` 组件不接受 `format` prop。该 prop 属于旧版 `@astrojs/image`（v3 已移除）。

**修复方案**: 若需多格式输出，应使用 `<Picture>` 组件，通过 `formats` 数组指定。

**修复后**:
```astro
import { Picture } from 'astro:assets';
<Picture src={hero} formats={['avif', 'webp']} width={800} height={600} alt="Hero" />
<Picture src={hero} formats={['avif', 'webp']} width={400} height={300} alt="Thumb" />
```

---

### 4. 同一图片多格式反模式 (MED)

**位置**: `src/components/Gallery.astro`

**问题**: 用两个 `<Image>` 分别输出 webp/avif 是错误做法。`<Picture>` 组件会生成 `<picture>` 标签，内含多 `<source>`，浏览器自动选择最优格式。

---

### 5. DOM 结构倒置 (LOW)

**位置**: `src/pages/index.astro:9-19`

**旧结构**:
```astro
<html>
  <head>...</head>
  <Layout>...</Layout>
</html>
```

**问题**: `<Layout>` 本身已包含 `<html>` / `<head>` / `<body>`，外部再包一层会导致嵌套错误。

**修复后**: 移除外层 `<html>`，`<ClientRouter />` 直接放入 `<Layout>` 的 slot 内容区（或移入 Layout 组件内部）。本次修复将 `<ClientRouter />` 放在 `<Layout>` 内部作为第一个子元素。

---

### 6. Tailwind v3 旧版组合 (INFO)

**位置**: `package.json`

**当前依赖**:
```json
"@astrojs/tailwind": "^5.1.0",
"tailwindcss": "^3.4.0"
```

**说明**: Tailwind v4 已发布，Astro 官方推荐新方案（`@tailwindcss/vite` 或直接 CSS import）。当前 v3 + `@astrojs/tailwind` 仍可工作，但属于旧版维护模式，建议未来升级。

---

## 验证结果

| 检查项 | 结果 |
|--------|------|
| `npx astro check` | 0 errors, 0 warnings, 0 hints |
| `npx astro build` | Build Complete! (1 page) |

---

## 建议后续行动

1. **评估 Tailwind v4 升级**: 参考 Astro 官方 `Remove @astrojs/tailwind integration` 指南。
2. **测试运行时行为**: 若项目有实际 Markdown 文件，验证 `import.meta.glob` 返回的 `url` 和 `frontmatter` 属性与旧 `Astro.glob` 一致。
3. **关注 Astro v6**: 当前修复已同时兼容 v5 和 v6（`ClientRouter`、`import.meta.glob`、`Picture` 均为 v6 标准 API）。
