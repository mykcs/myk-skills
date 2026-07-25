---
name: codex-provider-switch
description: |
  Codex CLI provider 切换 SOP (Kimi / MiniMax / Anthropic 等): config 切换步骤、
  env 变量核对、切换后验证。当用户要切换 codex provider、改 API base url、
  或排查 provider 配置漂移时触发。
license: MIT
metadata:
  version: 1.0.0
  category: utility
  author: mykcs
  migrated-from: ~/.claude/rules/codex-provider-switch.md (2026-07-25 rules 减重)
---

# 规则: Codex provider 切换 (Codex 0.144.6 直连非 OpenAI 上游必备 3 字段 + CC Switch Live Takeover 防护)

> **触发来源**: CASE-CODEX-MINIMAX-PROVIDER-FIELD-20260721 (2026-07-21 立, Codex 跑 MiniMax 失败 3 段根因 + 5 段失败路径)
> **生效**: 任何 Codex CLI / Codex desktop app 切 custom provider (直连非 OpenAI 上游，如 MiniMax / Anthropic / Gemini 等) 配置修改场景
> **强制执行**: claudecode 跑 Codex provider 切换前必跑 §3 5 字段前置验证 + §4 Codex 0.144.6 字段名硬约束

## §1. 适用范围

- **触发场景** (any-of 命中):
  - Codex CLI 跑非 OpenAI 上游 (MiniMax / Anthropic via direct / Gemini / Kimi direct 等)
  - Codex desktop app 切换 provider
  - Codex 配置从 CC Switch 代理改直连上游
- **不适用**: 用 OpenAI 官方 provider (`provider: openai` 默认)

## §2. Codex CLI 0.144.6 字段名硬约束 (3 字段必备)

Codex CLI 0.144.6 配置文件 `~/.codex/config.toml` 直连非 OpenAI 上游**必须**含以下 **3 个顶层字段 + 1 个子表**：

```toml
# 顶层 3 字段 (必备, 缺任一 → fallback OpenAI 官方)
model_provider = "custom"                            # 不是 provider, 是 model_provider
wire_api = "responses"                                # Codex 0.144.6 默认 wire_api
base_url = "https://api.<your-provider>.com/v1"      # 直连上游, 不走 CC Switch 代理

# 子表 1 个 (必备, codex 0.144.6 验证组合字段名)
[model_providers.custom]
name = "<short-name>"
base_url = "https://api.<your-provider>.com/v1"
wire_api = "responses"
requires_openai_auth = true
```

**字段名陷阱 (Codex 0.144.6 必读)**:

| ❌ 错字段名 | ✅ 正确字段名 | 后果 |
|------------|------------|------|
| `provider = "custom"` | `model_provider = "custom"` | codex 完全忽略, fallback OpenAI 官方 → 客户端连 `api.openai.com` |
| `experimental_bearer_token = "PROXY_MANAGED"` | (不写, 直接在 `OPENAI_API_KEY` env var 或 auth.json 放真 key) | codex 优先用 `experimental_bearer_token` 占位符, 走 CC Switch 代理时被覆写 |

**关键识别 (实测验)**：当 `model = "MiniMax-M3"` (从配置读) 但输出 `provider: openai` (fallback) → **缺 `model_provider` 顶层字段**。两个字段独立读取。

## §3. 5 字段前置验证 (改 config.toml 后必跑)

```bash
# 1. codex config 含 3 顶层字段 (path / model_provider / base_url / wire_api)
grep -E "^model_provider|^base_url|^wire_api" ~/.codex/config.toml

# 2. codex config 含 [model_providers.custom] 子表
grep -A 4 "^\[model_providers.custom\]" ~/.codex/config.toml

# 3. 顶层 model_provider = "custom" 不是 "openai" 也不是写错字段
test "$(grep '^model_provider' ~/.codex/config.toml | awk -F'"' '{print $2}')" = "custom" && echo "✅" || echo "❌ field wrong"

# 4. 直连上游 curl 验证 upstream 自身可达 (隔离 CC Switch 透传 bug)
curl -s -m 8 -X POST "https://api.<your-provider>.com/v1/responses" \
  -H "Authorization: Bearer ${OPENAI_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"model":"<model>","input":"hi"}' | head -c 200

# 5. codex CLI 实测端到端 (--skip-git-repo-check 必加)
codex exec "hi" --skip-git-repo-check 2>&1 | head -10
# 期望: model=<model> provider=custom + <echoed 回复>
```

## §4. CC Switch Live Takeover 防护 (settings.json 改动)

CC Switch 默认 `enableLocalProxy: true` 启用 Live Takeover 模式，**会周期性重写** `~/.codex/config.toml` 顶层字段（`model_provider` + `base_url` + `wire_api`），把 Codex 强制绑回 CC Switch 本地代理 `http://127.0.0.1:15721/v1`。

**CC Switch Codex 路径代理** 经实测有透传 bug：upstream 返 200，codex 客户端报 502。

**防护方案** (用户允许动 `~/.cc-switch/settings.json`)：

```bash
# 必先备份
TS=$(date +%Y%m%d-%H%M%S)
cp ~/.cc-switch/settings.json ~/.cc-switch/settings.json.backup.$TS

# 走 Bash + jq §A.1 SOP (per tooling/section-A) 改 enableLocalProxy = false
jq '.enableLocalProxy = false' ~/.cc-switch/settings.json > /tmp/settings.new.json \
  && mv /tmp/settings.new.json ~/.cc-switch/settings.json

# JSON validate
python3 -c "import json; json.load(open('/Users/myk/.cc-switch/settings.json'))"

# 验证
jq '.enableLocalProxy' ~/.cc-switch/settings.json
# 期望: false
```

**重启 CC Switch GUI app** 让新配置生效。

## §5. 5 IF...THEN 规则

1. **IF** Codex 自定义 provider 配置 **THEN** 必含 3 顶层字段 (`model_provider="custom"` + `wire_api="responses"` + `base_url="https://..."`) + `[model_providers.custom]` 子表 (per §2)
2. **IF** Codex 报 401 + url `api.openai.com` **THEN** 立即 grep `model_provider` 顶层字段，缺它 fallback OpenAI（不是 key 错，是字段名错）
3. **IF** Codex 报 502 + url `127.0.0.1:15721` (CC Switch 代理) **THEN** 必先 `curl` 直连 upstream 隔离 CC Switch 透传 bug，分清 upstream 200 vs 客户 502
4. **IF** Codex config 顶层字段每隔几分钟被覆写回 CC Switch 代理 **THEN** 必改 `~/.cc-switch/settings.json` 的 `enableLocalProxy=false`（用户在 `~/.cc-switch/`，允许动）+ 重启 CC Switch app
5. **IF** Codex CLI 报 `provider: openai` 但 config 有 `model = "<model>"` **THEN** 必查 `model_provider` (不是 `provider`) 顶层字段是否设对

## §6. 6 协议级反模式 (永久失效)

1. ❌ Codex 切 custom provider 用字段名 `provider = "custom"` (Codex 0.144.6 静默忽略)
2. ❌ 凭直觉猜测 Codex 配置字段名（必跑 §3 5 字段前置验证）
3. ❌ Codex 报 502 时改 OpenAI 官方 env var 来"修"（502 是 CC Switch 代理透传 bug, 不是 codex 配置问题）
4. ❌ Codex 报 401 时换 API key（401 是 fallback OpenAI 官方 + sk-cp-... 不是 OpenAI key, 是 config 字段名错）
5. ❌ codex config 反复覆写时不查 Live Takeover 模式（改 `~/.cc-switch/settings.json` 是根治）
6. ❌ 改 Codex config 不跑 `codex exec "hi" --skip-git-repo-check` 端到端验证

## §7. 联动 (cross-references)

- **Case SSOT**: `~/.claude/knowledge/cases/wiki/CASE-CODEX-MINIMAX-PROVIDER-FIELD-20260721.md` (含 5 失败路径 + 2 非平凡决策 + 3 根因)
- **ADR-0075**: `~/.claude/docs/adr/0075-codex-provider-switch-field-name.md` (整数 slot 0075 AVAILABLE per `ls ~/.claude/docs/adr/ | sort | tail` 验证)
- **§A.1 settings.json SOP**: `~/.claude/rules/tooling.md` §A (改 `~/.cc-switch/settings.json` 必跑 backup → jq → validate → diff check → atomic commit 5 件套)
- **CLAUDE.md §强约束**: 不许动 `~/.claude/` 任何文件（本规则不冲突，仅允许动 `~/.codex/` + `~/.cc-switch/`）

## §8. 历史 record

- **2026-07-21 v1.0 立**: per CASE-CODEX-MINIMAX-PROVIDER-FIELD-20260721, Codex 跑 MiniMax 直连 3 字段必备 + CC Switch Live Takeover 防护
