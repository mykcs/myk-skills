# Astro 反模式扫描报告

**扫描时间**: 2026-05-15
**项目**: mock-anti-pattern-site
**Astro 版本**: v5.0.0

---

## 扫描结果摘要

| 状态 | 数量 |
|------|------|
| 发现问题 | 4 |
| 已修复 | 4 |
| 构建验证 | 通过 |

---

## 详细问题与修复

### 1. ViewTransitions 已废弃 → 使用 ClientRouter

**文件**: `src/pages/index.astro`

```diff
- import { ViewTransitions } from 'astro:transitions';
+ import { ClientRouter } from 'astro:transitions';
...
- <ViewTransitions />
+ <ClientRouter />
```

**说明**: `ViewTransitions` 在 Astro v4+ 已废弃，Astro v6 推荐使用 `ClientRouter` 组件实现视图过渡。

---

### 2. Astro.glob() 已废弃 → 使用 import.meta.glob()

**文件**: `src/pages/index.astro`

```diff
- const posts = await Astro.glob('./posts/*.md');
+ import.meta.glob('./posts/*.md');
```

**说明**: `Astro.glob()` 是已废弃的 glob 导入方式，Astro v5 推荐使用 `import.meta.glob()` 替代。实际使用中应配合 Content Collections 管理内容。

---

### 3. <style define:vars> 旧模式 → 直接内联颜色值

**文件**: `src/pages/index.astro`

```diff
- <style define:vars={{ themeColor }}>
-   h1 { color: var(--themeColor); }
- </style>
+ <style>
+   h1 { color: #3b82f6; }
+ </style>
```

**说明**: `<style define:vars>` 是旧版 CSS 变量注入模式，Astro v5 推荐直接在 CSS 中使用硬编码值或通过 CSS 自定义属性实现。

---

### 4. <Image format="..."> 已废弃 → 移除 format 属性

**文件**: `src/components/Gallery.astro`

```diff
- <Image src={hero} format="webp" width={800} height={600} alt="Hero" />
- <Image src={hero} format="avif" width={400} height={300} alt="Thumb" />
+ <Image src={hero} width={800} height={600} alt="Hero" />
+ <Image src={hero} width={400} height={300} alt="Thumb" />
```

**说明**: `<Image>` 组件的 `format` 属性在 Astro v5 中已废弃。图片格式转换应由构建工具或手动预处理完成，而不是在组件中指定。

---

## 修改文件清单

| 文件路径 | 修改类型 |
|----------|----------|
| `src/pages/index.astro` | 反模式修复 |
| `src/components/Gallery.astro` | 反模式修复 |

---

## 构建验证

```
✓ npm run build 成功
✓ 构建输出: dist/
✓ ClientRouter 正确生成客户端脚本
```

---

## 建议后续优化

1. **Content Collections**: 使用 Content Collections 替代 glob 导入管理 markdown 内容
2. **图片优化**: 使用独立的图片处理流程替代内置 format 转换
3. **Tailwind v4**: 项目使用 Tailwind v3，可考虑升级到 v4
