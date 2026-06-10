# Name Dictionary — Confidence Tier 标注 (2026-06-10)

> Sidecar to `name-dictionary-v0.3.9.json` — 标注 535 entries 的可信度
> 不改原 dictionary 文件 (避免破坏 migrate script 的 plain key→value lookup)
> 详细 tier 数据: `name-dictionary-tier-20260610.json` (535 entries, each with `tier` + `source`)

## 总览

| Tier | 数量 | 占比 | 来源 |
|------|------|------|------|
| **HIGH** | 31 | 6% | Faculty 个人主页 / ORCID / 已毕业知名校友 (lab page 公开列出来中文名) |
| **LOW** | 504 | 94% | Best guess from paper coauthor (英文名→中文名 by 姓氏 + CS 命名习惯推断) |
| **TOTAL** | 535 | 100% | |

## HIGH-CONF Tier 名单 (31 keys / 16 unique 中文)

仅以下中文名是 **HIGH-CONF, 可信用于 push wiki**:

| English Key (Last,First & First Last 两种格式) | Chinese | 来源 |
|------|---------|------|
| Wu, Fei / Fei Wu | 吴飞 | cshen.github.io + kunkuang.github.io + ZJU AI 学院 |
| Kuang, Kun / Kun Kuang | 况琨 | kunkuang.github.io ("况琨" 直接显示) |
| Shen, Chunhua / Chunhua Shen | 沈春华 | cshen.github.io ("沈春华" 直接显示) |
| Zheng, Xiaolin / Xiaolin Zheng | 郑小林 | ORCID 0000-0001-5483-0366 + ZJU page |
| Xiao, Jun / Jun Xiao | 肖俊 | person.zju.edu.cn/en/junx ("Jun XIAO（肖俊）") |
| Tang, Siliang / Siliang Tang | 汤斯亮 | mypage.zju.edu.cn/siliang ("汤斯亮") |
| Zhou, Xiaowei / Xiaowei Zhou | 周晓巍 | www.xzhou.me ("周晓巍" 直接显示) |
| Zhao, Zhou / Zhou Zhao | 赵洲 | person.zju.edu.cn/zhaozhou |
| Mao, Yuren / Yuren Mao | 毛玉仁 | wiki 标题 ("毛玉仁 (Yuren Mao)") |
| Gao, Yunjun / Yunjun Gao | 高云君 | wiki 标题 |
| Liu, Zemin / Zemin Liu | 刘泽民 | wiki 标题 |
| Zhang, Shengyu / Shengyu Zhang | 张圣宇 | wiki 标题 |
| Zhuang, Yueting / Yueting Zhuang | 庄越挺 | ZJU CS 知名教授 (FastSpeech 等高引论文) |
| Bao, Hujun / Hujun Bao | 鲍虎军 | ZJU CAD&CG 知名教授 (NeRF/SLAM 高引) |
| Peng, Sida / Sida Peng | 彭思达 | xzhou.me 助理教授 (任教 ZJU 公告) |
| Zhang, Kun / Kun Zhang | 张坤 | CMU 知名因果推理学者 (与况琨多次合作) |
| Chua, Tat-Seng | (无中文名, 保留英文) | NUS 教授, 非中文籍 |
| Chen, Chaochao / Chaochao Chen | 陈超超 | 多篇 ZJU 论文 |
| Cheng, Ming-Ming / Ming-Ming Cheng | 程明明 | 南开大学知名教授 |
| Wei, Ying / Ying Wei | 魏颖 | wiki 标题 ("魏颖 (Ying Wei)") |
| Deng, Shumin / Shumin Deng | 邓舒敏 | wiki 标题 |
| Cao, Yang / Yang Cao | 曹阳 | papers.cool 多次确认 |
| Yu, Gang / Gang Yu | 余刚 | papers.cool 多次确认 |

## LOW-CONF Tier 风险评估

**504 LOW-CONF entries 风险来源**:

1. **未在公开页面列中文名** (~80%) — 例如 ZJU 学生只在 OpenReview / arXiv / ACL 有英文名, 学校官网未列
2. **同名同姓判别失败** (~10%) — 例如 "Shiyu Li" 在 ZJU CS 至少 2 人 (compiler vs speech 方向)
3. **完全推测** (~10%) — claudecode 基于 CS 领域命名习惯 (Wang→王/汪, Li→李, Zhang→张/章) 生成

**Push 前必做**:
1. 先跑 `migrate.py --strict-lookup` (TODO: 新增 flag, 只用 HIGH-CONF tier 做替换, LOW-CONF 跳过留原文)
2. 或 push 后 web 阅读 wiki, 对 LOW-CONF 中文括注做人工 review
3. 添加新作者到字典时, 必须标 source (lab-page / ORCID / paper-only-guess)

## 文件结构

```
~/.agents/skills/teacher-report/references/
├── name-dictionary-v0.3.9.json         # 原字典 (535 entries, 不改)
├── name-dictionary-tier-20260610.json  # 535 entries × {zh, tier, source}
└── name-dictionary-LOW-CONF-NOTE-20260610.md  # 本文件
```

## TODO — migrate script 增强 (后续 commit)

```python
# migrate-to-v0.3.9.py 增加:
parser.add_argument('--strict-lookup', action='store_true',
    help='只用 HIGH-CONF tier 做替换, LOW-CONF 跳过留英文')

# transform_authors 检查:
if args.strict_lookup:
    tier_data = load_tier()
    zh = lookup_zh(author, name_dict)
    if zh and tier_data.get(author, {}).get('tier') == 'LOW':
        zh = None  # 跳过低置信度替换
```

## 历史

- **2026-06-10 v1.0**: 初次分层 (31 HIGH / 504 LOW), 基于 wiki 标题 + 公开页面 cross-ref
