# W33 Theory of Everything

Living paper and executable research code for deriving structural Standard Model features from the finite geometry `W(3,3)` (point graph `W33`).

[![pytest](https://github.com/wilcompute/W33-Theory/actions/workflows/pytest.yml/badge.svg)](https://github.com/wilcompute/W33-Theory/actions/workflows/pytest.yml)
[![sage-verification](https://github.com/wilcompute/W33-Theory/actions/workflows/sage-verification.yml/badge.svg)](https://github.com/wilcompute/W33-Theory/actions/workflows/sage-verification.yml)
[![Lean 4 CI](https://github.com/wilcompute/W33-Theory/actions/workflows/lean4.yml/badge.svg)](https://github.com/wilcompute/W33-Theory/actions/workflows/lean4.yml)
[![Pillar21 Smoke](https://github.com/wilcompute/W33-Theory/actions/workflows/pillar21-smoke.yml/badge.svg)](https://github.com/wilcompute/W33-Theory/actions/workflows/pillar21-smoke.yml)

Canonical definitions and naming conventions live in `STANDARDIZATION.md`.

## Executive Snapshot

- Focus: finite-geometry to exceptional-Lie correspondence (`W(3,3)` / `W33` to `E6`, `E7`, `E8`) with reproducible scripts and tests.
- Research format: paper narrative in Markdown plus claim-to-script-to-test traceability.
- Current status (2026-02-11): 73 theorem-level results tracked, 120+ computational tests, 50+ quantitative predictions.
- Scope note: "verified" in this repository means computationally verified within the stated model and code path.

## Start Here

| Goal | Read | Run | Test |
|---|---|---|---|
| Understand the top-level correspondence | `README.md` (this page) + `docs/NOVEL_CONNECTIONS_2026_02_10.md` | `python scripts/w33_e8_correspondence_theorem.py` | `python -m pytest tests/test_e8_embedding.py -q` |
| Reproduce homology and spectrum claims | `docs/STATUS_AND_GAPS.md` | `python scripts/w33_homology.py` and `python scripts/w33_hodge.py` | `python -m pytest tests/test_w33_hodge.py -q` |
| Reproduce the qutrit/Heisenberg bridge | `reports/auto_ingest/W33_Heisenberg_action_bundle_20260209_v1_analysis_report.md` | `python scripts/w33_heisenberg_qutrit.py` | `python -m pytest tests/test_heisenberg_qutrit_structure.py -q` |
| Reproduce the E6/F3 trilinear pipeline | `docs/NOVEL_CONNECTIONS_2026_02_10.md` + `docs/REDUCED_ORBIT_THEOREM_2026_02_10.md` | `python tools/build_e6_f3_trilinear_map.py` then `python tools/analyze_e6_f3_trilinear_symmetry_breaking.py` | `python -m pytest tests/test_e6_f3_trilinear.py tests/test_check_min_cert_orbit_involution_rule_smoke.py -q` |
| Reproduce the `z=(2,2)` global exclusion | `docs/Z22_GLOBAL_STABILIZER_EXCLUSION_2026_02_11.md` | `python tools/prove_z22_no_global_stabilizer.py` | `python -m pytest tests/test_prove_z22_no_global_stabilizer_smoke.py -q` |
| Reproduce s12 universalization and Vogel scans | `docs/S12_UNIVERSALIZATION_2026_02_11.md` + `docs/VOGEL_UNIVERSAL_RESEARCH_2026_02_11.md` | `python tools/universalize_s12_algebra.py` and `python tools/vogel_universal_snapshot.py` | `python -m pytest tests/test_universalize_s12_algebra_smoke.py tests/test_vogel_universal_snapshot_smoke.py -q` |
| Inspect formalization progress in Lean 4 | `proofs/lean/README.md` | `cd proofs/lean && lake build` | CI: `.github/workflows/lean4.yml` |

## Quick Setup

```bash
python -m venv .venv
# PowerShell
.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements-dev.txt
```

Run the short confidence check:

```bash
python scripts/w33_e8_correspondence_theorem.py
python -m pytest tests/test_e8_embedding.py tests/test_heisenberg_qutrit_structure.py -q
```

Run full regression:

```bash
python -m pytest -q
```

## Repository Layout

```text
.github/workflows/   CI, smoke checks, Sage and Lean pipelines
scripts/             Core reproducibility scripts tied to claims
tools/               Extended theorem tooling and artifact builders
tests/               Pytest suite and smoke checks
proofs/lean/         Lean 4 formalization skeleton and CI target
docs/                Paper sections, theorem notes, and status documents
artifacts/           Machine-generated outputs used by writeups
```

## Manuscript and Historical Material

The previous long-form root manuscript has been preserved at:

- `docs/README_LIVING_PAPER_2026_02_11.md`

Additional high-signal documents:

- `docs/NOVEL_CONNECTIONS_2026_02_10.md`
- `docs/REDUCED_ORBIT_THEOREM_2026_02_10.md`
- `docs/REDUCED_ORBIT_FORMAL_PROOF_2026_02_11.md`
- `docs/S12_UNIVERSALIZATION_2026_02_11.md`
- `docs/S12_JACOBI_FAILURE_PATTERN_2026_02_11.md`
- `docs/S12_SL27_Z3_BRIDGE_2026_02_11.md`
- `docs/VOGEL_UNIVERSAL_RESEARCH_2026_02_11.md`

## Contribution Notes

- Use `CONTRIBUTING.md` for local workflow and pre-commit guidance.
- Keep claims executable: each theorem update should include script path, test path, and artifact path.
- Prefer adding new result documents under `docs/` and generated outputs under `artifacts/`.
