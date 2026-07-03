## 自动修复行为

### 脚本层安全修复（无破坏性）
- 删除指向不存在文件的 hook
- 清理过量的 settings.json 备份
- 重新格式化损坏的 JSON
- 将 777 权限重置为 644/755
- **Skill symlink 修复**: 物理目录 → symlink、broken symlink → 重建、missing symlink → 创建
- **Orphan 清理**: `.claude/skills/` 中存在但 `.agents/skills/` 中不存在的孤立项自动移除
- **Python**: 空 README.md 自动替换为模板、补充缺失的 requires-python

### AI 层语义修复（允许编辑）
- 合并重复规则、重写冲突段落
- 补充缺失的 Binary Assertions
- 更新陈旧的记忆引用
- **Python**: 建议统一 torch 版本、添加 lock 文件、修复 MarkupSafe 约束
