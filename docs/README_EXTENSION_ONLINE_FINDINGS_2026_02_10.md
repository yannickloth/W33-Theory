# README Extension: Online Findings and Hypothesis Chain (2026-02-10)

This file is the raw web-research appendix for the living paper in `README.md`.
It keeps source-driven notes, hypothesis formation, and verification links separate
from the layperson narrative.

## Scope and method

- Date of web pass: `2026-02-10`.
- Search goal: identify recent and foundational primary sources that can sharpen
  testable claims around the `E6/F3` trilinear sign layer and `AG(2,3)` structure.
- Rule: convert source ideas into explicit computational checks; avoid narrative-only
  additions.

## Source log (primary sources)

1. Artebani-Dolgachev, *The Hesse pencil of plane cubic curves*  
   URL: `https://arxiv.org/abs/math/0611590`  
   Raw note: finite-plane cubic/Hesse structure remains the core geometric template
   for the affine-line decomposition used in current scripts.

2. Hunt, *The 27 lines on the cubic surface and finite geometry*  
   URL: `https://arxiv.org/abs/math/0507118`  
   Raw note: classic 27-line finite-geometry viewpoint supports using explicit
   incidence/stabilizer computations rather than only representation-theoretic prose.

3. Mainkar et al., *Lines and Opposition in Exceptional Incidence Geometry*  
   URL: `https://arxiv.org/abs/2602.01110`  
   Raw note: recent exceptional-incidence framing motivated adding stronger subgroup
   and orbit diagnostics beyond just cardinalities.

4. Argyres-Chalykh-Lu, *E6 and F4 in Calogero-Moser Elliptic Integrable Systems*  
   URL: `https://arxiv.org/abs/2510.16417`  
   Raw note: modern `E6` context justified keeping the sign-layer analysis anchored
   to explicit finite invariants and exact witness certificates.

5. Frezzotti et al., *A simple lattice setup for E6 and E8 gauge theories*  
   URL: `https://arxiv.org/abs/2509.06785`  
   Raw note: reinforced emphasis on constructive, machine-checkable gauge data and
   reproducible computations.

6. Wootters, *Quantum measurements and finite geometry*  
   URL: `https://arxiv.org/abs/quant-ph/0406032`  
   Raw note: finite-phase-space and striation viewpoint motivated residual-orbit
   fingerprint checks on `AG(2,3)` points and lines.

7. Bandyopadhyay et al., *A New Proof for the Existence of Mutually Unbiased Bases*  
   URL: `https://arxiv.org/abs/0909.1671`  
   Raw note: finite-field MUB construction supports treating affine-line classes as
   meaningful qutrit-structure carriers.

## Hypothesis chain -> repo checks

H1. Residual subgroup should be an explicit affine-flag stabilizer.  
Status: verified in `tools/analyze_e6_f3_trilinear_symmetry_breaking.py`.

H2. Full-sign rigidity should admit a finite obstruction witness.  
Status: verified with exact minimum witness size `7` in Hessian216 candidate space.

H3. The minimum obstruction size should persist in full `AGL(2,3)` candidate space.  
Status: verified with exact minimum witness size `7` in both spaces.

H4. Residual `D12` should expose a ternary nucleus (unique order-`3` subgroup).  
Status: verified (`order3_element_count = 2`, unique `C3` subgroup present).

H5. Residual action should carry a rigid phase-space orbit signature on `AG(2,3)`.  
Status: verified (`point_orbit_sizes = [1,2,6]`, `line_orbit_sizes = [1,2,3,6]`,
missing point fixed, distinguished direction split `[1,2]`).

## Where each hypothesis is encoded

- Analysis script: `tools/analyze_e6_f3_trilinear_symmetry_breaking.py`
- Tests: `tests/test_e6_f3_trilinear_symmetry_breaking.py`
- Distilled narrative: `README.md` and `docs/NOVEL_CONNECTIONS_2026_02_10.md`

## Reproduction commands

```bash
python tools/build_e6_f3_trilinear_map.py
python tools/analyze_e6_f3_trilinear_symmetry_breaking.py
python -m pytest tests/test_e6_f3_trilinear.py tests/test_e6_f3_trilinear_symmetry_breaking.py -q
```

