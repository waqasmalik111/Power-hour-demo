#!/usr/bin/env bash
set -euo pipefail
ENV_FILE="${ENV_FILE:-.devspaces.env}"
# shellcheck disable=SC1090
if [ -f "$ENV_FILE" ]; then
  set -a
  . "$ENV_FILE"
  set +a
fi


# Accept ROUTE/LANG from args, or fall back to env (.devspaces.env)
ROUTE="${1:-${AGENT_ROUTE:-${ROUTE:-}}}"
LANG="${2:-${GEN_LANG:-}}"
PROMPT="${3:-}"

if [[ -z "${PROMPT}" ]]; then
  # If no 3rd arg, try to read prompt from STDIN (piped input)
  if [ ! -t 0 ]; then
    PROMPT="$(cat)"
  fi
fi

if [[ -z "${ROUTE}" || -z "${LANG}" || -z "${PROMPT}" ]]; then
  echo "Usage: $0 <ROUTE> <LANG> [PROMPT]" >&2
  echo "Example: $0 https://react-agent.apps.example.com python \"Write a function...\"" >&2
  exit 1
fi

# Debug (optional)
echo "Using ROUTE=${ROUTE} LANG=${LANG}" >&2

# Call your service
curl -fsSL -X POST "${ROUTE}/agent/execute" \
  -H "Content-Type: application/json" \
  -d "$(jq -n --arg q "$PROMPT" '{query:$q}')" \
  | jq -r '.answer // empty'
