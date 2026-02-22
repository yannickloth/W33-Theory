"""
OUTSIDE THE BOX: Novel Explorations of W33 ↔ E8
==============================================

Unconventional approaches to understanding the deep connection.
"""

from collections import Counter, defaultdict
from itertools import combinations, product

import numpy as np

print("=" * 70)
print("PART 1: E8 ROOTS MOD 3 - The Literal 'Mod 3 Shadow'")
print("=" * 70)


# Generate all 240 E8 roots
def generate_e8_roots():
    roots = []
    # Type 1: all permutations of (±1, ±1, 0, 0, 0, 0, 0, 0)
    for i in range(8):
        for j in range(i + 1, 8):
            for s1 in [1, -1]:
                for s2 in [1, -1]:
                    r = [0] * 8
                    r[i], r[j] = s1, s2
                    roots.append(tuple(r))
    # Type 2: (±1/2, ..., ±1/2) with even number of minus signs
    for signs in product([1, -1], repeat=8):
        if signs.count(-1) % 2 == 0:
            roots.append(tuple(s / 2 for s in signs))
    return roots


e8_roots = generate_e8_roots()
print(f"E8 roots: {len(e8_roots)}")

# What happens when we reduce mod 3?
# For type 1: ±1 mod 3 → ±1 (or 1, 2 in {0,1,2})
# For type 2: ±1/2 ... this is fractional!

# KEY INSIGHT: E8 has two coordinate systems!
# 1. Standard basis (allows half-integers)
# 2. A8 embedding (all integers)

# Let's use the "even coordinate system" where all roots have integer coords
# This is the D8 + spinor decomposition in a different basis

print("\n--- Analyzing root types mod 3 ---")

type1_roots = [r for r in e8_roots if all(abs(x) in [0, 1] for x in r)]
type2_roots = [r for r in e8_roots if any(abs(x) == 0.5 for x in r)]

print(f"Type 1 (integer coords): {len(type1_roots)}")
print(f"Type 2 (half-integer coords): {len(type2_roots)}")


# For type 1: reduce mod 3
def mod3(vec):
    """Reduce vector mod 3, mapping to {-1, 0, 1}"""
    return tuple(int(x) % 3 if int(x) == x else None for x in vec)


type1_mod3 = [mod3(r) for r in type1_roots]
unique_type1 = set(type1_mod3)
print(f"\nType 1 mod 3: {len(unique_type1)} unique patterns")

# Count occurrences
type1_counts = Counter(type1_mod3)
print("Distribution of type 1 mod 3 patterns:")
for pattern, count in sorted(type1_counts.items(), key=lambda x: -x[1])[:10]:
    print(f"  {pattern}: {count}")


# For type 2: multiply by 2 first to get integers, then mod 3
def type2_to_int_mod3(vec):
    """Convert half-integer to int, then mod 3"""
    return tuple(int(2 * x) % 3 for x in vec)


type2_mod3 = [type2_to_int_mod3(r) for r in type2_roots]
unique_type2 = set(type2_mod3)
print(f"\nType 2 (×2) mod 3: {len(unique_type2)} unique patterns")

type2_counts = Counter(type2_mod3)
print("Distribution of type 2 (×2) mod 3 patterns:")
for pattern, count in sorted(type2_counts.items(), key=lambda x: -x[1])[:10]:
    print(f"  {pattern}: {count}")

print("\n" + "=" * 70)
print("PART 2: THE 240 AS GAUGE DEGREES OF FREEDOM")
print("=" * 70)

print(
    """
In gauge theory:
- SU(N) has N² - 1 generators (gauge bosons)
- SO(N) has N(N-1)/2 generators
- Exceptional groups: E₆ has 78, E₇ has 133, E₈ has 248

E8 gauge theory:
- dim(E8) = 248 = 8 (Cartan) + 240 (roots)
- The 240 roots ↔ 240 non-diagonal generators
- These are the "charged" gauge bosons

W33 perspective:
- 240 edges = connections between 40 points
- Each edge represents a "transition" between states
- Gauge bosons mediate transitions!
"""
)

# The Standard Model gauge group
print("Standard Model: SU(3)×SU(2)×U(1)")
print(f"  Generators: 8 + 3 + 1 = 12")
print(f"  Gauge bosons: gluons (8) + W±,Z (3) + photon (1) = 12")

# E8 embedding
print(f"\nE8 → SM decomposition (hypothetical):")
print(f"  E8 = 248 dimensions")
print(f"  248 = 8 + 240 (Cartan + roots)")

# Key number: 240/12 = 20
print(f"\n  240 / 12 = {240/12} -- twenty copies of SM generators?")
print(f"  240 / 8 = {240/8} -- thirty copies of gluon-type?")

# What about W33?
print(f"\nW33 perspective:")
print(f"  40 vertices, 12 edges per vertex")
print(f"  Each vertex has 12 'gauge connections'")
print(f"  12 = dim(SM gauge) !")

# Coincidence or deep?
print(f"\n  Compare: degree of W33 = 12 = dim(SM gauge group)")
print(f"  Fermions in one generation: 15 (with right-handed ν) or 16 (with sterile)")
print(f"  Non-neighbors in W33: 40 - 1 - 12 = 27 (E6 fundamental!)")

print("\n" + "=" * 70)
print("PART 3: GF(3) AND THREE GENERATIONS - A RADICAL IDEA")
print("=" * 70)

print(
    """
GF(3) = {0, 1, 2} with arithmetic mod 3
Alternative view: {-1, 0, +1} (balanced ternary)

RADICAL HYPOTHESIS:
The three generations are the THREE ELEMENTS of GF(3)!

Generation 1 (e, ν_e, u, d)     ↔  0 ∈ GF(3)  (ground state)
Generation 2 (μ, ν_μ, c, s)    ↔  1 ∈ GF(3)  (first excitation)
Generation 3 (τ, ν_τ, t, b)    ↔  2 ∈ GF(3)  (second excitation)

Or in balanced form:
Generation 1  ↔  0   (matter)
Generation 2  ↔  +1  (heavier matter)
Generation 3  ↔  -1  (heaviest matter)
"""
)

# W33 is over GF(3)⁴ - the 4D vector space
print("W33 = W(3,3) over GF(3)⁴:")
print(f"  |GF(3)⁴| = 3⁴ = 81 vectors")
print(f"  Isotropic vectors: 40 (the W33 vertices)")
print(f"  Non-isotropic: 81 - 40 - 1 = 40 (counting zero)")

# Actually count properly
print("\n--- Counting vectors in GF(3)⁴ ---")

# Generate GF(3)^4
gf3_4 = list(product([0, 1, 2], repeat=4))
print(f"Total vectors: {len(gf3_4)}")


# The symplectic form: ω(x,y) = x₀y₁ - x₁y₀ + x₂y₃ - x₃y₂ (mod 3)
def symplectic(x, y):
    return (x[0] * y[1] - x[1] * y[0] + x[2] * y[3] - x[3] * y[2]) % 3


# Isotropic vectors: ω(v, ?) = 0 for all... no wait
# Actually isotropic means: the set of vectors perpendicular to v has dimension 3

# Let's find totally isotropic subspaces
# A vector v is isotropic if ω(v,v) = 0
# But ω is alternating, so ω(v,v) = 0 always!

# The "isotropic" condition for a subspace: ω(u,v) = 0 for all u,v in subspace

# For W(3,3), the points are 1-dimensional isotropic subspaces
# = projective points = (81-1)/2 = 40 projective points

print(f"Projective points in PG(3, GF(3)): (81-1)/2 = 40")

# Each projective point = {v, 2v} for v ≠ 0
# These are the 40 vertices of W33

print("\n--- The GF(3) trichotomy ---")
print(
    """
In GF(3), every nonzero element is ±1:
  1 = +1
  2 = -1 (since 2 ≡ -1 mod 3)

This gives a NATURAL PAIRING of projective points!

For any projective point [v], we can ask:
  Does a coordinate equal 0, 1, or 2?

The three generations might correspond to:
  - Points with "balanced" coordinates (more 0s)
  - Points with "positive" dominance (more 1s)
  - Points with "negative" dominance (more 2s)
"""
)


# Let's classify the 40 projective points
def normalize_projective(v):
    """Normalize to smallest nonzero leading coefficient"""
    for i, x in enumerate(v):
        if x != 0:
            if x == 2:  # multiply by 2 (= -1, inverse of 2 mod 3)
                return tuple((2 * c) % 3 for c in v)
            return v
    return v


projective_points = set()
for v in gf3_4:
    if v != (0, 0, 0, 0):
        pv = normalize_projective(v)
        projective_points.add(pv)

print(f"\nProjective points found: {len(projective_points)}")


# Classify by pattern
def classify_point(v):
    """Classify by counts of 0, 1, 2"""
    return (v.count(0), v.count(1), v.count(2))


classifications = defaultdict(list)
for p in projective_points:
    c = classify_point(p)
    classifications[c].append(p)

print("\nClassification by (count_0, count_1, count_2):")
for c, pts in sorted(classifications.items()):
    print(f"  {c}: {len(pts)} points")

print("\n" + "=" * 70)
print("PART 4: THE CORRESPONDENCE AT COUNTING LEVEL")
print("=" * 70)

print(
    """
Both E8 and W33 share these numbers:
  240 - roots / edges
  40  - ??? / vertices
  6   - roots per A₂ / edges per t.i. 2-space

E8 numbers:
  240 roots
  1120 A₂ subsystems
  2160 A₁ subsystems (maybe?)
  120 pairs of opposite roots

W33 numbers:
  40 vertices
  240 edges
  40 totally isotropic 2-spaces
  280 maximal cliques (4-cliques)
"""
)

# Let's verify the clique count
print("\n--- Counting structures in both ---")


# W33 graph construction
def build_w33():
    vertices = list(projective_points)
    edges = []
    for i, v in enumerate(vertices):
        for j, u in enumerate(vertices):
            if i < j:
                if symplectic(v, u) == 0:
                    edges.append((i, j))
    return vertices, edges


vertices, edges = build_w33()
print(f"W33: {len(vertices)} vertices, {len(edges)} edges")

# Build adjacency for clique finding
adj = defaultdict(set)
for i, j in edges:
    adj[i].add(j)
    adj[j].add(i)

# Count 3-cliques (triangles)
triangles = 0
for i in range(len(vertices)):
    for j in adj[i]:
        if j > i:
            for k in adj[i] & adj[j]:
                if k > j:
                    triangles += 1
print(f"Triangles (3-cliques): {triangles}")

# Count 4-cliques
four_cliques = 0
for i in range(len(vertices)):
    ni = adj[i]
    for j in ni:
        if j > i:
            common_ij = ni & adj[j]
            for k in common_ij:
                if k > j:
                    common_ijk = common_ij & adj[k]
                    for l in common_ijk:
                        if l > k:
                            four_cliques += 1
print(f"4-cliques: {four_cliques}")

# The 4-cliques are the totally isotropic 2-spaces!
print(f"\n4-cliques = t.i. 2-spaces = {four_cliques}")
print(f"This should be 40 (it's the dual structure!)")

print("\n" + "=" * 70)
print("PART 5: OUTSIDE THE BOX - QUTRIT QUANTUM MECHANICS")
print("=" * 70)

print(
    """
RADICAL REFRAMING: W33 is the "geometry of qutrits"

A QUTRIT has 3 basis states: |0⟩, |1⟩, |2⟩
This is quantum mechanics over GF(3) (in some sense)

The 40 vertices of W33 could represent:
- 40 "pure states" of a qutrit pair
- Measurement contexts
- Commuting observables

The symplectic form ω(v,u) = 0 means:
- v and u are "compatible" observables
- They can be measured simultaneously
- They share an eigenstate

PHYSICS INTERPRETATION:
- 40 vertices = 40 fundamental particles/states
- 12 neighbors = 12 gauge interactions
- 27 non-neighbors = 27 E6 "matter" states
- 240 edges = 240 gauge bosons (E8 roots)
"""
)

# Pauli matrices for qutrits (generalized)
print("\n--- Qutrit Pauli group structure ---")
print("Qutrit Paulis: X (shift), Z (phase), ω = exp(2πi/3)")
print("X|j⟩ = |j+1 mod 3⟩")
print("Z|j⟩ = ω^j |j⟩")
print("Pauli group on n qutrits: |G| = 2 × 3^(2n+1)")
print(f"For n=2 qutrits: |G| = 2 × 3⁵ = 2 × 243 = 486")

# The Heisenberg-Weyl group
print(f"\nHeisenberg-Weyl group HW(2, GF(3)):")
print(f"  Central extension of GF(3)⁴")
print(f"  Order: 3 × 3⁴ = 3⁵ = 243")
print(f"  Projective HW: 243/3 = 81 = |GF(3)⁴|")

print("\n" + "=" * 70)
print("PART 6: THE MISSING LINK - 22 vs 56")
print("=" * 70)

print(
    """
L(W33) has degree 22
E8 root graph has degree 56

Why such different degrees if 240 = 240?

INSIGHT: Different "inner products"!

L(W33): Two edges are adjacent if they SHARE a vertex
  - Edge {a,b} ~ Edge {b,c} because they share b
  - This is about GEOMETRIC incidence

E8 root: Two roots are adjacent if ⟨α,β⟩ = 1
  - This is about ALGEBRAIC inner product
  - Positive roots form half of the picture

The ratio: 56/22 ≈ 2.545... (not a nice number)
But: 56 - 22 = 34
And: 56 + 22 = 78 = dim(E6)!
"""
)

print(f"\n56 + 22 = {56 + 22} = dim(E6) !")
print(f"56 - 22 = {56 - 22}")
print(f"56 × 22 = {56 * 22}")
print(f"56 / 22 = {56/22:.6f}")

# More numerology
print(f"\n56 = 7 × 8 (dim of fundamental rep of E7)")
print(f"22 = 2 × 11")
print(f"78 = 3 × 26 = dim(E6)")
print(f"78/6 = 13 (projective plane order)")

# What about the edge counts?
print(f"\nEdge counts:")
print(f"  L(W33): 240 × 22 / 2 = {240*22//2}")
print(f"  E8 root graph: 240 × 56 / 2 = {240*56//2}")
print(f"  Ratio: {6720/2640} = {6720//2640 if 6720 % 2640 == 0 else 6720/2640:.4f}")

print("\n" + "=" * 70)
print("PART 7: SYNTHESIS - THE BIG PICTURE")
print("=" * 70)

print(
    """
╔══════════════════════════════════════════════════════════════════════╗
║                    W33 ↔ E8 CORRESPONDENCE                          ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  W33 (discrete, GF(3))          E8 (continuous, ℝ)                  ║
║  ─────────────────────          ─────────────────                    ║
║  40 isotropic points     ↔      40 = 1120/28 (A₂ quotient)          ║
║  240 edges               ↔      240 roots                            ║
║  12 neighbors/vertex     ↔      12 = dim(SM gauge)                   ║
║  27 non-neighbors        ↔      27 = dim(E6 fundamental)             ║
║  |Aut| = 51840           ↔      |W(E6)| = 51840                      ║
║                                                                      ║
║  SELF-DUAL!              ↔      E8 is self-dual lattice!            ║
║                                                                      ║
║  GF(3) = 3 elements      ↔      3 generations                        ║
║  3⁴ = 81 vectors         ↔      81 = 3⁴ (dimension magic)            ║
║                                                                      ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  KEY INSIGHT: W33 is the "SKELETON" of E8 in the following sense:   ║
║                                                                      ║
║  • W33 captures the COMBINATORIAL structure                          ║
║  • E8 adds the METRIC (angles, lengths)                              ║
║  • The metric introduces the factor 56/22 ≈ 2.5                      ║
║  • But the COUNT (240) and SYMMETRY (via E6) are preserved          ║
║                                                                      ║
║  It's like:  Graph (combinatorics) vs Geometry (metric)              ║
║              Digital (discrete) vs Analog (continuous)               ║
║              GF(3) (finite field) vs ℝ (real numbers)               ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
"""
)

# Final computation: what structure maps bijectively?
print("\n--- WHAT MAPS BIJECTIVELY? ---")
print(
    """
NOT the graphs (degrees differ: 22 vs 56)

POSSIBLY:
1. The 240-element sets (just as sets)
2. Under E6 action (51840 symmetries)
3. With the 40-partition respected

The E6 Weyl group acts on BOTH:
- On W33 as full automorphism group
- On E8 roots as subgroup of W(E8)

This suggests: W33 = E8/E6 in some quotient sense?
Index: |W(E8)|/|W(E6)| = 696729600/51840 = 13440 = 240 × 56
"""
)

print(f"\n13440 = 240 × 56 = (roots) × (root-graph degree)")
print(f"13440 = 40 × 336 = (vertices) × ???")
print(f"336 = 8! / (8-3)! / 3! × something?")
print(f"336 = 2⁴ × 21 = 16 × 21 = 16 × 3 × 7")

print("\n✓ The 13440 encodes BOTH the 240 and the 56!")
print("✓ This is the 'size' of the E8 structure relative to E6")
