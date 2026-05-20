---
name: website-improve
description: |
  综合性网站健康快速改进 skill。覆盖代码质量、性能、a11y、安全、布局/视觉 5 个维度。
  用户说"改进网站"、"website-improve"、"audit website"、"优化网站"时触发。
  定位为轻量快速入口（5-15min），深度问题委托给 rich-audit / site-modernizer。
license: MIT
metadata:
  version: "1.0.0"
  author: mykcs
  category: web-development
  triggers:
    - website-improve
    - 改进网站
    - 优化网站
    - audit website
    - 网站审计
    - 网站检查
    - improve site
    - site health
  tags:
    - audit
    - improve
    - astro
    - performance
    - a11y
    - security
    - layout
    - checklist
user-invocable: true
disable-model-invocation: true
---

# website-improve Skill

## 触发方式

- `website-improve`
- `改进网站`
- `优化网站`
- `audit website`
- `网站审计`
- `网站检查`
- `improve site`
- `site health`

---

## 定位

| Skill | 适用场景 |
|-------|---------|
| `rich-audit` | 深度三层进化审计（配置 + Astro + Python，30min+） |
| `site-modernizer` | 大规模重构、现代化、反模式扫描、项目页创建 |
| **`website-improve`** | **快速定向改进（5-15min），5 维度健康检查** |

本 skill 是轻量入口，**不替代**上述 skill，而是与之联动：
- 发现深层架构问题 → 建议调用 `rich-audit`
- 发现需大规模重构 → 建议调用 `site-modernizer`
- 发现 Astro 建站问题 → 建议调用 `publishing-astro-websites`

---

## 执行流程

```
User: "改进网站" / "website-improve"
  |
  v
[1] 意图识别
    用户是否指定了维度？
    ├─ 是 → 只跑该维度（如"只检查a11y"）
    └─ 否 → 跑全量快速扫描
  |
  v
[2] 快速扫描（5 维度）
    ├─ 代码质量: npx astro check, ESLint, TS 错误
    ├─ 性能: 图片懒加载、关键CSS、未使用依赖
    ├─ a11y: alt 文本、label、对比度、键盘导航
    ├─ 安全: set:html 审计、npm audit、secrets 扫描
    └─ 布局: Playwright 响应式溢出检测
  |
  v
[3] 问题分级（P0 / P1 / P2）
  |
  v
[4] 自动修复（安全、无破坏性的）
  |
  v
[5] 验证 → npm run build + 回归检查
  |
  v
[6] 报告 + 人工处理建议
```

---

## 5 维度快速扫描

### 维度 1：代码质量 (Code Quality)

**检测命令：**
```bash
# Astro 类型检查
npx astro check

# ESLint（如配置）
npx eslint src/ --ext .astro,.ts,.js

# 未使用依赖
deptree=$(npm ls --depth=0 2>/dev/null | tail -n +2)
echo "$deptree"
```

**检查项：**
| 项 | 通过标准 |
|---|---|
| `astro check` 0 errors | 无 TypeScript / 类型错误 |
| `astro check` 0 warnings | 无警告 |
| 无重复页面 | 不存在 `/cv.astro` + `/[lang]/cv.astro` 并存 |
| 无 `Astro.glob` | 已替换为 Content Collections 或 `import.meta.glob` |
| `package.json` 无废弃依赖 | 无 `@astrojs/tailwind`（v4 用 `@tailwindcss/vite`） |

**自动修复：**
- 删除重复页面（保留 `[lang]/` 版本）
- 添加 `Astro.redirect()` 到旧路径

---

### 维度 2：性能 (Performance)

详见 [references/performance-checklist.md](references/performance-checklist.md)

**核心检查：**
| 项 | 通过标准 |
|---|---|
| 非首屏图片有 `loading="lazy"` | 仅首屏图片除外 |
| 无 Google Fonts CDN `<link>` | 使用 `@fontsource/*` 本地字体 |
| 无未使用依赖 | `lodash`/`moment`/`jquery` 等未导入 |
| CSS 已内联或关键 CSS 已提取 | 无 render-blocking 外链 CSS |
| `prefetch` 配置正确 | `astro.config.mjs` 中 `prefetch: { prefetchAll: true }` |

**自动修复：**
- 给非首屏 `<img>` 添加 `loading="lazy" decoding="async"`
- 卸载未使用依赖

---

### 维度 3：可访问性 (a11y)

详见 [references/a11y-checklist.md](references/a11y-checklist.md)

**核心检查：**
| 项 | 通过标准 |
|---|---|
| 所有 `<img>` 有 `alt` | 无空 alt（除非装饰性） |
| 所有 `<input>` 有关联 `<label>` | 或通过 `aria-labelledby` |
| 颜色对比度 ≥ 4.5:1 | WCAG AA 标准 |
| 键盘可导航 | Tab 顺序合理，focus 可见 |
| 无 `outline: none` | 或仅在 `:focus-visible` 下恢复 |

**自动修复：**
- 给缺失 `alt` 的 `<img>` 添加描述（需用户确认内容）
- 给无 label 的 input 添加 `<label>`

---

### 维度 4：安全 (Security)

详见 [references/security-checklist.md](references/security-checklist.md)

**核心检查：**
| 项 | 通过标准 |
|---|---|
| `set:html` 使用审计 | 仅用于可信内容，无用户输入拼接 |
| 无硬编码 secrets | `.env` / GitHub Secrets 管理 |
| `npm audit` 无 HIGH/CRITICAL | 或已评估并记录例外 |
| 无 `dangerouslySetInnerHTML` 等效 | Astro 中即 `set:html` |
| 依赖无已知 CVE | `npm audit --audit-level=moderate` |

**自动修复：**
- 标记 `set:html` 位置供人工审查
- 运行 `npm audit fix` 处理无破坏性更新

---

### 维度 5：布局/视觉 (Layout & Visual)

**核心检查：**
| 项 | 通过标准 |
|---|---|
| 无水平溢出 | 375px / 768px / 1280px / 1920px 均通过 |
| 跨浏览器一致 | Chromium + WebKit 双端验证 |
| 无 FOUC | 首屏无未样式内容闪烁 |
| 响应式断点正常 | 导航、网格、字体大小适配 |
| 无控制台 Error | 零 Error-level 日志 |

**检测命令（Playwright）：**
```bash
# 水平溢出检测
page.evaluate(() => document.body.scrollWidth <= window.innerWidth)

# 控制台错误检测
page.on('pageerror', err => console.log('ERROR:', err.message))
```

**自动修复：**
- 标记溢出元素供人工处理（布局修复通常需人工判断）

---

## 输出格式

每维度报告格式：

```
## 维度: 代码质量
- 状态: PASS / WARN / FAIL
- 得分: X/5

### 发现项
| 优先级 | 问题 | 位置 | 建议动作 |
|--------|------|------|----------|
| P0 | astro check 报错 | src/pages/cv.astro:23 | 修复类型错误 |
| P1 | 未使用依赖 `lodash` | package.json | npm uninstall lodash |

### 自动修复已应用
- [x] 删除重复页面 `/cv.astro`
- [ ] 类型错误需人工修复（见上）
```

---

## 联动规则

触发以下情况时，建议调用对应 skill：

| 发现 | 推荐联动 |
|------|---------|
| 架构规则冲突 ≥ 3 处 | `rich-audit` |
| 需 Astro v6 迁移 / Tailwind v4 迁移 | `site-modernizer` |
| 需创建/重构项目页 | `site-modernizer` |
| 需部署/建站指导 | `publishing-astro-websites` |
| CI 持续失败、hook 错误 | `rich-audit` |

---

## 非协商规则

1. **不破坏构建**：任何修改后必须 `npm run build` 通过
2. **安全优先**：`set:html` / secrets 问题标记为 P0，不自动修复
3. **中英同步**：a11y 修复涉及 UI 文本时，同步更新 en.json / zh.json
4. **验证门禁**：声明完成前，粘贴 `npm run build` 最后 5 行输出 + `git log --oneline -1`
5. **Commit 必须**：修改文件后必须 `smart-autopush.sh` 提交
