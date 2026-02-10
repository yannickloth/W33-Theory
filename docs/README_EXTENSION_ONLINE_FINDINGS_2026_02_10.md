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

7. Bandyopadhyay et al., *A new proof for the existence of mutually unbiased bases*  
   URL: `https://arxiv.org/abs/quant-ph/0103162`  
   Raw note: finite-field MUB construction supports treating affine-line classes as
   meaningful qutrit-structure carriers.

8. Gibbons, Hoffman, Wootters, *Discrete phase space based on finite fields*  
   URL: `https://arxiv.org/abs/quant-ph/0401155`  
   Raw note: makes the striation picture explicit (lines grouped into parallel classes),
   suggesting direct tests of induced subgroup action on striation classes.

9. Zhu, *Quasiprobability representations of quantum mechanics with minimal negativity*  
   URL: `https://arxiv.org/abs/1505.01123`  
   Raw note: dimension-3 specialness in quasiprobability framing supports trying
   context-coverage constraints (not only unconstrained witness minima).

10. Gonano et al., *Discrete Wigner function for Quantum Information: an illustrative guide*  
    URL: `https://arxiv.org/abs/2503.18431`  
    Raw note: recent synthesis of Wigner/MUB constructions reinforces treating
    striation-complete witness sets as a first-class robustness diagnostic.

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

H6. Residual action on the 4 striations should fix one and induce full `S3` on the
other three (qutrit-MUB context splitting).  
Status: verified (`striation_orbit_sizes = [1,3]`,
`non_distinguished_permutation_is_s3 = true`,
`non_distinguished_permutation_kernel_size = 2`).

H7. Line orbits should coincide exactly with affine-flag incidence classes relative
to `(missing point, distinguished direction)`.  
Status: verified (class sizes
`1,2,3,6`, with one residual orbit per class).

H8. Under a distinct-line witness constraint (at most one witness per affine line),
minimum full-sign obstruction size should separate Hessian216 and full `AGL(2,3)`.  
Status: verified (`7` for Hessian216, `8` for full `AGL(2,3)`).

H9. Under a striation-complete witness constraint (cover all 4 affine striations /
qutrit-MUB contexts), minimum full-sign obstruction size should separate Hessian216
and full `AGL(2,3)`.  
Status: verified (`7` for Hessian216, `8` for full `AGL(2,3)`).

Additional witness-space note:
- Minimal witness geometry (size `7`) differs between candidate spaces: **Hessian216** = `5` unique lines with one full `z={0,1,2}` line; **AGL(2,3)** = `6` unique lines with one line appearing twice with two `z` values. See `artifacts/e6_f3_trilinear_symmetry_breaking.json` → `cross_checks.full_sign_obstruction_certificate_geotypes` for summaries and the exact witness rows.
- Computed result fits a clean split: one distinguished context is fixed, the other
  three are maximally mixed under full `S3`.
- This gives a stronger interpretation of symmetry breaking:
  not just local orbit asymmetry, but a concrete context hierarchy with one pinned
  basis and a 3-context permutation sector.

## Third-pass raw notes (same date, new loop)

- The `[1,2,3,6]` line-orbit pattern can still hide ambiguity unless it matches a
  canonical geometric partition. The natural candidate is the incidence partition by
  the distinguished affine flag.
- Computation confirms exact alignment: every residual orbit is homogeneous for this
  flag partition and each class is exactly one orbit.
- This sharpens the interpretation from "orbit counts look plausible" to
  "orbit decomposition equals a canonical flag-incidence decomposition."

## Fourth-pass raw notes (same date, new loop)

- Unconstrained witness minima can hide repetition effects (same line at multiple z).
- Adding a distinct-line constraint is a natural robustness stress test for the
  obstruction certificates.
- Result: Hessian216 still admits `7`, but full `AGL(2,3)` needs `8`, so the larger
  candidate space has a measurable extra geometric burden once line repetition is
  disallowed.

## Fifth-pass raw notes (same date, new loop)

- Distinct-line constraints probe geometric dispersion, but not context completeness.
- A direct MUB-context stress test is to force witness coverage across all 4
  affine striations and then recompute exact minima.
- Result: Hessian216 still admits `7`, while full `AGL(2,3)` rises to `8`.
- This confirms a second independent geometric penalty axis for the larger candidate
  space: context completeness, not only line distinctness.

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

