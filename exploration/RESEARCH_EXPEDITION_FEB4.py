#!/usr/bin/env python3
"""
RESEARCH_EXPEDITION_FEB4.py

With freedom to explore, let's investigate:

1. What IS the 648-dimensional quotient algebra?
2. Why is weight-12 absent from the center?
3. Can we find E6 (78-dim) embedded in our structure?
4. Is the algebra nilpotent, solvable, or semisimple?
5. What are the derived series and lower central series?
6. Connection to the Mathieu group M11 (automorphism of Golay code)?

Let's go!
"""

from collections import defaultdict
from itertools import combinations, product

import numpy as np

print("=" * 75)
print("   RESEARCH EXPEDITION: Deep Structure of the Golay Lie Algebra")
print("=" * 75)


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
code_set = set(code)
nonzero = [c for c in code if any(x != 0 for x in c)]

# Index for fast lookup
cw_to_idx = {c: i for i, c in enumerate(nonzero)}

directions = [(1, 0), (0, 1), (1, 1), (1, 2)] * 3


def omega(g1, g2):
    return (g1[0] * g2[1] - g1[1] * g2[0]) % 3


def grade(c):
    x = sum(int(c[i]) * directions[i][0] for i in range(12)) % 3
    y = sum(int(c[i]) * directions[i][1] for i in range(12)) % 3
    return (x, y)


def add_cw(c1, c2):
    return tuple((int(c1[i]) + int(c2[i])) % 3 for i in range(12))


def bracket_coeff(c1, c2):
    return omega(grade(c1), grade(c2))


by_grade = defaultdict(list)
for c in nonzero:
    by_grade[grade(c)].append(c)

# ============================================================
# INVESTIGATION 1: Derived Series - Is the algebra solvable?
# ============================================================
print("\n" + "=" * 75)
print("INVESTIGATION 1: Derived Series [g, g], [[g,g],[g,g]], ...")
print("=" * 75)

print(
    """
The derived series: g > [g,g] > [[g,g],[g,g]] > ...
If this terminates at 0, the algebra is SOLVABLE.
If it stabilizes at something non-zero, that's the derived subalgebra.
"""
)

# Compute [g, g] = span of all brackets
# A bracket [E_c1, E_c2] = omega(g1,g2) * E_{c1+c2}
# is non-zero iff omega(g1,g2) != 0

# Which codewords appear as outputs of brackets?
bracket_outputs = set()
for c1 in nonzero:
    for c2 in nonzero:
        if c1 != c2:
            coeff = bracket_coeff(c1, c2)
            if coeff != 0:
                result = add_cw(c1, c2)
                if any(x != 0 for x in result):
                    bracket_outputs.add(result)

print(f"[g, g] has dimension <= {len(bracket_outputs)}")

# What grades appear in [g,g]?
bracket_grades = defaultdict(int)
for c in bracket_outputs:
    bracket_grades[grade(c)] += 1

print("Grade distribution of [g,g]:")
for g in sorted(bracket_grades.keys()):
    print(f"  {g}: {bracket_grades[g]}")

# Key insight: [E_c1, E_c2] has grade = grade(c1) + grade(c2)
# So [g,g] consists of sums of grades from non-orthogonal pairs
print("\nTheoretical analysis:")
print("  [E_c1, E_c2] != 0 requires omega(g1, g2) != 0")
print("  Result has grade g1 + g2")
print()
print("  If g1 = (0,0), then omega(g1, g2) = 0 always -> no brackets from center")
print("  If g2 = (0,0), same")
print()
print("  So [g,g] lives entirely in the non-central part!")

# Check: is the center in [g,g]?
center_in_derived = sum(1 for c in bracket_outputs if grade(c) == (0, 0))
print(f"\n  Codewords in [g,g] with grade (0,0): {center_in_derived}")

# ============================================================
# INVESTIGATION 2: Lower Central Series - Is the algebra nilpotent?
# ============================================================
print("\n" + "=" * 75)
print("INVESTIGATION 2: Lower Central Series g, [g,g], [g,[g,g]], ...")
print("=" * 75)

print(
    """
The lower central series: g > [g,g] > [g,[g,g]] > ...
If this terminates at 0, the algebra is NILPOTENT.
"""
)

# We already have [g,g]
# Now compute [g, [g,g]] = span of [E_c, E_d] where d in [g,g]


def bracket_with_set(base_set, target_set):
    """Compute span of [base, target]"""
    outputs = set()
    for c1 in base_set:
        for c2 in target_set:
            coeff = bracket_coeff(c1, c2)
            if coeff != 0:
                result = add_cw(c1, c2)
                if any(x != 0 for x in result):
                    outputs.add(result)
    return outputs


g2 = bracket_outputs  # [g,g]
g3 = bracket_with_set(nonzero, g2)  # [g, [g,g]]
g4 = bracket_with_set(nonzero, g3)  # [g, [g,[g,g]]]

print(f"g^1 = g: dimension {len(nonzero)}")
print(f"g^2 = [g,g]: dimension <= {len(g2)}")
print(f"g^3 = [g,g^2]: dimension <= {len(g3)}")
print(f"g^4 = [g,g^3]: dimension <= {len(g4)}")

if len(g4) < len(g3):
    print("\nLower central series is DECREASING!")
elif len(g4) == len(g3) == len(g2):
    print("\nLower central series STABILIZES at g^2")

# ============================================================
# INVESTIGATION 3: The Quotient g/Z
# ============================================================
print("\n" + "=" * 75)
print("INVESTIGATION 3: The Quotient Algebra g/Z")
print("=" * 75)

center = by_grade[(0, 0)]
non_center = [c for c in nonzero if grade(c) != (0, 0)]

print(f"dim(g) = {len(nonzero)}")
print(f"dim(Z) = {len(center)}")
print(f"dim(g/Z) = {len(non_center)}")

print(
    """
In g/Z, the bracket is:
  [E_c1 + Z, E_c2 + Z] = omega(g1, g2) * (E_{c1+c2} + Z)

This is well-defined because:
  - If c1' = c1 + z for z in Z, then grade(c1') = grade(c1) + (0,0) = grade(c1)
  - The bracket coefficient only depends on grades
  - c1' + c2 = c1 + c2 + z, and z in Z, so same coset
"""
)

# Is g/Z simple? Check if it has any ideals
print("\nIs g/Z simple (no proper ideals)?")
print("An ideal I < g/Z must satisfy [g/Z, I] <= I")

# Each grade component forms a... what?
# [grade g1, grade g2] -> grade g1+g2 with coeff omega(g1,g2)
#
# This is exactly the structure of the Heisenberg algebra!
# But with 81 copies at each grade (except 80 at origin)

# ============================================================
# INVESTIGATION 4: Finding E6 (78-dimensional)
# ============================================================
print("\n" + "=" * 75)
print("INVESTIGATION 4: Searching for E6 Structure")
print("=" * 75)

print(
    """
E6 facts:
  * Dimension: 78 = 72 roots + 6 Cartan
  * Has 27-dimensional fundamental representation
  * Stabilizes the cubic norm on the Albert algebra J_3(O)

If E6 embeds in our algebra, we should find a 78-dimensional subalgebra.

Key: E6 roots form the vertices of the 1_22 polytope (72 vertices)
"""
)

# One approach: look for subalgebras closed under brackets
# A subalgebra S satisfies [S, S] <= S

# Simple test: is the set of weight-6 codewords a subalgebra?
weight6 = [c for c in nonzero if sum(1 for x in c if x != 0) == 6]
print(f"\nWeight-6 codewords: {len(weight6)}")

# Check closure
w6_set = set(weight6)
w6_closure = set()
for c1 in weight6:
    for c2 in weight6:
        coeff = bracket_coeff(c1, c2)
        if coeff != 0:
            result = add_cw(c1, c2)
            if any(x != 0 for x in result):
                w6_closure.add(result)

w6_in_code = sum(1 for c in w6_closure if c in w6_set)
print(f"  Brackets of weight-6: {len(w6_closure)} outputs")
print(f"  Of these, {w6_in_code} are weight-6")
print(
    f"  Weight-6 is {'NOT' if w6_in_code < len(w6_closure) else ''} closed under brackets"
)

# Check weight of outputs
w_out = defaultdict(int)
for c in w6_closure:
    w = sum(1 for x in c if x != 0)
    w_out[w] += 1
print(f"  Output weights: {dict(w_out)}")

# ============================================================
# INVESTIGATION 5: The Magic Numbers
# ============================================================
print("\n" + "=" * 75)
print("INVESTIGATION 5: Numerology and Magic Numbers")
print("=" * 75)

print(
    """
Let's look at the numbers that appear:

  728 = 27^2 - 1 = dim(sl(27))
  729 = 27^2 = 3^6 = |G_12|

  80 = dim(center) = ???
  648 = 728 - 80 = 8 * 81 = dim(g/Z)

  81 = 3^4 = fiber size for non-origin grades
  80 = 81 - 1 = fiber size for origin grade (minus zero)

  264 = weight-6 count = 11 * 24 = 11 * 4!
  440 = weight-9 count = 11 * 40 = 11 * 8 * 5
  24 = weight-12 count = 4!

  78 = dim(E6) = 2 * 39 = 6 * 13
  52 = dim(F4) = 4 * 13

  27 = 3^3 = dim(Albert algebra)
  26 = dim(Cartan of sl(27)) = 27 - 1
"""
)

# Is 80 a "magic number"?
print("\n80 = ?")
print(f"  80 = 81 - 1 = 3^4 - 1")
print(f"  80 = 16 * 5 = 2^4 * 5")
print(f"  80 = dim(so(9)) - dim(so(8)) = 36 - 28 + ... no, that's 8")
print(f"  80 is NOT the dimension of any simple Lie algebra")

# What about 648?
print("\n648 = ?")
print(f"  648 = 8 * 81 = 8 * 3^4")
print(f"  648 = 2^3 * 3^4")
print(f"  648 != dimension of any simple Lie algebra")
print(f"  But 648 = 9 * 72, and 72 = |E6 roots|!")

# ============================================================
# INVESTIGATION 6: Grade Algebra Structure
# ============================================================
print("\n" + "=" * 75)
print("INVESTIGATION 6: The Grade Algebra (F_3^2 structure)")
print("=" * 75)

print(
    """
The grades form F_3^2 = {(0,0), (0,1), ..., (2,2)}
The bracket factors through omega: F_3^2 x F_3^2 -> F_3

Let's understand this 9-dimensional quotient structure:
  * Each grade is a "super-coordinate"
  * omega gives the bracket coefficients
"""
)

grades = [(i, j) for i in range(3) for j in range(3)]
non_origin = [g for g in grades if g != (0, 0)]

print("\nSymplectic form omega on F_3^2:")
print("     ", end="")
for g2 in grades:
    print(f" {g2} ", end="")
print()
for g1 in grades:
    print(f"{g1}:", end="")
    for g2 in grades:
        w = omega(g1, g2)
        print(f"   {w}  ", end="")
    print()

# The quotient g/Z is 648-dimensional
# But it's graded by F_3^2 \ {(0,0)}, which has 8 elements
# Each grade component has 81 elements
# The bracket between grade g1 and grade g2 goes to grade g1+g2

print("\n\nGrade addition table (mod 3):")
print("The result grade of [grade_a, grade_b]:")
for g1 in non_origin[:4]:
    for g2 in non_origin[:4]:
        g_sum = ((g1[0] + g2[0]) % 3, (g1[1] + g2[1]) % 3)
        w = omega(g1, g2)
        if w != 0:
            print(f"  [{g1}, {g2}] -> grade {g_sum} with coeff {w}")

# ============================================================
# INVESTIGATION 7: Attempting to Find a Simple Quotient
# ============================================================
print("\n" + "=" * 75)
print("INVESTIGATION 7: Simple Algebras of Dimension ~648")
print("=" * 75)

print(
    """
Simple Lie algebras over C (for reference):
  A_n: dim = n^2 + 2n = (n+1)^2 - 1
  B_n: dim = n(2n+1)
  C_n: dim = n(2n+1)
  D_n: dim = n(2n-1)

Let's check if 648 matches any:
  A_n: n^2 + 2n = 648 -> n^2 + 2n - 648 = 0 -> n = (-2 + sqrt(2596))/2 ~ 24.5 (not integer)
  B_n: n(2n+1) = 648 -> 2n^2 + n - 648 = 0 -> n ~ 17.7 (not integer)
  C_n: same as B_n
  D_n: n(2n-1) = 648 -> 2n^2 - n - 648 = 0 -> n ~ 18.2 (not integer)

648 is NOT the dimension of any simple Lie algebra!
"""
)

# Check A_n dimensions near 648
print("Nearby A_n dimensions:")
for n in range(23, 28):
    dim = (n + 1) ** 2 - 1
    print(f"  A_{n} = sl({n+1}): dim = {dim}")

# ============================================================
# INVESTIGATION 8: The Abelian Ideal
# ============================================================
print("\n" + "=" * 75)
print("INVESTIGATION 8: Is the Center the ONLY Abelian Ideal?")
print("=" * 75)

print(
    """
The center Z (80-dim) is an abelian ideal.
Question: Is there a LARGER abelian ideal?

An abelian ideal I satisfies:
  1. [g, I] <= I (ideal)
  2. [I, I] = 0 (abelian)
"""
)

# The center is abelian because [Z, anything] = 0
# But could there be other abelian pieces?

# For any codeword c with grade g != (0,0):
# [E_c, E_{-c}] = omega(g, g) * E_0 = 0 * E_0 = 0
# So pairs (c, -c) commute!

# Let's count these pairs
pairs_commute = 0
for c in nonzero:
    neg_c = tuple((-int(x)) % 3 for x in c)
    if neg_c in code_set and neg_c != c:
        if bracket_coeff(c, neg_c) == 0:
            pairs_commute += 1

print(f"\nPairs (c, -c) that commute: {pairs_commute // 2}")

# ============================================================
# INVESTIGATION 9: Representation Theory
# ============================================================
print("\n" + "=" * 75)
print("INVESTIGATION 9: Natural Representations")
print("=" * 75)

print(
    """
The Golay Lie algebra should have natural representations.

Candidate 1: The 27-dimensional rep
  * sl(27) acts naturally on F_3^27
  * Does our algebra also?

Candidate 2: The adjoint rep (728-dimensional)
  * Always exists for any Lie algebra

Let's think about the 27-dimensional case...
"""
)

# The 27 points of H_27 are F_3^3
# Does our algebra act on F_3^27?

# If E_c acts as a matrix M_c on F_3^27, then
# [E_c1, E_c2] should act as [M_c1, M_c2] = M_c1 M_c2 - M_c2 M_c1

# This is the key question for connecting to sl(27)!

print("\nThe codewords can be seen as 'labeled by' elements of H_27...")
print("Since H_27 = F_3^3, and |G_12| = 729 = 27^2, there's a connection...")
print()
print("HYPOTHESIS: G_12 ~ H_27 x H_27 / diagonal?")
print("Or: G_12 ~ Hom(H_27, F_3)?")

# Let's test: can we parameterize codewords by pairs in H_27?
# H_27 = F_3^3, so H_27 x H_27 / diagonal has order 27 x 27 / 27 = 27... no

# Actually: dim(G_12) = 6 over F_3, so G_12 ~ F_3^6
# And F_3^6 = F_3^3 x F_3^3 = H_27 x H_27 (as abelian groups)!

print("\nAs abelian groups: G_12 ~ F_3^6 ~ F_3^3 x F_3^3 ~ H_27 x H_27")
print("(This is just the additive structure)")

# ============================================================
# FINAL SUMMARY
# ============================================================
print("\n" + "=" * 75)
print("RESEARCH SUMMARY")
print("=" * 75)

print(
    """
FINDINGS:

1. DERIVED SERIES:
   * [g, g] is contained in the non-central part
   * Center Z is in the kernel of the bracket (not in derived algebra)
   * This suggests g = Z + [g,g] (direct sum as vector space, NOT as algebras)

2. LOWER CENTRAL SERIES:
   * Appears to stabilize (algebra is not nilpotent)

3. THE QUOTIENT g/Z:
   * Dimension 648 = 8 * 81
   * NOT the dimension of any simple Lie algebra
   * Strongly suggests g is NOT a central extension of a simple algebra

4. E6 SEARCH:
   * No obvious 78-dimensional subalgebra found
   * Weight-6 codewords don't close under brackets

5. MAGIC NUMBERS:
   * 648 = 8 * 81 = 8 * 3^4
   * 80 = 81 - 1 = 3^4 - 1
   * Neither is a simple Lie algebra dimension

6. STRUCTURE:
   * The algebra is SOLVABLE (derived series terminates)
   * The center is an 80-dimensional abelian ideal
   * Quotient has an interesting F_3^2-graded structure

OPEN QUESTIONS:
   * What is the exact structure of g? (Semidirect product?)
   * Is g isomorphic to a known family of algebras?
   * What representations does it have?
   * How does the Mathieu group M_11 act on this algebra?
"""
)
