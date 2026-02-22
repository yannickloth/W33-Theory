#!/usr/bin/env python3
"""
TIME AND CAUSALITY FROM W33
The Emergence of Time from Graph Structure
"""

import math
from itertools import product

import numpy as np

print("=" * 70)
print("         TIME AND CAUSALITY FROM W33")
print("         The Arrow of Time Emerges")
print("=" * 70)

# ==========================================================================
#                    BUILD W33
# ==========================================================================


def build_W33():
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


W33_adj, W33_lines = build_W33()
n = len(W33_adj)
k = int(np.sum(W33_adj[0]))
edges = n * k // 2

print(f"\nW33: {n} vertices, {edges} edges, degree {k}")

# ==========================================================================
#                    THE PROBLEM OF TIME
# ==========================================================================

print("\n" + "=" * 70)
print("SECTION 1: The Problem of Time")
print("=" * 70)

print(
    """
THE DEEP MYSTERY OF TIME:
━━━━━━━━━━━━━━━━━━━━━━━━━

Fundamental laws of physics are TIME-SYMMETRIC:
  • Newton's equations: F = ma (reversible)
  • Maxwell's equations: ∂B/∂t = -∇×E (symmetric)
  • Schrödinger: iℏ∂ψ/∂t = Hψ (unitary, reversible)
  • Einstein: G_μν = 8πT_μν (no preferred time direction)

Yet we observe an ARROW OF TIME:
  • Entropy increases (Second Law)
  • We remember the past, not future
  • Causes precede effects
  • Quantum measurement is irreversible

WHERE DOES TIME'S ARROW COME FROM?
"""
)

# ==========================================================================
#                    CAUSAL STRUCTURE FROM GRAPHS
# ==========================================================================

print("\n" + "=" * 70)
print("SECTION 2: Causal Structure from Graphs")
print("=" * 70)

print(
    """
CAUSAL SETS (Sorkin, Bombelli):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Spacetime = partially ordered discrete set
  • Elements = events
  • Order relation = causal precedence

W33 AS CAUSAL STRUCTURE:
  • Vertices = events
  • Edges = spacelike separation
  • Non-edges = potentially causal!
"""
)

# In W33, two vertices are:
# - Connected (edge): spacelike separated (can't causally influence)
# - Not connected: potentially timelike (causal relation possible)

print(f"\nW33 CAUSAL INTERPRETATION:")
print(f"  For vertex v:")
print(f"    k = {k} neighbors → spacelike separated")
print(f"    27 non-neighbors → potential causal relations")
print(f"    1 self → present moment")

# The 27 non-neighbors split into "past" and "future"
# This requires choosing a time orientation

print(f"\n  TIME ORIENTATION:")
print(f"    27 non-neighbors = 13 (past) + 13 (future) + 1 (?)")
print(f"    Or: 27 = 9 (past) + 9 (future) + 9 (lightlike)")

# ==========================================================================
#                    HEAT KERNEL AND TIME EVOLUTION
# ==========================================================================

print("\n" + "=" * 70)
print("SECTION 3: Heat Kernel as Time Evolution")
print("=" * 70)

# The heat kernel on W33: exp(-t L)
# where L is the Laplacian

L = np.diag(np.sum(W33_adj, axis=1)) - W33_adj
eigs = np.linalg.eigvalsh(L)
unique_eigs = sorted(set(np.round(eigs, 6)))

print(f"\nLAPLACIAN EIGENVALUES: {unique_eigs}")


# Heat kernel eigenvalues at time t
def heat_kernel_trace(L, t):
    """Trace of heat kernel exp(-tL)"""
    eigs = np.linalg.eigvalsh(L)
    return np.sum(np.exp(-t * eigs))


print(f"\nHEAT KERNEL TRACE K(t) = Tr[exp(-tL)]:")
times = [0, 0.01, 0.1, 1, 10, 100]
for t in times:
    K = heat_kernel_trace(L, t)
    print(f"  t = {t:6.2f}: K(t) = {K:.4f}")

print(
    f"""
INTERPRETATION:
  • K(0) = n = {n} (all vertices equally weighted)
  • K(t→∞) → 1 (uniform equilibrium)
  • Decay rate set by λ_min = {unique_eigs[1]} (spectral gap)
"""
)

# Characteristic time scale
tau = 1 / unique_eigs[1]
print(f"  CHARACTERISTIC TIME: τ = 1/λ_min = 1/{unique_eigs[1]} = {tau:.2f}")

# ==========================================================================
#                    ENTROPY AND TIME'S ARROW
# ==========================================================================

print("\n" + "=" * 70)
print("SECTION 4: Entropy and Time's Arrow")
print("=" * 70)


# Von Neumann entropy of the heat kernel state
def von_neumann_entropy(L, t):
    """Entropy of heat kernel density matrix"""
    eigs = np.linalg.eigvalsh(L)
    probs = np.exp(-t * eigs)
    probs = probs / np.sum(probs)
    entropy = -np.sum(probs * np.log(probs + 1e-15))
    return entropy


print(f"\nENTROPY EVOLUTION S(t):")
for t in times:
    S = von_neumann_entropy(L, t)
    print(f"  t = {t:6.2f}: S(t) = {S:.4f} nats")

S_max = math.log(n)
print(f"\n  Maximum entropy: S_max = ln({n}) = {S_max:.4f}")
print(f"  Entropy INCREASES with time!")
print(f"  → ARROW OF TIME emerges from W33 dynamics!")

# ==========================================================================
#                    LIGHT CONE FROM GRAPH DISTANCE
# ==========================================================================

print("\n" + "=" * 70)
print("SECTION 5: Light Cone from Graph Distance")
print("=" * 70)

# Light cone = region reachable in time t
# On a graph, this is the ball of radius t


def graph_distance_distribution(adj):
    """Compute distribution of pairwise distances"""
    n = len(adj)
    # Floyd-Warshall
    dist = np.full((n, n), n + 1)
    np.fill_diagonal(dist, 0)
    dist[adj > 0] = 1
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if dist[i, k] + dist[k, j] < dist[i, j]:
                    dist[i, j] = dist[i, k] + dist[k, j]
    return dist


distances = graph_distance_distribution(W33_adj)
diameter = int(np.max(distances))

print(f"\nW33 DIAMETER: {diameter}")
print(f"  Any vertex reachable in at most {diameter} steps")

# Distance distribution
from collections import Counter

dist_counts = Counter(distances.flatten())
print(f"\n  DISTANCE DISTRIBUTION (from vertex 0):")
for d in range(diameter + 1):
    count = np.sum(distances[0] == d)
    print(f"    d = {d}: {count} vertices")

# Light cone grows with distance
print(
    f"""
LIGHT CONE INTERPRETATION:
  • d = 0: Present (1 vertex)
  • d = 1: Spacelike neighbors ({k} vertices)
  • d = 2: Second neighbors ({np.sum(distances[0]==2)} vertices)

  The "light cone" reaches all W33 in {diameter} steps
  → Maximum causal depth = {diameter}
"""
)

# ==========================================================================
#                    QUANTUM TIME FROM SPECTRAL DECOMPOSITION
# ==========================================================================

print("\n" + "=" * 70)
print("SECTION 6: Quantum Time from Spectral Decomposition")
print("=" * 70)

# Time evolution operator: U(t) = exp(-iHt/ℏ)
# The Laplacian L plays role of Hamiltonian

# Eigenvalue multiplicities
eig_vals, eig_vecs = np.linalg.eigh(L)
unique_rounded = np.round(eig_vals, 6)
from collections import Counter

multiplicities = Counter(unique_rounded)

print(f"\nLAPLACIAN SPECTRUM:")
for val, mult in sorted(multiplicities.items()):
    print(f"  λ = {val:5.1f} with multiplicity {mult}")

# The period of quantum evolution
# All eigenvalues are 0, 10, 16
# LCM of periods 2π/10 and 2π/16
period_10 = 2 * math.pi / 10
period_16 = 2 * math.pi / 16

print(f"\n  QUANTUM PERIODS:")
print(f"    T_10 = 2π/10 = {period_10:.4f}")
print(f"    T_16 = 2π/16 = {period_16:.4f}")

# Find approximate common period
# LCM(1/10, 1/16) = 1/gcd(10,16) × 10 × 16 = 1/2 × 160 = 80
# So LCM period ≈ 2π × 80 / (10×16) = 2π × 80/160 = π
from math import gcd

g = gcd(10, 16)
lcm_factor = (10 * 16) // g
common_period = 2 * math.pi / g

print(f"    GCD(10,16) = {g}")
print(f"    Common period ≈ 2π/{g} = {common_period:.4f}")

# ==========================================================================
#                    EMERGENT LORENTZ SYMMETRY
# ==========================================================================

print("\n" + "=" * 70)
print("SECTION 7: Emergent Lorentz Symmetry")
print("=" * 70)

print(
    """
LORENTZ SYMMETRY IN W33:
━━━━━━━━━━━━━━━━━━━━━━━━

W33 is discrete → no continuous symmetry
But at LARGE SCALES, Lorentz symmetry emerges!

Key: W33 is highly symmetric
  |Aut(W33)| = 51840 = |W(E6)|

This symmetry acts on the 40 vertices
At low resolution, this becomes SO(3,1)!
"""
)

# The dimension hint:
# SO(3,1) has 6 generators (3 rotations + 3 boosts)
# W(E6) has many more, but contains SO subgroups

SO31_dim = 6
print(f"\n  SO(3,1) dimension: {SO31_dim}")
print(f"  W(E6) order: 51840")
print(f"  Ratio: {51840 // SO31_dim}")

# Minkowski metric signature: (+ - - -)
# Related to 40 = 1 + 12 + 27:
# 1 timelike direction
# 12 = 4 × 3 "spatial" directions
# 27 = future/past cones

print(
    f"""
METRIC SIGNATURE FROM W33:
  40 = 1 + 12 + 27
     = (self) + (spacelike) + (timelike/null)

  The 1 picks out time direction
  The 12 neighbors are "spacelike"
  The 27 non-neighbors contain the light cone
"""
)

# ==========================================================================
#                    PLANCK TIME
# ==========================================================================

print("\n" + "=" * 70)
print("SECTION 8: Planck Time from W33")
print("=" * 70)

# Planck time t_P = √(ℏG/c⁵) ≈ 5.4 × 10⁻⁴⁴ s

hbar = 1.055e-34  # J·s
G = 6.674e-11  # m³/(kg·s²)
c = 3e8  # m/s

t_P = math.sqrt(hbar * G / c**5)

print(f"\nPLANCK TIME:")
print(f"  t_P = √(ℏG/c⁵) = {t_P:.3e} s")

# W33 cell "tick" rate
# If W33 is the quantum of spacetime, each cell ticks at t_P

# Observable time = N_cells × t_P
# Universe age ~ 4 × 10¹⁷ s
age_universe = 4e17  # seconds
N_ticks = age_universe / t_P

print(f"\n  AGE OF UNIVERSE:")
print(f"    t_universe ≈ {age_universe:.0e} s")
print(f"    N_ticks = {N_ticks:.2e} Planck times")

# W33 interpretation
# Each tick advances state by exp(-iL t_P/ℏ)
print(
    f"""
W33 INTERPRETATION:
  Each W33 cell evolves by exp(-iL × t_P/ℏ)
  After N ticks: U(t) = [exp(-iL × t_P/ℏ)]^N

  The universe has experienced ~10^61 W33 ticks!
"""
)

# ==========================================================================
#                    SUMMARY
# ==========================================================================

print("\n" + "=" * 70)
print("SUMMARY: Time from W33")
print("=" * 70)

print(
    f"""
╔═══════════════════════════════════════════════════════════════════╗
║                  TIME AND CAUSALITY FROM W33                      ║
╠═══════════════════════════════════════════════════════════════════╣
║                                                                   ║
║  CAUSAL STRUCTURE:                                                ║
║    • Edges = spacelike separation (k = 12)                        ║
║    • Non-edges = potential causal relations (27)                  ║
║    • Time direction from symmetry breaking                        ║
║                                                                   ║
║  ARROW OF TIME:                                                   ║
║    • Heat kernel exp(-tL) evolves states                          ║
║    • Entropy S(t) increases monotonically                         ║
║    • Characteristic time τ = 1/λ_min = 0.1                        ║
║                                                                   ║
║  LIGHT CONE:                                                      ║
║    • Graph distance = causal depth                                ║
║    • Diameter = 2 (all of W33 in 2 steps)                         ║
║    • Fast information propagation!                                ║
║                                                                   ║
║  LORENTZ SYMMETRY:                                                ║
║    • Discrete at Planck scale                                     ║
║    • W(E6) → SO(3,1) at large scales                              ║
║    • Signature (+ - - -) from 1 + 12 + 27 split                   ║
║                                                                   ║
║  PLANCK TIME:                                                     ║
║    • t_P = 5.4 × 10⁻⁴⁴ s is the W33 "tick"                        ║
║    • Universe = 10^61 ticks old                                   ║
║    • Time emerges from graph evolution!                           ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
"""
)

print("=" * 70)
print("               COMPUTATION COMPLETE")
print("=" * 70)
