"""
HYBRID_BIJECTION_CONSTRUCTION.py
=================================

BREAKTHROUGH SYNTHESIS:
- diff_pad: 52 exact E8 roots (difference, zero-padded)
- diff_double: 24 exact E8 roots (difference, doubled)
- concat: 4 exact E8 roots (concatenation)
- TOTAL: 52 + 24 + 4 = 80 (but there might be overlap!)

The bijection is PIECEWISE - different strategies for different edges!

We need 240 total. Let's construct the full bijection.
"""

from collections import defaultdict
from itertools import combinations, product

import numpy as np

print("=" * 70)
print("HYBRID BIJECTION CONSTRUCTION")
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


# ===== Build E8 roots =====
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
E8_root_set = set(E8_roots)


def lift_gf3(v):
    return tuple(c if c <= 1 else c - 3 for c in v)


def is_E8_root(vec, tol=1e-10):
    # Convert to tuple for comparison
    vec_tuple = tuple(float(x) for x in vec)
    for r in E8_roots:
        if all(abs(a - b) < tol for a, b in zip(vec_tuple, r)):
            return True, r
    return False, None


print(f"\nW33: {len(vertices)} vertices, {len(edges)} edges")
print(f"E8: {len(E8_roots)} roots")


# ===== STRATEGY 1: diff_pad (52 matches) =====
# v - w, padded with zeros → D4 subroot system
def lift_diff_pad(edge_idx):
    vi, wi = edges[edge_idx]
    v = np.array(lift_gf3(vertices[vi]))
    w = np.array(lift_gf3(vertices[wi]))
    d = v - w
    return np.concatenate([d, np.zeros(4)])


# ===== STRATEGY 2: diff_pad_right (might give more?) =====
def lift_diff_pad_right(edge_idx):
    vi, wi = edges[edge_idx]
    v = np.array(lift_gf3(vertices[vi]))
    w = np.array(lift_gf3(vertices[wi]))
    d = v - w
    return np.concatenate([np.zeros(4), d])


# ===== STRATEGY 3: diff_double (24 matches) =====
def lift_diff_double(edge_idx):
    vi, wi = edges[edge_idx]
    v = np.array(lift_gf3(vertices[vi]))
    w = np.array(lift_gf3(vertices[wi]))
    d = v - w
    return np.concatenate([d, d])


# ===== STRATEGY 4: concat (4 matches) =====
def lift_concat(edge_idx):
    vi, wi = edges[edge_idx]
    v = np.array(lift_gf3(vertices[vi]))
    w = np.array(lift_gf3(vertices[wi]))
    return np.concatenate([v, w])


# ===== NEW STRATEGIES to try =====
# Sum instead of diff
def lift_sum_pad(edge_idx):
    vi, wi = edges[edge_idx]
    v = np.array(lift_gf3(vertices[vi]))
    w = np.array(lift_gf3(vertices[wi]))
    s = v + w
    return np.concatenate([s, np.zeros(4)])


def lift_sum_double(edge_idx):
    vi, wi = edges[edge_idx]
    v = np.array(lift_gf3(vertices[vi]))
    w = np.array(lift_gf3(vertices[wi]))
    s = v + w
    return np.concatenate([s, s])


# Scaled versions
def lift_diff_pad_scaled(edge_idx, scale=1 / np.sqrt(2)):
    return lift_diff_pad(edge_idx) * scale


def lift_half_int(edge_idx):
    """Try to get half-integer type roots"""
    vi, wi = edges[edge_idx]
    v = np.array(lift_gf3(vertices[vi]))
    w = np.array(lift_gf3(vertices[wi]))
    # Scale to half-integers
    combined = np.concatenate([v, w]) * 0.5
    return combined


# ===== Count matches for all strategies =====
print("\n" + "=" * 70)
print("TESTING ALL STRATEGIES FOR EXACT MATCHES")
print("=" * 70)

strategies = {
    "diff_pad": lift_diff_pad,
    "diff_pad_right": lift_diff_pad_right,
    "diff_double": lift_diff_double,
    "concat": lift_concat,
    "sum_pad": lift_sum_pad,
    "sum_double": lift_sum_double,
    "half_int": lift_half_int,
}

strategy_matches = {}
for name, lift_fn in strategies.items():
    matches = []
    for i in range(len(edges)):
        vec = lift_fn(i)
        is_root, root = is_E8_root(vec)
        if is_root:
            matches.append((i, root))
    strategy_matches[name] = matches
    print(f"{name}: {len(matches)} exact E8 root matches")

# ===== Check for overlaps =====
print("\n" + "=" * 70)
print("CHECKING OVERLAPS AND BUILDING UNION")
print("=" * 70)

all_matched_edges = set()
all_matched_roots = set()
edge_to_root = {}

for name in ["diff_pad", "diff_double", "concat"]:  # Primary strategies
    for edge_idx, root in strategy_matches[name]:
        if edge_idx not in edge_to_root:
            edge_to_root[edge_idx] = (name, root)
            all_matched_edges.add(edge_idx)
            all_matched_roots.add(root)

print(f"Total unique edges matched: {len(all_matched_edges)}")
print(f"Total unique roots produced: {len(all_matched_roots)}")

# Check which edges are NOT matched
unmatched_edges = set(range(len(edges))) - all_matched_edges
print(f"Unmatched edges: {len(unmatched_edges)}")

# Check which roots are NOT produced
unmatched_roots = E8_root_set - all_matched_roots
print(f"Roots not yet assigned: {len(unmatched_roots)}")

# ===== Analyze the matched roots =====
print("\n" + "=" * 70)
print("ANALYZING MATCHED ROOTS")
print("=" * 70)

int_roots = [r for r in all_matched_roots if all(c == int(c) for c in r)]
half_roots = [r for r in all_matched_roots if all(c != int(c) for c in r)]

print(f"Integer-type roots matched: {len(int_roots)}")
print(f"Half-integer-type roots matched: {len(half_roots)}")

# Count by D4 structure
# D4 in first 4 coords: roots with last 4 = 0
D4_first = [
    r
    for r in all_matched_roots
    if r[4:] == (0, 0, 0, 0) or r[4:] == (0.0, 0.0, 0.0, 0.0)
]
D4_second = [
    r
    for r in all_matched_roots
    if r[:4] == (0, 0, 0, 0) or r[:4] == (0.0, 0.0, 0.0, 0.0)
]

print(f"Roots in D4 (first 4 coords): {len(D4_first)}")
print(f"Roots in D4 (last 4 coords): {len(D4_second)}")

# ===== Try to match remaining edges =====
print("\n" + "=" * 70)
print("ATTEMPTING TO MATCH REMAINING EDGES")
print("=" * 70)


# More aggressive strategies for unmatched edges
def lift_diff_scaled_variants(edge_idx):
    """Try multiple scalings of diff"""
    vi, wi = edges[edge_idx]
    v = np.array(lift_gf3(vertices[vi]))
    w = np.array(lift_gf3(vertices[wi]))
    d = v - w

    variants = []
    # Scale by 1/2 for half-integer type
    variants.append(np.concatenate([d * 0.5, d * 0.5]))  # (d/2, d/2)
    variants.append(np.concatenate([d * 0.5, -d * 0.5]))  # (d/2, -d/2)
    variants.append(
        np.concatenate([(v + w) * 0.5, (v - w) * 0.5])
    )  # ((v+w)/2, (v-w)/2)

    return variants


def lift_concat_variants(edge_idx):
    """Try variants of concatenation"""
    vi, wi = edges[edge_idx]
    v = np.array(lift_gf3(vertices[vi]))
    w = np.array(lift_gf3(vertices[wi]))

    variants = []
    variants.append(np.concatenate([v, -w]))  # (v, -w)
    variants.append(np.concatenate([-v, w]))  # (-v, w)
    variants.append(np.concatenate([-v, -w]))  # (-v, -w)
    variants.append(np.concatenate([w, v]))  # (w, v)
    variants.append(np.concatenate([w, -v]))  # (w, -v)
    variants.append(np.concatenate([-w, v]))  # (-w, v)
    variants.append(np.concatenate([-w, -v]))  # (-w, -v)

    return variants


def lift_half_int_variants(edge_idx):
    """Try half-integer embeddings"""
    vi, wi = edges[edge_idx]
    v = np.array(lift_gf3(vertices[vi]))
    w = np.array(lift_gf3(vertices[wi]))

    variants = []
    # Replace 0 with ±0.5 to get half-integer type
    for sv in [0.5, -0.5]:
        for sw in [0.5, -0.5]:
            vec = np.concatenate([v, w]).astype(float)
            for i in range(8):
                if vec[i] == 0:
                    vec[i] = sv if i < 4 else sw
            # Adjust for even number of minus signs
            if sum(1 for x in vec if x < 0) % 2 != 0:
                # Flip one sign
                for i in range(8):
                    if abs(vec[i]) == 0.5:
                        vec[i] = -vec[i]
                        break
            variants.append(vec)

    return variants


# Try all variants on unmatched edges
new_matches = {}
for edge_idx in list(unmatched_edges)[:50]:  # Test first 50 unmatched
    found = False

    # Try diff scaled variants
    for vec in lift_diff_scaled_variants(edge_idx):
        is_root, root = is_E8_root(vec)
        if is_root and root not in all_matched_roots:
            new_matches[edge_idx] = ("diff_scaled", root)
            all_matched_roots.add(root)
            found = True
            break

    if found:
        continue

    # Try concat variants
    for vec in lift_concat_variants(edge_idx):
        is_root, root = is_E8_root(vec)
        if is_root and root not in all_matched_roots:
            new_matches[edge_idx] = ("concat_var", root)
            all_matched_roots.add(root)
            found = True
            break

print(f"Additional matches found: {len(new_matches)}")
print(f"Total matched now: {len(edge_to_root) + len(new_matches)}")

# ===== The key insight: Scale factor =====
print("\n" + "=" * 70)
print("THE KEY INSIGHT: GLOBAL SCALE + ROTATION")
print("=" * 70)

"""
The problem might be that we need a SINGLE transformation
that maps ALL edges to roots, not multiple ad-hoc strategies.

KEY OBSERVATION:
- diff_pad gives 52 roots (all in D4 subsystem, first 4 coords)
- diff_pad_right gives another set (D4 in last 4 coords)
- Together these should give... let's count

D4 has 24 roots. With two D4s and orientation:
24 + 24 = 48 (but we got 52?)

Actually diff vectors can have norm² up to 4:
  ||v - w||² ≤ 2 × max vertex norm² = 2 × 4 = 8

For E8 roots in D4, we need ||d||² = 2.
So diff_pad only works when ||v - w||² = 2.
"""

# Count edges by difference norm²
diff_norm_sq_counts = defaultdict(list)
for i, (vi, wi) in enumerate(edges):
    v = np.array(lift_gf3(vertices[vi]))
    w = np.array(lift_gf3(vertices[wi]))
    d = v - w
    norm_sq = int(np.dot(d, d))
    diff_norm_sq_counts[norm_sq].append(i)

print("\nEdges by ||v - w||²:")
for n in sorted(diff_norm_sq_counts.keys()):
    count = len(diff_norm_sq_counts[n])
    print(f"  ||d||² = {n}: {count} edges")

# ||d||² = 2 edges → diff_pad gives D4 roots!
norm2_edges = diff_norm_sq_counts[2]
print(f"\n||d||² = 2: {len(norm2_edges)} edges")
print("These map via diff_pad to D4 roots (24 total).")

# But we also have diff_pad_right which gives another D4!
# And diff_double which gives diagonal embedding.

# ===== The D4 × D4 structure =====
print("\n" + "=" * 70)
print("THE D4 × D4 STRUCTURE IN E8")
print("=" * 70)

"""
E8 decomposes as:
  E8 = D4 × D4 + (8v, 8v) + (8s, 8s) + (8c, 8c)

where:
  - D4 × D4 = 24 + 24 = 48 roots
  - (8v, 8v) = 64 roots  (vector × vector)
  - (8s, 8s) = 64 roots  (spinor × spinor)
  - (8c, 8c) = 64 roots  (cospinor × cospinor)
  - Total: 48 + 64 + 64 + 64 = 240 ✓

This is the TRIALITY structure!

W33 edges should decompose similarly:
  - 52 edges → D4 in first 4 coords (via diff_pad)
  - Some edges → D4 in last 4 coords
  - Remaining edges → "mixed" type (8 × 8 = 64 each?)
"""

# Verify D4 structure
D4_roots_first = [r for r in E8_roots if r[4:] == (0, 0, 0, 0)]
D4_roots_second = [r for r in E8_roots if r[:4] == (0, 0, 0, 0)]
mixed_roots = [r for r in E8_roots if r[:4] != (0, 0, 0, 0) and r[4:] != (0, 0, 0, 0)]

print(f"E8 structure:")
print(f"  D4 in first 4 coords: {len(D4_roots_first)} roots")
print(f"  D4 in last 4 coords: {len(D4_roots_second)} roots")
print(f"  Mixed: {len(mixed_roots)} roots")
print(f"  Total: {len(D4_roots_first) + len(D4_roots_second) + len(mixed_roots)}")

# The mixed roots are the (8v,8v), (8s,8s), (8c,8c)
# These are half-integer type!
int_mixed = [r for r in mixed_roots if all(c == int(c) for c in r)]
half_mixed = [r for r in mixed_roots if all(c != int(c) for c in r)]
print(f"\n  Mixed integer: {len(int_mixed)}")  # These are e.g. (1,1,0,0,1,1,0,0)
print(f"  Mixed half-int: {len(half_mixed)}")  # These are the ±½ ones

# ===== NEW STRATEGY: Match edge types to root types =====
print("\n" + "=" * 70)
print("MATCHING EDGE TYPES TO ROOT TYPES")
print("=" * 70)

# Type 1: ||d||² = 2 → D4 roots
# Type 2: ||d||² = 1 → ???
# Type 3: ||d||² = 4,5,6,... → mixed roots?

# Actually let's check ||v||² + ||w||² for edges
concat_norm_sq_counts = defaultdict(list)
for i, (vi, wi) in enumerate(edges):
    v = np.array(lift_gf3(vertices[vi]))
    w = np.array(lift_gf3(vertices[wi]))
    concat = np.concatenate([v, w])
    norm_sq = int(np.dot(concat, concat))
    concat_norm_sq_counts[norm_sq].append(i)

print("\nEdges by concatenation norm² (||v||² + ||w||²):")
for n in sorted(concat_norm_sq_counts.keys()):
    count = len(concat_norm_sq_counts[n])
    # Also show how many match roots directly
    direct_matches = 0
    for idx in concat_norm_sq_counts[n]:
        vec = lift_concat(idx)
        is_root, _ = is_E8_root(vec)
        if is_root:
            direct_matches += 1
    print(f"  norm² = {n}: {count} edges ({direct_matches} direct E8 matches)")

# ===== CRITICAL INSIGHT =====
print("\n" + "=" * 70)
print("CRITICAL INSIGHT: THE BIJECTION STRUCTURE")
print("=" * 70)

print(
    """
═══════════════════════════════════════════════════════════════════════
                        THE BIJECTION STRUCTURE
═══════════════════════════════════════════════════════════════════════

Edge norm² distribution: {2:4, 3:24, 4:28, 5:48, 6:96, 7:32, 8:8}
                         Total: 4+24+28+48+96+32+8 = 240 ✓

E8 root types:
- 112 integer-type (exactly 2 nonzero entries ±1)
- 128 half-integer-type (all entries ±½, even # of minus)

THE MAPPING (CONJECTURE):

1. norm² = 2 edges (4 total):
   → E8 integer roots of form (±1,0,0,0,±1,0,0,0)
   via direct concatenation

2. norm² = 3,4 edges (24+28 = 52 total):
   → Remaining E8 integer roots (112 - 4 = 108... hmm)
   via some transformation?

3. norm² ≥ 5 edges (48+96+32+8 = 184 total):
   → E8 half-integer roots (128 total)
   via scaling by 1/√2 or similar?

But 52 + 184 = 236 ≠ 240, so this doesn't work directly.

THE KEY: We need a UNIFORM map that works for all edges!

═══════════════════════════════════════════════════════════════════════
"""
)

# ===== Try the uniform scaling approach =====
print("\n" + "=" * 70)
print("UNIFORM SCALING APPROACH")
print("=" * 70)

# If we rescale ALL edges to have norm² = 2, how close do they get?
print("For each edge, rescale to norm² = 2 and find nearest E8 root:")

closest_distances = []
for i, (vi, wi) in enumerate(edges):
    v = np.array(lift_gf3(vertices[vi]))
    w = np.array(lift_gf3(vertices[wi]))
    vec = np.concatenate([v, w])
    norm = np.linalg.norm(vec)
    vec_scaled = vec * np.sqrt(2) / norm if norm > 0 else vec

    # Find closest E8 root
    min_dist = float("inf")
    for r in E8_roots:
        dist = np.linalg.norm(vec_scaled - np.array(r))
        if dist < min_dist:
            min_dist = dist
    closest_distances.append((i, min_dist, norm))

# Sort by distance
closest_distances.sort(key=lambda x: x[1])

print("\nTop 20 closest (after scaling):")
for i, (edge_idx, dist, orig_norm) in enumerate(closest_distances[:20]):
    vi, wi = edges[edge_idx]
    print(f"  Edge {edge_idx}: dist={dist:.6f}, orig_norm={orig_norm:.3f}")

print("\nBottom 20 (farthest):")
for i, (edge_idx, dist, orig_norm) in enumerate(closest_distances[-20:]):
    vi, wi = edges[edge_idx]
    print(f"  Edge {edge_idx}: dist={dist:.6f}, orig_norm={orig_norm:.3f}")

# How many are "close enough"?
thresholds = [0.001, 0.1, 0.3, 0.5, 0.7, 0.9, 1.0, 1.1]
for t in thresholds:
    close_count = sum(1 for _, dist, _ in closest_distances if dist < t)
    print(f"\nEdges with distance < {t}: {close_count}")

print("\n" + "=" * 70)
print("HYBRID BIJECTION CONSTRUCTION COMPLETE")
print("=" * 70)
