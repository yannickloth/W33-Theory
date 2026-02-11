# Nontrivial Core Rulebook

- Rulebook view for nontrivial size-3 global UNSAT cores by z-map and striation.

Mode | z=(1,1) | z=(1,2) | z=(2,0) | z=(2,1) | z=(2,2)
--- | --- | --- | --- | --- | ---
all_agl | 3 | 1 | 2 | 2 | 1
hessian216 | 3 | 1 | 2 | 2 | 1

- Theorem flags: `{'at_most_two_varying_coordinates_per_direction_rule': True, 'at_most_one_missing_cartesian_point_per_direction_rule': True, 'unique_non_cartesian_family_per_mode': True, 'the_non_cartesian_family_is_z11_x_direction': True}`

## Example Rule (all_agl, z=(1,1), direction x)

- triples: `[[1, 1, 1], [1, 2, 1], [2, 1, 1]]`
- fixed: `{'z2': 1}`
- allowed: `{'z0': [1, 2], 'z1': [1, 2]}`
- missing cartesian points: `[[2, 2]]`
