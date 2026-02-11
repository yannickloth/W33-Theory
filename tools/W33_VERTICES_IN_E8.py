#!/usr/bin/env python3
"""
W33_VERTICES_IN_E8.py
=====================

Finding what the 40 W33 vertices correspond to in E8 structure.

Key question: W33 has 40 vertices and 240 edges.
              E8 has 240 roots and various 40-element substructures.

What is the 40 ↔ 40 correspondence that underlies the 240 ↔ 240 bijection?

Candidates:
1. 40 points of some polytope embedded in E8
2. 40 = coset representatives of some subgroup
3. 40 distinguished roots / root subsystem
4. 40 = some Weyl orbit decomposition

Let's investigate systematically.
"""

from collections import Counter, defaultdict
from fractions import Fraction
from itertools import combinations, product

import numpy as np

print("=" * 70)
print("40 W33 VERTICES ↔ ? IN E8 STRUCTURE")
print("=" * 70)

# =============================================================================
# PART 1: THE NUMBER 40 IN E8 CONTEXT
# =============================================================================

print("\n" + "=" * 70)
print("PART 1: WHERE DOES 40 APPEAR IN E8?")
print("=" * 70)

print(
    """
Let's find natural occurrences of 40 in E8-related structures.

E8 facts:
  - 240 roots
  - 240 / 6 = 40 (roots modulo some 6-element structure?)
  - |W(E8)| = 696,729,600 = 2^14 × 3^5 × 5^2 × 7
  - |W(E6)| = 51,840 = 2^7 × 3^4 × 5
  - |W(E8)| / |W(E6)| = 13,440 = 2^7 × 3 × 5 × 7

The ratio 240/40 = 6 is suggestive.
Each W33 vertex has degree 12 = 2×6.
"""
)

# 40 in terms of E8 structure
print("40 = ?")
print(f"  240 / 6 = {240 // 6}")
print(f"  240 / 40 = {240 // 40} (each vertex incident to 6 edges? No, degree is 12)")

# Wait, in W33 each vertex has degree 12
# So each vertex is incident to 12 edges
# Total vertex-edge incidences = 40 × 12 = 480 = 2 × 240 ✓ (each edge counted twice)

print(f"\n40 × 12 = {40 * 12} = 2 × 240 ✓ (vertex-edge incidence count)")

# =============================================================================
# PART 2: E8 ROOT SUBSYSTEMS
# =============================================================================

print("\n" + "=" * 70)
print("PART 2: ROOT SUBSYSTEMS CONTAINING 40 ELEMENTS")
print("=" * 70)

print(
    """
Root subsystems of E8:
  - E8: 240 roots
  - E7: 126 roots
  - E6: 72 roots
  - D8: 112 roots
  - D7: 84 roots
  - D6: 60 roots
  - D5: 40 roots  ← FOUND IT!
  - D4: 24 roots
  - A7: 56 roots
  - A6: 42 roots
  - A5: 30 roots
  - A4: 20 roots
  - A3: 12 roots
  - A2: 6 roots
  - A1: 2 roots

D5 has exactly 40 roots!
"""
)

print("D5 root system:")
print("  Rank: 5")
print("  Roots: 2 × C(5,2) = 2 × 10 × 2 = 40 ✓")
print("  Form: (±1, ±1, 0, 0, 0) and permutations in R^5")

# D_n has 2n(n-1) roots
for n in range(2, 9):
    dn_roots = 2 * n * (n - 1)
    print(f"  D{n}: {dn_roots} roots")

print(f"\nD5 has {2*5*4} = 40 roots ✓")

# =============================================================================
# PART 3: THE D5 EMBEDDING
# =============================================================================

print("\n" + "=" * 70)
print("PART 3: D5 ⊂ E8 AND THE 40-40 CORRESPONDENCE")
print("=" * 70)

print(
    """
HYPOTHESIS: W33 vertices ↔ D5 roots (both have 40 elements)

D5 embeds into E8 in several ways. The standard embedding uses
the first 5 coordinates of R^8.

Let's check if this gives the right structure.

D5 root system in R^5:
  - Roots: (±eᵢ ± eⱼ) for 1 ≤ i < j ≤ 5
  - Total: 2 × C(5,2) × 2 = 4 × 10 = 40 ✓

Embedded in E8 (first 5 coordinates):
  - D5 roots become E8 roots of form (±1, ±1, 0, 0, 0, 0, 0, 0) etc.
"""
)


# Generate D5 roots embedded in E8
def generate_d5_in_e8():
    """Generate D5 roots as a subset of E8 roots."""
    d5_roots = []

    # D5: (±1, ±1, 0, 0, 0) in positions 0-4, zeros in positions 5-7
    for pos in combinations(range(5), 2):
        for signs in product([1, -1], repeat=2):
            root = [0] * 8
            root[pos[0]] = signs[0]
            root[pos[1]] = signs[1]
            d5_roots.append(tuple(root))

    return d5_roots


d5_roots = generate_d5_in_e8()
print(f"D5 roots embedded in E8: {len(d5_roots)}")

# Verify they're E8 roots (squared length 2)
sq_lens = [sum(x * x for x in r) for r in d5_roots]
print(f"Squared lengths: {set(sq_lens)}")

# =============================================================================
# PART 4: D5 ROOT GRAPH = W33?
# =============================================================================

print("\n" + "=" * 70)
print("PART 4: IS THE D5 ROOT GRAPH ≅ W33?")
print("=" * 70)

print(
    """
The D5 root graph:
  - Vertices: 40 D5 roots
  - Edges: Two roots adjacent if their inner product is ±1

Let's compute this and compare with W33 parameters.
"""
)

# Build D5 root graph
d5_adj = defaultdict(set)
d5_edges = []

for i in range(len(d5_roots)):
    for j in range(i + 1, len(d5_roots)):
        ip = sum(a * b for a, b in zip(d5_roots[i], d5_roots[j]))
        if abs(ip) == 1:  # adjacent in root graph
            d5_adj[i].add(j)
            d5_adj[j].add(i)
            d5_edges.append((i, j))

print(f"D5 root graph edges: {len(d5_edges)}")

# Degree
d5_degrees = [len(d5_adj[i]) for i in range(len(d5_roots))]
print(f"D5 root graph degrees: {set(d5_degrees)}")

# Check λ (common neighbors for adjacent pair)
if d5_edges:
    i, j = d5_edges[0]
    common = d5_adj[i] & d5_adj[j]
    print(f"λ (common neighbors for adjacent): {len(common)}")

# Check μ (common neighbors for non-adjacent pair)
non_adj_pair = None
for i in range(40):
    for j in range(i + 1, 40):
        if j not in d5_adj[i]:
            non_adj_pair = (i, j)
            break
    if non_adj_pair:
        break

if non_adj_pair:
    common_non = d5_adj[non_adj_pair[0]] & d5_adj[non_adj_pair[1]]
    print(f"μ (common neighbors for non-adjacent): {len(common_non)}")

print(f"\nW33 parameters: SRG(40, 12, 2, 4)")
print(f"D5 root graph: SRG(40, ?, ?, ?)")

# =============================================================================
# PART 5: ALTERNATIVE - A3 × A1 OR OTHER STRUCTURES
# =============================================================================

print("\n" + "=" * 70)
print("PART 5: ALTERNATIVE 40-ELEMENT STRUCTURES")
print("=" * 70)

print(
    """
D5 root graph has different parameters than W33.
Let's look for other 40-element structures in E8.

Options:
1. Some orbit of W(E8) or W(E6) with 40 elements
2. A geometric structure (polytope vertices)
3. Coset representatives
"""
)

# W(E6) has order 51840
# If a subgroup H has index 51840/40 = 1296, then W(E6)/H has 40 elements
print(f"\n|W(E6)| / 40 = {51840 // 40} = 1296")
print(f"1296 = 2^4 × 3^4 = 16 × 81")

# Looking for subgroups of order 1296 in W(E6)
# W(E6) has a subgroup W(A5) × S2 of order 720 × 2 = 1440, close but not 1296
# W(E6) has W(D5) as subgroup of order 2^4 × 5! / 2 = 16 × 60 = 960, no

# Actually, let's think differently
# 40 isotropic lines in GF(3)^4 under Sp(4,3) action
# |Sp(4,3)| = 51840 (coincidentally = |W(E6)|)
# Stabilizer of a line has order 51840/40 = 1296

print(f"\nStabilizer of a line in Sp(4,3): order {51840 // 40}")

# =============================================================================
# PART 6: THE SP(4,3) ↔ W(E6) CONNECTION
# =============================================================================

print("\n" + "=" * 70)
print("PART 6: Sp(4,3) ≅ W(E6): THE ISOMORPHISM")
print("=" * 70)

print(
    """
CRUCIAL FACT: PSp(4, 3) ≅ W(E6) / Z₂

More precisely:
  |Sp(4,3)| = |W(E6)| = 51840

The symplectic group Sp(4, GF(3)) acting on GF(3)^4 IS (up to center)
the Weyl group of E6!

This means:
  - The 40 isotropic lines in GF(3)^4 = 40 objects in some E6 structure
  - The 240 orthogonal line pairs = 240 E8 roots (via E6 ⊂ E8)

The connection is:
  W33 = symplectic polar graph = E6-related structure embedded in E8
"""
)

# Let's verify |Sp(4,3)|
# |Sp(2n, q)| = q^(n²) × ∏ᵢ₌₁ⁿ (q^(2i) - 1)
# For n=2, q=3:
# |Sp(4,3)| = 3^4 × (3² - 1) × (3⁴ - 1) = 81 × 8 × 80 = 81 × 640 = 51840 ✓

sp4_3_order = 3**4 * (3**2 - 1) * (3**4 - 1)
print(f"\n|Sp(4,3)| = 3⁴ × (3² - 1) × (3⁴ - 1) = {sp4_3_order}")
print(f"|W(E6)| = 51840")
print(f"Match: {sp4_3_order == 51840}")

# =============================================================================
# PART 7: THE 40 VERTICES AS E6 WEIGHT STRUCTURE
# =============================================================================

print("\n" + "=" * 70)
print("PART 7: 40 VERTICES AS E6 WEIGHTS")
print("=" * 70)

print(
    """
E6 has several representations with interesting dimensions:
  - Fundamental rep (27-dimensional, related to exceptional Jordan algebra)
  - Adjoint rep (78-dimensional)
  - etc.

The 40 isotropic lines might correspond to:
  - 40 weights in some E6 representation
  - 40 = 27 + 13? or 27 + 12 + 1?
  - Or a different decomposition

Actually, 40 = 27 + 13... but 27 is the fundamental rep dimension.
Let's think about this more carefully.

The E6 weight lattice has various orbits under W(E6).
We need an orbit of size 40.
"""
)

# W(E6) orbit sizes
# The fundamental rep weights might give us insight
# E6 fundamental rep: 27 dimensional
# Under W(E6), the 27 weights might form multiple orbits

# Another approach: 40 points in the E6 root polytope
# E6 has 72 roots forming a polytope

print("E6 has 72 roots")
print("72 = 40 + 32 possible decomposition?")
print("Or: 72 / 2 = 36 (pairs {r, -r}), not 40")

# =============================================================================
# PART 8: THE RECTIFIED SIMPLEX CONNECTION
# =============================================================================

print("\n" + "=" * 70)
print("PART 8: 40 AND THE RECTIFIED SIMPLEX")
print("=" * 70)

print(
    """
40 appears in polytope theory:
  - Rectified 8-simplex has 36 vertices (not 40)
  - 4-rectified 8-simplex (different rectification) might have 40

Actually, let's count:
  - n-simplex has n+1 vertices
  - Rectified n-simplex has C(n+1, 2) = n(n+1)/2 vertices

For n=8: C(9,2) = 36, not 40.

What about:
  - 40 = C(9, 2) + 4?
  - 40 = C(5,2) × 4? = 10 × 4 = 40 ✓

Hmm, 40 = 10 × 4 suggests a product structure.
"""
)

print(f"C(5,2) × 4 = {10 * 4} = 40")
print(f"This could relate to: 10 edges of a 4-simplex × 4 'something'")

# =============================================================================
# PART 9: THE KEY REALIZATION - 40 AS AN E8/E6 QUOTIENT
# =============================================================================

print("\n" + "=" * 70)
print("PART 9: 40 AS A QUOTIENT STRUCTURE")
print("=" * 70)

print(
    """
KEY INSIGHT:

The 40 isotropic lines are the orbits of Sp(4,3) on GF(3)^4 / lines.
Equivalently, they are a QUOTIENT structure.

In the E8 ↔ W33 correspondence:
  - 240 E8 roots correspond to 240 W33 edges
  - The 40 W33 vertices are a COARSER structure

Relationship:
  240 edges / (edges per vertex) = 240 / 12 × 2 = 240 / 6 = 40

Wait, that's not right either. Let me reconsider.

Each W33 vertex is incident to 12 edges.
Total incidences = 40 × 12 = 480 = 2 × 240 (since each edge has 2 endpoints).

So the 40 vertices are determined by how the 240 edges "cluster".
The 40 W33 vertices represent a PARTITION of E8 roots into 6 groups of 40?
No, 240/40 = 6, so it's more like each vertex picks out 6 roots somehow.
"""
)

# Actually, each vertex is incident to 12 edges (degree 12)
# So 40 vertices, each associated with 12 edges
# But edges are counted twice (once per endpoint)
# So there's a 40:240 structure that's 1:12 locally but 1:6 globally

print(f"\n240 / 40 = {240 / 40} = 6")
print(f"degree = 12, so each vertex touches 12 edges")
print(f"12 = 2 × 6, accounting for double-counting")

# =============================================================================
# PART 10: SYNTHESIS
# =============================================================================

print("\n" + "=" * 70)
print("PART 10: SYNTHESIS - THE 40 ↔ 40 MAP")
print("=" * 70)

print(
    """
╔══════════════════════════════════════════════════════════════════════╗
║              THE 40 VERTICES: WHERE THEY LIVE IN E8                  ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  W33 SIDE:                                                           ║
║    40 isotropic lines in GF(3)^4 under symplectic form ω             ║
║    Acted on transitively by Sp(4,3) ≅ W(E6)                          ║
║                                                                      ║
║  E8 SIDE:                                                            ║
║    The 40 vertices correspond to a W(E6)-orbit in E8 structure       ║
║                                                                      ║
║    CANDIDATE: 40 = some orbit of W(E6) acting on E8 data             ║
║                                                                      ║
║    Specifically: W(E6) ⊂ W(E8) acts on 240 E8 roots.                 ║
║    Under this action, roots partition into orbits.                   ║
║    If there's an orbit of size 40, that's our correspondence!        ║
║                                                                      ║
║    But wait: W(E6) is a MAXIMAL subgroup of W(E8) index              ║
║    [W(E8) : W(E6)] = 13440 = 240 × 56                                ║
║                                                                      ║
║    W(E6) action on 240 roots:                                        ║
║    - Cannot be transitive (since 240 > |W(E6)|/|stabilizer|)         ║
║    - Must decompose into orbits                                      ║
║                                                                      ║
║    Possible orbit sizes: divisors of 240 that divide |W(E6)|         ║
║    40 divides 51840? 51840/40 = 1296 ✓                               ║
║    So orbits of size 40 are possible!                                ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
"""
)

# Check if 40 divides |W(E6)|
print(f"\n|W(E6)| / 40 = {51840 // 40} = 1296")
print(f"51840 mod 40 = {51840 % 40}")
print(f"So 40 | |W(E6)| ✓")

# This means W(E6) could have an orbit of size 40 on some set.
# If it acts on the 240 E8 roots, the orbits depend on the embedding.

print(
    f"""
CONCLUSION:

The 40 W33 vertices correspond to a 40-element orbit of W(E6) acting
on some E8 structure.

Most likely: The 40 vertices represent 40 "directions" in the E8
root system, with each direction containing 6 pairs of roots (12 total
half-roots, corresponding to the degree 12 in W33).

The bijection 40 ↔ 40 underlies and generates the bijection 240 ↔ 240.

NEXT: Explicitly compute W(E6) orbits on E8 roots to verify.
"""
)
