"""
HEXAD_BRACKET.py - The Bracket Lives in Hexad Intersection Structure!

Created: February 2026
Purpose: Exploit the discovered property that symmetric differences of
         intersecting hexads are always hexads.

THE KEY FINDING FROM BRACKET_MYSTERY:
  When |H1 ∩ H2| = 3, the symmetric diff H1 XOR H2 is ALWAYS a hexad!
  This was true for ALL 6060 pairs tested.

This is exactly what we need for a bracket:
  [c1, c2] should depend on c1 and c2 and produce c3

The hexad structure gives us: H1, H2 → H3 = H1 XOR H2

But we also need to handle the VALUES on the supports, not just supports.
A codeword c has support (a hexad) plus values {1,2} at those positions.

STRATEGY:
  1. When supp(c1) ∩ supp(c2) has size 3, define [c1, c2] using
     the values on the symmetric difference
  2. Check if this operation is antisymmetric and satisfies Jacobi
  3. Check if it closes on the code
"""

from collections import Counter
from itertools import combinations, product

import numpy as np

# ============================================================================
print("=" * 80)
print("HEXAD BRACKET: Using Support Structure to Define Lie Bracket")
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
codeword_set = set(codewords)
nonzero = [c for c in codewords if any(x != 0 for x in c)]


def weight(c):
    return sum(1 for x in c if x != 0)


def support(c):
    return frozenset(i for i, x in enumerate(c) if x != 0)


weight_6 = [c for c in nonzero if weight(c) == 6]
weight_9 = [c for c in nonzero if weight(c) == 9]
weight_12 = [c for c in nonzero if weight(c) == 12]

hexads = set(support(c) for c in weight_6)

print(
    f"Weight-6: {len(weight_6)}, Weight-9: {len(weight_9)}, Weight-12: {len(weight_12)}"
)
print(f"Distinct hexads: {len(hexads)}")

# ============================================================================
print("\n" + "=" * 80)
print("PART 1: Hexad Operations")
print("=" * 80)

# For hexads with |intersection| = 3, symmetric diff is always a hexad
# Let's verify this more systematically

print("\nCounting hexad pairs by intersection size:")
intersection_counts = Counter()
for H1, H2 in combinations(hexads, 2):
    inter_size = len(H1 & H2)
    intersection_counts[inter_size] += 1

for size, count in sorted(intersection_counts.items()):
    print(f"  |H1 ∩ H2| = {size}: {count} pairs")

# Check which give hexads as symmetric diff
print("\nSymmetric diff results:")
for size in sorted(intersection_counts.keys()):
    hexad_results = 0
    non_hexad_results = 0
    for H1, H2 in combinations(hexads, 2):
        if len(H1 & H2) == size:
            symdiff = H1 ^ H2
            if symdiff in hexads:
                hexad_results += 1
            else:
                non_hexad_results += 1
    print(f"  |∩| = {size}: hexad={hexad_results}, not_hexad={non_hexad_results}")

# ============================================================================
print("\n" + "=" * 80)
print("PART 2: Codewords on Symmetric Difference")
print("=" * 80)

print(
    """
When |H1 ∩ H2| = 3, symdiff H1 XOR H2 is a hexad (size 6).
Given codewords c1 on H1 and c2 on H2, can we construct c3 on H3 = H1 XOR H2?

The symmetric difference H1 XOR H2 = (H1 - H2) ∪ (H2 - H1)
  = (3 positions from H1 not in H2) ∪ (3 positions from H2 not in H1)

Let's see what values appear...
"""
)


def find_codewords_on_hexad(H):
    """Find all weight-6 codewords with support exactly H."""
    result = []
    for c in weight_6:
        if support(c) == H:
            result.append(c)
    return result


# Pick some hexad pairs with intersection 3
example_count = 0
for H1, H2 in combinations(hexads, 2):
    if len(H1 & H2) == 3 and example_count < 5:
        H3 = H1 ^ H2
        if H3 in hexads:
            cw1 = find_codewords_on_hexad(H1)
            cw2 = find_codewords_on_hexad(H2)
            cw3 = find_codewords_on_hexad(H3)

            print(f"\nExample {example_count + 1}:")
            print(f"  H1 = {sorted(H1)}, codewords: {len(cw1)}")
            print(f"  H2 = {sorted(H2)}, codewords: {len(cw2)}")
            print(f"  H3 = H1 XOR H2 = {sorted(H3)}, codewords: {len(cw3)}")
            print(f"  H1 ∩ H2 = {sorted(H1 & H2)}")

            example_count += 1

# ============================================================================
print("\n" + "=" * 80)
print("PART 3: Defining the Bracket Operation")
print("=" * 80)

print(
    """
For c1 with support H1 and c2 with support H2:

If |H1 ∩ H2| = 3:
  Let H3 = H1 XOR H2 (the resulting hexad)

  Define [c1, c2] = c3 where:
    - c3 has support H3
    - Values on H3 are determined by some rule involving c1 and c2

The question: WHAT rule for the values?

Option A: c3[i] = c1[i] for i in H1 - H2, c3[i] = c2[i] for i in H2 - H1
Option B: c3[i] = c1[i] * c2[j] for some pairing
Option C: Use the Steiner system structure to define pairing
"""
)


def bracket_attempt_A(c1, c2):
    """Try Option A: concatenate values from non-overlapping parts."""
    H1, H2 = support(c1), support(c2)
    if len(H1 & H2) != 3:
        return None  # Only defined for intersection size 3

    H3 = H1 ^ H2
    if H3 not in hexads:
        return None

    # Build c3
    c3 = [0] * 12
    for i in H1 - H2:
        c3[i] = c1[i]
    for i in H2 - H1:
        c3[i] = c2[i]

    return tuple(c3)


# Test Option A
print("\nTesting Option A: Direct value transfer")
bracket_in_code = 0
bracket_not_in_code = 0

for c1 in weight_6[:50]:
    for c2 in weight_6[:50]:
        H1, H2 = support(c1), support(c2)
        if len(H1 & H2) == 3:
            c3 = bracket_attempt_A(c1, c2)
            if c3 is not None:
                if c3 in codeword_set:
                    bracket_in_code += 1
                else:
                    bracket_not_in_code += 1

print(f"  In code: {bracket_in_code}")
print(f"  Not in code: {bracket_not_in_code}")
print(
    f"  Closure rate: {bracket_in_code / (bracket_in_code + bracket_not_in_code + 0.001):.2%}"
)

# ============================================================================
print("\n" + "=" * 80)
print("PART 4: The Matching Problem")
print("=" * 80)

print(
    """
Option A gives low closure. The issue: we need to match values carefully.

Key insight: Each hexad has exactly 2 codewords (c and -c = 2c mod 3).
So H3 has 2 codewords. We need to pick the RIGHT one!

Maybe: The intersection H1 ∩ H2 determines which codeword on H3 we get.
The 3 values at the intersection from c1 and c2 tell us something.
"""
)


def intersection_signature(c1, c2):
    """Get the values at the intersection positions."""
    H1, H2 = support(c1), support(c2)
    inter = H1 & H2
    vals1 = tuple(c1[i] for i in sorted(inter))
    vals2 = tuple(c2[i] for i in sorted(inter))
    return vals1, vals2


# Analyze intersection signatures
print("\nIntersection signatures for weight-6 pairs with |∩| = 3:")
sig_counts = Counter()
for c1, c2 in list(combinations(weight_6, 2))[:500]:
    H1, H2 = support(c1), support(c2)
    if len(H1 & H2) == 3:
        sig = intersection_signature(c1, c2)
        sig_counts[sig] += 1

print(f"  Found {len(sig_counts)} distinct signature pairs")
for sig, count in sorted(sig_counts.items(), key=lambda x: -x[1])[:10]:
    print(f"    {sig}: {count}")

# ============================================================================
print("\n" + "=" * 80)
print("PART 5: Product Rule Attempt")
print("=" * 80)

print(
    """
What if the bracket uses the intersection values multiplicatively?

For positions in the intersection, c1[i] and c2[i] are both nonzero.
Their product c1[i] * c2[i] (mod 3) might encode sign/direction info.
"""
)


def intersection_product(c1, c2):
    """Compute product of values at intersection positions."""
    H1, H2 = support(c1), support(c2)
    inter = H1 & H2
    prod = 1
    for i in inter:
        prod = (prod * c1[i] * c2[i]) % 3
    return prod


# Check distribution of products
print("\nProduct of intersection values (mod 3):")
prod_counts = Counter()
for c1, c2 in list(combinations(weight_6, 2))[:1000]:
    H1, H2 = support(c1), support(c2)
    if len(H1 & H2) == 3:
        prod = intersection_product(c1, c2)
        prod_counts[prod] += 1

for prod, count in sorted(prod_counts.items()):
    print(f"  Product = {prod}: {count} pairs")

# ============================================================================
print("\n" + "=" * 80)
print("PART 6: The Sign-Determined Bracket")
print("=" * 80)

print(
    """
IDEA: The intersection product determines which of the 2 codewords on H3.

If product = 1, choose c3
If product = 2, choose -c3 (= 2*c3 mod 3)

Let's test this!
"""
)


def bracket_attempt_B(c1, c2):
    """Try: use intersection product to select codeword on H3."""
    H1, H2 = support(c1), support(c2)
    if len(H1 & H2) != 3:
        return None

    H3 = H1 ^ H2
    if H3 not in hexads:
        return None

    # Find codewords on H3
    cw3_list = find_codewords_on_hexad(H3)
    if len(cw3_list) != 2:
        return None

    # Use intersection product to select
    prod = intersection_product(c1, c2)

    if prod == 0:
        return None  # Shouldn't happen if both have full support on intersection
    elif prod == 1:
        return cw3_list[0]
    else:  # prod == 2
        return cw3_list[1]


# Test Option B
print("\nTesting Option B: Product-determined selection")
bracket_in_code = 0
bracket_not_in_code = 0
bracket_undefined = 0

for c1 in weight_6[:100]:
    for c2 in weight_6[:100]:
        H1, H2 = support(c1), support(c2)
        if len(H1 & H2) == 3:
            c3 = bracket_attempt_B(c1, c2)
            if c3 is None:
                bracket_undefined += 1
            elif c3 in codeword_set:
                bracket_in_code += 1
            else:
                bracket_not_in_code += 1

print(f"  In code: {bracket_in_code}")
print(f"  Not in code: {bracket_not_in_code}")
print(f"  Undefined: {bracket_undefined}")

if bracket_in_code + bracket_not_in_code > 0:
    print(
        f"  Closure rate: {bracket_in_code / (bracket_in_code + bracket_not_in_code):.2%}"
    )

# ============================================================================
print("\n" + "=" * 80)
print("PART 7: Checking Antisymmetry")
print("=" * 80)

print(
    """
A Lie bracket must satisfy [c1, c2] = -[c2, c1].
In our GF(3) setting, this means [c1, c2] = 2*[c2, c1] (mod 3).
Or equivalently: [c1, c2] + [c2, c1] = 0 (mod 3).
"""
)

antisymmetry_pass = 0
antisymmetry_fail = 0

for c1 in weight_6[:50]:
    for c2 in weight_6[:50]:
        if c1 != c2:
            b12 = bracket_attempt_B(c1, c2)
            b21 = bracket_attempt_B(c2, c1)

            if b12 is not None and b21 is not None:
                # Check if b12 + b21 = 0 (mod 3)
                sum_bracket = tuple((b12[i] + b21[i]) % 3 for i in range(12))
                if all(x == 0 for x in sum_bracket):
                    antisymmetry_pass += 1
                else:
                    antisymmetry_fail += 1

print(f"  Antisymmetry satisfied: {antisymmetry_pass}")
print(f"  Antisymmetry violated: {antisymmetry_fail}")

# ============================================================================
print("\n" + "=" * 80)
print("PART 8: The Deep Issue")
print("=" * 80)

print(
    """
The bracket attempts so far don't work perfectly.

FUNDAMENTAL ISSUE:
  The Golay code has 728 nonzero codewords.
  sl(27) has 728 basis elements.
  But sl(27) has a SPECIFIC bracket structure determined by matrix multiplication.

  The Golay code has structure determined by the STEINER SYSTEM.

  These are two different mathematical objects!

RESOLUTION OPTIONS:
  1. The correspondence is NOT a direct "codeword = basis element" map.
     Instead, codewords PARAMETRIZE or INDEX the basis elements.

  2. There's a clever encoding where the Steiner structure
     BECOMES the matrix bracket structure under some transformation.

  3. The Lie algebra structure emerges from a DIFFERENT construction
     that happens to use 728 pieces of data from the code.

The most likely scenario: the 728 codewords encode the 728 basis
elements via a sophisticated map that respects both structures.
"""
)

# ============================================================================
print("\n" + "=" * 80)
print("PART 9: Counting Arguments")
print("=" * 80)

print(
    """
Let's check if the numbers even work out for a bracket:

For weight-6 codewords:
  264 total, 132 hexads with 2 codewords each

Pairs with |∩| = 3 should bracket to give weight-6 codewords.
How many such pairs?
"""
)

# Count pairs with intersection 3
pairs_int_3 = 0
for c1, c2 in combinations(weight_6, 2):
    H1, H2 = support(c1), support(c2)
    if len(H1 & H2) == 3:
        pairs_int_3 += 1

print(f"Pairs of weight-6 with |∩| = 3: {pairs_int_3}")

# For sl(27), how many [E_ij, E_jk] = E_ik type brackets?
# These are ordered triples (i,j,k) with i,j,k distinct
# That's 27 * 26 * 25 = 17550
print(f"\nFor sl(27): [E_ij, E_jk] = E_ik type brackets: 27*26*25 = {27*26*25}")

print(f"\nRatio: {pairs_int_3} / {27*26*25} = {pairs_int_3 / 17550:.3f}")

# ============================================================================
print("\n" + "=" * 80)
print("SYNTHESIS: What We've Learned")
print("=" * 80)

print(
    """
KEY INSIGHTS:

1. When two hexads intersect in 3 positions, their symmetric
   difference is ALWAYS another hexad. This is a beautiful
   algebraic property of the Steiner system S(5,6,12).

2. Simple attempts to define a bracket using this property
   don't immediately close or satisfy antisymmetry.

3. The correspondence 728 codewords <-> 728 basis elements
   is more subtle than a direct identification.

NEXT STEPS TO CRACK THIS:

A) Study how M12 acts on pairs and triples of codewords.
   The bracket structure should be M12-equivariant.

B) Look at the WEIGHT-9 codewords. They're the largest class
   (440 elements) and we haven't properly incorporated them.

C) Consider that the Lie algebra might emerge from a
   CROSSED PRODUCT or GROUP ALGEBRA construction involving
   the Mathieu group.

D) The 27 visible particles (AG(3,3) points) should be the
   matrix indices. Find the map: codeword -> (i,j) pair.
"""
)
