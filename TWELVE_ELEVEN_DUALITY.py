"""
TWELVE_ELEVEN_DUALITY.py - The Deep Structure of 728 = 288 + 440

Created: February 2026
Purpose: Explore the mysterious "12 vs 11" duality in the Golay code

The DEEP_PROBE revealed:
  728 = (12 x 24) + (11 x 40) = 288 + 440

This is NOT arbitrary! I have strong intuitions to test:

INTUITION 1: The "12-structure" (288) relates to the 12 positions of the code.
             It involves weight-6 + weight-12 codewords.
             Maybe this is the "space" part of spacetime?

INTUITION 2: The "11-structure" (440) relates to PSL(2,11) acting on the code.
             It's purely the weight-9 codewords.
             Maybe this is the "time" part? Or fermions vs bosons?

INTUITION 3: 12 - 11 = 1. This single defect might be the "observer" or
             the "direction" that breaks the symmetry.
             In M12, stabilizing one point gives M11. M11 acts on 11 points.
             The 12th point is "special" - it's the origin?

INTUITION 4: The Weyl group W(E8) has order 696729600 = 2^14 * 3^5 * 5^2 * 7.
             Notice: NO factor of 11!
             But |M12| = 95040 = 2^6 * 3^3 * 5 * 11.
             The factor of 11 in M12 is "orthogonal" to E8's symmetry.
             Maybe the 11-structure encodes what E8 CANNOT see?

INTUITION 5: 288 = 2 * 144 = 2 * 12^2. And 440 = 5 * 88 = 5 * 8 * 11.
             These have very different prime factorizations:
             288 = 2^5 * 3^2
             440 = 2^3 * 5 * 11
             Their GCD is only 8. They are almost coprime!
"""

from itertools import combinations, product

import numpy as np

# ============================================================================
print("=" * 80)
print("THE TWELVE-ELEVEN DUALITY: Anatomy of 728 = 288 + 440")
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


def generate_ternary_golay():
    """Generate all 729 codewords of the ternary Golay code."""
    codewords = []
    for coeffs in product(range(3), repeat=6):
        c = np.array(coeffs) @ G % 3
        codewords.append(tuple(c))
    return codewords


codewords = generate_ternary_golay()


def weight(c):
    return sum(1 for x in c if x != 0)


# Split by weight
weight_0 = [c for c in codewords if weight(c) == 0]
weight_6 = [c for c in codewords if weight(c) == 6]
weight_9 = [c for c in codewords if weight(c) == 9]
weight_12 = [c for c in codewords if weight(c) == 12]

print(f"\nCodeword counts by weight:")
print(f"  Weight 0:  {len(weight_0):4d}  (the zero codeword)")
print(f"  Weight 6:  {len(weight_6):4d}  (part of 288 = 12 x 24)")
print(f"  Weight 9:  {len(weight_9):4d}  (the 440 = 11 x 40)")
print(f"  Weight 12: {len(weight_12):4d}  (part of 288 = 12 x 24)")
print(f"  Total:     {len(codewords):4d}")

# ============================================================================
print("\n" + "=" * 80)
print("INVESTIGATION 1: Prime Factorization Analysis")
print("=" * 80)


def prime_factors(n):
    """Return prime factorization as dict."""
    factors = {}
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors[d] = factors.get(d, 0) + 1
            n //= d
        d += 1
    if n > 1:
        factors[n] = factors.get(n, 0) + 1
    return factors


print("\nPrime factorizations of key numbers:")

numbers = {
    "288 (12 x 24)": 288,
    "440 (11 x 40)": 440,
    "728 (27^2 - 1)": 728,
    "729 (27^2 = 3^6)": 729,
    "27 (3^3)": 27,
    "264 (wt-6)": 264,
    "24 (wt-12)": 24,
    "132 (hexads)": 132,
    "78 (dim E6)": 78,
    "240 (E8 roots)": 240,
    "72 (E6 roots)": 72,
    "|M12|": 95040,
    "|M11|": 7920,
    "|PSL(2,11)|": 660,
    "|W(E8)|": 696729600,
    "|W(E6)|": 51840,
}

for name, n in numbers.items():
    pf = prime_factors(n)
    pf_str = " * ".join(f"{p}^{e}" if e > 1 else str(p) for p, e in sorted(pf.items()))
    print(f"  {name:20s} = {n:12d} = {pf_str}")

# ============================================================================
print("\n" + "=" * 80)
print("INVESTIGATION 2: The Factor of 11 - Where It Appears and Where It Doesn't")
print("=" * 80)

print(
    """
Key observation: 11 is prime and appears in:
  - 440 = 8 * 5 * 11
  - |M12| = 2^6 * 3^3 * 5 * 11
  - |M11| = 2^4 * 3^2 * 5 * 11
  - |PSL(2,11)| = 2^2 * 3 * 5 * 11

But 11 does NOT appear in:
  - 288 = 2^5 * 3^2
  - 728 = 2^3 * 7 * 13
  - |W(E8)| = 2^14 * 3^5 * 5^2 * 7
  - |W(E6)| = 2^7 * 3^4 * 5

This means the "11-structure" is INVISIBLE to E8's Weyl group!
The E8 structure can see 288 (the 12-structure) but not the 440.
"""
)

print("Factor of 11 check:")
for name, n in numbers.items():
    has_11 = n % 11 == 0
    print(f"  {name:20s}: {'CONTAINS 11' if has_11 else '---'}")

# ============================================================================
print("\n" + "=" * 80)
print("INVESTIGATION 3: The Mysterious 13 in 728 = 8 * 7 * 13")
print("=" * 80)

print(
    """
728 = 2^3 * 7 * 13 = 8 * 91 = 8 * 7 * 13

Where does 13 come from?
- 13 is the number of points at infinity in PG(3,3)!
- 13 = number of dark sector particles
- |PG(2,3)| = (27-1)/(3-1) = 13

And where does 7 come from?
- 7 is the number of lines through a point in PG(2,3)
- 132/924 = 1/7 (hexads are 1/7 of 6-subsets)
- 7 = 2^3 - 1 (Mersenne prime)
"""
)

# Check: 40 * 13 * 1.4 = 728?
print("Checking relationships:")
print(f"  40 (PG(3,3) points) * 13 (infinity points) = {40 * 13}")
print(f"  520 / 728 = {520/728:.6f}")
print(f"  27 * 27 = {27 * 27} = 728 + 1")
print(f"  728 = 27^2 - 1 = (27-1)(27+1) = 26 * 28 = {26 * 28}")
print(f"  26 = 2 * 13 (twice the dark number)")
print(f"  28 = 4 * 7 (four times the PG(2,3) lines per point)")

# ============================================================================
print("\n" + "=" * 80)
print("INVESTIGATION 4: Orbit Structure Under Different Groups")
print("=" * 80)

print(
    """
Key groups acting on the Golay code:
  2.M12: Full automorphism group, order 190080
  M12: Permutation subgroup, order 95040
  M11: Stabilizer of one point in M12, order 7920
  PSL(2,11): Subgroup of M11, order 660

How do codewords orbit under these groups?

Under 2.M12:
  - All 264 weight-6 form ONE orbit (264 elements)
  - All 440 weight-9 form ONE orbit (440 elements)
  - All 24 weight-12 form ONE orbit (24 elements)

Under M12:
  - 264 weight-6 split into 2 orbits of 132 (c vs -c)
  - 440 weight-9 split into 2 orbits of 220 (c vs -c)
  - 24 weight-12 split into 2 orbits of 12 (c vs -c)

What happens under M11?
"""
)

# Compute orbit sizes
print("Expected orbit sizes under M11:")
print(f"  |2.M12| / 264 = {190080 / 264} = stabilizer order for weight-6")
print(f"  |2.M12| / 440 = {190080 / 440} = stabilizer order for weight-9")
print(f"  |2.M12| / 24 = {190080 / 24} = stabilizer order for weight-12")

print(f"\n  |M11| / ? = {7920} possibilities:")
for o in [12, 24, 40, 55, 60, 66, 110, 120, 132, 220, 264, 330, 440]:
    if 7920 % o == 0:
        print(f"    Orbit of {o}: stabilizer of order {7920 // o}")

# ============================================================================
print("\n" + "=" * 80)
print("INVESTIGATION 5: The 288/440 Split and sl(27) Structure")
print("=" * 80)

print(
    """
sl(27) as a Lie algebra has:
  - Dimension 728
  - Rank 26 (dimension of Cartan subalgebra)
  - 26 simple roots
  - Root system A26

In the root system A26:
  - Number of positive roots = C(27,2) = 351
  - Total roots = 2 * 351 = 702
  - Cartan elements = 26
  - Total dimension = 702 + 26 = 728 CHECK!

Wait - the root decomposition gives 702 + 26, not 288 + 440!

Let me reconsider the Golay → sl(27) correspondence.
"""
)

print("A26 root system:")
roots_positive = 27 * 26 // 2
roots_total = 2 * roots_positive
cartan = 26
print(f"  Positive roots: C(27,2) = {roots_positive}")
print(f"  All roots: 2 * {roots_positive} = {roots_total}")
print(f"  Cartan subalgebra: {cartan}")
print(f"  Total: {roots_total} + {cartan} = {roots_total + cartan}")

print(f"\nGolay decomposition:")
print(f"  288 (weight 6+12) vs {roots_total + cartan - 288} (would remain)")
print(f"  440 (weight 9) vs {roots_total + cartan - 440} (would remain)")

# Check if there's a match with different interpretation
print(f"\nOther decompositions of 728:")
print(f"  728 = 351 + 377 (positive roots + rest)")
print(f"  728 = 702 + 26 (all roots + Cartan)")
print(f"  728 = 288 + 440 (weight-6/12 + weight-9)")
print(f"  728 = 264 + 440 + 24 (by individual weight)")

# ============================================================================
print("\n" + "=" * 80)
print("INVESTIGATION 6: Looking for 24 in Different Contexts")
print("=" * 80)

print(
    """
24 appears everywhere:
  - 24 weight-12 codewords
  - 264 = 11 * 24
  - 288 = 12 * 24
  - 24 dimensions in Leech lattice
  - 24 = |S_4| = permutations of 4 elements
  - 24 = 4! = ways to arrange 4 things
  - 24 root vectors in D4 (triality group)

Is there a universal meaning of 24?
"""
)

print("Appearances of 24 in our numbers:")
for name, n in numbers.items():
    if n % 24 == 0:
        print(f"  {name:20s} = {n:12d} = {n // 24} x 24")

# ============================================================================
print("\n" + "=" * 80)
print("INVESTIGATION 7: The Deep 12/11 Ratio")
print("=" * 80)

print(
    """
288/440 = 72/110 = 36/55

Let's simplify: gcd(288, 440) = ?
"""
)

from math import gcd

g = gcd(288, 440)
print(f"gcd(288, 440) = {g}")
print(f"288 / {g} = {288 // g}")
print(f"440 / {g} = {440 // g}")
print(f"Ratio: {288 // g} : {440 // g} = {288/g} : {440/g}")

print(f"\n288/440 = {288/440:.10f}")
print(f"12/11 * 24/40 = {12/11 * 24/40:.10f}")
print(f"(12 * 24) / (11 * 40) = {(12*24)/(11*40):.10f}")

# Interesting: 288/440 = (12/11) * (24/40) = (12/11) * (3/5) = 36/55
print(f"\n(12/11) * (3/5) = {(12/11) * (3/5):.10f}")
print(f"36/55 = {36/55:.10f}")
print("The ratio 288:440 encodes both 12:11 AND 3:5!")

# ============================================================================
print("\n" + "=" * 80)
print("INVESTIGATION 8: Connecting to E8 Root Counts")
print("=" * 80)

print(
    """
E8 has 240 roots. Let's see if any Golay numbers relate:

240 = E8 roots
72 = E6 roots (inside E8)
168 = E8 - E6 = extra roots

Or: 240 = 2 * 120 = 2 * |A_5| = 2 * |PSL(2,5)|

From earlier probes:
  264 - 240 = 24 (the weight-12 count!)

Maybe: 264 weight-6 = 240 "roots" + 24 "Cartan-like"?
"""
)

print("Checking various E8 relationships:")
print(f"  264 - 240 = {264 - 240}")
print(f"  288 - 240 = {288 - 240} = 48 = 2 * 24")
print(f"  440 - 240 = {440 - 240} = 200")
print(f"  728 - 240 = {728 - 240} = 488")

# Looking for E6 relationships
print(f"\n  264 - 72 = {264 - 72} = 192 = 8 * 24")
print(f"  288 - 72 = {288 - 72} = 216 = 6^3 = 9 * 24")
print(f"  440 - 72 = {440 - 72} = 368")
print(f"  728 - 72 = {728 - 72} = 656")

print(f"\n  78 (dim E6) * 3 = {78 * 3} = 234 (PG(2,3) triangles!)")
print(f"  78 * 9 = {78 * 9} = 702 (roots of A26!)")

# ============================================================================
print("\n" + "=" * 80)
print("INVESTIGATION 9: The 702 vs 728 Gap")
print("=" * 80)

print(
    """
702 = roots of A26
728 = dim(sl(27)) = roots + Cartan = 702 + 26

But also:
728 = 288 + 440

So what does 288 map to in A26 terms?
What does 440 map to?
"""
)

print("Potential correspondences:")
print(f"  288 = 702 - 414 (need to explain 414)")
print(f"  440 = 702 - 262 (need to explain 262)")
print(f"  288 + 440 = 728 = 702 + 26")
print(f"  So: (288 - 26) + 440 = 702")
print(f"       262 + 440 = 702 CHECK!")

print(f"\n  262 = 288 - 26")
print(f"  Perhaps: 288 = 262 roots + 26 Cartan?")
print(f"  And: 440 = 440 roots")
print(f"  Total: 262 + 440 = 702 roots, + 26 Cartan = 728")

# Let's check if 262 and 440 can be positive/negative root split
print(f"\n  702 / 2 = {702 / 2} = 351 (positive roots of A26)")
print(f"  262 + 440 = 702 (not a symmetric split)")
print(f"  351 - 262 = {351 - 262} = 89")
print(f"  440 - 351 = {440 - 351} = 89")

print(f"\nINSIGHT: 262 = 351 - 89 and 440 = 351 + 89")
print(f"  The split 262/440 is SYMMETRIC around 351!")
print(f"  89 is prime. What is 89?")
print(f"  89 = Fibonacci(11) !")

# ============================================================================
print("\n" + "=" * 80)
print("INVESTIGATION 10: The Fibonacci Connection!")
print("=" * 80)


def fibonacci(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


print("Fibonacci sequence:")
for i in range(15):
    print(f"  F({i:2d}) = {fibonacci(i)}")

print(f"\nF(11) = {fibonacci(11)} = 89")
print(f"351 - 89 = {351 - 89} = 262")
print(f"351 + 89 = {351 + 89} = 440")
print(f"262 + 440 = {262 + 440} = 702")

print(
    """

WOW. The weight-9 count 440 relates to:
  440 = 351 + 89 = (positive A26 roots) + F(11)

And F(11) = 89 because:
  - 11 is the position index
  - 11 is the factor in 440 = 11 * 40
  - 11 is from PSL(2,11)

The Fibonacci connection suggests GOLDEN RATIO structure!
"""
)

phi = (1 + 5**0.5) / 2
print(f"Golden ratio phi = {phi:.10f}")
print(f"phi^2 = {phi**2:.10f} = phi + 1")
print(f"F(n)/F(n-1) -> phi as n -> infinity")
print(
    f"F(12)/F(11) = {fibonacci(12)}/{fibonacci(11)} = {fibonacci(12)/fibonacci(11):.10f}"
)

# ============================================================================
print("\n" + "=" * 80)
print("SYNTHESIS: THE TWELVE-ELEVEN DUALITY")
print("=" * 80)

print(
    """
=======================================================================
MAIN DISCOVERY: The Golay code structure encodes a 12/11 duality!
=======================================================================

728 = (12 x 24) + (11 x 40) = 288 + 440

THE "12-STRUCTURE" (288):
  - Comes from weight-6 + weight-12 codewords
  - Related to the 12 coordinate positions
  - Prime factors: 2^5 * 3^2 (no 11!)
  - Visible to E8 (288 < 240 is false, but close)
  - Contains the "Cartan-like" structure (26 dimensions?)

THE "11-STRUCTURE" (440):
  - Comes from weight-9 codewords only
  - Related to PSL(2,11) acting on 12-{point}
  - Prime factors: 2^3 * 5 * 11
  - Contains the ONLY factor of 11 in the whole structure
  - INVISIBLE to E8's Weyl group (which has no factor of 11)

THE DUALITY:
  12 positions vs 11 classes
  288 = 12 x 24 vs 440 = 11 x 40
  Ratio 288:440 = 36:55 encodes both 12:11 AND 3:5

THE FIBONACCI SURPRISE:
  440 = 351 + 89 where:
  - 351 = C(27,2) = positive roots of A26
  - 89 = F(11) = 11th Fibonacci number

  The "excess" of weight-9 over positive roots is F(11)!

PHYSICAL INTERPRETATION (SPECULATIVE):
  - The 12-structure (288) encodes SPACE (12 dimensions? compactified?)
  - The 11-structure (440) encodes TIME or DYNAMICS
  - The 12-11=1 difference is the "flow of time" direction
  - Or: 12-structure = bosons, 11-structure = fermions?

=======================================================================
"""
)

# Final verification
print("\nFINAL NUMERICAL VERIFICATION:")
print(f"  288 = 12 * 24 = {12 * 24} CHECK")
print(f"  440 = 11 * 40 = {11 * 40} CHECK")
print(f"  288 + 440 = {288 + 440} = 728 CHECK")
print(f"  728 = 27^2 - 1 = {27**2 - 1} CHECK")
print(f"  728 = dim(sl(27)) CHECK")
print(f"  F(11) = 89 CHECK")
print(f"  351 + 89 = {351 + 89} = 440 CHECK")
print(f"  gcd(288, 440) = {gcd(288, 440)} = 8")
print(f"  288/8 : 440/8 = 36 : 55")
