# SOP — v0.3.9 作者列表批量升级 (全作者中文括注)

> **作者**: claudecode + teacher-report v0.3.9
> **最后更新**: 2026-06-10
> **适用**: 任何已发布的 teacher-report docx (飞书) — 把作者列表从 v0.3.3 (仅 Fei Wu 单独标) 升级到 v0.3.9 (全作者带 `Name（中文名）` 格式)
> **背景**: v0.3.9 强化跨 paper card 一致性, 防止 LLM 在 6 节点 30+ papers 批量生成时只对高知名度作者标中文

## 0. 步骤 0: 备份 (按 SKILL.md §D 强制)

```bash
DOC="<DOC_TOKEN>"
DATE=$(date +%Y%m%d)
TEACHER="<teacher-name>"
mkdir -p /tmp/wiki-audit/backup-${DATE}-${TEACHER}
lark-cli docs +fetch --api-version v2 --doc $DOC --detail with-ids --format json \
  > /tmp/wiki-audit/backup-${DATE}-${TEACHER}/before.json
```

## 1. 步骤 1: 准备名字字典

```bash
# 检查名字字典是否存在 (535 entries, 覆盖 9 wiki 节点)
ls -la ~/.agents/skills/teacher-report/references/name-dictionary-DEPRECATED-UNMARKED.json

# 如果缺失, git pull 同步
cd ~/.agents/skills/teacher-report && git pull
```

## 2. 步骤 2: 运行 migration script (audit-only 模式)

```bash
# 先 audit-only 看现状 (不修改任何 wiki)
python3 ~/.agents/skills/teacher-report/bin/migrate.py --audit --all

# 或者 audit 单个 doc
python3 ~/.agents/skills/teacher-report/bin/migrate.py --audit <DOC_TOKEN>
```

输出示例:
```
Doc          v0.3.9     partial    placeholder  updated    unmapped
============================================================================
MqEzdtwcso2AGyxUPuCc          6          0            4          0 0
RjObd2e5qoz6qKxn1Xhc          8          0            0          0 0
```

## 3. 步骤 3: 运行 migration script (实际更新)

```bash
# 实际更新全部 9 dashboard wikis
python3 ~/.agents/skills/teacher-report/bin/migrate.py --all

# 或者更新单个 doc
python3 ~/.agents/skills/teacher-report/bin/migrate.py <DOC_TOKEN>
```

每篇 partial paper card 会:
1. 从字典查每个作者的中文名
2. 用 block_replace 添加 `Name（中文名）` 格式
3. 已 v0.3.9 完整的 paper card 跳过

## 4. 步骤 4: 验证

```bash
# 重新 audit 看效果
python3 ~/.agents/skills/teacher-report/bin/migrate.py --audit --all
```

## 5. 步骤 5: 处理 unmapped 作者

如果 audit 显示有 unmapped 作者, 编辑字典:

```bash
# 编辑字典
vim ~/.agents/skills/teacher-report/references/name-dictionary-DEPRECATED-UNMARKED.json

# 添加格式: "English Name (Last, First)": "中文名"
# 多个 surname variants 都需加:
#   "Tianle Liang": "梁天乐",
#   "Liang, Tianle": "梁天乐",
```

## 6. 注意事项

- ⚠️ **best guess 中文名**: 当前字典中部分中文名是 claudecode best guess (基于常见姓氏 + CS 领域命名习惯), **强烈建议 user 校对**。可在 audit 输出中查看 `unmapped` 列。
- 🔄 **idempotent**: 重复运行无副作用 (已 v0.3.9 的 paper card 跳过)
- 🛡️ **audit-only 默认安全**: 加 `--audit` flag 不会修改任何 wiki
- 📊 **输出统计**: 显示每个 doc 的 v0.3.9 / partial / placeholder 数量

## 7. 新建 wiki 自动应用 v0.3.9

下次 `teacher-report` skill 生成新 wiki 时, 自动按 v0.3.9 规范输出 (无需手动运行 migration):
- §Paper Entry Format v0.3.9 强制: 全作者 `Name（中文名）`
- §Output Schema v0.3.9: 作者列表 + 通讯作者 都带中文括注
- §Check 16 (v0.3.9 新增): 4 子项 a-d 验证全作者标注

## 8. 失败案例 + 回滚

如发现误改 (添加了错误的中文名):

```bash
# 从 backup 恢复
DOC="<DOC_TOKEN>"
BACKUP="/tmp/wiki-audit/backup-20260610-<teacher>/before.json"

# 用 backup 重建 doc
lark-cli docs +update --api-version v2 --doc $DOC --command overwrite --content "@${BACKUP}"
```

如字典错误, 修正后重新运行 migration script (idempotent).
