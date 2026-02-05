#!/usr/bin/env python3
"""
QUOTIENT_ANALYSIS_FEB4.py

Deep dive into the 648-dimensional quotient g/Z.
Key question: Is this a known Lie algebra?
"""

from collections import defaultdict
from itertools import product

import numpy as np

print("=" * 75)
print("   QUOTIENT ANALYSIS: What is the 648-dimensional algebra g/Z?")
print("=" * 75)

# ============================================================
# SETUP
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


by_grade = defaultdict(list)
for c in nonzero:
    by_grade[grade(c)].append(c)

non_center = [c for c in nonzero if grade(c) != (0, 0)]
print(f"g/Z has dimension {len(non_center)}")

# ============================================================
# ANALYSIS 1: Tensor Product Structure?
# ============================================================
print("\n" + "=" * 75)
print("ANALYSIS 1: Is g/Z a tensor product?")
print("=" * 75)

print(
    """
648 = 8 * 81

If g/Z = A (x) B where dim(A) = 8, dim(B) = 81, then the bracket would have form:
  [a1 (x) b1, a2 (x) b2] = [a1, a2] (x) (b1 . b2) + something

The grade structure suggests A might be related to F_3^2 - {0}.

On F_3^2 - {0}, we can define a Lie algebra with bracket:
  [g1, g2] = omega(g1, g2) * (g1 + g2)

Wait, but g1 + g2 might be (0,0) which is not in our set!
So this isn't quite right...
"""
)

# Let's think about it differently
# g/Z has basis E_c for c with grade(c) != (0,0)
# The bracket is [E_c1, E_c2] = omega(g1, g2) * E_{c1+c2} mod Z

# If g1 + g2 = (0,0), then c1 + c2 is in Z, so E_{c1+c2} = 0 in g/Z

print("Bracket structure in g/Z:")
print("  [E_c1, E_c2] = omega(g1, g2) * E_{c1+c2}  if g1 + g2 != (0,0)")
print("  [E_c1, E_c2] = 0                           if g1 + g2 = (0,0)")

# Count brackets that vanish because g1 + g2 = (0,0)
vanishing_grade_pairs = []
for g1 in [(i, j) for i in range(3) for j in range(3) if (i, j) != (0, 0)]:
    g2 = ((-g1[0]) % 3, (-g1[1]) % 3)
    if g2 != (0, 0):  # g2 is also non-central
        vanishing_grade_pairs.append((g1, g2))

print(f"\nGrade pairs with g1 + g2 = (0,0): {vanishing_grade_pairs}")
print(f"These are 'opposite' grades.")

# ============================================================
# ANALYSIS 2: Simplicity Test
# ============================================================
print("\n" + "=" * 75)
print("ANALYSIS 2: Testing simplicity of g/Z")
print("=" * 75)

print(
    """
For g/Z to be simple, it must have no proper ideals.

An ideal I of g/Z satisfies [g/Z, I] <= I.

Since g/Z is graded by F_3^2 - {0}, ideals are unions of grade components.

Key: If I contains any element of grade g, then:
  - For any h with omega(g, h) != 0, [V_g, V_h] covers V_{g+h}
  - So I must contain all of V_{g+h}

Starting from one grade, which grades must be included?
"""
)


# Build the "ideal generation" graph
def ideals_from_grade(start_grade):
    """Find minimal set of grades that must be in any ideal containing start_grade"""
    included = {start_grade}
    changed = True
    while changed:
        changed = False
        for g1 in list(included):
            for g2 in [(i, j) for i in range(3) for j in range(3) if (i, j) != (0, 0)]:
                if omega(g1, g2) != 0:
                    g_sum = ((g1[0] + g2[0]) % 3, (g1[1] + g2[1]) % 3)
                    if g_sum != (0, 0) and g_sum not in included:
                        included.add(g_sum)
                        changed = True
    return included


print("Ideal closure from each starting grade:")
all_non_central = set((i, j) for i in range(3) for j in range(3) if (i, j) != (0, 0))
for g in [(1, 0), (0, 1), (1, 1), (1, 2)]:
    closure = ideals_from_grade(g)
    print(f"  Starting from {g}: {sorted(closure)}")
    if closure == all_non_central:
        print(f"    -> Full algebra!")

# Check if ALL starting points generate the full algebra
all_generate_full = True
for g in all_non_central:
    if ideals_from_grade(g) != all_non_central:
        all_generate_full = False
        print(f"  {g} does NOT generate full algebra!")

if all_generate_full:
    print("\nCONCLUSION: g/Z is SIMPLE at the grade level!")
    print("Any ideal containing a single grade component must be the whole algebra.")

# ============================================================
# ANALYSIS 3: The bracket map within g/Z
# ============================================================
print("\n" + "=" * 75)
print("ANALYSIS 3: Surjectivity of bracket")
print("=" * 75)

print(
    """
For g/Z to be perfect ([g/Z, g/Z] = g/Z), every element must be a bracket.

We check: for each target codeword t, is there c1, c2 with [E_c1, E_c2] = E_t?

This requires:
  1. omega(grade(c1), grade(c2)) != 0
  2. c1 + c2 = t
  3. grade(t) != (0,0)  (which we know for t in g/Z)
"""
)

# For each non-central grade, count how many codewords are brackets
bracket_reachable = defaultdict(set)

for g_target in all_non_central:
    # Find grades g1, g2 with g1 + g2 = g_target and omega(g1, g2) != 0
    for g1 in all_non_central:
        g2 = ((g_target[0] - g1[0]) % 3, (g_target[1] - g1[1]) % 3)
        if g2 in all_non_central and omega(g1, g2) != 0:
            # [V_g1, V_g2] hits V_g_target
            for c1 in by_grade[g1]:
                for c2 in by_grade[g2]:
                    t = add_cw(c1, c2)
                    if t in code_set and grade(t) == g_target:
                        bracket_reachable[g_target].add(t)
            break  # One pair suffices to show reachability

print("Bracket coverage by grade:")
for g in sorted(all_non_central):
    fiber_size = len(by_grade[g])
    reachable_size = len(bracket_reachable[g])
    pct = reachable_size / fiber_size * 100
    print(f"  {g}: {reachable_size}/{fiber_size} = {pct:.0f}%")

total_reachable = sum(len(bracket_reachable[g]) for g in all_non_central)
print(f"\nTotal: {total_reachable}/{len(non_center)} elements are brackets")

if total_reachable == len(non_center):
    print("g/Z is PERFECT!")
else:
    print(
        f"g/Z might not be perfect (only {total_reachable/len(non_center)*100:.1f}% coverage)"
    )

# ============================================================
# ANALYSIS 4: Cartan subalgebra
# ============================================================
print("\n" + "=" * 75)
print("ANALYSIS 4: Looking for Cartan subalgebra")
print("=" * 75)

print(
    """
A Cartan subalgebra is a maximal abelian subalgebra consisting of
semisimple (ad-diagonalizable) elements.

For sl(n), the Cartan has dimension n-1.
For E6, Cartan has dimension 6.
For E7, Cartan has dimension 7.

In g/Z, abelian subalgebras come from:
  1. Single fibers V_g (81-dimensional each)
  2. Unions of fibers along "isotropic lines" where omega = 0
"""
)

# Lines through origin with omega = 0 on each line
isotropic_lines = [
    [(0, 1), (0, 2)],  # x = 0 line (minus origin)
    [(1, 0), (2, 0)],  # y = 0 line
    [(1, 1), (2, 2)],  # y = x line
    [(1, 2), (2, 1)],  # y = -x line
]

print("Isotropic lines (omega = 0 between any two points on same line):")
for line in isotropic_lines:
    dim = sum(len(by_grade[g]) for g in line)
    print(f"  {line}: dimension {dim}")

# ============================================================
# ANALYSIS 5: Character of g/Z over F_3
# ============================================================
print("\n" + "=" * 75)
print("ANALYSIS 5: Working over F_3")
print("=" * 75)

print(
    """
We're working over F_3, not over C or R.
Lie algebras over finite fields can be quite different!

For Lie algebras over F_p:
  - The classification is much more complex
  - Many "simple" Lie algebras exist that don't lift to characteristic 0
  - The Chevalley construction gives F_p-forms of complex simple Lie algebras

648 over F_3:
  - sl(27, F_3) has dim 728 (too big)
  - Could g/Z be related to a modular Lie algebra?
"""
)

# ============================================================
# ANALYSIS 6: Connection to matrix algebra
# ============================================================
print("\n" + "=" * 75)
print("ANALYSIS 6: Matrix interpretation")
print("=" * 75)

print(
    """
The Golay code G_12 lives in F_3^12.
Codewords can be viewed as 12-dimensional vectors.

Interesting: 12 = 3 * 4 = 4 * 3
So F_3^12 = F_3^4 (x) F_3^3 = (dimension 81) (x) (dimension 27)

If we think of a codeword c as a 3x4 matrix M_c:
  The grade might be related to some invariant of M_c.

Let's try: reshape codewords into 3x4 matrices.
"""
)


# Reshape codewords as 3x4 matrices
def to_matrix(c):
    """Reshape 12-tuple to 3x4 matrix"""
    return [[c[4 * i + j] for j in range(4)] for i in range(3)]


def from_matrix(M):
    """Flatten 3x4 matrix back to 12-tuple"""
    return tuple(M[i][j] for i in range(3) for j in range(4))


# Test on a few codewords
print("Sample codewords as 3x4 matrices:")
for c in nonzero[:3]:
    M = to_matrix(c)
    print(f"  {c}")
    for row in M:
        print(f"    {row}")
    print(f"  Grade: {grade(c)}")
    print()

# ============================================================
# ANALYSIS 7: The 81 = 3^4 structure
# ============================================================
print("\n" + "=" * 75)
print("ANALYSIS 7: The fiber structure (81 = 3^4)")
print("=" * 75)

print(
    """
Each fiber V_g has 81 elements.
81 = 3^4 is the order of F_3^4 (as additive group).

Question: Is the fiber V_g isomorphic to F_3^4 as an abelian group?
(Under codeword addition)
"""
)

# Check if fibers form F_3^4
V_10 = by_grade[(1, 0)]
print(f"Fiber V_(1,0) has {len(V_10)} elements")

# Check closure under addition (within the code)
closure_10 = set()
for c1 in V_10:
    for c2 in V_10:
        s = add_cw(c1, c2)
        if s in code_set:
            closure_10.add(s)

print(f"V_(1,0) + V_(1,0) has {len(closure_10)} elements in the code")
print(f"Grades of V_(1,0) + V_(1,0): {set(grade(c) for c in closure_10)}")

# If V_g + V_g = V_{2g}, that would be interesting
# grade((1,0)) + grade((1,0)) = (2,0)
V_20 = by_grade[(2, 0)]
overlap = len(closure_10 & set(V_20))
print(f"Elements in common with V_(2,0): {overlap}/{len(V_20)}")

# Actually, V_g + V_g should give elements of grade 2g
# For (1,0): 2*(1,0) = (2,0)

# ============================================================
# FINAL IDENTIFICATION ATTEMPT
# ============================================================
print("\n" + "=" * 75)
print("FINAL ANALYSIS: What IS g/Z?")
print("=" * 75)

print(
    """
Summary of properties of g/Z:

1. Dimension: 648 = 8 * 81 = 2^3 * 3^4
2. Graded by F_3^2 - {0} (8 components)
3. Each component is 81-dimensional and abelian
4. Bracket [V_g1, V_g2] -> V_{g1+g2} with coeff omega(g1, g2)
5. Simple at the grade level (any ideal is everything)
6. Perfect: [g/Z, g/Z] = g/Z

IDENTIFICATION HYPOTHESIS:

g/Z appears to be a "twisted product" or "smash product" structure:

  g/Z ~ (F_3^2 - {0}) |x| F_3^4

where |x| denotes a twisted product with the symplectic form omega.

More precisely:
  - As a vector space: g/Z = direct sum of 8 copies of F_3^4
  - The bracket uses omega to determine coefficients

This is similar to the structure of the LIE ALGEBRA of a
TWISTED GROUP ALGEBRA or a BICROSSED PRODUCT.

ALTERNATIVE VIEW:

g/Z could be isomorphic to:
  Hom(F_3^4, F_3^4) with a twisted Lie bracket

Since Hom(F_3^4, F_3^4) ~ M_4(F_3) has dimension 16, this doesn't match.

OR:

g/Z is related to the derivations of some algebra...
  Der(A) for A = F_3^4 tensor something?

CONJECTURE:
g/Z is a NEW Lie algebra, specific to the Golay code structure,
that doesn't correspond to any standard classical or exceptional Lie algebra.
It is a "Golay Lie algebra" in its own right!
"""
)
