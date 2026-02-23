# Curated external websites (short list)

This page collects external web resources I inspected on your request and
explains why they matter for the W33 ↔ E8 work.

- https://fgmarcelis.wordpress.com/ — Frans Marcelis (E8 / Witting / PG(3,2))
  - Witting→PG(3,2) trace‑map examples, Witting polytope visualizations,
    MiniMOG/MOG discussion, and explicit 40↔240 observations used repeatedly
    in our analyses.

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

If you want, I can:
- Add specific page references from these sites to `EXTERNAL_READING_NOTES_JAN28_2026.md`.
- Create visual tests that project our E8 roots onto the same Coxeter/elliptic
  planes used on those pages for direct visual comparison.

Additional sources (Vogel / Jacobi / modular-function identities):
- https://arxiv.org/abs/2601.01612 — Isaev (2026), *Universal Casimir projectors and invariant tensors*
  - Universal / Vogel-parameterized projector formulas may be a clean lens for the
    `s12` → `sl(27)` resonance (dimension 728) and for classifying which
    deformations (cocycles/phases) restore Jacobi.
- https://link.springer.com/article/10.1140/epjc/s10052-025-14260-8 — Morozov & Sleptsov (2025),
  *Classification Problem for Jacobi Identities*
  - Directly relevant to the “finite Jacobi obstruction set” we see in the grade-only
    `s12` universal algebra and motivates the “add the missing 2-cocycle/phase” strategy.
- https://en.wikipedia.org/wiki/Rogers%E2%80%93Ramanujan_continued_fraction — Rogers–Ramanujan continued fraction
  - Source for the explicit identity expressing the elliptic modular invariant `j(τ)`
    as a rational function of `R(q)^5`; used by `scripts/w33_monster_ogg_pipeline.py --verify-rr-j`.
