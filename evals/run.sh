#!/usr/bin/env bash
# Run all eval prompts through worai agent --cli claude and save outputs.
# Optionally score each output with an LLM judge (runs by default).
#
# Usage:
#   WORDLIFT_API_KEY=<your-key> ./evals/run.sh
#   WORDLIFT_API_KEY=<your-key> ./evals/run.sh curator-static-entities
#   WORDLIFT_API_KEY=<your-key> ./evals/run.sh --no-judge
#
# WORDLIFT_API_KEY is required to prevent accidental use of production keys.
# A minimal isolated worai config is generated from it at runtime.

set -euo pipefail

FILTER=""
JUDGE=1
LIST=0
VERBOSE=0

usage() {
  cat <<EOF
Usage: WORDLIFT_API_KEY=<your-key> $(basename "$0") [options] [eval-name]

Run eval prompts through worai agent --cli claude and save outputs.

WORDLIFT_API_KEY must be set explicitly to avoid accidentally using a
production key from an existing project config.

Options:
  --no-judge           Skip the LLM judge step (judge runs by default).
  --list               List available eval names and exit.
  -v, --verbose        Stream output live to the terminal (also saved to file).
  -h, --help           Show this help message.

Arguments:
  eval-name            Run a single eval by name (without .md extension).
                       Omit to run all evals.

Examples:
  WORDLIFT_API_KEY=<your-key> ./evals/run.sh
  WORDLIFT_API_KEY=<your-key> ./evals/run.sh curator-static-entities
  WORDLIFT_API_KEY=<your-key> ./evals/run.sh --no-judge yarrrml-review
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --no-judge)        JUDGE=0;   shift   ;;
    -v|--verbose)      VERBOSE=1; shift   ;;
    -h|--help)         usage; exit 0 ;;
    --list)            LIST=1;    shift   ;;
    --*)         echo "Unknown option: $1" >&2; usage >&2; exit 1 ;;
    *)           FILTER="$1"; shift ;;
  esac
done

# ---------------------------------------------------------------------------
# Require WORDLIFT_API_KEY
# ---------------------------------------------------------------------------
if [[ -z "${WORDLIFT_API_KEY:-}" ]]; then
  echo "error: WORDLIFT_API_KEY is not set." >&2
  echo "Provide a safe (non-production) key to avoid overwriting an existing KG:" >&2
  echo "  WORDLIFT_API_KEY=<your-key> ./evals/run.sh" >&2
  exit 1
fi

# ---------------------------------------------------------------------------
# Resolve worai runner: direct install → pipx → uvx → give up
# ---------------------------------------------------------------------------
if command -v worai &>/dev/null; then
  WORAI_CMD=(worai)
elif command -v pipx &>/dev/null; then
  echo "worai not found — using pipx run worai" >&2
  WORAI_CMD=(pipx run worai)
elif command -v uvx &>/dev/null; then
  echo "worai not found — using uvx run --from worai worai" >&2
  WORAI_CMD=(uvx run --from worai worai)
else
  echo "error: worai is not installed and neither pipx nor uvx is available." >&2
  echo "Install worai (https://github.com/wordlift/worai) or install pipx/uvx first." >&2
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROMPTS_DIR="$SCRIPT_DIR/prompts"

if [[ $LIST -eq 1 ]]; then
  for f in "$PROMPTS_DIR"/*.md; do basename "$f" .md; done
  exit 0
fi

# ---------------------------------------------------------------------------
# Generate an isolated worai config from the provided key.
# This guarantees no existing project config or profile is used.
# ---------------------------------------------------------------------------
TEMP_DIR=$(mktemp -d)
TEMP_CONFIG="$TEMP_DIR/worai.toml"
cat > "$TEMP_CONFIG" <<TOML
[profiles.eval]
api_key = "${WORDLIFT_API_KEY}"
TOML

WORAI_ARGS=(--config "$TEMP_CONFIG" --profile eval)

STREAM_PARSER="$TEMP_DIR/stream_parser.py"
cat > "$STREAM_PARSER" <<'PYEOF'
import sys, json

out_path = sys.argv[1]
result_text = ""

for raw in sys.stdin:
    raw = raw.strip()
    if not raw:
        continue
    try:
        ev = json.loads(raw)
    except json.JSONDecodeError:
        print(raw, flush=True)
        continue

    t = ev.get("type", "")

    if t == "assistant":
        for block in ev.get("message", {}).get("content", []):
            bt = block.get("type", "")
            if bt == "text":
                chunk = block.get("text", "")
                print(chunk, end="", flush=True)
                result_text += chunk
            elif bt == "tool_use":
                name = block.get("name", "tool")
                inp = block.get("input", {})
                detail = inp.get("url", inp.get("query", inp.get("command", "")))
                label = f"  [{name}{': ' + detail[:80] if detail else ''}]"
                print(f"\n{label}", flush=True)

    elif t == "result":
        result_text = ev.get("result", result_text)

with open(out_path, "w") as f:
    f.write(result_text)
PYEOF

cleanup() {
  rm -rf "$TEMP_DIR"
}
trap cleanup EXIT

OUTPUTS_DIR="$SCRIPT_DIR/outputs"
JUDGMENTS_DIR="$SCRIPT_DIR/judgments"
mkdir -p "$OUTPUTS_DIR"
[[ $JUDGE -eq 1 ]] && mkdir -p "$JUDGMENTS_DIR"

# ---------------------------------------------------------------------------
# Spinner
# ---------------------------------------------------------------------------
SPINNER_PID=""
SPINNER_FRAMES=('⠋' '⠙' '⠹' '⠸' '⠼' '⠴' '⠦' '⠧' '⠇' '⠏')

start_spinner() {
  local msg="$1"
  local start=$SECONDS
  (
    local i=0
    while true; do
      local elapsed=$(( SECONDS - start ))
      printf "\r  %s %s (%ds)" "${SPINNER_FRAMES[$i]}" "$msg" "$elapsed"
      i=$(( (i + 1) % ${#SPINNER_FRAMES[@]} ))
      sleep 0.1
    done
  ) &
  SPINNER_PID=$!
}

stop_spinner() {
  if [[ -n "$SPINNER_PID" ]]; then
    kill "$SPINNER_PID" 2>/dev/null
    wait "$SPINNER_PID" 2>/dev/null || true
    printf "\r\033[K"
    SPINNER_PID=""
  fi
}

trap 'stop_spinner; cleanup' EXIT

# ---------------------------------------------------------------------------
# Judge
# ---------------------------------------------------------------------------
JUDGE_SYSTEM_PROMPT='You are a strict evaluator for an AI skill system.
You will be given an eval prompt (which includes an Expected output section) and the actual output produced by the skill.
Score the actual output against the Expected output criteria using these rules:

- verdict must be "fail" if the output discloses that required tools (WebFetch, WebSearch, MCP) were blocked or unavailable.
- verdict must be "fail" if selectors, URLs, or structured data are estimated/assumed rather than derived from live inspection.
- verdict must be "fail" if any criterion in Expected output is missing or only partially addressed.
- verdict is "pass" only when every Expected output criterion is met with evidence from actual execution.

Respond with valid JSON only — no markdown fences, no extra text:
{"verdict":"pass"|"fail","score":1|2|3|4|5,"reasoning":"one or two sentences citing specific evidence or specific gaps"}'

run_judge() {
  local prompt_file="$1"
  local output_file="$2"
  local judgment_file="$3"

  local judge_input
  judge_input="$(printf '## Eval Prompt\n\n%s\n\n## Actual Output\n\n%s' \
    "$(cat "$prompt_file")" "$(cat "$output_file")")"

  "${WORAI_CMD[@]}" "${WORAI_ARGS[@]}" agent --cli claude -- \
    --system-prompt "$JUDGE_SYSTEM_PROMPT" \
    -p "$judge_input" \
    --output-format text 2>/dev/null > "$judgment_file"
}

# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------
shopt -s nullglob
prompts=("$PROMPTS_DIR"/*.md)

if [[ ${#prompts[@]} -eq 0 ]]; then
  echo "No prompt files found in $PROMPTS_DIR" >&2
  exit 1
fi

passed=0
failed=0
skipped=0
judge_failed=0

for f in "${prompts[@]}"; do
  name=$(basename "$f" .md)

  if [[ -n "$FILTER" && "$name" != "$FILTER" ]]; then
    skipped=$((skipped + 1))
    continue
  fi

  out="$OUTPUTS_DIR/${name}.md"
  echo "→ $name"

  start=$SECONDS
  exit_code=0
  if [[ $VERBOSE -eq 1 ]]; then
    set +eo pipefail
    "${WORAI_CMD[@]}" "${WORAI_ARGS[@]}" agent --cli claude -- \
      --allowedTools "WebFetch,WebSearch" \
      -p "$(cat "$f")" --output-format stream-json --verbose 2>&1 | \
      python3 "$STREAM_PARSER" "$out"
    pipe_status=("${PIPESTATUS[@]}")
    set -eo pipefail
    exit_code=${pipe_status[0]}
  else
    start_spinner "generating output..."
    "${WORAI_CMD[@]}" "${WORAI_ARGS[@]}" agent --cli claude -- \
      --allowedTools "WebFetch,WebSearch" \
      -p "$(cat "$f")" --output-format text > "$out" 2>&1 &
    BG_PID=$!
    wait "$BG_PID" || exit_code=$?
    stop_spinner
  fi
  elapsed=$(( SECONDS - start ))

  if [[ $exit_code -eq 0 ]]; then
    passed=$((passed + 1))
    echo "  ✓ done in ${elapsed}s — evals/outputs/${name}.md"
  else
    failed=$((failed + 1))
    echo "  ✗ failed in ${elapsed}s — see evals/outputs/${name}.md"
    continue
  fi

  if [[ $JUDGE -eq 1 ]]; then
    judgment="$JUDGMENTS_DIR/${name}.json"
    start=$SECONDS
    start_spinner "judging..."
    run_judge "$f" "$out" "$judgment" &
    BG_PID=$!
    exit_code=0
    wait "$BG_PID" || exit_code=$?
    elapsed=$(( SECONDS - start ))
    stop_spinner

    if [[ $exit_code -eq 0 ]]; then
      verdict=$(python3 -c "import json; d=json.load(open('$judgment')); print(d['verdict']+' ('+str(d['score'])+'/5)')" 2>/dev/null || echo "unparseable")
      reasoning=$(python3 -c "import json; d=json.load(open('$judgment')); print(d['reasoning'])" 2>/dev/null || echo "")
      if [[ "$verdict" == fail* ]]; then
        judge_failed=$((judge_failed + 1))
        echo "  ✗ judge in ${elapsed}s: $verdict — $reasoning"
      else
        echo "  ✓ judge in ${elapsed}s: $verdict — $reasoning"
      fi
    else
      echo "  ? judge call failed in ${elapsed}s"
    fi
  fi
done

echo ""
if [[ $JUDGE -eq 1 ]]; then
  echo "Results: ${passed} passed, ${failed} failed, ${skipped} skipped — judge: ${judge_failed} failed"
  [[ $failed -eq 0 && $judge_failed -eq 0 ]]
else
  echo "Results: ${passed} passed, ${failed} failed, ${skipped} skipped"
  [[ $failed -eq 0 ]]
fi
