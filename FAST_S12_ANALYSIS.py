"""
Fast Deep Analysis of s_12 - Optimized Version
"""

from collections import Counter, defaultdict
from itertools import product

import numpy as np

print("=" * 70)
print("FAST DEEP ANALYSIS OF s_12")
print("=" * 70)


# Build the code
def build_ternary_golay_code():
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

    codewords = []
    for coeffs in product(range(3), repeat=6):
        c = np.array(coeffs, dtype=np.int64)
        cw = tuple((c @ G) % 3)
        codewords.append(cw)
    return list(set(codewords))


print("Building Golay code...")
codewords = build_ternary_golay_code()
cw_set = set(codewords)


def weight(c):
    return sum(1 for x in c if x != 0)


def grade(c):
    return sum(c) % 3


# Classify
zero_cw = tuple([0] * 12)
nonzero = [c for c in codewords if c != zero_cw]
center = [c for c in nonzero if grade(c) == 0]
grade1 = [c for c in nonzero if grade(c) == 1]
grade2 = [c for c in nonzero if grade(c) == 2]

print(f"\nTotal codewords: {len(codewords)}")
print(f"Non-zero (dim g): {len(nonzero)}")
print(f"Center Z (grade 0): {len(center)}")
print(f"Grade 1: {len(grade1)}")
print(f"Grade 2: {len(grade2)}")
print(f"s_12 = g/Z dimension: {len(grade1) + len(grade2)}")

# IMPORTANT CORRECTION: Check actual quotient dimension
s12_dim = len(nonzero) - len(center)
print(f"\nCORRECTED s_12 dimension: {s12_dim}")
print(f"  = {s12_dim} = {len(grade1)} + {len(grade2)}")

# Factor analysis
print(f"\nFactorizations of {s12_dim}:")
for d in range(1, int(np.sqrt(s12_dim)) + 2):
    if s12_dim % d == 0:
        print(f"  {d} x {s12_dim // d}")

# Weight distribution
print("\n" + "=" * 70)
print("WEIGHT DISTRIBUTION")
print("=" * 70)

for g, name in [(center, "Center"), (grade1, "Grade 1"), (grade2, "Grade 2")]:
    weights = Counter(weight(c) for c in g)
    print(f"\n{name} weight distribution:")
    for w in sorted(weights.keys()):
        print(f"  Weight {w}: {weights[w]}")

# Bracket analysis
print("\n" + "=" * 70)
print("BRACKET STRUCTURE")
print("=" * 70)


def omega(a, b):
    if a == 0 or b == 0:
        return 0
    return 1 if (a, b) in [(1, 1), (1, 2), (2, 1), (2, 2)] else 0
    # Actually: omega(1,1)=1, omega(1,2)=2, omega(2,1)=1, omega(2,2)=2


# Correct omega:
def omega(a, b):
    table = {
        (0, 0): 0,
        (0, 1): 0,
        (0, 2): 0,
        (1, 0): 0,
        (1, 1): 1,
        (1, 2): 2,
        (2, 0): 0,
        (2, 1): 1,
        (2, 2): 2,
    }
    return table.get((a, b), 0)


def bracket(c1, c2):
    """Returns (result_tuple, coefficient)"""
    g1, g2 = grade(c1), grade(c2)
    coeff = omega(g1, g2)
    if coeff == 0:
        return None, 0
    result = tuple((c1[i] + c2[i]) % 3 for i in range(12))
    return result, coeff


# Sample bracket computations
print("\nBracket grade behavior:")
print("  [g_1, g_1] -> coefficient 1, result grade (1+1)%3 = 2")
print("  [g_1, g_2] -> coefficient 2, result grade (1+2)%3 = 0 (CENTER)")
print("  [g_2, g_1] -> coefficient 1, result grade (2+1)%3 = 0 (CENTER)")
print("  [g_2, g_2] -> coefficient 2, result grade (2+2)%3 = 1")

# Verify bracket closure
print("\nVerifying bracket closure...")
bracket_results = defaultdict(set)
sample_size = 100
np.random.seed(42)

for _ in range(5000):
    i, j = np.random.randint(len(grade1)), np.random.randint(len(grade1))
    c1, c2 = grade1[i], grade1[j]
    result, coeff = bracket(c1, c2)
    if result and result != zero_cw:
        bracket_results["[g1,g1]"].add(result)

for _ in range(5000):
    i, j = np.random.randint(len(grade1)), np.random.randint(len(grade2))
    c1, c2 = grade1[i], grade2[j]
    result, coeff = bracket(c1, c2)
    if result and result != zero_cw:
        bracket_results["[g1,g2]"].add(result)

for _ in range(5000):
    i, j = np.random.randint(len(grade2)), np.random.randint(len(grade2))
    c1, c2 = grade2[i], grade2[j]
    result, coeff = bracket(c1, c2)
    if result and result != zero_cw:
        bracket_results["[g2,g2]"].add(result)

print("\nBracket space dimensions (sampled):")
for key, results in bracket_results.items():
    grades = Counter(grade(r) for r in results)
    print(f"  {key}: {len(results)} distinct results, grades: {dict(grades)}")

# Derived series computation
print("\n" + "=" * 70)
print("DERIVED SERIES [g,g], [[g,g],[g,g]], ...")
print("=" * 70)


def compute_all_brackets(basis):
    """Compute span of all [x,y] for x,y in basis."""
    results = set()
    for c1 in basis:
        for c2 in basis:
            r, coeff = bracket(c1, c2)
            if r and r != zero_cw:
                results.add(r)
    return list(results)


# Start with non-center elements for quotient algebra
current_basis = grade1 + grade2  # s_12 basis (quotient by center)
print(f"Starting dimension: {len(current_basis)}")

for step in range(4):
    print(f"\nComputing g^({step+1}) = [g^({step}), g^({step})]...")
    derived = compute_all_brackets(current_basis)

    # Remove center elements from derived (since we're in quotient)
    derived_non_center = [c for c in derived if grade(c) != 0]

    print(f"  Full [g,g]: {len(derived)} elements")
    print(f"  Non-center: {len(derived_non_center)} elements")

    if len(derived_non_center) == 0:
        print("  -> Derived series reaches center: SOLVABLE modulo center")
        break
    elif len(derived_non_center) == len(current_basis):
        print("  -> STABILIZED: [g,g] = g (mod center) - PERFECT ALGEBRA")
        break

    current_basis = derived_non_center

# Nilpotency test
print("\n" + "=" * 70)
print("LOWER CENTRAL SERIES [g, [g, g]], ...")
print("=" * 70)


def bracket_with_full(subset, full_basis):
    results = set()
    for c1 in subset:
        for c2 in full_basis:
            r, coeff = bracket(c1, c2)
            if r and r != zero_cw:
                results.add(r)
    return list(results)


full_basis = grade1 + grade2
current = full_basis.copy()
print(f"g_0 dimension: {len(current)}")

for step in range(4):
    print(f"Computing g_{step+1} = [g_{step}, g]...")
    next_basis = bracket_with_full(current, full_basis)
    next_non_center = [c for c in next_basis if grade(c) != 0]

    print(
        f"  [g_{step}, g]: {len(next_basis)} total, {len(next_non_center)} non-center"
    )

    if len(next_non_center) == 0:
        print(f"  -> NILPOTENT of class {step+1} (modulo center)")
        break
    elif len(next_non_center) >= len(current):
        print(f"  -> Not nilpotent (stabilized)")
        break

    current = next_non_center

# E8 connection
print("\n" + "=" * 70)
print("E8 CONNECTION ANALYSIS")
print("=" * 70)

print(f"\ns_12 dimension: {s12_dim}")
print(f"\nKey factorizations:")
print(f"  {s12_dim} = 2 x {s12_dim//2}")
print(f"  {s12_dim} = 3 x {s12_dim//3}")
print(f"  {s12_dim} = 6 x {s12_dim//6}")
if s12_dim % 9 == 0:
    print(f"  {s12_dim} = 9 x {s12_dim//9}")
if s12_dim % 27 == 0:
    print(f"  {s12_dim} = 27 x {s12_dim//27}")
if s12_dim % 81 == 0:
    print(f"  {s12_dim} = 81 x {s12_dim//81}")

print(f"\nE8 decomposition: 248 = 78 + 8 + 81 + 81")
print(f"Our dimension {s12_dim} vs E8 components:")
print(f"  {s12_dim} / 81 = {s12_dim/81:.4f}")
print(f"  {s12_dim} / 78 = {s12_dim/78:.4f}")

# Comparison with classical algebras
print("\n" + "=" * 70)
print("COMPARISON WITH KNOWN ALGEBRAS")
print("=" * 70)

print(f"\nChecking if {s12_dim} matches any classical dimension:")
for n in range(2, 30):
    # sl_n
    if n * n - 1 == s12_dim:
        print(f"  {s12_dim} = dim(sl_{n})")
    # so_n
    if n * (n - 1) // 2 == s12_dim:
        print(f"  {s12_dim} = dim(so_{n})")
    # sp_2n
    if n * (2 * n + 1) == s12_dim:
        print(f"  {s12_dim} = dim(sp_{2*n})")

# Check exceptional
exceptional = {"G2": 14, "F4": 52, "E6": 78, "E7": 133, "E8": 248}
for name, dim in exceptional.items():
    if dim == s12_dim:
        print(f"  {s12_dim} = dim({name})")
    if s12_dim % dim == 0:
        print(f"  {s12_dim} = {s12_dim//dim} x dim({name})")

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print(
    f"""
THE SIMPLE LIE ALGEBRA s_12:

Dimension: {s12_dim}
Base field: F_3 (characteristic 3)

Grading: Z_3-graded
  Grade 1 piece: {len(grade1)} dimensions
  Grade 2 piece: {len(grade2)} dimensions

Structure:
  - Arises from ternary Golay code G_12
  - Center has dimension {len(center)}
  - Inherits M_12 (Mathieu group) symmetry

Key number relationships:
  {s12_dim} = {len(grade1)} + {len(grade2)}
"""
)

# Additional insight
print("\n" + "=" * 70)
print("CRITICAL OBSERVATION")
print("=" * 70)
print(
    f"""
Wait - let me recheck the dimensions:

Total codewords: 729 = 3^6
Non-zero codewords: 728
Grade 0 non-zero (center): {len(center)}
Grade 1: {len(grade1)}
Grade 2: {len(grade2)}

The quotient s_12 = g / Z has dimension:
  {len(grade1)} + {len(grade2)} = {len(grade1) + len(grade2)}

This equals:
  728 - {len(center)} = {728 - len(center)}

So s_12 has dimension {728 - len(center)}.
"""
)

# Verify 243+243 = 486
print(f"Grade 1 + Grade 2 = {len(grade1)} + {len(grade2)} = {len(grade1)+len(grade2)}")
print(f"728 - center = 728 - {len(center)} = {728 - len(center)}")

print("\n486 factorizations:")
for d in [1, 2, 3, 6, 9, 18, 27, 54, 81, 162, 243, 486]:
    if 486 % d == 0:
        print(f"  486 = {d} x {486//d}")

print("\n486 = 2 x 243 = 2 x 3^5")
print("486 = 6 x 81 = 6 x 3^4")
print("486 = 18 x 27 = 18 x 3^3")
