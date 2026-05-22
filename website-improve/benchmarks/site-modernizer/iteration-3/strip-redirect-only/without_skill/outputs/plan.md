# mykcs.github.io 精简为纯重定向站点 — 执行计划

## 目标

将 `mykcs.github.io` 仓库的所有内容删除，仅保留一个 301 重定向到 `https://wangrui2025.github.io/`。

## 当前状态（已执行）

最近一次 commit `7f3e664` 已完成大部分清理工作：
- 删除了 300+ 个文件（旧页面、组件、图片、论文素材、文档、脚本等）
- 保留了 Astro 最小构建骨架以利用现有的 GitHub Pages 部署工作流
- `astro/src/pages/index.astro` 已改为 301 重定向

## 保留文件清单（当前 HEAD）

```
.gitattributes
.github/workflows/deploy.yml
astro/.gitignore
astro/astro.config.mjs
astro/package-lock.json
astro/package.json
astro/src/pages/index.astro
CLAUDE.md
LICENSE
node_modules/.vite/deps/_metadata.json
node_modules/.vite/deps/package.json
paper/.DS_Store
README.md
```

## 待清理项（工作区未提交变更）

```
删除：node_modules/.vite/deps/_metadata.json
删除：node_modules/.vite/deps/package.json
删除：paper/.DS_Store
```

## 执行步骤

### 阶段 1：提交剩余清理

```bash
cd /Users/myk/Repo/mykcs/mykcs.github.io
git add -u
git commit -m "chore(cleanup): remove leftover node_modules and empty dirs after strip"
```

### 阶段 2：验证重定向生效

```bash
cd /Users/myk/Repo/mykcs/mykcs.github.io/astro
npm install
npm run build
cat dist/index.html
```

期望输出：Astro 生成的 `index.html` 包含 `<meta http-equiv="refresh" content="0;url=https://wangrui2025.github.io/">` 或等效 301 重定向标记。

### 阶段 3：可选 — 进一步极端精简（完全移除 Astro 依赖）

如果希望连 Astro 都不保留，可以替换为纯静态 HTML 重定向：

1. 删除 `astro/` 目录、`package-lock.json`、`.gitignore`
2. 在仓库根目录创建 `index.html`：

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta http-equiv="refresh" content="0; url=https://wangrui2025.github.io/">
  <title>Redirecting...</title>
  <link rel="canonical" href="https://wangrui2025.github.io/">
</head>
<body>
  <p>This page has moved to <a href="https://wangrui2025.github.io/">https://wangrui2025.github.io/</a>.</p>
</body>
</html>
```

3. 更新 `.github/workflows/deploy.yml` 为直接部署根目录：

```yaml
name: Deploy redirect to Pages
on:
  push:
    branches: [main]
  workflow_dispatch:
permissions:
  contents: read
  pages: write
  id-token: write
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/upload-pages-artifact@v3
        with:
          path: .
      - uses: actions/deploy-pages@v4
```

4. 提交：

```bash
git add -A
git commit -m "refactor(deploy): replace Astro with static HTML redirect"
```

### 阶段 4：部署验证

```bash
# 推送到 GitHub（使用 smart-autopush.sh）
bash /Users/myk/Repo/mykcs/scripts/smart-autopush.sh /Users/myk/Repo/mykcs/mykcs.github.io "deploy(redirect): activate 301 redirect to wangrui2025.github.io"

# 等待 GitHub Actions 完成后验证
curl -I https://mykcs.github.io/
```

期望响应头包含 `HTTP/2 301` 或页面包含 refresh meta tag。

## 验收标准

| 检查项 | 标准 |
|--------|------|
| 仓库体积 | < 1 MB（不含 .git） |
| 文件数量 | < 10 个有效文件 |
| 重定向行为 | 访问 `mykcs.github.io` 自动跳转到 `wangrui2025.github.io` |
| SEO | 包含 `canonical` link 和 301/refresh 语义 |
| 部署 | GitHub Actions 成功，Pages 站点可访问 |

## 风险声明

- `mykcs.github.io` 是 GitHub user site，其 Pages 部署会占用该组织的 Pages 配额。
- 旧 URL（如 `mykcs.github.io/paper/...`）在清理后将 404，无自动回退。
- 若选择纯 HTML 方案，需确保 `.github/workflows/deploy.yml` 正确引用构建产物路径。
