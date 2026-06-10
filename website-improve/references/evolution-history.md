# website-improve Skill Evolution History

> **来源**: 从 SKILL.md v3.6.0 (2026-06-09) 拆分（v3.7.0 progressive disclosure refactor, 2026-06-10）。
> **目的**: 沉淀网站改进 skill 自 2026-06-02 首次三仓审计以来的硬规则、反模式、orchestrator 硬化、agent 职责补全。
> **加载时机**: 排查跨站一致性问题 / 演化决策审计 / 准备新一轮 fan-out 时按需加载。

---

## Skill Evolution — Lessons from 2026-06-02 三仓审计

> **本节来源**：2026-06-02 对 `mykcs/mykcs.github.io`、`wangrui2025/GDKVM`、`wangrui2025/osa` 三仓库并行执行模式 A 全流程后沉淀的硬规则和反模式。每个新规则对应一个已归档的 case 文件，遵循 Deja-Vu Fix Protocol。

### 新增硬规则（紧接 §11 之后生效）

**§0 — 启动前必须验证 git remote**（**强制**，在 §1 之前执行）

> 之前我把 GDKVM 误判为 `mykcs/GDKVM`，实际是 `wangrui2025/GDKVM`（owner）— mykcs 只有 manager 权限。

```
1. cd <repo_path>
2. git remote -v                # 三次确认：origin / fetch / push 是否一致
3. git log --oneline -1         # 确认最近 commit 属于此 repo
4. 启动声明必须写 **owner/repo** 完整名，不要省略 owner
```

如果 push URL 与 fetch URL 不一致（如同时配置 `mykcs/GDKVM` 和 `wangrui2025/GDKVM`），**先问用户主推哪个 remote**，再开始任何修改。

**§12 — 已知 bug 版本不升级（白名单/黑名单机制）**

升级前必须查询 case 库（`~/.claude/knowledge/cases/wiki/`）的 anti_pattern 条目：

| 包 | 黑名单版本 | 白名单（推荐）| 原因 |
|----|----------|--------------|------|
| `tailwindcss` | `4.3.0` | `4.1.18` | tsconfigPaths compatibility bug（v4.3.x 仅 1 个 release，未修） |
| `@tailwindcss/vite` | `4.3.0` | `4.1.18` | 同上 |

**升级 agent 硬规则**：发现目标版本在黑名单 → 立即停止升级并报告，不继续。

**§13 — 文档与代码同步检查（CONTEXT.md/CLAUDE.md vs package.json）**

GDKVM 审计时发现 `CONTEXT.md` 写 `Tailwind CSS ^4.3.0` 但 `package.json` 是 `^4.1.18`（**case 触发**）— 文档漂移是审计的副产品。

**强制流程**：
1. 每次修改 `package.json` / `astro.config.mjs` / `tailwind.config.mjs` 关键版本字段
2. 必须搜索 `CLAUDE.md` / `CONTEXT.md` / `README.md` / `DESIGN.md` 中的版本号引用
3. 不一致 → 立即在同一次 commit 修复 + 注明原因

**§14 — 跨仓 owner/manager 关系（项目级备忘）**

| 仓库 | owner | manager | 推送主目标 |
|------|-------|---------|----------|
| `mykcs/mykcs.github.io` | mykcs | — | `origin` = `mykcs/mykcs.github.io` |
| `wangrui2025/GDKVM` | wangrui2025 | mykcs | `origin` = `wangrui2025/GDKVM` |
| `wangrui2025/osa` | wangrui2025 | mykcs | `origin` = `wangrui2025/osa` |
| `wangrui2025/wangrui2025.github.io` | wangrui2025 | — | 已重定向到 mykcs/mykcs.github.io |

**启动声明必须用 owner/repo 完整名**，不要写 `mykcs/GDKVM`。

**§15 — P0 修复必须产硬化机制（Deja-Vu 防护）**

> IF 同一类问题在 ≤30 天内出现第二次（**跨 repo 同模式也算**），立即停止继续修复并按 `behavioral-deja-vu-gate.md` 执行：
> 1. 对比上次根因 vs 本次根因
> 2. 必须产出一项硬化规则或工具改进
> 3. 否则禁止继续

**已知 Deja-Vu 案例**（已加硬化）：
- **CASE-HREFLANG-BASE-DUPLICATION-20260602**：GDKVM + OSA 同次审计同时出现 → 已加 `scan-checklist.md` §2.7 检测脚本 + 3 仓 CI 集成
- **CASE-GDKVM-TAILWIND-V4-BROKEN-20260528**：双 `tailwindcss()` 注册 → 已加 `scan-checklist.md` §6 + §6.1 + 黑名单规则 §12

**§16 — §2.7 / §6 类检测脚本必须自动集成进 CI**

> 之前我把 §2.7 脚本加进 `scan-checklist.md` 但 SKILL.md 没有强制要求同步集成到 `.github/workflows/`。这次补做时才发现：脚本不集成进 CI = 装饰品。

**强制流程**（修复任何 P0 涉及 build 产物检测时）：
1. 在 `scan-checklist.md` 加检测章节
2. **同一次 PR/commit** 集成进 3 仓 `.github/workflows/*.yml`（deploy.yml / astro.yml / main.yml 视项目命名）
3. 脚本优先用 Node 内置 `fs/path`，不引入新 npm dep
4. **负样本测试**：注入反例 URL 验证 CI 真的会 fail（OSA agent 2026-06-02 实施）

### 新增 Agent（Agent 职责清单补全）

| Agent | 检查什么 | 参考章节 |
|-------|---------|---------|
| Agent-Check-Hreflang | **§2.7 hreflang 路径去重**（subpath 站点硬编码 base 重复）| scan-checklist.md §2.7 |
| Agent-Check-DocSync | **§13 文档同步**（CONTEXT.md/CLAUDE.md/README.md/DESIGN.md vs package.json）| 新增 §13（本 SKILL） |

### 跨仓 audit 拆分策略（默认变更）

> 之前 SKILL.md 推荐"7-8 agents per repo"细粒度模式。本次 3 仓 × 7-8 = 21+ 并行 agent，**token 消耗过大但效果并不更好**（每个 agent 都要重新读 scan-checklist.md）。

**新默认（2026-06-02 同日 update，5-site audit 后）**：

| 场景 | 推荐模式 | agent 数 | 备注 |
|------|---------|---------|------|
| 单仓审计 | 1 主 agent 跑全 §1-§9 + 1 verify agent | 2 | — |
| 2-3 仓并行（默认）| **每仓 1 个 agent 跑全 phases**（含 subagent 内部使用 Explore） | N | token vs 隔离价值平衡点 |
| 4-5 仓（user override）| `Workflow` 工具 pipeline 编排 | 3-5N | 详见 `scan-checklist.md` §15 必备条件 |
| 6+ 仓 | 拒绝，建议拆 2 个 session | — | context overflow 风险 |

**4-5 仓 override 必备条件**（详见 `scan-checklist.md` §15）：

- 全部 sub-agent 传 `schema:`（避免 §15.1 push phase 静默 skip）
- push 限速 ≤ 2 + 必先 `git pull --rebase`（§15.2/§15.3）
- orchestrator 加 text fallback 解析（即使 schema 失败也能救回）
- aggregator agent 显式声明"cross-site shared issues"+"matrix conflicts"+"submodule consistency"

**否决条件**：
- 不要为了"细粒度"硬拆 agent — token 成本与隔离价值不对等
- 不要 21+ 个独立 agent 同时跑 — 浪费 context，主会话和子 agent 都会做相同工作
- N > 5 不要硬上 — 主动 ask 用户拆 session

### 跨仓 audit 启动检查清单（新增，2026-06-02 起强制）

1. **3 个 agent 并行上限**（避免 21+ agent 烧 token）：单次 audit ≤ 3 个仓
2. **per-repo 路径验证**（每个仓独立 `git remote -v` + `git log --oneline -1`）
3. **owner/manager 关系查表**（§14）
4. **package manager 检测**（pnpm vs npm — 影响 `npm install` vs `pnpm install`）
5. **base path 收集**（subpath 站点：`GDKVM` / `osa` / `''` — 用于 §2.7 配置）

### 已知跨仓约束

| 约束 | 原因 | 适用 |
|------|------|------|
| `tailwindcss` 三仓必须同步 | v4.3.0 bug 跨仓传染风险 | GDKVM / OSA / mykcs |
| `astro` major 升级需单独 session | Breaking change 风险 + CI 验证耗时 | 三仓 |
| `wangrui2025/*` 不能 push 到 mykcs | 双账号污染历史教训 | GDKVM / osa |

### 已集成的 CI 检测（2026-06-02）

| 仓库 | Workflow | 检测 | SHA |
|------|----------|------|-----|
| mykcs.github.io | deploy.yml | §2.7 跨仓 base contamination | `14dae80` |
| GDKVM | deploy.yml | §2.7 自身 base duplication | `6b73cda` |
| OSA | astro.yml | §2.7 自身 base duplication | `0dced6b` |

下次 audit 新加 subpath 站点时，必须把对应的 §2.7 BASE 常量加进该仓的 CI 脚本。

---

### 5 仓审计补强（2026-06-02 同日追加，5-site fan-out）

> 上文 §0/§12-§16 来自同日 3 仓审计。**同日 5 仓扩展**（mykcs + GDKVM + OSA + wangrui + academic）— 用户显式要求 5 仓并行「在 slowest-site time 内完成」。本次暴露新问题，追加 §17-§22。

**§17 — Workflow schema 提取健壮性**

sub-agent 不传 `schema:` 时，return value 是 final text message。Orchestrator 的结构化字段过滤会全部 `null` → phase 静默 skip。

**真实命中（2026-06-02）**：5-site audit fix phase 5 agents 全部返回 text（无 schema），orchestrator 的 `pushable = fixResults.filter(r => r && r.buildFinalStatus === 'pass')` 过滤为 0 → push phase 跳过 → 14 commits 卡在本地未被 push。修复后由 orchestrator（main context）单独 push 14 commits 全部 PASS。

详见 `scan-checklist.md` §15.1。修复优先级：
1. 始终给 sub-agent 传 `schema:`（即使 minimal）
2. 或 sub-agent 同时写盘 + 返回 schema 对象
3. 或 orchestrator 加 text fallback 解析

**§18 — Push 必先 `git pull --rebase`**

Multi-site 编排下 origin 可能在 push 之间有新 commit。`git push` 被 reject 不会自动恢复。

**真实命中（2026-06-02）**：wangrui push 在第一轮被 reject（origin 有 1 个新 commit）。需 `git pull --rebase origin main && git push origin main` 才成功。

详见 `scan-checklist.md` §15.2。修复：orchestrator 的 PUSH_PROMPT 必须显式写 `git pull --rebase origin main`。

**为什么不能用 smart-autopush.sh**：smart-autopush.sh 会在 pre-condition 不满足时 auto-commit（`git add -A`），对带 P0 uncommitted deletions 的 repo 会污染 finding。

**§19 — CI 失败可能为预期 signal**

新加的 pre-flight guard 触发的 CI 失败 = design-intended signal（如学术资源库的 validate-manifest failure flag P0-001）。看到 CI 失败先读 `gh run view <id> --log-failed` 区分 real regression / expected signal / transient。

**真实命中（2026-06-02）**：academic `validate-manifest.yml`（新加）失败 — 设计内行为，flag 了 P0-001（31 uncommitted GDKVM deletions + 2 dead image-map entries + 14 stale manifest entries）。

详见 `scan-checklist.md` §15.4。

**§20 — Pre-bump guard 限制**

`.github/workflows/bump-version.yml` 加的 working tree guard 在 CI 上看不见（fresh-clone）。Local uncommitted destructive deletions 不会被 tag 防御。

**真实命中（2026-06-02）**：academic bump-version.yml 加的 pre-bump guard `git status --porcelain | grep '^ D'` 在 CI 上看到的是 fresh-clone（无 destructive deletions）→ 永远不触发。实际 31 个 deletions 在 `~/Repo/webs/academic` 的 local working tree。

详见 `scan-checklist.md` §15.5。修复：local pre-push hook（`~/.claude/scripts/pre-push-academic.sh`）拦截在最早阶段。

**§21 — CDN ref mutable 检测**

`@main` / `@master` / `@HEAD` / `@latest` 是可变 ref，上游变 → 资源破坏。检测 + 改 semver/SHA。

**真实命中（2026-06-02）**：wangrui `Favicon.astro` 用 `sprites-gallery@main` → 改为 `@15b1dcb`（同 SHA 已用于 `CVLayout.astro:111`）。

详见 `scan-checklist.md` §14.2。

**§22 — Dead i18n key detection**

JSON 中的 key 无 `t('key')` 调用 → 删除。3 站（GDKVM/wangrui/OSA）发现 dead key pattern。

**真实命中（2026-06-02）**：GDKVM `src/i18n/{en,zh}.json`（218 行）整文件未 import → 整文件删除；footer.langSwitch、tool JSON 8 keys 全部 dead。

详见 `scan-checklist.md` §14.3。

### 已知跨仓约束（2026-06-02 5-site audit 补强）

| 约束 | 原因 | 适用 |
|------|------|------|
| `tailwindcss` 三仓必须同步 | v4.3.0 bug 跨仓传染风险 | GDKVM / OSA / mykcs |
| `astro` major 升级需单独 session | Breaking change 风险 + CI 验证耗时 | 三仓 |
| `wangrui2025/*` 不能 push 到 mykcs | 双账号污染历史教训 | GDKVM / osa |
| **CDN ref 必须 pinned**（@main/@master/@HEAD/@latest 禁用）| mutable ref 上游变 → 资源破坏 | 所有使用 cdn.jsdelivr.net 的仓 |
| **academic bump-version 必须在 pre-push 验证 destructive deletions** | CI fresh-clone 看不到 local working tree（§20）| academic |
| **i18n defaultLocale 跨镜像必须一致** | SEO 重复 + 用户预期不一致 | mykcs + wangrui 镜像对 |

---

## Skill Evolution v3.2.0 — 2026-06-03 3 站 Mode A 跨站 bug 模式

> **下沉到 references**：完整 155 行已迁出。本节仅保留摘要 + 链接。
> 详见 [`references/2026-06-03-skill-evolution-v3.2.0.md`](2026-06-03-skill-evolution-v3.2.0.md)

**摘要**：3 站 Mode A 修复过程暴露 5+ 跨站同模式 bug，对应 §23-§29：
- §23 `getRelativeLocaleUrl` + `prefixDefaultLocale: false` 陷阱
- §24 JSON-LD 必须用 `set:html`（禁用 `<script define:vars>`）
- §25 Critters 必须 filter meta-refresh 桩
- §26 Asset 优化（woff 4MB + pagefind 732K + translate.svg 本地化）
- §27 Sitemap filter post-process workaround
- §28 双语 `[lang]/404.astro` 必备
- §29 CI workflow 存在性 + 包管理匹配

---

## Skill Evolution v3.3.0 — 2026-06-03 自进化协议 + 反模式硬化

> **下沉到 references**：完整 132 行已迁出。本节仅保留摘要 + 链接。
> 详见 [`references/2026-06-03-skill-evolution-v3.3.0.md`](2026-06-03-skill-evolution-v3.3.0.md)

**摘要**：3 站 Mode A 跨站 audit 中暴露**反向漂移 + 自指 false-positive** 两个新反模式，触发自进化协议（§30）首次落地：
- §30 自进化协议（Self-Evolution Protocol）— 4 触发条件 + 5 步 checklist
- §31 §0 gh-api 双侧验证（doc-sync 反向漂移防护）
- §32 §14.1 self-resilient pattern（self-match false-positive 防护）

---

## Skill Evolution v3.6.0 — 2026-06-09 Orchestrator + Fix-Agent 硬化

> **来源**: `~/.claude/knowledge/cases/wiki/CASE-MULTI-SITE-IMPROVE-20260609.md` (3-site fan-out Run 5, 9 agents, 16.4 min)
> **触发**: Workflow orchestrator 在 Phase 4 聚合阶段 ASI 解析失败 (TypeError), fix agent 留下 staged-only deletion 残留, autopush 误判无改动导致需手动 direct push.
> **3 规则** 全部 沉到 orchestrator/fix-agent 必经节点, 不依赖 LLM 自觉.

### §33 — Workflow 脚本 ASI 防御（H1 硬化, Run 5 命中）

**Bug 模式**:
```js
SITES.map((s, i) => { ... return {...} })   // 1st call, result discarded
({ sites: SITES.map((s, i) => { ... }), ... })  // IIFE returning object
```
JS 解析为 `SITES.map(callback)({...})` — 把 1st `.map()` 返回的 array 当函数调用, 抛 `TypeError: SITES.map is not a function`.

**根因**: ASI 规则 — 下一行以 `(` 开头 = 可能继续表达式, **不**插入 `;`.

**修复强制** (所有 workflow 脚本):

| Pattern | OK? | 备注 |
|---------|-----|------|
| `SITES.map(...)\n({...})` | ❌ ASI ambiguity | TypeError 风险 |
| `SITES.map(...);` + `({...})` | ✅ 显式 `;` | 推荐 |
| `const result = { sites: SITES.map(...) }; result` | ✅ assignment + last expression | 隐式 return |
| `;SITES.map(...); ({...})` | ✅ 双 `;` | 最防御 |

**Lint 规则** (orchestrator 启动时):
- 扫描脚本中所有 `SITES.map(...)` / `.filter(...)` / `.reduce(...)` 调用
- 若下一非空行以 `(` 开头 且无前置 `;` → 阻断 + 报错 "ASI risk detected"

### §34 — Autopush Fallback 协议（H2 硬化, Run 5 命中）

**Bug 模式**: fix agent 跑完 `git commit` + `./scripts/autopush.sh ""` 后, autopush 报告 "⏭️ 无有效改动, 跳过" — 但实际 `git log @{u}..HEAD` 显示有 unpushed commit.

**根因**: smart-push.sh / autopush.sh 用文件 mtime / diff signature heuristic 判定"是否有改动", 不识别 staged-only deletion (`git rm` 后的 staged file removal).

**修复强制** (fix agent 流程末段):

```bash
# 1. Try autopush
./scripts/smart-autopush.sh ""

# 2. Cross-check: if `git log @{u}..HEAD` non-empty AND autopush said "skip", direct push
AHEAD=$(git log @{u}..HEAD --oneline | wc -l | tr -d ' ')
if [ "$AHEAD" -gt 0 ] && ./scripts/smart-autopush.sh 2>&1 | grep -q "无有效改动"; then
  echo "Autopush skipped but $AHEAD unpushed commits — falling back to direct push"
  git pull --rebase origin main && git push origin main
fi
```

**Future**: 升级 smart-push.sh 使用 `git status --porcelain` + `git diff --stat` 替代 mtime heuristic, 让 staged-only deletion 也被识别为 "valid change".

### §35 — Fix Agent 二次 Git Status 验证（H3 硬化, Run 5 命中）

**Bug 模式**: mykcs fix agent 报告 `p1_fixed: 5, commits: [b96d158], evidence_blocking: ""` — 看起来全 clean. 但实际 working tree 有 1 个 staged-only deletion (`astro/src/pages/index.astro` 已 commit 但 working tree 还有 untracked deletion), 需 orchestrator 后续手动 `git rm` + commit + push 清理.

**根因**: fix agent 验证协议不包含 working tree dirty check. commit 之后只跑了 `npx astro check` + build, 没跑 `git status`.

**修复强制** (fix agent commit 后必跑):

```bash
# After commit + (autopush or direct push):
WORK_TREE=$(git status --porcelain | wc -l | tr -d ' ')
AHEAD=$(git log @{u}..HEAD --oneline | wc -l | tr -d ' ')
if [ "$WORK_TREE" -gt 0 ]; then
  echo "Working tree has $WORK_TREE dirty entries after commit — auto-cleanup"
  git add -A
  git commit -m "fix(<scope>): cleanup residual working tree changes from P1 fix #N

Auto-cleanup of staged-only changes left behind by previous commit.
Per SKILL.md v3.6.0 §35 hardening protocol."
  git pull --rebase origin main && git push origin main
fi
```

**Lesson**: working tree 残留 (即使 commit + push 看起来都成功) 仍是 "修复未完成" 状态. fix agent 必须 self-verify working tree clean before reporting `done`.

---
