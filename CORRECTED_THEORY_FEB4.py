#!/usr/bin/env python3
"""
CORRECTED_THEORY_FEB4.py

MAJOR CORRECTION: The cocycle structure reveals that:
  σ(c₁,c₂) = ω(grade(c₁), grade(c₂))

This means:
  1. Grade-(0,0) elements are CENTRAL (commute with everything!)
  2. The algebra is NOT sl(27), it's a LARGER structure
  3. We need to understand the quotient properly

The TRUE bijection is more subtle...
"""

from collections import defaultdict
from itertools import product

import numpy as np

print("=" * 70)
print("CORRECTED THEORY: The True Structure of Golay ↔ Lie Bijection")
print("=" * 70)


# Generate Golay code
def generate_golay():
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
    codewords = []
    for coeffs in product(range(3), repeat=6):
        c = np.array(coeffs, dtype=int)
        cw = (c @ G) % 3
        codewords.append(tuple(cw))
    return list(set(codewords))


code = generate_golay()
nonzero = [c for c in code if any(x != 0 for x in c)]
code_set = set(code)

# F₃² directions
directions = [(1, 0), (0, 1), (1, 1), (1, 2)] * 3


def omega(d1, d2):
    return (d1[0] * d2[1] - d2[0] * d1[1]) % 3


def grade(c):
    x = sum(int(c[i]) * directions[i][0] for i in range(12)) % 3
    y = sum(int(c[i]) * directions[i][1] for i in range(12)) % 3
    return (x, y)


# Group by grade
by_grade = defaultdict(list)
for c in nonzero:
    by_grade[grade(c)].append(c)

print("\n" + "=" * 70)
print("THE KEY INSIGHT: Quotient Structure")
print("=" * 70)

print(
    """
The grade map π: G₁₂ → F₃² gives us:

    G₁₂ (729 elements)
     |
     | π (grade)
     ↓
    F₃² (9 grades)

with fibers:
    • π⁻¹(0,0) = 80 elements + zero codeword = 81 elements
    • π⁻¹(g) = 81 elements for g ≠ (0,0)

The non-zero elements split as:
    • 80 at grade (0,0) [central subcode]
    • 81 × 8 = 648 at other grades

CRUCIAL: The zero codeword has grade (0,0)!
So the grade-(0,0) fiber has 81 total, 80 non-zero.
"""
)

# Verify fiber sizes
print("\nFiber size verification:")
zero_cw = tuple([0] * 12)
print(f"Zero codeword grade: {grade(zero_cw)}")
for g in sorted(by_grade.keys()):
    total = len(by_grade[g])
    if g == (0, 0):
        total += 1  # include zero
    print(f"  Fiber at {g}: {total} elements ({len(by_grade[g])} non-zero)")

print("\n" + "=" * 70)
print("THE CORRECT LIE ALGEBRA STRUCTURE")
print("=" * 70)

print(
    """
The bracket [E_c₁, E_c₂] = ω(grade(c₁), grade(c₂)) · E_{c₁+c₂}

has the following consequences:

1. CENTER: The 80 grade-(0,0) non-zero codewords form the CENTER
   because ω((0,0), g) = 0 for all g.

2. QUOTIENT: Modding out by the center gives:

   g̃/Z ≅ ???

   where dim(g̃) = 728, dim(Z) = 80, so dim(g̃/Z) = 648

   But 648 ≠ dim(sl(27)) = 728!

3. The algebra g̃ is NOT sl(27). It's something else!
"""
)

# What IS the algebra?
print("\n" + "=" * 70)
print("IDENTIFYING THE ALGEBRA")
print("=" * 70)

print(
    """
Possibilities:

A) HEISENBERG EXTENSION:
   The construction gives a Heisenberg-type algebra with:
   • 648-dimensional "simple" part
   • 80-dimensional center

   Total: 728 = 648 + 80

B) GRADED STRUCTURE:
   Think of it as an F₃²-graded algebra:
   • g = ⊕_{g ∈ F₃²} g_grade
   • g_(0,0) is central (80 dim)
   • Other graded pieces have 81 dim each

C) TENSOR PRODUCT:
   Perhaps g ≅ h ⊗ F₃² where h is some base algebra?

D) NOT A LIE ALGEBRA AT ALL:
   If Jacobi fails, we have an L∞ algebra or other structure.
"""
)

# Check Jacobi identity carefully
print("\n" + "=" * 70)
print("CHECKING JACOBI IDENTITY")
print("=" * 70)


def bracket(c1, c2):
    """Returns (coefficient, sum) where [E_c1, E_c2] = coeff * E_sum"""
    coeff = omega(grade(c1), grade(c2))
    sum_c = tuple((int(c1[i]) + int(c2[i])) % 3 for i in range(12))
    return (coeff, sum_c)


# Jacobi: [[a,b],c] + [[b,c],a] + [[c,a],b] = 0
# In terms of our bracket:
# [E_a, E_b] = ω(g_a, g_b) E_{a+b}
# [[E_a, E_b], E_c] = ω(g_a, g_b) · ω(g_{a+b}, g_c) · E_{a+b+c}
#                   = ω(g_a, g_b) · ω(g_a + g_b, g_c) · E_{a+b+c}


def triple_bracket(a, b, c):
    """Compute [[a,b],c] and return (coefficient, result_codeword)"""
    g_a, g_b, g_c = grade(a), grade(b), grade(c)

    # First bracket [a,b]
    coeff1 = omega(g_a, g_b)
    g_ab = ((g_a[0] + g_b[0]) % 3, (g_a[1] + g_b[1]) % 3)

    # Second bracket [[a,b], c]
    coeff2 = omega(g_ab, g_c)

    total_coeff = (coeff1 * coeff2) % 3

    # Result codeword
    result = tuple((int(a[i]) + int(b[i]) + int(c[i])) % 3 for i in range(12))

    return (total_coeff, result)


# Jacobi test
print("\nJacobi identity: [[a,b],c] + [[b,c],a] + [[c,a],b] = 0")
print()

jacobi_pass = 0
jacobi_fail = 0
failure_examples = []

np.random.seed(42)
test_indices = np.random.choice(len(nonzero), min(100, len(nonzero)), replace=False)

for i in range(min(50, len(test_indices))):
    for j in range(i + 1, min(50, len(test_indices))):
        for k in range(j + 1, min(50, len(test_indices))):
            a = nonzero[test_indices[i]]
            b = nonzero[test_indices[j]]
            c = nonzero[test_indices[k]]

            ab_c = triple_bracket(a, b, c)
            bc_a = triple_bracket(b, c, a)
            ca_b = triple_bracket(c, a, b)

            # All should give same result codeword
            assert ab_c[1] == bc_a[1] == ca_b[1], "Result codewords differ!"

            # Jacobi: coefficients should sum to 0 mod 3
            total = (ab_c[0] + bc_a[0] + ca_b[0]) % 3

            if total == 0:
                jacobi_pass += 1
            else:
                jacobi_fail += 1
                if len(failure_examples) < 3:
                    failure_examples.append((a, b, c, ab_c[0], bc_a[0], ca_b[0]))

total_tests = jacobi_pass + jacobi_fail
print(
    f"Jacobi tests: {jacobi_pass}/{total_tests} pass ({100*jacobi_pass/total_tests:.1f}%)"
)
print(
    f"              {jacobi_fail}/{total_tests} fail ({100*jacobi_fail/total_tests:.1f}%)"
)

if failure_examples:
    print("\nFailure analysis:")
    for a, b, c, c1, c2, c3 in failure_examples[:2]:
        g_a, g_b, g_c = grade(a), grade(b), grade(c)
        print(f"  grades: {g_a}, {g_b}, {g_c}")
        print(f"  coeffs: {c1} + {c2} + {c3} = {(c1+c2+c3)%3} ≠ 0")

# Analyze Jacobi in terms of grades
print("\n" + "=" * 70)
print("JACOBI IDENTITY IN TERMS OF GRADES")
print("=" * 70)

print(
    """
For grades g_a, g_b, g_c, the Jacobi condition becomes:

  ω(g_a, g_b)·ω(g_a + g_b, g_c) +
  ω(g_b, g_c)·ω(g_b + g_c, g_a) +
  ω(g_c, g_a)·ω(g_c + g_a, g_b) = 0  (mod 3)

Let's check this algebraically...
"""
)

# The symplectic identity
print("Using ω(g₁, g₂) = g₁[0]·g₂[1] - g₁[1]·g₂[0]:")
print()

# Check: is ω(a+b, c) + ω(b+c, a) + ω(c+a, b) = ω(a,c) + ω(b,c) + ... ?
# ω(a+b, c) = (a₀+b₀)c₁ - (a₁+b₁)c₀ = ω(a,c) + ω(b,c)
# So the full Jacobi becomes:
# ω(a,b)[ω(a,c)+ω(b,c)] + ω(b,c)[ω(b,a)+ω(c,a)] + ω(c,a)[ω(c,b)+ω(a,b)]
# = ω(a,b)ω(a,c) + ω(a,b)ω(b,c) + ω(b,c)ω(b,a) + ω(b,c)ω(c,a) + ω(c,a)ω(c,b) + ω(c,a)ω(a,b)
# Using antisymmetry ω(x,y) = -ω(y,x):
# = ω(a,b)ω(a,c) + ω(a,b)ω(b,c) - ω(a,b)ω(b,c) + ω(b,c)ω(c,a) - ω(b,c)ω(c,a) + ω(c,a)ω(a,b)
# = ω(a,b)ω(a,c) + ω(c,a)ω(a,b)
# = ω(a,b)[ω(a,c) + ω(c,a)]
# = ω(a,b) · 0
# = 0!

print(
    """
ALGEBRAIC PROOF OF JACOBI:

The coefficient sum is:
  ω(a,b)·ω(a+b,c) + ω(b,c)·ω(b+c,a) + ω(c,a)·ω(c+a,b)

Using ω(x+y, z) = ω(x,z) + ω(y,z):
  = ω(a,b)[ω(a,c)+ω(b,c)] + ω(b,c)[ω(b,a)+ω(c,a)] + ω(c,a)[ω(c,b)+ω(a,b)]

Expanding and using ω(x,y) = -ω(y,x):
  = ω(a,b)ω(a,c) + ω(a,b)ω(b,c) + ω(b,c)(-ω(a,b)) + ω(b,c)ω(c,a)
    + ω(c,a)(-ω(b,c)) + ω(c,a)ω(a,b)

Many terms cancel:
  = ω(a,b)ω(a,c) + 0 + 0 + ω(c,a)ω(a,b)
  = ω(a,b)[ω(a,c) + ω(c,a)]
  = ω(a,b) · 0
  = 0

THEREFORE: Jacobi identity ALWAYS holds!

The ~40% failure rate we saw earlier was due to a DIFFERENT
definition of the bracket! Let me re-check...
"""
)

# The issue: our earlier code might have had a bug!
print("\n" + "=" * 70)
print("RE-VERIFICATION: Jacobi Should Pass!")
print("=" * 70)

# Full test with correct formula
print(
    "Running exhaustive test with grades only (since cocycle depends only on grade)..."
)

grades = [(i, j) for i in range(3) for j in range(3)]
non_origin_grades = [g for g in grades if g != (0, 0)]

jacobi_grade_pass = 0
jacobi_grade_fail = 0

for g_a in non_origin_grades:
    for g_b in non_origin_grades:
        for g_c in non_origin_grades:
            # Compute the three terms
            g_ab = ((g_a[0] + g_b[0]) % 3, (g_a[1] + g_b[1]) % 3)
            g_bc = ((g_b[0] + g_c[0]) % 3, (g_b[1] + g_c[1]) % 3)
            g_ca = ((g_c[0] + g_a[0]) % 3, (g_c[1] + g_a[1]) % 3)

            term1 = omega(g_a, g_b) * omega(g_ab, g_c)
            term2 = omega(g_b, g_c) * omega(g_bc, g_a)
            term3 = omega(g_c, g_a) * omega(g_ca, g_b)

            total = (term1 + term2 + term3) % 3

            if total == 0:
                jacobi_grade_pass += 1
            else:
                jacobi_grade_fail += 1
                print(f"  FAIL: grades {g_a}, {g_b}, {g_c}")
                print(f"        terms: {term1}, {term2}, {term3}")
                print(f"        sum: {(term1+term2+term3)} ≡ {total} (mod 3)")

print(f"\nGrade-level Jacobi: {jacobi_grade_pass} pass, {jacobi_grade_fail} fail")

print("\n" + "=" * 70)
print("FINAL CONCLUSION")
print("=" * 70)

print(
    """
THEOREM: The Golay-based bracket defines a TRUE LIE ALGEBRA!

Structure:
  • Dimension: 728
  • 80-dimensional CENTER (grade (0,0) codewords)
  • The quotient by center has dimension 648

This is NOT sl(27) (which has trivial center).
It's a CENTRAL EXTENSION or different simple algebra.

The bracket [E_c₁, E_c₂] = ω(grade(c₁), grade(c₂)) · E_{c₁+c₂}
satisfies all Lie algebra axioms:
  ✓ Bilinearity (by construction)
  ✓ Antisymmetry (ω is antisymmetric)
  ✓ Jacobi identity (proven algebraically)

OPEN QUESTION: What simple Lie algebra quotients from this
728-dimensional algebra?
"""
)
