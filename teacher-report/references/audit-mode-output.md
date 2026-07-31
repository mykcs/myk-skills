---
name: teacher-report-audit-mode-output
description: |
  teacher-report Audit mode 输出格式模板. 总览 + 失败项详情 + 修复命令 + Step A4 reply 模板 + Audit 模式限制.
---

# teacher-report Audit Mode 输出格式

## 总览
- 12 项检查: ✅ X / ❌ Y / ⚠️ Z (降级)
- 合规度: {百分比}%

## 失败项详情

### ❌ Check 4: h4 手动 (1) 编号
**位置**: §2.3 论文精读
**原始片段**: `<h4>(1) 大模型 + 因果(3 篇)</h4>`
**修复建议**: 改为 `<h4>1. 大模型 + 因果(3 篇)</h4>`

### ❌ Check 5: 内联 ① 字符
**位置**: §2.3 第 1 篇
**原始片段**: `<p><b>① Causality for LLMs...</b></p>`
**修复建议**: 改为 `<p><b>Causality for LLMs...</b></p>`

## 修复命令(可选)

如需批量应用所有修复, user 跑:

\`\`\`bash
lark-cli docs +update --api-version v2 --doc {doc_id} --command overwrite \\
  --content "<v0.2.5-compliant XML>"
\`\`\`

**Step A4 — Reply to user**

1. 1 行总结: `{老师} 报告 12 项检查: ✅ 8 / ❌ 3 / ⚠️ 1, 详情见 /tmp/audit-{name}.md`
2. 列出 ❌ 项 (每项 1 行)
3. 提示: `如需修复, 跑命令 ...`

## Audit 模式限制

- **不直接 overwrite** — 审计完只报问题, user 决定是否修复 (避免误覆盖已定制内容)
- **不抓新数据** — 只读现有 docx, 不重新跑 L1-L4 数据源
- **不比对历史版本** — 单一快照, 不做 diff
- **不验证内容正确性** — 只验证结构合规, 内容真伪 (数据来源) 超出 audit 范围
