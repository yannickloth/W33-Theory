"""
INVESTIGATING THE g1 × g2 FAILURES
==================================

The tests show:
- g1 × g1: super-antisymmetry PASSES (symmetric)
- g2 × g2: super-antisymmetry PASSES (symmetric)
- g1 × g2: super-antisymmetry FAILS (200 failures)

This suggests g1 × g2 has a different structure!
Let's investigate carefully.
"""

from collections import Counter
from itertools import product

import numpy as np


def build_golay():
    G = np.array(
        [
            [1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1],
            [0, 1, 0, 0, 0, 0, 1, 0, 1, 2, 2, 1],
            [0, 0, 1, 0, 0, 0, 1, 1, 0, 1, 2, 2],
            [0, 0, 0, 1, 0, 0, 1, 2, 1, 0, 1, 2],
            [0, 0, 0, 0, 1, 0, 1, 2, 2, 1, 0, 1],
            [0, 0, 0, 0, 0, 1, 1, 1, 2, 2, 1, 0],
        ],
        dtype=np.int64,
    )

    codewords = set()
    for coeffs in product(range(3), repeat=6):
        c = np.array(coeffs, dtype=np.int64)
        cw = tuple((c @ G) % 3)
        codewords.add(cw)
    return list(codewords)


codewords = build_golay()
cw_set = set(codewords)
zero_cw = tuple([0] * 12)


def grade(c):
    return int(sum(c)) % 3


def add_cw(c1, c2):
    return tuple((c1[i] + c2[i]) % 3 for i in range(12))


nonzero = [c for c in codewords if c != zero_cw]
grade0 = [c for c in nonzero if grade(c) == 0]
grade1 = [c for c in nonzero if grade(c) == 1]
grade2 = [c for c in nonzero if grade(c) == 2]


def omega(g1, g2):
    g1, g2 = int(g1), int(g2)
    if g1 == 0 or g2 == 0:
        return 0
    if g1 == 1 and g2 == 1:
        return 1
    if g1 == 1 and g2 == 2:
        return 2
    if g1 == 2 and g2 == 1:
        return 1
    if g1 == 2 and g2 == 2:
        return 2
    return 0


def bracket(c1, c2):
    g1, g2 = grade(c1), grade(c2)
    coeff = omega(g1, g2)
    if coeff == 0:
        return zero_cw, 0
    result = add_cw(c1, c2)
    if result not in cw_set:
        return zero_cw, 0
    return result, coeff


print("=" * 70)
print("DETAILED INVESTIGATION OF [g1, g2]")
print("=" * 70)

print("\n1. THE BRACKET COEFFICIENTS")
print("-" * 50)

print("For [E_a, E_b] where grade(a)=1, grade(b)=2:")
print("  omega(1, 2) = 2")
print("  omega(2, 1) = 1")
print("\nSo [E_a, E_b] = 2 * E_{a+b}")
print("   [E_b, E_a] = 1 * E_{a+b}")
print("\nRatio: [E_a, E_b] / [E_b, E_a] = 2/1 = 2 = -1 in F_3")
print("This means: [E_a, E_b] = -[E_b, E_a] (ANTISYMMETRIC!)")

print("\n2. VERIFYING ANTISYMMETRY FOR g1 × g2")
print("-" * 50)

np.random.seed(42)
antisym_pass = 0
antisym_fail = 0

for _ in range(500):
    c1 = grade1[np.random.randint(len(grade1))]
    c2 = grade2[np.random.randint(len(grade2))]

    xy, c_xy = bracket(c1, c2)
    yx, c_yx = bracket(c2, c1)

    if xy == zero_cw and yx == zero_cw:
        continue

    # Both should give the same codeword
    if xy != yx:
        print(f"  Different targets: {xy[:4]}... vs {yx[:4]}...")
        continue

    # For antisymmetry: c_xy = -c_yx = (3 - c_yx) % 3
    expected = (3 - c_yx) % 3
    if c_xy == expected:
        antisym_pass += 1
    else:
        antisym_fail += 1
        if antisym_fail <= 3:
            print(f"  Fail: c_xy={c_xy}, c_yx={c_yx}, expected={expected}")

print(f"\nResults: Pass={antisym_pass}, Fail={antisym_fail}")

if antisym_pass > 0 and antisym_fail == 0:
    print("CONCLUSION: [g1, g2] IS ANTISYMMETRIC!")

print("\n3. THE FULL PICTURE")
print("-" * 50)
print(
    """
CORRECTED ANTISYMMETRY STRUCTURE:

For ordinary Lie algebra: [x,y] = -[y,x]
For Lie superalgebra: [x,y] = -(-1)^{|x||y|} [y,x]

With |g_0| = 0 (even), |g_1| = |g_2| = 1 (odd):

[g_0, g_i]:  [x,y] = -(-1)^{0·1}[y,x] = -[y,x]     (antisymmetric)
[g_1, g_1]:  [x,y] = -(-1)^{1·1}[y,x] = +[y,x]     (symmetric)
[g_2, g_2]:  [x,y] = -(-1)^{1·1}[y,x] = +[y,x]     (symmetric)
[g_1, g_2]:  [x,y] = -(-1)^{1·1}[y,x] = +[y,x]     (symmetric??)

BUT empirically:
  omega(1,2) = 2, omega(2,1) = 1
  2 = -1 mod 3
  So [g1,g2] is ANTISYMMETRIC!
"""
)

print("\n4. REINTERPRETING THE GRADING")
print("-" * 50)
print(
    """
The issue: g1 and g2 are BOTH odd, so [g1,g2] should be symmetric
           BUT empirically it's antisymmetric!

This means the algebra is NOT a standard Z_2-graded Lie superalgebra.

Instead, it's a Z_3-graded algebra with specific bracket rules:
  - omega(a,b) = omega(b,a) for a=b (symmetric on same grade)
  - omega(1,2) = 2 = -omega(2,1) (antisymmetric across grades!)

This is consistent with grade(a) + grade(b) determining the structure:
  - grade 1 + grade 1 = grade 2: same output, symmetric
  - grade 2 + grade 2 = grade 1: same output, symmetric
  - grade 1 + grade 2 = grade 0: output to center, antisymmetric
"""
)

print("\n5. CHECKING THE JACOBI WITH CORRECT UNDERSTANDING")
print("-" * 50)

# For the standard Jacobi: [x,[y,z]] + [y,[z,x]] + [z,[x,y]] = 0
# Let's check this for g1 × g1 × g2 with careful coefficient tracking


def detailed_jacobi(x, y, z):
    """Compute each Jacobi term with full details"""
    gx, gy, gz = grade(x), grade(y), grade(z)

    # Term 1: [x, [y,z]]
    yz, c_yz = bracket(y, z)
    g_yz = grade(yz) if yz != zero_cw else 0
    if c_yz != 0 and yz != zero_cw:
        x_yz, c_x_yz = bracket(x, yz)
        coeff1 = (c_yz * c_x_yz) % 3
    else:
        x_yz, coeff1 = zero_cw, 0

    # Term 2: [y, [z,x]]
    zx, c_zx = bracket(z, x)
    g_zx = grade(zx) if zx != zero_cw else 0
    if c_zx != 0 and zx != zero_cw:
        y_zx, c_y_zx = bracket(y, zx)
        coeff2 = (c_zx * c_y_zx) % 3
    else:
        y_zx, coeff2 = zero_cw, 0

    # Term 3: [z, [x,y]]
    xy, c_xy = bracket(x, y)
    g_xy = grade(xy) if xy != zero_cw else 0
    if c_xy != 0 and xy != zero_cw:
        z_xy, c_z_xy = bracket(z, xy)
        coeff3 = (c_xy * c_z_xy) % 3
    else:
        z_xy, coeff3 = zero_cw, 0

    return (x_yz, coeff1), (y_zx, coeff2), (z_xy, coeff3)


# Detailed check for g1 × g1 × g2
print("Testing g1 × g1 × g2:")
print("Grade flow:")
print("  [g1, g1] -> g2")
print("  [g2, g1] -> g0")
print("  [g1, g2] -> g0")
print("\nSo for x,y in g1, z in g2:")
print("  [x, [y,z]]: [g1, g0] = 0")
print("  [y, [z,x]]: [g1, g0] = 0")
print("  [z, [x,y]]: [g2, g2] -> g1 ≠ 0!")
print("\nJacobi reduces to: [z, [x,y]] = 0")
print("But [z, [x,y]] ≠ 0 in general!")

# Let's verify
failures = 0
for _ in range(100):
    x = grade1[np.random.randint(len(grade1))]
    y = grade1[np.random.randint(len(grade1))]
    z = grade2[np.random.randint(len(grade2))]

    if x == y:
        continue

    terms = detailed_jacobi(x, y, z)
    total = {}
    for cw, c in terms:
        if c != 0 and cw != zero_cw:
            total[cw] = (total.get(cw, 0) + c) % 3
    total = {k: v for k, v in total.items() if v != 0}

    if total:
        failures += 1

print(f"\nJacobi failures for g1×g1×g2: {failures}/100")

print("\n6. THE COLOR LIE ALGEBRA JACOBI")
print("-" * 50)
print(
    """
For a COLOR Lie algebra with bicharacter epsilon:

  [x,[y,z]] + epsilon(|x|,|y|+|z|)[y,[z,x]] + epsilon(|x|+|y|,|z|)[z,[x,y]] = 0

Let's define epsilon properly and check.
"""
)


# Define epsilon that matches our omega
def epsilon(a, b):
    """
    epsilon(a,b) such that omega(a,b) = -epsilon(a,b) * omega(b,a)

    We have:
    omega(1,1)=1, omega(1,1)=1: need eps(1,1)*1 = -1 = 2 => eps(1,1)=2
    omega(1,2)=2, omega(2,1)=1: need eps(1,2)*1 = -2 = 1 => eps(1,2)=1
    omega(2,1)=1, omega(1,2)=2: need eps(2,1)*2 = -1 = 2 => eps(2,1)=1
    omega(2,2)=2, omega(2,2)=2: need eps(2,2)*2 = -2 = 1 => eps(2,2)=2
    """
    a, b = int(a) % 3, int(b) % 3
    if a == 0 or b == 0:
        return 1
    if a == 1 and b == 1:
        return 2
    if a == 1 and b == 2:
        return 1
    if a == 2 and b == 1:
        return 1
    if a == 2 and b == 2:
        return 2
    return 1


print("Epsilon table:")
for a in range(3):
    row = f"  {a}: "
    for b in range(3):
        row += f"{epsilon(a,b)} "
    print(row)


def color_jacobi(x, y, z):
    """Color Jacobi with epsilon factors"""
    gx, gy, gz = grade(x), grade(y), grade(z)

    # eps1 = 1 (coefficient for [x,[y,z]])
    # eps2 = epsilon(gx, (gy+gz)%3)
    # eps3 = epsilon((gx+gy)%3, gz)

    eps1 = 1
    eps2 = epsilon(gx, (gy + gz) % 3)
    eps3 = epsilon((gx + gy) % 3, gz)

    # Term 1: eps1 * [x, [y,z]]
    yz, c_yz = bracket(y, z)
    if c_yz != 0 and yz != zero_cw:
        x_yz, c_x_yz = bracket(x, yz)
        coeff1 = (eps1 * c_yz * c_x_yz) % 3
    else:
        x_yz, coeff1 = zero_cw, 0

    # Term 2: eps2 * [y, [z,x]]
    zx, c_zx = bracket(z, x)
    if c_zx != 0 and zx != zero_cw:
        y_zx, c_y_zx = bracket(y, zx)
        coeff2 = (eps2 * c_zx * c_y_zx) % 3
    else:
        y_zx, coeff2 = zero_cw, 0

    # Term 3: eps3 * [z, [x,y]]
    xy, c_xy = bracket(x, y)
    if c_xy != 0 and xy != zero_cw:
        z_xy, c_z_xy = bracket(z, xy)
        coeff3 = (eps3 * c_xy * c_z_xy) % 3
    else:
        z_xy, coeff3 = zero_cw, 0

    total = {}
    for cw, c in [(x_yz, coeff1), (y_zx, coeff2), (z_xy, coeff3)]:
        if c != 0 and cw != zero_cw:
            total[cw] = (total.get(cw, 0) + c) % 3
    total = {k: v for k, v in total.items() if v != 0}

    return len(total) == 0


print("\nColor Jacobi tests:")
for name, s1, s2, s3 in [
    ("g1×g1×g1", grade1, grade1, grade1),
    ("g2×g2×g2", grade2, grade2, grade2),
    ("g1×g1×g2", grade1, grade1, grade2),
    ("g1×g2×g2", grade1, grade2, grade2),
]:
    passes = 0
    for _ in range(300):
        x = s1[np.random.randint(len(s1))]
        y = s2[np.random.randint(len(s2))]
        z = s3[np.random.randint(len(s3))]
        if x == y or y == z or x == z:
            continue
        if color_jacobi(x, y, z):
            passes += 1
    print(f"  {name}: {passes}/~300 pass")

print("\n" + "=" * 70)
print("FINAL STRUCTURE")
print("=" * 70)
print(
    """
THE GOLAY ALGEBRA is a Z_3-GRADED COLOR LIE ALGEBRA with:

Bracket: [E_m, E_n] = omega(g_m, g_n) * E_{m+n}

Omega table:
    | 0  1  2
  --+--------
  0 | 0  0  0
  1 | 0  1  2
  2 | 0  1  2

Antisymmetry rule: [x,y] = -epsilon(|x|,|y|) [y,x]

Epsilon (sign factor):
    | 0  1  2
  --+--------
  0 | 1  1  1
  1 | 1  2  1   (2 = -1)
  2 | 1  1  2

Key properties:
- [g1, g1] symmetric (eps=2=-1, so [x,y]=-(-1)[y,x]=+[y,x])
- [g2, g2] symmetric
- [g1, g2] antisymmetric (eps=1, so [x,y]=-[y,x])
- [g0, *] = 0 (center)

Dimensions:
- Total: 728 = 27² - 1
- Center (g0): 242
- Quotient: 486 = 243 + 243

The COLOR JACOBI IDENTITY should hold with these epsilon factors.
"""
)
