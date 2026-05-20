# Evolution Sources & Benchmarks

> Layer 3 进化层的知识来源、外部基准和搜索策略。每次 rich审计 必须执行外部扫描，禁止跳过。

## 搜索策略（永不休眠）

**每次审计无条件执行**：
1. 至少 2 次 WebSearch 或 1 次 Context7 查询
2. 搜索方向必须覆盖以下至少 2 个维度
3. 报告中必须列出搜索关键词、来源 URL 与结论

## 来源优先级

| 优先级 | 来源 | 获取方式 | 适用场景 |
|--------|------|----------|----------|
| P0 | ECC 官方 skill 库 | `~/.claude/plugins/marketplaces/ecc/**/SKILL.md` | 框架级能力升级 |
| P1 | OMC 内置 skill | `~/.omc/skills/` | 工作流优化 |
| P2 | 用户自定义 skill | `~/.claude/skills/` | 特定任务增强 |
| P3 | 外部知识库 | Web Search / Context7 | 前沿实践、框架更新 |
| P4 | 行业基准研究 | `~/.claude/memory/reference/` | 方法论升级 |

## 强制搜索关键词池

每次审计从以下池中选取至少 2 个关键词执行搜索：

### Claude Code 生态
- "Claude Code best practices 2025"
- "Claude Code hooks security audit"
- "Claude Code ConfigChange hook compliance"
- "Claude Code skill format latest"
- "oh-my-claudecode OMC latest features"

### 前端框架
- "Astro v6 migration guide changelog"
- "Astro i18n routing redirectToDefaultLocale 2025"
- "Tailwind v4 Astro integration 2025"
- "Astro ClientRouter ViewTransitions migration"

### 安全与治理
- "Claude Code guardrails security configuration"
- "Claude Code enterprise audit governance"

### Python / ML 生态
- "PyTorch security advisory CVE 2025"
- "wandb API key security best practices"
- "torch 2.6.0 install MarkupSafe conflict resolution"
- "Python project audit checklist best practices"
- "pyright vs mypy 2025 comparison"
- "pip-compile vs uv lock file comparison"
- "CUDA version mismatch pytorch detection"

## 外部基准对比表

| 维度 | 外部基准来源 | 健康阈值 | 当前占位符 | 差距计算 |
|------|-------------|----------|-----------|---------|
| 规则总量 | Anthropic 官方文档 | < 200 行 | `{current}` | `{gap}` |
| CLAUDE.md | 社区最佳实践 | < 80 行 | `{current}` | `{gap}` |
| 单规则长度 | 注意力研究 | < 50 行 | `{current}` | `{gap}` |
| Hook 覆盖率 | 确定性拦截研究 | 100% 高风险操作 | `{current}%` | `{gap}` |
| 规则重复度 | 内部一致性 | 同一关键词 ≤2 文件 | `{current}` | `{gap}` |
| Skill 模板 | ECC 官方 | 跟随最新版本 | `{current}` | `{gap}` |
| ConfigChange 审计 | Claude Code 官方 Docs | 启用配置变更日志 | `{current}` | `{gap}` |

## 进化触发信号

| 信号 | 触发条件 | 预期行为 |
|------|----------|----------|
| **强制扫描** | **每次审计无条件触发** | 至少 2 次 WebSearch 或 1 次 Context7 |
| **规则重复** | 同一目标存在 3+ 规则 | 合并为更通用的规则 |
| **模式再现** | 同一问题 30 天内出现 ≥2 次 | 搜索外部解决方案并采纳 |
| **工具落后** | 用户使用传统 Unix 工具 | 推荐现代替代方案 |
| **知识老化** | 规则/记忆 90+ 天未更新 | 搜索最新实践并更新 |
| **外部基准** | 发现外部有更优工作流 | 对比后选择性采纳 |
| **分数持平** | 连续 2 次审计分数相同 | 主动搜索新维度/新基准 |

## 决策树

```
审计完成（无论得分高低）
  |
  v
[Step 0] 强制外部扫描（不可跳过）
  - 执行至少 2 次 WebSearch 或 1 次 Context7
  |
  v
[Step 1] 检查外部是否有更优解决方案
  - ECC skill 库是否有对应能力
  - OMC skill 库是否有现成实现
  - 官方 docs 是否有新 API/最佳实践
  |
  v
[Step 2] 对比当前方案 vs 外部方案
  - 哪个更高效/更安全/更符合用户习惯？
  - 外部方案是否需要较大迁移成本？
  |
  v
[Step 3] 决策：采纳 / 观望 / 记录 / 忽略
  - 采纳：立即应用，更新配置/规则/skill
  - 观望：记录到 MEMORY.md，等待时机
  - 记录：无差距但外部有新实践，写入进化报告
  - 忽略：已执行搜索且外部无新进展（附搜索证据）
  |
  v
[Step 4] 采纳后验证
  - 运行相关测试确认无回归
  - 更新健康评分
  - 记录到进化历史
```

## 已知外部基准（截至 2025-05）

### Python/ML 项目审计基准

| 维度 | 外部基准来源 | 健康阈值 | 检测方法 |
|------|-------------|----------|---------|
| torch 版本 | PyTorch Security Advisories | >= 2.5.0 | `python3 -c "import torch; print(torch.__version__)"` |
| CUDA 版本 | PyTorch CUDA Compatibility | torch.cuda.is_available() | `torch.version.cuda` |
| wandb 安全 | Weights & Biases Docs | 无硬编码 key | `grep -E "sk-\|ghp_"` |
| MarkupSafe | PyPI / torch install issues | 无 upper bound constraint | TOML 解析 |
| type check | pyright/mypy 官方 | 配置存在 | `grep "tool.pyright"` |
| 测试覆盖 | pytest 官方 | tests/ 目录存在 | `[ -d tests ]` |
| lock 文件 | pip-compile / uv | pyproject.lock 或 uv.lock | 文件存在性 |
| README | 社区最佳实践 | >= 20 行 | `wc -l < README.md` |

### Claude Code 官方 Hooks
- **ConfigChange 事件**: 官方推荐用于审计配置变更，记录到日志文件
- **PreToolUse / PostToolUse**: 用于确定性拦截和格式化
- **参考**: [Claude Code Hooks Guide](https://code.claude.com/docs/en/hooks-guide)

### 社区安全基准
- **Claude Guardrails** (`dwarvesf/claude-guardrails`):  hardened security config with deny rules, shell hooks, prompt injection defense
- **Claude Code Setup Audit**: 8-dimension audit framework (memory, rules, skills, agents, security, MCP, workflow, freshness)

### Astro 2025 基准
- `redirectToDefaultLocale` default changed to `false` in v6
- `<ViewTransitions />` removed, use `<ClientRouter />`
- `@astrojs/tailwind` deprecated, use `@tailwindcss/vite`
- Vue i18n CVE-2025-27597 patched
