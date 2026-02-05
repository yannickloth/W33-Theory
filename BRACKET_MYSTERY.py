"""
BRACKET_MYSTERY.py - The Missing Piece: How Does the Lie Bracket Emerge?

Created: February 2026
Purpose: Crack the fundamental question - how do Golay codewords form a Lie algebra?

THE PROBLEM:
  We have 728 nonzero codewords of the ternary Golay code.
  We claim they correspond to 728 basis elements of sl(27).
  sl(27) has a Lie bracket: [X,Y] = XY - YX

  But the ternary Golay code has NO OBVIOUS bracket structure!
  The inner product gives 0 for all pairs (total self-orthogonality).

  So HOW does the bracket emerge?

POSSIBLE APPROACHES:
  1. The bracket is NOT the inner product - it's something else
  2. The bracket involves TRIPLES of codewords, not pairs
  3. The bracket emerges from the SUPPORT structure (hexads)
  4. The bracket is defined via the automorphism group 2.M12
  5. The codewords parametrize a different construction (not direct)

Let me investigate each possibility systematically.
"""

from collections import Counter
from itertools import combinations, product

import numpy as np

# ============================================================================
print("=" * 80)
print("THE BRACKET MYSTERY: Seeking the Lie Algebra Structure")
print("=" * 80)

# Ternary Golay generator matrix
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
weight_9 = [c for c in nonzero if weight(c) == 9]
weight_12 = [c for c in nonzero if weight(c) == 12]

print(
    f"\nCodeword counts: {len(weight_6)} + {len(weight_9)} + {len(weight_12)} = {len(nonzero)}"
)

# ============================================================================
print("\n" + "=" * 80)
print("APPROACH 1: Bracket as Componentwise Operation?")
print("=" * 80)

print(
    """
In GF(3), we have: 0, 1, 2 with 1+2=0, 1*2=2, etc.

What if [c1, c2]_i = c1_i * c2_i - c2_i * c1_i = 0?
That's trivially zero (commutative multiplication).

What if [c1, c2]_i = c1_i * c2_{i+1} - c2_i * c1_{i+1} (mod 12)?
This is like a "cyclic bracket".
"""
)


def cyclic_bracket(c1, c2):
    """Try a cyclic bracket: [c1,c2]_i = c1_i * c2_{i+1} - c2_i * c1_{i+1}"""
    result = []
    for i in range(12):
        j = (i + 1) % 12
        val = (c1[i] * c2[j] - c2[i] * c1[j]) % 3
        result.append(val)
    return tuple(result)


# Test on a few pairs
print("\nTesting cyclic bracket on random pairs:")
import random

random.seed(42)
for _ in range(5):
    c1 = random.choice(weight_6)
    c2 = random.choice(weight_6)
    bracket = cyclic_bracket(c1, c2)
    in_code = bracket in codewords
    print(f"  [{c1[:4]}..., {c2[:4]}...] = {bracket[:6]}... in code? {in_code}")

# Check closure
print("\nChecking if cyclic bracket closes on weight-6:")
closure_count = 0
non_closure = 0
for c1 in weight_6[:50]:  # Sample
    for c2 in weight_6[:50]:
        bracket = cyclic_bracket(c1, c2)
        if bracket in codewords:
            closure_count += 1
        else:
            non_closure += 1

print(f"  Closed: {closure_count}, Not closed: {non_closure}")
print(f"  Closure rate: {closure_count / (closure_count + non_closure):.2%}")

# ============================================================================
print("\n" + "=" * 80)
print("APPROACH 2: Bracket via Support Intersection?")
print("=" * 80)

print(
    """
Hexads (supports of weight-6 codewords) have intersection structure.
What if the bracket is defined by:
  - [c1, c2] = 0 if supports disjoint
  - [c1, c2] = c3 where supp(c3) = supp(c1) XOR supp(c2) (symmetric diff)?
"""
)

# Analyze support intersections
print("\nSupport intersection sizes for weight-6 pairs:")
intersection_sizes = Counter()
for c1, c2 in combinations(weight_6[:100], 2):
    s1, s2 = support(c1), support(c2)
    inter = len(s1 & s2)
    intersection_sizes[inter] += 1

for size, count in sorted(intersection_sizes.items()):
    print(f"  |supp(c1) ∩ supp(c2)| = {size}: {count} pairs")

# For intersections of size 3, check symmetric difference
print("\nWhen |intersection| = 3, symmetric diff has size 6 (another hexad?):")
hexads = set(support(c) for c in weight_6)
count_hexad_symdiff = 0
count_not_hexad = 0

for c1, c2 in combinations(weight_6[:200], 2):
    s1, s2 = support(c1), support(c2)
    if len(s1 & s2) == 3:
        symdiff = s1 ^ s2
        if symdiff in hexads:
            count_hexad_symdiff += 1
        else:
            count_not_hexad += 1

print(f"  Symmetric diff is hexad: {count_hexad_symdiff}")
print(f"  Symmetric diff is NOT hexad: {count_not_hexad}")

# ============================================================================
print("\n" + "=" * 80)
print("APPROACH 3: The Matrix Embedding Approach")
print("=" * 80)

print(
    """
sl(27) consists of 27x27 traceless matrices.
Basis elements: E_{ij} for i≠j (702 off-diagonal)
               H_k = E_{kk} - E_{k+1,k+1} for k=1..26 (26 Cartan)
Total: 702 + 26 = 728 ✓

The bracket is [E_{ij}, E_{kl}] = δ_{jk} E_{il} - δ_{li} E_{kj}

KEY INSIGHT: The bracket depends on INDEX MATCHING!
  - E_{ij} and E_{jk} bracket to give E_{ik}
  - E_{ij} and E_{kl} with j≠k and i≠l give 0

Can we map codewords to indices (i,j)?
  - We have 27 visible particles (indices?)
  - E_{ij} for i≠j gives C(27,2)*2 = 702 elements
  - Plus 26 Cartan elements
"""
)

print("\nThe 27 indices could correspond to:")
print("  - 27 points of AG(3,3)")
print("  - 27 codewords of some subset?")
print("  - 27 = 3^3 elements of (Z/3Z)^3")

# How many distinct supports?
all_supports_6 = set(support(c) for c in weight_6)
all_supports_9 = set(support(c) for c in weight_9)
print(f"\nDistinct weight-6 supports (hexads): {len(all_supports_6)}")
print(f"Distinct weight-9 supports: {len(all_supports_9)}")

# ============================================================================
print("\n" + "=" * 80)
print("APPROACH 4: Looking at Weight-12 as Cartan")
print("=" * 80)

print(
    """
24 weight-12 codewords should map to Cartan elements (if our theory is right).
But Cartan subalgebra of sl(27) has dimension 26, not 24!

26 - 24 = 2. Where are the missing 2?

Maybe: The zero codeword splits into multiple Cartan elements?
Or: Two of the 26 Cartan elements are "special" (not from codewords)?
"""
)

print("\nWeight-12 codewords form pairs (c, -c):")
pairs_12 = []
seen = set()
for c in weight_12:
    neg_c = tuple((3 - x) % 3 if x != 0 else 0 for x in c)
    if c not in seen and neg_c not in seen:
        pairs_12.append((c, neg_c))
        seen.add(c)
        seen.add(neg_c)

print(f"  {len(weight_12)} codewords form {len(pairs_12)} pairs")

# Each weight-12 codeword has all positions nonzero
print("\nWeight-12 codeword structure:")
for i, c in enumerate(weight_12[:4]):
    ones = sum(1 for x in c if x == 1)
    twos = sum(1 for x in c if x == 2)
    print(f"  {c}: {ones} ones, {twos} twos")

# ============================================================================
print("\n" + "=" * 80)
print("APPROACH 5: The Steiner System Connection")
print("=" * 80)

print(
    """
The 132 hexads form a Steiner system S(5,6,12):
  - Any 5 positions determine a unique hexad containing them

This means: given 5 indices, there's exactly ONE hexad.

In the bracket [E_{ij}, E_{jk}] = E_{ik}:
  - We combine 2 matrix elements to get 1
  - The indices i,j,k determine the result

Can the Steiner property encode the bracket?
  - A hexad has 6 positions, we need 3 indices for E_{ij}, E_{jk}, E_{ik}
  - Maybe pairs of positions within a hexad encode matrix indices?
"""
)

# Check: C(6,2) = 15 pairs within a hexad
print("\nPairs within a hexad: C(6,2) = 15")
print("But we need to identify 27 indices somehow...")
print("27 = 27, and C(27,2) = 351 = positive roots of A26 ✓")

# ============================================================================
print("\n" + "=" * 80)
print("APPROACH 6: The Miracle We're Missing")
print("=" * 80)

print(
    """
WHAT IF: The 728 codewords don't DIRECTLY form sl(27),
but instead PARAMETRIZE a construction?

For instance:
  - Each codeword c defines a LINEAR FUNCTIONAL on sl(27)
  - Or: codewords index a DUAL BASIS
  - Or: codewords encode STRUCTURE CONSTANTS

The structure constants of sl(27) are:
  [X_a, X_b] = sum_c f^c_ab X_c

where f^c_ab are the structure constants.

Maybe the Golay code encodes the f^c_ab?
  - 728^3 possible structure constants? Too many.
  - But most are zero or determined by antisymmetry.
"""
)

# Count possible nonzero structure constants
print("\nStructure constant analysis:")
print(f"  Total dimension: 728")
print(f"  Possible [X_a, X_b]: C(728,2) = {728*727//2}")
print(f"  But most brackets are zero...")

# For sl(n), structure constants are sparse
# [E_ij, E_kl] = delta_jk E_il - delta_li E_kj
# Nonzero only when j=k or l=i

print(f"\n  For sl(27), nonzero structure constants:")
print(f"    [E_ij, E_jk] = E_ik type: 27*26*25 = {27*26*25}")
print(f"    [E_ij, E_ki] = -E_kj type: same count")
print(f"    [H_i, E_jk] type: 26 * 702 = {26 * 702}")

# ============================================================================
print("\n" + "=" * 80)
print("BREAKTHROUGH ATTEMPT: The 27 Points of AG(3,3)")
print("=" * 80)

print(
    """
IDEA: Use the 27 points of AG(3,3) as the indices for E_{ij}!

AG(3,3) = affine 3-space over GF(3) = {(a,b,c) : a,b,c ∈ {0,1,2}}

Then:
  - E_{pq} for p,q ∈ AG(3,3), p ≠ q gives C(27,2)*2 = 702 matrices
  - H_p for 26 independent diagonal combinations gives 26 Cartan
  - Total: 728 ✓

Now: How do codewords map to (p,q) pairs?

A codeword is a 12-tuple over GF(3).
We need to extract two 3-tuples (p and q) from it.

12 = 4 * 3. If we partition 12 positions into 4 groups of 3:
  - Group 1: positions 0,1,2 → gives a in p = (a,_,_)
  - Group 2: positions 3,4,5 → gives b in p = (_,b,_)
  - etc.

But this is arbitrary. Let me think differently...
"""
)

# The 12 positions of the Golay code
# Maybe they relate to lines in PG(2,3)?
# PG(2,3) has 13 points and 13 lines, 4 points per line

print("\nThe 12 positions might be:")
print("  - 12 edges of a tetrahedron? (but that's 6)")
print("  - 12 faces of a dodecahedron? (but that's 12, hmm)")
print("  - 12 = 4*3 = 4 groups of 3 coordinates")
print("  - 12 elements of PSL(2,11) orbit structure?")

# ============================================================================
print("\n" + "=" * 80)
print("THE KEY REALIZATION")
print("=" * 80)

print(
    """
The Golay code has automorphism group 2.M12.
M12 acts on 12 points.

The stabilizer of a codeword in 2.M12 tells us its "type".

For sl(27), the stabilizer of E_{ij} in the automorphism group is related
to the stabilizer of the pair (i,j).

MATCHING STABILIZERS could be the key!

Let me check what subgroups appear as stabilizers...
"""
)

# The stabilizer orders we computed earlier
print("Stabilizer orders in 2.M12:")
print(f"  Weight-6 codeword: |2.M12|/264 = {190080 // 264} = 720 = 6!")
print(f"  Weight-9 codeword: |2.M12|/440 = {190080 // 440} = 432")
print(f"  Weight-12 codeword: |2.M12|/24 = {190080 // 24} = 7920 = |M11|")

print(f"\nFor sl(27), stabilizer of E_{{ij}}:")
print(f"  Should be related to stabilizer of (i,j) pair in S_27")
print(f"  |S_27| / C(27,2) = 27! / 351 - too big!")

# ============================================================================
print("\n" + "=" * 80)
print("SYNTHESIS: What Would Crack This?")
print("=" * 80)

print(
    """
TO CRACK THE BRACKET MYSTERY, we need ONE of these:

1. EXPLICIT MAP: A function φ: Codewords → {E_{ij}, H_k}
   that respects the Lie bracket structure.

2. STRUCTURE CONSTANTS: Show that the Golay code encodes
   the structure constants f^c_ab of sl(27).

3. REPRESENTATION THEORY: Find a representation of 2.M12
   on sl(27) that identifies codewords with basis elements.

4. GEOMETRIC CONSTRUCTION: Build sl(27) from PG(3,3) geometry
   in a way that makes the codeword correspondence obvious.

The most promising approach seems to be:
  - Use 27 = |AG(3,3)| as the index set
  - Map weight-6 codewords to E_{ij} via hexad structure
  - Map weight-12 codewords to Cartan (but need 26, have 24)
  - Map weight-9 codewords to remaining off-diagonal elements

The 2 missing Cartan elements (26 - 24 = 2) are the key puzzle!
"""
)

print("\n" + "=" * 80)
print("FINAL OBSERVATION: The 26-24=2 Gap")
print("=" * 80)

print(
    """
sl(27) Cartan dimension: 26
Weight-12 codewords: 24
Gap: 2

Where do the 2 extra Cartan elements come from?

POSSIBILITY 1: The zero codeword counts as 2 Cartan elements
  - The zero codeword is the identity? No, sl has trace 0.

POSSIBILITY 2: Two weight-6 or weight-9 codewords are "Cartan-like"
  - But all weight-6 should be E_{ij} (off-diagonal)

POSSIBILITY 3: The map is NOT 1-to-1 on weight-12!
  - Maybe 24 codewords map to 26 Cartan via some 12→13 doubling?
  - 24 = 12 pairs of (c,-c), 26 = 13 pairs of Cartan?

POSSIBILITY 4: The Lie algebra is NOT exactly sl(27)
  - Maybe it's gl(27) (dimension 729 = 728 + 1)
  - Or a central extension
  - Or a different algebra of dimension 728

Let me check: what Lie algebras have dimension 728?
"""
)

print(f"\nLie algebras of dimension 728:")
print(f"  sl(27) = A26: 728 ✓")
print(f"  so(n): n(n-1)/2 = 728 → n = 38.6... not integer")
print(f"  sp(n): n(n+1)/2 = 728 → n = 37.5... not integer")
print(f"  Exceptional: E8=248, E7=133, E6=78, F4=52, G2=14")
print(f"\nOnly sl(27) has dimension exactly 728!")
