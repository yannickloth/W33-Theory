# Reduced Orbit: Formal Derivation (Draft) — 2026-02-11

This short draft collects compact algebraic arguments that explain the
involution-based reduced-orbit characterization and the observed restriction
on allowed `z` involutions.

## Lemma 1 (GL(2,3) involutions)

Let `A` be a `2x2` matrix over `F_3` with `det(A) = 2` (equivalently `-1`) and
`A^2 = I` (order 2). Then the characteristic polynomial of `A` divides
`x^2 - 1 = (x-1)(x+1)`. Since `det(A) = (-1)*1 = -1` the eigenvalues are
`1` and `-1` (which in `F_3` is `2`). Distinct eigenvalues imply `A` is
diagonalizable over `F_3`, hence `A` is conjugate in `GL(2,3)` to the
canonical diagonal matrix `diag(-1,1)`.

*Proof.* The minimal polynomial of `A` divides `x^2 - 1` and has distinct
roots, so `A` has a full eigenbasis and is conjugate to the diagonal matrix
of its eigenvalues.

## Lemma 2 (Affine `z` involutions on `Z_3`)

An affine `z` map over `F_3` has form `z -> a*z + b` with `a,b in F_3`. It is
an involution iff applying it twice is the identity. This gives the pair of
equations `a^2 = 1` and `b*(a + 1) = 0` in `F_3`.

Solving yields `a=1, b=0` or `a=2` with any `b` (so `z`-involutions are
exactly `(1,0)` and `(2,b)` for `b in F_3`). Thus there are four affine
`z`-involutions in total: `(1,0)`, `(2,0)`, `(2,1)`, `(2,2)`.

## Short explanation of the observed `z`-map restriction

The algebraic lemmas above reduce the problem: candidate `z`-involutions are
only `(1,0)` or `(2,b)`. The further restriction to the observed set
`{(1,0),(2,0),(2,1)}` is not purely a linear-algebraic consequence of the
`A` conjugacy class: it depends on the concrete sign-field `s(line,z)` and the
global product sign geometry `P(line)`. In other words, invariance under the
combined action `(A, z_map)` for a particular certificate can fail for some
`(2,b)` because the induced permutation of witness rows collides with the
per-row sign data.

In our exhaustive Hessian census we observe matches only for
`(1,0)`, `(2,0)`, and `(2,1)` (with empirical histogram counts); `(2,2)` is
never observed. That empirical exclusion is captured by the smoke test
`tests/test_reduced_orbit_zmap_restriction_smoke.py` and by the
artifact `committed_artifacts/min_cert_census_medium_2026_02_10/...`.

## Lemma 3 (Exclusion of `z=(2,2)`)

**Statement.** No canonical Hessian representative (in the exact census) is
invariant under an affine involution whose linear part has `det = 2` (i.e.
is conjugate to `diag(-1,1)`) together with the `z`-affine map `z -> 2*z + 2`.

**Proof (finite-case reduction, concise).**

1. By Lemma 1 every candidate linear part `A` with `det(A)=2` and `A^2=I` is
   `GL(2,3)`-conjugate to `diag(-1,1)`. Conjugacy invariance of the
   invariance condition allows us to pull a candidate involution back to the
   canonical affine representative `A_GAUGE := diag(-1,1)` in an adapted
   gauge.

2. The product-sign geometry determines a unique affine flag (a single point
   missing from all negative lines and a single direction with all-positive
   lines). For any gauge sending that flag to `((0,0), x-direction)` the
   coordinate-free shifted product law holds: `P(line) = +1` iff `b*c == 0`
   for normalized `a*x + b*y = c` (see the implementation
   `_line_product_coordinate_free_shifted_rule_check`).

3. If `(A_GAUGE, z_map=(2,2))` preserved the full sign field up to a global
   sign `epsilon`, then every line fixed by `A_GAUGE` would have to carry a
   set of `z`-labels closed under `z -> 2*z + 2` (an elementary combinatorial
   constraint).

4. There are finitely many adapted gauges; pulling back `A_GAUGE` through the
   (finite) set of adapted gauges produces a small explicit list of affine
   elements to check on the finite canonical dataset. The script
   `tools/prove_exclude_z22.py` implements this reduction: it first applies
   the symbolic fixed-line closure test from (3) and, whenever closure
   holds, performs a full pulled-back witness equality check. Running the
   script on the canonical Hessian census finds no invariant representatives,
   which completes the finite proof by exhaustion.

QED.

#### Short symbolic exclusion (pure algebraic)

A compact, purely symbolic contradiction is immediate in the adapted gauge.
Work in the gauge where the affine flag is `((0,0), x-direction)` and
`A_GAUGE = diag(-1,1)` acts by `(x,y) -> (2x,y)` over `F_3`.

- The vertical line `L: x=0` has normalized coefficients `(a,b,c)=(1,0,0)` and
  is fixed by `A_GAUGE` (apply `A_GAUGE` to its points and the set is unchanged).
- The `z`-map `z -> 2*z + 2` fixes `z=1`, so invariance of the full sign field
  would force the global sign `epsilon = 1` (since `s(L,1) = epsilon*s(L,1)`).
- For any fixed line under this involution, the `0<->2` swap implies
  `s(L,0) = s(L,2)`, hence
  `P(L) = s(L,0)*s(L,1)*s(L,2) = s(L,1)`.
- The coordinate-free product law (`P(line)=+1 iff b*c==0`) gives
  `P(L) = +1` for `L=x=0` (since `b*c = 0`).
- The closed-form full sign rule for `(a,b)=(1,0)` with `c=0` and `z=1` gives
  `s(L,1) = -1` (because `c^2 + 2c + z = 1 != 2`). Thus `P(L) = +1` but
  `s(L,1) = -1`, a contradiction.

Therefore `z_map=(2,2)` cannot preserve the sign field with any `A` conjugate
to `diag(-1,1)`, completing a short symbolic exclusion without recourse to
exhaustive checking.


### Finite-case reduction and diagnostic plots

As a pragmatic step we implemented `tools/prove_exclude_z22.py` to perform the
symbolic fixed-line closure test and the subsequent exhaustive pulled-back
invariance check described above. The script reports no invariant
representatives for `z_map=(2,2)` on the canonical Hessian census; the same
verification is exercised by the smoke test `tests/test_prove_exclude_z22_smoke.py`
and by the unit-level check `tests/test_formal_proof_z22.py` added here. For a
fully self-contained symbolic argument we also added `tools/formal_z22_proof.py`
(and unit test `tests/test_formal_z22_module.py`), which formalizes the short
`x=0` contradiction in an adapted gauge without referring to the census. A
Lean 4 skeleton formalization is available at `proofs/lean/z22_exclusion.lean`
as a starting point for a machine-checked proof; it now includes explicit
`zMap_one` and `z22_contradiction_via_zMap` lemmas for the same fixed-point
contradiction path.

To tighten the exclusion further, we added
`tools/prove_z22_no_global_stabilizer.py`, which checks a stronger global
statement directly on the closed-form sign law:
there is no full-sign stabilizer for `z_map=(2,2)` in either (i) all
`AGL(2,3)` candidates (`864` affine/epsilon combinations) or (ii) the
`det=2`, order-`2` involution subset (`216` combinations). Both match counts
are exactly `0`. This is covered by
`tests/test_prove_z22_no_global_stabilizer_smoke.py` and documented in
`docs/Z22_GLOBAL_STABILIZER_EXCLUSION_2026_02_11.md`.

We also added `tools/classify_global_full_sign_stabilizers.py` for a full
`z`-map census. It shows that in both `AGL(2,3)` and `Hessian216`, the only
global full-sign stabilizer cell is `z_map=(1,0)` with exactly one match
(the trivial symmetry), while the involution subset has zero matches for all
`z` maps. See `docs/GLOBAL_FULL_SIGN_STABILIZER_CENSUS_2026_02_11.md` and
`tests/test_classify_global_full_sign_stabilizers_smoke.py`.

Finally, `tools/minimal_global_full_sign_cores.py` computes minimal UNSAT cores
for each global cell. Nontrivial `z` cells in `AGL(2,3)` and `Hessian216`
admit compact contradiction cores of size `3`; the involution subset has core
size `4` at `z=(1,0)` and size `3` elsewhere. This quantifies how many
line/z constraints are minimally needed to rule out each cell.

Complementing those UNSAT witnesses, `tools/minimal_global_identity_certificates.py`
computes exact positive certificates for the unique surviving global cell
(`z=(1,0)`). The identity is isolated by `6` constraints in full `AGL(2,3)`
and by `5` constraints in `Hessian216`, with exact multiplicities
`688` and `33` minimal certificates respectively.

For visual diagnostics we produce two small figures (Hessian medium run) via
`tools/plot_zmap_involution_profiles.py`:

- `artifacts/min_cert_census_medium_2026_02_10/figures/zmap_hist_hessian.png`
- `artifacts/min_cert_census_medium_2026_02_10/figures/match_count_hist_hessian.png`

Both the finite-case script and plotting script have smoke tests added under
`tests/` (`test_prove_exclude_z22_smoke.py` and
`test_plot_zmap_involution_profiles_smoke.py`). The new global exclusion check
is covered by `test_prove_z22_no_global_stabilizer_smoke.py`.

This document is a living draft; the finite-case symbolic reduction above is
now implemented and machine-checked in the test suite. Contributions and
shorter formal lemmas are welcome as follow-ups.
