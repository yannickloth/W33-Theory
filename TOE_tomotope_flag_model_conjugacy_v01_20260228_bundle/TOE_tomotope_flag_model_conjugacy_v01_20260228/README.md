# TOE Tomotope Flag Model + Conjugacy (v01, 2026-02-28)

This bundle builds an explicit **192-flag rank-4 maniplex** model (tomotope-like) **inside the axis-line stabilizer** H (order 192) extracted from the W33↔octonion torsor pipeline.

## Key outputs

- `tomotope_flag_model_192.json`
  - flags = 192, indexed by H-elements **sorted by `stab_index`**
  - generators `r0..r3` are **involutions** satisfying the maniplex commutation axioms:
    - r0 commutes with r2,r3
    - r1 commutes with r3
  - **Intersection condition fails** dramatically:
    - |<r0,r1,r2>| = 48
    - |<r1,r2,r3>| = 192 (=H)
    - |<r1,r2>| = 12
    - |<r0,r1,r2> ∩ <r1,r2,r3>| = 48 ≠ |<r1,r2>|
  - This is the defining “tomotope is not a C-group” signature.

- `flag_adjacency_r0_r3_permutations.json`
  - The 4 edge-colored adjacency involutions on the 192 flags.

- `flag_orbits_under_symmetry96.csv`
  - The subgroup `H_plus_axisSignPlus` (order 96) has exactly **2 flag orbits of size 96**, matching the tomotope metadata:
    - flag count 192
    - symmetry order 96
    - flag orbits 2

- `conjugators.json`
  - `axis_torsor_index_to_flag_index` = identity (same stab_index ordering)
  - `inversion_conjugator_left_to_right` = inversion map turning **left regular** ↔ **right regular** actions.

- `verify_tomotope_flag_model.py`
  - Recomputes the commutation checks and the conjugacy check.

## How this connects to our TOE pipeline

- The 192-set is the same “tomotope flags = |W(D4)| = 192” layer recorded in `PART_CXIV_tomotope_connection.json`.
- The welded triality element is `stab_index=399` (order 3), already identified from the pocket-stabilizer C3.

Run verification:
```bash
python verify_tomotope_flag_model.py
```


## Face counts induced by this flag system
This model reproduces the tomotope's **(4 vertices, 12 edges, 16 faces)** as the counts of i-face orbits under the standard maniplex formula.
(One generator is redundant at the group-generation level, which is part of the same non-C-group pathology.)
