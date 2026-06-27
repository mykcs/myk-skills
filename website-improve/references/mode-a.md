## 模式 A: 检查+提升流程

**核心理念**：先检查（发现错误），后提升（现代化改进）。禁止混为一谈。

**v4.0.0 默认行为** (架构重构): mode A 不再是 "user 选 1 个 mode", 而是 **sub-mode A 在 v4 sweep 中默认必跑**。任何 website intent 触发后, mode A 必跑, 然后根据 sites count / Astro 检测 / 触发词决定后续 sub-mode (B/C/D) 是否跑。

**v4.0.0 强化**: Sub-mode A 必跑 `§A.5 Multi-Round Audit Protocol` (snapshot diff vs last audit, 强制). 这是 v3.9.0 的 sub-provision #4, v4.0.0 升级为必跑项 (per "全 sweep" 原则, 增量 audit 不再存在).

```
阶段 1 — 并行检查（Check）【发现所有错误】
  ├─ Agent-Check-Build     → 构建错误、类型错误、CI 失败、弃用警告
  ├─ Agent-Check-Buttons   → 按钮功能完整性（data-action 监听器、下载链接文件存在性）
  ├─ Agent-Check-CodeQuality → GitHub 高星模板对照（组件结构、事件处理、print CSS）
  ├─ Agent-Check-Code      → 反模式、安全漏洞、重复页面、死代码
  ├─ Agent-Check-Content   → SEO 缺失、a11y 问题、i18n 不对等
  ├─ Agent-Check-Deps      → 未使用依赖、lockfile 问题、版本冲突
  ├─ Agent-Check-CV        → CV 页面 CSS specificity、作者颜色（主站必须）
  └─ Agent-Check-Routing   → i18n switch URL 指向实际文件、redirect 不截断 switch URL

阶段 2 — 顺序修复错误（Fix Errors）【必须清零】
  BUILD_PASS → TYPECHECK_PASS → CI_PASS → ZERO_WARNINGS

阶段 3 — 并行提升（Improve）【现代化改进】
  ├─ Agent-Upgrade-Deps       → 依赖升级、迁移到推荐方案
  ├─ Agent-Modernize-Code     → Astro 6.x 模式、Tailwind v4 最佳实践
  └─ Agent-Optimize-Assets    → 图片优化、字体本地化、学术资产库化、**CDN 加载模式 OSA vs GDKVM 判定（§12.2）**

阶段 4 — 并行验证（Verify）【检查+提升双重确认】
  ├─ Agent-Verify-Build    → npm run build + npx astro check
  ├─ Agent-Verify-CV       → Playwright 截图验证 CV 作者颜色
  ├─ Agent-Verify-Visual   → Playwright 响应式 + WebKit 验证
  └─ Agent-Verify-i18n     → zh/en 内容对等检查
```

### Agent 职责清单

| Agent | 检查什么 | 参考章节 |
|-------|---------|---------|
| Agent-Check-Build | npm run build、npx astro check、CI 历史、GitHub Actions 版本 | scan-checklist.md §1 |
| Agent-Check-Buttons | [data-action] 监听器、下载链接文件存在性、onclick 函数、外部链接 | scan-checklist.md §2 |
| Agent-Check-CodeQuality | 组件行数、事件委托模式、dark mode 实现、print CSS、GitHub 高星对照 | scan-checklist.md §3 |
| Agent-Check-Code | set:html XSS（**已知限制见 §4.6.1/§4.6.2 不修复**）、Astro.glob、ViewTransitions→ClientRouter、重复页面 | scan-checklist.md §4 |
| Agent-Check-Content | OG 标签、JSON-LD、PWA、i18n 对等性 | scan-checklist.md §5 |
| Agent-Check-Deps | 未使用依赖、tailwind.config.mjs 废弃、postcss.config.mjs、**npm audit 中危 dev-only（§4.6.1 不修复）** | scan-checklist.md §6 |
| Agent-Check-CV | .cv-paper-author-* CSS specificity、Playwright 截图验证 | scan-checklist.md §7 |
| Agent-Check-Routing | i18n switch URL 实际文件存在性、redirect 不截断 switch URL | scan-checklist.md §9 |
| Agent-Check-Hreflang | **§2.7 hreflang 路径去重**（subpath 站点硬编码 base 重复检测）| scan-checklist.md §2.7 |
| Agent-Verify-CV | Playwright + getComputedStyle 验证作者颜色 | — |

---
