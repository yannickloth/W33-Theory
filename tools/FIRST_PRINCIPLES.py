#!/usr/bin/env python3
"""
THE DEEP STRUCTURE: WHY 240 = 240 AND 51840 = 51840

Let me approach this from FIRST PRINCIPLES.
What is the ACTUAL mathematical relationship?
"""

from collections import defaultdict
from fractions import Fraction
from itertools import combinations, product

import numpy as np

print("=" * 80)
print("THE MATHEMATICAL RELATIONSHIP: FIRST PRINCIPLES")
print("=" * 80)

# =============================================================================
# THE TWO OBJECTS
# =============================================================================

print(
    """
OBJECT 1: W33 - The Symplectic Polar Graph W(3,3)

    W(3,3) = polar graph of W₃(3) = symplectic polar space

    Vertices: 40 = (3⁴ - 1)/(3 - 1) = points in PG(3,3)
    Edges: 240 = isotropic pairs (commuting Paulis)

    This is SRG(40, 12, 2, 4)

OBJECT 2: E8 - The Exceptional Lie Algebra

    Roots: 240
    Weyl group W(E8): order 696729600

    Subgroup W(E6): order 51840

OBJECT 3: Sp(4,3) - Symplectic Group over F_3

    |Sp(4,3)| = 51840

    This is the automorphism group of W33!

THE COINCIDENCES:
    1. |Edges(W33)| = |Roots(E8)| = 240
    2. |Aut(W33)| = |Sp(4,3)| = |W(E6)| = 51840
"""
)

# =============================================================================
# COMPUTING THESE NUMBERS FROM FIRST PRINCIPLES
# =============================================================================

print("\n" + "=" * 80)
print("COMPUTING THE NUMBERS")
print("=" * 80)

# |Sp(4,3)|
# General formula: |Sp(2n,q)| = q^(n²) × ∏_{i=1}^{n} (q^(2i) - 1)
# For n=2, q=3:
# |Sp(4,3)| = 3^4 × (3² - 1) × (3⁴ - 1) = 81 × 8 × 80 = 51840

sp43 = 3**4 * (3**2 - 1) * (3**4 - 1)
print(f"|Sp(4,3)| = 3⁴ × (3²-1) × (3⁴-1) = 81 × 8 × 80 = {sp43}")

# |W(E6)|
# W(E6) = Sp(4,3).2  (almost simple, contains Sp(4,3) with index 2... wait)
# Actually: |W(E6)| = 2⁷ × 3⁴ × 5 = 51840

we6 = 2**7 * 3**4 * 5
print(f"|W(E6)| = 2⁷ × 3⁴ × 5 = {2**7} × {3**4} × 5 = {we6}")

# These are EQUAL: 51840 = 51840
print(f"\n|Sp(4,3)| = {sp43}")
print(f"|W(E6)| = {we6}")
print(f"Equal? {sp43 == we6}")


# Factor both
def factor(n):
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


print(f"\nPrime factorization of 51840:")
print(f"  {factor(51840)}")
print(f"  = 2⁷ × 3⁴ × 5")

# =============================================================================
# WHY ARE THEY EQUAL?
# =============================================================================

print("\n" + "=" * 80)
print("WHY ARE |Sp(4,3)| AND |W(E6)| EQUAL?")
print("=" * 80)

print(
    """
This is NOT a coincidence. There is a deep theorem:

THEOREM (CLASSICAL):
    The Weyl group W(E6) is isomorphic to the automorphism group
    of the 27-line configuration on a cubic surface.

    This group is PSp(4,3).2 = Sp(4,3)/Z(Sp(4,3)) extended.

More precisely:
    |W(E6)| = |Sp(4,3)| = 51840

    But W(E6) is NOT isomorphic to Sp(4,3).
    They have the same ORDER but different STRUCTURE.

    W(E6) ≅ O(6,2)⁺ (orthogonal group over F_2)
    W(E6) contains Sp(4,3) as a subgroup of index 2?

Actually, let me check the group theory more carefully...
"""
)

# The exact relationship:
# W(E6) ≅ SO(5,3) ≅ PSp(4,3):2
# This means W(E6) has a normal subgroup of index 2 isomorphic to PSp(4,3)

# |PSp(4,3)| = |Sp(4,3)| / 2 = 25920
psp43 = sp43 // 2
print(f"|PSp(4,3)| = |Sp(4,3)|/2 = {psp43}")
print(f"|W(E6)| = 2 × |PSp(4,3)| = {2 * psp43}")

# So W(E6) ≅ PSp(4,3).2 (an extension of PSp(4,3) by Z_2)
# The full group Sp(4,3) has center of order 2
# PSp(4,3) = Sp(4,3) / Z(Sp(4,3))

# =============================================================================
# THE 240 EDGES / 240 ROOTS
# =============================================================================

print("\n" + "=" * 80)
print("WHY 240 = 240?")
print("=" * 80)

print(
    """
The number 240 appearing in both places:

W33:
    40 vertices, each with degree 12
    Sum of degrees = 40 × 12 = 480 = 2 × (# edges)
    # edges = 480 / 2 = 240

E8:
    dim(E8) = 248 = 240 + 8
    240 roots + 8 Cartan generators

    The 240 roots are: the minimal vectors of the E8 lattice

Is there a STRUCTURAL connection?
"""
)


# Count edges in W33
def symplectic_form(v1, v2):
    return (v1[0] * v2[1] - v1[1] * v2[0] + v1[2] * v2[3] - v1[3] * v2[2]) % 3


def get_projective_points():
    points = []
    seen = set()
    for vec in product(range(3), repeat=4):
        if vec == (0, 0, 0, 0):
            continue
        v = list(vec)
        for i in range(4):
            if v[i] != 0:
                inv = pow(v[i], -1, 3)
                v = tuple((x * inv) % 3 for x in v)
                break
        if v not in seen:
            seen.add(v)
            points.append(v)
    return points


vertices = get_projective_points()
edges = [
    (i, j)
    for i in range(40)
    for j in range(i + 1, 40)
    if symplectic_form(vertices[i], vertices[j]) == 0
]

print(f"W33 edges computed: {len(edges)}")

# =============================================================================
# THE KEY: ORBIT-STABILIZER
# =============================================================================

print("\n" + "=" * 80)
print("THE ORBIT-STABILIZER RELATIONSHIP")
print("=" * 80)

print(
    """
Sp(4,3) acts on PG(3,3) preserving the symplectic form.
It acts on edges (isotropic pairs) transitively.

So: |Sp(4,3)| = |Orbit| × |Stabilizer|
    51840 = 240 × |Stab(edge)|
    |Stab(edge)| = 51840 / 240 = 216

Let's verify this makes sense.
"""
)

stab_size = 51840 // 240
print(f"Stabilizer of an edge in Sp(4,3): |Stab| = 51840/240 = {stab_size}")
print(f"Factor: {factor(stab_size)} = 2³ × 3³ = {2**3 * 3**3}")

# For E8:
print(f"\nFor E8 roots under W(E8):")
print(f"|W(E8)| = {696729600}")
print(f"|Roots| = 240")
print(f"|Stab(root)| = {696729600 // 240} = {factor(696729600 // 240)}")

# W(E7) is the stabilizer of a root in W(E8)
we7 = 2**10 * 3**4 * 5 * 7
print(f"|W(E7)| = 2^10 × 3^4 × 5 × 7 = {we7}")
print(f"Check: |W(E8)|/|W(E7)| = {696729600 // we7}")

# So the stabilizer of a root in W(E8) is NOT W(E7)...
# Actually roots come in pairs (α, -α), so orbit size might be different

# =============================================================================
# THE ACTUAL DEEP THEOREM
# =============================================================================

print("\n" + "=" * 80)
print("THE DEEP THEOREM")
print("=" * 80)

print(
    """
THEOREM (KNOWN):
    The Weyl group W(E6) is isomorphic to the orthogonal group O⁻(6,2).

    O⁻(6,2) acts on a 6-dimensional space over F_2 with a quadratic form
    of minus type.

    The 27 singular points of this quadric correspond to the 27 lines
    on a cubic surface.

    The 27 weights of the fundamental 27-rep of E6 also have this structure!

CONNECTION TO Sp(4,3):
    The isometry group of PG(3,3) with symplectic form is Sp(4,3).

    There is a classical isomorphism:
        PSp(4,3) ≅ PSU(4,2) ≅ subgroup of W(E6)

    The full W(E6) is PSp(4,3):2.

THE 240 CONNECTION:
    W33 is the symplectic polar graph over F_3.
    E8 lattice is related to the Gosset lattice.
    Both involve the same underlying combinatorics!

    Specifically: the "40 lines" in W33 correspond to some
    structure in the E8 root system via the E6 connection.
"""
)

# =============================================================================
# WHAT WE CAN ACTUALLY PROVE
# =============================================================================

print("\n" + "=" * 80)
print("WHAT WE CAN PROVE RIGOROUSLY")
print("=" * 80)

print(
    """
✓ PROVEN:
    1. |Sp(4,3)| = |W(E6)| = 51840
       (Direct calculation, both = 2⁷ × 3⁴ × 5)

    2. |Edges(W33)| = |Roots(E8)| = 240
       (Direct construction)

    3. Sp(4,3) acts transitively on edges of W33
       (Classical result in finite geometry)

    4. W(E8) acts transitively on roots of E8
       (Standard Lie theory)

? CONJECTURED / NEEDS PROOF:
    5. There exists an equivariant bijection φ: Edges(W33) → Roots(E8)
       such that the Sp(4,3) action corresponds to W(E6) action

    6. This bijection respects additional structure
       (e.g., 40 lines ↔ some 6-root structures)

✗ NOT PROVEN:
    7. This structure implies anything about physics
    8. Coupling constants, masses, etc. follow from geometry
"""
)

# =============================================================================
# THE MATHEMATICAL CONTENT
# =============================================================================

print("\n" + "=" * 80)
print("THE MATHEMATICAL CONTENT")
print("=" * 80)

print(
    """
The relationship between Sp(4,3), W(E6), and the 27 lines on a cubic surface
is CLASSICAL and WELL-KNOWN in algebraic geometry.

What we have observed:
    - The symplectic polar graph W33 has 240 edges
    - E8 has 240 roots
    - Both have related symmetry groups of order 51840

What this MIGHT mean:
    - There's a deeper geometric structure connecting quantum observables
      (2-qutrit Paulis → W33) to exceptional Lie algebras (E8)
    - The "27 lines" structure appears in both:
        * E6 has a 27-dimensional representation
        * The cubic surface has 27 lines
        * PG(3,3) geometry is related

What this DOES NOT mean (yet):
    - We can derive physics from geometry
    - The Standard Model "emerges" from this structure
    - Coupling constants have geometric meaning

THE HONEST CONCLUSION:
    The numerical coincidence 240 = 240 and 51840 = 51840 is REAL
    and has deep mathematical content.

    But we have NOT established a CAUSAL connection to physics.

    The mathematical question (is there an equivariant bijection?)
    is a well-posed RESEARCH PROBLEM, not a solved theorem.
"""
)

# =============================================================================
# FINAL NUMBERS
# =============================================================================

print("\n" + "=" * 80)
print("SUMMARY OF KEY NUMBERS")
print("=" * 80)

print(
    f"""
SYMPLECTIC GEOMETRY (F_3):
    PG(3,3) points:     40
    W33 vertices:       40
    W33 edges:          240
    W33 4-cliques:      40
    |Sp(4,3)|:          51840
    Degree in W33:      12
    λ (adjacent):       2
    μ (non-adjacent):   4

E8 LIE ALGEBRA:
    dim(E8):            248
    rank(E8):           8
    roots:              240
    |W(E8)|:            696729600
    |W(E6)|:            51840
    Coxeter number:     30

SHARED NUMBERS:
    240 = 240           ← edges / roots
    51840 = 51840       ← |Sp(4,3)| / |W(E6)|
    40 = 40             ← vertices = 4-cliques (self-dual)

DERIVED:
    51840 / 240 = 216   (stabilizer size in both cases)
    240 / 40 = 6        (edges per line = C(4,2))

PRIME FACTORIZATIONS:
    240 = 2⁴ × 3 × 5
    51840 = 2⁷ × 3⁴ × 5
    40 = 2³ × 5
    216 = 2³ × 3³
"""
)

for name, num in [("240", 240), ("51840", 51840), ("40", 40), ("216", 216)]:
    print(f"    {name} = {factor(num)}")
