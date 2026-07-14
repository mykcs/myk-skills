#!/usr/bin/env bash
# arxiv-fetch.sh — arXiv API → JSON title/authors/abstract (per Q4 重试 3 次)
# 用法: bash arxiv-fetch.sh <ARXIV_ID>   (e.g. 1706.03762)
# 输出: JSON {"title": "...", "authors": [...], "abstract": "..."}
# 铁律: 3 次重试都失败 → exit 1 + 报错, 不写 fallback record (per Q4)

set -euo pipefail
ARXIV_ID="${1:-}"
if [ -z "$ARXIV_ID" ]; then
  echo "用法: bash arxiv-fetch.sh <ARXIV_ID>" >&2
  exit 1
fi

URL="https://export.arxiv.org/api/query?id_list=${ARXIV_ID}&max_results=1"
RATE_LIMIT="${ARXIV_RATE_LIMIT_SEC:-3}"

RESPONSE_FILE=$(mktemp)
trap 'rm -f "$RESPONSE_FILE"' EXIT

# 错峰启动 (per arXiv TOU: 全局 1 req/3s, 跑前随机 sleep 0-10s 避开累计峰值)
INITIAL_BACKOFF=$((RANDOM % 10))
[ "$INITIAL_BACKOFF" -gt 0 ] && sleep "$INITIAL_BACKOFF"

# 重试 3 次, 每次 backoff 5s/10s/20s (指数增长, per arXiv 限速)
BACKOFF=5
for i in 1 2 3; do
  if curl -fsSLG "$URL" -o "$RESPONSE_FILE" 2>/dev/null; then
    break
  fi
  echo "retry $i/3 failed for $ARXIV_ID, backoff ${BACKOFF}s..." >&2
  sleep "$BACKOFF"
  BACKOFF=$((BACKOFF * 2))
done

if [ ! -s "$RESPONSE_FILE" ]; then
  echo "❌ arXiv 抓取失败 (3 次重试 + 指数 backoff): $ARXIV_ID" >&2
  echo "💡 建议: wait 30s 后再跑, arXiv 全局限速 1 req/3s" >&2
  exit 1
fi

# ElementTree 解析 Atom XML → JSON (从 tmpfile 读, 不用 stdin 避免 heredoc 冲突)
python3 - "$RESPONSE_FILE" <<'PY'
import sys
import xml.etree.ElementTree as ET
import json

xml_path = sys.argv[1]
with open(xml_path, 'r', encoding='utf-8') as f:
    root = ET.fromstring(f.read())

ns = {'atom': 'http://www.w3.org/2005/Atom'}
entry = root.find('atom:entry', ns)
if entry is None:
    print(json.dumps({"error": "no entry"}))
    sys.exit(1)

title = entry.find('atom:title', ns).text.strip()
authors = [a.find('atom:name', ns).text for a in entry.findall('atom:author', ns)]
abstract = entry.find('atom:summary', ns).text.strip()

print(json.dumps({
    "title": title,
    "authors": authors,
    "abstract": abstract,
}, ensure_ascii=False, indent=2))
PY