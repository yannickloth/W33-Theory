# Qiskit Local Workflow

This folder contains the durable local setup and experiment entrypoints for using
the Qiskit Code Assistant with a local Ollama backend from this machine.

## What Is Working

- VS Code extension: `qiskit.qiskit-vscode`
- Backend: Windows-side Ollama on `http://localhost:11434`
- Verified local model: `Granite-3.3-8B-Qiskit-GGUF:latest`
- Linux-side Python runtime: `/home/wiljd/.venvs/qiskit-local`

## Why The Official Setup Fails Here

This machine is a WSL + Windows Ollama split setup.

- WSL `curl http://localhost:11434` does not see the Windows-side Ollama server.
- The official `setup_local.sh` model test uses `ollama run ... --verbose`, which
  is not the same path the VS Code extension uses.
- The default Qiskit `Qwen2.5-Coder 14B` model is too large for the available RAM
  on this machine and crashes the Ollama runner.

The durable path here is:

1. Use Windows Ollama.
2. Verify the actual OpenAI-compatible endpoint `/v1/completions`.
3. Use the smaller Qiskit-tuned Granite model.

## One-Time Manual VS Code Step

After running the setup script below, in VS Code run:

`Qiskit Code Assistant: Select Model`

Then choose:

`Granite-3.3-8B-Qiskit-GGUF:latest`

The extension does not currently expose a durable preseeded selected-model
setting, so this remains a one-time UI action.

## Local Setup

From the repo root:

```bash
bash tools/qiskit/local_setup_wsl_windows_ollama.sh
```

That script:

- starts Windows Ollama if needed
- installs or reuses the Qiskit Granite model
- writes the VS Code Qiskit extension settings
- verifies `/v1/models`
- verifies `/v1/completions`

## Helper Commands

These were also installed in `~/bin`:

```bash
qiskit-code-assistant-start
qiskit-code-assistant-smoke
qiskit-python -V
```

## Permutation Search Workflow

The reusable Qiskit experiment driver is:

```bash
qiskit-python tools/qiskit/permutation_grover_search.py \
  --items A B C \
  --mark A,B,C \
  --shots 512
```

Example with two marked permutations:

```bash
qiskit-python tools/qiskit/permutation_grover_search.py \
  --items 0 1 2 3 \
  --mark 0,1,2,3 \
  --mark 3,2,1,0 \
  --shots 1024 \
  --top 8
```

The script outputs JSON with:

- encoded search size
- number of qubits
- Grover iterations used
- marked permutations
- top measured hits
- decoded valid and invalid bitstrings

## Batch Sweep

Run a sweep across multiple sizes and iteration offsets:

```bash
qiskit-python tools/qiskit/permutation_grover_batch.py \
  --min-size 3 \
  --max-size 5 \
  --mark-mode identity-reverse \
  --iteration-offsets -1 0 1 \
  --shots 512 \
  --output /tmp/qiskit_batch.json
```

Then summarize it:

```bash
qiskit-python tools/qiskit/analyze_permutation_runs.py /tmp/qiskit_batch.json
```

## Upstream Patch

I also included a concrete patch draft for the Qiskit setup flow:

`tools/qiskit/qiskit_code_assistant_wsl_windows_ollama.patch`

It fixes three things:

- WSL + Windows Ollama readiness checks
- model verification through `/v1/completions`
- smaller default model selection on low-memory machines

## Tight Loop

The intended loop is:

1. Use Qiskit Code Assistant in VS Code to edit or extend the experiment.
2. Run the script with `qiskit-python`.
3. Inspect the JSON output.
4. Revise the circuit or scoring logic.
5. Repeat.
