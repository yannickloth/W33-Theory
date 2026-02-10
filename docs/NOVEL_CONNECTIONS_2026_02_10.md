# Novel Connections (2026-02-10)

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

Outputs:

- `artifacts/e6_f3_trilinear_symmetry_breaking.json`
- `artifacts/e6_f3_trilinear_symmetry_breaking.md`

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

Both now pass directly in `tools/analyze_e6_f3_trilinear_symmetry_breaking.py`
and `tests/test_e6_f3_trilinear_symmetry_breaking.py`.

## External references used

- Artebani, Dolgachev, *The Hesse pencil of plane cubic curves*, arXiv:math/0611590  
  Link: `https://arxiv.org/abs/math/0611590`
- Manivel, *Configurations of lines and models of Lie algebras*, EMS Surveys in Mathematical Sciences, 2007  
  Link: `https://ems.press/journals/emss/articles/15549`
- Mainkar et al., *Lines and Opposition in Exceptional Incidence Geometry*, arXiv:2602.01110 (2026)  
  Link: `https://arxiv.org/abs/2602.01110`
- Alisauskas et al., *Spherical reduction and generalized Dirac-Dunkl operators in dimensions >2*, arXiv:2512.02559 (2025)  
  Link: `https://arxiv.org/abs/2512.02559`
