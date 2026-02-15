# claude_workspace

Helper scripts and utilities for running verification and collection.

## Running tests locally 🧪

- Create the virtual environment (Windows PowerShell):

  ```powershell
  python -m venv .venv
  .\.venv\Scripts\python.exe -m pip install --upgrade pip
  .\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
  ```

- Run tests without changing PowerShell execution policy (Windows):

  ```cmd
  cd claude_workspace
  scripts\run_local_tests.bat
  # or, to run all tests:
  scripts\run_all_tests.bat
  ```

- Or on PowerShell you can run for the session only:

  ```powershell
  Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
  . .\.venv\Scripts\Activate.ps1
  pytest -q
  ```

## Notes

- CI runs `sage-verification` workflow which produces `SUMMARY_RESULTS.json` and `NUMERIC_COMPARISONS.json` as artifacts. These files are validated by tests using JSON Schemas in `schemas/`.
| Reproduce W33 = 2‑qutrit Pauli geometry | `QUANTUM_INFORMATION_EXTENSION.md` | `python scripts/w33_two_qutrit_pauli.py` | `python -m pytest tests/test_e8_embedding.py::TestTwoQutritPauli -q` |
| Reproduce [g1,g1] → co-exact 120 (Lie bracket) | `scripts/w33_lie_bracket.py` | `python scripts/w33_lie_bracket.py` | `python -m pytest tests/test_e8_embedding.py::TestLieBracket -q` |
| Reproduce the E6/F3 trilinear pipeline | `docs/NOVEL_CONNECTIONS_2026_02_10.md` + `docs/REDUCED_ORBIT_THEOREM_2026_02_10.md` | `python tools/build_e6_f3_trilinear_map.py` then `python tools/analyze_e6_f3_trilinear_symmetry_breaking.py` | `python -m pytest tests/test_e6_f3_trilinear.py tests/test_check_min_cert_orbit_involution_rule_smoke.py -q` |
| Reproduce the `z=(2,2)` global exclusion | `docs/Z22_GLOBAL_STABILIZER_EXCLUSION_2026_02_11.md` | `python tools/prove_z22_no_global_stabilizer.py` | `python -m pytest tests/test_prove_z22_no_global_stabilizer_smoke.py -q` |
| Reproduce the full global `z`-map census | `docs/GLOBAL_FULL_SIGN_STABILIZER_CENSUS_2026_02_11.md` | `python tools/classify_global_full_sign_stabilizers.py` | `python -m pytest tests/test_classify_global_full_sign_stabilizers_smoke.py -q` |
| Reproduce minimal contradiction cores for global cells | `docs/MINIMAL_GLOBAL_FULL_SIGN_CORES_2026_02_11.md` | `python tools/minimal_global_full_sign_cores.py` | `python -m pytest tests/test_minimal_global_full_sign_cores_smoke.py -q` |
| Reproduce nontrivial UNSAT core geometry census | `docs/NONTRIVIAL_UNSAT_CORE_GEOMETRY_2026_02_11.md` | `python tools/classify_nontrivial_unsat_core_geometry.py` | `python -m pytest tests/test_classify_nontrivial_unsat_core_geometry_smoke.py -q` |
| Reproduce nontrivial core rulebook compression | `docs/NONTRIVIAL_CORE_RULEBOOK_2026_02_11.md` | `python tools/nontrivial_core_rulebook.py` | `python -m pytest tests/test_nontrivial_core_rulebook_smoke.py -q` |
| Reproduce rulebook-to-census motif link check | `docs/CORE_RULEBOOK_MIN_CERT_LINK_2026_02_11.md` | `python tools/link_core_rulebook_to_min_cert_census.py` | `python -m pytest tests/test_link_core_rulebook_to_min_cert_census_smoke.py -q` |
| Reproduce core-motif orbit polarization check | `docs/CORE_MOTIF_ORBIT_POLARIZATION_2026_02_11.md` | `python tools/classify_core_motif_orbit_polarization.py` | `python -m pytest tests/test_classify_core_motif_orbit_polarization_smoke.py -q` |
| Reproduce core-motif enrichment statistics | `docs/CORE_MOTIF_ENRICHMENT_STATS_2026_02_11.md` | `python tools/core_motif_enrichment_stats.py` | `python -m pytest tests/test_core_motif_enrichment_stats_smoke.py -q` |
| Reproduce core-motif anchor channels | `docs/CORE_MOTIF_ANCHOR_CHANNELS_2026_02_11.md` | `python tools/core_motif_anchor_channels.py` | `python -m pytest tests/test_core_motif_anchor_channels_smoke.py -q` |
| Reproduce full core-motif chain (all four layers) | `docs/CORE_MOTIF_ANCHOR_CHANNELS_2026_02_11.md` + related docs | `python tools/run_core_motif_chain.py` | `python -m pytest tests/test_run_core_motif_chain_smoke.py -q` |
| Reproduce minimal identity certificates at `z=(1,0)` | `docs/MINIMAL_GLOBAL_IDENTITY_CERTIFICATES_2026_02_11.md` | `python tools/minimal_global_identity_certificates.py` | `python -m pytest tests/test_minimal_global_identity_certificates_smoke.py -q` |
| Reproduce dual rigidity profile (negative vs positive) | `docs/GLOBAL_SIGN_RIGIDITY_DUAL_PROFILE_2026_02_11.md` | `python tools/global_sign_rigidity_dual_profile.py` | `python -m pytest tests/test_global_sign_rigidity_dual_profile_smoke.py -q` |
| Reproduce s12 universalization and Vogel scans | `docs/S12_UNIVERSALIZATION_2026_02_11.md` + `docs/VOGEL_UNIVERSAL_RESEARCH_2026_02_11.md` | `python tools/universalize_s12_algebra.py` and `python tools/vogel_universal_snapshot.py` | `python -m pytest tests/test_universalize_s12_algebra_smoke.py tests/test_vogel_universal_snapshot_smoke.py -q` |
| Reproduce the Vogel resonance bridge | `docs/VOGEL_RESONANCE_BRIDGE_2026_02_11.md` | `python tools/analyze_vogel_resonance_bridge.py` | `python -m pytest tests/test_analyze_vogel_resonance_bridge_smoke.py -q` |
| Reproduce the `GL(2,3)` involution conjugacy bridge | `docs/GL2_F3_INVOLUTION_CONJUGACY_2026_02_11.md` | `python tools/analyze_gl2_f3_involution_conjugacy.py` | `python -m pytest tests/test_analyze_gl2_f3_involution_conjugacy_smoke.py -q` |
| Reproduce the `AGL(2,3)` det-`2` involution class | `docs/AGL23_DET2_INVOLUTION_CLASS_2026_02_11.md` | `python tools/analyze_agl23_det2_involution_class.py` | `python -m pytest tests/test_analyze_agl23_det2_involution_class_smoke.py -q` |
| Reproduce the W33 neighbor action realizing `AGL(2,3)` | `docs/W33_NEIGHBOR_ACTION_AGL23_2026_02_11.md` | `python tools/analyze_w33_neighbor_action_agl23.py` | `python -m pytest tests/test_analyze_w33_neighbor_action_agl23_smoke.py -q` |
| Reproduce the orbit-stabilizer bridge | `docs/ORBIT_STABILIZER_BRIDGE_2026_02_11.md` | `python tools/analyze_orbit_stabilizer_bridge.py` | `python -m pytest tests/test_analyze_orbit_stabilizer_bridge_smoke.py -q` |
| Reproduce reduced-orbit stabilizer census | `docs/REDUCED_REP_STABILIZER_CENSUS_2026_02_11.md` | `python tools/analyze_reduced_rep_stabilizer_census.py` | `python -m pytest tests/test_analyze_reduced_rep_stabilizer_census_smoke.py -q` |
| Inspect reduced-orbit stabilizer outliers (non-identity `z`) | `docs/REDUCED_REP_STABILIZER_OUTLIERS_2026_02_11.md` | `python tools/analyze_reduced_rep_stabilizer_outliers.py` | `python -m pytest tests/test_analyze_reduced_rep_stabilizer_outliers_smoke.py -q` |
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
- `docs/NONTRIVIAL_UNSAT_CORE_GEOMETRY_2026_02_11.md`
- `docs/NONTRIVIAL_CORE_RULEBOOK_2026_02_11.md`
- `docs/CORE_RULEBOOK_MIN_CERT_LINK_2026_02_11.md`
- `docs/CORE_MOTIF_ORBIT_POLARIZATION_2026_02_11.md`
- `docs/CORE_MOTIF_ENRICHMENT_STATS_2026_02_11.md`
- `docs/CORE_MOTIF_ANCHOR_CHANNELS_2026_02_11.md`
- `docs/GLOBAL_SIGN_RIGIDITY_DUAL_PROFILE_2026_02_11.md`
- `docs/MINIMAL_GLOBAL_IDENTITY_CERTIFICATES_2026_02_11.md`
- `docs/README_EXTENSION_ONLINE_FINDINGS_2026_02_10.md` (raw web-source log)
- `docs/S12_UNIVERSALIZATION_2026_02_11.md`
- `docs/S12_JACOBI_FAILURE_PATTERN_2026_02_11.md`
- `docs/S12_SL27_Z3_BRIDGE_2026_02_11.md`
- `docs/VOGEL_UNIVERSAL_RESEARCH_2026_02_11.md`
- `docs/VOGEL_RESONANCE_BRIDGE_2026_02_11.md`
- `docs/GL2_F3_INVOLUTION_CONJUGACY_2026_02_11.md`
- `docs/AGL23_DET2_INVOLUTION_CLASS_2026_02_11.md`
- `docs/W33_NEIGHBOR_ACTION_AGL23_2026_02_11.md`
- `docs/ORBIT_STABILIZER_BRIDGE_2026_02_11.md`
- `docs/REDUCED_REP_STABILIZER_CENSUS_2026_02_11.md`
- `docs/REDUCED_REP_STABILIZER_OUTLIERS_2026_02_11.md`

## Contribution Notes

- Use `CONTRIBUTING.md` for local workflow and pre-commit guidance.
- Keep claims executable: each theorem update should include script path, test path, and artifact path.
- Prefer adding new result documents under `docs/` and generated outputs under `artifacts/`.

## GitHub Repository Metadata

- About text and topics are tracked in `.github/settings.yml`.
- Social preview image asset: `docs/assets/w33-social-preview.png`.
- Upload path in GitHub UI: `Settings -> General -> Social preview -> Upload an image`.
