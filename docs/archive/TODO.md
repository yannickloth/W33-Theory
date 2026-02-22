Short TODOs and next actions (updated 2026-02-09)

High priority:
- [x] Validate qutrit Heisenberg identification (Pillar 21) across all vertices using `scripts/w33_heisenberg_qutrit.py` (checks/*.json) âœ…
- [x] Build canonical translation lifts Tx, Ty and central Z; produce `W33_Heisenberg_generators_Tx_Ty_Z.json` and `W33_translation_lifts_canonical.csv` âœ…
- [x] Propagate canonical phases to all 12 N12 vectors using affine (AGL) transport + Weyl translations; verify `parallelogram_holonomy_vs_bargmann.json` = 54/54 âœ…
- [x] Make Pillar 21 tests Linux/CI-friendly (no Windows-only `py` runner; use `sys.executable`) âœ…
- [x] Add tests: `tests/test_heisenberg_qutrit_structure.py`, `tests/test_heisenberg_translations.py` âœ…
- [x] Package holonomy push bundle: `artifacts/bundles/W33_Heisenberg_action_bundle_20260209_v1/analysis/W33_holonomy_push_bundle_20260209.zip` âœ…
- [x] Run triangle decomposition (`scripts/w33_triangle_decomposition.py`) and record result: `checks/PART_CVII_triangle_decomp_1770661095.json` (160 = 90 + 30 + 30 + 10) âœ…

Medium priority:
- [x] Add a lightweight CI job that runs only the Pillar 21 / Clifford-lift tests (fast regression signal) in `/.github/workflows`
- [x] Extend `tools/phase_correct_mubs.py` to optionally write an explicit `H27_vertices_as_F3_cube_xy_t_holonomy_gauge.csv` (record of the solved global t-gauge)
- [x] Sweep other bundles (AG23 qutrit MUB bundle, cubic-surface dictionary) to confirm portability of the phase-correction workflow

Research / Theory tasks:
- [ ] Formalize the link: Heisenberg(F3) â†” E6 cubic invariant on the 27. Read/annotate Manivel, Landsberg & Mukai references; attempt to express the cubic form in terms of the Heisenberg structure on the 27 points.
- [x] Compute explicit structure constants / trilinear map 27x27x27 -> Z3 (or F3 dual) and compare with cubic trilinear invariant (over C) - look for a finite-field analogue over F3. (`tools/build_e6_f3_trilinear_map.py`, `artifacts/e6_f3_trilinear_map.json`)
- [x] Analyze symmetry breaking of the E6 F3 trilinear sign layer under AG(2,3)/Hessian affine actions. (`tools/analyze_e6_f3_trilinear_symmetry_breaking.py`, `artifacts/e6_f3_trilinear_symmetry_breaking.json`)
- [ ] Publish a short note (W33 Pillar 21: Heisenberg phase-space identification) with examples and computational proofs (link to the `analysis` artifacts and tests).

Low priority / polishing:
- [ ] Add a PR summary + merge PR (#38) once CI is green
- [ ] Add README snippet and `W33_COMPLETE_SOLUTION.md` update to reference Pillar 21 (done: README updated; add W33_COMPLETE_SOLUTION cross-ref)

If you'd like, I can start on any of the items above â€” say which to prioritize next and I'll take it on.
