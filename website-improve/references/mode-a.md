## 模式 A: 检查 + 提升流程 — v4.2.0

**核心理念**：先检查真实问题，再修复，再用与改动层匹配的证据验收。禁止把“某个历史 CI/工具存在”当成网站质量本身。

Mode A 是普通 website audit / improvement 的默认能力。它默认作用于 **plan 中实际列出的站点**；是否追加 B/C/D 由站点技术栈、用户目标和 multi-site scope 决定。

```text
阶段 1 — Check：收集真实证据
  ├─ Build/Type       → 项目自己的 build / typecheck / lint 契约
  ├─ Buttons/Routing  → 交互、下载、导航、语言切换、redirect
  ├─ Code Quality     → 结构、反模式、重复、死代码、安全风险
  ├─ Content          → SEO、a11y、i18n、内容完整性
  ├─ Dependencies     → 未使用依赖、lockfile、版本/配置冲突
  ├─ Visual           → 响应式、重叠、可读性、交互状态
  └─ Deployed layer   → 仅当部署行为属于本次 scope

阶段 2 — Fix：按优先级修复已证实问题
  └─ 不把 speculative “verify X” 当 finding；没有证据就先验证

阶段 3 — Improve：做 scope 内的现代化/体验提升
  ├─ dependencies / platform migration（若相关）
  ├─ code/layout modernization
  └─ assets/content/interaction optimization

阶段 4 — Verify：按 plan.verification_targets 重新验收
  ├─ build/test/typecheck/lint（按仓库契约）
  ├─ browser/visual（UI 改动）
  ├─ i18n/a11y（相关改动）
  └─ curl/deployed/native evidence（仅当相关）
```

### Build / CI 解释

`scan-checklist.md` 中保留了一些历史 GitHub Actions / Astro 站点检查项，作为发现特定仓库问题的参考。v4.2.0 的活动规则是：

- 先读当前仓库自己的验证/部署配置；
- GitHub Actions、Cloudflare、Pages、Workers、Vercel 等只在该仓库实际使用时才检查；
- 不使用 GitHub Actions 的站点，不因为“最近 3 次 Actions 未 success”产生 finding；
- hosted CI 不存在或故意不运行时，使用 plan 中声明的 repo-owned/local validation；
- `skipped` / missing / stale check 不能伪装成 PASS；
- CI 是否属于最终 acceptance 由 task scope 和 publication contract 决定，不是 Mode A 的固定字段。

### Agent 职责映射

| 检查 lane | 检查什么 | 参考 |
| --- | --- | --- |
| Build | 当前项目 build/typecheck/lint、lockfile、实际 CI contract（若存在） | `scan-checklist.md §1` + repo config |
| Buttons | data-action、下载、onclick、外链、锚点、导航路径 | `scan-checklist.md §2` |
| CodeQuality | 组件结构、事件模式、theme/print、重复/复杂度 | `scan-checklist.md §3` |
| Code | 安全、废弃 API、重复页面、死代码 | `scan-checklist.md §4` |
| Content | SEO、JSON-LD、PWA、a11y、i18n | `scan-checklist.md §5` |
| Deps | 未使用依赖、lockfile、配置迁移 | `scan-checklist.md §6` |
| Visual | 实际浏览器截图/交互证据 | plan verification targets |
| Routing | 语言切换、redirect、hreflang、built-path 存在性 | `scan-checklist.md §2.6/§2.7/§9` |

### 验收

Mode A 自身不拥有最终 PASS。Executor 把实际验证写入 modern `exec-log.json`，独立 Verifier 再根据 modern Acceptance 判定。

- 单站任务：只验该站及真正共享的依赖面；
- multi-site：验所有实际 scoped sites；
- explicit historical four-site sweep：四站全部在 scope，此时四站证据都必须满足 plan；
- publication 未请求：不强制 commit/push/hosted CI；
- deployed outcome 在 scope：必须补 live/deployed evidence。
