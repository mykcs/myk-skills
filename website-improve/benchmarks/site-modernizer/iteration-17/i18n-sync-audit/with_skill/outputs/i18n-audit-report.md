# i18n 审计报告

## 发现的问题

### 1. JSON key 不同步（P0）
- `en.json` 缺少 `nav.contact`、`hero.cta`、`footer.backToTop`
- `zh.json` 缺少 `nav.contact`（后续统一补齐）
- 两文件 key 集合不一致，会导致英文页面 fallback 到 raw key

### 2. 条件渲染硬编码（P0）
- `Hero.astro:5`：`{lang === 'zh' ? '欢迎' : 'Welcome'}`
- `[lang]/index.astro:12`：`title={lang === 'zh' ? '演示站点' : 'Demo Site'}`
- 违反 site-modernizer i18n 反模式规则：所有双语文本必须走 `t()`

### 3. 组件内硬编码中文（P1）
- `Hero.astro`：`<p>这是一个演示网站</p>`、`<button>立即开始</button>`
- `Navbar.astro`：`<a href="/">首页</a>`、`<a href="/about/">关于我们</a>`、`<span>当前语言: {lang}</span>`
- `Layout.astro`：`<html lang="zh">` 固定语言
- `[lang]/index.astro`：`<footer>保留所有权利 © 2024</footer>`

## 修复内容

1. **补齐 key**：两 JSON 文件现拥有完全一致的 key 集合
2. **新增 `src/lib/i18n.ts`**：极简 `t(key, lang)` helper，支持点号路径
3. **消除所有条件渲染**：`Hero.astro`、`[lang]/index.astro` 中的 `lang === 'zh'` 已替换为 `t()`
4. **消除所有硬编码 UI 文本**：Navbar、Hero、index 页面全部使用 `t()`
5. **Layout 语言属性**：已改为动态 `lang={lang}`

## 验证结果

- `grep -rn "lang ===" src/` → 零匹配
- `diff` 顶层/二层 key → 无差异
- `npm run build` → 通过（3 pages built）
- `git log --oneline -1` → `9909122 fix(i18n): sync en/zh keys, replace conditionals with t() helper`

## 状态

| 检查项 | 状态 |
|--------|------|
| en/zh key 同步 | 通过 |
| 条件渲染清零 | 通过 |
| 硬编码文本清零 | 通过 |
| 构建通过 | 通过 |
| 已提交 | 通过 |
