#!/usr/bin/env python3
"""
TOTALLY ISOTROPIC 2-SPACES AND THE 240 CORRESPONDENCE

Key insight from previous analysis:
- 240 edges = 40 totally isotropic 2-spaces × 6 edges per space
- Each 2-space contains 4 isotropic lines
- C(4,2) = 6 pairs of lines = 6 edges

This gives a PARTITION of the 240 edges into 40 groups of 6.

Can we find a similar structure in E8?
"""

from collections import defaultdict
from itertools import combinations, product

import numpy as np

print("=" * 70)
print("TOTALLY ISOTROPIC 2-SPACES AND E8")
print("=" * 70)

# ==============================================================
# PART 1: ENUMERATE TOTALLY ISOTROPIC 2-SPACES
# ==============================================================

print("\n" + "=" * 70)
print("PART 1: TOTALLY ISOTROPIC 2-SPACES IN W33")
print("=" * 70)

GF3 = [0, 1, 2]


def omega(u, v):
    """Symplectic form on GF(3)^4"""
    return (u[0] * v[1] - u[1] * v[0] + u[2] * v[3] - u[3] * v[2]) % 3


def normalize(p):
    """Canonical representative of line through p"""
    for i, x in enumerate(p):
        if x != 0:
            inv = pow(x, -1, 3)
            return tuple((c * inv) % 3 for c in p)
    return p


def add_GF3(u, v):
    """Vector addition in GF(3)^4"""
    return tuple((a + b) % 3 for a, b in zip(u, v))


def scalar_mult(c, v):
    """Scalar multiplication in GF(3)^4"""
    return tuple((c * x) % 3 for x in v)


# Get all lines
all_points = [p for p in product(GF3, repeat=4) if p != (0, 0, 0, 0)]
lines = list(set(normalize(p) for p in all_points))
line_to_idx = {L: i for i, L in enumerate(lines)}

print(f"Number of isotropic lines: {len(lines)}")

# Find all totally isotropic 2-spaces
# A 2-space is spanned by two independent vectors u, v with omega(u,v) = 0
# It contains 4 lines: <u>, <v>, <u+v>, <u+2v>


def get_2space_lines(u, v):
    """Get the 4 lines in the 2-space spanned by u and v"""
    space_lines = set()
    for a in GF3:
        for b in GF3:
            if a == 0 and b == 0:
                continue
            # point a*u + b*v
            p = tuple((a * u[i] + b * v[i]) % 3 for i in range(4))
            space_lines.add(normalize(p))
    return frozenset(space_lines)


# Find all totally isotropic 2-spaces
isotropic_2spaces = set()

for L1 in lines:
    for L2 in lines:
        if L1 < L2:  # avoid duplicates
            if omega(L1, L2) == 0:
                # L1 and L2 are orthogonal, span a t.i. 2-space
                space = get_2space_lines(L1, L2)
                isotropic_2spaces.add(space)

print(f"Number of totally isotropic 2-spaces: {len(isotropic_2spaces)}")

# Verify each 2-space has 4 lines
for space in isotropic_2spaces:
    assert len(space) == 4, f"2-space has {len(space)} lines, expected 4"
print("Each 2-space contains exactly 4 lines ✓")

# Each 2-space gives C(4,2) = 6 edges
total_edges_from_2spaces = len(isotropic_2spaces) * 6
print(f"Total edge count: {len(isotropic_2spaces)} × 6 = {total_edges_from_2spaces}")

# ==============================================================
# PART 2: VERIFY EDGE PARTITION
# ==============================================================

print("\n" + "=" * 70)
print("PART 2: EDGE PARTITION")
print("=" * 70)

# Build edges
edges = []
for L1 in lines:
    for L2 in lines:
        if L1 < L2 and omega(L1, L2) == 0:
            edges.append((L1, L2))

print(f"Total edges: {len(edges)}")

# Check: each edge belongs to exactly how many 2-spaces?
edge_to_2spaces = defaultdict(list)

for space in isotropic_2spaces:
    space_list = list(space)
    for i, L1 in enumerate(space_list):
        for L2 in space_list[i + 1 :]:
            edge = (min(L1, L2), max(L1, L2))
            edge_to_2spaces[edge].append(space)

# Count how many 2-spaces each edge belongs to
space_counts = [len(v) for v in edge_to_2spaces.values()]
print(f"Each edge belongs to {set(space_counts)} 2-space(s)")

if len(set(space_counts)) == 1 and space_counts[0] == 1:
    print("Each edge belongs to EXACTLY ONE 2-space!")
    print("This gives a PARTITION of 240 edges into 40 groups of 6 ✓")

# ==============================================================
# PART 3: RELATIONSHIP TO W33 VERTICES
# ==============================================================

print("\n" + "=" * 70)
print("PART 3: 2-SPACES AND VERTICES")
print("=" * 70)

print(
    f"""
We have:
  - 40 vertices (isotropic lines)
  - 40 totally isotropic 2-spaces

Is there a bijection between them?
"""
)

# Each 2-space contains 4 lines (vertices)
# Each line is in how many 2-spaces?

line_to_2spaces = defaultdict(list)
for space in isotropic_2spaces:
    for L in space:
        line_to_2spaces[L].append(space)

spaces_per_line = [len(v) for v in line_to_2spaces.values()]
print(f"Each line is in {set(spaces_per_line)} 2-space(s)")

# So each line is in 6 2-spaces
# Total incidences: 40 lines × 6 = 240
# Also: 40 2-spaces × 4 lines = 160
# Wait, these don't match...

print(f"\nIncidence count:")
print(f"  40 lines × {spaces_per_line[0]} 2-spaces = {40 * spaces_per_line[0]}")
print(f"  40 2-spaces × 4 lines = {40 * 4}")

# So each line is in 4 2-spaces, not 6
# Let me recount...
print(f"\n2-spaces per line: {spaces_per_line[0]}")

# ==============================================================
# PART 4: THE INCIDENCE STRUCTURE
# ==============================================================

print("\n" + "=" * 70)
print("PART 4: INCIDENCE STRUCTURE")
print("=" * 70)

# Build incidence matrix: lines × 2-spaces
space_list = list(isotropic_2spaces)
incidence = np.zeros((40, 40), dtype=int)

for j, space in enumerate(space_list):
    for L in space:
        i = line_to_idx[L]
        incidence[i, j] = 1

print(f"Incidence matrix shape: {incidence.shape}")
print(f"Lines per 2-space (column sum): {incidence.sum(axis=0)[0]}")
print(f"2-spaces per line (row sum): {incidence.sum(axis=1)[0]}")

# This is a (40, 40, 4, 4) design?
# Each line is in 4 2-spaces
# Each 2-space contains 4 lines
# What about pairs?


# How many 2-spaces contain both line i and line j?
def common_2spaces(i, j):
    return sum(incidence[i, k] * incidence[j, k] for k in range(40))


# For adjacent lines (omega = 0)
adj_common = []
nonadj_common = []
for i, L1 in enumerate(lines):
    for j, L2 in enumerate(lines):
        if i < j:
            n_common = common_2spaces(i, j)
            if omega(L1, L2) == 0:
                adj_common.append(n_common)
            else:
                nonadj_common.append(n_common)

print(f"\nCommon 2-spaces for adjacent lines: {set(adj_common)}")
print(f"Common 2-spaces for non-adjacent lines: {set(nonadj_common)}")

# Adjacent lines share exactly 1 2-space (the one they span!)
# Non-adjacent lines share 0 2-spaces

# ==============================================================
# PART 5: DUAL STRUCTURE
# ==============================================================

print("\n" + "=" * 70)
print("PART 5: DUAL STRUCTURE")
print("=" * 70)

print(
    """
The incidence structure has beautiful duality:
  - 40 lines (points of W33)
  - 40 totally isotropic 2-spaces (blocks)
  - Each line in 4 blocks
  - Each block contains 4 lines
  - Two adjacent lines share exactly 1 block
  - Two non-adjacent lines share 0 blocks

This is a (40, 40, 4, 4, 1) divisible design!
"""
)

# Compute block-block adjacency
# Two blocks (2-spaces) are adjacent if they share a line
block_adj = np.zeros((40, 40), dtype=int)
for i in range(40):
    for j in range(i + 1, 40):
        shared = sum(incidence[k, i] * incidence[k, j] for k in range(40))
        if shared > 0:
            block_adj[i, j] = block_adj[j, i] = 1

block_degree = block_adj.sum(axis=1)
print(f"Block graph degree: {block_degree[0]}")

# This might be W33 itself!
# Check if it's regular
print(f"Block degrees: min={block_degree.min()}, max={block_degree.max()}")

# ==============================================================
# PART 6: E8 ROOT PARTITIONS
# ==============================================================

print("\n" + "=" * 70)
print("PART 6: E8 ROOT PARTITIONS")
print("=" * 70)


# Generate E8 roots
def generate_E8_roots():
    roots = []
    for i, j in combinations(range(8), 2):
        for si in [1, -1]:
            for sj in [1, -1]:
                root = [0] * 8
                root[i] = si
                root[j] = sj
                roots.append(tuple(root))
    for signs in product([1, -1], repeat=8):
        if signs.count(-1) % 2 == 0:
            root = tuple(s * 0.5 for s in signs)
            roots.append(root)
    return roots


E8_roots = generate_E8_roots()

print(
    """
Can we partition 240 E8 roots into 40 groups of 6,
analogous to the W33 edge partition?

The 240 edges of W33 partition as:
  240 = 40 (2-spaces) × 6 (edges per 2-space)

For E8, we need to find a similar structure.
"""
)

# One natural partition: by support
# Type 1 roots have support on 2 coordinates
# Group by which pair of coordinates

# Partition type 1 roots by their support
type1_roots = [r for r in E8_roots if 0 in r]
type2_roots = [r for r in E8_roots if 0 not in r]

print(f"Type 1 roots: {len(type1_roots)}")
print(f"Type 2 roots: {len(type2_roots)}")

# Type 1: group by support pair
support_groups = defaultdict(list)
for r in type1_roots:
    support = tuple(i for i, x in enumerate(r) if x != 0)
    support_groups[support].append(r)

print(f"\nType 1 partition (by coordinate support):")
print(f"  {len(support_groups)} groups")
for support, roots in list(support_groups.items())[:3]:
    print(f"    Support {support}: {len(roots)} roots")

# Each support pair gives 4 roots: (±1, ±1)
# So we have C(8,2) = 28 groups of 4 roots
# 28 × 4 = 112 ✓

# Type 2: group by... what?
# All 128 type 2 roots have support on all 8 coordinates
# They differ by sign patterns

# One natural grouping: by the product of signs
# Even number of minus signs → even subset of {1,...,8}

print(f"\nType 2 roots: all have full support")
print(f"They can be grouped by which coordinates are negative")

# ==============================================================
# PART 7: THE CORRESPONDENCE REFINED
# ==============================================================

print("\n" + "=" * 70)
print("PART 7: REFINED CORRESPONDENCE")
print("=" * 70)

print(
    """
SUMMARY OF STRUCTURES:

W33:
  - 40 vertices (isotropic lines)
  - 240 edges (orthogonal pairs)
  - 40 totally isotropic 2-spaces
  - Each 2-space contains 4 lines, C(4,2)=6 edge-pairs
  - Edges partition: 240 = 40 × 6

E8:
  - 240 roots
  - 112 type-1 (±1, ±1, 0, ..., 0)
  - 128 type-2 (all ±1/2)
  - Type-1 partition: 112 = 28 × 4 (by coordinate pair)
  - Type-2: 128 = 2^7 (half of 2^8, those with even parity)

The 240 = 240 correspondence is NOT a simple bijection preserving
all structure. Rather:

  W33 is a "mod 3 reduction" of E8

Just as:
  - GF(3) is a finite field
  - E8 lives over the reals (or rationals)

W33 captures the COMBINATORIAL SHADOW of E8,
with the number 3 replacing continuous structure.
"""
)

# ==============================================================
# PART 8: THE 40 = 40 CONNECTION
# ==============================================================

print("\n" + "=" * 70)
print("PART 8: THE 40 = 40 = 40 PATTERN")
print("=" * 70)

print(
    """
Three different 40s appear:

1. W33 vertices: 40 isotropic lines in GF(3)^4

2. Totally isotropic 2-spaces: 40 such spaces

3. Something in E8?
   - 240/6 = 40 (if we can partition E8 roots into groups of 6)

Let's check: can we find 40 groups of 6 roots in E8?
"""
)

# One attempt: group roots by some invariant
# For type-1 roots: 28 groups of 4 (not 6)
# We need to combine these somehow

# Alternative: find 40 "maximal totally isotropic" structures in E8
# These would be maximal commuting sets of roots

# In E8, a maximal torus has dimension 8
# The 240 roots span a 8-dimensional space

# A more direct approach:
# The 40 in W33 comes from (3^4-1)/(3-1) = 40 = number of lines in PG(3,3)
# This is also |Sp(4,3)|/(q^2-1)(q+1) related

print(
    """
The number 40 arises as:

  40 = (3^4 - 1)/(3 - 1) = (81 - 1)/2 = number of lines through origin in GF(3)^4

This is a projective geometry count:
  |PG(3, 3)| points = (3^4 - 1)/(3 - 1) = 40

In E8, we have 240 roots in 8 dimensions.
  240/8 = 30 (roots per dimension, roughly)
  240/6 = 40 (groups of 6)

The factor of 6 appears because:
  6 = C(4,2) = edges in K_4 = edges in a totally isotropic 2-space

And also:
  6 = |GF(3)*|^2 - 1 = 8 - 2 = 6 (another GF(3) count)
"""
)

print("\n" + "=" * 70)
print("ANALYSIS COMPLETE")
print("=" * 70)
