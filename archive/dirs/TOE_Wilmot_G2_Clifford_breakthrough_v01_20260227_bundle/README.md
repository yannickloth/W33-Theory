TOE / Wilmot G2 / Clifford Breakthrough Bundle (v01 2026-02-27)
==============================================================

This bundle does two things, reproducibly:

1) Reproduces Wilmot's "480 representations of the octonions" by an explicit finite computation:
   - Fix a Cayley–Dickson octonion basis {1, e1..e7}.
   - Consider the full signed-permutation group on {e1..e7} (order 2^7 * 7! = 645120).
   - Count the subgroup that preserves the multiplication table (stabilizer).
   - Orbit size = 645120 / |stabilizer| = 480.

2) Computes the derivation algebra of the octonions (Der(O) ≅ g2):
   - Build the linear system D(xy)=D(x)y + xD(y) over GF(p).
   - Nullspace dimension is 14 (for several primes).
   - Add constraints D(e7)=0 to get the axis-stabilizer subalgebra dimension 8 (≅ sl3).

Quick start
-----------
python run_all.py

Outputs are written to ./out/

Files
-----
src/octonion.py
  - multiplication table from oriented Fano triples (matching Cayley–Dickson basis)

src/orbit_480.py
  - counts stabilizer of multiplication table inside signed-permutation group
  - outputs stabilizer order + orbit size

src/derivations_g2.py
  - builds derivation constraint matrix over GF(p)
  - computes nullspace dimension and a basis (mod p)
  - also computes the D(e7)=0 subalgebra

Notes
-----
notes/paper_alignment.md
  - where Wilmot's claims show up in the paper & what we compute here

notes/bridge_to_W33_pockets.md
  - how the 8-dim sl3 axis-stabilizer is the same algebraic core we keep seeing in
    the W33-derived 7-pocket skeletons (1 ⊕ 3 ⊕ 3̄).

