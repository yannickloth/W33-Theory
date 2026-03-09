# Algebra Review And Vogel Route

This note records the executable algebra review that currently matters for the
W33 finite-geometry program. It is not a promoted public doc layer.

## Repo spine

1. Local qutrit shell:
   - `scripts/w33_heisenberg_qutrit.py` proves that for every base vertex,
     `H27` is an `F_3^3` shell with `9` fibers of size `3`, while `N12`
     splits into `4` MUB classes.
   - The archived check payload confirms:
     `H27` induced degree `8`, Schläfli parameters `(27,16,10,8)`,
     `n_mub_bases = 4`, `n_missing_tritangent = 9`,
     and generation split `(9,9,9)`.

2. Global 2-qutrit shell:
   - `tests/test_e8_embedding.py` and `scripts/w33_two_qutrit_pauli.py`
     identify `W(3,3)` with the commutation graph of the `40`
     projective non-identity two-qutrit Pauli operators.
   - Exact global data:
     `40` points, degree `12`, `240` edges, `40` lines, `4` lines through each
     point.

3. s12/Golay/Monster closure:
   - `tools/s12_universal_algebra.py` gives the grade-only model with
     dimensions `(242,243,243)` and exactly `6` Jacobi-obstruction grade
     triples, while `ad^3` and grade-level Jordan symmetry still hold.
   - `scripts/s12_sl27_heisenberg_algebra.py` resolves the obstruction by
     passing to a genuine Weyl-Heisenberg commutator model.
   - `scripts/w33_monster_3b_s12_sl27_bridge.py` aligns this with
     `3^{1+12}` Heisenberg data and the `3`-qutrit operator basis:
     `729 = 3^6`, `728 = 27^2 - 1 = dim sl(27)`.
   - `scripts/w33_golay_lie_algebra.py` then exposes an exact `24`-dimensional
     perfect centerless Lie algebra over `F_3` with a self-centralizing
     Cartan-like `6`-slice.

4. Tomotope/Reye/contextuality spine:
   - `tools/tomotope_reye_e8_connection.py` and
     `data/w33_twist_transport_reye.json` preserve the exact `12/16` motif:
     tomotope `(12 edges, 16 faces, |Aut|=96)` and Reye `(12 points, 16 lines)`.
   - The hard obstruction remains exact:
     tomotope signature `[48,6,6,6]` differs from the axis signature
     `[48,12,6]`.

5. Vogel arithmetic position:
   - `tools/vogel_rational_dimension_theorem.py` shows that the positive
     nondegenerate exceptional-line hit set does **not** contain
     `242`, `486`, or `728`.
   - The nearest positive hits used elsewhere in the repo remain:
     `242 -> 248`, `486 -> 484`, `728 -> 782`.
   - `728` still has a classical `A_26` dimension interpretation
     (`26^2 - 1 = 728`), but not a positive exceptional-line hit.

## Consequence

The repo already points to one algebraic ladder, not several disconnected ones:

`H27 (1 qutrit, 4 MUBs) -> W33 (2 qutrits, Pauli commutation geometry) -> s12/Golay Heisenberg lift -> sl(27) (3 qutrits)`

That is the route worth pushing on the quark/Yukawa residual. The local
Heisenberg/MUB shell should organize the phase transport first. Only after the
Lie closure is exact should Vogel be applied as a universal constraint on the
resulting Lie/kernel data.

## Outside work worth tracking

The current outside Vogel literature is moving in the same direction as the
repo's strongest obstruction data: away from naive dimension matching and toward
Jacobi, diagrammatic kernels, refinements, and categorical structure.

- `Vogel universality and beyond` (arXiv:2601.01612)
- `Vogel's universality and the classification problem for Jacobi identities`
  (arXiv:2506.15280)
- `On Refined Vogel's universality and link homologies`
  (arXiv:2504.13831)
- `Construction of the Lie algebra weight system kernel via Vogel algebra`
  (arXiv:2411.14417)
- `The Tomotope` by Monson, Pellicer, Williams
- Aravind's `How Reye's configuration helps in proving the Bell-Kochen-Specker theorem`

The actionable inference is narrow:

Do not try to force `728` directly into Vogel's positive exceptional-line hit
set. Use Vogel after the qutrit/Heisenberg closure, at the level of Jacobi
resolution, weight-system kernel structure, and universal constraints on the
completed Lie data.
