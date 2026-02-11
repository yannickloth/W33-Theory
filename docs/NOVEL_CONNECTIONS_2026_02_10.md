# Novel Connections (2026-02-10)

For raw source-mining notes and search-to-hypothesis chaining, see
`docs/README_EXTENSION_ONLINE_FINDINGS_2026_02_10.md`.

## New computational result

Using the new `F3` trilinear extraction (`tools/build_e6_f3_trilinear_map.py`) and
the Heisenberg labeling on H27, we now have a sparse finite-field cubic model with:

- `45` unordered nonzero triads (`270` ordered symmetric entries),
- geometric split `36` affine-line triads + `9` fiber triads,
- explicit per-line/per-layer sign field `s(line, z)`.

This is exported to:

- `artifacts/e6_f3_trilinear_map.json`
- `artifacts/e6_f3_trilinear_map.md`

## New symmetry-breaking probe

`tools/analyze_e6_f3_trilinear_symmetry_breaking.py` quantifies how the sign layer
changes affine/Hessian symmetries:

- support-only affine lines retain full affine symmetry,
- full sign field stabilizer collapses strongly (identity in current gauge),
- line-product sign keeps a small residual subgroup.
- empirical closed-form for line-product sign:
  `P(line)=+1 iff b*(a+b+c)=0 mod 3` for normalized line equation `a*x+b*y=c`.
- empirical closed-form for full sign field `s(line,z)`:
  piecewise by line direction (the `(a,b)` of normalized `a*x+b*y=c`), now checked in `tools/analyze_e6_f3_trilinear_symmetry_breaking.py`.
- exact affine parametrization of the residual line-product subgroup in `AGL(2,3)`:
  `A=[[a,0],[c,d]], shift=(a-1,c+d-1)`, with `a,d in F3*`, `c in F3`, giving 12 elements.
- resulting residual group structure matches `D12` (dihedral order 12), with determinant-1 slice a cyclic `C6`.
- new flag-geometric interpretation from computation:
  the `-1` lines miss exactly one affine point (`[2,2]`), and the `+1` lines are exactly
  `(all lines through [2,2]) union (the full x-constant parallel class)`.
- equivalent shifted law around the missing point:
  in translated coordinates centered at `[2,2]`, `P(line)=+1 iff b*c_shift=0`
  (with normalized `a*x+b*y=c` and `c_shift = c - a*p_x - b*p_y`).
- gauge-independent canonical form check:
  for every affine gauge that sends `(missing point, distinguished direction)` to
  `((0,0), x-direction)`, the transformed rule is exactly `P(line)=+1 iff b*c=0`.
- residual subgroup identity:
  the 12-element line-product stabilizer is exactly the `AGL(2,3)` stabilizer of that
  affine flag `(missing point, distinguished direction)`.
- full-sign obstruction certificate:
  in the full candidate space `(Hessian216 on u) x (affine z maps) x {global sign}`,
  there is exactly one stabilizer element, and an exact minimum of `7` line/z witness
  constraints already forces that uniqueness.
- dual-space robustness check:
  repeating the same obstruction search in the larger candidate space
  `(AGL(2,3) on u) x (affine z maps) x {global sign}` still gives exact minimum
  witness size `7` (with one stabilizer element).
- residual-group `Z3` core check:
  the computed line-product residual subgroup (`D12`) contains exactly two order-`3`
  elements and a unique order-`3` subgroup (`C3`), now exported and tested.
- qutrit-phase-space orbit fingerprint:
  under the residual `D12` action on `AG(2,3)`, point orbits are `[1,2,6]` and line
  orbits are `[1,2,3,6]`; the missing point is fixed and the distinguished direction
  class splits into line-orbits `[1,2]`.
- qutrit-striation/MUB action check:
  on the 4 affine striations (MUB contexts), residual action has orbit sizes `[1,3]`,
  fixes the distinguished striation, and induces full `S3` on the other three
  (permutation kernel size `2` inside the 12-element residual subgroup).
- affine-flag line-class decomposition:
  line orbits are not only size-patterned (`[1,2,3,6]`) but exactly coincide with the
  four incidence classes relative to the distinguished flag
  `(missing point, distinguished direction)`, with class sizes `1,2,3,6`.
- distinct-line obstruction split:
  if obstruction witnesses are constrained to use distinct affine lines, the exact
  minimum stays `7` in Hessian216 but rises to `8` in full `AGL(2,3)` candidate space.
- striation-complete obstruction split:
  if obstruction witnesses are required to cover all 4 affine striations
  (`x`, `y`, `y=x`, `y=2x`, i.e. qutrit/MUB contexts), the exact minimum stays `7`
  in Hessian216 but rises to `8` in full `AGL(2,3)` candidate space.
- exact minimal-certificate multiplicity split (bounded exact pass):
  using `tools/enumerate_minimal_certificates.py --mode exact` on the canonical
  12-line fixture with cap `max_exact_solutions=200`, Hessian216 reaches the cap
  with `190` distinct canonical representatives, while full `AGL(2,3)` terminates
  with `7` total minimal certificates and `7` representatives.
- involution criterion for reduced Hessian certificate orbits:
  in the exhaustive Hessian census (`256` canonical reps), reduced-orbit reps
  (`orbit_size=1296`) are exactly those fixed by at least one symmetry whose
  affine part has `det=2`, affine order `2`, and whose `z` map is one of
  `(1,0)`, `(2,0)`, `(2,1)`.
- strict reduced-orbit symmetry profile:
  the same exhaustive Hessian census has exact match-count split `0:201`, `1:55`,
  i.e., every full-orbit rep has zero involution matches and every reduced rep
  has exactly one match.
- full affine z-map scan check:
  allowing all six affine `z` maps leaves the split unchanged and still observes
  matches only at `(1,0)`, `(2,0)`, `(2,1)`.
- Formal theorem and short proof sketch: `docs/REDUCED_ORBIT_THEOREM_2026_02_10.md`. Equivalence verified by `tools/check_reduced_orbit_closed_form_equiv.py` and `tests/test_check_reduced_orbit_closed_form_equiv_smoke.py`. Medium-run artifacts (enumeration JSONs, classified reps, closed-form checks, and galleries) are archived in
  `committed_artifacts/min_cert_census_medium_2026_02_10` and included in follow-up PR #52.
- exact checker profile:
  `201` reps have no matching involution witness and stay full orbit (`2592`);
  `55` reps have exactly one witness and are reduced (`1296`).
- end-to-end census automation:
  `tools/run_min_cert_census.py` now executes exact enumeration, canonical
  classification, involution-rule checking, reduced-orbit closed-form
  equivalence checking, and markdown gallery/summary generation in a single
  bounded run.
- bounded cross-space census replay (`2026-02-11`):
  with `--max-exact-solutions 80 --time-limit-sec 45`, Hessian reaches cap at
  `80` solutions / `79` canonical reps with orbit split `1296:11`, `2592:68`,
  while `AGL(2,3)` completes at `7` solutions / `7` reps (all `2592`);
  involution-rule checker and reduced closed-form checker both return `0`
  mismatches in both spaces, and reduced-form strict profile check is true in
  both spaces.
- Vogel universality cross-check (`2026-02-11`):
  `tools/vogel_universal_snapshot.py` verifies exceptional-line Vogel dimensions,
  then scans s12 dimensions (`728`, `486`, `242`) across universal families;
  `728` matches classical `A_26 = sl_27`, while `486` and `242` show no bounded
  classical or exceptional-line rational hits (`denominator <= 24`).
- extended rational-hit catalog (`2026-02-11`):
  `tools/vogel_rational_hit_catalog.py` verifies that in `D in [200,1000]`,
  non-degenerate rational exceptional-line hits occur exactly at
  `{248, 287, 336, 484, 603, 782}`; s12 dimensions (`728`, `486`, `242`)
  remain outside this rational-hit set.
- arithmetic closure theorem for integer-dimensional hits (`2026-02-11`):
  `tools/vogel_rational_dimension_theorem.py` reduces the discriminant to
  `Delta(D)=(D+122)^2-120^2` and the hit condition to
  `(D+122-r)(D+122+r)=14400`, yielding the exact positive hit set
  `{1,3,8,14,28,47,52,78,96,119,133,190,248,287,336,484,603,782,1081,1680,3479}`.
- hit-set family crosswalk (`2026-02-11`):
  `tools/vogel_rational_hit_crosswalk.py` splits the 21 positive hits into
  classical-family hits (`7` dims), direct-table hits (`7` dims), and
  arithmetic-only hits (`10` dims). s12 targets remain outside the hit set;
  nearest-hit distances are `54` for `728`, `2` for `486`, and `6` for `242`.
- integer-parameter divisor locus (`2026-02-11`):
  `tools/vogel_integer_m_locus.py` rewrites exceptional-line dimension as
  `D = 30*(m+4) - 122 + 120/(m+4)`, proving that for integer `m != -4`,
  `D` is integer iff `(m+4)` divides `120`. The positive integer-`m` dimension
  set is exactly `{8,28,52,78,133,190,248,336,484,603,782,1081,1680,3479}`.
- global `z=(2,2)` exclusion at full-sign level (`2026-02-11`):
  `tools/prove_z22_no_global_stabilizer.py` checks closed-form full-sign
  invariance for `z_map=(2,2)` over all affine candidates and finds no
  stabilizer: `0/864` matches in full `AGL(2,3)` (including global sign) and
  `0/216` matches in the `det=2`, order-`2` involution subset.
- global full-sign `z`-map census (`2026-02-11`):
  `tools/classify_global_full_sign_stabilizers.py` scans all six affine
  `z` maps across `{all_agl, hessian216, involution_det2}`.
  Only two nonzero cells remain:
  `(all_agl, z=(1,0), count=1)` and `(hessian216, z=(1,0), count=1)`;
  all other cells are zero.
- minimal contradiction-core census (`2026-02-11`):
  `tools/minimal_global_full_sign_cores.py` computes exact minimal UNSAT cores
  per global cell; nontrivial `z` cells are ruled out by small cores
  (size `3` in `all_agl/hessian216`, size `4` for involution mode at `z=(1,0)`).
- minimal positive-identity certificate census (`2026-02-11`):
  `tools/minimal_global_identity_certificates.py` computes exact minimal
  witness sets that isolate the unique global identity cell `z=(1,0)`:
  size `6` with `688` certificates in full `AGL(2,3)`, and size `5` with
  `33` certificates in `Hessian216`.
- s12 Jacobi-failure pattern check (`2026-02-11`):
  `tools/analyze_s12_jacobi_failure_pattern.py` verifies the six grade-level
  Jacobi failures are exactly the nonzero triples with nonzero mod-3 sum,
  forming two `S3` orbits of size `3`.
- structural bridge refinement (`2026-02-11`):
  `tools/analyze_s12_sl27_z3_bridge.py` upgrades the Vogel hit from total
  dimension-only to full grade-structure matching:
  the s12 split `(242,243,243)` is uniquely realized by a 3-block cyclic
  `Z3` grading of `sl_27` with partition `27=9+9+9`.

Outputs:

- `artifacts/e6_f3_trilinear_symmetry_breaking.json`
- `artifacts/e6_f3_trilinear_symmetry_breaking.md`
- `artifacts/e6_f3_trilinear_min_cert_orbit_involution_rule_check_hessian_exhaustive2.json`
- `artifacts/e6_f3_trilinear_min_cert_orbit_involution_rule_check_agl_exhaustive.json`
- `artifacts/min_cert_census_summary.json`
- `artifacts/min_cert_census_summary.md`
- `artifacts/vogel_universal_snapshot_2026_02_11.json`
- `docs/VOGEL_UNIVERSAL_RESEARCH_2026_02_11.md`
- `artifacts/vogel_rational_dimension_theorem_2026_02_11.json`
- `docs/VOGEL_RATIONAL_DIMENSION_THEOREM_2026_02_11.md`
- `artifacts/vogel_rational_hit_crosswalk_2026_02_11.json`
- `docs/VOGEL_RATIONAL_HIT_CROSSWALK_2026_02_11.md`
- `artifacts/vogel_integer_m_locus_2026_02_11.json`
- `docs/VOGEL_INTEGER_M_LOCUS_2026_02_11.md`
- `artifacts/z22_global_stabilizer_exclusion_2026_02_11.json`
- `docs/Z22_GLOBAL_STABILIZER_EXCLUSION_2026_02_11.md`
- `artifacts/global_full_sign_stabilizer_census_2026_02_11.json`
- `docs/GLOBAL_FULL_SIGN_STABILIZER_CENSUS_2026_02_11.md`
- `artifacts/minimal_global_full_sign_cores_2026_02_11.json`
- `docs/MINIMAL_GLOBAL_FULL_SIGN_CORES_2026_02_11.md`
- `artifacts/minimal_global_identity_certificates_2026_02_11.json`
- `docs/MINIMAL_GLOBAL_IDENTITY_CERTIFICATES_2026_02_11.md`
- `artifacts/s12_jacobi_failure_pattern_2026_02_11.json`
- `docs/S12_JACOBI_FAILURE_PATTERN_2026_02_11.md`
- `artifacts/s12_sl27_z3_bridge_2026_02_11.json`
- `docs/S12_SL27_Z3_BRIDGE_2026_02_11.md`

## Why this is interesting

The support geometry matches the expected Hesse/Heisenberg affine-line structure,
while the sign layer behaves like an additional symmetry-breaking datum. That gives
a concrete computational bridge between:

1. finite geometry (`AG(2,3)` lines, Heisenberg coordinates on H27),
2. E6 cubic support/sign data,
3. reduced residual symmetry after adding sign information,
4. a concrete finite subgroup fingerprint (`D12`) on the line-product layer,
5. a canonical affine-flag geometry extracted directly from signs.

This can be used as a next-stage target for deriving sign laws (or cocycles) rather
than only support laws.

## Web-guided hypothesis loop

Using recent incidence-geometry references as prompts, we tested two specific
computational hypotheses in-repo:

1. the residual `D12` should act as a concrete affine flag stabilizer,
2. full-sign rigidity should admit a finite obstruction certificate.
3. the full-sign obstruction minimum should be stable when moving from Hessian216
   to the larger full `AGL(2,3)` candidate space.
4. the residual group should expose a concrete `Z3` nucleus (unique `C3` subgroup),
   compatible with the project-wide ternary (`F3`) framing.
5. the residual action should realize a nontrivial but rigid orbit signature on
   `AG(2,3)` points/lines consistent with qutrit finite-phase-space structure.
6. the residual action on qutrit striations should single out one context and realize
   full `S3` mixing on the remaining three contexts.
7. line orbits should coincide exactly with affine-flag incidence classes relative to
   `(missing point, distinguished direction)`.
8. line-distinct full-sign obstruction should separate Hessian216 from full `AGL(2,3)`.
9. striation-complete full-sign obstruction should separate Hessian216 from full
   `AGL(2,3)` when every qutrit/MUB context must be represented.
10. exact minimal-certificate multiplicity should differ sharply across candidate
    spaces, not only the minimum certificate size constraints.
11. reduced-orbit Hessian representatives should satisfy a deterministic
    involution-based predicate, not only a post-hoc orbit-size split.
12. if `728` is `A_26`, then the full split `(242,243,243)` should be realizable
    by a canonical `Z3` graded model of `sl_27`, ideally uniquely up to block
    permutation.
13. the six Jacobi-obstructed grade triples should satisfy a compact closed form
    (not only a count), ideally a permutation-stable mod-3 predicate.
14. if only one global full-sign stabilizer survives, there should be small
    exact positive witness sets that isolate it, and their size should separate
    `Hessian216` from full `AGL(2,3)`.

Both now pass directly in `tools/analyze_e6_f3_trilinear_symmetry_breaking.py`
and `tests/test_e6_f3_trilinear_symmetry_breaking.py`.
The involution predicate check is encoded in
`tools/check_min_cert_orbit_involution_rule.py` and
`tests/test_check_min_cert_orbit_involution_rule_smoke.py`.
The Jacobi-failure pattern check is encoded in
`tools/analyze_s12_jacobi_failure_pattern.py` and
`tests/test_analyze_s12_jacobi_failure_pattern_smoke.py`.
The `sl_27` bridge check is encoded in
`tools/analyze_s12_sl27_z3_bridge.py` and
`tests/test_analyze_s12_sl27_z3_bridge_smoke.py`.

## External references used

- Artebani, Dolgachev, *The Hesse pencil of plane cubic curves*, arXiv:math/0611590
  Link: `https://arxiv.org/abs/math/0611590`
- Manivel, *Configurations of lines and models of Lie algebras*, EMS Surveys in Mathematical Sciences, 2007
  Link: `https://ems.press/journals/emss/articles/15549`
- Mainkar et al., *Lines and Opposition in Exceptional Incidence Geometry*, arXiv:2602.01110 (2026)
  Link: `https://arxiv.org/abs/2602.01110`
- Argyres, Chalykh, Lu, *E6 and F4 in Calogero-Moser Elliptic Integrable Systems*, arXiv:2510.16417 (2025)
  Link: `https://arxiv.org/abs/2510.16417`
- Frezzotti et al., *A simple lattice setup for E6 and E8 gauge theories*, arXiv:2509.06785 (2025)
  Link: `https://arxiv.org/abs/2509.06785`
- Wootters, *Quantum measurements and finite geometry*, arXiv:quant-ph/0406032
  Link: `https://arxiv.org/abs/quant-ph/0406032`
- Gibbons, Hoffman, Wootters, *Discrete phase space based on finite fields*, arXiv:quant-ph/0401155
  Link: `https://arxiv.org/abs/quant-ph/0401155`
- Bandyopadhyay et al., *A new proof for the existence of mutually unbiased bases*, arXiv:quant-ph/0103162
  Link: `https://arxiv.org/abs/quant-ph/0103162`
- Zhu, *Quasiprobability representations of quantum mechanics with minimal negativity*, arXiv:1505.01123
  Link: `https://arxiv.org/abs/1505.01123`
- Gonano et al., *Discrete Wigner function for Quantum Information: an illustrative guide*, arXiv:2503.18431 (2025)
  Link: `https://arxiv.org/abs/2503.18431`
- Cretu et al., *Vogel universality and beyond*, arXiv:2601.01612 (2026)
  Link: `https://arxiv.org/abs/2601.01612`
- Cretu et al., *A universal Lie algebra generated by one element and one relation*, arXiv:2506.15280 (2025)
  Link: `https://arxiv.org/abs/2506.15280`
- Cretu et al., *On Refined Vogel's universality and link homologies*, arXiv:2504.13831 (2025)
  Link: `https://arxiv.org/abs/2504.13831`
- Cretu et al., *On Macdonald deformation of Vogel's universality and LMOV-like formula for exceptional hyperpolynomials*, arXiv:2505.16569 (2025)
  Link: `https://arxiv.org/abs/2505.16569`
- Cretu et al., *Vogel's universality and Macdonald dimensions*, arXiv:2507.11414 (2025)
  Link: `https://arxiv.org/abs/2507.11414`
- Cretu et al., *Construction of the Lie algebra weight system kernel via Vogel algebra*, arXiv:2411.14417 (2024)
  Link: `https://arxiv.org/abs/2411.14417`
- Cretu et al., *Vogel universality and differential operators on Jacobi diagrams*, EPJC (2025)
  Link: `https://link.springer.com/article/10.1140/epjc/s10052-025-14406-9`
- Cretu et al., *The Vogel plane, the F4 line, and TQFT at level one*, arXiv:2508.01834 (2025)
  Link: `https://arxiv.org/abs/2508.01834`
- Cretu et al., *Classification Problem on Vogel's Plane*, EPJC (2025)
  Link: `https://link.springer.com/article/10.1140/epjc/s10052-025-14943-y`
- Cretu et al., *On Macdonald deformation of Vogel's universality and LMOV-like formula for exceptional hyperpolynomials*, Phys. Lett. B (2025)
  Link: `https://doi.org/10.1016/j.physletb.2025.139730`
- Zinoviev, *Diophantine equations and platonic solids*, arXiv:1604.06062 (2016)
  Link: `https://arxiv.org/abs/1604.06062`
