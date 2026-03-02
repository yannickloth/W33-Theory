INFINITY_NEIGHBOR_CHARGE_TABLE_BUNDLE_v01
========================================

This bundle is computed directly from the proven outer-twist action in:
  /mnt/data/H27_OUTER_TWIST_ACTION_BUNDLE_v01.zip

and the canonical PG(3,3) indexing implied by your perm40 list:
  - infinity plane: ids 0..12  (PG(2,3) with canonical lex reps)
  - affine chart:   ids 13..39 with id = 13 + 9x + 3y + t.

Core construction
----------------
We model the 40 points as projective 1-spaces in F_3^4:
  - infinity point i (0<=i<=12): vector (0,a,b,c) where (a,b,c) is its PG(2,3) rep
  - affine point (x,y,t): vector (1,x,y,t).

We fix the alternating (rank-4) symplectic form J (mod 3) stored in
  symplectic_form_and_outer_matrix.json

and define collinearity in W(3,3) by:
  points v,w are collinear  <=>  v^T J w = 0 (mod 3).

This yields the W(3,3) collinearity graph:
  - 40 vertices
  - regular degree 12
  - 240 edges (edge list in W33_collinearity_edges_240.csv)

Key fact: the "charge table"
----------------------------
For every affine point (x,y,t), the set of its neighbors in the infinity plane
is exactly 4 points, and depends only on u=(x,y), not on t.

Explicitly, an infinity direction rep (a,b,c) is collinear with affine u=(x,y)
iff the linear equation holds:

  c + x*b - y*a = 0   (mod 3)
  equivalently  c = y*a - x*b  (mod 3).

So each u in F_3^2 parametrizes one of the 9 projective lines of PG(2,3)
that do NOT pass through the special infinity point id=0.

Outputs
-------
- u_to_4_infinity_neighbors_compressed9.csv
    9 rows (u=(x,y)), each gives the 4 infinity ids and their PG(2,3) reps.

- affine_point_to_4_infinity_neighbors_full27.csv
    27 rows (x,y,t), each gives the same 4 infinity ids (constant along t).

Outer twist orbit structure
---------------------------
The outer twist is represented by the homogeneous matrix N4 (mod 3)
also stored in symplectic_form_and_outer_matrix.json, with multiplier lambda=2:

  N4^T J N4 = 2 J.

Orbit data is in outer_orbit_summaries.json:
  - vertices (affine) split into 3 eight-cycles + 1 fixed + 1 two-cycle
  - edges (240) split into 26 orbits of size 8 and 8 orbits of size 4.
