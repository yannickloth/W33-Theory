# Canonical forbid decision

**Canonical forbid chosen:** `[0,20,23]`

**Rationale:**
- Anchored CP‑SAT for forbid `[0,20,23]` was run across the sign‑consistent W set (`0,4,5,6,7,8,9,10,11,12,13,14,15`) and found **FEASIBLE** mappings with **matched=19** for every tested W (see `reports/anchor_forbid_0-20-23.md`).
- GF(2) contradiction certificates exist for the previously-discovered optimal mappings (see `artifacts/gf2_certificates.json`), which justifies forbidding a singleton triad to repair parity contradictions.

**Notes:**
- We also computed full-group and AGL(2,3)×Z3 orbits and tested the canonical picks from multiple tie-break rules (`lex_min`, `max_stab`). The final choice favors reproducibility and anchored feasibility across the test set.
- Artifacts & summary: `artifacts/canonical_forbid_choice.json`, `reports/canonical_forbid_verification_summary.md`.

**Next steps:**
- Add the canonical forbid to CI tests and final PR; auto-merge on green as authorized.
