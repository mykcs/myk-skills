---
date: 2026-05-17
status: resolved
tags: [bash, path, npm, fnm, node-version-manager]
related: []
---

# CASE-BASH-NPM-PATH-FNM-20260517: Bash script failed because npm not in PATH

## 症状
- Bash 脚本调用 `npm` 命令时报错：`npm: command not found`
- 错误出现在自动化脚本或 CI/CD 流程中
- 退出码：127
- 手动在终端运行 `npm` 正常，但脚本内失败

## 根因
fnm (Fast Node Manager) 安装的 Node.js 版本不在默认 PATH 中。fnm 将 Node.js 安装到用户目录 `~/.local/share/fnm/node-versions/`，该路径默认不在系统 PATH 里。脚本在非交互式 shell 中执行时，没有加载 fnm 的环境初始化脚本，导致找不到 npm。

## 失败路径还原

### 尝试 1：直接调用 npm
**做了什么**：在 Bash 脚本中直接写 `npm install`
**为什么失败**：`npm: command not found`，因为 fnm 管理的 Node.js 不在 PATH 中
**误导性证据**：手动在终端运行 `npm --version` 返回正常版本号，误以为 npm 已全局可用

### 最终生效：显式设置 PATH
**做了什么**：在调用 npm 前添加完整的 fnm Node.js bin 路径
```bash
PATH=/Users/myk/.local/share/fnm/node-versions/v22.14.0/installation/bin:$PATH
npm install
```

## 非平凡技术决策

### 为什么是直接设置 PATH 而不是 source fnm 脚本
- **方案 A：source fnm 环境脚本** → `eval "$(fnm env --use-on-cd)"` → 优点：自动切换版本 / 缺点：依赖 fnm 安装和 shell 初始化
- **方案 B：显式设置 PATH** → 硬编码 fnm 安装路径 → 优点：确定性高，无依赖 / 缺点：版本硬编码，换版本需手动更新
- **选择 B 的核心原因**：在脚本/自动化场景中需要确定性行为，显式 PATH 避免 shell 环境差异

### 隐性约束
- fnm 的 installation 目录包含所有版本，但 `node-versions/` 下可能有多个版本
- 必须使用 `installation/bin` 子路径，而不是 `node-versions/v22.14.0/bin`

## 解决

### P0：阻断性修复
在脚本中添加 fnm Node.js 路径到 PATH：
```bash
export PATH="/Users/myk/.local/share/fnm/node-versions/v22.14.0/installation/bin:$PATH"
npm install
```

### P1：环境一致性验证
确保脚本运行环境与本地终端环境一致：
```bash
# 验证 PATH 设置后 npm 可用
which npm  # 应返回 fnm 安装路径
npm --version  # 应返回版本号
```

### P2：长期方案
考虑使用 `.tool-versions` 文件配合 fnm 的自动环境变量设置，或在脚本开头统一 source fnm 环境。

## 验证

### 修复前
```bash
$ npm --version
bash: npm: command not found
$ echo $PATH
/usr/local/bin:/usr/bin:/bin  # 不包含 fnm 路径
```

### 修复后
```bash
$ PATH=/Users/myk/.local/share/fnm/node-versions/v22.14.0/installation/bin:$PATH npm --version
v22.14.0
$ which npm
/Users/myk/.local/share/fnm/node-versions/v22.14.0/installation/bin/npm
```

## 教训

### 可执行的预防规则
**IF** Bash 脚本需要调用 Node.js/npm **THEN** 必须显式设置 fnm PATH 或 source fnm 环境 **ELSE** 脚本将在非交互式 shell 中失败

**IF** 使用 fnm 管理 Node.js 版本 **THEN** 脚本中应使用 `eval "$(fnm env --use-on-cd)"` 或显式 PATH **ELSE** npm 命令将找不到

### 思维转变
- 从"本地终端可用 = 环境可用"切换到"脚本环境与终端环境可能不同"
- 非交互式 shell 不会自动加载 shell 初始化脚本（如 .bashrc, .zshrc）

### 建议的工程硬约束
- CI/CD 脚本中明确设置所有依赖工具的 PATH
- 使用容器镜像时确保包含所需的 Node.js 路径
- 添加健康检查：`command -v npm || { echo "npm not found in PATH"; exit 1; }`

## 引用
- fnm 文档: https://github.com/Schniz/fnm
- Node.js 安装路径: `/Users/myk/.local/share/fnm/node-versions/`
- Node 版本: v22.14.0