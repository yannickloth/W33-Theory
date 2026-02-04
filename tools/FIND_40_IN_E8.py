#!/usr/bin/env python3
"""
FINDING THE 40 STRUCTURES IN E8 THAT PARTITION 240 ROOTS

W33: 40 lines × 6 edges/line = 240 edges
E8:  40 ? × 6 roots/? = 240 roots

What are the 40 structures?
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
    # Spinor part: (±1/2, ..., ±1/2) with even # of minus (128 roots)
    for signs in product([1, -1], repeat=8):
        if signs.count(-1) % 2 == 0:
            roots.append(tuple(s * 0.5 for s in signs))
    return roots


e8_roots = construct_e8_roots()
print(f"E8 roots: {len(e8_roots)}")
print(
    f"  D8 type (integer): {len([r for r in e8_roots if all(x == int(x) for x in r)])}"
)
print(
    f"  Spinor type (half-integer): {len([r for r in e8_roots if any(x != int(x) for x in r)])}"
)

# =============================================================================
# APPROACH 1: PARTITION BY ROOT PAIR (α, -α)
# =============================================================================

print("\n" + "=" * 80)
print("APPROACH 1: ROOT PAIRS")
print("=" * 80)

# Each root α has its negative -α
# 240 roots = 120 pairs
# But 120 ≠ 40 × 6

# What about TRIPLES? (α, -α, something?)
# 240 / 3 = 80, still not 40

# What about groups of 6?
# 240 / 6 = 40 ✓

print(
    """
We need to partition 240 roots into 40 groups of 6.

In E8, roots come in "opposite pairs" (α, -α).
So maybe: 40 groups, each containing 3 pairs = 6 roots.
"""
)

# =============================================================================
# APPROACH 2: LOOK FOR A2 SUBSYSTEMS PROPERLY
# =============================================================================

print("\n" + "=" * 80)
print("APPROACH 2: A2 SUBSYSTEMS (CORRECTED)")
print("=" * 80)


def inner_product(r1, r2):
    return sum(a * b for a, b in zip(r1, r2))


# A2 root system: 6 roots forming a regular hexagon
# α, β, α+β, -α, -β, -(α+β)
# where ⟨α, β⟩ = 1, |α|² = |β|² = 2

# Find all A2 sublattices
a2_systems = []
root_set = set(e8_roots)

for i, alpha in enumerate(e8_roots):
    for j, beta in enumerate(e8_roots):
        if i >= j:
            continue
        if abs(inner_product(alpha, beta) - 1) < 1e-10:  # ⟨α,β⟩ = 1
            # Then α + β should be a root
            gamma = tuple(a + b for a, b in zip(alpha, beta))
            norm_gamma = sum(x**2 for x in gamma)

            if abs(norm_gamma - 2) < 1e-10:  # |α+β|² = 2
                # Check if gamma is actually in the root system
                if gamma in root_set:
                    # Found an A2! The 6 roots are:
                    # α, β, α+β, -α, -β, -(α+β)
                    neg_alpha = tuple(-x for x in alpha)
                    neg_beta = tuple(-x for x in beta)
                    neg_gamma = tuple(-x for x in gamma)

                    a2 = frozenset([alpha, beta, gamma, neg_alpha, neg_beta, neg_gamma])
                    if len(a2) == 6:  # Make sure all 6 are distinct
                        a2_systems.append(a2)

print(f"A2 subsystems found: {len(a2_systems)}")

# Each A2 is found multiple times (once for each choice of α, β among the 6 roots)
# Count unique A2 systems
unique_a2 = set(a2_systems)
print(f"Unique A2 subsystems: {len(unique_a2)}")

# The number of times each A2 is counted:
# Choose 2 roots from 6 with positive inner product
# That's 6 pairs (forming the positive roots of A2)
# So each A2 is counted 6 times

if len(a2_systems) > 0:
    expected_unique = len(a2_systems) // 6
    print(f"Expected unique (if each counted 6 times): {expected_unique}")

# Check if these A2 systems partition the roots
if unique_a2:
    all_roots_in_a2 = set()
    for a2 in unique_a2:
        all_roots_in_a2.update(a2)
    print(f"Roots covered by A2 systems: {len(all_roots_in_a2)}")

    # Do the A2 systems overlap?
    overlapping = 0
    for a2_1, a2_2 in combinations(unique_a2, 2):
        if a2_1 & a2_2:
            overlapping += 1
    print(f"Pairs of overlapping A2 systems: {overlapping}")

# =============================================================================
# APPROACH 3: D4 SUBLATTICES
# =============================================================================

print("\n" + "=" * 80)
print("APPROACH 3: D4 SUBLATTICES")
print("=" * 80)

# D4 has 24 roots
# But 240/24 = 10, not 40

# A3 = D3 has 12 roots
# 240/12 = 20, not 40

# What has 6 roots?
# A2 (6), G2 (12), A1×A1×A1 (6)

print(
    """
Looking for structures with exactly 6 roots...

A2: 6 roots (hexagon)
A1×A1×A1: 6 roots (three orthogonal pairs)

Let's check A1×A1×A1: three mutually orthogonal pairs of roots.
"""
)

# A1×A1×A1: {±α, ±β, ±γ} where α, β, γ are mutually orthogonal
a1x3_systems = []

for i, alpha in enumerate(e8_roots):
    neg_alpha = tuple(-x for x in alpha)

    # Find all β orthogonal to α
    for j, beta in enumerate(e8_roots):
        if j <= i:
            continue
        if abs(inner_product(alpha, beta)) > 1e-10:
            continue  # Not orthogonal

        neg_beta = tuple(-x for x in beta)

        # Find all γ orthogonal to both α and β
        for k, gamma in enumerate(e8_roots):
            if k <= j:
                continue
            if abs(inner_product(alpha, gamma)) > 1e-10:
                continue
            if abs(inner_product(beta, gamma)) > 1e-10:
                continue

            neg_gamma = tuple(-x for x in gamma)

            # Found A1×A1×A1
            system = frozenset([alpha, neg_alpha, beta, neg_beta, gamma, neg_gamma])
            if len(system) == 6:
                a1x3_systems.append(system)

unique_a1x3 = set(a1x3_systems)
print(f"A1×A1×A1 systems found: {len(unique_a1x3)}")

# Check overlap
if unique_a1x3:
    # Does each root appear in the same number of A1×A1×A1 systems?
    root_count = defaultdict(int)
    for sys in unique_a1x3:
        for r in sys:
            root_count[r] += 1

    counts = list(root_count.values())
    print(f"Each root in # of systems: min={min(counts)}, max={max(counts)}")

    if len(set(counts)) == 1:
        c = counts[0]
        print(f"Each root is in exactly {c} A1×A1×A1 systems")
        print(f"240 roots × {c} = {240 * c} incidences")
        print(
            f"{len(unique_a1x3)} systems × 6 roots = {len(unique_a1x3) * 6} incidences"
        )

# =============================================================================
# APPROACH 4: THE KEY - MAXIMAL TORI
# =============================================================================

print("\n" + "=" * 80)
print("APPROACH 4: FRAMES OF ORTHOGONAL ROOTS")
print("=" * 80)

# In E8, we can have 8 mutually orthogonal roots (an orthogonal frame)
# But with opposite pairs, that's 4 pairs (8 roots)
# 240/8 = 30

# Can we have frames of 6 mutually orthogonal roots?
# No - if ±α, ±β, ±γ are mutually orthogonal, that's 3 pairs = 6 roots
# There are 240/6 = 40 such frames? Let's see...

# Actually, the A1×A1×A1 systems we found ARE these 3-orthogonal-pair systems

print(f"A1×A1×A1 = '3 orthogonal pairs' systems: {len(unique_a1x3)}")
print(f"240 roots / 6 roots per system = 40")

if len(unique_a1x3) == 40:
    # Check if they partition the roots
    all_roots = set()
    for sys in unique_a1x3:
        all_roots.update(sys)
    if len(all_roots) == 240:
        print("\n*** PERFECT PARTITION FOUND! ***")
        print("40 A1×A1×A1 systems, each with 6 roots, partition all 240 E8 roots!")
else:
    print(f"But we have {len(unique_a1x3)} systems, not 40")

# =============================================================================
# UNDERSTANDING THE DISCREPANCY
# =============================================================================

print("\n" + "=" * 80)
print("ANALYZING THE STRUCTURE")
print("=" * 80)

# We found many A1×A1×A1 systems, but they overlap
# Let's understand the combinatorics

if unique_a1x3:
    # Total "coverage" = sum of system sizes
    total_coverage = len(unique_a1x3) * 6
    print(f"Total coverage: {len(unique_a1x3)} systems × 6 = {total_coverage}")
    print(f"If no overlap, would cover: {total_coverage} roots")
    print(f"Actual roots to cover: 240")
    print(f"Average times each root covered: {total_coverage / 240:.2f}")

# =============================================================================
# THE RIGHT QUESTION: WHAT PARTITIONS 240?
# =============================================================================

print("\n" + "=" * 80)
print("THE RIGHT QUESTION")
print("=" * 80)

print(
    """
In W33:
    - 40 lines partition the 240 edges (each edge in exactly 1 line)
    - The 40 lines are the MAXIMAL CLIQUES

In E8:
    - What partitions the 240 roots into groups of 6?

The answer might NOT be A2 or A1×A1×A1 as root subsystems.
Instead, it might be a combinatorial/geometric partition.

Let's try: partition roots by POSITION IN COORDINATE SPACE.
"""
)

# Partition D8 roots (112) vs Spinor roots (128)
d8_roots = [r for r in e8_roots if all(x == int(x) for x in r)]
spinor_roots = [r for r in e8_roots if any(x != int(x) for x in r)]

print(f"D8 roots: {len(d8_roots)}")
print(f"Spinor roots: {len(spinor_roots)}")

# D8 roots: ±e_i ± e_j
# There are C(8,2) = 28 pairs of coordinates
# Each pair gives 4 roots: (e_i+e_j), (e_i-e_j), (-e_i+e_j), (-e_i-e_j)
# 28 × 4 = 112 ✓

# But 28 ≠ 40

# Spinor roots: 128
# These are (±1/2, ...) with even sign changes
# 128 = 2^7

# =============================================================================
# NEW INSIGHT: THE WEYL ORBIT STRUCTURE
# =============================================================================

print("\n" + "=" * 80)
print("WEYL ORBIT STRUCTURE")
print("=" * 80)

print(
    """
Key fact: The 240 E8 roots form a SINGLE orbit under W(E8).

But under smaller Weyl groups, they might decompose:

W(E8) has several maximal subgroups including W(D8), W(A8), W(E7×A1), W(E6×A2).

Under W(E6), the 240 roots should decompose as:
    240 = 72 + 54 + 54 + ...  (various representations)

The "40" we're looking for might come from dividing by W(E6) action!

|W(E8)| / |W(E6)| = 696729600 / 51840 = 13440

Hmm, that's not 40. But:

51840 = 40 × 1296 = 40 × 6^4

And 240 × 51840 / X = 40 for some X...
X = 240 × 51840 / 40 = 311040

Interesting: 311040 = 240 × 1296 = |E8 roots| × 6^4
"""
)

# =============================================================================
# THE ACTUAL CONNECTION
# =============================================================================

print("\n" + "=" * 80)
print("THE ACTUAL NUMBERS")
print("=" * 80)

print(
    """
Let's just state what we KNOW:

W33:
    - |V| = 40 (vertices)
    - |E| = 240 (edges)
    - k = 12 (regular degree)
    - λ = 2 (common neighbors for adjacent)
    - μ = 4 (common neighbors for non-adjacent)
    - 40 maximal 4-cliques (lines)
    - |Aut(W33)| = 51840

E8:
    - 240 roots
    - |W(E8)| = 696729600
    - |W(E6)| = 51840

The number 40 appears in W33 twice (vertices, lines).
In E8, is there a natural "40"?

One candidate: 240 / 6 = 40 (if roots partition into groups of 6)
Another: The stabilizer structure of W(E6) acting on something

Let me compute: Sp(4,3) acts on PG(3,3).
How many orbits does Sp(4,3) have on the 240 edges?
"""
)


# Rebuild W33 to check orbit structure
def symplectic_form(v1, v2):
    a1, b1, c1, d1 = v1
    a2, b2, c2, d2 = v2
    return (a1 * b2 - b1 * a2 + c1 * d2 - d1 * c2) % 3


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
edges = []
for i, v1 in enumerate(vertices):
    for j, v2 in enumerate(vertices):
        if i < j and symplectic_form(v1, v2) == 0:
            edges.append((i, j))

print(f"W33: {len(vertices)} vertices, {len(edges)} edges")

# Sp(4,3) acts transitively on the 240 edges (they're all "isotropic pairs")
# So there's only ONE orbit!

print(
    """
Sp(4,3) acts TRANSITIVELY on the 240 edges of W33.
There is exactly 1 orbit of edges.

Similarly, W(E6) acts on 240 E8 roots.
How many orbits?
"""
)

# Under W(E6) ⊂ W(E8), the 240 roots decompose:
# The stabilizer of a weight in E6 gives the orbit sizes

# E8 → E6 decomposition:
# 240 = 72 (E6 roots) + 27 + 27 + ...
# Actually: 240 = 72 + 27 + 27̄ + 27 + 27̄ + 60 based on branching rules

print(
    """
Under E6 ⊂ E8, the adjoint rep of E8 branches as:
    248 → 78 + 27 + 27̄ + 1 + 1 + ... (depends on embedding)

The 240 ROOTS of E8, under W(E6), should form several orbits.
But the key connection remains elusive without deeper Lie theory.
"""
)

# =============================================================================
# FINAL SUMMARY
# =============================================================================

print("\n" + "=" * 80)
print("SUMMARY: WHAT WE'VE FOUND")
print("=" * 80)

print(
    f"""
PROVEN STRUCTURES:

W33 (SYMPLECTIC POLAR GRAPH):
    - 40 vertices (points in W(3,3))
    - 240 edges (isotropic pairs)
    - 40 lines (maximal totally isotropic subspaces)
    - Each line has 4 points
    - Each pair of points on a line = 1 edge
    - 40 × C(4,2) = 40 × 6 = 240 ✓
    - |Sp(4,3)| = 51840

E8:
    - 240 roots
    - |W(E6)| = 51840
    - A1×A1×A1 systems: {len(unique_a1x3)} found (overlap heavily)

THE PARALLEL:
    W33:    40 lines          × 6 edges/line = 240 edges
    E8:     40 "structures"?  × 6 roots/structure = 240 roots ???

THE GAP:
    We haven't found 40 disjoint 6-root structures in E8 that partition all 240 roots.

    The A1×A1×A1 systems (orthogonal triples of pairs) number {len(unique_a1x3)},
    but they OVERLAP - they don't partition the roots.

THE QUESTION REMAINS:
    Is there a bijection φ: Edges(W33) → Roots(E8)
    that maps lines to some natural 6-root structures?
"""
)

if unique_a1x3:
    print(f"\nDETAIL: {len(unique_a1x3)} A1×A1×A1 systems, each covering 6 roots")
    print(f"Total coverage: {len(unique_a1x3) * 6}, overlapping significantly")
