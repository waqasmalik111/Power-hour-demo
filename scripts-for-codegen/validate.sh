#!/usr/bin/env bash
set -euo pipefail

ROUTE="${1:-${AGENT_ROUTE:-${ROUTE:-}}}"
LANG="${2:-${VALIDATE_LANG:-python}}"
CODE="${3:-}"

# If no 3rd arg, read from stdin (selectedText piped from task)
if [[ -z "${CODE}" ]]; then
  if [ ! -t 0 ]; then
    CODE="$(cat)"
  fi
fi

if [[ -z "${ROUTE}" || -z "${LANG}" || -z "${CODE}" ]]; then
  echo "Usage: $0 <ROUTE> <LANG> [CODE]" >&2
  echo "Example: $0 https://react-agent.apps.example.com python \"print('hi')\"" >&2
  exit 1
fi

# Build payload expected by your Flask /agent/validate
payload=$(jq -n --arg code "$CODE" --arg lang "$LANG" \
  '{ language: $lang, code: $code }')

# Call the validation endpoint
curl -fsSL -X POST "${ROUTE%/}/agent/validate" \
  -H "Content-Type: application/json" \
  -d "$payload" \
  | jq -r '.report // .answer // .message // .error // .'
