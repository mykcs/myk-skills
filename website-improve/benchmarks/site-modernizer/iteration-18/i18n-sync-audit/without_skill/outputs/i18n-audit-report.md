# i18n 同步审计报告

**项目**: mock-i18n-site  
**日期**: 2026-05-15  
**状态**: 已修复并验证通过

---

## 一、发现的问题

### P0 - JSON 键值不对齐

`en.json` 与 `zh.json` 存在键缺失：

| 键路径 | en.json | zh.json |
|--------|---------|---------|
| `nav.contact` | **缺失** | "联系我们" |
| `hero.cta` | **缺失** | "立即开始" |
| `footer.backToTop` | **缺失** | "返回顶部" |

### P0 - 组件硬编码中文（未走 i18n 系统）

| 文件 | 位置 | 硬编码内容 | 影响 |
|------|------|-----------|------|
| `Hero.astro` | L6 | `<p>这是一个演示网站</p>` | 英文页仍显示中文 |
| `Hero.astro` | L7 | `<button>立即开始</button>` | 英文页仍显示中文 |
| `Navbar.astro` | L5 | `<a href="/">首页</a>` | 英文页仍显示中文，链接无语言前缀 |
| `Navbar.astro` | L6 | `<a href="/about/">关于我们</a>` | 与 `nav.about` 值不一致（"关于我们" vs "关于"），链接无语言前缀 |
| `[lang]/index.astro` | L16 | `<footer>保留所有权利 © 2024</footer>` | 英文页仍显示中文 |

### P1 - Layout 语言属性硬编码

| 文件 | 位置 | 问题 |
|------|------|------|
| `Layout.astro` | L5 | `<html lang="zh">` 硬编码，未接收 `lang` prop |

---

## 二、修复内容

### 1. 补全 en.json 缺失键

- `nav.contact` = "Contact"
- `hero.cta` = "Get Started"
- `footer.backToTop` = "Back to Top"

### 2. 组件改用 i18n JSON 驱动

- **Hero.astro**: 引入 `en.json` / `zh.json`，通过 `lang` prop 选择翻译对象，替换所有硬编码文本
- **Navbar.astro**: 引入 i18n JSON，链接改为模板字符串 `href={`/${lang}/`}`，翻译文本走 `t.nav.home` / `t.nav.about`
- **[lang]/index.astro**: 引入 i18n JSON，footer 文本改为 `t.footer.copyright`，并向 Layout 传递 `lang` prop

### 3. Layout 动态 lang 属性

- **Layout.astro**: 接收 `lang` prop，`<html lang={lang}>` 动态渲染

---

## 三、验证结果

`npm run build` 构建成功，3 页面生成无误。

### /zh/index.html 输出

```html
<html lang="zh">
  <title>演示站点</title>
  <nav>
    <a href="/zh/">首页</a>
    <a href="/zh/about/">关于</a>
    <span>当前语言: zh</span>
  </nav>
  <h1>欢迎</h1>
  <p>这是一个演示网站</p>
  <button>立即开始</button>
  <footer>保留所有权利 © 2024</footer>
```

### /en/index.html 输出

```html
<html lang="en">
  <title>Demo Site</title>
  <nav>
    <a href="/en/">Home</a>
    <a href="/en/about/">About</a>
    <span>Language: en</span>
  </nav>
  <h1>Welcome</h1>
  <p>This is a demo site</p>
  <button>Get Started</button>
  <footer>All rights reserved © 2024</footer>
```

---

## 四、修改文件清单

| 文件 | 操作 | 行数变化 |
|------|------|---------|
| `src/content/i18n/en.json` | 补全 3 个缺失键 | ~+3 |
| `src/components/Hero.astro` | 改用 i18n JSON | ~+4 |
| `src/components/Navbar.astro` | 改用 i18n JSON + 模板链接 | ~+5 |
| `src/pages/[lang]/index.astro` | 引入 i18n + 传 lang prop | ~+3 |
| `src/layouts/Layout.astro` | 接收 lang prop | ~+1 |

---

## 五、风险声明

1. **Navbar 链接**: `/zh/about/` 和 `/en/about/` 目前无对应页面文件，若用户访问会 404。建议补充 `src/pages/[lang]/about.astro`。
2. **i18n 配置与手动路由并存**: `astro.config.mjs` 中已配置 `i18n` 对象，但项目同时使用了手动 `[lang]` 动态路由。未来可考虑统一为 Astro 内置 i18n 路由，减少维护成本。
3. **内容集合警告**: 构建时提示 `src/content/i18n` 被自动生成为集合，建议显式定义 `src/content.config.ts` 以消除弃用警告。
