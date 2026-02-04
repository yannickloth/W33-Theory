#!/usr/bin/env python3
"""
FINDING THE REAL CONNECTION: W33 → E8

The Lie algebra of 2-qutrit Paulis is su(9), not E8.
But the GRAPH W33 has the same structure as E8/E6.

Let's find what actually connects them.
"""

from collections import defaultdict
from itertools import combinations, product

import numpy as np

print("=" * 80)
print("SEARCHING FOR THE REAL W33 → E8 CONNECTION")
print("=" * 80)

# =============================================================================
# REBUILD W33 AND E8
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
for i, v1 in enumerate(vertices):
    for j, v2 in enumerate(vertices):
        if i < j and symplectic_form(v1, v2) == 0:
            edges.append((i, j))


def construct_e8_roots():
    roots = []
    for i in range(8):
        for j in range(i + 1, 8):
            for s1, s2 in product([1, -1], repeat=2):
                r = [0] * 8
                r[i], r[j] = s1, s2
                roots.append(tuple(r))
    for signs in product([1, -1], repeat=8):
        if signs.count(-1) % 2 == 0:
            roots.append(tuple(s * 0.5 for s in signs))
    return roots


e8_roots = construct_e8_roots()

print(f"W33: {len(vertices)} vertices, {len(edges)} edges")
print(f"E8: {len(e8_roots)} roots")

# =============================================================================
# KEY INSIGHT: THE INCIDENCE GEOMETRY
# =============================================================================

print("\n" + "=" * 80)
print("KEY INSIGHT: INCIDENCE GEOMETRY OF PG(3,3)")
print("=" * 80)

print(
    """
PG(3,3) is a projective space with:
- 40 points  (we have these as vertices)
- 130 lines  (each line has 4 points)
- 130 planes (each plane has 13 points, 13 lines)

The LINES are crucial! A line is a maximal totally isotropic subspace.

In W33:
- An edge connects two points that are "compatible" (commute)
- A 4-clique is a maximal set of pairwise commuting observables = CONTEXT

Let's count the contexts (maximal cliques = lines through origin).
"""
)

# Build adjacency for clique finding
adjacency = defaultdict(set)
for i, j in edges:
    adjacency[i].add(j)
    adjacency[j].add(i)


# Find maximal cliques (these are the "lines" - totally isotropic subspaces)
def find_all_maximal_cliques(adj, n):
    """Bron-Kerbosch algorithm"""
    cliques = []

    def bk(R, P, X):
        if not P and not X:
            if len(R) >= 2:
                cliques.append(frozenset(R))
            return
        pivot = max(P | X, key=lambda v: len(adj[v] & P), default=None)
        for v in list(P - (adj[pivot] if pivot else set())):
            bk(R | {v}, P & adj[v], X & adj[v])
            P = P - {v}
            X = X | {v}

    bk(set(), set(range(n)), set())
    return cliques


cliques = find_all_maximal_cliques(adjacency, 40)
clique_sizes = defaultdict(list)
for c in cliques:
    clique_sizes[len(c)].append(c)

print(f"\nMaximal cliques in W33:")
for size in sorted(clique_sizes.keys()):
    print(f"  Size {size}: {len(clique_sizes[size])} cliques")

# The lines in PG(3,3) are totally isotropic 2-subspaces
# Each such "line" has 4 points (projectively)
num_4_cliques = len(clique_sizes.get(4, []))
print(f"\nNumber of 4-cliques (maximal contexts): {num_4_cliques}")

# =============================================================================
# THE LINE GRAPH CONSTRUCTION
# =============================================================================

print("\n" + "=" * 80)
print("THE LINE GRAPH APPROACH")
print("=" * 80)

print(
    """
W33 is NOT directly the E8 root system.
But maybe the LINE GRAPH of W33 has 240 vertices?

Line graph L(G): vertices = edges of G, edges connect adjacent edges in G.

Let's check...
"""
)

# Line graph of W33
# Vertices = 240 edges
# Two edges are adjacent in L(W33) if they share a vertex in W33


def build_line_graph_adjacency(edges, n_vertices):
    """Build adjacency for line graph."""
    # First, build vertex-to-edge mapping
    vertex_edges = defaultdict(list)
    for idx, (i, j) in enumerate(edges):
        vertex_edges[i].append(idx)
        vertex_edges[j].append(idx)

    # Two edges are adjacent if they share a vertex
    line_adj = defaultdict(set)
    for v in range(n_vertices):
        edge_list = vertex_edges[v]
        for e1 in edge_list:
            for e2 in edge_list:
                if e1 < e2:
                    line_adj[e1].add(e2)
                    line_adj[e2].add(e1)

    return line_adj, vertex_edges


line_adj, vertex_edges = build_line_graph_adjacency(edges, 40)

print(f"Line graph L(W33):")
print(f"  Vertices: {len(edges)}")
n_line_edges = sum(len(line_adj[i]) for i in range(len(edges))) // 2
print(f"  Edges: {n_line_edges}")

# Degree in line graph
line_degrees = [len(line_adj[i]) for i in range(len(edges))]
print(f"  Degree distribution: min={min(line_degrees)}, max={max(line_degrees)}")
print(f"  Unique degrees: {sorted(set(line_degrees))}")

# Is the line graph regular?
if len(set(line_degrees)) == 1:
    print(f"  L(W33) is REGULAR of degree {line_degrees[0]}")
else:
    print(f"  L(W33) is NOT regular")

# =============================================================================
# ANOTHER APPROACH: EDGES AS ROOTS
# =============================================================================

print("\n" + "=" * 80)
print("EMBEDDING EDGES INTO R^8")
print("=" * 80)

print(
    """
Idea: Each edge (v1, v2) in W33 is a pair of points in Z_3^4.
Can we map this to a vector in R^8?

Approach 1: Embed Z_3 → C using cube roots of unity
           Then Z_3^4 → C^4 ≅ R^8
"""
)

# Cube roots of unity embedding
omega = np.exp(2j * np.pi / 3)


def z3_to_complex(x):
    """Map 0,1,2 to 1, ω, ω²"""
    return omega**x


def vertex_to_c4(v):
    """Map vertex (Z_3^4) to C^4"""
    return np.array([z3_to_complex(x) for x in v])


def vertex_to_r8(v):
    """Map vertex to R^8 via C^4"""
    c4 = vertex_to_c4(v)
    return np.concatenate([c4.real, c4.imag])


# Embed all vertices
vertex_embeddings = [vertex_to_r8(v) for v in vertices]

# For each edge, we could try:
# - Sum of endpoints
# - Difference of endpoints
# - Some other combination

# Let's try: edge → sum of embeddings
edge_vectors_sum = []
for i, j in edges:
    vec = vertex_embeddings[i] + vertex_embeddings[j]
    edge_vectors_sum.append(vec)

# Normalize
edge_vectors_sum = [
    v / np.linalg.norm(v) if np.linalg.norm(v) > 1e-10 else v for v in edge_vectors_sum
]

# Check: do any edge vectors match E8 roots?
e8_normalized = [np.array(r) / np.linalg.norm(r) for r in e8_roots]


def vectors_match(v1, v2, tol=1e-6):
    return np.allclose(v1, v2, atol=tol) or np.allclose(v1, -v2, atol=tol)


matches = 0
for ev in edge_vectors_sum:
    for er in e8_normalized:
        if vectors_match(ev, er):
            matches += 1
            break

print(f"\nEdge embeddings (sum) matching E8 roots: {matches}/{len(edges)}")

# Try: edge → difference
edge_vectors_diff = []
for i, j in edges:
    vec = vertex_embeddings[i] - vertex_embeddings[j]
    if np.linalg.norm(vec) > 1e-10:
        vec = vec / np.linalg.norm(vec)
    edge_vectors_diff.append(vec)

matches_diff = 0
for ev in edge_vectors_diff:
    for er in e8_normalized:
        if vectors_match(ev, er):
            matches_diff += 1
            break

print(f"Edge embeddings (diff) matching E8 roots: {matches_diff}/{len(edges)}")

# =============================================================================
# THE REAL CONNECTION: 240 = ORBIT SIZE
# =============================================================================

print("\n" + "=" * 80)
print("THE REAL CONNECTION: ORBIT STRUCTURE")
print("=" * 80)

print(
    """
Key observation:
- 240 is not just any number
- 240 = |W(E8)| / |W(D8)| = orbit size of a vector under W(E8)
- 240 = 2 × 120 = 2 × |W(H4)| related to 4D symmetry

Let's check: Under Sp(4,3), how do the 240 edges decompose into orbits?
"""
)

# We need to understand the orbit structure
# Sp(4,3) acts on PG(3,3), hence on pairs of points

# First, classify edges by some invariant
# Invariant 1: "type" based on the structure of the pair


def edge_type(i, j, vertices):
    """Compute an invariant of the edge."""
    v1, v2 = vertices[i], vertices[j]
    # The pair (v1, v2) spans a 2-space in Z_3^4
    # What's the "type" of this 2-space?

    # One invariant: rank of the matrix [v1; v2] over F_3
    # But both are nonzero and distinct, so rank = 2

    # Another: the symplectic inner product v1 · Ω · v2
    # But we know this is 0 (they commute)

    # How about: Hamming distance between v1 and v2?
    # Where they differ
    diff_positions = sum(1 for a, b in zip(v1, v2) if a != b)

    # Or: number of zeros in each
    zeros_v1 = sum(1 for x in v1 if x == 0)
    zeros_v2 = sum(1 for x in v2 if x == 0)

    return (min(zeros_v1, zeros_v2), max(zeros_v1, zeros_v2), diff_positions)


edge_types = defaultdict(list)
for idx, (i, j) in enumerate(edges):
    t = edge_type(i, j, vertices)
    edge_types[t].append(idx)

print("\nEdge types (zeros_min, zeros_max, diff_positions):")
for t in sorted(edge_types.keys()):
    print(f"  {t}: {len(edge_types[t])} edges")

# =============================================================================
# THE E6 WITHIN E8 CONNECTION
# =============================================================================

print("\n" + "=" * 80)
print("THE E6 ⊂ E8 DECOMPOSITION")
print("=" * 80)

print(
    """
Under E6 ⊂ E8, the 240 E8 roots decompose:
    240 = 72 + 54 + 54 + 27 + 27 + 6

Where:
    72 = roots of E6
    27, 27* = fundamental reps of E6
    54, 54* = ...
    etc.

Let's verify this decomposition explicitly.
"""
)

# E6 embedding in E8
# Standard: E6 is the subalgebra preserving a certain vector
# The 72 E6 roots are E8 roots orthogonal to two specific E8 roots

# Simple approach: E6 roots are E8 roots with specific constraint
# E6 ⊂ E8 via: roots perpendicular to α_7 and α_8 (simple roots 7,8)

# E8 simple roots (one standard convention):
alpha = [
    (1, -1, 0, 0, 0, 0, 0, 0),  # α_1
    (0, 1, -1, 0, 0, 0, 0, 0),  # α_2
    (0, 0, 1, -1, 0, 0, 0, 0),  # α_3
    (0, 0, 0, 1, -1, 0, 0, 0),  # α_4
    (0, 0, 0, 0, 1, -1, 0, 0),  # α_5
    (0, 0, 0, 0, 0, 1, 1, 0),  # α_6 (changed for E8)
    (-0.5,) * 8,  # α_7 (half-integer)
    (0, 0, 0, 0, 0, 1, -1, 0),  # α_8
]

# Actually, let's just count roots by their projection properties
# E6 roots: those with x_7 = x_8 = 0 (projection onto E6 subspace)


def is_e6_root(r):
    """Check if root is in E6 subspace (last two coords equal or zero pattern)"""
    # E6 ⊂ E8: roots with x_7 + x_8 = 0 and some other constraint
    # Simpler: count roots by last two coordinate sum
    return abs(r[6] + r[7]) < 1e-10 and abs(r[6] - r[7]) < 1e-10


e6_roots = [r for r in e8_roots if is_e6_root(r)]
print(f"Roots with x_7 = x_8 = 0: {len(e6_roots)}")

# That's not right. Let me try another approach.
# E6 roots in E8 are characterized by:
# The last 2 coordinates form an A2 pattern

# Actually, the standard embedding gives 72 E6 roots
# Let's just verify the count: E6 has 72 roots

# E6 root count formula: 2 × 36 = 72
print(f"E6 should have 72 roots")

# Under E8 → E6, we get 240 = 72 + 27 + 27 + 27 + 27 + 30 + 30 or similar
# The exact decomposition depends on the embedding

# Let me check root inner products to understand the structure
print("\nE8 root inner product structure:")
inner_products = defaultdict(int)
for r in e8_roots:
    for s in e8_roots:
        ip = sum(a * b for a, b in zip(r, s))
        inner_products[ip] += 1

for ip in sorted(inner_products.keys()):
    print(f"  ⟨r,r'⟩ = {ip:5.1f}: {inner_products[ip]:6d} pairs")

# Each root has inner product 2 with itself (240 roots)
# Inner product -2 with its negative (240 pairs with opposite)
# etc.

# =============================================================================
# THE ACTUAL MATHEMATICAL QUESTION
# =============================================================================

print("\n" + "=" * 80)
print("THE ACTUAL MATHEMATICAL QUESTION")
print("=" * 80)

print(
    """
We have established:
    |Edges(W33)| = 240 = |Roots(E8)|
    |Sp(4,3)| = 51840 = |W(E6)|

The mathematical question is:

    Does there exist a bijection φ: Edges(W33) → Roots(E8)
    such that the Sp(4,3) action on edges corresponds to
    the W(E6) action on roots?

To answer this, we need:
1. Understand the orbit structure of Sp(4,3) on edge pairs
2. Understand the orbit structure of W(E6) on E8 roots
3. Match these structures

ORBIT STRUCTURE OF Sp(4,3) ON EDGES:

Sp(4,3) acts on PG(3,3), which induces an action on pairs of points.
The edges are pairs of COMMUTING points (isotropic pairs).
"""
)

# How many orbits of Sp(4,3) on the 240 edges?
# This is related to the double coset structure

# For symplectic groups on isotropic pairs:
# Two isotropic pairs (p1, p2) and (q1, q2) are in same orbit
# iff they have the same "type" (span the same kind of subspace)

# For PG(3,3) with symplectic form:
# Isotropic pairs span either:
#   - A totally isotropic line (both on the same line)
#   - A non-degenerate 2-space (the span is not totally isotropic)

# Wait - if (p1, p2) are commuting (isotropic), their span might be:
#   - 1-dimensional if p2 = λ p1 (but we have projective points, so p1 ≠ p2)
#   - 2-dimensional otherwise

# In 2D, the symplectic form restricted could be:
#   - 0 (totally isotropic = degenerate)
#   - non-zero (non-degenerate)

print("\nClassifying edges by span type:")


def span_type(i, j, vertices):
    """What kind of 2-space do vertices i,j span?"""
    v1, v2 = np.array(vertices[i]), np.array(vertices[j])

    # Check if they're on a totally isotropic line
    # A line through p1, p2 contains: p1, p2, p1+p2, p1+2p2, p1-p2, etc. (projectively)

    # Actually, the span is totally isotropic iff
    # all linear combinations are isotropic (symplectic form = 0)

    # For v1, v2 both isotropic and mutually orthogonal (commuting),
    # check if v1+v2 is also isotropic

    v_sum = (v1 + v2) % 3
    # Normalize v_sum
    for k in range(4):
        if v_sum[k] != 0:
            inv = pow(int(v_sum[k]), -1, 3)
            v_sum = tuple((int(x) * inv) % 3 for x in v_sum)
            break

    # Check if v_sum is also commuting with v1 and v2
    v1_tuple = tuple(v1 % 3)
    v2_tuple = tuple(v2 % 3)

    comm_with_v1 = symplectic_form(v_sum, v1_tuple) == 0
    comm_with_v2 = symplectic_form(v_sum, v2_tuple) == 0

    if comm_with_v1 and comm_with_v2:
        return "totally_isotropic"
    else:
        return "non_degenerate"


span_types = defaultdict(list)
for idx, (i, j) in enumerate(edges):
    t = span_type(i, j, vertices)
    span_types[t].append(idx)

print(f"  Totally isotropic spans: {len(span_types['totally_isotropic'])}")
print(f"  Non-degenerate spans: {len(span_types['non_degenerate'])}")

# =============================================================================
# FINAL INSIGHT
# =============================================================================

print("\n" + "=" * 80)
print("FINAL INSIGHT: THE STRUCTURE OF 240")
print("=" * 80)

# Count edges within each 4-clique (totally isotropic line)
edges_in_4cliques = 0
cliques_4 = clique_sizes.get(4, [])
for clique in cliques_4:
    clique = list(clique)
    for i in range(len(clique)):
        for j in range(i + 1, len(clique)):
            edges_in_4cliques += 1

print(f"Number of 4-cliques: {len(cliques_4)}")
print(f"Edges within 4-cliques: {edges_in_4cliques}")
print(f"C(4,2) × {len(cliques_4)} = {6 * len(cliques_4)}")

# Each 4-clique contributes C(4,2) = 6 edges
# So edges within 4-cliques = 6 × (number of 4-cliques)

expected = 6 * len(cliques_4)
if expected == edges_in_4cliques:
    print("✓ Each edge is in exactly one 4-clique? Let's check...")

# Check if every edge is in exactly one 4-clique
edge_clique_count = defaultdict(int)
for clique in cliques_4:
    clique = list(clique)
    for i in range(len(clique)):
        for j in range(i + 1, len(clique)):
            a, b = min(clique[i], clique[j]), max(clique[i], clique[j])
            edge_clique_count[(a, b)] += 1

edges_not_in_cliques = [e for e in edges if edge_clique_count[e] == 0]
edges_in_multiple = [e for e in edges if edge_clique_count[e] > 1]

print(f"Edges in 0 4-cliques: {len(edges_not_in_cliques)}")
print(f"Edges in >1 4-cliques: {len(edges_in_multiple)}")
print(
    f"Edges in exactly 1 4-clique: {len(edges) - len(edges_not_in_cliques) - len(edges_in_multiple)}"
)

print("\n" + "=" * 80)
print("SUMMARY OF WHAT WE'VE FOUND")
print("=" * 80)

print(
    f"""
STRUCTURE OF W33:
    - 40 vertices (projective points in PG(3,3))
    - 240 edges (commuting pairs)
    - {len(cliques_4)} maximal 4-cliques (totally isotropic lines = contexts)
    - {len(span_types['totally_isotropic'])} edges on totally isotropic lines
    - {len(span_types['non_degenerate'])} edges spanning non-degenerate 2-spaces

OBSERVATION:
    240 = {len(span_types['totally_isotropic'])} + {len(span_types['non_degenerate'])}

    This partition might correspond to some E8 structure!

THE MATHEMATICAL QUESTION REMAINS:
    Is there a natural bijection φ matching these structures to E8 roots?

    240 E8 roots = 112 (D8) + 128 (spinor)

    Does {len(span_types['totally_isotropic'])} relate to one part?
    Does {len(span_types['non_degenerate'])} relate to another?
"""
)

# Check if the partition matches
print(f"\nChecking if partition matches E8 decomposition:")
print(
    f"  W33 partition: {len(span_types['totally_isotropic'])} + {len(span_types['non_degenerate'])} = 240"
)
print(f"  E8 partition:  112 (D8) + 128 (spinor) = 240")

if (
    len(span_types["totally_isotropic"]) == 112
    or len(span_types["totally_isotropic"]) == 128
):
    print("  → MATCH FOUND!")
else:
    print(f"  → No direct match ({len(span_types['totally_isotropic'])} ≠ 112 or 128)")
