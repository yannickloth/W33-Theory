# WE6-even / PSp(4,3) actions on 120 objects: what is (and is not) conjugate

## 0) Key point
You currently have **two different degree-120 permutation actions** floating around:

1) **Edgepair action** (degree 120, transitive)
   - Source: `artifacts/sp43_edgepair_generators.json`  (field `pair_generators`)
   - Interpretation: coset action on a 120-element homogeneous space (stabilizer order 216).

2) **Line action** (degree 120, intransitive)
   - Source: `SP43_TO_WE6_TRUE_FIXED_BUNDLE_v01_2026-02-25/sp43_line_perms_fixed.json`
   - Interpretation: action induced on **E8 root lines** (antipodal pairs), then restricted
     to the WE6-even copy of PSp(4,3) via the computed word map.

These actions are *not the same representation* of the abstract group.

## 1) Non-conjugacy certificate (cheap + definitive)
If two subgroups of S_120 are conjugate, they have the same orbit partition on {0..119}.

- The edgepair action is **transitive** (one orbit of size 120).
- The line action is **intransitive** with orbits:
  **36 + 27 + 27 + 27 + 1 + 1 + 1**.

Therefore they cannot be conjugate in S_120.
The script `scripts/verify_orbit_decompositions.py` computes and prints this.

This replaces (and strengthens) any cycle-type or class-by-class argument.

## 2) Why 36 + 27 + 27 + 27 + 1 + 1 + 1 is the smoking gun for E6×A2
E8’s root system (240 roots) splits under an E6×A2 embedding as:

- 72 roots = E6 roots
- 6 roots  = A2 roots
- 162 roots = weights of (27,3) ⊕ (\bar{27}, \bar{3}) at the root level

Passing to **root lines** (antipodal pairs), that becomes:

- 72 roots / 2 = **36** E6 root lines
- 6 roots / 2  = **3** A2 root lines
- 162 roots / 2 = **81** mixed root lines = **3 × 27** lines

So the orbit partition in the line action is exactly:
- 36 (E6)
- 27+27+27 (three SU(3)/A2 “colors”)
- 1+1+1 (the three A2 root lines fixed pointwise by W(E6))

That’s the algebraic backbone behind the “3 generations” / “SU(3) color” reading:
the 27 appears *literally* at the root-line level.

## 3) Where this is already encoded in your repo
`artifacts/explicit_bijection_decomposition.json` encodes a dot-pair invariant using:

- u1 = (1,1,1,1,1,1,1,1)
- u2 = (1,1,1,1,1,1,-1,-1)

Each root r gets a key (r·u1, r·u2). The file provides:
- `class72_key = (0,0)`  → 72 roots
- `class1_keys` (6 keys) → 6 singleton roots
- `class27_keys` (6 keys) → 6 classes of size 27 (total 162)

Those six 27-classes pair by sign into three 54-sets = three 27-line orbits.

The script `scripts/classify_e8_roots_dotpair.py` re-derives these counts from the artifact.

## 4) Why this matters for the TOE workflow (practical)
This decomposition gives you a **canonical, group-theoretic block structure** for any
E8-root-indexed object (including W33 edges via the explicit bijection):

- You can run any invariant / holonomy / commutator test **sector-by-sector**:
  - E6 sector (72)
  - A2 sector (6)
  - mixed 27×3 sector (162)

- You can also impose sector constraints in CP-SAT / hillclimb search:
  e.g. do not allow a move that sends an E6 edge into the mixed sector unless the map
  is explicitly allowed to break E6×A2 structure.

The script `scripts/classify_w33_edges_by_rootclass.py` writes:
- artifacts/w33_edges_by_rootclass.csv
- artifacts/w33_edges_by_rootclass_counts.json

so you can start instrumenting the dynamics harness with these tags.
