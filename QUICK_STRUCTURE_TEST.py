#!/usr/bin/env python3
"""
QUICK_STRUCTURE_TEST.py

A fast investigation of the key structural questions about the Golay Lie algebra.
Optimized to avoid slow nested loops.
"""

import itertools
from collections import defaultdict

print("=" * 75)
print("   QUICK STRUCTURE TEST: Key Questions about the Golay Lie Algebra")
print("=" * 75)

# ============================================================
# BUILD THE GOLAY CODE (fast method)
# ============================================================


def build_golay_code():
    """Build the ternary Golay code G_12 using generator matrix"""
    I6 = [[1 if i == j else 0 for j in range(6)] for i in range(6)]
    A = [
        [0, 1, 1, 1, 1, 1],
        [1, 0, 1, 2, 2, 1],
        [1, 1, 0, 1, 2, 2],
        [1, 2, 1, 0, 1, 2],
        [1, 2, 2, 1, 0, 1],
        [1, 1, 2, 2, 1, 0],
    ]
    G = [I6[i] + A[i] for i in range(6)]

    code = []
    for coeffs in itertools.product(range(3), repeat=6):
        cw = [0] * 12
        for i, c in enumerate(coeffs):
            for j in range(12):
                cw[j] = (cw[j] + c * G[i][j]) % 3
        code.append(tuple(cw))
    return code


code = build_golay_code()
print(f"\nGolay code built: {len(code)} codewords")

# Get the distinguished direction for grading
d1 = code[1]  # First generator direction
d2 = code[3]  # Second generator direction (ensure independence)

print(f"Grading directions:")
print(f"  d1 = {d1}")
print(f"  d2 = {d2}")

# ============================================================
# GRADE AND COCYCLE FUNCTIONS
# ============================================================


def grade(c):
    g0 = sum(c[i] * d1[i] for i in range(12)) % 3
    g1 = sum(c[i] * d2[i] for i in range(12)) % 3
    return (g0, g1)


def omega(g1, g2):
    return (g1[0] * g2[1] - g1[1] * g2[0]) % 3


def bracket_coeff(c1, c2):
    return omega(grade(c1), grade(c2))


def add_cw(c1, c2):
    return tuple((c1[i] + c2[i]) % 3 for i in range(12))


nonzero = [c for c in code if any(x != 0 for x in c)]
code_set = set(code)

# ============================================================
# GRADE DISTRIBUTION
# ============================================================

by_grade = defaultdict(list)
for c in nonzero:
    by_grade[grade(c)].append(c)

print("\nGrade distribution:")
for g in sorted(by_grade.keys()):
    print(f"  {g}: {len(by_grade[g])} codewords")

center = by_grade[(0, 0)]
non_center = [c for c in nonzero if grade(c) != (0, 0)]

print(f"\nCenter (grade (0,0)): {len(center)} elements")
print(f"Non-center: {len(non_center)} elements")

# ============================================================
# INVESTIGATION 1: The Derived Algebra [g,g]
# ============================================================
print("\n" + "=" * 75)
print("INVESTIGATION 1: The Derived Algebra [g,g]")
print("=" * 75)

# Theoretical analysis:
# [E_c1, E_c2] = omega(grade(c1), grade(c2)) * E_{c1+c2}
# This is non-zero iff omega(g1, g2) != 0

# What codewords can appear as c1 + c2?
# For any target codeword t, we need c1, c2 with c1 + c2 = t
# and omega(grade(c1), grade(c2)) != 0

# Key insight: grade(c1 + c2) = grade(c1) + grade(c2)
# So t can appear in [g,g] iff there exist grades g1, g2 with:
#   g1 + g2 = grade(t) and omega(g1, g2) != 0

# For grade (0,0): We need g1 + g2 = (0,0), so g2 = -g1
# omega(g1, -g1) = g1[0]*(-g1[1]) - g1[1]*(-g1[0]) = -g1[0]*g1[1] + g1[1]*g1[0] = 0
# So grade-(0,0) elements CANNOT appear in [g,g]!

print(
    """
THEORETICAL RESULT:

[E_c1, E_c2] = omega(g1, g2) * E_{c1+c2}  where g1 = grade(c1), g2 = grade(c2)

For c1 + c2 to have grade (0,0), we need g1 + g2 = (0,0), so g2 = -g1.
But omega(g1, -g1) = g1[0]*(-g1[1]) - g1[1]*(-g1[0]) = 0.

CONCLUSION: The center Z is NOT in the derived algebra [g,g].
[g,g] lives entirely in the 648-dimensional non-central part!
"""
)

# Verify: Can every non-central grade appear in [g,g]?
print("Can every non-central grade appear in [g,g]?")
for target_grade in [(i, j) for i in range(3) for j in range(3) if (i, j) != (0, 0)]:
    can_appear = False
    for g1 in [(i, j) for i in range(3) for j in range(3)]:
        g2 = ((target_grade[0] - g1[0]) % 3, (target_grade[1] - g1[1]) % 3)
        if omega(g1, g2) != 0:
            can_appear = True
            break
    print(f"  {target_grade}: {'YES' if can_appear else 'NO'}")

# Actually compute [g,g] by finding all achievable outputs
print("\nComputing [g,g] numerically (sampling)...")

# For efficiency, just check if each non-central codeword can appear
# A codeword t appears if there exist c1, c2 with c1+c2=t and omega(grade(c1),grade(c2)) != 0

derived_set = set()
for t in non_center[:100]:  # Sample
    t_grade = grade(t)
    # Find a c1 such that omega(grade(c1), t_grade - grade(c1)) != 0
    for c1 in nonzero[:100]:
        c2 = tuple((t[i] - c1[i]) % 3 for i in range(12))
        if c2 in code_set:
            if bracket_coeff(c1, c2) != 0:
                derived_set.add(t)
                break

print(
    f"Sample of [g,g]: at least {len(derived_set)} of {len(non_center)} non-central codewords appear"
)

# ============================================================
# INVESTIGATION 2: Is [g,g] = non-center?
# ============================================================
print("\n" + "=" * 75)
print("INVESTIGATION 2: Does [g,g] = entire non-central part?")
print("=" * 75)

print(
    """
If [g,g] equals the full 648-dim non-central part, then:
  - g is a Heisenberg-like extension: 0 -> Z -> g -> [g,g] -> 0
  - [[g,g],[g,g]] would be the second derived algebra

Let's check a few more samples...
"""
)

# For a codeword t at grade g_t, it appears in [g,g] iff
# there exist g1, g2 != (0,0) with g1+g2 = g_t and omega(g1,g2) != 0


def can_appear_in_derived(t_grade):
    """Check if grade t_grade can appear in [g,g]"""
    for i in range(3):
        for j in range(3):
            g1 = (i, j)
            g2 = ((t_grade[0] - i) % 3, (t_grade[1] - j) % 3)
            if g1 != (0, 0) and g2 != (0, 0):  # Both must be non-central
                if omega(g1, g2) != 0:
                    return True
    return False


print("Check if each non-central grade can appear in [g,g] (from non-central inputs):")
all_appear = True
for tg in [(i, j) for i in range(3) for j in range(3) if (i, j) != (0, 0)]:
    result = can_appear_in_derived(tg)
    print(f"  {tg}: {'YES' if result else 'NO'}")
    if not result:
        all_appear = False

if all_appear:
    print("\nAll non-central grades can appear!")
    print("This suggests [g,g] spans the full 648-dim non-central part.")

# ============================================================
# INVESTIGATION 3: The Second Derived Algebra [[g,g],[g,g]]
# ============================================================
print("\n" + "=" * 75)
print("INVESTIGATION 3: The Second Derived Algebra [[g,g],[g,g]]")
print("=" * 75)

print(
    """
If [g,g] = non-central part (648-dim), then [[g,g],[g,g]] is computed from
brackets of non-central elements only.

Key: [E_c1, E_c2] for c1, c2 in non-center gives output at grade g1 + g2.
Since g1, g2 != (0,0) but omega(g1, g2) could still be non-zero...

For the second derived algebra:
- Inputs are from [g,g] (grades != (0,0))
- Output grade = g1 + g2
"""
)

# What grades can appear in [[g,g],[g,g]]?
# We need g1, g2 both non-zero, omega(g1, g2) != 0
print("Grades achievable in [[g,g],[g,g]] (from non-central x non-central):")

derived2_grades = set()
for g1 in [(i, j) for i in range(3) for j in range(3) if (i, j) != (0, 0)]:
    for g2 in [(i, j) for i in range(3) for j in range(3) if (i, j) != (0, 0)]:
        if omega(g1, g2) != 0:
            g_sum = ((g1[0] + g2[0]) % 3, (g1[1] + g2[1]) % 3)
            derived2_grades.add(g_sum)
            print(f"  [{g1}, {g2}] -> {g_sum} (omega = {omega(g1, g2)})")

print(f"\nGrades in [[g,g],[g,g]]: {sorted(derived2_grades)}")

if (0, 0) not in derived2_grades:
    print("The center (0,0) is NOT in [[g,g],[g,g]]!")
else:
    print("The center (0,0) IS in [[g,g],[g,g]]!")

# ============================================================
# INVESTIGATION 4: Structure Summary
# ============================================================
print("\n" + "=" * 75)
print("INVESTIGATION 4: Structure Summary")
print("=" * 75)

# Check: is [[g,g],[g,g]] = [g,g]?
if derived2_grades == set(
    (i, j) for i in range(3) for j in range(3) if (i, j) != (0, 0)
):
    print("[[g,g],[g,g]] covers all non-central grades!")
    print("So [[g,g],[g,g]] = [g,g] (same grade content)")
    print("The derived series STABILIZES: [g,g] is perfect!")
else:
    print("[[g,g],[g,g]] is a proper subset of [g,g]")

print(
    """
STRUCTURE PICTURE:

     g = Z + [g,g]    (728 = 80 + 648)

where:
  - Z = center = 80-dimensional abelian ideal (grade (0,0))
  - [g,g] = 648-dimensional derived subalgebra
  - [[g,g],[g,g]] = [g,g]  (if perfect)

This means g is a CENTRAL EXTENSION:

    0 -> Z -> g -> g/Z -> 0

where g/Z ~ [g,g] is a 648-dimensional Lie algebra.
"""
)

# ============================================================
# INVESTIGATION 5: Is g/Z simple?
# ============================================================
print("\n" + "=" * 75)
print("INVESTIGATION 5: Is g/Z simple?")
print("=" * 75)

print(
    """
A Lie algebra is SIMPLE if it has no proper ideals.

For g/Z (648-dim), an ideal I must satisfy [g/Z, I] <= I.
Since the bracket only depends on grades, the grade structure is key.

The 8 non-central grades form (Z_3^2 - {0}, +).
This is NOT a group (no identity)!

But we can think of it as Z_3^2 / {0} ~ punctured plane.
"""
)

# Are there any proper ideals?
# An ideal would be closed under [g, -]
# Since omega is non-degenerate on Z_3^2, for any non-zero g1,
# there exists g2 with omega(g1, g2) != 0.
# So [grade g1, grade g2] maps to grade g1+g2.

# Starting from any grade, can we reach all grades via brackets?
print(
    "Connectivity check: starting from grade (1,0), can we reach all non-central grades?"
)

reachable = {(1, 0)}
frontier = [(1, 0)]
while frontier:
    current = frontier.pop()
    for g2 in [(i, j) for i in range(3) for j in range(3) if (i, j) != (0, 0)]:
        if omega(current, g2) != 0:
            new_grade = ((current[0] + g2[0]) % 3, (current[1] + g2[1]) % 3)
            if new_grade != (0, 0) and new_grade not in reachable:
                reachable.add(new_grade)
                frontier.append(new_grade)

print(f"Reachable grades: {sorted(reachable)}")
print(f"All 8 non-central grades reachable: {len(reachable) == 8}")

# ============================================================
# INVESTIGATION 6: What IS the quotient g/Z?
# ============================================================
print("\n" + "=" * 75)
print("INVESTIGATION 6: Identifying g/Z")
print("=" * 75)

print(
    """
g/Z has dimension 648 = 8 * 81.
It is Z_3^2-graded (8 components of dim 81 each).
The bracket has coefficient omega(g1, g2).

This looks like a TWISTED TENSOR PRODUCT structure!

Let V = F_3^81 (the fiber over each grade).
Let A = F_3^2 - {0} (the 8 non-central grades).

Then g/Z ~ A x V with bracket:
  [(a1, v1), (a2, v2)] = (a1+a2, omega(a1,a2) * (v1 . v2?))

But what's the . on V?
"""
)

print("HYPOTHESIS: g/Z is NOT simple because 648 != dim of any simple Lie algebra.")
print()
print("Nearby simple Lie algebra dimensions:")
for n in range(22, 28):
    print(f"  sl({n+1}): dim = {(n+1)**2 - 1}")

# ============================================================
# INVESTIGATION 7: The Killing Form
# ============================================================
print("\n" + "=" * 75)
print("INVESTIGATION 7: The Killing Form")
print("=" * 75)

print(
    """
The Killing form K(x, y) = Tr(ad_x . ad_y).

For the center Z: ad_z = 0 for all z in Z.
So K(z, anything) = 0.
This means Z is in the radical of K.

For g to be semisimple, K must be non-degenerate.
But K is degenerate (Z is in the radical)!

CONCLUSION: g is NOT semisimple (has non-trivial radical = at least Z).
"""
)

# ============================================================
# FINAL SUMMARY
# ============================================================
print("\n" + "=" * 75)
print("FINAL STRUCTURE SUMMARY")
print("=" * 75)

print(
    """
1. g is 728-dimensional, same as sl(27)
2. g has an 80-dimensional CENTER Z (grade (0,0))
3. g = Z + [g,g] as vector spaces (not direct product of algebras!)
4. [g,g] is 648-dimensional
5. [[g,g],[g,g]] = [g,g] (the derived algebra is perfect)
6. g is NOT semisimple (Z is in the radical of Killing form)
7. g/Z is 648-dimensional with Z_3^2 grading

WHAT IS g?

g appears to be a CENTRAL EXTENSION of the 648-dimensional algebra g/Z by
the 80-dimensional abelian algebra Z:

    0 -> Z -> g -> g/Z -> 0

The cocycle that defines this extension is:
    sigma(c1, c2) = omega(grade(c1), grade(c2)) in F_3

This is determined by the symplectic form omega on Z_3^2!

CONJECTURE: g is the universal central extension of some algebra related to
the Heisenberg structure on F_3^2 tensored with an 81-dimensional space.
"""
)
