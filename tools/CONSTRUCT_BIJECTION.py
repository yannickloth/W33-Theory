#!/usr/bin/env python3
"""
ATTEMPT TO CONSTRUCT THE BIJECTION φ: Edges(W33) → Roots(E8)

The key insight: Both have |G|/240 structure where G acts transitively.

W33: Sp(4,3) acts on 240 edges, stabilizer has order 216
E8:  W(E6) acts on 240 roots (under E6 ⊂ E8 embedding)?

Let's try to construct an EXPLICIT bijection.
"""

import json
from collections import defaultdict
from itertools import combinations, product

import numpy as np

print("=" * 80)
print("CONSTRUCTING THE BIJECTION")
print("=" * 80)

# =============================================================================
# STEP 1: Build W33 with explicit edge labeling
# =============================================================================


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
print(f"W33 vertices: {len(vertices)}")

# Build edges with explicit pairs
edges = []
edge_to_vertices = {}
for i, v1 in enumerate(vertices):
    for j, v2 in enumerate(vertices):
        if i < j and symplectic_form(v1, v2) == 0:
            edge_idx = len(edges)
            edges.append((i, j))
            edge_to_vertices[edge_idx] = (v1, v2)

print(f"W33 edges: {len(edges)}")

# =============================================================================
# STEP 2: Build E8 roots with explicit labeling
# =============================================================================


def construct_e8_roots():
    roots = []
    # D8 part: ±e_i ± e_j
    for i in range(8):
        for j in range(i + 1, 8):
            for s1, s2 in product([1, -1], repeat=2):
                r = [0] * 8
                r[i], r[j] = s1, s2
                roots.append(tuple(r))
    # Spinor part
    for signs in product([1, -1], repeat=8):
        if signs.count(-1) % 2 == 0:
            roots.append(tuple(s * 0.5 for s in signs))
    return roots


e8_roots = construct_e8_roots()
print(f"E8 roots: {len(e8_roots)}")

# =============================================================================
# STEP 3: Analyze the stabilizer structure
# =============================================================================

print("\n" + "=" * 80)
print("STABILIZER ANALYSIS")
print("=" * 80)

# The stabilizer of an edge in W33 has order 216 = 2³ × 3³
# The stabilizer of a root in E8 under W(E6) has what order?

# W(E6) acting on E8 roots: need to understand the E6 ⊂ E8 embedding
# Under this embedding, the 240 E8 roots decompose into W(E6) orbits

# Standard decomposition: E8 = E6 + {something}
# The 240 E8 roots under E6 decompose as:
#   - 72 roots of E6
#   - 27 + 27̄ (the fundamental reps of E6)
#   - Other pieces

# Actually, W(E6) acting on 240 E8 roots:
# 240 is NOT divisible by 51840, so W(E6) does NOT act transitively on all 240 roots
# The orbits have different sizes!

print(
    """
KEY INSIGHT: W(E6) does NOT act transitively on all 240 E8 roots!

The 240 E8 roots decompose into MULTIPLE W(E6)-orbits:
  - 72 roots of E6 (those orthogonal to the complementary A2)
  - Other orbits involving the 27 and 27̄ weights

But Sp(4,3) DOES act transitively on all 240 edges of W33.

This means the bijection CANNOT be W(E6)-equivariant!
"""
)

# Let's verify this by computing orbit sizes

# First, let's identify the E6 roots within E8
# E6 ⊂ E8: standard embedding where E6 is in the first 6 coordinates

# E8 roots in R^8, E6 roots are those with certain constraints
# One standard: E6 roots have x_7 = x_8 pattern

# Simple approach: E6 simple roots span a 6-dim subspace
# E6 roots are E8 roots lying in this subspace AND having norm² = 2

# For D8+spinor decomposition:
# D8 roots ±e_i±e_j: E6 roots have i,j ∈ {1,...,6} with specific constraint
# Spinor roots: more complex

# Let's just count by type
d8_roots = [r for r in e8_roots if all(x == int(x) for x in r)]
spinor_roots = [r for r in e8_roots if any(x != int(x) for x in r)]

print(f"\nE8 root types:")
print(f"  D8 (integer): {len(d8_roots)}")
print(f"  Spinor (half-int): {len(spinor_roots)}")

# =============================================================================
# STEP 4: A Different Approach - Match Invariants
# =============================================================================

print("\n" + "=" * 80)
print("APPROACH: MATCHING COMBINATORIAL INVARIANTS")
print("=" * 80)

print(
    """
Instead of group-theoretic bijection, try combinatorial matching.

For each edge in W33, compute invariants:
  - The 4-clique (line) it belongs to
  - Some structural property of the vertex pair

For each root in E8, compute invariants:
  - Inner product structure with other roots
  - Type (D8 or spinor)

Then match edges to roots that share invariant patterns.
"""
)

# Build adjacency for W33
adjacency = defaultdict(set)
for i, j in edges:
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
print(f"4-cliques in W33: {len(cliques_4)}")

# Map each edge to its clique
edge_to_clique = {}
for clique_idx, clique in enumerate(cliques_4):
    clique = list(clique)
    for i in range(4):
        for j in range(i + 1, 4):
            a, b = min(clique[i], clique[j]), max(clique[i], clique[j])
            for edge_idx, (vi, vj) in enumerate(edges):
                if (vi, vj) == (a, b):
                    edge_to_clique[edge_idx] = clique_idx
                    break

print(f"Edges assigned to cliques: {len(edge_to_clique)}")


# For E8: group roots by inner product pattern
def inner_product(r1, r2):
    return sum(a * b for a, b in zip(r1, r2))


# For each root, compute its "signature" = sorted list of inner products with all others
def root_signature(root_idx, roots):
    r = roots[root_idx]
    ips = []
    for j, s in enumerate(roots):
        if j != root_idx:
            ips.append(inner_product(r, s))
    return tuple(sorted(ips))


# All roots have the same signature (they're all equivalent under W(E8))
# So we need a DIFFERENT invariant


# Try: for each root, count neighbors at each inner product value
def root_profile(root_idx, roots):
    r = roots[root_idx]
    profile = defaultdict(int)
    for j, s in enumerate(roots):
        if j != root_idx:
            ip = inner_product(r, s)
            profile[ip] += 1
    return dict(profile)


# Check if all roots have the same profile
profiles = [root_profile(i, e8_roots) for i in range(240)]
unique_profiles = set(tuple(sorted(p.items())) for p in profiles)
print(f"Unique root profiles in E8: {len(unique_profiles)}")

if len(unique_profiles) == 1:
    print("All E8 roots have identical inner product profiles.")
    print(f"Profile: {profiles[0]}")

# =============================================================================
# STEP 5: The Line Graph Connection
# =============================================================================

print("\n" + "=" * 80)
print("THE LINE GRAPH CONNECTION")
print("=" * 80)

print(
    """
W33 edges form the vertices of the LINE GRAPH L(W33).
L(W33) has 240 vertices and is regular of degree 22.

E8 roots form a graph where edges connect roots at angle 60° (ip=1).
This E8 root graph is regular of degree 56.

Different graph structure! The bijection is not obvious.
"""
)

# Build E8 root adjacency (ip=1)
root_adj = defaultdict(set)
for i in range(240):
    for j in range(240):
        if i < j and abs(inner_product(e8_roots[i], e8_roots[j]) - 1) < 1e-10:
            root_adj[i].add(j)
            root_adj[j].add(i)

root_degrees = [len(root_adj[i]) for i in range(240)]
print(f"E8 root graph degree: {root_degrees[0]} (all same)")

# Build W33 line graph adjacency
line_adj = defaultdict(set)
vertex_edges = defaultdict(list)
for edge_idx, (i, j) in enumerate(edges):
    vertex_edges[i].append(edge_idx)
    vertex_edges[j].append(edge_idx)

for v in range(40):
    edge_list = vertex_edges[v]
    for e1 in edge_list:
        for e2 in edge_list:
            if e1 < e2:
                line_adj[e1].add(e2)
                line_adj[e2].add(e1)

line_degrees = [len(line_adj[i]) for i in range(240)]
print(f"L(W33) degree: {line_degrees[0]} (all same)")

# =============================================================================
# STEP 6: Finding the Right Correspondence
# =============================================================================

print("\n" + "=" * 80)
print("THE RIGHT QUESTION")
print("=" * 80)

print(
    """
The graphs are different:
  - L(W33): 240 vertices, degree 22
  - E8 root graph: 240 vertices, degree 56

So the bijection φ: Edges(W33) → Roots(E8) is NOT a graph isomorphism.

What IS preserved?

Possibility 1: Some HIGHER structure (not just adjacency)
Possibility 2: A different graph on E8 roots matches L(W33)
Possibility 3: The correspondence works at the CLIQUE/LINE level

Let's try Possibility 3: Map the 40 W33 lines to 40 E8 structures.
"""
)

# Each W33 line has 6 edges
# We need 40 groups of 6 E8 roots

# What's special about 6 roots in E8?
# - A2 sublattice: 6 roots forming a hexagon
# - 3 orthogonal pairs: 6 roots

# We found that A1×A1×A1 (3 orthogonal pairs) systems don't partition E8 roots
# (there are 37800 of them, heavily overlapping)

# What about looking for 40 SPECIAL 6-root structures?

# Idea: Use the stabilizer order 216 = 2³ × 3³
# 51840 / 216 = 240 (orbit size)
# 51840 / (216 × 6) = 40 (if 6-root structures form orbit)

# So maybe: There are 40 orbits of "6-tuples of roots" under W(E6)
# and these 40 orbits correspond to the 40 lines of W33

# This would require W(E6) to act on 6-tuples with orbit size = 6
# Then 40 × 6 × |Stab(6-tuple)| = 51840
# |Stab(6-tuple)| = 51840 / 240 = 216 ✓

# This is consistent! But we need to find the 40 special 6-tuples.

print(
    """
ORBIT COUNTING:

If W(E6) acts on special 6-tuples of E8 roots:
  |W(E6)| = 40 × 6 × |Stabilizer of 6-tuple|
  51840 = 240 × |Stab|
  |Stab| = 216

This matches the W33 stabilizer structure!

CONCLUSION: The bijection should map:
  - 40 W33 lines ↔ 40 "special 6-tuples" (orbits under some action)
  - Each line's 6 edges ↔ the 6 roots in that 6-tuple

The question is: WHAT are these special 6-tuples in E8?
"""
)

# =============================================================================
# STEP 7: Searching for Special 6-Tuples
# =============================================================================

print("\n" + "=" * 80)
print("SEARCHING FOR SPECIAL 6-TUPLES")
print("=" * 80)

# Try: 6-tuples where each pair has the SAME inner product
# In W33, all 6 edges of a line connect vertices at "distance 1" (adjacent)
# What's the E8 analog?

# For a 4-clique in W33, all C(4,2)=6 pairs are edges (adjacent)
# For a 6-tuple in E8, what's the condition?

# Try: All roots in the 6-tuple are mutually at some fixed angle
# Possible angles: 0° (same), 60° (ip=1), 90° (ip=0), 120° (ip=-1), 180° (opposite)

# We already know:
# - Mutually orthogonal (ip=0): 37800 A1×A1×A1 systems (too many)
# - Mutually at 60° (ip=1): Let's check how many 6-cliques in E8 root graph

print("Checking for 6-cliques in E8 root graph (all pairs at ip=1)...")

# A 6-clique means all C(6,2)=15 pairs have ip=1
# This is rare because the E8 root graph has chromatic number constraints

# Quick check: can 6 roots all be mutually at ip=1?
# Each root has 56 neighbors at ip=1
# For a 6-clique, we need at least 5 common neighbors
# among any two roots already in the clique

# Start with one root, find its 56 neighbors
# Among those 56, find those that are mutual neighbors (2-clique = edge)
# Etc.


def count_cliques_up_to_6(adj, start, max_size=6):
    """Count cliques containing 'start' up to size max_size."""
    cliques_by_size = defaultdict(int)

    def extend(clique, candidates):
        cliques_by_size[len(clique)] += 1
        if len(clique) >= max_size:
            return
        for v in candidates:
            new_candidates = [c for c in candidates if c > v and c in adj[v]]
            extend(clique | {v}, new_candidates)

    initial_candidates = sorted(adj[start])
    extend({start}, initial_candidates)

    return dict(cliques_by_size)


# Sample: check cliques from root 0
sample_cliques = count_cliques_up_to_6(root_adj, 0, max_size=6)
print(f"Cliques containing root 0 in E8 graph: {sample_cliques}")

# Check if there are any 6-cliques at all
total_6_cliques = 0
for start in range(0, 240, 24):  # Sample every 24th root
    cliques = count_cliques_up_to_6(root_adj, start, max_size=6)
    total_6_cliques += cliques.get(6, 0)
    if cliques.get(6, 0) > 0:
        print(f"  Root {start} is in {cliques[6]} 6-cliques")

print(f"Estimated 6-cliques in E8 root graph: ~{total_6_cliques * 24}")

# =============================================================================
# FINAL SUMMARY
# =============================================================================

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

print(
    """
WHAT WE'VE ESTABLISHED:

1. W33 has 240 edges partitioned into 40 lines × 6 edges
2. E8 has 240 roots
3. Both structures have symmetry groups of order 51840
4. The stabilizer structure (216) matches

WHAT WE NEED:

To construct bijection φ: Edges(W33) → Roots(E8), we need to find
40 special 6-tuples of E8 roots that:
  - Partition all 240 roots (no overlap)
  - Have some natural geometric meaning
  - Match the line structure of W33

THE OBSTACLE:

The E8 root graph (edges = ip=1) has degree 56, vs L(W33) has degree 22.
This means adjacency structure is different.

The "special 6-tuples" we seek are NOT:
  - 6-cliques in the E8 root graph (there aren't 40 of them)
  - A2 sublattices (they don't partition)
  - A1×A1×A1 systems (37800 of them, heavy overlap)

OPEN QUESTION:

What ARE the 40 special 6-tuples that partition 240 E8 roots
and correspond to the 40 lines of W33?

This remains the key unsolved problem.
"""
)
