#!/usr/bin/env python3
"""
THE REAL STRUCTURE: 40 CONTEXTS × 6 EDGES = 240

Key discovery: W33 has exactly 40 maximal cliques (4-cliques),
each edge belongs to exactly one clique.

40 × 6 = 240

Now: E8 has 240 roots. Is there a "40 × 6" structure in E8?
"""

from collections import defaultdict
from itertools import combinations, product

import numpy as np

print("=" * 80)
print("THE 40 × 6 STRUCTURE")
print("=" * 80)

# =============================================================================
# REBUILD STRUCTURES
# =============================================================================


def symplectic_form(v1, v2):
    a1, b1, c1, d1 = v1
    a2, b2, c2, d2 = v2
    return (a1 * b2 - b1 * a2 + c1 * d2 - d1 * c2) % 3


def get_projective_points():
    points = []
    seen = set()
    for a in range(3):
        for b in range(3):
            for c in range(3):
                for d in range(3):
                    if (a, b, c, d) == (0, 0, 0, 0):
                        continue
                    v = [a, b, c, d]
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
adjacency = defaultdict(set)
for i, v1 in enumerate(vertices):
    for j, v2 in enumerate(vertices):
        if i < j and symplectic_form(v1, v2) == 0:
            edges.append((i, j))
            adjacency[i].add(j)
            adjacency[j].add(i)


# Find 4-cliques
def find_4_cliques(adj, n):
    cliques = []
    for a in range(n):
        for b in adj[a]:
            if b > a:
                for c in adj[a] & adj[b]:
                    if c > b:
                        for d in adj[a] & adj[b] & adj[c]:
                            if d > c:
                                cliques.append(frozenset([a, b, c, d]))
    return cliques


cliques_4 = find_4_cliques(adjacency, 40)
print(f"Number of 4-cliques: {len(cliques_4)}")

# Map each edge to its unique clique
edge_to_clique = {}
for idx, clique in enumerate(cliques_4):
    clique = list(clique)
    for i in range(4):
        for j in range(i + 1, 4):
            a, b = min(clique[i], clique[j]), max(clique[i], clique[j])
            edge_to_clique[(a, b)] = idx

print(f"All {len(edges)} edges mapped to cliques: {len(edge_to_clique) == len(edges)}")

# =============================================================================
# E8 ROOT SYSTEM: SEARCHING FOR 40 × 6 STRUCTURE
# =============================================================================

print("\n" + "=" * 80)
print("SEARCHING FOR 40 × 6 STRUCTURE IN E8 ROOTS")
print("=" * 80)


def construct_e8_roots():
    roots = []
    # D8 part: ±e_i ± e_j
    for i in range(8):
        for j in range(i + 1, 8):
            for s1, s2 in product([1, -1], repeat=2):
                r = [0] * 8
                r[i], r[j] = s1, s2
                roots.append(tuple(r))
    # Spinor part: (±1/2, ..., ±1/2) with even number of minus signs
    for signs in product([1, -1], repeat=8):
        if signs.count(-1) % 2 == 0:
            roots.append(tuple(s * 0.5 for s in signs))
    return roots


e8_roots = construct_e8_roots()
print(f"E8 roots: {len(e8_roots)}")

# In E8, two roots r1, r2 can have inner product: -2, -1, 0, 1, 2
# Roots with inner product 2 are the same, -2 are negatives
# Roots with inner product 1 are "adjacent" in the root system


# Build the "positive root graph": edges when inner product = 1
def inner_product(r1, r2):
    return sum(a * b for a, b in zip(r1, r2))


print("\nBuilding root adjacency (inner product = 1)...")
root_adj = defaultdict(set)
for i, r1 in enumerate(e8_roots):
    for j, r2 in enumerate(e8_roots):
        if i < j:
            ip = inner_product(r1, r2)
            if ip == 1:  # Adjacent roots
                root_adj[i].add(j)
                root_adj[j].add(i)

# Degrees in this graph
degrees = [len(root_adj[i]) for i in range(240)]
print(
    f"Root adjacency degrees: min={min(degrees)}, max={max(degrees)}, avg={sum(degrees)/240:.1f}"
)

# How many 4-cliques in the E8 root graph?
print("\nCounting 4-cliques in E8 root graph (ip=1)...")
e8_cliques_4 = find_4_cliques(root_adj, 240)
print(f"Number of 4-cliques in E8 root graph: {len(e8_cliques_4)}")

# =============================================================================
# ALTERNATIVE: CONSIDER OPPOSITE ROOTS AS "SAME"
# =============================================================================

print("\n" + "=" * 80)
print("CONSIDERING 120 POSITIVE ROOTS")
print("=" * 80)

# E8 has 240 roots, but 120 positive + 120 negative
# What structure do the 120 positive roots have?

# Standard: positive roots have first nonzero coordinate positive
positive_roots = []
positive_indices = []
for i, r in enumerate(e8_roots):
    for x in r:
        if abs(x) > 1e-10:
            if x > 0:
                positive_roots.append(r)
                positive_indices.append(i)
            break

print(f"Positive roots: {len(positive_roots)}")

# 120 = 40 × 3?
# 120 = 24 × 5?
# 120 = 20 × 6?
# 120 = 15 × 8?
# 120 = 12 × 10?

print("\nFactorizations of 120:")
for a in range(1, 121):
    if 120 % a == 0:
        print(f"  {a} × {120//a}")

# =============================================================================
# THE CROSS-RATIO: 40 CONTEXTS, EACH A "TETRAHEDRON"
# =============================================================================

print("\n" + "=" * 80)
print("THE 40 CONTEXTS AS TETRAHEDRA")
print("=" * 80)

print(
    """
Each 4-clique in W33 is a totally isotropic line in PG(3,3).
A totally isotropic line has 4 points (projectively).

In quantum mechanics, a 4-clique = a "context" =
a maximal set of mutually commuting observables.

There are 40 contexts, each with 4 observables.
Each pair within a context gives one edge.
C(4,2) = 6 edges per context.
40 × 6 = 240 edges.

QUESTION: Is there a similar "40 tetrahedra" structure in E8?
"""
)

# In E8 root system, is there a set of 40 "tetrahedra"
# that partition all 240 roots into groups of 6?

# A tetrahedron in root space: 4 roots that are pairwise...what?
# If they're pairwise orthogonal (ip=0), that's a frame
# If they're pairwise at angle 60° (ip=1), that's a simplex

# How many mutually orthogonal roots can we have?
# In R^8, we can have at most 8 mutually orthogonal directions
# But roots come in pairs (r, -r), so maybe 4 pairs = 8 roots

# Let's find maximal sets of mutually orthogonal roots
print("Looking for orthogonal root frames...")
orth_adj = defaultdict(set)
for i, r1 in enumerate(e8_roots):
    for j, r2 in enumerate(e8_roots):
        if i < j and abs(inner_product(r1, r2)) < 1e-10:
            orth_adj[i].add(j)
            orth_adj[j].add(i)

# Count orthogonal neighbors
orth_degrees = [len(orth_adj[i]) for i in range(240)]
print(f"Orthogonality degrees: min={min(orth_degrees)}, max={max(orth_degrees)}")


# Find maximal orthogonal cliques
# This is expensive, so let's just sample
def find_maximal_orthogonal_sets():
    """Find some maximal sets of mutually orthogonal roots."""
    max_sets = []

    # Start with each root and greedily extend
    for start in range(0, 240, 10):  # Sample every 10th root
        current = {start}
        candidates = orth_adj[start].copy()

        while candidates:
            # Find a candidate orthogonal to all current
            found = None
            for c in candidates:
                if all(c in orth_adj[x] for x in current):
                    found = c
                    break

            if found is None:
                break

            current.add(found)
            candidates = candidates & orth_adj[found]

        if len(current) >= 4:
            max_sets.append(frozenset(current))

    return list(set(max_sets))


max_orth = find_maximal_orthogonal_sets()
print(f"Sample of maximal orthogonal sets: {len(max_orth)}")
if max_orth:
    sizes = [len(s) for s in max_orth]
    print(f"Sizes: {sorted(set(sizes))}")

# =============================================================================
# THE E8 LATTICE STRUCTURE
# =============================================================================

print("\n" + "=" * 80)
print("E8 LATTICE STRUCTURE")
print("=" * 80)

print(
    """
E8 lattice has:
- 240 minimal vectors (the roots, norm² = 2)
- Kissing number 240 (each sphere touches 240 others)

The 240 roots form a polytope called the "4_21 polytope"
which has interesting sub-structures.

The 4_21 polytope contains:
- 17280 edges (pairs of roots at angle 60°)
- 2160 triangles (triples pairwise at 60°)
- ... etc.

Does it contain 40 special tetrahedra?
"""
)

# Count edges in root graph (ip=1, meaning angle 60°)
n_edges_e8 = sum(len(root_adj[i]) for i in range(240)) // 2
print(f"Edges in E8 root graph (angle 60°): {n_edges_e8}")

# This should relate to the structure of the 4_21 polytope
# 240 × 56 / 2 = 6720 if each root has 56 neighbors at 60°

avg_deg = sum(len(root_adj[i]) for i in range(240)) / 240
print(f"Average degree: {avg_deg}")

# =============================================================================
# KEY INSIGHT: THE DUAL GRAPH
# =============================================================================

print("\n" + "=" * 80)
print("THE DUAL PERSPECTIVE: 40 OBJECTS")
print("=" * 80)

print(
    """
W33: 40 vertices, 240 edges, 40 4-cliques
     Each vertex is in exactly k 4-cliques (for some k)
     Each edge is in exactly 1 4-clique

Let's compute k:
"""
)

# How many 4-cliques contain each vertex?
vertex_clique_count = defaultdict(int)
for clique in cliques_4:
    for v in clique:
        vertex_clique_count[v] += 1

clique_counts = list(vertex_clique_count.values())
print(f"Cliques per vertex: min={min(clique_counts)}, max={max(clique_counts)}")
if len(set(clique_counts)) == 1:
    print(f"Each vertex is in exactly {clique_counts[0]} cliques")
    k = clique_counts[0]
    print(
        f"Check: 40 vertices × {k} cliques/vertex / 4 vertices/clique = {40 * k // 4} cliques"
    )

# =============================================================================
# THE MATHEMATICAL CONNECTION
# =============================================================================

print("\n" + "=" * 80)
print("THE MATHEMATICAL CONNECTION")
print("=" * 80)

print(
    """
STRUCTURE OF W33:
    - 40 vertices = points in PG(3,3)
    - 40 4-cliques = totally isotropic lines in PG(3,3)
    - 240 edges = {point pairs on same line}

This is the INCIDENCE STRUCTURE of the symplectic quadric W(3,3).

The number 40 appears twice: 40 points, 40 lines.
This is because W(3,3) is SELF-DUAL!

SELF-DUALITY:
    Points ↔ Lines (both have 40)
    Incidence is symmetric

The 240 flags (point-line pairs where point ∈ line)
correspond to the edges!
    40 lines × 6 points/line = 240 flags (overcounts)
    Wait, each line has 4 points, so 40 × 4 = 160...

Hmm, let me recompute.
"""
)

# Points per line (= vertices per clique) = 4
# Lines per point (= cliques per vertex) = 4
# Total point-line incidences = 40 × 4 = 160

print(f"Point-line incidences: 40 vertices × {k} cliques/vertex = {40 * k}")
print(f"Alternatively: 40 cliques × 4 vertices/clique = {40 * 4}")

# So there are 160 incidences (flags), not 240
# The 240 edges are pairs of points on the same line
# C(4,2) = 6 pairs per line, 40 lines → 240 pairs

print(f"\nEdges = pairs of points on same line")
print(f"  = 40 lines × C(4,2) pairs/line")
print(f"  = 40 × 6 = 240 ✓")

# =============================================================================
# E8 ANALOGY: 40 "LINES" WITH 6 "PAIRS" EACH?
# =============================================================================

print("\n" + "=" * 80)
print("SEARCHING FOR 40 'LINES' IN E8")
print("=" * 80)

print(
    """
If W33 edges correspond to E8 roots, then:
    40 W33 "lines" should correspond to 40 E8 "structures"
    each containing 6 roots

What are these 40 structures in E8?
"""
)

# Possibility 1: 40 "root pairs with their 4 friends"
# Each pair (r, -r) is central, and there are 4 other pairs they relate to?
# 120 root pairs / 3 = 40 groups?

# Possibility 2: 40 sublattices or subroot systems
# A2 (6 roots) × 40 = 240?
# Let's check if E8 contains A2 sublattices

print("Checking for A2 (hexagon of 6 roots) sublattices in E8...")

# A2 has 6 roots forming a regular hexagon
# These would be: r1, r2, r1+r2, -r1, -r2, -(r1+r2) with ⟨r1,r2⟩ = 1


def find_a2_sublattices():
    """Find all A2 sublattices in E8."""
    a2_systems = []

    for i, r1 in enumerate(e8_roots):
        for j in root_adj[i]:  # r2 with ⟨r1,r2⟩ = 1
            r2 = e8_roots[j]
            # r1 + r2 should also be a root
            r3 = tuple(a + b for a, b in zip(r1, r2))

            # Check if r3 is in E8 roots (allow for normalization)
            norm_sq = sum(x**2 for x in r3)

            if abs(norm_sq - 2) < 1e-10:  # Should have norm² = 2
                # Check if r3 is actually in E8
                for k, r in enumerate(e8_roots):
                    if all(abs(a - b) < 1e-10 for a, b in zip(r, r3)):
                        # Found! Now check that -r1, -r2, -r3 are also there
                        a2_systems.append(frozenset([i, j, k]))
                        break

    return a2_systems


a2_sublattices = find_a2_sublattices()
# Each A2 is counted 6 times (once for each positive root as "r1")
unique_a2 = set()
for trip in a2_sublattices:
    trip_list = sorted(trip)
    unique_a2.add(tuple(trip_list))

print(f"A2 positive triangles found: {len(unique_a2)}")
print(f"Full A2 systems (including negatives): {len(unique_a2)} (each has 6 roots)")

if len(unique_a2) == 40:
    print("\n*** MATCH! 40 A2 sublattices partition the 240 roots! ***")
elif len(unique_a2) * 6 == 240:
    print(f"\n*** 40 A2's × 6 roots = 240! ***")
else:
    print(f"\n40 × 6 = 240, but we have {len(unique_a2)} A2's")

# How many roots are covered?
covered_roots = set()
for trip in unique_a2:
    for idx in trip:
        covered_roots.add(idx)
        # Also add the negative
        neg = tuple(-x for x in e8_roots[idx])
        for k, r in enumerate(e8_roots):
            if all(abs(a - b) < 1e-10 for a, b in zip(r, neg)):
                covered_roots.add(k)
                break

print(f"Roots covered by A2 sublattices: {len(covered_roots)}")

# =============================================================================
# CONCLUSION
# =============================================================================

print("\n" + "=" * 80)
print("CURRENT STATUS")
print("=" * 80)

print(
    f"""
W33 STRUCTURE:
    - 40 totally isotropic lines (4-cliques)
    - Each line contains 4 points
    - Each line gives C(4,2) = 6 edges
    - 40 × 6 = 240 edges ✓
    - Each edge is in exactly 1 line ✓

E8 STRUCTURE:
    - {len(unique_a2)} A2 sublattices found
    - Each A2 has 6 roots
    - 240 roots to account for

THE STRUCTURAL CORRESPONDENCE:
    W33 line (4 points) ↔ ? in E8
    W33 edge (pair of points) ↔ E8 root?

WHAT'S MISSING:
    A direct construction showing W33 "line" → E8 "structure"
    that explains WHY the numbers match.
"""
)
