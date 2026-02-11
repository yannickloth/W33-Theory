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

### Finite-case reduction and diagnostic plots

As a pragmatic step we implemented `tools/prove_exclude_z22.py` to perform the
symbolic fixed-line closure test and the subsequent exhaustive pulled-back
invariance check described above. The script reports no invariant
representatives for `z_map=(2,2)` on the canonical Hessian census; the same
verification is exercised by the smoke test `tests/test_prove_exclude_z22_smoke.py`
and by the unit-level check `tests/test_formal_proof_z22.py` added here.

For visual diagnostics we produce two small figures (Hessian medium run) via
`tools/plot_zmap_involution_profiles.py`:

- `artifacts/min_cert_census_medium_2026_02_10/figures/zmap_hist_hessian.png`
- `artifacts/min_cert_census_medium_2026_02_10/figures/match_count_hist_hessian.png`

Both the finite-case script and plotting script have smoke tests added under
`tests/` (`test_prove_exclude_z22_smoke.py` and
`test_plot_zmap_involution_profiles_smoke.py`).

This document is a living draft; the finite-case symbolic reduction above is
now implemented and machine-checked in the test suite. Contributions and
shorter formal lemmas are welcome as follow-ups.
