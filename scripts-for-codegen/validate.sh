#!/usr/bin/env bash
set -euo pipefail

########################################
# Path resolution
########################################

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

########################################
# Load .devspaces.env from repo root
########################################

DEVSPACES_ENV="${REPO_ROOT}/.devspaces.env"

if [[ -f "${DEVSPACES_ENV}" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "${DEVSPACES_ENV}"
  set +a
  echo "✓ Loaded environment from ${DEVSPACES_ENV}"
else
  echo "⚠️  ${DEVSPACES_ENV} not found. Environment variables may be missing."
fi

########################################
# Parse arguments and environment
########################################

# First arg can be either a file path or ROUTE
ARG1="${1:-}"
LANG="${2:-${VALIDATE_LANG:-python}}"
CODE="${3:-}"

# Determine if ARG1 is a file or ROUTE
if [[ -n "${ARG1}" && -f "${ARG1}" ]]; then
  # ARG1 is a file, read code from it
  CODE="$(cat "${ARG1}")"
  ROUTE="${AGENT_ROUTE:-}"
elif [[ -n "${ARG1}" ]]; then
  # ARG1 is the ROUTE
  ROUTE="${ARG1}"
else
  # No ARG1, use environment
  ROUTE="${AGENT_ROUTE:-${ROUTE:-}}"
fi

# If still no CODE, try reading from stdin
if [[ -z "${CODE}" ]]; then
  if [ ! -t 0 ]; then
    CODE="$(cat)"
  fi
fi

########################################
# Validate inputs
########################################

if [[ -z "${ROUTE}" ]]; then
  echo "❌ ROUTE not provided and AGENT_ROUTE not set" >&2
  echo "" >&2
  echo "Usage:" >&2
  echo "  $0 <file_path>                    # Validates file, uses AGENT_ROUTE from env" >&2
  echo "  $0 <ROUTE> <LANG> <CODE>          # Explicit validation" >&2
  echo "  echo 'code' | $0 <ROUTE> <LANG>   # Pipe code via stdin" >&2
  echo "" >&2
  echo "Example:" >&2
  echo "  $0 /path/to/file.py" >&2
  echo "  $0 https://agent.example.com/agent/execute python \"print('hi')\"" >&2
  echo "" >&2
  echo "Expected AGENT_ROUTE in: ${DEVSPACES_ENV}" >&2
  exit 1
fi

if [[ -z "${CODE}" ]]; then
  echo "❌ No code provided (via file, argument, or stdin)" >&2
  exit 1
fi

########################################
# Construct validation endpoint
########################################

# Replace /agent/execute with /agent/validate if present
if [[ "${ROUTE}" == */agent/execute ]]; then
  VALIDATE_ROUTE="${ROUTE%/agent/execute}/agent/validate"
elif [[ "${ROUTE}" == */agent/execute/ ]]; then
  VALIDATE_ROUTE="${ROUTE%/agent/execute/}/agent/validate"
else
  # Assume ROUTE is base URL, append /agent/validate
  VALIDATE_ROUTE="${ROUTE%/}/agent/validate"
fi

########################################
# Build and send validation request
########################################

echo "👉 Using AGENT_ROUTE=${ROUTE}"
echo "👉 Validation endpoint: ${VALIDATE_ROUTE}"
echo "👉 Validating ${LANG} code from: ${ARG1:-stdin}"

payload=$(jq -n --arg code "$CODE" --arg lang "$LANG" \
  '{ language: $lang, code: $code }')

response=$(curl -fsSL -X POST "${VALIDATE_ROUTE}" \
  -H "Content-Type: application/json" \
  -d "$payload" 2>&1) || {
    echo "❌ Error calling validation endpoint" >&2
    echo "$response" >&2
    exit 1
  }

# Extract and display the report
result=$(echo "$response" | jq -r '.report // .answer // .message // .error // .')

if [[ -z "$result" || "$result" == "null" ]]; then
  echo "❌ No validation result returned" >&2
  echo "Raw response:" >&2
  echo "$response" >&2
  exit 1
fi

echo ""
echo "📋 Validation Report:"
echo "─────────────────────"
echo "$result"
echo "─────────────────────"

# Check if validation passed
if echo "$response" | jq -e '.success == true' >/dev/null 2>&1; then
  echo "✅ Validation passed"
  exit 0
elif echo "$response" | jq -e '.success == false' >/dev/null 2>&1; then
  echo "⚠️  Validation failed"
  exit 1
else
  # No explicit success field, assume success if we got a report
  exit 0
fi