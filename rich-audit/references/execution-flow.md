## 执行流程（三层进化系统 + 并行 Agent 架构）

```
User: "rich审计" / "进化"
  |
  v
[1] Layer 1 — 审计层（Audit）【并行 Agent 启动】
    ├─ Agent-Audit-A → Claude Code 配置审计（默认）
    ├─ Agent-Audit-C → Python/ML 项目审计（条件触发）
    └─ 汇总 → 合并两份审计 JSON，计算综合健康分
  |
  v
[2] Layer 2 — 修复层（Fix）【顺序执行】
    AI 读取 Layer 1 汇总 JSON + 关键配置文件
    执行规则语义冲突检测、行为漂移检测、OMC 健康评估
    自动修复安全可论证的问题
  |
  v
[3] Layer 3 — 进化层（Evolve）【3-tool WebSearch cascade + 并行 Agent 启动】
    ├─ Step 1 (primary): mcp__MiniMax__web_search — Claude Code / OMC / Python/ML 最新实践
    ├─ Step 2 (deeper): kimi-webbridge skill — 真实浏览器交互, 抓需要登录的 docs / 论坛 / GitHub issues
    ├─ Step 3 (cross-validate): anysearch skill — 多源 cross-search 验证 (避免单源偏差)
    ├─ Context7: 官方文档 fallback (Python / Claude SDK)
    └─ 汇总 → 3-tool cascade 产出进化建议
  |
  v
[4] 生成进化报告（五段式）
  |
  v
[5] 最终报告（前后健康分 + 修复清单 + 进化清单 + 待处理项）
```

---


📂 **并行 Agent 策略** → see [`references/agent-strategy.md`](references/agent-strategy.md) (loaded on demand)

## 双模扫描范围

> **模式 A**: Claude Code 配置审计（默认）。详见 [`references/audit-patterns.md`](references/audit-patterns.md)（663 行详细检测命令）。
>
> **模式 B**: Python / ML 项目审计（条件触发，检测 `pyproject.toml` / `requirements.txt` 时启用）。详见 [`references/python-checklist.md`](references/python-checklist.md)。

**模式 A 路径清单**（速查表，详细检测见 audit-patterns.md）：

| 路径 | 用途 |
|------|------|
| `~/.claude/rules/` | 行为护栏与约束 |
| `~/.claude/memory/` | 持久化用户/项目/上下文记忆 |
| `~/.claude/knowledge/cases/wiki/` | Case 文件系统（221+ case files） |
| **mem0 ↔ filesystem 对齐** | 双轨记忆同步检测 |
| `~/.claude/hooks/` | PreToolUse / PostToolUse / Stop hooks |
| `~/.claude/scripts/` | 自动化脚本 |
| `~/.claude/skills/` | OMC 和自定义 skills |
| `~/.claude/settings.json` | Claude Code 配置 |
| `~/.omc/skills/` | OMC 市场与用户 skills |
| `~/.agents/skills/` | `.agents` 框架 skills（应与 `~/.claude/skills/` 保持硬链接一致） |

---

## 架构健康度检测（Architecture Health）

| 指标 | 健康阈值 | 超标后果 |
|------|----------|----------|
| 规则文件总数 | ≤ 10 个 | 注意力竞争 |
| 规则总行数 | ≤ 200 行 | 遵守率暴跌 |
| CLAUDE.md 长度 | ≤ 80 行 | resume 挤占上下文 |
| 单规则文件长度 | ≤ 50 行 | 长规则被忽略 |
| frontmatter 覆盖率 | 100% | 加载器不识别 |

> 检测命令、可执行脚本、9 维度加权模型见 [`references/audit-patterns.md`](references/audit-patterns.md)。

---


📂 **v2.6.2+ 新增检测脚本 (2026-06-10)** → see [`references/detection-scripts.md`](references/detection-scripts.md) (loaded on demand)

## 记忆系统对齐检测（双轨同步）

> 详细内容见 [`references/memory-alignment.md`](references/memory-alignment.md)。摘要：
> - **L1** MEMORY.md → case 文件：Phantom entries
> - **L2** case 文件 → MEMORY.md：Missing entries
> - **L3** mem0 → case 文件：mem0 cloud drift
> - 已知陷阱（2026-06-02）：glob 模式不递归 `archive-*/` 子目录导致 197 false positives（已修）

---

