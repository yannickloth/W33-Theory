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
Cross-check: the trilinear analysis' distinguished direction and unique missing AG(2,3) point were confirmed to match the Heisenberg H27 fiber mapping (per `scripts/w33_heisenberg_qutrit.py`) in `tests/test_cross_script_striation_consistency.py`.

Additional witness-space note:
- Minimal witness geometry (size `7`) differs between candidate spaces: **Hessian216** = `5` unique lines with one full `z={0,1,2}` line; **AGL(2,3)** = `6` unique lines with one line appearing twice with two `z` values. See `artifacts/e6_f3_trilinear_symmetry_breaking.json` → `cross_checks.full_sign_obstruction_certificate_geotypes` and `cross_checks.full_sign_obstruction_certificate_orbits` for orbit sizes and canonical representatives.
- Randomized enumeration (greedy sampler) results: the sampler was extended with parallel sampling, early-stopping, and checkpointing support (`--workers`, `--batch-size`, `--patience`, `--checkpoint-interval`, `--stop-if-found`). Running a medium sweep (20k samples, `--workers 4 --batch-size 1000 --checkpoint-interval 2000`) produced: Hessian216: **134** distinct canonical representatives (`artifacts/e6_f3_trilinear_min_cert_enumeration_hessian_20k.json`); AGL(2,3): **7** distinct canonical representatives (`artifacts/e6_f3_trilinear_min_cert_enumeration_agl_20k.json`). A subsequent exhaustive enumeration of all size-7 witness combinations for the Hessian candidate space produced **256** distinct canonical representatives and **273** covering combinations (`artifacts/e6_f3_trilinear_min_cert_enumeration_hessian_exhaustive2.json`), confirming the sampling-based findings and revealing a larger hidden diversity. These results indicate a much larger variety of minimal witness orbit types in the Hessian candidate space compared to AGL space.
- Exhaustive engine note: the shared exhaustive path now uses deterministic branch-and-bound (instead of raw combination scanning), with optional `--max-exhaustive-solutions` and `--time-limit-sec` caps in `tools/enumerate_minimal_certificates.py`, and the standalone wrapper `tools/enumerate_minimal_certificates_exhaustive.py` calls that shared core.
- Computed result fits a clean split: one distinguished context is fixed, the other
  three are maximally mixed under full `S3`.
- This gives a stronger interpretation of symmetry breaking:
  not just local orbit asymmetry, but a concrete context hierarchy with one pinned
  basis and a 3-context permutation sector.

## Where each hypothesis is encoded

- Analysis script: `tools/analyze_e6_f3_trilinear_symmetry_breaking.py`
- Tests: `tests/test_e6_f3_trilinear_symmetry_breaking.py`
- Distilled narrative: `README.md` and `docs/NOVEL_CONNECTIONS_2026_02_10.md`

## Reproduction commands

```bash
python tools/build_e6_f3_trilinear_map.py
python tools/analyze_e6_f3_trilinear_symmetry_breaking.py
python tools/enumerate_minimal_certificates.py --in-json artifacts/e6_f3_trilinear_map.json --candidate-space hessian --max-samples 20000 --seed 42 --workers 4 --batch-size 1000 --checkpoint-interval 2000 --out-json artifacts/e6_f3_trilinear_min_cert_enumeration_hessian_20k.json --progress
python tools/enumerate_minimal_certificates_exhaustive.py --in-json artifacts/e6_f3_trilinear_map.json --candidate-space hessian --progress --out-json artifacts/e6_f3_trilinear_min_cert_enumeration_hessian_exhaustive2.json
python -m pytest tests/test_e6_f3_trilinear.py tests/test_e6_f3_trilinear_symmetry_breaking.py tests/test_witness_certificate_classification.py tests/test_enumerate_minimal_certificates_smoke.py tests/test_enumerate_minimal_certificates_parallel_smoke.py tests/test_enumerate_minimal_certificates_exhaustive_smoke.py -q
```
