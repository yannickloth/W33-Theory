#!/usr/bin/env python3
"""
FINAL_ATTACK.py - The definitive analysis

We've learned:
1. W33 has 40 lines × 6 edges = 240 edges (perfect partition)
2. E8 has 1120 A2 systems, but they can't partition the 240 roots into 40 disjoint sets
3. The bijection φ: Edges(W33) → Roots(E8) cannot be "A2-based"

NEW APPROACH:
What if we use the VERTICES (points) of W33, not the lines?

Each W33 vertex has degree 12 (connected to 12 other vertices)
12 edges per vertex, but each edge is counted twice
Actually: 40 vertices × 12 = 480 = 2 × 240 ✓

What if the bijection maps:
- 40 W33 vertices → 40 "special configurations" in E8
- Each configuration contains exactly 6 E8 roots
- Together they partition all 240 roots?

But we already showed this fails for A2 systems. What else has size 6?
"""

from collections import Counter, defaultdict
from itertools import combinations, permutations, product

import numpy as np

print("=" * 70)
print("FINAL ATTACK: THE DEFINITIVE ANALYSIS")
print("=" * 70)

# =============================================================================
# Build E8 roots
# =============================================================================

e8_roots = []
for i in range(8):
    for j in range(i + 1, 8):
        for s1 in [1, -1]:
            for s2 in [1, -1]:
                root = [0] * 8
                root[i] = s1
                root[j] = s2
                e8_roots.append(tuple(root))

for signs in product([1, -1], repeat=8):
    if sum(1 for s in signs if s == -1) % 2 == 0:
        root = tuple(s / 2 for s in signs)
        e8_roots.append(root)

e8_roots_set = set(e8_roots)
print(f"E8 roots: {len(e8_roots)}")

# =============================================================================
# INSIGHT: Use the 40 points from the E6 × SU(3) decomposition
# =============================================================================

print("\n" + "=" * 70)
print("NEW INSIGHT: THE 40 = 27 + 13 DECOMPOSITION?")
print("=" * 70)

# Under E6 × SU(3), the 240 roots decompose as:
# 72 (E6) + 6 (SU(3)) + 81 (27×3) + 81 (27̄×3̄)

# Let's look at the (27,3) component more carefully
# These are 81 roots = 27 × 3
# The "27" are weights of E6 fundamental rep (27 lines!)
# The "3" are the SU(3) colors

# Can we identify the 27 within the 81?


def classify_e8_root(root):
    """Classify E8 root by its E6×SU(3) decomposition."""
    r = np.array(root)
    last3 = r[5:]
    last3_sum = sum(last3)

    # E6 roots: last 3 coords all equal
    if last3[0] == last3[1] == last3[2]:
        if abs(last3[0]) <= 0.5:
            return "E6"

    # SU(3) roots: first 5 coords are 0
    if np.allclose(r[:5], 0):
        return "SU3"

    # (27,3) vs (27̄,3̄)
    if last3_sum < 0 or (last3_sum == 0 and last3[0] < 0):
        return "27x3"
    else:
        return "27x3_bar"


# Classify all roots
root_classes = {r: classify_e8_root(r) for r in e8_roots}
class_counts = Counter(root_classes.values())
print(f"Root classification: {class_counts}")

# Get the (27,3) roots
roots_27x3 = [r for r in e8_roots if root_classes[r] == "27x3"]
roots_27x3_bar = [r for r in e8_roots if root_classes[r] == "27x3_bar"]
roots_e6 = [r for r in e8_roots if root_classes[r] == "E6"]
roots_su3 = [r for r in e8_roots if root_classes[r] == "SU3"]

print(f"\n(27,3): {len(roots_27x3)}")
print(f"(27̄,3̄): {len(roots_27x3_bar)}")
print(f"E6: {len(roots_e6)}")
print(f"SU(3): {len(roots_su3)}")

# =============================================================================
# ANALYZE: What are the "27" in (27,3)?
# =============================================================================

print("\n" + "=" * 70)
print("ANALYZING THE 27 IN (27,3)")
print("=" * 70)

# The 81 roots in (27,3) should partition into 27 triplets by SU(3) color
# Within each triplet, the roots differ by SU(3) roots

# Two roots are in the same "27-class" if their difference is an SU(3) root (or 0)
# The SU(3) roots are the 6 permutations of (0,0,0,0,0, 1,-1,0) etc.


def get_27_class(root, roots_su3):
    """Get the "27-class" identifier for a (27,3) root."""
    # Project out the SU(3) part
    r = np.array(root)
    # The SU(3) acts on last 3 coords
    # The "27" part is the first 5 coords + the sum of last 3 coords (the E6 weight)
    first5 = tuple(r[:5])
    last3_sum = sum(r[5:])
    return (first5, last3_sum)


# Group (27,3) roots by 27-class
class_27_groups = defaultdict(list)
for root in roots_27x3:
    cls = get_27_class(root, roots_su3)
    class_27_groups[cls].append(root)

print(f"Number of 27-classes: {len(class_27_groups)}")
sizes = [len(v) for v in class_27_groups.values()]
print(f"Sizes of 27-classes: {Counter(sizes)}")

if len(class_27_groups) == 27 and all(len(v) == 3 for v in class_27_groups.values()):
    print("\n*** CONFIRMED: 81 = 27 × 3 structure! ***")

# =============================================================================
# INSIGHT: The 40 = 27 + 12 + 1 structure?
# =============================================================================

print("\n" + "=" * 70)
print("EXPLORING THE 40 STRUCTURE")
print("=" * 70)

print(
    """
We have:
- 27 "lines" from the (27,3) structure
- 72 E6 roots = ? × ?
- 6 SU(3) roots = 1 × 6

The 72 E6 roots:
- E6 has rank 6, so 72 = 2 × 36 positive/negative
- Or 72 = 12 × 6 (12 classes with 6 roots each?)

Let me check if 72 E6 roots partition into 12 sets of 6:
- Actually, under A5 ⊂ E6, there's a natural partition!
"""
)

# =============================================================================
# ANALYZE E6 ROOT STRUCTURE
# =============================================================================

print("\n" + "=" * 70)
print("ANALYZING E6 ROOT STRUCTURE")
print("=" * 70)

# The 72 E6 roots
# These have last 3 coords all equal: 0, 1/2, or -1/2

# Group by the last 3 coord value
e6_by_tail = defaultdict(list)
for root in roots_e6:
    tail = root[5]  # Last 3 are all equal
    e6_by_tail[tail].append(root)

print(f"E6 roots grouped by tail value:")
for tail, roots in sorted(e6_by_tail.items()):
    print(f"  Tail={tail}: {len(roots)} roots")

# The tail=0 roots are the D5 subsystem (or A5)
# Let's see if 72 = some nice product

# Actually: 72 = 72 (rank 6 root system, no nice 6-partition)
# But: 72 = 12 × 6 would give us 12 classes

# Let me try a different decomposition
# E6 → A5 × A1 (or D5 × U(1))

# Under A5 (= SU(6)):
# E6 decomposes as: adjoint + ...

print(
    """
E6 ROOT ANALYSIS:
- 72 roots total
- Under E6 → D5: 72 = 40 (D5 vector) + 32 (spinor)
- D5 has 40 roots (same as W33 vertices!)

WAIT - D5 has 40 roots!
And Sp(4) (the compact form of what we've been studying) is related to D5!
"""
)

# D5 roots: permutations of (±1, ±1, 0, 0, 0) - that's 40!
# But wait, the FULL D5 root system has 40 roots
# Let's check: D_n has 2n(n-1) roots
# D5: 2 × 5 × 4 = 40 ✓

print("\nD5 has exactly 40 roots!")
print("This matches the 40 vertices of W33!")

# =============================================================================
# THE KEY DISCOVERY
# =============================================================================

print("\n" + "=" * 70)
print("*** THE KEY DISCOVERY ***")
print("=" * 70)

print(
    """
CRITICAL OBSERVATION:
=====================

D5 = SO(10) has exactly 40 roots!
W33 has exactly 40 vertices!

Under the chain E8 ⊃ E6 ⊃ D5:
- E8 has 240 roots
- E6 ⊂ E8 (as a maximal subgroup), E6 has 72 roots
- D5 ⊂ E6 (as a maximal subgroup), D5 has 40 roots

The 40 roots of D5 can be viewed as:
- 40 vertices of a graph
- This graph might BE W33 or closely related!

TESTING: Is the D5 root graph isomorphic to W33?

D5 root graph:
- Vertices: 40 roots of D5
- Edges: when two roots have inner product = ±1 (adjacent in some sense)

Let me check the structure...
"""
)

# =============================================================================
# CHECK: Is D5 root graph related to W33?
# =============================================================================

print("\n" + "=" * 70)
print("CHECKING D5 ROOT GRAPH STRUCTURE")
print("=" * 70)

# D5 roots: (±1, ±1, 0, 0, 0) and permutations, in R^5
d5_roots = []
for i in range(5):
    for j in range(i + 1, 5):
        for s1 in [1, -1]:
            for s2 in [1, -1]:
                root = [0] * 5
                root[i] = s1
                root[j] = s2
                d5_roots.append(tuple(root))

print(f"D5 roots: {len(d5_roots)}")

# D5 root graph: edge when inner product = 1 or -1 (orthogonally adjacent)
# Actually, in the Dynkin diagram sense, roots are connected if ip = -1


# Let's check various adjacency conditions
def d5_inner_product(r1, r2):
    return sum(a * b for a, b in zip(r1, r2))


# Check ip distributions
ip_dist = Counter()
for i, r1 in enumerate(d5_roots):
    for r2 in d5_roots[i + 1 :]:
        ip = d5_inner_product(r1, r2)
        ip_dist[ip] += 1

print(f"D5 root inner product distribution: {ip_dist}")

# W33 parameters: (40, 12, 2, 4)
# So degree 12, λ=2 (common neighbors for adjacent), μ=4 (common neighbors for non-adjacent)

# For D5, let's try different adjacency conditions
for threshold in [1, -1, 0]:
    adj_d5 = {i: set() for i in range(40)}
    for i, r1 in enumerate(d5_roots):
        for j, r2 in enumerate(d5_roots):
            if i < j:
                ip = d5_inner_product(r1, r2)
                if ip == threshold:
                    adj_d5[i].add(j)
                    adj_d5[j].add(i)

    degrees = [len(adj_d5[i]) for i in range(40)]
    if len(set(degrees)) == 1:
        deg = degrees[0]
        edges = sum(degrees) // 2
        print(f"ip={threshold}: Regular degree {deg}, {edges} edges")

        # Check SRG parameters
        if deg == 12:
            # Check λ (common neighbors for adjacent)
            lambdas = []
            for i in range(40):
                for j in adj_d5[i]:
                    common = len(adj_d5[i] & adj_d5[j])
                    lambdas.append(common)
            print(f"  λ values: {Counter(lambdas)}")

# =============================================================================
# TRY: ip = ±1 (both adjacent)
# =============================================================================

print("\n" + "=" * 70)
print("TRYING ip ∈ {1, -1} ADJACENCY")
print("=" * 70)

adj_d5 = {i: set() for i in range(40)}
for i, r1 in enumerate(d5_roots):
    for j, r2 in enumerate(d5_roots):
        if i < j:
            ip = d5_inner_product(r1, r2)
            if abs(ip) == 1:
                adj_d5[i].add(j)
                adj_d5[j].add(i)

degrees = [len(adj_d5[i]) for i in range(40)]
print(f"Degree distribution: {Counter(degrees)}")

if len(set(degrees)) == 1:
    deg = degrees[0]
    edges = sum(degrees) // 2
    print(f"Regular graph with degree {deg}, {edges} edges")

    # Check SRG parameters
    lambdas = []
    mus = []
    for i in range(40):
        for j in range(40):
            if i != j:
                common = len(adj_d5[i] & adj_d5[j])
                if j in adj_d5[i]:
                    lambdas.append(common)
                else:
                    mus.append(common)

    print(f"λ (adjacent common neighbors): {Counter(lambdas)}")
    print(f"μ (non-adjacent common neighbors): {Counter(mus)}")

    if len(set(lambdas)) == 1 and len(set(mus)) == 1:
        lam = lambdas[0]
        mu = mus[0]
        print(f"\n*** SRG({40}, {deg}, {lam}, {mu}) ***")

        if (40, deg, lam, mu) == (40, 12, 2, 4):
            print("*** THIS IS W33! ***")

# =============================================================================
# CONCLUSION
# =============================================================================

print("\n" + "=" * 70)
print("CONCLUSION")
print("=" * 70)

print(
    """
FINDING:
========

The D5 root graph with adjacency ip ∈ {1, -1} has:
- 40 vertices (D5 roots)
- Some regular degree

If this matches W33's parameters (40, 12, 2, 4), then:
W33 ≅ D5 ROOT GRAPH!

This would establish:
- W33 vertices ↔ D5 roots
- The Sp(4,3) action ↔ Some subgroup of W(D5)

Since D5 ⊂ E6 ⊂ E8, this gives a chain:
W33 vertices → D5 roots → E6 roots → E8 roots

This is THE connection we've been looking for!
"""
)
