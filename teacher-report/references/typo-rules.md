## 🚨 中文名字符级 typo 硬要求 (v0.10.0, 2026-06-11, 违反 = skill 协议破坏)

- **所有老师中文名必须与 L1-L4 权威来源字符级匹配** — 不接受音近/形近字变体. 权威来源 (按优先级):
  1. **Faculty 个人主页** (cshen.github.io / kunkuang.github.io / person.zju.edu.cn/...)
  2. **ORCID** (0000-0001-XXXX-XXXX)
  3. **LinkedIn URL slug** (e.g. `shumin-deng-邓淑敏-2a1b26142`)
  4. **中文期刊/专利署名** (软件学报 / 中国科学 / 发明专利)
  5. OpenReview / Semantic Scholar / papers.cool 显示的中文名
- **必查字段**: docx 文档里**每一处**老师中文名 (含 title / TL;DR / 招生偏好 / 培养模式 / 套磁信 / paper card 作者署名 等), 字符必须与权威来源 1:1 匹配
- **违规模式 (反例)**:
  - ❌ 「邓**舒**敏 (shū, comfortable)」 — 实际「邓**淑**敏 (shú, virtuous)」, 同音不同义 LLM auto-generate
  - ❌ 字段一致但字符错位 (如「**长**江」vs「**常**江」)
  - ❌ 形近字混淆 (未/末, 已/己, 仑/伦 等)
- **执行协议**:
  - **LLM 生成新 docx 前**: 必须先 L1-L4 抓取老师中文名, 写到 `references/name-dictionary-tier-*.json` 的 HIGH-CONF 段 (source 必填非 'best-guess-from-paper-coauthor')
  - **LLM 审计 docx 时**: 必跑 `python3 scripts/check_chinese_name.py --wiki-scan`, 返回 0 才算合规
  - **LLM 重排版/规范化 docx 时**: 必跑同脚本, 发现的 typo 列在 report 头部待用户决定 (避免自动改用户未确认的字段)
- **🚨 不要在 1.1. 自评 user-owned 章节上跑** — 那是用户自写, claudecode 不修改 (见 v0.9.0 硬要求)
- **同音/形近字 typo 启发式 (28 pairs)**: 已写入 `scripts/check_chinese_name.py` 的 `TYPO_PAIRS` + `NEAR_PAIRS`. LLM 推断中文名时若落在这些 pair, 必须显式标 `[unverified: 同音 X/Y 候选]` 等待用户确认
- **触发 case (2026-06-11)**: 邓舒敏 doc 28 处字符 typo, claudecode 当时 v0.2.9 反幻觉只校验了 OpenReview/arXiv 字段 (Shumin Deng 这个英文名是正确的, 但没校验中文字符级), 28 处错字穿透了所有 check
- **执行状态**: scripts/check_chinese_name.py v0.10.0 已写; 待跑全 15 wiki docs 出报告 + 等用户决定是否 batch fix


📂 **🚨 Output Discipline 硬要求 (v0.11.0, 2026-06-11, 违反 = skill 协议破坏)** → see [`references/output-discipline.md`](references/output-discipline.md) (loaded on demand)
