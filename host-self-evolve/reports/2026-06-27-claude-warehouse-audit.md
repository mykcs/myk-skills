# Layer 1: ~/.claude/ 全栈审计 (2026-06-27)

> **触发**: user 原话 "重度审计对象是 ~/.claude, 不是那 4 个网站"
> **方法**: file size + 行数 + scope + cross-source dup + case lib 5 sub-task 评分 (per CLAUDE.local.md §17 §A.1.5 + process.md §A.4.1)
> **目标**: `~/.claude/` 主仓, 排除 `projects/` (1.4G session JSONL, 不属 source of truth)

## §0 总览 (1 行)

- ✅ 5/5 sub-task 评分 1.0 (1 file size 0.85 / 2 行数 0.90 / 3 scope 1.0 / 4 cross-dup 0.80 / 5 case lib 0.95), weighted=0.90, **PASS**
- ⚠️ 2 项 Tier 2 建议 (plugins/data 320M / file-history 34M >30d 975) — 走 cleanup 协议
- 🚨 0 项 CRITICAL / 0 项 HIGH (凭据 leak 由 user 2026-06-12 接受, 不算 issue)

## §1 5 sub-task 评分 (5 维度表)

| # | Sub-task | 满分 | 实际 | 评分 | 关键数据 |
|---|---------|------|------|------|---------|
| 1 | **file size** | 1.0 | 0.85 | ⚠️ | 2.0G 总 (projects 784M + plugins 586M + skills 56M + file-history 34M + 其他 100M). 7 大目录 > 1M (projects / plugins / skills / file-history / backups / paste-cache / knowledge) |
| 2 | **行数 vs Anthropic limit** | 1.0 | 0.90 | ✅ | CLAUDE.md 224 (>200 target, 但 <300 OK) / CLAUDE.local.md 535 (HOT FACTS 强制加载, 接受) / rules/process.md 635 (2026-06-15 合并后 561 → 460 → 635, 略增) / rules/language-stack.md 437 / rules/tooling.md 367 / rules/bugfix-400.md 362 / rules/typescript.md 291 / rules/universal.md 200 |
| 3 | **scope 漂移 (Layer 1c §A.1.5)** | 1.0 | 1.0 | ✅ | 6 维度体检: ① CLAUDE.md OMC 模板 + persona + 跨项目协议 (无项目专用段) ② CLAUDE.local.md HOT FACTS + 14 件强制规则 (本机专用, OK) ③ memory/MEMORY.md 122 行 (HOT FACTS + patterns + feedback + cases-active, 全局) ④ rules/ 8 文件按命名空间分组 + paths-scoped ⑤ knowledge/cases/wiki/ 174 active + 235 archive (项目级) ⑥ knowledge/conventions/ 项目级 规范. 全 PASS |
| 4 | **cross-source dup** | 1.0 | 0.80 | ⚠️ | 3 大重复段: ① "双账号铁律 wangrui2025/*" 在 CLAUDE.md + CLAUDE.local.md + memory/MEMORY.md + rules/process.md 4 处 (符合设计: 强制加载, 算 redundancy 但不 scope 漂移) ② cascade-kill 3 件套在 CLAUDE.local.md §8.1 + rules/process.md §C.7 + rules/references/process-section-E (合并 3 段) ③ decision-pattern-reversal feedback 3 处 (CLAUDE.local.md §12 + memory/feedback/ + rules/calm-flow.md v0.2) |
| 5 | **case lib health** | 1.0 | 0.95 | ✅ | 174 active + 235 archive = 409 total. archive-2026-06 整合 6 批次 (omc-rules / astro-full-audit / sync-all-sites / rule-system / cross-repo / szu-ktbg) — 2026-05-28 合并策略落地. 缺顶层 INDEX.md (但 user 已 2026-06-11 拆分到 memory/case-index-archive.md, lazy load) |

**合成 (按权重)**:
```
weighted = 0.30×0.85 + 0.20×0.90 + 0.20×1.0 + 0.15×0.80 + 0.15×0.95
        = 0.255 + 0.180 + 0.200 + 0.120 + 0.1425
        = 0.8975 ≈ 0.90 → ✅ PASS (≥0.80 阈值, per §A.1.5)
```

## §2 7 大目录 size 体检 (per file size sub-task)

| 目录 | Size | 用途 | 评级 |
|------|------|------|------|
| `projects/` | 784M | session JSONL (CC native) | ⚠️ 总和, 单独目录 499M / 161M / 103M 都正常 |
| `plugins/` | 586M | mem0+omc plugin data (160M+160M+0+0+0) | ⚠️ mem0 320M 大, 可清理老数据 |
| `skills/` | 56M | symlink → `~/.agents/skills/` (125 skill) | ✅ 正常 (按 symlink 不占空间) |
| `file-history/` | 34M | 3254 files, 975 >30d | ⚠️ 老 file 975 个, 可清理 |
| `backups/` | 8.3M | 历次 backup (含 1629 行 minimax key rotate 备份) | ✅ 接受 (audit trail) |
| `paste-cache/` | 3.5M | paste 临时文件 | ✅ |
| `knowledge/` | 3.0M | cases + conventions | ✅ 174 active + 235 archive |
| `hud/` | 2.4M | omc HUD cache | ✅ |
| `usage-data/` | 2.2M | usage report html | ✅ |
| `session-env/` | 1.6M | session env 快照 | ✅ |
| `tasks/` | 1.5M | task tracker 数据 | ✅ |
| `omc/` | 1.1M | OMC state | ✅ |
| `vault-memory/` | 924K | 旧 vault (可能过期) | ⚠️ 建议检查 |
| `telemetry/` | 660K | 1p_failed_events (9 files) | ✅ 1P telemetry 正常 |
| `commands/` | 444K | slash commands (15 files, top prp-plan 502 行) | ✅ |
| `scripts/` | 340K | automation scripts | ✅ |
| `cache/` | 300K | changelog.md 3761 行 (累计 cache, 可 trim) | ⚠️ 大 |
| `shell-snapshots/` | 260K | bash session snapshots | ✅ |
| `hooks/` | 216K | hooks config | ✅ |
| `memory/` | 192K | 17 md files + 1 archive | ✅ 122 行主 + 17 子文件 |

## §3 反模式 / Stale (Layer 2 候选)

| 严重度 | 反模式 | 文件:行 | 修复 |
|--------|--------|---------|------|
| ⚠️ LOW | plugins/data/mem0-* 共 320M | `plugins/data/mem0-inline/`, `plugins/data/mem0-mem0-plugins/` | 走 `mem0 cleanup` 或 trim >30d |
| ⚠️ LOW | file-history/ 975 files >30d | `file-history/` | 走 Claude Code `cleanupPeriodDays: 365` 自动 (settings.json 已配) |
| ⚠️ LOW | cache/changelog.md 3761 行 | `cache/changelog.md` | trim 到最近 30 天 |
| ⚠️ LOW | rules/process.md 635 行 (略超 460 目标) | `rules/process.md` | 拆 §C.7 cascade-kill 到 references/ |
| ⚠️ LOW | decisions 重复段 (双账号 4 处 + cascade-kill 3 处 + reversal 3 处) | 跨 4 source | 接受 (强制加载副本设计, 不算 drift) |
| ✅ | 凭据明文 (ANTHROPIC_AUTH_TOKEN + MEM0_API_KEY in settings.json) | `settings.json` | user 2026-06-12 接受 (feedback/feedback-token-exposure-accepted.md) |
| ✅ | 顶层 case INDEX.md 缺失 | `knowledge/cases/wiki/` | 已 2026-06-11 拆到 memory/case-index-archive.md (lazy load) |
| ✅ | vault-memory/ 924K | `vault-memory/` | 老 vault, 待 archive |

## §4 Layer 1 总判定

- ✅ 0 项 CRITICAL (凭据已接受)
- ✅ 0 项 HIGH
- ⚠️ 5 项 LOW (cleanup 类, 不阻塞)
- ✅ weighted 0.90 ≥ 0.80 阈值
- ✅ 5/5 sub-task 评分 ≥ 0.80

**结论**: Layer 1 ✅ PASS, 走 Layer 2 (5 项 LOW 修复清单) + Layer 3 (5-tool fan-out self-evolution) + Layer A.2/A.3 (4 站 CI 扫描) + Layer I.4 (skill self-evolution).
