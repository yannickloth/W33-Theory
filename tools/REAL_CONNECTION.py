#!/usr/bin/env python3
"""
REAL_CONNECTION.py - Building the ACTUAL mathematical connection

KEY INSIGHT FROM RESEARCH:
==========================

The W(E6) group (order 51,840) acts on:
1. The 27 lines on a cubic surface (as permutations)
2. The E6 root system (as reflections)
3. The 240 E8 roots decompose under E6 × SU(3)

CRITICAL FACTS:
- E8 adjoint (248) decomposes under E6 × SU(3) as:
  (78,1) + (1,8) + (27,3) + (27̄,3̄)
  = 78 + 8 + 81 + 81 = 248

- The 240 E8 ROOTS decompose as:
  72 roots of E6 + 6 roots of SU(3) + 81 + 81 = 240

Actually, let's count more carefully:
E6 has 72 roots
SU(3) has 6 roots
27×3 = 81 objects
27̄×3̄ = 81 objects
Total: 72 + 6 + 81 + 81 = 240 ✓

So the 240 E8 roots naturally decompose into structures involving 27!

Now, what is Sp(4,3)?
- Sp(4,3) = Symplectic group over F_3 (field with 3 elements)
- |Sp(4,3)| = 51,840 = |W(E6)|
- This is NOT a coincidence - these groups are isomorphic!

The symplectic polar graph W33 comes from Sp(4,3):
- Vertices: Points of the symplectic polar space
- Edges: When points are perpendicular

So the connection is:
  Sp(4,3) ≅ W(E6) (as abstract groups)
  Both act on sets related to E6/E8 geometry

Let me build this properly.
"""

from collections import Counter
from itertools import combinations, product

import numpy as np

print("=" * 70)
print("BUILDING THE REAL MATHEMATICAL CONNECTION")
print("=" * 70)

# =============================================================================
# PART 1: THE E8 DECOMPOSITION UNDER E6
# =============================================================================
print("\n" + "=" * 70)
print("PART 1: E8 ROOTS AND THEIR E6 DECOMPOSITION")
print("=" * 70)

# E8 roots: 240 = 112 (D8) + 128 (spinor)
# Generate all 240 E8 roots
e8_roots = []

# D8 roots: all permutations of (±1, ±1, 0, 0, 0, 0, 0, 0)
for i in range(8):
    for j in range(i + 1, 8):
        for s1 in [1, -1]:
            for s2 in [1, -1]:
                root = [0] * 8
                root[i] = s1
                root[j] = s2
                e8_roots.append(tuple(root))

# Spinor roots: (±1/2, ±1/2, ..., ±1/2) with even number of minus signs
for signs in product([1, -1], repeat=8):
    if sum(1 for s in signs if s == -1) % 2 == 0:
        root = tuple(s / 2 for s in signs)
        e8_roots.append(root)

print(f"Total E8 roots: {len(e8_roots)}")
print(f"  D8 roots: {len([r for r in e8_roots if all(x in [0, 1, -1] for x in r)])}")
print(f"  Spinor roots: {len([r for r in e8_roots if all(abs(x) == 0.5 for x in r)])}")

# =============================================================================
# E6 is embedded in E8 by taking roots where last 3 coordinates satisfy:
# sum of last 3 = 0 (they're equal or specific patterns)
# =============================================================================


def get_e6_type(root):
    """
    Classify E8 root by its E6×SU(3) decomposition.

    Under E6×SU(3), the E8 root system decomposes as:
    - 72 roots of E6 (where last 3 coords are (0,0,0), (-1/2,-1/2,-1/2), or (1/2,1/2,1/2))
    - 6 roots of SU(3) (first 5 coords are 0)
    - 81 roots in (27,3)
    - 81 roots in (27̄,3̄)
    """
    r = np.array(root)
    first5 = r[:5]
    last3 = r[5:]

    # Check if it's an E6 root (last 3 coords sum to 0 in specific patterns)
    last3_sum = sum(last3)
    last3_set = tuple(sorted(last3))

    # E6 roots: last 3 coordinates are all equal
    if last3[0] == last3[1] == last3[2]:
        val = last3[0]
        if val in [0, 0.5, -0.5]:
            if not np.allclose(first5, 0):
                return "E6"
            else:
                # Pure Cartan direction
                return "Cartan"

    # SU(3) roots: first 5 coords are 0, last 3 are permutations of (1, -1, 0)
    if np.allclose(first5, 0):
        if set(last3) == {0, 1, -1} or (abs(sum(last3)) < 0.01 and max(abs(last3)) > 0):
            return "SU3"

    # Classify by last 3 pattern for the (27,3) and (27̄,3̄)
    # (27,3): permutations of (-1,0,0), (-1/2,1/2,1/2), (0,1,1)
    # (27̄,3̄): permutations of (1,0,0), (1/2,-1/2,-1/2), (0,-1,-1)

    last3_patterns_27_3 = [{-1, 0, 0}, {-0.5, 0.5, 0.5}]

    # Check for (27,3) type
    s = sum(last3)
    if s < 0:
        return "27×3"
    elif s > 0:
        return "27̄×3̄"
    else:
        # sum = 0
        if np.allclose(first5, 0):
            return "SU3"
        else:
            return "E6"


# Classify all roots
classifications = [get_e6_type(r) for r in e8_roots]
counts = Counter(classifications)

print("\nE8 root classification under E6×SU(3):")
for typ, cnt in sorted(counts.items()):
    print(f"  {typ}: {cnt}")

# =============================================================================
# PART 2: THE SYMPLECTIC POLAR GRAPH W33
# =============================================================================
print("\n" + "=" * 70)
print("PART 2: BUILDING THE SYMPLECTIC POLAR GRAPH W33")
print("=" * 70)

# W33 is the symplectic polar graph from the symplectic space V = F_3^4
# with the standard symplectic form ω(u,v) = u^T J v mod 3
# where J = [[0,I],[-I,0]]

# A point in projective symplectic polar space corresponds to
# an isotropic 1-dimensional subspace (isotropic means ω(v,v) = 0 for all v in it)

# In F_3^4, every nonzero vector v has ω(v,v) = 0 (since we're mod 3 and symplectic form is skew)
# So we need totally isotropic subspaces

# Actually, for the polar graph:
# - Vertices: isotropic points (1-dim totally isotropic subspaces)
# - Edges: when the points are perpendicular (their span is totally isotropic)

# Let's build it properly using F_3^4

F3 = [0, 1, 2]  # Field with 3 elements


# Symplectic form: ω(u,v) = u0*v2 - u2*v0 + u1*v3 - u3*v1 (mod 3)
def symplectic_form(u, v):
    """Standard symplectic form on F_3^4."""
    return (u[0] * v[2] - u[2] * v[0] + u[1] * v[3] - u[3] * v[1]) % 3


# An isotropic point is a nonzero vector v with ω(v,v) = 0
# For symplectic form, ω(v,v) = 0 always (skew-symmetric)

# Generate all nonzero vectors in F_3^4
vectors = []
for v in product(F3, repeat=4):
    if v != (0, 0, 0, 0):
        vectors.append(v)

print(f"Nonzero vectors in F_3^4: {len(vectors)}")  # Should be 80

# Two vectors represent the same projective point if one is a scalar multiple of the other
# In F_3, scalars are 1 and 2 (0 doesn't give a point)


def canonical_rep(v):
    """Get canonical representative of projective point."""
    # Find first nonzero entry, scale so it's 1
    for i, x in enumerate(v):
        if x != 0:
            inv = 1 if x == 1 else 2  # 2 * 2 = 4 ≡ 1 mod 3
            return tuple((inv * c) % 3 for c in v)
    return v


# Get projective points
proj_points = set()
for v in vectors:
    proj_points.add(canonical_rep(v))

points = list(proj_points)
print(f"Projective points: {len(points)}")  # Should be 40

# Build adjacency: two points are adjacent if they're perpendicular
# i.e., if ω(u, v) = 0 (mod 3)
adj = {i: set() for i in range(len(points))}

for i, p1 in enumerate(points):
    for j, p2 in enumerate(points):
        if i < j:
            if symplectic_form(p1, p2) == 0:
                adj[i].add(j)
                adj[j].add(i)

# Count degrees
degrees = [len(adj[i]) for i in range(len(points))]
print(f"Degree distribution: {Counter(degrees)}")
print(f"This should be degree 12 for all vertices (SRG(40, 12, 2, 4))")

# Count edges
num_edges = sum(degrees) // 2
print(f"Total edges: {num_edges}")  # Should be 240

# =============================================================================
# PART 3: THE KEY CONNECTION - 27 LINES AND W33
# =============================================================================
print("\n" + "=" * 70)
print("PART 3: THE KEY MATHEMATICAL INSIGHT")
print("=" * 70)

print(
    """
THE CRITICAL CONNECTION:
========================

1. |Sp(4,3)| = 51,840 = |W(E6)|
   This is NOT a coincidence - these groups are isomorphic!

   Sp(4,3) ≅ W(E6)

2. W33 has 40 vertices, 240 edges
   - Sp(4,3) acts transitively on vertices
   - Sp(4,3) acts transitively on edges

3. E6 has:
   - 72 roots (acted on by W(E6))
   - A 27-dimensional fundamental representation
   - The 27 corresponds to the 27 lines on a cubic surface

4. The 240 E8 roots under E6×SU(3) decompose as:
   72 (E6 roots) + 6 (SU(3)) + 81 (27×3) + 81 (27̄×3̄) = 240

5. HERE'S THE KEY:
   - The 240 edges of W33 correspond naturally to the 240 E8 roots
   - The correspondence respects the group action:
     Sp(4,3) on W33 edges ↔ W(E6) on suitable E8 structure
"""
)

# =============================================================================
# PART 4: VERIFY THE GROUP ORDER
# =============================================================================
print("\n" + "=" * 70)
print("PART 4: VERIFYING |Sp(4,3)| = |W(E6)| = 51,840")
print("=" * 70)

# |Sp(2n, q)| = q^(n²) × ∏_{i=1}^{n} (q^(2i) - 1)
# For Sp(4,3) = Sp(2×2, 3): n=2, q=3
# |Sp(4,3)| = 3^4 × (3^2 - 1) × (3^4 - 1) = 81 × 8 × 80 = 51840

n = 2
q = 3
sp_order = q ** (n * n)
for i in range(1, n + 1):
    sp_order *= q ** (2 * i) - 1

print(f"|Sp(4,3)| = 3^4 × (9-1) × (81-1)")
print(f"         = 81 × 8 × 80 = {sp_order}")

# |W(E6)| = 51840 = 2^7 × 3^4 × 5
we6_order = 51840
print(f"|W(E6)| = {we6_order}")
print(f"Match: {sp_order == we6_order}")


# Factorizations
def factorize(n):
    factors = {}
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors[d] = factors.get(d, 0) + 1
            n //= d
        d += 1
    if n > 1:
        factors[n] = factors.get(n, 0) + 1
    return factors


print(f"\nFactorization: {factorize(51840)}")
print(f"51840 = 2^7 × 3^4 × 5")

# =============================================================================
# PART 5: THE ISOMORPHISM Sp(4,3) ≅ W(E6)
# =============================================================================
print("\n" + "=" * 70)
print("PART 5: WHY Sp(4,3) ≅ W(E6)")
print("=" * 70)

print(
    """
THE MATHEMATICAL FACT:
======================

The group PSp(4,3) = Sp(4,3)/{±I} is isomorphic to O(5,3), the orthogonal
group over F_3.

MORE PRECISELY:
- W(E6) acts on the 27 lines of a cubic surface
- Sp(4,3) acts on the 40 points of the polar space
- These are related through the exceptional isomorphism:

  Sp(4,3) / Z ≅ Ω(5,3) ≅ W(E6) / Z

where Z is the center.

THE 27 LINES AND THE 40 POINTS:
- The 27 lines on a cubic surface
- The 40 points of the Sp(4,3) polar space

These are related through:
- The dual of the 27-line configuration has 27 points and 45 lines
- Blowing down to P^2 gives 6 points
- The 40 points of W33 relate to a different but compatible structure

THE DEFINITIVE CONNECTION:
The group W(E6) = Sp(4,3) acts on both:
1. The 240 edges of W33 (transitively)
2. Various subsets of the 240 E8 roots

The bijection φ: Edges(W33) → Roots(E8) should be W(E6)-equivariant!
"""
)

# =============================================================================
# PART 6: CONSTRUCT THE EQUIVARIANT BIJECTION
# =============================================================================
print("\n" + "=" * 70)
print("PART 6: THE STRUCTURE OF THE BIJECTION")
print("=" * 70)

# The edges of W33
edges = []
for i in range(len(points)):
    for j in adj[i]:
        if i < j:
            edges.append((i, j))

print(f"Number of W33 edges: {len(edges)}")

# For the bijection, we need to find how W(E6) acts on E8 roots
# Under E6 ⊂ E8, the 240 E8 roots decompose, but W(E6) doesn't
# act transitively on all 240.

# HOWEVER, there's a key insight:
# The 240 roots of E8 correspond to pairs of lines from the 27 lines!

# Number of ordered pairs minus the 27 diagonal: 27×27 - 27 = 702
# But 27×2 + 27×8 = 270... not quite

# Actually, let's think differently:
# E8 = 248 = 78 + 8 + 81 + 81 (under E6 × SU(3))
# Roots: 72 + 6 + 81 + 81 = 240

# The 81 = 27 × 3 suggests:
# - 27 copies (from the 27-dim rep)
# - each appearing 3 times (from the 3-dim SU(3) rep)

print(
    """
INSIGHT: THE 240 = 81 + 81 + 72 + 6 DECOMPOSITION
=================================================

Under E6 × SU(3) ⊂ E8:
- 72 E6 roots
- 6 SU(3) roots
- 81 = 27 × 3 (fundamental E6 rep × fundamental SU(3))
- 81 = 27̄ × 3̄ (dual reps)

This gives 240 objects, and W(E6) acts on:
- The 72 E6 roots (as the Weyl group)
- The 27 appearing in (27,3) (as fundamental rep)
- The 27̄ appearing in (27̄,3̄) (as dual rep)

THE W33 CONNECTION:
- W33 has 40 vertices acted on by Sp(4,3) ≅ W(E6)
- W33 has 240 edges acted on by Sp(4,3) ≅ W(E6)

The action of W(E6) on the 240 E8 roots has orbit structure:
- One orbit of size 72 (E6 roots)
- One orbit of size 6 (SU(3) roots)
- Orbits in the 81s...

But the 240 W33 edges are in a SINGLE ORBIT under Sp(4,3)!

This means: The bijection φ: Edges(W33) → Roots(E8)
           CANNOT be simply W(E6)-equivariant
           (since E8 roots split into orbits)

UNLESS we use a different subgroup!
"""
)

# =============================================================================
# PART 7: THE REAL RESOLUTION
# =============================================================================
print("\n" + "=" * 70)
print("PART 7: THE ACTUAL MATHEMATICAL SITUATION")
print("=" * 70)

print(
    """
THE REAL SITUATION:
==================

1. PROVEN FACTS:
   - |Sp(4,3)| = |W(E6)| = 51,840
   - Both are isomorphic to the same abstract group
   - W33 has 240 edges, E8 has 240 roots

2. BUT:
   - W(E6) acts on 240 E8 roots in MULTIPLE orbits (72 + 6 + ...)
   - Sp(4,3) acts on 240 W33 edges in a SINGLE orbit

   These actions are NOT the same!

3. THE MATHEMATICAL QUESTION:
   Is there SOME bijection φ: Edges(W33) → Roots(E8)?

   Yes, trivially (they have the same cardinality).

   Is there a MEANINGFUL bijection?
   This requires understanding what "meaningful" means.

4. WHAT THE LITERATURE SAYS:
   - The connection between Sp(4,3) and W(E6) is well-known
   - The 27 lines, E6, and cubic surfaces are deeply connected
   - The 40 points of W33 and 27 lines are related through
     the exceptional geometry of E6

5. THE OPEN QUESTION:
   What is the precise geometric relationship between:
   - The 240 edges of W33
   - The 240 roots of E8

   Is it just a numerical coincidence, or is there deeper structure?

CONCLUSION:
===========
The group isomorphism Sp(4,3) ≅ W(E6) is REAL and PROVEN.
The number coincidence 240 = 240 is REAL.
The connection to physics (if any) is UNPROVEN.
"""
)

# =============================================================================
# PART 8: WHAT WE CAN DEFINITIVELY SAY
# =============================================================================
print("\n" + "=" * 70)
print("PART 8: DEFINITIVE STATEMENTS")
print("=" * 70)

print(
    """
WHAT IS MATHEMATICALLY TRUE:
============================

1. Sp(4,3) ≅ W(E6) (group isomorphism)
   |Sp(4,3)| = |W(E6)| = 51,840

2. W33 (symplectic polar graph):
   - 40 vertices (points of symplectic polar space over F_3)
   - 240 edges
   - Strongly regular with parameters (40, 12, 2, 4)
   - Automorphism group contains Sp(4,3)

3. E6 and E8:
   - E6 has 72 roots, dimension 78
   - E8 has 240 roots, dimension 248
   - E6 × SU(3) ⊂ E8 (maximal subgroup)

4. Under E6 × SU(3):
   248 = 78 + 8 + 27×3 + 27̄×3̄
   240 roots = 72 + 6 + 81 + 81

5. The 27-dimensional representation of E6:
   - Corresponds to 27 lines on a cubic surface
   - W(E6) acts on these 27 lines

WHAT IS A CONJECTURE:
=====================
The 240 edges of W33 have a meaningful bijection to the 240 E8 roots
that respects some structure (possibly through the 81+81 decomposition).

WHAT IS UNSUPPORTED:
====================
Any claim that this leads to physics (particle masses, coupling constants).
"""
)
