# Memory 目录结构

## 位置

`~/.claude/memory/`

## 文件结构

```
memory/
├── MEMORY.md                    # 主索引（必须保持 ≤200 行）
├── user-role.md                 # 用户角色信息
├── global-context.md           # 全局上下文/偏好
├── session-insights-*.md       # 会话数据分析
├── feedback/                   # 用户反馈（触发行为规则）
│   ├── voice-input-preference.md
│   ├── agent-initiative-bounds.md
│   └── ...
├── project/                     # 项目专属记忆
│   └── sprites-gallery.md
└── knowledge/
    └── cases/
        └── wiki/              # Case 归档（已完成案例）
```

## 记忆类型

| 类型 | 说明 | 维护者 |
|------|------|--------|
| user | 用户角色、偏好 | 用户手动 |
| feedback | 触发行为的规则 | AI 自动 + 用户确认 |
| insights | 会话数据分析 | AI 自动生成 |
| project | 项目专属知识 | AI 自动 + 用户确认 |
| reference | 按需读取的参考 | 用户手动 |
| cases | 已归档案例 | AI 自动生成 |

## 加载策略

按优先级从低到高加载：
1. Library 级（共享给组织内所有人）
2. 项目记忆（通过 Git 共享）
3. Rules（通过 Git 共享）
4. 用户级（`~/.claude/memory/`）
5. 项目本地（`~/.claude/projects/<project>/memory/`）
