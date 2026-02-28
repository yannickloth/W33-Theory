# Tomotope ↔ Triality ↔ Axis-192 Local Weld

## What you asked for
You asked to execute:

1. Build K = <g2,g3,g5,g8,g9>.
2. Export its action on the 192 torsor and on the 2-sheet deck flip.
3. Find the matching action inside the octonion stabilizer-192.
4. The resulting conjugacy is the local weld.

All four are recomputed here, from the uploaded bundles.

---

## 1) K = <g2,g3,g5,g8,g9> (on SRG36)
- |K| = **162**
- Orders: g2,g3,g5 have order 3; g8,g9 have order 2.
- Base pocket P = [0, 1, 2, 14, 15, 17, 27]
- Orbit of P under K: **54** pockets.

Stabilizer of P in K has size **3**, with local permutations on the 7 pocket vertices:
- id
- σ  = [1, 3, 5, 0, 2, 4, 6]
- σ⁻¹= [3, 0, 4, 1, 5, 2, 6]

---

## 2) Export action on the 192 torsor + deck flip
We use the two axis-fixed torsors:
- enc0: 192 elements
- enc1: 192 elements

Action rule on embeddings is by **precomposition with σ⁻¹ on local indices** (verified).

**Deck flip:** for both nontrivial σ, the torsor class is preserved (enc0→enc0, enc1→enc1). No swapping occurs.

---

## 3) Match inside octonion axis-line stabilizer H (order 192)
Let H be the explicit axis-line stabilizer subgroup of the signed-permutation table stabilizer.

Then the torsor action matches **right multiplication in H**:
- σ  ↦ r with **stab_index 399** (order 3)
- σ⁻¹↦ r⁻¹ with **stab_index 246** (order 3)
- id ↦ identity with **stab_index 7**

This equality holds on **all 192 elements** of both enc0 and enc1.

So C3 ≤ K_stab(P) is welded to the triality C3 ≤ H.

---

## 4) The conjugacy = local weld
The local weld is the explicit map:
- pocket stabilizer element σ ↔ octonion stabilizer element r (stab_index 399)
and the statement that the induced torsor action is right multiplication by r.

See: `C3_torsor_right_multiplication_weld.json`.

---

# Tomotope link (your hunch is correct)
From the repo file `PART_CXIV_tomotope_connection.json`:
- tomotope flags = **192 = |W(D4)|**
- |W(E6)|/|W(D4)| = **270**

In our data:
- the axis torsor lives on a **192-element** stabilizer H (exact same “192” object),
- the Schreier graph for K acting on the 54-pocket orbit has **270 directed edges** (=54×5 generator labels).

This places the “axis-192 torsor” exactly where your tomotope/D4 notes say it should live: at the W(D4)=192 level, with an order-3 triality element providing the 3-cycle.

## Bonus: the order-96 Tomotope subgroup inside H
Inside H, the subset with axis sign +1 is a subgroup of order 96 (matches |Γ(Tomotope)|=96 used in your tomotope notes).
We exhibit:
- a normal subgroup of order 16 inside it (abelian Z4×Z4),
- and the quotient action on 6 cosets (S3-sized).

Files:
- `H_plus_axisSignPlus_subgroup_96.json`
- `H_plus_normal_16_Z4xZ4.json`
- `H_plus_quotient_on_6_cosets.json`

