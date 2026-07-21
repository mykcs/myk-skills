#!/bin/bash
# ntn api call wrapper v2 — TERM-then-KILL watchdog (per ADR-0075-b + CASE-NTN-CLI-SILENT-BUFFER-20260719)
#
# v1 → v2 升级:
#   1. watchdog `kill -9` 改为 `kill -TERM` (给 ntn 30s flush 缓冲)
#   2. 仅当 TERM 30s 后仍存活才 `kill -9` (兜底)
#   3. ntn-call.sh 已存在, 本文件拆出独立 wrapper (per deep-dive C §4)
#
# Two failure modes the wrapper prevents:
#   1. ntn v0.18.1 stdout 全缓冲 + 后台 + 重定向 → watchdog `kill -9` 直接 0 字节返
#      v2 修法: TERM 给 flush 机会, 仅超时才 KILL
#   2. arg-order bug: `-X POST -d body` after `path` makes ntn treat `-d` as extra URL segment
#
# Usage:
#   ./run-ntn.sh GET   <path> [seconds=30]
#   ./run-ntn.sh POST  <path> <json-body> [seconds=30]
#   ./run-ntn.sh PATCH <path> <json-body> [seconds=30]
#
# Output: prints response body to stdout; empty body → exit 1 with stderr message.

set +e
method="${1:-GET}"
path="$2"
body="$3"
sec="${4:-30}"

out="${NTN_OUT:-/tmp/notion-verify/resp.json}"
mkdir -p "$(dirname "$out")"
rm -f "$out"

# v2: 确保 out 文件可写 (避免 ntn 写失败 → 0 字节误判)
touch "$out"

case "$method" in
    GET)
        { ntn api "$path" -X GET --notion-version 2026-03-11; } > "$out" 2>&1 &
        ;;
    POST|PATCH)
        { ntn api "$path" -X "$method" --notion-version 2026-03-11 -d "$body"; } > "$out" 2>&1 &
        ;;
    *)
        echo "usage: $0 GET|POST|PATCH <path> [body] [seconds]" >&2
        exit 2
        ;;
esac

pid=$!

# v2 升级 watchdog: 优先 TERM 给 flush 机会, 仅超时才 KILL
# (per CASE-NTN-CLI-SILENT-BUFFER-20260719 + W4c ntn v0.19 升级协同)
TERM_WAIT=30  # TERM 后等 30s 让 ntn flush stdout buffer
for i in $(seq 1 $((sec / 2))); do
    sleep 2
    if ! kill -0 $pid 2>/dev/null; then break; fi
done

# 先 TERM
kill -TERM $pid 2>/dev/null
# 等 TERM_WAIT 秒, 给 ntn flush stdout buffer (v0.19 已解 buffer 问题, 但保留兜底)
for i in $(seq 1 $((TERM_WAIT / 2))); do
    sleep 2
    if ! kill -0 $pid 2>/dev/null; then break; fi
done

# 仅 TERM 仍不退出才 KILL (兜底, 正常路径不触发)
if kill -0 $pid 2>/dev/null; then
    kill -9 $pid 2>/dev/null
fi
wait $pid 2>/dev/null

if [ ! -s "$out" ]; then
    echo "ERROR: empty response (ntn may have failed silently, even after TERM+KILL)" >&2
    exit 1
fi
cat "$out"