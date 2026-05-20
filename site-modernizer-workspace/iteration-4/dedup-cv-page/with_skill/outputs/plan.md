# CV 页面去重执行计划

## 目标

清理重复的 CV 页面，删除 `src/pages/cv.astro`（纯中文），保留 `src/pages/[lang]/cv.astro`（双语），并确保用户访问 `/cv/` 时自动跳转到 `/zh/cv/`。

## 现状分析

### 文件结构

```
src/
├── pages/
│   ├── cv.astro              # 纯中文，硬编码 lang='zh'
│   └── [lang]/
│       └── cv.astro          # 双语，支持 en/zh
├── components/
│   └── CvContent.astro       # 接收 lang prop，双语渲染
└── layouts/
    └── Layout.astro          # 接收 lang prop
```

### 两个页面差异对比

| 维度 | `src/pages/cv.astro` | `src/pages/[lang]/cv.astro` |
|------|----------------------|----------------------------|
| 路径 | `/cv/` | `/en/cv/`、`/zh/cv/` |
| 语言 | 硬编码 `zh` | 动态 `en` / `zh` |
| Layout 导入 | `../layouts/Layout.astro` | `../../layouts/Layout.astro` |
| 组件导入 | `../components/CvContent.astro` | `../../components/CvContent.astro` |
| 静态生成 | 单页 | `getStaticPaths()` 生成两页 |

### Astro i18n 配置

```js
i18n: {
  locales: ['en', 'zh'],
  defaultLocale: 'zh',
  prefixDefaultLocale: false,  // /zh/xxx 不会自动映射到 /xxx
  routing: {
    prefixDefaultLocale: false,
  },
}
```

当前配置 `prefixDefaultLocale: false` 表示默认语言 `zh` 的页面**不会**自动去掉前缀。即 `/zh/cv/` 和 `/cv/` 是两个独立路由。

## 执行步骤

### 步骤 1：删除重复页面 `src/pages/cv.astro`

```bash
rm src/pages/cv.astro
```

**说明**：该页面与 `[lang]/cv.astro` 在 `lang=zh` 时功能完全重复，且 `[lang]/cv.astro` 已覆盖 `zh` 场景。

### 步骤 2：创建 `/cv/` → `/zh/cv/` 重定向

在 `src/pages/cv.astro` 位置创建一个重定向页面：

```astro
---
return Astro.redirect('/zh/cv/');
---
```

**说明**：Astro 在 frontmatter 中执行 `return Astro.redirect('/zh/cv/')` 会返回 302 重定向响应，将 `/cv/` 流量导向 `/zh/cv/`。

**替代方案（如需 301）**：

若需要 301 永久重定向，使用：

```astro
---
return Astro.redirect('/zh/cv/', 301);
---
```

### 步骤 3：验证构建输出

```bash
npm run build
```

**预期输出检查清单**：

- [ ] `dist/cv.html` 不存在（或存在但内容为重定向）
- [ ] `dist/zh/cv.html` 存在且内容正确
- [ ] `dist/en/cv.html` 存在且内容正确
- [ ] 构建日志无报错

### 步骤 4：验证重定向行为

```bash
# 启动预览服务器
npm run preview &

# 测试 /cv/ 返回 302/301 并指向 /zh/cv/
curl -I http://localhost:4321/cv/
# 预期：Location: /zh/cv/

# 测试 /zh/cv/ 正常返回 200
curl -I http://localhost:4321/zh/cv/
# 预期：HTTP/1.1 200 OK

# 测试 /en/cv/ 正常返回 200
curl -I http://localhost:4321/en/cv/
# 预期：HTTP/1.1 200 OK
```

### 步骤 5：检查内部链接引用

搜索项目中是否有硬编码指向 `/cv/` 的链接：

```bash
grep -r 'href="/cv/"' src/
grep -r "href='/cv/'" src/
grep -r '"/cv"' src/
```

**若有发现**：将内部链接更新为 `/zh/cv/`（或根据上下文使用相对路径）。

## 完整命令清单

```bash
# 1. 进入工作目录
cd /Users/myk/.claude/skills/site-modernizer-workspace/iteration-2/dedup-cv-page/mock-repo/

# 2. 删除旧的纯中文 cv.astro
rm src/pages/cv.astro

# 3. 创建重定向页面
cat > src/pages/cv.astro << 'EOF'
---
return Astro.redirect('/zh/cv/');
---
EOF

# 4. 构建验证
npm run build

# 5. 检查构建产物
ls dist/cv.html dist/zh/cv.html dist/en/cv.html

# 6. 检查内部链接（如有需要则更新）
grep -r 'href="/cv/"' src/ || true
grep -r "href='/cv/'" src/ || true
```

## 风险与回滚

| 风险 | 缓解措施 |
|------|---------|
| 外部书签/SEO 指向 `/cv/` 失效 | 重定向页面保留，旧 URL 仍可用 |
| 构建失败 | 保留原文件备份，或从 git 恢复 |
| 内部链接断裂 | 步骤 5 主动扫描并修复 |

**回滚命令**：

```bash
git checkout -- src/pages/cv.astro
```

## 验收标准

- [ ] `src/pages/cv.astro` 已替换为重定向逻辑（非重复内容）
- [ ] `src/pages/[lang]/cv.astro` 保留且功能正常
- [ ] `npm run build` 成功无报错
- [ ] `/cv/` 访问时浏览器地址栏变为 `/zh/cv/`
- [ ] `/en/cv/` 和 `/zh/cv/` 均可正常访问
- [ ] 项目中无指向 `/cv/` 的断裂内部链接
