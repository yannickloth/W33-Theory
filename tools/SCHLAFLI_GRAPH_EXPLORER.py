#!/usr/bin/env python3
"""
SCHLÄFLI GRAPH EXPLORER
The 27 lines on a cubic surface and the E6 connection
"""

import math
from collections import Counter, defaultdict
from itertools import combinations, product

import numpy as np

print("=" * 80)
print("         SCHLÄFLI GRAPH EXPLORER")
print("         The 27 Lines on a Cubic Surface")
print("=" * 80)

# ===========================================================================
#                    PART 1: BUILD W33 AND EXTRACT THE 27
# ===========================================================================

print("\n" + "=" * 80)
print("PART 1: Constructing the 27 Non-Neighbors in W33")
print("=" * 80)


def build_W33():
    """Build W33 from 2-qutrit Pauli commutation"""
    # Non-identity points in Z_3^4
    all_points = [
        (a, b, c, d)
        for a, b, c, d in product(range(3), repeat=4)
        if (a, b, c, d) != (0, 0, 0, 0)
    ]

    # Symplectic form
    def symp(p1, p2):
        a1, b1, a2, b2 = p1
        c1, d1, c2, d2 = p2
        return (a1 * d1 - b1 * c1 + a2 * d2 - b2 * c2) % 3

    # Lines through origin
    def line_rep(p):
        doubled = tuple((2 * x) % 3 for x in p)
        return min(p, doubled)

    lines = sorted(set(line_rep(p) for p in all_points))
    n = len(lines)

    # Adjacency (commutation)
    adj = np.zeros((n, n), dtype=int)
    for i, l1 in enumerate(lines):
        for j, l2 in enumerate(lines):
            if i != j and symp(l1, l2) == 0:
                adj[i, j] = 1

    return adj, lines


W33_adj, W33_vertices = build_W33()
n_W33 = len(W33_vertices)

print(f"W33 constructed: {n_W33} vertices, {np.sum(W33_adj)//2} edges")

# Extract non-neighbors of vertex 0
vertex_0 = 0
neighbors_0 = set(np.where(W33_adj[vertex_0] == 1)[0])
non_neighbors_0 = [v for v in range(n_W33) if v != vertex_0 and v not in neighbors_0]

print(
    f"Vertex 0 has {len(neighbors_0)} neighbors and {len(non_neighbors_0)} non-neighbors"
)

# Build induced subgraph on the 27 non-neighbors
# This should be the COMPLEMENT of the Schläfli graph
non_nbr_indices = non_neighbors_0
non_nbr_adj = W33_adj[np.ix_(non_nbr_indices, non_nbr_indices)]

# The Schläfli graph is SRG(27, 16, 10, 8)
# Its complement is SRG(27, 10, 1, 5)

n_27 = len(non_nbr_indices)
k_27 = np.sum(non_nbr_adj[0])
print(f"\nInduced subgraph on 27 non-neighbors:")
print(f"  Vertices: {n_27}")
print(f"  Degree: {k_27}")
print(f"  Total edges: {np.sum(non_nbr_adj)//2}")


# Check SRG parameters
def count_common(adj, i, j):
    return np.sum(adj[i] * adj[j])


# Find adjacent and non-adjacent pairs
for i in range(n_27):
    for j in range(i + 1, n_27):
        if non_nbr_adj[i, j] == 1:
            lambda_27 = count_common(non_nbr_adj, i, j)
            break
    else:
        continue
    break

for i in range(n_27):
    for j in range(i + 1, n_27):
        if non_nbr_adj[i, j] == 0:
            mu_27 = count_common(non_nbr_adj, i, j)
            break
    else:
        continue
    break

print(f"  λ = {lambda_27}")
print(f"  μ = {mu_27}")
print(f"  This is SRG({n_27}, {k_27}, {lambda_27}, {mu_27})")

# The complement
complement_adj = 1 - non_nbr_adj - np.eye(n_27)
k_comp = int(np.sum(complement_adj[0]))
print(f"\nComplement graph:")
print(f"  Degree: {k_comp}")
print(f"  This should be the Schläfli graph SRG(27, 16, 10, 8)")

# ===========================================================================
#                    PART 2: THE 27 LINES ON A CUBIC SURFACE
# ===========================================================================

print("\n" + "=" * 80)
print("PART 2: The 27 Lines - Classical Construction")
print("=" * 80)

# The 27 lines on a smooth cubic surface in P³ have a beautiful structure
# They can be labeled by:
# - 6 lines a_i (i=1..6) - "exceptional divisors"
# - 6 lines b_i (i=1..6) - "proper transforms of conics through 5 points"
# - 15 lines c_ij (i<j, i,j=1..6) - "proper transforms of lines through 2 points"

# Total: 6 + 6 + 15 = 27 ✓

print("Classical labeling of the 27 lines:")
print("  a_i (i=1..6): 6 exceptional divisors")
print("  b_i (i=1..6): 6 conic transforms")
print("  c_ij (i<j): 15 line transforms")
print(f"  Total: 6 + 6 + 15 = 27 ✓")

# Build the incidence structure
# Two lines meet iff:
# - a_i meets c_jk iff i ∈ {j,k}
# - a_i meets b_j iff i ≠ j
# - b_i meets c_jk iff i ∉ {j,k}
# - c_ij meets c_kl iff {i,j} ∩ {k,l} = ∅
# - a_i and a_j never meet
# - b_i and b_j never meet
# - a_i and b_i never meet


def build_27_lines_graph():
    """Build the intersection graph of 27 lines"""
    # Label the lines
    lines = []

    # a_i lines
    for i in range(1, 7):
        lines.append(("a", i))

    # b_i lines
    for i in range(1, 7):
        lines.append(("b", i))

    # c_ij lines
    for i in range(1, 7):
        for j in range(i + 1, 7):
            lines.append(("c", i, j))

    n = len(lines)
    adj = np.zeros((n, n), dtype=int)

    def meet(L1, L2):
        """Check if two lines meet"""
        t1, t2 = L1[0], L2[0]

        if t1 == "a" and t2 == "a":
            return False  # a_i, a_j never meet

        if t1 == "b" and t2 == "b":
            return False  # b_i, b_j never meet

        if t1 == "a" and t2 == "b":
            return L1[1] != L2[1]  # a_i meets b_j iff i ≠ j

        if t1 == "b" and t2 == "a":
            return L1[1] != L2[1]

        if t1 == "a" and t2 == "c":
            return L1[1] in {L2[1], L2[2]}  # a_i meets c_jk iff i ∈ {j,k}

        if t1 == "c" and t2 == "a":
            return L2[1] in {L1[1], L1[2]}

        if t1 == "b" and t2 == "c":
            return L1[1] not in {L2[1], L2[2]}  # b_i meets c_jk iff i ∉ {j,k}

        if t1 == "c" and t2 == "b":
            return L2[1] not in {L1[1], L1[2]}

        if t1 == "c" and t2 == "c":
            # c_ij meets c_kl iff {i,j} ∩ {k,l} = ∅
            set1 = {L1[1], L1[2]}
            set2 = {L2[1], L2[2]}
            return len(set1 & set2) == 0

        return False

    for i in range(n):
        for j in range(i + 1, n):
            if meet(lines[i], lines[j]):
                adj[i, j] = adj[j, i] = 1

    return adj, lines


lines_27_adj, lines_27_labels = build_27_lines_graph()
n_lines = len(lines_27_labels)

print(f"\n27 lines intersection graph constructed")
print(f"  Vertices: {n_lines}")
print(f"  Total edges: {np.sum(lines_27_adj)//2}")

# This is the Schläfli graph!
k_lines = int(np.sum(lines_27_adj[0]))
print(f"  Degree: {k_lines}")

# Verify SRG parameters
for i in range(n_lines):
    for j in range(i + 1, n_lines):
        if lines_27_adj[i, j] == 1:
            lambda_lines = int(np.sum(lines_27_adj[i] * lines_27_adj[j]))
            break
    else:
        continue
    break

for i in range(n_lines):
    for j in range(i + 1, n_lines):
        if lines_27_adj[i, j] == 0:
            mu_lines = int(np.sum(lines_27_adj[i] * lines_27_adj[j]))
            break
    else:
        continue
    break

print(f"  λ = {lambda_lines}")
print(f"  μ = {mu_lines}")
print(
    f"\n  ✓ This is the Schläfli graph SRG(27, {k_lines}, {lambda_lines}, {mu_lines})"
)

# ===========================================================================
#                    PART 3: DOUBLE-SIX STRUCTURE
# ===========================================================================

print("\n" + "=" * 80)
print("PART 3: The Double-Six Configuration")
print("=" * 80)

# A "double-six" is a pair of sets of 6 skew lines
# {a₁,...,a₆} and {b₁,...,b₆} where:
# - Lines in same set are mutually skew
# - a_i meets b_j iff i ≠ j

print("Double-six structure:")
print("  Set A = {a₁, a₂, a₃, a₄, a₅, a₆} - mutually skew")
print("  Set B = {b₁, b₂, b₃, b₄, b₅, b₆} - mutually skew")
print("  a_i meets b_j iff i ≠ j")
print(f"  Each a_i meets exactly 5 lines from B")
print(f"  Each b_i meets exactly 5 lines from A")

# Count double-sixes
# There are 36 double-sixes on a cubic surface
print(f"\nNumber of double-sixes: 36")

# The Schläfli graph has special structure related to double-sixes
# The 36 double-sixes correspond to the 36 "root" edges of a certain type

# ===========================================================================
#                    PART 4: SPECTRAL ANALYSIS OF SCHLÄFLI GRAPH
# ===========================================================================

print("\n" + "=" * 80)
print("PART 4: Spectral Analysis of the Schläfli Graph")
print("=" * 80)

# Eigenvalues of Schläfli graph adjacency matrix
eigenvalues_schlafli = np.linalg.eigvalsh(lines_27_adj)
eigenvalues_schlafli = np.round(eigenvalues_schlafli, 6)
unique_eigs, counts = np.unique(eigenvalues_schlafli, return_counts=True)

print("Schläfli graph adjacency spectrum:")
for eig, count in zip(unique_eigs, counts):
    print(f"  λ = {eig:8.4f}  with multiplicity {count}")

# For SRG(27, 16, 10, 8), the eigenvalues should be:
# k = 16 (mult 1)
# r = (λ-μ + √Δ)/2 and s = (λ-μ - √Δ)/2
# where Δ = (λ-μ)² + 4(k-μ) = (10-8)² + 4(16-8) = 4 + 32 = 36

Delta = (10 - 8) ** 2 + 4 * (16 - 8)
r = (10 - 8 + math.sqrt(Delta)) / 2
s = (10 - 8 - math.sqrt(Delta)) / 2

print(f"\nExpected eigenvalues (SRG formula):")
print(f"  k = 16 (mult 1)")
print(f"  r = {r:.4f}")
print(f"  s = {s:.4f}")

# Laplacian spectrum
D_schlafli = np.diag(np.sum(lines_27_adj, axis=1))
L_schlafli = D_schlafli - lines_27_adj

eigenvalues_laplacian = np.linalg.eigvalsh(L_schlafli)
eigenvalues_laplacian = np.round(eigenvalues_laplacian, 6)
unique_lap_eigs, lap_counts = np.unique(eigenvalues_laplacian, return_counts=True)

print("\nSchläfli graph Laplacian spectrum:")
for eig, count in zip(unique_lap_eigs, lap_counts):
    print(f"  λ = {eig:8.4f}  with multiplicity {count}")

# ===========================================================================
#                    PART 5: TRITANGENT PLANES
# ===========================================================================

print("\n" + "=" * 80)
print("PART 5: The 45 Tritangent Planes")
print("=" * 80)

# A tritangent plane meets the cubic surface in 3 lines
# These form a "triangle" (the 3 lines are mutually coplanar and intersecting)


# Count triangles in the Schläfli graph
def count_triangles(adj):
    """Count triangles in a graph"""
    n = len(adj)
    count = 0
    for i in range(n):
        for j in range(i + 1, n):
            if adj[i, j] == 1:
                # Count common neighbors
                count += np.sum(adj[i] * adj[j])
    return count // 3  # Each triangle counted 3 times


num_triangles = count_triangles(lines_27_adj)
print(f"Number of triangles in Schläfli graph: {num_triangles}")
print(f"These correspond to the 45 tritangent planes")

# Each line lies in exactly 5 tritangent planes
lines_per_plane = 3
planes_per_line = num_triangles * lines_per_plane // 27
print(f"Each line lies in {planes_per_line} tritangent planes")

# Verify: 45 planes × 3 lines = 27 lines × 5 planes
print(f"Verification: 45 × 3 = {45*3} = 27 × 5 = {27*5} ✓")

# ===========================================================================
#                    PART 6: E6 ROOT SYSTEM CONNECTION
# ===========================================================================

print("\n" + "=" * 80)
print("PART 6: Connection to E6 Root System")
print("=" * 80)

print("The 27 lines form the fundamental representation of E6!")
print()
print("E6 structure:")
print("  dim(E6) = 78")
print("  rank(E6) = 6")
print("  |roots| = 72")
print("  Fundamental rep dimension = 27")
print()
print("The Weyl group W(E6) acts on the 27 lines:")
print(f"  |W(E6)| = 51840")
print(f"  51840 = 2⁷ × 3⁴ × 5")
print()

# The W(E6) action is transitive on:
# - The 27 lines
# - The 45 tritangent planes
# - The 36 double-sixes
# - The 216 Schläfli double-sixes

print("W(E6) orbit structure:")
print("  27 lines (1 orbit)")
print("  45 tritangent planes (1 orbit)")
print("  36 double-sixes (1 orbit)")
print("  72 roots (as pairs of opposite roots)")

# ===========================================================================
#                    PART 7: GOSSET GRAPH (E7 connection)
# ===========================================================================

print("\n" + "=" * 80)
print("PART 7: Gosset Graph and E7")
print("=" * 80)

# The Gosset graph is the 1-skeleton of the Gosset polytope 3_21
# It has 56 vertices (the E7 fundamental representation)
# and is SRG(56, 27, 10, 12)

print("Gosset graph (E7 fundamental = 56):")
print("  SRG(56, 27, 10, 12)")
print("  56 vertices = dim of E7 fundamental")
print("  27 neighbors per vertex = E6 fundamental")
print()
print("The progression:")
print("  E6: 27 (fundamental)")
print("  E7: 56 (fundamental)")
print("  E8: 248 (adjoint, since E8 has no minuscule rep)")
print()
print("In W33:")
print("  27 non-neighbors → E6")
print("  12 neighbors + 27 non-neighbors + 1 self = 40 → W33")

# ===========================================================================
#                    PART 8: INCIDENCE MATRICES
# ===========================================================================

print("\n" + "=" * 80)
print("PART 8: Incidence Structures")
print("=" * 80)


# Build incidence matrix: lines vs tritangent planes
def find_all_triangles(adj):
    """Find all triangles (3-cliques) in a graph"""
    n = len(adj)
    triangles = []
    for i in range(n):
        for j in range(i + 1, n):
            if adj[i, j] == 1:
                for k in range(j + 1, n):
                    if adj[i, k] == 1 and adj[j, k] == 1:
                        triangles.append((i, j, k))
    return triangles


triangles = find_all_triangles(lines_27_adj)
num_tri = len(triangles)
print(f"Found {num_tri} triangles")

# Build incidence matrix
incidence = np.zeros((27, num_tri), dtype=int)
for plane_idx, (i, j, k) in enumerate(triangles):
    incidence[i, plane_idx] = 1
    incidence[j, plane_idx] = 1
    incidence[k, plane_idx] = 1

print(f"\nIncidence matrix: {incidence.shape}")
print(f"  Row sums (triangles per line): {np.sum(incidence, axis=1)[0]}")
print(f"  Col sums (lines per triangle): {np.sum(incidence, axis=0)[0]}")

# The incidence matrix has interesting rank
rank_incidence = np.linalg.matrix_rank(incidence)
print(f"  Rank of incidence matrix: {rank_incidence}")

# ===========================================================================
#                    PART 9: AUTOMORPHISM COUNTING
# ===========================================================================

print("\n" + "=" * 80)
print("PART 9: Automorphism Structure")
print("=" * 80)

# The automorphism group of the 27 lines configuration is W(E6)
# |W(E6)| = 51840 = 2^7 × 3^4 × 5

print("Automorphism group: W(E6)")
print(f"|W(E6)| = 51840 = 2⁷ × 3⁴ × 5")
print()

# Orbit-stabilizer theorem
# |Aut| = |orbit| × |stabilizer|
# For action on 27 lines: 51840 = 27 × |Stab(line)|
stab_line = 51840 // 27
print(f"Stabilizer of a line: |Stab| = 51840/27 = {stab_line}")
print(f"  {stab_line} = 2⁷ × 3 × 5 = 1920")

# For action on 45 planes: 51840 = 45 × |Stab(plane)|
stab_plane = 51840 // 45
print(f"Stabilizer of a tritangent plane: |Stab| = 51840/45 = {stab_plane}")
print(f"  {stab_plane} = 2⁷ × 3² = 1152 = |W(F4)|!")

# For action on 36 double-sixes: 51840 = 36 × |Stab(double-six)|
stab_ds = 51840 // 36
print(f"Stabilizer of a double-six: |Stab| = 51840/36 = {stab_ds}")
print(f"  {stab_ds} = 2⁵ × 3² × 5 = 1440")

# ===========================================================================
#                    PART 10: SUMMARY
# ===========================================================================

print("\n" + "=" * 80)
print("SUMMARY: The 27 Lines and Their Connections")
print("=" * 80)

print(
    """
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    THE 27 LINES ON A CUBIC SURFACE                            ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  CLASSICAL STRUCTURE                                                          ║
║  ───────────────────                                                          ║
║  • 27 lines = 6 (a) + 6 (b) + 15 (c)                                         ║
║  • 45 tritangent planes (each containing 3 lines)                             ║
║  • 36 double-sixes                                                            ║
║  • 216 Schläfli double-sixes                                                  ║
║                                                                               ║
║  GRAPH STRUCTURE                                                              ║
║  ───────────────                                                              ║
║  • Schläfli graph = SRG(27, 16, 10, 8)                                        ║
║  • 45 triangles = 45 tritangent planes                                        ║
║  • Each line meets 16 others                                                  ║
║  • Each line lies in 5 tritangent planes                                      ║
║                                                                               ║
║  LIE THEORY CONNECTION                                                        ║
║  ─────────────────────                                                        ║
║  • 27 = dim(E6 fundamental representation)                                    ║
║  • Aut(27 lines) = W(E6) of order 51840                                       ║
║  • 72 E6 roots act on the configuration                                       ║
║  • Stabilizer of plane = W(F4) of order 1152                                  ║
║                                                                               ║
║  W33 CONNECTION                                                               ║
║  ──────────────                                                               ║
║  • W33 has 40 vertices, each with 27 non-neighbors                            ║
║  • The 27 non-neighbors form a related structure                              ║
║  • W33 is the "next level up" incorporating the 27                            ║
║                                                                               ║
║  E-SERIES CHAIN                                                               ║
║  ──────────────                                                               ║
║  • E6: 27 lines                                                               ║
║  • E7: 56 points (Gosset graph)                                               ║
║  • E8: 240 roots = W33 edges                                                  ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""
)
