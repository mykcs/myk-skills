# PER Workflow 框架（Plan → Execute → Verify）

> 统一 workflow 抽象，供 website-improve / host-self-evolve / paper-into-notion 引用。
> Source of truth: `~/.agents/skills/website-improve/references/per-workflow-framework.md`

## 核心思想

把任何复杂 skill 的执行拆成三段：

1. **Plan（计划）**：理解意图、定范围、识别风险、输出阶段计划。
2. **Execute（执行）**：按 plan 改文件、跑命令、记录日志。
3. **Verify（验收）**：按验收标准检查，PASS 才 done；FAIL 则 reject 回 Execute 重做。

三段之间通过 **artifact 文件** handoff，不允许口头传话或共享 context window。

## 角色与职责

| 角色 | 可做什么 | 不可做什么 | 产出 artifact |
|------|----------|-----------|---------------|
| **Planner** | 解析请求、写 plan、标风险、排阶段 | 直接改文件、跑构建、自己标 done | `plan.json` / `plan.md` |
| **Executor** | 读 plan、改文件、跑命令、写 exec log | 跳过 plan、自己标 done、绕过 verifier | `exec-log.json` / `exec-log.md` |
| **Verifier** | 读 plan + exec log、跑验收、出 verdict | 改文件、替 executor 修 bug | `verdict.json` / `verdict.md` |

## Handoff 规则

1. Planner → Executor：必须交付 plan artifact，含 scope、acceptance criteria、risk list。
2. Executor → Verifier：必须交付 exec-log artifact，含实际改动、命令输出、git commits。
3. Verifier → Executor（FAIL）：必须指出具体 FAIL 项 + 复现证据，Executor 重做整轮。
4. Verifier → User（PASS）：必须附 5 字段自检表（path / commit / push / CI / owner）。

## Artifact Schema

### plan.json

```json
{
  "skill": "website-improve",
  "version": "4.1.0",
  "trigger": "user prompt",
  "scope": ["A", "B", "D"],
  "sites": ["mykcs.github.io", "GDKVM", "OSA", "content2html"],
  "acceptance_criteria": [
    "4 站 CI green",
    "5 字段自检全过",
    "no P0/P1 deferred"
  ],
  "risks": [
    {
      "item": "owner 隔离",
      "level": "high",
      "mitigation": "push 前 git remote -v 三次确认"
    }
  ],
  "phases": [
    {"name": "pre-flight", "owner": "planner"},
    {"name": "audit", "owner": "executor"},
    {"name": "fix", "owner": "executor"},
    {"name": "verify", "owner": "verifier"}
  ]
}
```

### exec-log.json

```json
{
  "plan_ref": "plan.json",
  "files_changed": [
    {"path": "src/layouts/BaseLayout.astro", "add": 12, "del": 3}
  ],
  "commands_run": [
    {"cmd": "npm run build", "exit": 0}
  ],
  "git_commits": [
    {"site": "mykcs.github.io", "sha": "a1b2c3d", "msg": "fix(a11y): ..."}
  ],
  "deferred": [],
  "blocked": []
}
```

### verdict.json

```json
{
  "plan_ref": "plan.json",
  "exec_log_ref": "exec-log.json",
  "verdict": "PASS",
  "checks": {
    "path": "PASS",
    "commit": "PASS",
    "push": "PASS",
    "ci": "PASS",
    "owner": "PASS"
  },
  "notes": "4/4 CI success, no deferred items"
}
```

## 反模式（永久失效）

- ❌ 1 个 sub-agent 跑完 3 角色。
- ❌ Executor 自己标 done。
- ❌ Verifier FAIL 还强行 ship。
- ❌ sub-agent 之间口头传话，不走 artifact。
- ❌ Planner 直接改文件或跑命令。
- ❌ Verifier 改文件替 Executor 修 bug。

## 与三技能的映射

| 技能 | Planner 做什么 | Executor 做什么 | Verifier 做什么 |
|------|---------------|----------------|----------------|
| **website-improve** | 输出 7 段 pre-flight + sub-mode 路由（A/B/C/D） | 跑 audit、fix、smart-push | 4 站 CI green + 5 字段自检 + curl live URL |
| **host-self-evolve** | banner + Phase 1 说明 + Layer 0-3 任务拆分 | 跑 7 sub-task、cleanup、N-tool fan-out | 5/6 字段自检 + memory-bench score + CI gate |
| **paper-into-notion** | 解析 URL + 判定 modal + 选 Notion db/page | fetch、fill 3 字段、patch block | 5 字段验证 + block layout check + patch recovery |

## 失败处理

| 场景 | 处理 |
|------|------|
| Verifier FAIL 第 1 次 | Executor 重做整轮 |
| Verifier FAIL 第 2 次 | AskUserQuestion：A 再试 / B 降级 / C 停止 |
| Executor 无法复现 | Verifier 提供最小复现命令 |
| Planner scope 不清 | 先 AskUserQuestion 明确 scope 再出 plan |

## 何时使用本框架

任何 skill 满足以下任一条件时，应显式引用本框架：

- 需要 2 个以上阶段才能完成的任务。
- 需要独立验收者才能避免 false completion。
- 输出质量不稳定、某类任务反复出错。
- 用户明确说“要有 workflow / 计划者 / 执行者 / 验收者”。
