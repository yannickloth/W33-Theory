TOE: E6 antipode-pair algebra extracted from the equivariant map (W33 edges → oriented root-pair triples)

This folder is derived from:
  /mnt/data/TOE_edge_to_oriented_rootpairs_v01_20260227

Key computed structures:

1) 36 antipode pairs (E6 root-pairs)
-----------------------------------
From the 72-root orbit of the PSp(4,3) action on E8 roots, take the antipode involution.
This yields 36 unordered antipode pairs.
File: e6_antipode_pairs_36.json

2) Strongly regular graph on 36 vertices
----------------------------------------
Define a graph on these 36 vertices: connect two vertices iff they co-occur in a block (see below).
Result is strongly regular with parameters:
  (v,k,λ,μ) = (36,20,10,12)
Spectrum: 20^1, 2^20, (-4)^15.
Files:
  e6pair_srg_edges_36_k20_lambda10_mu12.csv
  e6pair_srg_adj_36x36.npy

3) Triangle decomposition (120 blocks)
--------------------------------------
Each W33 edgepair (opposite-edge pair on a 4-point line) maps to an *unoriented* triple of antipode-pairs.
Those 120 triples are triangles in the SRG, and they partition all 360 SRG edges:
  SRG edges = disjoint union of 120 triangles.
File: triangle_decomposition_120_blocks.json

4) Generator action on the 36-vertex SRG
----------------------------------------
The 10 sp43 generators induce permutations on the 36 vertices:
File: sp43_generators_on_e6pairs_36.json

5) Transport cocycles on edges
------------------------------
Using the oriented-triple model (cyclic order on 3 pairs), we get:
  • Z3 rotation transport (which cyclic rotation occurs)
  • Z2 flip transport (whether generator swaps an edge with its opposite)
Files:
  transport_rotation_Z3_by_edge_and_generator.csv
  transport_rotation_Z3_stats.json
  transport_flip_Z2_by_edge_and_generator.csv
  transport_flip_Z2_stats.json

6) W33 line ↔ 3 triangles correspondence
----------------------------------------
Each W33 line contains 3 opposite-edge pairs (edgepairs), hence 3 triangles in the SRG.
File: w33_line_to_e6pair_triangles.json
