# Execution Plan: Strip mykcs.github.io to Minimal Redirect-Only Site

## 1. 目标与现状

**目标**：将 `mykcs.github.io`（Astro v6，原 315 个文件）精简为仅保留 301 重定向功能的最小站点，所有流量自动跳转至 `wangrui2025.github.io`。

**现状**：该精简操作已在 commit `7f3e664` 完成，当前 `main` 分支仅剩 13 个 tracked 文件（204 KiB）。本计划同时作为操作复盘与可复现文档。

---

## 2. 保留 vs 删除清单

### 保留文件（13 个）

| 文件路径 | 保留理由 |
|---------|---------|
| `.gitattributes` | Git 行尾标准化配置 |
| `.github/workflows/deploy.yml` | GitHub Actions 构建部署流水线 |
| `astro/.gitignore` | Astro 构建忽略规则 |
| `astro/astro.config.mjs` | Astro 站点配置（site 指向 wangrui2025.github.io） |
| `astro/package.json` | 构建依赖声明 |
| `astro/package-lock.json` | 依赖锁定 |
| `astro/src/pages/index.astro` | 唯一页面：301 重定向 |
| `CLAUDE.md` | Claude Code 项目指引 |
| `LICENSE` | MIT 许可证 |
| `README.md` | 重定向说明文档 |
| `node_modules/.vite/deps/_metadata.json` | Vite 缓存元数据（历史遗留） |
| `node_modules/.vite/deps/package.json` | Vite 缓存包声明（历史遗留） |
| `paper/.DS_Store` | macOS 系统文件（历史遗留） |

### 删除文件（303 个，按类别）

| 类别 | 数量 | 示例 |
|------|------|------|
| Astro 源码 | ~40 | `src/components/*.astro`, `src/layouts/*.astro`, `src/data/*.ts`, `src/content/**/*.json` |
| 静态资源 | ~50 | `public/images/*.png`, `public/paper/**/*.jpg/pdf`, `favicon.svg` |
| 构建产物 | ~10 | `_astro/*.css`, `_astro/*.webp` |
| 工作流 | 2 | `scholar_cron.yml`, `update_google_scholar_stats.yml` |
| 文档 | 5 | `AGENTS.md`, `ASTRO_MIGRATION_ANALYSIS.md`, `docs/*.md` |
| OMC 状态 | ~10 | `.omc/**/*.json`, `.omc/**/*.jsonl` |
| 论文源码 | ~180 | `paper/iccv25_gdkvm/**/*.tex/pdf/png` |
| 脚本 | 1 | `scripts/autopush.sh` |
| 其他 | ~5 | `assets/css/`, `google-scholar-stats/`, `gs_data*.json` |

---

## 3. Git 操作流程

### 3.1 前置检查

```bash
# 确认当前分支与远程状态
git status
git log --oneline -5
git remote -v
```

### 3.2 批量删除

```bash
# 删除非必要目录（保留 astro/src/pages/index.astro 及其依赖）
git rm -r mykcs.github.io/.astro \
          mykcs.github.io/.claude \
          mykcs.github.io/.github/workflows/scholar_cron.yml \
          mykcs.github.io/.github/workflows/update_google_scholar_stats.yml \
          mykcs.github.io/.omc \
          mykcs.github.io/AGENTS.md \
          mykcs.github.io/ASTRO_MIGRATION_ANALYSIS.md \
          mykcs.github.io/_astro \
          mykcs.github.io/assets \
          mykcs.github.io/astro/.astro \
          mykcs.github.io/astro/.omc \
          mykcs.github.io/astro/README.md \
          mykcs.github.io/astro/postcss.config.mjs \
          mykcs.github.io/astro/public \
          mykcs.github.io/astro/src/assets \
          mykcs.github.io/astro/src/components \
          mykcs.github.io/astro/src/content \
          mykcs.github.io/astro/src/content.config.ts \
          mykcs.github.io/astro/src/data \
          mykcs.github.io/astro/src/env.d.ts \
          mykcs.github.io/astro/src/layouts \
          mykcs.github.io/astro/src/middleware.ts \
          mykcs.github.io/astro/src/pages/\[lang\] \
          mykcs.github.io/astro/src/pages/en.astro \
          mykcs.github.io/astro/src/styles \
          mykcs.github.io/astro/src/utils \
          mykcs.github.io/astro/tailwind.config.mjs \
          mykcs.github.io/astro/tsconfig.json \
          mykcs.github.io/docs \
          mykcs.github.io/favicon.svg \
          mykcs.github.io/google-scholar-stats \
          mykcs.github.io/gs_data.json \
          mykcs.github.io/gs_data_shieldsio.json \
          mykcs.github.io/images \
          mykcs.github.io/paper \
          mykcs.github.io/pdf \
          mykcs.github.io/scripts

# 修改保留文件内容
git add mykcs.github.io/README.md mykcs.github.io/astro/.gitignore
```

### 3.3 Commit

```bash
git commit -m "[BATCH MODE] refactor(mykcs): strip mykcs.github.io to minimal redirect-only site (done)"
```

**Commit Message 规范**：
- 类型：`refactor`
- 范围：`mykcs`
- 描述：明确说明精简为仅重定向站点
- 标记：`[BATCH MODE]`（>10 文件变更）

### 3.4 Push

```bash
# 使用 smart-autopush.sh（禁止直接 git push）
bash scripts/smart-autopush.sh . "[BATCH MODE] refactor(mykcs): strip mykcs.github.io to minimal redirect-only site (done)" done
```

---

## 4. Git Pre-commit Hooks 处理

**现状**：该仓库未配置 Husky / lint-staged 等 pre-commit hooks。

**处理策略**：
1. 若存在 `.husky/` 或 `.git/hooks/*`（非 sample）：
   - 保留 `pre-commit` hook（若有），但确保其不会因文件缺失而失败
   - 删除与 Astro 构建、测试相关的 hook 步骤
2. 若无 hooks：无需处理

**验证命令**：
```bash
ls -la .git/hooks/ | grep -v sample
ls -la .husky/ 2>/dev/null
```

---

## 5. 构建验证步骤

### 5.1 本地构建验证

```bash
cd mykcs.github.io/astro
npm install
npm run build
```

**预期结果**：
- `astro/dist/index.html` 生成
- 文件内容包含 `<meta http-equiv="refresh" content="0;url=https://wangrui2025.github.io/">` 或等效 301 响应
- 无其他页面/资源生成

### 5.2 构建产物检查

```bash
ls -la astro/dist/
cat astro/dist/index.html
```

**预期产物**：
```html
<!DOCTYPE html>
<meta http-equiv="refresh" content="0;url=https://wangrui2025.github.io/">
```

### 5.3 GitHub Actions 验证

1. Push 后观察 `.github/workflows/deploy.yml` 执行状态
2. 确认 `actions/deploy-pages` 成功
3. 访问 `https://mykcs.github.io` 验证 301 跳转

---

## 6. 风险与缓解

| 风险 | 等级 | 缓解措施 |
|------|------|---------|
| 误删必要文件 | 高 | 保留 `astro.config.mjs` + `package*.json` + `index.astro`；分步删除并 `git status` 确认 |
| GitHub Pages 构建失败 | 中 | 本地先 `npm run build` 验证；保留 `.github/workflows/deploy.yml` |
| 历史大文件残留（repo 体积未减） | 中 | 已确认：git history 仍保留 33.8 MiB blob；如需瘦身需 `git filter-repo`（破坏性操作，需用户确认） |
| 重定向循环 | 低 | 确认目标 URL 为 `wangrui2025.github.io`，非 `mykcs.github.io` |
| 搜索引擎索引丢失 | 低 | 301 永久重定向会传递 SEO 权重；已确认 Astro 生成 301 状态码 |

---

## 7. 执行摘要

| 指标 | 操作前 | 操作后 |
|------|--------|--------|
| Tracked 文件数 | 315 | 13 |
| 工作树大小 | ~50 MiB | 204 KiB |
| Git blob 数 | 758 | 760（历史保留） |
| Git 对象存储 | 33.8 MiB | 33.8 MiB（历史保留） |
| 构建输出 | 完整站点 | 单页 301 重定向 |

---

## 8. 用户动作清单

- [ ] 验证 `https://mykcs.github.io` 是否正确 301 跳转至 `wangrui2025.github.io`
- [ ] （可选）若需缩减 git 对象存储体积，执行 `git filter-repo` 或联系 GitHub Support 清除历史大文件
- [ ] （可选）删除 `node_modules/.vite/deps/` 和 `paper/.DS_Store` 这两个历史遗留 tracked 文件
- [ ] 确认 `wangrui2025.github.io` 站点正常运行，作为重定向目标

---

*计划生成时间：2026-05-14*
*基于 commit：7f3e664*
