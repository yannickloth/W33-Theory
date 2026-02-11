# Orbit-Stabilizer Bridge (2026-02-11)

- action size: `2592` (`AGL(2,3)=432`, `z-affine=6`)
- claim holds: `True`

## hessian

- source: `artifacts\e6_f3_trilinear_min_cert_enumeration_hessian_exhaustive2_with_geotypes.json`
- representatives: `256`
- orbit histogram: `{'1296': 55, '2592': 201}`
- stabilizer histogram: `{'1': 201, '2': 55}`
- orbit-stabilizer identity holds: `True`
- nontrivial stabilizer reps: `55`
- nontrivial z-map histogram: `{'[1, 0]': 49, '[2, 0]': 5, '[2, 1]': 1}`
- nontrivial linear det/order hist: `det={'2': 55}, order={'2': 55}`
- nontrivial point signatures: `[[1, 1, 1, 2, 2, 2]]`
- nontrivial line signatures: `[[1, 1, 1, 1, 2, 2, 2, 2]]`

## agl

- source: `artifacts\e6_f3_trilinear_min_cert_classified_agl_exhaustive.json`
- representatives: `7`
- orbit histogram: `{'2592': 7}`
- stabilizer histogram: `{'1': 7}`
- orbit-stabilizer identity holds: `True`
- nontrivial stabilizer reps: `0`
- nontrivial z-map histogram: `{}`
- nontrivial linear det/order hist: `det={}, order={}`
- nontrivial point signatures: `[]`
- nontrivial line signatures: `[]`

## Claim Checks

- `orbit_stabilizer_identity_holds_all_spaces`: `True`
- `hessian_reduced_orbits_have_stabilizer_2`: `True`
- `full_orbits_have_stabilizer_1`: `True`
- `nontrivial_stabilizers_only_in_hessian`: `True`
- `all_hessian_nontrivial_linear_parts_are_det2_order2`: `True`
- `hessian_nontrivial_cycle_signatures_match_gl2_bridge`: `True`
