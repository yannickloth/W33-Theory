# Curated external websites (short list)

This page collects external web resources I inspected on your request and
explains why they matter for the W33 ↔ E8 work.

- https://fgmarcelis.wordpress.com/ — Frans Marcelis (E8 / Witting / PG(3,2))
  - Witting→PG(3,2) trace‑map examples, Witting polytope visualizations,
    MiniMOG/MOG discussion, and explicit 40↔240 observations used repeatedly
    in our analyses.
  - Key page for the 45-tritangent split: https://fgmarcelis.wordpress.com/2014/03/07/e8-%C2%A7-11-pg24-in-pg34/
    - Enumerates **9 diameters** partitioning the 27-vertex Hessian/Witting model into 9 triples, with **12** ways to
      pick 3 diameters (3 rows + 3 columns + 6 determinant terms). This matches our intrinsic
      artifacts/e6_cubic_affine_heisenberg_model.json split (36 affine u-lines + 9 constant-u fibers) and explains why
      the firewall forbids exactly the 9 fiber triads.

- https://bendwavy.org/klitzing/explain/gc.htm — B. Klitzing / Bendwavy
  - Comprehensive reference on abstract and Grünbaum‑Coxeter polytopes (elliptic
    polytopes, antipodal identifications, incidence matrices, Petrie polygons).
    Useful for alternative polytopal realizations of the 40‑vertex / W33 type
    configurations.

Why these matter (quick):
- Marcelis supplies concrete coordinate/tracing constructions (Witting → PG(3,2))
  which directly cross‑check our `tools/witting_trace_map_*` scripts.
- Klitzing/Bendwavy documents several families of "hemi/elliptical" polytopes
  and mod‑wrapped constructions that give combinatorial templates (vertex
  counts/incidence matrices) useful when comparing geometric vs. algebraic
  realizations of W33/Witting/E8.

Quick canonical encyclopedia references for the same structure:
- https://en.wikipedia.org/wiki/Hessian_polyhedron — Hessian polyhedron / Hessian configuration
  - 27 vertices; 12 van Oss polygons (_3{4}_2); Hessian configuration (9_4, 12_3). This matches our AG(2,3) u-plane:
    9 u-points, 12 u-lines, 4 lines through each point (verified by scripts/e6_hessian_tritangents.py).
- https://en.wikipedia.org/wiki/Witting_polytope — Witting polytope context / symmetry

If you want, I can:
- Add specific page references from these sites to `EXTERNAL_READING_NOTES_JAN28_2026.md`.
- Create visual tests that project our E8 roots onto the same Coxeter/elliptic
  planes used on those pages for direct visual comparison.

Additional sources (Vogel / Jacobi / modular-function identities):
- https://www.math.rwth-aachen.de/~Thomas.Breuer/ctbllib/ctbltoc/data/7%5E1%2B4.2A7.html — CTblLib: `7^{1+4}.2A7`
  - Listed as the **7B centralizer in the Monster** (order 84,707,280), matching our ATLAS-derived
    cofactor magnitude |C_M(7B)|/7 = 12,101,040 and justifying the recognition label `7^4:2A7`
    in `scripts/w33_monster_centralizer_cofactor_groups.py`.
- https://www.math.rwth-aachen.de/~Thomas.Breuer/ctbllib/ctbltoc/data/13%5E1%2B2.2A4.html — CTblLib: `13^{1+2}.2A4`
  - This entry documents the **13B centralizer** (order 52,728 = 13^{1+2}·|2A4|), confirming the
    cofactor |C_M(13B)|/13 = 4,056 and leading to recognition string `13^2:2A4` in the same script.
- https://www.math.rwth-aachen.de/~Thomas.Breuer/ctbllib/ctbltoc/data/5%5E1%2B6.2J2.html — CTblLib: `5^{1+6}.2J2`
  - The **5B centralizer** has order 94,500,000,000 = 5^{1+6}·|2J2|, giving cofactor 18,900,000,000
    and justifying the `5^6:2J2` cofactor label used in the pipeline.
- https://www.math.rwth-aachen.de/~Thomas.Breuer/ctbllib/ctbltoc/data/3%5E1%2B12.2Suz.html — CTblLib: `3^{1+12}.2Suz`
  - Documents the **3B centralizer shape** `3^{1+12}.2Suz`, used in
    `scripts/w33_monster_3b_s12_sl27_bridge.py` to connect Monster’s non-Fricke 3B
    class to the `s12` / Heisenberg / `sl(27)` closure (3^6−1 = 728).
- https://atlas.math.rwth-aachen.de/Atlas/v3/spor/M/ — ATLAS (RWTH): Monster group page
  - Lists prime-order class centralizers (including `3B`) and maximal subgroups
    (including the normalizer `3^{1+12}.2Suz.2`), providing an independent
    cross-check for the numeric identity |C_M(3B)| = 3^{1+12}·|2Suz|.
- https://arxiv.org/abs/2601.01612 — Isaev (2026), *Vogel universality and beyond*
  - Universal / Vogel-parameterized projector formulas may be a clean lens for the
    `s12` → `sl(27)` resonance (dimension 728) and for classifying which
    deformations (cocycles/phases) restore Jacobi.
- https://link.springer.com/article/10.1140/epjc/s10052-025-14943-y — Morozov & Sleptsov (2025),
  *Vogel’s universality and the classification problem for Jacobi identities*
  - Directly relevant to the “finite Jacobi obstruction set” we see in the grade-only
    `s12` universal algebra and motivates the “add the missing 2-cocycle/phase” strategy.
- https://arxiv.org/abs/2504.13831 — Bishler & Mironov (2025), *On refined Vogel’s universality*
  - Refined Chern–Simons / Macdonald dimensions suggest an extension of universality
    to refined settings; relevant to our TQFT and modularity pillars.
- https://en.wikipedia.org/wiki/Rogers%E2%80%93Ramanujan_continued_fraction — Rogers–Ramanujan continued fraction
  - Source for the explicit identity expressing the elliptic modular invariant `j(τ)`
    as a rational function of `R(q)^5`; used by `scripts/w33_monster_ogg_pipeline.py --verify-rr-j`.
