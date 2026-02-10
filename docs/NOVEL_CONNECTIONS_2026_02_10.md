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

Outputs:

- `artifacts/e6_f3_trilinear_symmetry_breaking.json`
- `artifacts/e6_f3_trilinear_symmetry_breaking.md`

## Why this is interesting

The support geometry matches the expected Hesse/Heisenberg affine-line structure,
while the sign layer behaves like an additional symmetry-breaking datum. That gives
a concrete computational bridge between:

1. finite geometry (`AG(2,3)` lines, Heisenberg coordinates on H27),
2. E6 cubic support/sign data,
3. reduced residual symmetry after adding sign information.

This can be used as a next-stage target for deriving sign laws (or cocycles) rather
than only support laws.

## External references used

- Artebani, Dolgachev, *The Hesse pencil of plane cubic curves*, arXiv:math/0611590  
  Link: `https://arxiv.org/abs/math/0611590`
- Manivel, *Configurations of lines and models of Lie algebras*, EMS Surveys in Mathematical Sciences, 2007  
  Link: `https://ems.press/journals/emss/articles/15549`
