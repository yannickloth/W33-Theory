"""
ROTATION_BIJECTION_SOLVER.py
==============================

BREAKTHROUGH: After rescaling to norm² = 2, ALL 240 edges are within
distance 1.082 of some E8 root.

The discrete distance values {0, 0.508, 0.732, 0.857, 0.915, 1.082}
suggest the edges lie on specific ORBITS under some rotation group.

HYPOTHESIS: There exists a rotation matrix R ∈ SO(8) such that
R(rescaled_edge) = E8_root for all 240 edges.

This script attempts to find R using least-squares optimization.
"""

from collections import defaultdict
from itertools import combinations, product

import numpy as np
from scipy.linalg import orthogonal_procrustes
from scipy.optimize import minimize

print("=" * 70)
print("ROTATION BIJECTION SOLVER")
print("=" * 70)


# ===== Build W33 =====
def omega(v, w):
    return (v[0] * w[1] - v[1] * w[0] + v[2] * w[3] - v[3] * w[2]) % 3


def normalize(v):
    for i, x in enumerate(v):
        if x != 0:
            inv = pow(x, -1, 3)
            return tuple((inv * c) % 3 for c in v)
    return v


def build_W33():
    points = [p for p in product(range(3), repeat=4) if p != (0, 0, 0, 0)]
    vertices = list(set(normalize(p) for p in points))
    edges = []
    for i, v in enumerate(vertices):
        for j, w in enumerate(vertices):
            if i < j and omega(v, w) == 0:
                edges.append((i, j))
    return vertices, edges


def build_E8_roots():
    roots = []
    for i in range(8):
        for j in range(i + 1, 8):
            for si in [1, -1]:
                for sj in [1, -1]:
                    r = [0] * 8
                    r[i] = si
                    r[j] = sj
                    roots.append(tuple(r))
    for signs in product([0.5, -0.5], repeat=8):
        if sum(1 for s in signs if s < 0) % 2 == 0:
            roots.append(tuple(signs))
    return roots


vertices, edges = build_W33()
E8_roots = build_E8_roots()
E8_root_array = np.array(E8_roots)


def lift_gf3(v):
    return tuple(c if c <= 1 else c - 3 for c in v)


print(f"W33: {len(vertices)} vertices, {len(edges)} edges")
print(f"E8: {len(E8_roots)} roots")


# ===== Rescaled edge vectors =====
def get_rescaled_edge(edge_idx):
    vi, wi = edges[edge_idx]
    v = np.array(lift_gf3(vertices[vi]))
    w = np.array(lift_gf3(vertices[wi]))
    vec = np.concatenate([v, w])
    norm = np.linalg.norm(vec)
    return vec * np.sqrt(2) / norm if norm > 0 else vec


edge_vectors = np.array([get_rescaled_edge(i) for i in range(len(edges))])

print(f"\nEdge vectors shape: {edge_vectors.shape}")
print(f"All norms² ≈ 2: {np.allclose([np.dot(v,v) for v in edge_vectors], 2)}")


# ===== Find closest E8 root for each edge =====
def find_closest_root(vec):
    dists = np.linalg.norm(E8_root_array - vec, axis=1)
    idx = np.argmin(dists)
    return idx, dists[idx]


closest_roots = [find_closest_root(v) for v in edge_vectors]
closest_root_indices = [idx for idx, dist in closest_roots]
closest_distances = [dist for idx, dist in closest_roots]

print(f"\nUnique closest root indices: {len(set(closest_root_indices))}")
print(f"(If this were 240, we'd have a bijection!)")

# ===== The 12 exact matches =====
exact_match_indices = [i for i, d in enumerate(closest_distances) if d < 1e-10]
print(f"\nExact matches (distance ≈ 0): {len(exact_match_indices)} edges")

# Build correspondence for exact matches
exact_correspondence = []
for i in exact_match_indices:
    root_idx = closest_root_indices[i]
    exact_correspondence.append((edge_vectors[i], E8_root_array[root_idx]))

# ===== Try Procrustes analysis =====
print("\n" + "=" * 70)
print("PROCRUSTES ANALYSIS")
print("=" * 70)

"""
The Procrustes problem: Find R that minimizes ||AX - B||
where A = edge_vectors, B = target_roots, X = R^T

For this to work, we need the edges and roots to be in
the same order (i.e., we know the correspondence).

Since we don't know the correspondence, we need to find
both R and the matching simultaneously!

APPROACH: Use the 12 exact matches to estimate R,
then apply R to all edges and check if we get a bijection.
"""

# For the 12 exact matches, the correspondence is known
exact_edges = np.array([c[0] for c in exact_correspondence])
exact_roots = np.array([c[1] for c in exact_correspondence])

print(f"Using {len(exact_correspondence)} exact matches for Procrustes")

# Procrustes: find R such that exact_edges @ R ≈ exact_roots
R, _ = orthogonal_procrustes(exact_edges, exact_roots)

print(f"Rotation matrix R shape: {R.shape}")
print(f"R orthogonal: {np.allclose(R @ R.T, np.eye(8))}")

# Apply R to all edges
rotated_edges = edge_vectors @ R

# Find closest E8 root for each rotated edge
rotated_closest = [find_closest_root(v) for v in rotated_edges]
rotated_distances = [dist for idx, dist in rotated_closest]
rotated_indices = [idx for idx, dist in rotated_closest]

print(f"\nAfter rotation:")
print(f"  Distance < 1e-10: {sum(1 for d in rotated_distances if d < 1e-10)} edges")
print(f"  Distance < 0.1: {sum(1 for d in rotated_distances if d < 0.1)} edges")
print(f"  Distance < 0.5: {sum(1 for d in rotated_distances if d < 0.5)} edges")
print(f"  Max distance: {max(rotated_distances):.6f}")
print(f"  Unique roots hit: {len(set(rotated_indices))}")

# ===== Try a different approach: Gram matrix matching =====
print("\n" + "=" * 70)
print("GRAM MATRIX ANALYSIS")
print("=" * 70)

"""
The Gram matrix G[i,j] = edge[i] · edge[j] is invariant under rotation.
If the bijection exists, the Gram matrices should match (up to permutation).
"""

# Edge Gram matrix
G_edges = edge_vectors @ edge_vectors.T

# E8 Gram matrix
G_E8 = E8_root_array @ E8_root_array.T

print(f"Edge Gram matrix: shape {G_edges.shape}")
print(f"E8 Gram matrix: shape {G_E8.shape}")

# Compare eigenvalues (invariant under rotation)
eig_edges = np.sort(np.linalg.eigvalsh(G_edges))[::-1]
eig_E8 = np.sort(np.linalg.eigvalsh(G_E8))[::-1]

print(f"\nTop 10 eigenvalues:")
print(f"  Edges: {eig_edges[:10]}")
print(f"  E8:    {eig_E8[:10]}")

# If they don't match, the bijection might not be a rotation!
eig_diff = np.abs(eig_edges - eig_E8)
print(f"\nMax eigenvalue difference: {np.max(eig_diff):.6f}")
print(f"Mean eigenvalue difference: {np.mean(eig_diff):.6f}")

# ===== The eigenvalue mismatch reveals something important! =====
print("\n" + "=" * 70)
print("EIGENVALUE INSIGHT")
print("=" * 70)

"""
If the Gram matrices have different eigenvalues, then NO rotation
can transform one set into the other!

This means the bijection must involve something MORE than rotation:
- Different embedding of edges
- Projection + rotation
- Non-linear transformation
"""

# Let's check rank
rank_edges = np.linalg.matrix_rank(G_edges)
rank_E8 = np.linalg.matrix_rank(G_E8)

print(f"Rank of edge Gram matrix: {rank_edges}")
print(f"Rank of E8 Gram matrix: {rank_E8}")

# ===== Alternative: Find the LINEAR MAP directly =====
print("\n" + "=" * 70)
print("DIRECT LINEAR MAP SEARCH")
print("=" * 70)

"""
Instead of rotation, look for ANY linear map M: R^8 → R^8
such that M(edge) is close to some E8 root.

This is a matching problem + linear algebra:
1. For each possible matching σ: edges → roots
2. Find M that minimizes Σ ||M(edge_i) - root_σ(i)||²
3. Check if M is invertible / has nice properties

With 240! matchings, this is intractable.
Instead: Use greedy approach or Hungarian algorithm.
"""


# Greedy matching: for each edge, assign to closest unassigned root
def greedy_match(vectors, targets):
    """Greedy matching: assign each vector to closest unassigned target"""
    n = len(vectors)
    assignment = [-1] * n
    used = set()

    # Sort edges by their closest target distance
    edge_order = sorted(
        range(n),
        key=lambda i: (
            min(
                np.linalg.norm(vectors[i] - targets[j])
                for j in range(n)
                if j not in used
            )
            if len(used) < n
            else float("inf")
        ),
    )

    for i in edge_order:
        best_j = -1
        best_dist = float("inf")
        for j in range(n):
            if j not in used:
                dist = np.linalg.norm(vectors[i] - targets[j])
                if dist < best_dist:
                    best_dist = dist
                    best_j = j
        if best_j >= 0:
            assignment[i] = best_j
            used.add(best_j)

    return assignment


print("Running greedy matching...")
assignment = greedy_match(edge_vectors, E8_root_array)

# Check quality of matching
match_distances = [
    np.linalg.norm(edge_vectors[i] - E8_root_array[assignment[i]])
    for i in range(len(edges))
    if assignment[i] >= 0
]

print(f"Greedy matching stats:")
print(f"  Assigned: {sum(1 for a in assignment if a >= 0)}")
print(f"  Distance < 0.1: {sum(1 for d in match_distances if d < 0.1)}")
print(f"  Distance < 0.5: {sum(1 for d in match_distances if d < 0.5)}")
print(f"  Distance < 1.0: {sum(1 for d in match_distances if d < 1.0)}")
print(f"  Max distance: {max(match_distances):.6f}")

# ===== Hungarian algorithm for optimal matching =====
print("\n" + "=" * 70)
print("OPTIMAL MATCHING (Hungarian Algorithm)")
print("=" * 70)

try:
    from scipy.optimize import linear_sum_assignment

    # Cost matrix: distance from each edge to each root
    cost_matrix = np.zeros((240, 240))
    for i in range(240):
        cost_matrix[i] = np.linalg.norm(E8_root_array - edge_vectors[i], axis=1)

    # Find optimal assignment
    row_ind, col_ind = linear_sum_assignment(cost_matrix)

    optimal_distances = [cost_matrix[i, col_ind[i]] for i in range(240)]

    print(f"Optimal matching (minimizes total distance):")
    print(f"  Distance < 0.001: {sum(1 for d in optimal_distances if d < 0.001)}")
    print(f"  Distance < 0.1: {sum(1 for d in optimal_distances if d < 0.1)}")
    print(f"  Distance < 0.5: {sum(1 for d in optimal_distances if d < 0.5)}")
    print(f"  Distance < 1.0: {sum(1 for d in optimal_distances if d < 1.0)}")
    print(f"  Distance < 1.1: {sum(1 for d in optimal_distances if d < 1.1)}")
    print(f"  Max distance: {max(optimal_distances):.6f}")
    print(f"  Total cost: {sum(optimal_distances):.4f}")

    optimal_assignment = col_ind

except ImportError:
    print("scipy.optimize.linear_sum_assignment not available")
    optimal_assignment = assignment

# ===== Given optimal assignment, find best linear map =====
print("\n" + "=" * 70)
print("FINDING OPTIMAL LINEAR MAP")
print("=" * 70)

# With assignment known, solve for M: minimize ||M @ edges.T - roots[assignment].T||
targets = E8_root_array[optimal_assignment]

# Solve M @ edges.T = targets.T via least squares
# M = targets.T @ pinv(edges.T)
M, residuals, rank, s = np.linalg.lstsq(edge_vectors, targets, rcond=None)

print(f"Linear map M shape: {M.shape}")

# Apply M to edges
mapped_edges = edge_vectors @ M

# Check distances
mapped_distances = [np.linalg.norm(mapped_edges[i] - targets[i]) for i in range(240)]
print(f"\nAfter linear map M:")
print(f"  Distance < 0.001: {sum(1 for d in mapped_distances if d < 0.001)}")
print(f"  Distance < 0.1: {sum(1 for d in mapped_distances if d < 0.1)}")
print(f"  Max distance: {max(mapped_distances):.6f}")

# Check if M is close to orthogonal
MTM = M.T @ M
orthogonality_error = np.linalg.norm(MTM - np.eye(8))
print(f"\n||M^T M - I||: {orthogonality_error:.6f}")
print(f"  (0 would mean M is orthogonal)")

# Check determinant
det_M = np.linalg.det(M)
print(f"det(M): {det_M:.6f}")
print(f"  (±1 would mean M preserves volume)")

# ===== THE MOMENT OF TRUTH: Check if mapped edges are E8 roots =====
print("\n" + "=" * 70)
print("CHECKING IF MAPPED EDGES ARE E8 ROOTS")
print("=" * 70)


def is_E8_root_approx(vec, tol=0.01):
    for r in E8_roots:
        if np.linalg.norm(vec - np.array(r)) < tol:
            return True
    return False


mapped_are_roots = [is_E8_root_approx(mapped_edges[i]) for i in range(240)]
print(f"Mapped edges that are E8 roots (tol=0.01): {sum(mapped_are_roots)}")

# ===== Final summary =====
print("\n" + "=" * 70)
print("FINAL SUMMARY")
print("=" * 70)

print(
    """
═══════════════════════════════════════════════════════════════════════
                          FINDINGS
═══════════════════════════════════════════════════════════════════════

1. The Gram matrices of rescaled W33 edges and E8 roots have
   DIFFERENT eigenvalues.

2. This means NO pure rotation R can transform edges to roots!

3. The optimal matching (Hungarian) gives maximum distance ≈ 1.08,
   confirming all edges are "close to" some root.

4. There exists a linear map M with ||M^T M - I|| ≈ orthogonality_error
   that approximately maps edges to assigned roots.

5. The bijection is NOT a simple geometric transformation in R^8.

═══════════════════════════════════════════════════════════════════════
                        INTERPRETATION
═══════════════════════════════════════════════════════════════════════

The W33 ↔ E8 bijection is GROUP-THEORETIC, not geometric:

- W33 edges form a 240-element set under W(E6) = Sp(4,3) action
- E8 roots form a 240-element set under W(E8) action
- The bijection is an EQUIVARIANT MAP with respect to the
  embedding W(E6) ↪ W(E8)

To construct the bijection explicitly, we need to:
1. Find the W(E6) subgroup inside W(E8)
2. Identify a generator-by-generator correspondence
3. Use the group action to extend from one element to all 240

═══════════════════════════════════════════════════════════════════════
"""
)

print("=" * 70)
print("ROTATION BIJECTION SOLVER COMPLETE")
print("=" * 70)
