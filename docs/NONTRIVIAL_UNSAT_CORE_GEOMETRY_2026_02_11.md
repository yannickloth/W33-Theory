# Nontrivial UNSAT Core Geometry (Global Cells)

- Statement: classify all minimal size-3 UNSAT cores in nontrivial global z-cells for `all_agl` and `hessian216`.

Mode | z=(1,1) | z=(1,2) | z=(2,0) | z=(2,1) | z=(2,2)
--- | --- | --- | --- | --- | ---
all_agl | 6 (parallel=6) | 2 (parallel=2) | 4 (parallel=4) | 2 (parallel=2) | 2 (parallel=2)
hessian216 | 6 (parallel=6) | 2 (parallel=2) | 4 (parallel=4) | 2 (parallel=2) | 2 (parallel=2)

- Theorem flags: `{'all_cells_parallel_class_triplets': True, 'core_counts_match_between_agl_and_hessian': True, 'core_signatures_match_between_agl_and_hessian': True}`

## Example (all_agl, z=(1,1))

- line-type profile: `{'x': 3, 'y=1x': 1, 'y=2x': 2}`
- sample cores: `[{'indices': [1, 31, 34], 'constraints': [{'line': [[0, 0], [0, 1], [0, 2]], 'line_type': 'x', 'abc': [1, 0, 0], 'z': 1}, {'line': [[1, 0], [1, 1], [1, 2]], 'line_type': 'x', 'abc': [1, 0, 1], 'z': 1}, {'line': [[2, 0], [2, 1], [2, 2]], 'line_type': 'x', 'abc': [1, 0, 2], 'z': 1}]}, {'indices': [1, 32, 34], 'constraints': [{'line': [[0, 0], [0, 1], [0, 2]], 'line_type': 'x', 'abc': [1, 0, 0], 'z': 1}, {'line': [[1, 0], [1, 1], [1, 2]], 'line_type': 'x', 'abc': [1, 0, 1], 'z': 2}, {'line': [[2, 0], [2, 1], [2, 2]], 'line_type': 'x', 'abc': [1, 0, 2], 'z': 1}]}, {'indices': [2, 31, 34], 'constraints': [{'line': [[0, 0], [0, 1], [0, 2]], 'line_type': 'x', 'abc': [1, 0, 0], 'z': 2}, {'line': [[1, 0], [1, 1], [1, 2]], 'line_type': 'x', 'abc': [1, 0, 1], 'z': 1}, {'line': [[2, 0], [2, 1], [2, 2]], 'line_type': 'x', 'abc': [1, 0, 2], 'z': 1}]}, {'indices': [7, 19, 23], 'constraints': [{'line': [[0, 0], [1, 1], [2, 2]], 'line_type': 'y=1x', 'abc': [1, 2, 0], 'z': 1}, {'line': [[0, 1], [1, 2], [2, 0]], 'line_type': 'y=1x', 'abc': [1, 2, 2], 'z': 1}, {'line': [[0, 2], [1, 0], [2, 1]], 'line_type': 'y=1x', 'abc': [1, 2, 1], 'z': 2}]}]`

## External Context

- Hesse configuration / `AG(2,3)` incidence background: https://arxiv.org/abs/math/0611590
- Affine-plane parallel classes summary: https://en.wikipedia.org/wiki/Incidence_geometry
- Hessian216 group context (det=1 affine transformations over `F3`): https://en.wikipedia.org/wiki/Hessian_group
