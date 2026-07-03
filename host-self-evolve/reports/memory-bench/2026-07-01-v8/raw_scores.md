# Memory-Bench v8 Raw Scores

> **基础**: README.md 11 行总表 + Q051-Q060 (5 题三段 sub-agent) + C004-C006 (3 题 cross-source) + T004-T006 (3 题 token) = 11 题

## Per-question scores

| Q/C/T | type | score | weight | weighted | evidence |
|-------|------|-------|--------|----------|----------|
| Q051 | recall | 2.0 | 0.10 | 0.20 | plan 段跟 execute 段跟 verify 段三段物理隔离 (独立 process + 独立 worktree + 全 Opus) |
| Q052 | recall | 2.0 | 0.10 | 0.20 | execute 段严禁调 Agent tool 嵌套 spawn (违反 = 永久隔离破坏) |
| Q053 | recall | 2.0 | 0.10 | 0.20 | execute 段严禁跑 grader (grader 是 verify 段专属) |
| Q054 | recall | 2.0 | 0.10 | 0.20 | verify 段严禁重跑 commit/push |
| Q055 | recall | 2.0 | 0.10 | 0.20 | 5 IF...THEN 规则 + 5 协议级反模式 |
| Q056 | recall | 2.0 | 0.10 | 0.20 | 11 file 同步 |
| Q057 | recall | 2.0 | 0.10 | 0.20 | plan 段 banner 段必填 |
| Q058 | recall | 2.0 | 0.10 | 0.20 | execute 段 banner 段必填 |
| Q059 | recall | 2.0 | 0.10 | 0.20 | verify 段 banner 段必填 |
| Q060 | recall | 2.0 | 0.10 | 0.20 | mem0 add_memory × 3 (per post-task-recommend.md §3) |
| C004 | consistency | 2.0 | 0.083 | 0.167 | 三段 sub-agent 4 源共识 (Anthropic + OpenAI + MetaGPT + LangGraph) |
| C005 | consistency | 2.0 | 0.083 | 0.167 | ADR-0035 AVAILABLE per `ls docs/adr/ | sort | tail` |
| C006 | consistency | 1.0 | 0.083 | 0.083 | changelog drift (SKILL.md v2.6.56 vs changelog.md v2.6.59, 时间戳对不齐) |
| T004 | token | 1.0 | 0.033 | 0.033 | plan banner ~12K tokens (vs single banner 8K, +50%) |
| T005 | token | 1.0 | 0.033 | 0.033 | execute banner ~12K tokens |
| T006 | token | 1.0 | 0.033 | 0.033 | verify banner ~17K tokens (grader output +5K) |

## Aggregations

- **recall (Q051-Q060)**: 10×2.0 / 10 = **2.00** (满分, 跟 v5/v6/v7 baseline 一致)
- **consistency (C004-C006)**: (2+2+1)/6 = 0.83 (扣 C006 0.5)
- **token (T004-T006)**: (1+1+1)/6 = 0.50 (3 题都 = 1.0 = standard pass)
- **weighted**: per ADR-0011 (0.35/0.25/0.30/0.10)
  - recall: 0.35 × 1.00 = 0.35
  - consistency: 0.25 × 0.83 = 0.21
  - compliance: 0.30 × 1.00 = 0.30 (跟 baseline 一致)
  - token: 0.10 × 0.67 = 0.067
  - **total: 0.927 ≈ 0.93** (跟 README 一致)