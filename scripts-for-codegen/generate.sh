#!/usr/bin/env bash
set -euo pipefail

if [ $# -lt 3 ]; then
  echo "Usage: $0 <route-url> <language> <output-dir> [prompt...]"
  exit 1
fi

ROUTE_URL="$1"
LANGUAGE="$2"
OUTDIR="$3"
shift 3
PROMPT="${*:-}"

mkdir -p "$OUTDIR"

case "$LANGUAGE" in
  python|py) EXT="py" ;;
  typescript|ts) EXT="ts" ;;
  javascript|js) EXT="js" ;;
  go) EXT="go" ;;
  *) EXT="txt" ;;
esac

TS="$(date +%Y%m%d-%H%M%S)"
OUTFILE="$OUTDIR/code_${TS}.${EXT}"

PAYLOAD=$(jq -n --arg q "$PROMPT" '{query:$q}')

echo "→ Generating from prompt: $PROMPT"
curl -sS -X POST "$ROUTE_URL/agent/execute" \
  -H 'Content-Type: application/json' \
  -d "$PAYLOAD" \
  | jq -r '.answer // "// (no answer returned)"' > "$OUTFILE"

echo "✓ Saved: $OUTFILE"
sed -n '1,80p' "$OUTFILE" || true

