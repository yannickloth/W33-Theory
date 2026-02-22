#!/usr/bin/env python3
"""
THE 40 PARTITION: A Different Approach

We need 40 groups of 6 roots that PARTITION all 240 E8 roots.
Total 6-cliques in E8 graph ≈ 2.9 million - these don't partition!

New idea: Look for a partition based on COORDINATES, not graph structure.
"""

from collections import defaultdict
from itertools import combinations, product

import numpy as np

print("=" * 80)
print("FINDING THE 40-FOLD PARTITION OF E8 ROOTS")
print("=" * 80)

# =============================================================================
# E8 ROOT SYSTEM
# =============================================================================


def construct_e8_roots():
    roots = []
    # D8 part: ±e_i ± e_j (112 roots)
    for i in range(8):
        for j in range(i + 1, 8):
            for s1, s2 in product([1, -1], repeat=2):
                r = [0] * 8
                r[i], r[j] = s1, s2
                roots.append(tuple(r))
    # Spinor part: (±1/2)^8 with even # of minus signs (128 roots)
    for signs in product([1, -1], repeat=8):
        if signs.count(-1) % 2 == 0:
            roots.append(tuple(s * 0.5 for s in signs))
    return roots


e8_roots = construct_e8_roots()
d8_roots = [r for r in e8_roots if all(x == int(x) for x in r)]  # 112
spinor_roots = [r for r in e8_roots if any(x != int(x) for x in r)]  # 128

print(f"E8: {len(e8_roots)} roots = {len(d8_roots)} D8 + {len(spinor_roots)} spinor")

# =============================================================================
# PARTITION D8 ROOTS (112 = 28 × 4? or 112/6 = 18.67 - doesn't divide!)
# =============================================================================

print("\n" + "=" * 80)
print("ANALYZING ROOT STRUCTURE")
print("=" * 80)

print(
    f"""
The D8 roots are ±eᵢ ± eⱼ for i < j.
There are C(8,2) = 28 coordinate pairs.
Each pair gives 4 roots: +eᵢ+eⱼ, +eᵢ-eⱼ, -eᵢ+eⱼ, -eᵢ-eⱼ

112 = 28 × 4

The spinor roots are (±½)⁸ with even # of minus signs.
128 = 2⁷

Neither 112 nor 128 is divisible by 6!
So the 40-fold partition MUST mix D8 and spinor roots!

112 + 128 = 240 = 40 × 6 ✓

But: 112 = 40×2 + 32 = ...
     128 = 40×3 + 8  = ...

Hmm, let's think differently.
"""
)

# =============================================================================
# KEY INSIGHT: THE 40 MUST COME FROM PG(3,3) STRUCTURE
# =============================================================================

print("\n" + "=" * 80)
print("THE PG(3,3) STRUCTURE IN E8")
print("=" * 80)

print(
    """
In W33:
    - 40 = number of points in PG(3,3) = (3⁴-1)/(3-1) = 40
    - 40 = number of lines in W(3,3) (self-dual)

E8 lattice can be constructed via "Construction A" from codes!

The E8 lattice via extended Hamming code H₈:
    E8 = ½(C + 1) ∪ ½C
    where C is the extended [8,4,4] Hamming code over Z/2Z

The Hamming code H₈ has structure related to PG(2,2) = Fano plane.

But PG(3,3) is different - it's over F₃, not F₂.

Alternative: Is there a code over F₃ that gives the same structure?
"""
)

# =============================================================================
# APPROACH: IDENTIFY F_3^4 WITH SOMETHING IN E8
# =============================================================================

print("\n" + "=" * 80)
print("EMBEDDING F₃⁴ INTO E8 LATTICE")
print("=" * 80)

print(
    """
The E8 lattice points include:
    - D8: integer coordinates summing to even
    - Shifted: half-integer coordinates summing to even/odd (specific parity)

F₃⁴ has 81 elements. We need 40 projective points.

Idea: Embed F₃ → Z using 0 → 0, 1 → 1, 2 → -1
Then F₃⁴ → Z⁴ ⊂ Z⁸

Let's see if this creates any structure.
"""
)


def f3_to_z(x):
    """Map F_3 element to integer: 0→0, 1→1, 2→-1"""
    if x == 0:
        return 0
    if x == 1:
        return 1
    return -1


def embed_f3_4_to_z8(v):
    """Embed F_3^4 into Z^8 (first 4 coordinates, rest zero)"""
    return tuple([f3_to_z(x) for x in v] + [0, 0, 0, 0])


# Get the 40 projective points
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


pg_points = get_projective_points()
print(f"PG(3,3) points: {len(pg_points)}")

# Embed them
embedded_points = [embed_f3_4_to_z8(p) for p in pg_points]

# Which of these are E8 roots?
e8_root_set = set(e8_roots)
embedded_in_e8 = [p for p in embedded_points if p in e8_root_set]
print(f"Embedded points that are E8 roots: {len(embedded_in_e8)}")

# Let's check: the embedding might need scaling
# E8 roots have norm² = 2
for p in embedded_points[:5]:
    norm_sq = sum(x**2 for x in p)
    print(f"  {p} → norm² = {norm_sq}")

# Most have norm² = 1 or 2, but we're only using 4 coordinates

# =============================================================================
# DIFFERENT APPROACH: USE FULL 8 COORDINATES
# =============================================================================

print("\n" + "=" * 80)
print("ALTERNATIVE: ENCODE PG(3,3) IN ALL 8 COORDINATES")
print("=" * 80)

print(
    """
PG(3,3) has 40 points. We need to map these to structures that
use all 8 coordinates of E8.

Idea: Use the symplectic form to define pairs/opposites
      Each pair of points (orthogonal under symplectic form)
      becomes an edge in W33, which should map to an E8 root.

Wait - that's the problem we're trying to solve!

Let me try yet another approach: QUOTIENT STRUCTURE.
"""
)

# =============================================================================
# THE QUOTIENT: E8/SOMETHING ≈ 40
# =============================================================================

print("\n" + "=" * 80)
print("QUOTIENT APPROACH")
print("=" * 80)

print(
    """
240 roots / 6 = 40 groups

What's the "6" in E8 root terms?
    - A root and its negative: 2
    - A root and 2 partners: 3
    - Some other structure: 6

In A₂: 6 roots form a hexagon (2 triangles)
In D₄: 24 roots, 24/6 = 4 groups

For E8: Can we find a natural equivalence relation with 6 classes?
"""
)

# Try: Group roots by some modular property
# For D8 roots (±eᵢ ± eⱼ), the pair (i,j) could be the "key"
# 28 pairs × 4 roots/pair = 112

# For spinor roots, group by sign pattern
# 128 patterns with even # of minus signs

# What if we use mod 3 structure?

# =============================================================================
# MOD 3 STRUCTURE ON E8 ROOTS
# =============================================================================

print("\n" + "=" * 80)
print("MOD 3 STRUCTURE")
print("=" * 80)


# For each E8 root, compute something mod 3
def root_mod3_signature(r):
    """Compute a mod-3 signature of a root."""
    # For integer roots: coordinates are 0, ±1 → mod 3: 0, 1, 2
    # For half-integer: coordinates are ±0.5 → 2*(±0.5) = ±1 → mod 3: 1, 2

    # Double the root to make everything integer
    doubled = tuple(int(2 * x) for x in r)
    # Now mod 3
    mod3 = tuple(x % 3 for x in doubled)
    return mod3


mod3_classes = defaultdict(list)
for i, r in enumerate(e8_roots):
    sig = root_mod3_signature(r)
    mod3_classes[sig].append(i)

print(f"Number of distinct mod-3 signatures: {len(mod3_classes)}")

# How are roots distributed?
class_sizes = sorted([len(v) for v in mod3_classes.values()], reverse=True)
print(f"Class sizes: {class_sizes[:20]}...")

# If there are 40 classes with 6 roots each, we're done!
if len(mod3_classes) == 40 and all(len(v) == 6 for v in mod3_classes.values()):
    print("*** PERFECT 40-FOLD PARTITION FOUND! ***")
else:
    # How many have size 6?
    size_6 = [k for k, v in mod3_classes.items() if len(v) == 6]
    print(f"Classes with exactly 6 roots: {len(size_6)}")

# =============================================================================
# THE 40 = 4 × 10 STRUCTURE
# =============================================================================

print("\n" + "=" * 80)
print("FACTORING 40")
print("=" * 80)

print(
    """
40 = 8 × 5 = 4 × 10 = 2 × 20 = 2 × 4 × 5

In E8:
    - 8 = rank
    - 5 = Coxeter number of A₄ (part of E8)

In W33:
    - 40 = 4 × 10 = each vertex in 4 lines, each line has 4 vertices
    - 40 = (3⁴ - 1)/(3 - 1) = projective count

The self-duality (40 points = 40 lines) is key!
"""
)

# =============================================================================
# WHAT WE'VE LEARNED
# =============================================================================

print("\n" + "=" * 80)
print("CONCLUSION")
print("=" * 80)

print(
    f"""
STRUCTURE ANALYSIS:

1. E8 roots don't naturally partition into 40 groups of 6 via:
   - Mod 3 signatures: {len(mod3_classes)} classes, not 40
   - Root graph cliques: ~2.9 million 6-cliques, far too many
   - A1×A1×A1 systems: 37,800 systems with heavy overlap

2. The D8 (112) and spinor (128) parts don't separately give multiples of 6:
   - 112 = 40×2 + 32
   - 128 = 40×3 + 8
   - Mixed: must interleave

3. The embedding F₃⁴ → Z⁸ doesn't directly map to E8 roots

4. The parallel structure (40 lines in W33 ↔ 40 groups in E8) is NOT obvious

IMPLICATIONS:

The numerical coincidence 240 = 240 might be:
   (a) A DIFFERENT kind of correspondence (not a partition)
   (b) Requires sophisticated math (weight lattice structure, etc.)
   (c) Simply a coincidence without deeper structure

Without finding the explicit 40-fold partition, we cannot claim
a "natural bijection" between W33 edges and E8 roots.
"""
)

# =============================================================================
# ONE MORE TRY: THE WEIGHT LATTICE
# =============================================================================

print("\n" + "=" * 80)
print("FINAL ATTEMPT: WEIGHT LATTICE")
print("=" * 80)

print(
    """
E8 = E8*, so the root lattice equals the weight lattice.

For other simple Lie algebras, roots and weights are different.
E6 has a weight lattice that's NOT equal to its root lattice.

The 27 lines on a cubic surface correspond to the 27 weights of E6.
These have stabilizer structure related to the 27!

Can we find 40 special objects in the E8 weight structure?

E8 has no fundamental representation of dimension 40.
(Dimensions: 248, 3875, 147250, ...)

This suggests 40 is NOT a natural number in E8 representation theory.
"""
)

# =============================================================================
# FINAL ANSWER
# =============================================================================

print("\n" + "=" * 80)
print("FINAL ANSWER")
print("=" * 80)

print(
    """
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║  THE BIJECTION φ: Edges(W33) → Roots(E8) HAS NOT BEEN CONSTRUCTED.           ║
║                                                                               ║
║  The numerical coincidence 240 = 240 is REAL but its MEANING is UNKNOWN.     ║
║                                                                               ║
║  The group order coincidence |Sp(4,3)| = |W(E6)| = 51840 is REAL             ║
║  and has deep mathematical content (both related to 27-line structure).       ║
║                                                                               ║
║  But we have NOT shown that:                                                  ║
║    1. There's a natural bijection respecting some structure                   ║
║    2. The 40 lines of W33 correspond to 40 objects in E8                     ║
║    3. This has anything to do with physics                                    ║
║                                                                               ║
║  This is where we are. This is the honest truth.                             ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""
)
