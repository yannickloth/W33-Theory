"""
EXACT_BIJECTION_HUNT.py
=======================

MISSION: Construct the explicit 240 ↔ 240 bijection between W33 edges and E8 roots.

KEY INSIGHT FROM PREVIOUS ANALYSIS:
- gcd(80 Plücker classes, 120 E8 root pairs) = 40 = W33 vertices!
- Both structures are "built on top of" the 40 vertices

NEW ATTACK: The "AFFINE HEXAD" approach
- 40 vertices of W33 correspond to 40 "special points" in E8 structure
- Each vertex is incident to 12 edges (k=12 in SRG)
- Total incidences: 40 × 12 = 480 = 2 × 240
- Each edge is incident to 2 vertices
- This is consistent: 480 / 2 = 240 edges ✓

THE HEXAD CONNECTION:
- Steiner system S(5,8,24) has 759 octads
- 40 is related: 40 = 24 + 16 (partition of 24?)
- Or: 40 = 8 × 5 (8 octads × 5?)
"""

from collections import defaultdict
from itertools import combinations

import numpy as np
from scipy.optimize import linear_sum_assignment

print("=" * 70)
print("EXACT BIJECTION HUNT: THE FINAL ATTACK")
print("=" * 70)


# ===== Build W33 (SRG(40, 12, 2, 4)) =====
def build_W33():
    """
    W33 vertices: 40 isotropic points in GF(3)^4 with symplectic form
    """
    from itertools import product

    # Standard symplectic form: ω((a,b,c,d), (a',b',c',d')) = ab' - a'b + cd' - c'd (mod 3)
    def omega(v, w):
        return (v[0] * w[1] - v[1] * w[0] + v[2] * w[3] - v[3] * w[2]) % 3

    # All nonzero points in GF(3)^4 (projective: 80 points)
    points = [p for p in product(range(3), repeat=4) if p != (0, 0, 0, 0)]

    # Isotropic points: ω(v, v) = 0 (always true for symplectic!)
    # For totally isotropic, need subspace where ω vanishes
    # Actually for W33, we take the GRAPH where adjacent = orthogonal under ω

    # W33: vertices are the 40 "nonzero" elements, adjacency by orthogonality
    # But we need to quotient by scalar multiplication? Let's check.

    # Actually, the 40 vertices come from a specific construction.
    # Let's use: GF(3)^4 / ±1 for isotropic vectors under a specific quadratic form.

    # Simpler: Vertices of W33 are 40 lines through origin in GF(3)^4 that are isotropic
    # For a line {v, 2v} we pick representative with first nonzero coord = 1

    def normalize(v):
        """Normalize so first nonzero entry is 1"""
        for i, x in enumerate(v):
            if x != 0:
                inv = pow(x, -1, 3)  # Multiplicative inverse in GF(3)
                return tuple((inv * c) % 3 for c in v)
        return v

    # Get all normalized nonzero points
    normalized = set()
    for p in points:
        normalized.add(normalize(p))

    vertices = list(normalized)
    print(f"Total normalized points: {len(vertices)}")

    # Build adjacency: v ~ w iff ω(v, w) = 0 and v ≠ w
    edges = []
    adj = defaultdict(list)

    for i, v in enumerate(vertices):
        for j, w in enumerate(vertices):
            if i < j and omega(v, w) == 0:
                edges.append((i, j))
                adj[i].append(j)
                adj[j].append(i)

    return vertices, edges, adj


# ===== Build E8 roots =====
def build_E8_roots():
    """
    E8 roots: 240 vectors in R^8 with norm² = 2
    Type A: all integer coords with exactly two ±1, rest 0 (112 roots)
    Type B: all half-integer coords with even number of minus signs (128 roots)
    """
    roots = []

    # Type A: (±1, ±1, 0, 0, 0, 0, 0, 0) permutations
    for i in range(8):
        for j in range(i + 1, 8):
            for si in [1, -1]:
                for sj in [1, -1]:
                    r = [0] * 8
                    r[i] = si
                    r[j] = sj
                    roots.append(tuple(r))

    # Type B: (±½, ±½, ±½, ±½, ±½, ±½, ±½, ±½) with even number of minus signs
    from itertools import product

    for signs in product([0.5, -0.5], repeat=8):
        if sum(1 for s in signs if s < 0) % 2 == 0:
            roots.append(tuple(signs))

    return roots


# ===== Analysis =====
vertices, edges, adj = build_W33()
E8_roots = build_E8_roots()

print(f"\nW33: {len(vertices)} vertices, {len(edges)} edges")
print(f"E8: {len(E8_roots)} roots")

# Check SRG parameters
degrees = [len(adj[i]) for i in range(len(vertices))]
print(f"W33 degrees: min={min(degrees)}, max={max(degrees)}")
if all(d == 12 for d in degrees):
    print("✓ All vertices have degree 12 (k=12)")

print("\n" + "=" * 70)
print("THE COORDINATE INSIGHT")
print("=" * 70)

"""
KEY OBSERVATION:
- E8 integer-type roots have coords in {-1, 0, 1}
- W33 vertices have coords in GF(3) = {0, 1, 2}
- Lift: 0→0, 1→1, 2→-1

But edges need PAIRS of vertices mapped to SINGLE E8 roots.

NEW IDEA: Use the BARYCENTER or MIDPOINT of edges!
For edge (v, w):
  midpoint = (v + w) / 2 (over reals after GF(3)→{-1,0,1} lift)

This gives vectors with coords in {-1, -0.5, 0, 0.5, 1}
Scale by 2: coords in {-2, -1, 0, 1, 2}

Hmm, not quite E8...

ALTERNATE: Use DIFFERENCE v - w instead of concatenation!
This gives vectors in R^4 with coords in {-2, -1, 0, 1, 2}
"""


def lift_gf3_to_Z(v):
    """Lift GF(3) vector to integers: 0→0, 1→1, 2→-1"""
    return tuple(c if c <= 1 else c - 3 for c in v)


print("\nEdge analysis using DIFFERENCE vectors:")
print("-" * 70)

diff_vectors = []
for i, (vi, wi) in enumerate(edges[:10]):  # First 10 edges
    v = vertices[vi]
    w = vertices[wi]
    v_lifted = lift_gf3_to_Z(v)
    w_lifted = lift_gf3_to_Z(w)
    diff = tuple(v_lifted[k] - w_lifted[k] for k in range(4))
    norm_sq = sum(d * d for d in diff)
    diff_vectors.append(diff)
    print(f"  Edge {i}: {v} - {w} → {diff}, ||d||² = {norm_sq}")

# Collect all differences
all_diffs = []
for vi, wi in edges:
    v = vertices[vi]
    w = vertices[wi]
    v_lifted = lift_gf3_to_Z(v)
    w_lifted = lift_gf3_to_Z(w)
    diff = tuple(v_lifted[k] - w_lifted[k] for k in range(4))
    all_diffs.append(diff)

norm_sq_dist = defaultdict(int)
for d in all_diffs:
    norm_sq = sum(x * x for x in d)
    norm_sq_dist[norm_sq] += 1

print(f"\nDifference vector norm² distribution:")
for n, count in sorted(norm_sq_dist.items()):
    print(f"  ||d||² = {n}: {count} edges")

print("\n" + "=" * 70)
print("THE WEYL REFLECTION APPROACH")
print("=" * 70)

"""
IDEA: W(E6) acts on both W33 and E8!
Use this to construct the bijection as an equivariant map.

W(E6) ≅ Sp(4,3) acts on:
- 40 W33 vertices as symplectic space
- The 36 roots of E6 (inside E8)

The E6 root system has 72 roots, which come in 36 pairs.
E8 = E6 + "more stuff"

Specifically: E8 = E6 ⊕ A2 (sort of)

Could the bijection respect the E6 structure?
"""

# E6 roots inside E8
# E6 has 72 roots, they are E8 roots orthogonal to certain vectors

# Standard E6 embedding: take E8 roots (r1, ..., r8) with r7 + r8 = 0
E6_roots = [r for r in E8_roots if r[6] + r[7] == 0]
print(f"\nE6 roots (r7 + r8 = 0): {len(E6_roots)}")

# Hmm, that's not quite right. Let me use a different embedding.
# E6 inside E8: roots orthogonal to a specific A2

# Actually let's try: E6 roots are E8 roots with sum of last 3 coords = 0
E6_v2 = [r for r in E8_roots if abs(sum(r[5:])) < 0.01]
print(f"E6 roots (sum of last 3 ≈ 0): {len(E6_v2)}")

# Another try: E6 sits in hyperplane x1 + x2 + ... + x8 = 0 with additional constraint
coord_sums = [sum(r) for r in E8_roots]
print(f"E8 root coordinate sums: {set(coord_sums)}")

print("\n" + "=" * 70)
print("THE SYMPLECTIC → QUADRATIC LIFT")
print("=" * 70)

"""
FUNDAMENTAL THEOREM:
A symplectic form ω on V lifts to a quadratic form Q on a larger space.

For V = GF(3)^4 with symplectic form:
The "theta lift" goes to dimension 8!

CONSTRUCTION (following Weil representation):
V = GF(3)^4 → R^8 via characters

χ_v(x) = exp(2πi * trace(v·x) / 3) for v ∈ V

The Weil representation gives an 8-dimensional space (over C)
where Sp(4,3) acts - and this is related to E8!
"""


# Let's try the CHARACTER approach
def trace_gf3(x):
    """Trace map GF(3) → Z/3Z (identity for prime field)"""
    return x % 3


def character(v, x):
    """Character χ_v(x) = exp(2πi * v·x / 3)"""
    dot = sum(v[i] * x[i] for i in range(4)) % 3
    return np.exp(2j * np.pi * dot / 3)


# For each W33 vertex v, we can compute a "Gauss sum" type object
# over its neighbors

print("\nCharacter sums over neighborhoods:")
print("-" * 70)

omega_cube = np.exp(2j * np.pi / 3)  # Primitive cube root of unity

for i in range(5):  # First 5 vertices
    v = vertices[i]
    v_char_sum = sum(character(v, vertices[j]) for j in adj[i])
    print(f"  Vertex {i} = {v}: Σ_neighbors χ_v(w) = {v_char_sum:.4f}")

print("\n" + "=" * 70)
print("THE DIRECT EMBEDDING APPROACH")
print("=" * 70)

"""
SIMPLEST POSSIBLE BIJECTION:

What if the 40 W33 vertices embed directly into E8 as a specific set?

E8 has distinguished subsets:
- 120 vertices of 600-cell
- 600 vertices of 120-cell
- etc.

Could 40 W33 vertices correspond to a distinguished subset of E8?

CHECK: 40 in relation to E8 structure
- 240/40 = 6
- 40 = 8 × 5 = dim(E8) × 5
- 40 = 120/3 = (E8/2)/3
"""

# Let's see if there's a natural 40-element subset in E8

# Idea 1: Roots whose first 4 coords are 0
zero_prefix = [r for r in E8_roots if r[:4] == (0, 0, 0, 0)]
print(f"E8 roots with first 4 coords = 0: {len(zero_prefix)}")


# Idea 2: Roots lying in a D4 sublattice
# D4 has 24 roots
def is_D4_root(r):
    """Check if r is a D4 root (norm² = 2, integer coords, sum even)"""
    if not all(c == int(c) for c in r):
        return False
    if sum(c * c for c in r) != 2:
        return False
    return sum(r) % 2 == 0


# Idea 3: Find the 40 "special" roots using some criterion
# E8 roots that have a specific symmetry

# Let's look at automorphism orbits
# The W(E8) group has order 696729600

print("\nLooking for natural 40-element subsets of E8 roots...")

# Try: roots with exactly k nonzero coordinates
for k in range(1, 9):
    subset = [r for r in E8_roots if sum(1 for c in r if c != 0) == k]
    print(f"  {k} nonzero coords: {len(subset)} roots")

# Integer type vs half-integer type
int_type = [r for r in E8_roots if all(c == int(c) for c in r)]
half_type = [r for r in E8_roots if all(c != int(c) for c in r)]
print(f"\nInteger-type roots: {len(int_type)}")
print(f"Half-integer-type roots: {len(half_type)}")

print("\n" + "=" * 70)
print("THE TRIALITY INSIGHT")
print("=" * 70)

"""
D4 TRIALITY:
D4 has an exceptional S3 outer automorphism (triality)
This permutes the three 8-dimensional representations:
- Vector (8v)
- Spinor (8s)
- Co-spinor (8c)

E8 decomposes under D4 × D4 (or Spin(8) × Spin(8)):

E8 roots =
  (D4 roots, 0) ∪ (0, D4 roots) ∪
  (8v, 8v) ∪ (8s, 8s) ∪ (8c, 8c)

Count: 24 + 24 + 64 + 64 + 64 = 240 ✓

THE CONNECTION TO W33:
40 = 24 + 16
where 24 = |D4 roots|/2 (root pairs) and 16 = ???

Or: 40 = 8 + 8 + 8 + 8 + 8 (five 8-element sets from triality?)
"""

# D4 roots in first 4 coordinates
D4_1 = [r for r in E8_roots if r[4:] == (0, 0, 0, 0)]
D4_2 = [r for r in E8_roots if r[:4] == (0, 0, 0, 0)]

print(f"D4 in coords 1-4: {len(D4_1)} roots")
print(f"D4 in coords 5-8: {len(D4_2)} roots")

# The "mixed" roots (8v, 8v) etc.
mixed = [r for r in E8_roots if r[:4] != (0, 0, 0, 0) and r[4:] != (0, 0, 0, 0)]
print(f"Mixed (neither D4): {len(mixed)} roots")

print("\n" + "=" * 70)
print("THE GRAPH HOMOMORPHISM APPROACH")
print("=" * 70)

"""
What if the bijection is a GRAPH HOMOMORPHISM?

Construct a graph on E8 roots where edges connect "compatible" roots.
Then look for a bijection that preserves edge structure.

E8 root graph: r ~ r' iff ⟨r, r'⟩ = ±1 (adjacent in root system)

For E8:
- ⟨r, r⟩ = 2 (norm squared)
- ⟨r, r'⟩ ∈ {-2, -1, 0, 1, 2} for roots r ≠ r'
- ⟨r, r'⟩ = 2 only for r = r'
- ⟨r, r'⟩ = -2 only for r' = -r
- ⟨r, r'⟩ = ±1 for "adjacent" roots
"""


def inner(r1, r2):
    return sum(a * b for a, b in zip(r1, r2))


# Build E8 adjacency graph (roots at inner product 1)
E8_adj = defaultdict(list)
for i, r1 in enumerate(E8_roots):
    for j, r2 in enumerate(E8_roots):
        if i < j:
            ip = inner(r1, r2)
            if ip == 1:
                E8_adj[i].append(j)
                E8_adj[j].append(i)

# Degree distribution in E8 root graph
E8_degrees = [len(E8_adj[i]) for i in range(len(E8_roots))]
print(f"E8 root graph (inner product = 1):")
print(f"  Degrees: min={min(E8_degrees)}, max={max(E8_degrees)}")
if len(set(E8_degrees)) == 1:
    print(f"  All degrees = {E8_degrees[0]} → regular graph!")
    print(f"  Total edges = {sum(E8_degrees) // 2}")

# Compare with W33
print(f"\nW33:")
print(f"  Degrees: all = 12")
print(f"  Total edges = {len(edges)}")

# Hmm, degrees don't match (E8 root graph has degree 56, W33 has degree 12)
# But maybe there's a QUOTIENT structure?

print("\n" + "=" * 70)
print("THE QUOTIENT BIJECTION")
print("=" * 70)

"""
W33 has 240 edges, degree 12
E8 root graph has 240 vertices, degree 56

56 / 12 ≈ 4.67 (not integer)

But wait - what if we consider ORIENTED edges?
240 edges → 480 oriented edges
E8: 240 roots with degree 56 → 240 × 56 / 2 = 6720 edges

Hmm, that doesn't match either.

NEW APPROACH: The bijection might not preserve graph structure directly.
Instead, it might preserve GROUP STRUCTURE.

W(E6) = Sp(4,3) acts transitively on:
- 240 W33 edges (stabilizer of order 216)
- Some 240-element set in E8 structure (need to find!)

Could the bijection be: Pick a base point and extend by group action?
"""

# Let's check edge stabilizer sizes
# |W(E6)| = 51840
# 51840 / 240 = 216

# In E8, what has stabilizer of order 216 under W(E6)?
# Note: W(E6) is a subgroup of W(E8)
# |W(E8)| = 696729600
# |W(E8)| / |W(E6)| = 696729600 / 51840 = 13440

print("|W(E8)| / |W(E6)| = 696729600 / 51840 =", 696729600 // 51840)

# 13440 = 56 × 240 = degree × |roots|/2
# This is interesting!

print("13440 = 56 × 240 =", 56 * 240)
print("56 = degree of E8 root in root graph")
print("240 = number of E8 roots = number of W33 edges")

print("\n" + "=" * 70)
print("BREAKTHROUGH: THE COVERING MAP")
print("=" * 70)

"""
INSIGHT: The numbers suggest a COVERING MAP structure!

W(E8) / W(E6) = 13440
E8 roots = 240
Root degree = 56

13440 / 240 = 56 ✓

So W(E8) acts on E8 roots with stabilizer of order 696729600/240 = 2903040

2903040 / 51840 = 56

This means: W(E6) "fits" 56 times into the E8 root stabilizer!

THE MAP:
E8 root stabilizer in W(E8) has order 2903040
W(E6) is a subgroup of W(E8) of index 13440
Each E8 root stabilizer contains W(E6)-cosets

This is getting complicated. Let me try a more direct approach.
"""

# Direct approach: Just try to find SOME bijection with nice properties

# Attempt 1: Lexicographic matching
# Sort both sets and pair them up

vertices_lifted = [lift_gf3_to_Z(v) for v in vertices]


# Sort W33 edges by their lifted concatenation
def edge_to_8vec(e):
    vi, wi = e
    v = vertices_lifted[vi]
    w = vertices_lifted[wi]
    return v + w  # Concatenation


edge_8vecs = [(edge_to_8vec(e), i) for i, e in enumerate(edges)]
edge_8vecs_sorted = sorted(edge_8vecs)

# Sort E8 roots
E8_sorted = sorted(enumerate(E8_roots), key=lambda x: x[1])

print("Attempting lexicographic bijection...")
print("-" * 70)

# Show first few pairings
for i in range(10):
    edge_vec, edge_idx = edge_8vecs_sorted[i]
    _, e8_root = E8_sorted[i]

    vi, wi = edges[edge_idx]
    v, w = vertices[vi], vertices[wi]

    print(f"  Edge {edge_idx}: {v} ⊥ {w} → {edge_vec}")
    print(f"  E8 root: {e8_root}")

    # Check if they're "close" in some sense
    dist = np.sqrt(sum((a - b) ** 2 for a, b in zip(edge_vec, e8_root)))
    print(f"  Distance: {dist:.4f}")
    print()

print("\n" + "=" * 70)
print("THE INVARIANT APPROACH: GRAM MATRIX")
print("=" * 70)

"""
If the bijection preserves some structure, then the GRAM MATRICES should be related.

For W33 edges: G_W[i,j] = some function of edges i and j
For E8 roots: G_E[i,j] = ⟨r_i, r_j⟩

If bijection φ: edges → roots preserves structure, then
G_W ≈ G_E (up to some transformation)
"""

# Compute Gram matrix for W33 edges (using lifted vectors)
print("Computing Gram matrices...")

# This is 240 × 240, might be slow
sample_size = 50
sample_edges = edges[:sample_size]
sample_E8 = E8_roots[:sample_size]


# W33 edge Gram matrix (using concatenated lifted vectors)
def edge_gram(e1, e2):
    v1 = lift_gf3_to_Z(vertices[e1[0]]) + lift_gf3_to_Z(vertices[e1[1]])
    v2 = lift_gf3_to_Z(vertices[e2[0]]) + lift_gf3_to_Z(vertices[e2[1]])
    return sum(a * b for a, b in zip(v1, v2))


G_W = np.array([[edge_gram(e1, e2) for e2 in sample_edges] for e1 in sample_edges])

# E8 root Gram matrix
G_E = np.array([[inner(r1, r2) for r2 in sample_E8] for r1 in sample_E8])

print(f"W33 edge Gram matrix (sample): shape {G_W.shape}")
print(f"  Diagonal entries: {set(G_W.diagonal())}")
print(
    f"  Off-diagonal range: [{G_W[G_W != G_W.diagonal()].min()}, {G_W[G_W != G_W.diagonal()].max()}]"
)

print(f"\nE8 root Gram matrix (sample): shape {G_E.shape}")
print(f"  Diagonal entries: {set(G_E.diagonal())}")
print(
    f"  Off-diagonal range: [{G_E[~np.eye(sample_size, dtype=bool)].min()}, {G_E[~np.eye(sample_size, dtype=bool)].max()}]"
)

# Eigenvalue comparison
eigW = np.linalg.eigvalsh(G_W)
eigE = np.linalg.eigvalsh(G_E)

print(f"\nW33 edge Gram eigenvalues (top 5): {sorted(eigW, reverse=True)[:5]}")
print(f"E8 root Gram eigenvalues (top 5): {sorted(eigE, reverse=True)[:5]}")

print("\n" + "=" * 70)
print("THE MOMENT OF TRUTH: TRYING RESCALED BIJECTIONS")
print("=" * 70)

"""
The Gram matrices have different scales.
- W33 edge diagonals: various (depends on lifting)
- E8 root diagonals: all 2

Try to find a RESCALING that makes them compatible.
"""


# Rescale W33 edges so diagonal = 2 (like E8)
def rescale_edge(e):
    v1 = np.array(lift_gf3_to_Z(vertices[e[0]]))
    v2 = np.array(lift_gf3_to_Z(vertices[e[1]]))
    vec = np.concatenate([v1, v2])
    norm = np.linalg.norm(vec)
    if norm > 0:
        return vec * np.sqrt(2) / norm
    return vec


print("Rescaling W33 edge vectors to have norm² = 2...")

rescaled_edges = [rescale_edge(e) for e in edges]


# Check how close rescaled edges are to E8 roots
def closest_E8_root(vec):
    min_dist = float("inf")
    best_root = None
    for r in E8_roots:
        dist = np.linalg.norm(vec - np.array(r))
        if dist < min_dist:
            min_dist = dist
            best_root = r
    return best_root, min_dist


print("\nFirst 10 rescaled edges and nearest E8 roots:")
for i in range(10):
    vec = rescaled_edges[i]
    root, dist = closest_E8_root(vec)
    print(f"  Edge {i}: dist to nearest E8 root = {dist:.4f}")

# Distribution of distances
distances = [closest_E8_root(v)[1] for v in rescaled_edges[:50]]
print(
    f"\nDistance distribution (first 50): min={min(distances):.4f}, max={max(distances):.4f}"
)
print("\n" + "=" * 70)
print("ATTEMPTING OPTIMAL MATCHING VIA HUNGARIAN ALGORITHM")
print("=" * 70)

# build cost matrix between rescaled edges and E8 roots (squared distance)
cost_matrix = np.zeros((len(edges), len(E8_roots)))
for i, vec in enumerate(rescaled_edges):
    for j, root in enumerate(E8_roots):
        cost_matrix[i, j] = np.linalg.norm(vec - np.array(root)) ** 2

row_ind, col_ind = linear_sum_assignment(cost_matrix)
total_cost = cost_matrix[row_ind, col_ind].sum()
print(f"Optimal total squared distance: {total_cost:.6f}")
print(f"Average squared distance per mapping: {total_cost/len(edges):.6f}")
zero_matches = sum(1 for d in cost_matrix[row_ind, col_ind] if d < 1e-6)
print(f"Zero distance matches: {zero_matches}")

print("\nSome sample mappings from optimal assignment:")
for k in range(10):
    i = row_ind[k]
    j = col_ind[k]
    print(f"  Edge {i} -> Root {j}, dist^2 = {cost_matrix[i,j]:.6f}")
print("\n" + "=" * 70)
print("SYNTHESIS: WHAT WE'VE LEARNED")
print("=" * 70)

print(
    """
═══════════════════════════════════════════════════════════════════════
                        CURRENT UNDERSTANDING
═══════════════════════════════════════════════════════════════════════

1. DIRECT COORDINATE LIFTS DON'T WORK
   - GF(3) → {-1, 0, 1} lift gives vectors NOT in E8 lattice
   - Rescaling doesn't give exact E8 roots

2. THE BIJECTION IS NOT "NAIVE"
   - It's not a simple coordinate map
   - Must involve deeper group-theoretic structure

3. THE KEY NUMBERS:
   - 240 = |edges| = |E8 roots|
   - 40 = |vertices| = gcd(80 Plücker, 120 root pairs)
   - 80 = |Plücker classes| = 2 × 40
   - 120 = |E8 root pairs| = 3 × 40

4. THE STRUCTURE:
   - W33 edges → 80 Plücker classes (fiber size varies: 1-5)
   - E8 roots → 120 pairs (fiber size always 2)
   - Both built on "base" of size 40!

5. THE GROUP ACTION:
   - W(E6) = Sp(4,3) acts on both structures
   - |W(E6)| = 51840 = 240 × 216 = 80 × 648 = 40 × 1296

6. THE BIJECTION EXISTS (by counting) BUT:
   - Finding it explicitly requires understanding the W(E6) orbits
   - May need to use representation theory
   - The "fiber" structures must align somehow

═══════════════════════════════════════════════════════════════════════
                            NEXT STEPS
═══════════════════════════════════════════════════════════════════════

A. Find the W(E6) orbits on E8 roots explicitly
B. Match these orbits to W33 edge orbits
C. Use the orbit-stabilizer theorem to construct bijection
D. Verify the bijection preserves some invariant (Gram matrix?)

THE BIJECTION IS THERE - WE JUST NEED TO FIND ITS EXACT FORM!
═══════════════════════════════════════════════════════════════════════
"""
)

print("=" * 70)
print("EXACT BIJECTION HUNT COMPLETE")
print("=" * 70)
