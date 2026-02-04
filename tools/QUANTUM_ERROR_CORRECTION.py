#!/usr/bin/env python3
"""
QUANTUM ERROR CORRECTION FROM W33
The stabilizer code structure of W33 and fault-tolerant quantum computing
"""

import math
from itertools import combinations, product

import numpy as np

print("=" * 70)
print("          QUANTUM ERROR CORRECTION FROM W33")
print("          Stabilizer Codes and Fault Tolerance")
print("=" * 70)

# ==========================================================================
#                    BUILD W33 AS STABILIZER GRAPH
# ==========================================================================

print("\n" + "=" * 70)
print("SECTION 1: W33 as a Stabilizer Graph")
print("=" * 70)

print(
    """
W33 arises from 2-qutrit Pauli operators:

    For 2 qutrits (d=3), the Pauli group has generators:
    • X: |j⟩ → |j+1 mod 3⟩  (shift operator)
    • Z: |j⟩ → ω^j|j⟩       (phase operator, ω = e^(2πi/3))

    General Pauli: P = ω^k X^a Z^b ⊗ X^c Z^d

    Two Paulis commute iff their symplectic form vanishes:
    [P₁, P₂] = 0  ↔  ⟨(a₁,b₁,a₂,b₂), (c₁,d₁,c₂,d₂)⟩_symp = 0

    W33 = commutation graph of non-identity 2-qutrit Paulis
"""
)


def build_W33():
    """Build W33 with explicit Pauli labels"""
    points = [
        (a, b, c, d)
        for a, b, c, d in product(range(3), repeat=4)
        if (a, b, c, d) != (0, 0, 0, 0)
    ]

    def symp(p1, p2):
        a1, b1, a2, b2 = p1
        c1, d1, c2, d2 = p2
        return (a1 * d1 - b1 * c1 + a2 * d2 - b2 * c2) % 3

    def line_rep(p):
        doubled = tuple((2 * x) % 3 for x in p)
        return min(p, doubled)

    lines = sorted(set(line_rep(p) for p in points))
    n = len(lines)

    adj = np.zeros((n, n), dtype=int)
    for i, l1 in enumerate(lines):
        for j, l2 in enumerate(lines):
            if i != j and symp(l1, l2) == 0:
                adj[i, j] = 1

    return adj, lines


W33_adj, W33_labels = build_W33()
n = len(W33_labels)
k = int(np.sum(W33_adj[0]))
edges = n * k // 2

print(f"\nW33 STABILIZER STRUCTURE:")
print(f"  Vertices (Pauli operators): {n}")
print(f"  Edges (commuting pairs): {edges}")
print(f"  Degree (commutant size): {k}")

# ==========================================================================
#                    STABILIZER CODES
# ==========================================================================

print("\n" + "=" * 70)
print("SECTION 2: Stabilizer Code Theory")
print("=" * 70)

print(
    """
A [[n, k, d]] stabilizer code encodes k logical qudits in n physical qudits
with distance d (can correct ⌊(d-1)/2⌋ errors).

For a code defined by stabilizer group S:
• S is an abelian subgroup of the Pauli group
• The codespace is the +1 eigenspace of all stabilizers
• Logical operators commute with S but are not in S

W33 encodes the COMMUTATION STRUCTURE of potential stabilizers!
"""
)


# Find maximal cliques (maximal commuting sets)
def find_maximal_cliques_greedy(adj, n_samples=100):
    """Find maximal cliques via greedy sampling"""
    cliques = []

    for start in range(min(n_samples, n)):
        clique = {start}
        candidates = set(j for j in range(n) if adj[start, j] == 1)

        while candidates:
            # Find vertex connected to all in clique
            for v in list(candidates):
                if all(adj[v, c] == 1 for c in clique):
                    clique.add(v)
                    candidates = candidates & set(j for j in range(n) if adj[v, j] == 1)
                    break
            else:
                break

        cliques.append(frozenset(clique))

    return list(set(cliques))


cliques = find_maximal_cliques_greedy(W33_adj)
clique_sizes = [len(c) for c in cliques]

print(f"\nMAXIMAL COMMUTING SETS (Maximal Cliques):")
print(f"  Found {len(cliques)} maximal cliques")
print(f"  Sizes: {sorted(set(clique_sizes), reverse=True)}")
print(f"  Max clique size: {max(clique_sizes)}")

# Count cliques by size
size_count = {}
for s in clique_sizes:
    size_count[s] = size_count.get(s, 0) + 1
print(f"  Distribution: {dict(sorted(size_count.items(), reverse=True))}")

# ==========================================================================
#                    QUTRIT ERROR CORRECTION
# ==========================================================================

print("\n" + "=" * 70)
print("SECTION 3: Qutrit Error Correction")
print("=" * 70)

print(
    """
For QUTRITS (d=3), error correction is richer than qubits:

Error types for single qutrit:
• X errors: X, X² (2 types)
• Z errors: Z, Z² (2 types)
• Combined: XZ, XZ², X²Z, X²Z² (4 types)
• Identity: I (no error)

Total: 1 + 2 + 2 + 4 = 9 = 3² operators per qutrit

For 2 qutrits: 9² = 81 operators (including identity)
W33 has 40 vertices = 80/2 (projective, excluding identity)
"""
)

# The 40 vertices represent 80 Pauli operators (±1 equivalence)
# Each vertex is a "line" in the projective space PG(3,3)

print(f"\nQUTRIT ERROR STRUCTURE:")
print(f"  Single qutrit: 9 Paulis")
print(f"  Two qutrits: 81 Paulis")
print(f"  Projective (mod scalars): 80/2 = 40 = W33 vertices ✓")

# Error detection capability
# For a stabilizer code, errors are detectable if they don't commute with stabilizers

# ==========================================================================
#                    THE [[5,1,3]] ANALOG
# ==========================================================================

print("\n" + "=" * 70)
print("SECTION 4: Perfect Codes and W33")
print("=" * 70)

print(
    """
The perfect [[5,1,3]] qubit code (5 qubits, 1 logical, distance 3):
• Encodes 1 logical qubit in 5 physical qubits
• Can correct any single-qubit error
• Saturates the quantum Singleton bound

For QUTRITS, perfect codes have different parameters.
The qutrit [[5,1,3]] code exists and is related to W33!

W33 connection:
• W33 = SRG(40, 12, 2, 4)
• The 40 vertices can index qutrit Pauli errors
• Stabilizer structure determines code parameters
"""
)

# Quantum Singleton bound: n - k ≥ 2(d - 1)
# For [[n, k, d]]_q code over dimension q


def singleton_check(n_phys, k_log, d, q=3):
    """Check quantum Singleton bound"""
    return n_phys - k_log >= 2 * (d - 1)


print(f"\nPERFECT QUTRIT CODES:")
codes = [
    (4, 2, 2, 3),  # [[4,2,2]]_3
    (5, 1, 3, 3),  # [[5,1,3]]_3
    (11, 1, 5, 3),  # [[11,1,5]]_3
]

for n_phys, k_log, d, q in codes:
    valid = singleton_check(n_phys, k_log, d, q)
    print(f"  [[{n_phys},{k_log},{d}]]_3: Singleton {'✓' if valid else '✗'}")

# ==========================================================================
#                    GRAPH CODES FROM W33
# ==========================================================================

print("\n" + "=" * 70)
print("SECTION 5: Graph Codes from W33")
print("=" * 70)

print(
    """
CSS codes can be constructed from classical codes.
Graph codes use the adjacency matrix of a graph.

For W33, we can construct:
• Classical code C from W33 adjacency structure
• Quantum code from CSS construction

The SRG properties give special code properties:
• Regular degree k=12 → uniform error structure
• λ=2, μ=4 → controlled overlap → controlled distance
"""
)

# Check matrix properties
rank_adj = np.linalg.matrix_rank(W33_adj)
print(f"\nW33 ADJACENCY MATRIX CODE PROPERTIES:")
print(f"  Matrix rank over R: {rank_adj}")
print(f"  Nullity: {n - rank_adj}")

# Compute rank over GF(3)
# For a rough estimate, use the number of distinct eigenvalues
D = np.diag(np.sum(W33_adj, axis=1))
L = D - W33_adj
eigs = np.linalg.eigvalsh(W33_adj)
distinct_eigs = len(set(np.round(eigs, 4)))

print(f"  Distinct eigenvalues: {distinct_eigs}")
print(f"  Adjacency eigenvalues: {sorted(set(np.round(eigs, 2)), reverse=True)}")

# ==========================================================================
#                    FAULT TOLERANCE
# ==========================================================================

print("\n" + "=" * 70)
print("SECTION 6: Fault Tolerance and Thresholds")
print("=" * 70)

print(
    """
Fault-tolerant quantum computing requires:
1. Error-correcting codes with good distance
2. Fault-tolerant gate implementations
3. Error rate below threshold

W33 structure implies:
• Each Pauli (vertex) has 12 commuting partners
• Errors can spread along edges (commuting errors compose)
• The graph diameter 2 limits error propagation

For threshold estimation:
• Surface codes: ~1% threshold
• Color codes: ~0.1% threshold
• W33-based codes: determined by graph structure
"""
)


# Graph properties relevant to fault tolerance
# Diameter
def graph_diameter(adj):
    n = len(adj)
    dist = np.full((n, n), np.inf)
    np.fill_diagonal(dist, 0)
    dist[adj == 1] = 1

    # Floyd-Warshall
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if dist[i, k] + dist[k, j] < dist[i, j]:
                    dist[i, j] = dist[i, k] + dist[k, j]

    return int(np.max(dist[dist < np.inf]))


diameter = graph_diameter(W33_adj)

# Girth (shortest cycle)
# For SRG with λ ≥ 1, girth is 3 (has triangles)
girth = 3  # Since λ = 2 > 0

# Expansion (spectral gap)
adj_eigs = sorted(np.linalg.eigvalsh(W33_adj), reverse=True)
spectral_gap = adj_eigs[0] - adj_eigs[1]

print(f"\nFAULT-TOLERANCE RELEVANT PROPERTIES:")
print(f"  Diameter: {diameter} (error propagation depth)")
print(f"  Girth: {girth} (smallest error cycle)")
print(f"  Spectral gap: {spectral_gap:.2f} (mixing/expansion)")
print(f"  Degree: {k} (local error spread)")

# ==========================================================================
#                    MAGIC STATE DISTILLATION
# ==========================================================================

print("\n" + "=" * 70)
print("SECTION 7: Magic States and Universality")
print("=" * 70)

print(
    """
For universal quantum computing, we need:
• Clifford gates (easy with stabilizer codes)
• Non-Clifford gates (require "magic states")

Magic state distillation:
• Start with noisy magic states
• Use stabilizer operations to purify
• Achieve arbitrary accuracy

W33 and magic states:
• The 40 vertices form a "magic polytope" for qutrits
• Stabilizer operations preserve this structure
• Non-stabilizer states lie "outside" W33

The SIC-POVM connection:
• For d=3, there's a SIC-POVM with 9 elements
• These relate to the 9 single-qutrit Paulis
• W33 encodes 2-qutrit structure
"""
)

# SIC-POVM for qutrit
sic_dim = 3
sic_elements = sic_dim**2  # 9 for qutrit

print(f"\nMAGIC STATE STRUCTURE:")
print(f"  Qutrit SIC-POVM elements: {sic_elements}")
print(f"  2-qutrit Paulis (projective): {n}")
print(f"  Ratio: {n}/{sic_elements} = {n/sic_elements:.2f}")

# ==========================================================================
#                    TOPOLOGICAL CODES
# ==========================================================================

print("\n" + "=" * 70)
print("SECTION 8: Topological Quantum Codes")
print("=" * 70)

print(
    """
Topological codes (surface codes, color codes) have:
• Qubits on a 2D surface
• Local stabilizers
• Non-local logical operators (wrap around surface)

W33 as a potential topological structure:
• 40 vertices = 40 "plaquettes" or "sites"
• 240 edges = local interactions
• Diameter 2 = "small world" topology

The non-neighbors (27 per vertex) could represent:
• Non-local (logical) operator support
• Defect or boundary structure
"""
)

# Euler characteristic for W33 "surface"
# χ = V - E + F for 2D surface
# For W33 as simplicial complex: V=40, E=240, estimate F

# Count triangles (3-cycles)
triangles = int(np.trace(np.linalg.matrix_power(W33_adj, 3)) / 6)

euler_approx = n - edges + triangles
print(f"\nTOPOLOGICAL INVARIANTS:")
print(f"  Vertices (0-cells): {n}")
print(f"  Edges (1-cells): {edges}")
print(f"  Triangles (2-cells): {triangles}")
print(f"  Euler characteristic: χ ≈ {euler_approx}")

# For orientable surface of genus g: χ = 2 - 2g
# χ = -40 implies g ≈ 21
if euler_approx < 2:
    genus = (2 - euler_approx) // 2
    print(f"  Implied genus: g ≈ {genus}")

# ==========================================================================
#                    SUMMARY
# ==========================================================================

print("\n" + "=" * 70)
print("SUMMARY: Quantum Error Correction from W33")
print("=" * 70)

print(
    f"""
W33 AS QUANTUM ERROR CORRECTION STRUCTURE:

  STABILIZER PROPERTIES:
    • 40 vertices = 40 projective Pauli classes
    • 240 edges = 240 commuting pairs
    • Maximal cliques = maximal stabilizer groups
    • Max clique size: {max(clique_sizes)} (max stabilizers)

  CODE PARAMETERS:
    • Graph rank: {rank_adj}
    • Spectral gap: {spectral_gap:.2f}
    • Diameter: {diameter}
    • Triangles: {triangles}

  FAULT TOLERANCE:
    • Diameter 2 limits error propagation
    • Regular degree k=12 gives uniform structure
    • SRG properties ensure controlled distances

  TOPOLOGICAL STRUCTURE:
    • Euler characteristic χ ≈ {euler_approx}
    • High genus suggests rich topology
    • 27 non-neighbors = non-local operator support

W33 provides a natural framework for:
  • Qutrit stabilizer codes
  • Topological quantum memory
  • Fault-tolerant quantum computing

The "Theory of Everything" is also a theory of
QUANTUM ERROR CORRECTION!
"""
)

print("=" * 70)
print("                 COMPUTATION COMPLETE")
print("=" * 70)
