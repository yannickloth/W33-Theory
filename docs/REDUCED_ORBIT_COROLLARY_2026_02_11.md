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
`zMap_one` and `z22_contradiction_via_zMap` in `proofs/lean/z22_exclusion.lean`.

Global strengthening:
- closed-form stabilizer scan for `z=(2,2)` gives zero matches in full
  `AGL(2,3)` (`0/864`) and in the involution subset (`0/216`)
  via `tools/prove_z22_no_global_stabilizer.py`.
- full `z`-map census keeps only trivial identity cells at `z=(1,0)`
  (`tools/classify_global_full_sign_stabilizers.py`).
- minimal contradiction-core extraction shows nontrivial global cells are
  eliminated by compact cores (size `3` in `AGL/Hessian`) via
  `tools/minimal_global_full_sign_cores.py`.
- minimal positive-certificate extraction for the surviving identity cell
  `z=(1,0)` gives witness size `6` in full `AGL(2,3)` and `5` in `Hessian216`
  via `tools/minimal_global_identity_certificates.py`; this `6` vs `5` split
  persists under distinct-line and striation-complete witness constraints.
