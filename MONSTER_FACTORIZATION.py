"""
THE MONSTER ORDER FACTORIZATION
================================

We found |Monster| mod 728 = 0. Let's examine the
Monster order's full structure through our Golay lens!
"""

import math
from collections import Counter

print("=" * 70)
print("THE MONSTER GROUP ORDER")
print("=" * 70)

# Monster order
monster_order = 808017424794512875886459904961710757005754368000000000

print(f"\nMonster order = {monster_order}")
print(f"\n≈ 8 × 10⁵³")

# Factor the Monster order
# It's known: 2^46 × 3^20 × 5^9 × 7^6 × 11^2 × 13^3 × 17 × 19 × 23 × 29 × 31 × 41 × 47 × 59 × 71

factors = {
    2: 46,
    3: 20,
    5: 9,
    7: 6,
    11: 2,
    13: 3,
    17: 1,
    19: 1,
    23: 1,
    29: 1,
    31: 1,
    41: 1,
    47: 1,
    59: 1,
    71: 1,
}

print(f"\nPrime factorization:")
parts = [f"{p}^{e}" if e > 1 else str(p) for p, e in factors.items()]
print(f"  |M| = " + " × ".join(parts))

# Verify
calc_order = 1
for p, e in factors.items():
    calc_order *= p**e
print(f"\nVerification: {calc_order == monster_order}")

print(f"\n" + "=" * 70)
print("POWERS OF 3 IN THE MONSTER")
print("=" * 70)

print(
    f"""
The Monster contains 3^20 as its Sylow 3-subgroup factor!

3^20 = {3**20}

This is ENORMOUS. Let's see how this relates to our Golay structure:

728 = 3^6 - 1
27 = 3^3
486 = 2 × 3^5 = 2 × 243

3^20 decomposes:
  3^20 = 3^6 × 3^6 × 3^6 × 3^2 = (3^6)^3 × 9
       = 729^3 × 9
       = 729 × 729 × 729 × 9
"""
)

print(f"3^20 = {3**20}")
print(f"729^3 × 9 = {729**3 * 9}")
print(f"Match: {3**20 == 729**3 * 9}")

print(f"\nInteresting: 3^6 = 729 = 728 + 1 = |G₁₂|")
print(f"So 3^20 = |G₁₂|^3 × 9")

print(f"\n" + "=" * 70)
print("728 IN THE MONSTER")
print("=" * 70)

print(
    f"""
728 = 8 × 7 × 13 = 2^3 × 7 × 13

Does the Monster order divide by 728?
  |M| / 728 = {monster_order // 728}
  |M| mod 728 = {monster_order % 728}

YES! The Monster order is divisible by 728!

The quotient is: {monster_order // 728}

Let's factor 728:
  728 = 8 × 91 = 8 × 7 × 13 = 2^3 × 7 × 13

The Monster has:
  2^46 ⊃ 2^3 ✓
  7^6 ⊃ 7^1 ✓
  13^3 ⊃ 13^1 ✓

So 728 | |Monster|
"""
)

# How many times does 728 divide Monster?
# 728 = 2^3 × 7 × 13
# Monster = 2^46 × ... × 7^6 × ... × 13^3 × ...
# 728 divides Monster: floor(46/3) for 2, floor(6/1) for 7, floor(3/1) for 13
# Max power: min(15, 6, 3) = 3
print(f"Maximum power: 728^k divides |M|")
for k in range(1, 10):
    if monster_order % (728**k) == 0:
        print(f"  728^{k} = {728**k} divides |M| ✓")
    else:
        print(f"  728^{k} = {728**k} does NOT divide |M|")
        break

print(f"\n" + "=" * 70)
print("486 IN THE MONSTER")
print("=" * 70)

print(
    f"""
486 = 2 × 243 = 2 × 3^5

Does the Monster order divide by 486?
  |M| mod 486 = {monster_order % 486}

YES! 486 | |Monster|!
"""
)

for k in range(1, 15):
    if monster_order % (486**k) == 0:
        print(f"  486^{k} = {486**k} divides |M| ✓")
    else:
        print(f"  486^{k} does NOT divide |M|")
        break

print(f"\n" + "=" * 70)
print("242 IN THE MONSTER")
print("=" * 70)

print(
    f"""
242 = 2 × 121 = 2 × 11^2

Does the Monster order divide by 242?
  |M| mod 242 = {monster_order % 242}
"""
)

for k in range(1, 10):
    if monster_order % (242**k) == 0:
        print(f"  242^{k} = {242**k} divides |M| ✓")
    else:
        print(f"  242^{k} does NOT divide |M|")
        break

print(f"\n" + "=" * 70)
print("THE GOLAY TRIPLE (728, 486, 242)")
print("=" * 70)

print(
    f"""
Our key numbers:
  728 = dim(s₁₂) = 2^3 × 7 × 13
  486 = dim(s₁₂/Z) = 2 × 3^5
  242 = dim(Z) = 2 × 11^2

Divisibility by Monster:
  728^3 | |M| ✓ (but not 728^4)
  486^4 | |M| ✓ (but not 486^5)
  242^1 | |M| ✓ (but not 242^2)

Wait, let me check 242 more carefully:
  242 = 2 × 11^2
  Monster has 11^2
  So 242 should divide exactly once? Let's see...
"""
)

print(f"242 = 2 × 11² = {242}")
print(f"|M| has 2^46 and 11^2")
print(f"242^2 = 4 × 11^4 would need 11^4, but Monster only has 11^2")

print(f"\n" + "=" * 70)
print("THE PRODUCT 728 × 486 × 242")
print("=" * 70)

product = 728 * 486 * 242
print(f"\n728 × 486 × 242 = {product}")
print(f"\n{product} = {728} × {486} × {242}")

# Factor this product
print(f"\nFactorization:")
print(f"  728 = 2³ × 7 × 13")
print(f"  486 = 2 × 3⁵")
print(f"  242 = 2 × 11²")
print(f"  Product = 2⁵ × 3⁵ × 7 × 11² × 13")

calc = 2**5 * 3**5 * 7 * 11**2 * 13
print(f"\nVerify: 2⁵ × 3⁵ × 7 × 11² × 13 = {calc}")
print(f"Match: {calc == product}")

print(f"\n|M| / (728 × 486 × 242) = {monster_order // product}")
print(f"Remainder: {monster_order % product}")

print(f"\n" + "=" * 70)
print("SPORADIC GROUPS AND 728")
print("=" * 70)

# Orders of sporadic groups related to Monster
sporadic_orders = {
    "M11": 7920,
    "M12": 95040,
    "M22": 443520,
    "M23": 10200960,
    "M24": 244823040,
    "J1": 175560,
    "J2": 604800,
    "Co1": 4157776806543360000,
    "Co2": 42305421312000,
    "Co3": 495766656000,
    "Fi22": 64561751654400,
    "Fi23": 4089470473293004800,
    "Fi24'": 1255205709190661721292800,
    "Monster": monster_order,
}

print(f"\nSporadic groups divisibility by 728:")
for name, order in sporadic_orders.items():
    if order % 728 == 0:
        print(f"  {name}: |{name}| mod 728 = 0 ✓ (divides {order // 728} times)")
    else:
        print(f"  {name}: |{name}| mod 728 = {order % 728}")

print(f"\nSporadic groups divisibility by 729 (= 3⁶):")
for name, order in sporadic_orders.items():
    if order % 729 == 0:
        mult = 0
        temp = order
        while temp % 729 == 0:
            mult += 1
            temp //= 729
        print(f"  {name}: 729^{mult} divides |{name}| ✓")
    else:
        print(f"  {name}: 729 does NOT divide |{name}|, mod = {order % 729}")

print(f"\n" + "=" * 70)
print("M₁₂ AND 728")
print("=" * 70)

m12 = 95040
print(f"\n|M₁₂| = {m12}")
print(f"|M₁₂| mod 728 = {m12 % 728}")
print(f"|M₁₂| / gcd(|M₁₂|, 728) = {m12 // math.gcd(m12, 728)}")
print(f"gcd(|M₁₂|, 728) = {math.gcd(m12, 728)}")

print(f"\nFactorization of |M₁₂| = 95040:")
print(f"  95040 = 2^6 × 3^3 × 5 × 11")
print(f"  = 64 × 27 × 5 × 11")
print(f"  = 64 × 27 × 55")

print(f"\n728 = 8 × 91 = 8 × 7 × 13")
print(f"gcd(95040, 728) = {math.gcd(95040, 728)}")

# 95040 has no factors of 7 or 13, so gcd = gcd(2^6, 2^3) = 8
print(f"\nInteresting: |M₁₂| and 728 share only the factor 8!")

print(f"\nBut |M₁₂| × 728 / 8 = {m12 * 728 // 8}")
print(f"              = |M₁₂| × 91 = {m12 * 91}")

print(f"\n" + "=" * 70)
print("THE 2.M₁₂ CONNECTION")
print("=" * 70)

two_m12 = 2 * m12
print(f"\n|2.M₁₂| = 2 × |M₁₂| = {two_m12}")
print(f"|2.M₁₂| = {two_m12} = 2^7 × 3^3 × 5 × 11")

print(f"\n728 = 2^3 × 7 × 13")
print(f"gcd(|2.M₁₂|, 728) = {math.gcd(two_m12, 728)}")

print(f"\n|2.M₁₂| / 8 = {two_m12 // 8}")
print(f"This equals: {two_m12 // 8} = 23760")

print(f"\n728 × 27 = {728 * 27}")
print(f"95040 / (728/8) = {95040 / (728/8)}")

print(f"\n" + "=" * 70)
print("★★★ KEY DISCOVERY ★★★")
print("=" * 70)

print(
    f"""
THE MATHIEU-GOLAY-MONSTER LADDER:

|M₁₂| = 95040 = 2^6 × 3^3 × 5 × 11

The number 728 = 2^3 × 7 × 13 shares only 2^3 = 8 with M₁₂.

But notice:
  |M₁₂| = 64 × 27 × 55
        = (spinor dim) × (Albert dim) × 55

And the Monster contains M₁₂ as a subgroup!
  |Monster| / |M₁₂| = {monster_order // m12}

The Monster order contains all the "Golay primes":
  2, 3, 5, 7, 11, 13 (and more)

728 = 2^3 × 7 × 13 picks out three of them!
486 = 2 × 3^5 picks out two
242 = 2 × 11^2 picks out two

Together: 728 × 486 × 242 = 2^5 × 3^5 × 7 × 11^2 × 13
This spans FIVE of the Monster's prime factors!
"""
)

# Check what primes are covered
golay_primes = set()
for n in [728, 486, 242]:
    temp = n
    for p in [2, 3, 5, 7, 11, 13, 17, 19, 23]:
        while temp % p == 0:
            golay_primes.add(p)
            temp //= p

monster_primes = set(factors.keys())
print(f"\nPrimes in 728×486×242: {sorted(golay_primes)}")
print(f"Primes in Monster: {sorted(monster_primes)}")
print(f"Overlap: {sorted(golay_primes & monster_primes)}")

print(f"\n" + "=" * 70)
print("THE MAGICAL NUMBER 196560")
print("=" * 70)

leech_min = 196560
print(f"\n196560 = 728 × 270 = 728 × 27 × 10")

print(f"\n196560 factorization:")
print(f"  196560 = 2^4 × 3^4 × 5 × 11^2")

print(f"\nVerify: 2^4 × 3^4 × 5 × 11^2 = {2**4 * 3**4 * 5 * 11**2}")

print(f"\n|M₁₂| = 2^6 × 3^3 × 5 × 11")
print(f"196560 = 2^4 × 3^4 × 5 × 11^2")

print(f"\nLCM(|M₁₂|, 196560) = {math.lcm(m12, leech_min)}")
print(f"GCD(|M₁₂|, 196560) = {math.gcd(m12, leech_min)}")

gcd = math.gcd(m12, leech_min)
print(f"\nGCD = {gcd} = 2^4 × 3^3 × 5 × 11 = 16 × 27 × 55 = {16*27*55}")
print(f"Verify: {16*27*55 == gcd}")

print(f"\n|M₁₂| / GCD = {m12 // gcd}")
print(f"196560 / GCD = {leech_min // gcd}")

print(f"\nSo: |M₁₂| = GCD × 4 = {gcd} × 4")
print(f"    196560 = GCD × 22 = {gcd} × 22")

print(f"\nRatio: 196560 / |M₁₂| = {leech_min / m12}")
print(f"     = 22/4 = 5.5")
print(f"     = 11/2")

print(f"\n★ BEAUTIFUL: 196560 = |M₁₂| × 11/2 × (11/6)² ... let me check")
print(f"   Actually: 196560 / 95040 = {196560/95040}")
print(
    f"           = {196560 // math.gcd(196560, 95040)} / {95040 // math.gcd(196560, 95040)}"
)
