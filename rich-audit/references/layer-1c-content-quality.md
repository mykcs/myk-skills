# Layer 1c: 内容质量审查 (CLAUDE.md / rules/ scope 检测, v2.6.37, 2026-06-27)

> **触发**: rich-audit 跑 Layer 1 文件结构扫描时, **自动加跑** scope + 内容质量检查, 不仅看行数, 还看"是否恰当、合适、高效、有用" (per user 2026-06-27 原话).
> **范围**: 全局 CLAUDE.md (`~/.claude/CLAUDE.md`) + 项目级 CLAUDE.md (`<repo>/CLAUDE.md`) + rules/ 目录.
> **完整 SOP**: §1.1 scope 边界检测 + §1.2 内容质量审查 + §1.3 严重度分级 + §1.4 修复建议模板 + §1.5 反模式.

---

## §1.1 Scope 边界检测 (CLAUDE.md 该装什么)

**核心原则** (per Anthropic 官方 docs + community 共识):

| Scope | 位置 | 该装什么 | 不该装什么 |
|-------|------|---------|-----------|
| **Global** | `~/.claude/CLAUDE.md` | 全局 OMC 编排 + persona + 跨项目协议 | 项目技术栈 / 部署平台 / 单仓 build 命令 |
| **Project** | `<repo>/CLAUDE.md` | 该项目的技术栈 / 部署 / 学术特性 / 设计系统 / content 同步 | 跨项目通用协议 / 双账号铁律 / OMC 编排层 |
| **Path-scoped** | `~/.claude/rules/<name>.md` (paths: 限定) | 特定路径类型的规则 (CSS / TypeScript / Python) | 无路径限定时不要复用 rules/ |

**scope 漂移检测 6 维度**:

| 维度 | 检测方法 | 反模式 |
|------|---------|--------|
| 1. 全局 CLAUDE.md 含项目专用内容 | `grep -E "astro\|tailwind\|katex\|deploy" ~/.claude/CLAUDE.md` | ❌ 全局塞 Astro 细节 |
| 2. 项目 CLAUDE.md 含全局协议 | `grep -E "oh-my-claudecode\|双账号\|persona" <repo>/CLAUDE.md` | ❌ 项目塞 OMC 协议 |
| 3. 跨项目同一技术栈出现 > 3 次 | grep 4 个 active 仓的 CLAUDE.md 找重复内容 | ❌ 复制粘贴 4 份相同 Astro 段 |
| 4. CLAUDE.md > 200 行 | `wc -l <repo>/CLAUDE.md` | ❌ 跟官方建议 < 200 行 drift |
| 5. 含 emoji + marketing 风格 | `grep -c "🎉\|🚀\|✨" <repo>/CLAUDE.md` | ⚠️ 可接受但过量 (>5) 是反模式 |
| 6. 跟 path-scoped rules/ 重复 | `diff <repo>/CLAUDE.md ~/.claude/rules/*.md` | ❌ 同一规则写两遍 |

**真实案例 (2026-06-27)**:
- `mykcs.github.io/CLAUDE.md` 224 行, 含: Astro v6.1.5 / Tailwind v4 / KaTeX / Prism / @astrojs/prism / Bilingual / 设计系统 (Times New Roman) / 自动推送 / 学术资源管理 — **100% 项目专用, 全局无用**
- `~/.claude/CLAUDE.md` 160 行, 100% OMC 编排 + persona + repo confirmation — **0% 项目专用**
- 4 个 active 仓的 CLAUDE.md 大小: mykcs.github.io 224 / GDKVM 91 / OSA 84 / content2html 0 (无) — **mykcs.github.io 异常大**

---

## §1.2 内容质量审查 (恰当 / 合适 / 高效 / 有用 4 维度)

**4 维度评分** (per user 原话 "保证恰当、合适、高效、有用"):

| 维度 | 含义 | 检测方法 | 0-3 分 |
|------|------|---------|--------|
| **恰当 (Appropriate)** | 内容是否在该 scope 该出现? | §1.1 6 维度 scope 漂移检测 | 3=纯该 scope, 0=严重 scope 漂移 |
| **合适 (Suitable)** | 内容是否适合 claudecode 读? | 是否含操作步骤 / 命令 / 验收标准 | 3=可操作, 0=纯描述没 actionable |
| **高效 (Efficient)** | 是否有冗余 / 重复 / 过期? | grep 重复段 + 过期信息 (>6 个月没更新) | 3=精简直击, 0=大段复制粘贴 |
| **有用 (Useful)** | 是否解决 claudecode 在该仓的真实问题? | 跟 case library 已知问题对得上 | 3=覆盖已知 case, 0=装饰性内容 |

**总分公式**: `quality_score = 恰当*0.4 + 合适*0.2 + 高效*0.2 + 有用*0.2` (恰当权重最高, 避免 scope 漂移)

**判定矩阵**:

| 总分 | 判定 | 修复建议 |
|------|------|---------|
| 9-12 | ✅ PASS | 不动 |
| 6-9 | ⚠️ WARNING | 列改进建议 (Tier 2 auto-fix) |
| 3-6 | ❌ TIER1 FIX | 自动拆分 / 删冗余 (Tier 1 mechanical) |
| 0-3 | 🚨 BLOCKED | 必问 user, 拆 scope 错位严重 |

---

## §1.3 严重度分级 (跟 rich-audit auto-fix tier 对齐)

| 严重度 | Tier | 例子 | 处理 |
|--------|------|------|------|
| **CRITICAL** | 3 (user 必问) | 全局 CLAUDE.md 含项目专用 Astro 段 | AskUserQuestion 确认拆分方案 |
| **HIGH** | 2 (auto + revert window) | 项目 CLAUDE.md > 250 行 (Anthropic 软限 200 超出 25%) | auto-suggest 拆分, 30-min revert window |
| **MEDIUM** | 2 | 跨 3+ 仓复制粘贴相同技术栈段 | auto-suggest 提到 shared `~/.claude/rules/typescript.md` |
| **LOW** | 1 (auto) | 过期信息 (> 6 个月没更新) | 自动删 / 加过期警告 |

---

## §1.4 修复建议模板 (output contract)

```markdown
## 内容质量审查报告 (Layer 1c, v2.6.37)

### Scope 漂移检测
- 🚨 CRITICAL: 全局 CLAUDE.md 含项目专用内容 (n 处)
- ⚠️ WARNING: 项目 CLAUDE.md 含全局协议 (n 处)

### 4 维度评分
| 维度 | 分数 | 详情 |
|------|------|------|
| 恰当 | 1/3 | 全局塞 Astro 细节 (-2) |
| 合适 | 2/3 | 命令可执行 |
| 高效 | 1/3 | 多处重复 (-2) |
| 有用 | 2/3 | 覆盖已知 deploy issue |
| **总分** | **6/12** | ⚠️ WARNING |

### 修复建议 (按 Tier 分组)
- Tier 1 (auto): [自动修复 N 项]
- Tier 2 (auto + 30-min revert): [半自动修复 M 项]
- Tier 3 (user 必问): [拆分方案 K 项, AskUserQuestion]
```

---

## §1.5 反模式 (claudecode 必避)

- ❌ **只看行数不看 scope** = 行数 PASS 但 scope 错位, 等于审计失败 (user 2026-06-27 原话 "里面的内容也要保证一些, 保证恰当、合适、高效、有用")
- ❌ **scope 漂移自动拆不告诉 user** = 跨项目 OMC 编排塞进项目 CLAUDE.md, 影响别的项目 → 必问
- ❌ **用 emoji ✅ 替代 actionable 修复建议** = 4 维度评分要给具体 grep / 命令, 不是"看起来 OK"
- ❌ **CLAUDE.md 无限增长** = 不强制 < 200 行就回到 Anthropic soft limit 的反模式
- ❌ **path-scoped rules/ 跟 CLAUDE.md 重复** = 同一规则两份维护, drift 风险
- ❌ **不区分 4 个维度** = "恰当"和"高效"是两个轴, 不能合并打分

---

## Cross-References

- rich-audit SKILL.md §A.1 Layer 0 (5 commands verification, 不含内容审查)
- rich-audit SKILL.md §I.4 Layer 4 (skill self-evolution, 跟本 Layer 1c 是平行的, 不重叠)
- Anthropic 官方 CLAUDE.md 最佳实践: <https://code.claude.com/docs/en/memory>
- 真实 case: 本次 session (2026-06-27) mykcs.github.io/CLAUDE.md 224 行全是项目专用, 全局不该塞
- 真实 case: v2.6.30 skill evolution 引发的 SKILL.md 同步 4 处强制约束 (跟本 Layer 1c 互补: 本 Layer 是审查 CLAUDE.md 是不是合适 scope, v2.6.30 是审查 skill 自身是不是要升级)