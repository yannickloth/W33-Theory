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

## Next steps for a full symbolic proof

- Formalize how `s(line,z)` transforms under a `z`-affine map and characterize
  necessary compatibility conditions for a certificate to be invariant under
  `(A, z_map)`.
- Show that for `z_map=(2,2)` these compatibility constraints contradict the
  canonical product-sign law (`P(line)` closed form) for some line class or
  witness configuration.
- Optionally, derive a short case analysis that rules out `(2,2)` using only
  the canonical shifted `P(line)` law in adapted gauges.

### Finite-case reduction and diagnostic plots

As a pragmatic step we implemented a small finite-case reduction that reduces
the exclusion of `z_map=(2,2)` to checking the (canonicalized)
representatives from the Hessian exact census. The script
`tools/prove_exclude_z22.py` performs a symbolic closure test on fixed lines
and, if necessary, a full invariance check across all adapted gauges. On our
medium run it reports no invariant representatives for `(2,2)` (see the
artifact `committed_artifacts/min_cert_census_medium_2026_02_10/e6_f3_trilinear_reduced_orbit_closed_form_equiv_hessian_exact_full.json`).

For visual diagnostics we produce two small figures (Hessian medium run) via
`tools/plot_zmap_involution_profiles.py`:

- `artifacts/min_cert_census_medium_2026_02_10/figures/zmap_hist_hessian.png`
- `artifacts/min_cert_census_medium_2026_02_10/figures/match_count_hist_hessian.png`

Both the finite-case script and plotting script have smoke tests added under
`tests/` (`test_prove_exclude_z22_smoke.py` and
`test_plot_zmap_involution_profiles_smoke.py`).

This document is a living draft; computational corroboration is already
available in the follow-up artifact set (PR #52). Contributions and
shorter formal lemmas are welcome as follow-ups.
