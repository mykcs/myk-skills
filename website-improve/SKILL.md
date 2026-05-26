---
name: website-improve
description: |
  一站式网站改进 skill。覆盖检查+提升、Astro 建站、项目页创建三大场景。
  所有"改进/审计/优化/检查/upgrade/modernize/重构/cleanup"类请求默认进入检查+提升模式；
  说"create astro""deploy astro""build static blog"时触发 Astro 建站指南；说"project page""项目页"时触发项目页创建。
  这是网站相关工作的唯一入口，替代 site-modernizer、publishing-astro-websites 等分散 skill。
license: MIT
metadata:
  version: "2.4.0"
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
    - health check
    - check website
    - site check
    - audit site
    - upgrade
    - modernize
    - 升级
    - 重构
    - cleanup
    - clean up
    - 清理
    - 反模式扫描
    - anti-pattern scan
    - build fix
    - fix build
    - architecture decision
    - ADR
    - build pipeline
    - 构建脚本
    - duplicate pages
    - 重复页面
    - merge scripts
    - redirect
    - 重定向
    - project page
    - 项目页
    - astro
    - astro website
    - astro static site
    - astro content collections
    - astro deployment
    - astro firebase
    - astro mermaid
    - starlight
    - build astro site
    - create astro site
    - deploy astro to firebase
    - set up content collections
    - add mermaid diagrams to astro
    - configure astro i18n
    - build static blog
    - astro markdown setup
  tags:
    - audit
    - improve
    - astro
    - performance
    - a11y
    - security
    - layout
    - modernization
    - deployment
    - checklist
user-invocable: true
disable-model-invocation: false
---

# website-improve Skill

## 调用方式

> **副作用声明**：本 skill 会修改代码、执行构建、并自动 `smart-autopush.sh` 提交。请勿在不确定时自动触发。

**用户主动调用**：说出触发词即可，例如：
- `website-improve`
- `改进网站` / `优化网站` / `audit website`
- `project page` / `项目页`
- `create astro site` / `deploy astro`

---

## 触发方式

- `website-improve`
- `改进网站` / `优化网站` / `audit website` / `网站审计` / `网站检查`
- `improve site` / `site health` / `health check`
- `check website` / `site check` / `audit site`
- `upgrade` / `modernize` / `升级` / `重构` / `cleanup` / `clean up` / `清理`
- `反模式扫描` / `anti-pattern scan`
- `build fix` / `fix build`
- `project page` / `项目页`
- `astro` / `create astro site` / `deploy astro` / `build static blog`
- `redirect` / `重定向`

---

## 定位

| 模式 | 场景 | 预计耗时 | 加载的 Reference |
|------|------|---------|-----------------|
| **A. 检查+提升** | 默认模式。所有"改进/审计/优化/检查"类请求进入此模式 | 30min+ | `scan-checklist.md` + `astro-modernization-checklist.md` + `site-audit-checklist.md` + `academic-project-checklist.md`(条件加载) |
| **B. Astro 建站** | "create astro/deploy astro"等 | 视 scope | `astro-build-guide.md` + `astro-modernization-checklist.md` + `deployment-platforms.md` + `markdown-deep-dive.md` |
| **C. 项目页创建** | "project page/项目页" | 20-40min | `project-page-template.astro` + `academic-project-checklist.md` |

---

## 意图路由

收到请求后，按以下优先级判断模式：

```
用户输入
  |
  v
包含 "project page" / "项目页" ?
  ├─ 是 → 模式 C: 项目页创建
  └─ 否 → 包含 "create astro" / "deploy astro" / "build static blog" / "astro markdown" / "starlight" ?
       ├─ 是 → 模式 B: Astro 建站指南
       └─ 否 → 模式 A: 检查+提升（默认）
```

**模式 A 的子路由（运行时检测，非用户输入触发）：**

```
进入模式 A 后
  |
  v
检测项目类型
  ├─ 发现 DESIGN.md 或 Poster/Slides 组件 → 学术项目页审计
  │   ├─ 有 DESIGN.md → 读取硬约束，执行学术项目专用检查
  │   └─ 无 DESIGN.md → 自动创建 DESIGN.md 模板，标记为 P0 建议人工填充
  └─ 未发现 → 通用网站审计
```

---

## 模式 A: 检查+提升（默认）

**加载**: `references/scan-checklist.md` + `references/astro-modernization-checklist.md` + `references/site-audit-checklist.md` + 条件加载 `references/academic-project-checklist.md`

核心理念：**先检查（发现错误），后提升（现代化改进）**。禁止混为一谈。

```
阶段 1 — 并行检查（Check）【发现所有错误】
  ├─ Agent-Check-Build    → 构建错误、类型错误、CI 失败、弃用警告
  ├─ Agent-Check-Code     → 反模式、安全漏洞、重复页面、死代码
  ├─ Agent-Check-Content  → SEO 缺失、a11y 问题、i18n 不对等
  └─ Agent-Check-Deps     → 未使用依赖、lockfile 问题、版本冲突
  |
  v
阶段 2 — 顺序修复错误（Fix Errors）【必须清零】
  BUILD_PASS → TYPECHECK_PASS → CI_PASS → ZERO_WARNINGS
  |
  v
阶段 3 — 并行提升（Improve）【现代化改进】
  ├─ Agent-Upgrade-Deps      → 依赖升级、迁移到推荐方案
  ├─ Agent-Modernize-Code    → Astro 6.x 模式、Tailwind v4 最佳实践
  └─ Agent-Optimize-Assets   → 图片优化、字体本地化、学术资产库化
  |
  v
阶段 4 — 并行验证（Verify）【检查+提升双重确认】
  ├─ Agent-Verify-Build   → npm run build + npx astro check
  ├─ Agent-Verify-Visual  → Playwright 响应式 + WebKit 验证
  └─ Agent-Verify-i18n    → zh/en 内容对等检查
```

---

### 检查层（Check）— 发现错误

**目标**：找出所有导致构建失败、运行时错误、CI 警告、安全漏洞、可访问性缺陷的问题。**检查不修改代码，只生成问题清单。**

#### Agent-Check-Build — 构建与 CI 检查

```
Agent({
  description: "Check build and CI errors",
  prompt: "Run 'npm run build' and 'npx astro check'. Check '.github/workflows/*.yml' for: Node.js 20 deprecation warnings (configure-pages@v5, deploy-pages@v4), outdated action versions, missing FORCE_JAVASCRIPT_ACTIONS_TO_NODE24. Check CI history with 'gh run list --limit=3'. Return: {build_passed: bool, typecheck_passed: bool, ci_passed: bool, deprecations: [{action, current_version, recommended_version}], errors: [...]}"
})
```

**检查清单**：
- [ ] `npm run build` 是否通过
- [ ] `npx astro check` 0 errors / 0 warnings / 0 hints
- [ ] GitHub Actions 最近 3 次运行是否全部 success
- [ ] 是否存在 Node.js 20 弃用警告（`actions/configure-pages@v5`, `actions/deploy-pages@v4`）
- [ ] `.github/workflows/*.yml` 是否使用推荐版本（checkout@v6, setup-node@v5, upload-pages-artifact@v5）
- [ ] 是否设置 `FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true`

#### Agent-Check-Code — 代码与安全问题检查

```
Agent({
  description: "Check code patterns and security",
  prompt: "Explore src/ directory. Check for CRITICAL errors: set:html injecting user input, missing alt text on images, is:inline used outside allowed scope (FOUC/theme/JSON-LD/SW/third-party CDN), getEntry(...)! non-null assertion, __themeBound/__copyBound event delegation (should use e.target.closest), duplicate pages (e.g. /cv.astro + /[lang]/cv.astro both exist), Astro.glob usage (should be import.meta.glob), ViewTransitions component (should be ClientRouter), Image format='webp' prop (Astro 6 deprecated). Check i18n HTML in translations: if en.json/zh.json values contain HTML tags, verify components use set:html. Return: {issues: [{file, line, severity: 'CRITICAL'|'HIGH'|'MEDIUM', message, fix_type}]}"
})
```

**检查清单**：
- [ ] `set:html` 是否注入不可信数据（用户输入、URL 参数）→ CRITICAL
- [ ] 图片是否有 `alt` 属性
- [ ] `is:inline` 是否超出允许范围
- [ ] 是否存在重复页面（`/page.astro` + `/[lang]/page.astro`）
- [ ] `Astro.glob` → 应改为 `import.meta.glob(..., { eager: true })`
- [ ] `<ViewTransitions />` → 应改为 `<ClientRouter />`
- [ ] `<Image format="webp" />` → 应移除 format 属性
- [ ] `getEntry(...)!` → 应改为 `if (!entry) throw new Error(...)`
- [ ] `__themeBound` / `__copyBound` → 应使用事件委托 `e.target.closest('[data-action]')`
- [ ] i18n 条件渲染 `lang === 'zh' ? '中文' : 'English'` → 应统一为 `t('key')`
- [ ] 非首屏图片是否缺失 `loading="lazy" decoding="async"`

#### Agent-Check-Content — 内容与 SEO 检查

```
Agent({
  description: "Check content and SEO issues",
  prompt: "Check SEO meta tags, Open Graph, JSON-LD, PWA manifest. Verify en.json/zh.json parity (key count, missing keys). Check for broken links, missing favicon, missing 404 page. Return: {issues: [...], i18n_gaps: [{key, missing_in}], seo_score: number}"
})
```

**检查清单**：
- [ ] `og:title`, `og:description`, `og:image` 是否完整
- [ ] JSON-LD 结构化数据是否存在
- [ ] PWA manifest 是否存在
- [ ] en.json / zh.json 键值是否对等
- [ ] 是否存在断链

#### Agent-Check-Deps — 依赖检查

```
Agent({
  description: "Check dependency issues",
  prompt: "Check package.json, astro.config.mjs. Identify: unused deps (zod with empty collections, @fontsource/* without imports, @astrojs/compiler-rs without experimental.rustCompiler, astro-expressive-code without code blocks), missing lock file, @tailwindcss/postcss (should be @tailwindcss/vite), legacy tailwind.config.mjs (v4 ignores it), legacy postcss.config.mjs, @astrojs/tailwind (should use Tailwind v4 + @tailwindcss/vite). Return: {unused_deps: [{package, reason}], legacy_configs: [...], outdated_deps: [...]}"
})
```

**检查清单**：
- [ ] 未使用依赖：`zod`（空 collections）、`@fontsource/*`（无 import）、`@astrojs/compiler-rs`（未启用 rustCompiler）
- [ ] `@tailwindcss/postcss` → 应迁移到 `@tailwindcss/vite`
- [ ] `tailwind.config.mjs` + Tailwind v4 → v4 已忽略此文件，主题应写在 `global.css` 的 `@theme {}` 中
- [ ] `postcss.config.mjs` + Tailwind v4 + Vite → 应删除
- [ ] `@astrojs/tailwind` → 应使用 Tailwind v4 + `@tailwindcss/vite`

---

### 修复层（Fix Errors）— 错误清零

**原则**：检查阶段发现的所有 CRITICAL 和 HIGH 问题必须修复，且 `npm run build` + `npx astro check` + CI 全部通过，才能进入提升阶段。

**修复优先级**：
1. 构建错误（build fail）→ 立即修复
2. 类型错误（type check fail）→ 立即修复
3. CI 失败 → 立即修复
4. 安全漏洞（CRITICAL）→ 立即修复
5. 弃用警告 → 立即修复
6. HIGH 级别代码问题 → 尽快修复
7. MEDIUM/LOW → 可进入提升阶段后处理

**门禁**：修复完成后必须满足：
```bash
npm run build        # 通过
npx astro check      # 0 errors / 0 warnings / 0 hints
git push origin main # CI 状态 success
```

---

### 提升层（Improve）— 现代化改进

**目标**：在零错误的基础上，将代码库提升到当前最佳实践。**提升不修复错误，只改进质量。**

#### Agent-Upgrade-Deps — 依赖升级

**升级流程**：
1. 读取 `~/.claude/memory/reference/do-not-upgrade-packages.md` 黑名单
2. `pnpm outdated` / `npm outdated` 列出可升级包
3. **Patch/Minor**（如 4.2.2 → 4.3.0）：可直接升级，构建验证通过即可 push
4. **Major**（如 1.8.6 → 2.0.0）：需先读 CHANGELOG，确认无破坏性变更后再升级
5. 升级后必须执行：`npx astro check` + `npm run build`

**当前已知可升级项（2026-05-20）**：
- `tailwindcss` 4.2.2 → 4.3.0（**四站全部完成**）
- `astro-expressive-code` 0.41.7 → 0.42.0（GDKVM 已完成，零影响确认）
- `astro` 6.1.8 → 6.3.6（wangrui2025.github.io 已完成，其他站待评估）
- `astro-pagefind` 1.8.6 → 2.0.0（**major**，需读 CHANGELOG 再决定）

**兼容性记录（已解决）**：
- wangrui2025.github.io `@tailwindcss/vite` 4.3.0 构建失败 → **修复方案**：显式锁定 `vite` 到 `^7.3.2`（避免 npm 解析到 Vite 8.x）。mykcs.github.io 因使用 pnpm-lock 天然锁定 Vite 7.x，未触发此问题。

#### Agent-Modernize-Code — 代码现代化

**Astro 6.x 迁移清单**：
- `Astro.glob(...)` → `import.meta.glob(..., { eager: true })`
- `<ViewTransitions />` → `<ClientRouter />`
- `<Image format="webp" />` → 移除 format 属性（Sharp 自动优化）
- `getEntry(...)!` → `if (!entry) throw new Error(...)`
- `__themeBound` / `__copyBound` → 事件委托 `e.target.closest('[data-action]')`
- 字符串拼接 locale URL → `getRelativeLocaleUrl(locale, path)`
- `is:inline` 页面级脚本 → `src/scripts/` + `astro:page-load`
- i18n 条件渲染 → `t('key')` 统一翻译函数

**Tailwind CSS v4 迁移清单**：
- `tailwind.config.mjs` 主题配置 → 迁移到 `src/styles/global.css` 的 `@theme {}` 块
- `@tailwindcss/postcss` → `@tailwindcss/vite`
- 删除 `postcss.config.mjs`（Vite 插件不再需要）
- `darkMode` class 配置 → `@custom-variant dark (&:where(.dark, .dark *))`
- `--text-*` 长度变量 → 禁止用 `text-[--var]`（会生成 `color:` 而非 `font-size:`）

#### Agent-Optimize-Assets — 资源优化

- Google Fonts CDN → `@fontsource/*` 本地字体
- 非首屏图片 → 添加 `loading="lazy" decoding="async"`
- 学术资产库化 → 迁移到 `mykcs/academic` CDN（见下方"学术资产库化"章节）
- 图片格式 → 使用 Astro `<Image />` 让 Sharp 自动优化，禁止硬编码 `format="webp"`

---

### 验证层（Verify）— 双重确认

```
Agent({
  description: "Verify build passes",
  prompt: "Run 'npm run build' and 'npx astro check'. Return: {build_passed: bool, errors: [...], astro_check_passed: bool}."
})
Agent({
  description: "Verify visual layout",
  prompt: "Run Playwright responsive checks (mobile/desktop). If academic project with Poster/Slides, run WebKit verification per DESIGN.md constraints. Return: {responsive_ok: bool, webkit_ok: bool, screenshots: [...]}."
})
Agent({
  description: "Verify i18n parity",
  prompt: "Compare en.json and zh.json key counts. Check for missing keys in either language. Return: {parity_ok: bool, missing_en: [...], missing_zh: [...]}."
})
```

---

### 跨站点依赖同步升级

> 适用于 `repo/webs` 下的多站点矩阵（mykcs.github.io / wangrui2025.github.io / OSA / GDKVM 等）

**触发条件**：发现某一站点升级了共享依赖（如 Tailwind CSS、Astro、@tailwindcss/vite），或用户问"其他站点是否也能升级"。

**执行顺序**：
1. **扫描版本矩阵**
   ```bash
   cd ~/Repo/webs
   for d in */; do
     echo "=== $d ==="
     cat "$d/package.json" 2>/dev/null | grep -E "tailwindcss|@tailwindcss/vite|astro" | head -6
     cat "$d/astro/package.json" 2>/dev/null | grep -E "tailwindcss|@tailwindcss/vite|astro" | head -6
   done
   ```
2. **判断升级范围**
   - 主站（mykcs.github.io）→ 优先升级，作为验证基准
   - 活跃维护子站（OSA / GDKVM）→ 同步升级
   - 重定向/归档站（wangrui2025.github.io / sprites-gallery）→ 也升级，保持依赖一致，避免技术债
3. **先主站验证，再批量同步**
   - 步骤 A：主站升级 → `npm run build` 通过 → `smart-autopush.sh` 提交
   - 步骤 B：其他站逐站执行相同升级 → 每站 `npm run build` 验证 → 逐站提交
   - 禁止：多站同时改完再一起验证（一旦失败难以定位）
4. **Commit 规范**：`chore(deps): upgrade tailwindcss to 4.3.0`
5. **版本差异记录**：升级完成后更新 `webs-context.md` 中的依赖版本表

---

### 触类旁通三层扫描协议

> 触发条件：发现构建配置/反模式/依赖问题时，或用户说"触类旁通"

**L1 — workspace 内检查**
```bash
cd ~/Repo/webs
for d in */; do
  echo "=== $d ==="
  cat "$d/package.json" 2>/dev/null | grep -E '@tailwindcss/(postcss|vite)|@astrojs/tailwind'
  ls "$d/tailwind.config"* "$d/astro/tailwind.config"* 2>/dev/null
  ls "$d/postcss.config"* "$d/astro/postcss.config"* 2>/dev/null
done
```
- 所有活跃维护子站（OSA / GDKVM / 主站）必须同步修复
- 归档/暂停站点记录问题但不强制修复

**L2 — 全机器 repo 扫描**
```bash
find ~/Repo ~/Projects ~/PyPjcts -maxdepth 4 -name 'package.json' -not -path '*/node_modules/*' -exec grep -l '@tailwindcss/postcss\|@astrojs/tailwind' {} \;
find ~/Repo ~/Projects ~/PyPjcts -maxdepth 3 -name 'tailwind.config*' -not -path '*/node_modules/*'
find ~/Repo ~/Projects ~/PyPjcts -maxdepth 3 -name 'postcss.config*' -not -path '*/node_modules/*'
```
- 发现其他项目存在同样问题时，按同样标准修复

**L3 — 同类现象扫描**
- 检查是否有其他"应该用 A 但实际用 B"的构建工具配置
- 例如：Astro.glob → import.meta.glob、ViewTransitions → ClientRouter、format="webp" → 移除
- 检查 is:inline 是否超出允许范围（FOUC/theme/JSON-LD/SW/第三方 CDN）
- 检查 set:html 是否注入不可信数据

**执行规范**：生成处理报告 → 依次执行 L1 → L2 → L3 → 结果同步到 `webs-context.md`

**评分**: Build Health 20% + Astro 6.x Compliance 15% + i18n Parity 15% + Responsive 10% + Performance 10% + Security 10% + **Project-Specific 20%**（学术项目：Poster 约束/WebKit/公式渲染；主站：SEO/OG/PWA）

---

### 已知项目设计约束（审计时禁止误改）

**mykcs.github.io（主站）**：
- Timeline（`timeline_items`）按**重要程度降序排列**，非时间顺序。当前优先级：国家奖学金 > 校级特等奖 > 校级一等奖 > 学术启航奖学金 > 论文接收 > 入学/毕业 > 其他。**Agent 审计时禁止按时间重新排序。**
- `skills_items` 与 `cv.ts` 的 `hobbies` 必须保持内容一致（纯文本，`·` 分隔）。
- 字体全站硬编码为 Times New Roman，禁止改回 Inter/Plus Jakarta Sans。
- 首页 section 标题使用 `section-heading--academic`（10pt uppercase，细实线底边，无渐变装饰线）。

---

### 学术资产库化（Academic Asset Library）

**触发条件**：项目使用 `mykcs/academic` 管理学术图片，或需要建立统一的学术资源引用规范。当前已知消费者：OSA（`/osa/`）、主站（`wangrui2025.github.io`）、GDKVM 等。

**目标**：将学术图片资源集中管理，所有消费者项目通过**版本化 CDN** 引用，消除本地资源副本和路径硬编码。

**三阶段工作流**：

```
阶段 1 — academic 仓库自动化
  ├─ 添加 `.github/workflows/bump-version.yml`
  ├─ 每次 push 到 main 自动递增 patch tag（v1.0.0 → v1.0.1）
  └─ 消费者统一引用：cdn.jsdelivr.net/gh/mykcs/academic@<tag>/images/...
  |
  v
阶段 2 — 消费者项目迁移
  ├─ 扫描所有消费者项目中的本地学术资产（src/assets/paper/、public/paper/ 等）
  ├─ 将 /academic/images/... 或 @main 引用改为带 tag 的版本化 URL
  └─ 删除消费者项目中的本地学术资产副本
  |
  v
阶段 3 — 统一路径管理模块
  ├─ 设计可复用的常量/函数，供所有项目复用
  └─ 在消费者项目中建立 src/constants/assets.ts（或类似文件）
```

**阶段 1 — academic 仓库自动 tag Action**：
```yaml
# .github/workflows/bump-version.yml
name: Bump Version
on:
  push:
    branches: [main]
jobs:
  bump:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: Bump patch version
        run: |
          git fetch --tags
          latest=$(git describe --tags --abbrev=0 2>/dev/null || echo "v0.0.0")
          version=${latest#v}
          IFS='.' read -r major minor patch <<< "$version"
          new_tag="v${major}.${minor}.$((patch + 1))"
          git tag "$new_tag"
          git push origin "$new_tag"
```

**阶段 2 — 消费者迁移检查清单**：
- [ ] 搜索消费者项目中的学术图片引用：`grep -rn "academic/images" src/ public/`
- [ ] 替换 `@main` 或裸 `/academic/images/` 为带 tag 的 jsDelivr URL
- [ ] 检查并删除本地副本：`find src/assets public -name "*.png" -o -name "*.svg" | grep -iE "(paper|publication|logo)"`
- [ ] 构建验证：`npm run build` + 检查 dist/ 中无残留 `/academic/images/` 绝对路径

**已知问题与最佳实践**：

1. **jsDelivr 新 tag 同步延迟**
   - 刚 `git push origin v1.0.0` 后，jsDelivr 可能还未同步，访问 `@v1.0.0` 会返回 502。
   - **验证**：`curl -sI https://cdn.jsdelivr.net/gh/mykcs/academic@v1.0.0/images/avatar/avatar.png`
   - **Workaround**：改用短 commit hash（如 `@2d8a325`），同样不可变且立即可用：
     ```typescript
     export const ACADEMIC_VERSION = '2d8a325';  // 或 'v1.0.0' 待 CDN 同步后切回
     ```
   - commit hash 与 tag 在不可变性和缓存锁定上等价，只是可读性稍差。

2. **Astro `<Image>` 组件需要 `remotePatterns`**
   - 如果消费者项目使用 Astro `<Image>` 引用远程图片，必须在 `astro.config.mjs` 中声明：
     ```js
     image: {
       remotePatterns: [
         { protocol: 'https', hostname: 'cdn.jsdelivr.net' },
       ],
     }
     ```
   - 原生 `<img>` 标签不需要此配置。

3. **目录结构约定**
   ```
   mykcs/academic/images/
   ├── publications/{paper-name}/fig/     # 论文图表
   ├── publications/{paper-name}/tab/     # 论文表格
   ├── logos/                             # 会议/学校 logo
   ├── icons/                             # 翻译、社交等图标
   └── avatar/                            # 个人头像
   ```
   - URL 格式：`https://cdn.jsdelivr.net/gh/mykcs/academic@{version}/images/{category}/{path}`

4. **构建时图片下载行为**
   - Astro `<Image>` 在 `npm run build` 时会实际请求远程图片进行 Sharp 优化。
   - 如果 URL 404 或 502，build 会直接报错中断，而不是静默失败。
   - 这意味着 **build 通过 = 所有远程图片可访问**，比运行时检查更严格。

**阶段 3 — 统一路径管理模块模板**：
```typescript
// src/constants/assets.ts
export const ACADEMIC_VERSION = 'v1.0.0';
export const ACADEMIC_BASE = `https://cdn.jsdelivr.net/gh/mykcs/academic@${ACADEMIC_VERSION}/images`;

export function academicImage(path: string): string {
  return `${ACADEMIC_BASE}/${path}`;
}

// 使用示例
// <img src={academicImage('logos/szu.svg')} alt="SZU Logo">
```

**Commit 规范**：
- academic 仓库：`chore(ci): add auto-tag workflow`
- 消费者项目：`refactor(assets): migrate to versioned academic CDN`

---

## 模式 B: Astro 建站指南

**加载**: `references/astro-build-guide.md` + `references/astro-modernization-checklist.md` + `references/deployment-platforms.md` + `references/markdown-deep-dive.md`

覆盖：
- 项目初始化与目录结构（`astro-build-guide.md`）
- Tailwind CSS v4 集成（`astro-build-guide.md`）
- Content Collections 配置（`astro-build-guide.md`）
- i18n 路由设置（`astro-build-guide.md`）
- 布局、组件、Slots（`astro-build-guide.md`）
- 图片与资源处理（`astro-build-guide.md`）
- SEO / Open Graph / JSON-LD（`astro-build-guide.md`）
- 升级路径与反模式（`astro-modernization-checklist.md`）
- 部署平台配置（`deployment-platforms.md`）
- Markdown/MDX、Mermaid 图表（`markdown-deep-dive.md`）

---

## 模式 C: 项目页创建

**加载**: `references/project-page-template.astro`

为论文创建双语项目展示页（如 `/osa/`、`/gdkvm/`）：

**Stack**: Astro 6.x + Tailwind CSS v4 + `@fontsource/*` + `oklch()` 色彩
**URL 结构**: `/<project>/` → redirect → `/<project>/en/` + `/<project>/zh/`
**标准区块**: Hero → Abstract → Motivation → Method → Results → BibTeX → Links

创建后：Stage → `smart-autopush.sh` → `git log --oneline -1` 确认。

---

## 通用非协商规则

适用于所有模式：

1. **不破坏构建**：任何修改后必须 `npm run build` 通过
2. **安全优先**：`set:html` / secrets 问题标记为 P0，不自动修复
3. **中英同步**：a11y/UI 修复涉及文本时，同步更新 en.json / zh.json
4. **Commit 必须**：修改文件后必须 `smart-autopush.sh` 提交（永远不要裸 `git push`）
5. **验证门禁**：声明完成前，粘贴 `npm run build` 最后 5 行 + `git log --oneline -1`
6. **批量维护标记**：>10 文件变更时 commit message 加 `[BATCH MODE]`，完成后 `git log --oneline` + `git diff --stat`
7. **CSS 跨浏览器验证**：涉及 grid/flex/图片尺寸时，必须双端验证（Chromium + WebKit）
8. **视觉布局协议**：修改前 FULL_AUDIT（Playwright 测溢出）→ 变更批处理 → 修改后重新 FULL_AUDIT → 零溢出才报告 done
9. **CI 门禁**：push 后必须检查 GitHub Actions 状态。若 run fail，必须修复至全部 pass 才算完成。禁止停在"本地构建通过但 CI 失败"的状态。
   - **检查命令**：`gh run list --repo=<owner>/<repo> --limit=1 --json conclusion,status,headSha`
   - **诊断命令**：`gh run view <run-id> --log-failed`
   - **修复循环**：定位根因 → 本地复现 → 修复 → commit → push → 重新检查 CI，直到 `conclusion: success`
   - **修复优先级**：构建错误 > 测试失败 > Lint 警告
   - **典型场景**：
     - 构建产物路径变更
     - vendor/academic submodule 未更新
     - lockfile 与 CI 环境不兼容
     - Playwright WebKit 在 CI 缺失系统依赖 → 需 `npx playwright install-deps chromium webkit`
     - `.github/workflows/` 修改需 `workflow` scope → 若 token 缺失，提示用户执行 `gh auth login --scopes repo,workflow`
10. **GitHub Actions Node.js 弃用修复**：遇到 `Node.js 20 actions are deprecated` 警告时，按以下矩阵升级：
    - `actions/configure-pages@v5` → `v6`（Node 24）
    - `actions/deploy-pages@v4` → `v5`（Node 24）
    - `actions/checkout@v5` → `v6`
    - `actions/upload-pages-artifact@v3` → `v5`
    - `actions/upload-artifact@v4` → `v7`（v5/v6 仍使用 Node 20）
    - 同时添加环境变量：`FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true`
    - `actions/configure-pages@v6` 输入名变更：`static_generator_mode` → `static_site_generator`
    - `working-directory` 陷阱：若 step 设置了 `working-directory: website`，后续 `upload-artifact` 的 `path` 仍需写完整相对路径（如 `website/playwright-report/`），因为 upload-artifact 不继承 working-directory
    - **跨站点同步**：主站（mykcs.github.io）、OSA、GDKVM 等使用 GitHub Pages 部署的站点需逐一检查 `.github/workflows/*.yml`，确保全部升级，禁止只修一个站。
    - **验证**：升级后 push，通过 `gh run view` 确认警告消失。

11. **决策固化到 DESIGN.md**：每次 skill 执行后，若对项目做了架构/设计层面的改动（如路由变更、依赖迁移、设计模式调整），必须将改动原因写入 `DESIGN.md` 或 `CONTEXT.md`，注明"**原因**：xxx"，防止未来反复修改同一问题。
    - 示例：`astro-pagefind` 从 1.x 升级到 2.0 时，记录到 `CONTEXT.md`，避免下次 skill 重复提议升级。
    - 只记录"**为什么这样改**"，不记录改动细节（细节在 git commit message）。
    - 若项目无 `DESIGN.md`，跳过此规则。
