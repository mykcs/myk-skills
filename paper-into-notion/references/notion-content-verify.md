# Notion Content Verify Protocol — 5 类逐项 + 字符级验证

> **SSOT 引用**: paper-into-notion 改 Notion block 后, 走本协议 verify. 跟 `notion-block-layout.md` 协同 (layout 管"怎么写", 本表管"写完怎么查")
> **起源**: weekly-report-phd v1.1 §9 verify 协议 (line 294-449) — 30+ 次 user 反馈累积
> **适用范围**: 任何 Notion 文档 verify (paper 摘要 / 周报 / 调研报告), 跨项目稳定
> **核心原则**: 1 句话 user 反馈可能含多类 bug, 必 1:1 grep 全查, 不只改 1 处

---

## §1 5 类逐项 verify (字符级)

| # | 类 | grep 模式 | 期望命中 | 例 (错误 → 正确) |
|---|---|---|---|---|
| 1 | 数字格式 | `0[。.][0-9]` (中文数字 + 全角点) | 0 | `0。1` → `0.1` |
| 2 | 数字格式 | `\dv0[。.][0-9]` (smart_fix_period 双 v) | 0 | `vv0.1` → `v0.1` |
| 3 | 半角标点 | `(?<!\d)[,;:'"](?!\d)` (半角在中文环境) | 0 | `": "` → `"： "` |
| 4 | 标题用字 | `^#+\s*(一|二|三|四|五|六|七|八|九|十)[、.]` (h1/h2 中文数字) | 0 | `"一、对"` → `"1. 对"` |
| 5 | 内容字面 | 1:1 跟 user 最新原话 diff | 0 字符差 | e.g. `v0.1` 跟 `0.1` 混 |

---

## §2 5 步 verify 流程 (必跑)

### Step 1: 拿当前 Notion 全文

```bash
PAGE_ID="<notion page id>"
TOKEN=$(echo $NOTION_TOKEN)  # 走 ntn CLI 内部获取
ntn api v1/blocks/${PAGE_ID}/children?page_size=100 > /tmp/page_now.json

# 提取纯文本 (按 block 类型递归 rich_text[])
python3 -c "
import json, sys
d = json.load(open('/tmp/page_now.json'))
print('\n'.join(
    ''.join(c.get('plain_text','') for c in r.get(r.get('type'),{}).get('rich_text',[]))
    for r in d['results']
    if r.get('type') in ('paragraph','bulleted_list_item','numbered_list_item',
                         'heading_1','heading_2','heading_3','callout','quote')
))
" > /tmp/page_now.txt
```

### Step 2: 5 类 grep

```bash
echo "=== verify 5 类 ==="
echo "[1] 0[。.][0-9]:"; grep -oE '0[。.][0-9]' /tmp/page_now.txt | head -5
echo "[2] vv0[。.][0-9]:"; grep -oE 'vv0[。.][0-9]' /tmp/page_now.txt | head -5
echo "[3] 半角标点:"; grep -oE '(?<!\d)[,;:"'"'"'](?!\d)' /tmp/page_now.txt | head -5
echo "[4] 标题中文数字:"; grep -oE '^#+\s*(一|二|三|四|五|六|七|八|九|十)[、.]' /tmp/page_now.txt | head -5
```

### Step 3: 1:1 字符级跟原话对比

```bash
# user 最新原话写到 /tmp/page_expected.txt (1:1)
diff /tmp/page_now.txt /tmp/page_expected.txt
# 期望: 无输出 (0 字符差)
```

### Step 4: 列出 4 类荒谬 (Python regex)

```python
import re
text = open('/tmp/page_now.txt').read()
issues = []
for m in re.finditer('0[。.][0-9]', text):
    issues.append(('0[。.]X', m.group(), m.start()))
for m in re.finditer('vv0[。.][0-9]', text):
    issues.append(('vv0[。.]X', m.group(), m.start()))
for m in re.finditer(r'(?<!\d)[,;:\'"](?!\d)', text):
    issues.append(('半角标点', m.group(), m.start()))
for m in re.finditer(r'^#+\s*(一|二|三|四|五|六|七|八|九|十)[、.]', text, re.MULTILINE):
    issues.append(('标题中文数字', m.group(), m.start()))
if issues:
    print(f'荒谬 found: {len(issues)} 处')
    for cat, txt, pos in issues[:20]:  # 最多列 20
        print(f'  [{cat}] {txt!r} at {pos}')
else:
    print('0 荒谬 found ✅')
```

### Step 5: 改完必 verify 0 issues 才 declare done

```bash
# 跑 §2 Step 1-4 + 期望全部 0 命中
# 失败 → 改 → 重跑, 不接受 "差不多完成"
```

---

## §3 5 类 verify 决策表

| grep 命中 | 修复方向 | 注意点 |
|---|---|---|
| `0。1` / `v0。1` | `。` → `.` (全角点 → 半角点) | 保留 0/v 字母位置, 不硬塞 `vv0.1` |
| `vv0.1` | 删 1 个 v (双 v → 单 v) | smart_fix_period 副作用 |
| `: ` 中文环境 | `:` → `：`, `,` → `，` | 数字上下文保留半角 (e.g. `100:200` 不改) |
| `一、xxx` 标题 | `一、` → `1. ` | h1 用阿拉伯数字 + 点, 不用中文数字 |
| `v0.1` vs `0.1` 混用 | 1:1 跟 user 最新原话, 取其一统一 | grep `v?0\.[0-9]+` 找全 |

---

## §4 IF...THEN 规则 (4 类必跑协议)

### §4.1 1 句话 user 反馈 = 1:1 diff 多类 bug

**触发**: user 说 "X 错" / "X 荒谬"

**协议**:
1. **Step 1**: 跑 §2 Step 1-2 全 5 类 grep, **不只改 1 处**
2. **Step 2**: 列出 N 个匹配 (可能 1 句话含 4 类 bug)
3. **Step 3**: 1:1 修复每类, 不批量替换 (避免 `v0.1` 被改成 `0.1` 错位)

**反模式**:
- ❌ 1 句话当 1 个 bug 处理 (可能含多类)
- ❌ 批量 replace 不查上下文 (`v0.1` → `0.1` 会破坏 `vv0.1`)

**例子 (user "0。1 错" → 4 类全找到)**:
```bash
echo "0。1 已跑通, v0。1 推进中" > /tmp/page_now.txt
grep -oE '0[。.][0-9]' /tmp/page_now.txt
# → ["0。1", "0。1"]
# 实际含 2 处: "0。1" + "v0。1" → 改 "0。1" → "0.1" + "v0。1" → "v0.1"
# 1 句话 → 2 处改
```

### §4.2 1 段 user 改写 = 1:1 grep 找全同关键词 N 处

**触发**: user 给 1 句改写 (人话短版 / 信息简化 / 改语气)

**协议**:
1. **Step 1**: 拿当前 Notion 全文 → grep user 原句关键词 (e.g. `"1 周内读 10 篇"` / `"v0.1"`)
2. **Step 2**: 列出 N 个匹配 block
3. **Step 3**: **必先 AskUserQuestion 1 字母选项** (改 1 处 vs 改 N 处 vs 改信息密度)
4. **Step 4**: user 拍板后改, 1:1 verify N 处全改 + 其他段保留

**反模式**:
- ❌ 直接批量改 N 处不 ask (违反路线选择必问)
- ❌ 改 1 处后才发现 user 期望 N 处全改 (累积残留)
- ❌ 改 N 处后忘 verify 其他段保留

### §4.3 改时间点 = 整张时间表

**触发**: user 改 1 处时间点 (e.g. `"7/20 → 7 月底"`)

**协议**:
1. **Step 1**: 跑 §2 Step 1 拿全文
2. **Step 2**: grep 时间 pattern 找全所有时间 block:
   ```bash
   grep -oE '(\d+月\d+日|\d+\.\d+|\d+月[初中末底]|\d+月\d+-\d+月\d+|\d+-\d+|\d+\.\d+ - \d+\.\d+)' /tmp/page_now.txt | sort -u
   ```
3. **Step 3**: **必先 AskUserQuestion 1 字母选项** (改 1 处 vs 改 N 处含范围)
4. **Step 4**: user 拍板后批量改, 含联动项:
   - 改 1 阶段时间范围必查相邻阶段 (e.g. 改阶段一 7.10-7.24 → 阶段二 7.25-8.15 起点必同步)
   - 改答时间必改答所在阶段
   - 改阶段时间必改总体策略 + h1 §2 + §4 本周计划 (3 处联动)
5. **Step 5**: 1:1 verify 0 旧时间点残留 + N 处新时间点出现

**反模式**:
- ❌ 改 1 处时间点不 grep 全 (改 7/20 → 阶段四 10.1-10.20 / h1 §2 / §4 全 13 处残留)
- ❌ 改 1 阶段忘改相邻阶段 (范围错位)
- ❌ 改阶段时间忘改答时间 (答在雏形交前矛盾)

### §4.4 callout 整段重写

**触发**: 改 callout 内任 1 段 (P1/P2/P3)

**协议**:
1. **Step 1**: GET callout block 拿全文 (callout 是 1 个 block, rich_text 数组含所有段)
2. **Step 2**: 整段重写 (改 P1 必保留 P2/P3 1:1)
3. **Step 3**: PATCH 时必传完整新内容 + icon + color (否则 icon/color 丢失)
4. **Step 4**: verify callout 其他段 1:1 保留

**反模式**:
- ❌ PATCH callout 时只传 P1 (rich_text 数组被覆盖, P2/P3 丢失)
- ❌ 改 P1 后忘 verify P2/P3 (累积残留)

---

## §5 8 条永久失效反模式

1. ❌ verify 只查数量 (5 h1 / 5 h2 / 3 callout) 不查内容 (5 h1 是 "1. 对组内方向" 还是 "TL;DR" 错位?)
2. ❌ 改 1 段漏跑 5 类逐项 (regex grep 5 类)
3. ❌ 1 句话 user 反馈当 1 个 bug 处理 (可能含多类)
4. ❌ 1 session 改 > 3 次 (累积残留)
5. ❌ 改完不 1:1 字符级对比 user 最新原话
6. ❌ 1 段 user 改写直接批量改 N 处不 ask (per §4.2)
7. ❌ 改时间点不 grep 全 + 联动项忘改 (per §4.3)
8. ❌ 改 callout 段不传完整 rich_text + 忘 verify 其他段 (per §4.4)

---

## §6 联动

- `references/notion-block-layout.md` (写布局怎么写, 本表管写完怎么查)
- `~/.agents/skills/paper-into-notion/SKILL.md` (主 SKILL)
- 起源: `~/.agents/skills/_archive/weekly-report-phd/SKILL.md` §9 (line 294-449, v1.1 2026-07-14)

---

## §7 历史

- 2026-07-16 v1.0 立 — 从 weekly-report-phd v1.1 §9 抽离, 通用化 (跨项目 stable)
- 起源 case: 30+ 次 user 反馈累积, 周报项目实证