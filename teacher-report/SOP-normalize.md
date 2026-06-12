# SOP — v0.3.0 Paper Card 批量规范化

> **作者**: claudecode + teacher-report v0.3.0
> **最后更新**: 2026-06-08
> **适用**: 任何已发布的 teacher-report docx (飞书) — 把 §4 表格内 100+ 论文批量转 6 行 paper card
> **目标耗时**: 102 篇 ≈ 10 分钟 (arXiv 限流 3s/req + retry)

## 0. 步骤 0: 清理 doc 旧 v0.3.0 段（仅 doc 已脏时跑）

> **何时跑**: doc 已有 v0.3.0 段但是乱 / 重复 / 含假命令时。先清理再重新 batch。

```bash
cd ~/.agents/skills/teacher-report/scripts

# 0.1 先 dry-run 扫描看 doc 现状
python3 cleanup.py --doc <DOC_TOKEN> --dry-run

# 0.2 实际清理 (删旧 + 重 append 干净 §7)
python3 cleanup.py --doc <DOC_TOKEN>
```

清理脚本行为：
- 扫描 doc 找 `v0.3.0 Paper Card 详展` + `7.4 剩余 92` + `本文档由 claudecode` 块
- `block_delete` H2 块（级联删 H3/H4/paragraph 子块）
- 重生成干净 §7（41 found + 59 not_found + 真命令段）append 到末尾
- 全程 ~30 秒

**注意**: cleanup 复用 `/tmp/normalize-report.json` 缓存（不再查 arXiv）。若要重新查 arXiv，先跑 `normalize.py --doc <DOC> --dry-run` 刷新缓存。

## 1. 目标与背景

v0.3.0 起的 teacher-report skill 要求所有论文条目用 6 行 paper card 格式（标题 + 完整作者列表 + Fei Wu 显式标注 + 发表 venue/year/role + arXiv URL + papers.cool URL）。但已发布的 docx 还在用 v0.2.5 的紧凑 `<p><b>标题 (venue year) ⭐</b></p>` 格式。

本文档配套脚本 `scripts/normalize.py`，一键完成：
1. **EXTRACT** — 从飞书 doc §4.x 表格提取 102+ 论文元数据
2. **LOOKUP** — 串行查 arXiv API (3s 限流 + retry/backoff) — **NOTE: arXiv 不容忍并发, 强制 1 worker**
3. **BUILD** — 按 v0.3.0 6 行 paper card 格式生成 markdown (含 not_found 列表 + 真命令段)
4. **APPEND** — 用 lark-cli append 到 doc 末尾
5. **REPORT** — 输出 JSON 报告 (哪些找到/未找到/失败)

清理脚本 `scripts/cleanup.py` 在 doc 乱时先跑步骤 0。

## 2. 前置条件

| 依赖 | 版本 | 用途 |
|------|------|------|
| Python 3.10+ | 已验证 3.14.4 | 跑脚本 |
| lark-cli | 已安装 1.0.19 | 飞书 docx 读写 |
| 网络 | OK 出口到 `export.arxiv.org` | arXiv API 查询 |
| 飞书 docx 权限 | `--doc` 参数的 token 有写权限 | 追加内容 |

**无需** requests/aiohttp — 用 stdlib `urllib.request` + `xml.etree`。

## 3. 快速使用

### 3.1 Dry-run（先生成 + 报告，不 append 到 doc）

```bash
cd ~/.agents/skills/teacher-report/scripts
python3 normalize.py \
  --doc EFlmwpPgKiUARAkTplIcoOqrn3w \
  --workers 4 \
  --dry-run
```

输出:
- `/tmp/paper-cards-batch.md` — paper cards 段 markdown
- `/tmp/normalize-report.json` — 102 篇的逐篇状态 (found/not_found/error/ambiguous)
- stdout — 进度 + summary

### 3.2 正式 append 到飞书 doc

```bash
cd ~/.agents/skills/teacher-report/scripts
python3 normalize.py \
  --doc EFlmwpPgKiUARAkTplIcoOqrn3w \
  --workers 4
# workers 参数保留为兼容，实际强制 1 (arXiv 限流)
```

输出:
- 同上 + 飞书 doc 末尾新增 `## 7. v0.3.0 Paper Card 详展` 段 (含 102 篇 paper cards + 未找到列表)
- doc revision_id 推进 (e.g. 128 → 129)

### 3.3 只处理特定年份

```bash
python3 normalize.py \
  --doc EFlmwpPgKiUARAkTplIcoOqrn3w \
  --year-range 2025 2026 \
  --dry-run
```

只处理 2025-2026 年的论文，§4.1 (2026, 13 篇) + §4.2 (2025, 38 篇) = 51 篇 ≈ 5 分钟。

## 4. 输出格式说明

### 4.1 paper cards 段结构 (6 行/篇)

```markdown
#### {N}. {verbatim 论文标题}

作者：
{作者 1, 作者 2, ..., Fei Wu（吴飞）, ..., 末位作者}

发表：{venue} ({year}){role 状态标记}
arXiv：<https://arxiv.org/abs/{arxiv-id}>
paperscool：<https://papers.cool/arxiv/{arxiv-id}>
```

例:
```markdown
#### 1. WorldEdit: Towards Open-World Image Editing with a Knowledge-Informed Benchmark

作者：
Wang Lin, Feng Wang, Majun Zhang, Wentao Hu, Tao Jin (学生), Zhou Zhao, Fei Wu（吴飞）, Jingyuan Chen, Alan Yuille, Sucheng Ren

发表：arXiv preprint (2026)
arXiv：<https://arxiv.org/abs/2602.07095>
paperscool：<https://papers.cool/arxiv/2602.07095>
```

### 4.2 状态标记

| 状态 | 标记 | 含义 |
|------|------|------|
| `found` | 无 | arXiv ID + 完整作者已找到 |
| `ambiguous` | ` ⚠️` | arXiv 找到但标题相似度 < 90%, 需人工核 |
| `not_found` | ` ❓ arXiv 未找到` | arXiv 0 结果, 可能被改名/DOI 论文/中文期刊 |
| `error` | ` ❓ {error}` | HTTP 5xx/SSL/timeout, 已重试 3 次仍失败 |

### 4.3 报告 (JSON)

```json
{
  "ts": "2026-06-08T...",
  "total": 102,
  "by_status": {"found": 65, "not_found": 20, "error": 15, "ambiguous": 2},
  "papers": [
    {
      "seq": "1",
      "title_table": "WorldEdit: ...",
      "year": "2026",
      "venue": "arXiv 2602.07095",
      "arxiv_id": "2602.07095",
      "title_verified": "WorldEdit: ...",
      "authors": ["Wang Lin", ..., "Fei Wu"],
      "year_arxiv": "2026",
      "status": "found"
    },
    ...
  ]
}
```

## 5. 已知限制与对策

### 5.1 arXiv API 限流

- **官方限制**: 1 req / 3s, 不允许并发 outstanding
- **本脚本**: 强制 1 worker + `_throttle()` 函数确保间隔 ≥ 3s
- **实测**: 5 篇 + 1 次 429 重试 ≈ 18s
- **102 篇预计**: 102 × 3s + retry ≈ 8-12 分钟

### 5.2 中英混杂表头

表格有的行是中文期刊 (e.g. JCRD, Eng. Sci.) — arXiv 找不到。脚本会标 `not_found`，用户后续人工补 DOI 即可。

### 5.3 标题精确匹配

arXiv `ti:"..."` 是 literal match。若表格标题有 OCR/转写错字（如 "叶鑫海"vs"叶昕海"），会找不到。脚本会标 `not_found`，**不会**回退到模糊搜索以避免误匹配。

### 5.4 Section 7 已存在时

直接 append 会产生多个 `## 7.` 段。建议:
- 跑前先 `lark-cli docs +update --command block_delete` 删掉旧 §7
- 或改用 `--section-no 8` (脚本支持自定义)

### 5.5 飞书 doc 解析局限

`parse_papers_from_xml()` 用 regex 解析 §4 表格。如果文档结构有 h3/h4 嵌套异常 (e.g. 误用 h4 当 h3)，可能漏抽。验证: `python3 -c "import normalize as N; ..."` 后看 extracted count 是否 = 表格行数 - header rows。

## 6. 重跑安全 (idempotency)

- 脚本**始终 append** 新段到 doc 末尾，不修改现有表格
- 重跑会产生**多个** §7 段 (内容可能重复)
- 如要替换: 先 `--dry-run` 验证新输出，再手动删旧 §7，最后正式跑
- 或改 `--section-no 8/9/10` 顺序 append

## 7. 高级: 集成到 teacher-report skill 流程

`teacher-report/SKILL.md` 未来的 generate mode 可以:
1. 生成完 docx 后, **自动**调用 `normalize.py --doc {new_doc_id} --dry-run`
2. 检查报告 by_status, 若 `not_found + error > 30%` 触发 ⚠️ callout
3. 用户确认后再 `python3 normalize.py --doc {new_doc_id}` append

## 8. 故障排查

| 错误 | 原因 | 修法 |
|------|------|------|
| `lark-cli docs +fetch failed` | 飞书 auth 失效 | `lark-cli auth login` |
| `SSL: UNEXPECTED_EOF_WHILE_READING` | arXiv 出口 SSL 抖动 | 脚本已自动 retry 3 次, 通常能过 |
| `HTTP Error 429: Too Many Requests` | arXiv 限流 | 脚本已自动 sleep 10s/20s/30s, 串行模式不会触发 |
| `Max retries exceeded` | 持续 429/SSL 失败 | 加大 `--workers 1` (默认), 或稍后重试 |
| `parse_papers_from_xml` 提取数 = 0 | 表格结构异常 | 检查 doc 是否用了 v0.2.5 的 `H1` 而非 `H3` 分年 |
| Append 后 doc 出现 2 个 §7 | 重跑产生重复 | 手动删旧的 `## 7. v0.3.0 ...` 段, 或下次用 `--section-no 8` |

## 9. 参考

- v0.3.0 SKILL.md — `## Paper Entry Format (v0.3.0) — 硬要求`
- v0.3.0 report-template.md — `## 5.1 Paper Card 6 行模板`
- v0.3.0 audit-checklist.md — `## Check 13 — 论文 6 行 Paper Card 格式`
- arXiv API 文档: https://info.arxiv.org/help/api/user-manual.html
- lark-shared skill — `references/lark-doc-update.md` (gotcha 1: --content @file 相对路径)
