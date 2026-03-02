"""
THE_TWELVE_GENERATORS.py - Explicit Construction

KEY FACTS:
  - 729 = 3^6 codewords = 27² matrices
  - The 12 positions generate a 6-dim code
  - The 6-dim code must act on 27-dim space
  - 27 = 3³ = AG(3,3) points
  - The action is through LINES in AG(3,3)

CONSTRUCTION:
  Each of 12 positions → one of 12 special "direction operators"
  These operators act on the 27-point space AG(3,3)
"""

from collections import Counter, defaultdict
from itertools import combinations, product

import numpy as np

print("=" * 80)
print("CONSTRUCTING THE TWELVE GENERATORS")
print("=" * 80)

# ============================================================================
print("\n" + "=" * 80)
print("PART 1: The 27-Dimensional Space")
print("=" * 80)

# AG(3,3) points as basis
points = [(a, b, c) for a in range(3) for b in range(3) for c in range(3)]
point_to_idx = {p: i for i, p in enumerate(points)}

print(f"27 basis vectors: e_{{(a,b,c)}} for (a,b,c) ∈ GF(3)³")

# ============================================================================
print("\n" + "=" * 80)
print("PART 2: Shift Operators")
print("=" * 80)

print(
    """
Define SHIFT OPERATORS T_d for each direction d:
  T_d : e_P → e_{P+d}  (translation by d)

These act on the 27-dim space and generate a group.

For d ∈ GF(3)³ with d ≠ 0:
  T_d has matrix entries: T_d[i,j] = 1 if P_j + d = P_i

The shift operators satisfy: T_d · T_{d'} = T_{d+d'}
So shifts form an ABELIAN group (Z/3Z)³.
"""
)


def shift_matrix(d):
    """Construct the shift matrix T_d."""
    M = np.zeros((27, 27), dtype=int)
    for j, P in enumerate(points):
        P_shifted = tuple((P[k] + d[k]) % 3 for k in range(3))
        i = point_to_idx[P_shifted]
        M[i, j] = 1
    return M


# Compute all shift matrices
shifts = {}
for d in product(range(3), repeat=3):
    if d != (0, 0, 0):
        shifts[d] = shift_matrix(d)

print(f"Number of non-trivial shifts: {len(shifts)}")

# ============================================================================
print("\n" + "=" * 80)
print("PART 3: From Shifts to sl(27)")
print("=" * 80)

print(
    """
The shifts T_d are PERMUTATION matrices (orthogonal).
To get elements of sl(27), we need:
  1. Traceless: Tr(A) = 0
  2. Not just permutations - need linear combinations

IDEA: Take DIFFERENCES of shifts!
  A_d = T_d - I (has trace 27 - 27 = 0? No... T_d has trace = #{fixed points})

For d ≠ 0, T_d has NO fixed points (P + d ≠ P when d ≠ 0).
So Tr(T_d) = 0 already!

The shift matrices T_d with d ≠ 0 are already traceless!
They lie in sl(27)!
"""
)

# Verify tracelessness
for d in list(shifts.keys())[:3]:
    T = shifts[d]
    print(f"  Tr(T_{{{d}}}) = {np.trace(T)}")

# ============================================================================
print("\n" + "=" * 80)
print("PART 4: The 26 Non-Trivial Shifts")
print("=" * 80)

print(
    """
We have 26 = 3³ - 1 non-trivial directions.
Each gives a traceless matrix in sl(27).

But: We need 12 generators, not 26!

REDUCTION: The directions come in opposite pairs: d and -d = 2d.
  T_d and T_{2d} are related: T_{2d} = T_d⁻¹ = T_d² (since T_d³ = I)

So: 26/2 = 13 independent directions (projective).

We need to pick 12 of these 13!
"""
)

# Build projective directions
proj_directions = []
seen = set()
for d in product(range(3), repeat=3):
    if d == (0, 0, 0):
        continue
    # Normalize: d and 2d are equivalent
    d_neg = tuple((3 - d[k]) % 3 if d[k] != 0 else 0 for k in range(3))
    key = min(d, d_neg)
    if key not in seen:
        seen.add(key)
        proj_directions.append(d)

print(f"Projective directions: {len(proj_directions)}")
for i, d in enumerate(proj_directions):
    print(f"  D{i}: {d}")

# ============================================================================
print("\n" + "=" * 80)
print("PART 5: The Special Direction")
print("=" * 80)

print(
    """
We have 13 projective directions but need 12 positions.
One direction must be OMITTED.

Which one? It should be "special" in some sense.

CANDIDATE: The "all-ones" direction (1,1,1).
This is the unique direction fixed by the permutation (abc) → (bca).

If we omit (1,1,1), the remaining 12 directions are:
  - 3 "axis" directions: (1,0,0), (0,1,0), (0,0,1)
  - 9 "mixed" directions
"""
)

# Check which direction to omit
all_ones = (1, 1, 1)
print(f"\nThe 'all-ones' direction: {all_ones}")

# Remove (1,1,1) to get 12 directions
directions_12 = [d for d in proj_directions if d != all_ones]
print(f"Remaining 12 directions after omitting (1,1,1): {len(directions_12)}")

# ============================================================================
print("\n" + "=" * 80)
print("PART 6: The 12 Generator Matrices")
print("=" * 80)

print(
    """
The 12 generators are: B_i = T_{d_i} for i = 0, ..., 11
where d_0, ..., d_{11} are the 12 chosen directions.

Let's verify these generate a structure compatible with
the ternary Golay code!
"""
)

# Build the 12 generator matrices
generators = [shifts[d] for d in directions_12]

print(f"\nGenerator matrices B_0, ..., B_{{11}}:")
for i, d in enumerate(directions_12):
    print(f"  B{i} = T_{d}")

# ============================================================================
print("\n" + "=" * 80)
print("PART 7: Commutators")
print("=" * 80)

print(
    """
The Lie bracket in sl(27) is the commutator:
  [A, B] = AB - BA

For shift matrices:
  [T_d, T_{d'}] = T_d · T_{d'} - T_{d'} · T_d
                = T_{d+d'} - T_{d'+d}
                = T_{d+d'} - T_{d+d'} = 0!

WAIT - shifts COMMUTE! So [T_d, T_{d'}] = 0 for all d, d'.

This means the 12 shifts span an ABELIAN subalgebra!
That's not what we want for a full Lie algebra structure.

We need to modify the construction!
"""
)

# Verify commutation
T1, T2 = generators[0], generators[1]
comm = T1 @ T2 - T2 @ T1
print(f"[B0, B1] = 0? {np.allclose(comm, 0)}")

# ============================================================================
print("\n" + "=" * 80)
print("PART 8: Enhanced Generators - Diagonal + Shift")
print("=" * 80)

print(
    """
NEW IDEA: Combine DIAGONAL and SHIFT parts.

Define: B_d = D_d + ω · T_d

where:
  - D_d is a diagonal matrix depending on d
  - ω is a primitive cube root of unity (in GF(3): ω = 1)
  - T_d is the shift

For the diagonal part:
  D_d[P, P] = some function of P and d

A natural choice: D_d[P, P] = <P, d> = P·d (dot product mod 3)

This gives a CHARACTER of the shift action!
"""
)


def enhanced_generator(d):
    """Build enhanced generator D_d + T_d where D_d is diagonal."""
    M = np.zeros((27, 27), dtype=int)
    for j, P in enumerate(points):
        # Diagonal part: coefficient based on dot product
        diag_val = sum(P[k] * d[k] for k in range(3)) % 3
        M[j, j] = diag_val

        # Shift part
        P_shifted = tuple((P[k] + d[k]) % 3 for k in range(3))
        i = point_to_idx[P_shifted]
        M[i, j] = (M[i, j] + 1) % 3

    return M


# Build enhanced generators
enh_generators = [enhanced_generator(d) for d in directions_12]

# Check commutator
E0, E1 = enh_generators[0], enh_generators[1]
comm = (E0 @ E1 - E1 @ E0) % 3
print(f"\n[E0, E1] = 0? {np.allclose(comm, 0)}")
print(f"[E0, E1] non-zero entries: {np.count_nonzero(comm)}")

# ============================================================================
print("\n" + "=" * 80)
print("PART 9: The Heisenberg-Weyl Approach")
print("=" * 80)

print(
    """
The WEYL-HEISENBERG construction for finite fields:

Define operators on C^{27} (or (Z/3Z)^{27}):
  X_d : |P> → |P + d>  (translation)
  Z_a : |P> → ω^{<a,P>} |P>  (phase by character)

where ω = e^{2πi/3} (or just use GF(3) arithmetic).

The commutation relation is:
  X_d · Z_a = ω^{<a,d>} · Z_a · X_d

This is the FINITE HEISENBERG GROUP!

For our purposes:
  Generator B_{(a,d)} = Z_a · X_d  (combined)

The bracket structure depends on the pairing <a, d>.
"""
)

# ============================================================================
print("\n" + "=" * 80)
print("PART 10: GF(3) Weyl Matrices")
print("=" * 80)


def weyl_matrix(a, d):
    """
    Weyl matrix Z_a X_d acting on GF(3)^27.
    Z_a : |P> -> omega^{<a,P>} |P>
    X_d : |P> -> |P + d>
    Combined: |P> -> omega^{<a,P>} |P + d>

    We use GF(3) arithmetic, so omega = 1 (trivial phase).
    More properly, we should track phases, but let's first
    see the structure.
    """
    M = np.zeros((27, 27), dtype=int)
    for j, P in enumerate(points):
        # Phase from Z_a
        phase = sum(a[k] * P[k] for k in range(3)) % 3
        # Target from X_d
        P_shifted = tuple((P[k] + d[k]) % 3 for k in range(3))
        i = point_to_idx[P_shifted]
        # Matrix entry (in GF(3), phase is 0,1,2 corresponding to 1,ω,ω²)
        M[i, j] = (1 + phase) % 3 if phase != 0 else 1
    return M


# Test some Weyl matrices
W00_10 = weyl_matrix((0, 0, 0), (1, 0, 0))  # Pure shift
W10_00 = weyl_matrix((1, 0, 0), (0, 0, 0))  # Pure phase
W10_01 = weyl_matrix((1, 0, 0), (0, 1, 0))  # Mixed

print("Testing Weyl matrices:")
print(f"  W((0,0,0), (1,0,0)) trace: {np.trace(W00_10)}")
print(f"  W((1,0,0), (0,0,0)) trace: {np.trace(W10_00)}")

# ============================================================================
print("\n" + "=" * 80)
print("PART 11: The Codeword-to-Matrix Map")
print("=" * 80)

print(
    """
HYPOTHESIS: The 12 Golay positions correspond to 12 specific
Weyl matrices W(a_i, d_i).

A codeword c = (c_0, ..., c_{11}) maps to:
  M_c = Σ c_i · W(a_i, d_i)  (mod 3)

The key is finding the right (a_i, d_i) pairs!

CONSTRAINT: The hexad bracket must match matrix commutator.
This constrains the symplectic form <(a,d), (a',d')> = <a,d'> - <a',d>.
"""
)

# ============================================================================
print("\n" + "=" * 80)
print("PART 12: Counting Degrees of Freedom")
print("=" * 80)

print(
    """
The Weyl group has (3³)² = 729 elements: (a, d) pairs.
We need to choose 12 of these.

Constraints:
  1. The 12 should generate a structure matching the Golay code.
  2. The bracket structure must match the hexad combinatorics.

The Golay code is a 6-dim subspace of GF(3)^12.
We need the 12 Weyl matrices to span a 728-dim subspace of sl(27).

This is possible because:
  - 12 generators
  - Each generator has 27² - 1 = 728 degrees of freedom in sl(27)
  - Commutators fill in the rest

The exact matching to hexads requires careful choice of the 12 pairs!
"""
)

# ============================================================================
print("\n" + "=" * 80)
print("PART 13: The Symplectic Structure")
print("=" * 80)

print(
    """
The Weyl group has a natural SYMPLECTIC form:
  σ((a,d), (a',d')) = <a, d'> - <a', d>  (mod 3)

Two Weyl operators W(a,d) and W(a',d') satisfy:
  [W(a,d), W(a',d')] ~ ω^σ · W(a+a', d+d')

The bracket is NON-ZERO when σ((a,d), (a',d')) ≠ 0!

For the hexad structure:
  - |H1 ∩ H2| = 3 corresponds to σ ≠ 0 (non-commuting)
  - |H1 ∩ H2| ≠ 3 corresponds to σ = 0 (commuting)

Let's check if this matches!
"""
)

# ============================================================================
print("\n" + "=" * 80)
print("SYNTHESIS: The Structure Theorem")
print("=" * 80)

print(
    """
THE EMERGING STRUCTURE:

1. The 728 non-zero ternary Golay codewords parametrize
   a basis for sl(27) via the Weyl construction.

2. Each codeword c = (c_0, ..., c_{11}) maps to:
   M_c = Σ c_i W(a_i, d_i)

   where (a_0, d_0), ..., (a_{11}, d_{11}) are 12 specific
   points in the symplectic space GF(3)³ × GF(3)³.

3. The hexad bracket [c1, c2] on |H1 ∩ H2| = 3 corresponds to:
   [M_{c1}, M_{c2}] in sl(27)

   with the symplectic form encoding the intersection structure.

4. The Steiner system S(5,6,12) is encoded by:
   The 12 points {(a_i, d_i)} forming a special configuration
   such that "hexad" 6-subsets give non-trivial commutators.

5. The exceptional structures (E₆, J₃(O), etc.) arise because:
   This special 12-point configuration is UNIQUE up to symplectic
   automorphism, and relates to the exceptional Lie algebras.

THE FINAL PIECE:
Find the explicit 12 pairs (a_i, d_i) that make this work!
"""
)

# ============================================================================
print("\n" + "=" * 80)
print("VERIFICATION ATTEMPT")
print("=" * 80)

# Try a simple configuration: 12 = 6 + 6 (a-space and d-space)
# Let's use: 6 pure shifts + 6 pure phases

pure_shifts = [
    ((0, 0, 0), (1, 0, 0)),
    ((0, 0, 0), (0, 1, 0)),
    ((0, 0, 0), (0, 0, 1)),
    ((0, 0, 0), (1, 1, 0)),
    ((0, 0, 0), (1, 0, 1)),
    ((0, 0, 0), (0, 1, 1)),
]

pure_phases = [
    ((1, 0, 0), (0, 0, 0)),
    ((0, 1, 0), (0, 0, 0)),
    ((0, 0, 1), (0, 0, 0)),
    ((1, 1, 0), (0, 0, 0)),
    ((1, 0, 1), (0, 0, 0)),
    ((0, 1, 1), (0, 0, 0)),
]

test_config = pure_shifts + pure_phases
print(f"Test configuration: {len(test_config)} pairs")

# Build matrices for this config
test_matrices = [weyl_matrix(a, d) for (a, d) in test_config]

# Check commutator structure
print(f"\nCommutator structure (σ values):")
sigma_matrix = np.zeros((12, 12), dtype=int)
for i, (a1, d1) in enumerate(test_config):
    for j, (a2, d2) in enumerate(test_config):
        sigma = (
            sum(a1[k] * d2[k] for k in range(3)) - sum(a2[k] * d1[k] for k in range(3))
        ) % 3
        sigma_matrix[i, j] = sigma

print("σ-matrix (mod 3):")
print(sigma_matrix)

# Count non-zero off-diagonal entries
nonzero_sigma = sum(
    1 for i in range(12) for j in range(12) if i < j and sigma_matrix[i, j] != 0
)
print(f"\nNon-zero σ pairs: {nonzero_sigma}")
print(f"Zero σ pairs: {66 - nonzero_sigma}")

# Compare to hexad structure: should have specific pattern
# Each position should have 40 non-commuting partners...
# but we only have 12 positions, so max is 11 per position
