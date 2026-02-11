# Minimal Global Full-Sign Contradiction Cores

- Each unsat cell is annotated with a minimal contradiction-core size.
- SAT cells list full match count (global stabilizers).

Mode | z=(1,0) | z=(1,1) | z=(1,2) | z=(2,0) | z=(2,1) | z=(2,2)
--- | --- | --- | --- | --- | --- | ---
all_agl | sat:1 | unsat:3 | unsat:3 | unsat:3 | unsat:3 | unsat:3
hessian216 | sat:1 | unsat:3 | unsat:3 | unsat:3 | unsat:3 | unsat:3
involution_det2 | unsat:4 | unsat:3 | unsat:3 | unsat:3 | unsat:3 | unsat:3

- Theorem flags: `{'all_agl_only_identity_at_z10': True, 'hessian_only_identity_at_z10': True, 'involution_subset_all_unsat': True, 'nontrivial_cells_need_four_striations_in_agl_hessian': True, 'involution_z10_needs_five_with_striation_complete': True}`

## Variant-Constrained Core Sizes

Mode | Variant | z=(1,0) | z=(1,1) | z=(1,2) | z=(2,0) | z=(2,1) | z=(2,2)
--- | --- | --- | --- | --- | --- | --- | ---
all_agl | unconstrained | - | 3 | 3 | 3 | 3 | 3
all_agl | distinct_lines | - | 3 | 3 | 3 | 3 | 3
all_agl | striation_complete | - | 4 | 4 | 4 | 4 | 4
all_agl | distinct_lines_striation_complete | - | 4 | 4 | 4 | 4 | 4
hessian216 | unconstrained | - | 3 | 3 | 3 | 3 | 3
hessian216 | distinct_lines | - | 3 | 3 | 3 | 3 | 3
hessian216 | striation_complete | - | 4 | 4 | 4 | 4 | 4
hessian216 | distinct_lines_striation_complete | - | 4 | 4 | 4 | 4 | 4
involution_det2 | unconstrained | 4 | 3 | 3 | 3 | 3 | 3
involution_det2 | distinct_lines | 4 | 3 | 3 | 3 | 3 | 3
involution_det2 | striation_complete | 5 | 4 | 4 | 4 | 4 | 4
involution_det2 | distinct_lines_striation_complete | 5 | 4 | 4 | 4 | 4 | 4

## Example Minimal Core (all_agl, z=(2,2))

- core size: `3`
- constraints: `[{'line': [[0, 0], [1, 0], [2, 0]], 'line_type': 'y', 'abc': [0, 1, 0], 'z': 0}, {'line': [[0, 1], [1, 1], [2, 1]], 'line_type': 'y', 'abc': [0, 1, 1], 'z': 0}, {'line': [[0, 2], [1, 2], [2, 2]], 'line_type': 'y', 'abc': [0, 1, 2], 'z': 0}]`
