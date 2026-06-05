# 2026-06-05 飞书标题号规范化审计追踪

> **事件**:v0.2.5 (`56f0e3b`) 首次在 `report-template.md §5` 加入"飞书标准标题号"硬规则,但 **4 个已发布的 docx 仍带 v0.2.3 模板残缺**(`(1) (2) (3)` h4 手动编号 / `① ② ③` 内联字符 / `████████` 字符画)。
>
> **响应**:批量 overwrite 规范化 + dashboard 摘要清理,记录于此文件,**防止 user 以为 v0.2.5 自动覆盖历史**。

## 4 个 docx 规范化清单

| 文档 | doc_id | rev | h2 章节 | 修复内容 |
|------|--------|-----|---------|---------|
| **浙江大学 吴飞** wiki | `HpyNdN2s2oiy7xxhXumcEKr3nHO` | 73 | 1./2./3./4./5. + 🆕 补强 | Kimi 整理版 + 6-5 append 补强版统一 v0.2.5 |
| **浙江大学 况琨** v0.2.2 | `J35xdiI04oeQEUxhRajc8QJmnLd` | 13 | 1./2./3./4./5. | 中文数字"一、二、三"改阿拉伯数字 |
| **浙江大学 况琨** v0.2.3 | `DnlbdntvNoiUTexclCic00ChnYe` | 17 | 1./2./3./4./5. | 补全 §2 h2 标题(脚本没识别到锚点) |
| **浙江大学 况琨** v0.2.4 子节点 | `MqEzdtwcso2AGyxUPuCcyQRAnwe` | 11 | 1./2./3./4./5. | 原本就 OK,无操作 |
| **申博 dashboard** | `WBLvdxoFCokxmLxSU27cxIxjnSe` | 4 | 索引页 | 清理 v0.2.3 残缺版摘要行,加规范化说明 |

## 统一规范(任何 teacher-report 输出必须满足)

- **h2**:阿拉伯数字 `1.` `2.` `3.` `4.` `5.`
- **h3**:子节 `1.1` `2.1` 等
- **h4**:`1.` `2.` `3.` `4.`(无 `(1)` `②` 括号)
- **论文精读**:`<p><b>完整标题</b></p>`(无 `①` `②` 内联字符)
- **趋势表**:用 `<table>` 精确计数(无 `████████` 字符画)
- **§5 数据缺口**:集中 ⚠️ callout

## 重跑方法(后续维护)

如果又有新老师跑 v0.2.5 之前的报告,用以下命令批量规范化:

```bash
# 1. 拉取现状
lark-cli docs +fetch --api-version v2 --doc {doc_id}

# 2. 全量 overwrite v0.2.5 模板
lark-cli docs +update --api-version v2 --doc {doc_id} --command overwrite \
  --content "<v0.2.5 full XML>"

# 3. (dashboard 专用)追加规范化说明
lark-cli docs +update --api-version v2 --doc {DASHBOARD_TOKEN} --command append \
  --content "<规范化说明 block>"
```

## 教训固化

1. **规则升级 ≠ 历史自动迁移** — v0.2.5 在 SKILL.md 改了硬规则,但 4 个已发布 docx 仍是 v0.2.3 模板。每次规则升级后必须**显式重跑现有 docx**。
2. **"埋得深"的规则不生效** — 硬规则必须在 SKILL.md 顶层 (🚨 callout),不能只在 references/ 的 §5。已在 v0.2.7 提升到 SKILL.md §Step 1。
3. **dashboard 索引是隐藏污染源** — 子节点已经升级到 v0.2.5,但 dashboard 摘要行的链接或残缺版文字会**误导 user 以为"已升级"**。每次升级子节点必须同步更新 dashboard 摘要。

## Status

- ✅ 4 个 docx 全部规范化完成(2026-06-05 17:44)
- ✅ 硬规则提升到 SKILL.md 顶层(v0.2.7)
- ✅ 写入 llm-prompt.md 反模式 + 检查清单(v0.2.7)
- ⏳ v0.2.7 commit pending push
