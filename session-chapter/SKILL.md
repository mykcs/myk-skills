---
name: session-chapter
description: |
  上下文章节管理：在压缩前保存分层状态，并支持新窗口无缝恢复。
  触发词：上下文满了、保存章节、新窗口继续、待会再继续、chapter resume、继续任务。
version: "1.0.0"
author: "mykcs"
license: "MIT"
last_updated: "2026-07-19"
---

# Session Chapter v2 — 上下文章节保存与恢复

> 设计参考：
> - MemoryForge compaction survival loop (marolinik/claude-code#25999)
> - LangGraph semantic checkpointing (phantom-byte.com)
> - Factory.ai anchored iterative summarization (zylos.ai)
> - Claude Code native `/rewind`, `/compact [instruction]`, named sessions

## 核心改进（v2 vs v1）

| 维度 | v1 | v2 |
|------|-----|-----|
| 存储位置 | `.omc/notepad.md` Working Memory（不被 SessionStart 自动加载） | `.omc/chapters/` 分层文件 + **Priority Context**（SessionStart 自动注入） |
| 压缩策略 | 直接 `/compact` | 优先 `/rewind` 定点压缩，次选带自定义指令的 `/compact` |
| 恢复方式 | `--resume UUID` 为主 | **新窗口干净上下文** 为主，`--resume` 为备用 |
| 决策记录 | 覆盖式 | **追加-only** `decisions.md`，形成决策链 |
| 诊断步骤 | 无 | 先运行 `/context` 查看 token 组成 |
| 跨窗口恢复 | 手动 `/notepad_read` + 粘贴 | `SessionStart` hook **自动注入** Priority Context |

---

## 触发条件

以下任一出现时立即执行（不要等到自动压缩）：

1. Token 使用率 > 60%（Claude Code StatusLine 显示）
2. 对话超过 40 轮且涉及多文件修改
3. 用户说"上下文满了"、"保存章节"、"新窗口继续"、"待会再继续"
4. **Drift 信号**：Claude 开始重复之前的内容、反复建议已尝试过的方案
5. 一个自然子任务完成（如"规划完成"、"测试通过"、"build 成功"）

---

## 执行步骤

### 第一步：诊断上下文状态

运行 `/context`（或 `/cost`），记录：
- 当前 token 使用率
- 距离上限还剩多少 tokens
- 主要消耗来源（大量文件读取 / 长命令输出 / 对话轮数）

### 第二步：提取并分层保存状态

#### 2.1 读取现有状态
- `git status --short`
- `/notepad_read`（读取 Priority Context 和 Working Memory）
- 从当前对话中提取：任务名称、阶段、关键决策、下一步、阻塞项

#### 2.2 创建 `.omc/chapters/` 目录（如不存在）

```bash
mkdir -p .omc/chapters
```

#### 2.3 写入 `current-chapter.md`（覆盖式）

```markdown
## 任务：[任务名称]
## 阶段：[数字/总阶段，如 2/5]
## 完成：
- [关键成果 1]
- [关键成果 2]
## 下一步：
[具体下一步，精确到文件名和动作]
## 阻塞：
[未解决问题 + 已尝试方法]
## 涉及文件：
[git status --short 输出的文件列表]
## Token：[使用率]/[总量] @ [ISO 时间戳]
```

#### 2.4 追加 `decisions.md`（追加-only，仅当有新决策时）

```markdown
### [ISO 时间戳]
- **决策**：[决策内容]
- **原因**：[为什么做这个选择]
- **替代方案**：[考虑过但放弃的方案]
- **影响文件**：[相关文件]
```

> **Why append-only**：事件溯源模式。决策链不会被覆盖，新窗口恢复时能看到完整推理历史。

#### 2.5 追加 `session-log.md`

```markdown
- [时间戳] Chapter [序号] | Token [使用率] | 阶段 [X/Y] | 下一步：[一句话摘要]
```

#### 2.6 更新 Priority Context（关键！）

使用 `/notepad_write_priority`，内容格式：

```markdown
**当前任务**：[任务名称] — 阶段 [X/Y]
**下一步**：[精确到文件和动作]
**阻塞**：[如有]
**涉及文件**：[文件列表]
**决策锚点**：见 `.omc/chapters/decisions.md`
**恢复时间**：[ISO 时间戳]
```

> **Why Priority Context**：用户的 `session-start.mjs` 会在每次 SessionStart 时自动注入 `## Priority Context` 到上下文。把章节摘要放在这里，**新窗口启动时自动恢复**，无需手动操作。

### 第三步：选择压缩策略

根据上下文诊断结果，选择最佳压缩方式：

#### 策略 A：定点压缩（最精准）
如果用户知道从哪一段对话开始变得臃肿：
1. 让用户按 `Esc` + `Esc` 打开 `/rewind`
2. 选择一个早期的消息点
3. 选择 **"Summarize from here"**
4. 保留指令： `"Keep current task, decisions, and next steps. Summarize exploration and failed attempts."`

> 定点压缩只压缩指定点之后的对话，保留前面完整上下文，比 `/compact` 全量压缩更可控。

#### 策略 B：自定义指令压缩（默认）
如果无法定点：
```
/compact Keep the current task stage, next steps, and key decisions in .omc/chapters/. Summarize exploration, failed attempts, and redundant file reads.
```

#### 策略 C：不压缩，直接新窗口（如果已 > 85%）
如果 token 使用率已非常高，压缩效果有限：
- 直接输出恢复提示
- 建议用户**开新窗口**继续（获得 100% 干净上下文）

### 第四步：输出恢复提示

获取 Session UUID：
```bash
ls -t ~/.claude/sessions/*.json | head -1 | xargs jq -r '.sessionId'
```

输出格式：
```
═══════════════════════════════════════════════════════════════════
📌 章节已保存 | Token: [使用率]/[总量] | 阶段: [X/Y]

[推荐] 新窗口继续（干净上下文）：
  cd [项目绝对路径] && claude
  → SessionStart hook 会自动注入 Priority Context
  → 然后说：/chapter_resume 查看完整决策链

[备用] 恢复本会话：
  claude --resume [sessionId]

[保险] 交互选择：
  claude --resume
═══════════════════════════════════════════════════════════════════
```

### 第五步：执行压缩（如选择策略 B）

执行 `/compact [custom instruction]`

---

## 新窗口恢复流程

### 方式 A（推荐）：干净上下文 + 自动注入

```bash
cd [项目路径] && claude
```

启动后 `session-start.mjs` 会自动注入 Priority Context。Claude 立刻知道：
- 当前任务是什么
- 下一步做什么
- 有哪些阻塞

### 方式 B：读取完整决策链

在新窗口中说：
```
/chapter_resume
```

本 Skill 被触发后执行：
1. 读取 `.omc/chapters/current-chapter.md`
2. 读取 `.omc/chapters/decisions.md`（最近 5 条）
3. 读取 `.omc/chapters/session-log.md`
4. 输出结构化恢复摘要

### 方式 C：恢复原始会话

```bash
claude --resume [sessionId]
```

> 注意：`--resume` 恢复的是**完整对话历史**，token 使用率不变。如果原会话已经 85%+，恢复后很快会再次触达上限。优先使用方式 A。

---

## 与 OMC 工具的配合

| 工具 | 角色 |
|------|------|
| `SessionStart` hook | 自动注入 Priority Context，实现跨窗口恢复 |
| `/notepad_write_priority` | 保存章节摘要到压缩后仍存活的位置 |
| `/notepad_read` | 查看完整 notepad |
| `/rewind` | 定点压缩，保留早期上下文 |
| `/compact` | 全量压缩，配合自定义指令使用 |
| `.omc/chapters/` | 分层持久化状态（current + decisions + log） |

---

## 推荐配置：PostCompact Hook（可选增强）

如果希望压缩后**当前会话**也自动恢复提示，可在 `~/.claude/settings.json` 中添加：

```json
{
  "hooks": {
    "PostCompact": [
      {
        "type": "command",
        "command": "cat .omc/chapters/current-chapter.md 2>/dev/null || true"
      }
    ]
  }
}
```

这样压缩完成后，当前窗口会自动看到章节摘要。

---

## 已知问题与修复记录

### 2026-04-15 v1 → v2 升级
**问题**：v1 把章节摘要写入 `.omc/notepad.md` 的 Working Memory，但 `session-start.mjs` 只自动注入 Priority Context。导致新窗口启动后**不会自动恢复**任务状态。

**修复**：
1. 章节摘要改写入 `/notepad_write_priority`
2. 同时创建 `.omc/chapters/` 分层文件作为详细备份
3. 恢复方式从 `--resume` 改为**新窗口干净上下文**为主

### 2026-04-15: `--resume` 必须是 UUID
**已在 v2 中降级为备用方案**。

---

## Generalized Heuristic

> **IF** 长任务会话的上下文压力 > 60% 或出现 drift 信号
> **THEN** 执行 `/session-chapter`：诊断 → 分层保存 → 写入 Priority Context → 精准压缩 → 输出恢复提示
> **AND** 新窗口首选 `cd [项目] && claude` 获得干净上下文，由 SessionStart hook 自动恢复
> **BECAUSE** Priority Context 是 OMC 中唯一被 `session-start.mjs` 自动注入的跨窗口状态通道
