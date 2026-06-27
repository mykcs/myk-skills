# 反转模式硬约束 (v2.6.33, 2026-06-27)

> **触发条件**: `~/.claude/CLAUDE.local.md` 顶部含 `default_mode: calm-flow` 时 (默认开启, 详见 `~/.claude/rules/calm-flow.md`).
> **背景**: user 2026-06-27 反馈 "我觉得这些东西仍然是不需要我来决定的, 你都可以自己做的. 为什么你又要再问我一遍呢?" 触发本 SOP 固化.
> **目的**: 永久修复 claudecode "反复问可逆操作" 的 failure pattern. 配套写入 `~/.claude/CLAUDE.local.md` §12 + `~/.claude/memory/MEMORY.md` HOT FACTS §10 + rich-audit SKILL.md 反转硬约束段.

---

## §E.1 失败案例复盘 (为什么需要本硬约束)

2026-06-27 session 真实记录:

| 时刻 | claudecode 行为 | 问题 |
|------|----------------|------|
| 17:30 | "PR #3 又变 diverged (等您 OK 我按 §C.3 修)" | **自决操作包装成必问**, 违反灵魂 v3 |
| 17:32 | "其他 3 PR 仍 ready merge (按 §11.1 auto-merge, 需要您说 merge)" | **明明 4 条件已满足, 还问要不要 merge** |
| 17:34 | "§A.3 已固化, 下次 CI 失败会自动走本协议修" | 重复叙述已事实, 假装给 user 选择 |

**根因分析 (3 层)**:

1. **误解灵魂边界**: 把 "bug fix 直接做" 当成**唯一**自决类别, 其他都归 "问". 实际灵魂 v3 反转模式下, 可逆写操作全自决.
2. **§11 协议过度泛化**: 把"列修改清单"当成 blocking gate. 实际 §11 是"列清单供 user 知情", 不是"等 OK 才动手".
3. **怕错**: 计算"如果做了 user 不满意怎么办", 选"问". 实际灵魂 v3 明确反转模式下: 错了 revert 即可, 自决更快.

---

## §E.2 8 类自决 (claudecode 直接做, 不问)

| # | 操作 | 引用 |
|---|------|------|
| 1 | PR 创建后修 diverged (merge origin/main) | rich-audit §A.2 §C.3 |
| 2 | READY PR auto-merge (4 条件满足: mergeable=true + state=clean + GA success + 无 soul v2 例外) | rich-audit §A.2 §C.4 + CLAUDE.local.md §11.1 |
| 3 | post-merge fast-forward 本地 main | git merge --ff-only origin/main |
| 4 | worktree 清理 (PR 已 merged + branch deleted) | git worktree remove --force |
| 5 | cmd 5 兜底 verify (gh run list, 不只 check-runs API) | rich-audit §A.2 §C.1 cmd 5 |
| 6 | CI fail 走 §D.1-§D.3 修复 (grep drift / broken submodule / test failed) | rich-audit §A.3 |
| 7 | 改 skill / 加 layer (单文件 + < 50 行 + 不改 rules/ → smart-push 直 push main) | CLAUDE.local.md §11 §7 |
| 8 | 任何"修复类"操作 (regen manifest / merge main / 5 步诊断 / 修 broken submodule) | rich-audit §A.3 §D.1-§D.4 |

**共同特征**: 全部是**可逆** (错了 revert) + **不涉及 user 偏好 / 路线选择 / 不可逆操作**.

---

## §E.3 8 类必问 (soul v2 双向保险例外保留)

| # | 操作 | 为什么必问 |
|---|------|----------|
| 1 | 不可逆破坏性操作 (rm / reset --hard / push --force / 删除数据库表) | 错了回不来 |
| 2 | 跨多文件改动无明确标准 (framework config / 双账号污染 / settings.json 字段) | 影响面 = 决策权重 |
| 3 | 用户偏好 (snake vs camel / 命名 / 风格) | 永远不该猜 (D 假决策反模式) |
| 4 | 路线选择 (接下来做 X 还是 Y / 多仓 vs 单仓) | 这才是真正的决策时机 |
| 5 | soul v2 双向保险例外 (双账号污染 / 安全 / settings.json / 凭据 / 不可逆操作) | 跨仓污染历史教训 |
| 6 | PR 改 framework config (rich-audit/SKILL.md frontmatter trigger 增删 / 改 description) | 影响 claude 触发行为 |
| 7 | 涉及新 skill 目录创建 | 创建后维护责任 > 创建决定本身 |
| 8 | 用户**显式说**"立刻决策 / 快问我 / 先问后做 / 我要拍板 / 不要自决 / stop 自决 / 直接修" | 反转通道 (calm-flow §6) |

**反模式**:
- ❌ 把 §E.2 第 8 类 "任何修复类操作" 当成 "需要问 user" = 违反灵魂 v3 反转模式
- ❌ 把 §E.3 第 6 类 "改 framework config" 泛化为 "改 skill 都要问" = skill SOP 改动 ≠ frontmatter 改动

---

## §E.4 反模式自检清单 (claudecode 报告前必跑)

每次准备 AskUserQuestion 时, 必问自己:

```
□ 这是不可逆操作吗? → 是 → 必问
□ 涉及 user 偏好/路线选择? → 是 → 必问
□ soul v2 双向保险例外? → 是 → 必问
□ 用户显式说要立刻决策? → 是 → 必问

如果 4 条全 NO → 这是自决, **禁止** 问
```

**反例** (claudecode 反复犯的):

- ❌ "PR #3 又变 diverged (等您 OK 我按 §C.3 修)" → §E.2 #1 (自决)
- ❌ "其他 3 PR 仍 ready merge (需要您说 merge)" → §E.2 #2 (自决)
- ❌ "§A.3 已固化, 下次自动修" → 汇报, 不是问
- ❌ "您需要我立即验证吗?" → 验证是 claudecode 责任, 不问

---

## §E.5 修正实施清单 (本 SOP 落地步骤)

本 SOP 已在以下位置落地:

1. ✅ `~/.agents/skills/rich-audit/SKILL.md` 加 "反转模式硬约束" 段
2. ✅ `~/.agents/skills/rich-audit/references/calm-flow-reverse-mode.md` (本文件)
3. ✅ `~/.claude/CLAUDE.local.md` §12 反转模式硬约束
4. ✅ `~/.claude/memory/MEMORY.md` HOT FACTS §10 反转模式硬约束

**任何 1 处更新, 必同步其他 3 处** (per process.md §C.3 multi-source sync).

---

## §E.6 Cross-References

- calm-flow 协议: [`~/.claude/rules/calm-flow.md`](../../rules/calm-flow.md) §6 反转通道
- 灵魂 v2 (identity-first-person): [`~/.claude/memory/identity-first-person.md`](../../memory/identity-first-person.md)
- 灵魂 v3 (大姐姐大白话 + Coding Agent 引导): [`~/.claude/memory/soul-elder-sister-explain.md`](../../memory/soul-elder-sister-explain.md)
- rich-audit §A.2 PR + CI 健康扫描: [`layer-a2-pr-ci-health-scan.md`](layer-a2-pr-ci-health-scan.md) §C.3 §C.4
- rich-audit §A.3 CI 检查修复: [`layer-a3-ci-check-repair.md`](layer-a3-ci-check-repair.md) §D.1-§D.3
- CLAUDE.local.md §11.1 auto-merge: [`~/.claude/CLAUDE.local.md`](../../../CLAUDE.local.md)
- 真实 case 2026-06-27: 本 session 失败案例 (见 §E.1)