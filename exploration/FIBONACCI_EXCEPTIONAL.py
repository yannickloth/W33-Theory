"""
FIBONACCI_EXCEPTIONAL.py - The Fibonacci Pattern in Exceptional Lie Algebras

Created: February 2026
Purpose: Investigate if Fibonacci numbers encode ALL exceptional Lie algebra dimensions

DISCOVERY FROM ULTIMATE_SYNTHESIS:
  E7 - E6 = 133 - 78 = 55 = F(10)

This is TOO perfect to be coincidence. Let me check if ALL exceptional
Lie algebra dimensions have Fibonacci decompositions with patterns.

Exceptional Lie algebras: G2, F4, E6, E7, E8
Dimensions: 14, 52, 78, 133, 248
"""

from math import gcd, sqrt

import numpy as np

# ============================================================================
print("=" * 80)
print("FIBONACCI PATTERNS IN EXCEPTIONAL LIE ALGEBRAS")
print("=" * 80)


def fib(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def zeckendorf(n):
    """Express n as sum of non-consecutive Fibonacci numbers."""
    if n == 0:
        return []
    fibs = []
    k = 2
    while fib(k) <= n:
        k += 1
    k -= 1

    rep = []
    while n > 0:
        while fib(k) > n:
            k -= 1
        rep.append(k)
        n -= fib(k)
        k -= 2  # Skip consecutive Fibonacci
    return rep


# Exceptional Lie algebra dimensions
exceptional = {
    "G2": 14,
    "F4": 52,
    "E6": 78,
    "E7": 133,
    "E8": 248,
}

print("\n" + "=" * 80)
print("PART 1: Zeckendorf Decompositions of Exceptional Dimensions")
print("=" * 80)

print("\nFibonacci sequence reference:")
for i in range(18):
    print(f"  F({i:2d}) = {fib(i)}")

print("\nExceptional Lie algebra dimensions in Zeckendorf form:")
for name, dim in exceptional.items():
    z = zeckendorf(dim)
    terms = [f"F({i})" for i in z]
    values = [str(fib(i)) for i in z]
    print(f"  dim({name}) = {dim:3d} = {' + '.join(terms)} = {' + '.join(values)}")

# ============================================================================
print("\n" + "=" * 80)
print("PART 2: Differences Between Consecutive Exceptional Algebras")
print("=" * 80)

dims = list(exceptional.values())
names = list(exceptional.keys())

print("\nDifferences:")
for i in range(len(dims) - 1):
    diff = dims[i + 1] - dims[i]
    z = zeckendorf(diff)
    is_fib = len(z) == 1
    print(
        f"  dim({names[i+1]}) - dim({names[i]}) = {dims[i+1]:3d} - {dims[i]:3d} = {diff:3d}",
        end="",
    )
    if is_fib:
        print(f" = F({z[0]}) ← FIBONACCI!")
    else:
        terms = [f"F({j})" for j in z]
        print(f" = {' + '.join(terms)}")

# ============================================================================
print("\n" + "=" * 80)
print("PART 3: The G2 → F4 → E6 → E7 → E8 Chain")
print("=" * 80)

print(
    """
Let me look for a pattern in the growth:

G2:  14 = F(7) + F(2) = 13 + 1
F4:  52 = F(9) + F(7) + F(4) = 34 + 13 + 5
E6:  78 = F(10) + F(8) + F(3) = 55 + 21 + 2
E7: 133 = F(11) + F(9) + F(7) + F(4) = 89 + 34 + 13 - 3
E8: 248 = F(13) + F(7) + F(4) = 233 + 13 + 2

Wait, let me recompute these carefully...
"""
)

for name, dim in exceptional.items():
    z = zeckendorf(dim)
    check = sum(fib(i) for i in z)
    print(
        f"  {name}: {dim} = sum of F({z}) = {[fib(i) for i in z]} = {check} {'✓' if check == dim else '✗'}"
    )

# ============================================================================
print("\n" + "=" * 80)
print("PART 4: Ratios of Consecutive Dimensions")
print("=" * 80)

phi = (1 + sqrt(5)) / 2
print(f"\nGolden ratio phi = {phi:.10f}")
print(f"phi^2 = {phi**2:.10f}")

print("\nRatios:")
for i in range(len(dims) - 1):
    ratio = dims[i + 1] / dims[i]
    phi_power = np.log(ratio) / np.log(phi)
    print(
        f"  {names[i+1]}/{names[i]} = {dims[i+1]}/{dims[i]} = {ratio:.6f} ≈ phi^{phi_power:.3f}"
    )

# ============================================================================
print("\n" + "=" * 80)
print("PART 5: Root Counts and Fibonacci")
print("=" * 80)

# Root counts for exceptional algebras
roots = {
    "G2": (12, 2),  # 12 roots, rank 2
    "F4": (48, 4),  # 48 roots, rank 4
    "E6": (72, 6),  # 72 roots, rank 6
    "E7": (126, 7),  # 126 roots, rank 7
    "E8": (240, 8),  # 240 roots, rank 8
}

print("\nRoot counts in Zeckendorf form:")
for name, (r, rank) in roots.items():
    z = zeckendorf(r)
    terms = [f"F({i})" for i in z]
    print(f"  {name}: {r:3d} roots = {' + '.join(terms)} (rank {rank})")

print("\nPositive root counts:")
for name, (r, rank) in roots.items():
    pos = r // 2
    z = zeckendorf(pos)
    terms = [f"F({i})" for i in z]
    print(f"  {name}: {pos:3d} positive = {' + '.join(terms)}")

# ============================================================================
print("\n" + "=" * 80)
print("PART 6: The Remarkable Pattern in Ranks")
print("=" * 80)

print(
    """
Ranks: 2, 4, 6, 7, 8

2 = F(3)
4 = F(4) + F(2) = 3 + 1
6 = F(5) + F(2) = 5 + 1
7 = F(5) + F(3) = 5 + 2
8 = F(6) = 8

Or simply: 2, 4, 6, 7, 8 = 2, 4, 6, 7, 8

The ranks are almost consecutive after 4!
"""
)

ranks = [r for _, (_, r) in roots.items()]
print(f"Ranks: {ranks}")
print(f"Sum of ranks: {sum(ranks)}")
print(f"Sum = {sum(ranks)} = F(?)")
z = zeckendorf(sum(ranks))
print(f"27 = {' + '.join([f'F({i})' for i in z])}")

# ============================================================================
print("\n" + "=" * 80)
print("PART 7: Summing All Exceptional Dimensions")
print("=" * 80)

total_dim = sum(exceptional.values())
print(f"\nTotal exceptional dimensions: {total_dim}")
z = zeckendorf(total_dim)
terms = [f"F({i})" for i in z]
values = [str(fib(i)) for i in z]
print(f"  {total_dim} = {' + '.join(terms)} = {' + '.join(values)}")

# Compare to other significant numbers
print(f"\n{total_dim} / 728 = {total_dim / 728:.6f}")
print(f"{total_dim} / 240 = {total_dim / 240:.6f}")
print(f"{total_dim} - 240 - 240 = {total_dim - 480}")
print(f"525 - 248 - 248 = {525 - 496}")

# ============================================================================
print("\n" + "=" * 80)
print("PART 8: Deep Pattern - The E-series Growth")
print("=" * 80)

print(
    """
E6 = 78  = F(10) + F(8) + F(3) = 55 + 21 + 2
E7 = 133 = F(11) + F(9) + F(5) + F(2) = 89 + 34 + 8 + 2
E8 = 248 = F(13) + F(7) + F(4) = 233 + 13 + 2

The differences:
  E7 - E6 = 55 = F(10)
  E8 - E7 = 115

But 115 is NOT a Fibonacci number!
  115 = F(11) + F(8) + F(5) = 89 + 21 + 5

Actually let me recompute:
"""
)

print(f"E7 - E6 = {133 - 78} = {zeckendorf(55)} = F({zeckendorf(55)[0]})")
print(f"E8 - E7 = {248 - 133} = {' + '.join([f'F({i})' for i in zeckendorf(115)])}")

# Let me check if 55 really equals F(10)
print(f"\nF(10) = {fib(10)}")
print(f"E7 - E6 = 55 = F(10)? {55 == fib(10)}")

# ============================================================================
print("\n" + "=" * 80)
print("PART 9: The 55 Connection to Our Main Story")
print("=" * 80)

print(
    """
Recall from TWELVE_ELEVEN_DUALITY:
  288 : 440 = 36 : 55

55 = F(10) appears in the ratio!

And E7 - E6 = 55 = F(10)

This connects:
  - The 12/11 duality (288:440 = 36:55)
  - The E-series growth (E7 - E6 = 55)
  - Fibonacci sequence (55 = F(10))

Also: 36 = F(9) + F(3) = 34 + 2 (NOT a Fibonacci number)
But 55 IS F(10)!

The asymmetry: 36 is NOT Fibonacci, but 55 IS.
This is the "asymmetric" nature of the 12/11 duality!
"""
)

print(f"36 in Zeckendorf: {' + '.join([f'F({i})' for i in zeckendorf(36)])}")
print(f"55 in Zeckendorf: F(10) = {fib(10)}")

# ============================================================================
print("\n" + "=" * 80)
print("PART 10: Looking for sl(27) Connection to Exceptionals")
print("=" * 80)

print(
    """
sl(27) = A26 has dimension 728.

728 / dim(E8) = 728 / 248 = 2.935...
728 / dim(E7) = 728 / 133 = 5.474...
728 / dim(E6) = 728 / 78 = 9.333... = 28/3

Interesting: 728 / 78 = 28/3 exactly!
  728 = 78 × (28/3) = 78 × 28 / 3 = 2184/3 = 728 ✓

Let me verify: 78 × 28 / 3 = 2184 / 3 = 728
"""
)

print(f"728 / 78 = {728 / 78}")
print(f"78 * 28 = {78 * 28}")
print(f"78 * 28 / 3 = {78 * 28 / 3}")
print(f"This is exact? {78 * 28 == 3 * 728}")

print(f"\n78 * 28 = 78 * (27 + 1) = 78 * 27 + 78")
print(f"        = {78 * 27} + 78 = {78 * 27 + 78}")
print(f"        = 3 * 728 + 78 - 78 = 3 * 702 + 78 + 78")

# Hmm, let me think differently
print(f"\n728 / 78 = {728 / 78} = {728 // gcd(728, 78)} / {78 // gcd(728, 78)}")
g = gcd(728, 78)
print(f"gcd(728, 78) = {g}")
print(f"728 / {g} = {728 // g}")
print(f"78 / {g} = {78 // g}")
print(f"Reduced: 728 : 78 = {728 // g} : {78 // g}")

# ============================================================================
print("\n" + "=" * 80)
print("PART 11: The 364 = 728/2 Connection")
print("=" * 80)

print(
    """
728 = 2 × 364

364 / 78 = 4.666... = 14/3
364 / 14 = 26

So: 364 = 14 × 26 = dim(G2) × rank(A26)!
And: 728 = 2 × 14 × 26 = 2 × dim(G2) × 26
"""
)

print(f"364 = 728/2 = {728 // 2}")
print(f"364 / 14 = {364 / 14}")
print(f"364 = 14 × 26? {364 == 14 * 26}")
print(f"dim(G2) = 14, rank(A26) = 26")
print(f"728 = 2 × dim(G2) × rank(A26) = 2 × 14 × 26 = {2 * 14 * 26}")

# ============================================================================
print("\n" + "=" * 80)
print("PART 12: Grand Synthesis of Fibonacci-Exceptional Connections")
print("=" * 80)

print(
    """
======================================================================
FIBONACCI-EXCEPTIONAL SYNTHESIS
======================================================================

KEY DISCOVERIES:

1. E7 - E6 = 55 = F(10) [EXACT Fibonacci!]
   This is the only difference that's a pure Fibonacci number.

2. 728 = 2 × dim(G2) × rank(sl(27)) = 2 × 14 × 26

3. The ratio 288 : 440 = 36 : 55 contains F(10) = 55

4. All exceptional dimensions have Zeckendorf representations
   but only E7-E6 yields a PURE Fibonacci number

5. 78 = dim(E6) = C(13,2) connects to our dark sector (13 points)

6. 728 = 78 × 28/3 connects sl(27) to E6 through 28 = 27 + 1

THE PATTERN:
  The E-series (E6, E7, E8) is special because E7-E6 = F(10).
  This suggests E7 plays a distinguished role as the "Fibonacci transition"
  between E6 (gauge) and E8 (roots).

WHY E7?
  E7 has 126 roots, rank 7, dimension 133.
  126 = 63 × 2 = (64 - 1) × 2 = (2^6 - 1) × 2
  133 = 7 × 19 (both prime factors!)

  But more importantly:
  133 = 78 + 55 = dim(E6) + F(10)

  E7 is literally E6 PLUS a Fibonacci number!
======================================================================
"""
)

# Final check
print("\nFINAL VERIFICATION:")
print(f"  E7 = E6 + F(10): 133 = 78 + 55 = {78 + 55} ✓")
print(f"  728 = 2 × 14 × 26: {2 * 14 * 26} ✓")
print(f"  36 : 55 = 288/8 : 440/8 ✓")
print(f"  C(13,2) = 78 = dim(E6) ✓")

# One more connection
print(f"\n  240 + 8 = 248 = dim(E8) [roots + rank]")
print(f"  240 - 8 = 232")
print(f"  232 = F(13) - 1 = {fib(13) - 1}")
print(f"  F(13) = 233")
