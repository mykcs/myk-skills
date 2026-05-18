# Auto Dream Benchmark System

## 核心思想

每个 benchmark 有：
- **目标分数**（target）：优化方向
- **当前分数**（score）：每次做梦后更新
- **差距**（gap）：target - score
- **行动项**（actions）：缩小差距的具体步骤

---

## Benchmark 分类

### 1. Memory Health（记忆健康度）

| 指标 | target | 检查方法 |
|------|--------|---------|
| MEMORY.md 行数 | ≤200 | `wc -l MEMORY.md` |
| 过时条目（>30天） | 0 | 检查 frontmatter date |
| 相对时间残留 | 0 | grep "昨天\|上周\|最近\|以前" |
| 矛盾条目 | 0 | 检查 CONFLICT 注释 |

**当前分数计算**：`100 - (过时×10 + 矛盾×20 + 行数超标×0.5)`

---

### 2. Deduplication（去重效率）

| 指标 | target | 检查方法 |
|------|--------|---------|
| 重复记忆文件 | 0 | 相似度 >80% 检测 |
| 重复 CASE 文件 | 0 | 相似标题/根因检测 |
| 重复规则 | 0 | 规则内容重复检测 |
| 孤立索引项 | 0 | 索引存在但文件不存在 |

**当前分数计算**：`100 - (重复记忆×15 + 重复CASE×10 + 孤立×5)`

---

### 3. Rule Quality（规则质量）

| 指标 | target | 检查方法 |
|------|--------|---------|
| Binary Assertions 完整率 | 100% | 检查每个规则是否有 [x] |
| 规则冲突 | 0 | 检测同名触发条件不同行为 |
| 规则覆盖空白 | 最小 | 对照 CASE 提取缺失规则 |
| 规则腐坏（orphaned） | 0 | rules/ 下无引用的规则 |

**当前分数计算**：`100 - (无BA×10 + 冲突×30 + 空白×15 + 腐坏×20)`

---

### 4. Case Quality（案例质量）

| 指标 | target | 检查方法 |
|------|--------|---------|
| resolved 状态标记率 | 100% | 检查 status 字段 |
| 案例完整性（5步格式） | 100% | 检查 5 步是否齐全 |
| 根因可提取规则 | 已提取 | 检查是否已融入 rules/ |
| 重复案例 | 0 | 同类问题不重复归档 |

**当前分数计算**：`100 - (未标记×10 + 不完整×20 + 未提取×15 + 重复×10)`

---

### 5. Completeness（完整性）

| 指标 | target | 检查方法 |
|------|--------|---------|
| 核心记忆文件齐全 | 100% | user-role, global-context 存在 |
| Feedback 覆盖 | 覆盖高频摩擦 | 对照 Insights friction 数据 |
| Reference 可用性 | 无死链 | 检查外部链接有效性 |

---

## Benchmark 报告格式

每次做梦后输出：

```
[Auto Dream] Benchmark 报告
===========================
时间: {current_time}

1. Memory Health: {score}/100 (目标: {target})
   - 过时条目: {N} 个
   - 矛盾条目: {N} 个
   - MEMORY.md 行数: {L} 行

2. Deduplication: {score}/100 (目标: {target})
   - 重复记忆: {N} 个
   - 重复 CASE: {N} 个
   - 孤立索引: {N} 个

3. Rule Quality: {score}/100 (目标: {target})
   - 缺失 Binary Assertions: {N} 个规则
   - 规则冲突: {N} 对
   - 未融入的案例: {N} 个

4. Case Quality: {score}/100 (目标: {target})
   - 未标记 resolved: {N} 个
   - 不完整: {N} 个
   - 可提取规则: {N} 个

综合分数: {total}/500
目标: 450+
差距: {-diff}

Top 行动项:
1. {action 1}
2. {action 2}
3. {action 3}
```

---

## 优化目标设定

| 方向 | target | 说明 |
|------|--------|------|
| memory-health | 95+ | 记忆整洁、无过时、无矛盾 |
| deduplication | 100 | 零重复、零孤立 |
| rule-quality | 90+ | 规则完整、无冲突、可执行 |
| case-quality | 85+ | 案例规范、可提取 |
| completeness | 100 | 核心文件齐全 |

**总目标**：综合 450+/500 (90%)

---

## 持续优化机制

每次做梦后：
1. 计算各维度分数
2. 记录到 `.omc/state/auto-dream-benchmarks.json`
3. 对比上次分数，输出变化趋势
4. 生成 top 3 行动项

**分数下降时**（负向变化）：
- 标记为 `[REGRESSION]` 并报告
- 追溯原因（新增文件？规则冲突？）

**分数长期停滞**时：
- 输出 `[STALLED]` 警告
- 建议更激进的优化手段
