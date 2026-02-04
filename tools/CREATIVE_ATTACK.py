#!/usr/bin/env python3
"""
CREATIVE_ATTACK.py - Finding the REAL bijection between W33 edges and E8 roots

NEW IDEAS TO TRY:
1. Line graph of W33 → has 240 vertices! Compare to E8 root graph
2. Association scheme structure
3. Explicit bijection via spectral methods
4. Double cover / lift approach
5. The 40×6 = 240 factorization through a clever partition

Let's get creative!
"""

import random
from collections import Counter, defaultdict
from itertools import combinations, permutations

import numpy as np

print("=" * 75)
print("CREATIVE ATTACK: Finding the W33 ↔ E8 Bridge")
print("=" * 75)

# ============================================================================
# PART 1: BUILD W33 FROM SCRATCH
# ============================================================================


def build_w33():
    """Build W33 = Sp(4,3) symplectic polar graph"""
    F3 = [0, 1, 2]  # Field with 3 elements

    # Points: nonzero vectors in F3^4, up to scalar multiple
    # Actually we need ISOTROPIC points (v^T J v = 0)

    # Symplectic form: J = [[0,I], [-I,0]] for 2×2 blocks
    # So (a,b,c,d) is isotropic iff ad - bc = 0 (mod 3)

    points = []
    seen = set()

    for a in F3:
        for b in F3:
            for c in F3:
                for d in F3:
                    if (a, b, c, d) == (0, 0, 0, 0):
                        continue
                    # Check isotropic: ad - bc ≡ 0 (mod 3)
                    if (a * d - b * c) % 3 != 0:
                        continue

                    # Normalize (choose canonical representative)
                    v = (a, b, c, d)
                    # Find first nonzero and scale
                    for i, x in enumerate(v):
                        if x != 0:
                            inv = pow(x, -1, 3)  # Modular inverse
                            v_norm = tuple((inv * y) % 3 for y in v)
                            break

                    if v_norm not in seen:
                        seen.add(v_norm)
                        points.append(v_norm)

    print(f"W33 vertices (isotropic points in PG(3,3)): {len(points)}")

    # Adjacency: orthogonal under symplectic form
    # (a,b,c,d) ⊥ (e,f,g,h) iff af - be + ch - dg ≡ 0 (mod 3)
    # Using J = [[0,1],[-1,0]] ⊗ I₂
    # Actually standard: <v,w> = v₁w₃ + v₂w₄ - v₃w₁ - v₄w₂
    # Simplified: v₁w₃ - v₃w₁ + v₂w₄ - v₄w₂ = 0

    def symplectic_ip(v, w):
        return (v[0] * w[2] - v[2] * w[0] + v[1] * w[3] - v[3] * w[1]) % 3

    n = len(points)
    adj = np.zeros((n, n), dtype=int)

    for i in range(n):
        for j in range(i + 1, n):
            if symplectic_ip(points[i], points[j]) == 0:
                adj[i, j] = adj[j, i] = 1

    # Remove self-loops (a point is always orthogonal to itself for isotropic)
    np.fill_diagonal(adj, 0)

    degrees = adj.sum(axis=1)
    edges = adj.sum() // 2

    print(f"Degrees: {Counter(degrees)}")
    print(f"Edges: {edges}")

    return points, adj


points_w33, adj_w33 = build_w33()

# Verify SRG parameters
n = len(points_w33)
k = adj_w33.sum(axis=1)[0]

lambda_count = Counter()
mu_count = Counter()
for i in range(n):
    for j in range(i + 1, n):
        common = sum(adj_w33[i, t] * adj_w33[j, t] for t in range(n))
        if adj_w33[i, j] == 1:
            lambda_count[common] += 1
        else:
            mu_count[common] += 1

print(f"λ: {lambda_count}")
print(f"μ: {mu_count}")

if n == 40 and k == 12 and 2 in lambda_count and 4 in mu_count:
    print("✓ Confirmed: W33 = SRG(40, 12, 2, 4)")

# ============================================================================
# PART 2: BUILD THE LINE GRAPH OF W33
# ============================================================================

print("\n" + "=" * 75)
print("IDEA 1: LINE GRAPH OF W33")
print("=" * 75)

print(
    """
The LINE GRAPH L(W33) has:
- One vertex for each EDGE of W33
- Two vertices adjacent iff the corresponding edges share an endpoint

W33 has 240 edges → L(W33) has 240 vertices!
E8 has 240 roots.

Could L(W33) ≅ E8 root graph?
"""
)

# Build list of edges
edges_w33 = []
for i in range(n):
    for j in range(i + 1, n):
        if adj_w33[i, j] == 1:
            edges_w33.append((i, j))

print(f"W33 has {len(edges_w33)} edges")

# Build line graph adjacency
m = len(edges_w33)
adj_line = np.zeros((m, m), dtype=int)

for a in range(m):
    for b in range(a + 1, m):
        e1, e2 = edges_w33[a], edges_w33[b]
        # Adjacent if they share a vertex
        if e1[0] in e2 or e1[1] in e2:
            adj_line[a, b] = adj_line[b, a] = 1

degrees_line = adj_line.sum(axis=1)
edges_line = adj_line.sum() // 2

print(f"L(W33): {m} vertices, {edges_line} edges")
print(f"Degrees: {Counter(degrees_line)}")

# Compare to E8 root graph which is 56-regular with 6720 edges
print(f"\nE8 root graph: 240 vertices, 6720 edges, 56-regular")
print(f"L(W33):        {m} vertices, {edges_line} edges, {degrees_line[0]}-regular")

if degrees_line[0] == 56 and edges_line == 6720:
    print("\n🎉 LINE GRAPH MATCHES E8 ROOT GRAPH PARAMETERS!")
else:
    print(f"\n❌ Parameters don't match ({degrees_line[0]}-regular vs 56-regular)")

# Compute spectrum of L(W33)
print("\nComputing spectrum of L(W33)...")
eigenvalues_line = np.linalg.eigvalsh(adj_line)
eigenvalues_line_rounded = np.round(eigenvalues_line).astype(int)
print(f"L(W33) spectrum: {Counter(eigenvalues_line_rounded)}")

# ============================================================================
# PART 3: BUILD E8 ROOT GRAPH FOR COMPARISON
# ============================================================================

print("\n" + "=" * 75)
print("E8 ROOT GRAPH FOR COMPARISON")
print("=" * 75)


def build_e8_roots():
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
    return np.array(roots)


roots_e8 = build_e8_roots()
print(f"E8: {len(roots_e8)} roots")

# E8 root graph: adjacent if inner product = 1
ne8 = len(roots_e8)
adj_e8 = np.zeros((ne8, ne8), dtype=int)
for i in range(ne8):
    for j in range(i + 1, ne8):
        if abs(np.dot(roots_e8[i], roots_e8[j]) - 1) < 0.01:
            adj_e8[i, j] = adj_e8[j, i] = 1

degrees_e8 = adj_e8.sum(axis=1)
edges_e8 = adj_e8.sum() // 2
print(f"E8 root graph: {ne8} vertices, {edges_e8} edges, {degrees_e8[0]}-regular")

eigenvalues_e8 = np.linalg.eigvalsh(adj_e8)
eigenvalues_e8_rounded = np.round(eigenvalues_e8).astype(int)
print(f"E8 spectrum: {Counter(eigenvalues_e8_rounded)}")

# ============================================================================
# PART 4: CHECK IF L(W33) ≅ E8 ROOT GRAPH
# ============================================================================

print("\n" + "=" * 75)
print("CHECKING ISOMORPHISM: L(W33) vs E8 ROOT GRAPH")
print("=" * 75)

spec_line = Counter(eigenvalues_line_rounded)
spec_e8 = Counter(eigenvalues_e8_rounded)

print(f"L(W33) spectrum: {dict(sorted(spec_line.items()))}")
print(f"E8 spectrum:     {dict(sorted(spec_e8.items()))}")

if spec_line == spec_e8:
    print("\n🎉🎉🎉 SPECTRA MATCH! Graphs might be isomorphic! 🎉🎉🎉")
else:
    print("\n❌ Spectra differ - graphs are NOT isomorphic")

# ============================================================================
# PART 5: TRY DIFFERENT ADJACENCY ON E8 - INNER PRODUCT = 0
# ============================================================================

print("\n" + "=" * 75)
print("IDEA 2: E8 with DIFFERENT adjacency (ip = 0)")
print("=" * 75)

adj_e8_ip0 = np.zeros((ne8, ne8), dtype=int)
for i in range(ne8):
    for j in range(i + 1, ne8):
        if abs(np.dot(roots_e8[i], roots_e8[j])) < 0.01:  # ip = 0
            adj_e8_ip0[i, j] = adj_e8_ip0[j, i] = 1

degrees_e8_ip0 = adj_e8_ip0.sum(axis=1)
edges_e8_ip0 = adj_e8_ip0.sum() // 2
print(
    f"E8 (ip=0): {ne8} vertices, {edges_e8_ip0} edges, degrees: {Counter(degrees_e8_ip0)}"
)

eigenvalues_e8_ip0 = np.linalg.eigvalsh(adj_e8_ip0)
eigenvalues_e8_ip0_rounded = np.round(eigenvalues_e8_ip0).astype(int)
print(f"E8 (ip=0) spectrum: {Counter(eigenvalues_e8_ip0_rounded)}")

# ============================================================================
# PART 6: THE 40 LINES OF W33 - CAN WE MAP TO E8 STRUCTURE?
# ============================================================================

print("\n" + "=" * 75)
print("IDEA 3: THE 40 LINES AND THEIR STRUCTURE")
print("=" * 75)


# Find all maximal cliques (should be 40 4-cliques)
def find_maximal_cliques_greedy(adj, n):
    """Find maximal cliques via simple search"""
    cliques = []

    # Start from each vertex
    for start in range(n):
        # BFS/greedy to extend
        clique = {start}
        candidates = set(j for j in range(n) if adj[start, j] == 1)

        while candidates:
            # Try to add vertices that are adjacent to all current clique members
            for v in list(candidates):
                if all(adj[v, c] == 1 for c in clique):
                    clique.add(v)
                    candidates = candidates & set(j for j in range(n) if adj[v, j] == 1)
                    break
            else:
                break

        # Check if maximal
        is_maximal = True
        for v in range(n):
            if v not in clique and all(adj[v, c] == 1 for c in clique):
                is_maximal = False
                break

        if is_maximal and len(clique) > 2:
            cliques.append(frozenset(clique))

    return list(set(cliques))


# More systematic: find all 4-cliques
def find_all_4_cliques(adj, n):
    cliques = []
    for i in range(n):
        nbrs_i = [j for j in range(n) if adj[i, j] == 1]
        for j in nbrs_i:
            if j <= i:
                continue
            nbrs_ij = [k for k in nbrs_i if adj[j, k] == 1 and k > j]
            for k in nbrs_ij:
                nbrs_ijk = [l for l in nbrs_ij if adj[k, l] == 1 and l > k]
                for l in nbrs_ijk:
                    cliques.append(frozenset([i, j, k, l]))
    return cliques


cliques_4 = find_all_4_cliques(adj_w33, n)
print(f"Found {len(cliques_4)} 4-cliques in W33")

# Check which are maximal (lines)
maximal_4 = []
for c in cliques_4:
    is_maximal = True
    for v in range(n):
        if v not in c and all(adj_w33[v, x] == 1 for x in c):
            is_maximal = False
            break
    if is_maximal:
        maximal_4.append(c)

print(f"Of which {len(maximal_4)} are maximal (the 40 lines)")

# Each line has 6 edges
for line in maximal_4[:3]:
    verts = list(line)
    line_edges = [(verts[i], verts[j]) for i in range(4) for j in range(i + 1, 4)]
    print(f"Line {verts}: {len(line_edges)} edges")

# ============================================================================
# PART 7: MAP LINES TO A2 SYSTEMS - ALTERNATIVE APPROACH
# ============================================================================

print("\n" + "=" * 75)
print("IDEA 4: SPECTRAL BIJECTION")
print("=" * 75)

print(
    """
Both W33 edges and E8 roots live in 240-dimensional "worlds".
Can we find a bijection using SPECTRAL methods?

Strategy:
1. Compute eigenvectors of both adjacency matrices
2. Use them to embed vertices in R^240
3. Find a rotation/permutation that aligns them
"""
)

# Get eigenvectors of W33 (40×40)
eigenvalues_w33, eigenvectors_w33 = np.linalg.eigh(adj_w33)
print(f"W33 eigenvalues: {Counter(np.round(eigenvalues_w33).astype(int))}")

# The key insight: W33 has spectrum {12^1, 2^24, -4^15}
# E8 has spectrum {56^1, ...}

# They live in different spaces - need to think differently

# ============================================================================
# PART 8: THE INCIDENCE STRUCTURE
# ============================================================================

print("\n" + "=" * 75)
print("IDEA 5: INCIDENCE MATRIX APPROACH")
print("=" * 75)

# Build vertex-line incidence matrix
# Each vertex is in exactly 4 lines
# Each line has exactly 4 vertices

M = np.zeros((40, 40), dtype=int)  # 40 vertices × 40 lines

for i, line in enumerate(maximal_4):
    for v in line:
        M[v, i] = 1

print(f"Incidence matrix M: {M.shape}")
print(f"Row sums (vertices per line count): {Counter(M.sum(axis=1))}")
print(f"Col sums (vertices per line): {Counter(M.sum(axis=0))}")

# Verify: M @ M^T should give adjacency info
# M @ M^T has diagonal = number of lines through each vertex = 4
# Off-diagonal (i,j) = number of lines through both i and j
# For GQ(3,3): two points on at most 1 line

MMT = M @ M.T
print(f"\nM @ M^T diagonal: {Counter(MMT.diagonal())}")
off_diag = [MMT[i, j] for i in range(40) for j in range(40) if i != j]
print(f"M @ M^T off-diagonal: {Counter(off_diag)}")

# ============================================================================
# PART 9: THE BIG INSIGHT - EDGE-LINE INCIDENCE
# ============================================================================

print("\n" + "=" * 75)
print("IDEA 6: EDGE-LINE INCIDENCE (40 lines × 240 edges)")
print("=" * 75)

# Build edge-line incidence matrix N: 240 edges × 40 lines
N = np.zeros((240, 40), dtype=int)

edge_to_idx = {e: i for i, e in enumerate(edges_w33)}

for line_idx, line in enumerate(maximal_4):
    verts = list(line)
    for i in range(4):
        for j in range(i + 1, 4):
            e = tuple(sorted([verts[i], verts[j]]))
            if e in edge_to_idx:
                N[edge_to_idx[e], line_idx] = 1

print(f"Edge-line incidence N: {N.shape}")
print(f"Edges per line: {Counter(N.sum(axis=0))}")  # Should be 6
print(f"Lines per edge: {Counter(N.sum(axis=1))}")  # How many lines contain each edge?

# Key: N @ N^T gives edge-edge relationships!
# (N @ N^T)[i,j] = number of lines containing both edge i and edge j

NNT = N @ N.T
print(f"\nN @ N^T shape: {NNT.shape}")
print(f"Diagonal (lines per edge squared?): {Counter(NNT.diagonal())}")
off_diag_edges = [NNT[i, j] for i in range(240) for j in range(i + 1, 240)]
print(f"Off-diagonal edge-edge values: {Counter(off_diag_edges)}")

# ============================================================================
# PART 10: COMPARE NNT TO E8 INNER PRODUCTS!
# ============================================================================

print("\n" + "=" * 75)
print("🔥 BREAKTHROUGH ATTEMPT: Does N @ N^T relate to E8? 🔥")
print("=" * 75)

# In E8, the inner product between roots takes values {-2, -1, 0, 1, 2}
# Let's see if NNT (with suitable scaling) matches!

# First, let's look at the E8 Gram matrix
gram_e8 = roots_e8 @ roots_e8.T
print(f"E8 Gram matrix values: {Counter(np.round(gram_e8.flatten()).astype(int))}")

# NNT values
nnt_values = Counter(NNT.flatten())
print(f"N @ N^T values: {nnt_values}")

# Normalize NNT
NNT_normalized = NNT / np.max(NNT) * 2
print(
    f"Normalized N @ N^T range: [{NNT_normalized.min():.2f}, {NNT_normalized.max():.2f}]"
)

# ============================================================================
# PART 11: THE KILLER TEST - BUILD BIJECTION AND CHECK
# ============================================================================

print("\n" + "=" * 75)
print("🎯 CONSTRUCTING AN EXPLICIT BIJECTION 🎯")
print("=" * 75)

print(
    """
Strategy: Use the LINE structure to guide the bijection.

W33: 40 lines, each with 6 edges
E8: Need to find 40 disjoint 6-sets

Previous: A2 systems only gave 37 disjoint sets.

NEW IDEA: What if we use a DIFFERENT 6-element structure in E8?

In E8, each root α has inner product distribution:
- ip = 2: 1 root (itself, or -α for ip = -2)
- ip = 1: 56 roots
- ip = 0: 126 roots
- ip = -1: 56 roots
- ip = -2: 1 root (-α)

What if we look at HEXAGONS in the E8 graph?
Or ORTHOGONAL 6-TUPLES?
"""
)


# Find 6-tuples of E8 roots that are mutually orthogonal
def find_orthogonal_6tuples():
    """Find sets of 6 mutually orthogonal roots"""
    # This is hard combinatorially, but let's try

    # Build orthogonality graph
    ortho_adj = np.zeros((240, 240), dtype=int)
    for i in range(240):
        for j in range(i + 1, 240):
            if abs(np.dot(roots_e8[i], roots_e8[j])) < 0.01:
                ortho_adj[i, j] = ortho_adj[j, i] = 1

    # Each root is orthogonal to 126 others
    print(f"Orthogonality degrees: {Counter(ortho_adj.sum(axis=1))}")

    # Finding 6-cliques in this graph would give orthogonal 6-tuples
    # But 6-cliques are expensive to find...

    # Alternatively: E8 has 240 roots in 8D
    # Max orthogonal set size = 8 (orthonormal basis)
    # But roots have norm √2, so at most 8 mutually orthogonal

    # Actually for ROOTS (not arbitrary vectors), max orthogonal set might be smaller
    # Let's check with a greedy approach

    max_clique = []
    remaining = list(range(240))
    random.shuffle(remaining)

    for r in remaining:
        if all(abs(np.dot(roots_e8[r], roots_e8[c])) < 0.01 for c in max_clique):
            max_clique.append(r)

    print(f"Greedy max orthogonal set: {len(max_clique)} roots")

    return ortho_adj, max_clique


ortho_adj, max_ortho = find_orthogonal_6tuples()

print(f"\nMax orthogonal roots found: {len(max_ortho)}")
if len(max_ortho) >= 6:
    # Check the roots
    for i, idx in enumerate(max_ortho[:6]):
        print(f"  Root {i}: {roots_e8[idx]}")

# ============================================================================
# PART 12: THE E8 FRAME STRUCTURE
# ============================================================================

print("\n" + "=" * 75)
print("IDEA 7: E8 FRAMES (8 mutually orthogonal roots)")
print("=" * 75)


def find_frames():
    """
    A FRAME in E8 is a set of 8 mutually orthogonal roots.
    These exist and form an interesting structure.
    Let's count them and see if 40 divides the count!
    """

    # Use greedy to find several frames
    frames = []
    used = set()

    for start in range(240):
        if start in used:
            continue

        frame = [start]
        for r in range(240):
            if r in used or r in frame:
                continue
            if all(abs(np.dot(roots_e8[r], roots_e8[f])) < 0.01 for f in frame):
                frame.append(r)
                if len(frame) == 8:
                    break

        if len(frame) == 8:
            frames.append(frame)
            # Don't mark used yet - frames can overlap

    print(f"Found {len(frames)} potential frames")

    # How many roots are in exactly k frames?
    root_frame_count = Counter()
    for r in range(240):
        count = sum(1 for f in frames if r in f)
        root_frame_count[count] += 1

    print(f"Roots by frame membership: {root_frame_count}")

    return frames


frames = find_frames()

# ============================================================================
# PART 13: THE FINAL CREATIVE IDEA - TRIALITY
# ============================================================================

print("\n" + "=" * 75)
print("🌟 IDEA 8: USE D4 TRIALITY TO ORGANIZE 240 = 3 × 80 🌟")
print("=" * 75)

print(
    """
E8 ⊃ D4 × D4, and D4 has TRIALITY (outer automorphism S₃).

D4 has three 8-dimensional representations:
- V (vector): the standard 8-dim
- S+ (even spinor): 8-dim
- S- (odd spinor): 8-dim

Under D4 × D4 ⊂ E8:
248 = (28,1) + (1,28) + (8v,8v) + (8s,8s) + (8c,8c)
    = 28 + 28 + 64 + 64 + 64 = 248

For the ADJOINT (248), but for ROOTS (240):
240 = 112 (D8 roots) + 128 (spinor weights)

But with D4 × D4:
We might get 240 = something × 3 × something!

Let's check: 240 = 80 × 3
And 80 = 40 × 2!

So: 240 = 40 × 6 = 40 × 3 × 2

The factor of 3 could come from TRIALITY!
The factor of 2 could come from ±roots!
The factor of 40 matches W33 lines!
"""
)

# Check: group E8 roots by their behavior under some D4 subgroup
# This is complex, so let's just verify the arithmetic

print("\n240 = 40 × 6 = 40 × 3 × 2")
print("     = (W33 lines) × (triality) × (±)")
print("\nThis suggests a natural partition IF we can identify the D4 action!")

# ============================================================================
# FINAL SUMMARY
# ============================================================================

print("\n" + "=" * 75)
print("CREATIVE ATTACK SUMMARY")
print("=" * 75)

print(
    f"""
ATTEMPTS AND RESULTS:
====================

1. LINE GRAPH L(W33):
   - {m} vertices, {edges_line} edges, {degrees_line[0]}-regular
   - E8 root graph: 240 vertices, 6720 edges, 56-regular
   - NOT isomorphic (different degrees)

2. W33 LINES:
   - {len(maximal_4)} lines confirmed
   - Each line has 6 edges
   - 40 × 6 = 240 ✓

3. EDGE-LINE INCIDENCE N @ N^T:
   - Gives a 240×240 matrix with interesting structure
   - Values: {dict(Counter(NNT.flatten()))}

4. ORTHOGONAL ROOTS:
   - Max orthogonal set: {len(max_ortho)} roots
   - E8 CAN have 8 mutually orthogonal roots (a "frame")

5. TRIALITY DECOMPOSITION:
   - 240 = 40 × 6 = 40 × 3 × 2
   - Suggests: (lines) × (triality) × (sign)

NEXT STEPS:
===========
- Investigate D4 triality structure on E8 roots
- Check if NNT (scaled) matches some E8 structure
- Look for a bijection preserving the 40×6 partition
"""
)
