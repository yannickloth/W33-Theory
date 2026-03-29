# Qiskit Local Workflow

This folder contains the durable local setup and experiment entrypoints for using
the Qiskit Code Assistant with a local Ollama backend from this machine.

## What Is Working

- VS Code extension: `qiskit.qiskit-vscode`
- Backend: Windows-side Ollama on `http://localhost:11434`
- Verified local model: `granite-3.3-8b-qiskit-gguf-cpu:latest`
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

After running the setup script below, completely quit and reopen VS Code.

If only one local model is installed, the extension should auto-select it on
startup after the restart.

If you still want to set it manually, run:

`Qiskit Code Assistant: Select Model`

Then choose:

`granite-3.3-8b-qiskit-gguf-cpu:latest`

The extension does not currently expose a durable preseeded selected-model
setting, so this remains a one-time UI action.

If the extension still complains that your API token is invalid while you are
trying to use local Ollama, the extension is still on the IBM cloud path. This
repo now pins `qiskitCodeAssistant.url` at the workspace level and includes a
local-mode patcher for the installed extension so non-IBM URLs stay on the
OpenAI-compatible path instead of the IBM token path.

On this machine the CPU-safe Granite alias is the stable path:

`granite-3.3-8b-qiskit-gguf-cpu:latest`

## Local Auth / Token Error Fix

If model selection says your API token is invalid or unauthorized while you are
trying to use local Ollama, the extension has fallen into the IBM cloud path
instead of the local OpenAI-compatible path.

This repo now carries a local fix for that case:

```bash
python3 tools/qiskit/patch_installed_qiskit_extension_local_mode.py
```

That patch does three things:

- treats any non-IBM Qiskit URL as local OpenAI-compatible mode
- skips IBM credential startup prompts in local mode
- stops rewriting all local `401/403` responses as IBM token failures

The setup script below also runs that patch automatically.

Also note that this machine has both VS Code stable and VS Code Insiders in
use. The setup script now writes Qiskit settings to:

- Windows VS Code stable user settings
- Windows VS Code Insiders user settings
- this repo's workspace settings

## Local Setup

From the repo root:

```bash
bash tools/qiskit/local_setup_wsl_windows_ollama.sh
```

That script:

- starts Windows Ollama if needed
- installs or reuses the Qiskit Granite model
- writes the stable, Insiders, and workspace Qiskit extension settings
- patches installed Qiskit extensions so local URLs bypass IBM token flow
- verifies `/v1/models`
- verifies `/v1/completions`

## Helper Commands

These were also installed in `~/bin`:

```bash
qiskit-code-assistant-start
qiskit-code-assistant-smoke
qiskit-python -V
```

## Direct Local Delegate

If you want me to use the local Qiskit model as an auxiliary coding assistant,
the repo now includes a direct Ollama caller:

```bash
python3 tools/qiskit/qiskit_local_codegen.py \
  --prompt "Write a Qiskit 2.0 function that builds a Bell pair circuit."
```

This does not turn the model into a native Codex `spawn_agent` target, but it
does let me delegate bounded Qiskit coding subtasks to the same local model the
extension uses, inspect the result, and continue the loop inside the repo.

If only one local model is exposed from `/v1/models`, the helper auto-selects
it. Otherwise pass `--model`.

List live models:

```bash
python3 tools/qiskit/qiskit_local_codegen.py --list-models
```

On this machine, model discovery through `/v1/models` is reliable, but direct
CLI completions through `/v1/completions` can still time out under the WSL ->
Windows Ollama split. So the CLI helper is useful as a bounded auxiliary path,
but the simulator-side Qiskit workflow should not depend on it being fast on
every call.

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

## First TOE Search Target

The first TOE-specific Qiskit search in this repo is:

```bash
qiskit-python tools/qiskit/toe_support_hierarchy_search.py --shots 512
```

That search does not guess new physics. It encodes the exact bridge support
hierarchy already proved in the repo:

- `2E13` image channel lives on the head-compatible line
- first family-sensitive `A4` packet has minimal carrier `U1`
- transport completion lives on the full avatar
- the local `U3` and `E8_2` packets remain unconstrained in relative order

So the oracle marks exactly the support permutations whose first three slots are:

- `head_line`
- `u1_plane`
- `transport_avatar`

The next exact search layer is:

```bash
qiskit-python tools/qiskit/toe_bridge_product_search.py \
  --mode formal-completion \
  --shots 256 \
  --seed 7
```

That product-state oracle combines three exact theorem sectors on one search
space:

- strict support hierarchy
- five-factor packet ordering
- glue state: current zero split shadow vs unique nonzero formal completion

The next refinement is:

```bash
qiskit-python tools/qiskit/toe_bridge_line_factor_search.py \
  --mode formal-completion \
  --shots 256 \
  --seed 7
```

That line-factor oracle adds the exact `U1` line choice:

- `head_compatible_u1_line`
- `tail_biased_u1_line`

and keeps only the theorem-compatible head line in the marked sector. The
explicit product space has size `57600`, padded to `16` qubits. On the seeded
verification runs (`seed = 7`, `256` shots), both `current-shadow` and
`formal-completion` modes hit only marked states with target-hit probability
`1.0`. A two-seed study over seeds `7,8` shows the `16`-qubit oracle is
cleanest at `44` iterations rather than `45`.

The next exact filter is:

```bash
qiskit-python tools/qiskit/toe_bridge_weight_filter_search.py \
  --mode formal-completion \
  --shots 256 \
  --seed 7
```

That adds one theorem-backed concentration bit:

- `dominant_weight_filter_pass`
- `dominant_weight_filter_fail`

with `pass` meaning the exact current inequalities:

- `U3` carries more than `4/5` of the hyperbolic packet
- `E8_2` carries more than `8/9` of the exceptional packet

The explicit product space has size `115200`, padded to `17` qubits. On the
seeded verification runs (`seed = 7`, `256` shots), both `current-shadow` and
`formal-completion` modes hit only marked states with target-hit probability
`1.0`. A two-seed study over seeds `7,8` shows the `17`-qubit oracle is
cleanest at `63` iterations rather than `64`.

The next exact refinement is:

```bash
qiskit-python tools/qiskit/toe_bridge_split_weight_filter_search.py \
  --mode formal-completion \
  --shots 256 \
  --seed 7
```

That splits the concentration theorem into two independent exact factors:

- `hyperbolic_dominance_pass` / `hyperbolic_dominance_fail`
- `exceptional_dominance_pass` / `exceptional_dominance_fail`

The marked sector keeps only the exact `pass/pass` state, so Qiskit can now
distinguish "hyperbolic only" and "exceptional only" filter failures instead
of collapsing everything to one joint fail bit. The explicit product space has
size `230400`, padded to `18` qubits. On the seeded verification runs
(`seed = 7`, `256` shots), both `current-shadow` and `formal-completion` modes
hit only marked states with target-hit probability `1.0`. A local
formal-completion probe at `89`, `90`, and `91` iterations stayed on the same
`1.0` plateau for seed `7`.

The next diagnostic refinement is:

```bash
qiskit-python tools/qiskit/toe_bridge_diagnostic_order_search.py \
  --mode formal-completion \
  --shots 256 \
  --seed 7
```

That keeps the same factor-state cardinality but factorizes the five-factor
ordering exactly as:

- hyperbolic order on `U1/U2/U3`
- exceptional order on `E8_1/E8_2`
- interleaving pattern choosing the `3` hyperbolic slots among `5`

with `5! = C(5,3) * 3! * 2! = 10 * 6 * 2`. So the oracle becomes diagnostic by
theorem sector without changing the underlying `120`-state factor space. The
full product space is again `230400`, padded to `18` qubits. On the seeded
verification runs (`seed = 7`, `256` shots), both `current-shadow` and
`formal-completion` modes hit only marked states with target-hit probability
`1.0`.

For heavier bridge oracles, use the reusable study runner:

```bash
qiskit-python tools/qiskit/toe_bridge_oracle_iteration_study.py \
  --target product \
  --iterations 31 32 33 \
  --seeds 7 8 \
  --shots 256 \
  --top 6
```

The first product study shows the `15`-qubit formal-completion oracle is
cleanest at `31` iterations on seeds `7,8`.

The next exact diagnostic layer is
[toe_bridge_diagnostic_relaxation_search.py](/mnt/c/Repos/Theory%20of%20Everything/tools/qiskit/toe_bridge_diagnostic_relaxation_search.py).
It keeps the same factorized `18`-qubit bridge space fixed and relaxes the two
order theorems one sector at a time, while the interleaving sector stays free
just as it already does in the diagnostic-order oracle. That gives a fixed
exact state space of `230400` states on `18` qubits with marked counts
`20 / 40 / 120 / 240` for:

- `exact`
- `exceptional-order-relaxed`
- `hyperbolic-order-relaxed`
- `both-orders-relaxed`

On seeded verification runs (`seed = 7`, `256` shots), both
`current-shadow` and `formal-completion` modes gave the same sector-by-sector
operating points:

- `45` iterations for `exact` with target-hit probability `1.0`
- `32` iterations for `exceptional-order-relaxed` with target-hit probability `1.0`
- `18` iterations for `hyperbolic-order-relaxed` with target-hit probability `1.0`
- `13` iterations for `both-orders-relaxed` with target-hit probability `0.99609375`

So the theorem-facing selectivity is explicit rather than buried in one
combined permutation rule: the exceptional order contributes the exact binary
factor, the hyperbolic order contributes the exact 6-fold factor, and the
interleaving sector is already free in the diagnostic-order oracle.

The current promoted bridge-oracle stack is summarized in
[bridge_oracle_ledger.json](/mnt/c/Repos/Theory%20of%20Everything/tools/qiskit/bridge_oracle_ledger.json).
For a GitHub-readable surface, use
[ORACLE_LEDGER.md](/mnt/c/Repos/Theory%20of%20Everything/tools/qiskit/ORACLE_LEDGER.md).

## Stronger TOE Search Target

The next exact search target is the five-factor external packet hierarchy:

```bash
qiskit-python tools/qiskit/toe_bridge_permutation_search.py \
  --mode five-factor-hierarchy \
  --shots 512
```

That oracle marks exactly the permutations compatible with the current exact
bridge inequalities:

- `U3 > U1 > U2`
- `E8_2 > E8_1`

So this search is not inventing new physics. It is searching the theorem-
compatible ordering sector of the already-rigid `U1/U2/U3/E8_1/E8_2` packet.
