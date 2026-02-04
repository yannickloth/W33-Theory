#!/usr/bin/env python3
"""
FINAL_EXPLORATION.py

One more attack: What about the FLAGS (vertex-edge pairs)?

W33 has:
- 40 vertices × 12 edges each = 480 flags (with 2-fold overcounting)
- Actually 40 × 12 / 2 × 2 = 480 incidences total

Wait, let's think more carefully about what structures we have.
"""

from collections import Counter

import numpy as np

print("=" * 70)
print("FINAL EXPLORATION: FLAGS AND INCIDENCES")
print("=" * 70)

# W33 Data
print(
    """
W33 COUNTING:
============

W33 = SRG(40, 12, 2, 4)
- 40 vertices
- 240 edges (each vertex in 12 edges, 40×12/2 = 240)
- 40 lines (maximal 4-cliques)

Each vertex is in exactly 4 lines (since it's a generalized quadrangle GQ(3,3))
Each line contains exactly 4 vertices
Total vertex-line incidences: 40 × 4 = 160 = 40 × 4

Each line has C(4,2) = 6 edges
40 lines × 6 edges = 240 edges ✓

COUNTING VERIFICATION:
- Vertex-edge pairs (flags): 40 × 12 = 480
- But each edge has 2 endpoints, so 240 × 2 = 480 ✓

Now let's see if 480 connects to anything in E8...
"""
)

# E8 counting
print("=" * 70)
print("E8 COUNTING")
print("=" * 70)

print(
    """
E8 ROOT SYSTEM:
==============

- 240 roots
- Each root has inner product 1 with exactly 56 others
- Total "adjacent pairs": 240 × 56 / 2 = 6720

Under E6 × SU(3) decomposition:
- 240 = 72 + 6 + 81 + 81 = (E6 roots) + (SU(3) roots) + (27×3) + (27̄×3̄)

The 27 representation of E6:
- 27 weights
- Forms the Schläfli graph

Interesting numbers:
- 27 × 6 = 162 (not 240)
- 27 × 8 = 216 = Schläfli edges
- 40 × 6 = 240 = E8 roots = W33 edges ✓ ← This is the coincidence!

So the mathematical fact is:
|W33 vertices| × |edges per line| = |E8 roots|
40 × 6 = 240
"""
)

print("=" * 70)
print("EXPLORING THE 40 × 6 = 240 STRUCTURE")
print("=" * 70)

print(
    """
W33 PERSPECTIVE:
===============

W33 has 40 maximal 4-cliques (lines).
Each line contains 6 edges.
40 lines × 6 edges per line = 240 edges

This gives a PERFECT PARTITION of the 240 edges into 40 groups of 6.

E8 PERSPECTIVE:
==============

Can we partition E8's 240 roots into 40 groups of 6?

We tried A2 systems (6 roots each) and found only 37 disjoint ones.

But wait - what about a DIFFERENT 6-element structure?

IDEA: What if we use E6's 72 roots differently?

Under E6 × SU(3):
- 72 E6 roots
- 6 SU(3) roots
- 81 from (27, 3)
- 81 from (27̄, 3̄)

The SU(3) has only 6 roots!
72 = 12 × 6 = 12 copies of something?
81 = 27 × 3 = 27 copies of 3-element sets?
"""
)

# Let's analyze E6 roots
print("=" * 70)
print("ANALYZING E6 ROOT STRUCTURE")
print("=" * 70)


def build_e6_roots_in_e8():
    """
    Build E6 roots within E8.
    E6 ⊂ E8 can be embedded in various ways.
    Standard: E6 roots are E8 roots orthogonal to a certain A2.
    """
    # E8 roots
    roots = []

    # Type 1: ±e_i ± e_j
    for i in range(8):
        for j in range(i + 1, 8):
            for si in [1, -1]:
                for sj in [1, -1]:
                    r = np.zeros(8)
                    r[i] = si
                    r[j] = sj
                    roots.append(r)

    # Type 2: half-integer with even minus signs
    for bits in range(256):
        signs = [1 if (bits >> i) & 1 == 0 else -1 for i in range(8)]
        if sum(1 for s in signs if s == -1) % 2 == 0:
            r = 0.5 * np.array(signs)
            roots.append(r)

    roots = np.array(roots)

    # E6 can be identified as roots with certain tail coordinates
    # One standard embedding: E6 roots have x_7 + x_8 = 0
    # Let's check this

    e6_roots = []
    for r in roots:
        if abs(r[6] + r[7]) < 0.01:  # x_7 + x_8 = 0
            e6_roots.append(r)

    return np.array(e6_roots), roots


e6, e8 = build_e6_roots_in_e8()
print(f"E6 roots (with tail constraint): {len(e6)}")
print(f"E8 roots: {len(e8)}")

# Actually for E6 in E8, we need a more careful embedding
# The 72 E6 roots should satisfy specific conditions

print("\nActually, let's verify the 72+6+81+81 decomposition directly...")

# The decomposition under E6 × SU(3) ⊂ E8
# Standard coordinates: let's use the last two components for SU(3)


# Classify E8 roots by their "SU(3) part"
def classify_e8_roots():
    roots = []

    # Type 1: ±e_i ± e_j
    for i in range(8):
        for j in range(i + 1, 8):
            for si in [1, -1]:
                for sj in [1, -1]:
                    r = np.zeros(8)
                    r[i] = si
                    r[j] = sj
                    roots.append(r)

    # Type 2: half-integer
    for bits in range(256):
        signs = [1 if (bits >> i) & 1 == 0 else -1 for i in range(8)]
        if sum(1 for s in signs if s == -1) % 2 == 0:
            r = 0.5 * np.array(signs)
            roots.append(r)

    # The tail (last 2 components) determines the SU(3) weight
    tails = {}
    for r in roots:
        tail = (round(r[6], 2), round(r[7], 2))
        if tail not in tails:
            tails[tail] = []
        tails[tail].append(r)

    return tails


tails = classify_e8_roots()
print("\nClassification by (x_7, x_8) tail:")
for tail, rs in sorted(tails.items()):
    print(f"  {tail}: {len(rs)} roots")

print(f"\nTotal tail types: {len(tails)}")

# Group by SU(3) weight norm
tail_norms = Counter()
for tail, rs in tails.items():
    norm = round(tail[0] ** 2 + tail[1] ** 2, 2)
    tail_norms[norm] += len(rs)

print(f"\nBy tail norm: {tail_norms}")

print("\n" + "=" * 70)
print("KEY OBSERVATION")
print("=" * 70)

print(
    """
The E8 decomposition under E6 × SU(3) is:

tail = (0, 0): should give 72 E6 roots + 6 SU(3) roots? Let's check...
"""
)

zero_tail = tails.get((0.0, 0.0), []) + tails.get((0, 0), [])
print(f"Roots with zero tail: {len(zero_tail)}")

# Find roots with specific tail patterns
su3_tails = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, -1), (-1, 1)]
su3_roots = []
for tail in su3_tails:
    if tail in tails:
        su3_roots.extend(tails[tail])

print(f"\nPure SU(3) roots (unit vectors in last 2): checking...")

# Actually the SU(3) embeds differently. Let's count properly.
# E6 × A2 ⊂ E8 means:
# - E6 roots: 72
# - A2 roots: 6
# - Mixed: 81 + 81

# A cleaner approach: count orbits under E6 action
print("\n" + "=" * 70)
print("FINAL MATHEMATICAL PICTURE")
print("=" * 70)

print(
    """
THE COMPLETE PICTURE
====================

We have established:

1. PROVEN MATHEMATICS:
   - Sp(4,3) ≅ W(E6), both order 51,840
   - E8 → Gosset → Schläfli neighborhood chain
   - Weyl group indices: 240, 56, 27

2. THE 240 = 240 COINCIDENCE:
   - W33: 40 lines × 6 edges = 240 edges
   - E8: 240 roots

   This is NUMERICALLY the same but STRUCTURALLY different.

3. THE OBSTRUCTION:
   - Under W(E6) ≅ Sp(4,3):
     * W33 edges: 1 orbit (transitive action)
     * E8 roots: 4 orbits (72 + 6 + 81 + 81)

   No equivariant bijection possible.

4. WHAT WOULD BE NEEDED:
   - A bijection φ: Edges(W33) → Roots(E8)
   - That respects SOME structure (not W(E6)-equivariance)
   - Perhaps respects the 40×6 factorization?

5. THE OPEN QUESTION:
   - Is there a bijection that sends:
     * Each W33 line (4-clique with 6 edges) →
     * Some 6-element subset of E8 roots?
   - What would those 6-element subsets be?
   - The natural guess (A2 systems) doesn't work (only 37 disjoint)

CONCLUSION:
===========

The W33 ↔ E8 connection through Sp(4,3) ≅ W(E6) is REAL mathematics.

The 240 = 240 coincidence is STRIKING but has no known structural explanation.

If there IS a meaningful bijection, it must NOT be equivariant - it must
exploit some OTHER property we haven't identified.

This remains an OPEN MATHEMATICAL PROBLEM.
"""
)
