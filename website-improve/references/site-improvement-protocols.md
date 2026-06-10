# Site Improvement Protocols (v3.7.0+ 下沉)

> **来源**: 从 SKILL.md v3.6.0 (2026-06-09) 拆分（v3.7.0 progressive disclosure refactor, 2026-06-10）。
> **目的**: 网站改进相关的次级协议 (跨站点依赖同步 / 触类旁通 / 学术资产库化) — 按需加载。
> **加载时机**: 多站点矩阵同步 / 触类旁通扫描 / 学术资产管理场景。

---

## 跨站点依赖同步升级

> 适用于 `repo/webs` 下的多站点矩阵（mykcs.github.io / wangrui2025.github.io / OSA / GDKVM）

**触发条件**：发现某一站点升级了共享依赖，或用户问"其他站点是否也能升级"

**执行顺序**：主站优先验证 → 批量同步逐站验证 → 禁止同时改完再验证

详见 `scan-checklist.md` §跨站点依赖同步升级。

---

## 触类旁通三层扫描协议

> 触发条件：发现构建配置/反模式/依赖问题时，或用户说"触类旁通"

- **L1**：workspace 内检查（`~/Repo/webs` 下所有站点）
- **L2**：全机器 repo 扫描
- **L3**：同类现象扫描

详见 `scan-checklist.md` §触类旁通三层扫描协议。

---

## 学术资产库化（Academic Asset Library）

> 适用于使用 `mykcs/academic` 管理学术图片的项目。

**三阶段**：academic 仓库自动 tag → 消费者项目迁移 → 统一路径管理模块

详见 `scan-checklist.md` §学术资产库化。
