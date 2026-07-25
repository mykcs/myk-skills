# Filtered Papers 模板 (Stage 2)

> **来源**: weiying20260624 week2 FILTER-AGENT 输出 (commit 5dd4cca)
> **过滤标准**: A 高引用 + B Survey 推荐 + C 团队强, 三方交叉
> **硬规则**: 7 个 jsonl 中识别重复 paper, 按"评分高 / 证据足"原则选 1 份保留

## 复制下面整段, 改占位符

```markdown
# FILTER-AGENT 输出 — <TASK_NAME> 三方交叉验证表 (<date>)

> **任务**: 过滤 SEARCH-AGENT <N_RAW> 条候选, A + B + C 三方交叉
> **过滤标准**:
> - 奠基 Paper: 引用数 ≥ <CITE_MIN> OR 出现在 ≥ 2 个工具返回结果中 (cross-validate) AND 团队强
> - 新工作: 发表日期 ≥ <DATE_MIN> AND 跟种子 Query 主题相关
> - 团队强: 作者来自 <LAB_LIST>

---

## Part 1: 通过候选 (<N_PASS> 篇)

### 1.1 奠基 Paper (<N_FOUNDATION> 篇)

| Paper | A-高引用 | B-Survey 推荐 | C-团队强 | 最终分级 | 备注 |
|-------|----------|---------------|----------|----------|------|
| <Paper 1> (<arXiv ID>) | <✅/❌ + 引用数> | <✅/❌ + 推荐源> | <✅/❌ + 团队> | <奠基起手锚 / 顶刊锚 / 技术演进锚> | <1 句说明> |
| ... | ... | ... | ... | ... | ... |

### 1.2 新工作 (<N_NEW> 篇)

| Paper | A-高引用 | B-Survey | C-团队强 | 最终分级 | 备注 |
|-------|----------|----------|----------|----------|------|
| ... | ... | ... | ... | ... | ... |

### 1.3 备选候选 (评分边缘, <N_BACKUP> 篇备选)

| Paper | A | B | C | 评分 | 备注 |
|-------|---|---|---|------|------|
| ... | ... | ... | ... | ... | ... |

---

## Part 2: 冲突裁决表 (分歧 paper 填)

| 维度 | 早期正面 (<source 1>) | 负面 (<source 2>) | **裁决** |
|------|---------------------|------------------|---------|
| 评分源 | <...> | <...> | <高+证据足侧> |
| 证据 | <...> | <...> | <...> |
| 顶刊背书 | <...> | <...> | <...> |
| **结论** | <...> | <...> | **双向收录 / 评分高侧引** |

---

## Part 3: Dedup 跨子方向重复处理 (可选)

| 重复 paper | 出现位置 | 保留版本 | 理由 |
|-----------|---------|---------|------|
| <paper> | <C1 #X, C3 #Y> | <C3> | <C3 evidence 完整> |

---

## Part 4: 通过清单 (供 STAGE 3 输入)

| # | Paper | 子方向 | arXiv | 引用数 | 评分 |
|---|-------|--------|-------|-------|------|
| 1 | <...> | <...> | <...> | <...> | <...> |
| ... | ... | ... | ... | ... | ... |
```

## 字段说明

| 字段 | 必填 | 说明 |
|---|---|---|
| `<TASK_NAME>` | ✅ | 任务名, 跟 loop-protocol 一致 |
| `<date>` | ✅ | 跑 FILTER 的日期 |
| `<N_RAW>` | ✅ | 原始候选数 (从 7 jsonl 汇总) |
| `<CITE_MIN>` | ✅ | 引用数阈值, week2 用 50 |
| `<DATE_MIN>` | ✅ | 新工作时间窗, week2 用 2025-06-01 |
| `<LAB_LIST>` | ✅ | 强团队白名单, week2 用 Sakana/Stanford/MIT/... |
| `<N_FOUNDATION>` | ✅ | 奠基 paper 数, 3-5 |
| `<N_NEW>` | ✅ | 新工作数, 5-7 |
| `<N_BACKUP>` | ✅ | 备选数, 0-2 |

## 🔗 相关

- `~/.agents/skills/loop-engineering/SKILL.md` §4 反模式 #2 (单源 web search)
- weiying20260624/04-artifacts/agents-output/filtered-papers-20260630.md (week2 实跑版, 39 篇)
- [`~/.claude/rules/protocols/N-tool-search.md`](~/.claude/rules/protocols/N-tool-search.md) v1.1.3 (N-tool fan-out, N 当前 = 6 含 mmx; 旧名 `process.md §F Force-All-Search Protocol (5-tool fan-out)`, per ADR-0056)
