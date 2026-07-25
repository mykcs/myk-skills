## 🎯 v3.2.9 report-card 模板段 (2026-07-18 立, per ADR-0066)

> **触发**: user 2026-07-18 拍板 "把 §memory-bench 必跑段扩展为 report-card 模板 (跑分报告 11 行总表标准化)". 跟 §C.3.3 v2.6.56 强约束 + §H 5 字段自检 + ADR-0016 memory-bench 归属决策 协同.
>
> **协议位**: memory-bench 跑分报告 (per ADR-0065 + §C.3.3 v2.6.56) **必走 11 行总表 report-card 标准模板**, 字段顺序 + 单位 + 加权方法 100% 一致.

**11 行总表标准模板**:

| #   | 字段              | 格式                                     | 单位    |
| --- | ----------------- | ---------------------------------------- | ------- |
| 1   | run_id            | `memory-bench-{YYYY-MM-DD}-v{n}`         | string  |
| 2   | timestamp         | ISO 8601 + timezone                      | string  |
| 3   | host              | `mykcs/{local-path}`                     | string  |
| 4   | skill_version     | `v{X.Y.Z}`                               | semver  |
| 5   | model             | actual answer runtime, e.g. `MiniMax via mmx text chat` | string  |
| 6   | judge             | actual judge runtime, e.g. `mmx dual-order judge`                | string  |
| 7   | recall_total      | N/50 (sum)                               | 整数    |
| 8   | consistency_total | N/15 (sum)                               | 整数    |
| 9   | compliance_total  | N/12 (sum)                               | 整数    |
| 10  | weighted_score    | `raw=0.0-2.0; normalized=0-100`（同一行）         | float   |
| 11  | target_met        | `✅ ≥ 60 / ❌ < 60`                      | boolean |

**模板示例** (per §C.3.3 v2.6.56 实战):

```markdown
| #   | 字段              | 值                         |
| --- | ----------------- | -------------------------- |
| 1   | run_id            | memory-bench-2026-07-18-v1 |
| 2   | timestamp         | 2026-07-18T15:30:00+08:00  |
| 3   | host              | mykcs@/Users/myk/.claude   |
| 4   | skill_version     | v3.2.9                     |
| 5   | model             | MiniMax via mmx text chat  |
| 6   | judge             | MiniMax via mmx dual-order judge |
| 7   | recall_total      | 42/50                      |
| 8   | consistency_total | 13/15                      |
| 9   | compliance_total  | 11/12                      |
| 10  | weighted_score    | raw=1.20; normalized=60.0  |
| 11  | target_met        | ✅ ≥ 60                    |
```

**失败处理** (per §C.3.6.1 no-stuck 协同):

- 跑分报告缺 11 行总表任一字段 → 报告无效, 立即重跑
- 跑分报告字段顺序错乱 → 报告无效, 立即重排
- weighted_score 用百分制 (0-100) 而非 5 级 (0-2.0) → 报告无效, 立即改回
- target_met 字段不填 / 填 "YES" / 填 "是" → 报告无效, 必用 ✅/❌
- score < 60 target + 11 行总表完整 → 走 §v3.2.8 立即修协议

**横向对比协议** (per §C.3.3 v2.6.56 baseline compare):

- baseline v1 vs SOTA v8 vs ablation-5: 11 行总表字段顺序 100% 一致才能对比
- weighted_score 差异 ≥ 0.1 = 实质改善 (跨版本提交决策依据)
- target_met ❌ → 不接受新版本 (除非 user 显式 override)

**反模式 (永久失效, 5 条, per ADR-0066 §4)**:

1. ❌ 跑分报告缺 11 行总表任一字段 = 违反 v3.2.9 段
2. ❌ 跑分报告字段顺序错乱 (e.g. recall_total 在 consistency_total 前) = 违反 report-card 模板
3. ❌ weighted_score 用百分制 (0-100) 而非 5 级 (0-2.0) = 违反 §C.3.3 v2.6.56
4. ❌ target_met 字段不填 / 填 "YES" / 填 "是" = 违反 report-card 模板 (必用 ✅/❌)
5. ❌ 跑分报告跑通后不跟 baseline / SOTA 横向对比 = 违反 §C.3.3 v2.6.56 baseline compare

**联动**:

- 跟 ADR-0065 (memory-bench 必跑) 协同 — 本 ADR 立 report-card 模板 = 必跑段的下一步标准化
- 跟 §C.3.3 v2.6.56 (memory-bench 强约束) + §C.3.3 v2.6.46 (重版约束) 协同
- 跟 ADR-0016 (memory-bench into rich-audit, 归属决策) 协同
- 跟 §C.3.6.1 no-stuck 协议 协同
- 跟 §H Acceptance Protocol (5 字段自检 → 7 字段新增 row 7 format) 协同

**历史 record**:

- 2026-07-18 v3.2.9: 立 (per user 2026-07-18 拍板 "把 §memory-bench 必跑段扩展为 report-card 模板" + ADR-0066 整数 slot 0066)

---

## 🎯 v3.2.8 memory-bench 必跑段 (2026-07-18 立, per ADR-0065)

> **触发**: user 2026-07-18 原话 "把'memory-bench 50 题'作为 host-self-evolve 必跑". 跟 §C.3.3 v2.6.56 强约束 + §C.3.3 v2.6.46 重版约束 + §C.3.6.1 no-stuck + §H 5 字段自检 协同.
>
> **协议位**: host-self-evolve v3.2.8+ run **必跑 memory-bench 50 题** (per §C.3.3 v2.6.56), **不允许 PENDING 跳过**, 跑分结果 (weighted score) 必落 `~/.agents/skills/host-self-evolve/reports/memory-bench/{date}-v{n}.md`.

**跑分流程** (per §C.3.3, 7 步):

| Step | 行为                                                                                   | 输出             |
| ---- | -------------------------------------------------------------------------------------- | ---------------- |
| 1    | 读 `~/.agents/skills/host-self-evolve/references/memory-bench-50q-sample.json`         | 50 题题库        |
| 2    | 50 题逐题独立调用 mmx text chat（每题独立 prompt，防前后题污染）                                  | 50 session 报告  |
| 3    | mmx 双序 judge 逐题评分（0-1），4 metric 合成后缩放到 0-2                                   | 评分报告         |
| 4    | 15 consistency 跨源 grep + mmx/脚本语义判定                                             | consistency 报告 |
| 5    | 12 compliance 触发场景, 跑对应 hook/script                                             | compliance 报告  |
| 6    | 4 metric 加权求和 → total score                                                        | total score      |
| 7    | 写 11 行总表到 `~/.agents/skills/host-self-evolve/reports/memory-bench/{date}-v{n}.md` | 报告文件         |

**失败处理** (per §C.3.6.1 no-stuck 协同):

- 跑分中途 token 限制 / mmx API 失败 → 暂停 + 报告 user + AskUserQuestion (走 4 类必问白名单)
- 跑分发现 P0 安全问题 → 立即停止 + 报告 user
- 跑分时间长 (3h) → 拆多 session, 进度写 decision-stream

**score < 60 target** → 立即修协议 (per §C.3.3 v2.6.56 强约束).

**反模式 (永久失效, 5 条, per ADR-0065 §4)**:

1. ❌ host-self-evolve 跑分 PENDING 跳过 memory-bench 50 题 = 违反 v3.2.8 段
2. ❌ 跑分报告不写 weighted total score / 不写 11 行总表 = 违反 §C.3.3 v2.6.56 强约束
3. ❌ 跑分中途 token 限制不报 user 不 AskUserQuestion = 违反 §C.3.6.1 no-stuck
4. ❌ 跑分 score < 60 target 不立即修协议 = 违反 §C.3.3 v2.6.56
5. ❌ 跑分报告写到非 `~/.agents/skills/host-self-evolve/reports/memory-bench/` 路径 = 违反 §C.3.3 路径规约

**联动**:

- 跟 §C.3.3 v2.6.56 强约束 + §C.3.3 v2.6.46 重版约束 协同
- 跟 ADR-0016 (memory-bench into rich-audit, user 立的归属决策) 协同
- 跟 ADR-0065 (本 ADR, 整数 slot 0065) 协同
- 跟 §C.3.6.1 no-stuck 协议 协同
- 跟 §H Acceptance Protocol 5 字段自检表 (新增第 6 字段: score) 协同

**历史 record**:

- 2026-07-18 v3.2.8: 立 (per user 2026-07-18 拍板 "把 memory-bench 50 题作为 host-self-evolve 必跑" + ADR-0065 整数 slot)
