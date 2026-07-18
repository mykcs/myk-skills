#!/bin/bash
# ntn api call wrapper — fixed pattern (2026-07-19).
#
# Two failure modes the wrapper prevents:
#   1. ntn stdout buffer loss when redirect+kill — solved by `&` + watchdog (no kill on natural exit)
#   2. arg-order bug: `-X POST -d body` after `path` makes ntn treat `-d` as extra URL segment,
#      returning 400 invalid_request_url. Fix: keep `-X POST` after path, but ntn needs args
#      in PATH-first order, so pass `-X POST` BEFORE the path.
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

case "$method" in
    GET)
        { ntn api "$path" -X GET --notion-version 2026-03-11 2>&1; } > "$out" &
        ;;
    POST|PATCH)
        { ntn api "$path" -X "$method" --notion-version 2026-03-11 -d "$body" 2>&1; } > "$out" &
        ;;
    *)
        echo "usage: $0 GET|POST|PATCH <path> [body] [seconds]" >&2
        exit 2
        ;;
esac

pid=$!
for i in $(seq 1 $((sec / 2))); do
    sleep 2
    if ! kill -0 $pid 2>/dev/null; then break; fi
done
kill -9 $pid 2>/dev/null
wait $pid 2>/dev/null

if [ ! -s "$out" ]; then
    echo "ERROR: empty response (ntn may have failed silently)" >&2
    exit 1
fi
cat "$out"