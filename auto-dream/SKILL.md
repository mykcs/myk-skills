---
name: auto-dream
description: |
  Claude Code 跨会话记忆整合引擎。模仿官方 Auto Dream 功能，定期整理 memory/ 目录，去除过时内容，合并重复条目，将相对时间转为绝对时间。
  触发场景：用户说"整理记忆"、"运行 dream"、"auto dream"、"整理我的记忆"、"记忆整合"时使用。
user-invocable: true
disable-model-invocation: true
license: MIT
metadata:
  version: "1.1.0"
  author: mykcs
  category: memory-maintenance
  triggers:
    - 整理记忆
    - 运行 dream
    - auto dream
    - 记忆整合
    - 整理我的记忆
  tags:
    - memory
    - consolidation
    - auto-dream
    - maintenance
---

# Auto Dream — 记忆整合 Skill

## 功能

模仿 Claude Code 官方的 Auto Dream 功能，对 `~/.claude/memory/` 目录进行跨会话记忆整合：

1. **删除过时内容** — 移除已过期、无效的记忆条目
2. **合并重复条目** — 合并相同主题的重复记忆
3. **时间规范化** — 将相对时间（如"昨天"、"上周"）转为绝对时间戳
4. **解决矛盾** — 标记或解决同一主题的冲突信息
5. **保持索引精简** — 确保 MEMORY.md 索引文件不超过 200 行

## 触发条件

- **手动触发**：用户说"整理记忆"、"运行 dream"、"auto dream"时
- **自动触发（参考官方）**：距上次整合 ≥24小时 且 新会话数 ≥5

## 整合流程

### Phase 1: 扫描

扫描 `~/.claude/memory/` 下所有 .md 文件：
- `MEMORY.md` — 主索引
- `*.md` — 各分类记忆文件
- `knowledge/cases/wiki/*.md` — Case 归档

同时记录：
- 每个文件的最后修改时间
- 文件总行数
- 当前 MEMORY.md 行数

### Phase 2: 分析

对每个记忆文件按以下维度打分：

#### 过时判断（Staleness Criteria）

| 等级 | 条件 | 行动 |
|------|------|------|
| **高危** | 超过 90 天无更新 且 内容与当前项目/偏好无关 | 建议删除或归档 |
| **观察** | 30-90 天无更新 | 保留但标注"待验证" |
| **活跃** | 30 天内有更新 | 保留 |
| **永久** | 包含用户偏好、身份、项目路径等持久信息 | 永不删除 |

**过时判断命令**：
```bash
find ~/.claude/memory -name "*.md" -not -name "MEMORY.md" -mtime +90 -not -path "*/cases/*"
```

#### 重复检测（Duplicate Detection）

**检测方法**（按优先级）：
1. **标题相似度**：文件名或 `name:` 字段重复 → 保留最新
2. **内容哈希**：MD5 哈希相同 → 硬重复，删除其一
3. **语义相似度**：内容重复率 >80%（用 AI 判断）→ 合并

**合并策略**：保留时间戳最新、描述最完整的版本，其余移至 `archive/`。

#### 时间规范化（Time Normalization Patterns）

检测并替换以下相对时间表达：

| 相对表达 | 替换为 |
|---------|--------|
| "昨天"、"昨日" | 实际日期 |
| "上周"、"上上周" | 实际周数 |
| "最近"、"近来"、"近期" | 具体日期或"YYYY-MM" |
| "目前"、"现在" | 整合时的实际日期 |
| "几天前"、"数日前" | 具体天数 |

**替换原则**：将表达替换为"YYYY-MM-DD 或 YYYY-MM-DD 周几"格式。

#### 矛盾检测

对同一主题的多个记忆条目，检查：
- **事实矛盾**：同一事件描述冲突 → 保留证据最充分的一个
- **时间矛盾**：同一事件时间线矛盾 → 以最早来源为准
- **优先级矛盾**：同一主题但结论相反 → 保留最新，标注历史版本

### Phase 3: 整合

执行以下操作：

```bash
# 1. 创建归档目录
mkdir -p ~/.claude/knowledge/cases/archive/auto-dream-$(date +%Y%m%d)

# 2. 移动过时文件（如有）
# mv <过时文件> ~/.claude/knowledge/cases/archive/auto-dream-YYYYMMDD/

# 3. 更新 MEMORY.md（如有删除）
# 删除对应的索引行

# 4. 验证 MEMORY.md 不超过 200 行
wc -l ~/.claude/memory/MEMORY.md
```

### Phase 4: 验证

- [ ] `wc -l ~/.claude/memory/MEMORY.md` ≤ 200 行
- [ ] 所有引用路径仍然有效（`grep -r "\.md" ~/.claude/memory/MEMORY.md`）
- [ ] 无孤立文件（在 MEMORY.md 索引中但文件不存在）
- [ ] 相对时间已全部替换为绝对时间

## 输出格式

```markdown
[Auto Dream] 记忆整合报告
========================
扫描时间: YYYY-MM-DD HH:mm
扫描文件: N 个

过时分析:
  高危（建议删除）: X 个
  观察（待验证）: Y 个
  活跃: Z 个

重复分析:
  标题重复: X 对
  内容重复: Y 对
  已合并: Z 个

时间规范化:
  替换条目: N 个

MEMORY.md 行数: W 行（目标 ≤200）

待处理（需人工判断）:
  - 矛盾条目: [列表]
  - 高危文件: [列表]
```

## 反模式（Anti-Patterns）

以下情况**禁止**执行整合：

- ❌ **活跃项目期间**：`memory/` 中有正在进行的项目记忆，此时整合可能丢失上下文
- ❌ **会话压缩前**：先压缩再整合，顺序不能颠倒（压缩产生新上下文）
- ❌ **距上次 <24小时**：频繁整合浪费资源，且可能丢失累积的上下文价值
- ❌ **未检查高危文件就直接删除**：删除前必须列出并确认

## 联动技能

- **整合前**：运行 `/rich-audit` 检查 memory/ 完整性
- **整合后**：如有新的教训/案例，运行 `/learned` 提取知识
- **归档**：过时的项目记忆 → `knowledge/cases/archive/`

## 参考文档

- `references/consolidation-prompt.md` — 整合提示词模板
- `references/memory-structure.md` — memory/ 目录结构说明
