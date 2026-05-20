---
name: rich-audit
description: |
  三层进化系统：审计（发现问题）→ 修复（解决问题）→ 进化（主动获取外部先进知识并应用）。
  三模审计：Claude Code 配置审计 + Astro 前端项目审计 + Python/ML 项目审计。
  触发词：rich审计, /rich-audit, 进化
license: MIT
metadata:
  version: "2.3.0"
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
    - astro
    - frontend
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

## 执行流程（三层进化系统 + 并行 Agent 架构）

```
User: "rich审计" / "进化"
  |
  v
[1] Layer 1 — 审计层（Audit）【并行 Agent 启动】
    ├─ Agent-Audit-A → Claude Code 配置审计（默认）
    ├─ Agent-Audit-B → Astro 前端项目审计（条件触发）
    ├─ Agent-Audit-C → Python/ML 项目审计（条件触发）
    └─ 汇总 → 合并三份审计 JSON，计算综合健康分
  |
  v
[2] Layer 2 — 修复层（Fix）【顺序执行】
    AI 读取 Layer 1 汇总 JSON + 关键配置文件
    执行规则语义冲突检测、行为漂移检测、OMC 健康评估
    自动修复安全可论证的问题
  |
  v
[3] Layer 3 — 进化层（Evolve）【并行 Agent 启动】
    ├─ Agent-Evolve-1 → WebSearch: Claude Code / OMC 最新实践
    ├─ Agent-Evolve-2 → WebSearch: 前端/Astro/Tailwind 最新实践（如有 Mode B）
    ├─ Agent-Evolve-3 → WebSearch: Python/ML/PyTorch 最新实践（如有 Mode C）
    ├─ Agent-Evolve-4 → Context7 查询官方文档（Astro / Python / Claude SDK）
    └─ 汇总 → 对比当前配置，产出进化建议
  |
  v
[4] 生成进化报告（五段式）
  |
  v
[5] 最终报告（前后健康分 + 修复清单 + 进化清单 + 待处理项）
```

---

## 并行 Agent 策略

> **核心原则**：无依赖关系的任务必须并行启动 Agent，缩短总耗时；有依赖关系（如修复依赖审计结果、报告依赖修复结果）的任务必须顺序执行。

### Layer 1 审计层 — 三模并行

三个审计模式相互独立，**同时启动**三个 Agent：

| Agent | 名称 | 职责 | 输出格式 |
|-------|------|------|----------|
| `Agent-Audit-A` | 配置审计 | 扫描 `~/.claude/rules/`、`memory/`、`skills/`、`settings.json`，计算架构健康度 | JSON：`{ "architecture_health": N, "rules_issues": [...], "memory_issues": [...] }` |
| `Agent-Audit-B` | 前端审计 | 检测 Astro 项目（如有），执行 build/check、i18n 对比、合规性检查 | JSON：`{ "frontend_health": N, "build_status": "pass/warn/fail", "i18n_issues": [...] }` |
| `Agent-Audit-C` | ML 审计 | 检测 Python 项目（如有），检查依赖安全、版本一致性、CUDA 兼容、类型检查 | JSON：`{ "python_health": N, "dependency_issues": [...], "type_check_status": "..." }` |

**启动方式**：单次 `Agent` 工具调用中批量发送（单次消息内多个 Agent 调用并行执行）。

**汇总规则**：
- 等待全部 Agent 返回后，合并三份 JSON
- 综合健康分 = weighted_average(8 维度加权模型)
  - architecture 25% | integrity 25% | security 15% | consistency 15%
  - github_sync 5% | timeliness 5% | redundancy 5% | performance 5%
  - 前端/ML 触发时，额外叠加前端健康度 × 0.25 / ML 健康度 × 0.25（从基础权重中各扣除 12.5%）
- 脚本层使用 `_FileIndex` 统一预扫描 + `ThreadPoolExecutor(max_workers=4)` 并行执行维度，消除重复 rglob

### Layer 3 进化层 — 多源并行扫描

Layer 2 完成后，**同时启动**多个进化 Agent：

| Agent | 名称 | 职责 | 搜索关键词示例 |
|-------|------|------|----------------|
| `Agent-Evolve-1` | 配置进化 | WebSearch: Claude Code 最新最佳实践、OMC 生态更新 | `"Claude Code best practices 2026"`, `"OMC oh-my-claudecode latest"` |
| `Agent-Evolve-2` | 前端进化 | WebSearch: Astro 6.x / Tailwind v4 / 前端构建最新实践（仅 Mode B 触发） | `"Astro 6 best practices 2026"`, `"Tailwind v4 new features"` |
| `Agent-Evolve-3` | ML 进化 | WebSearch: Python / PyTorch / ML 项目最佳实践（仅 Mode C 触发） | `"PyTorch best practices 2026"`, `"Python project structure 2026"` |
| `Agent-Evolve-4` | 文档进化 | Context7 查询：Astro docs / Python docs / Claude SDK docs | 使用 `mcp__context7__resolve-library-id` + `query-docs` |

**启动方式**：单次 `Agent` 工具调用中批量发送。

**汇总规则**：
- 收集所有 Agent 返回的 "新知识条目"
- 与当前配置逐项对比，标记：
  - `ADOPTED` — 已采纳并应用
  - `PENDING` — 待用户确认
  - `REJECTED` — 不适用或已过时
  - `NO_CHANGE` — 无新进展（仍需列出搜索证据）

### 禁止并行的环节（顺序执行）

| 环节 | 原因 |
|------|------|
| Layer 2 修复层 | 必须基于 Layer 1 完整汇总结果才能判断修复优先级 |
| 生成进化报告 | 必须基于 Layer 2 修复结果 + Layer 3 进化结果 |
| Verification Gates | 必须在所有修改完成后执行，否则验证结果不完整 |

---

### Layer 3 进化层详解

进化层是区分"审计"与"自我进化"的核心。详细来源、基准和搜索策略见 [references/evolution-sources.md](references/evolution-sources.md)。

**核心约束**：无论当前健康度多少，每次 `rich审计` 都必须执行 Layer 3 外部扫描。禁止以"分数已经很高"为由跳过 WebSearch / Context7。

---

## 三模扫描范围

### 模式 A: Claude Code 配置审计（默认）

| 路径 | 用途 |
|------|------|
| `~/.claude/rules/` | 行为护栏与约束 |
| `~/.claude/memory/` | 持久化用户/项目/上下文记忆 |
| `~/.claude/hooks/` | PreToolUse / PostToolUse / Stop hooks |
| `~/.claude/scripts/` | 自动化脚本 |
| `~/.claude/skills/` | OMC 和自定义 skills |
| `~/.claude/settings.json` | Claude Code 配置 |
| `~/.omc/skills/` | OMC 市场与用户 skills |
| `~/.agents/skills/` | `.agents` 框架 skills（应与 `~/.claude/skills/` 保持硬链接一致） |

### 模式 B: Astro 前端项目审计（条件触发）

检测 `astro.config.mjs` / `package.json` 中有 `astro` 时叠加：
- **Build Health**: `npm run build` + `astro check`
- **i18n Parity**: `en.json` / `zh.json` key 对比
- **Astro 2025 Compliance**: `ClientRouter`、 `@tailwindcss/vite`

详见 [references/frontend-checklist.md](references/frontend-checklist.md)。

### 模式 C: Python / ML 项目审计（条件触发）

检测 `pyproject.toml` / `requirements.txt` 时叠加：
- **Dependency Security**: torch CVE 检查、wandb/GitHub token 检测
- **Version Consistency**: torch 版本、MarkupSafe 冲突
- **CUDA Compatibility**: `torch.cuda.is_available()`
- **Project Completeness**: README 质量、requires-python
- **Type Checking**: pyright/mypy 配置

详见 [references/python-checklist.md](references/python-checklist.md)。

---

## 架构健康度检测（Architecture Health）

| 指标 | 健康阈值 | 超标后果 |
|------|----------|----------|
| 规则文件总数 | ≤ 10 个 | 注意力竞争 |
| 规则总行数 | ≤ 200 行 | 遵守率暴跌 |
| CLAUDE.md 长度 | ≤ 80 行 | resume 挤占上下文 |
| 单规则文件长度 | ≤ 50 行 | 长规则被忽略 |
| frontmatter 覆盖率 | 100% | 加载器不识别 |

检测命令见 [references/audit-patterns.md](references/audit-patterns.md)。

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
  "project_modes": { "astro": false, "python": true, "python_ml": true },
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
- **`project_modes`**: 自动检测当前工作区的 Astro / Python 项目类型

---

## 自动修复行为

### 脚本层安全修复（无破坏性）
- 删除指向不存在文件的 hook
- 清理过量的 settings.json 备份
- 重新格式化损坏的 JSON
- 将 777 权限重置为 644/755
- **Skill symlink 修复**: 物理目录 → symlink、broken symlink → 重建、missing symlink → 创建
- **Orphan 清理**: `.claude/skills/` 中存在但 `.agents/skills/` 中不存在的孤立项自动移除
- **Python**: 空 README.md 自动替换为模板、补充缺失的 requires-python

### AI 层语义修复（允许编辑）
- 合并重复规则、重写冲突段落
- 补充缺失的 Binary Assertions
- 更新陈旧的记忆引用
- **Python**: 建议统一 torch 版本、添加 lock 文件、修复 MarkupSafe 约束

---

## OMC 生态联动

- **审计前**: 调用 `/instinct-status`，将 instinct 健康度纳入上下文
- **审计后**: 若发现 >= 3 个同类问题，建议运行 `/evolve` 固化新本能
- **Case 联动**: 若发现新的失败模式，建议生成 CASE 归档

---

## 触类旁通处理协议

> 触发词："触类旁通"、或发现问题但未指定 scope 时自动联想
>
> 记录位置：`~/Repo/webs/webs-context.md`（网站矩阵专用上下文）

### 三层行动规范

| 层 | 触发时机 | 动作 |
|----|---------|------|
| **L1** | 发现/修复问题时 | 检查 `~/Repo/webs/OSA/` 和 `~/Repo/webs/GDKVM/` 是否同样受影响 |
| **L2** | central 脚本变更时 | 扫描所有 git repo，确认 `~/.claude/scripts/` 下游无副本残留，全部 symlink 化 |
| **L3** | 发现新 central 脚本时 | 检查是否需要同样建立 symlink 下游分发机制 |

### Central Scripts 扫描命令

```bash
SCRIPT_NAMES=$(find ~/.claude/scripts -maxdepth 1 -type f | xargs -I{} basename {} | sort)
find ~ -maxdepth 5 -name ".git" -type d 2>/dev/null | sed 's/\/.git$//' | while read repo; do
  case "$repo" in "$HOME/.claude"|"$HOME/.claude/"*) continue ;; esac
  for name in $SCRIPT_NAMES; do
    find "$repo" -maxdepth 6 -name "$name" ! -type l 2>/dev/null | while read f; do
      echo "[COPY] $f"
    done
  done
done 2>/dev/null | grep -v "/.claude/" | sort
```

### 处理报告模板

```
### REPORT-{issue-id}-{date}
**问题**：{一句话描述}
**发现位置**：{哪个 repo/文件}
**修复**：{怎么修的}
**触类旁通三层**：
1. L1（workspace 内检查）：{OSA/GDKVM 是否受影响}
2. L2（全机器 repo 扫描）：{发现 X 处副本，已处理}
3. L3（同类现象）：{是否有其他 central 脚本存在同样问题}
```

### 自动联想规则

触发"触类旁通"时，Agent 必须：
1. 生成处理报告（填模板）
2. 依次执行 L1 → L2 → L3
3. 将结果同步到 `~/Repo/webs/webs-context.md`

---

## 成功标准

1. `rich审计` 触发后执行完整三层流水线（审计 + 修复 + 进化）
2. 三模检测：Claude Code 配置 + Astro 项目（如适用）+ Python/ML 项目（如适用）
3. Layer 1 JSON 输出有效，覆盖架构健康度 + 前端健康度 + Python 健康度
4. Layer 3 产出进化报告，包含外部知识对比与搜索证据
5. 安全机械修复自动应用，无需用户干预
6. 计算修复前后健康评分（0-100）和进化度评分（0-100）
7. **永不休眠：无论健康度多少，Layer 3 必须执行至少 2 次 WebSearch 或 1 次 Context7 查询，并在报告中列出搜索关键词、来源 URL 与结论**
8. **进化报告必须包含"本次搜索发现的新知识"段落，即使结论为"无新进展"，也必须附搜索证据**

## Verification Gates (报告完成前强制检查)

**在声明 "审计完成" 前，必须执行以下物理验证并粘贴输出：**

1. **备份确认**: `ls -la ~/.claude/backups/ | head -5` — 确认本次审计备份已创建
2. **规则语法检查**: 如修改了任何 `.md` 规则文件，执行 `head -5 <file>` 确认 frontmatter 未损坏
3. **JSON 有效性**: 如修改了 `settings.json`，执行 `python3 -m json.tool ~/.claude/settings.json > /dev/null && echo "JSON_VALID"` — 确认无语法错误
4. **差异摘要**: `git -C ~/.claude diff --stat 2>/dev/null || echo "NO_GIT_TRACKING"` — 确认变更范围符合预期
5. **GitHub 同步状态**: 执行 `git -C ~/.claude log @{u}..HEAD --oneline 2>/dev/null | wc -l` 和 `git -C ~/.agents/skills log @{u}..HEAD --oneline 2>/dev/null | wc -l` — 确认无未推送提交
6. **项目模式检测验证**: 如当前工作区含 Astro/Python 项目，确认 `project_modes` 输出正确标记了对应模式
7. **Skill 目录 Symlink 一致性**: 如修改了 skill 文件，执行以下命令确认 `.claude/skills/` 与 `.agents/skills/` symlink 一致：
   ```bash
   find ~/.claude/skills -maxdepth 1 -type l | while read f; do
     rel=$(basename "$f")
     target=$(readlink "$f")
     expected="$HOME/.agents/skills/$rel"
     [ "$target" = "$expected" ] && echo "[OK] $rel" || echo "[MISMATCH] $rel -> $target (expected $expected)"
   done
   ```
8. **健康分计算**: 重新运行 `python3 ~/.claude/scripts/rich_audit.py`，确认 8 维度分数已正确记录

**若任何验证失败，审计未完成。** 修复后重新运行验证。

**Why**: rich-audit 自身曾多次出现误报（memory-audit cascade、ghost case detection）。验证门禁防止审计工具自身的幻觉被当作结论输出。

---

## 安全与回滚

- 任何修改前自动备份到 `~/.claude/backups/rich-audit-YYYY-MM-DD-HHMMSS/`
- 所有修复均为幂等操作，可安全重跑
