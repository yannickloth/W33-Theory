#!/usr/bin/env python3
"""
DEEP_ANALYSIS.py - Searching for the actual bijection structure

The key insight from the previous analysis:
- W(E6) acts on E8 roots in orbits: 72 + 6 + 81 + 81 = 240
- Sp(4,3) acts on W33 edges in ONE orbit of size 240

So any equivariant bijection must involve a DIFFERENT group!

What groups act transitively on both?
- The full W(E8) acts transitively on all 240 E8 roots
- Aut(W33) acts transitively on all 240 W33 edges

Let's analyze both structures more carefully.
"""

from collections import Counter, defaultdict
from itertools import combinations, product

import numpy as np

print("=" * 70)
print("DEEP ANALYSIS: SEARCHING FOR THE BIJECTION STRUCTURE")
print("=" * 70)

# =============================================================================
# PART 1: Build W33 completely
# =============================================================================

F3 = [0, 1, 2]


def symplectic_form(u, v):
    """Standard symplectic form on F_3^4."""
    return (u[0] * v[2] - u[2] * v[0] + u[1] * v[3] - u[3] * v[1]) % 3


def canonical_rep(v):
    """Get canonical representative of projective point."""
    for i, x in enumerate(v):
        if x != 0:
            inv = 1 if x == 1 else 2  # 2 * 2 = 4 ≡ 1 mod 3
            return tuple((inv * c) % 3 for c in v)
    return v


# Get projective points
vectors = [v for v in product(F3, repeat=4) if v != (0, 0, 0, 0)]
proj_points = list(set(canonical_rep(v) for v in vectors))
n_points = len(proj_points)

print(f"\nW33: {n_points} vertices")

# Build adjacency
adj = {i: set() for i in range(n_points)}
for i, p1 in enumerate(proj_points):
    for j, p2 in enumerate(proj_points):
        if i < j and symplectic_form(p1, p2) == 0:
            adj[i].add(j)
            adj[j].add(i)

# Get edges
w33_edges = []
for i in range(n_points):
    for j in adj[i]:
        if i < j:
            w33_edges.append((i, j))

print(f"W33: {len(w33_edges)} edges")

# =============================================================================
# PART 2: Build E8 roots completely
# =============================================================================

e8_roots = []

# D8 roots: ±e_i ± e_j
for i in range(8):
    for j in range(i + 1, 8):
        for s1 in [1, -1]:
            for s2 in [1, -1]:
                root = [0] * 8
                root[i] = s1
                root[j] = s2
                e8_roots.append(tuple(root))

# Spinor roots: (±1/2)^8 with even number of minus signs
for signs in product([1, -1], repeat=8):
    if sum(1 for s in signs if s == -1) % 2 == 0:
        root = tuple(s / 2 for s in signs)
        e8_roots.append(root)

print(f"\nE8: {len(e8_roots)} roots")

# =============================================================================
# PART 3: Analyze the structure of W33 more carefully
# =============================================================================

print("\n" + "=" * 70)
print("ANALYZING W33 STRUCTURE")
print("=" * 70)


# Find maximal cliques in W33
def find_cliques_of_size(adj, k):
    """Find all cliques of size k."""
    cliques = []
    vertices = list(adj.keys())
    for combo in combinations(vertices, k):
        is_clique = True
        for i, v1 in enumerate(combo):
            for v2 in combo[i + 1 :]:
                if v2 not in adj[v1]:
                    is_clique = False
                    break
            if not is_clique:
                break
        if is_clique:
            cliques.append(set(combo))
    return cliques


# Find 4-cliques (lines in the polar space)
cliques_4 = find_cliques_of_size(adj, 4)
print(f"Number of 4-cliques in W33: {len(cliques_4)}")

# These 40 4-cliques are "lines" in the symplectic polar space
# Each has 4 vertices and C(4,2) = 6 edges
# 40 × 6 = 240 edges total!

# Verify each edge is in exactly one 4-clique
edge_to_clique = {}
for idx, clique in enumerate(cliques_4):
    clique_list = list(clique)
    for i, v1 in enumerate(clique_list):
        for v2 in clique_list[i + 1 :]:
            edge = (min(v1, v2), max(v1, v2))
            if edge in edge_to_clique:
                print(f"Edge {edge} is in multiple cliques!")
            edge_to_clique[edge] = idx

print(f"Edges covered by 4-cliques: {len(edge_to_clique)}")
print(f"Each edge in exactly one 4-clique: {len(edge_to_clique) == 240}")

# =============================================================================
# PART 4: The 40 × 6 structure
# =============================================================================

print("\n" + "=" * 70)
print("THE 40 × 6 = 240 STRUCTURE")
print("=" * 70)

print(
    f"""
W33 has a beautiful structure:
- 40 vertices (points)
- 40 lines (maximal 4-cliques)
- Each line has 4 points and 6 edges
- 40 lines × 6 edges = 240 edges (PERFECT PARTITION)

This is the structure of a GENERALIZED QUADRANGLE GQ(3,3)!
- 40 points
- 40 lines
- Each point on 4 lines
- Each line through 4 points
- Parameters: s = t = 3
"""
)

# =============================================================================
# PART 5: Look for similar structure in E8
# =============================================================================

print("\n" + "=" * 70)
print("SEARCHING FOR 40-FOLD STRUCTURE IN E8")
print("=" * 70)

# E8 has 240 roots. Are there 40 "special objects" that partition them?

# APPROACH 1: Use the E6 × SU(3) decomposition
# 72 + 6 + 81 + 81 = 240
# Can we find 40 objects?

# The 72 E6 roots form one piece
# Can we partition 72 into something × 6? 72 = 12 × 6

# The 81 = 27 × 3. So 27 objects, each appearing 3 times
# If we consider (27,3) as 27 "things with color 3"...

# Let me think differently:
# What are the natural "40" objects in E8?

# IDEA: Positive roots!
# E8 has 120 positive roots (half of 240)
# But we need 40...

# IDEA: Maximal tori / Cartan directions
# E8 has rank 8, so 8 Cartan directions. Not 40.

# IDEA: The W(E8) cosets by W(E6)
# |W(E8)| = 696,729,600
# |W(E6)| = 51,840
# |W(E8)| / |W(E6)| = 13,440. Too big.

# IDEA: The roots modulo some equivalence
# E8 has 240 roots. 240 / 6 = 40
# What if we group roots into sets of 6?

print("Looking for natural 40-fold partitions of E8 roots...")

# Check: Are there 40 "lines" (sets of 6 roots with special structure)?

# A1 × A1 × A1 subsystems
# Each A1 has 2 roots, so A1 × A1 × A1 has 8 roots
# That's not 6...

# A2 subsystems
# A2 has 6 roots!
# Are there 40 mutually disjoint A2 subsystems? No, 40 × 6 = 240 but they overlap


# Let me check A2 subsystems
def is_A2_system(roots_subset):
    """Check if 6 roots form an A2 system."""
    roots = list(roots_subset)
    if len(roots) != 6:
        return False
    # A2 roots: ±α, ±β, ±(α+β) where α·β = -1 (120° apart)
    # All roots have same length, angles are 60° or 120°
    for i, r1 in enumerate(roots):
        for r2 in roots[i + 1 :]:
            ip = sum(a * b for a, b in zip(r1, r2))
            # For length-sqrt(2) roots, ip should be -1, 0, 1, or 2 (same root)
            # For A2, we need ip = -1 (120°) or ip = 1 (60°)
            if ip not in [-1, 1]:
                return False
    return True


# Find A2 subsystems (this will take time)
print("Searching for A2 subsystems...")

# Actually let's be smarter - construct A2s directly
# Pick two roots α, β with α·β = -1, then the A2 is {±α, ±β, ±(α+β)}

a2_systems = []
for i, alpha in enumerate(e8_roots):
    for j, beta in enumerate(e8_roots[i + 1 :], i + 1):
        ip = sum(a * b for a, b in zip(alpha, beta))
        if ip == -1:  # 120° angle
            # α + β should also be a root
            alpha_plus_beta = tuple(a + b for a, b in zip(alpha, beta))
            if (
                alpha_plus_beta in e8_roots
                or tuple(-x for x in alpha_plus_beta) in e8_roots
            ):
                # Normalize to check
                apb_norm = sum(x * x for x in alpha_plus_beta)
                if apb_norm == 2:  # Length sqrt(2)
                    if alpha_plus_beta in e8_roots:
                        a2 = frozenset(
                            [
                                alpha,
                                beta,
                                alpha_plus_beta,
                                tuple(-x for x in alpha),
                                tuple(-x for x in beta),
                                tuple(-x for x in alpha_plus_beta),
                            ]
                        )
                    else:
                        neg_apb = tuple(-x for x in alpha_plus_beta)
                        a2 = frozenset(
                            [
                                alpha,
                                beta,
                                neg_apb,
                                tuple(-x for x in alpha),
                                tuple(-x for x in beta),
                                alpha_plus_beta,
                            ]
                        )
                    if len(a2) == 6:
                        a2_systems.append(a2)

# Remove duplicates
unique_a2 = list(set(a2_systems))
print(f"Number of A2 subsystems in E8: {len(unique_a2)}")

# Each root is in how many A2s?
root_to_a2_count = Counter()
for a2 in unique_a2:
    for r in a2:
        root_to_a2_count[r] += 1

a2_counts = Counter(root_to_a2_count.values())
print(f"Distribution of A2-containment: {a2_counts}")

# Can we find 40 disjoint A2s?
print(f"\nIf 40 disjoint A2s exist, we'd have 40 × 6 = 240")
print(f"Total A2 subsystems: {len(unique_a2)}")

# =============================================================================
# PART 6: Alternative approach - use the 40 vertices of W33 → 40 objects in E8
# =============================================================================

print("\n" + "=" * 70)
print("ALTERNATIVE: MAPPING 40 W33 VERTICES TO E8 STRUCTURES")
print("=" * 70)

# The 40 vertices of W33 are points of the symplectic polar space Sp(4,3)
# What are the natural "40" objects in E8?

# From Wikipedia on E8:
# Under E6 × SU(3), E8 decomposes as 78 + 8 + 27×3 + 27×3
# The 27 is the fundamental rep of E6

# The 27 lines on a cubic surface...
# And there are relationships to 40!

# Actually, the Schläfli graph (complement of the 27-line graph) has:
# - 27 vertices
# - The 27-line configuration has 27 lines meeting in 135 pairs

# But we need 40, not 27...

# WAIT - let me check something
# Sp(4,3) acts on 40 points
# W(E6) acts on 27 lines
# These are DIFFERENT objects!

# The connection might be:
# - 40 points of Sp(4,3)
# - Some 40-element set related to E6/E8

# From E6: the 72 roots can be partitioned...
# 72 / 6 = 12. Not 40.

# From the decomposition 81 + 81 + 72 + 6:
# 81 = 27 × 3
# What if the "40" comes from combining the 27 and something else?
# 27 + 13? Not obvious...

# DIFFERENT APPROACH:
# Let's look at what Sp(4,3) acting on 40 points tells us

print(
    """
KEY INSIGHT:
============

W33 vertices = 40 points of symplectic polar space over F_3
W33 edges = 240 (pairs of perpendicular points)
W33 lines = 40 (totally isotropic 2-subspaces)

Each LINE is a 4-element set of mutually perpendicular points
Each line contains C(4,2) = 6 edges
40 lines × 6 edges = 240 edges

This PERFECTLY PARTITIONS the edges!

For E8:
We need to find 40 "objects" such that each partitions
6 of the 240 roots, and together they cover all 240 exactly once.

CANDIDATE: The 40 might be related to:
- Subsystems of E8
- Cosets of some subgroup
- Special configurations
"""
)

# =============================================================================
# PART 7: THE A2 PARTITION ATTEMPT
# =============================================================================

print("\n" + "=" * 70)
print("ATTEMPTING TO FIND 40 DISJOINT A2 SYSTEMS")
print("=" * 70)

# Greedy search for disjoint A2 systems
remaining_roots = set(e8_roots)
disjoint_a2s = []

# Sort A2 systems by some criterion for greedy
for a2 in unique_a2:
    if a2 <= remaining_roots:  # All roots still available
        disjoint_a2s.append(a2)
        remaining_roots -= a2

print(f"Found {len(disjoint_a2s)} disjoint A2 systems")
print(f"Covering {len(disjoint_a2s) * 6} roots")
print(f"Remaining uncovered: {len(remaining_roots)}")

if len(disjoint_a2s) == 40:
    print("\n*** SUCCESS! Found 40 disjoint A2 systems! ***")
else:
    print(f"\nNeed 40, found {len(disjoint_a2s)}")

# =============================================================================
# PART 8: Check the exact match
# =============================================================================

print("\n" + "=" * 70)
print("STRUCTURE COMPARISON")
print("=" * 70)

print(
    f"""
W33:
- 40 lines (4-cliques)
- Each line: 4 vertices, 6 edges
- 40 × 6 = 240 edges (perfect partition)

E8 A2 attempt:
- {len(disjoint_a2s)} A2 subsystems found greedily
- Each A2: 6 roots
- Covered: {len(disjoint_a2s) * 6} roots

The numbers {"MATCH" if len(disjoint_a2s) == 40 else "DON'T MATCH"}!
"""
)

# =============================================================================
# PART 9: If we don't have 40, why not?
# =============================================================================

if len(disjoint_a2s) != 40:
    print("\n" + "=" * 70)
    print("ANALYSIS: WHY WE DON'T GET 40 DISJOINT A2s")
    print("=" * 70)

    print(
        f"""
The greedy algorithm found {len(disjoint_a2s)} disjoint A2 systems.

This suggests that 240 E8 roots CANNOT be partitioned into 40 A2 systems!

Let's verify: Is there a mathematical obstruction?

Consider: Each A2 ⊂ E8 corresponds to an embedding of sl(3) in e8.
The question is whether there exist 40 MUTUALLY ORTHOGONAL such embeddings.

Key constraint: If A2_1 and A2_2 share a root, they're not disjoint.
Each root is in multiple A2 systems (we found the distribution above).

If each root is in k A2 systems on average, then:
240 × k = 6 × (number of A2 systems)
So k = 6 × {len(unique_a2)} / 240 = {6 * len(unique_a2) / 240:.1f}

This high overlap suggests disjoint partition may not exist!
"""
    )

    # Alternative: what DOES partition E8 roots?
    print("\nLooking for OTHER partitions of 240...")

    # 240 = 8 × 30 = 6 × 40 = 5 × 48 = 4 × 60 = 3 × 80 = 2 × 120
    # We want 40 parts of size 6

    # What about: 40 cosets of some structure?
    # |W(E8)| = 696,729,600
    # 696,729,600 / 40 = 17,418,240
    # This isn't the order of any nice subgroup

    print("No obvious partition structure found.")
