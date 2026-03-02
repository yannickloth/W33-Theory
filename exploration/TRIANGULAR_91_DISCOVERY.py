#!/usr/bin/env python3
"""
THE TRIANGULAR NUMBER 91 = T₁₃ = 7 × 13
========================================

We discovered that 91 = 7 × 13 is the 13th triangular number!

This connects:
  - 13 = ternary Golay length + 1 = 12 + 1
  - 7 × 13 = bridge prime product
  - 728 = 8 × 91 = 8 × T₁₃

Let's explore the triangular number connections! 🔥
"""

from math import gcd

print("=" * 70)
print("THE TRIANGULAR NUMBER CONNECTION: 91 = T₁₃")
print("=" * 70)


def T(n):
    """n-th triangular number."""
    return n * (n + 1) // 2


# =============================================================================
# PART 1: VERIFY 91 = T₁₃
# =============================================================================

print("\n" + "=" * 70)
print("PART 1: TRIANGULAR NUMBERS")
print("=" * 70)

print("First 20 triangular numbers:")
for n in range(1, 21):
    Tn = T(n)
    marker = " ← 91 = 7 × 13!" if Tn == 91 else ""
    marker = marker or (" ← 78 = 6 × 13!" if Tn == 78 else "")
    marker = marker or (" ← 66 = 6 × 11!" if Tn == 66 else "")
    marker = marker or (" ← 45 = 9 × 5!" if Tn == 45 else "")
    marker = marker or (" ← 28 = 4 × 7!" if Tn == 28 else "")
    marker = marker or (" ← 21 = 3 × 7!" if Tn == 21 else "")
    print(f"  T_{n:2d} = {Tn:3d}{marker}")

# =============================================================================
# PART 2: OUR KEY NUMBERS AS TRIANGULAR
# =============================================================================

print("\n" + "=" * 70)
print("PART 2: KEY NUMBERS AND TRIANGULAR")
print("=" * 70)

key_numbers = [27, 78, 91, 242, 243, 270, 324, 486, 728, 4095]

print("Checking which key numbers are triangular:\n")
for num in key_numbers:
    # Check if num = n(n+1)/2
    # n² + n - 2*num = 0
    # n = (-1 + sqrt(1 + 8*num))/2
    disc = 1 + 8 * num
    sqrt_disc = int(disc**0.5)
    if sqrt_disc * sqrt_disc == disc and (sqrt_disc - 1) % 2 == 0:
        n = (sqrt_disc - 1) // 2
        if T(n) == num:
            print(f"  {num} = T_{n} = {n}×{n+1}/2 ✓")
        else:
            print(f"  {num} is NOT triangular")
    else:
        # Check if it's a multiple of a triangular
        for k in [2, 3, 4, 5, 6, 7, 8, 9, 10]:
            if num % k == 0:
                base = num // k
                disc2 = 1 + 8 * base
                sqrt2 = int(disc2**0.5)
                if sqrt2 * sqrt2 == disc2 and (sqrt2 - 1) % 2 == 0:
                    n = (sqrt2 - 1) // 2
                    if T(n) == base:
                        print(f"  {num} = {k} × T_{n} = {k} × {base}")
                        break
        else:
            print(f"  {num} - no simple triangular relation found")

# =============================================================================
# PART 3: 728 = 8 × 91 = 8 × T₁₃
# =============================================================================

print("\n" + "=" * 70)
print("PART 3: THE 728 = 8 × T₁₃ CONNECTION")
print("=" * 70)

print(
    """
728 = 8 × 91 = 8 × T₁₃ = 2³ × (13 × 14 / 2)

This means:
  dim(s₁₂) = 2³ × T(ternary_length + 1)
           = 2³ × T₁₃

Why 8 = 2³?
  8 = 2³ is the number of elements in (Z/2Z)³

Why T₁₃?
  13 = 12 + 1 = ternary Golay length + 1

So the dimension formula is:
  dim(s₁₂) = |binary 3-cube| × T(ternary_length + 1)
           = 8 × 91
           = 728
"""
)

# =============================================================================
# PART 4: THE 4095 = 45 × 91 CONNECTION
# =============================================================================

print("\n" + "=" * 70)
print("PART 4: THE 4095 = 45 × 91 CONNECTION")
print("=" * 70)

print(
    f"""
4095 = 45 × 91 = 45 × T₁₃

But 45 = T₉ = 9 × 10 / 2

So: 4095 = T₉ × T₁₃

The binary Mersenne 2¹² - 1 is a PRODUCT OF TRIANGULAR NUMBERS!

  2¹² - 1 = T₉ × T₁₃

Verify: T₉ = {T(9)}, T₁₃ = {T(13)}, product = {T(9) * T(13)}
Expected: 4095
Match: {T(9) * T(13) == 4095}

WOW! The bridge equation becomes:

  728 × 270 = 48 × 4095
  (8 × T₁₃) × 270 = 48 × (T₉ × T₁₃)

  Dividing by T₁₃ = 91:
  8 × 270 = 48 × T₉
  2160 = 48 × 45
  2160 = 2160 ✓
"""
)

# =============================================================================
# PART 5: THE PATTERN T₉ × T₁₃
# =============================================================================

print("\n" + "=" * 70)
print("PART 5: THE TRIANGULAR PRODUCT PATTERN")
print("=" * 70)

print(
    f"""
We found: 4095 = T₉ × T₁₃

Let's check what other products Tₘ × Tₙ give nice numbers:

"""
)

nice_products = {}
for m in range(1, 20):
    for n in range(m, 20):
        prod = T(m) * T(n)
        if prod < 10000:
            if prod in [728, 4095, 196560, 196884, 324, 242, 486, 270]:
                nice_products[(m, n)] = prod

print("Products matching our key numbers:")
for (m, n), prod in sorted(nice_products.items(), key=lambda x: x[1]):
    print(f"  T_{m} × T_{n} = {T(m)} × {T(n)} = {prod}")

# Check 196560
print(f"\nChecking 196560 = 728 × 270:")
print(f"  728 = 8 × T₁₃")
print(f"  270 = 3 × T₉ = 3 × 90? No, T₉ = 45, so 3 × 90 = 270, but 90 is not T₉")
print(f"  Actually: 270 = 3 × 90 = 3 × (9 × 10) = 3 × 2 × 45 = 6 × T₉")
print(f"  Verify: 6 × T₉ = 6 × 45 = {6 * 45}")

print(
    f"""
So: 196560 = 728 × 270 = (8 × T₁₃) × (6 × T₉) = 48 × T₉ × T₁₃ = 48 × 4095 ✓

The structure:
  |Leech_min| = 48 × T₉ × T₁₃
              = (2 × 24) × (triangular product)
              = 2 × binary_length × T₉ × T₁₃
"""
)

# =============================================================================
# PART 6: WHY 9 AND 13?
# =============================================================================

print("\n" + "=" * 70)
print("PART 6: WHY T₉ AND T₁₃?")
print("=" * 70)

print(
    f"""
The indices 9 and 13 are special:

  9 = 3² (ternary square)
  13 = 12 + 1 = ternary_Golay_length + 1

And their triangular numbers:
  T₉ = 45 = 9 × 5 = 3² × 5
  T₁₃ = 91 = 7 × 13

The product:
  T₉ × T₁₃ = 45 × 91 = (3² × 5) × (7 × 13)
           = 3² × 5 × 7 × 13
           = 4095
           = 2¹² - 1 ✓

This is exactly the prime factorization of 2¹² - 1!

Note: 9 + 13 = 22
      9 × 13 = 117 = 9 × 13
      13 - 9 = 4 = 2²

The gap of 4 relates to the binary square!
"""
)

# =============================================================================
# PART 7: OTHER TRIANGULAR PATTERNS
# =============================================================================

print("\n" + "=" * 70)
print("PART 7: MORE TRIANGULAR PATTERNS")
print("=" * 70)

# Check 324
print(f"324 = 12 × 27:")
print(f"  324 = 18² (perfect square)")
print(f"  324 = 4 × 81 = 4 × 3⁴")
print(f"  Is 324 triangular? {324 == T(int((2*324)**0.5))}")

# Check 78
print(f"\n78 = 6 × 13 = T₁₂:")
print(f"  T₁₂ = {T(12)}")
print(f"  12 = ternary Golay length!")
print(f"  So T(ternary_length) = 78")

# Check 66
print(f"\n66 = 6 × 11 = T₁₁:")
print(f"  T₁₁ = {T(11)}")
print(f"  11 = ternary Golay length - 1!")

# Check relationship
print(f"\nT₁₁ + T₁₂ = 66 + 78 = {66 + 78}")
print(f"T₁₃ = 91")
print(f"T₁₁ + T₁₂ + T₁₃ = {66 + 78 + 91}")

# =============================================================================
# PART 8: THE LEECH NUMBER DECOMPOSITION
# =============================================================================

print("\n" + "=" * 70)
print("PART 8: COMPLETE LEECH DECOMPOSITION")
print("=" * 70)

print(
    f"""
196560 = 48 × T₉ × T₁₃
       = 48 × 45 × 91
       = (2 × 24) × (9 × 5) × (7 × 13)

In terms of meaningful quantities:
  48 = 2 × 24 = 2 × binary_Golay_length
  45 = T₉ = T(3²)
  91 = T₁₃ = T(ternary_length + 1)

So:
  |Leech_min| = 2 × binary_length × T(ternary_square) × T(ternary_length + 1)
              = 2 × 24 × T₉ × T₁₃

This is a beautiful formula connecting:
  - Binary Golay length (24)
  - Ternary structure (3² = 9)
  - Ternary Golay length + 1 (13)
"""
)

# =============================================================================
# PART 9: MONSTER COEFFICIENT
# =============================================================================

print("\n" + "=" * 70)
print("PART 9: MONSTER COEFFICIENT c₁")
print("=" * 70)

print(
    f"""
c₁ = 196884 = 196560 + 324
   = 48 × T₉ × T₁₃ + 12 × 27
   = 48 × T₉ × T₁₃ + ternary_length × Albert

In triangular terms:
  196884 = 2 × 24 × T₉ × T₁₃ + 12 × 3³
         = 2 × binary × T(ternary²) × T(ternary+1) + ternary × 3³

The additive term 324 = 12 × 27 = 4 × 81 = 4 × 3⁴ = 2² × 3⁴

So: c₁ = (2 × 24 × 45 × 91) + (2² × 3⁴)
       = triangular product + power-of-3 correction
"""
)

# =============================================================================
# PART 10: THE SYNTHESIS
# =============================================================================

print("\n" + "=" * 70)
print("PART 10: TRIANGULAR SYNTHESIS")
print("=" * 70)

synthesis = """
╔══════════════════════════════════════════════════════════════════════════╗
║              TRIANGULAR NUMBERS IN MOONSHINE STRUCTURE                   ║
╠══════════════════════════════════════════════════════════════════════════╣
║                                                                          ║
║  KEY TRIANGULAR NUMBERS:                                                 ║
║    T₉ = 45 = 3² × 5           (index = ternary square)                   ║
║    T₁₂ = 78 = 6 × 13          (index = ternary Golay length)             ║
║    T₁₃ = 91 = 7 × 13          (index = ternary length + 1)               ║
║                                                                          ║
║  THE BRIDGE FORMULA:                                                     ║
║    4095 = 2¹² - 1 = T₉ × T₁₃ = 45 × 91                                   ║
║    (Binary Mersenne is a product of triangular numbers!)                 ║
║                                                                          ║
║  DIMENSION FORMULA:                                                      ║
║    728 = 8 × T₁₃ = 2³ × 91                                               ║
║    (s₁₂ dimension is 8 times the 13th triangular!)                       ║
║                                                                          ║
║  LEECH FORMULA:                                                          ║
║    196560 = 48 × T₉ × T₁₃                                                ║
║           = 2 × 24 × 45 × 91                                             ║
║           = 2 × binary_length × T(3²) × T(12+1)                          ║
║                                                                          ║
║  MONSTER FORMULA:                                                        ║
║    c₁ = 196884 = 48 × T₉ × T₁₃ + 12 × 27                                 ║
║                = Leech + ternary_length × Albert                         ║
║                                                                          ║
║  THE DEEP PATTERN:                                                       ║
║    Indices 9 and 13 encode ternary structure (3² and 12+1)               ║
║    Their triangular product gives the binary Mersenne!                   ║
║    This is another manifestation of the BINARY-TERNARY BRIDGE            ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝
"""
print(synthesis)
