# 5 维度快速检查清单

> 本清单供 `website-improve` skill 快速扫描使用。每项检测命令可直接运行。

---

## 代码质量 (Code Quality)

| # | 检查项 | 命令 | 通过标准 |
|---|--------|------|----------|
| 1 | Astro 类型检查 | `npx astro check` | 0 errors, 0 warnings |
| 2 | 重复页面 | `ls src/pages/cv.astro src/pages/[lang]/cv.astro 2>/dev/null` | 不同时存在 |
| 3 | 废弃 API | `grep -rn "Astro.glob\|ViewTransitions" src/ --include="*.astro"` | 无结果 |
| 4 | 未使用依赖 | 检查 `package.json` 中无零导入的包 | 无 |
| 5 | lock 文件一致 | 仅一种 lock 文件存在 | 是 |

---

## 性能 (Performance)

| # | 检查项 | 命令 | 通过标准 |
|---|--------|------|----------|
| 1 | 图片懒加载 | `grep -rn "<img" src/ --include="*.astro" | grep -v "loading=\"lazy\"\|loading=\"eager\""` | 仅首屏图片可无 lazy |
| 2 | CDN 字体 | `grep -r "fonts.googleapis.com\|fonts.gstatic.com" src/ public/` | 无结果 |
| 3 | 未使用依赖 | `for pkg in lodash moment jquery; do grep -r "from ['\"]$pkg['\"]" src/ || echo "$pkg unused"; done` | 无不使用的 |
| 4 | Prefetch 配置 | `grep -A3 "prefetch" astro.config.mjs` | 已配置 |
| 5 | CSS 阻塞 | `grep -c '<link rel="stylesheet"' dist/index.html` | ≤ 1（内联后） |

---

## 可访问性 (a11y)

| # | 检查项 | 命令 | 通过标准 |
|---|--------|------|----------|
| 1 | 图片 alt | `grep -rn "<img" src/ --include="*.astro" | grep -v "alt=" | grep -v "decorative"` | 无结果 |
| 2 | Input label | `grep -rn "<input" src/ --include="*.astro" | grep -v "aria-label\|aria-labelledby\|<label"` | 无结果 |
| 3 | Focus 可见 | `grep -rn "outline: none\|outline:none" src/ --include="*.css" --include="*.astro"` | 无结果，或有 `:focus-visible` 恢复 |
| 4 | 语义化标题 | `grep -rn "<h1" src/ --include="*.astro" | wc -l` | 每页 1 个 |
| 5 | lang 属性 | `grep -rn '<html lang=' src/layouts/ --include="*.astro"` | 存在且正确 |

---

## 安全 (Security)

| # | 检查项 | 命令 | 通过标准 |
|---|--------|------|----------|
| 1 | set:html 审计 | `grep -rn "set:html" src/ --include="*.astro"` | 有则标记审查 |
| 2 | 硬编码 secrets | `grep -rni "api_key\|apikey\|secret\|token\|password" src/ --include="*.astro" --include="*.ts" | grep -v "process.env\|import.meta.env"` | 无结果 |
| 3 | npm audit | `npm audit --audit-level=moderate` | 0 HIGH/CRITICAL |
| 4 | .env 忽略 | `grep "\.env" .gitignore` | 存在 |
| 5 | 依赖 CVE | `npm audit --json 2>/dev/null | grep -c "severity":"critical"` | 0 |

---

## 布局/视觉 (Layout)

| # | 检查项 | 命令 | 通过标准 |
|---|--------|------|----------|
| 1 | 水平溢出 | Playwright: `document.body.scrollWidth <= window.innerWidth` | 4 个 viewport 均通过 |
| 2 | 控制台错误 | Playwright: 监听 `pageerror` | 0 Error |
| 3 | FOUC | 首屏截图对比刷新前后 | 无闪烁 |
| 4 | 跨浏览器 | Chromium + WebKit 截图对比 | 一致 |
| 5 | 响应式 | 375/768/1280/1920 截图 | 无元素重叠/截断 |
