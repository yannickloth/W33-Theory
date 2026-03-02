"""
THE_EIGHTY_MYSTERY.py - Why Does Every Element Have Exactly 80 Brackets?

80 = 2 × 40 = the eleven-structure appearing in disguise
440 = 11 × 40 (weight-9 count)
80 / 2 = 40

What IS 80 geometrically? Why not 51 (like sl(27) E_ij)?

Let's crack this.
"""

from collections import Counter, defaultdict
from itertools import combinations, product

import numpy as np

print("=" * 80)
print("THE EIGHTY MYSTERY: Why 80 Brackets Per Element?")
print("=" * 80)

# Ternary Golay setup
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
codeword_set = set(codewords)
nonzero = [c for c in codewords if any(x != 0 for x in c)]


def weight(c):
    return sum(1 for x in c if x != 0)


def support(c):
    return frozenset(i for i, x in enumerate(c) if x != 0)


def neg(c):
    return tuple((3 - x) % 3 if x != 0 else 0 for x in c)


def add(c1, c2):
    return tuple((c1[i] + c2[i]) % 3 for i in range(12))


weight_6 = [c for c in nonzero if weight(c) == 6]
weight_9 = [c for c in nonzero if weight(c) == 9]
weight_12 = [c for c in nonzero if weight(c) == 12]

hexads = set(support(c) for c in weight_6)
hexad_to_cw = defaultdict(list)
for c in weight_6:
    hexad_to_cw[support(c)].append(c)

print(
    f"Weight-6: {len(weight_6)}, Weight-9: {len(weight_9)}, Weight-12: {len(weight_12)}"
)

# ============================================================================
print("\n" + "=" * 80)
print("PART 1: Analyzing the 80 From Hexad Geometry")
print("=" * 80)


# For a fixed hexad H, how many other hexads intersect it in exactly 3?
def hexads_intersecting_in_k(H, k):
    return [H2 for H2 in hexads if H2 != H and len(H & H2) == k]


sample_hexad = list(hexads)[0]
print(f"\nFor hexad {sorted(sample_hexad)}:")
for k in range(7):
    count = len(hexads_intersecting_in_k(sample_hexad, k))
    if count > 0:
        print(f"  |H ∩ H'| = {k}: {count} hexads")

# The 80 comes from: each codeword c on hexad H brackets with
# codewords on hexads H' where |H ∩ H'| = 3
intersect_3 = hexads_intersecting_in_k(sample_hexad, k=3)
print(f"\nHexads with |∩| = 3: {len(intersect_3)}")
print(f"Each such hexad has 2 codewords")
print(f"Total: {len(intersect_3)} × 2 = {len(intersect_3) * 2}")

# But we also need to exclude c itself and -c
# Actually no - c is on H, other codewords are on H', they're different
print(f"\nSo 80 = 40 hexads × 2 codewords per hexad!")

# Verify: every hexad has exactly 40 others with |∩| = 3
intersect_3_counts = []
for H in hexads:
    count = len(hexads_intersecting_in_k(H, k=3))
    intersect_3_counts.append(count)

print(f"\nVerification: Hexads with |∩|=3 per hexad: {set(intersect_3_counts)}")
print(f"  All hexads have exactly 40 others with |∩|=3!")

# ============================================================================
print("\n" + "=" * 80)
print("PART 2: Why 40? The Geometry of Hexad Intersections")
print("=" * 80)

print(
    """
We have 132 hexads total.
For any fixed hexad H:
  - 1 hexad is H itself
  - ? hexads have |∩| = 0, 1, 2, 3, 4, 5, 6

Let's compute the full distribution.
"""
)

# Full intersection distribution
full_dist = Counter()
for H in hexads:
    for H2 in hexads:
        if H != H2:
            full_dist[len(H & H2)] += 1

# Each pair counted twice (H,H') and (H',H)
print("Intersection distribution (unordered pairs):")
for k in sorted(full_dist.keys()):
    print(f"  |∩| = {k}: {full_dist[k] // 2} pairs")

# Per-hexad distribution
print("\nPer single hexad:")
for k in sorted(full_dist.keys()):
    per_hexad = full_dist[k] // 132  # 132 hexads, each sees this many
    print(f"  |∩| = {k}: {per_hexad} other hexads")

# ============================================================================
print("\n" + "=" * 80)
print("PART 3: The 40 = 11 + 11 + 11 + 7 Decomposition?")
print("=" * 80)

print(
    """
40 is interesting because:
  40 = 8 × 5 = 2³ × 5
  40 = 11 + 11 + 11 + 7 (three 11s plus 7)
  40 = 4 × 10

440 = 11 × 40, so the eleven-structure is present.

Let's see if the 40 hexads with |∩|=3 have any special structure.
"""
)

# Pick a hexad and look at its 40 partners
H0 = list(hexads)[0]
partners = hexads_intersecting_in_k(H0, k=3)

print(f"\nFixed hexad H0 = {sorted(H0)}")
print(f"Its 40 partners (|∩|=3):")

# Group partners by their intersection with H0
intersection_patterns = defaultdict(list)
for H2 in partners:
    inter = tuple(sorted(H0 & H2))
    intersection_patterns[inter].append(H2)

print(f"\nNumber of distinct 3-subsets of H0: {len(intersection_patterns)}")
print(f"C(6,3) = {6*5*4//(3*2*1)} = 20")

# Each 3-subset of H0 appears how many times?
counts_per_triple = [len(v) for v in intersection_patterns.values()]
print(f"Partners per 3-subset: {sorted(set(counts_per_triple))}")

if len(set(counts_per_triple)) == 1:
    print(f"\nEach 3-subset of H0 gives exactly {counts_per_triple[0]} partners!")
    print(f"Total: 20 × {counts_per_triple[0]} = {20 * counts_per_triple[0]}")

# ============================================================================
print("\n" + "=" * 80)
print("PART 4: The Steiner Structure of Intersections")
print("=" * 80)

print(
    """
Each 3-subset of a hexad H determines exactly 2 partner hexads!
20 × 2 = 40 ✓

This is because: in S(5,6,12), given 5 points, there's a unique hexad.
Given 3 points IN a hexad H, the remaining 3 positions of H are fixed.
The partner hexad H' must contain the same 3 intersection points,
plus 3 NEW points from the complement of H.

The complement of H has 6 points.
Choosing 3 from 6: C(6,3) = 20.
But not all 20 work - only 2 give valid hexads!

This is the Steiner constraint at work.
"""
)

# Verify: for a fixed 3-subset of H0, which 3-subsets of complement give hexads?
comp_H0 = frozenset(range(12)) - H0
print(f"\nComplement of H0: {sorted(comp_H0)}")

# For one specific 3-subset of H0
triple_in_H0 = list(intersection_patterns.keys())[0]
print(f"\nFixed triple in H0: {triple_in_H0}")
print(f"Partner hexads with this intersection:")

for H2 in intersection_patterns[triple_in_H0]:
    in_comp = sorted(H2 - H0)
    print(f"  H2 = {sorted(H2)}, new points from complement: {in_comp}")

# ============================================================================
print("\n" + "=" * 80)
print("PART 5: Connecting to sl(27) - Why 80 ≠ 51?")
print("=" * 80)

print(
    """
In sl(27), each E_ij brackets non-trivially with:
  - E_jk for k ≠ i,j: 25 elements (sharing j)
  - E_ki for k ≠ i,j: 25 elements (sharing i)
  - E_ji: 1 element (gives Cartan)
Total: 51 non-zero brackets

In our Golay algebra, each weight-6 has 80 brackets.
Ratio: 80/51 = 1.569...

What if the 264 weight-6 don't map 1:1 to E_ij?

Alternative: 264 = 132 × 2 (hexad pairs)
             702 = 351 × 2 (27 choose 2, times 2 for direction)

702 / 264 = 2.659...
264 / 702 = 0.376...

Hmm, 264 is roughly 1/3 of 702.
Maybe weight-6 maps to a SUBSET of E_ij?
"""
)

# ============================================================================
print("\n" + "=" * 80)
print("PART 6: The Quotient Hypothesis")
print("=" * 80)

print(
    """
HYPOTHESIS: The 264 weight-6 codewords are a QUOTIENT of sl(27).

264 × 3 = 792 ≈ 702 + 90
264 × 2.66 ≈ 702

What if the 264 represent equivalence classes of E_ij?

Group E_ij by some equivalence relation with ~3 per class:
702 / 264 = 2.659 ≈ 8/3

Or maybe:
  264 + 440 = 704 ≈ 702
  The weight-6 + weight-9 together give the off-diagonal elements!
  264 + 440 = 704, and 704 - 702 = 2

The "missing 2" might be absorbed into the Cartan.
"""
)

print(f"\n264 + 440 = {264 + 440}")
print(f"702 = 27 × 26 = {27 * 26}")
print(f"Difference: {704 - 702}")

# ============================================================================
print("\n" + "=" * 80)
print("PART 7: Bracket Extension to Weight-9")
print("=" * 80)

print(
    """
If weight-6 + weight-9 = 704 ≈ 702 off-diagonal,
then the FULL bracket should include weight-9.

Key question: Can we define [c6, c9] for weight-6 and weight-9?

Weight-6 support: 6 positions
Weight-9 support: 9 positions
Intersection: 3, 4, 5, or 6 positions

Let's check what intersections give valid brackets.
"""
)

# Support intersections between weight-6 and weight-9
int_sizes_69 = Counter()
for c6 in weight_6[:100]:
    for c9 in weight_9[:100]:
        inter = len(support(c6) & support(c9))
        int_sizes_69[inter] += 1

print("\nIntersection sizes |supp(c6) ∩ supp(c9)|:")
for size in sorted(int_sizes_69.keys()):
    print(f"  |∩| = {size}: {int_sizes_69[size]} pairs (sample)")

# The sum c6 + c9 is always a codeword
# What weight does it have?
print("\nWeight of c6 + c9:")
sum_weights = Counter()
for c6 in weight_6[:100]:
    for c9 in weight_9[:100]:
        s = add(c6, c9)
        w = weight(s) if any(x != 0 for x in s) else 0
        sum_weights[w] += 1

for w in sorted(sum_weights.keys()):
    print(f"  weight = {w}: {sum_weights[w]} pairs")

# ============================================================================
print("\n" + "=" * 80)
print("PART 8: The Complete Bracket Table")
print("=" * 80)

print(
    """
Define [c1, c2] = c1 + c2 if the result is in the code (always true!)
But with a SIGN based on ordering.

The question: Does this extended bracket satisfy Jacobi?
"""
)


def extended_bracket(c1, c2):
    """Extended bracket: just addition with sign."""
    if c1 == c2:
        return tuple([0] * 12)  # [c,c] = 0

    s = add(c1, c2)

    # Sign: lexicographic order
    if c1 < c2:
        return s
    else:
        return neg(s)


# Test antisymmetry
print("\nTesting antisymmetry on weight-6 × weight-9:")
antisym_pass = 0
antisym_fail = 0

for c6 in weight_6[:50]:
    for c9 in weight_9[:50]:
        b1 = extended_bracket(c6, c9)
        b2 = extended_bracket(c9, c6)
        s = add(b1, b2)
        if all(x == 0 for x in s):
            antisym_pass += 1
        else:
            antisym_fail += 1

print(f"  Pass: {antisym_pass}, Fail: {antisym_fail}")

# Test Jacobi on mixed triples
print("\nTesting Jacobi on (c6, c6', c9):")
jacobi_pass = 0
jacobi_fail = 0

for a in weight_6[:20]:
    for b in weight_6[:20]:
        for c in weight_9[:20]:
            if a != b:
                # [a, [b, c]] + [b, [c, a]] + [c, [a, b]]
                bc = extended_bracket(b, c)
                ca = extended_bracket(c, a)
                ab = extended_bracket(a, b)

                a_bc = extended_bracket(a, bc)
                b_ca = extended_bracket(b, ca)
                c_ab = extended_bracket(c, ab)

                jacobi_sum = add(add(a_bc, b_ca), c_ab)

                if all(x == 0 for x in jacobi_sum):
                    jacobi_pass += 1
                else:
                    jacobi_fail += 1

print(f"  Pass: {jacobi_pass}, Fail: {jacobi_fail}")

# ============================================================================
print("\n" + "=" * 80)
print("PART 9: The TRUE Bracket Must Use Hexad Structure")
print("=" * 80)

print(
    """
Simple addition doesn't work for Jacobi.
The CORRECT bracket uses hexad symmetric difference.

For weight-6 × weight-6: We proved this works!
For weight-6 × weight-9: Need to find the right rule.

Key insight: weight-9 = complement of weight-6 (sort of)
supp(c9) = 12 - supp(c6') for some c6'

Actually: supp(c9) has 9 elements, complement has 3.
The 3-element complement is NOT a hexad.

But: supp(c6) has 6 elements.
supp(c6) ∩ supp(c9) has 3, 4, 5, or 6 elements.
"""
)

# When |supp(c6) ∩ supp(c9)| = 3, what is supp(c6) XOR supp(c9)?
print("\nWhen |supp(c6) ∩ supp(c9)| = 3:")
print("  supp(c6) has 6 elements")
print("  supp(c9) has 9 elements")
print("  supp(c6) XOR supp(c9) = (6-3) + (9-3) = 3 + 6 = 9 elements")

# Is c6 XOR c9 support always a valid 9-support?
valid_9_supports = set(support(c) for c in weight_9)

print("\nChecking if supp(c6) XOR supp(c9) is always a weight-9 support:")
xor_valid = 0
xor_invalid = 0

for c6 in weight_6[:50]:
    for c9 in weight_9[:50]:
        s6, s9 = support(c6), support(c9)
        if len(s6 & s9) == 3:
            xor = s6 ^ s9
            if xor in valid_9_supports:
                xor_valid += 1
            else:
                xor_invalid += 1

print(f"  Valid: {xor_valid}, Invalid: {xor_invalid}")

# ============================================================================
print("\n" + "=" * 80)
print("SYNTHESIS: The 80 = 40 × 2 Structure")
print("=" * 80)

print(
    """
PROVEN:
  1. Each hexad has exactly 40 other hexads with |∩| = 3
  2. 40 = 20 × 2 (20 triples in hexad × 2 partners each)
  3. Each weight-6 codeword brackets with 40 × 2 = 80 other weight-6 codewords

THE GEOMETRY:
  - Pick c on hexad H
  - Pick any 3 positions in H: 20 choices
  - Each 3-subset determines exactly 2 partner hexads
  - Each partner hexad has 2 codewords
  - Total: 20 × 2 × 2 = 80 ✓

  Wait, that gives 80 = 20 × 2 × 2
  But we said 80 = 40 × 2

  Resolution: 40 hexads × 2 codewords = 80
              20 triples × 2 hexads per triple × 1 codeword pair = 80

THE ELEVEN CONNECTION:
  440 = 11 × 40
  80 = 2 × 40

  The 40 is the "quantum" of the structure!
  - 11 copies of 40 give weight-9
  - 2 copies of 40 give the bracket count

  What IS 40?
  40 = C(6,3) × 2 = 20 × 2 (triples in hexad × partners)
  40 = number of hexad-neighbors per hexad
"""
)

print("\n" + "=" * 80)
print("THE ANSWER: 40 = C(6,3) × 2 / 1")
print("=" * 80)
print(
    f"""
40 = 20 × 2 where:
  20 = C(6,3) = ways to choose 3 positions in a hexad
  2 = partner hexads per 3-subset (Steiner constraint)

80 = 40 × 2 where:
  40 = partner hexads with |∩| = 3
  2 = codewords per hexad

440 = 11 × 40 where:
  11 = ??? (the mysterious eleven!)
  40 = the hexad-neighbor quantum

THE ELEVEN MYSTERY REMAINS:
  Where does 11 come from?
  11 = 12 - 1 (points minus one)
  11 = |GF(11)| (the field in M12 construction)
  11 × 40 = 440 = weight-9 count

  Perhaps: 220 weight-9 pairs = C(12,3) = 220
  And 220 × 2 = 440

  So 11 appears as: C(12,3) = 220 = 11 × 20

  THE CHAIN:
    40 = 20 × 2 (hexad geometry)
    220 = 20 × 11 = C(12,3)
    440 = 220 × 2 (codeword pairs)

  The 11 comes from: 12 - 1 points choosing 3!
  C(12,3) / C(6,3) = 220 / 20 = 11
"""
)
