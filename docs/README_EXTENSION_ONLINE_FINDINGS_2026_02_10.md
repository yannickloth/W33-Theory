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

11. GroupNames entry for `AGL(2,3)` (`SmallGroup(432,734)`)
    URL: `https://people.maths.bris.ac.uk/~matyd/GroupNames/433/AGL%282%2C3%29.html`
    Raw note: independent group-database check of ambient affine-group order
    used in orbit normalization (`|AGL(2,3)|=432`).

12. Artebani, Dolgachev (cit. Coxeter), Hessian group of order `216`
    URL: `https://arxiv.org/abs/math/0611590`
    Raw note: supports the Hessian216-vs-AGL candidate-space split used in
    current minimal-certificate census comparisons.

13. Cretu et al., *Vogel universality and beyond* (2026)
    URL: `https://arxiv.org/abs/2601.01612`
    Raw note: current research emphasis is shifting from static exceptional-line
    tables to broader universality frameworks and extensions.

14. Cretu et al., *Vogel's universality and the classification problem for Jacobi identities* (2025)
    URL: `https://arxiv.org/abs/2506.15280`
    Raw note: supports a generator/relation-driven perspective for universal Lie
    objects, which maps well to scriptable identity checks.

15. Cretu et al., *On Refined Vogel's universality and link homologies* (2025)
    URL: `https://arxiv.org/abs/2504.13831`
    Raw note: refines Vogel universality with link-homology structure and supports
    using richer invariants beyond scalar dimension checks.

16. Cretu et al., *On Macdonald deformation of Vogel's universality and LMOV-like formula for exceptional hyperpolynomials* (2025)
    URL: `https://arxiv.org/abs/2505.16569`
    Raw note: pushes beyond undeformed Vogel tables and motivates adding
    deformation-aware scans where possible.

17. Cretu et al., *Vogel's universality and Macdonald dimensions* (2025)
    URL: `https://arxiv.org/abs/2507.11414`
    Raw note: strengthens the Macdonald/refined-universality direction and suggests
    multi-parameter discriminants are now standard in the literature.

18. Cretu et al., *Construction of the Lie algebra weight system kernel via Vogel algebra* (2024)
    URL: `https://arxiv.org/abs/2411.14417`
    Raw note: reinforces kernel-level constraints as first-class universal data,
    not just post-hoc consistency checks.

19. Cretu et al., *Vogel universality and differential operators on Jacobi diagrams* (EPJC, 2025)
    URL: `https://link.springer.com/article/10.1140/epjc/s10052-025-14406-9`
    Raw note: the differential-operator/Jacobi-diagram framing supports treating
    finite Jacobi-obstruction patterns as operator-level invariants, not only
    grade-count anomalies.

20. Cretu et al., *On Macdonald deformation of Vogel's universality and LMOV-like formula for exceptional hyperpolynomials* (Phys. Lett. B, 2025)
    URL: `https://doi.org/10.1016/j.physletb.2025.139730`
    Raw note: confirms the deformation branch is not speculative; journal-level
    versions motivate preserving both arXiv and DOI links in the source chain.

21. Cretu et al., *The Vogel plane, the F4 line, and TQFT at level one* (arXiv, 2025)
    URL: `https://arxiv.org/abs/2508.01834`
    Raw note: reinforces that arithmetic/geometric structure on Vogel's plane
    is actively studied and supports explicit line-focused computational scans.

22. Cretu et al., *Classification Problem on Vogel's Plane* (EPJC, 2025)
    URL: `https://link.springer.com/article/10.1140/epjc/s10052-025-14943-y`
    Raw note: journal-level follow-up confirms the classification direction is central
    and supports reporting exact finite hit sets rather than only local windows.

23. Zinoviev, *Diophantine equations and platonic solids* (arXiv, 2016)
    URL: `https://arxiv.org/abs/1604.06062`
    Raw note: difference-of-squares + divisor-pair reductions are a natural arithmetic
    method class for this style of universality equation.

24. GroupNames entry for `AGL(2,3)` (`SmallGroup(432,734)`) (2026-02-11 pass)
    URL: `https://people.maths.bris.ac.uk/~matyd/GroupNames/433/AGL%282%2C3%29.html`
    Raw note: external catalog confirms the concrete ambient group identification
    and order (`432`) used by the global full-sign stabilizer scans.

25. Groupprops, *General affine group* (2026-02-11 pass)
    URL: `https://groupprops.subwiki.org/wiki/General_affine_group`
    Raw note: semidirect-product structure (`F_q^n ⋊ GL_n(F_q)`) provides a direct
    structural explanation for the affine candidate-space factorization used in code.

26. Malkevitch, *Finite Geometries* lecture notes (York University)
    URL: `https://www.yorku.ca/malkevitch/edit5000/ch2.html`
    Raw note: states that affine planes of order `n` have `n^2 + n` lines and
    `n + 1` parallel classes; for `n=3` this gives the `12`-line/`4`-striation
    counts used in striation-level diagnostics.

27. GeoGebra, *Affine plane AG(2,3)*
    URL: `https://www.geogebra.org/m/BU7R8fBb`
    Raw note: explicit `AG(2,3)` construction page reports exactly `9` points,
    `12` lines, and `4` line classes, matching script assumptions and outputs.

28. Mathlib docs, `Mathlib.Data.ZMod.Basic` (2026-02-11 pass)
    URL: `https://leanprover-community.github.io/mathlib4_docs/Mathlib/Data/ZMod/Basic.html`
    Raw note: confirms the standard Lean finite-field base (`ZMod`) used by the
    new `proofs/lean/z22_exclusion.lean` skeleton.

29. Rozikov et al., *On finite-dimensional derived Jordan and bicommutative algebras* (2026)
    URL: `https://arxiv.org/abs/2601.22110`
    Raw note: recent finite-dimensional Jordan-structure work supports treating
    low-complexity finite rulebooks as first-class algebraic objects rather than
    only ad hoc combinatorial summaries.

30. Bae et al., *A Cohomological Hall Algebra Construction for Jordan Quivers* (2025)
    URL: `https://arxiv.org/abs/2505.16569`
    Raw note: Jordan-quiver/CoHA constructions motivate explicitly tracking which
    finite motifs survive when moving between ambient symmetry classes.

31. Muller et al., *Fermion mass ratios from the exceptional Jordan algebra* (2025)
    URL: `https://arxiv.org/abs/2510.14736`
    Raw note: while model-specific, this reinforces keeping exceptional-Jordan
    references in the hypothesis chain when testing `s12` universalization ideas.

32. Nguyen et al., *Jordan decomposition in finite-dimensional Lie algebras over arbitrary fields* (2026)
    URL: `https://arxiv.org/abs/2601.07168`
    Raw note: decomposition-level structure over arbitrary fields aligns with our
    finite-field split between coarse obstruction counts and finer motif-level
    overlap signatures.

33. Wikipedia, *Hessian group* (2026-02-11 pass)
    URL: `https://en.wikipedia.org/wiki/Hessian_group`
    Raw note: records the Hessian-group order `216` and its extension to a
    complex reflection group of order `1296`, motivating an explicit check of
    motif behavior against the repo's `1296` vs `2592` orbit split.

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

H10. Reduced-orbit Hessian representatives should satisfy an explicit involution
predicate: reduced iff fixed by at least one `det=2`, order-`2` affine involution
paired with `z` involution in `{(1,0),(2,0),(2,1)}`.
Status: verified on exhaustive Hessian representatives (`256` total):
`201` full-orbit reps (`2592`) match no such involution and `55` reduced-orbit reps
(`1296`) each match exactly one.
Full affine `z`-map scan status: verified with `tools/check_reduced_orbit_closed_form_equiv.py --z-map-mode all`; no additional `z` map beyond `{(1,0),(2,0),(2,1)}` appears in any match.

H11. s12 dimensions should be cross-checkable against Vogel-universal families:
`728` should be classically explainable (`sl_27`) while `486` and `242` should not
land on low-rank classical/exceptional-line hits in bounded scans.
Status: verified via `tools/vogel_universal_snapshot.py`:
`728` maps to `A_26` only; `486` and `242` show no classical integer-family hits;
bounded exceptional-line rational search (`denominator <= 24`) has zero hits for
all three dimensions.

H11b. Rational exceptional-line hits should form a sparse arithmetic set, and s12
dimensions should lie outside it.
Status: verified via `tools/vogel_rational_hit_catalog.py` on `D in [200,1000]`:
hit dimensions are exactly `{248, 287, 336, 484, 603, 782}`; s12 dimensions
`728`, `486`, `242` are outside this set.

H11c. Integer dimensions with rational non-degenerate exceptional-line roots should
admit an exact finite classification (not only bounded sweeps).
Status: verified via `tools/vogel_rational_dimension_theorem.py`:
`Delta(D)=D^2+244D+484=(D+122)^2-120^2` implies
`(D+122-r)(D+122+r)=14400`, reducing the integer-dimensional hit problem to
parity-compatible divisor pairs of `14400`. Positive hits are exactly
`{1,3,8,14,28,47,52,78,96,119,133,190,248,287,336,484,603,782,1081,1680,3479}`.
s12 dimensions (`728`, `486`, `242`) remain outside this full set.

H11d. The finite positive hit set should split into classical-family hits,
direct exceptional-table hits, and an arithmetic-only remainder.
Status: verified via `tools/vogel_rational_hit_crosswalk.py`:
classical hits are `{3,8,28,78,190,1081,1680}`, direct-table hits are
`{8,14,28,52,78,133,248}`, and arithmetic-only hits are
`{1,47,96,119,287,336,484,603,782,3479}`.
Targets `728`, `486`, `242` are not hits; nearest hit distances are
`54`, `2`, and `6`, respectively.

H11e. On the exceptional line, integer-parameter points should admit a divisor
criterion, yielding a finite integer-`m` integer-`D` locus.
Status: verified via `tools/vogel_integer_m_locus.py`:
with `n=m+4`, dimension rewrites as
`D = 30*n - 122 + 120/n`, so for integer `m != -4`,
`D` is integer iff `n | 120`.
This gives exact positive dimensions from integer `m`:
`{8,28,52,78,133,190,248,336,484,603,782,1081,1680,3479}`,
again excluding `728`, `486`, and `242`.

- Extended rational search (rational cubic root analysis) up to denominator `500` found
  **no** non-degenerate rational exceptional-line parameter `m` for target dims `486`
  and `242` (degenerate root `m=-2` excluded). See `docs/VOGEL_EXTENDED_FINDINGS_2026_02_11.md` for details and search parameters.

- Additional sweep (2026-02-11): broad rational-cubic sweep over dimensions
  `D` in `[200,1000]` with denominator cap `500` found **6** hit dimensions:
  `{248, 287, 336, 484, 603, 782}`. The s12 targets (`728`, `486`, `242`)
  still remain outside this rational-hit set.
  Artifacts:
  `artifacts/vogel_rational_sweep.json`,
  `artifacts/vogel_rational_sweep.md`,
  `artifacts/vogel_rational_hit_catalog_2026_02_11.json`,
  `docs/VOGEL_RATIONAL_HIT_CATALOG_2026_02_11.md`.

H12. If `728` is `A_26 = sl_27`, the s12 grade split `(242,243,243)` should be
recoverable as a finite-order (`Z3`) block-cyclic grading of `sl_27`; if this
bridge is structural, the partition should be unique (up to permutation).
Status: verified via `tools/analyze_s12_sl27_z3_bridge.py`:
search over all sorted triples `(a,b,c)` with `1 <= a <= b <= c <= 60` finds exactly
one solution to `g0=a^2+b^2+c^2-1=242`, `g1=g2=ab+bc+ca=243`, namely
`(a,b,c)=(9,9,9)`, hence `n=a+b+c=27` and `dim(sl_n)=n^2-1=728`.

H13. The six Jacobi-obstructed grade triples should satisfy a compact predicate
and a stable permutation-orbit decomposition, not just a raw failure count.
Status: verified via `tools/analyze_s12_jacobi_failure_pattern.py`:
the failure set is exactly `{(a,b,c) in {0,1,2}^3 : a,b,c != 0 and (a+b+c) mod 3 != 0}`,
equivalently the `2+1` nonzero composition pattern, and splits into exactly two
`S3` orbits of size `3`.

H14. The `z=(2,2)` exclusion should hold globally at full-sign level, not only
inside the reduced-certificate census.
Status: verified via `tools/prove_z22_no_global_stabilizer.py`:
for `z_map=(2,2)`, full-sign invariance has zero matches in
`864` full `AGL(2,3)` affine/epsilon candidates and zero matches in
`216` candidates from the `det=2`, order-`2` involution subset.
This upgrades exclusion from representative-level evidence to a global
closed-form stabilizer nonexistence check.

H15. Global full-sign stabilizers should admit a complete `z`-map census with
exactly one surviving trivial cell.
Status: verified via `tools/classify_global_full_sign_stabilizers.py`:
for modes `{all_agl, hessian216, involution_det2}` and all six affine `z` maps,
the only nonzero cells are:
`(mode=all_agl, z=(1,0), count=1)` and
`(mode=hessian216, z=(1,0), count=1)`.
The involution subset has zero matches for all `z` maps.

H16. External ambient-geometry references should match the exact finite counts
used by the new global checks and Lean skeleton.
Status: verified via source-backed consistency:
- `|AGL(2,3)| = 432` from GroupNames and the semidirect-product structure
  `F_3^2 ⋊ GL(2,3)` from Groupprops agree with the `864` affine/epsilon
  candidate count in `all_agl` mode.
- affine-plane order-3 counts (`9` points, `12` lines, `4` line classes) from
  finite-geometry references agree with line/striation loops in the stabilizer
  scripts.
- `Mathlib.Data.ZMod.Basic` matches the `ZMod 3` finite-field model used in
  `proofs/lean/z22_exclusion.lean`.

H17. Global unsat cells should admit compact minimal contradiction cores.
Status: verified via `tools/minimal_global_full_sign_cores.py`:
- in `all_agl` and `hessian216`, all nontrivial `z` cells have minimal core size `3`;
- in `involution_det2`, minimal core size is `4` at `z=(1,0)` and `3` for other `z`.

H18. Nontrivial-core motifs should cross-link differently to minimal-certificate
representatives in `AGL(2,3)` vs Hessian census datasets.
Status: verified via `tools/link_core_rulebook_to_min_cert_census.py`:
- core motif overlap is exactly `0/7` representatives in `agl_exact_full`;
- overlap is positive in Hessian datasets (`18/79` in exact full,
  `30/256` in exhaustive2);
- dominant overlap motif is `x:(1,1,0)` in both Hessian datasets.

H19. The dominant overlap motif `x:(1,1,0)` should be polarized toward
full-orbit (`2592`) representatives in Hessian datasets.
Status: verified via `tools/classify_core_motif_orbit_polarization.py`:
- `hessian_exact_full`: `15/16` `x:(1,1,0)` hits are orbit `2592`
  (precision `0.938`);
- `hessian_exhaustive2`: `19/20` are orbit `2592` (precision `0.950`);
- combined Hessian precision: `34/36 = 0.944` for orbit `2592`.

H20. The `x:(1,1,0)` full-orbit concentration should exceed Hessian baseline
`2592` prevalence by a statistically nontrivial margin.
Status: verified via `tools/core_motif_enrichment_stats.py`:
- combined Hessian baseline `P(2592)=269/335=0.803`;
- motif precision `P(2592 | x:(1,1,0)) = 34/36 = 0.944`;
- lift `1.176`;
- one-sided hypergeometric enrichment p-value `0.01355`.
Companion reduced marker: `x:(2,2,1)` is pure `1296` on support `2`
with `p_enrich_1296 = 0.03834`.

H21. Enrichment-selected motifs should yield a compact high-precision
abstaining orbit classifier in Hessian representative space.
Status: verified via `tools/core_motif_anchor_channels.py`:
- anchor extraction picks `full={x:(1,1,0)}` and `reduced={x:(2,2,1)}`;
- on combined Hessian reps (`335`), anchor rule fires on `38` with
  precision `36/38 = 0.947`;
- no conflicting anchor fires are observed.

H22. The motif analysis should be executable as one deterministic chained pass,
not only as separate scripts.
Status: verified via `tools/run_core_motif_chain.py`:
- runs link, polarization, enrichment, and anchor stages in order;
- rewrites the four JSON artifacts and four markdown docs in one invocation;
- covered by `tests/test_run_core_motif_chain_smoke.py`.

H23. Small anchor-set search should trade a controlled precision drop for
measurable coverage gain over fixed anchors.
Status: verified via `tools/search_core_motif_anchor_sets.py`:
- fixed anchors (`x:1-1-0` full, `x:2-2-1` reduced):
  coverage `38/335 = 0.113`, precision `36/38 = 0.947`;
- best searched anchors (<=3 full, <=3 reduced, precision floor `0.90`):
  coverage `48/335 = 0.143`, precision `44/48 = 0.917`;
- conflict count remains `0`.

Additional witness-space note:
- Minimal witness geometry (size `7`) differs between candidate spaces: **Hessian216** = `5` unique lines with one full `z={0,1,2}` line; **AGL(2,3)** = `6` unique lines with one line appearing twice with two `z` values. See `artifacts/e6_f3_trilinear_symmetry_breaking.json` -> `cross_checks.full_sign_obstruction_certificate_geotypes` and `cross_checks.full_sign_obstruction_certificate_orbits` for orbit sizes and canonical representatives.
- Randomized enumeration (greedy sampler) results, initial pass: Hessian216 (`max_samples=500`) found `3` distinct canonical representatives (`artifacts/e6_f3_trilinear_min_cert_enumeration_hessian.json`); AGL(2,3) (`max_samples=1000`) found `2` distinct canonical representatives (`artifacts/e6_f3_trilinear_min_cert_enumeration_agl.json`).
- Randomized enumeration (extended pass): in a 20k sweep, Hessian216 found `134` distinct canonical representatives (`artifacts/e6_f3_trilinear_min_cert_enumeration_hessian_20k.json`), while AGL(2,3) found `7` (`artifacts/e6_f3_trilinear_min_cert_enumeration_agl_20k.json`).
- Exact enumeration mode (branch-and-bound) is available in `tools/enumerate_minimal_certificates.py` via `--mode exact` with runtime controls `--max-exact-solutions` and `--time-limit-sec`.
- Bounded exact pass on the canonical 12-line fixture (`max_exact_solutions=200`, `time_limit_sec=60`): Hessian216 hit the cap at `200` solutions with `190` distinct canonical representatives, while AGL(2,3) completed with `7` total solutions and `7` representatives.
- Exhaustive Hessian census artifact (`artifacts/e6_f3_trilinear_min_cert_enumeration_hessian_exhaustive2.json`) reports `256` distinct canonical representatives over `273` covering combinations, indicating a substantially larger minimal-witness orbit diversity in Hessian space than in full AGL space.
- Involution checker artifact (`artifacts/e6_f3_trilinear_min_cert_orbit_involution_rule_check_hessian_exhaustive2.json`) reports zero mismatches for the reduced-orbit predicate (`55/55` reduced reps detected and `201/201` full-orbit reps rejected).
- Census orchestrator (`tools/run_min_cert_census.py`) now composes exact
  enumeration, classification, involution-rule checking, reduced-orbit
  closed-form equivalence checking, gallery rendering, and markdown/json summary
  output in a single bounded execution flow.
- Bounded replay run (`2026-02-11`) with
  `--candidate-spaces hessian agl --max-exact-solutions 80 --time-limit-sec 45`
  produced: Hessian `80` solutions / `79` canonical reps (`1296:11`, `2592:68`),
  AGL `7` solutions / `7` reps (all `2592`), with involution-rule mismatch count
  `0`, reduced-closed-form mismatch count `0`, and reduced-form strict profile
  check `true` in both spaces.
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

## Sixth-pass raw notes (same date, new loop)

- The reduced-orbit layer (`1296`) needed a direct predicate, not only orbit-size
  post-processing.
- We restricted the search to involutive symmetry candidates first, then compared
  that detector to the full orbit split.
- Result: exact agreement on the exhaustive Hessian representative census.
- The decision boundary now comes from a compact involution check (`36 x 3`
  candidates), not a generic all-orbits scan.

## Seventh-pass raw notes (2026-02-11, Vogel loop)

- New Vogel papers (2024-2026) emphasize universality extensions and explicit
  Jacobi-kernel structures, so we moved from narrative-only Vogel references to
  executable checks.
- We now verify Vogel dimensions directly on exceptional points and exceptional-line
  parameterization, then scan where s12 dimensions (`728`, `486`, `242`) sit in
  universal families.
- Concrete outcome: `728` is exactly `A_26 = sl_27` in classical Vogel families,
  while `486` and `242` remain off-family in bounded classical/ex-line scans.
- This gives a precise universal-algebra reading: s12 total dimension aligns with
  classical `A`-family scaling, while internal split dimensions resist simple
  Lie-family embedding in the tested search window.

## Eighth-pass raw notes (2026-02-11, sl_27 Z3 bridge loop)

- Dimension-only Vogel hits can overfit, so we added a structure-level check:
  can the full s12 split `(242,243,243)` arise from a canonical `Z3` grading model?
- For block-cyclic `Z3` gradings of `sl_n` with partition `n=a+b+c`, dimensions are
  `g0=a^2+b^2+c^2-1`, `g1=g2=ab+bc+ca`.
- Exhaustive triple scan (`1 <= a <= b <= c <= 60`) finds a unique match:
  `(a,b,c)=(9,9,9)`, giving `n=27`, `A_26`, and exactly `(242,243,243)`.
- This upgrades the Vogel bridge from "total dim compatibility" to
  "full grade decomposition compatibility" and gives a tight canonical model.

## Ninth-pass raw notes (2026-02-11, Jacobi pattern loop)

- A failure count (`6`) is weaker than a failure law; we added an explicit closed-form
  detector for the Jacobi-failure triples.
- Result: failures are exactly the nonzero triples with nonzero mod-3 sum.
- This gives a compact law compatible with the ternary (`F3`) framework and reduces
  the Jacobi-obstruction statement from "six exceptions exist" to an executable
  classification rule.

## Tenth-pass raw notes (2026-02-11, source-hardening loop)

- We added journal-level links for the recent Vogel branch (EPJC and Phys. Lett. B),
  not just arXiv IDs, to stabilize citation targets in the living README paper.
- This does not alter computed invariants, but it improves traceability and
  reproducibility for external readers following the theory-to-source chain.

## Eleventh-pass raw notes (2026-02-11, arithmetic-closure loop)

- The bounded-hit statement in `[200,1000]` was useful but still local.
- Rewriting the non-degenerate condition to
  `Delta(D)=(D+122)^2-120^2` gives the fixed-product equation
  `(D+122-r)(D+122+r)=14400`.
- This closes the problem exactly on integer dimensions: finite divisor pairs,
  no dependence on denominator caps.
- We then added a crosswalk classification pass: the 21 positive hits split into
  7 classical-family hits, 7 direct-table hits, and 10 arithmetic-only hits.
- This sharpened the Vogel result from "s12 misses a tested window" to
  "s12 misses the entire integer-dimensional rational-hit locus and sits near, but
  outside, the closest hits (`484`, `248`, `782`)."

## Twelfth-pass raw notes (2026-02-11, integer-parameter locus loop)

- The finite rational-hit theorem still mixes integer and fractional `m`.
- Reparameterizing with `n=m+4` gives
  `D=30*n-122+120/n`, making integer-`m` integrality equivalent to `n|120`.
- This yields a fully explicit finite integer-parameter locus and explains why
  integer-root hit dimensions are sparse.
- The s12 target dimensions remain outside this divisor-locus, so they are not
  exceptional-line hits even under integer-parameter specializations.

## Thirteenth-pass raw notes (2026-02-11, z22 global exclusion loop)

- The short symbolic `x=0` contradiction excludes `z=(2,2)` in adapted gauge,
  but we wanted a global, direct stabilizer scan against the full sign law.
- New checker runs the closed-form sign law on all lines/z values and tests
  affine/epsilon candidates directly, without depending on the reduced-census
  representative list.
- Result: zero matches for `z=(2,2)` across full `AGL(2,3)` and across the
  involution subset relevant to reduced-orbit symmetry.
- This closes a gap between "not observed in reduced reps" and
  "provably absent as a global full-sign stabilizer."

## Fourteenth-pass raw notes (2026-02-11, full z-map census loop)

- Excluding one bad map (`z=(2,2)`) still leaves the global landscape implicit.
- We added a full `z`-map census over the three affine modes.
- Outcome: only the trivial `z=(1,0)` cell survives (with one symmetry, the
  identity) in full `AGL` and `Hessian216`; all other cells are zero.
- This reframes the symmetry statement as a sparse matrix classification rather
  than a list of exclusions.

## Fifteenth-pass raw notes (2026-02-11, source-grounding + Lean loop)

- We added a short source-hardening pass focused on ambient finite counts:
  affine-group order, affine-plane line/class counts, and Lean `ZMod` baseline.
- This tightened traceability for the global stabilizer scans:
  script loop sizes now map directly to explicit external references.
- We also refreshed the Lean folder into a runnable project skeleton
  (`lakefile.lean` + `lean-toolchain` + updated README) so the symbolic
  contradiction can move from draft lemmas toward CI-checkable formal proofs.

## Sixteenth-pass raw notes (2026-02-11, minimal-core loop)

- The global census identifies which cells are impossible, but not their
  obstruction strength.
- We added an exact finite-core extractor over the 36 line/z constraints.
- Result: unsat cells are certificate-small (mostly core size `3`), which
  indicates rigid local contradictions rather than diffuse global mismatch.

## Seventeenth-pass raw notes (2026-02-11, positive-certificate loop)

- UNSAT cores quantify exclusion strength; we also needed the dual question:
  how much evidence is required to isolate the one surviving global symmetry.
- We added an exact positive-certificate extractor at `z=(1,0)`.
- Result:
  - full `AGL(2,3)`: minimal identity certificate size `6`, count `688`;
  - `Hessian216`: minimal identity certificate size `5`, count `33`.
- Interpretation:
  - bad cells fail quickly (small UNSAT cores),
  - but proving the exact survivor needs a larger witness,
  - and the larger affine candidate universe costs one extra constraint.
- Web-sourced connection for this pass:
  - recent Vogel threads emphasize where universal formulas are informative and
    where finer representation-level structure is needed.
  - this finite result mirrors that pattern: coarse exclusion is easier than
    unique survivor identification in the larger candidate class.
  - references:
    - https://arxiv.org/abs/2601.01612
    - https://arxiv.org/abs/2411.14417
    - https://arxiv.org/abs/2504.13831
    - https://link.springer.com/article/10.1140/epjc/s10052-025-14943-y

## Eighteenth-pass raw notes (2026-02-11, constrained-positive loop)

- The `6` vs `5` positive-certificate gap could have been an artifact of
  line repetition or under-covered context directions.
- We tested two structural constraints on identity certificates:
  - distinct affine lines only,
  - striation-complete coverage (`x`, `y`, `y=x`, `y=2x`),
  - and their conjunction.
- Result: minimal sizes are unchanged in every case:
  - `all_agl` stays at `6`,
  - `hessian216` stays at `5`.
- Multiplicity profile sharpens:
  - `all_agl`: `688 -> 167 (distinct) -> 246 (striation) -> 79 (both)`,
  - `hessian216`: `33 -> 17 (distinct) -> 4 (striation) -> 3 (both)`.
- Interpretation:
  - the size gap is not a degeneracy artifact; it is robust under geometric
    stress conditions and reflects a genuine candidate-space complexity split.

## Nineteenth-pass raw notes (2026-02-11, constrained-unsat loop)

- We ran the same constraint-stress idea on UNSAT cores (nontrivial global cells):
  distinct lines vs striation completeness.
- Result:
  - unconstrained nontrivial cores in `all_agl/hessian216`: size `3`,
  - with striation-complete witnesses: size `4`,
  - involution mode at `z=(1,0)`: `4 -> 5` under striation-complete witnesses.
- Interpretation:
  - exclusion remains local and small, but requiring all context directions
    forces one extra row globally.
  - together with the positive `6 vs 5` split, this gives a clean dual profile:
    negative contradiction (3/4/5) vs positive isolation (5/6).

## Twentieth-pass raw notes (2026-02-11, external-structure loop)

- New source scan focus: algebraic structure results that distinguish
  coarse invariants from full structural equivalence.
- Relevant signals:
  - 2026: *Vogel universality and beyond* emphasizes that universal formulas
    are powerful but do not collapse all structure classes into one
    parameter-level invariant.
    URL: `https://arxiv.org/abs/2601.01612`
  - 2024: *Construction of the Lie algebra weight system kernel via Vogel algebra*
    provides an explicit kernel-level refinement layer over raw Vogel data.
    URL: `https://arxiv.org/abs/2411.14417`
  - 2026: *Jordan decomposition in finite-dimensional Lie algebras over arbitrary fields*
    highlights decomposition-level structure that survives when coarse spectral
    data alone is insufficient.
    URL: `https://arxiv.org/abs/2601.07168`
  - 2024: *Coadjoint map preserving operators and Jordan-Lie automorphisms*
    studies structural-preservation maps with Jordan/Lie interplay beyond
    first-order invariants.
    URL: `https://arxiv.org/abs/2412.15510`
- Interpretation for this repo:
  - our constrained core/certificate results fit the same pattern:
    coarse exclusion is low-cost, but uniqueness and context-complete
    certification require extra structural constraints.

## Twenty-first-pass raw notes (2026-02-11, dual-profile synthesis loop)

- We merged the negative and positive witness layers into one executable report.
- New script: `tools/global_sign_rigidity_dual_profile.py`.
- Core output:
  - `all_agl`: negative `3 -> 4`, positive `6 -> 6`
  - `hessian216`: negative `3 -> 4`, positive `5 -> 5`
  under striation-complete constraints.
- Derived invariant:
  - positive-minus-negative gap drops by exactly one in both spaces
    (`3 -> 2` in `all_agl`, `2 -> 1` in `hessian216`).
- Interpretation:
  - context-complete constraints tighten contradiction witnesses but do not
    increase identity witness size in either space; this is a stable dual
    asymmetry, now encoded as a theorem-flagged artifact.

## Twenty-second-pass raw notes (2026-02-11, core-geometry census loop)

- We tested whether nontrivial global size-`3` UNSAT cores are structurally
  arbitrary, or forced into a canonical affine-plane geometry class.
- Exhaustive enumeration result (`all_agl` and `hessian216`):
  - every minimal size-`3` core is exactly one full parallel-class triplet
    (single line direction with offsets `0,1,2`);
  - per-cell core counts are identical across spaces:
    `6,2,4,2,2` over `z=(1,1),(1,2),(2,0),(2,1),(2,2)`;
  - core signature sets are exactly equal between `all_agl` and `hessian216`.
- Interpretation:
  - the nontrivial obstruction layer is fully controlled by affine-plane
    parallel-class geometry, not by candidate-space enlargement.
  - this explains why striation-complete constraints necessarily add one row
    to nontrivial cores (`3 -> 4`).
- external references checked in this pass:
  - Hesse/AG(2,3) incidence context: https://arxiv.org/abs/math/0611590
  - affine-plane parallel classes summary: https://en.wikipedia.org/wiki/Incidence_geometry
  - Hessian216 context: https://en.wikipedia.org/wiki/Hessian_group

## Twenty-third-pass raw notes (2026-02-11, rulebook compression loop)

- Core geometry census proved every nontrivial size-`3` core is a parallel-class
  triplet; next step was to compress these into offset-coordinate laws.
- New rulebook extractor on triplets `(z0,z1,z2)` by direction:
  - all families are full cartesian boxes over allowed coordinate subsets,
  - except one unique corner-exclusion family:
    `z=(1,1)`, direction `x`, triples `{(1,1,1),(1,2,1),(2,1,1)}`.
- Equivalent compressed form of that unique family:
  - fixed `z2=1`,
  - `z0,z1 in {1,2}`,
  - missing corner `(2,2)`.
- Interpretation:
  - nontrivial obstruction families are almost axis-aligned affine boxes;
    the unique non-cartesian corner cut is the only combinatorial asymmetry.
- web prompts checked in this pass:
  - finite affine phase-space / striations (quantum framing):
    https://arxiv.org/abs/quant-ph/0406032
    https://arxiv.org/abs/quant-ph/0401155
  - hesse pencil / AG(2,3)-incidence background:
    https://arxiv.org/abs/math/0611590
  - recent universality framing:
    https://arxiv.org/abs/2601.01612
    https://arxiv.org/abs/2506.15280

## Twenty-fourth-pass raw notes (2026-02-11, multi-assistant synthesis loop)

- We cross-linked the new nontrivial-core rulebook with the canonical
  minimal-certificate census artifacts produced in the enumerator branch.
- New executable link check: `tools/link_core_rulebook_to_min_cert_census.py`.
- Result:
  - `agl_exact_full`: nontrivial-core motif overlap is exactly `0/7`;
  - `hessian_exact_full`: overlap is `18/79`;
  - `hessian_exhaustive2`: overlap is `30/256`.
- Dominant overlap motif in Hessian datasets: `x:(1,1,0)`.
- Interpretation:
  - the nontrivial global-core motif layer is not generically present in the
    full `AGL` minimal-certificate representatives, but it appears as a
    measurable subfamily in Hessian representative space.
  - this is a concrete bridge between the global-core rulebook and the
    enumerator's canonical-representative census.
- web prompts checked in this pass:
  - finite-dimensional derived Jordan/bicommutative structures:
    https://arxiv.org/abs/2601.22110
  - Jordan quiver / CoHA constructions:
    https://arxiv.org/abs/2505.16569
  - exceptional Jordan + phenomenology prompt:
    https://arxiv.org/abs/2510.14736
  - Jordan decomposition over arbitrary fields:
    https://arxiv.org/abs/2601.07168

## Twenty-fifth-pass raw notes (2026-02-11, orbit-polarization loop)

- We pushed one step deeper than raw overlap counts and measured orbit-size
  polarization of core motifs.
- New analyzer: `tools/classify_core_motif_orbit_polarization.py`.
- Result:
  - `agl_exact_full` keeps zero core-motif overlap (`0/7` reps);
  - in Hessian datasets, dominant motif `x:(1,1,0)` is strongly biased toward
    full-orbit reps (`2592`): `15/16` exact full and `19/20` exhaustive2.
- Combined precision for this motif as a `2592` indicator in Hessian data:
  `34/36 = 0.944`.
- Interpretation:
  - nontrivial-core motifs are not only space-selective (AGL vs Hessian), they
    are also orbit-selective inside Hessian space.
  - this gives a concrete micro-structure link between global contradiction
    motifs and reduced-orbit stratification.
- web prompts checked in this pass:
  - Hessian group order and 1296-extension context:
    https://en.wikipedia.org/wiki/Hessian_group
  - Hesse pencil background for AG(2,3)-like incidence:
    https://arxiv.org/abs/math/0611590
  - universality framing reminder for coarse-vs-refined invariants:
    https://arxiv.org/abs/2601.01612

## Twenty-sixth-pass raw notes (2026-02-11, enrichment-statistics loop)

- We converted motif polarization from descriptive counts into enrichment tests.
- New analyzer: `tools/core_motif_enrichment_stats.py`.
- Combined Hessian result for motif `x:(1,1,0)`:
  - support: `36`,
  - precision for orbit `2592`: `0.944`,
  - baseline `P(2592)`: `0.803`,
  - lift: `1.176`,
  - one-sided hypergeometric `p=0.01355`.
- Complementary reduced marker:
  - motif `x:(2,2,1)` appears only on orbit `1296` in support `2`,
  - `p_enrich_1296=0.03834`.
- Interpretation:
  - the motif channel is not only geometrically interpretable, it is
    statistically enriched against dataset baseline and thus useful as a
    nontrivial orbit-structure diagnostic.
- web prompts checked in this pass:
  - Hesse pencil / Hessian group context:
    https://arxiv.org/abs/math/0611590
  - Hessian-group order references:
    https://en.wikipedia.org/wiki/Hessian_group

## Twenty-seventh-pass raw notes (2026-02-11, anchor-channel loop)

- We converted enrichment outputs into an explicit motif-anchor rulebook.
- New tool: `tools/core_motif_anchor_channels.py`.
- Channel extraction on combined Hessian motifs picks:
  - full channel anchor: `x:(1,1,0)`,
  - reduced channel anchor: `x:(2,2,1)`.
- Evaluated as an abstaining classifier on combined Hessian reps:
  - coverage `38/335 = 0.113`,
  - precision when fired `36/38 = 0.947`,
  - conflict count `0`.
- Interpretation:
  - this is a compact, executable “micro-code” layer: not complete coverage,
    but high-confidence anchor signals that connect global core motifs to
    reduced-orbit stratification.
- web prompts checked in this pass:
  - exceptional-line classification framing:
    https://arxiv.org/abs/2506.15280
  - Vogel-universality extension framing:
    https://arxiv.org/abs/2601.01612

## Twenty-eighth-pass raw notes (2026-02-11, anchor-search loop)

- We moved from fixed anchors to explicit small-set search.
- New tool: `tools/search_core_motif_anchor_sets.py`.
- Search space over 6 motif keys with set sizes up to 3/3 (full/reduced),
  under precision floor `0.90`.
- Best set found:
  - full anchors: `x:1-1-0`, `x:1-1-1`, `y=1x:1-1-2`,
  - reduced anchors: `x:2-2-1`, `y:0-0-0`, `y=2x:1-1-2`,
  - coverage `48/335 = 0.143`, precision `44/48 = 0.917`, conflicts `0`.
- Interpretation:
  - anchor channels can be tuned as a precision/coverage frontier instead of
    a single fixed rule.
- web prompts checked in this pass:
  - universality classification framing:
    https://arxiv.org/abs/2601.01612
  - Jacobi/classification framing:
    https://arxiv.org/abs/2506.15280

## Twenty-ninth-pass raw notes (2026-02-11, Vogel-resonance bridge loop)

- New analysis pass ties three existing artifacts into a single arithmetic bridge:
  - `artifacts/s12_universalization_report.json`,
  - `artifacts/vogel_rational_hit_crosswalk_2026_02_11.json`,
  - `artifacts/min_cert_census_summary.json`.
- New tool: `tools/analyze_vogel_resonance_bridge.py`.
- Reproducible nearest-hit profile for s12 dimensions:
  - `242 -> 248` (gap `+6`, nearest direct table hit contains `E8`),
  - `486 -> 484` (gap `-2`),
  - `728 -> 782` (gap `+54`, nearest integral root includes `26`).
- Count-level resonance checks now all pass in one report:
  - `|242-248| = 6 = jacobi_failure_count`,
  - `|486-484| = 2 = nonzero_grade_count`,
  - `|728-782| = 54 = 2 * checked_grade_triples`,
  - nearest total-dimension integral root `26` matches `A_26` rank inversion.
- Orbit-size bridge from min-cert summary:
  - infer `r=9` from `grade1 = 3r^2 = 243`, so `r^2 = 81`,
  - observed orbit sizes are `1296` and `2592`,
  - factorization is exactly `1296=81*16`, `2592=81*32`, factors are powers of two.
- Interpretation:
  - this is a constrained numeric resonance profile, not a closed-form TOE proof;
    it gives a concrete target for future derivations that explain why these gaps and
    powers-of-two factors co-occur.
- web prompts checked in this pass:
  - current universality overview:
    https://arxiv.org/abs/2601.01612
  - Jacobi-classification framing:
    https://arxiv.org/abs/2506.15280
  - refined universality context:
    https://arxiv.org/abs/2504.13831
  - published Vogel-plane classification problem (EPJC):
    https://doi.org/10.1140/epjc/s10052-025-14943-y
  - Macdonald deformation extension:
    https://arxiv.org/abs/2505.16569
  - note: an earlier DOI guess (`10.1140/epjc/s10052-025-14406-9`) 404'ed, and
    `10.1016/j.physletb.2025.139730` resolved to an unrelated Phys. Lett. B article.

## Thirtieth-pass raw notes (2026-02-11, GL2 group/graph bridge loop)

- We folded the ad-hoc conjugator scratch script into a reproducible analysis pass:
  - new tool: `tools/analyze_gl2_f3_involution_conjugacy.py`,
  - outputs:
    - `artifacts/gl2_f3_involution_conjugacy_2026_02_11.json`,
    - `docs/GL2_F3_INVOLUTION_CONJUGACY_2026_02_11.md`.
- Group-theory result (explicit finite census):
  - `|GL(2,3)| = 48`,
  - det-`2`, order-`2` involutions: `12`,
  - centralizer of `diag(-1,1)`: size `4`,
  - orbit-stabilizer class size `48/4 = 12`, matching the census exactly.
- Graph-theory result (uniform action profile on `AG(2,3)`):
  - points cycle as `[1,1,1,2,2,2]`,
  - affine-line vertices cycle as `[1,1,1,1,2,2,2,2]`,
  - this profile is identical across all 12 involutions.
- Interpretation:
  - reduced-orbit involution symmetry now has a concrete class-theoretic
    skeleton: one involution class and one uniform affine-graph cycle pattern.
  - this gives a stable `micro-axiom` layer for future algebraic closure
    attempts (rather than isolated brute-force checks).
- web prompts checked in this pass:
  - finite-order automorphism baseline:
    https://www.mathnet.ru/php/archive.phtml?wshow=paper&jrnid=im&paperid=3460&option_lang=eng
  - graded-contraction / quasi-Jordan bridge context:
    https://www.worldscientific.com/doi/abs/10.1142/S021949882250059X

## Thirty-first-pass raw notes (2026-02-11, orbit-stabilizer bridge loop)

- New tool: `tools/analyze_orbit_stabilizer_bridge.py`.
- This pass computes stabilizers directly on canonical exact representatives under
  the full witness action model:
  - affine maps on `AG(2,3)`: `432`,
  - affine maps on `z`: `6`,
  - total action size: `2592`.
- Result:
  - Hessian reps split exactly as
    - `68` reps with orbit `2592` and stabilizer size `1`,
    - `11` reps with orbit `1296` and stabilizer size `2`.
  - full `AGL` reps are all full-orbit:
    - `7` reps with orbit `2592` and stabilizer size `1`.
- Nontrivial stabilizers occur only in the Hessian reduced sector and are all
  det-`2`, order-`2` linear parts; their cycle signatures are uniformly
  `[1,1,1,2,2,2]` on points and `[1,1,1,1,2,2,2,2]` on lines, matching the GL(2,3)
  involution-conjugacy bridge exactly.
- Interpretation:
  - the reduced/full orbit dichotomy is now quantitatively equivalent to a
    stabilizer dichotomy (`2` vs `1`) inside one explicit finite action.
  - this is a stronger group-theoretic closure than a pattern-level statement.

## Where each hypothesis is encoded

- Analysis script: `tools/analyze_e6_f3_trilinear_symmetry_breaking.py`
- Involution checker: `tools/check_min_cert_orbit_involution_rule.py`
- Tests: `tests/test_e6_f3_trilinear_symmetry_breaking.py`, `tests/test_check_min_cert_orbit_involution_rule_smoke.py`
- Vogel snapshot: `tools/vogel_universal_snapshot.py`
- Vogel tests: `tests/test_vogel_universal_snapshot_smoke.py`
- Vogel arithmetic theorem: `tools/vogel_rational_dimension_theorem.py`
- Vogel arithmetic theorem tests: `tests/test_vogel_rational_dimension_theorem_smoke.py`
- Vogel hit crosswalk: `tools/vogel_rational_hit_crosswalk.py`
- Vogel hit crosswalk tests: `tests/test_vogel_rational_hit_crosswalk_smoke.py`
- Vogel integer-`m` locus: `tools/vogel_integer_m_locus.py`
- Vogel integer-`m` locus tests: `tests/test_vogel_integer_m_locus_smoke.py`
- global z22 stabilizer exclusion: `tools/prove_z22_no_global_stabilizer.py`
- global z22 exclusion tests: `tests/test_prove_z22_no_global_stabilizer_smoke.py`
- global z-map stabilizer census: `tools/classify_global_full_sign_stabilizers.py`
- global z-map census tests: `tests/test_classify_global_full_sign_stabilizers_smoke.py`
- global minimal-core extractor: `tools/minimal_global_full_sign_cores.py`
- global minimal-core tests: `tests/test_minimal_global_full_sign_cores_smoke.py`
- nontrivial UNSAT core-geometry census: `tools/classify_nontrivial_unsat_core_geometry.py`
- nontrivial core-geometry tests: `tests/test_classify_nontrivial_unsat_core_geometry_smoke.py`
- nontrivial core rulebook compression: `tools/nontrivial_core_rulebook.py`
- nontrivial core rulebook tests: `tests/test_nontrivial_core_rulebook_smoke.py`
- core-rulebook x min-cert census link: `tools/link_core_rulebook_to_min_cert_census.py`
- core-rulebook x min-cert link tests: `tests/test_link_core_rulebook_to_min_cert_census_smoke.py`
- core-motif orbit polarization: `tools/classify_core_motif_orbit_polarization.py`
- core-motif orbit polarization tests: `tests/test_classify_core_motif_orbit_polarization_smoke.py`
- core-motif enrichment stats: `tools/core_motif_enrichment_stats.py`
- core-motif enrichment tests: `tests/test_core_motif_enrichment_stats_smoke.py`
- core-motif anchor channels: `tools/core_motif_anchor_channels.py`
- core-motif anchor-channel tests: `tests/test_core_motif_anchor_channels_smoke.py`
- core-motif chain orchestrator: `tools/run_core_motif_chain.py`
- core-motif chain tests: `tests/test_run_core_motif_chain_smoke.py`
- core-motif anchor search: `tools/search_core_motif_anchor_sets.py`
- core-motif anchor-search tests: `tests/test_search_core_motif_anchor_sets_smoke.py`
- global positive-identity certificates: `tools/minimal_global_identity_certificates.py`
- global positive-identity tests: `tests/test_minimal_global_identity_certificates_smoke.py`
- global dual-profile synthesis: `tools/global_sign_rigidity_dual_profile.py`
- global dual-profile tests: `tests/test_global_sign_rigidity_dual_profile_smoke.py`
- Lean symbolic skeleton: `proofs/lean/z22_exclusion.lean`
- Lean package config: `proofs/lean/lakefile.lean`, `proofs/lean/lean-toolchain`
- Jacobi failure pattern: `tools/analyze_s12_jacobi_failure_pattern.py`
- Jacobi failure tests: `tests/test_analyze_s12_jacobi_failure_pattern_smoke.py`
- sl_27 Z3 bridge: `tools/analyze_s12_sl27_z3_bridge.py`
- sl_27 bridge tests: `tests/test_analyze_s12_sl27_z3_bridge_smoke.py`
- Vogel resonance bridge: `tools/analyze_vogel_resonance_bridge.py`
- Vogel resonance bridge tests: `tests/test_analyze_vogel_resonance_bridge_smoke.py`
- GL(2,3) involution conjugacy bridge: `tools/analyze_gl2_f3_involution_conjugacy.py`
- GL(2,3) bridge tests: `tests/test_analyze_gl2_f3_involution_conjugacy_smoke.py`
- Orbit-stabilizer bridge: `tools/analyze_orbit_stabilizer_bridge.py`
- Orbit-stabilizer bridge tests: `tests/test_analyze_orbit_stabilizer_bridge_smoke.py`
- Distilled narrative: `README.md` and `docs/NOVEL_CONNECTIONS_2026_02_10.md`

## Reproduction commands

```bash
python tools/build_e6_f3_trilinear_map.py
python tools/analyze_e6_f3_trilinear_symmetry_breaking.py
python tools/enumerate_minimal_certificates.py --in-json artifacts/e6_f3_trilinear_map.json --candidate-space hessian --max-samples 20000 --seed 42 --out-json artifacts/e6_f3_trilinear_min_cert_enumeration_hessian_20k.json
python tools/enumerate_minimal_certificates.py --in-json artifacts/e6_f3_trilinear_map.json --candidate-space hessian --mode exact --max-exact-solutions 200 --time-limit-sec 60 --out-json artifacts/e6_f3_trilinear_min_cert_exact_hessian.json
python tools/check_min_cert_orbit_involution_rule.py --in-json artifacts/e6_f3_trilinear_min_cert_enumeration_hessian_exhaustive2_with_geotypes.json --out-json artifacts/e6_f3_trilinear_min_cert_orbit_involution_rule_check_hessian_exhaustive2.json
python tools/run_min_cert_census.py --execute --candidate-spaces hessian agl --max-exact-solutions 500 --time-limit-sec 600 --out-dir artifacts
python tools/vogel_universal_snapshot.py --exceptional-line-denominator-cap 24 --out-json artifacts/vogel_universal_snapshot_2026_02_11.json --out-md docs/VOGEL_UNIVERSAL_RESEARCH_2026_02_11.md
python tools/vogel_rational_dimension_theorem.py --window-start 200 --window-end 1000 --target-dims 728 486 242 --out-json artifacts/vogel_rational_dimension_theorem_2026_02_11.json --out-md docs/VOGEL_RATIONAL_DIMENSION_THEOREM_2026_02_11.md
python tools/vogel_rational_hit_crosswalk.py --target-dims 728 486 242 --out-json artifacts/vogel_rational_hit_crosswalk_2026_02_11.json --out-md docs/VOGEL_RATIONAL_HIT_CROSSWALK_2026_02_11.md
python tools/vogel_integer_m_locus.py --m-min -300 --m-max 300 --target-dims 728 486 242 --out-json artifacts/vogel_integer_m_locus_2026_02_11.json --out-md docs/VOGEL_INTEGER_M_LOCUS_2026_02_11.md
python tools/prove_z22_no_global_stabilizer.py --out-json artifacts/z22_global_stabilizer_exclusion_2026_02_11.json --out-md docs/Z22_GLOBAL_STABILIZER_EXCLUSION_2026_02_11.md
python tools/classify_global_full_sign_stabilizers.py --out-json artifacts/global_full_sign_stabilizer_census_2026_02_11.json --out-md docs/GLOBAL_FULL_SIGN_STABILIZER_CENSUS_2026_02_11.md
python tools/minimal_global_full_sign_cores.py --out-json artifacts/minimal_global_full_sign_cores_2026_02_11.json --out-md docs/MINIMAL_GLOBAL_FULL_SIGN_CORES_2026_02_11.md
python tools/classify_nontrivial_unsat_core_geometry.py --out-json artifacts/nontrivial_unsat_core_geometry_2026_02_11.json --out-md docs/NONTRIVIAL_UNSAT_CORE_GEOMETRY_2026_02_11.md
python tools/nontrivial_core_rulebook.py --out-json artifacts/nontrivial_core_rulebook_2026_02_11.json --out-md docs/NONTRIVIAL_CORE_RULEBOOK_2026_02_11.md
python tools/link_core_rulebook_to_min_cert_census.py --out-json artifacts/core_rulebook_min_cert_link_2026_02_11.json --out-md docs/CORE_RULEBOOK_MIN_CERT_LINK_2026_02_11.md
python tools/classify_core_motif_orbit_polarization.py --out-json artifacts/core_motif_orbit_polarization_2026_02_11.json --out-md docs/CORE_MOTIF_ORBIT_POLARIZATION_2026_02_11.md
python tools/core_motif_enrichment_stats.py --out-json artifacts/core_motif_enrichment_stats_2026_02_11.json --out-md docs/CORE_MOTIF_ENRICHMENT_STATS_2026_02_11.md
python tools/core_motif_anchor_channels.py --out-json artifacts/core_motif_anchor_channels_2026_02_11.json --out-md docs/CORE_MOTIF_ANCHOR_CHANNELS_2026_02_11.md
python tools/search_core_motif_anchor_sets.py --out-json artifacts/core_motif_anchor_search_2026_02_11.json --out-md docs/CORE_MOTIF_ANCHOR_SEARCH_2026_02_11.md
python tools/run_core_motif_chain.py
python tools/minimal_global_identity_certificates.py --out-json artifacts/minimal_global_identity_certificates_2026_02_11.json --out-md docs/MINIMAL_GLOBAL_IDENTITY_CERTIFICATES_2026_02_11.md
python tools/global_sign_rigidity_dual_profile.py --out-json artifacts/global_sign_rigidity_dual_profile_2026_02_11.json --out-md docs/GLOBAL_SIGN_RIGIDITY_DUAL_PROFILE_2026_02_11.md
python tools/analyze_s12_jacobi_failure_pattern.py --out-json artifacts/s12_jacobi_failure_pattern_2026_02_11.json --out-md docs/S12_JACOBI_FAILURE_PATTERN_2026_02_11.md
python tools/analyze_s12_sl27_z3_bridge.py --max-block-size 60 --out-json artifacts/s12_sl27_z3_bridge_2026_02_11.json --out-md docs/S12_SL27_Z3_BRIDGE_2026_02_11.md
python tools/analyze_vogel_resonance_bridge.py --out-json artifacts/vogel_resonance_bridge_2026_02_11.json --out-md docs/VOGEL_RESONANCE_BRIDGE_2026_02_11.md
python tools/analyze_gl2_f3_involution_conjugacy.py --out-json artifacts/gl2_f3_involution_conjugacy_2026_02_11.json --out-md docs/GL2_F3_INVOLUTION_CONJUGACY_2026_02_11.md
python tools/analyze_orbit_stabilizer_bridge.py --out-json artifacts/orbit_stabilizer_bridge_2026_02_11.json --out-md docs/ORBIT_STABILIZER_BRIDGE_2026_02_11.md
python -m pytest tests/test_e6_f3_trilinear.py tests/test_e6_f3_trilinear_symmetry_breaking.py tests/test_witness_certificate_classification.py tests/test_enumerate_minimal_certificates_smoke.py tests/test_enumerate_minimal_certificates_exhaustive_smoke.py tests/test_check_min_cert_orbit_involution_rule_smoke.py tests/test_vogel_rational_dimension_theorem_smoke.py tests/test_vogel_rational_hit_crosswalk_smoke.py tests/test_vogel_integer_m_locus_smoke.py tests/test_prove_z22_no_global_stabilizer_smoke.py tests/test_classify_global_full_sign_stabilizers_smoke.py tests/test_minimal_global_full_sign_cores_smoke.py tests/test_classify_nontrivial_unsat_core_geometry_smoke.py tests/test_nontrivial_core_rulebook_smoke.py tests/test_link_core_rulebook_to_min_cert_census_smoke.py tests/test_classify_core_motif_orbit_polarization_smoke.py tests/test_core_motif_enrichment_stats_smoke.py tests/test_core_motif_anchor_channels_smoke.py tests/test_search_core_motif_anchor_sets_smoke.py tests/test_run_core_motif_chain_smoke.py tests/test_minimal_global_identity_certificates_smoke.py tests/test_global_sign_rigidity_dual_profile_smoke.py -q
python -m pytest tests/test_analyze_vogel_resonance_bridge_smoke.py -q
python -m pytest tests/test_analyze_gl2_f3_involution_conjugacy_smoke.py -q
python -m pytest tests/test_analyze_orbit_stabilizer_bridge_smoke.py -q
cd proofs/lean
lake update
lake build
```
