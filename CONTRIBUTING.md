# Contributing

## Quick Start

```bash
# Clone and set up
git clone https://github.com/wilcompute/W33-Theory.git
cd W33-Theory
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Run the test suite
python -m pytest tests/test_e8_embedding.py -q
```

## Pre-commit Hooks

This repo uses **black** and **isort** for formatting. Install hooks with:

```bash
pip install pre-commit && pre-commit install
```

## Adding a New Pillar

1. Create a verification script: `scripts/w33_<pillar_name>.py`
   - Include `if __name__ == '__main__':` guard
   - Print key results with clear labels
2. Add a test class to `tests/test_e8_embedding.py`
   - Use `scope="class"` fixtures for expensive setup
   - 3-5 tests per pillar, each testing one key claim
3. Update the pillar table in `README.md`

## Guidelines

- Every claim must be computationally verified
- Avoid heavy computation at import time
- `scripts.w33_permrep_association.analyze_gap_permrep_association` will attempt to recover a full transitive orbit by searching alternate base points if the provided `base` yields an incomplete orbit — prefer calling the function directly rather than invoking its CLI fallback in tests.
- Use `json.dump(..., indent=2, default=str)` for serialization
- Keep assertions tight: use `np.isclose` or `pytest.approx` with explicit tolerances

````

## Optional performance flags

- `TOE_USE_NUMBA`: enable the optional Numba-accelerated kernel for `cubic_sym`.
  - Usage: `E8Z3Bracket(..., use_numba=True)` or set `TOE_USE_NUMBA=1` in the environment.
  - Opt-in only — behavior is unchanged when `numba` is not installed or the flag is not set.
  - Numeric parity with the NumPy implementation is enforced by tests (`tests/test_perf_numba_cubic_sym.py`).

- `TOE_USE_FAST_CUBIC_SYM`: enable guarded fast-NumPy scatter (`np.bincount`) for `cubic_sym` when profiling shows benefit.

Examples:

```bash
# Linux / macOS (bash)
export TOE_USE_NUMBA=1
python -m pytest -q tests/test_perf_numba_cubic_sym.py

# Windows PowerShell
$env:TOE_USE_NUMBA = '1'
python -m pytest -q tests/test_perf_numba_cubic_sym.py
```

> Note: these flags are non-breaking; enable them only for benchmarking or when profiling indicates a gain.

- Keep assertions tight: use `np.isclose` or `pytest.approx` with explicit tolerances
