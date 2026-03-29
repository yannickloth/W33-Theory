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

create_model_alias() {
  local alias="$1"
  local source_model="$2"
  local extra_parameter="${3:-}"
  local modelfile
  modelfile="$(mktemp)"
  cat >"$modelfile" <<EOF
FROM $source_model

PARAMETER temperature 0
PARAMETER top_k 1
PARAMETER top_p 1
PARAMETER repeat_penalty 1.05
PARAMETER num_ctx 4096
EOF
  if [ -n "$extra_parameter" ]; then
    printf '%s\n' "$extra_parameter" >>"$modelfile"
  fi
  "$OLLAMA_EXE" create "$alias" -f "$(wslpath -w "$modelfile")"
  rm -f "$modelfile"
}

completion_smoke() {
  local model_id="$1"
  local model_json prompt_json payload response
  model_json="$(json_escape "$model_id")"
  prompt_json="$(json_escape "from qiskit import QuantumCircuit")"
  payload="$(printf '{"model":%s,"prompt":%s,"stream":false,"max_tokens":16}' "$model_json" "$prompt_json")"
  response="$(curl.exe -sS -m 45 -X POST "http://localhost:11434/v1/completions" -H "Content-Type: application/json" --data-binary "$payload" || true)"
  if printf '%s' "$response" | rg -q '"error"'; then
    printf '%s\n' "$response" >&2
    return 1
  fi
  return 0
}

detect_model_ids() {
  local payload
  payload="$(curl.exe -sS "http://localhost:11434/v1/models")"
  python3 -c 'import json, sys; payload=json.loads(sys.argv[1]); [print(entry["id"]) for entry in payload.get("data", [])]' "$payload"
}

OLLAMA_EXE="$(find_ollama_exe)" || {
  echo "Could not find Windows Ollama. Install it first from https://ollama.com/download" >&2
  exit 1
}

MODEL_RAW="$(choose_model "${1:-auto}")"
MODEL_ALIAS="$(printf '%s' "${MODEL_RAW#hf.co/Qiskit/}" | tr '[:upper:]' '[:lower:]')"
MODEL_VERIFY_ID="${MODEL_ALIAS}:latest"

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

create_model_alias "$MODEL_ALIAS" "$MODEL_RAW"

# Drop the raw HF entry to keep the model picker clean. The alias keeps the same blob.
"$OLLAMA_EXE" rm "${MODEL_RAW}:latest" >/dev/null 2>&1 || true

python3 - <<'PY' "$ROOT_DIR"
import json
import pathlib
import sys

root = pathlib.Path(sys.argv[1])
targets = [
    pathlib.Path("/mnt/c/Users/wiljd/AppData/Roaming/Code/User/settings.json"),
    pathlib.Path("/mnt/c/Users/wiljd/AppData/Roaming/Code - Insiders/User/settings.json"),
    root / ".vscode" / "settings.json",
]

patched = []
for path in targets:
    if not path.exists() and path.parent.exists():
        data = {}
    elif path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
    else:
        continue
    data["qiskitCodeAssistant.url"] = "http://localhost:11434"
    data["qiskitCodeAssistant.enableTelemetry"] = False
    data["qiskitCodeAssistant.enableStreaming"] = True
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    patched.append(str(path))

for path in patched:
    print(path)
PY

python3 "$ROOT_DIR/tools/qiskit/patch_installed_qiskit_extension_local_mode.py"

PREFERRED_MODEL_ID="$MODEL_VERIFY_ID"
if ! completion_smoke "$PREFERRED_MODEL_ID"; then
  CPU_ALIAS="${MODEL_ALIAS}-cpu"
  CPU_MODEL_ID="${CPU_ALIAS}:latest"
  echo "Primary model smoke failed. Creating CPU-safe alias: $CPU_MODEL_ID"
  create_model_alias "$CPU_ALIAS" "$MODEL_RAW" "PARAMETER num_gpu 0"
  completion_smoke "$CPU_MODEL_ID"
  PREFERRED_MODEL_ID="$CPU_MODEL_ID"
fi

curl.exe -fsS "http://localhost:11434/v1/models" >/dev/null

echo
echo "Local Qiskit Code Assistant backend is ready."
echo "Model: $PREFERRED_MODEL_ID"
echo "Available /v1/models ids:"
detect_model_ids | sed 's/^/  - /'
echo "VS Code setting: qiskitCodeAssistant.url=http://localhost:11434"
echo "Installed Qiskit extensions were patched to force local URLs through OpenAI-compatible mode."
echo
echo "Next step in VS Code:"
echo "  Fully quit and reopen VS Code or VS Code Insiders"
echo "  If needed: Qiskit Code Assistant: Select Model -> $PREFERRED_MODEL_ID"
echo
echo "Smoke test:"
echo "  qiskit-code-assistant-smoke $PREFERRED_MODEL_ID"
echo
echo "Permutation workflow:"
echo "  qiskit-python \"$ROOT_DIR/tools/qiskit/permutation_grover_search.py\" --items A B C --mark A,B,C"
echo
echo "TOE support hierarchy workflow:"
echo "  qiskit-python \"$ROOT_DIR/tools/qiskit/toe_support_hierarchy_search.py\" --shots 512"
