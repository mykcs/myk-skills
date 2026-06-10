# website-improve Long-Tail Triggers (v3.7.0+ 拆分)

> **来源**: 从 SKILL.md v3.6.0 (2026-06-09) frontmatter `triggers:` 拆分（v3.7.0 progressive disclosure refactor, 2026-06-10）。
> **目的**: SKILL.md frontmatter 只保留 24 个核心触发器（按 4 类分组），长尾 24 个触发器按需加载本文件。
> **加载时机**: 用户输入含长尾触发器关键词但 SKILL.md frontmatter 不直接命中时，grep 本文件。

---

## 长尾触发器列表 (24 个, 按类别分组)

### Mode A — 检查+提升 (8 个)
- `improve site` — Mode A 同义词
- `health check` — 通用健康检查入口
- `check website` — 同义词
- `site check` — 同义词
- `audit site` — 同义词
- `upgrade` — 升级改造入口
- `modernize` — 现代化改造
- `升级` — 中文升级同义词

### Mode A — 反模式 / 构建 (5 个)
- `重构` — 重构请求
- `cleanup` / `clean up` / `清理` — 清理请求
- `反模式扫描` / `anti-pattern scan` — 反模式专项
- `build fix` / `fix build` — 构建失败修复

### Mode A — 架构决策 (3 个)
- `architecture decision` / `ADR` — 架构决策记录
- `build pipeline` / `构建脚本` — 构建脚本相关

### Mode A — 页面级 (4 个)
- `duplicate pages` / `重复页面` — 重复页面检测
- `merge scripts` — 脚本合并
- `redirect` / `重定向` — 重定向配置

### Mode B — Astro 详细 (8 个)
- `astro` / `astro website` / `astro static site` — Astro 总入口
- `astro content collections` — Content Collections 配置
- `astro deployment` — 部署相关
- `astro firebase` — Firebase 部署
- `astro mermaid` — Mermaid 集成
- `starlight` — Starlight 主题
- `set up content collections` — Content Collections 初始化
- `add mermaid diagrams to astro` — Mermaid 集成
- `configure astro i18n` — i18n 配置

### Mode D — Multi-Site 详细 (3 个)
- `fan out` — fan-out 同义词（无连字符）
- `parallel sites` — 并行多站点
- `并行部署` — 中文 fan-out

---

## 触发器优先级

**SKILL.md frontmatter 核心触发器** (24 个):
- 必查, 触发后立即加载 SKILL.md 全文
- 涵盖 4 大模式入口

**references/triggers.md 长尾触发器** (24 个):
- 必查 SKILL.md frontmatter 之后, 再 grep 本文件
- 命中后按关键词类别路由到对应模式
- 不命中 → 兜底走 Mode A（默认）

---

## Changelog

- **v3.7.0** (2026-06-10): 从 SKILL.md frontmatter 拆出 24 个长尾触发器。原 frontmatter 触发器 60+ 个 → 24 个 (核心) + 24 个 (本文件)。
