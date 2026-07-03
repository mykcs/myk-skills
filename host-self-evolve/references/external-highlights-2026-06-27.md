# External Highlights — 2026-06-27 §I.1 step 2 (rich-audit self-evolution cycle)

> 触发: rich-audit v2.6.31 §I self-evolution cycle, Layer 3 必跑 5-tool fan-out
> 工具: MiniMax (10 results) + WebFetch (Anthropic 官方) + exa (4+8 results) + anysearch (5 results)
> 状态: 8+ 资源 highlights 已抓, internalize → ADR-0020 + SKILL.md changelog v2.6.32

---

## 共识 (高 confidence, 4 源 + Anthropic 官方)

### 1. SKILL.md frontmatter 规范 (Anthropic 官方)

| 字段 | max chars | 校验 | rich-audit 当前值 | 反模式 |
|------|-----------|------|------------------|--------|
| `name` | 64 | ✅ rich-audit = 10 chars | `rich-audit` | 包含 XML / reserved words (anthropic, claude) |
| `description` | 1024 | ✅ rich-audit = 186 chars | 三层进化系统描述 | 空 / 含 XML |
| `metadata.*` | 自定义 | ✅ 2.6.36 | `metadata.version: "2.6.31"` | 缺 metadata.version |

**Anthropic 官方推荐**: `description` 必须包含 "what + when to use"，建议包含 5 anti-trigger examples（"Do NOT use this skill for X/Y/Z"）。

### 2. Progressive disclosure 3-level 架构

| Level | When Loaded | Token Cost | Content |
|-------|-------------|------------|---------|
| **Level 1: Metadata** | Always (startup) | ~100 tokens/Skill | `name` + `description` frontmatter |
| **Level 2: Instructions** | When triggered | <5K tokens | SKILL.md body |
| **Level 3+: Resources** | As needed | Effectively unlimited | Bundled files via bash (不载入 context) |

**rich-audit 当前**: 已用 progressive disclosure (v2.6.20 split 88+87+78 lines → references/), 主 SKILL.md 332 行, 4 references/ 文件, 完美对齐 Level 2/3 架构。

### 3. SKILL.md body 500 行硬限 (Anthropic 官方 + 4 源共识)

> "Keep SKILL.md body under 500 lines for optimal performance. If your content exceeds this, split it into separate files using the progressive disclosure patterns."

**rich-audit 当前**: 332 行 ✅ (离 500 软限还有 168 行 buffer)

### 4. Self-improvement 3 模式 (4 源共识)

| 模式 | 来源 | 核心机制 |
|------|------|---------|
| **Learnings.md (4 phases)** | mindstudio fallback | 强制 read first + write last + confidence scoring |
| **Capture-vs-Judgment** | annexiao/claude-code-self-evolution | 2 capture streams + 1 /evolve judgment surface + 4 gates + cost-aware routing |
| **Confidence-Gated Evolution** | shanraisshan 68 skills 6 weeks | HIGH≥0.7 auto-deploy / MEDIUM 0.3-0.7 surface / LOW<0.3 log only |
| **Karpathy 4 principles + refinement loop** | DailyTopAI | Think before coding + Simplicity + Surgical + Goal-driven + 内置 refinement loop |

**rich-audit 当前**: 已有 §I self-evolution cycle 8 步 (5-tool fan-out → 8+ 资源 → internalize → ADR → SKILL.md → commit → PR → 5 commands)。但**缺 confidence gating** + **缺 capture-vs-judgment 分离** + **缺 cost-aware routing**。

---

## 冲突 (需溯源 / 已判定)

### C1: SKILL.md 500 行 vs 900 行

| 立场 | 来源 |
|------|------|
| 500 行 | Anthropic 官方 best-practices |
| 900 行 | Agent Engineer Master (AEM quality protocol 2026) |

**判定**: 用 Anthropic 官方的 500 行。rationale: 官方 > 第三方, 软限不是硬限 (避免 false-positive)。

### C2: Frequency-based 自动更新 vs 严格 confidence-gated

| 立场 | 来源 |
|------|------|
| 频率自动更新 ("Claude failed 3 次 → 更新") | 多数 LLM 教程 |
| **拒绝 frequency-only, 用 confidence-gated** | shanraisshan 6 weeks 实证 (6.1% correction rate, HIGH 几乎不触发) |

**判定**: 用 confidence-gated (HIGH≥0.7 才 auto-deploy)。rich-audit 5-tool fan-out 跑出来的 insights 自动进 §I internalize = MEDIUM 档 (因为单次跑 < 5 资源时 confidence 低)。

### C3: Learning 文件粒度 (60 行 vs 80 行 vs 无硬限)

| 立场 | 来源 |
|------|------|
| 60 行 | Agent Engineer Master |
| 80 行 | mindstudio fallback |
| 无硬限 | annexiao (rule < memory < skill < agent cost-aware) |

**判定**: 不设硬限, 走 cost-aware routing (rule 5 行 / memory 25 行 / skill 不限 / agent 看实际)。rationale: 硬限会导致 false-positive 删 evidence。

---

## 缺失 / 待补 (rich-audit §I.4 self-evolution 下一步)

### M1: Confidence-Gated Evolution (HIGH ≥0.7 auto-deploy)

**现状**: rich-audit §I internalize 是 MEDIUM 档（直接 update ADR + SKILL.md），没 confidence scoring。

**补法**: 加 §I.1 step 1.5 confidence gate:
- HIGH: 5-tool fan-out ≥4 源共识 + Anthropic 官方支持 → auto-deploy
- MEDIUM: 3-4 源共识 → internalize to references/ (不进 SKILL.md changelog)
- LOW: <3 源 → log only

### M2: Capture-vs-Judgment 分离

**现状**: rich-audit §I 把 capture (5-tool fan-out) 和 judgment (internalize) 混在一起跑。

**补法**: 拆 2 阶段:
- **Phase 1 Capture**: 5-tool fan-out → dump to `~/.claude/knowledge/insights/{date}-v{n}.md` (queue, 不进 changelog)
- **Phase 2 Judgment**: `/evolve` trigger → 读 queue → confidence-gated → internalize

### M3: Cost-aware routing (rule < memory < skill < agent)

**现状**: rich-audit insights 直接进 ADR (cost 重) + SKILL.md changelog (cost 重)。

**补法**: 加 §I.2 cost-aware routing:
- 1 行 fact → MEMORY.md §X (cost 最低, 永远 load)
- 5-10 行 rule → CLAUDE.local.md §X (cost 中, load via SessionStart hook)
- >10 行 protocol → references/process-section-X.md (cost 重, load on demand)
- 跨多文件 / framework config → ADR-XXXX (cost 最重, 永久 load)

### M4: Refinement loop 内置 (Karpathy)

**现状**: rich-audit 跑完 → report → done，没 refinement loop（无 re-run / 自检 / grade 自己输出）。

**补法**: 加 §I.3 refinement loop:
- 跑完 report 后自动跑 `memory-bench` 50 题验证 (skill 是否仍 recall 100%)
- 若 recall < 100% → auto-rollback (跟 shanraisshan HIGH-confidence 失败 auto-rollback 一致)
- 若 recall ≥ 100% → keep, log to MEMORY.md

---

## 4 源 + Anthropic 官方摘要表

| 来源 | 类型 | 核心 1 句 | rich-audit 借鉴 |
|------|------|-----------|-----------------|
| **Anthropic 官方 best-practices** | 官方 | SKILL.md <500 行 + 3-level progressive disclosure + description 含 when-to-use | ✅ 已对齐 |
| **shanraisshan 68 skills 6 weeks** | 实战 | Confidence-gated evolution (HIGH≥0.7 auto-deploy) + 6.1% correction rate | ⚠️ 待加 (M1) |
| **annexiao/claude-code-self-evolution** | 开源 | Capture-vs-judgment + 4 gates + cost-aware routing | ⚠️ 待加 (M2 + M3) |
| **Agent Engineer Master (AEM)** | 教程 | Output contract + 5 anti-triggers + checkpoint self-grade | ✅ 部分对齐 (§H acceptance protocol) |
| **mindstudio fallback** | 教程 | Learnings.md 4 phases (read first + write last + confidence) | ⚠️ 待加 (M1 confidence) |
| **Karpathy DailyTopAI** | 教程 | 4 principles + refinement loop 内置 | ⚠️ 待加 (M4) |
| **zenn N=1 alignment** | 实战 | Hook + conversation log mining → UserPromptSubmit 自动触发 | ❌ out of scope (v2.6.32 暂不实现) |
| **AutoSkill + XSKILL 论文** | 学术 | 双循环架构 + 协同进化 (静态 Skill → 自我进化 Skill) | ⚠️ future (v3.0) |
| **Peter Yang (eval + memory)** | 教程 | evals.md pass/fail + memory.md 单独 keep lessons | ⚠️ 待加 (M4 refinement loop) |
| **MiniMax 中文社区 2026 趋势** | 中文 | Skill 2026 = 自我升级 + Dreaming + Outcomes 4-agent pipeline + bump.sh | ⚠️ future (v3.0) |

---

## internalize 决策 (rich-audit §I.1 step 3)

✅ **v2.6.32 必 internalize (HIGH confidence, 4 源 + Anthropic 官方共识)**:
1. SKILL.md <500 行硬限 + 3-level progressive disclosure (Anthropic 官方) → 已有 ✅
2. `description` 含 5 anti-trigger examples (Anthropic 官方) → 待加 (current: 6 trigger words, 0 anti-triggers)
3. Confidence-Gated Evolution (shanraisshan) → §I.1 加 step 1.5
4. Capture-vs-Judgment 分离 (annexiao) → §I.2 加 cost-aware routing
5. Refinement loop (Karpathy + Peter Yang) → §I.3 加 memory-bench auto-verify

⚠️ **v2.6.33+ 待 internalize (MEDIUM)**:
- output contract 5 anti-triggers → AEM quality protocol (already have §H acceptance)
- Cost-aware routing 4-level (rule < memory < skill < agent) → §I.2 partial

❌ **future (LOW confidence / out of scope)**:
- N=1 alignment hook mining (zenn) → 太重, 需重写 hook 体系
- AutoSkill + XSKILL 双循环 → 学术 prototype, production not ready
- dream / outcomes / 4-agent pipeline → v3.0 远期