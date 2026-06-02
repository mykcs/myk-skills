# 触类旁通处理协议

> 详细内容参考文件。从主 SKILL.md 拆分（2026-06-02 rich-audit v2.2）。

> 触发词："触类旁通"、或发现问题但未指定 scope 时自动联想
>
> 记录位置：`~/.claude/knowledge/cascade-reports.md`（跨项目联动上下文）

## 三层行动规范

| 层 | 触发时机 | 动作 |
|----|---------|------|
| **L1** | 发现/修复问题时 | 检查同 workspace 内其他项目是否同样受影响 |
| **L2** | central 脚本变更时 | 扫描所有 git repo，确认 `~/.claude/scripts/` 下游无副本残留，全部 symlink 化 |
| **L3** | 发现新 central 脚本时 | 检查是否需要同样建立 symlink 下游分发机制 |

## Central Scripts 扫描命令

```bash
SCRIPT_NAMES=$(find ~/.claude/scripts -maxdepth 1 -type f | xargs -I{} basename {} | sort)
find ~ -maxdepth 5 -name ".git" -type d 2>/dev/null | sed 's/\/.git$//' | while read repo; do
  case "$repo" in "$HOME/.claude"|"$HOME/.claude/"*) continue ;; esac
  for name in $SCRIPT_NAMES; do
    find "$repo" -maxdepth 6 -name "$name" ! -type l 2>/dev/null | while read f; do
      echo "[COPY] $f"
    done
  done
done 2>/dev/null | grep -v "/.claude/" | sort
```

## 处理报告模板

```
### REPORT-{issue-id}-{date}
**问题**：{一句话描述}
**发现位置**：{哪个 repo/文件}
**修复**：{怎么修的}
**触类旁通三层**：
1. L1（workspace 内检查）：{同 workspace 其他项目是否受影响}
2. L2（全机器 repo 扫描）：{发现 X 处副本，已处理}
3. L3（同类现象）：{是否有其他 central 脚本存在同样问题}
```

## 自动联想规则

触发"触类旁通"时，Agent 必须：
1. 生成处理报告（填模板）
2. 依次执行 L1 → L2 → L3
3. 将结果同步到 `~/.claude/knowledge/cascade-reports.md`
