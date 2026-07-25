### ⚠️ §L19 4-Site CI 全绿硬规则 (v4.0.1, 强制, 适用所有 sub-mode)

> **Source**: user 2026-06-27 原话 "把这个四站全绿, 或者是你, 就是只要你提升网页的站, 都都要保持这个运行成功". CASE-MULTI-SITE-FULL-AUDIT-V4-20260627 验证 v4.0.0 4 站 fan-out 可达 CI 全绿.
>
> **PER 角色归属**: **Verifier** 负责判定 4 站 CI 状态并输出 verdict；CI red 时 **Executor** 重做 fix 整轮；**Planner** 在 pre-flight 中将 §L19 列为验收标准。

**硬规则 (Hard Rule)**: 任何 website-improve run (单 sub-mode 或 v4 sweep) 涉及 **4 active sites = mykcs.github.io / GDKVM / OSA / content2html** 中任一站 → **4 站 CI 必须全部 `conclusion: success` 才算 done**.

**判定**:

- ✅ Run 4/4 CI green → done
- ❌ 任一站 CI red/pending → **BLOCKED on `<site>: <reason>`**, 禁止声明 "完成"
- ❌ 任一站 CI red 但 fix 不可行 (e.g. 物理不可达) → **BLOCKED on user decision**, 必须 `AskUserQuestion` 给选项 (回滚 / 接受 red / 重试)

**强制流程** (Phase 4 末段 + 任何 fix 之后):

```bash
# 4 站 CI 5 commands verification (per site, /check-runs 优先 per process.md §H.1 + ADR-0070)
for owner_repo in "mykcs/mykcs.github.io" "wangrui2025/GDKVM" "wangrui2025/osa" "mykcs/content2html"; do
  gh api "repos/$owner_repo/commits/HEAD/check-runs" \
    | python3 -c "import json,sys; d=json.load(sys.stdin); [print(r['name'], r['conclusion'] or r['status']) for r in d.get('check_runs',[])]"
done

# 4/4 check-runs 全 conclusion=success → 输出 "✅ 4 站 CI 全绿", 写 case file + decision-stream
# < 4 success → 输出 "❌ BLOCKED on <site> CI red/queued", 走 fix 路径或 AskUserQuestion
# 注: gh run list 也可用 (拉 workflow run 视角), 但 /check-runs 直接拉 commit-级 check, 更接近"commit 通过 CI"语义
# 反模式 (per CASE-WEBSITE-IMPROVE-4SITE-20260719 v2): ❌ 用 /status endpoint 返 pending + 空 statuses 误判 green
```

**触发判断**:

- ✅ 单 sub-mode A sweep 4 站 → 触发
- ✅ Multi-site D fan-out → 触发
- ✅ 任何 Phase 3 fix 后 → 触发 (per-site CI verify, 至少修过的站必须 green)
- ✅ 跨项目改动 (e.g. 改 shared script 被 4 站共用) → 触发
- ❌ 单 sub-mode A 跑 1 站 + user override scope (e.g. "只跑 mykcs") → 不触发 (4 站全绿不适用)

**owner 隔离 (双账号铁律)**:

- mykcs/* → mykcs/GitHub token
- wangrui2025/* → wangrui2025/GitHub token
- 跑前必 `git remote -v` 三次确认, 避免 push 错 owner (历史污染 4+ 次)

**反模式 (claudecode 历史反复踩)**:

- ❌ 报 "完成" 但 1+ 站 CI red / pending → 违反 §C verification gate
- ❌ "CI 大概会过" / "应该 OK" → 违反 §H acceptance protocol
- ❌ 不跑 `/check-runs` 直接声明 done → 违反 CLAUDE.local.md §5.2 5 commands verification + ADR-0070
- ❌ "我只跑 X 站, 其他站不用管" → 违反 v4.0.0 default 4-site scope

---

### ⚠️ §L20 Fix-Validate-Build 防 Lockfile 漂移 (v4.0.1, 强制, 适用 Phase 3 fix agent)

> **Source**: CASE-MULTI-SITE-FULL-AUDIT-V4-20260627 — GDKVM fix agent 改 `package.json` exact pin (`^4.1.18` → `4.1.18`) 但**未跑 `npm install` 重生成 `package-lock.json`** → CI `npm ci` 拒绝 (lockfile 含 `tailwindcss@4.3.0` caret 解析, 与 package.json 4.1.18 exact pin 冲突) → CI red → 二次 commit `72294b3` 修复. 根因: fix agent 改 package.json 后口头报 "已 fix", 未跑 build verify.
>
> **PER 角色归属**: **Executor** 负责在改 `package.json` 后执行 `npm install` + `npm run build` 验证；**Verifier** 验收时检查 exec-log 中是否包含该验证命令输出。

**硬规则 (Hard Rule)**: 任何 Phase 3 fix agent 修改 `package.json` 或 `package-lock.json` 后 → **必跑 `npm install` (重生成 lockfile) + `npm run build` (验证 build pass)** → 才算 commit 完成. 禁止口头报 "改完" 无 verify.

**强制流程** (Phase 3 fix agent 末段):

```bash
# Step 1: 改完 package.json 后, 必重生成 lockfile
npm install
# 或 --save-exact (如果改 pin):
npm install --save-exact <pkg>@<version>

# Step 2: 验证 build pass (本地)
npm run build
echo "exit=$?"  # 必须 0

# Step 3: 验证 build pass (本地跑 ci 关键步骤, 模拟)
npm ci        # 模拟 CI 用 lockfile 安装
npm run build
echo "exit=$?"  # 必须 0
```

**触发判断**:

- ✅ 改 package.json (dependencies / devDependencies / scripts / version pin) → 必跑
- ✅ 改 package-lock.json 直接 → 必跑 `npm ci` 验证一致性
- ❌ 只改 source code (.astro / .ts / .mjs / .css) → 不强制 (但建议 build smoke test)

**反模式**:

- ❌ 改 package.json exact pin 但不跑 `npm install` → 假 fix, lockfile 漂移
- ❌ 改完口头报 "已 fix" 无 build 验证 → §C.5 false-positive 风险
- ❌ 信任 agent 自报 "我跑了 build" → 必自己跑, 不可信报告

**联动**: §C.5 5 步 false-positive 诊断协议 — 改某项后 E2E fail, revert 后仍 fail, 怀疑 lockfile 漂移时, 优先跑 `npm install --save-exact` 重 lockfile.

---

### ⚠️ §L25 Deployed-Layer Verify Protocol (v4.0.4, Round 11 P0/P1 regression 治本)

> **Source**: Round 11 (2026-06-29) §A.5 snapshot diff 发现 2 个 P0/P1 deployed-layer regression:
>
> 1. **mysite**: `astro/public/.well-known/security.txt` 文件 on disk, 但 `curl https://mykcs.github.io/.well-known/security.txt` 返 HTTP 404 (Astro 404 handler 拦截 .well-known/ 路径).
> 2. **content2html**: `public/_headers` 文件 17 行 (X-Frame-Options / CSP / X-Content-Type-Options), 但 `curl -sI https://mykcs.github.io/content2html/` 返 HTTP 200, **无任何 security header** — GH Pages user/org site 不 serve `_headers` 文件 (仅 Project Pages 支持).
>
> 文件存在 ≠ deployed. 治本 = §A.5 sub-provision #2 deployed behavior check 必跑.
>
> **PER 角色归属**: **Verifier** 负责在 fix commit 后 curl live URL 并记录到 verdict；**Executor** 在 exec-log 中提供已修改 `public/` 文件列表供 Verifier 使用。

**硬规则 (Hard Rule)**: 任何 Phase 3 fix commit 包含下列类型文件时, 必跑 deployed-layer verify (curl live URL) 才算 fix 完成:

| 文件类型               | 必跑 curl 验证                                                             | 反例 (Round 11)                                                             |
| ---------------------- | -------------------------------------------------------------------------- | --------------------------------------------------------------------------- |
| `public/_headers`      | `curl -sI <live-url>/` 看是否含 X-Frame-Options/CSP/X-Content-Type-Options | content2html _headers 文件 on disk but GH Pages user/org site 不 serve (P0) |
| `public/.well-known/*` | `curl -sI <live-url>/.well-known/<file>` 看是否 200 + correct content-type | mysite security.txt on disk but Astro 404 handler 拦截 (P1)                 |
| `public/robots.txt`    | `curl -s <live-url>/robots.txt` 看内容是否匹配 disk                        | (Round 11 content2html 验证 ✅ pass)                                        |
| `public/manifest.json` | `curl -sI <live-url>/manifest.json`                                        | (待 Round 12 验证)                                                          |
| `public/sitemap*.xml`  | `curl -s <live-url>/sitemap.xml` 看内容                                    | (待 Round 12 验证)                                                          |

**强制流程** (Phase 3 fix commit 后, before declaring done):

```bash
# For each modified static file in public/, run live curl verify
for f in $(git diff --name-only HEAD~1 | grep -E '^public/'); do
  url="https://<live-domain>/${f#public/}"
  echo "=== $url ==="
  curl -sI "$url" | head -10
done
```

**反模式 (Round 11 教训)**:

- ❌ `test -f public/_headers` 通过就报 "已 fix" → 违反 §A.5 sub-provision #2 deployed behavior
- ❌ 信任 agent "我跑了 curl" → 必 orchestrator 端实测 + 贴 curl 输出到 verdict
- ❌ GH Pages user/org site 假设 serve `_headers` 文件 → 实测才知, 不写 spec 等同假设

---

### ⚠️ §L26 "CI 全绿" 5 字段自检表 (v4.0.4, Verifier 必跑)

> **Source**: §H Acceptance Protocol + §C.3.7 4 站 CI 全绿硬规则 + 灵魂 v6 任务后建议协同.
>
> **PER 角色归属**: **Verifier** 在 verdict.json 必填 5 字段, Verifier 输 5 字段 + verdict 是 website-improve run "完成" 的硬证据.

**5 字段自检表** (per `protocols/5-field-acceptance.md` SSOT):

| #   | 字段                      | 验收标准                                                             | Verifier 必填 |
| --- | ------------------------- | -------------------------------------------------------------------- | ------------- |
| 1   | **path**                  | 4 站修改文件绝对路径已输出 (含 owner 隔离)                           | ✅            |
| 2   | **commit**                | 4 站 `git log -1` 有新 commit (含 commit hash)                       | ✅            |
| 3   | **push**                  | 4 站 `git log @{u}..HEAD` 空 (0 ahead, owner 正确)                   | ✅            |
| 4   | **CI**                    | `gh api repos/<owner>/<repo>/commits/HEAD/check-runs` × 4 全 success | ✅            |
| 5   | **owner 隔离 + 验收证据** | `git remote get-url origin` + 1+ 行 curl 200 证据                    | ✅            |

**强制流程** (Verifier 跑 verdict 前):

```bash
# 5 commands verification (per site, 4 站全跑)
for owner_repo in "mykcs/mykcs.github.io" "wangrui2025/GDKVM" "wangrui2025/osa" "mykcs/content2html"; do
  site_name="${owner_repo##*/}"
  d="$HOME/Claude/Projects/webs/$site_name"
  echo "=== $owner_repo ==="
  echo "path: $d"
  cd "$d"
  echo "commit: $(git log -1 --format='%h | %s')"
  echo "push: $(git rev-list --left-right --count @{u}...HEAD | tr '\t' '/')"
  echo "owner: $(git remote get-url origin)"
  gh api "repos/$owner_repo/commits/HEAD/check-runs" \
    | python3 -c "import json,sys; d=json.load(sys.stdin); [print('  ', r['name'], r['conclusion'] or r['status']) for r in d.get('check_runs',[])]"
done
```

**判定矩阵**:

- ✅ 5 字段全过 + 4 站 CI 全 green → Verdict PASS
- ❌ 任一站 CI red/pending → Verdict BLOCKED on <site>
- ❌ 任一站 owner 错 (mykcs/wangrui2025 污染) → Verdict BLOCKED on owner contamination
- ❌ 任一站 push ahead/behind != 0 0 → Verdict BLOCKED on sync (跑 §post-pr-merge-ff-verify)

**反模式**:

- ❌ Verifier 报 PASS 但 5 字段有任一 ❌ → false completion (per §C.5)
- ❌ Verifier 用 emoji ✅ 替代实际 5 字段证据 → 违反 §H 反模式
- ❌ Verifier 只验 1 站 (e.g. "我只 verify mysite") → 违反 v4.0.0 default 4-site scope

**联动**:

- §H Acceptance Protocol 5 字段 (主协议位)
- §C.3.7 4 站 CI 全绿硬规则
- post-pr-merge-ff-verify-rule.md (ahead/behind 兜底)
- 灵魂 v6 任务后建议 (跑通后必输出 2 段)
