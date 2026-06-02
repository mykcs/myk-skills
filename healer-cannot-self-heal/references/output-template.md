# 输出模板 — Session Autopsy Report

每个 `医者不可自医` invocation 产出的报告必须按此结构。

## 文件位置

```
~/.claude/state/healer-reports/{session-id}-{YYYYMMDD-HHMMSS}.md
```

## 模板

```markdown
# Session Autopsy Report — {session-id}

**Generated**: {YYYY-MM-DD HH:MM:SS}
**Trigger**: {触发词原文}
**Transcript path**: {transcript 绝对路径}
**Mode**: 人工召唤 (非自动)

---

## 1. 触发时上下文

| 维度 | 值 |
|------|-----|
| Token 使用率 | {百分比} (?) |
| 对话轮数 | {整数} |
| 工具调用总次数 | {整数} |
| 错误次数 | {整数} (?) |
| 重复命令次数 | {整数} |

> claudecode 观察到 token 接近耗尽。证据见 L{L1}-L{L2}。
> (?) 表示 claudecode 对此数据点不确定。

---

## 2. 症状清单

按时间倒序排列（最近的在前）。每条症状附：
- **时间窗口**（L 编号）
- **证据块**（默认完整工具调用，关键反复处升上下文窗口）
- **置信标注**（只在不确定时标 `?`）
- **可能根因**（仅列出，不下判断）

### 症状 S1: {症状名}

**时间窗**: L{L_start}-L{L_end}
**类型**: {工具调用模式 / 错误升级 / 漂移 / 其他}
**置信**: {high / medium / low / ?}

**证据**:
```json
{完整工具调用原文，input + output + error}
```

或（关键反复处）：

```text
{上下文窗口原文，前后各 N 行}
```

**可能根因**（多选，claudecode 不下判断）：
- 假设 A：...
- 假设 B：...
- 假设 C：...

---

## 3. claudecode 行为模式（按维度切片）

### 3.1 工具调用分布
- Bash: {n} 次
- Grep: {n} 次
- Read: {n} 次
- Edit: {n} 次
- ... 其他

### 3.2 错误类型分布
- exit 1: {n} 次
- Permission denied: {n} 次
- TypeError: {n} 次
- ... 其他

### 3.3 同一命令重复次数（top 5）
| 命令 | 重复次数 | 时间窗 |
|------|---------|--------|
| {cmd} | {n} | L{L1}-L{L2} |

---

## 4. 模式识别（claudecode 观察，不下判断）

claudecode 观察到以下模式，但**不**认为自己的判断可靠：

- **模式 1**: {描述} (?) — 证据 L{L1}-L{L2}
- **模式 2**: {描述} — 证据 L{L3}-L{L4}
- **模式 3**: {描述} (?) — 证据 L{L5}-L{L6}

> 上述模式基于 transcript 切片。claudecode 承认：自己的模式识别能力可能正是失效原因之一。

---

## 5. next-step hints（LOW-CONFIDENCE 区）

> ⚠️ **claudecode 给出的"处方"本质上不可信**。以下每条都标 LOW-CONF，**用户（医者）应独立判断**。

- 考虑调 `/record-case` 把本次症状归档为 case (conf: **LOW**)
- 考虑调 `/rich-audit` 对 ~/.claude 配置做更深层审计 (conf: **LOW**)
- 考虑调 `/session-chapter` 保存当前状态后开新窗口 (conf: **LOW**)
- 考虑人工 review 本报告后，决定是否需要修改 `rules/` 或 `scripts/` (conf: **LOW**)

---

## 6. 元信息

| 维度 | 值 |
|------|-----|
| 报告生成者 | claudecode (via 医者不可自医 skill) |
| 报告可信度 | **LOW**（医者不可自医原则） |
| 不变量已遵守 | ✅ 不写 case / 不改规则 / 不调 audit / 不调 evolution-trigger / 不调 record-case |
| 落盘位置 | ~/.claude/state/healer-reports/{filename}.md |
```

## 字段说明

| 字段 | 必填 | 含义 |
|------|------|------|
| `症状 S#` | ✅ | 每个观察到的症状一条 |
| `时间窗` | ✅ | L 编号区间，引用 transcript |
| `证据` | ✅ | 原始材料，**不能改写** |
| `置信` | ✅ | high/medium/low/? |
| `可能根因` | 可选 | 多假设列出，不下判断 |
| `模式` | 可选 | 跨症状的模式，claudecode 承认不可靠 |
| `next-step hints` | ✅ | LOW-CONF 区，**用户判断** |

## 不变量

- ❌ 不写"我错了" / "我搞砸了"
- ❌ 不输出没有证据的叙述
- ❌ 不调 audit/run-audit.py
- ❌ 不调 record-case / rich-audit / evolution-trigger（只建议）
- ❌ 不把处方当事实
- ✅ 报告主体是 transcript 原始材料
- ✅ claudecode 作第三方主语
- ✅ 怀疑标注只在不确定时出现
- ✅ 报告必须包含 transcript 原始路径

## 与其他模板的区别

| 模板 | 用途 | 关键差异 |
|------|------|---------|
| `record-case` Case 模板 | 知识归档 | 写 case 文件，落盘 |
| `rich-audit` Layer 1 报告 | 项目审计 | 自动修复 |
| `nightly-meta-cognition` 报告 | 周期体检 | dry-run 默认 |
| **本模板** | **session 急诊** | **不落地，只描述** |
