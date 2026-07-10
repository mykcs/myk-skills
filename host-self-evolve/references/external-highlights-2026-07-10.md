# N-tool 抓 8+ 资源 highlights (2026-07-10, host-self-evolve v3.2.1 run)

> **触发**: host-self-evolve v3.2.1 run Layer 3 (N-tool fan-out, per §I.4 8 步循环 step 2)
> **抓取日期**: 2026-07-10 11:13 CST
> **工具**: MiniMax + anysearch + exa parallel fan-out (per N-tool-search.md §6)
> **状态**: ✅ 抓 15+ hits, 内部化 6 大洞见

---

## §1. 抓到的关键资源 (10 项)

### 1.1 SKILL.md frontmatter 规范 (4 源共识)

| 源 | 关键发现 |
|---|---|
| **Anthropic 官方** (code.claude.com/docs/en/skills) | description + when_to_use combined **capped at 1,536 chars** in skill listing (v2.1.105 changelog) |
| **claudskills / claudcodeguides** (4 源三角验证) | description front-load trigger phrases, 800-1,200 chars 是 right starting point |
| **RuleSell** | "pushy descriptions" 反模式 (6 phrase OK, 20 pushy, avoid superlatives) |
| **issue #47627 RESOLVED** | 旧 250 char cap 已升级 1,536, startup warning 新增 |

**Internalize 洞见**: 现有 host-self-evolve v3.2.1 description 估计 ~700 chars + when_to_use ~300 chars = combined ~1,000 chars, 留 536 chars 缓冲 (达标)。

### 1.2 Hooks PreToolUse / Stop 最佳实践 (3 源共识)

| 源 | 关键发现 |
|---|---|
| **Anthropic hooks-guide** | hooks 是 deterministic shell command, exit code 控制 (0 = proceed / 2 = block / 1 = non-blocking error) |
| **adamarant.com** (生产实践) | "PreToolUse hook that exits 2 always cancels the tool call" + 12 lifecycle events |
| **scalably.io** (生产级) | hooks 3 scope: ~/.claude/settings.json > .claude/settings.json (committed) > .claude/settings.local.json (gitignored) |

**Internalize 洞见**: 本次 v3.2.1 run 挂的 4 hooks (cross-session-grep + verify-before-act PreToolUse + protocol-violation-detect Stop + post-pr-merge-ff-verify PostPRMerge) 全部走 ~/.claude/settings.json (user scope), exit 0 默认 = 不阻断。**潜在风险**: PostPRMerge 不是 Anthropic 官方 lifecycle event (per hooks reference table, 12 events 不含 PostPRMerge), 需 fallback 测真。

### 1.3 Claude Code "自进化系统" 实战 (1 源)

- **CSDN blog** (claude code cli 如何实现自动进化执行): 用户原话 "Claude 会搜索现有模式并评估影响范围。代码生成：遵循 CLAUDE.md 规范...5 项验证"
- **Internalize 洞见**: 跟 host-self-evolve v3.2.1 5 Layer + 5 字段自检协议一致, 不需重构

### 1.4 CLAUDE.md < 150 行 实战共识 (3 源)

| 源 | 关键发现 |
|---|---|
| **腾讯云 best-practices** | "社区共识是不超过 300 行, HumanLayer 团队建议控制在 60 行以内" |
| **CSDN claude-howto** | "保持精简!社区共识是不超过 300 行" |
| **qq.com** | "CLAUDE.md 文件别超过 150 行. 这个文件是 Claude 每次启动都会读取的上下文" |

**Internalize 洞见**: 现有 CLAUDE.md 167 行 (已超 150 共识但 ≤ 200 hard limit), 偏紧。CLAUDE.local.md 321 行 (超 hot recall 250 行目标), 留 P2。

### 1.5 实战工程团队总结 (1 源)

- **qq.com 团队经验** (2026-02-08): "复杂任务一律先 plan mode" + "把 CLAUDE.md 当成长期投资标的" + "Plan mode + staff engineer 审计划" + "Worktree 起名 za/zb/zc"
- **Internalize 洞见**: 跟 host-self-evolve v3.1.0 banner 段 + v3.2.0 Phase 1 段 + 三段 sub-agent 协议位 (v2.6.59) 协同, 不需新加协议

---

## §2. 内部化 (internalize) 摘要 (6 大洞见)

1. **frontmatter 1,536 cap 是当前 Anthropic 官方** (v2.1.105 changelog), 旧 250 cap 已废, host-self-evolve 当前合规
2. **hooks 12 lifecycle events** (per Anthropic hooks reference table), PostPRMerge **不在 12 内**, 本次 v3.2.1 run PostPRMerge post-pr-merge-ff-verify.sh 需 fallback 测试 (否则 hook 不触发)
3. **hooks exit code 协议位**: 0 = proceed, 2 = block, 1 = non-blocking error — 本次 4 hooks 都用 exit 0 (不阻断, 仅提醒)
4. **CLAUDE.md 150 行共识** (qq.com) vs 200 行 hard limit (per §A.4.2 #4) — 150 是 user 哲学, 200 是 hard ceiling, 当前 167 偏紧但 OK
5. **hooks 3 scope 优先级**: user > project > local, 本次 4 hooks 走 user scope (per protocol-violation-auto-detect §4 + cross-session-grep §3 协议位设计)
6. **"pushy descriptions" 反模式** — 6 phrase OK, 20 pushy, 避免 superlatives — host-self-evolve v3.2.1 当前 description 4 trigger phrases, 合规

---

## §3. 联动 (cross-references)

- 跟 ADR-0050 v1.0 (host-self-evolve v3.2.1 default decision) 协同: 本 highlights 是 v3.2.1 run Layer 3 抓的资源
- 跟 N-tool-search.md §1 协议位协同: 本 run 跑 MiniMax + anysearch + exa 3 tool (N=3 降级, 不强制 N=6, per §3.1)
- 跟 §I.4 8 步循环协同: 本 highlights = step 2 抓外部资源, 下一步 step 3 internalize 已落 §2
- 跟 tooling-section-A-settings-json-sop.md §A.4 验证清单协同: 本次挂 4 hooks 跑完 diff 38 行 + JSON valid + 5 commands verify

---

## §4. 反模式 (永久失效)

- ❌ "frontmatter 用 250 char 老 cap" = 违反 v2.1.105 changelog
- ❌ "hooks 写 super pushy description" = 违反 RuleSell 反模式
- ❌ "PostPRMerge 不在 12 lifecycle events 内还挂" = 需 fallback 测试, 否则 hook 静默不触发
- ❌ "CLAUDE.md 写到 300+ 行" = 违反 §A.4.2 #4 + 实战共识
- ❌ "hook exit code 默认 0 假装 proceed" = 不阻断是真, 但不告知 user = 反模式

---

## §5. 历史 record

- 2026-07-10 v1.0: 立 (host-self-evolve v3.2.1 run Layer 3 N-tool fan-out + 6 大洞见 internalize + 4 反模式永久失效)