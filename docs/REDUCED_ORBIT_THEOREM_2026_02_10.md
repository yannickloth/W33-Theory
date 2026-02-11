# Reduced Orbit Theorem (2026-02-10)

**Theorem (Reduced Orbit Characterization).**

Let R be a canonical representative of a minimal full-sign obstruction certificate in the Hessian216 candidate space, canonicalized up to the action of affine maps and z-maps. Then R has reduced orbit size (1296) if and only if there exists an affine involution A in AGL(2,3) with det(A) = 2 and order 2, together with a z-map z in {(1,0), (2,0), (2,1)}, such that R is invariant under the combined action (A, z) (i.e., each witness row of R is mapped to a witness row of R by (A, z)).

Equivalently, after choosing an adapted affine gauge sending the distinguished affine flag (missing point, full-positive direction) to ((0,0), x-direction), R is invariant under the canonical diagonal involution diag(-1,1) together with one of the three allowed z-maps.

## Proof sketch (canonical algebraic argument)

1. (Matrix spectral type)
   Any 2x2 matrix over F3 of order 2 and determinant 2 has eigenvalues {1, -1} and is diagonalizable over F3. Therefore such a matrix is conjugate in GL(2,3) to the canonical diagonal matrix diag(-1,1).

2. (Gauge conjugation and invariance)
   If A is conjugate to diag(-1,1), then A = g^{-1} diag(-1,1) g for some gauge g in AGL(2,3). Conjugation preserves invariance: R is fixed by A (with some z-map) iff g(R) is fixed by diag(-1,1) (with the corresponding pulled-back z-map).

3. (The z-map restriction)
   The allowed z-maps {(1,0),(2,0),(2,1)} are exactly those that, when paired with diag(-1,1) in the adapted gauge, produce the observed fixed/swapped line pattern on affine lines that matches the empirical reduced representatives. This can be verified by checking the finite set of possibilities.

> See the short corollary and publication blurb: `docs/REDUCED_ORBIT_COROLLARY_2026_02_11.md`.
> The short symbolic exclusion and machine-checked modules are in `tools/formal_z22_proof.py`, `tests/test_formal_z22_module.py`, and `proofs/lean/z22_exclusion.lean`.

4. (Computational sufficiency and necessity)
   We verify the condition on an exhaustive Hessian canonical-representative census (256 representatives). The computational checker `tools/check_reduced_orbit_closed_form_equiv.py` tests equivalence between the involution-based orbit-reduction definition and the gauge-canonical diag(-1,1) formulation. On the exhaustive Hessian dataset, the two tests are equivalent (zero mismatches), and the stronger match-count profile is exact: `201` full-orbit reps have `0` matches while all `55` reduced reps have exactly `1` match.

5. (z-map restriction is exact under full affine z scan)
   Extending the checker to all affine `z` maps (`(a,b)` with `a in {1,2}`, `b in F3`, total `6`) gives the same reduced/full split and finds matches only for `z` maps `{(1,0),(2,0),(2,1)}`. No additional `z` map contributes any match.

### Corollary (symbolic exclusion of `z=(2,2)`)

A short, purely symbolic contradiction rules out `z=(2,2)` in an adapted gauge. Work in the gauge sending the distinguished affine flag to `((0,0), x-direction)` so that the canonical involution is `A_GAUGE = diag(-1,1)` acting by `(x,y) -> (2x,y)`.

- The vertical line `L: x=0` is fixed by `A_GAUGE` and, by the coordinate-free shifted product law, has product-sign `P(L)=+1` (since `b*c == 0` for its normalized equation).
- The affine `z`-map `z -> 2*z + 2` fixes `z=1`, so invariance would force `s(L,1)` to equal the global pulled-back sign on that row. Because fixed-line swapping forces `s(L,0)=s(L,2)`, one has `P(L)=s(L,1)`.
- The closed-form full-sign rule gives `s(L,1) = -1` for `(a,b,c)=(1,0,0)`, contradicting `P(L)=+1`.

Hence `z=(2,2)` cannot preserve the full sign field for any involution conjugate to `diag(-1,1)`, so `z=(2,2)` is algebraically excluded. (See `docs/REDUCED_ORBIT_FORMAL_PROOF_2026_02_11.md` and `tests/test_formal_proof_z22.py` for the machine-checked reduction.)

### Corollary (global exclusion under closed-form sign law)

A stronger global scan now checks all affine `u`-maps (and the involution subset)
against the closed-form sign law with `z_map=(2,2)`. The checker
`tools/prove_z22_no_global_stabilizer.py` finds:

- `864` candidates checked in full `AGL(2,3)` (including `eps in {+1,-1}`), `0` matches.
- `216` candidates checked in the `det=2`, order-`2` involution subset, `0` matches.

So `z=(2,2)` is not only absent from reduced-representative matches; it has
no global full-sign stabilizer in these candidate spaces.

## Scripts & tests

- Computation and candidate derivation: `tools/derive_reduced_orbit_closed_form.py` (outputs `docs/MIN_CERT_REDUCED_ORBIT_RULE_2026_02_10.md`).
- Equivalence checker (canonical algebraic test): `tools/check_reduced_orbit_closed_form_equiv.py` (writes `artifacts/e6_f3_trilinear_reduced_orbit_closed_form_equiv.json`).
- Global z22 stabilizer exclusion: `tools/prove_z22_no_global_stabilizer.py` (writes `artifacts/z22_global_stabilizer_exclusion_2026_02_11.json` and `docs/Z22_GLOBAL_STABILIZER_EXCLUSION_2026_02_11.md`).
- Global z-map census: `tools/classify_global_full_sign_stabilizers.py` (writes `artifacts/global_full_sign_stabilizer_census_2026_02_11.json` and `docs/GLOBAL_FULL_SIGN_STABILIZER_CENSUS_2026_02_11.md`).
- Minimal contradiction cores: `tools/minimal_global_full_sign_cores.py` (writes `artifacts/minimal_global_full_sign_cores_2026_02_11.json` and `docs/MINIMAL_GLOBAL_FULL_SIGN_CORES_2026_02_11.md`).
- Nontrivial UNSAT core geometry census: `tools/classify_nontrivial_unsat_core_geometry.py` (writes `artifacts/nontrivial_unsat_core_geometry_2026_02_11.json` and `docs/NONTRIVIAL_UNSAT_CORE_GEOMETRY_2026_02_11.md`).
- Nontrivial core rulebook compression: `tools/nontrivial_core_rulebook.py` (writes `artifacts/nontrivial_core_rulebook_2026_02_11.json` and `docs/NONTRIVIAL_CORE_RULEBOOK_2026_02_11.md`).
- Rulebook-to-census motif link: `tools/link_core_rulebook_to_min_cert_census.py` (writes `artifacts/core_rulebook_min_cert_link_2026_02_11.json` and `docs/CORE_RULEBOOK_MIN_CERT_LINK_2026_02_11.md`).
- Minimal positive identity certificates: `tools/minimal_global_identity_certificates.py` (writes `artifacts/minimal_global_identity_certificates_2026_02_11.json` and `docs/MINIMAL_GLOBAL_IDENTITY_CERTIFICATES_2026_02_11.md`).
- Dual rigidity profile: `tools/global_sign_rigidity_dual_profile.py` (writes `artifacts/global_sign_rigidity_dual_profile_2026_02_11.json` and `docs/GLOBAL_SIGN_RIGIDITY_DUAL_PROFILE_2026_02_11.md`).
- Smoke tests: `tests/test_derive_reduced_orbit_closed_form_smoke.py`, `tests/test_check_reduced_orbit_closed_form_equiv_smoke.py`, `tests/test_prove_z22_no_global_stabilizer_smoke.py`, `tests/test_classify_global_full_sign_stabilizers_smoke.py`, `tests/test_minimal_global_full_sign_cores_smoke.py`, `tests/test_classify_nontrivial_unsat_core_geometry_smoke.py`, `tests/test_nontrivial_core_rulebook_smoke.py`, `tests/test_link_core_rulebook_to_min_cert_census_smoke.py`, `tests/test_minimal_global_identity_certificates_smoke.py`, `tests/test_global_sign_rigidity_dual_profile_smoke.py`.
- GL-conjugacy unit test (new): `tests/test_gl2_3_involution_conjugacy.py`.

## Notes and future work

- The above proof is a concise, canonical algebraic argument augmented by exhaustive computational verification on the canonical Hessian representative census. The finite-case reduction to exclude `z=(2,2)` has now been implemented and machine-checked (`tools/prove_exclude_z22.py`, `tests/test_prove_exclude_z22_smoke.py`, `tests/test_formal_proof_z22.py`), and a global closed-form scan now confirms zero stabilizers for `z=(2,2)` in full `AGL(2,3)` as well (`tools/prove_z22_no_global_stabilizer.py`, `tests/test_prove_z22_no_global_stabilizer_smoke.py`). The surviving identity cell at `z=(1,0)` is now also quantified by exact positive certificates: minimal witness size `6` in full `AGL(2,3)` and `5` in `Hessian216` (`tools/minimal_global_identity_certificates.py`), and this gap is robust under distinct-line and striation-complete witness constraints. Dually, contradiction cores for nontrivial global cells lift from `3` to `4` when striation-complete witnesses are required (`5` at involution `z=(1,0)`), giving a context-complete rigidity profile. A fully symbolic, machine-assisted formal proof that removes the finite verification step remains a short-term target; a compact derivation explaining exactly why the allowed `z`-maps are `{(1,0),(2,0),(2,1)}` would be valuable.
- The above proof is a concise, canonical algebraic argument augmented by exhaustive computational verification on the canonical Hessian representative census. The finite-case reduction to exclude `z=(2,2)` has now been implemented and machine-checked (`tools/prove_exclude_z22.py`, `tests/test_prove_exclude_z22_smoke.py`, `tests/test_formal_proof_z22.py`), and a global closed-form scan now confirms zero stabilizers for `z=(2,2)` in full `AGL(2,3)` as well (`tools/prove_z22_no_global_stabilizer.py`, `tests/test_prove_z22_no_global_stabilizer_smoke.py`). The surviving identity cell at `z=(1,0)` is now also quantified by exact positive certificates: minimal witness size `6` in full `AGL(2,3)` and `5` in `Hessian216` (`tools/minimal_global_identity_certificates.py`), and this gap is robust under distinct-line and striation-complete witness constraints. Dually, contradiction cores for nontrivial global cells lift from `3` to `4` when striation-complete witnesses are required (`5` at involution `z=(1,0)`), giving a context-complete rigidity profile. In addition, exhaustive nontrivial core-geometry census shows every size-`3` core in `AGL/Hessian` is exactly one full parallel-class triplet, with identical core-signature families across the two spaces (`tools/classify_nontrivial_unsat_core_geometry.py`), and rulebook compression reduces those families to low-complexity coordinate laws with one unique non-cartesian case (`tools/nontrivial_core_rulebook.py`). A fully symbolic, machine-assisted formal proof that removes the finite verification step remains a short-term target; a compact derivation explaining exactly why the allowed `z`-maps are `{(1,0),(2,0),(2,1)}` would be valuable.

- See `docs/NOVEL_CONNECTIONS_2026_02_10.md` for discussion and empirical statistics.
