#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

find_ollama_exe() {
  if command -v ollama.exe >/dev/null 2>&1; then
    command -v ollama.exe
    return 0
  fi

  local direct="/mnt/c/Users/${USER}/AppData/Local/Programs/Ollama/ollama.exe"
  if [ -x "$direct" ]; then
    printf '%s\n' "$direct"
    return 0
  fi

  local discovered
  discovered="$(find /mnt/c/Users -maxdepth 4 -path '*/AppData/Local/Programs/Ollama/ollama.exe' -print -quit 2>/dev/null || true)"
  if [ -n "$discovered" ]; then
    printf '%s\n' "$discovered"
    return 0
  fi

  return 1
}

choose_model() {
  local mem_gib
  mem_gib="$(free -g | awk '/^Mem:/ {print $2}')"

  case "${1:-auto}" in
    auto)
      if [ "$mem_gib" -ge 24 ]; then
        printf '%s\n' "hf.co/Qiskit/Mistral-Small-3.2-24B-Qiskit-GGUF"
      elif [ "$mem_gib" -ge 12 ]; then
        printf '%s\n' "hf.co/Qiskit/Qwen2.5-Coder-14B-Qiskit-GGUF"
      else
        printf '%s\n' "hf.co/Qiskit/Granite-3.3-8B-Qiskit-GGUF"
      fi
      ;;
    granite|granite-3.3-8b)
      printf '%s\n' "hf.co/Qiskit/Granite-3.3-8B-Qiskit-GGUF"
      ;;
    qwen|qwen2.5|qwen2.5-coder-14b)
      printf '%s\n' "hf.co/Qiskit/Qwen2.5-Coder-14B-Qiskit-GGUF"
      ;;
    mistral|mistral-small|mistral-small-24b)
      printf '%s\n' "hf.co/Qiskit/Mistral-Small-3.2-24B-Qiskit-GGUF"
      ;;
    *)
      printf '%s\n' "$1"
      ;;
  esac
}

json_escape() {
  python3 - <<'PY' "$1"
import json, sys
print(json.dumps(sys.argv[1]))
PY
}

OLLAMA_EXE="$(find_ollama_exe)" || {
  echo "Could not find Windows Ollama. Install it first from https://ollama.com/download" >&2
  exit 1
}

MODEL_RAW="$(choose_model "${1:-auto}")"
MODEL_ALIAS="$(printf '%s' "${MODEL_RAW#hf.co/Qiskit/}" | tr '[:upper:]' '[:lower:]')"
MODEL_VERIFY_ID="${MODEL_ALIAS}:latest"
SETTINGS_JSON="/mnt/c/Users/wiljd/AppData/Roaming/Code/User/settings.json"

echo "Using Ollama: $OLLAMA_EXE"
echo "Using raw model: $MODEL_RAW"
echo "Using alias: $MODEL_VERIFY_ID"

if ! curl.exe -fsS "http://localhost:11434/v1/models" >/dev/null 2>&1; then
  powershell.exe -NoProfile -Command "Start-Process -FilePath 'C:\\Users\\wiljd\\AppData\\Local\\Programs\\Ollama\\ollama app.exe'" >/dev/null
fi

for _ in $(seq 1 30); do
  if curl.exe -fsS "http://localhost:11434/v1/models" >/dev/null 2>&1; then
    break
  fi
  sleep 1
done

curl.exe -fsS "http://localhost:11434/v1/models" >/dev/null

"$OLLAMA_EXE" list | rg -q "^${MODEL_ALIAS}\b|^$(printf '%s' "${MODEL_RAW#hf.co/}")\b|^$(printf '%s' "${MODEL_RAW#hf.co/Qiskit/}")\b" || "$OLLAMA_EXE" pull "$MODEL_RAW"

MODELTMP="$(mktemp)"
cat >"$MODELTMP" <<EOF
FROM $MODEL_RAW

PARAMETER temperature 0
PARAMETER top_k 1
PARAMETER top_p 1
PARAMETER repeat_penalty 1.05
PARAMETER num_ctx 4096
EOF

"$OLLAMA_EXE" create "$MODEL_ALIAS" -f "$(wslpath -w "$MODELTMP")"
rm -f "$MODELTMP"

# Drop the raw HF entry to keep the model picker clean. The alias keeps the same blob.
"$OLLAMA_EXE" rm "${MODEL_RAW}:latest" >/dev/null 2>&1 || true

python3 - <<'PY' "$SETTINGS_JSON"
import json, pathlib, sys
path = pathlib.Path(sys.argv[1])
data = {}
if path.exists():
    data = json.loads(path.read_text(encoding="utf-8"))
data["qiskitCodeAssistant.url"] = "http://localhost:11434"
data["qiskitCodeAssistant.enableTelemetry"] = False
data["qiskitCodeAssistant.enableStreaming"] = True
path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
PY

MODEL_JSON="$(json_escape "$MODEL_VERIFY_ID")"
PROMPT_JSON="$(json_escape "from qiskit import QuantumCircuit")"
PAYLOAD="$(printf '{"model":%s,"prompt":%s,"stream":false,"max_tokens":48}' "$MODEL_JSON" "$PROMPT_JSON")"

curl.exe -fsS "http://localhost:11434/v1/models" >/dev/null
curl.exe -fsS -X POST "http://localhost:11434/v1/completions" \
  -H "Content-Type: application/json" \
  --data-binary "$PAYLOAD" >/dev/null

echo
echo "Local Qiskit Code Assistant backend is ready."
echo "Model: $MODEL_VERIFY_ID"
echo "VS Code setting: qiskitCodeAssistant.url=http://localhost:11434"
echo
echo "Next manual step in VS Code:"
echo "  Qiskit Code Assistant: Select Model"
echo "  -> $MODEL_VERIFY_ID"
echo
echo "Smoke test:"
echo "  qiskit-code-assistant-smoke $MODEL_VERIFY_ID"
echo
echo "Permutation workflow:"
echo "  qiskit-python \"$ROOT_DIR/tools/qiskit/permutation_grover_search.py\" --items A B C --mark A,B,C"
