# Minimal Global Full-Sign Contradiction Cores

- Each unsat cell is annotated with a minimal contradiction-core size.
- SAT cells list full match count (global stabilizers).

Mode | z=(1,0) | z=(1,1) | z=(1,2) | z=(2,0) | z=(2,1) | z=(2,2)
--- | --- | --- | --- | --- | --- | ---
all_agl | sat:1 | unsat:3 | unsat:3 | unsat:3 | unsat:3 | unsat:3
hessian216 | sat:1 | unsat:3 | unsat:3 | unsat:3 | unsat:3 | unsat:3
involution_det2 | unsat:4 | unsat:3 | unsat:3 | unsat:3 | unsat:3 | unsat:3

- Theorem flags: `{'all_agl_only_identity_at_z10': True, 'hessian_only_identity_at_z10': True, 'involution_subset_all_unsat': True}`

## Example Minimal Core (all_agl, z=(2,2))

- core size: `3`
- constraints: `[{'line': [[0, 0], [1, 0], [2, 0]], 'line_type': 'y', 'abc': [0, 1, 0], 'z': 0}, {'line': [[0, 1], [1, 1], [2, 1]], 'line_type': 'y', 'abc': [0, 1, 1], 'z': 0}, {'line': [[0, 2], [1, 2], [2, 2]], 'line_type': 'y', 'abc': [0, 1, 2], 'z': 0}]`
