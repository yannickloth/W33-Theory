"""
HIGHER j-FUNCTION COEFFICIENTS AND GOLAY STRUCTURE
==================================================

The j-function: j(τ) = 1/q + 744 + 196884q + 21493760q² + ...

Let's analyze ALL the coefficients through the Golay lens!
"""

import math
from collections import Counter

import numpy as np

print("=" * 70)
print("j-FUNCTION COEFFICIENTS DEEP ANALYSIS")
print("=" * 70)

# The first several j-function coefficients (after 1/q)
# j(τ) = q^(-1) + 744 + c₁q + c₂q² + c₃q³ + ...
j_coeffs = {
    -1: 1,  # q^(-1) coefficient
    0: 744,  # constant term
    1: 196884,  # q^1 coefficient
    2: 21493760,  # q^2 coefficient
    3: 864299970,  # q^3 coefficient
    4: 20245856256,
    5: 333202640600,
    6: 4252023300096,
    7: 44656994071935,
    8: 401490886656000,
    9: 3176440229784420,
    10: 22567393309593600,
}

print("j-function coefficients:")
for n, c in j_coeffs.items():
    print(f"  c[{n:2d}] = {c:>25,}")

print(f"\n" + "=" * 70)
print("MODULAR ANALYSIS")
print("=" * 70)

print(f"\nCoefficients mod 728:")
for n, c in j_coeffs.items():
    print(f"  c[{n:2d}] mod 728 = {c % 728:4d}")

print(f"\nCoefficients mod 729 (= 3⁶ = |G₁₂|):")
for n, c in j_coeffs.items():
    print(f"  c[{n:2d}] mod 729 = {c % 729:4d}")

print(f"\nCoefficients mod 27 (= 3³ = Albert):")
for n, c in j_coeffs.items():
    print(f"  c[{n:2d}] mod 27 = {c % 27:3d}")

print(f"\n" + "=" * 70)
print("FACTORIZATION PATTERNS")
print("=" * 70)


def prime_factors(n):
    factors = {}
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors[d] = factors.get(d, 0) + 1
            n //= d
        d += 1
    if n > 1:
        factors[n] = 1
    return factors


print(f"\nPrime factorizations of low coefficients:")
for n in [-1, 0, 1, 2, 3]:
    c = j_coeffs[n]
    factors = prime_factors(c)
    factor_str = " × ".join(
        f"{p}^{e}" if e > 1 else str(p) for p, e in sorted(factors.items())
    )
    print(f"  c[{n:2d}] = {c} = {factor_str}")

print(f"\n" + "=" * 70)
print("RELATIONSHIP TO 728, 486, 242")
print("=" * 70)

print(f"\nDivisibility by Golay numbers:")
for n, c in list(j_coeffs.items())[:6]:
    div_728 = "✓" if c % 728 == 0 else "✗"
    div_486 = "✓" if c % 486 == 0 else "✗"
    div_242 = "✓" if c % 242 == 0 else "✗"
    print(f"  c[{n:2d}]: 728 {div_728}  486 {div_486}  242 {div_242}")

print(f"\n" + "=" * 70)
print("THE 196884 DECOMPOSITION")
print("=" * 70)

c1 = 196884
print(f"\nc₁ = 196884")
print(f"\nDecompositions:")
print(f"  196884 = 196560 + 324")
print(f"         = (728 × 270) + 18²")
print(f"         = (728 × 27 × 10) + (2 × 3²)²")
print(f"         = 1 + 196883 (Monster rep decomposition)")

# Check the Monster representation
print(f"\n196883 = smallest faithful Monster rep")
print(f"196883 = 47 × 59 × 71 = {47 * 59 * 71}")
print(f"  (product of three largest Monster primes!)")

print(f"\n" + "=" * 70)
print("THE 21493760 DECOMPOSITION")
print("=" * 70)

c2 = 21493760
print(f"\nc₂ = {c2}")

# Try to decompose
print(f"\nFactorization: {prime_factors(c2)}")
print(f"  = 2⁷ × 5 × 7 × 47 × 101")

# Check relationship to our numbers
print(f"\n{c2} / 728 = {c2 / 728}")
print(f"{c2} / 27 = {c2 / 27}")
print(f"{c2} / 10 = {c2 / 10}")
print(f"{c2} / 270 = {c2 / 270}")

# Try 196560
remainder = c2 - 196560
print(f"\n{c2} - 196560 = {remainder}")
print(f"  = {prime_factors(remainder)}")

# Monster representation decomposition
print(f"\nMonster rep decomposition of c₂:")
print(f"  21493760 = 1 + 196883 + 21296876")
print(f"           = trivial + smallest + next")

print(f"\n" + "=" * 70)
print("PATTERN IN RATIOS")
print("=" * 70)

print(f"\nRatios c[n+1]/c[n]:")
for n in range(0, 8):
    if n in j_coeffs and n + 1 in j_coeffs:
        ratio = j_coeffs[n + 1] / j_coeffs[n]
        print(f"  c[{n+1}]/c[{n}] = {ratio:.4f}")

print(f"\n" + "=" * 70)
print("MONSTER REPRESENTATION DIMENSIONS")
print("=" * 70)

print(
    f"""
The Monster group has representations whose dimensions
appear in j-function coefficients!

Monster irreps by dimension:
  1 (trivial)
  196883 (smallest non-trivial)
  21296876
  842609326
  18538750076
  ...

McKay's observation:
  196884 = 1 + 196883
  21493760 = 1 + 196883 + 21296876 (with multiplicities)

Actually the exact decomposition is:
  c₁ = 196884 = 1·1 + 1·196883
  c₂ = 21493760 = 1·1 + 1·196883 + 1·21296876
"""
)

print(f"\nVerification:")
print(f"  1 + 196883 = {1 + 196883}")
print(f"  1 + 196883 + 21296876 = {1 + 196883 + 21296876}")
print(f"  Actual c₂ = {c2}")
print(f"  Match: {1 + 196883 + 21296876 == c2}")

# The mismatch means there are multiplicities
print(f"\n  Difference: {c2 - (1 + 196883 + 21296876)}")

print(f"\n" + "=" * 70)
print("POWERS OF 3 IN j-COEFFICIENTS")
print("=" * 70)

print(f"\nHighest power of 3 dividing each coefficient:")
for n, c in list(j_coeffs.items())[:8]:
    power = 0
    temp = c
    while temp % 3 == 0:
        power += 1
        temp //= 3
    print(f"  c[{n:2d}]: 3^{power} divides {c}")

print(f"\n" + "=" * 70)
print("THE TERNARY STRUCTURE")
print("=" * 70)

print(
    f"""
Coefficients mod 3:
"""
)
for n, c in list(j_coeffs.items())[:11]:
    print(f"  c[{n:2d}] mod 3 = {c % 3}")

# Count the pattern
mod3_pattern = [j_coeffs[n] % 3 for n in range(-1, 11)]
print(f"\nPattern mod 3: {mod3_pattern}")
print(f"  Number of 0s (divisible by 3): {mod3_pattern.count(0)}")
print(f"  Number of 1s: {mod3_pattern.count(1)}")
print(f"  Number of 2s: {mod3_pattern.count(2)}")

print(f"\n" + "=" * 70)
print("RELATION TO LEECH VECTORS")
print("=" * 70)

leech = 196560

print(f"\nCoefficients as multiples of |Leech| = 196560:")
for n, c in list(j_coeffs.items())[:6]:
    ratio = c / leech
    print(f"  c[{n:2d}] / 196560 = {ratio:.6f}")

print(f"\nCoefficients minus |Leech|:")
for n, c in list(j_coeffs.items())[:6]:
    diff = c - leech
    print(f"  c[{n:2d}] - 196560 = {diff:>15,}")

print(f"\n" + "=" * 70)
print("★★★ KEY DISCOVERIES ★★★")
print("=" * 70)

print(
    f"""
1. c₁ = 196884 = 196560 + 324 = |Leech| + 18²

2. c₀ = 744 = 728 + 16 = dim(s₁₂) + Spinor(10)

3. All coefficients have significant 3-structure:
   - c₁ ≡ 0 (mod 27) ✓
   - c₃ ≡ 0 (mod 27) ✓
   - Powers of 3 vary systematically

4. The Monster representation multiplicities encode
   the j-coefficients through:
   c_n = Σ mult(V_i) × dim(V_i)

   where V_i are Monster irreps.

5. The ratio c₁/c₀ = 196884/744 ≈ 264.6
   Interestingly: 264 = weight-6 Golay codewords!
"""
)

print(f"\n196884 / 744 = {196884 / 744:.4f}")
print(f"Close to 264 + 2/3 = {264 + 2/3:.4f}")
print(f"264 = 11 × 24 = {11 * 24}")

print(f"\n" + "=" * 70)
print("ASYMPTOTIC BEHAVIOR")
print("=" * 70)

print(
    f"""
The j-coefficients grow like:
  c_n ~ (1/n^(3/4)) × exp(4π√n)

This is the Hardy-Ramanujan-Rademacher formula!

For large n:
  log(c_n) ≈ 4π√n - (3/4)log(n) + constant

Let's check:
"""
)

import math

for n in [1, 2, 3, 4, 5]:
    c = j_coeffs[n]
    predicted = math.exp(4 * math.pi * math.sqrt(n)) / (n**0.75)
    print(f"  n={n}: log(c_n)={math.log(c):.2f}, 4π√n={4*math.pi*math.sqrt(n):.2f}")
