## Procedure

### Step 0 — Mode selection (v0.3.4+)

- **Generation mode (default)**: user 提供老师姓名/学校 → 生成新 docx
- **Audit mode**: user 提供 docx URL/doc_id → 审计合规性
- **Rewrite mode (v0.3.4+)**: user 提供 docx + "按模板重写/排版/规范化/升级" 指令 → 全量 regenerate

**Mode 判定**: 触发词含 "审计/audit/检查/合规/review" → Audit; 含 "调研/生成/写一份" → Generation; 显式提供老师姓名 → Generation; 显式 docx URL 且无 Generation 触发词 → Audit.

**Rewrite 触发词**: "按 skill 模板重写" / "按 v0.3.3 重写" / "规范化 doc" / "重排版" / "按模板排版" / "升级到最新格式" / "fix this doc to match the skill" / "regenerate according to skill template".

**Rewrite 不响应场景**: user 只说 "审计一下 [URL]" → Audit mode, 不自动 rewrite. user 说 "fix this" 但没指明 docx URL → 反问 user 哪一篇.
