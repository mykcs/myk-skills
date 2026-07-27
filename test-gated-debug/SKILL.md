---
name: test-gated-debug
description: |
  测试门控迭代调试：先写一个会失败的最小复现测试，再对着它迭代到转绿，自审后才提交。
  治「修了一个又弄坏另一个」的打地鼠循环。适用于代码 bug 修复，不适用 settings/config 修复。
  触发场景: 用户说 "测试门控 / test-gated / 先写失败测试 / 严格调试 / 收敛调试 / test-gated-debug"，
  或代码 bug 反复修不好、改 A 坏 B、需要可证伪的根因验证。
when_to_use: |
  Trigger when user says: "测试门控" / "test-gated" / "先写失败测试再修" / "严格调试这个问题" /
  "收敛调试" / "test-gated-debug" / "别再打地鼠了". 针对代码 bug（有测试框架的项目）。
  NOT: settings.json / config / hook 修复（走 bugfix-400 端到端 fix 脚本协议）/
  无测试框架可写测试的场景（退化为 process.md §C.6 5 步诊断）/ 文档 typo。
user-invocable: true
license: MIT
---

# test-gated-debug

测试门控迭代调试。把「修一个又弄坏另一个」的打地鼠，变成对着失败测试收敛的搜索。

## 硬约束（先读）

- **先红后绿**：没写出失败的复现测试、没给用户看红色输出前，禁止动被调试的代码。
- **一次一个假设**：每轮只验证一个根因假设；失败就回滚再试下一个，不叠加修改。
- **绿才可提交**：新测试转绿 + 全量套件不红 + 自审清单清空，三者齐了才提交。
- **证据收尾**：宣布成功的那条消息必须含绿色测试输出（实测，不是「应该过了」）。
- **不适用硬边界**：settings.json / config / hook 修复走 `bugfix-400.md §C` 端到端 fix 脚本，不用本 skill。

## 流程（5 步）

1. **写最小失败测试**：用项目现有测试框架写一个能复现 bug 的最小测试。跑它，把**红色输出**给用户看。写不出复现测试 → 退化为 `process.md §C.6` 5 步 false-positive 诊断，不硬套本流程。
2. **假设根因**：动代码前，用 ≤2 句话写下根因假设（可证伪的形式：「改 X 应该让测试 Y 转绿」）。
3. **最小修复**：应用能让假设成立的最小改动，跑新测试 + 全量套件。
4. **红则回滚重试**：还红 → `git checkout -- <改动>` 回滚，回到第 2 步换下一个假设。**最多 5 次迭代**，每次记录假设 + 结果；5 次全失败 → STOP，走 §C.6 诊断或 AskUserQuestion，不无限循环。
5. **绿后自审**：修复有没有动到无关代码？会不会让相邻行为回归？（对照 process.md §D Bonus Test：补一个同时触发所有相关机制的端到端用例。）自审清空后，把测试和修复**一起**提交。

## 输出模板（收尾用，极简）

```
测试门控调试 <bug> — 收敛

复现测试: <path>:<name> (先红后绿 ✅)
根因: <1 句>
迭代: <N> 次 (各假设: <列出>)
改动: <files> (+新测试)
验证: 新测试绿 + 全量套件 <pass 数> + 自审清空
commit: <hash>
```

## 反模式（永久失效）

- ❌ 没写失败测试就直接改代码「试试看」
- ❌ 一轮叠多个修改，搞不清是哪个起的作用
- ❌ 测试还红就宣布「差不多好了」（false completion，process.md §C.5 零容忍）
- ❌ 收尾消息不给绿色测试输出，只说「应该过了」
- ❌ 5 次迭代全红还继续瞎试（违反 no-stuck §C.3.6.1）
- ❌ 把 settings/config 修复硬套本流程（该走 bugfix-400）
- ❌ 修复和测试分开 commit（要原子提交，回归证据随修复走）

## 联动

- `bugfix-400.md §C` — settings/config/hook 修复的端到端 fix 脚本协议（本 skill 的边界互补）
- `process.md §C.6` — 5 步 false-positive 诊断（写不出复现测试 / 5 次迭代全红时的降级）
- `process.md §D` — Bonus Test 模式（第 5 步自审的强证据标准）
- `process.md §C.5` — false completion 反模式（红就说好 = 违反）
- `rules/references/process-section-C.3.6-no-stuck.md` — 5 次迭代上限的 no-stuck 依据
