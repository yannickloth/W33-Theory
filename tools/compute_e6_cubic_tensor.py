#!/usr/bin/env python3
"""
EXPLICIT E6 CUBIC TENSOR FROM OCTONIONIC ALBERT ALGEBRA

The exceptional Jordan algebra J₃(O) consists of 3×3 Hermitian matrices
over the octonions. This has dimension 27.

The determinant of such a matrix gives the CUBIC INVARIANT.

Key insight: E6 = SL(3,O) = determinant-preserving transformations

The cubic tensor C_abc is defined by:
  det(x) = (1/6) C_abc x^a x^b x^c

This script computes the explicit structure constants.
"""

from itertools import combinations, product
from math import sqrt

import numpy as np

print("=" * 80)
print("EXPLICIT E6 CUBIC TENSOR FROM OCTONIONIC ALBERT ALGEBRA")
print("=" * 80)

# ============================================================================
# PART 1: OCTONION ALGEBRA
# ============================================================================

print("\n" + "=" * 80)
print("1. OCTONION MULTIPLICATION TABLE")
print("=" * 80)

# Octonion basis: {1, e1, e2, e3, e4, e5, e6, e7}
# Multiplication: e_i * e_j = -δ_ij + ε_ijk e_k

# The Fano plane encodes the multiplication:
# Lines: {124}, {235}, {346}, {457}, {156}, {267}, {137}
# e_i * e_j = e_k if (i,j,k) is a cyclic line ordering

FANO_LINES = [
    (1, 2, 4),
    (2, 3, 5),
    (3, 4, 6),
    (4, 5, 7),
    (1, 5, 6),
    (2, 6, 7),
    (1, 3, 7),
]

# Build multiplication table
# e_i * e_j for i,j ∈ {1,...,7}
# Result is ±e_k for some k, or 0 if i=j (gives -1)


def octonion_mult_table():
    """
    Build the octonion multiplication table.
    Returns (real_part, imag_index, sign)
    """
    # mult[i][j] = (is_real, index, sign)
    # if is_real: result = sign * 1
    # else: result = sign * e_{index}

    mult = [[None for _ in range(8)] for _ in range(8)]

    # e_0 = 1 is the identity
    for j in range(8):
        mult[0][j] = (j == 0, j, 1)
        mult[j][0] = (j == 0, j, 1)

    # e_i * e_i = -1
    for i in range(1, 8):
        mult[i][i] = (True, 0, -1)

    # Use Fano plane for other products
    for line in FANO_LINES:
        a, b, c = line
        # e_a * e_b = e_c, e_b * e_c = e_a, e_c * e_a = e_b (cyclic)
        # e_b * e_a = -e_c, etc. (anti-cyclic)
        mult[a][b] = (False, c, 1)
        mult[b][a] = (False, c, -1)
        mult[b][c] = (False, a, 1)
        mult[c][b] = (False, a, -1)
        mult[c][a] = (False, b, 1)
        mult[a][c] = (False, b, -1)

    return mult


MULT_TABLE = octonion_mult_table()

# Verify: check a few products
print("Sample products:")
for i, j in [(1, 2), (2, 1), (3, 4), (1, 1)]:
    is_real, idx, sign = MULT_TABLE[i][j]
    if is_real:
        print(f"  e_{i} * e_{j} = {sign}")
    else:
        print(f"  e_{i} * e_{j} = {'+' if sign > 0 else '-'}e_{idx}")

# ============================================================================
# PART 2: 3×3 HERMITIAN OCTONIONIC MATRICES
# ============================================================================

print("\n" + "=" * 80)
print("2. HERMITIAN 3×3 OCTONIONIC MATRICES (27 dimensions)")
print("=" * 80)

# A general element of J₃(O) is:
#
#   | a    x̄    ȳ |
#   | x    b    z̄ |
#   | y    z    c |
#
# where a, b, c ∈ R (diagonal, real)
# and x, y, z ∈ O (off-diagonal, octonionic)
#
# Dimension: 3 (diagonal) + 3 × 8 (off-diagonal) = 3 + 24 = 27

# Index the 27 basis elements as:
# 0, 1, 2: diagonal (a, b, c)
# 3-10: x (8 octonion components)
# 11-18: y (8 octonion components)
# 19-26: z (8 octonion components)

BASIS_NAMES = (
    ["a", "b", "c"]
    + [f"x{i}" for i in range(8)]
    + [f"y{i}" for i in range(8)]
    + [f"z{i}" for i in range(8)]
)

print(f"27 basis elements: {BASIS_NAMES}")


def make_J3O_element(coeffs):
    """
    Given 27 real coefficients, construct the J₃(O) matrix.
    Returns a 3×3 array where each entry is an 8-tuple (octonion).
    """
    assert len(coeffs) == 27

    # Diagonal entries: real scalars (as octonions with only e_0 component)
    a = np.array([coeffs[0], 0, 0, 0, 0, 0, 0, 0], dtype=float)
    b = np.array([coeffs[1], 0, 0, 0, 0, 0, 0, 0], dtype=float)
    c = np.array([coeffs[2], 0, 0, 0, 0, 0, 0, 0], dtype=float)

    # Off-diagonal: octonions
    x = np.array(coeffs[3:11], dtype=float)
    y = np.array(coeffs[11:19], dtype=float)
    z = np.array(coeffs[19:27], dtype=float)

    # Conjugate: flip sign of imaginary parts
    def conj(o):
        return np.array([o[0]] + [-o[i] for i in range(1, 8)], dtype=float)

    # Build 3×3 matrix (each entry is 8-tuple)
    matrix = np.zeros((3, 3, 8), dtype=float)
    matrix[0, 0] = a
    matrix[1, 1] = b
    matrix[2, 2] = c
    matrix[0, 1] = conj(x)
    matrix[1, 0] = x
    matrix[0, 2] = conj(y)
    matrix[2, 0] = y
    matrix[1, 2] = conj(z)
    matrix[2, 1] = z

    return matrix


# ============================================================================
# PART 3: OCTONION MULTIPLICATION
# ============================================================================


def oct_mult(a, b):
    """Multiply two octonions a and b (each as 8-tuple)."""
    result = np.zeros(8, dtype=float)

    for i in range(8):
        for j in range(8):
            is_real, idx, sign = MULT_TABLE[i][j]
            if is_real:
                result[0] += sign * a[i] * b[j]
            else:
                result[idx] += sign * a[i] * b[j]

    return result


def oct_conj(a):
    """Conjugate of octonion."""
    return np.array([a[0]] + [-a[k] for k in range(1, 8)], dtype=float)


def oct_trace(a):
    """Real part (trace) of octonion."""
    return a[0]


# ============================================================================
# PART 4: DETERMINANT (CUBIC INVARIANT)
# ============================================================================

print("\n" + "=" * 80)
print("3. CUBIC INVARIANT: DETERMINANT")
print("=" * 80)

# For 3×3 Hermitian octonionic matrix M, the determinant is:
#
# det(M) = abc + 2Re(xyz) - a|z|² - b|y|² - c|x|²
#
# This is the CUBIC FORM on the 27-dimensional space.


def J3O_determinant(matrix):
    """
    Compute the determinant (cubic invariant) of a J₃(O) element.

    det = a*b*c + 2*Re(x*y*z) - a*|z|² - b*|y|² - c*|x|²
    """
    a = matrix[0, 0, 0]  # Real part of diagonal
    b = matrix[1, 1, 0]
    c = matrix[2, 2, 0]

    x = matrix[1, 0]  # Full octonion
    y = matrix[2, 0]
    z = matrix[2, 1]

    # |x|² = x * x̄ = Re part
    norm_sq_x = np.dot(x, x)  # Since conjugate flips sign of imag, |x|² = Σ x_i²
    norm_sq_y = np.dot(y, y)
    norm_sq_z = np.dot(z, z)

    # xyz term
    xy = oct_mult(x, y)
    xyz = oct_mult(xy, z)
    re_xyz = xyz[0]

    det = a * b * c + 2 * re_xyz - a * norm_sq_z - b * norm_sq_y - c * norm_sq_x

    return det


# Test with identity-like element
test_coeffs = [1, 1, 1] + [0] * 24
test_M = make_J3O_element(test_coeffs)
print(f"det(diag(1,1,1)) = {J3O_determinant(test_M):.4f} (should be 1)")

# ============================================================================
# PART 5: COMPUTE CUBIC TENSOR C_abc
# ============================================================================

print("\n" + "=" * 80)
print("4. COMPUTING CUBIC TENSOR C_{abc}")
print("=" * 80)

# The cubic tensor C_abc is defined by:
#   det(x) = (1/6) Σ_{a,b,c} C_abc x^a x^b x^c
#
# Equivalently, C is totally symmetric and:
#   C_abc = (∂³ det / ∂x^a ∂x^b ∂x^c)
#
# We can compute this by numerical differentiation.


def cubic_tensor_element(a, b, c, eps=1e-5):
    """
    Compute C_abc by numerical third derivative.
    """
    # det(x + ε_a e_a + ε_b e_b + ε_c e_c) expanded to third order
    # gives C_abc as coefficient of ε_a ε_b ε_c

    # Use centered differences for better accuracy
    result = 0.0

    for sa in [-1, 1]:
        for sb in [-1, 1]:
            for sc in [-1, 1]:
                coeffs = np.zeros(27)
                coeffs[a] += sa * eps
                coeffs[b] += sb * eps
                coeffs[c] += sc * eps

                M = make_J3O_element(coeffs)
                d = J3O_determinant(M)

                result += sa * sb * sc * d

    result /= 8 * eps**3
    return result


# Compute a subset of the tensor
print("\nComputing sample cubic tensor elements...")

# The tensor should be nonzero when (a,b,c) form a "triad"
# Triads come from the determinant formula:
# - (0,1,2) for abc term
# - (3+i, 11+j, 19+k) for xyz term (with specific Fano structure)
# - (0, 19+i, 19+j) for a|z|² term (when i=j)
# etc.

key_elements = [
    (0, 1, 2),  # abc term
    (0, 0, 1),  # Should be 0 (no aa term with b)
    (3, 11, 19),  # xyz term: x0 y0 z0
    (4, 12, 20),  # xyz term: x1 y1 z1
    (0, 19, 19),  # a z0 z0 term
]

print(f"\n{'(a,b,c)':<15} {'C_abc':<15}")
print("-" * 30)
for a, b, c in key_elements:
    C = cubic_tensor_element(a, b, c)
    print(f"{(a,b,c)!s:<15} {C:>12.4f}")

# ============================================================================
# PART 6: STRUCTURE OF THE 45 TRIADS
# ============================================================================

print("\n" + "=" * 80)
print("5. IDENTIFYING THE 45 CUBIC TRIADS")
print("=" * 80)

# A "triad" is a triple (a,b,c) where C_abc ≠ 0
# From the determinant formula, there are specific patterns.

# Count triads by scanning (expensive but thorough)
print("\nScanning for nonzero C_abc...")

nonzero_triads = []
for a in range(27):
    for b in range(a, 27):
        for c in range(b, 27):
            C = cubic_tensor_element(a, b, c, eps=1e-4)
            if abs(C) > 0.01:  # Threshold for numerical noise
                nonzero_triads.append((a, b, c, C))

print(f"\nFound {len(nonzero_triads)} nonzero triads:")
for a, b, c, C in nonzero_triads[:20]:
    print(f"  C[{BASIS_NAMES[a]},{BASIS_NAMES[b]},{BASIS_NAMES[c]}] = {C:.3f}")

if len(nonzero_triads) > 20:
    print(f"  ... and {len(nonzero_triads) - 20} more")

# ============================================================================
# PART 7: ANALYSIS
# ============================================================================

print("\n" + "=" * 80)
print("6. TRIAD ANALYSIS")
print("=" * 80)

# Categorize triads
diagonal_triads = [
    (a, b, c, C) for (a, b, c, C) in nonzero_triads if a < 3 and b < 3 and c < 3
]
mixed_triads = [
    (a, b, c, C) for (a, b, c, C) in nonzero_triads if min(a, b, c) < 3 < max(a, b, c)
]
off_diag_triads = [(a, b, c, C) for (a, b, c, C) in nonzero_triads if min(a, b, c) >= 3]

print(f"Diagonal triads (a,b,c in diagonal): {len(diagonal_triads)}")
print(f"Mixed triads: {len(mixed_triads)}")
print(f"Off-diagonal triads: {len(off_diag_triads)}")

# Save results
import json

results = {
    "total_triads": len(nonzero_triads),
    "diagonal_triads": len(diagonal_triads),
    "mixed_triads": len(mixed_triads),
    "off_diagonal_triads": len(off_diag_triads),
    "triads": [(int(a), int(b), int(c), float(C)) for (a, b, c, C) in nonzero_triads],
}

with open("artifacts/e6_cubic_tensor_analysis.json", "w") as f:
    json.dump(results, f, indent=2, default=str)

print("\nWrote artifacts/e6_cubic_tensor_analysis.json")

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

print(
    f"""
The E6 cubic tensor C_abc has been partially computed.

From the octonionic Albert algebra structure:
- det(M) = abc + 2Re(xyz) - a|z|² - b|y|² - c|x|²

This gives rise to triads:
- Diagonal: C[a,b,c] = 1 (one triad)
- Cross-norm: C[a,z_i,z_i] = -1, etc.
- Octonionic: C[x_i,y_j,z_k] ~ Re(e_i e_j e_k)

The 45 triads in our W33 model should correspond to specific
combinations derived from this structure.

NEXT: Map the W33 coordinate system to the J₃(O) basis
to verify the triad count and structure.
"""
)
