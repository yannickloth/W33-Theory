"""
ANTISYMMETRY_FIX.py - We Have Closure, Now Fix Antisymmetry!

Created: February 2026
Purpose: The product-determined bracket gives 100% closure.
         Now we need to fix the antisymmetry property.

THE SITUATION:
  - When |H1 ∩ H2| = 3, the product of intersection values is either 1 or 2
  - Using this to pick which codeword on H3 gives 100% CLOSURE
  - But antisymmetry fails: [c1,c2] + [c2,c1] ≠ 0

THE FIX:
  - [c1, c2] = +c3 or -c3 needs a SIGN that depends on ORDER
  - Swapping c1 and c2 should flip the sign
  - The intersection product is SYMMETRIC in c1, c2 (same positions, same values)
  - So we need an ASYMMETRIC factor

IDEA: Use the ORDERING of the symmetric difference pieces!
  H1 - H2 and H2 - H1 are swapped when we swap c1, c2
  This provides natural asymmetry.
"""

from collections import Counter
from itertools import combinations, product

import numpy as np

print("=" * 80)
print("FIXING ANTISYMMETRY: The Sign Must Depend on Order!")
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
hexads = set(support(c) for c in weight_6)


def find_codewords_on_hexad(H):
    result = []
    for c in weight_6:
        if support(c) == H:
            result.append(c)
    return result


def neg(c):
    """Negation in GF(3): -c = 2*c mod 3"""
    return tuple((3 - x) % 3 if x != 0 else 0 for x in c)


def add(c1, c2):
    """Addition in GF(3)"""
    return tuple((c1[i] + c2[i]) % 3 for i in range(12))


# ============================================================================
print("\n" + "=" * 80)
print("ANALYSIS: What Changes When We Swap c1 and c2?")
print("=" * 80)

print(
    """
When we compute [c1, c2] vs [c2, c1]:

1. H1 and H2 swap roles
2. H1 ∩ H2 stays the same
3. H3 = H1 XOR H2 stays the same
4. H1 - H2 and H2 - H1 SWAP

The codeword on H3 has values on (H1 - H2) and (H2 - H1).
These two sets swap when we swap c1, c2.

Let's compute an ORDER-DEPENDENT signature.
"""
)


def order_signature(c1, c2):
    """Compute a signature that changes when c1, c2 are swapped."""
    H1, H2 = support(c1), support(c2)
    if len(H1 & H2) != 3:
        return None

    # The positions unique to H1 vs unique to H2
    only_H1 = sorted(H1 - H2)
    only_H2 = sorted(H2 - H1)

    # Values from c1 on positions only in H1
    vals_c1 = tuple(c1[i] for i in only_H1)
    # Values from c2 on positions only in H2
    vals_c2 = tuple(c2[i] for i in only_H2)

    # A simple asymmetric combination: sum over GF(3)
    sum_c1 = sum(vals_c1) % 3
    sum_c2 = sum(vals_c2) % 3

    return (sum_c1, sum_c2)


# Test
print("\nOrder signatures for some pairs:")
for c1, c2 in list(combinations(weight_6, 2))[:10]:
    H1, H2 = support(c1), support(c2)
    if len(H1 & H2) == 3:
        sig12 = order_signature(c1, c2)
        sig21 = order_signature(c2, c1)
        print(
            f"  [c1,c2] sig: {sig12}, [c2,c1] sig: {sig21}, swapped: {sig12 == (sig21[1], sig21[0])}"
        )

# ============================================================================
print("\n" + "=" * 80)
print("NEW BRACKET: Using Order-Dependent Sign")
print("=" * 80)


def intersection_product(c1, c2):
    """Product of values at intersection."""
    H1, H2 = support(c1), support(c2)
    inter = H1 & H2
    prod = 1
    for i in inter:
        prod = (prod * c1[i] * c2[i]) % 3
    return prod


def bracket_v1(c1, c2):
    """Original bracket with product-based selection."""
    H1, H2 = support(c1), support(c2)
    if len(H1 & H2) != 3:
        return None

    H3 = H1 ^ H2
    if H3 not in hexads:
        return None

    cw3_list = find_codewords_on_hexad(H3)
    if len(cw3_list) != 2:
        return None

    prod = intersection_product(c1, c2)

    if prod == 1:
        return cw3_list[0]
    else:
        return cw3_list[1]


def bracket_v2(c1, c2):
    """Bracket with order-dependent sign correction."""
    H1, H2 = support(c1), support(c2)
    if len(H1 & H2) != 3:
        return None

    H3 = H1 ^ H2
    if H3 not in hexads:
        return None

    cw3_list = find_codewords_on_hexad(H3)
    if len(cw3_list) != 2:
        return None

    # Base selection from intersection product
    prod = intersection_product(c1, c2)
    base_cw = cw3_list[0] if prod == 1 else cw3_list[1]

    # Order-dependent sign: compare min elements of H1-H2 vs H2-H1
    only_H1 = H1 - H2
    only_H2 = H2 - H1

    min_H1 = min(only_H1)
    min_H2 = min(only_H2)

    # If min(H1-H2) > min(H2-H1), flip sign
    if min_H1 > min_H2:
        return neg(base_cw)
    else:
        return base_cw


print("\nTesting bracket_v2 for antisymmetry:")
antisym_pass = 0
antisym_fail = 0

for c1 in weight_6[:100]:
    for c2 in weight_6[:100]:
        H1, H2 = support(c1), support(c2)
        if len(H1 & H2) == 3 and c1 != c2:
            b12 = bracket_v2(c1, c2)
            b21 = bracket_v2(c2, c1)

            if b12 is not None and b21 is not None:
                sum_bracket = add(b12, b21)
                if all(x == 0 for x in sum_bracket):
                    antisym_pass += 1
                else:
                    antisym_fail += 1

print(f"  Antisymmetry satisfied: {antisym_pass}")
print(f"  Antisymmetry violated: {antisym_fail}")
print(f"  Rate: {antisym_pass / (antisym_pass + antisym_fail + 0.001):.2%}")

# ============================================================================
print("\n" + "=" * 80)
print("ALTERNATIVE: Try Different Order Rules")
print("=" * 80)


def bracket_v3(c1, c2):
    """Use lexicographic comparison of the full codewords."""
    H1, H2 = support(c1), support(c2)
    if len(H1 & H2) != 3:
        return None

    H3 = H1 ^ H2
    if H3 not in hexads:
        return None

    cw3_list = find_codewords_on_hexad(H3)
    if len(cw3_list) != 2:
        return None

    # Base: first codeword on H3
    base_cw = cw3_list[0]

    # Sign from lexicographic comparison of c1, c2
    # This is naturally antisymmetric
    if c1 < c2:
        return base_cw
    else:
        return neg(base_cw)


print("\nTesting bracket_v3 (lex order) for antisymmetry:")
antisym_pass = 0
antisym_fail = 0
closure_pass = 0
closure_fail = 0

for c1 in weight_6[:100]:
    for c2 in weight_6[:100]:
        H1, H2 = support(c1), support(c2)
        if len(H1 & H2) == 3 and c1 != c2:
            b12 = bracket_v3(c1, c2)
            b21 = bracket_v3(c2, c1)

            if b12 is not None and b21 is not None:
                # Check closure
                if b12 in codeword_set:
                    closure_pass += 1
                else:
                    closure_fail += 1

                # Check antisymmetry
                sum_bracket = add(b12, b21)
                if all(x == 0 for x in sum_bracket):
                    antisym_pass += 1
                else:
                    antisym_fail += 1

print(f"  Closure: {closure_pass} pass, {closure_fail} fail")
print(f"  Antisymmetry: {antisym_pass} pass, {antisym_fail} fail")

# ============================================================================
print("\n" + "=" * 80)
print("V4: Combine Intersection Product with Lex Order")
print("=" * 80)


def bracket_v4(c1, c2):
    """Combine intersection product with lex order for antisymmetry."""
    H1, H2 = support(c1), support(c2)
    if len(H1 & H2) != 3:
        return None

    H3 = H1 ^ H2
    if H3 not in hexads:
        return None

    cw3_list = find_codewords_on_hexad(H3)
    if len(cw3_list) != 2:
        return None

    # Choose based on intersection product (for closure)
    prod = intersection_product(c1, c2)
    base_cw = cw3_list[0] if prod == 1 else cw3_list[1]

    # Apply sign based on lex order (for antisymmetry)
    if c1 < c2:
        return base_cw
    else:
        return neg(base_cw)


print("\nTesting bracket_v4 (product + lex):")
antisym_pass = 0
antisym_fail = 0
closure_pass = 0
closure_fail = 0

for c1 in weight_6[:100]:
    for c2 in weight_6[:100]:
        H1, H2 = support(c1), support(c2)
        if len(H1 & H2) == 3 and c1 != c2:
            b12 = bracket_v4(c1, c2)
            b21 = bracket_v4(c2, c1)

            if b12 is not None and b21 is not None:
                # Check closure
                if b12 in codeword_set:
                    closure_pass += 1
                else:
                    closure_fail += 1

                # Check antisymmetry
                sum_bracket = add(b12, b21)
                if all(x == 0 for x in sum_bracket):
                    antisym_pass += 1
                else:
                    antisym_fail += 1

print(f"  Closure: {closure_pass} pass, {closure_fail} fail")
print(f"  Antisymmetry: {antisym_pass} pass, {antisym_fail} fail")

if antisym_pass > 0 and antisym_fail == 0:
    print("\n  *** ANTISYMMETRY ACHIEVED! ***")

    # Now test Jacobi identity
    print("\n  Testing Jacobi identity: [a,[b,c]] + [b,[c,a]] + [c,[a,b]] = 0")
    jacobi_pass = 0
    jacobi_fail = 0

    sample = weight_6[:30]
    for a in sample:
        for b in sample:
            for c in sample:
                if a != b and b != c and a != c:
                    # Only test if all intermediate brackets are defined
                    bc = bracket_v4(b, c)
                    ca = bracket_v4(c, a)
                    ab = bracket_v4(a, b)

                    if bc is not None and ca is not None and ab is not None:
                        a_bc = bracket_v4(a, bc) if bc in weight_6 else None
                        b_ca = bracket_v4(b, ca) if ca in weight_6 else None
                        c_ab = bracket_v4(c, ab) if ab in weight_6 else None

                        if a_bc is not None and b_ca is not None and c_ab is not None:
                            jacobi_sum = add(add(a_bc, b_ca), c_ab)
                            if all(x == 0 for x in jacobi_sum):
                                jacobi_pass += 1
                            else:
                                jacobi_fail += 1

    print(f"    Jacobi pass: {jacobi_pass}")
    print(f"    Jacobi fail: {jacobi_fail}")

# ============================================================================
print("\n" + "=" * 80)
print("DEEPER ANALYSIS: Why Does Product Matter for Closure?")
print("=" * 80)

print(
    """
The intersection product being exactly 1 or 2 (never 0) is key.
Each hexad has 2 codewords: c and -c.
The intersection product distinguishes between "compatible" and "incompatible"
combinations.

Let me analyze this more carefully...
"""
)

# For a fixed hexad pair with |∩|=3, how do the 4 codeword pairs behave?
print("\nFor hexad pairs with |∩|=3, analyzing all 4 codeword combinations:")

analyzed = 0
for H1, H2 in combinations(hexads, 2):
    if len(H1 & H2) == 3 and analyzed < 3:
        H3 = H1 ^ H2
        cw1 = find_codewords_on_hexad(H1)
        cw2 = find_codewords_on_hexad(H2)
        cw3 = find_codewords_on_hexad(H3)

        print(f"\nH1={sorted(H1)}, H2={sorted(H2)}, H3={sorted(H3)}")

        for c1 in cw1:
            for c2 in cw2:
                prod = intersection_product(c1, c2)
                base_cw = cw3[0] if prod == 1 else cw3[1]
                print(
                    f"  c1, c2 -> prod={prod} -> {'c3' if base_cw == cw3[0] else '-c3'}"
                )

        analyzed += 1

# ============================================================================
print("\n" + "=" * 80)
print("SYNTHESIS")
print("=" * 80)

print(
    """
FINDINGS:

1. CLOSURE (100%): The intersection product determines which of the two
   codewords on H3 to choose. This gives perfect closure.

2. ANTISYMMETRY: Combining the product rule with lexicographic ordering
   gives both closure AND antisymmetry (if v4 works).

3. JACOBI: Still needs to be verified fully.

THE BRACKET STRUCTURE IS EMERGING!

The key insight: The ternary Golay code has a natural "bracket" operation
on weight-6 codewords defined by:
  - Support: H3 = H1 XOR H2 (when |H1∩H2|=3)
  - Sign selection: intersection product
  - Order sign: lexicographic comparison

This partial bracket on weight-6 might extend to the full 728 elements
via the weight-9 and weight-12 codewords.
"""
)
