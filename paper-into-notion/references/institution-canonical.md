# Institution Canonical Mapping (per ADR-0057 v3.5, 2026-07-14)

> **目的**: arxiv-affiliations.py + institutions-judge.sh 输出统一用简写 (HKBU / USTC / HKUST / SZU / PolyU 等), 避免 group by 时 "Hong Kong Baptist University" / "HKBU" 拆成不同 group
>
> **规则**:
> - 优先匹配长 full name (e.g. "Hong Kong Baptist University" → HKBU, 不要让 "University" 通用规则吞)
> - 多个 full name 映射到同 1 个 canonical (e.g. "Google Brain" / "Google Research" / "Google DeepMind" → Google)
> - canonical 用 1-4 chars 大写 (HKBU / SZU) 或 1 词大写 (Google / Anthropic / OpenAI)
> - 不在 mapping 的机构 → 保留原 full name (Notion schema 自动加 option)

## 高校 (Universities, alpha by canonical)

| Canonical | Full name patterns (匹配任一) |
|----------|------------------------------|
| **HKBU** | Hong Kong Baptist University / 香港浸会大学 |
| **HKU** | The University of Hong Kong / 香港大学 |
| **HKUST** | Hong Kong University of Science and Technology / 香港科技大学 |
| **CUHK** | Chinese University of Hong Kong / 香港中文大学 |
| **CityU** | City University of Hong Kong / 香港城市大学 |
| **PolyU** | The Hong Kong Polytechnic University / Hong Kong Polytechnic University / 香港理工大学 |
| **HKBU-SZ** | Hong Kong Baptist University (Shenzhen) / 香港浸会大学（深圳） |
| **SZU** | Shenzhen University / 南方科技大学（SUSTech 除外）/ 深圳大学 / College of Computer Science and Software Engineering, Shenzhen University |
| **SUSTech** | Southern University of Science and Technology / 南方科技大学 |
| **PKU** | Peking University / 北京大学 |
| **THU** | Tsinghua University / 清华大学 |
| **SJTU** | Shanghai Jiao Tong University / 上海交通大学 |
| **FDU** | Fudan University / 复旦大学 |
| **ZJU** | Zhejiang University / 浙江大学 |
| **NJU** | Nanjing University / 南京大学 |
| **WHU** | Wuhan University / 武汉大学 |
| **SYSU** | Sun Yat-sen University / 中山大学 |
| **USTC** | University of Science and Technology of China / 中国科学技术大学 |
| **HIT** | Harbin Institute of Technology / 哈尔滨工业大学 |
| **CAS** | Chinese Academy of Sciences / 中国科学院 |
| **BUPT** | Beijing University of Posts and Telecommunications |
| **SCUT** | South China University of Technology / 华南理工大学 |
| **XJTU** | Xi'an Jiaotong University |
| **BIT** | Beijing Institute of Technology / 北京理工大学 |

## 国际高校

| Canonical | Full name patterns |
|----------|-------------------|
| **MIT** | Massachusetts Institute of Technology |
| **Stanford** | Stanford University |
| **CMU** | Carnegie Mellon University |
| **Princeton** | Princeton University |
| **Berkeley** | University of California, Berkeley / UC Berkeley |
| **UCLA** | University of California, Los Angeles |
| **UCSF** | University of California, San Francisco |
| **Caltech** | California Institute of Technology |
| **Cornell** | Cornell University |
| **Oxford** | University of Oxford |
| **Cambridge** | University of Cambridge |
| **Edinburgh** | University of Edinburgh |
| **ETH** | ETH Zurich / Swiss Federal Institute of Technology |

## 工业研究院 (Company Research)

| Canonical | Full name patterns |
|----------|-------------------|
| **Google** | Google Brain / Google Research / Google DeepMind / Google |
| **Anthropic** | Anthropic / anthropic.com |
| **OpenAI** | OpenAI |
| **DeepMind** | Google DeepMind (sub) / DeepMind |
| **Meta** | Meta AI / Meta Research / Facebook AI Research (FAIR) |
| **Microsoft** | Microsoft Research / Microsoft |
| **IBM** | IBM Research / IBM |
| **NVIDIA** | NVIDIA / Nvidia |
| **Apple** | Apple |
| **Huawei** | Huawei / 华为 |
| **Baidu** | Baidu / 百度 |
| **Tencent** | Tencent / 腾讯 |
| **Alibaba** | Alibaba / 阿里巴巴 / DAMO Academy |
| **SakanaAI** | Sakana AI / SakanaAI |
| **TCL** | TCL Corporate Research / TCL |
| **Salesforce** | Salesforce Research |

## 维护规则

- 匹配顺序: 长 full name 优先 (避免 "University" 通用规则误吞 "Hong Kong Baptist University")
- canonical 大小写: 全部大写 (HKBU / USTC) 或 1 词首字母大写 (Google / Anthropic)
- 不在 mapping 的机构: 保留原 full name (Notion multi_select 自动加 option, 不报错)
- 加新机构: user 决定加哪个, 改 mapping.md 然后跑 sync-institution-options.py 同步

## 反模式 (永久失效)

- ❌ "把 Hong Kong Baptist University 简写成 Hong Kong Baptist" — 不全, 丢 University
- ❌ "直接用 full name 不映射" — Notion group by 会拆成多个 group (HKBU / Hong Kong Baptist University 算 2 个)
- ❌ "用 SZU 当 Shen Zhen University 缩写" — 已被 Shen Zhen University 占用, 改 Shenzhen University

## 联动

- `scripts/arxiv-affiliations.py` v3.5 调 mapping 简写输出
- `scripts/institutions-judge.sh` v3.5 Layer 0 用 mapping
- `scripts/sync-institution-options.py` schema auto-add (Notion multi_select)
- 主仓 ADR-0057 v3.5
