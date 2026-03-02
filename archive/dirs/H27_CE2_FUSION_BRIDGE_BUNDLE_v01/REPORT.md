# H27 ↔ CE2/Weil fusion bridge (constructed from W33 geometry + your H27 Heisenberg artifact)

## What is fused
- Rebuilt W33 = symplectic point graph on PG(3,3) (40 vertices, 12-regular).
- Computed H27 (27 non-neighbors of base vertex 0 in our PG ordering).
- Matched our H27 induced graph (degree 8) to your artifact labeling (vertex ids + (x,y,t)).
- Identified the center element z (order 3) whose cycles define the 9 fibers and verified it matches t→t+1.
- Inside the point stabilizer (order 648), found elements inducing SL(2,3) matrices S and T on u=(x,y).
- Recovered the μ-cochain from t-shifts and solved the unique gauge to match canonical Weil μ from f(u)=2xy.

## Key certificates
- `pg_point_to_h27_vertex_coords.csv`: explicit mapping from our PG point ids to artifact vertex ids and (x,y,t).
- `center_orbits_fibers.csv`: the 9 center cycles (t=0,1,2 order) in both labelings.
- `stabilizer_SL2_and_mu_bridge.json`: S,T permutations, observed μ, canonical μ, and gauge (a(u),c) solving μ_obs = μ_can + a(Au)-a(u)+c.

Run `python verify_fusion.py` to re-check all assertions.
