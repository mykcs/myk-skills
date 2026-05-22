# i18n 同步审计与修复报告

## 发现问题

### 1. 键值未对齐（JSON 层面）
| 键 | en.json | zh.json | 状态 |
|---|---|---|---|
| nav.contact | 缺失 | 存在 | 已修复 |
| hero.cta | 缺失 | 存在 | 已修复 |
| footer.backToTop | 缺失 | 存在 | 已修复 |

### 2. 硬编码文本（组件层面）
| 文件 | 硬编码内容 | 修复方式 |
|---|---|---|
| Navbar.astro | "首页"、"关于我们"、"当前语言" | 引入 i18n JSON，动态读取 |
| Hero.astro | "欢迎"/"Welcome" 三元表达式、"这是一个演示网站"、"立即开始" | 统一从 i18n 读取 |
| [lang]/index.astro | "保留所有权利 © 2024"、Layout title 三元表达式 | 统一从 i18n 读取 |
| Layout.astro | `lang="zh"` 硬编码 | 改为接收 `lang` prop |

## 修复内容

1. **补全 en.json**：新增 `nav.contact`、`hero.cta`、`footer.backToTop` 三个缺失键。
2. **组件 i18n 化**：Navbar、Hero、[lang]/index 均引入对应语言 JSON，所有可见文本走 i18n。
3. **Layout 动态 lang**：`html lang` 属性从硬编码 `"zh"` 改为接收 `lang` prop，支持 `en`/`zh` 切换。
4. **导航链接语言前缀**：Navbar 链接改为 `/{lang}/` 格式，确保语言一致性。

## 验证结果

- `npm run build` 通过，无报错。
- 生成 `/en/index.html` 和 `/zh/index.html`，路由正常。

## 修改文件清单

- `src/content/i18n/en.json`
- `src/components/Navbar.astro`
- `src/components/Hero.astro`
- `src/pages/[lang]/index.astro`
- `src/layouts/Layout.astro`
