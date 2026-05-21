# Audit Patterns Reference

> 从实际运行中提取的检测模式，每个模式都附有**检测命令**，供 AI 在审计时直接运行。

## Config & Rules

### 插件目录失效检测（Plugin Directory Missing）

**现象**: 所有 hook 调用均失败，报错 `Failed to run: Plugin directory does not exist`

**根因**: hooks.json 引用了插件缓存路径，但该目录在插件卸载/升级后残留引用。

**检测命令**:
```bash
grep -r "plugins/cache" ~/.claude/settings.json ~/.claude/hooks/ 2>/dev/null | while read line; do
  path=$(echo "$line" | grep -o '/Users/[^:]*' | head -1); [ -d "$path" ] || echo "MISSING: $path"
done
```

### Hook 脚本硬编码过期插件 cache 路径检测（Stale Plugin Cache Path in Hook Scripts）

**现象**: Hook 脚本（如 `omc-orchestrator.mjs`）中硬编码了 `/plugins/cache/<vendor>/<plugin>/<version>` 路径，但该 cache 目录已被删除或插件已迁移到 marketplaces 目录。

**根因**: 插件升级后 cache 目录被清理，但 hook 脚本中的硬编码路径未同步更新。与 `hooks.json` 中的引用不同，这种硬编码不会触发框架的自动重建机制。

**检测命令**:
```bash
grep -rn "/plugins/cache/" ~/.claude/hooks/ --include="*.sh" --include="*.mjs" --include="*.js" --include="*.py" --include="*.json" 2>/dev/null | while read line; do
  path=$(echo "$line" | grep -o '/Users/[^"'"'"'\s]*' | head -1)
  [ -d "$path" ] || echo "STALE_CACHE_REF: $line"
done
```

**修复建议**:
1. 找到插件的实际安装位置（通常在 `~/.claude/plugins/marketplaces/` 下）
2. 更新 hook 脚本中的硬编码路径为实际路径
3. 或改用动态路径解析（如读取 `installed_plugins.json`）

### 权限剧场检测（Permission Theater）

**现象**: `~/.claude.json` 与 `~/.claude/.claude.json` 的 `allowedTools` 不一致，导致自动同意授权未实际生效。

**检测命令**:
```bash
diff <(jq -S '.allowedTools' ~/.claude.json 2>/dev/null) <(jq -S '.allowedTools' ~/.claude/.claude.json 2>/dev/null) && echo "MATCH" || echo "MISMATCH"
```

### ECC Fact-Forcing Gate 检测

**现象**: 每次 session 的第一次 Bash/Edit/Write 命令被阻塞，报错插件目录不存在。

**检测命令**:
```bash
grep -q "gateguard-fact-force" ~/.claude/settings.json && echo "PROTECTED" || echo "MISSING: ECC_DISABLED_HOOKS"
```

### 插件残留检测（Plugin Residue）

**检测命令**:
```bash
jq -r '.[] | .installPath' ~/.claude/plugins/installed_plugins.json 2>/dev/null | while read p; do [ -d "$p" ] || echo "ORPHAN: $p"; done
find ~/.claude/plugins/cache -mindepth 1 -maxdepth 2 -type d 2>/dev/null | while read d; do basename "$d" | grep -qvf <(jq -r '.[].version' ~/.claude/plugins/installed_plugins.json 2>/dev/null) && echo "UNREGISTERED: $d"; done
```

### 插件版本漂移检测（Plugin Version Drift）

**检测命令**:
```bash
jq -r '.[] | "\(.version) \(.installPath)"' ~/.claude/plugins/installed_plugins.json 2>/dev/null | while IFS=' ' read -r ver path; do
  dir=$(dirname "$path")
  actual=$(basename "$path")
  [ "$ver" = "$actual" ] || echo "DRIFT: recorded=$ver actual=$actual in $dir"
done
```

### fnm 懒加载破坏 MCP 检测

**检测命令**:
```bash
grep -l "_fnm_lazy_load" ~/.zshrc ~/.bashrc 2>/dev/null && echo "FOUND: fnm lazy load detected" || echo "OK"
```

### Skill 目录 Symlink 一致性检测（Skill Directory Symlink Consistency）

**现象**: `.claude/skills/` 中存在物理目录或 broken symlink，或 `.agents/skills/` 中的 skill 未暴露给 Claude Code。

**根因**: `.agents/skills/` 是 skill 管理的物理 source of truth（有 `.skill-lock.json`），Claude Code 通过 `.claude/skills/` 扫描加载。两者不一致会导致：修改了 skill 但 Claude Code 加载的是旧版本；或 skill 安装后无法使用。

**检测命令**:
```bash
echo "=== Physical directories in .claude/skills/ (should be 0) ==="
find ~/.claude/skills -maxdepth 1 -type d | grep -v "^/Users/.*/.claude/skills$" | while read d; do echo "[PHYSICAL] $d"; done

echo "=== Broken symlinks in .claude/skills/ (should be 0) ==="
find ~/.claude/skills -maxdepth 1 -type l | while read l; do [ -e "$l" ] || echo "[BROKEN] $l -> $(readlink $l)"; done

echo "=== Missing in .claude/skills/ (skill exists in .agents but no symlink) ==="
ls ~/.agents/skills/ | while read name; do [ -e ~/.claude/skills/"$name" ] || echo "[MISSING] $name"; done

echo "=== Orphan in .claude/skills/ (exists in .claude but not in .agents) ==="
ls ~/.claude/skills/ | while read name; do [ -e ~/.agents/skills/"$name" ] || echo "[ORPHAN] $name"; done
```

**修复建议**:
1. **物理目录 → symlink**: `mv ~/.claude/skills/{name} ~/.agents/skills/ && ln -s ~/.agents/skills/{name} ~/.claude/skills/{name}`
2. **broken symlink → 重新创建**: `rm ~/.claude/skills/{name} && ln -s ~/.agents/skills/{name} ~/.claude/skills/{name}`
3. **missing symlink → 创建**: `ln -s ~/.agents/skills/{name} ~/.claude/skills/{name}`
4. **orphan entry → 确认是否迁移**: 若应纳入管理则 `mv ~/.claude/skills/{name} ~/.agents/skills/ && ln -s ~/.agents/skills/{name} ~/.claude/skills/{name}`，否则直接删除

### BATCH MODE 文档-实现同步检测

**检测命令**:
```bash
grep -q "BATCH MODE\|\.autopush-batch-mode" ~/.claude/scripts/smart-autopush.sh && echo "IMPLEMENTED" || echo "MISSING: BATCH MODE in smart-autopush.sh"
```

### Git 运行时污染检测

**检测命令**:
```bash
for pattern in ".omc/state" "homunculus" "logs" "plugins/cache" ".scheduled_tasks.lock"; do
  grep -q "$pattern" ~/.claude/.gitignore || echo "MISSING: $pattern in .gitignore"
done
```

### 规则文件 Binary Assertions 缺失检测

**检测命令**:
```bash
find ~/.claude/rules -name "*.md" 2>/dev/null | while read f; do
  if ! grep -q "Binary Assertions" "$f"; then
    echo "NO_BINARY_ASSERTIONS: $f"
  elif ! grep -q "\[x\]" "$f"; then
    echo "EMPTY_BINARY_ASSERTIONS: $f"
  fi
done
```

### Memory Index 漂移检测

**检测命令**:
```bash
grep -h '\]\([^)]*\.md\)' ~/.claude/memory/MEMORY.md 2>/dev/null | sed 's/.*](\([^)]*\)).*/\1/' | while read path; do
  full="${path/#~\/.claude/$HOME/.claude}"
  [ -f "$full" ] || echo "INDEX_DRIFT: $path"
done
```

### Scheduled Tasks Lock 文件污染检测

**检测命令**:
```bash
lock=~/.claude/scheduled_tasks.lock
[ -f "$lock" ] && find "$lock" -mtime +1 2>/dev/null | grep -q . && echo "STALE_LOCK: $(stat -f %Sm -t %Y-%m-%dT%H:%M "$lock" 2>/dev/null || echo 'unknown age')" || echo "OK: lock file fresh or absent"
```

### Skill 目录失效 symlink 检测

**检测命令**:
```bash
find ~/.claude/skills -maxdepth 1 -type l 2>/dev/null | while read link; do
  target=$(readlink "$link")
  [ -e "$target" ] || echo "BROKEN_SYMLINK: $link -> $target"
done
```

### .agents/skills/ Git 备份检测

**现象**: `.agents/skills/` 不是 git repo，skill 修改没有版本控制；或有未提交变更；或最后一次 push 超过 7 天。

**根因**: `.agents/skills/` 是 skill 的物理 source of truth，但它不在 `~/.claude/` 的 git repo 内。如果不独立备份，SKILL.md 更新、case 归档等修改可能丢失。

**检测命令**:
```bash
# 1. Git repo 存在性
[ -d ~/.agents/skills/.git ] || echo "MISSING_GIT: .agents/skills/ is not a git repo"

# 2. 未提交变更
unc=$(git -C ~/.agents/skills status --short 2>/dev/null | wc -l | tr -d ' ')
[ "$unc" -gt 0 ] && echo "UNCOMMITTED: $unc files in .agents/skills/"

# 3. 最后一次提交距今天数
days=$(git -C ~/.agents/skills log -1 --format=%ct 2>/dev/null | awk "{print int((\"$(date +%s)\" - \$1) / 86400)}")
[ -n "$days" ] && [ "$days" -gt 7 ] && echo "STALE_BACKUP: .agents/skills/ last commit was ${days}d ago"
```

**修复建议**:
```bash
cd ~/.agents/skills
git init
git remote add origin https://github.com/mykcs/myk-skills || true
~/.claude/scripts/smart-autopush.sh ~/.agents/skills "chore(skills): sync all skills" done
```

### settings.json 权限错误检测

**检测命令**:
```bash
for f in ~/.claude/settings.json ~/.claude/.claude.json ~/.claude.json; do
  [ -f "$f" ] || continue
  perm=$(stat -f %Lp "$f" 2>/dev/null)
  [ "$perm" = "644" ] || [ "$perm" = "600" ] && echo "OK: $f ($perm)" || echo "BAD_PERMS: $f ($perm)"
done
```

### MCP Server 名称冲突检测

**现象**: `/doctor` 报告 `MCP server "X" skipped — same command/URL as already-configured "X"`。多个插件注册了同名的 MCP server。

**根因**: 插件市场独立插件的 `.mcp.json` 中注册的 server 名称与另一个插件（如 `everything-claude-code`）内置的 MCP server 同名。Claude Code 的 MCP server 注册是全局命名空间，不允许同名共存。

**检测命令**:
```bash
python3 -c "
import json, glob, os
from pathlib import Path

servers = {}  # name -> [(plugin, source)]
plugins_dir = Path.home() / '.claude/plugins'

# 1. 扫描所有插件的 .mcp.json
for mcp_file in plugins_dir.rglob('.mcp.json'):
    plugin_name = mcp_file.parent.name
    try:
        data = json.loads(mcp_file.read_text())
        for name in data.get('mcpServers', {}).keys():
            servers.setdefault(name, []).append((plugin_name, str(mcp_file)))
    except Exception:
        pass

# 2. 扫描 installed_plugins.json 中的内置 server
installed = plugins_dir / 'installed_plugins.json'
if installed.exists():
    try:
        ip = json.loads(installed.read_text())
        for plugin_name, entries in ip.get('plugins', {}).items():
            for entry in entries:
                install_path = entry.get('installPath', '')
                mcp_file = Path(install_path) / '.mcp.json'
                if mcp_file.exists():
                    data = json.loads(mcp_file.read_text())
                    for name in data.get('mcpServers', {}).keys():
                        servers.setdefault(name, []).append((plugin_name, str(mcp_file)))
    except Exception:
        pass

# 3. 报告冲突
for name, sources in servers.items():
    if len(sources) > 1:
        print(f'MCP_CONFLICT: server \"{name}\" registered by {len(sources)} plugins:')
        for plugin, path in sources:
            print(f'  - {plugin}: {path}')
"
```

**修复建议**:
1. 优先保留综合 MCP 聚合器（如 `everything-claude-code`），清理独立重复插件
2. 清理时必须同时检查并清除全部六个持久化来源：`settings.json` enabledPlugins、`settings.local.json`、`installed_plugins.json`、`plugin-catalog-cache.json`、`marketplace.json`、物理缓存目录
3. 清理后执行 `/reload-plugins` 并再次 `/doctor` 确认零 errors

### installed_plugins.json 多源一致性检测

**现象**: `installed_plugins.json` 中的 `installPath` 指向已不存在的 `plugins/cache/` 目录，或版本与 `marketplace.json` / submodule tag 不一致。

**根因**: 插件从 `cache/` 迁移到 `marketplaces/` 后，注册表未同步更新；或手动 submodule 升级后未更新注册表版本字段。

**检测命令**:
```bash
python3 -c "
import json
from pathlib import Path

plugins_dir = Path.home() / '.claude/plugins'
installed = plugins_dir / 'installed_plugins.json'
marketplace = plugins_dir / 'marketplaces/claude-plugins-official/.claude-plugin/marketplace.json'
catalog = plugins_dir / 'plugin-catalog-cache.json'

issues = []

# 1. installed_plugins.json cache 路径有效性
if installed.exists():
    ip = json.loads(installed.read_text())
    for plugin_name, entries in ip.get('plugins', {}).items():
        for entry in entries:
            path = entry.get('installPath', '')
            if 'cache/' in path and not Path(path).exists():
                issues.append(f'STALE_CACHE_PATH: {plugin_name} -> {path}')

# 2. marketplace.json 一致性
if marketplace.exists() and installed.exists():
    mp = json.loads(marketplace.read_text())
    mp_ids = {p.get('id') or p.get('name') for p in mp.get('plugins', [])}
    ip_ids = set()
    for entries in ip.get('plugins', {}).values():
        for entry in entries:
            ip_ids.add(entry.get('id') or entry.get('name'))
    # 检测 installed 中有但 marketplace 中没有的条目
    for pid in ip_ids - mp_ids:
        issues.append(f'ORPHAN_IN_INSTALLED: {pid} not in marketplace.json')

# 3. catalog-cache 一致性
if catalog.exists():
    cat = json.loads(catalog.read_text())
    cat_ids = {p.get('id') or p.get('name') for p in cat.get('plugins', [])}
    for pid in ip_ids - cat_ids:
        issues.append(f'CATALOG_LAG: {pid} in installed but not in catalog-cache')

for i in issues:
    print(i)
"
```

### 副作用 Skill 文档完备性检测

**现象**: 设置了 `disable-model-invocation: true` 的 skill，其 SKILL.md 未说明正确的替代调用方式，导致用户困惑。

**根因**: 安全设计（防止 Agent 自主执行副作用操作）与用户体验设计脱节。用户不知道不能通过 `/skill-name` 调用，也不知道应该直接说自然语言指令。

**检测命令**:
```bash
python3 -c "
import re
from pathlib import Path

skills_dir = Path.home() / '.claude/skills'
for skill_dir in skills_dir.iterdir():
    if not skill_dir.is_dir():
        continue
    skill_md = skill_dir / 'SKILL.md'
    if not skill_md.exists():
        continue
    content = skill_md.read_text()
    
    # 检查是否设置了 disable-model-invocation
    if 'disable-model-invocation: true' not in content:
        continue
    
    # 检查是否有调用方式说明
    has_invocation_guide = any(kw in content for kw in [
        '调用方式', 'Invocation', 'how to use', 'correct usage',
        '不能通过', 'cannot be used with Skill tool', '直接说', 'say directly'
    ])
    
    if not has_invocation_guide:
        print(f'MISSING_INVOCATION_GUIDE: {skill_dir.name} (has disable-model-invocation but no usage guide)')
"
```

**修复建议**:
1. 在 SKILL.md 标题后第一段添加"调用方式（重要）"章节
2. 说明：为什么不能 `/` 调用（具体副作用：push/备份/部署）
3. 说明：正确用法（直接说自然语言指令）
4. 提供 2-3 个示例话术

### MEMORY.md Phantom Rules 检测

**现象**: MEMORY.md 的 Rules 表或 Reference 区引用了物理不存在的规则文件或案例文件。

**根因**: 从 CLAUDE.md 或历史记录中复制规则名称到索引表，但未验证物理存在性；或文件被归档/删除后索引未同步更新。

**检测命令**:
```bash
python3 -c "
import re
from pathlib import Path

memory_md = Path.home() / '.claude/memory/MEMORY.md'
if not memory_md.exists():
    exit(0)

content = memory_md.read_text()
base_dir = memory_md.parent

# 提取 markdown 链接，正确解析相对路径
links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
for text, path in links:
    # 跳过外部 URL
    if path.startswith('http'):
        continue
    # 跳过锚点
    if path.startswith('#'):
        continue
    # 处理相对路径
    link_path = Path(path)
    if not link_path.is_absolute():
        link_path = base_dir / link_path
    if not link_path.exists():
        print(f'PHANTOM_ENTRY: {text} -> {path} (resolved to {link_path})')
"
```

**修复建议**:
1. 索引必须可信：宁可少列，不可列错
2. 修复前必须先用 `ls` 或 `os.path.exists` 物理验证每个条目
3. 归档文件不应出现在活跃索引中，用"见 archive/"说明替代

## Cases & Memory

### Ghost Case 引用检测

**检测命令**:
```bash
grep -h "^related:" ~/.claude/knowledge/cases/wiki/CASE-*.md 2>/dev/null | sed 's/related: \[\(.*\)\]/\1/' | tr ',' '\n' | sed 's/\[//g;s/\]//g;s/ //g' | grep -v "^$" | sort -u | while read ref; do
  [ -f "$(find ~/.claude/knowledge/cases -name "${ref}*.md" 2>/dev/null | head -1)" ] || echo "GHOST: $ref"
done
```

### Frontmatter 日期不匹配检测

**检测命令**:
```bash
find ~/.claude/knowledge/cases/wiki -name "CASE-*.md" 2>/dev/null | while read f; do
  fname_date=$(echo "$f" | grep -o '[0-9]\{8\}' | head -1)
  front_date=$(awk '/^date:/{print $2; exit}' "$f")
  [ -n "$fname_date" ] && [ -n "$front_date" ] && [ "$fname_date" != "${front_date//-/}" ] && echo "MISMATCH: $f (file=$fname_date front=$front_date)"
done
```

## OMC & Ecosystem

### OMC HUD 冷启动检测

**检测命令**:
```bash
output=$(jq -r '.hud.outputFile' ~/.claude/settings.json 2>/dev/null); [ -f "$output" ] && [ ! -s "$output" ] && echo "EMPTY: $output" || echo "OK: $output"
```

### 多窗口并行整合检查

**检测命令**:
```bash
cd ~/.claude && git log --oneline -5 && echo "---" && git diff --name-status HEAD~3..HEAD
```

## False Positive 修复模式

> 来自 CASE-RICH-AUDIT-FP-FIXES 的经验总结

### 注释行未过滤导致误报

**现象**: grep 命中了注释行中的防御性代码（如 `# NEVER use git add -A`），导致误报 `git add -A` 使用。

**根因**: 全文本匹配未排除 `#` 开头的注释行。

**检测命令**:
```bash
# 危险模式检测必须先排除注释行
grep -rn "git add -A\|git reset\|chmod 777" --include="*.sh" \
  | grep -v "^[^:]*:[^:]*:#" | grep -v "^[^:]*:#" \
  | while read line; do
    # 进一步验证：跳过以 # 开头或包含 # 的行
    if ! echo "$line" | grep -qE "^[^:]*:[^:]*\s+#"; then
      echo "PATTERN_FOUND: $line"
    fi
  done
```

### Markdown 相对路径解析 bug

**现象**: `MEMORY.md` 中 `[text](path)` 的 link_path 被 CWD 而非文件所在目录解析，导致所有相对链接报为 missing。

**根因**: 对相对路径直接用 `Path(raw)`，未处理 base dir。

**检测命令**:
```bash
# 正确解析 Markdown 相对路径：以被扫描文件的父目录为 base
python3 -c "
import re
from pathlib import Path

md_file = Path('~/.claude/memory/MEMORY.md').expanduser()
content = md_file.read_text()
links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
for text, path in links:
    link_path = Path(path)
    if not link_path.is_absolute():
        link_path = md_file.parent / link_path
    if not link_path.exists():
        print(f'INDEX_DRIFT: {path} (resolved to {link_path})')
"
```

### 插件 Managed Cache 误判

**现象**: 插件系统会在检测到缺失缓存时自动重新下载，导致孤儿目录反复出现。

**根因**: 未区分"真正的 orphan"和"插件自动重建的 managed cache"。

**检测命令**:
```bash
# 真正的 orphan：不在 installed_plugins.json 注册，且非 submodule
jq -r '.[] | .installPath' ~/.claude/plugins/installed_plugins.json 2>/dev/null | \
  while read p; do [ -d "$p" ] || echo "ORPHAN_REG: $p"; done

# registered 但 cache 被清空的目录（managed cache，会自动重建）
find ~/.claude/plugins/cache -mindepth 1 -maxdepth 2 -type d 2>/dev/null | \
  while read d; do
    basename "$d" | grep -qvf <(jq -r '.[].version' ~/.claude/plugins/installed_plugins.json 2>/dev/null) \
      && echo "MANAGED_CACHE_REBUILD: $d (will auto-rebuild, not a true orphan)"
  done
```

## GitHub Actions 依赖版本检查

**现象**: GitHub Actions workflow 中的 action 版本过旧，存在已知安全漏洞或已被弃用。

**触发条件**: 检测到 `.github/workflows/*.yml` 或 `.github/workflows/*.yaml`。

**常见过时版本**:
| Action | 过时版本 | 推荐版本 |
|--------|----------|---------|
| `actions/cache` | v3, v4 | v5 |
| `actions/upload-pages-artifact` | v3, v4 | v5 |
| `actions/download-pages-artifact` | v3, v4 | v5 |
| `pnpm/action-setup` | v3, v4 | v6 |
| `actions/setup-node` | v3, v4 | v5 |
| `actions/checkout` | v3 | v5 |
| `azure/login` | v1 | v2 |
| `google-github-actions/auth` | v1 | v2 |
| `aws-actions/configure-aws-credentials` | v3 | v4+ |

**检测命令**:
```bash
# 扫描所有 workflow 文件，检查 action 版本（正向匹配过时版本）
# @v[34]($|[^0-9]) 匹配 v3/v4 后面是行尾或非数字字符（防止匹配 v34/v40 等）
for f in .github/workflows/*.yml .github/workflows/*.yaml; do
  [ -f "$f" ] || continue
  # actions/cache: 检测 v3/v4（当前是 v5）
  grep -n "actions/cache@" "$f" | grep -E "@v[34]($|[^0-9])" && echo "OUTDATED: actions/cache"
  # pnpm/action-setup: 检测 v3/v4/v5（当前是 v6）
  grep -n "pnpm/action-setup@" "$f" | grep -E "@v[345]($|[^0-9])" && echo "OUTDATED: pnpm/action-setup"
  # actions/checkout: 检测 v3/v4（当前是 v5）
  grep -n "actions/checkout@" "$f" | grep -E "@v[34]($|[^0-9])" && echo "OUTDATED: actions/checkout"
  # actions/setup-node: 检测 v3/v4（当前是 v5）
  grep -n "actions/setup-node@" "$f" | grep -E "@v[34]($|[^0-9])" && echo "OUTDATED: actions/setup-node"
  # upload-pages-artifact: 检测 v3/v4（当前是 v5）
  grep -n "actions/upload-pages-artifact@" "$f" | grep -E "@v[34]($|[^0-9])" && echo "OUTDATED: upload-pages-artifact"
  # download-pages-artifact: 检测 v3/v4（当前是 v5）
  grep -n "actions/download-pages-artifact@" "$f" | grep -E "@v[34]($|[^0-9])" && echo "OUTDATED: download-pages-artifact"
done
```

**修复建议**:
```yaml
# actions/cache: v4 → v5
- uses: actions/cache@v5

# pnpm/action-setup: v4 → v6
- uses: pnpm/action-setup@v6

# actions/checkout: v4 → v5
- uses: actions/checkout@v5

# actions/setup-node: v4 → v5
- uses: actions/setup-node@v5
```

**为何重要**: 过时的 GitHub Actions 版本可能包含已知漏洞（CVEs）、缺失的性能优化，或在 GitHub 弃用后导致 build 失败。

## Python / ML 项目审计

### Torch 版本 CVE 检测

**自动修复**: 检测到 torch < 2.5.0 时，建议升级到 2.6.0 并使用 `pip install torch==2.6.0 --index-url https://download.pytorch.org/whl/cu124`

### WandB API Key 硬编码检测

**自动修复**: 将 wandb key 替换为环境变量引用 `os.environ.get("WANDB_API_KEY")`

### MarkupSafe 版本冲突

**自动修复**: 移除 `<3.0.0` 上界约束

**现象**: torch < 2.5.0 存在已知安全漏洞。

**检测命令**:
```bash
python3 -c "
import sys
try:
    import torch
    v = torch.__version__.split('.')
    major, minor = int(v[0]), int(v[1])
    if major < 2 or (major == 2 and minor < 5):
        print('VULNERABLE: torch < 2.5.0')
    else:
        print('OK: torch >= 2.5.0')
except:
    print('SKIP: torch not installed')
"
```

### WandB API Key 硬编码检测

**现象**: wandb login key 直接写在代码中，存在泄露风险。

**检测命令**:
```bash
# 高置信度 pattern：sk- 开头的 key
grep -rn "sk-[a-zA-Z0-9]\{20,\}" --include="*.py" --include="*.sh" \
  --exclude-dir=".venv" --exclude-dir="venv" | \
  grep -v "^[^:]*:#" | grep -v "^[^:]*:import" | \
  while read line; do
    echo "SECRET_FOUND: $line"
  done
```

### MarkupSafe 版本冲突

**现象**: `MarkupSafe>=2.1.5,<3.0.0` 会导致 torch 2.6.0 安装失败。

**检测命令**:
```bash
grep -i "markupsafe" pyproject.toml requirements.txt 2>/dev/null && \
echo "MARKUPSAFE_CONSTRAINT: potential conflict with torch 2.6.0"
```

### CUDA 版本不一致

**现象**: 不同项目使用不同的 CUDA 编译版本（cu118 vs cu124），导致 GPU 利用率差异。

**检测命令**:
```bash
grep -A5 "torch" pyproject.toml 2>/dev/null | grep -i "cu118\|cu124\|cu126" || echo "NO_CUDA_INDEX"
```

### README 空洞检测

**现象**: README.md 只有 "Add your description here" 模板内容。

**检测命令**:
```bash
if [ -f "README.md" ]; then
    line_count=$(wc -l < README.md)
    placeholder_count=$(grep -ci "add your description\|todo\|tbd\|placeholder" README.md 2>/dev/null || echo 0)
    [ "$line_count" -lt 20 ] || [ "$placeholder_count" -gt 2 ] && echo "INCOMPLETE: README needs attention"
fi
```

### Type Checker 缺失

**现象**: 无 pyright/mypy 配置，Python 类型检查缺失。

**检测命令**:
```bash
grep -q "tool.pyright\|tool.mypy" pyproject.toml 2>/dev/null || \
echo "TYPE_CHECKER: missing (recommend adding pyright or mypy)"
```

## Meta-Audit

rich-audit 自身也必须被审计。每次运行时检查：

1. **扫描范围完整性**：`~/.claude/rules/` 是否被包含在扫描路径中？
2. **量化阈值存在性**：是否有数字红线（如"规则总行数 ≤ 200"）？
3. **基准对比机制**：是否有外部来源的对比表？
4. **架构 vs 故障**：是否同时检查"点故障"和"面健康"？

**检测命令**:
```bash
grep -q "架构健康度\|Architecture Health\|规则总行数\|max_total_rules_lines" ~/.claude/skills/rich-audit/SKILL.md 2>/dev/null && echo "ARCHITECTURE_CHECK: OK" || echo "ARCHITECTURE_CHECK: MISSING"
grep -q "外部基准\|Benchmark\|Anthropic\|社区最佳实践" ~/.claude/skills/rich-audit/SKILL.md 2>/dev/null && echo "BENCHMARK_CHECK: OK" || echo "BENCHMARK_CHECK: MISSING"
```
