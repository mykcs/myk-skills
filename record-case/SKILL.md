---
name: record-case
description: |
  统一知识归档 skill：先输出位置，再决策类型，最后按模板深度归档。
  支持 Case(深度)/Pattern(轻量)/Decision(决策) 三种类型，覆盖所有知识沉淀场景。
  触发场景: 用户说"记录这个/归档/留档/case 一下/学到了/总结经验"、修复完成后的知识沉淀、调试 ≥2 轮后的根因落地。
user-invocable: true
license: MIT
metadata:
  version: "3.0.0"
  author: mykcs
  category: knowledge
  triggers:
    - 记录这个
    - 归档
    - 留档
    - case 一下
    - 存为案例
    - record case
    - archive this
    - 写成 case
    - 学到了
    - 记录经验
    - 总结教训
    - 提取知识
    - learned
    - 经验总结
    - 这个要记住
    - 下次这样做
  tags:
    - knowledge
    - case
    - archive
    - postmortem
    - deep-archive
    - pattern
    - decision
---

# Record Case — 统一知识归档 v3.0

## 何时触发

| 场景 | 信号 | 路由类型 |
|------|------|---------|
| Bug 修复完成 | 用户确认"修好了"+ 调试 ≥2 轮 | **Case** |
| 工作流踩坑 | 同类问题第二次出现 | **Case** |
| 配置/架构决策 | 多个方案中选定一个 | **Decision** |
| 工具行为发现 | CLI/MCP/SDK 实际行为与文档不符 | **Case** or **Pattern** |
| 工作流技巧 | "原来应该先 X 再 Y" | **Pattern** |
| 显式请求 | "记录/归档/case 一下/学到了" | 按需路由 |

## 执行流程

### Step 1: 识别知识价值

判断是否值得提取：
- 这个问题将来还会遇到吗？
- 这个教训可以泛化到其他场景吗？
- 这个发现有什么证据支撑？

如果 3 个问题中有 2 个及以上"否" → **不提取**。

### Step 2: 提取核心要素

1. **问题**：具体是什么情况？（不是"配置文件出错"而是"settings.json 的 hooks 字段引用了不存在的脚本路径"）
2. **根因**：为什么会出现这个问题？
3. **解决**：具体做了什么来解决？（步骤）
4. **教训**：以后怎么避免？（IF...THEN... 规则）
5. **证据**：怎么验证这个教训是对的？（命令、输出、截图）

### Step 3: 先输出位置，再决策类型

**必须先说**：
```
📁 存储位置: ~/.claude/knowledge/cases/wiki/
📦 知识类型: Case（工程案例）
```

**路由决策表**（按优先级判断）：

| 位置 | 类型 | 判断标准 | 模板 |
|------|------|---------|------|
| `cases/wiki/` | **Case** | 有明确根因、解决步骤、调试≥2轮、失败路径≥1条 | [Case 深度模板](#case-深度模板) |
| `memory/patterns/` | **Pattern** | 行为偏好、工具使用习惯、工作流发现 | [Pattern 轻量模板](#pattern-轻量模板) |
| `memory/decisions.md` | **Decision** | 多方案中选择、架构决策 | [Decision 决策模板](#decision-决策模板) |

**优先级**：Case > Decision > Pattern
- 只要满足 Case 条件（bug 修复 / 踩坑 / 调试≥2轮 / 有明确根因）→ **必须**路由到 `cases/wiki/`，禁止降级为 Pattern 或 Decision
- 多方案决策 + 有踩坑过程 → 按 Case 处理
- 如果进入 `cases/wiki/` → **禁止**使用简化模板，必须执行深度归档

**关键规则**：
- 同时满足多个类型条件时，按优先级取最高

---

## Agent 执行步骤（被调用后必须按序执行）

1. **内容提取**：从用户消息 / 会话上下文提取要归档的事实
   - 若用户仅说"记录这个"但无具体内容 → 运行[信息不足追问模板]
   - 禁止在信息不足时凭空编造内容填充模板
2. **价值判断**：运行 Step 1 的 3 个问题，≥2 个"否"则停止并说明原因
3. **播报决策**：按"先输出位置，再决策类型"格式向用户播报存储位置和知识类型
4. **内容生成**：按对应模板（Case/Pattern/Decision）完整填充，禁止简化
5. **自检**：运行对应类型的检查清单，任一维度缺失则回滚补全
6. **重复检查**：`grep ~/.claude/knowledge/cases/wiki/ -l "<核心症状关键词>"` 确认非重复归档
7. **写入 + 验证**：
   - 写入文件 → `ls -la` 确认物理存在
   - `cat` 抽查关键段落（症状 / P0 / 教训）
8. **更新索引**：
   - Case → 追加到 `~/.claude/memory/MEMORY.md` 的 `## Cases`
   - 同时写入 mem0：`metadata.type="case"`，`metadata.tags=[tag1, tag2]`，`metadata.source="CASE-<DESCRIPTOR>-<YYYYMMDD>"`
   - 若 MEMORY.md 写入被 hook 拦截 → 改用 `mcp__plugin_mem0_mem0__add_memory`
9. **升级评估**：若 case 涉及可复现的失败模式 → 评估是否新增 rule 到 `~/.claude/rules/`；若 case 重复出现 ≥2 次 → 必须升级为 hook/lint/test

---

## 信息不足时的追问模板

若用户未提供完整信息，输出：

```
需要补充以下要素才能深度归档：

- 问题：具体遇到了什么？（错误信息 / exit code / 可观察现象）
- 场景：什么操作触发的？在什么环境 / 版本下？
- 解决：你做了什么让它好了？（具体步骤 / 命令 / 配置）
- 证据：有命令输出、截图或 commit SHA 吗？
- 失败尝试：中间试过哪些方案？为什么失败？
```

禁止在信息不足时猜测填充模板。

---

## Case 深度模板

```markdown
---
date: YYYY-MM-DD
status: resolved|investigating|deferred
tags: [tag1, tag2, tag3]
related: [CASE-OTHER-YYYYMMDD]  # 无相关 case 时删除本行或写 []
---

# CASE-<DESCRIPTOR>-<YYYYMMDD>: 一句话标题

## 症状
- 用户视角的可观察现象,具体到错误信息/截图描述/exit code
- 触发条件(什么操作 → 什么结果)
- 影响范围

## 根因
- 第一性原因(不是表层"代码错了",而是"为什么会写错")
- 系统层面的不变量被违反时
- 配置/环境/版本/上下文中真正的失配点

## 失败路径还原(禁止省略)

### 尝试 1：XXX
**做了什么**：...
**为什么失败**：...
**误导性证据**：...(如 curl 假阳性、缓存干扰、"build 成功"但功能缺失)

### 尝试 2：XXX
...

### 最终生效：XXX
...

## 非平凡技术决策

### 为什么是方案 A 而不是 B
- 方案 A：... → 优点 / 缺点
- 方案 B：... → 优点 / 缺点
- **选择 A 的核心原因**：...

### 隐性约束
- gitignore / CI 盲区 / submodule 行为差异 / 框架默认行为等
- "如果去掉 X 约束，结论是否会变？"

## 解决(按 P0/P1/P2 优先级排序)

### P0：阻断性修复(必须最先做)
- 不先做这一步，后续全部无效
- 代码 diff / 命令 / 配置

### P1：支撑性修复(依赖 P0)
- 在 P0 基础上才能生效的改动
- 代码 diff / 命令 / 配置

### P2：验证/加固(最后做)
- 测试用例 / audit 脚本 / lint 规则
- 防止回归的工程硬约束

## 验证

### 修复前
```bash
# 命令 + 实际输出
```

### 修复后
```bash
# 命令 + 实际输出
```

## 教训

### 可执行的预防规则(必须是触发式)
**IF** ... **THEN** ... **ELSE** ...
- ❌ 禁止："下次注意"
- ✅ 必须："如果 X 则必须 Y"

### 思维转变
- 从"X 思路"切换到"Y 思路"
- 什么旧假设被打破了

### 建议的工程硬约束
- 新增 hook / lint 规则 / 测试用例 / audit 阈值的具体内容
- 如果 case 重复出现 ≥2 次 → 必须升级为硬约束

## 引用
- 相关 commit: `git log` SHA
- 相关 PR/Issue: URL
- 相关文件: `path:line`
```

### Case 4 维度强制检查清单

写完后必须逐项自检，缺少任何一项 = **回答无效，必须回滚补全**。

| 维度 | 检查点 | 不合格示例 | 合格示例 |
|------|--------|-----------|---------|
| **失败路径还原** | 是否记录了≥1次失败尝试？是否有"误导性证据"？ | "我试了 A 不行，然后 B 行了" | "尝试 A 时 build 成功但 dist 少了图片 → 误导性证据是体积骤降" |
| **非平凡决策** | 是否说明了"为什么 A 而不是 B"？是否有隐性约束？ | "因为 symlink 简单" | "symlink 会被 Astro 递归展开 → 隐性约束是 build 工具行为" |
| **P0/P1/P2** | 修改点是否按阻断/支撑/验证排序？ | "先改 CI，再改脚本" | "P0: setup-links.sh 改 selective copy → P1: audit-build.sh 体积门控 → P2: CI 去冗余" |
| **触发式规则** | 教训是否是 `IF...THEN...` 格式？ | "下次注意 symlink" | "IF vendor/ 同时含源码和静态资源 THEN 禁止 symlink 到 public/" |

---

## Pattern 轻量模板

**存储**：`~/.claude/memory/patterns/{domain}.md`
**适用**：行为偏好、工具使用习惯、工作流发现

```markdown
### {模式名称} | {YYYY-MM-DD}

**适用**：{在什么情况下使用}
**操作**：{具体步骤}
**边界**：{什么情况下有效，什么情况下无效}
```

**质量检查**：
- [ ] 有具体步骤（不是"要小心"而是"先用 X 再 Y，否则会 Z"）
- [ ] 有边界条件（"在 Z 情况下有效，其他情况未必"）

---

## Decision 决策模板

**存储**：`~/.claude/memory/decisions.md`（追加模式）
**适用**：在多个方案中做出选择后的决策记录

```markdown
### {决策标题} | {YYYY-MM-DD}

**问题**：{要解决的核心问题}
**选项**：
  - A：{方案描述} → {优缺点}
  - B：{方案描述} → {优缺点}
**选择**：{选择了哪个}
**原因**：{选择的核心原因}
**后续**：{如果选错了怎么处理}
```

### Decision 质量检查清单

写完后逐项自检，任一维度缺失则回滚补全：

| 维度 | 检查点 | 不合格示例 | 合格示例 |
|------|--------|-----------|---------|
| **选项完整性** | 是否列出≥2个选项？每个选项是否有优缺点？ | "方案A简单，方案B复杂" | "方案A： symlink → 优点零拷贝/缺点被Astro递归展开; 方案B：selective copy → 优点可控/缺点多一步脚本" |
| **核心原因** | "原因"是否说明"为什么A而不是B"？是否涉及隐性约束？ | "因为A简单" | "symlink会被Astro递归展开是隐性约束，所以必须选selective copy" |
| **纠错机制** | "后续"是否写了"选错怎么纠"？ | "后续再看" | "IF selective copy导致public/体积膨胀 THEN 切回symlink+配置exclude" |
| **可逆性** | 决策是否可逆？不可逆决策是否标注风险？ | "直接迁移" | "不可逆：数据库schema变更；回退策略：先建shadow表验证" |

---

## 文件命名

### Case
```
~/.claude/knowledge/cases/wiki/CASE-<DESCRIPTOR>-<YYYYMMDD>.md
```
- `<DESCRIPTOR>`: 全大写,连字符分隔,15 字以内,语义化
- `<YYYYMMDD>`: 绝对日期,不要相对日期

### Pattern
```
~/.claude/memory/patterns/{domain}.md
```

---

## 禁止行为(反模式)

| ❌ 禁止 | ✅ 必须 |
|--------|---------|
| 只列 症状→根因→解决 三段式流水账 | 必须包含"失败路径还原"和"非平凡决策" |
| 不记录失败尝试(只写最终方案) | 记录每次尝试、失败原因、误导性证据 |
| 不说明隐性约束 | 说明 CI 盲区 / gitignore 影响 / 框架行为差异 |
| 修改点按时间排序 | 修改点按 P0→P1→P2 优先级排序 |
| "下次注意" / "应该没问题" | `IF...THEN...` 触发式规则 |
| "代码错了" | "在 X 文件 Y 行,因为 Z 假设错误,导致 W" |
| "重启就好了" | "重启绕开了 X 问题,根因是 Y,长期需修 Z" |
| "可能是缓存" | "实测清除 X 缓存后问题消失,根因是 Y 缓存键不匹配" |
| 空洞感悟 | 具体到可以搜索的问题描述 |
| 无证据的结论 | 具体现象 + 验证步骤 |
| 已归档案例的重复 | 先 grep 检查是否已有相同根因 |
| 纯情绪发泄 | 保留在 session 记录中，不进入知识库 |

---

## 写完后必做

1. **物理验证**：`ls -la` 确认文件存在
2. **重复检查**：`grep -r "<核心症状关键词>" ~/.claude/knowledge/cases/wiki/ --include="*.md"` 确认非重复归档；若发现同类根因 → 更新已有 case 而非新建
3. **更新索引**：
   - Case → 追加到 `~/.claude/memory/MEMORY.md` 的 `## Cases`
   - 同时写入 mem0：`metadata.type="case"`，`metadata.tags=[tag1, tag2]`，`metadata.source="CASE-<DESCRIPTOR>-<YYYYMMDD>"`
   - 若 MEMORY.md 写入被 hook 拦截 → 改用 `mcp__plugin_mem0_mem0__add_memory`，内容结构化存储（标题 + frontmatter + 教训摘要）
4. **Rule 升级评估**：若 case 涉及可复现的失败模式 → 评估是否需要新增 rule 到 `~/.claude/rules/`
5. **硬约束评估**：若 case 重复出现 ≥2 次 → 必须升级为 hook/lint/test

---

## v3.0 变更日志

- **合并**：吸收 `learned` skill 的路由逻辑 + Pattern/Decision 模板
- **统一入口**：一个 skill 覆盖所有知识归档场景（Case + Pattern + Decision）
- **保留**：`record-case` v2.0 的 4 维度深度检查清单
- **新增**："先输出位置，再决策类型"强制流程
- **新增**：Agent 执行步骤（9 步可执行链）
- **新增**：Decision 质量检查清单（4 维度）
- **新增**：信息不足时的追问模板
- **新增**：路由优先级（Case > Decision > Pattern）
- **删除**：`learned` skill（功能已合并至此）

### v2.0 → v3.0 迁移说明

| v2.0 用法 | v3.0 对应 |
|-----------|-----------|
| 调用 `record-case` 归档 bug/踩坑 | 不变，自动路由到 Case |
| 调用 `learned` 归档工作流技巧 | 改用 `record-case`，自动路由到 Pattern |
| 手动写 `memory/decisions.md` | 改用 `record-case`，按 Decision 模板生成 |
