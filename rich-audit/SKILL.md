---
name: rich-audit
description: |
  三层进化系统：审计（发现问题）→ 修复（解决问题）→ 进化（主动获取外部先进知识并应用）。
  双模审计：Claude Code 配置审计 + Python/ML 项目审计。
  触发词：rich审计, /rich-audit, 进化
license: MIT
metadata:
  version: "2.5.0"
  author: mykcs
  category: self-evolution
  triggers:
    - rich审计
    - /rich-audit
    - rich audit
    - claude 审计
    - audit claude files
    - 进化
    - 自我升级
  tags:
    - audit
    - evolve
    - self-improvement
    - claude-code
    - omc
    - knowledge
    - benchmark
    - python
    - ml
    - pytorch
user-invocable: true
---

# rich-audit Skill

## 触发方式

- **中文**: `rich审计`
- **英文**: `/rich-audit`
- **别名**: `rich audit`, `claude 审计`, `audit claude files`

---

## 零确认协议（Zero-Confirmation Protocol）[强制 · 不可绕过 · 2026-06-05 固化]

> **核心规则**：rich-audit 触发后，**禁止**任何形式的用户确认（AskUserQuestion / 等待输入 / 等待 "y" / 等待 "go"）。
> 全部三层流水线（审计 + 修复 + 进化）默认直接执行；用户从触发词到执行无任何中间确认。

**默认行为（不可变）**：

| 维度 | 默认值 | 触发后行为 |
|------|--------|----------|
| 深度 | 完整三层（Layer 1 审计 + Layer 2 修复 + Layer 3 进化） | 不询问，自动跑完 |
| 模式 | 双模（配置审计 A + Python/ML 审计 B） | 不询问，并行启动 |
| 范围 | `~/.claude/` + `~/.agents/skills/` + mem0 对齐 | 不询问，全范围 |
| 修复 | 安全可论证的修复自动应用 | 不询问，幂等执行 |
| 备份 | 自动备份到 `~/.claude/backups/rich-audit-*/` | 不询问，先备份后修 |
| 报告 | 五段式进化报告 | 不询问，跑完输出 |

**反例（禁止 · 出现即视为违反本协议）**：

```text
❌ "是否要执行 rich-audit？（是/否）"
❌ "选择模式：A. Claude Code 配置 / B. Python/ML"
❌ "选择深度：1. 完整三层 / 2. 只审计不修 / 3. 审计+修复"
❌ "确认要修复 N 个问题吗？"
❌ "目标范围是？项目 A / B / C？"
❌ 任何 AskUserQuestion 触发的 rich-audit 预确认
```

**唯一允许的"决策点"**：

| 时机 | 形式 | 备注 |
|------|------|------|
| 报告末尾 | PENDING 进化项让用户决定 | 不是预确认，是事后决策 |
| 报告中段 | 检测到 P0 高危修复时输出"⚠️ P0 风险点"提示 | 仅展示，不阻塞 |
| 修复后 | Verification Gates 失败时暂停 | 硬性失败，非询问 |

**Why**（背景）：
- 用户触发词（`rich审计` / `/rich-audit` / `进化`）本身已是明确意图信号
- OMC 摩擦数据：misunderstood_request 32 次 / wrong_approach 31 次，多与反复确认相关
- rich-audit 的所有修复都是幂等的（见 §自动修复行为），失败可回滚
- Verification Gates (10 项) 是物理安全边界，事后验证强于事前确认
- 用户反馈（2026-06-05）："修改 skill 以后不要问我"

**生效范围**：本协议覆盖 §预声明、§执行流程、§自动修复行为 三个章节。任何与之冲突的旧表述以本协议为准。

---

## 预声明（Pre-flight Declaration）[强制]

> **触发时机**：用户说出触发词（`rich审计` / `/rich-audit` / `进化` 等）后，**立即**输出本段，**再**进入 Layer 1 审计。
>
> **Why**: 防止审计跑偏到错误范围（例如误以为是"全机器扫描"），并向用户明示"我接下来要做什么"。同时与 OMC 协议中"先告诉用户再动手"的原则对齐。

**固定输出格式**（中文，大声、明确、不可省略）：

```
═══════════════════════════════════════════════════════════
🚀 rich-audit 启动 — 预声明（Pre-flight Declaration）
═══════════════════════════════════════════════════════════

📌 审计目标（What I will audit）：
  ├─ [Layer 1 — 审计层]
  │   ├─ 模式 A（默认）：Claude Code 配置审计
  │   │   ├─ 规则系统：~/.claude/rules/
  │   │   ├─ 记忆系统：~/.claude/memory/
  │   │   ├─ 案例库：  ~/.claude/knowledge/cases/wiki/
  │   │   ├─ Hooks:   ~/.claude/hooks/
  │   │   ├─ 脚本:    ~/.claude/scripts/
  │   │   ├─ Skills:  ~/.claude/skills/ + ~/.agents/skills/
  │   │   └─ 配置:    ~/.claude/settings.json
  │   └─ 模式 B（条件触发）：Python/ML 项目审计
  │       └─ 仅当工作区含 pyproject.toml / requirements.txt
  ├─ [Layer 2 — 修复层] 基于 Layer 1 汇总结果执行安全可论证的修复
  └─ [Layer 3 — 进化层] 外部知识扫描（WebSearch + Context7）—— 永不可跳过

📂 目标文件夹（Target folders）：
  ├─ 主审计范围：~/.claude/  （独立配置仓库，default scope）
  ├─ 关联范围 1：~/.agents/skills/  （skill 源，需与 ~/.claude/skills 保持 symlink 一致）
  ├─ 关联范围 2：mem0 云端记忆  （双轨同步检测的 L3 来源）
  └─ 条件范围  ：当前工作区 Python 项目  （仅 Layer 1 模式 B 触发时审计）

⏱️ 预期耗时：60-180 秒（取决于 Agent 并行度 + WebSearch 响应速度）
🎯 完成标准：五段式进化报告 + 前后健康分 + 10 项 Verification Gates 全部通过

═══════════════════════════════════════════════════════════
              预声明结束 — 正式审计即将开始
═══════════════════════════════════════════════════════════
```

**特殊情况处理**：

| 场景 | 预声明补充内容 |
|------|----------------|
| 用户未指定工作区，但当前 cwd 在 `~/Repo/xxx` 下且有 Python 项目 | 在 "条件范围" 一行追加：当前 cwd = `$(pwd)` |
| 用户明确指定了"只审计 X" | 将"目标文件夹"章节替换为用户指定的 X，其他保持默认 |
| 用户说"全面审计" / "深度审计" | 在 "Layer 3 进化层" 标注 `深度模式：3-tool cascade (minimax → kimi-webbridge → anysearch) + 2 次 Context7` |
| mem0 MCP 不可用 | 在 "关联范围 2" 后追加警告：`⚠️ mem0 MCP 不可用，L3 记忆对齐将降级为 L1/L2 双轨` |

**反例（禁止）**：

```text
❌ 直接开始扫描 ~/.claude/rules/ 而无任何说明
❌ "我将审计你的 Claude Code 配置..."  ← 太口语、缺格式
❌ 只说"开始审计"  ← 完全没告知范围
```

---

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

## 并行 Agent 策略

> **下沉到 references**：完整 108 行已迁出（含 3 个 Layer Agent 启动模板 + 8 维度加权模型）。
> 详见 [`references/agent-strategy.md`](references/agent-strategy.md)

**核心原则**：无依赖关系的任务必须并行启动 Agent，缩短总耗时；有依赖关系的任务必须顺序执行。

**3 个并行域**：
- **Layer 1 双模并行**: `Agent-Audit-A`（配置）+ `Agent-Audit-C`（Python/ML）同时启动
- **Layer 3 多源并行**: `Agent-Evolve-1/2/3`（配置/ML/文档）同时启动
- **Layer 2 子任务并行**: `Agent-Fix-Rules/Memory/Skills/Python` 按文件类型并行

**8 维度加权模型**：architecture 25% + integrity 30% + security 20% + consistency 20% + github_sync 5% + timeliness 5% + redundancy 5% + performance 5%。

**Consistency 父维度展开 (v2.6, 2026-06-10)**:
父维度 20% 拆为 6 个子维度, 详见 [`references/consistency-6d/`](references/consistency-6d/):

| # | 子维度 | 文件 |
|---|------|------|
| 1 | 术语一致性 | [`1-terminology.md`](references/consistency-6d/1-terminology.md) |
| 2 | 交叉引用完整性 | [`2-cross-references.md`](references/consistency-6d/2-cross-references.md) |
| 3 | 规则冲突检测 | [`3-rule-conflicts.md`](references/consistency-6d/3-rule-conflicts.md) |
| 4 | 索引/指针有效性 | [`4-index-validity.md`](references/consistency-6d/4-index-validity.md) |
| 5 | 格式/前置元数据 | [`5-frontmatter.md`](references/consistency-6d/5-frontmatter.md) |
| 6 | 优先级与作用域 | [`6-priority-scope.md`](references/consistency-6d/6-priority-scope.md) |

**审计覆盖扩展 (v2.6.1, 2026-06-10)**: 2 个新检测维度, 跟 consistency-6d 互补
- **Dead Code / Orphan** → [`dead-code-orphan.md`](references/dead-code-orphan.md)
- **Commands → Skills Migration** → [`commands-to-skills-migration.md`](references/commands-to-skills-migration.md)

**Layer 3 进化层约束**：每次 `rich审计` 都必须执行外部扫描（禁止以"分数已经很高"为由跳过 WebSearch / Context7）。

**Tri-Search Protocol v2.6 (2026-06-10 升级, 替换旧 3-tool cascade)**:

4-tool **parallel fan-out** → merge + compare → 冲突再查 (≤2 层递归) → 输出契约

| Phase | 工具 | 角色 |
|-------|------|------|
| **A. Parallel Fan-out** | `mcp__MiniMax__web_search` ∥ `kimi-webbridge` ∥ `anysearch` ∥ `WebFetch` | 4 路独立采信, 同 query |
| **B. Merge + Compare** | (内部) | 共识 (高 confidence) / 冲突 (需溯源) |
| **C. Conflict Resolve** | Phase A 递归, ≤2 层 | 冲突项再查; 仍不收敛 → 报告"未收敛"降级人工 |

**输出契约 (3 字段必填)**: 工具 / 搜索内容 / 结论

**Why 4 tools**: 三角测量 = (a) redundancy (1 tool 挂掉不影响) + (b) depth (kimi-webbridge 抓单源抓不到) + (c) cross-validation (anysearch 验证 minimax) + (d) direct fetch (WebFetch 读 top URL 全文). 比 3-tool cascade 多了 WebFetch 抓 URL 全文这一层, 防"搜到 URL 但没读全文"假性验证.

**降级**: 任一工具不可用时 (e.g. kimi-webbridge 502), 用同源工具替代, 报告标注"降级". 完整协议见 [`references/tri-search-protocol.md`](references/tri-search-protocol.md).

---
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

## 记忆系统对齐检测（双轨同步）

> 详细内容见 [`references/memory-alignment.md`](references/memory-alignment.md)。摘要：
> - **L1** MEMORY.md → case 文件：Phantom entries
> - **L2** case 文件 → MEMORY.md：Missing entries
> - **L3** mem0 → case 文件：mem0 cloud drift
> - 已知陷阱（2026-06-02）：glob 模式不递归 `archive-*/` 子目录导致 197 false positives（已修）

---

## 输出格式（五段式进化报告 + Action Plan）

1. **审计层**: 按维度汇总发现，附证据
2. **指令进化**: 建议新增/修改的规则
3. **SOP 提取**: 可复用检查流程
4. **进化层**: 外部知识扫描结果 + 已采纳/待确认进化项
5. **最终状态**: 前后健康分 + 修复清单 + 待处理项

### JSON 报告结构（v2.0）

```json
{
  "meta": { "tool": "rich-audit.py", "version": "2.0.0", "fix_mode": false },
  "project_modes": { "python": true, "python_ml": true },
  "dimensions": { "integrity": { "findings_count": 0, "findings": [] }, ... },
  "summary": {
    "health_score": 98,
    "severity_counts": { "HIGH": 0, "MED": 3, "LOW": 2 },
    "score_breakdown": {
      "architecture": { "raw_score": 100, "weight": 0.25, "contribution": 25.0, ... }
    }
  },
  "action_plan": {
    "P0": [],
    "P1": [ { "severity": "MED", "message": "...", "auto_fix": "fix_symlink" } ],
    "P2": []
  }
}
```

- **`action_plan`**: 按 P0/P1/P2 优先级分组，每条附 `auto_fix` 类型（如有）
- **`score_breakdown`**: 8 维度加权明细，便于定位短板
- **`project_modes`**: 自动检测当前工作区的 Python 项目类型

---

## 自动修复行为

> 完整 19 行已下沉到 [`references/auto-fix.md`](references/auto-fix.md)。本节保留摘要。

**脚本层安全修复**（无破坏性）：hook 清理、JSON 修复、权限重置、skill symlink 修复、orphan 清理、Python README 模板。

**AI 层语义修复**（允许编辑）：合并重复规则、补充 Binary Assertions、更新陈旧记忆引用、统一 torch 版本。

---

## OMC 生态联动

- **审计前**: 调用 `/instinct-status`，将 instinct 健康度纳入上下文
- **审计后**: 若发现 >= 3 个同类问题，建议运行 `/evolve` 固化新本能
- **Case 联动**: 若发现新的失败模式，建议生成 CASE 归档

---

## 触类旁通处理协议

> 详细内容见 [`references/cascade-reports.md`](references/cascade-reports.md)。摘要：
> - 触发词："触类旁通" / 未指定 scope
> - 三层行动：L1 workspace / L2 全机器 repo / L3 同类现象
> - 报告位置：`~/.claude/knowledge/cascade-reports.md`

---

## 成功标准

1. `rich审计` 触发后执行完整三层流水线（审计 + 修复 + 进化）
2. 双模检测：Claude Code 配置 + Python/ML 项目（如适用）
3. Layer 1 JSON 输出有效，覆盖架构健康度 + Python 健康度
4. Layer 3 产出进化报告，包含外部知识对比与搜索证据
5. 安全机械修复自动应用，无需用户干预
6. 计算修复前后健康评分（0-100）和进化度评分（0-100）
7. **永不休眠：无论健康度多少，Layer 3 必须执行 Tri-Search Protocol v2.6 (4-tool parallel fan-out: `mcp__MiniMax__web_search` ∥ `kimi-webbridge` ∥ `anysearch` ∥ `WebFetch` → merge+compare → 冲突再查 ≤2 层) + 1 次 Context7 查询。输出契约 (3 字段必填): 工具 / 搜索内容 / 结论。**
8. **进化报告必须包含"本次搜索发现的新知识"段落，即使结论为"无新进展"，也必须附搜索证据**

## Verification Gates (报告完成前强制检查)

> **下沉到 references**：10 项物理验证完整版见 [`references/verification-gates.md`](references/verification-gates.md)。
>
> **Why**：rich-audit 自身曾多次出现误报（memory-audit cascade、ghost case detection）。验证门禁防止审计工具自身的幻觉被当作结论输出。

**简版 5 项速查**（完整 10 项见 references）：

1. **备份确认**: `ls -la ~/.claude/backups/` — 确认本次审计备份已创建
2. **规则语法检查**: 修改的 `.md` 规则文件 frontmatter 未损坏
3. **JSON 有效性**: 修改的 `settings.json` `python3 -m json.tool` 通过
4. **GitHub 同步状态**: `git -C ~/.claude log @{u}..HEAD --oneline` 无未推送
5. **MEMORY.md 索引一致性**: L1_PHANTOM=0 / L2_MISSING=0 / L3_CASE_GAP=0
## 安全与回滚

- 任何修改前自动备份到 `~/.claude/backups/rich-audit-YYYY-MM-DD-HHMMSS/`
- 所有修复均为幂等操作，可安全重跑
