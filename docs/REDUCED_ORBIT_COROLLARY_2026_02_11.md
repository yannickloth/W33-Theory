# Reduced Orbit Corollary (Short)

In an adapted affine gauge sending the distinguished affine flag to
((0,0), x-direction) the canonical diagonal involution A = diag(-1,1)
acts by (x,y) -> (2x,y) over F3. The vertical line L: x=0 is fixed by A
and, by the coordinate-free shifted product law, satisfies P(L) = +1.
The affine z-map z -> 2*z + 2 fixes z = 1, while the closed-form full-sign
law predicts s(L,1) = -1 for L. These conclusions are incompatible, which
provides a short algebraic contradiction ruling out z=(2,2) for any
representative invariant under such an involution. The argument is both
symbolic and machine-checked (see `tools/formal_z22_proof.py` and
`tests/test_formal_z22_module.py`), with a Lean skeleton now exposing both
`zMap_one`, `zMap_involution`, and `z22_contradiction_via_zMap` in
`proofs/lean/z22_exclusion.lean`.
In the same Lean file, `zMap_fixed_iff` pins `z=1` as the unique fixed point
of `z -> 2*z+2` and `zMap_table` makes the `0 <-> 2` swap explicit.
It now also includes `zMap_fixed_point_unique`,
`z22_contradiction_of_fixed_point`, and
`z22_contradiction_of_fixed_point_via_zMap`, so the contradiction is reusable
from an abstract fixed-point hypothesis and not only from the literal `z=1`.
The Lean skeleton now also exposes
`z22_no_fixed_point_stabilizer` and
`z22_no_fixed_point_stabilizer_via_zMap`, i.e. there exists no `z` fixed by
`z -> 2*z+2` for which vertical-line product/full signs can agree.

Global strengthening:
- closed-form stabilizer scan for `z=(2,2)` gives zero matches in full
  `AGL(2,3)` (`0/864`) and in the involution subset (`0/216`)
  via `tools/prove_z22_no_global_stabilizer.py`.
- full `z`-map census keeps only trivial identity cells at `z=(1,0)`
  (`tools/classify_global_full_sign_stabilizers.py`).
- minimal contradiction-core extraction shows nontrivial global cells are
  eliminated by compact cores (size `3` in `AGL/Hessian`) via
  `tools/minimal_global_full_sign_cores.py`.
- under striation-complete witnesses, those contradiction cores lift to size
  `4` in nontrivial `AGL/Hessian` cells and to `5` for involution mode at
  `z=(1,0)` (same tool).
- exhaustive core-geometry census shows every nontrivial size-`3` UNSAT core
  in `AGL/Hessian` is a full affine parallel class triplet (same direction,
  three offsets) via `tools/classify_nontrivial_unsat_core_geometry.py`.
- rulebook compression reduces each nontrivial core family to compact
  coordinate constraints on `(z0,z1,z2)` with a unique non-cartesian case at
  `z=(1,1)` in direction `x` via `tools/nontrivial_core_rulebook.py`.
- minimal positive-certificate extraction for the surviving identity cell
  `z=(1,0)` gives witness size `6` in full `AGL(2,3)` and `5` in `Hessian216`
  via `tools/minimal_global_identity_certificates.py`; this `6` vs `5` split
  persists under distinct-line and striation-complete witness constraints.
- dual profile synthesis (`tools/global_sign_rigidity_dual_profile.py`) shows
  the positive-minus-negative gap contracts by exactly one under
  striation-complete constraints in both `AGL` and `Hessian216`.
- cross-link to minimal-certificate census
  (`tools/link_core_rulebook_to_min_cert_census.py`) finds zero overlap with
  nontrivial core motifs in `agl_exact_full` (`0/7`) but positive overlap in
  Hessian datasets (`18/79` exact full, `30/256` exhaustive2), with dominant
  overlap motif `x:(1,1,0)`.
- orbit-polarization refinement
  (`tools/classify_core_motif_orbit_polarization.py`) shows the dominant
  motif `x:(1,1,0)` is a high-precision full-orbit marker in Hessian
  representatives (`34/36` overlap occurrences at orbit `2592`).
- enrichment refinement (`tools/core_motif_enrichment_stats.py`) quantifies
  that marker as statistically enriched for orbit `2592` in combined Hessian
  datasets (`p=0.01355`, lift `1.176`).
- anchor-channel refinement (`tools/core_motif_anchor_channels.py`) yields a
  high-precision abstaining classifier:
  anchors `x:(1,1,0)` (full) and `x:(2,2,1)` (reduced), precision `36/38=0.947`
  on combined Hessian reps when the anchor rule fires.
