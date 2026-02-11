Thanks for checking out this repository!

Quick start
---------
- Create a virtual environment and activate it: `python -m venv .venv` then `source .venv/bin/activate` (or Windows PowerShell: `.venv\Scripts\Activate.ps1`).
- Install dependencies: `pip install -r requirements.txt` (or `pip install -e .`).
- For development (tests, optional tooling): `pip install -r requirements-dev.txt`.
- Run the test suite: `python -m pytest -q`.

Pre-commit and CI
----------------
- This repo uses pre-commit for formatting and linting. Install hooks with `pip install pre-commit && pre-commit install`.
- CI is set up with GitHub Actions in `.github/workflows/ci.yml` to run the test suite on push and PR.

Developer tools
----------------
- `scripts/find_top_level_calls.py` detects modules that execute work at import time (e.g., `plt.show()` or top-level function calls). Use it locally to find and fix modules that should be safe to import.

Guidelines
----------
- Avoid heavy computations or blocking calls at import time.
- Put runtime logic in `main()` and protect with `if __name__ == '__main__':`.
- Use `json.dump(..., indent=2, default=str)` for robust serialization of non-native JSON types.

If you'd like, I can open a branch and a draft PR with these changes, add CI badges to the README, and run the top-level scanner and fix remaining modules automatically. Let me know which you'd like next.

Local hotspot diagnostics & verification
---------------------------------------
- `scripts/local_hotspot_feasibility.py` now supports `--offset` and `--limit` for deterministic, resumable batch runs and detects OR-Tools import/linker problems (e.g., missing helper DLLs such as `utf8_validity.dll`) and emits explicit `ERROR_MISSING_DLL` entries in its JSON output to make automation resilient.
- `scripts/verify_and_register_pairs.py` verifies locally INFEASIBLE pairs with the global CP-SAT solver (`scripts/solve_e8_embedding_cpsat.py --force-seed`) and automatically appends verified pair forbids into `checks/PART_CVII_forbids.json` (use `--commit` to mirror to `committed_artifacts` and attempt a git commit).
