# Reproduce key artifacts (quick guide)

This document shows the minimal commands to reproduce the repository's central computational artifacts (bijection + physics predictions).

Prerequisites
- Python 3.11 virtualenv (repo `.venv` is used in CI)
- Install requirements: `pip install -r requirements.txt` (or use the provided `.venv`)

Commands

1) Rebuild the W33 ↔ E8 bijection and structural artifact

```bash
python tools/construct_w33_e8_bijection.py
# writes: w33_e8_bijection_data.json
```

2) Regenerate the consolidated physics predictions

```bash
python PHYSICS_PREDICTIONS_MASTER.py
# writes: PHYSICS_PREDICTIONS_MASTER.json
```

3) (Optional) Run the predictions comparison utility if you have `data/predictions.json` and `tests/reference_values.json` prepared

```bash
python tools/generate_predictions_report.py
# writes: artifacts/predictions_report.json and artifacts/predictions_report.md
```

Developer tips
- Run `pytest -q` to execute the full verification suite (smoke + integration tests).
- Use `scripts/run_quick_checks.py` for a fast sanity check of core invariants.

Want me to add a one-click GitHub Actions workflow that executes steps (1) and (2) and publishes the two JSON artifacts? Reply: `Yes, add CI`.
