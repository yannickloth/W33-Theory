# W33 Neighbor Action Realizes AGL(2,3) (2026-02-11)

- base vertex: `0`
- claim holds: `True`

## Group Orders

- point count: `40`
- |Aut(W33)|: `51840`
- |Stab(v)|: `1296`

## Neighborhood Geometry

- neighbor count: `12`
- induced degree histogram: `{'2': 12}`
- triangle components (parallel classes): `[[0, 1, 2], [3, 4, 5], [6, 7, 8], [9, 10, 11]]`
- triangles OK: `True`

## Induced Neighbor Action

- induced group order: `432`
- kernel order: `3`
- action on 4 triangles: `24` (S4: `True`)
- triangle-kernel order: `18`
- translations (Z3^2) inside kernel: `9` (normal+abelian: `True`)

## Involutions (Reflections vs Half-Turns)

- total involutions: `45`
- reflections (fix a full triangle): `36`
- half-turns (no full triangle fixed): `9`
- reflections form one conjugacy class: `True`
- reflection centralizer order histogram (D12): `{'1': 1, '2': 7, '3': 2, '6': 2}`
- reflection fixed-triangle histogram: `{'0': 9, '1': 9, '2': 9, '3': 9}`
- reflection axis-triangle histogram: `{'0': 9, '1': 9, '2': 9, '3': 9}`
- centralizer size histograms: `{'reflection': {'12': 36}, 'rotation': {'48': 9}}`

## Cross-Reference

- The reflection centralizer fingerprint (`12`) matches the det=2 involution class computation in `docs/AGL23_DET2_INVOLUTION_CLASS_2026_02_11.md`.
