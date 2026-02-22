# Cubic-surface dictionary (27 lines) recovered from a double-six

This repo now recovers the *classical* labeling and incidence rules of the 27 lines on a smooth cubic surface **directly from the computed Schläfli 27-orbit**.

## Objects

Pick a reference double-six `(A,B)` (one of 36). Then label:

- `A = {a_0,…,a_5}` (6 mutually skew lines)
- `B = {b_0,…,b_5}` (6 mutually skew lines), indexed by the perfect matching `a_i ↔ b_i`
- The remaining 15 lines as `c_{ij}` for `0 ≤ i < j ≤ 5`
  - `c_{ij}` is the unique remaining vertex meeting exactly `a_i` and `a_j`

This is the standard “double-six” presentation of the 27 lines.
References:
- https://en.wikipedia.org/wiki/Double_six
- https://en.wikipedia.org/wiki/Cubic_surface

## Verified incidence rules (in-repo, deterministic)

Using the convention:

- “skew adjacency” in the Schläfli graph is inner-product `= 1`
- “meet adjacency” (intersection graph) is inner-product `= 0`

we verify:

- `a_i` meets `b_j` iff `i ≠ j` (and `a_i` is skew to `b_i`).
- `c_{ij}` meets exactly `a_i, a_j, b_i, b_j`.
- `c_{ij}` meets `c_{kl}` iff `{i,j}` and `{k,l}` are disjoint.
- Every line meets exactly 10 others (intersection degree 10).
References:
- https://en.wikipedia.org/wiki/Double_six
- https://en.wikipedia.org/wiki/Schl%C3%A4fli_graph

All of this is enforced by tests; see `tests/test_cubic_surface_labeling.py`.

## Tritangent planes = triangles in the intersection graph

The intersection graph triangles are exactly the 45 tritangent planes.
References:
- https://en.wikipedia.org/wiki/Cubic_surface
- https://en.wikipedia.org/wiki/Schl%C3%A4fli_graph

Our computations recover the standard 45-plane split relative to a double-six:

- **30** planes: `{a_i, b_j, c_{ij}}` with `i ≠ j`
- **15** planes: `{c_{ij}, c_{kl}, c_{mn}}` where `(ij)(kl)(mn)` is a perfect matching of `{0..5}`

This is verified by `tools/classify_tritangent_planes_double_six.py` and `tests/test_tritangent_planes_double_six.py`.

## PG(3,2) on the “remaining 15”

The 15 remaining vertices `c_{ij}` also carry a canonical `PG(3,2)` incidence structure (15 points, 35 lines) via the duad model.
Reference:
- https://en.wikipedia.org/wiki/Projective_space#Finite_projective_spaces

In our setting, the 15 **perfect matchings** correspond exactly to the 15 all-`c_{ij}` tritangent planes.

## Where this pushes the project

This closes a major gap: the “E6 / cubic-surface side” is no longer a loose analogy; it is now *explicitly reconstructed and verified* from the same computational objects (E8 roots → W(E6) 27-orbits → Schläfli).

Next step is **phase/sign structure** (beyond support-only): see `docs/E6_CUBIC_SIGN_STRUCTURE.md`.
