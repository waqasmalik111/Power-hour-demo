#!/usr/bin/env bash
set -euo pipefail

if [ $# -lt 2 ]; then
  echo "Usage: $0 <route-url> <language> [guidelines] [file]"
  exit 1
fi

ROUTE_URL="$1"             # e.g. https://react-agent-<ns>.<domain>
LANGUAGE="$2"              # python | go | typescript | ...
GUIDELINES="${3:-PEP8}"
FILE="${4:-${PWD}/__CURRENT_FILE__}"

CODE_JSON=$(jq -Rs . < "$FILE")

PAYLOAD=$(jq -n \
  --arg language "$LANGUAGE" \
  --arg guidelines "$GUIDELINES" \
  --argjson code "$CODE_JSON" \
  '{language:$language, guidelines:$guidelines, code:$code}')

echo "→ Validating $FILE as $LANGUAGE …"
curl -sS -X POST "$ROUTE_URL/agent/validate" \
  -H 'Content-Type: application/json' \
  -d "$PAYLOAD" | tee /tmp/validation.json

echo -e "\n✓ Saved to /tmp/validation.json"

