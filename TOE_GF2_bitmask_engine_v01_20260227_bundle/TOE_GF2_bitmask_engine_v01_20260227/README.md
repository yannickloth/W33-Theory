# GF(2) bitmask linear algebra engine (TOE tooling)

This folder contains a **pure-Python, fast GF(2) linear algebra** module using `int` bitmasks.

Why:
- Our TOE objects naturally produce big sparse incidence/boundary matrices.
- Over GF(2) we can store each row as a bitmask and eliminate with XOR.

Main module:
- `src/gf2lin.py`

Examples:
- `examples/triangle_complex_homology.py` rebuilds the SRG(36,20,10,12) triangle complex from the existing TOE bundles and recomputes ranks/H1.
- `examples/fixed_subspace_H1.py` computes the fixed-subspace dimension in H1 under the 10 sp43 generators (over GF(2)) using a constraint-only approach (no quotient matrices).

Notes:
- `notes/G2_bridge.md` ties the G2/Clifford paper reference to our 240/480/728 numerology and the “3-idempotent triple” structure we are computing.

Run:
```bash
python examples/triangle_complex_homology.py
python examples/fixed_subspace_H1.py
```

- `examples/nonassociative_triangle_algebra.py` builds a non-associative algebra from the 120 face triangles and reports associator statistics.

- `examples/octonion_pockets_7.py` enumerates all **540 closed 7-pockets** in the 36-vertex triangle-product algebra and verifies they form a single G-orbit (stabilizer 48).
