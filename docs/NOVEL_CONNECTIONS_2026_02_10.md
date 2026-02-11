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
- exact checker profile:
  `201` reps have no matching involution witness and stay full orbit (`2592`);
  `55` reps have exactly one witness and are reduced (`1296`).
- end-to-end census automation:
  `tools/run_min_cert_census.py` now executes exact enumeration, canonical
  classification, involution-rule checking, and markdown gallery/summary generation
  in a single bounded run.
- bounded cross-space census replay (`2026-02-11`):
  with `--max-exact-solutions 80 --time-limit-sec 45`, Hessian reaches cap at
  `80` solutions / `79` canonical reps with orbit split `1296:11`, `2592:68`,
  while `AGL(2,3)` completes at `7` solutions / `7` reps (all `2592`);
  involution-rule checker returns `0` mismatches in both spaces.

Outputs:

- `artifacts/e6_f3_trilinear_symmetry_breaking.json`
- `artifacts/e6_f3_trilinear_symmetry_breaking.md`
- `artifacts/e6_f3_trilinear_min_cert_orbit_involution_rule_check_hessian_exhaustive2.json`
- `artifacts/e6_f3_trilinear_min_cert_orbit_involution_rule_check_agl_exhaustive.json`
- `artifacts/min_cert_census_summary.json`
- `artifacts/min_cert_census_summary.md`

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

Both now pass directly in `tools/analyze_e6_f3_trilinear_symmetry_breaking.py`
and `tests/test_e6_f3_trilinear_symmetry_breaking.py`.
The involution predicate check is encoded in
`tools/check_min_cert_orbit_involution_rule.py` and
`tests/test_check_min_cert_orbit_involution_rule_smoke.py`.

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
