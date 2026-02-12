# Project map — W33 / E8 / E6 repository

## Purpose
Concise mapping from major theoretical claims → canonical code locations → verification/tests/artifacts. Use this as the single-page onboarding map for reviewers.

---

### Core mathematical claims
- 240 ↔ 240 bijection (W33 edges ↔ E8 roots)
  - Code: `tools/construct_w33_e8_bijection.py`, `tools/w33_e8_mapping_analysis.py`
  - Tests: `tests/test_e8_root_edge_bijection.py`
  - Artifacts: `w33_e8_bijection_data.json`, `artifacts_archive/e8_root_to_w33_edge.json`

- W33 = SRG(40,12,2,4); Aut(W33) = W(E6) = 51840
  - Docs: `MASTER_INDEX_JAN2026.md`, `COMPLETE_SUMMARY.md`
  - Code: `scripts/finite_geometry/compute_w33_aut.py`, `scripts/w33_complete_analysis.py`
  - Tests: `tests/test_w33_core.py`, `tests/test_edge_orbit_census_smoke.py`

- Tomotope / Reye / Freudenthal → E8 (triality bridge)
  - Docs: `TOMOTOPE_REYE_E8_SYNTHESIS.md`, `Freudenthal` notes in docs/
  - Code: `tools/tomotope_reye_e8_connection.py`, `tools/deep_bijection_analysis.py`

- E6 embedding, 27 representation → particle map, masses and mixings
  - Code: `CKM_FROM_27_LINES.py`, `MASS_PREDICTIONS.py`, `PHYSICS_PREDICTIONS_MASTER.py`
  - Tests: `tests/test_e6_27rep_minuscule.py`, `tests/test_ckm_predictor.py` (smoke)
  - Artifacts: `PHYSICS_PREDICTIONS_MASTER.json`

---

### Computational verification / pipelines
- Bijection construction and structural checks
  - Entry-point: `tools/construct_w33_e8_bijection.py` (produces `w33_e8_bijection_data.json`)
  - Validation scripts: `tools/w33_e8_mapping_analysis.py`, `scripts/w33_e8_bijection.py`

- Prediction synthesis
  - Entry-point: `PHYSICS_PREDICTIONS_MASTER.py` (produces `PHYSICS_PREDICTIONS_MASTER.json`)
  - Supporting: `MASS_PREDICTIONS.py`, `CKM_FROM_27_LINES.py`, `RG_PRECISION_MASSES.py`

- Formalization / proofs
  - Directory: `proofs/lean/` (Lean artifacts & generated conjugators)
  - Scripts: `scripts/generate_conjugators_lean.py`
  - Tests: `tests/test_proofs_execution.py`, `tests/test_lean_workflow_smoke.py`

---

### High-value verification coverage (status)
- Unit tests: broad coverage for algebraic building blocks (many `tests/` present)
- Integration tests: bijection & prediction pipelines have smoke/integration checks
- Gaps: formal, machine-checked proofs for bijection & physical-derivation chain

### External resources (recommended reading)
- `docs/EXTERNAL_WEBSITES.md` — curated external websites (Marcelis, Bendwavy/Klitzing, finitegeometry.org)
- `EXTERNAL_RESOURCES_SYNTHESIS.py` — synthesis and annotated notes from Marcelis & Cullinane (already in repo)

---

## Suggested next priorities (short list)
1. Add an integration test that asserts `w33_e8_bijection_data.json` equals the canonical artifact in `artifacts_archive/` (makes CI pick up `tools/construct_*` outputs). ✅
2. Formalize key lemmas (W33→E6 bijection; triangle→mass mapping) in `proofs/lean/` and wire tests that run the Lean checks. (medium)
3. Produce a reproducible predictions report (one-click) and publish `committed_artifacts/predictions_YYYYMMDD.json` (high value for review). (short)
4. Add a README section `docs/REPRODUCE.md` that lists the minimal commands to reproduce the central artifacts. (quick win)

---

If you want I can: run the prediction pipeline and open a PR that adds the integration test (1), or start porting key proofs into `proofs/lean/` (2). Tell me which to prioritize or say "Surprise me" and I'll continue with (1) then (3).
