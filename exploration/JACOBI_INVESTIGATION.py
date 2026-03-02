"""
CRITICAL: Investigating Jacobi Identity
=======================================
The previous test showed 500/500 violations - we need to understand why.
This is critical for determining if we have a true Lie algebra.
"""

from collections import Counter
from itertools import product

import numpy as np


# Rebuild code
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
    return sum(c) % 3


def add_cw(c1, c2):
    return tuple((c1[i] + c2[i]) % 3 for i in range(12))


nonzero = [c for c in codewords if c != zero_cw]
grade1 = [c for c in nonzero if grade(c) == 1]
grade2 = [c for c in nonzero if grade(c) == 2]

print("=" * 70)
print("JACOBI IDENTITY INVESTIGATION")
print("=" * 70)


# Define omega carefully
def omega(g1, g2):
    """The bracket coefficient omega(grade1, grade2)"""
    # omega is defined such that [E_m, E_n] = omega(gr(m), gr(n)) * E_{m+n}
    # From our earlier analysis:
    # omega(1,1) = 1, omega(1,2) = 2, omega(2,1) = 1, omega(2,2) = 2
    # omega(0,*) = omega(*,0) = 0
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


# Verify antisymmetry: [x,y] = -[y,x]
print("\n1. ANTISYMMETRY CHECK")
print("-" * 40)
print("For Lie algebra: [x,y] = -[y,x]")
print("In F_3: -1 = 2, so [y,x] should equal 2*[x,y]")

# [E_a, E_b] = omega(g_a, g_b) * E_{a+b}
# [E_b, E_a] = omega(g_b, g_a) * E_{b+a} = omega(g_b, g_a) * E_{a+b}
# For antisymmetry: omega(g_a, g_b) = -omega(g_b, g_a) = 2*omega(g_b, g_a) mod 3

print("\nChecking omega antisymmetry:")
for g1 in [1, 2]:
    for g2 in [1, 2]:
        w1 = omega(g1, g2)
        w2 = omega(g2, g1)
        neg_w2 = (3 - w2) % 3  # This is -w2 in F_3
        print(
            f"  omega({g1},{g2}) = {w1}, omega({g2},{g1}) = {w2}, -omega({g2},{g1}) = {neg_w2}"
        )
        if w1 != neg_w2:
            print(f"    -> ANTISYMMETRY VIOLATED! {w1} != {neg_w2}")

print("\nCRITICAL: omega(1,2)=2 but omega(2,1)=1")
print("For antisymmetry we need omega(1,2) = -omega(2,1) = -1 = 2 mod 3")
print("So omega(2,1) should be 1... which it is!")
print("Let's double-check: 2 = -(1) = 3-1 = 2. Hmm, -1 = 2 mod 3.")
print("So we need omega(2,1) = -omega(1,2) = -2 = 1 mod 3. YES!")

print("\nActually the antisymmetry IS satisfied:")
print("  omega(1,1) = 1, need -omega(1,1) = -1 = 2. ")
print("  But [E_a, E_a] should be 0 for antisymmetry!")

print("\n2. CHECKING [x,x] = 0")
print("-" * 40)

# For a Lie algebra, [x,x] = 0 for all x
# [E_a, E_a] = omega(g_a, g_a) * E_{2a}
# This should be 0

print("Testing [E_a, E_a]:")
c = grade1[0]  # A grade-1 element
g = grade(c)
coeff = omega(g, g)
result = add_cw(c, c)
print(f"  Element c has grade {g}")
print(f"  [c, c] = omega({g},{g}) * E_{{c+c}} = {coeff} * E_{result}")
print(f"  Result grade: {grade(result)}")

if coeff != 0 and result != zero_cw:
    print("  -> [x,x] != 0 for non-zero elements!")
    print("  This means our algebra is NOT a Lie algebra in the classical sense!")

print("\n3. THE ISSUE: omega(g,g) != 0")
print("-" * 40)
print("omega(1,1) = 1 != 0")
print("omega(2,2) = 2 != 0")
print("\nThis means [E_a, E_a] != 0 when grade(a) != 0")
print("VIOLATES the axiom [x,x] = 0 of Lie algebras!")

print("\n4. WHAT KIND OF ALGEBRA IS THIS?")
print("-" * 40)
print(
    """
Since [x,x] != 0, this is NOT a Lie algebra!

In characteristic 2, [x,x] = 0 is replaced by [x,x] = 0 is automatic from antisymmetry.
In characteristic 3, things are different.

This could be a:
1. Lie superalgebra
2. Color Lie algebra
3. Hom-Lie algebra
4. Some other generalized structure

Let's check what we actually have...
"""
)

# Check if it's a color Lie algebra
print("\n5. COLOR LIE ALGEBRA CHECK")
print("-" * 40)
print(
    """
A color Lie algebra has:
  [x,y] = -epsilon(|x|,|y|) [y,x]

where epsilon is a bicharacter on the grading group.

Our bracket: [E_a, E_b] = omega(g_a, g_b) * E_{a+b}

For color antisymmetry: omega(g1, g2) = -epsilon(g1, g2) * omega(g2, g1)
"""
)

# Compute what epsilon would need to be
print("Computing implied epsilon values:")
for g1 in [1, 2]:
    for g2 in [1, 2]:
        w12 = omega(g1, g2)
        w21 = omega(g2, g1)
        if w21 != 0:
            # w12 = -epsilon * w21 => epsilon = -w12/w21 mod 3
            # In F_3: 1/1=1, 1/2=2, 2/1=2, 2/2=1
            inv_w21 = pow(w21, -1, 3)  # Modular inverse
            epsilon = ((-w12 % 3) * inv_w21) % 3
            print(f"  epsilon({g1},{g2}) implied by antisymmetry: {epsilon}")

print("\n6. LET'S RE-EXAMINE THE ORIGINAL DEFINITION")
print("-" * 40)
print(
    """
Going back to the definition:
  [E_m, E_n] = omega(grade(m), grade(n)) * E_{m+n}

For this to be a Lie algebra, we need:
1. Antisymmetry: [x,y] = -[y,x]
2. [x,x] = 0
3. Jacobi identity

Let's check if omega was supposed to be ANTISYMMETRIC...
"""
)

# What if omega should be antisymmetric?
print("If omega is antisymmetric: omega(a,b) = -omega(b,a)")
print(
    "Then omega(a,a) = -omega(a,a) => 2*omega(a,a) = 0 => omega(a,a) = 0 in char != 2"
)

print("\nBut our omega(1,1) = 1 != 0")
print("This suggests the original definition might need adjustment.")

print("\n7. ALTERNATIVE: ANTISYMMETRIC OMEGA")
print("-" * 40)


def omega_antisym(g1, g2):
    """Antisymmetric version of omega"""
    if g1 == 0 or g2 == 0:
        return 0
    if g1 == g2:
        return 0  # Forced by antisymmetry
    if g1 == 1 and g2 == 2:
        return 1
    if g1 == 2 and g2 == 1:
        return 2  # = -1 mod 3
    return 0


print("Antisymmetric omega:")
for g1 in range(3):
    for g2 in range(3):
        print(f"  omega_anti({g1},{g2}) = {omega_antisym(g1, g2)}")

print("\nWith antisymmetric omega:")
print("  [g_1, g_1] = 0 (coefficient 0)")
print("  [g_2, g_2] = 0 (coefficient 0)")
print("  [g_1, g_2] = 1 * E_{m+n} -> grade 0 (center)")
print("  [g_2, g_1] = 2 * E_{m+n} = -1 * E_{m+n} -> grade 0 (center)")

print("\nBut then [g_1, g_1] = 0 means grade-1 elements don't bracket to grade-2!")
print("The algebra structure becomes very different...")

print("\n8. PERHAPS A DIFFERENT INTERPRETATION")
print("-" * 40)
print(
    """
Looking at the original papers more carefully:

The bracket might be defined with a NORMALIZATION:
  [E_m, E_n] = omega(m,n) * E_{m+n}   if m != n
  [E_m, E_m] = 0

Or there might be a sign/symmetry factor we're missing.

Let's check if with [E_a, E_a] = 0 imposed, Jacobi holds...
"""
)


def bracket_with_diagonal_zero(c1, c2):
    """Bracket with [x,x] = 0 enforced"""
    if c1 == c2:
        return zero_cw, 0
    g1, g2 = grade(c1), grade(c2)
    coeff = omega(g1, g2)
    if coeff == 0:
        return zero_cw, 0
    return add_cw(c1, c2), coeff


print("\n9. TESTING JACOBI WITH CORRECTED BRACKET")
print("-" * 40)


def test_jacobi_corrected():
    violations = 0
    checks = 0

    np.random.seed(42)
    for _ in range(200):
        # Pick three distinct elements
        indices = np.random.choice(len(grade1), 3, replace=False)
        x, y, z = (
            grade1[indices[0]],
            grade1[indices[1]],
            grade2[np.random.randint(len(grade2))],
        )

        # Term 1: [x, [y,z]]
        yz, c_yz = bracket_with_diagonal_zero(y, z)
        if c_yz != 0 and yz != zero_cw:
            x_yz, c_x_yz = bracket_with_diagonal_zero(x, yz)
            coeff1 = (c_yz * c_x_yz) % 3
            term1 = x_yz if coeff1 != 0 else zero_cw
        else:
            term1, coeff1 = zero_cw, 0

        # Term 2: [y, [z,x]]
        zx, c_zx = bracket_with_diagonal_zero(z, x)
        if c_zx != 0 and zx != zero_cw:
            y_zx, c_y_zx = bracket_with_diagonal_zero(y, zx)
            coeff2 = (c_zx * c_y_zx) % 3
            term2 = y_zx if coeff2 != 0 else zero_cw
        else:
            term2, coeff2 = zero_cw, 0

        # Term 3: [z, [x,y]]
        xy, c_xy = bracket_with_diagonal_zero(x, y)
        if c_xy != 0 and xy != zero_cw:
            z_xy, c_z_xy = bracket_with_diagonal_zero(z, xy)
            coeff3 = (c_xy * c_z_xy) % 3
            term3 = z_xy if coeff3 != 0 else zero_cw
        else:
            term3, coeff3 = zero_cw, 0

        # The Jacobi identity needs coefficient tracking too
        # [x,[y,z]] + [y,[z,x]] + [z,[x,y]] = 0
        # means coeff1*term1 + coeff2*term2 + coeff3*term3 = 0

        # For simplicity, check if all land in same place with total coeff 0
        checks += 1

        # All three should land in same graded piece for Jacobi to be meaningful
        if term1 != zero_cw or term2 != zero_cw or term3 != zero_cw:
            sum_cw = add_cw(
                add_cw(
                    tuple((coeff1 * term1[i]) % 3 for i in range(12)),
                    tuple((coeff2 * term2[i]) % 3 for i in range(12)),
                ),
                tuple((coeff3 * term3[i]) % 3 for i in range(12)),
            )

            if sum_cw != zero_cw:
                violations += 1

    return checks, violations


checks, violations = test_jacobi_corrected()
print(f"Jacobi checks: {checks}")
print(f"Violations: {violations}")

if violations == 0:
    print("-> JACOBI SATISFIED with corrected bracket!")
else:
    print(f"-> Still {violations} violations")

print("\n" + "=" * 70)
print("CONCLUSION")
print("=" * 70)
print(
    """
The original bracket definition with omega(g,g) != 0 violates [x,x] = 0.

Options:
1. Modify to [E_a, E_a] = 0 explicitly (standard Lie algebra)
2. Accept non-zero [x,x] (generalized/Hom-Lie algebra)
3. The algebra is a Lie algebra on the QUOTIENT by identifying E_a with -E_{-a}

The key insight is that the Golay code structure naturally gives:
  g = span{E_c : c in G_12, c != 0}

And the quotient algebra s_12 = g/Z is the interesting object.
"""
)
