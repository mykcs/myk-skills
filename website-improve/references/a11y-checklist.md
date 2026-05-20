# a11y 检查清单 (WCAG 2.2 AA 精简版)

> 面向 Astro 静态站点的可访问性快速检查，覆盖最常见问题。

---

## 1. 图片 (Images)

### 1.1 所有 `<img>` 必须有 `alt`

```bash
grep -rn "<img" src/ --include="*.astro" | grep -v "alt=" | grep -v "decorative"
```

**通过标准：** 无结果。

**修复：**
```astro
<!-- 信息性图片 -->
<img src="..." alt="论文方法示意图：GDKVM 架构概览" />

<!-- 装饰性图片 -->
<img src="..." alt="" role="presentation" />
```

### 1.2 复杂图表需长描述

如果图片包含数据图表，提供 `<figure>` + `<figcaption>` 或 `aria-describedby` 指向详细描述。

---

## 2. 表单 (Forms)

### 2.1 每个 `<input>` 有关联标签

```bash
grep -rn "<input" src/ --include="*.astro" | grep -v "aria-label\|aria-labelledby\|<label"
```

**修复：**
```astro
<!-- 显式 label -->
<label for="email">邮箱</label>
<input id="email" type="email" />

<!-- 或隐式包裹 -->
<label>
  邮箱
  <input type="email" />
</label>

<!-- 或 aria-label -->
<input type="search" aria-label="搜索论文" />
```

### 2.2 错误提示可访问

错误信息需关联到输入框：
```astro
<input aria-describedby="email-error" aria-invalid="true" />
<span id="email-error" role="alert">请输入有效邮箱</span>
```

---

## 3. 键盘导航 (Keyboard)

### 3.1 所有交互元素可 Tab 聚焦

- `<a>`、`<button>`、`<input>` 天然可聚焦
- 自定义组件需 `tabindex="0"` 和 `keydown` 处理

### 3.2 无键盘陷阱

Tab 顺序应自然流动，不陷入无法退出的组件。

### 3.3 Focus 指示器可见

```bash
grep -rn "outline: none\|outline:none" src/ --include="*.css" --include="*.astro"
```

**禁止裸 `outline: none`。** 如需自定义：
```css
:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}
```

---

## 4. 颜色与对比度 (Color & Contrast)

### 4.1 文本对比度 ≥ 4.5:1

| 场景 | 比例 |
|------|------|
| 正常文本 (< 18pt) | 4.5:1 |
| 大文本 (≥ 18pt bold / 24pt) | 3:1 |
| UI 组件（按钮边框等） | 3:1 |

**检测工具：**
- DevTools → Lighthouse → Accessibility
- 在线工具：https://webaim.org/resources/contrastchecker/

### 4.2 不单独用颜色传递信息

错误状态不应只用红色，需配合图标或文字：
```astro
<!-- 错误 -->
<span class="text-red-500">必填</span>

<!-- 正确 -->
<span class="text-red-500" aria-label="错误">⚠ 必填</span>
```

---

## 5. 语义化 HTML (Semantics)

### 5.1 每页一个 `<h1>`

```bash
grep -rn "<h1" src/pages/ --include="*.astro" | wc -l
```

### 5.2 标题层级不跳级

`<h1>` → `<h2>` → `<h3>`，不跳过。

### 5.3 使用地标元素

```astro
<header>  <!-- 而非 <div class="header"> -->
<nav>
<main>
<footer>
<aside>
```

### 5.4 lang 属性正确

```astro
<html lang={lang}>  <!-- zh / en -->
```

---

## 6. 动态内容 (Dynamic Content)

### 6.1 页面标题更新

路由切换后更新 `<title>`，供屏幕阅读器朗读。

### 6.2 状态变化通知

使用 `aria-live` 区域通知动态内容：
```astro
<div aria-live="polite" aria-atomic="true">
  {statusMessage}
</div>
```

---

## 7. 精简 a11y 检测脚本

```bash
#!/bin/bash
echo "=== a11y Quick Scan ==="
echo "--- Images without alt ---"
grep -rn "<img" src/ --include="*.astro" | grep -v "alt=" | grep -v "decorative" || echo "PASS"

echo "--- Inputs without label ---"
grep -rn "<input" src/ --include="*.astro" | grep -v "aria-label\|aria-labelledby\|<label" || echo "PASS"

echo "--- Outline none ---"
grep -rn "outline: none\|outline:none" src/ --include="*.css" --include="*.astro" || echo "PASS"

echo "--- Multiple h1 ---"
find src/pages -name "*.astro" -exec sh -c 'count=$(grep -c "<h1" "$1"); [ "$count" -gt 1 ] && echo "$1: $count h1"' _ {} \;
```
