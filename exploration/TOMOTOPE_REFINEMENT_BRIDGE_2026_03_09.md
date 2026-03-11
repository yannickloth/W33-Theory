# Tomotope Refinement Bridge

## What the tomotope actually fixes

The tomotope gives the project the one thing a frozen finite spectrum cannot:
an explicit infinite family above a finite seed.

From Section 5 of *The Tomotope*:

- `Q_k` is a toroidal family built from a `2k x 2k x 2k` block of unit cubes.
- `|W_k| = 24 * (2k)^3`.
- For `k > 1`, `Q_k` has:
  - `4k^3` vertices
  - `24k^3` edges
  - `32k^3` triangles
  - `8k^3` tetrahedra
  - `4k^3` octahedra
- `|Mon(Q_k)| = 576 * (2k)^6 = 36864 * k^6`.
- `Q_k` covers `Q_m` whenever `m` divides `k`.
- For coprime odd `p, q > 1`, Theorem 5.9 yields distinct minimal regular covers
  `R_p` and `R_q`, neither covering the other.

So the tomotope does supply a genuine infinite cover tower.

## What it does not fix by itself

The explicit carrier in the paper scales like `k^3`, not `k^4`.

That means the natural geometric growth visible in the `Q_k` family is cubic.
So the family is enough to break the "one finite graph has no scale parameter"
firewall, but not enough to prove the exact 4D refinement/scaling theorem
required by the live paper.

My current verdict is:

- The tomotope is a valid refinement source.
- The native `Q_k` tower is best interpreted as an internal or crystallographic
  tower.
- If the goal is a true 4D spectral-action limit, the tomotope tower should be
  coupled to an external 4D refinement family or to an almost-commutative 4D
  spectral triple.

## Why the Reye and 24-cell line still matters

The finite bridge remains structurally important:

- Tomotope edges = `12`
- Tomotope faces = `16`
- Reye points = `12`
- Reye lines = `16`
- 24-cell axes = `12`
- 24-cell hexagons = `16`
- D4 roots = `24`

So the tomotope/Reye/24-cell chain still looks like the right finite internal
geometry. The new point is that the cover family should be used for scaling,
not as a proof that the native carrier is already 4-dimensional.
