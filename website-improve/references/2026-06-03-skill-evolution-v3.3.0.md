## Skill Evolution v3.3.0 — 2026-06-03 自进化协议 + 反模式硬化

> **本节来源**：3 站 Mode A 跨站 audit 中**反向漂移 + 自指 false-positive** 两个新反模式，触发自进化协议（§30）首次落地。每个规则对应 §30-§32。

### §30 — 自进化协议（Self-Evolution Protocol）

> **meta-capability**：本协议让 website-improve skill 本身具备自进化能力。
> 来源：CASE-CROSS-REPO-OWNER-DRIFT-20260603

#### 触发条件（4 类）

1. **跨仓 audit 完成**（≥2 仓 Mode A 跑完）
2. **P0/P1 反模式新类别**（如 owner 漂移反转 / §14.1 self-match）
3. **Deja-Vu Fix 触发**（30 天内同 repo 同类 bug 第二次，per `~/.claude/rules/behavioral-deja-vu-gate.md`）
4. **用户显式触发**（"skill 升级" / "自进化" / "沉淀"）

#### 自进化 checklist（5 步强制）

- [ ] **Step 1 — 总结新发现**
  - 区分：单仓 quirk vs 跨仓通用
  - 单仓 quirk → **只进 case file**（不污染 skill）
  - 跨仓通用 → 进 skill（§N+ 新章节）

- [ ] **Step 2 — 升级 SKILL.md**
  - Version bump v3.X.0 → v3.(X+1).0
  - 新增 §N+ 跨仓 bug pattern 章节
  - 已有 §0/§12/§13/§14/§15/§16 视情况扩展
  - 启动验证如升级 → §0 加新条目

- [ ] **Step 3 — 升级 scan-checklist.md**
  - 新增 §M.Y 检测章节（可执行 bash/node 脚本）
  - **至少 1 仓 CI 集成**（multi-site-checks.yml）—— §16 强制要求

- [ ] **Step 4 — 沉淀 case file**
  - 命名：`~/.claude/knowledge/cases/wiki/CASE-{TOPIC}-{YYYYMMDD}.md`
  - MEMORY.md 索引更新
  - SKILL.md 引用回 case（"详见 CASE-XXX"）

- [ ] **Step 5 — Commit + Push**（atomic 一次性提交）
  - mykcs/myk-skills: SKILL.md + scan-checklist.md + case 引用
  - 三仓 multi-site-checks.yml: 集成新检测 step
  - **禁止拆多个 commit**（自进化 = atomic 行为）

#### 自进化反模式（禁止）

- ❌ **单仓 quirk 推为通用规则**（污染 skill）
- ❌ **自进化后不更新 version**（用户无法追踪）
- ❌ **SKILL.md 写规则但 scan-checklist.md 不写脚本**（无操作性）
- ❌ **scan-checklist.md 写脚本但不集成 CI**（装饰品，违反 §16）
- ❌ **Case file 不引用回 SKILL.md**（孤儿 case）
- ❌ **自进化拆多个 commit**（违反 atomic）

#### 自进化本身审计

- 每月 / 每 N 次 audit 后回顾：
  - skill 升级次数 vs 实际解决问题数
  - 哪些规则被频繁触发（设计正确）
  - 哪些规则从未触发（可能过度设计）
  - 哪些反模式被重复犯（需要硬化）

### §31 — §0 gh-api 双侧验证（doc-sync 反向漂移防护）

> 来源：CASE-CROSS-REPO-OWNER-DRIFT-20260603

**问题**：doc-sync agent 仅看 `git remote -v`（git config）→ 不验证 GitHub 实际状态 → 误信 stale remote（如 mykcs/OSA 指向 404 URL）→ 4 处 mykcs/OSA 替换污染 SKILL.md / CLAUDE.md / CASE-097。

**强制流程**（在 §0 之后加第 5 条）：

```
5. **gh api 双侧验证（cross-repo 强制）**
   - 对所有引用的 owner/repo 跑 `gh api repos/<owner>/<repo>`
   - 至少 1 个 404 → STOP，task 描述的 owner 假设可能反转
   - 适用：跨 owner 文档同步、doc-sync、SKILL.md §14 更新、CLAUDE.md 活跃站点索引
   - 不适用：单仓 audit、已验证 owner 的小改动
```

**anti-pattern**：
- ❌ `git remote -v 列出 = remote 存在`（错：git config 可指向任意 URL 包括 404）
- ❌ `task 描述 = 事实`（错：用户给的 owner 假设可能基于过时文档）
- ❌ `doc-sync agent 可比 audit agent 宽松`（错：两类 agent 必须共享 §0 硬规则）

**检测**：scan-checklist §14.7 + 三仓 multi-site-checks.yml 集成。

### §32 — §14.1 self-resilient pattern（self-match false-positive 防护）

> 来源：mykcs.github.io multi-site-checks.yml §14.1 自指失败（commit a38916e + 245f1bb GDKVM 验证）

**问题**：检测脚本用 `grep "submodules: recursive"` 匹配所有 yml 文件，但脚本自身（multi-site-checks.yml）也包含该字符串。`basename skip` 不可靠——文件名/路径不匹配即失效。

**强制规则**：
- 检测脚本中的 grep pattern 必须 **line-anchored** 且 **EOL-anchored**
- 禁止依赖 basename skip 来自我排除
- 标准模式：`^[[:space:]]+KEY:[[:space:]]+VALUE[[:space:]]*$`

**修复**（a38916e / 245f1bb）：

```bash
# ❌ 错：依赖 basename skip（fragile）
if grep -q "submodules: recursive" "$yml" 2>/dev/null; then
  [ "$(basename "$yml")" = "multi-site-checks.yml" ] && continue

# ✅ 对：line-anchored pattern（自排除，无需 skip）
if grep -qE '^[[:space:]]+submodules:[[:space:]]+recursive[[:space:]]*$' "$yml" 2>/dev/null; then
  # pattern 不会匹配 grep 自身
```

**附加硬化**（commit 245f1bb 在 GDKVM 验证）：
- `.gitmodules` 必须存在 **且** 包含至少 1 个 `[submodule "..."]` 段
- 仅文件存在但为空 → 仍算 dead workflow

**anti-pattern**：
- ❌ `detection script grep -q "PATTERN" file → 匹配自身`（self-match false-positive）
- ❌ `basename skip` 作为唯一 self-exclusion（路径不匹配即失效）

**检测**：scan-checklist §14.1 加 self-resilient pattern 强制标准。

### v3.3.0 增量（与 v3.0/v3.1/v3.2 对比）

| 版本 | 来源 | 增量 |
|------|------|------|
| v3.0.0 | 2026-06-02 三仓 audit | §0/§12-§16 |
| v3.1.0 | 2026-06-02 同日 5-site audit | §17-§22 |
| v3.2.0 | 2026-06-03 三站 Mode A 修复 | §23-§29（执行层跨站 bug 模式） |
| **v3.3.0** | **2026-06-03 同次 audit 反向漂移 + 自指反模式** | **§30-§32（meta 自进化 + 反模式硬化）** |

### 已知跨仓约束（v3.3.0 追加）

| 约束 | 原因 | 适用 |
|------|------|------|
| **gh-api 双侧验证** | git remote 可指向 404 URL | 所有跨仓文档同步 / doc-sync / cross-repo owner 变更 |
| **§14.1 self-resilient pattern** | basename skip 不可靠 | 所有 detection scripts |
| **skill 自进化必须 atomic commit** | 拆 commit = 半成品 state | 任何 skill version bump |
