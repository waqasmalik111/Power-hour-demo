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
else
  echo "⚠️  ${DEVSPACES_ENV} not found. Environment variables may be missing."
fi

########################################
# Validate environment
########################################

if [[ -z "${AGENT_ROUTE:-}" ]]; then
  echo "❌ AGENT_ROUTE not set. Check your .devspaces.env in: ${REPO_ROOT}"
  exit 1
fi

GEN_LANG="${GEN_LANG:-python}"
VALIDATE_LANG="${VALIDATE_LANG:-${GEN_LANG}}"

########################################
# Parse arguments
########################################

if [[ $# -ne 2 ]]; then
  echo "Usage: $0 \"<prompt>\" <target_file>"
  exit 1
fi

PROMPT="$1"
TARGET_FILE="$2"

echo "👉 Using AGENT_ROUTE=${AGENT_ROUTE}"
echo "👉 Prompt: ${PROMPT}"
echo "👉 Target file: ${TARGET_FILE}"

########################################
# Build JSON payload (backend expects `query`)
########################################

PAYLOAD="$(
  GEN_PROMPT="${PROMPT}" \
  GEN_TARGET_FILE="${TARGET_FILE}" \
  GEN_LANG="${GEN_LANG}" \
  VALIDATE_LANG="${VALIDATE_LANG}" \
  python - << 'PYCODE'
import json, os, sys

prompt = os.environ.get("GEN_PROMPT", "")
target_file = os.environ.get("GEN_TARGET_FILE", "")
gen_lang = os.environ.get("GEN_LANG", "python")
validate_lang = os.environ.get("VALIDATE_LANG", gen_lang)

data = {
    "query": prompt,              # REQUIRED by backend
    "prompt": prompt,             # extra metadata (optional)
    "target_file": target_file,
    "language": gen_lang,
    "validate_language": validate_lang,
}

json.dump(data, sys.stdout)
PYCODE
)"

########################################
# Call the agent
########################################

RESPONSE_FILE="$(mktemp)"
trap "rm -f '${RESPONSE_FILE}'" EXIT

curl -sS -X POST \
  -H "Content-Type: application/json" \
  -d "${PAYLOAD}" \
  "${AGENT_ROUTE}" > "${RESPONSE_FILE}" || {
    echo "❌ Error calling agent at ${AGENT_ROUTE}"
    exit 1
  }

if [[ ! -s "${RESPONSE_FILE}" ]]; then
  echo "❌ No response from agent at ${AGENT_ROUTE}"
  exit 1
fi

########################################
# Extract code from response
########################################

CODE="$(python - << PYCODE
import sys, json

try:
    with open("${RESPONSE_FILE}", "r") as f:
        raw = f.read()
    
    # Parse the JSON properly
    data = json.loads(raw)
    
    if "answer" not in data:
        print("ERROR: Could not find 'answer' field in agent response.", file=sys.stderr)
        print(raw, file=sys.stderr)
        sys.exit(1)
    
    answer = data["answer"]
    code = answer.strip()
    
    # Strip markdown code fences if present
    if code.startswith("\`\`\`python"):
        code = code[len("\`\`\`python"):]
    elif code.startswith("\`\`\`"):
        code = code[len("\`\`\`"):]
    
    if code.endswith("\`\`\`"):
        code = code[:-3]
    
    code = code.strip()
    
    if not code:
        print("ERROR: Extracted code is empty.", file=sys.stderr)
        print(answer, file=sys.stderr)
        sys.exit(1)
    
    sys.stdout.write(code)
    
except json.JSONDecodeError as e:
    print(f"ERROR: Failed to parse JSON response: {e}", file=sys.stderr)
    with open("${RESPONSE_FILE}", "r") as f:
        print(f.read(), file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f"ERROR: {e}", file=sys.stderr)
    sys.exit(1)
PYCODE
)" || {
  echo "❌ Failed to extract code from agent response."
  echo "Raw response was:"
  cat "${RESPONSE_FILE}"
  exit 1
}

########################################
# Write code to target file
########################################

mkdir -p "$(dirname "${TARGET_FILE}")"
printf '%s\n' "${CODE}" > "${TARGET_FILE}"

echo "✅ Code written to ${TARGET_FILE}"