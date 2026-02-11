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

4. (Computational sufficiency and necessity)
   We verify the condition on an exhaustive Hessian canonical-representative census (256 representatives). The computational checker `tools/check_reduced_orbit_closed_form_equiv.py` tests equivalence between the involution-based orbit-reduction definition and the gauge-canonical diag(-1,1) formulation. On the exhaustive Hessian dataset, the two tests are equivalent (zero mismatches).

## Scripts & tests

- Computation and candidate derivation: `tools/derive_reduced_orbit_closed_form.py` (outputs `docs/MIN_CERT_REDUCED_ORBIT_RULE_2026_02_10.md`).
- Equivalence checker (canonical algebraic test): `tools/check_reduced_orbit_closed_form_equiv.py` (writes `artifacts/e6_f3_trilinear_reduced_orbit_closed_form_equiv.json`).
- Smoke tests: `tests/test_derive_reduced_orbit_closed_form_smoke.py`, `tests/test_check_reduced_orbit_closed_form_equiv_smoke.py`.
- GL-conjugacy unit test (new): `tests/test_gl2_3_involution_conjugacy.py`.

## Notes and future work

- The above proof is a concise, canonical algebraic argument augmented by exhaustive computational verification on the canonical Hessian representative census. A fully symbolic, machine-assisted formal proof (removing the finite computational check) is desirable and remains a short-term target. In particular, a compact derivation that explains why the set of allowed z-maps is exactly `{(1,0),(2,0),(2,1)}` would be valuable.

- See `docs/NOVEL_CONNECTIONS_2026_02_10.md` for discussion and empirical statistics.
