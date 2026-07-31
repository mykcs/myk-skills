---
name: teacher-report-paper-set-diff
description: |
  teacher-report Paper-Set Diff 硬规则 (H1, 2026-06-10 写入). 任何 teacher-report wiki 推 draft / migrate 任务 push 前必须做 paper-set 双向 diff. 来源 case: CASE-V039-DRAFT-WIKI-MISMATCH-20260610.
---

# Paper-Set Diff 硬规则 (H1, teacher-report)

> **触发场景**: 任何 teacher-report wiki 推 draft / migrate 任务, **push 前必须做 paper-set 双向 diff**。
>
> **来源 case**: `~/.claude/knowledge/cases/wiki/CASE-V039-DRAFT-WIKI-MISMATCH-20260610.md`
> **背景**: 2026-06-10 6 teacher wikis 共有 44 papers, draft 36 papers, **仅 5 papers match (11%)**。两套 papers 来自不同检索 query 时段, 几乎不重叠。直接 push 36 cards 实际**无法命中任何 placeholder**, 浪费 1.5h 工作 + 暴露 2 个 migrate.py bug。

## 触发条件 (任一即触发)

- 推 `/tmp/v039-cards-{teacher}.md` 等 draft 到 wiki
- 跑 `migrate.py --all` (会列 wikis 并 transform placeholder)
- 跨 session 推 v0.3.x 论文条目到 v0.4.0 doc
- 任何"我有 N 个 draft papers 要推"的批量操作

## 强制流程 (push 前必跑)

```bash
# Step 1: 列 wiki 实际 paper titles (注意用 24-char obj_token, 非 19-char prefix)
python3 -c "
import re, json
import subprocess
for tok in WIKI_TOKENS:  # 从 wiki +node-list --parent-node-token=P49mwGQU0iEh9CkXbCTcC418nPb 取
    out = subprocess.check_output(['lark-cli','docs','+fetch','--api-version=v2','--doc',tok,'--detail','with-ids','--format','json'])
    titles = re.findall(r'<p[^>]*><b>([^<]+)</b></p>', out.decode())
    print(f'{tok}: {titles}')
" > /tmp/wiki-titles.json

# Step 2: 列 draft paper titles
grep "^###" /tmp/v039-cards-*.md > /tmp/draft-titles.txt

# Step 3: 双向 diff (normalize: lowercase, strip punctuation, strip subtitle)
python3 -c "
import re
def norm(s): return re.sub(r'[:—].*$','',re.sub(r'[^\w\s]','',s.lower())).strip()
wiki = load_wiki()  # parse /tmp/wiki-titles.json
draft = load_draft()  # parse /tmp/draft-titles.txt
matched = set(wiki) & set(draft)
print(f'wiki={len(wiki)} draft={len(draft)} matched={len(matched)}')
print(f'wiki-only ({len(set(wiki)-set(draft))}):', sorted(set(wiki)-set(draft))[:5], '...')
print(f'draft-only ({len(set(draft)-set(wiki))}):', sorted(set(draft)-set(wiki))[:5], '...')
"
```

## 判定矩阵 (claudecode 强制 STOP 条件)

| 场景 | matched 比例 | 决策 |
|------|-------------|------|
| matched == wiki == draft | 100% | ✅ 直接 push |
| matched == draft (draft ⊂ wiki) | draft 100% | ⚠️ wiki 有 extras, 先**清理 wiki 残留 placeholder** 或**重抓 wiki-only** |
| matched == wiki (wiki ⊂ draft) | wiki 100% | ⚠️ draft 有 extras, **加 wiki slot** 或**保留 draft 备用** |
| matched < 50% max(wiki, draft) | **STOP** | 🛑 **整套 query 错了**, 回去对齐检索策略 (该 case 的真实状态) |
| matched == 0 | **STOP** | 🛑 推上去无意义, 重新对齐 source-of-truth |

## 同期暴露的 2 个 migrate.py bug (已修)

| Bug | 现象 | 修复 |
|-----|------|------|
| **Bug 1**: `transform_authors` regex 只匹配 `Last, First（中文）` 格式 | wiki 现有 v0.3.9 cards 用 `First Last（中文）` 无逗号格式, transform 永远 0 替换 | rewrite regex 改 split-on-comma 方案, 同时支持两种格式 (commit 推送中) |
| **Bug 2**: `transform_authors` 不处理 placeholder cards | placeholder 卡片是空 `<p>作者：</p>` + `<p>[完整作者列表待补]</p>`, 不是 author 行 | scope 推迟 (wiki 已 v0.4.0, placeholder 不存在) |
