# Continuation: why the A5-based 480-weld cannot be equivariant

This bundle exhausts **all sign-lift homomorphisms** of the two possible injective
A5 embeddings into the signed-permutation group on 7 imaginaries, and records their
orbit signatures on the **480 octonion tables**.

It then extracts the **axis-fixed stabilizer subgroup of size 192** (the 1344 stabilizer
restricted to permutations fixing the chosen axis unit 7), which matches the
count identity you already observed: 192 = 1344 / 7.

## A5 embeddings tested (exhaustive)

### (1) Degree-6 embedding: PSL(2,5) acting on P¹(F5) (6 points) with 1 fixed unit
- Generators: s = x ↦ -1/x (order 2), t = x ↦ x+1 (order 5), with (st) of order 3.
- We brute-forced all sign vectors on 7 units satisfying:
  - s² = 1
  - t⁵ = 1
  - (st)³ = 1
- Result: **64 valid sign lifts**, collapsing into **two orbit-patterns** on the 480 tables:
  - 12×20 + 4×60
  - 8×10 + 8×20 + 8×30

See: `octonion_A5_degree6_signlift_groups.json`.

### (2) Degree-5 embedding: A5 acting on 5 units (fixing two units)
- Presentation generators x (order 2), y (order 3) with (xy) order 5.
- Exhaustive sign-lift search yields **16 valid lifts**.
- All 16 produce the same orbit pattern on the 480 tables:
  - 8×60

See: `octonion_A5_degree5_signlift_groups.json`.

## Consequence for the W33-directed-edge 480-set

On the W33 side (PSp(4,3) acting on the 480 directed edges), every sampled A5 subgroup
acts with orbit signature:

- 6×60 + 6×20

See: `w33_A5_orbit_signature.json`.

Because **no injective A5 embedding into the signed-permutation octonion action**
produces 6×60 + 6×20, there is no way for a would-be 480↔480 weld to be
A5-equivariant where the octonion-side A5 comes from unit signed-permutations.

In other words: the “A5/K5 spine” is real in the W33 transport geometry, but it is not
the right shared symmetry to pin a conjugacy-based weld directly against the octonion 480 orbit.

## Next leverage point: the axis-fixed stabilizer 192 = 1344 / 7

From `octonion_stabilizer_1344.json`, the subset of stabilizer elements fixing axis 7
has size exactly **192**.

We find a 3-element generating set for this subgroup (in its induced action on the 480 tables)
and compute its orbit signature:

- 2×64 + 4×32 + 6×24 + 4×12 + 4×6 + 2×2 + 4×1

See: `octonion_axis7_stabilizer_192_summary.json`.

This is the cleanest “hard match” currently available between:
- Wilmot’s 1344 stabilizer logic, and
- the 192 axis-fixed completion counts already observed in the W33 pocket lift computations.

## Files
- `recompute_exhaust_A5_and_axis192.py` — full recompute (pure Python, no external deps)
- `octonion_A5_degree6_signlift_groups.json`
- `octonion_A5_degree5_signlift_groups.json`
- `w33_A5_orbit_signature.json`
- `octonion_axis7_stabilizer_192_summary.json`
