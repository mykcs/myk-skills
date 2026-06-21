# teacher-report bin/ 工具说明 (v0.13.0)

> **本目录是当前 active 工具**, 旧版 v0.4.0 时期脚本已归档到 `archive/v04-legacy/`. 触发现 active 工具列表时使用本目录文件, 触发现 archive 文件仅作历史参考.

## 当前 active 工具 (2 个)

| 工具 | 行数 | 用途 | 触发场景 |
|------|------|------|----------|
| `migrate.py` | 469 | 主迁移工具 — 批量 docx v0.X → v0.Y 升级 (编号 / emoji / 装饰 / 中文名 等) | 13 PIs wiki docx 跑批量升级时 |
| `fix-v012-tao-ci.py` | 257 | v0.12.0 套磁 section 清理 — 删除 v0.5.0 旧 §1.4 套磁 h2, 升级 v0.13.0 §1.6 套磁清单 | 2 PIs wiki (毛玉仁 / 高云君, v0.5.0+v0.9.0 模板) |

## 归档工具 (4 个, v0.4.0 时期)

> **路径**: `bin/archive/v04-legacy/`
> **触发场景**: 仅作历史 audit / 案例研究, 不要再 trigger 跑这些脚本. 如需 v0.4.0 升级能力, 用 `migrate.py` 替代.

| 工具 | 行数 | 用途 | 状态 |
|------|------|------|------|
| `push-v039-cards.py` | 291 | v0.3.9 paper card push 工具 (v0.3.9 → v0.4.0 升级时用) | deprecated, 用 migrate.py 替代 |
| `reorder-dengshumin-v040-h2.py` | 168 | 邓舒敏 v0.4.0 H2 重排工具 (一次性 2026-06-10) | deprecated, 历史脚本 |
| `reorder-h2-fix.py` | 161 | v0.4.0 H2 修复通用工具 | deprecated, 用 migrate.py 替代 |
| `v040-fixed.xml` | (大量) | v0.4.0 邓舒敏 fixed XML 快照 (2026-06-10) | deprecated, 历史 snapshot |

## 配套 reference

- `references/output-schema.md` — 22 项 LLM 自检 (Check 1-22)
- `references/audit-checklist.md` — 12 项 audit mode 合规检查
- `references/report-template.md` — v0.13.0 飞书 docx XML 模板
- `references/output-contract.md` — v0.13.0 6 章节必含硬要求

## 工具触发方式

LLM 调 `bin/*.py` 前必读:
1. `references/output-contract.md` 理解 v0.13.0 输出规范
2. `references/audit-checklist.md` 理解 audit mode 触发场景
3. 工具自身的 `--help` 输出

## 工具不触发场景

- ❌ 不要 trigger `archive/v04-legacy/*.py` 跑生产数据 (数据格式已变, 跑会坏)
- ❌ 不要 trigger `bin/*.py` 改 docx 不写 backup (`migrate.py` 自带 backup, 其他工具无)
- ❌ 不要 trigger 工具不读 references 盲目跑 (工具假设 docx 格式与模板一致)
