# 7-pocket derivations (triangle algebra on 36 E6-antipode-pairs)

This folder derives and verifies **derivations on a 7-pocket** inside the 36-vertex E6-antipode-pair SRG triangle algebra.

## Inputs
- `TOE_E6pair_SRG_triangle_decomp_v01_20260227_bundle.zip`
- `TOE_edge_to_oriented_rootpairs_v01_20260227_bundle.zip`

From these, we build a partial nonassociative multiplication on basis elements `e_i` (i=0..35):
- Each oriented triangle block `(a,b,c)` yields products:
  - `a*b =  c`, `b*c = a`, `c*a = b`
  - `b*a = -c`, etc.
- This gives exactly 720 ordered products on the 36-basis.

## 7-pockets
Define `closure(S)` as the smallest subset closed under the above product whenever the product result stays inside.
Enumerating all 4-subsets of the 36 vertices yields **540 distinct 7-pockets**.

Every 7-pocket has:
- **6 active elements** (participate in products)
- **1 silent element** (never appears as left/right/output of any internal product)

Example pocket (global indices): `[0, 1, 2, 14, 15, 17, 27]`
- Active: `[0, 1, 2, 14, 15, 17]`
- Silent: `27`
- Internal triangles (unoriented): [(0, 1, 14), (0, 2, 15), (14, 15, 17), (1, 2, 17)]

## Derivations
A derivation is a linear map `D` with:
`D(x*y) = D(x)*y + x*D(y)` for all basis products (including zero products).

For the example 7-pocket (over **Q**):
- `dim Der = 9`
- Derived (commutator) subalgebra has dimension **8**
- Killing form on the 8-dim derived subalgebra is nondegenerate (rank 8)
- A generic element has a 2-dim centralizer ⇒ **rank 2**

Conclusion:
- Semisimple part is **sl3(Q)**
- Full derivation algebra is a 1-dim central extension (≅ **gl3(Q)**)

Representation perspective:
- The 7-dimensional pocket module decomposes as `1 ⊕ 3 ⊕ 3̄` after complexification (commutant dimension 3).

## Files
- `REPORT.json` — summary + key invariants
- `derivation_basis.json` — 9 basis derivation matrices (7×7, column-major images)
- `sl3_structure_constants.json` — commutator structure constants on the 8-dim semisimple basis
- `sl3_killing_form.csv` — Killing form matrix on the 8-dim semisimple basis

