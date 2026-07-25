### ⚠️ §A.5 Multi-Round Audit Protocol (v3.9.0, 强制)

> **单 audit run 不能保证找全所有 bug**. Round 1+Round 2 案例 (CASE-WEBSITE-IMPROVE-INCREMENTAL-AUDIT-20260622) 证明: Round 1 修了 canonical/og:image → Round 2 发现 hreflang x-default regression + CVE + i18n + 404. 每次 audit 必跑 4 sub-provisions:

1. **Re-evaluate deferred items** — Round 1 deferred ≠ 关掉. Round 2 必重新评估 (用更新的工具 + 视角).
2. **Deployed behavior check** — 不是 source grep. 必 `curl <deployed-url>/...` 测真实行为. e.g. 404 page 必须 `curl /nonexistent-path/` 验证 HTTP 404 + content, 不只 `test -f src/pages/[lang]/404.astro`.
3. **CVE registry override** — `npm audit --registry=https://registry.npmjs.org/` 绕过 npmmirror 404. 否则 dev-only 中危会被遗漏.
4. **Snapshot diff** — 每次 audit 写 `/tmp/audit-<site>-<date>.md`, diff vs 上次. 立刻看到: 新增 finding (regression) / 已修 finding (progress) / 长期存在 (stale deferred, 重新评估).

**触发式决策**:

- IF user 触发 audit, 必先 `ls -1t /tmp/audit-<site>-*.md 2>/dev/null | head -1` 找上次 snapshot
- IF 上次存在 → 跑 audit + diff vs 上次 → 输出 regression report
- IF 上次不存在 → 跑 audit + 写 snapshot (无 diff)
- IF 用户说 "再检查一遍" → 必走 snapshot diff 流程, 不允许"manual 重跑全部 agent"

**Bonus test (v3.9.0)**: `diff -u <last-snapshot> <new-snapshot>` 在响应中显示 (用户可见). Empty diff = 项目干净.

---

### §A.6 Verifier Self-Test Protocol (v3.10.0, 强制)

> **Verifier 没 self-test = false-positive / false-negative 双风险**. content2html v3.9.0 verifier 用 absolute 5KB threshold → 6-page paper (2606.18246) 每页 ~2.4KB at 50dpi → 全 false-positive "blank page" 警报. 改 relative threshold (`<avg × 0.5`) 解决.

**Hard rule**: 任何 E2E verifier 必含 **2-sample test**:

1. **PASS sample**: known-good state → verifier 报 PASS
2. **FAIL sample**: known-bad state (e.g. 注入 trailing blank, 改 CSS 制造 overflow) → verifier 报 FAIL

**Trigger 模式**:

- IF verifier 改动后没跑 self-test → 必跑 2-sample (PASS sample first, then FAIL sample)
- IF 2-sample 任意一个 fail → revert verifier 改动, 重写
- IF 2-sample 都 PASS → ship verifier

**Real examples (content2html)**:

```javascript
// PASS sample: known-good 13-page paper
SLIDE_COUNT=13 node scripts/verify-print-e2e.mjs
// expected: ✅ PASS, noBlank=true

// PASS sample 2: known-good 16-page paper
SLIDE_COUNT=16 node scripts/verify-print-e2e.mjs
// expected: ✅ PASS, noBlank=true (relative threshold, not absolute)

// FAIL sample: artificially inject trailing blank page
echo "extra blank" >> dist/index.html
SLIDE_COUNT=16 node scripts/verify-print-e2e.mjs
// expected: ❌ FAIL, noBlank=false
```

---

### §A.7 Template Consistency Check (v3.10.0, 强制)

> **Template drift = silent regression**. content2html 2606.18246 R5 之前只有 4 slides (plain headings, no Swiss editorial signature) vs 2603.12109 16 slides (full template: top-accent + accent-bar + kicker + takeaway-item + info-corner). Template 不一致 → 视觉混乱.

**Hard rule**: 当多页面 share 同一 template (e.g. paper slides × N papers) → 必跑 `check-template-consistency.sh` 在每次 commit 后.

**Trigger 模式**:

- IF N pages share template (e.g. paper-slide × papers collection) → 必 verify:
  - 同一组 template elements (top-accent + meta-page + accent-bar + kicker + h2 count + takeaway-item count)
  - 同一组 helpers (extractBullets / cleanHeading / slide structure)
  - 同一 visual signature (font sizes, spacing, info-corner)

**Real examples (content2html)**:

```bash
# scripts/check-template-consistency.sh
# 验证 paper slide.astro 在所有 N papers 有相同 template structure:
# 1. grep "slide-top-accent" count: should be N (slides)
# 2. grep "slide-info-corner" count: should be N papers
# 3. grep "kicker" count: should be similar across files
# 4. grep "takeaway-item" count: should be similar (depends on content)
# 5. JSX structure: same slide-page attrs (top-accent, meta-bar, accent-bar order)
```

**Diff output** (per file):

```
src/pages/zh/paper/2603.12109/slide.astro:
  slide-top-accent: 16 ✓
  slide-info-corner: 1
  kicker: 16
  takeaway-item: 39

src/pages/zh/paper/2606.18246/slide.astro:
  slide-top-accent: 6 ✓
  slide-info-corner: 1
  kicker: 5
  takeaway-item: 0
```
