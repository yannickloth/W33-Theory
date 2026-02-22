#!/usr/bin/env python3
"""
DEEP_EXPLORATION_FEB4.py

Now that we understand the basic structure, let's explore:
1. Is g/Z simple?
2. What IS the 648-dimensional quotient?
3. Can we find E6 (78-dim) inside?
4. Connection to Albert algebra
5. How does M11 act?
"""

from collections import defaultdict
from itertools import combinations, product

import numpy as np

print("=" * 75)
print("   DEEP EXPLORATION: Advanced Questions about the Golay Lie Algebra")
print("=" * 75)

# ============================================================
# BUILD THE CODE AND GRADING
# ============================================================


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

directions = [(1, 0), (0, 1), (1, 1), (1, 2)] * 3


def omega(d1, d2):
    return (d1[0] * d2[1] - d2[0] * d1[1]) % 3


def grade(c):
    x = sum(int(c[i]) * directions[i][0] for i in range(12)) % 3
    y = sum(int(c[i]) * directions[i][1] for i in range(12)) % 3
    return (x, y)


def add_cw(c1, c2):
    return tuple((c1[i] + c2[i]) % 3 for i in range(12))


def neg_cw(c):
    return tuple((-x) % 3 for x in c)


def bracket_coeff(c1, c2):
    return omega(grade(c1), grade(c2))


by_grade = defaultdict(list)
for c in nonzero:
    by_grade[grade(c)].append(c)

center = by_grade[(0, 0)]
non_center = [c for c in nonzero if grade(c) != (0, 0)]

print(f"Setup complete: {len(nonzero)} non-zero codewords")
print(f"Center: {len(center)}, Non-center: {len(non_center)}")

# ============================================================
# QUESTION 1: Is g/Z simple?
# ============================================================
print("\n" + "=" * 75)
print("QUESTION 1: Is g/Z simple?")
print("=" * 75)

print(
    """
g/Z is 648-dimensional with Z_3^2 grading (8 components of dim 81).

A Lie algebra is SIMPLE if:
  1. It has no non-trivial ideals
  2. It is non-abelian

We know g/Z is non-abelian (omega is non-degenerate on F_3^2 - {0}).

For simplicity, we need to check that every ideal is either 0 or all of g/Z.

An ideal I satisfies [g/Z, I] <= I.
Since the bracket respects the grading, any ideal is a union of grade components.
"""
)

# Can we build ideals from subsets of grades?
print("Testing if g/Z has proper ideals by grade structure:")

# The non-central grades are F_3^2 - {0}
non_origin_grades = [(i, j) for i in range(3) for j in range(3) if (i, j) != (0, 0)]

# For an ideal, if it contains grade g, then [g, h] for any h with omega(g,h) != 0
# gives g+h with non-zero coefficient
print("\nGrade connectivity under brackets:")

# Build the graph: edge from g1 to g2 if there exists h with [g1, h] -> g2 non-trivially
for g1 in non_origin_grades[:4]:
    targets = set()
    for h in non_origin_grades:
        if omega(g1, h) != 0:
            g_sum = ((g1[0] + h[0]) % 3, (g1[1] + h[1]) % 3)
            if g_sum != (0, 0):
                targets.add(g_sum)
    print(f"  From {g1}, can reach: {sorted(targets)}")

print(
    """
Key observation: The grade structure is TRANSITIVE under brackets.
Starting from any non-zero grade, we can reach all other non-zero grades.

This suggests g/Z might be simple (or close to it).
Let's verify more carefully...
"""
)

# ============================================================
# QUESTION 2: Decomposition of 648
# ============================================================
print("\n" + "=" * 75)
print("QUESTION 2: Decomposition of 648")
print("=" * 75)

print(
    """
648 = 8 * 81 = 8 * 3^4 = 2^3 * 3^4

Interesting factorizations:
  648 = 72 * 9   (72 = |E6 roots|, 9 = |F_3^2|)
  648 = 27 * 24  (27 = |Albert algebra|, 24 = |codewords of weight 12|)
  648 = 81 * 8   (81 = fiber size, 8 = non-central grades)

Could g/Z be related to something like E6 tensor F_3^something?
"""
)

print("\n648 vs famous dimensions:")
dimensions = {
    "sl(n)": [(n, n**2 - 1) for n in range(2, 30)],
    "so(n)": [(n, n * (n - 1) // 2) for n in range(3, 40)],
    "sp(2n)": [(n, n * (2 * n + 1)) for n in range(1, 20)],
    "E6": 78,
    "E7": 133,
    "E8": 248,
    "F4": 52,
    "G2": 14,
}

# Check 648 against sums/products
print("Checking 648 = sum or product of simple Lie algebra dimensions:")
simple_dims = [78, 133, 248, 52, 14]
for n in range(2, 30):
    simple_dims.append(n**2 - 1)  # sl(n+1)

# Check sums
for d1 in simple_dims[:20]:
    d2 = 648 - d1
    if d2 > 0 and d2 in simple_dims:
        print(f"  648 = {d1} + {d2}")

# ============================================================
# QUESTION 3: The 80-dimensional center
# ============================================================
print("\n" + "=" * 75)
print("QUESTION 3: Understanding the 80-dim center")
print("=" * 75)

print(
    f"""
The center Z has {len(center)} = 81 - 1 = 3^4 - 1 elements.

This is the number of non-zero elements in F_3^4!

Could Z be related to the dual of F_3^4?
Or perhaps to the projective space PG(3, 3)?

|PG(3, 3)| = (3^4 - 1)/(3 - 1) = 80/2 = 40 points... no, that's different.

Actually PG(n, q) has (q^{n+1} - 1)/(q - 1) points.
So PG(3, 3) has (81 - 1)/2 = 40 points.

80 = 2 * 40 = 2 * |PG(3, 3)|

Interesting!
"""
)

# Weight distribution in center
center_weights = defaultdict(int)
for c in center:
    w = sum(1 for x in c if x != 0)
    center_weights[w] += 1

print("Weight distribution in center:")
for w in sorted(center_weights.keys()):
    print(f"  Weight {w}: {center_weights[w]} codewords")

# ============================================================
# QUESTION 4: Searching for E6 (78-dimensional)
# ============================================================
print("\n" + "=" * 75)
print("QUESTION 4: Searching for E6 inside the algebra")
print("=" * 75)

print(
    """
E6 has dimension 78 = 72 + 6 (roots + Cartan).
E6 naturally acts on the 27-dimensional Albert algebra.

If E6 embeds in our algebra, it would be as a 78-dimensional subalgebra.
Such a subalgebra must be closed under brackets.

Let's search for 78-element closed subsets...
"""
)

# A subalgebra S has [S, S] <= S
# Since our bracket only gives non-zero output when omega != 0,
# we need the set of grades in S to be "symplectically closed"

print("Grade patterns that could give subalgebras:")
print("For S to be a subalgebra, the grades in S must satisfy:")
print("  if g1, g2 in grades(S) and omega(g1, g2) != 0, then g1+g2 in grades(S)")

# Try: just the center (grades = {(0,0)})
print("\n  Center only: grades = {(0,0)}, dim = 80")
print("    [Z, Z] = 0 (trivially closed, but abelian)")

# Try: center + one fiber
print("\n  Center + one fiber: e.g. grades = {(0,0), (1,0)}, dim = 80+81 = 161")
print("    [V_{(1,0)}, V_{(1,0)}] = 0 (omega((1,0),(1,0)) = 0)")
print("    This is abelian! Not interesting as Lie algebra.")

# Try: center + two non-commuting fibers
print("\n  Center + two fibers: e.g. {(0,0), (1,0), (0,1)}")
print("    omega((1,0), (0,1)) = 1 != 0")
print("    [(1,0), (0,1)] -> (1,1)")
print("    Not closed unless we include (1,1)!")

# ============================================================
# QUESTION 5: The quotient structure
# ============================================================
print("\n" + "=" * 75)
print("QUESTION 5: What IS g/Z?")
print("=" * 75)

print(
    """
g/Z has structure:
  - 8 abelian fibers V_g (g != 0), each 81-dimensional
  - Bracket: [V_g1, V_g2] -> V_{g1+g2} with coefficient omega(g1, g2)

This is like a "super-Heisenberg" structure!

The standard 2n+1 dimensional Heisenberg algebra has:
  - Basis: x_1, ..., x_n, y_1, ..., y_n, z
  - [x_i, y_i] = z, all others zero

Our structure is:
  - 8 "super-directions" (the non-zero grades)
  - Each direction has 81 basis elements
  - Bracket controlled by symplectic form on F_3^2
"""
)

# The key question: how do the 81 elements within a fiber interact when
# bracketed with elements from another fiber?

print("\nFiber interaction analysis:")
print("Take V_{(1,0)} and V_{(0,1)}. omega((1,0),(0,1)) = 1 != 0.")
print("So [V_{(1,0)}, V_{(0,1)}] -> V_{(1,1)} non-trivially.")
print()
print("For c1 in V_{(1,0)} and c2 in V_{(0,1)}:")
print("  [E_{c1}, E_{c2}] = 1 * E_{c1+c2}")
print("  where c1+c2 is in V_{(1,1)}")

# Check: do we hit all of V_{(1,1)} this way?
V_10 = by_grade[(1, 0)]
V_01 = by_grade[(0, 1)]
V_11 = by_grade[(1, 1)]

outputs = set()
for c1 in V_10:
    for c2 in V_01:
        result = add_cw(c1, c2)
        if result in code_set and grade(result) == (1, 1):
            outputs.add(result)

print(
    f"\n[V_{{(1,0)}}, V_{{(0,1)}}] produces {len(outputs)} of {len(V_11)} elements in V_{{(1,1)}}"
)

if len(outputs) == len(V_11):
    print("COMPLETE: The bracket is surjective onto V_{(1,1)}!")
else:
    print(f"PARTIAL: Only {len(outputs)/len(V_11)*100:.1f}% coverage")

# ============================================================
# QUESTION 6: Representation on F_3^27
# ============================================================
print("\n" + "=" * 75)
print("QUESTION 6: Does g act on F_3^27?")
print("=" * 75)

print(
    """
sl(27) naturally acts on F_3^27 by matrix multiplication.
Does our algebra g also have a 27-dimensional representation?

The codewords live in F_3^12.
There are 729 = 27^2 of them.
Could we pair them somehow with matrices?

Hypothesis: The algebra g acts on some 27-dimensional space related to
the Albert algebra or the projective plane PG(2, 3).

|PG(2, 3)| = (3^3 - 1)/(3 - 1) = 26/2 = 13 points
Hmm, that's 13, not 27.

27 = 3^3 is the order of the Heisenberg group H_3(F_3).
27 is also dim(Albert algebra J_3(O)).
"""
)

# ============================================================
# QUESTION 7: Connection to Mathieu group M11
# ============================================================
print("\n" + "=" * 75)
print("QUESTION 7: M11 action")
print("=" * 75)

print(
    """
The Mathieu group M11 is the automorphism group of the Golay code G12.
|M11| = 7920 = 8 * 9 * 10 * 11

M11 acts on the 12 coordinate positions.
This induces an action on codewords, and hence on our Lie algebra.

Since M11 permutes codewords, it permutes the basis elements E_c.
The key question: Does M11 preserve the Lie bracket?

[E_{sigma(c1)}, E_{sigma(c2)}] = omega(grade(sigma(c1)), grade(sigma(c2))) * E_{sigma(c1)+sigma(c2)}
                                = omega(grade(sigma(c1)), grade(sigma(c2))) * E_{sigma(c1+c2)}

For M11 to act as automorphisms, we need:
  omega(grade(sigma(c1)), grade(sigma(c2))) = omega(grade(c1), grade(c2))

This means M11 must preserve the grade structure!
"""
)

# Does M11 preserve grades?
# The grade is determined by the directions pattern
# If M11 permutes positions that have the same direction, grades are preserved

print("Grade is computed from directions:")
print(f"  Positions 0,4,8 have direction (1,0)")
print(f"  Positions 1,5,9 have direction (0,1)")
print(f"  Positions 2,6,10 have direction (1,1)")
print(f"  Positions 3,7,11 have direction (1,2)")
print()
print("For M11 to preserve grades, it must map each direction-class to itself")
print("(or at least preserve the symplectic pairing).")
print()
print("This is a strong constraint on which M11 elements are automorphisms!")

# ============================================================
# FINAL SYNTHESIS
# ============================================================
print("\n" + "=" * 75)
print("SYNTHESIS AND CONJECTURES")
print("=" * 75)

print(
    """
STRUCTURE OF THE GOLAY LIE ALGEBRA g:

1. DIMENSION: 728 = 27^2 - 1 (same as sl(27))

2. CENTER: 80-dimensional, spanned by grade-(0,0) codewords
   These are exactly the "isotropic" codewords w.r.t. the grade pairing.

3. DERIVED ALGEBRA: [g,g] = 648-dimensional (non-central part)
   This is PERFECT: [[g,g],[g,g]] = [g,g]

4. QUOTIENT: g/Z ~ [g,g] (as vector spaces, with bracket)
   This is a 648-dimensional Lie algebra graded by F_3^2 - {0}

5. FIBER STRUCTURE:
   - Each fiber V_g (81-dim) is abelian
   - [V_g1, V_g2] -> V_{g1+g2} with coefficient omega(g1, g2)
   - This is "super-Heisenberg" structure

6. MAXIMAL ABELIAN SUBALGEBRAS:
   - Lines in F_3^2 give 242-dim abelian subalgebras
   - Z + V_g is 161-dim abelian

CONJECTURES:

A. g is NOT isomorphic to sl(27) (different centers)

B. g/Z is likely SIMPLE or close to simple
   (the grade structure is strongly connected)

C. g may be related to a central extension of some tensor product
   involving the Heisenberg algebra and an 81-dimensional representation

D. The 80-dim center may be related to the 80 non-trivial elements of F_3^4

E. E6 (78-dim) probably does NOT embed as a subalgebra
   (grade structure forces larger dimensions)

F. M11 likely acts on g, but may not preserve the full algebra structure
   depending on how it interacts with the grading

OPEN QUESTIONS:

1. What IS g/Z exactly? Is it simple?
2. Is g the universal central extension of g/Z?
3. How does the algebra relate to the exceptional Lie algebras?
4. Is there a natural 27-dimensional representation?
5. What is the precise action of M11?
"""
)

print("\n" + "=" * 75)
print("END OF DEEP EXPLORATION")
print("=" * 75)
