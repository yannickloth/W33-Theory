"""
QUTRIT QUANTUM MECHANICS AND THE THREE GENERATIONS
===================================================

The radical hypothesis: W33 is the "Pauli geometry" for 2 qutrits,
and the 3 generations emerge from the 3 eigenvalue sectors.
"""

import cmath
from collections import defaultdict
from itertools import product

import numpy as np

print("=" * 70)
print("PART 1: QUTRIT PAULI OPERATORS")
print("=" * 70)

# Qutrit computational basis
print(
    """
A qutrit has basis states |0⟩, |1⟩, |2⟩

The qutrit Pauli operators are:
  X (shift): X|j⟩ = |j+1 mod 3⟩
  Z (phase): Z|j⟩ = ω^j |j⟩  where ω = e^(2πi/3)

These satisfy: XZ = ωZX (non-commuting!)
"""
)

# Define omega
omega = cmath.exp(2j * cmath.pi / 3)
print(f"ω = e^(2πi/3) = {omega:.4f}")
print(f"ω³ = {omega**3:.4f} = 1")
print(f"1 + ω + ω² = {1 + omega + omega**2:.4f} = 0")

# Single qutrit Pauli group
print("\n--- Single Qutrit Pauli Group ---")
print("Elements: ω^k X^a Z^b for k,a,b ∈ {0,1,2}")
print(f"Order: 3 × 3 × 3 = 27")

# For two qutrits: X₁, X₂, Z₁, Z₂
print("\n--- Two Qutrit System ---")
print("Operators: X₁, X₂, Z₁, Z₂ (and products)")
print("Pauli group order: 3^5 = 243 (including phases)")
print("Projective Pauli group: 243/3 = 81 operators")

print("\n" + "=" * 70)
print("PART 2: MAXIMAL COMMUTING SETS (MCS)")
print("=" * 70)

print(
    """
A key structure in quantum information:
- Maximal Commuting Sets of Pauli operators
- For n qubits: MCS have 2^n - 1 = 2ⁿ - 1 elements
- For n qutrits: MCS have 3^n - 1 elements in projective group

For 2 qutrits:
- Projective Pauli group has 81 - 1 = 80 non-identity elements
- MCS have 3² - 1 = 8 elements each
- How many MCS are there?

The geometry of MCS is exactly the symplectic polar space W(2n-1, p)!
For 2 qutrits over GF(3): W(3,3) with 40 points!
"""
)

# The W33 connection
print("\n--- W33 as MCS Geometry ---")
print("Each vertex of W33 ↔ A maximal commuting set of Pauli operators")
print("Two vertices adjacent ↔ The MCS share a common Pauli operator")
print("40 vertices = 40 MCS = 40 measurement contexts")

# Let's verify this counting
print("\n--- Counting Verification ---")

# Generate projective Pauli operators for 2 qutrits
# An operator is X₁^a Z₁^b X₂^c Z₂^d (ignoring phase)
# This is a vector (a,b,c,d) ∈ GF(3)⁴

# Two operators commute iff their symplectic form vanishes
# [X₁^a Z₁^b, X₁^{a'} Z₁^{b'}] ∝ ω^{ab' - a'b}
# For 2 qutrits: form is ω^{a₁b₁' - a₁'b₁ + a₂b₂' - a₂'b₂}

# So: (a,b,c,d) and (a',b',c',d') commute iff
# ab' - a'b + cd' - c'd ≡ 0 (mod 3)

# This is exactly the symplectic form!


def symplectic(v, u):
    """Symplectic form for 2 qutrits"""
    a, b, c, d = v
    ap, bp, cp, dp = u
    return (a * bp - ap * b + c * dp - cp * d) % 3


# Generate all projective points (= projective Pauli operators)
gf3_4 = list(product([0, 1, 2], repeat=4))


def normalize(v):
    """Normalize to first nonzero = 1"""
    for i, x in enumerate(v):
        if x != 0:
            if x == 2:  # Multiply by 2 = inverse of 2 mod 3
                return tuple((2 * c) % 3 for c in v)
            return v
    return v


proj_paulis = set()
for v in gf3_4:
    if v != (0, 0, 0, 0):
        proj_paulis.add(normalize(v))

print(f"Projective Pauli operators: {len(proj_paulis)}")
print("(= 40 vertices of W33 ✓)")

# Find maximal totally isotropic subspaces (= MCS)
# These are the "lines" in projective terms, 4 points each

proj_list = list(proj_paulis)

# Build adjacency (commuting = adjacent in W33)
adj = defaultdict(set)
for i, v in enumerate(proj_list):
    for j, u in enumerate(proj_list):
        if i != j and symplectic(v, u) == 0:
            adj[i].add(j)

print(f"\nAdjacency built: each vertex has degree {len(adj[0])}")

# A maximal totally isotropic subspace (MCS) corresponds to
# a clique of size 4 in W33 (totally isotropic 2-space)

# Actually, let's think more carefully:
# - A t.i. 2-space has 3² = 9 vectors, 4 projective points
# - These 4 operators all mutually commute
# - This is a complete measurement context

# Find all 4-cliques
four_cliques = []
for i in range(len(proj_list)):
    ni = adj[i]
    for j in ni:
        if j > i:
            common = ni & adj[j]
            for k in common:
                if k > j:
                    for l in common & adj[k]:
                        if l > k:
                            four_cliques.append((i, j, k, l))

print(f"4-cliques (maximal commuting sets): {len(four_cliques)}")

print("\n" + "=" * 70)
print("PART 3: EIGENVALUE STRUCTURE AND GENERATIONS")
print("=" * 70)

print(
    """
Each projective Pauli operator has eigenvalues {1, ω, ω²}.

HYPOTHESIS: The three generations correspond to the three eigenvalue sectors!

Generation 1: Eigenstates with eigenvalue 1 (identity sector)
Generation 2: Eigenstates with eigenvalue ω (first excitation)
Generation 3: Eigenstates with eigenvalue ω² (second excitation)

Since ω³ = 1, this is naturally cyclic (Z₃ symmetry).
"""
)

# The eigenvalues of generalized Pauli operators
print("\n--- Eigenvalue Analysis ---")
print("Any Pauli operator P has eigenvalues {1, ω, ω²}")
print("Each with multiplicity 3 (for dimension 9)")
print("So: 9 = 3 + 3 + 3 (equal multiplicity)")

# For a measurement context (MCS of 4 operators):
# The 9 joint eigenstates split into groups

print("\n--- Joint Eigenstates ---")
print("A 4-clique defines a complete measurement context")
print("The 9 basis states are joint eigenstates")
print("Each state labeled by 4 eigenvalues in {1, ω, ω²}")
print("But with constraint: product of eigenvalues = 1 (since X^3 = Z^3 = I)")

# Actually for 2 qutrits, dimension is 3² = 9
# A commuting set of 8 operators would fully specify a basis
# But our 4-cliques have only 4 operators...

# Let's count eigenvalue patterns
print("\n--- Eigenvalue Patterns in GF(3) ---")
print("Mapping: eigenvalue 1 → 0, ω → 1, ω² → 2")
print("A joint eigenstate ↔ vector in GF(3)⁴")
print("This is EXACTLY the W33 vertex structure!")

print("\n" + "=" * 70)
print("PART 4: THE WEIGHT-MOD-3 PARTITION REVISITED")
print("=" * 70)

# Earlier we found: Weight 0: 13, Weight 1: 14, Weight 2: 13


def weight_mod3(v):
    return sum(v) % 3


weight_classes = defaultdict(list)
for v in proj_list:
    w = weight_mod3(v)
    weight_classes[w].append(v)

print("W33 vertices by weight (sum of coords mod 3):")
for w in [0, 1, 2]:
    count = len(weight_classes[w])
    print(f"  Weight {w}: {count} vertices")

print("\n13 + 14 + 13 = 40 ✓")
print("\nThis is ALMOST a perfect 3-way partition!")
print("The asymmetry (14 vs 13) might be physically meaningful...")

# Let's look at the 14 more carefully
print(f"\n--- The 14 vertices with weight 1 ---")
print("These might represent the 'first generation sector'")

weight1_verts = weight_classes[1]
print(f"Vertices: {weight1_verts[:5]}...")  # First few


# Check their positions - are they special?
# Count adjacencies between classes
def count_cross_edges(class1, class2, adj_dict, proj_list):
    count = 0
    idx1 = [proj_list.index(v) for v in class1]
    idx2 = [proj_list.index(v) for v in class2]
    for i in idx1:
        for j in idx2:
            if j in adj_dict[i]:
                count += 1
    return count // 2  # Each edge counted twice


# Cross-class adjacency analysis
print("\n--- Cross-class adjacency ---")
w0 = weight_classes[0]
w1 = weight_classes[1]
w2 = weight_classes[2]

# Edges within each class
within_0 = count_cross_edges(w0, w0, adj, proj_list)
within_1 = count_cross_edges(w1, w1, adj, proj_list)
within_2 = count_cross_edges(w2, w2, adj, proj_list)

# Actually let's count more carefully
adj_matrix = [[0] * 40 for _ in range(40)]
for i in range(40):
    for j in adj[i]:
        adj_matrix[i][j] = 1


def count_edges_in_set(vertices, adj_matrix, proj_list):
    indices = [proj_list.index(v) for v in vertices]
    count = 0
    for i in indices:
        for j in indices:
            if i < j and adj_matrix[i][j]:
                count += 1
    return count


print(
    f"Edges within weight-0 class (13 vertices): {count_edges_in_set(w0, adj_matrix, proj_list)}"
)
print(
    f"Edges within weight-1 class (14 vertices): {count_edges_in_set(w1, adj_matrix, proj_list)}"
)
print(
    f"Edges within weight-2 class (13 vertices): {count_edges_in_set(w2, adj_matrix, proj_list)}"
)


# Edges between classes
def count_edges_between(v1, v2, adj_matrix, proj_list):
    idx1 = [proj_list.index(v) for v in v1]
    idx2 = [proj_list.index(v) for v in v2]
    count = 0
    for i in idx1:
        for j in idx2:
            if adj_matrix[i][j]:
                count += 1
    return count


print(
    f"\nEdges between weight-0 and weight-1: {count_edges_between(w0, w1, adj_matrix, proj_list)}"
)
print(
    f"Edges between weight-0 and weight-2: {count_edges_between(w0, w2, adj_matrix, proj_list)}"
)
print(
    f"Edges between weight-1 and weight-2: {count_edges_between(w1, w2, adj_matrix, proj_list)}"
)

total_edges = (
    count_edges_in_set(w0, adj_matrix, proj_list)
    + count_edges_in_set(w1, adj_matrix, proj_list)
    + count_edges_in_set(w2, adj_matrix, proj_list)
    + count_edges_between(w0, w1, adj_matrix, proj_list)
    + count_edges_between(w0, w2, adj_matrix, proj_list)
    + count_edges_between(w1, w2, adj_matrix, proj_list)
)
print(f"\nTotal edges: {total_edges} (should be 240)")

print("\n" + "=" * 70)
print("PART 5: ALTERNATIVE PARTITION - BY HAMMING WEIGHT")
print("=" * 70)


def hamming(v):
    return sum(1 for x in v if x != 0)


hamming_classes = defaultdict(list)
for v in proj_list:
    h = hamming(v)
    hamming_classes[h].append(v)

print("Vertices by Hamming weight (number of nonzero coords):")
for h in sorted(hamming_classes.keys()):
    print(f"  Hamming {h}: {len(hamming_classes[h])} vertices")

print("\n4 + 12 + 16 + 8 = 40 ✓")

# Interesting: 4 + 12 = 16 and 16 + 8 = 24
# Or: 4, 12, 16, 8 could relate to particle content

print("\n--- Physical interpretation ---")
print("Hamming 1 (4 vertices): Operators involving only one qutrit → 4 particles?")
print("Hamming 2 (12 vertices): Mixed operators → 12 = SM gauge dimension!")
print("Hamming 3 (16 vertices): Highly entangled → 16 fermions per generation?")
print("Hamming 4 (8 vertices): Fully mixed → 8 gluons?")

# Check: 4 + 12 + 16 + 8 = 40
# SM: 8 gluons + 3 weak + 1 photon + 16 fermions = 28?

print("\n" + "=" * 70)
print("PART 6: THE TRIPARTITION THAT GIVES EXACTLY 3 GENERATIONS")
print("=" * 70)

print(
    """
We need a natural partition of 40 into pieces related to generations.
The most physics-aligned would be:

40 = 3 × 13 + 1  (but 3×13=39)
40 = 3 × 12 + 4  (36 + 4 = 40, and 12 is gauge dimension)
40 = 3 × 8 + 16  (24 + 16 = 40, and 8 is SU(3), 16 is fermions)

Let's look for an automorphism-invariant 3-partition!
"""
)

# The automorphism group Sp(4,3) acts on W33
# Find orbits under some subgroup

# Alternative: Look at the "quotient" by the Z₃ scaling action
# (a,b,c,d) → (2a, 2b, 2c, 2d) mod 3


def scale_by_2(v):
    return tuple((2 * x) % 3 for x in v)


# This is actually the identity on projective points (since 2 = -1, and we quotient by scalars)
# So we need a different action...


# Consider: action by cyclic permutation of coordinates
def cyclic_perm(v):
    """(a,b,c,d) → (b,c,d,a)"""
    return (v[1], v[2], v[3], v[0])


# Find orbits under this action
orbits = []
seen = set()
for v in proj_list:
    if v not in seen:
        orbit = set()
        current = v
        for _ in range(4):
            orbit.add(current)
            orbit.add(normalize(current))
            current = cyclic_perm(current)
        orbits.append(orbit)
        seen.update(orbit)

print(f"\nOrbits under cyclic coordinate permutation: {len(orbits)}")
orbit_sizes = [len(o) for o in orbits]
print(f"Orbit sizes: {sorted(set(orbit_sizes))}")
size_counts = {s: orbit_sizes.count(s) for s in set(orbit_sizes)}
print(f"Distribution: {size_counts}")

# The fixed points (size 1 orbits) are (a,a,a,a) type
fixed = [o for o in orbits if len(o) == 1]
print(f"\nFixed points: {[list(o)[0] for o in fixed]}")

print("\n" + "=" * 70)
print("PART 7: SYNTHESIS - QUTRITS AND GENERATIONS")
print("=" * 70)

print(
    """
╔══════════════════════════════════════════════════════════════════════╗
║           QUTRIT QUANTUM MECHANICS ↔ THREE GENERATIONS               ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  W33 = Geometry of 2-qutrit Pauli operators                          ║
║                                                                      ║
║  STRUCTURE:                                                          ║
║  • 40 projective Pauli operators = 40 W33 vertices                   ║
║  • 40 maximal commuting sets = 40 t.i. 2-spaces                      ║
║  • Self-dual structure!                                              ║
║                                                                      ║
║  THREE GENERATIONS VIA:                                              ║
║                                                                      ║
║  1. Eigenvalue sectors: {1, ω, ω²} where ω = e^(2πi/3)              ║
║     - Gen 1: eigenvalue 1 (ground states)                            ║
║     - Gen 2: eigenvalue ω (first excitation)                         ║
║     - Gen 3: eigenvalue ω² (second excitation)                       ║
║                                                                      ║
║  2. Weight mod 3: vertices split 13 + 14 + 13 ≈ 40/3 each           ║
║     - Near-perfect tripartition!                                     ║
║     - The 14 might be "heavier" (more mass?)                        ║
║                                                                      ║
║  3. GF(3) arithmetic: {0, 1, 2} ↔ {neutral, +, -}                   ║
║     - Each generation is a "charge sector"                           ║
║                                                                      ║
║  WHY 3 GENERATIONS?                                                  ║
║                                                                      ║
║  Because quantum mechanics over GF(3) NECESSARILY has                ║
║  three sectors - it's built into the field structure!                ║
║                                                                      ║
║  The fact that physics has exactly 3 generations                     ║
║  suggests the universe does quantum computing with QUTRITS,          ║
║  not qubits!                                                         ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
"""
)

# Final numerology
print("\n--- Key Numbers ---")
print(f"3 = |GF(3)| = number of qutrit states = generations")
print(f"9 = 3² = dimension of 2-qutrit Hilbert space")
print(f"40 = projective Paulis = (81-1)/2 = W33 vertices")
print(f"240 = edges = qutrit transitions = E8 roots")
print(f"51840 = |Aut(W33)| = |Sp(4,3)| = |W(E6)|")

# The qutrit → generation mass hierarchy?
print("\n--- Mass Hierarchy Speculation ---")
print("If generations are qutrit sectors:")
print("  m₂/m₁ ∝ ω/1 = ω (complex!)")
print("  m₃/m₂ ∝ ω²/ω = ω")
print("  m₃/m₁ ∝ ω²/1 = ω²")
print("\nBut masses are real! So perhaps:")
print("  m ∝ |⟨eigenvalue|H|eigenvalue⟩|")
print("  With some Hermitian H that breaks the Z₃ symmetry")
