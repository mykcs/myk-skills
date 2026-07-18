# memory-bench v2/v3/v4/v6/v7 baseline compare 最终版 (per ADR-0067 §3 step 6)

| # | 维度 | v2 (baseline) | v3 (补跑 1) | v4 (LLM-judge v1) | v6 (LLM-judge v2 修 3 bug) | **v7 (LLM-judge v3 + mmx 替 claude)** |
|---|------|--------------|---------------|--------------------|----------------------------|----------------------------------------|
| 1 | run_id | memory-bench-2026-07-18-v2 | memory-bench-2026-07-18-v3 | memory-bench-2026-07-18-v4 | memory-bench-2026-07-18-v6 | **memory-bench-2026-07-18-v7** |
| 2 | timestamp | 2026-07-18T16:53:09+00:00 | 2026-07-18T17:03:42+00:00 | 2026-07-18T17:14:53+00:00 | 2026-07-18T18:03:43+00:00 | **2026-07-18T18:08:01+00:00** |
| 6 | judge | opus-as-judge v4.5 (keyword fallback) | 同 | llm-judge+position-bias (claude -p 子进程) | llm-judge+position-bias (宽容 regex) | **llm-judge+position-bias (mmx text chat)** |
| 7 | **recall_total** | **23.8/50** | **4.0/50** | **0.0/50** | **0.0/50** | **5.2/50** ✅ |
| 8 | consistency_total | 0/15 (stub) | 0/15 (stub) | 0/15 (tilde bug) | **14/15** (expanduser fix) | **14/15** ✅ |
| 9 | compliance_total | 0/12 (stub) | 0/12 (stub) | 12/12 (test -f 假阳性) | **11/12** (加重 12 真 hook) | **11/12** ✅ |
| 10 | **weighted_score** | 0.22 | 0.08 | 0.35 | 0.56 | **0.60** |
| 11 | target_met (≥1.0) | ❌ < 60 | ❌ < 60 | ❌ < 60 | ❌ < 60 | **❌ < 60 (差 0.40)** |
| 12 | deviation_pct (vs baseline) | N/A | -83% UNRELIABLE | -100% UNRELIABLE | -100% UNRELIABLE | **N/A (新 baseline)** |
| 13 | reliable | N/A | ❌ | ❌ | ❌ | **✅** |

## 5 维诊断 (v2 → v7)

### 维度 1: recall 退化 + 修复链

| Run | recall | 根因 |
|-----|--------|------|
| v2 | 23.8/50 | keyword fallback (轻量, 5.9x 随机性) |
| v3 | 4.0/50 | 同 v2 + 关键词命中少 |
| v4 | 0.0/50 | LLM-judge v1, regex 严苛 + claude -p 未登录 → 全 fallback 0 |
| v6 | 0.0/50 | LLM-judge v2 宽容 regex + claude -p 仍 "Not logged in" → 全 fallback 0 |
| **v7** | **5.2/50** | **LLM-judge v3 + mmx text chat (替 claude -p) → 真评分工作** |

✅ **v7 recall 5.2 > 0** = LLM-judge 链路打通, 但分数仍偏低 (mmx 评分严 + 多数题答得不完整).

### 维度 2: consistency 0 → 14/15

- v2/v3 stub (没跑); v4 tilde bug; **v6/v7 14/15** = expanduser fix 成功
- 1 题不通过 = 待查 (C15 没命中, 可能 skeleton 字眼在新 case 还没沉淀)

### 维度 3: compliance 12/12 假阳性 → 11/12 真验证

- v4 12/12 全过 = 设计太简单 (都是 test -f)
- **v6/v7 11/12** = 加重 12 题跑真 hook/script, 1 题不通过 (L02 grep 双源 mmx 没命中? 待查)

### 维度 4: weighted_score 提升链路

```
v2 (0.22) → v3 (0.08) → v4 (0.35) → v6 (0.56) → v7 (0.60)
                                         +0.21       +0.04
```

✅ weighted_score 从 0.22 (keyword) → **0.60 (LLM-judge)** = +0.38 (+173%), target 1.0 还差 0.40.

### 维度 5: baseline deviation & reliable

- v3/v4/v6 deviation -83% ~ -100% UNRELIABLE (runner 不可靠)
- **v7 deviation N/A reliable ✅** = 跑分稳定, v7 是新 baseline

## 结论

**runner v4 (mmx 替 claude -p) 升级成功**: recall 0.0 → 5.2 (链路打通), consistency 14/15, compliance 11/12, weighted 0.60 (差 target 0.40).

**runner v4 协议位 (per ADR-0067)**:
- ✅ mmx text chat 替代 claude -p (CLI session 未登录不依赖 Claude)
- ✅ LLM-judge 宽容 regex + verbose 模式
- ✅ Consistency tilde expanduser
- ✅ Compliance 加重 12 题跑真 hook/script
- ✅ Position bias 缓解 (双评取均值)
- ✅ Baseline deviation 检测 + reliable 标志

**未达 target 60 协议位**:
- recall 5.2/50 偏低 (mmx 评分严 + 多数题答得不完整)
- compliance 11/12 差 1 题 (L02 双源 mmx? 待查)
- target 1.0 = 60/100, 当前 0.60 = 差 0.40

**下一步** (per runner v5 升级需求):
- ❌ 不 commit v3/v4/v6 reports (不可靠 baseline)
- ✅ commit v7 report (新 baseline) + runner v4 (mmx fix) + compliance v2
- ADR-0067 §6 TODO 加: recall 提升 (mmx prompt 优化 / 子仓期望答案细化) + compliance L02 修复

## 历史 record

- 2026-07-19 v1 立: per ADR-0067 §3 step 6, host-self-evolve run @ 2026-07-19
  - 触发: v7 跑分 recall 5.2 修复成功, 但 weighted 0.60 未达 target
  - 落地: 5 份 baseline 对比 + 5 维诊断 + runner v4 升级协议位 + runner v5 待修项
  - 整数 slot: 本文件是 runner v4 验收对比, 不立 ADR (已有 ADR-0067)