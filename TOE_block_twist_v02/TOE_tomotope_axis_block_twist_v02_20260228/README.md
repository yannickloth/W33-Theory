TOE_tomotope_axis_block_twist_v01_20260228

What this is
------------
Deep-dive alignment diagnostics between:

(1) Axis-192 torsor flag model (order-192 regular monodromy) from:
    TOE_tomotope_flag_model_conjugacy_v01_20260228_bundle.zip
    - flag_adjacency_r0_r3_permutations.json

(2) TRUE tomotope 192-flag maniplex monodromy (order 18432) transported into the
    axis flag labeling via the conjugator pi (fixes r0 and matches r3):

    tomotope_r_generators_in_axis_coords.json

Key structural discovery (the thing to stare at)
------------------------------------------------
The subgroup <r0,r3> is IDENTICAL between the two worlds.

Its 48 orbits (each of size 4) are exactly the 48 incidence pairs (edge,face)
in the tomotope middle layer. This gives a canonical 48×(2×2) fiber:
    48 incidence blocks × (vertex bit) × (cell bit) = 192 flags.

Axis vs tomotope differ *only* in how r1 and r2 glue these 48 blocks together.

Files to read first
-------------------
- SUMMARY.json
- flag_coordinates_tomotope_vs_axis.csv
- blocks48_labeled_by_tomotope_edge_face.csv

Overlap matrices (flag-level)
-----------------------------
- MAT_tomoEdges12_vs_axisEdges16.csv
- MAT_tomoEdges12_vs_axisFaces12.csv
- MAT_tomoFaces16_vs_axisEdges16.csv
- MAT_tomoFaces16_vs_axisFaces12.csv

Overlap matrices (block-level; much cleaner)
--------------------------------------------
- MAT_blocks_tomoEdges12_vs_axisEdges16.csv
- MAT_blocks_tomoEdges12_vs_axisFaces12.csv

Interpretation of block-level overlaps:
- Each tomotope edge = 4 blocks
- Each axis edge = 3 blocks
- Each axis "12-edge model" (exclude r2) = 4 blocks but packed differently.

Next computation to run (now well-posed)
----------------------------------------
Solve for a minimal "rewire" of the axis r1,r2 matchings on these 48 blocks (with
the 2×2 fiber bits) that reproduces the true tomotope r1,r2 glue exactly.

We already have the answer explicitly as permutations in:
  tomotope_r_generators_in_axis_coords.json
So the remaining task is to extract a *small rule* (holonomy / cocycle) that
explains that glue in terms of the axis 7-pocket / octonion constraints.


Added in v02
------------
- tomotope_r1_swaps_edges_given_VFC.csv
- tomotope_r2_swaps_faces_given_VEC.csv
- tomotope_r0_swaps_vertices_given_EFC.csv
- tomotope_r3_swaps_cells_given_VEF.csv
- axis_r1_r2_delta_patterns_in_tomotope_coords.json
