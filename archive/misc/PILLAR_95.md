# Pillar 95: Heisenberg presentation of N & direct‑product refactor

This pillar carries forward the four follow‑on tasks requested by the user.
Its main achievements are:

* **Explicit generators for the regular subgroup \(N\)** – by examining the
  delta map constructed in Pillars 89 and 94 we located two elements
  \(a,b\in N\) whose projected Heisenberg coordinates form a basis of
  \(\mathbb F_3^2\).  The commutator
  \(z = a b a^{-1} b^{-1}\) lies in the centre and has pure‑z coordinate; the
  triple \(a,b,z\) satisfies the familiar Heisenberg presentation with
  orders dividing 3.  The data are saved in `N_heis_presentation.json`.

* **Direct‑product utility applied to bundles** – the helper from
  `THEORY_PART_CXCIV_DIRECT_PRODUCT_UTILS` was exercised in a new module that
  recomputes the closure of \(\Gamma\) with the automorphism set \(H\) and
  confirms the size equals the product |\Gamma|·|H|.  This demonstration shows
  how future analyses of the S3‑sheet and axis‑block‑twist bundles can be
  simplified: one need only handle the monodromy part, then append the
  commuting phase later.

The pillar includes two new scripts, `THEORY_PART_CXCV_N_PRESENTATION.py` and
`THEORY_PART_CXCV_REFINE_BUNDLES.py`, along with corresponding tests.

## Consequences

- We now possess a concrete presentation of \(N\) as a central extension of
  \(\mathbb F_3^2\) by \(\mathbb Z_3\), clarifying its role as the
  translation subgroup in the Heisenberg model.
- The direct‑product viewpoint has been codified and tested, so all future
  bundle work may be refactored accordingly with minimal effort.

## Next steps

Pillar 96 will embed these constructions into an explicit algebraic model and
verify the homomorphism property in code.  Beyond that, the path is clear for
integrating the whole structure into Clifford/Heisenberg algebras and for
continuing the theory of everything sequence with further bundle analyses.
