"""
THE 10-14 SPLIT: WHY LEECH IS 24-DIMENSIONAL
=============================================

We discovered: 4095 = C(10,2) x C(14,2) = T_9 x T_13

The sets that generate these binomial coefficients have sizes 10 and 14.
And 10 + 14 = 24 = dimension of Leech lattice!

Is this a coincidence, or does the Leech lattice somehow "know"
about this 10-14 split?
"""

import math
from fractions import Fraction

print("=" * 70)
print("THE 10-14 DECOMPOSITION OF 24")
print("=" * 70)


def C(n, k):
    return math.comb(n, k)


def T(n):
    return n * (n + 1) // 2


print("\nThe key equation:")
print(f"  4095 = 2^12 - 1")
print(f"       = C(10, 2) x C(14, 2)")
print(f"       = {C(10,2)} x {C(14,2)}")
print(f"       = T_9 x T_13")
print(f"       = {T(9)} x {T(13)}")

print(f"\n  10 + 14 = 24 = dim(Leech)")
print(f"  10 - 14 = -4")
print(f"  10 * 14 = 140")
print(f"  10 / 14 = {10/14:.6f} = 5/7")

print("\n" + "=" * 70)
print("THE NUMBERS 10 AND 14 IN CODING THEORY")
print("=" * 70)

print(
    """
Binary Golay code G_24:
  - 24 positions total
  - 12 information bits
  - 12 check bits

Could the 10-14 split represent something else?

Let's check: what is special about 10 and 14?
"""
)

print("Properties of 10:")
print(f"  10 = 2 x 5")
print(f"  10 = T_4 (4th triangular)")
print(f"  C(10, 2) = 45 = T_9")
print(f"  C(10, 5) = 252 (middle binomial)")

print("\nProperties of 14:")
print(f"  14 = 2 x 7")
print(f"  14 = 7 + 7")
print(f"  C(14, 2) = 91 = T_13 = 7 x 13")
print(f"  C(14, 7) = 3432 (middle binomial)")

print("\n" + "=" * 70)
print("COULD 10 AND 14 RELATE TO ROOT SYSTEMS?")
print("=" * 70)

# In string theory, 10 = spacetime dimension, 26-16 = 10
# 14 = ?

print(
    """
String theory dimensions:
  10 = superstring spacetime dimension
  26 = bosonic string spacetime dimension
  16 = compactification dimension (E_8 x E_8 or SO(32))

  26 - 16 = 10 ✓

So: 10 (visible) + 14 (?) = 24 (Leech)

What is 14?
  14 = 26 - 12 (bosonic minus Golay length?)
  14 = 2 x 7 (7 = first bridge prime)
  14 = 6 + 8 (E_6 rank + E_8 rank)
"""
)

print(f"\n  6 + 8 = 14")
print(f"  rank(E_6) + rank(E_8) = 6 + 8 = 14")
print(f"  rank(E_8) + rank(SU(3)) = 8 + 2 = 10")
print(f"  Sum: 14 + 10 = 24 = dim(Leech)")

print("\n" + "=" * 70)
print("THE E6-E8-SU(3) INTERPRETATION")
print("=" * 70)

print(
    """
If we decompose 24 as:
  24 = (rank(E_6) + rank(E_8)) + (rank(E_8) + rank(SU(3)))
     = (6 + 8) + (8 + 2)
     = 14 + 10

This suggests a two-factor structure where:
  - One factor involves E_6 x E_8 (14 = 6 + 8)
  - Other factor involves E_8 x SU(3) (10 = 8 + 2)

The E_8 appears in BOTH factors!
The E_8 is the bridge between the two factors!
"""
)

# Let's check what C(14,2) and C(10,2) count in terms of roots
print("Root pair counts:")
print(f"  E_6 has {78} generators, rank 6, {72} roots")
print(f"  E_8 has {248} generators, rank 8, {240} roots")
print(f"  SU(3) has {8} generators, rank 2, {6} roots")

print(f"\n  C(14, 2) = 91 = ?")
print(f"  72 + 19 = 91 (roots of E_6 plus 19)")
print(f"  78 + 13 = 91 (dim(E_6) plus 13!)")

print(f"\n  C(10, 2) = 45 = ?")
print(f"  45 = 3 x 15 = 3 x T_5")
print(f"  45 = 9 x 5")

print("\n" + "=" * 70)
print("DEEPER: 4095 AS INCIDENCE STRUCTURE")
print("=" * 70)

print(
    """
4095 = C(10,2) x C(14,2)

This is the SIZE of a bipartite incidence structure where:
  - One side has C(10,2) = 45 elements (pairs from a 10-set)
  - Other side has C(14,2) = 91 elements (pairs from a 14-set)
  - Full structure has 45 x 91 = 4095 incidences

A binary Golay codeword corresponds to an incidence!
Each of the 4095 non-trivial codewords picks out
one specific relationship between:
  - A pair from the "10-set"
  - A pair from the "14-set"
"""
)

print("\n" + "=" * 70)
print("THE LEECH LATTICE'S 10-14 STRUCTURE")
print("=" * 70)

# Leech lattice can be constructed from binary Golay
# Does the 10-14 split appear there?

print(
    """
The Leech lattice L_24 can be constructed from the binary Golay code.

If 4095 (non-trivial Golay codewords) = 45 x 91 = C(10,2) x C(14,2),
then the Leech might decompose as:

  L_24 = L_10 x L_14 (in some twisted sense)

Let's check: 196560 = |minimal vectors of Leech|

  196560 = 728 x 270 = 48 x 4095

We know 4095 = 45 x 91, so:
  196560 = 48 x 45 x 91
         = 2160 x 91
         = 48 x 45 x 91

What is 2160?
"""
)

print(f"  2160 = 48 x 45 = {48 * 45}")
print(f"  2160 = 16 x 135 = {16 * 135}")
print(f"  2160 = 24 x 90 = {24 * 90}")
print(f"  2160 = 27 x 80 = {27 * 80}")
print(f"  2160 = 45 x 48")

print(f"\n  45 = T_9 = C(10,2)")
print(f"  48 = 24 x 2 = 16 x 3 = 6 x 8")
print(f"  48 = rank(E_6) x rank(E_8) = {6 * 8}")

print("\n  OH! 48 = 6 x 8 = rank(E_6) x rank(E_8)")

print("\n" + "=" * 70)
print("THE GRAND FACTORIZATION")
print("=" * 70)

print(
    """
196560 = 48 x 45 x 91
       = (6 x 8) x T_9 x T_13
       = rank(E_6) x rank(E_8) x C(10,2) x C(14,2)

The Leech minimal vector count encodes:
  - The ranks of E_6 and E_8 (as their product 48)
  - The pair counts from 10-set and 14-set (as 45 x 91)
  - And 10 + 14 = 24 = dim(Leech)!
"""
)

print(f"\n  Let's verify: {6} x {8} x {45} x {91} = {6 * 8 * 45 * 91}")

print("\n" + "=" * 70)
print("CONNECTION TO EXCEPTIONAL JORDAN ALGEBRA")
print("=" * 70)

print(
    """
The Albert algebra (exceptional Jordan algebra) has dimension 27.

  27 = 3^3 = 3 x 9 = 3 x T_3 (sort of)

But also: 27 x 3 = 81 and 27 x 27 = 729 = |ternary Golay|

In E_8 branching: 248 = 78 + 8 + 2x(27x3)
  The 27 of E_6 appears with a triplet!

  91 = T_13 = 78 + 13 = dim(E_6) + 13

  The gap from T_13 to dim(E_6) is exactly 13, a bridge prime!
"""
)

print(f"\n  91 - 78 = {91 - 78} (bridge prime!)")
print(f"  T_13 - T_12 = {T(13) - T(12)} = {91 - 78} = 13")
print(f"\n  In general: T_n - T_(n-1) = n")
print(f"  So T_13 - T_12 = 13 is automatic.")
print(f"  But dim(E_6) = T_12 is the MAGIC!")

print("\n" + "=" * 70)
print("WHY DIM(E_6) = T_12?")
print("=" * 70)

print(
    """
The exceptional Lie algebra E_6 has dimension 78 = T_12.

E_6 has:
  - Rank 6
  - 72 root vectors
  - 6 Cartan generators
  - Total: 72 + 6 = 78

78 = C(13, 2) = "pairs from 13 objects"

E_6 is the "algebra of pairs from 13 things"!

But what are the 13 things?
  - 12 = ternary Golay code length
  - 13 = 12 + 1 = Golay length plus "infinity point"

E_6 might be the automorphisms of the projective
completion of the ternary Golay positions!
"""
)

print(f"\nThe exceptional series and triangular numbers:")
print(f"  dim(G_2) = 14 = 2 x 7 (not triangular, but 7 = F_5!)")
print(f"  dim(F_4) = 52 = 4 x 13")
print(f"  dim(E_6) = 78 = T_12")
print(f"  dim(E_7) = 133 = 7 x 19")
print(f"  dim(E_8) = 248 = 8 x 31")

# Check which are triangular
print(f"\nTriangular checks:")
for n in [14, 52, 78, 133, 248]:
    # Check if triangular
    discriminant = 1 + 8 * n
    sqrt_disc = int(math.sqrt(discriminant))
    if sqrt_disc * sqrt_disc == discriminant and (sqrt_disc - 1) % 2 == 0:
        k = (sqrt_disc - 1) // 2
        print(f"  {n} = T_{k}")
    else:
        print(f"  {n} is NOT triangular")

print("\n  Only E_6 is triangular! E_6 is SPECIAL.")

print("\n" + "=" * 70)
print("THE PROJECTIVE LINE INTERPRETATION")
print("=" * 70)

print(
    """
78 = C(13, 2) = pairs from 13 elements

The projective line PG(1, 12) over F_12 would have 13 points.
But F_12 doesn't exist (12 isn't a prime power).

However: The projective line PG(1, 11) over F_11 has 12 points.
(11 finite + 1 at infinity = 12)

And PG(1, 13) over F_13 has 14 points.

Hmm, but our structure wants exactly 13 points.
13 = prime, so F_13 exists.
PG(1, F_13) - {1 point} = 13 affine points?

Actually: 13 points means we're looking at the affine line over F_13!
The affine line A^1(F_13) has exactly 13 points.

E_6 counts "unordered pairs of points on A^1(F_13)"!
"""
)

print(f"\n  |A^1(F_13)| = 13")
print(f"  Pairs from A^1(F_13) = C(13, 2) = 78 = dim(E_6)")

print("\n" + "=" * 70)
print("THE 10-14 AS AFFINE LINES")
print("=" * 70)

print(
    """
If pairs-from-13 gives dim(E_6) = 78,
then:
  - C(10, 2) = 45 = pairs from A^1(F_9) + point?
    (F_9 has 9 elements, A^1 has 9 points, add 1 = 10)
  - C(14, 2) = 91 = pairs from A^1(F_13) + point?
    (F_13 has 13 elements, A^1 has 13 points, add 1 = 14)

But 9 and 13 are meaningful:
  9 = 3^2 (F_9 exists!)
  13 = prime (F_13 exists!)

So:
  10 = |A^1(F_9)| + 1 = projective completion
  14 = |A^1(F_13)| + 1 = projective completion

The 10-14 split might be:
  PG(1, F_9) x PG(1, F_13) structure
  (projective lines over F_9 and F_13)
"""
)

print(f"\n  |PG(1, F_9)| = 9 + 1 = 10")
print(f"  |PG(1, F_13)| = 13 + 1 = 14")
print(f"  Product of pair counts: C(10,2) x C(14,2) = 45 x 91 = 4095")

print("\n" + "=" * 70)
print("CONNECTION TO TERNARY GOLAY")
print("=" * 70)

print(
    """
The ternary Golay code exists over F_3.
It has:
  - 12 positions
  - 729 = 3^6 codewords

F_9 = F_{3^2} is a degree-2 extension of F_3.
F_13 is unrelated to F_3... OR IS IT?

3^3 = 27 (mod 13) = 1 (since 27 = 2*13 + 1)
So 3 has order dividing 3 in (Z/13Z)*.

Actually: 3^1 = 3, 3^2 = 9, 3^3 = 27 = 1 (mod 13)
So 3 has order EXACTLY 3 in the multiplicative group of F_13!

This means F_3 embeds into F_13 in a natural way (via the subgroup of order 3).
"""
)

print(f"\nOrder of 3 in (Z/13Z)*:")
for k in range(1, 13):
    if pow(3, k, 13) == 1:
        print(f"  3^{k} ≡ 1 (mod 13)")
        print(f"  Order of 3 in F_13* is {k}")
        break

print(
    """
So F_3 "embeds" into F_13 via: {0, 1, 3, 9} → {0, 1, 3, 9}
where 3 acts as a primitive cube root of unity (since 3^3 ≡ 1).

The ternary Golay code over F_3 has a hidden F_13 structure!
"""
)

print("\n" + "=" * 70)
print("ULTIMATE SYNTHESIS")
print("=" * 70)

print(
    """
4095 = 2^12 - 1 = C(10,2) x C(14,2)

Where:
  10 = |PG(1, F_9)| = projective line over F_{3^2}
  14 = |PG(1, F_13)| = projective line over F_13

And:
  - F_9 = F_{3^2} is an extension of F_3 (ternary Golay base)
  - F_13 has F_3* as a subgroup (3^3 ≡ 1 mod 13)

Both projective lines are connected to F_3!

The binary Mersenne 2^12 - 1 encodes the product of
two projective line structures, both related to the
ternary field F_3.

This explains the bridge between binary (2^12 - 1) and
ternary (3^6 - 1 = 728) structures!

BINARY ←→ TERNARY bridge lives in:
  PG(1, F_9) x PG(1, F_13)
  (both connected to F_3)
"""
)
