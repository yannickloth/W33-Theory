"""
DEEP NUMEROLOGY: 6720, 480, AND NEW PATTERNS
============================================
Exploring G2 × Octonion_reps and other combinations
"""

print("=" * 70)
print("6720 = 14 × 480 = G2 × OCTONION_REPRESENTATIONS")
print("=" * 70)

print(
    f"""
We know:
  G2 has dimension 14
  There are 480 octonion multiplications

Their product:
  14 × 480 = 6720
"""
)


# Factorization of 6720
def prime_factors(n):
    factors = []
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors.append(d)
            n //= d
        d += 1
    if n > 1:
        factors.append(n)
    return factors


print(f"\n6720 = {' × '.join(map(str, prime_factors(6720)))}")
print(f"6720 = 2^6 × 3 × 5 × 7 = {2**6 * 3 * 5 * 7}")

print("\n" + "-" * 50)
print("Relationships with key numbers:")
print("-" * 50)

tests = [
    ("6720 / 728", 6720 / 728),
    ("6720 / 744", 6720 / 744),
    ("6720 / 248", 6720 / 248),
    ("6720 / 240", 6720 / 240),
    ("6720 / 14", 6720 / 14),
    ("6720 / 52", 6720 / 52),
    ("6720 / 27", 6720 / 27),
    ("6720 / 8", 6720 / 8),
    ("6720 / 7!", 6720 / 5040),
    ("6720 / 8!", 6720 / 40320),
    ("6720 + 728", 6720 + 728),
    ("6720 - 728", 6720 - 728),
]

for expr, result in tests:
    if result == int(result):
        print(f"  {expr:20s} = {int(result):>10}")
    else:
        print(f"  {expr:20s} = {result:>10.4f}")

print("\n" + "=" * 70)
print("6720 = 28 × 240")
print("=" * 70)

print(
    f"""
Key factorization:
  6720 = 28 × 240

where:
  28 = dim(SO(8)) = D4 adjoint (triality!)
  240 = E8 roots

So: G2 × Octonion_reps = SO(8) × E8_roots!

This connects triality (SO(8)) with E8!
"""
)

print(f"28 × 240 = {28 * 240}")

print("\n" + "=" * 70)
print("840 = 6720 / 8")
print("=" * 70)

print(
    f"""
6720 / 8 = 840

840 = 2³ × 3 × 5 × 7 = {2**3 * 3 * 5 * 7}
840 = 7! / 6 = 5040 / 6 = {5040 // 6}

Also:
  840 = 12 × 70
  840 = 14 × 60
  840 = 28 × 30
  840 = 35 × 24
  840 = 42 × 20

Note: 840 = LCM(3,4,5,6,7,8) = smallest number divisible by 3-8
"""
)

import math

lcm = 1
for i in range(3, 9):
    lcm = lcm * i // math.gcd(lcm, i)
print(f"LCM(3,4,5,6,7,8) = {lcm}")

print("\n" + "=" * 70)
print("EXPLORING 5992 = 6720 - 728")
print("=" * 70)

print(
    f"""
6720 - 728 = 5992

Factorization:
  5992 = {' × '.join(map(str, prime_factors(5992)))}
  5992 = 8 × 749
  5992 = 8 × 7 × 107

Hmm, 107 is prime. Let's check:
  5992 / 8 = {5992 / 8}
  5992 / 728 = {5992 / 728}

Ratio: 5992/728 ≈ 8.23
"""
)

print("\n" + "=" * 70)
print("7448 = 6720 + 728")
print("=" * 70)

print(
    f"""
6720 + 728 = 7448

Factorization:
  7448 = {' × '.join(map(str, prime_factors(7448)))}
  7448 = 8 × 931
  7448 = 8 × 7² × 19

Note: 7² = 49 appears (7 is octonion imaginary units!)
  19 is prime

7448 / 728 = {7448 / 728}
7448 / 744 = {7448 / 744}
"""
)

print("\n" + "=" * 70)
print("THE 8 × 840 STRUCTURE")
print("=" * 70)

print(
    f"""
6720 = 8 × 840

The "8" connects to:
  - Octonion dimension
  - Triality (8v, 8s, 8c)
  - E8 name (8-dim diagram)

840 factorizations:
  840 = 7!/(6) = {5040//6}
  840 = 4 × 210 = 4 × C(10,4) [binomial]
  840 = 3 × 280
  840 = 5 × 168 [168 = |PSL(2,7)|!]

PSL(2,7) has order 168!
This is the automorphism group of the Fano plane!
"""
)

print(f"5 × 168 = {5 * 168}")
print(f"|PSL(2,7)| = 168")

print("\n" + "=" * 70)
print("168 AND THE FANO PLANE")
print("=" * 70)

print(
    f"""
168 = |PSL(2,7)| = |SL(3,2)|

The Fano plane (projective plane over F2):
  - 7 points
  - 7 lines
  - Each line has 3 points
  - Each point is on 3 lines

Fano plane encodes octonion multiplication!

168 connections:
  168 × 4 = {168 * 4} = 672 (close to 728)
  168 × 5 = {168 * 5} = 840
  168 × 6 = {168 * 6} (= 1008)

728 - 168 = {728 - 168}
728 = 168 × 4 + 56
    = 168 × 4 + 7 × 8
    = 4 × 168 + 7 × 8
"""
)

print(f"\n728 = 4 × 168 + 56 = {4 * 168 + 56}")

print("\n" + "=" * 70)
print("480 AND 168 CONNECTION")
print("=" * 70)

print(
    f"""
480 / 168 = {480 / 168}

Hmm, not clean. But:

480 = 168 × 2 + 144
    = 2 × 168 + 12²

480 = 168 + 168 + 144
    = 2 × PSL(2,7) + 12²

Or:
480 - 168 = {480 - 168} = 312 = 8 × 39 = 8 × 3 × 13
480 + 168 = {480 + 168} = 648 = 8 × 81 = 8 × 3⁴

648 is interesting:
  648 = 8 × 81 = 8 × 3⁴
  648 = 3⁴ × 8 = (Golay ternary)⁴ × octonion
"""
)

print(f"480 - 168 = {480 - 168}")
print(f"480 + 168 = {480 + 168}")
print(f"648 = 8 × 81 = {8 * 81}")

print("\n" + "=" * 70)
print("SEARCHING FOR 728 IN 6720")
print("=" * 70)

print(
    f"""
6720 = 728 × 9 + 168

Verification: 728 × 9 + 168 = {728 * 9 + 168}

This is beautiful!
  6720 = 728 × 9 + 168
       = 9 × s₁₂ + PSL(2,7)
       = 3² × (Golay) + (Fano automorphisms)

The ternary structure (3²) and Fano plane appear together!
"""
)

print(f"728 × 9 + 168 = {728 * 9 + 168}")

print("\n" + "=" * 70)
print("MASTER RELATIONS")
print("=" * 70)

print(
    f"""
DISCOVERED RELATIONS:

1. 728 = 480 + 248
   (Octonion reps + E8)

2. 728 = 14 × 52
   (G2 × F4)

3. 480 = 52 × 9 + 12
   (F4 × 3² + Golay_length)

4. 6720 = 14 × 480 = G2 × Octonion_reps

5. 6720 = 28 × 240 = SO(8) × E8_roots

6. 6720 = 8 × 840 = Octonion × (5 × PSL(2,7))

7. 6720 = 728 × 9 + 168
   (9 × Golay + Fano_auts)

8. 840 = 5 × 168 = 5 × |PSL(2,7)|
"""
)

print("\n" + "=" * 70)
print("VERIFICATION")
print("=" * 70)

checks = [
    ("728 = 480 + 248", 728, 480 + 248),
    ("728 = 14 × 52", 728, 14 * 52),
    ("480 = 52 × 9 + 12", 480, 52 * 9 + 12),
    ("6720 = 14 × 480", 6720, 14 * 480),
    ("6720 = 28 × 240", 6720, 28 * 240),
    ("6720 = 8 × 840", 6720, 8 * 840),
    ("6720 = 728 × 9 + 168", 6720, 728 * 9 + 168),
    ("840 = 5 × 168", 840, 5 * 168),
    ("728 = 4 × 168 + 56", 728, 4 * 168 + 56),
]

for expr, expected, computed in checks:
    status = "✓" if expected == computed else "✗"
    print(f"  {status} {expr}")
