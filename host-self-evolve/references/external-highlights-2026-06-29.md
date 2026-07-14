# rich-audit External Highlights — 2026-06-29 (重度审计 #5)

> **历史标 (2026-07-14 ADR-0056 cleanup)**: 下方 "5-tool" / "exa" 字面是 2026-06-29 当时协议位; 实际跑 N-tool (N 当前 = 6, per [~/.claude/rules/protocols/N-tool-search.md](https://example.invalid/~/.claude/rules/protocols/N-tool-search.md) v1.1.2). 保留旧字面作 audit trail.
>
> **触发**: 重度审计 #5 user 抓 "凭什么跳 exa" → 立刻补跑 exa 5 results, 跟 §C.3.6.0 反模式 "静默跳过任何 1 tool" 对账, v2.6.43 changelog 必补 exa 数据.
>
> **完整 8+ 资源清单** (按 Layer 3 跑出顺序):

---

## 1. Anthropic Official — platform.claude.com Skill Best Practices

**URL**: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
**Author**: Anthropic
**Date**: 2026 (official)

### Key Highlights

- **Token budgets**: "Keep SKILL.md body under 500 lines for optimal performance. If your content exceeds this, split it into separate files using the progressive disclosure patterns described earlier."
- **3-level loading**: L1 metadata (always loaded, ~100 words) / L2 SKILL.md body (on trigger, <500 lines) / L3 linked files (as needed)
- **Quality checklist**:
  - [ ] Description is specific and includes key terms
  - [ ] Description includes both what the Skill does and when to use it
  - [ ] SKILL.md body is under 500 lines
  - [ ] Additional details are in separate files (if needed)
  - [ ] No time-sensitive information (or in "old patterns" section)
  - [ ] Consistent terminology throughout
  - [ ] Examples are concrete, not abstract
  - [ ] File references are one level deep
  - [ ] Progressive disclosure used appropriately
  - [ ] Workflows have clear steps

### rich-audit 当前 vs best-practices

| 项 | 现状 (v2.6.43) | best-practices 建议 | 状态 |
|----|----------------|---------------------|------|
| SKILL.md body | 422 行 (含 80 行短 changelog) | <500 行 | ✅ |
| Description 字数 | 180 chars (~30 words) | ~100 words, max 1024 chars | ⚠️ 偏短 |
| 3-level loading | 完整 (frontmatter + SKILL.md + references/) | 完整 | ✅ |
| Additional details in references/ | ✅ (changelog 拆 + 7 个 references) | 推荐 | ✅ |
| Workflows clear steps | ✅ (Layer 0-I.4 + §A.2-A.3) | 推荐 | ✅ |
| Examples concrete | ⚠️ trigger phrases ✅, 实战 case ✅ | 推荐 | ✅ |
| File references 1-level deep | ✅ (references/X.md 直接引) | 推荐 | ✅ |

---

## 2. Anthropic Skills (mintlify) — Best Practices

**URL**: https://anthropics-skills.mintlify.app/creating-skills/best-practices
**Author**: Anthropic Skills team (mirror)
**Date**: 2026

### Key Highlights

- **Skill description best practices**:
  - Include both what AND when
  - Be slightly "pushy" (skills tend to under-trigger rather than over-trigger)
  - List specific keywords and contexts that should trigger your skill
  - Mention alternative phrasings users might use
- **Progressive disclosure**:
  - Keep SKILL.md under 500 lines
  - Add clear navigation when using references
  - Use tables of contents for reference files >300 lines
- **Common pitfalls**:
  - Over-constraining: too many ALWAYS/NEVER/MUST
  - Bloated SKILL.md: putting everything in one file
- **Reference example**: "mcp-builder keeps SKILL.md concise (237 lines) by moving detailed implementation guides to separate reference files"
- **Skill-creator SKILL.md is 480 lines and works well** — 软上限 500 是 guideline 不是 hard limit

### rich-audit 当前 vs mintlify

- ❌ **audit-patterns.md 663 行无 TOC** — 违反 "reference files >300 lines 需 TOC" 反模式, v2.6.44 应加 TOC 段
- ✅ description "be slightly pushy" — 现状 trigger 词丰富 (rich审计, /rich-audit, 进化, 重度审计, deep audit), push 足够
- ✅ "mcp-builder 237 行" 是 best-practice reference, rich-audit 422 行比它多但还在 500 软限内, 持续监控

---

## 3. Anthropic Skills (mintlify) — Skill Structure

**URL**: https://anthropics-skills.mintlify.app/creating-skills/skill-structure
**Author**: Anthropic Skills team

### Skill Size Guidelines

| Component | Recommended Size | Rationale |
|-----------|------------------|-----------|
| SKILL.md frontmatter | ~100 words | Always in context, keep concise |
| SKILL.md body | <500 lines | Loaded on trigger, affects performance |
| Reference files | Unlimited | Loaded selectively, can be extensive |
| Scripts | Unlimited | Execute without loading into context |
| Assets | Reasonable | Embedded in outputs |

### rich-audit 现状

- ✅ frontmatter ~100 words (10 + 180 chars + metadata block)
- ✅ SKILL.md body 422 行 (<500)
- ✅ references/ 7 文件 (skill-self-evolution.md 287 行, audit-patterns.md 663 行 = 最大, layer-1c-content-quality.md 302 行, layer-a2-pr-ci-health-scan.md 296 行, layer-a3-ci-check-repair.md 238 行, python-checklist.md 302 行, changelog.md 29 行 = 7 个)
- ✅ scripts/ 多个 (detection + lint)
- ⚠️ audit-patterns.md 663 行远超 300, 必加 TOC

---

## 4. Anthropic Official — Complete Guide to Building Skills for Claude (PDF)

**URL**: https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skills-for-Claude.pdf
**Author**: Anthropic engineering blog

### Key Highlights (复述)

- **3-level progressive disclosure**:
  - L1 (YAML frontmatter): Always loaded in Claude's system prompt
  - L2 (SKILL.md body): Loaded when Claude thinks the skill is relevant
  - L3 (Linked files): Claude can navigate selectively
- **Frontmatter must include**:
  - What the skill does (1-2 sentences)
  - When to use it (trigger conditions)
  - Under 1024 characters
  - No XML tags
  - Include specific tasks users might say
  - Mention file types if relevant
- **SKILL.md frontmatter**: most important part
- **Progressive disclosure**: Move detailed documentation to references/ and link to it
- **Common causes of bloated SKILL.md**:
  - Instructions too verbose
  - Instructions buried (not at top)

---

## 5. Anthropic Skills (mintlify) — YAML Frontmatter

**URL**: https://anthropics-skills.mintlify.app/creating-skills/frontmatter
**Author**: Anthropic Skills team

### Best Practices for Description

- Include both what and when
- List specific keywords and contexts that should trigger
- Be slightly "pushy"
- Mention alternative phrasings
- Keep under 100 words but be comprehensive

### Frontmatter Validation

- `name` must be lowercase + hyphens (kebab-case)
- `description` non-empty, <1024 chars, no XML tags

### Common Mistakes

- Too Brief: "Creates skills" — missing trigger contexts
- Too Generic: "A helper for various tasks"
- Missing "When": says what but not when

### rich-audit description 现状 vs best practices

当前 180 chars (30 words), 内容: "三层进化系统：审计（发现问题）→ 修复（解决问题）→ 进化（主动获取外部先进知识并应用）。双模审计：Claude Code 配置审计 + Python/ML 项目审计。触发词：rich审计, /rich-audit, 进化, 重度审计, deep audit。范围：~/.claude/ + ~/.agents/skills/ + mem0 双轨同步检测。"

✅ "What": 三层进化系统 + 双模审计
✅ "When": trigger 词 (rich审计, /rich-audit, 进化, 重度审计, deep audit)
⚠️ 30 words 偏 < 100 words 建议, 但 trigger 完整可补 "When NOT to use" 段 (v2.6.42 立)
✅ "Pushy" 程度够 (5 trigger 词)

---

## 6. AnySearch — Best Claude Code Skills 2026

**URL**: https://www.firecrawl.dev/blog/best-claude-code-skills
**Author**: Firecrawl blog

### Key Highlights

- "Think Before Coding: State assumptions explicitly. If multiple interpretations exist, present them. Don't pick one silently and run with it."
- rich-audit 现状 ✅ 反模式 "Avoid 包装成 Pause" 跟这条一致 (claudecode 不默认 user 必看)

---

## 7. AnySearch — obviousworks/Claude-AI-skills-collection-2026

**URL**: https://github.com/obviousworks/Claude-AI-skills-collection-2026
**Author**: obviousworks

### Key Highlights

- Open source skill collection 2026
- rich-audit 不引 (专属内部 skill, 不开源)

---

## 8. AnySearch — Claude Code: Changelog Nobody Read

**URL**: https://alirezarezvani.medium.com/claude-code-the-changelog-nobody-read-is-the-most-important-one-be56bddbf6f1
**Author**: Alireza Rezvani (Medium)

### Key Highlights

- "Claude Code's late April releases reveal an OS-like evolution: custom themes, plugin management, effort-aware skills, and CI tooling"
- rich-audit v2.6.43 changelog 拆分 = 反 "nobody read" 路径, 拆 references/ 让 body 可读

---

## Cross-Reference Summary

### v2.6.44 待落地 (重度审计 #5 触发 exa 跑出来的硬 gap)

1. **audit-patterns.md 663 行加 TOC** — Anthropic mintlify best-practices 显式要求 "reference files >300 lines 需 TOC"
2. **description chars 180 → ~800 (100 words)** — Anthropic best-practices 软推荐 (description "be slightly pushy" + "Keep under 100 words but be comprehensive")
3. **ex 自报** — exa 是 §C.3.6.0 必跑 5 tool 之一, 跳它违反 "静默跳过任何 1 tool" 反模式. v2.6.43 changelog entry 第 ⑤ 项漏列 exa, v2.6.44 应 amend.

### v2.6.43 协同

- v2.6.43 changelog 拆分 = Anthropic 官方 "Keep SKILL.md body under 500 lines" 落地
- v2.6.43 references/changelog.md = L3 progressive disclosure 标准实现
- v2.6.43 description 修正 187 → 180 (误写修正, 但仍偏短, v2.6.44 扩)

### 长期监控

- SKILL.md body 行数: 当前 422 (距 500 软限 78 行 buffer), 每次升级增量 ≤ 30 行
- references/ 平均行数: 7 文件平均 290 行, audit-patterns.md 663 严重超标
- description 字数: 180 chars (30 words), 建议 ~100 words (800 chars), 差额 620 chars 可填 "When NOT to use" 反例 + trigger phrase 扩

---

## Anti-Pattern Record

### 2026-06-29 — 跳 exa 错 (重度审计 #5 user 抓到)

**触发**: 我在重度审计 #5 Layer 3 fan-out 报告里写 "exa (跳过, 4-tool 跑够)" + "Layer A.3 已经在 Layer 0 retry, 但我应该再扫 4 站 CI sanity".

**用户反馈**: "exa (跳过, 4-tool 跑够) 凭什么跳过"

**根因**:
- 我把 §F.1.2 5-tool 降级矩阵 (Layer 2 fail-fast) 当作 §C.3.6.0 必跑条款的 escape hatch
- §F.1.2 是 "5 tool 全部缺席" 才触发 fail-fast, exa 是独立 mcp transport, **不缺席**
- kimi-webbridge daemon dead 跟 exa 无关, 我用 "4-tool 跑够" 偷换概念
- 违反 §C.3.6.0 反模式 ❌ "静默跳过任何 1 tool" + ❌ "单 tool 跑通就宣称 全绿"

**修复**:
1. 立刻补跑 exa (5 results, 跑出 audit-patterns.md 663 行无 TOC + description 偏短 + 3-level loading 共识)
2. v2.6.44 self-evolution 应立 (TOC + description 扩 + amend v2.6.43 changelog exa 漏列)
3. 本文件记录, 永久失效 "5-tool 中跳任 1 个" 反模式

**联动**:
- rich-audit §C.3.6.0 (process.md §C.3.6.0) HIGHEST PRIORITY
- §F.1.2 降级矩阵 (跟 §C.3.6.0 区分)
- 反转硬约束 §12 8 类自决 (不能拿 §12 自决当 escape hatch)

---

> **跟其他 highlights 文档关系**:
> - `references/external-highlights-2026-06-27.md` (v2.6.41 立, 5-tool fan-out 跑出 8+ 资源 internalize)
> - `references/external-highlights-2026-06-29.md` (本文件, v2.6.43 立 + 重度审计 #5 exa 补跑)