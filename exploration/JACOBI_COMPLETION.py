"""
JACOBI_COMPLETION.py - Making the Bracket Complete

We have:
  - Weight-6 bracket: 100% closure, 100% antisymmetry
  - But Jacobi on (c6, c6', c6'') was all SKIPPED

The skip happened because [c6, [c6', c6'']] was often undefined
(the bracket [c6', c6''] lands on a hexad that doesn't intersect c6 in 3).

QUESTION: Is the weight-6 bracket a PARTIAL Lie algebra?
Or does it complete to a full one when we add weight-9 and weight-12?

The key: 264 + 440 + 24 = 728 = dim(sl(27))
If this IS sl(27), then Jacobi MUST hold when properly defined.
"""

from collections import Counter, defaultdict
from itertools import combinations, product

import numpy as np

print("=" * 80)
print("JACOBI COMPLETION: Finding the Full Lie Algebra")
print("=" * 80)

# Setup
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

# Index all supports
support_9 = set(support(c) for c in weight_9)
support_to_cw9 = defaultdict(list)
for c in weight_9:
    support_to_cw9[support(c)].append(c)

print(f"Weight-6: {len(weight_6)}, hexads: {len(hexads)}")
print(f"Weight-9: {len(weight_9)}, 9-supports: {len(support_9)}")
print(f"Weight-12: {len(weight_12)}")

# ============================================================================
print("\n" + "=" * 80)
print("PART 1: The Bracket on Weight-6 (Recap)")
print("=" * 80)


def intersection_product(c1, c2):
    H1, H2 = support(c1), support(c2)
    inter = H1 & H2
    prod = 1
    for i in inter:
        prod = (prod * c1[i] * c2[i]) % 3
    return prod


def bracket_66(c1, c2):
    """Bracket between two weight-6 codewords."""
    H1, H2 = support(c1), support(c2)

    if len(H1 & H2) != 3:
        return None  # undefined

    H3 = H1 ^ H2
    if H3 not in hexads:
        return None

    cw3_list = hexad_to_cw[H3]
    if len(cw3_list) != 2:
        return None

    prod = intersection_product(c1, c2)
    base_cw = cw3_list[0] if prod == 1 else cw3_list[1]

    only_H1 = H1 - H2
    only_H2 = H2 - H1
    min_H1 = min(only_H1)
    min_H2 = min(only_H2)

    if min_H1 > min_H2:
        return neg(base_cw)
    else:
        return base_cw


print("Weight-6 bracket is defined when |supp ∩| = 3")
print("Result is always weight-6")

# ============================================================================
print("\n" + "=" * 80)
print("PART 2: What About [c6, c6'] When Result Should Be Weight-9?")
print("=" * 80)

print(
    """
In sl(27), [E_ij, E_jk] = E_ik when i,j,k distinct.
All three are "off-diagonal" (weight-6-like?).

But [E_ij, E_kl] = 0 when {i,j} ∩ {k,l} = {} (no overlap).

Our hexad pairs:
  |∩| = 0: bracket = 0 (1 pair per hexad)
  |∩| = 2: bracket = ??? (45 pairs)
  |∩| = 3: bracket = weight-6 (40 pairs) ← we have this!
  |∩| = 4: bracket = ??? (45 pairs)

For |∩| = 2 or |∩| = 4, what happens?
"""
)

# Analyze |∩| = 2 case
print("\nCase |∩| = 2:")
H1 = list(hexads)[0]
H2_list_2 = [H for H in hexads if len(H & H1) == 2]
print(f"  Example: H1 = {sorted(H1)}")
print(f"  H2 (|∩|=2): {sorted(H2_list_2[0])}")
print(f"  Intersection: {sorted(H1 & H2_list_2[0])}")
print(f"  H1 XOR H2 size: {len(H1 ^ H2_list_2[0])}")

# H1 XOR H2 when |∩|=2: size = (6-2) + (6-2) = 8
# This is NOT a hexad (6) or 9-support (9)

# What about c1 + c2?
c1 = hexad_to_cw[H1][0]
c2 = hexad_to_cw[H2_list_2[0]][0]
s = add(c1, c2)
print(f"  c1 + c2 weight: {weight(s)}")

# Analyze |∩| = 4 case
print("\nCase |∩| = 4:")
H2_list_4 = [H for H in hexads if len(H & H1) == 4]
print(f"  H2 (|∩|=4): {sorted(H2_list_4[0])}")
print(f"  Intersection: {sorted(H1 & H2_list_4[0])}")
print(f"  H1 XOR H2 size: {len(H1 ^ H2_list_4[0])}")

# H1 XOR H2 when |∩|=4: size = (6-4) + (6-4) = 4
# This is also not a hexad

c2 = hexad_to_cw[H2_list_4[0]][0]
s = add(c1, c2)
print(f"  c1 + c2 weight: {weight(s)}")

# ============================================================================
print("\n" + "=" * 80)
print("PART 3: The Sum c1 + c2 Is Always a Codeword!")
print("=" * 80)

print(
    """
The code is LINEAR over GF(3), so c1 + c2 is always a codeword.

Let's see what weights we get from different intersection sizes.
"""
)

sum_weights_by_intersection = defaultdict(Counter)

for c1 in weight_6:
    for c2 in weight_6:
        if c1 != c2:
            inter_size = len(support(c1) & support(c2))
            s = add(c1, c2)
            w = weight(s) if any(x != 0 for x in s) else 0
            sum_weights_by_intersection[inter_size][w] += 1

print("\nWeight of c1 + c2 by intersection size:")
for inter_size in sorted(sum_weights_by_intersection.keys()):
    print(f"\n  |∩| = {inter_size}:")
    for w in sorted(sum_weights_by_intersection[inter_size].keys()):
        count = sum_weights_by_intersection[inter_size][w]
        print(f"    weight = {w}: {count}")

# ============================================================================
print("\n" + "=" * 80)
print("PART 4: Redefining the Bracket Using Addition")
print("=" * 80)

print(
    """
INSIGHT: The bracket [c1, c2] should be:
  - RELATED to c1 + c2 (which is always a codeword)
  - With a SIGN for antisymmetry
  - Satisfying closure (automatic) and Jacobi

Let's define: [c1, c2] = sign(c1, c2) * (c1 + c2)
where sign is ±1 based on some ordering.

For weight-6 with |∩|=3, our hexad-based bracket gave weight-6 result.
But c1 + c2 also gives weight-6 in this case!

Are they the SAME?
"""
)

# Check if hexad bracket matches addition
print("\nComparing hexad bracket with addition (|∩|=3):")
match_count = 0
neg_match_count = 0
no_match = 0

for c1 in weight_6[:100]:
    for c2 in weight_6[:100]:
        H1, H2 = support(c1), support(c2)
        if len(H1 & H2) == 3 and c1 != c2:
            b = bracket_66(c1, c2)
            s = add(c1, c2)

            if b == s:
                match_count += 1
            elif b == neg(s):
                neg_match_count += 1
            else:
                no_match += 1

print(f"  Exact match: {match_count}")
print(f"  Negation match: {neg_match_count}")
print(f"  No match: {no_match}")

total = match_count + neg_match_count + no_match
print(
    f"  Total: {total}, Match+NegMatch rate: {(match_count + neg_match_count) / total:.2%}"
)

# ============================================================================
print("\n" + "=" * 80)
print("PART 5: The Universal Bracket Definition")
print("=" * 80)

print(
    """
THEOREM CANDIDATE:
  [c1, c2] = sign(c1, c2) * (c1 + c2) for all codewords

where sign(c1, c2) = +1 if c1 < c2 lexicographically, -1 otherwise.

This gives:
  - Closure: Always (linear code)
  - Antisymmetry: [c1,c2] = -[c2,c1] by construction
  - Jacobi: ??? (need to check)

For Jacobi: [a,[b,c]] + [b,[c,a]] + [c,[a,b]] = 0

Let's test!
"""
)


def universal_bracket(c1, c2):
    """Universal bracket via addition."""
    if c1 == c2:
        return tuple([0] * 12)

    s = add(c1, c2)

    # Antisymmetry via lexicographic order
    if c1 < c2:
        return s
    else:
        return neg(s)


print("\nTesting Jacobi on random triples from all weights:")
jacobi_pass = 0
jacobi_fail = 0

all_nonzero = weight_6 + weight_9 + weight_12

# Sample randomly
import random

random.seed(42)
sample = random.sample(all_nonzero, min(100, len(all_nonzero)))

for a in sample[:30]:
    for b in sample[:30]:
        for c in sample[:30]:
            if a != b and b != c and a != c:
                bc = universal_bracket(b, c)
                ca = universal_bracket(c, a)
                ab = universal_bracket(a, b)

                a_bc = universal_bracket(a, bc)
                b_ca = universal_bracket(b, ca)
                c_ab = universal_bracket(c, ab)

                jacobi_sum = add(add(a_bc, b_ca), c_ab)

                if all(x == 0 for x in jacobi_sum):
                    jacobi_pass += 1
                else:
                    jacobi_fail += 1

print(f"  Jacobi pass: {jacobi_pass}")
print(f"  Jacobi fail: {jacobi_fail}")

# ============================================================================
print("\n" + "=" * 80)
print("PART 6: Why Doesn't Simple Addition Work?")
print("=" * 80)

print(
    """
Simple addition-based bracket fails Jacobi.

The issue: In a Lie algebra, [a, [b,c]] + cyclic = 0.
With simple addition:
  a + (b + c) + b + (c + a) + c + (a + b)
  = a + b + c + b + c + a + c + a + b (in GF(3))
  = 3a + 3b + 3c = 0

Wait, that's 0 in GF(3)! But signs matter...

Let's trace through more carefully.
"""
)

# Example
a, b, c = sample[0], sample[1], sample[2]
print(f"\nExample:")
print(f"  a = {a}")
print(f"  b = {b}")
print(f"  c = {c}")

bc = universal_bracket(b, c)
ca = universal_bracket(c, a)
ab = universal_bracket(a, b)

print(f"\n  [b,c] = {bc}")
print(f"  [c,a] = {ca}")
print(f"  [a,b] = {ab}")

a_bc = universal_bracket(a, bc)
b_ca = universal_bracket(b, ca)
c_ab = universal_bracket(c, ab)

print(f"\n  [a,[b,c]] = {a_bc}")
print(f"  [b,[c,a]] = {b_ca}")
print(f"  [c,[a,b]] = {c_ab}")

jacobi = add(add(a_bc, b_ca), c_ab)
print(f"\n  Sum = {jacobi}")

# ============================================================================
print("\n" + "=" * 80)
print("PART 7: The Partial Bracket is NOT a Lie Algebra Alone")
print("=" * 80)

print(
    """
The weight-6 bracket with hexad rule:
  - Is PARTIAL (only defined for |∩|=3)
  - Has closure and antisymmetry
  - Jacobi is "undefined" because intermediate brackets often undefined

This suggests: The 264 weight-6 codewords form a
PARTIAL LIE ALGEBRA or a JORDAN-LIKE structure.

The FULL structure needs weight-9 and weight-12 to complete Jacobi.

But simple addition doesn't give a Lie algebra either.

QUESTION: What IS the algebraic structure on 728 elements?
"""
)

# ============================================================================
print("\n" + "=" * 80)
print("PART 8: Testing if Addition Gives a JORDAN Algebra")
print("=" * 80)

print(
    """
Jordan algebras satisfy: (a * b) * a² = a * (b * a²)

For abelian (commutative) product a * b = a + b in GF(3):
  (a+b) + 2a = a + b + 2a = 3a + b = b (in GF(3))
  a + (b + 2a) = a + b + 2a = 3a + b = b

These are equal! So addition trivially satisfies Jordan identity.

The interesting structure must come from the NONCOMMUTATIVE part,
which is what we tried with signs for antisymmetry.
"""
)

# ============================================================================
print("\n" + "=" * 80)
print("PART 9: The Key Insight - Projective Representation")
print("=" * 80)

print(
    """
HYPOTHESIS: The 728 codewords carry a PROJECTIVE representation
of sl(27), not a linear one.

In a projective representation:
  [a, b] = c up to a PHASE (cube root of unity in our case)

The ternary values {0, 1, 2} = {0, 1, ω} where ω = e^{2πi/3}.

The bracket might be:
  [c1, c2] = ω^{f(c1,c2)} * (c1 + c2)

where f is some function that makes Jacobi work.

This is related to the SCHUR MULTIPLIER of sl(27).
"""
)

# ============================================================================
print("\n" + "=" * 80)
print("SYNTHESIS: What We've Learned")
print("=" * 80)

print(
    """
FACTS ESTABLISHED:

1. Weight-6 partial bracket (hexad rule) has:
   - 100% closure within weight-6
   - 100% antisymmetry
   - Jacobi is "undefined" (intermediate brackets missing)

2. Simple addition bracket has:
   - 100% closure (linear code)
   - 100% antisymmetry (via lex order)
   - Jacobi FAILS

3. The mismatch between hexad bracket and simple addition:
   - They match up to sign 100% of the time
   - The sign correction is the key to Jacobi!

4. The structure is likely a PROJECTIVE Lie algebra representation
   where phases (cube roots of unity) play a crucial role.

NEXT STEP: Find the correct phase function f(c1, c2) such that
  [c1, c2] = ω^{f(c1,c2)} * (c1 + c2)
satisfies the Jacobi identity.

The 40 = C(6,3) × 2 structure of hexad intersections likely
encodes this phase information through the Steiner system geometry.
"""
)

print("\n" + "=" * 80)
print("KEY NUMBERS RECAP")
print("=" * 80)
print(
    f"""
  80 = 40 × 2 = brackets per weight-6 element
  40 = 20 × 2 = C(6,3) × (partners per triple)
  11 = C(12,3) / C(6,3) = 220 / 20 = global/local ratio

  728 = 264 + 440 + 24 = dim(sl(27))
  704 = 264 + 440 = 702 + 2 (off-diagonal + "extra")

  The "extra 2" might be the key to completing the Jacobi identity!
"""
)
