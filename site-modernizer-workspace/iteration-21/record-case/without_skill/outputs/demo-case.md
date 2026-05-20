---
date: 2026-05-17
status: resolved
tags: [bash, path, fnm, npm, environment]
related: []
---

# CASE-BASH-NPM-PATH-MISSING-20260517: Bash script failed because npm not in PATH

## 症状
- Bash script 执行时提示 `npm: command not found`
- 手动在终端运行正常，但脚本内调用失败
- 错误信息：`bash: npm: command not found`
- 影响范围：所有在 script 中调用 npm 的操作

## 根因
- macOS 默认 shell 不包含 fnm 管理的 Node.js 路径
- fnm 安装的 Node.js 位于 `/Users/myk/.local/share/fnm/node-versions/v22.14.0/installation/bin/`
- 该路径未加入 Bash 脚本继承的 PATH 环境变量
- 交互式 shell 因加载了 fnm 配置文件（`~/.zshrc` 或 `~/.bashrc`）而包含此路径

## 失败路径还原

### 尝试 1：直接运行脚本
**做了什么**：在脚本中直接调用 `npm run build`
**为什么失败**：脚本在非交互式环境下执行，无法访问 fnm 配置的 PATH
**误导性证据**：手动在终端执行正常，暗示 npm 已安装

### 最终生效：在脚本开头添加 PATH 扩展
**解决方案**：
```bash
export PATH=/Users/myk/.local/share/fnm/node-versions/v22.14.0/installation/bin:$PATH
```
**生效原因**：显式将 fnm 管理的 Node.js 路径加入 PATH，确保 npm 可被发现

## 非平凡技术决策

### 为什么是方案 A 而不是 B
- 方案 A：在脚本中硬编码 fnm 路径 → 优点：无需外部依赖；缺点：版本变更需手动更新
- 方案 B：使用 `fnm use` 自动切换版本 → 优点：自动管理版本；缺点：需要 fnm 在 PATH 中
- **选择 A 的核心原因**：调试场景临时修复，最小改动解决问题

### 隐性约束
- 交互式 shell 自动加载 fnm 配置，非交互式 shell 不会
- CI 环境通常使用非交互式 shell，需显式配置 PATH

## 解决(按 P0/P1/P2 优先级排序)

### P0：阻断性修复
- 在脚本开头添加 PATH 扩展：
  ```bash
  export PATH=/Users/myk/.local/share/fnm/node-versions/v22.14.0/installation/bin:$PATH
  ```

### P1：支撑性修复
- 如需跨版本兼容，可使用：
  ```bash
  export PATH="$HOME/.local/share/fnm/node-versions/v*/installation/bin:$PATH"
  ```

### P2：验证/加固
- 运行 `which npm` 确认路径正确
- 在新 shell 中验证脚本可正常执行

## 验证

### 修复前
```bash
$ which npm
npm not found
$ ./build-script.sh
bash: npm: command not found
```

### 修复后
```bash
$ export PATH=/Users/myk/.local/share/fnm/node-versions/v22.14.0/installation/bin:$PATH
$ which npm
/Users/myk/.local/share/fnm/node-versions/v22.14.0/installation/bin/npm
$ ./build-script.sh
# 正常执行
```

## 教训

### 可执行的预防规则(必须是触发式)
**IF** 在 Bash script 中调用 npm/node 但报 `command not found` **THEN** 必须在脚本开头添加 fnm 路径到 PATH，或使用 `source ~/.zshrc` 加载环境配置

**IF** 脚本在 CI 环境中失败但本地正常 **THEN** 检查 CI 是否加载了 shell 配置文件（`.bashrc` / `.zshrc`）

### 思维转变
- 从"本地能用就行"切换到"脚本需自包含环境配置"
- 交互式 shell 和非交互式 shell 的环境差异是常见踩坑点

### 建议的工程硬约束
- 在脚本头部添加 shebang 和必要的 PATH 配置
- CI 配置中添加 source 步骤加载环境变量

## 引用
- 相关文件: fnm 默认安装路径
- 相关工具: fnm (Fast Node Manager)