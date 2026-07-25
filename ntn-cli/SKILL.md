---
name: ntn-cli
description: |
  ntn CLI 使用规范与注意事项。当用户提到 ntn、调用 ntn 命令、
  或需要配置 / 排查 ntn CLI 时触发。
license: MIT
metadata:
  version: 1.0.0
  category: utility
  author: mykcs
  migrated-from: ~/.claude/rules/ntn-cli.md (2026-07-25 rules 减重)
---

# ntn-cli Rule — Notion CLI 调用 SOP (cross-project, 2026-07-15 立)

> **触发**: 任何调用 `ntn api --method ...` 的 skill / script / automation
> **来源**: paper-into-notion v4.2 (PR #52) 实测 ntn api 偶发 30s+ 卡死, 提炼共享 SOP

## §1 硬规则 (Hard Rules)

### 1.1 ntn api 调用必走公共 client + retry + 60s timeout

```python
# 共享 client 模式 (per paper-into-notion/v4/ntn_client.py)
def ntn_call(method, path, body=None, timeout=60):
    """60s timeout + 3 retry + 统一 JSON decode error."""
    for attempt in range(3):
        try:
            r = subprocess.run(["ntn", "api", "--method", method, path, ...], timeout=timeout)
            if r.returncode != 0: continue
            return json.loads(r.stdout) if r.stdout.strip() else {}
        except (TimeoutExpired, JSONDecodeError):
            continue
    raise RuntimeError(f"ntn api {method} {path} failed after 3 retries")
```

**WHY**: ntn 内部走 OAuth + Notion REST API, 偶发 30s+ 卡死 (跟 CASE-PAGE-FIX-FABLE-2026 同源). 30s timeout 直接 crash 用户体验差, 60s + 3 retry = 总 180s 兜底.

### 1.2 每个 ntn api 端点必带 Notion-Version header

```python
cmd = ["ntn", "api", "--method", "POST",
       f"/v1/data_sources/{ds_id}/query",
       "-H", "Notion-Version: 2026-03-11",   # 必带
       "-d", json.dumps(body)]
```

**WHY**: Notion 2026-03-11 multi-source database 是当前稳定版, 不带 header 走默认旧版 = database query API (已废).

### 1.3 stderr 不污染 stdout parse

```bash
# BAD
ntn api ... > /tmp/out.json   # stderr (warn/debug) 跟 stdout 混
python3 -c "json.load(open('/tmp/out.json'))"  # parse fail

# GOOD
ntn api ... 2>/dev/null > /tmp/out.json   # 切 stderr, 只留 stdout
```

**WHY**: ntn 偶尔输出 cache/permission warning 到 stderr, 跟 stdout 拼接后 json.loads 失败 (实测 2026-07-15 schema query).

## §2 触发场景 (skill / 自动化脚本)

- ✅ paper-into-notion 跑 v4 全流程 (抓 + LLM judge + 写 Notion + verify)
- ✅ weekly-report-phd 周报同步 Notion
- ✅ teacher-report 写飞书 docx 跟 Notion dual sync (per ADR-0043)
- ✅ feishu-agent 跟 Notion 互转 (per phr-agent 集成)
- ✅ 任何 Notion automation (skill 立的脚本)

## §3 已知踩坑 + 反模式

| 反模式 | 真因 | 修法 |
|---|---|---|
| ntn api 30s timeout 直接 raise | Notion API 偶发 30s+ 卡死 | 60s + 3 retry (per §1.1) |
| stdout 含 stderr 拼 JSON parse 失败 | ntn 偶尔 warn 到 stderr | 必加 `2>/dev/null` |
| ntn api GET schema 卡 4+ min | ntn 内部 oauth state 检查 | introspect.py 不调 ntn api GET, 改 query page 反推字段 (per v4 schema.py) |
| ntn api POST 400 `XX is not a property` | db 字段名改了, code 还在用旧名 | query 1 个 page 反推 + 5min TTL schema cache (per schema.FieldMap.from_page) |

## §4 联动

- `paper-into-notion/v4/ntn_client.py` (子仓 mykcs/myk-skills, 公共 client 实现)
- `paper-into-notion/v4/paper-into-notion.py` (从 ntn_client import, 单一入口)
- `paper-into-notion/v4/verify_all_fields.py` (从 ntn_client import)
- `~/.claude/CLAUDE.md` §强约束 (跨项目稳定, 跟本规则协同)

## §5 反例 (永久失效)

- ❌ 任何 skill / script 单独 hardcoded `subprocess.run(["ntn", ...], timeout=30)` 不 retry
- ❌ schema 反推走 ntn api GET (v3.0 introspect.py 走的, 实测 4+ min 卡死)
- ❌ PATCH body 不 verify 真实字段名 (drift 第 4 次教训)
- ❌ ntn cli 走 fallback 到 hardcoded schema cache 24h (silent loss 教训, per v3.8 #50)

## §6 历史

- 2026-07-15: 立 (per paper-into-notion v4.2 PR #52 + 多次实测)
  - 触发: paper-into-notion v3.x 累积第 4 次 schema drift + v4 ntn api 偶发卡死
  - 落地: 5 IF...THEN + 4 反模式 + 1 共享 client (sub-module)
EOF