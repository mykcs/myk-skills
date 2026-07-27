---
name: friction-mining
description: |
  摩擦挖掘闭环：扫最近 session 转录里的摩擦事件（误解请求 / 错误方案 / 改动过多 / 啰嗦格式），
  对复发 ≥3 次的模式自动起草硬规则 + 验证探针，开原子 PR。把一次性手动挖掘固化成可重复的一键动作。
  触发场景: 用户说 "摩擦挖掘 / friction-mining / 挖摩擦 / 扫 session 找复发问题 / 自愈闭环 / friction"，
  或想把近期反复踩的坑固化成规则 + 探针。
when_to_use: |
  Trigger when user says: "摩擦挖掘" / "friction-mining" / "挖一下最近的摩擦" / "扫 session 找复发问题" /
  "自愈闭环" / "把最近踩的坑固化成规则" / "friction". 输入是 session 转录，输出是规则 + 探针 + PR。
  NOT: 单个具体 bug 的修复（走 test-gated-debug 或 bugfix-400）/ 网站改进（走 website-improve）/
  host 跨层一致性审计（走 host-self-evolve）。
user-invocable: true
license: MIT
---

# friction-mining

摩擦挖掘闭环。扫 session 转录找复发摩擦，对每个 ≥3 次的模式起草硬规则 + 验证探针，开原子 PR。

## 硬约束（先读）

- **证据先行**：每条规则必须引 ≥3 个证据 session（id 或路径）。凑不齐 3 次 → 不立规则，只记录观察。
- **规则 + 探针成对**：立一条规则必配一个能跑通的 grep 探针，探针必须实测 exit=0（防空架子）。
- **原子 PR**：每条规则一个 commit/PR，链接 session 证据；不把多条揉成一团。
- **可逆自决，不可逆才问**：改 soul.md / rules / 新建探针是可逆的，自决 + 事后告知；遇不可逆或路线分歧才合并成单个 AskUserQuestion（per soul.md §2.2.1 批量例外）。
- **保护路径绕行**：soul.md 非 protected 可直接改；若规则要落到 CLAUDE.md / settings.json / hooks（protected path），走文档记载的 Bash+Python 绕行，不让 Edit 失败。

## 流程（5 步）

1. **扫转录**：定位最近 N 个 session 转录（`~/.claude/projects/**/*.jsonl`），grep 摩擦信号：用户纠正（「不对 / 我是说 / 不是这个 / 你搞错了」）、返工、啰嗦吐槽、过度工程打断。按模式归类（误解请求 / 错误方案 / 改动过多 / 啰嗦格式 / 其他）。
2. **计数筛模式**：每个模式统计复发次数。**只取 ≥3 次的**进入下一步；<3 次记为观察，不动手。
3. **起草规则**：对每个入选模式，起草一条硬规则（触发词 + 行为 + 反面 + 证据 session），落点到 soul.md 或对应 rules 文件。先跑 6 件套 grep 确认无重复锚点。
4. **配探针**：每条规则写一个 `~/.claude/scripts/<topic>-probes/p<N>-*.sh`（只读 grep 锚点防回归），实测跑到 exit=0。
5. **原子 PR + 报告**：每条规则一个 commit（五段 message：改了什么/为什么/在哪/安全/验证），push；汇总报告已落地规则 + 探针结果 + 观察项（<3 次的）。

## 输出模板（收尾用，极简）

```
摩擦挖掘 <范围: 最近 N session> — 收敛

入选模式 (≥3 次): <M> 个
- P<n> <模式名> (<次数> 次, 证据: <session ids>) → 规则落 <file §> + 探针 <path> ✅
观察项 (<3 次): <列出, 不立规则>
PR/commit: <hashes>
验证: 探针全绿 <x/y exit=0> + 6 件套 grep 无重复 + 增量非 stub
```

## 反模式（永久失效）

- ❌ 凭印象立规则，不引 ≥3 个证据 session（违反证据先行）
- ❌ 立规则不配探针 / 探针没实跑就标 ✅（空架子，process.md §C.5 false completion）
- ❌ <3 次的偶发也立规则（规则膨胀，信噪比下降）
- ❌ 多条规则揉一个 commit（违反原子 PR）
- ❌ 把「挖过一次」当成「闭环建成」——本 skill 才是可重复机制，手动挖是一次性
- ❌ 直接 Edit protected path（CLAUDE.md/settings/hooks）导致失败，不走 Bash+Python 绕行
- ❌ 报告里写「建议下次挖掘」而不实际跑（deferred theater，process.md §C.2 零容忍）

## 联动

- `soul.md §2.2.1` — 批量修复例外（多个摩擦模式合并决策的依据）
- `process.md §C.2 / §C.5` — deferred theater / false completion 零容忍（探针必须实测）
- `rules/cross-session-grep-mandatory.md` — 立新文件/锚点前 6 件套 grep
- `claudecode-verify-before-act.md §4` — protected path 的 Bash+Python 绕行
- `host-self-evolve` — 跨层一致性审计（互补：它审结构，本 skill 挖行为摩擦）
- `feedback-claude-repo-auto-push` — ~/.claude/ 仓改完默认直 push main
