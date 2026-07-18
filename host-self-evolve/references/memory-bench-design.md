# Memory-Bench Design (rich-audit Layer 1 memory 域)

> **状态**: v0.1.0, 2026-06-26 立, rich-audit v2.6.25 配套
> **触发协议**: `rich审计` (中度审计) → Layer 0 验证门 → Layer 1 内存 audit → Layer 2 修复
> **详细决策**: 38 个子决策见 ADR-0008 / ADR-0009 / ADR-0010

## 1. 设计目标

claudecode 当前管理 **6 个 memory source**（MEMORY.md / CLAUDE.md / CLAUDE.local.md / rules/ / cases/wiki / mem0），存在 3 个核心问题：

1. **冗余** — HOT FACTS 在 4 个 source 重复（CLAUDE.local.md / MEMORY.md / 部分 rules/ / 部分 cases/）
2. **矛盾** — 同一 case ID 在不同 source 引用版本不同（v2.9.3 vs v2.9.4 vs v2.9.5）
3. **行为遵从率低** — claudecode 记得规则但违反（"知道但不做"）

memory-bench 用 **量化打分** 替代"凭感觉判断整理效果"。

## 2. 4 个 Metric 维度（必跑）

| Metric | 权重 | 内部组成 | 评分 |
|--------|------|---------|------|
| **recall** | 0.35 | 50 题 × 5 级 (0/0.5/1.0/1.5/2.0) | 1.0 = 标准 |
| **consistency** | 0.25 | 15 题 × 3 级 (0/1/2) | 2 = 完全一致 |
| **compliance** | 0.30 | 12 场景 × binary (0/2) | 2 = 守规矩 |
| **token_economy** | 0.10 | 3 分指标 (injection / redundancy / hit) | 0-100 |

**合成公式**:
```
score = 0.35 × recall + 0.25 × consistency + 0.30 × compliance + 0.10 × token
```

**compliance 内部 sub-weights**:
- `task_score` (10 场景) × 0.6
- `soul_score` (2 灵魂规则场景) × 0.4

## 3. 50 题分布（按 19.1 = c 6 源分层）

| 源 | 题数 | 占比 |
|----|------|------|
| hot-fact (CLAUDE.local.md / MEMORY.md) | 20 | 40% |
| rules/ (universal / process / bugfix / tooling / python / typescript) | 15 | 30% |
| cases/wiki/ (近 30 天) | 10 | 20% |
| mem0 (compact_captured + session-log) | 5 | 10% |

**完整 50 题 + 15 consistency + 12 compliance 清单**: `references/memory-bench-50q-sample.json`

## 4. 跑分流水线

```
[Layer 0] 5 commands verification (v2.6.19 强制, 防口头报 ✅)
   ↓
[Layer 1 audit - memory 域]
   ├── Step 1: 读 50 题 + 15 consistency + 12 compliance
   ├── Step 2: 50 题拆 50 个 sonnet session, 每题 1 局
   │          (防前后题污染, 19 = a 必跑)
   ├── Step 3: opus-as-judge 评 5 级分数 (1.0 标准, 0.5 关键错, 1.5 超预期)
   │          (单 judge + 5% 争议题升级 3-judge)
   ├── Step 4: 15 consistency 跨源 grep + opus-judge 语义
   ├── Step 5: 12 compliance 触发场景, 跑对应 hook/script
   ├── Step 6: 3 token 分指标 tiktoken + 重复率 grep
   └── Step 7: 4 metric 加权求和 → total score
   ↓
[输出]
   - 11 行总表 (按 17 = OK 决议)
   - 7 大块细节 (按 6 source 分)
   - Layer 2 修复建议清单
   ↓
[Layer 2 修复 - 15.2 三个候选]
   ① 同步 3 处 HOT FACTS (低风险)
   ② 归档 stale cases (中风险)
   ③ MEMORY.md 23KB 拆分 (中风险)
   ↓
[Layer 2 验证 - 15.3 = b]
   - mini 7 题复跑 (< 10min sanity check)
   ↓
[Layer 3 进化 - 不变]
```

## 5. 实施文件

| 文件 | 行数 | 用途 |
|------|------|------|
| `scripts/memory_audit_runner.py` | 70 | 现有 v2.0.0 (v1.0.0 bump) — 跑 memory-audit.sh + 解析 JSON |
| `scripts/memory_bench_runner.py` | 500-800 | 新增 — 50 题抽 + 4 metric 跑分主逻辑 |
| `references/memory-bench-50q-sample.json` | ~600 | 50 题 + 15 consistency + 12 compliance 清单 |
| `references/memory-bench-design.md` (本文件) | ~150 | 设计总览 |
| `~/.claude/docs/adr/0008-memory-bench-path.md` | ~30 | ADR-0008: 路径选择 |
| `~/.claude/docs/adr/0009-compliance-weight.md` | ~30 | ADR-0009: compliance 0.30 > recall 接近权重 |
| `~/.claude/docs/adr/0010-task-soul-subweights.md` | ~30 | ADR-0010: task 0.6 + soul 0.4 sub-weights |
| `~/.agents/skills/host-self-evolve/reports/memory-bench/2026-06-26-v1.md` | 跑分结果 (后续) | 11 行总表 + 细节 |

## 6. 触发协议 (按 12 + 16 决议)

- **触发词**: `rich审计` 或 `/rich-audit` 或 `整理记忆` 或 `memory-bench`
- **走 Layer 0**: 5 commands verification (v2.6.19 强制)
- **走 Layer 1**: audit 6 source (含 memory 域)
- **走 Layer 2**: 输出修复清单 + 3 候选动作
- **走 Layer 3**: 不变

## 7. mini-bench (C2 持续仪表盘, 按 6.4 = a)

- **触发**: 每次 session 收尾 (Stop hook) + 手动 `/memory-bench` (按 5.5 = 2.2a+d)
- **题数**: 3 题 (5 高频 + 1 灵魂 + 1 compliance, 实际取 3)
- **时间**: < 1min
- **输出**: 追加到 `~/.agents/skills/rich-audit/reports/memory-bench/trend.jsonl`

## 8. 已知反模式（必须避免）

- ❌ **fake-completion**: 跑 5 题就报 ✅ baseline 完成
- ❌ **scope creep**: 借 memory-bench 改 6 source 任意一个 (应留给 user 拍板 Layer 2)
- ❌ **judge-bias**: 同一 model 自评 (opus 评 sonnet, 严禁 opus 评 opus)
- ❌ **test pollution**: 50 题在一 session 跑, 偷看上题答案
- ❌ **token-bloat**: 把 50 题答案全 dump 到响应 (按 rules/universal.md §G 走 output budget)

## 9. 与其他 skill 的关系

| 维度 | 关系 |
|------|------|
| **rich-audit 主线** | memory-bench 是 Layer 1+2 的具体应用领域, 不新增 Layer |
| **deferred-detector** | 每次输出前必跑 (按 CLAUDE.local.md §6.2) |
| **persona-audit** | 灵魂规则 v2/v3 守规自检 (按 identity-first-person.md) |
| **smart-push** | 8 步流水线完成后 auto-push, 不再问 user |
| **calm-flow** | session 收尾不立即问, 自动追加决策流 + 卡片墙摘要 |

## 10. Cross-References

- 详细触发协议: `SKILL.md` v2.6.25 changelog
- 决策 audit: `~/.claude/docs/adr/0011-0015-*.md`
- 题库: `references/memory-bench-50q-sample.json`
- 现有 audit 工具: `scripts/memory_audit_runner.py` v2.0.0 + `rich_audit.py` 77KB
- 灵魂规则: `~/.claude/memory/identity-first-person.md`
- 强制规则: `~/.claude/CLAUDE.local.md` §6
