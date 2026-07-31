# Mode × Fetch × Outcome 接口表 (2026-07-26 重构)

> 原 5 个叙述式 examples 改接口表 (per trq212 Claude 5 规则 2: 枚举/参数表达行为空间, 不用 few-shot 收窄探索).
> 叙述版全文见 git history (2026-07-26 前).

## Mode 枚举 (触发 → 动作管道 → 输出 contract)

| Mode | 触发信号 | 动作管道 | 输出 contract |
| --- | --- | --- | --- |
| `single` (默认) | "调研/看看 <学校> <老师>" | L1 → L2 → L3 → L4 (→ L7 社区源, v0.5.0+) | docx URL + TL;DR 匹配度信号 + 论文按 2023-2026 分年 |
| `sparse` (自动降级) | L1 成功 + L2/L3/L4 半失败 — 非独立触发, single 管道内自动判定; **L1-L4 全失败 → 不报 sparse, 报 "信息黑洞 — 建议手动提供主页 URL", 禁止编造** | 存活 L 层继续, 失败层跳过 + 去重 | TL;DR 🟡 数据稀疏 + `5. 数据来源` 段**必须**显式声明各层成败 (透明, 不掩饰); 一作顶会 = 0 → 🟡 通讯/末位 PI 模式, 套磁时追问 1v1 带生 |
| `batch` | 用户同时调研 ≥3 位老师 | `phd-scout --mode batch` | 同 single, 批量 |
| `audit` (v0.2.8+) | "审计一下 <docx-id>" | A1 fetch → A2 12 项 check → A3 写报告 | 1 行总结 `<主题> <版本> 子节点: ✅ N/12` + 报告路径 `/tmp/teacher-report-audit-<主题>-<id>.md`; 有 ❌ 时附 "跑 overwrite 命令可修复" |
| `rewrite` (v0.3.4+) | "按 skill 模板重写 <wiki-url>" | R1 fetch → R2 解析 → R3 L4/L5/L6 重抓 → R4 11-12 block/论文 → R5 12 项自检 → R6 overwrite → R7 验证 | 新 docx URL + diff summary |

## Fetch ladder 参数 (single/sparse 共用)

| 层 | 源 | 失败语义 |
| --- | --- | --- |
| L1 | 学校学院主页 | 失败且 L2-L4 也全失败 → 信息黑洞 (禁止编造) |
| L2 | S2 API (论文) | 半失败 → sparse, 跟 L3 overlap 去重 |
| L3 | DBLP | 半失败 → sparse |
| L4 | 个人页 + 相关学者 context | 过期个人页 → 标注 stale |
| L7 (v0.5.0+) | mysupervisor.org + 知乎 + 小红书 + 学院 PDF | 字段必带 [社区来源] 标签跟 L1 区分 |

## 匹配度信号枚举 (TL;DR 位)

- 🟢 高匹配 — 无 🟡 信号时的默认位 (L 层全活)
- 🟡 数据稀疏 — L1 成功 + L2/L3/L4 任一半失败, 来源段已声明
- 🟡 通讯/末位 PI 模式 — 一作顶会论文 = 0, 套磁时追问 1v1 带生
- 失败可修复信号 — audit ❌ 项 → 提示 rewrite
