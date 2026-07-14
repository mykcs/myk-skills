#!/usr/bin/env bash
# add-property.sh — 给 Notion data source 加 1 个 property
#
# 用法:
#   bash add-property.sh <data_source_id> <property_name> <type> [options_json]
#
# 参数:
#   data_source_id  : Notion data source UUID (e.g. 39dfedee-6267-807a-bcb2-000ba858dff2)
#   property_name   : property 名称 (e.g. "link" / "亮点" / "模态类型")
#   type            : url | rich_text | select | multi_select | status | date | number | checkbox
#   options_json    : 可选, select/multi_select/status 时必传 (JSON array of {name,color})
#                      例: '[{"name":"arXiv","color":"blue"}]'
#
# 输出 (stdout):
#   "✅ <name> added  total: <N>  options: [...]"
#
# 退出码:
#   0 = 成功
#   1 = API 报错 (参数错 / 权限错 / 校验错)
#   2 = 参数解析错
#
# 例子:
#   bash add-property.sh 39dfedee-... "link" "url"
#   bash add-property.sh 39dfedee-... "模态类型" "select" '[{"name":"arXiv","color":"blue"}]'
#   bash add-property.sh 39dfedee-... "状态" "status" '[{"name":"未开始","color":"default"}]'
#
# 来源: CASE-PAPER-INTO-NOTION-CROSS-DB-SCHEMA-MIGRATION-20260714 (踩坑 1)
#       跟 docs "Notion API 不支持 add property" 矛盾, 2025-09 release 后 PATCH 支持
# 协议: v2.6.30 §I self-evolution (skill 升级时拆小可复用单元)

set -euo pipefail

DS_ID="${1:-}"
PROP_NAME="${2:-}"
PROP_TYPE="${3:-}"
OPTIONS_JSON="${4:-}"

# 参数校验
if [ -z "$DS_ID" ] || [ -z "$PROP_NAME" ] || [ -z "$PROP_TYPE" ]; then
  echo "❌ 参数不完整" >&2
  echo "用法: bash add-property.sh <data_source_id> <property_name> <type> [options_json]" >&2
  echo "  type: url | rich_text | select | multi_select | status | date | number | checkbox" >&2
  exit 2
fi

# type 映射
case "$PROP_TYPE" in
  url)         TYPE_CONFIG='{"url":{}}' ;;
  rich_text)   TYPE_CONFIG='{"rich_text":{}}' ;;
  date)        TYPE_CONFIG='{"date":{}}' ;;
  number)      TYPE_CONFIG='{"number":{}}' ;;
  checkbox)    TYPE_CONFIG='{"checkbox":{}}' ;;
  status)      TYPE_CONFIG='{"status":{}}' ;;
  select)      TYPE_CONFIG='{"select":{}}' ;;
  multi_select) TYPE_CONFIG='{"multi_select":{}}' ;;
  *)
    echo "❌ 不支持的 type: $PROP_TYPE" >&2
    echo "  支持: url | rich_text | select | multi_select | status | date | number | checkbox" >&2
    exit 2
    ;;
esac

# select / multi_select / status 必传 options
if [[ "$PROP_TYPE" =~ ^(select|multi_select|status)$ ]]; then
  if [ -z "$OPTIONS_JSON" ]; then
    echo "❌ $PROP_TYPE 必传 options_json" >&2
    echo "  例子: '[{\"name\":\"arXiv\",\"color\":\"blue\"}]'" >&2
    exit 2
  fi
  # 验证 options JSON
  if ! echo "$OPTIONS_JSON" | python3 -c "import json, sys; json.load(sys.stdin)" 2>/dev/null; then
    echo "❌ options_json 不是合法 JSON" >&2
    exit 2
  fi
  # 注入 options
  TYPE_CONFIG=$(echo "$TYPE_CONFIG" | python3 -c "
import json, sys
cfg = json.load(sys.stdin)
opts = json.loads('''$OPTIONS_JSON''')
key = list(cfg.keys())[0]
cfg[key] = {'options': opts}
print(json.dumps(cfg))
")
fi

# 构造 payload
PAYLOAD=$(python3 -c "
import json
print(json.dumps({'properties': {'$PROP_NAME': json.loads('''$TYPE_CONFIG''')}}))
")

# PATCH 请求
RESPONSE=$(ntn api "/v1/data_sources/$DS_ID" -X PATCH -d "$PAYLOAD" 2>&1)

# 解析 response
RESULT=$(echo "$RESPONSE" | python3 -c "
import json, sys
raw = sys.stdin.read()
start = raw.find('{')
if start < 0:
    print('ERROR:no_json:' + raw[:200])
    sys.exit(1)
try:
    d = json.loads(raw[start:])
    if d.get('object') == 'error':
        print('ERROR:' + d.get('code', 'unknown') + ':' + d.get('message', '')[:200])
        sys.exit(1)
    props = d.get('properties', {})
    if '$PROP_NAME' not in props:
        print('ERROR:not_in_response')
        sys.exit(1)
    p = props['$PROP_NAME']
    t = p.get('type', '?')
    extras = []
    inner = p.get(t, {})
    if isinstance(inner, dict) and 'options' in inner:
        extras.append('options=' + str([o['name'] for o in inner['options']]))
    print('OK:' + '$PROP_NAME' + ':type=' + t + ':' + ':'.join(extras) + ':total=' + str(len(props)))
except Exception as e:
    print('ERROR:parse_fail:' + str(e) + ':' + raw[:200])
    sys.exit(1)
")

# 输出
if [[ "$RESULT" == OK:* ]]; then
  echo "✅ $RESULT"
  exit 0
else
  echo "$RESULT" >&2
  exit 1
fi
