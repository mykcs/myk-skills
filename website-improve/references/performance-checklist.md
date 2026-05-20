# 性能检查清单

> 面向 Astro 静态站点的性能快速优化检查。聚焦可手动验证、可自动修复的项。

---

## 1. 图片优化

### 1.1 懒加载

**检测：**
```bash
grep -rn "<img" src/ --include="*.astro" | grep -v "loading=\"lazy\"\|loading=\"eager\""
```

**规则：**
- 首屏/hero 图片：`loading="eager"`（或省略，默认 eager）
- 其他所有图片：`loading="lazy" decoding="async"`

**修复：**
```astro
<!-- 首屏 -->
<img src="hero.png" alt="..." loading="eager" />

<!-- 下方内容 -->
<img src="figure1.png" alt="..." loading="lazy" decoding="async" />
```

### 1.2 使用 Astro `<Image />` 组件

```astro
---
import { Image } from 'astro:assets';
import myImage from '../assets/figure.png';
---

<!-- 自动优化、生成多尺寸 srcset -->
<Image src={myImage} alt="..." loading="lazy" />
```

**检测未使用 `<Image />` 的地方：**
```bash
grep -rn '<img src="/' src/ --include="*.astro"
```

---

## 2. 字体优化

### 2.1 禁止 Google Fonts CDN

**检测：**
```bash
grep -r "fonts.googleapis.com\|fonts.gstatic.com" src/ public/
```

**修复：** 使用 `@fontsource/*`
```bash
npm install @fontsource/inter
```

```astro
---
import '@fontsource/inter/400.css';
import '@fontsource/inter/700.css';
---
```

### 2.2 字体预加载关键 weight

```html
<link rel="preload" href="/fonts/inter-400.woff2" as="font" type="font/woff2" crossorigin />
```

---

## 3. CSS 优化

### 3.1 关键 CSS 内联

Astro + Tailwind v4 的 `build-pipeline` integration 已自动内联 CSS。验证：

```bash
grep -c '<style>' dist/index.html
grep -c '<link rel="stylesheet"' dist/index.html
```

### 3.2 移除未使用 CSS

Tailwind v4 的 JIT 模式已自动处理。如使用自定义 CSS，检查：

```bash
grep -rn "@apply" src/ --include="*.css" --include="*.astro"
```

---

## 4. JavaScript 优化

### 4.1 Islands 架构审查

```bash
grep -rn "client:load\|client:idle\|client:visible" src/ --include="*.astro"
```

**评估：**
- `client:load` — 是否真的需要立即 hydrate？
- `client:idle` — 是否可以降级为 `client:visible`？
- 无交互的组件 — 是否可以移除 client directive（纯静态）？

### 4.2 第三方脚本延迟

```bash
grep -rn "<script" src/ --include="*.astro" | grep -v "type=\"module\""
```

外部脚本应使用 `async` 或 `defer`：
```html
<script async src="https://analytics.com/script.js"></script>
```

---

## 5. 构建输出检查

### 5.1 资源大小

```bash
du -sh dist/
find dist/ -name "*.js" -exec ls -lh {} \; | sort -k5 -rh | head -10
find dist/ -name "*.css" -exec ls -lh {} \; | sort -k5 -rh | head -10
```

### 5.2 HTML 压缩

Astro 生产构建自动压缩。验证：
```bash
head -c 200 dist/index.html | cat -v
```
无多余空格 = 已压缩。

---

## 6. Lighthouse 关键指标

| 指标 | 目标 |
|------|------|
| LCP (Largest Contentful Paint) | ≤ 2.5s |
| FID (First Input Delay) / INP | ≤ 100ms |
| CLS (Cumulative Layout Shift) | ≤ 0.1 |
| TTFB (Time to First Byte) | ≤ 600ms |

**运行：**
```bash
npm run build
npm run preview
# 另开终端
npx lighthouse http://localhost:4321 --output=html --output-path=./lighthouse-report.html
```

---

## 7. 快速扫描脚本

```bash
#!/bin/bash
echo "=== Performance Quick Scan ==="

echo "--- Images without lazy (excl. hero) ---"
grep -rn "<img" src/ --include="*.astro" | grep -v "loading=\"lazy\"\|loading=\"eager\"" || echo "PASS"

echo "--- Google Fonts CDN ---"
grep -r "fonts.googleapis.com\|fonts.gstatic.com" src/ public/ || echo "PASS"

echo "--- Unused deps ---"
for pkg in lodash moment jquery; do
  grep -r "from ['\"]$pkg['\"]" src/ || echo "$pkg: unused or N/A"
done

echo "--- Client directives ---"
grep -rn "client:load\|client:idle\|client:visible" src/ --include="*.astro"

echo "--- Build size ---"
du -sh dist/ 2>/dev/null || echo "No dist/ yet"
```
