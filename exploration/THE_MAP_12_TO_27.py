"""
THE_MAP_12_TO_27.py - Finding the Explicit Bijection

KEY INSIGHT: AG(3,3) has 27 points and 13 parallel classes of lines.
Our 12 positions should embed as 12 of these 13 classes!

Let's find the map.
"""

from collections import Counter, defaultdict
from itertools import combinations, product

import numpy as np

print("=" * 80)
print("THE MAP FROM 12 TO 27")
print("=" * 80)

# ============================================================================
print("\n" + "=" * 80)
print("PART 1: AG(3,3) Structure")
print("=" * 80)

print(
    """
AG(3,3) = Affine 3-space over GF(3)

Points: All (a,b,c) with a,b,c ∈ {0,1,2} → 27 points

Lines: Each line has 3 points, determined by:
  - A point P and a direction vector d ≠ 0
  - Line = {P, P+d, P+2d}

Number of directions: (3³-1)/2 = 13 (projective points)
Lines per direction: 9 (parallel class)
Total lines: 13 × 9 = 117
"""
)

# Build AG(3,3)
points = [(a, b, c) for a in range(3) for b in range(3) for c in range(3)]
print(f"Points: {len(points)}")

# Build directions (projective: d and 2d are same direction)
directions = []
for d in product(range(3), repeat=3):
    if d == (0, 0, 0):
        continue
    # Normalize: first non-zero entry is 1
    for i in range(3):
        if d[i] != 0:
            factor = pow(d[i], -1, 3)  # Inverse in GF(3)
            d_norm = tuple((factor * d[j]) % 3 for j in range(3))
            if d_norm not in directions:
                directions.append(d_norm)
            break

print(f"Directions: {len(directions)}")


# Build lines by direction class
def add_pts(p1, p2):
    return tuple((p1[i] + p2[i]) % 3 for i in range(3))


def scale_pt(k, p):
    return tuple((k * p[i]) % 3 for i in range(3))


lines_by_dir = {d: [] for d in directions}
for d in directions:
    seen_lines = set()
    for p in points:
        line = frozenset(add_pts(p, scale_pt(k, d)) for k in range(3))
        if line not in seen_lines:
            seen_lines.add(line)
            lines_by_dir[d].append(line)

print(f"Lines per direction: {[len(lines_by_dir[d]) for d in directions]}")

# ============================================================================
print("\n" + "=" * 80)
print("PART 2: The 13 Directions")
print("=" * 80)

print(f"\nThe 13 directions in AG(3,3):")
for i, d in enumerate(directions):
    print(f"  d{i}: {d}")

print(f"\nWe need to choose 12 of these 13 directions!")
print(f"The omitted direction will be SPECIAL.")

# ============================================================================
print("\n" + "=" * 80)
print("PART 3: S(5,6,12) from AG(3,3)")
print("=" * 80)

print(
    """
CONSTRUCTION: (following Hill-Tonchev)

In AG(3,3), a MAXIMAL CAP is a set of points, no 3 collinear.
The maximal cap size in AG(3,3) is 20.

The COMPLEMENT of a 20-cap is a 7-set.
These 7-sets form a design!

But for our purposes:
Take 12 DIRECTIONS and map them to positions 0-11.
A HEXAD corresponds to 6 directions that form a "flat" structure.
"""
)

# Alternative construction: The ternary Golay code from AG(3,3)
# The 12 positions correspond to special "points" or "hyperplanes"

# Let's try mapping positions to AG(3,3) structures

# IDEA: The 12 positions might be the "affine hyperplanes"
# In AG(3,3), there are 4 parallel classes of planes
# Each class has 3 planes, total 12 planes... wait that's just 12!

print(f"\n12 = number of affine hyperplanes in AG(3,3)?")
print(f"  Hyperplanes: 3 axes × 4 classes = 12? No...")
print(f"  Actually: 3 directions × 3 values = 9 per direction...")

# Better: use the coordinate planes
# Hyperplanes are: x = const, y = const, z = const, x+y+z = const
# 3 choices each × 4 = 12... still not quite

# ============================================================================
print("\n" + "=" * 80)
print("PART 4: Direct Construction")
print("=" * 80)

print(
    """
Let's build the map directly.

Map: Position i → something in {0,1,...,26}

The constraint: The 132 hexads must map to special 6-subsets of [27].

IDEA: Use the dual - map codewords to matrix elements!

A weight-6 codeword c with support H corresponds to:
  A linear combination of 6 matrix elements E_{ab} in sl(27)

If positions map to pairs (a,b), then:
  Position i → (a_i, b_i) with a_i ≠ b_i

The hexad {i,j,k,l,m,n} → ∑_{pos in hexad} c[pos] E_{a,b}

For this to close under bracket, we need:
  [E_{ab}, E_{cd}] = δ_{bc} E_{ad} - δ_{ad} E_{cb}

This means pairs (a,b) and (c,d) bracket to (a,d) when b=c.
The resulting pair must also be in our 12 positions!
"""
)

# ============================================================================
print("\n" + "=" * 80)
print("PART 5: The Petersen Graph!")
print("=" * 80)

print(
    """
The Petersen graph has 10 vertices and 15 edges.
It's the Kneser graph K(5,2) - vertices are 2-subsets of {0,1,2,3,4}.
Two vertices are adjacent iff the 2-subsets are disjoint.

BUT: We have 12 positions, not 10.

The "extended Petersen" or other small graphs...

Actually, let's think about this differently:

  12 positions
  Each hexad = 6 positions
  C(12,6) = 924 possible 6-sets
  Only 132 are hexads (Steiner system constraint)

The Steiner system S(5,6,12) has incidence matrix I:
  I is 132 × 12
  I[h,i] = 1 if position i is in hexad h

This matrix encodes the geometry!
"""
)

# ============================================================================
print("\n" + "=" * 80)
print("PART 6: Building the Steiner System")
print("=" * 80)

# Build the ternary Golay code
G = np.array(
    [
        [1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1],
        [0, 1, 0, 0, 0, 0, 1, 0, 1, 2, 2, 1],
        [0, 0, 1, 0, 0, 0, 1, 1, 0, 1, 2, 2],
        [0, 0, 0, 1, 0, 0, 1, 2, 1, 0, 1, 2],
        [0, 0, 0, 0, 1, 0, 1, 2, 2, 1, 0, 1],
        [0, 0, 0, 0, 0, 1, 1, 1, 2, 2, 1, 0],
    ],
    dtype=int,
)


def generate_codewords():
    codewords = []
    for coeffs in product(range(3), repeat=6):
        c = np.array(coeffs) @ G % 3
        codewords.append(tuple(c))
    return codewords


codewords = generate_codewords()
nonzero = [c for c in codewords if any(x != 0 for x in c)]


def weight(c):
    return sum(1 for x in c if x != 0)


def support(c):
    return frozenset(i for i, x in enumerate(c) if x != 0)


weight_6 = [c for c in nonzero if weight(c) == 6]
hexads = list(set(support(c) for c in weight_6))

print(f"Hexads: {len(hexads)}")

# Build incidence matrix
incidence = np.zeros((len(hexads), 12), dtype=int)
for h_idx, h in enumerate(hexads):
    for pos in h:
        incidence[h_idx, pos] = 1

print(f"Incidence matrix shape: {incidence.shape}")

# Column sums (how many hexads contain each position)
col_sums = incidence.sum(axis=0)
print(f"Hexads per position: {col_sums}")  # Should be 66 each

# Row sums (sanity check - should all be 6)
row_sums = incidence.sum(axis=1)
print(f"Positions per hexad: {set(row_sums)}")

# ============================================================================
print("\n" + "=" * 80)
print("PART 7: The Block Graph")
print("=" * 80)

print(
    """
The BLOCK GRAPH of S(5,6,12):
  Vertices = 132 hexads
  Edges = pairs of hexads with |H1 ∩ H2| = k for some k

For |∩| = 3: This gives our 40 neighbors per hexad!
For |∩| = 2: Different structure
For |∩| = 0: Complementary hexads

Let's compute the intersection distribution.
"""
)

intersection_counts = Counter()
for i, h1 in enumerate(hexads):
    for j, h2 in enumerate(hexads):
        if i < j:
            inter = len(h1 & h2)
            intersection_counts[inter] += 1

print(f"\nHexad intersection distribution:")
for k in sorted(intersection_counts.keys()):
    print(f"  |H1 ∩ H2| = {k}: {intersection_counts[k]} pairs")

# Verify 40 per hexad for |∩|=3
per_hexad = Counter()
for h1 in hexads:
    count = sum(1 for h2 in hexads if h1 != h2 and len(h1 & h2) == 3)
    per_hexad[count] += 1
print(f"\n|∩|=3 neighbors per hexad: {dict(per_hexad)}")

# ============================================================================
print("\n" + "=" * 80)
print("PART 8: The Point Graph")
print("=" * 80)

print(
    """
The POINT GRAPH:
  Vertices = 12 positions
  Edge between i,j iff they appear together "often" in hexads

In S(5,6,12), any pair {i,j} appears in exactly C(10,4)/C(4,4) = 210/1 = 210?
No wait, let's calculate:
  Any 2-set is contained in: C(10,4)/? hexads
  By design property: each 2-set is in 15 hexads? Let's check.
"""
)

pair_counts = Counter()
for h in hexads:
    for pair in combinations(h, 2):
        pair_counts[pair] += 1

pair_dist = Counter(pair_counts.values())
print(f"Pairs per count: {dict(pair_dist)}")

# This tells us how often each pair appears
# In S(5,6,12), any 5-set appears in exactly 1 hexad
# So... let's check 5-sets
five_counts = Counter()
for h in hexads:
    for five in combinations(h, 5):
        five_counts[five] += 1

five_dist = Counter(five_counts.values())
print(f"5-sets in exactly 1 hexad: {five_dist}")

# ============================================================================
print("\n" + "=" * 80)
print("PART 9: The Automorphism Group M₁₂")
print("=" * 80)

print(
    """
The automorphism group of S(5,6,12) is M₁₂.
|M₁₂| = 95040

M₁₂ acts:
  - Transitively on the 12 positions
  - Transitively on the 132 hexads
  - Transitively on pairs {(position, hexad) : position ∈ hexad}

This transitivity means:
  ALL positions are equivalent (symmetric design)
  ALL hexads are equivalent

So the map 12 → 27 should respect M₁₂ in some way!
"""
)

# ============================================================================
print("\n" + "=" * 80)
print("PART 10: The E₆ Weyl Group")
print("=" * 80)

print(
    """
The Weyl group W(E₆) has order 51840.
  51840 = 27 × 1920
  51840 = 72 × 720

Compare to M₁₂:
  |M₁₂| = 95040 = 51840 × (95040/51840)
  95040 / 51840 = 11/6? No...
  95040 = 51840 × 1.836... not a nice ratio

But! M₁₁ ⊂ M₁₂:
  |M₁₁| = 7920
  51840 / 7920 = 6.545... not nice either

However:
  |W(E₆)| = 51840 = 2⁷ × 3⁴ × 5
  |M₁₂| = 95040 = 2⁶ × 3³ × 5 × 11

Common divisors suggest a connection through:
  gcd(51840, 95040) = 2⁶ × 3³ × 5 = 8640

8640 = |some important subgroup|
"""
)

print(f"\n51840 = {51840} = 2^7 × 3^4 × 5")
print(f"95040 = {95040} = 2^6 × 3^3 × 5 × 11")
print(f"gcd = {np.gcd(51840, 95040)}")

# ============================================================================
print("\n" + "=" * 80)
print("PART 11: The KEY Observation")
print("=" * 80)

print(
    """
THE BREAKTHROUGH:

27 = 3³ and 27 = 12 + 12 + 3

In sl(27), the Cartan subalgebra has dimension 26 (not 27).
But we can decompose:

  27 × 27 = 729 matrices
  729 - 1 (trace condition) = 728 = dim(sl(27))

  Our code has 729 codewords!
  729 - 1 (zero codeword) = 728 non-zero!

THE BIJECTION IS:
  Codeword c = (c_0, c_1, ..., c_{11}) over GF(3)
  Matrix M_c = sum_{i=0}^{11} c_i · B_i

Where B_0, ..., B_{11} are 12 GENERATING matrices of sl(27)!

The 12 generators must satisfy:
  - They generate sl(27) (span is full 728-dim)
  - Their "bracket structure" matches the hexad bracket

The generators are NOT arbitrary - they must be chosen
to make the hexad combinatorics work!
"""
)

# ============================================================================
print("\n" + "=" * 80)
print("PART 12: Candidate Generators")
print("=" * 80)

print(
    """
In sl(27), good candidates for generators come from:

CASE 1: Root generators
  E₆ has 72 roots. Pick 12 that generate.

CASE 2: Parabolic decomposition
  sl(27) = n⁻ ⊕ h ⊕ n⁺ (nilpotent + Cartan + nilpotent)
  Pick generators from each part.

CASE 3: Symmetric decomposition
  Split into 27 = 12 + 15 (or similar)
  Generators act on this split.

CASE 4: Jordan algebra approach
  J₃(O) has 27 dimensions.
  The 12 coordinate positions → 12 special derivations?

Let's try to identify the 12!
"""
)

# ============================================================================
print("\n" + "=" * 80)
print("SYNTHESIS: The Emerging Map")
print("=" * 80)

print(
    """
SUMMARY:

1. The 12 Golay positions map to 12 generators of sl(27).

2. Each generator is a matrix B_i ∈ sl(27).

3. A codeword c = (c_0, ..., c_{11}) maps to:
   M_c = Σ c_i B_i (sum over non-zero positions)

4. The hexad bracket [c1, c2] corresponds to:
   [M_{c1}, M_{c2}] (matrix commutator)

5. The product=2 condition (giving weight-6 output) means:
   [B_i, B_j] lies in the span of 6 generators!

6. The 40 "bracket partners" per codeword reflects:
   Each B_i brackets with 40 other generators in specific ways.

The 12 generators B_0, ..., B_{11} form a VERY SPECIAL
configuration in sl(27) - they are "hexadal generators"!

NEXT: Construct these 12 matrices explicitly.
"""
)

# ============================================================================
print("\n" + "=" * 80)
print("The Numbers Again")
print("=" * 80)

print(
    f"""
Checking consistency:

  728 non-zero codewords = dim(sl(27)) ✓

  264 weight-6 codewords should span a 264-dim subspace?
  No - they lie on a 6-dim variety (6 generators active)!

  Actually: The 264 weight-6 codewords each use 6 of 12 generators.
  But the SPAN of 264 weight-6 codewords should be...

  Wait - codewords span the full code (6-dimensional GF(3)-space)!

  The 728 non-zero codewords are the PROJECTIVE elements
  of a 6-dimensional vector space over GF(3).

  (3^6 - 1) = 728 ✓

  So the "dimension" of the code is 6, not 728.
  The 728 is the number of non-zero VECTORS.

THE REAL MAP:
  6-dim code → 728-dim sl(27)

  This is a REPRESENTATION!
  The 6-dim code acts on 27-dim space.
  The induced action on End(27) = 729-dim has:
    - 1-dim trace = 0 subspace
    - 728-dim sl(27)

  So: The ternary Golay code REPRESENTS as sl(27)!
"""
)
