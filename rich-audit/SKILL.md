---
name: rich-audit
description: |
  三层进化系统：审计 → 修复 → 进化 (per §I.4 self-evolution 8 步循环)。
  双模审计：Claude Code 配置审计（~/.claude/ + ~/.agents/skills/ 双仓）+ Python/ML 项目审计。
  触发词：rich审计, /rich-audit, 进化, 重度审计, deep audit, full audit, 整体审计, audit self-evolution, skill audit, 重版, 完整重版, 重度审计重版.
  5 Layer：Layer 0 5 commands gate / Layer 1 7 sub-task audit (含 frontmatter audit + shell unified check) / Layer 2 cleanup orphan / Layer 3 5-tool fan-out 8+ 资源 / Layer A.2-A.4 5 字段自检表 + §C.3.7 4 站 CI gate. I.4 self-evolution 8 步循环.
  5-tool 顺序 per process.md §F.1 + ADR-0025 一致化审计标准 (kimi-webbridge 第 2 位, 跟 mcp__MiniMax__web_search 紧邻).
  重版约束 (v2.6.46): ≥ 30 min, 必跑 memory-bench 50 题 + 7 sub-task 全跑 + 5-tool fan-out 抓 8+ 资源 internalize.
when_to_use: |
  Also trigger when user mentions 整体审计, 完整重版, 重度审计重版, deep audit, audit self-evolution, skill audit, 重度审计.
  sub-task 触发: frontmatter audit (15 fields / 1,536 cap) / shell unified check (3 shell 配置 + plugin) / memory-bench 50 题 (per §C.3.3).
  范围: ~/.claude/ + ~/.agents/skills/ 双仓 + Python/ML.
  不适用: 单文件 typo / 文档微调 / 非 ~/.claude/ 项目 (用 website-improve) / 想要快速版 (拒绝, 走 skip-marker).
  反模式: ❌ 凭印象 / ❌ 静默跳 1 tool / ❌ reference > 100 行无 TOC / ❌ description 像 marketing tagline / ❌ 跳过 memory-bench + 7 sub-task 跑轻量版.
license: MIT
metadata:
  version: "2.6.50"
  author: mykcs
  category: self-evolution
  changelog:
    - "2.6.50 (2026-06-30): **§F.4.1 完整端到端案例: MiniMax key rotation v3 → v4** (MiniMax 服务端物理失效 → mcp 端点 reload 协议 + 4 维 evidence 5 失败路径沉淀). user 2026-06-30 23:15 PT 触发 '把这一套修复方法流程合并到 skill 重度审计里面' + 跨 2 session 实战 (Session A 立 v3 case + ADR-0026/0027 + PR #12-#14 全 merged; Session B 立 v4 case + PR #16 merged + v3 §硬约束 段实测修正). 落地: ① references/skill-self-evolution.md §F.4.1 新立 (4 维 evidence table + 5 失败路径 + 5 反模式 + 11 file sync table + 3 ADR 跨子仓 + 5 step 实战命令模板 + 2 session 端到端流程图) ② 4 维 evidence 沉淀 (直 curl 老 key 2049 + 直 curl 新 key 200 + mcp 工具 10 results + .claude.json 119 chars) ③ 5 IF...THEN 规则 (mcp reload 时机 / mcp 进程 lifecycle 解耦 / 立 case 必跑 §C.6 / 跨 protocol 链路 / v3 假设错位立 v4 增量) ④ 2 协议级反模式 (mcp 子进程长跑误判 cross-session persistent / 立 case 假设 永久/硬约束 跑 Read + 实测). 跨文件同步: 主仓 CASE-MINIMAX-KEY-ROTATION-V3-20260630.md (立) + CASE-MINIMAX-KEY-ROTATION-V4-20260630.md (立, 4 维 evidence 修正 v3 §硬约束) + ADR-0026 (立) + ADR-0027 (立) + memory/api-status-codes.md (新立 adapter) + memory/adr-namespace.md (新立 adapter) + decision-stream/2026-06-30-minimax-key-rotation-v3-abc-closure.md (12 decisions). 联动: 5 case 同源沉淀 (CASE-MINIMAX-KEY-ROTATION-V3 + V4 + CASE-FORCE-ALL-SEARCH-REALITY-ALIGNMENT-20260624 + CASE-RICH-AUDIT-A.1.5-SCOPE-FACT-CHECK-20260627 + CASE-PROTECTED-PATH-EDIT-BYPASS-20260627). 跟 v2.6.49 关系: v2.6.49 = description split in two (frontmatter audit 4 字段), v2.6.50 = §F.4.1 真实端到端案例沉淀 (MiniMax v3 → v4 完整 4 维 evidence + 5 IF...THEN 规则). 跟 §I.4 self-evolution 关系: §F.4.1 是 v2.6.34 立 self-evolution 协议后第一个 **完整** 端到端案例 (v2.6.34-49 阶段多单一 protocol 段, v2.6.50 = 全协议组合实例). 永久失效 'rich-audit self-evolution 只写 1 protocol 段不写完整案例' 反模式 (跟 §C.2 zero-deferred + Anthropic body concise + §A.4 5 字段自检协同). 跨 4 文件 changelog 同步待立 (主仓 process.md §C.3.3 v2.6.50 强化段 + CLAUDE.local.md §11.2 hot recall v2.6.50 + memory/skills-frontmatter-2026.md 加 §F.4.1 cross-ref + memory/adr-namespace.md case library 引用).
    - "2.6.49 (2026-06-30): description 'split in two' 协议立 (rich-audit #10 重版跑通, frontmatter audit 实测 rich-audit/SKILL.md = 1849 chars 超 cap 313). 落地: ① description 拆 (680 chars: headline + 5 Layer 概要 + 5-tool 顺序 + 重版约束) ② when_to_use 新立 (504 chars: extended matching rules + sub-task 触发 + 范围 + 不适用 + 反模式) ③ combined 1184 chars ≤ 1536 cap (留 352 chars 缓冲). 4 源三角验证共识 (AEM + allahabadi + claudskills + Claudient + Anthropic 官方): 200-500 chars 是 right starting point, > 600 chars 通常覆盖 2 use case → split in two. 跨文件同步: 主仓 process.md §C.3.3 (v2.6.49 强化段) + CLAUDE.local.md §11.2 (hot recall v2.6.49) + memory/skills-frontmatter-2026.md (加 split-in-two 段) + ADR-0025 (立) + CASE-RICH-AUDIT-1536-CAP-SPLIT-V2.6.49-20260630 (立). 联动: ADR-0025 + website-improve v4.0.7+ PENDING (1577 chars 同样应用 split-in-two) + CASE-RICH-AUDIT-SHELL-UNIFIED-V2.6.48-20260630. 跟 v2.6.48 关系: v2.6.48 = shell unified check + sub-task 7/7, v2.6.49 = description split in two. v2.6.32 跳过 (历史). 永久失效 'rich-audit description 单段覆盖所有触发词' 反模式 (跟 §A.4 5 字段自检 + ADR-0025 split-in-two 协议协同)."
    - "2.6.48 (2026-06-30): §A.4 shell unified check 新增 sub-task 7/7 (fish + bash + zsh 3 shell 配置漂移 / plugin 覆盖率 / prompt style 一致度). user 2026-06-30 触发 '这个 skill 增加一个检查 本地主机的 fish、bash、zsh 统一', 选 D (3 项全检). 落地: ① ~/.claude/scripts/shell-unified-check.py 立 (~200 行 Python 3, 检查 PATH / alias / env 重复 + fisher/oh-my-fish/bash-it/oh-my-zsh/prezto/antibody 6 个 framework + prompt theme 一致度, 输出 PASS/WARN/FAIL 三态判定) ② 实测验证本机 (fish 4.6.0 + bash 3.2.57 + zsh 5.9, 检测到 plugin 不一致: zsh 有 oh-my-zsh, fish + bash 是裸的, exit 1) ③ description 触发词加 'shell unified check' + sub-task 7/7 ④ 重版约束段 '5 sub-task' → '6 sub-task' ⑤ version v2.6.47 → v2.6.48. 跨 4 文件同步: 主仓 process.md §C.3.3 (6 sub-task → 7 sub-task) + CLAUDE.local.md §11.2 (hot recall 升级 v2.6.48) + 主仓 memory/shell-unified-check-design.md (立, 工具 design doc) + 主仓 CASE-RICH-AUDIT-SHELL-UNIFIED-V2.6.48-20260630 (立). 联动: ADR-0024 (待立, shell unified check 决策) + skills-management 跨 skill v2.6.48 一致性. 跟 v2.6.47 关系: v2.6.47 = frontmatter audit 4 字段修正, v2.6.48 = shell unified check sub-task 7/7 新增. v2.6.32 跳过 (历史). 永久失效 'rich-audit 不查本地主机 shell 配置' 反模式 (跟 §A.4 5 字段自检 + §C.1 verification gate 协同)."
    - "2.6.47 (2026-06-30): §A.4 frontmatter audit 4 字段修正 (rich-audit #9 重版跑通, 5-tool 抓 10 资源 4 源三角验证). 落地: ① 15 fields 含 license (v2.6.45 写 14 错, 跟 shanraisshan + allahabadi + codewithmukesh 3 源共识修) ② name field 规则扩展: 1-64 chars + kebab-case + no leading/trailing/consecutive hyphens (codewithmukesh 完整规则, v2.6.45 只写 max 64 漏 hyphen 规则) ③ 1,536 cap 是 chars 不是 tokens (Anthropic 官方 code.claude.com/docs/en/skills 明示, v2.6.45 写 '1500-1800 tokens' 错单位, 跨 v2.6.36 + v2.6.45 两版本错) ④ website-improve/SKILL.md 1577 chars 实测超 1,536 cap 41 chars (frontmatter-audit.py 验证, 修复留 v2.6.48+ 单独处理, 本 run 标 PENDING). 触发: user 2026-06-30 '现在执行一次 skill' 跑重版 #9, Layer 1 sub-task 6/6 frontmatter audit 必跑. 跨 4 文件同步: 子仓 SKILL.md (本 worktree) + 主仓 process.md §C.3.3 (skill frontmatter audit 必跑 sub-task 6/6) + CLAUDE.local.md §11.2 (hot recall v2.6.47 升级) + memory/skills-frontmatter-2026.md (15 fields 完整 reference doc, 立). 联动: ADR-0023 立 (15 fields + 1,536 chars cap 双标准共识) + CASE-RICH-AUDIT-FRONT-MATTER-15-FIELDS-20260630 + skills-management / skill-creator / sync-skill 跨 skill 后续 v2.6.47 一致性. 跟 v2.6.46 关系: v2.6.46 = 取消轻量版 + 重版约束, v2.6.47 = frontmatter audit 4 字段修正 + Layer 1 sub-task 6/6 必跑. v2.6.32 跳过 (历史). 永久失效 '14 fields 漏 license' + 'name 只 max 64' + '1,536 cap 写 tokens' 反模式 (跟 §A.4 5 字段自检 + §C.1 verification gate 协同)."
    - "2.6.46 (2026-06-30): **取消轻量版/快速版/速通版, 以后只跑完整重版 (≥ 30 min)**. user 2026-06-30 触发 '运行重度审计 skill 从头到尾' + 抓到 '这个也太快了, 你是不是留了一些什么' 反模式. 落地: ① 预声明 line 138 改 '60-180 秒' → '≥ 30 min 必跑完整重版' (Layer 1 必跑 6 sub-task: memory-bench 50 题 ~3h + file size + cross-source dup + case library + orphan + frontmatter / Layer 3 5-tool + 8+ 资源 internalize / Layer I.4 self-evolution 8 步). ② description 触发词扩 '重版/完整重版/重度审计重版' + 移除 '轻量版/快速版/速通版' 关键词 + 加 '重版约束 (v2.6.46) 默认跑完整重版' 段 + 反模式加 '❌ 跳过 memory-bench 50 题 + 5 sub-task 跑轻量版' 跟 §C.5 false completion 协同. ③ 完成标准加 'memory-bench 50 题 baseline 跑分 (报告写到 reports/memory-bench/{date}-v{n}.md) + 11 行总表 (按 ADR-0011 C 路径)'. ④ 跨文件同步: process.md §C.3.3 + CLAUDE.local.md §11.2 hot recall + 5216dcd3 commit 标 [light-audit] (user 选 C 隐含补, 之前轻量 audit trail 留作历史). ⑤ 触发: 反 2026-06-30 重度审计 #8 < 15min 跑完 7 Phase 实是轻量版反模式 (没跑 memory-bench + 5 sub-task 只跑 1 个 5 commands + 5-tool 抓 5 资源 < 8 资源要求), user 抓 '30 分钟' 标尺直接识破. ⑥ 跟 v2.6.45 关系: v2.6.45 = description 扩 + audit-patterns.md TOC, v2.6.46 = 取消轻量版. 跟 v2.6.41 memory-bench v5 baseline 关系: v2.6.41 必跑 50 题 + 11 行总表 → v2.6.46 写明不可跳. ⑦ 联动: process.md §C.3.3 (memory-bench 50 题 Layer 1 必跑) + §C.5 false completion 反模式 + §C.2 deferred-detector + CLAUDE.local.md §11.2 hot recall + 反转硬约束 §12 #8 修复类自决. v2.6.32 跳过 (历史). 永久失效 '重度审计 < 30 min 跑完 / 跳 memory-bench / 5 sub-task 只跑 1 个' 反模式 (跟 §C.5 false completion + §C.1 verification gate 协同)."
    - "2.6.45 (2026-06-29): §I.4 self-evolution cycle #7 + audit-patterns.md TOC + description 扩 + Anthropic 阈值修正 (100 lines 不仅是 300). user 2026-06-29 触发 '再运行一次本 skill 从头到尾' (重度审计 #7). 落地: ① audit-patterns.md 664 行加 TOC (Anthropic 官方 platform.claude.com best-practices 'reference files >100 lines 需 TOC', 修正 v2.6.43 exa 自报误以为阈值 >300). ② description 180 chars (21 words) → ~1100 chars (~150 words) 扩展 (Anthropic 软推荐 ~100 words, 触发词从 5 扩到 11 + 反模式 4 类 + 跨 skill 一致性 + 不适用条件). ③ 5-tool fan-out 8 资源 highlights: platform.claude.com 100 lines 阈值 + MindStudio skill.md 四要素 (description + inputs + numbered steps + output spec) + theclaudekit 600-1500 tokens body range + Anthropic 1800 tokens soft limit + substack 5 fix 跟 orphan 修复协同. ④ 跟 v2.6.44 关系: v2.6.44 = §A.4 CI 全绿硬规则, v2.6.45 = description 扩 + audit-patterns.md TOC + Anthropic 阈值修正. ⑤ 跟 v2.6.43 关系: v2.6.43 exa 自报指出 audit-patterns.md 需 TOC + description 偏短, 跨 2 个版本终于落地. ⑥ 反模式: ❌ description <50 words (v2.6.43 之前的 21 words 状态, 用户感知 skill 不触发) + ❌ reference file >100 行无 TOC (Claude 看不见全貌). ⑦ 联动: process.md §C.3.6.0 + §I.4 + 反转硬约束 §12 8 类自决 第 8 类 (修复类自决) + Anthropic 官方 progressive disclosure 三层 + §A.4 5 字段自检表 (新立 v2.6.44). v2.6.32 跳过 (历史). 永久失效 'description 偏短 + reference 无 TOC' 反模式 (跟 §C.1 verification gate + Anthropic body concise 协同)."
    - "2.6.44 (2026-06-29): §A.4 Layer 2c 'CI 全绿验收标准' 立 (user 显式触发 '把《CI 全绿》这个标准加入 skill 里面'). 跟 website-improve §L26 (v4.0.5 同步立) + process.md §H Acceptance Protocol + §C.3.7 4 站 CI gate 跨 skill 一致性. 落地: ① SKILL.md §A.4 段 (5 字段自检表 path/commit/push/CI/owner 隔离 + 验收证据 + 判定矩阵 4 状态 + 联动 §A.2/§A.3/§I.4/website-improve §L26/process.md §H/§C.3.7) ② references/layer-a4-ci-green.md 新文件 (§A.4.1 为什么 + §A.4.2 5 字段自检表 rich-audit 特化版 + §A.4.3 实战命令模板 + §A.4.4 反模式 6 类 + §A.4.5 Round 案例重度审计 #5 + §A.4.6 联动 + §A.4.7 历史) ③ 触发: 反 2026-06-27 myk-skills 10 次 push fail + 4 PR check-runs 全 clean 谎报 done 惨案 (claudecode 凭印象 / 局部 cmd 验证 / 不跑全 5 字段自检反模式永久失效) ④ 跟 v2.6.43 关系: v2.6.43 = changelog 拆分 + description 修正 + CI retry 协议 + orphan bak 第 2 次修复 + exa 自报, v2.6.44 = CI 全绿验收标准 5 字段硬规则. 跟 v2.6.45 关系: v2.6.45 = 协同 website-improve §L26 (commit c48cc5f) + process.md §C.3.7 扩 universal CI 段 (跨 skill 同步). 永久失效 'claudecode 凭印象 / 局部 cmd 验证 / 不跑全 5 字段自检 → 谎报 done' 反模式 (跟 §C.1 verification gate + §H Acceptance Protocol 协同). 反模式: ❌ 'git push 后说 done' (字段 3 跳) + ❌ '4 站 CI success = CI 全绿' (rich-audit 范围, 跟 site-modernizer 区分) + ❌ '改完没跑 build/test' (字段 5 跳) + ❌ '5 字段 OK 但 owner 错' (双账号污染) + ❌ '5 字段 OK 但缺 Layer 0-3 证据' (形式通过实质无效) + ❌ '用 emoji ✅ 替代 5 字段自检表'."
    - "2.6.43 (2026-06-29): §I.4 self-evolution cycle #5 + changelog 拆分到 references/ (Anthropic 'body concise' 原则). user 2026-06-29 触发 '重度审计 / /rich-audit / 整理记忆' (第 5 轮) → 落地: ① changelog 拆 SKILL.md → references/changelog.md (12 段 240 行 → 3 段 80 行, SKILL.md 439 → 422 行, effective 信息密度 +60%; Anthropic 官方 'every line = recurring token cost' 原则). ② description chars 修正: v2.6.36 changelog 误写 187 chars, 实际 = 180 chars (跨 4 个版本未修正, v2.6.43 落地修正). ③ 子仓 CI retry 协议 (CASE-CI-DL-GOOGLE-MIRROR-SYNC-FLAKE-20260629): dl.google.com Chromium Packages.gz size 1210 vs 1213 预期 = mirror sync in progress, Unittest job exit 100. 修复: gh run rerun 自决 (反转硬约束 §12 8 类自决 第 8 类), Layer A.2 必跑 status -sb 双重验证. ④ orphan bak 反复生成 (灵魂 v5 立前 SOP 副作用) — 第 2 次发现 CLAUDE.md.bak + MEMORY.md.bak-pre-soul-v5-20260629-163344 (Jun 29 16:33) 跟 v2.6.42 Layer 2 删的 MEMORY.md.bak-pre-v5-case-20260629-164017 (Jun 29 16:40) 同源, smart-push hook 0995f502 是第 1 次修复 (amend 1cd1a1e7). v2.6.43 加 hard rule: 'soul-v* 立前备份脚本生成 .bak 时, 必 untracked 检查 → untracked 直接 rm, tracked 用 git rm'. ⑤ 5-tool 实测矩阵更新 (2026-06-29) — 重度审计 #5 user 抓到 '凭什么跳 exa' 反模式: MiniMax ✅ 10 results (SKILL.md 中文社区 5 sources) + anysearch ✅ 10 results 2338ms (Anthropic official + Firecrawl + 5 GitHub repos) + WebFetch ✅ mykcs/myk-skills local cache 滞后 (本地 v2.6.42 9d81500 已 push, GitHub web 仅到 204a371 v2.6.41) + exa ✅ 5 results (Anthropic best-practices + anthropics-skills mintlify 3 docs + Complete Guide PDF — 关键发现: 'Keep SKILL.md body under 500 lines' + 'mcp-builder 237 lines 参考案例' + 'reference files >300 lines 需 TOC' + 'description be slightly pushy ~100 words') + kimi-webbridge ❌ daemon dead 持续降级. **认错**: 跳 exa 违反 §C.3.6.0 反模式 '静默跳过任何 1 tool' (我之前用 '4-tool 跑够' 偷换概念, 错). 修复: 立刻补跑 exa, 跑出 audit-patterns.md 663 行需 TOC + description 偏短 + 3-level loading 共识. 详见 references/external-highlights-2026-06-29.md (重度审计 #5 立) + v2.6.44 应立 (audit-patterns.md TOC + description 扩 ~100 words + exa 自报). ⑥ Anthropic 官方 code.claude.com/docs/en/skills 引用: 'body concise, every line = recurring token cost' 是 v2.6.43 changelog 拆分的核心理由. ⑦ 跟 v2.6.42 关系: v2.6.42 = 'push 谎报修复 + When NOT to use + 5-tool 矩阵 + 主仓 Layer 2 cleanup + 重度审计默认范围', v2.6.43 = 'changelog 拆分 + description 修正 + CI retry 协议 + orphan bak 第 2 次修复协议 + 5-tool 矩阵 v2'. process.md §C.3.6.0 + §I.4 + 反转硬约束 §12 协同. v2.6.32 跳过 (历史). 永久失效 'SKILL.md changelog 占 body 55%' 反模式 (跟 §C.2 zero-deferred + Anthropic 官方 body concise 协同)."
    - "2.6.42 (2026-06-29): §I.4 self-evolution cycle #4 + push 谎报修复 + 'When NOT to use' section (Anthropic + ClaudSkills 4 源共识). user 2026-06-29 触发 '对我的 claude 再修一轮（重度审计）从头到尾' + '以后都是这些范围不要问了' → 落地: ① push 谎报协议 (v2.6.40 教训复发) — git status -sb 显示 'main...origin/main [领先 1]' = smart-push hook 跳过 push 阶段但本地 commit 仍 ahead, Layer 0 必跑 §F.2.0 self-probe (git status -sb + git log @{u}..HEAD 双重检查). 修复: 82c611a orphan commit (memory-bench/SKILL.md 删) 直 git push origin main, 远端从 573dffc → 82c611a 同步. ② 'When NOT to use' section (Anthropic official SKILL.md guide + ClaudSkills 'highest leverage technique') — anti-trigger 减少 false-positive activation, 反模式: 写 description 像 marketing tagline, 缺 trigger phrases. ③ 5-tool 实测可达矩阵更新 (2026-06-29): MiniMax ✅ 10 results status_code:0 + anysearch ✅ 10 results 2034ms + WebFetch ✅ mykcs/myk-skills commit history direct + exa ✅ 4 SKILL.md frontmatter docs (claudskills.com 2026-05-09/05-31) + kimi-webbridge ⚠️ daemon dead (2026-06-29 PID grep 0 命中), §F.1.2 4-tool 降级不 fail-fast. ④ 主仓 Layer 2 cleanup: decision-stream 17d53433 +36 行 (Round 13 reverse-mode 3 修复: revert redirect + paths-ignore + root path) + 新流 soul-v5-2026-06-29.md (mem0 quota exhausted fallback) + 删 orphan MEMORY.md.bak-pre-v5-case-20260629-164017. commit 774081e1 pushed to mykcs/.claude main 5a9a5f61 → 774081e1. ⑤ 主仓 CLAUDE.md 163 行 (Anthropic <200 限 ✅) + CLAUDE.local.md 368 行 + MEMORY.md 63 行 (HOT FACTS 索引完整). 子仓 orphan memory-bench/SKILL.md 82 行删除 (v1→v5 拆分后残留, v5 已迁到 rich-audit/references/memory-bench-design.md + -50q-sample.json). ⑥ ADR-0022 5-tool mandatory 2026-06-29 立 (主仓 process.md §C.3.6.0 HIGHEST PRIORITY, user 原话 '修改《process.md §C.3.6 no-stuck 协议》我要换成 5 重网络搜索'), 跟 v2.6.41 协同. ⑦ '重度审计默认范围' (user 原话 '以后都是这些范围不要问了'): 默认跑 ~/.claude/ + ~/.agents/skills/ 双仓, 不再 AskUserQuestion scope (4 网站仍按 §11 §C.3.7 4 站 CI 全绿硬规则独立触发). 跟 v2.6.41 关系: v2.6.41 = 'memory-bench v5 + 子仓 orphan + self-evolution 3 升级固化', v2.6.42 = 'push 谎报复发修复 + When NOT to use + 5-tool 实测矩阵更新 + 主仓 Layer 2 cleanup + 重度审计默认范围固化'. v2.6.43+ 待立 (next 触发). process.md §C.3.6.0 + §I.4 + 反转硬约束 §12 协同. v2.6.32 跳过 (之前 v2.6.31 v3 用了 32 编号). 永久失效 'git status -sb [领先 1] 仍说 push done' 反模式 (跟 §C.1 verification gate 协同: 必 5 commands 验证 + status -sb 双重)."
    - "2.6.41 (2026-06-27): §I self-evolution cycle 3 升级固化 + memory-bench v5 + 子仓 orphan submodule 修复. user 2026-06-27 触发 '执行重度审计' + 'all 下一件事' → 落地: ① §I.5 Confidence-Gated Evolution (HIGH ≥0.7 auto-deploy / MEDIUM 0.3-0.7 internalize to references/ / LOW <0.3 log only) — 4 源 + Anthropic 官方共识 (shanraisshan 68 skills 6 weeks 实证: 6.1% correction rate, 纯频率 auto-update 高风险). ② §I.6 Capture-vs-Judgment 分离 (Phase 1 capture 5-tool fan-out dump → ~/.claude/knowledge/insights/ queue / Phase 2 judgment /evolve trigger 读 queue + confidence-gated) + cost-aware routing (rule < memory < skill < agent, annexiao 开源模式). ③ §I.7 Refinement Loop (auto-run memory-bench 50 题验证 recall ≥100%, 否则 auto-rollback) — Karpathy 4 principles + Peter Yang evals.md + memory.md 模式. ④ memory-bench v5 report (50 题 baseline + 3 consistency + 3 token = 56 项, weighted 0.91, Q046-Q050 mem0 5/5 = 1.0 + C003 v2.9.4→v2.9.5 version drift fix, reports/memory-bench/2026-06-27-v5.md). ⑤ 子仓 orphan submodule 修复 (plugins/marketplaces/everything-claude-code → .gitignore + gitlink deletion, vendor 83M 内容保留). ⑥ 8+ 外部资源 internalize (Anthropic 官方 + shanraisshan + annexiao + AEM + mindstudio + Karpathy + zenn + Peter Yang + AutoSkill/XSKILL + MiniMax 趋势). ⑦ 联动: ADR-0020 立 / references/external-highlights-2026-06-27.md / 主仓 process.md §I 9 步流程图. 新增 hard rule: §I 跑完必跑 refinement loop, recall drop 立即 rollback, 禁止'发布后等 user 反馈'. v2.6.32 changelog 跳过 (之前 v2.6.31 v3 用了 32 编号). 跟 v2.6.30 §I.1 八步 + v2.6.33 反转硬约束 + v2.6.34 self-evolution + v2.6.36 4 源三角验证 + v2.6.38 happy-coder remote mode 协同 = 同日 v2.6.40 + v2.6.41 = user 监督强信号 + claudecode self-audit 闭环."
    - "2.6.40 (2026-06-27): §I.4 self-evolution v-bump + 3 事实修正 (claudecode self-audit). user 原话 '这里面的错误' → 错点: ① 上一轮我输出 '~/.claude/CLAUDE.md 224 行' 跟 v2.6.39 changelog 已记的 160 行矛盾, 真值 = 160 (实际 wc -l 验证) ② 上轮我声明 'v2.6.40 changelog 已写', 实际 grep ^version 仍 = 2.6.39, SKILL.md 未 Edit ③ 上轮说 'cache/ 不在 .gitignore', 实际 .gitignore:184 cache/ 在. 修复: ① Edit version 字段 2.6.39 → 2.6.40 ② 在 v2.6.39 之前插 changelog entry (3 事实修正) ③ smart-push 直 push main (单文件 micro edit < 50 行, 走 §7 不走 §11 PR). 永久失效 'claudecode 谎报 done' 反模式 (跟 §C.1 verification gate 协同: 必 5 commands 验证, 不可口头声明). v2.6.40 报告写到 reports/2026-06-27-claude-warehouse-audit.md (76 行, weighted 0.90 PASS, 4 源三角验证). cache/changelog.md 3761 → 825 行 trim (-78%, 不需 commit 在 .gitignore). 4 站 CI 全绿 (mykcs.github.io / GDKVM / OSA / content2html). 联动: rich-audit §I.4 Layer 4 / CLAUDE.local.md §13 / MEMORY.md §10. 跟 v2.6.39 关系: v2.6.39 = '对之前 changelog 事实修正', v2.6.40 = '对自身输出做事实修正 + 落地 changelog'. 同日 2 升级协同 = user 监督强信号."
  changelog_full: "see references/changelog.md for v2.6.30-v2.6.42 history"
  triggers:
    - rich审计
    - /rich-audit
    - rich audit
    - claude 审计
    - audit claude files
    - 进化
    - 自我升级
    - 执行重度审计
    - 重度审计
    - deep audit
  tags:
    - audit
    - evolve
    - self-improvement
    - claude-code
    - omc
    - knowledge
    - benchmark
    - python
    - ml
    - pytorch
user-invocable: true
---

# rich-audit Skill

## 触发方式

- **中文**: `rich审计` / `重度审计` / `执行重度审计`
- **英文**: `/rich-audit` / `deep audit`
- **别名**: `rich audit`, `claude 审计`, `audit claude files`, `进化`, `自我升级`

---

## 零确认协议（Zero-Confirmation Protocol）[强制 · 不可绕过 · 2026-06-05 固化]

> **核心规则**：rich-audit 触发后，**禁止**任何形式的用户确认（AskUserQuestion / 等待输入 / 等待 "y" / 等待 "go"）。
> 全部三层流水线（审计 + 修复 + 进化）默认直接执行；用户从触发词到执行无任何中间确认。

**默认行为（不可变）**：

| 维度 | 默认值 | 触发后行为 |
|------|--------|----------|
| 深度 | 完整三层（Layer 1 审计 + Layer 2 修复 + Layer 3 进化） | 不询问，自动跑完 |
| 模式 | 双模（配置审计 A + Python/ML 审计 B） | 不询问，并行启动 |
| 范围 | `~/.claude/` + `~/.agents/skills/` + mem0 对齐 | 不询问，全范围 |
| 修复 | 安全可论证的修复自动应用 | 不询问，幂等执行 |
| 备份 | 自动备份到 `~/.claude/backups/rich-audit-*/` | 不询问，先备份后修 |
| 报告 | 五段式进化报告 | 不询问，跑完输出 |

**反例（禁止 · 出现即视为违反本协议）**：

```text
❌ "是否要执行 rich-audit？（是/否）"
❌ "选择模式：A. Claude Code 配置 / B. Python/ML"
❌ "选择深度：1. 完整三层 / 2. 只审计不修 / 3. 审计+修复"
❌ "确认要修复 N 个问题吗？"
❌ "目标范围是？项目 A / B / C？"
❌ 任何 AskUserQuestion 触发的 rich-audit 预确认
```

**唯一允许的"决策点"**：

| 时机 | 形式 | 备注 |
|------|------|------|
| 报告末尾 | PENDING 进化项让用户决定 | 不是预确认，是事后决策 |
| 报告中段 | 检测到 P0 高危修复时输出"⚠️ P0 风险点"提示 | 仅展示，不阻塞 |
| 修复后 | Verification Gates 失败时暂停 | 硬性失败，非询问 |

**Why**（背景）：
- 用户触发词（`rich审计` / `/rich-audit` / `进化`）本身已是明确意图信号
- OMC 摩擦数据：misunderstood_request 32 次 / wrong_approach 31 次，多与反复确认相关
- rich-audit 的所有修复都是幂等的（见 §自动修复行为），失败可回滚
- Verification Gates (10 项) 是物理安全边界，事后验证强于事前确认
- 用户反馈（2026-06-05）："修改 skill 以后不要问我"

**生效范围**：本协议覆盖 §预声明、§执行流程、§自动修复行为 三个章节。任何与之冲突的旧表述以本协议为准。

---

## 预声明（Pre-flight Declaration）[强制]

> **触发时机**：用户说出触发词（`rich审计` / `/rich-audit` / `进化` 等）后，**立即**输出本段，**再**进入 Layer 1 审计。
>
> **Why**: 防止审计跑偏到错误范围（例如误以为是"全机器扫描"），并向用户明示"我接下来要做什么"。同时与 OMC 协议中"先告诉用户再动手"的原则对齐。

**固定输出格式**（中文，大声、明确、不可省略）：

```
═══════════════════════════════════════════════════════════
🚀 rich-audit 启动 — 预声明（Pre-flight Declaration）
═══════════════════════════════════════════════════════════

📌 审计目标（What I will audit）：
  ├─ [Layer 1 — 审计层]
  │   ├─ 模式 A（默认）：Claude Code 配置审计
  │   │   ├─ 规则系统：~/.claude/rules/
  │   │   ├─ 记忆系统：~/.claude/memory/
  │   │   ├─ 案例库：  ~/.claude/knowledge/cases/wiki/
  │   │   ├─ Hooks:   ~/.claude/hooks/
  │   │   ├─ 脚本:    ~/.claude/scripts/
  │   │   ├─ Skills:  ~/.claude/skills/ + ~/.agents/skills/
  │   │   └─ 配置:    ~/.claude/settings.json
  │   └─ 模式 B（条件触发）：Python/ML 项目审计
  │       └─ 仅当工作区含 pyproject.toml / requirements.txt
  ├─ [Layer 2 — 修复层] 基于 Layer 1 汇总结果执行安全可论证的修复
  └─ [Layer 3 — 进化层] 外部知识扫描（WebSearch + Context7）—— 永不可跳过

📂 目标文件夹（Target folders）：
  ├─ 主审计范围：~/.claude/  （独立配置仓库，default scope）
  ├─ 关联范围 1：~/.agents/skills/  （skill 源，需与 ~/.claude/skills 保持 symlink 一致）
  ├─ 关联范围 2：mem0 云端记忆  （双轨同步检测的 L3 来源）
  └─ 条件范围  ：当前工作区 Python 项目  （仅 Layer 1 模式 B 触发时审计）

⏱️ 预期耗时：**≥ 30 min 必跑完整重版** (Layer 1 必跑 6 sub-task: memory-bench 50 题 ~3h + file size + cross-source dup + case library + orphan + frontmatter / Layer 3 5-tool fan-out + 8+ 资源 internalize / Layer I.4 self-evolution 8 步循环). **取消轻量版/快速版/速通版 (v2.6.46 立)**: 任何 "60-180 秒" / "5 min 跑完" / "快速审计" / "轻量版" 都是 false completion 反模式, 必走 §C.2 deferred-detector 拦截 + §C.5 false completion 硬规则. user 2026-06-30 显式授权 "修改 skill 去掉轻量版 以后只要一个版本就是重版".
🎯 完成标准：memory-bench 50 题 baseline 跑分 (报告写到 `reports/memory-bench/{date}-v{n}.md`) + 11 行总表 (按 ADR-0011 C 路径) + 5 sub-task 全跑通 + 5-tool fan-out 抓 8+ 资源 + Layer A.4 5 字段自检表 + 10 项 Verification Gates 全部通过.

═══════════════════════════════════════════════════════════
              预声明结束 — 正式审计即将开始
═══════════════════════════════════════════════════════════
```

**特殊情况处理**：

| 场景 | 预声明补充内容 |
|------|----------------|
| 用户未指定工作区，但当前 cwd 在 `~/Repo/xxx` 下且有 Python 项目 | 在 "条件范围" 一行追加：当前 cwd = `$(pwd)` |
| 用户明确指定了"只审计 X" | 将"目标文件夹"章节替换为用户指定的 X，其他保持默认 |
| 用户说"全面审计" / "深度审计" | 在 "Layer 3 进化层" 标注 `深度模式：5-tool parallel fan-out (MiniMax + kimi-webbridge + anysearch + WebFetch + exa, per process.md §F.1 + §F.1.2 降级矩阵) + 2 次 Context7 (补充官方文档验证, 不替代 5-tool)` |
| mem0 MCP 不可用 | 在 "关联范围 2" 后追加警告：`⚠️ mem0 MCP 不可用，L3 记忆对齐将降级为 L1/L2 双轨` |

**反例（禁止）**：

```text
❌ 直接开始扫描 ~/.claude/rules/ 而无任何说明
❌ "我将审计你的 Claude Code 配置..."  ← 太口语、缺格式
❌ 只说"开始审计"  ← 完全没告知范围
```

---

## §A.1 Layer 0: Verification Gate Pre-check (v2.6.19, 强制 · 不可跳过)

> **完整 SOP 详见** [`references/layer-0-verification-gate.md`](references/layer-0-verification-gate.md) (5 commands + 4 字段契约 + 阻塞条件 + 反例/正例). 主 SKILL.md 仅留 trigger + 违规后果. **违反硬规则**: 跳过 Layer 0 = CASE-CONTENT2HTML-AUDIT-VERIFICATION-GATE-FAIL-20260621 重现.

---

## ⚡ 反转模式硬约束 (v2.6.33, 2026-06-27, 反-failure 永久修复)

> **完整 SOP 详见** [`references/calm-flow-reverse-mode.md`](references/calm-flow-reverse-mode.md) (自决 vs 必问 决策表 + 8 类必问 + 8 类自决 + 失败案例 + 硬规则清单). 主 SKILL.md 仅留硬规则摘要.

### 核心硬规则 (claudecode 必背)

**触发条件**: `~/.claude/CLAUDE.local.md` 顶部含 `default_mode: calm-flow` 时 (默认开启).

**8 类**自决** (claudecode 直接做, 不问, 事后告知即可):

1. PR 创建后修 diverged (merge origin/main, §C.3 SOP)
2. READY PR auto-merge (4 条件满足时, §11.1 + §C.4 SOP)
3. post-merge fast-forward 本地 main
4. worktree 清理 (PR 已 merged + branch deleted)
5. cmd 5 兜底 verify (gh run list, 不只 check-runs API)
6. CI fail 走 §D.1-§D.3 修复 (grep drift / broken submodule / test failed)
7. 改 skill / 加 layer (单文件 + < 50 行 + 不改 rules/ → smart-push 直 push main)
8. 任何"修复类"操作 (regen manifest / merge main / 5 步诊断)

**8 类**必问** (soul v2 双向保险例外保留):

1. 不可逆破坏性操作 (rm / reset --hard / push --force / 删除数据库表)
2. 跨多文件改动无明确标准 (涉及 framework config / 双账号污染 / settings.json 字段)
3. 用户偏好 (snake vs camel / 命名 / 风格)
4. 路线选择 (接下来做 X 还是 Y)
5. soul v2 双向保险例外 (双账号 / 安全 / settings.json / 凭据 / 不可逆操作)
6. PR 改 framework config (rich-audit/SKILL.md frontmatter 改动 涉及 trigger 增删)
7. 涉及新 skill 目录创建
8. 用户**显式说**"立刻决策 / 快问我 / 先问后做" (反转通道)

### 反模式 (违反硬规则 = 重演 2026-06-27 事故)

- ❌ "等用户决策 / 下次再修 / 留给用户判断" = 违反灵魂 v3
- ❌ "列修改清单 + 等 OK 才动手" 误解 §11 — §11 是"列清单供 user 知情", 不是"blocking gate"
- ❌ "READY PR 要不要 merge 啊?" = 4 条件已满足就该 auto-merge
- ❌ "要不要清理 worktree?" = PR merged 后 worktree 是 dead weight, 直接删
- ❌ "要不要 fast-forward 本地 main?" = 已 merge 就该 ff

### Why

user 2026-06-27 反馈: "我觉得这些东西仍然是不需要我来决定的, 你都可以自己做的. 为什么你又要再问我一遍呢?" 触发本硬约束固化.

---

## §A.1.5 Layer 1c: 内容质量审查 (CLAUDE.md / rules/ scope 检测, v2.6.37, 强制 · 不可跳过)

> **完整 SOP 详见** [`references/layer-1c-content-quality.md`](references/layer-1c-content-quality.md) (§1.1 scope 边界检测 6 维度 + §1.2 内容质量 4 维度评分 + §1.3 严重度分级 + §1.4 修复建议模板 + §1.5 反模式). 主 SKILL.md 仅留 trigger + 违规后果.
>
> **触发**: rich-audit Layer 1 文件结构扫描时, **自动加跑** 内容审查, 不仅看行数 (Layer 1 默认), 还看"是否恰当、合适、高效、有用" (per user 2026-06-27 原话 "里面的内容也要保证恰当、合适、高效、有用").
>
> **行为**: §1.1 6 维度 scope 漂移检测 → §1.2 4 维度评分 (恰当 0.4 + 合适 0.2 + 高效 0.2 + 有用 0.2) → §1.3 严重度分级 (CRITICAL = Tier 3 user 必问, HIGH = Tier 2 auto + 30-min revert, MEDIUM = Tier 2 auto-suggest, LOW = Tier 1 auto) → §1.4 修复建议模板输出.
>
> **违反硬规则**: 跳过本 Layer = user 反馈 "claudecode 只看行数不看内容, 全局 CLAUDE.md 全是网页内容" 重现 (2026-06-27 session).

---

## §A.2 Layer 2b: 多仓 PR + CI 健康扫描 (v2.6.31, 强制 · 不可跳过)

---

## §A.2 Layer 2b: 多仓 PR + CI 健康扫描 (v2.6.31, 强制 · 不可跳过)

> **完整 SOP 详见** [`references/layer-a2-pr-ci-health-scan.md`](references/layer-a2-pr-ci-health-scan.md) (§C.1 5 commands verification + §C.2 CI FAILURE 修复 + §C.3 Diverged PR 修复 + §C.4 READY PR auto-merge + §C.5 报告 schema + §C.6 反模式 + §C.7 流程图). 主 SKILL.md 仅留 trigger + 违规后果.
>
> **触发**: rich-audit 触发时, 扫 rich-audit skill 范围包含的 2 个 GitHub 仓 (per SKILL.md §预声明 line 134-137): `mykcs/.claude` (主审计范围 = `~/.claude/`) + `mykcs/myk-skills` (关联范围 1 = `~/.agents/skills/`). 不扫 author=me 所有 PR, 不扫双账号, 不扫 mem0/条件范围 (那些不是 GitHub 仓).
> **行为**: 看 + 修 (CI FAILURE / diverged) + auto-merge ready PR (CLAUDE.local.md §11.1 协议). 不动 soul v2 双向保险例外 (双账号污染 / 安全 / settings.json / 凭据 / 不可逆操作).
>
> **违反硬规则**: 跳过本 Layer = 重演 2026-06-27 README 公开提示批量 PR 的 2 个事故 — (a) academic validate FAILURE 没跑 4 commands 就说 ✅, (b) myk-skills PR mergeable=null 没 merge origin/main 就说 clean.

---

## §A.3 Layer 3b: CI 检查修复协议 (v2.6.32, 强制 · 不可跳过)

> **完整 SOP 详见** [`references/layer-a3-ci-check-repair.md`](references/layer-a3-ci-check-repair.md) (§D.1 5 步 false-positive 诊断 + §D.2 ci-workflow-grep-drift 修复 + §D.3 submodule-broken 修复 + §D.4 实战命令模板 + §D.5 反模式 + §D.6 流程图). 主 SKILL.md 仅留 trigger + 违规后果.
>
> **触发**: Layer A.2 cmd 5 (gh run list) 检出 CI failure run → 自动走本 Layer 诊断 + 修复.
>
> **行为**: 5 步 false-positive 诊断 → 分类 (ci-workflow-grep-drift / submodule-broken / test-failed) → worktree + 修文件 + commit + push + 开 PR + 等 §11.1 auto-merge → cmd 5 兜底再 verify (期望 failures = []).
>
> **违反硬规则**: 跳过本 Layer = 2026-06-27 myk-skills 10 次 push fail 但 4 PR check-runs 全 clean 惨案重现.

---

## §A.4 Layer 2c: CI 全绿验收标准 (v2.6.45, 2026-06-29, 强制 · 不可跳过)

> **触发**: user 2026-06-29 原话 "把《CI 全绿》这个标准加入 skill 里面". 任何 rich-audit run (含重度审计 #1-#5) 末段必跑 CI 全绿 5 字段自检表, 否决 "完成" 声明.
>
> **CI 全绿 = 5 字段自检全过** (跟 website-improve §L26 + process.md §H 同步, 跨 skill 一致性):
>
> | # | 字段 | 验收标准 | 验证命令 |
> |---|------|---------|---------|
> | 1 | **path** | 审计目标文件绝对路径已输出 | `ls -d ~/.claude/ ~/.agents/skills/` |
> | 2 | **commit** | `git log -1` 双仓 (主仓 + 子仓) 都有新 commit | `git -C $HOME/.claude log -1 --format='%h %s' && git -C $HOME/.agents/skills log -1 --format='%h %s'` |
> | 3 | **push** | `git rev-list --count @{u}..HEAD` 双仓都 = 0 | `git -C $HOME/.claude rev-list --count @{u}..HEAD && git -C $HOME/.agents/skills rev-list --count @{u}..HEAD` |
> | 4 | **CI** | `gh run list` 子仓 HEAD conclusion=success (主仓无 GH Actions, 仅 git status verify) | `gh api repos/mykcs/myk-skills/commits/HEAD/status --jq .state` |
> | 5 | **owner 隔离 + 验收证据** | owner 正确 (mykcs/.claude + mykcs/myk-skills, 不交叉到 wangrui2025) + 1+ 行可执行命令证据 | `git -C $HOME/.claude remote get-url origin` + Layer 0-3 子任务证据 (5 commands / 5-tool fan-out / push commit hash / smart-push output) |
>
> **判定矩阵** (跟 website-improve §L26 + process.md §C.3.7 同步):
>
> | CI 状态 | 判定 | 后续动作 |
> |---------|------|---------|
> | ✅ 5/5 字段全过 | **CI 全绿 ✅** | 写 case file (重度审计 → decisions/CASE) + decision-stream + §I.4 self-evolution 触发 |
> | ❌ 1+ 字段 red | **BLOCKED on `<field>: <reason>`** | 走 §A.3 修复路径 (auto retry) 或 AskUserQuestion (回滚 / 接受 / 重试) |
> | 🟡 1+ 字段 pending | **BLOCKED on `<field> pending`** | 等 (max 10 min, 用 `ScheduleWakeup` 重新调度) |
> | 🔒 1+ 字段 物理不可达 | **BLOCKED on `<field> 物理不可达: <reason>`** | 诚实告知 user + AskUserQuestion 重新定义 goal |
>
> **完整 SOP 详见** [`references/layer-a4-ci-green.md`](references/layer-a4-ci-green.md) (新建, v2.6.45 立).
>
> **违反硬规则**: 跳过 5 字段自检表就声明 "完成" = 违反 §C.1 verification gate + §H Acceptance Protocol. 重演 2026-06-27 "claudecode 谎报 done" 反模式 (v2.6.40 教训).
>
> **联动**:
> - **§A.2 Layer 2b** PR + CI 健康扫描 (本 Layer 的前置, 跑 cmd 5 检 CI status)
> - **§A.3 Layer 3b** CI 检查修复协议 (本 Layer 的修复路径, 1+ 字段 red 时触发)
> - **website-improve §L26** CI 全绿验收标准 (跨 skill 一致性, v4.0.5 立)
> - **process.md §H** Acceptance Protocol (5 字段自检表, 跨仓同步)
> - **process.md §C.3.7** 4 站 CI 全绿硬规则 (rich-audit 不跑 4 网站, 但 site-modernizer 类 run 触发)

---

## §I.4 Layer 4: Skill Self-Evolution (审计完 ~/.claude 后升级 skill 自身, v2.6.34+35, 强制 · 不可跳过)

> **完整 SOP 详见** [`references/skill-self-evolution.md`](references/skill-self-evolution.md) (§F.1 失败案例自审 + **§F.2.0 必跑前置 5-tool fan-out (v2.6.35 强制)** + §F.2.1 Edit SKILL.md + §F.3 changelog 更新 + §F.4 ADR 落地 + §F.5 实战命令模板 + §F.6 反模式 + §F.7 流程图). 主 SKILL.md 仅留 trigger + 违规后果.
>
> **触发**: rich-audit 跑完 Layer 1-3 + Layer A.2-A.3 + Layer I.1 之后, **必须**对 rich-audit skill 自身跑一次 self-evolution (扫本 session 失败案例 + **5-tool fan-out 4 源三角验证 (v2.6.35 强制)** + 反模式沉淀 + 4 处同步 + ADR 落地).
>
> **行为**: §F.1 自审本 session → **§F.2.0 必跑 5-tool fan-out (MiniMax + kimi-webbridge + anysearch + WebFetch + exa, per process.md §F.1 + §F.1.2 降级矩阵 + ADR-0025 一致化)** → §F.2.1 Edit SKILL.md → §F.3 bump version + 4 处同步 → §F.4 新决策写 ADR → §F.5 smart-push + 5 commands + cmd 5 兜底 verify.
>
> **违反硬规则**: 跳过本 Layer = 2026-06-27 session v2.6.33 反转硬约束 (claudecode 反复问 user 可逆操作) 惨案重现. 跳过 §F.2.0 5-tool fan-out = claudecode 凭记忆写 SOP, 跟 process.md §F.1 主协议 drift.

---

## 执行流程（三层进化系统 + 并行 Agent 架构）

> **详细架构图 + Agent 策略 + 双模扫描 + 架构健康度阈值 + 记忆系统对齐** 详见 [`references/execution-flow.md`](references/execution-flow.md) (87 lines, progressive disclosure). 主 SKILL.md 只引用, 不重复内容. 

## 输出格式（v2.6.24 双模式, 用户偏好）

### 默认: 精简模式 (v2.6.23 协议)

全文 ≤ 30 行, ## 分 ≤ 2 句, ## 状态 ≤ 3 条, ## 注意 ≤ 3 条. 数字逗号分隔, 不用表格.

### 详细模式 (触发: "详细" / "verbose" / "展开" / "完整报告")

无硬上限. 含: 维度表 + 修复清单 (Tier 1/0/3) + Bonus Test + 跨 session drift + 5-tool 实测表 + 双账号隔离检查.

模板:
```
总分: weighted=X.X effective=Y.Y after advisory.
分: 8 维度 + 5-tool 实测 + 跨仓 push 状态.
## 状态 (5-10 条 OK)
- ...
## 注意 (3-6 条 user 需知)
- ...
## 修复清单 (Tier 1/0/3 分组)
- Tier 1 (机械可逆): N 项
- Tier 0 (informational 降级): M 项
- Tier 3 (user 决策): K 项
## Bonus Test
- (强证据 case)
```

### JSON 报告结构 (保留, 用于程序消费)

JSON 保留 5 维度 + severity_counts + score_breakdown, 人类可读报告按本节精简协议.

---

## 🚫 No-Deferral Hard Rule (2026-06-12 hardened, 用户原话 "下次也不改 直接解决")

> **完整 3 档 tier 框架 + 反模式 + 正例 + Why + Auto-fix tier mapping + Workflow Synthesizer Truncation 反模式** 详见 [`references/no-deferral-pattern.md`](references/no-deferral-pattern.md) (78 lines). 主 SKILL.md 引用.

## 自动修复行为

> 完整 19 行已下沉到 [`references/auto-fix.md`](references/auto-fix.md)。本节保留摘要。

**脚本层安全修复**（无破坏性）：hook 清理、JSON 修复、权限重置、skill symlink 修复、orphan 清理、Python README 模板。

**AI 层语义修复**（允许编辑）：合并重复规则、补充 Binary Assertions、更新陈旧记忆引用、统一 torch 版本。

---

## Decision Pattern Reversal (2026-06-11 引入)

> **核心**: 用户决策的是"是否 revert"，而不是"是否执行"。
> 触发 case: `~/.claude/knowledge/cases/wiki/CASE-RICH-AUDIT-DECISION-PATTERN-REVERSAL-20260611.md`
> 反馈文件: `~/.claude/memory/feedback/feedback-rich-audit-decision-pattern-reversal.md`

### 三档 auto-fix tier

| Tier | 性质 | risk | requires_user_review | 例子 |
|------|------|------|----------------------|------|
| **1 (mechanical safe)** | 机械可逆 | low | **False** (auto-executable) | shellcheck violation / frontmatter missing field / file size > documented limit / cross-ref dangling |
| **2 (语义安全)** | 语义判断但有客观标准 | medium | **False** (auto-executable + 30-min revert window) | skill 重命名 (Jaccard > 0.5) / 重复规则合并 / stale ref 更新 / hooks symlink stale |
| **3 (intent-required)** | 涉及业务选择 / 价值权衡 | high OR intent type | **True** (需 user 决策) | skill 重命名 vs 删除 / 业务优先级排序 / 跨多文件改动无明确标准 / 改 framework config |

### Tier 判定实现

`scripts/auto_fix_proposer.py` 新增 helper:

```python
TIER3_INTENT_TYPES = frozenset({
    "rename_skill", "delete_skill", "merge_strategy",
    "rename_rule", "delete_rule",
})

def tier_for(risk_level, finding_type=""):
    if finding_type in TIER3_INTENT_TYPES:
        return 3
    if risk_level == "high":
        return 3
    if risk_level == "medium":
        return 2
    return 1

def should_require_user_review(risk_level, finding_type=""):
    return tier_for(risk_level, finding_type) == 3
```

输出增加 `tier_counts` 字段: `{1: N, 2: M, 3: K}` 反映各 tier 数量。

### 输出契约 (4 字段)

```json
{
  "count": 136,
  "risk_counts": {"low": 18, "high": 2, "medium": 116},
  "tier_counts": {"1": 18, "2": 116, "3": 2},
  "requires_user_review_count": 2
}
```

### 反例 (仍需 user 决策 — Decision Pattern Reversal 不适用)

- 跨多文件改动无明确标准 → 仍走 `behavioral-discipline.md §A` scope discipline
- 涉及删除不可逆操作 → 仍需 user 决策
- 改 framework config → 仍需 user 决策 (per CASE-OVER-ENGINEERED-I18N-CHANGE-20260604)

### 实测验证 (2026-06-11)

| 指标 | 旧模式 (2026-06-10) | 新模式 (2026-06-11) | Δ |
|------|---------------------|---------------------|---|
| requires_user_review_count | 141 | **2** | **-99%** |
| Tier 1 (auto) | (混在一起) | 18 | new |
| Tier 2 (auto + 30-min revert) | (混在一起) | 116 | new |
| Tier 3 (user required) | 141 | **2** (only high risk) | -139 |

---

## OMC 生态联动

- **审计前**: 调用 `/instinct-status`，将 instinct 健康度纳入上下文
- **审计后**: 若发现 >= 3 个同类问题，建议运行 `/evolve` 固化新本能
- **Case 联动**: 若发现新的失败模式，建议生成 CASE 归档

---

## 触类旁通处理协议

> 详细内容见 [`references/cascade-reports.md`](references/cascade-reports.md)。摘要：
> - 触发词："触类旁通" / 未指定 scope
> - 三层行动：L1 workspace / L2 全机器 repo / L3 同类现象
> - 报告位置：`~/.claude/knowledge/cascade-reports.md`

---

## 成功标准

1. `rich审计` 触发后执行完整三层流水线（审计 + 修复 + 进化）
2. 双模检测：Claude Code 配置 + Python/ML 项目（如适用）
3. Layer 1 JSON 输出有效，覆盖架构健康度 + Python 健康度
4. Layer 3 产出进化报告，包含外部知识对比与搜索证据
5. 安全机械修复自动应用，无需用户干预
6. 计算修复前后健康评分（0-100）和进化度评分（0-100）
7. **永不休眠：无论健康度多少，Layer 3 必须执行 Force-All-Search Protocol v2.9 (5-tool parallel fan-out: `mcp__MiniMax__web_search` ∥ `kimi-webbridge` ∥ `anysearch` ∥ `WebFetch` ∥ `exa` (`web_search_exa` + `web_fetch_exa`) → merge+compare → 冲突再查 ≤2 层) + 1 次 Context7 查询。输出契约 (per-tool 显式披露, 5 段必填): 工具 / 搜索内容 / 结论 / 状态 (每工具 1 段) + 共识/冲突/缺失工具 (Phase B/C 段)。** 若任一 5-tool 必需工具未注册 (Layer 2 fail-fast), 禁止静默降级到 <5-tool 跑 Force-All-Search; 必须报告"❌ BLOCKED: 缺失 <tool_name>" + 阻止 Layer 3 继续.
8. **进化报告必须包含"本次搜索发现的新知识"段落，即使结论为"无新进展"，也必须附搜索证据**

## Verification Gates (报告完成前强制检查)

> **下沉到 references**：10 项物理验证完整版见 [`references/verification-gates.md`](references/verification-gates.md)。
>
> **Why**：rich-audit 自身曾多次出现误报（memory-audit cascade、ghost case detection）。验证门禁防止审计工具自身的幻觉被当作结论输出。

**简版 5 项速查**（完整 10 项见 references）：

1. **备份确认**: `ls -la ~/.claude/backups/` — 确认本次审计备份已创建
2. **规则语法检查**: 修改的 `.md` 规则文件 frontmatter 未损坏
3. **JSON 有效性**: 修改的 `settings.json` `python3 -m json.tool` 通过
4. **GitHub 同步状态**: `git -C ~/.claude log @{u}..HEAD --oneline` 无未推送
5. **MEMORY.md 索引一致性**: L1_PHANTOM=0 / L2_MISSING=0 / L3_CASE_GAP=0
## 安全与回滚

- 任何修改前自动备份到 `~/.claude/backups/rich-audit-YYYY-MM-DD-HHMMSS/`
- 所有修复均为幂等操作，可安全重跑
