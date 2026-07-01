# Report Index 模板 (Stage 4)

> **来源**: weiying20260624 week2 REPORT-AGENT (commit cb76b63, md 31K + html 41K, 39 paper, 7 cluster, 15 milestone)
> **2 形态输出**: md (人类读) + html (周报 publish)
> **4 粒度对位**: 子方向 / 时间窗 / 方法机制 / 跟组里连接

## 复制下面整段

```markdown
# 全谱系索引 — <TASK_NAME> (<DATE>)

> **生成时间**: <YYYY-MM-DD HH:MM>
> **输入**: <N_NOTE> 份 paper note (从 STAGE 3 收)
> **覆盖**: <N_SUB> 个子方向 × <T_WINDOW> 时间窗
> **目标**: 给 weekly / 给老师看, 用 4 粒度对位

---

## §1 子方向 × paper 对位表

| 子方向 | paper 数 | 核心 paper (引用数降序) | 关键 insight (1 句) |
|--------|---------|----------------------|---------------------|
| C1 | <N> | <paper 1, 2, 3> | <...> |
| C2 | <N> | ... | ... |
| ... | ... | ... | ... |
| C<N_SUB> | <N> | ... | ... |

## §2 时间轴 × 阶段对位表 (5 代际法)

| 阶段 | 时间窗 | 代表 paper | 关键事件 |
|------|--------|------------|---------|
| 1 奠基期 | <YYYY-MM-YYYY-MM> | <...> | <...> |
| 2 演进期 | ... | ... | ... |
| 3 爆发期 | ... | ... | ... |

## §3 方法机制 × paper 对位表 (group 4 粒度)

| 机制 | paper 数 | 代表 |
|------|---------|------|
| memory | <N> | <...> |
| prompt | <N> | <...> |
| skills | <N> | <...> |
| modules | <N> | <...> |
| reasoning patterns | <N> | <...> |

## §4 跟组里连接 × paper 对位表

| 组里方向 | 关联 paper | 关联深度 |
|---------|-----------|---------|
| <compositionality> | <paper 1, 2> | <深 / 中 / 浅> |
| ... | ... | ... |

---

## §5 主题聚类 (<N_CLUSTER> 个 cluster, 8 个候选 → 实际选)

| Cluster | 候选数 | 跟组里连接 | 描述 |
|---------|--------|-----------|------|
| C1: AI Scientist 端到端 | <N> | <concepts / reasoning> | <1 句> |
| C2: 长时 multi-agent | <N> | <skills / modules> | <1 句> |
| ... | ... | ... | ... |

---

## §6 里程碑事件 (<N_MILESTONE> 个, 按时间升序)

| # | 时间 | 事件 | paper |
|---|------|------|-------|
| 1 | <YYYY-MM> | <GPT-3 / ReAct / AI Scientist v1> | <...> |
| ... | ... | ... | ... |

---

## §7 引用数降序 top 10

| # | Paper | 引用数 | 子方向 | venue |
|---|-------|-------|--------|-------|
| 1 | <paper> | <N> | <C> | <venue> |
| ... | ... | ... | ... | ... |

---

## §8 慎引清单 (≤ 3 分, <N_CAUTION> 篇)

| Paper | 综合分 | 风险 |
|-------|--------|------|
| <...> | <score> | <reason> |

---

## §9 用户真读 pending 清单 (<N_PENDING> 篇, weekly 引用前必读)

| Paper | 风险点 |
|-------|--------|
| <...> | <reason> |
```

## HTML 版本生成

```bash
# Stage 4 必跑: 跟 md 同步产出 html (周报发布用)
pandoc -s report-<date>.md -o report-<date>.html --css=<style>
# 或用 marp / reveal.js (per 项目 SOP)
```

## 4 粒度对位硬规则

| 维度 | 必填项 | 作用 |
|---|---|---|
| 子方向 | §1 7 子方向 × paper 对位 | 跟主题聚类对位 |
| 时间轴 | §2 5 代际法 | 奠基/演进/爆发分段 |
| 方法机制 | §3 group 4 粒度 | 跟 weekly §3 方法论对位 |
| 组里连接 | §4 compositionality 等 | 跟 weekly 引言对位 |

## 反模式 (永久失效)

- ❌ 只产 md 不产 html (周报 publish 卡住)
- ❌ 少 1 个粒度对位 (4 件必全)
- ❌ 不给慎引清单 (weekly 引用风险)
- ❌ 不给真读 pending (user 误信幻觉)

## 🔗 相关

- `~/.agents/skills/loop-engineering/SKILL.md` §Stage 4 全谱索引
- weiying20260624/04-artifacts/agents-output/full-canvas-filtered-20260630.md (参考实跑)
- `process.md §C.3.3` memory-bench 协议 (cross-validate)
