# ntn-call.sh — ntn public client wrapper

**Location**: `paper-into-notion/scripts/ntn-call.sh`
**Status**: stable (v1, 2026-07-19)
**Origin**: [CASE-NTN-CLI-SILENT-BUFFER-20260719.md](../../../knowledge/cases/wiki/CASE-NTN-CLI-SILENT-BUFFER-20260719.md)

## Why

`ntn api` 直接调用存在两个稳定问题（v0.18.1 实测）：

1. **stdout buffer 丢失**：当 `ntn api … > file &` + watchdog SIGKILL 时，stdout 仍驻留在 Go runtime buffer，文件落地 0 字节。修复：后台 + 自然 exit 不主动 kill。
2. **参数顺序 bug**：`-X POST -d body` 写在 `path` 之后时，ntn parser 把 `-d body` 当成 URL 段，返 400 invalid_request_url。修复：`-X METHOD` 写在 `path` 之前。

## Usage

```bash
# 3 个 verb：GET / POST / PATCH
./ntn-call.sh GET  <path> [seconds=30]
./ntn-call.sh POST <path> <json-body> [seconds=30]
./ntn-call.sh PATCH <path> <json-body> [seconds=30]

# 示例
./ntn-call.sh GET  /v1/databases/<id> | jq '.title'
./ntn-call.sh POST /v1/data_sources/<id>/query '{"page_size":50}'
./ntn-call.sh PATCH /v1/pages/<id> '{"properties":{"名称":{"title":[…]}}}'
```

输出：response body 写到 stdout；empty stdout → exit 1 + stderr `ERROR: empty response`。

## Conventions

- 默认 `seconds=30`；超过则 watchdog 强杀（可能导致 0 字节，正常调用不会触发）
- Body 必传 JSON 字符串，wrapper 自动用 `-d` 喂给 ntn
- Path 必以 `/v1/...` 开头
- Notion-Version header 写死 `2026-03-11`（per `ntn-cli.md` §1.2）

## 已被本 skill 调用方替换

TODO (跨多 session 推进):
- [ ] `scripts/add-property.sh`
- [ ] `scripts/backfill-knowledge-growth.sh`
- [ ] `scripts/field-merge.sh`
- [ ] `scripts/get-page-props.sh`
- [ ] `scripts/introspect.py`（若仍走 ntn 子进程）

迁移策略：在每个调用方加 `NTN_CALL="$(dirname "$0")/ntn-call.sh"`，把 `ntn api --method …` 替换为 `"$NTN_CALL" …`。

## 反模式 (Permanent Fail)

1. ❌ `ntn api … > file &; kill -9 $!` → 0 字节
2. ❌ `ntn api path -X POST -d body` → 400 invalid_request_url
3. ❌ `timeout 30 ntn …` → Linux only，macOS 无 `timeout` 二进制
4. ❌ `nohup ntn … &` + 提前 kill → 仍丢 buffer