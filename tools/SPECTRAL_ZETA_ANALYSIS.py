#!/usr/bin/env python3
"""
SPECTRAL ZETA FUNCTIONS AND ANALYTIC NUMBER THEORY
Exploring deep spectral connections in W33/E8
"""

import math
from fractions import Fraction
from itertools import combinations, product

import numpy as np

print("=" * 70)
print("          SPECTRAL ANALYSIS AND ZETA FUNCTIONS")
print("          Number-theoretic structures in W33/E8")
print("=" * 70)

# ==========================================================================
#                    BUILD W33
# ==========================================================================


def build_W33():
    """Build W33 from 2-qutrit Pauli commutation"""
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


print("\nBuilding W33...")
W33_adj, W33_vertices = build_W33()
n = len(W33_vertices)
print(f"W33: {n} vertices")

# ==========================================================================
#                    SPECTRAL DECOMPOSITION
# ==========================================================================

print("\n" + "=" * 70)
print("SECTION 1: Complete Spectral Analysis")
print("=" * 70)

# Adjacency matrix eigenvalues
adj_eigs = np.linalg.eigvalsh(W33_adj)
adj_eigs_rounded = np.round(adj_eigs, 6)

# Laplacian eigenvalues
D = np.diag(np.sum(W33_adj, axis=1))
L = D - W33_adj
lap_eigs = np.linalg.eigvalsh(L)
lap_eigs_rounded = np.round(lap_eigs, 6)

# Normalized Laplacian
D_inv_sqrt = np.diag(1.0 / np.sqrt(np.sum(W33_adj, axis=1)))
L_norm = np.eye(n) - D_inv_sqrt @ W33_adj @ D_inv_sqrt
norm_lap_eigs = np.linalg.eigvalsh(L_norm)

print("\n1. ADJACENCY SPECTRUM:")
unique_adj = sorted(set(adj_eigs_rounded), reverse=True)
print(f"   Eigenvalues: {unique_adj}")
for ev in unique_adj:
    mult = np.sum(np.abs(adj_eigs_rounded - ev) < 0.001)
    print(f"   λ = {ev:7.2f}, multiplicity = {mult}")

print("\n2. LAPLACIAN SPECTRUM:")
unique_lap = sorted(set(lap_eigs_rounded))
print(f"   Eigenvalues: {unique_lap}")
for ev in unique_lap:
    mult = np.sum(np.abs(lap_eigs_rounded - ev) < 0.001)
    print(f"   μ = {ev:7.2f}, multiplicity = {mult}")

print("\n3. NORMALIZED LAPLACIAN SPECTRUM:")
unique_norm = sorted(set(np.round(norm_lap_eigs, 6)))
print(f"   Eigenvalues: {[round(x, 4) for x in unique_norm]}")

# ==========================================================================
#                    GRAPH ZETA FUNCTIONS
# ==========================================================================

print("\n" + "=" * 70)
print("SECTION 2: Graph Zeta Functions")
print("=" * 70)

# Ihara zeta function: ζ_G(u) = Π_[p] (1 - u^|p|)^{-1}
# where product is over prime cycles
# Determinant formula: ζ_G(u)^{-1} = (1-u²)^{E-V} det(I - Au + (k-1)u²I)
# for k-regular graphs

k = int(np.sum(W33_adj[0]))  # degree
E = n * k // 2  # edges

print("\nIHARA ZETA FUNCTION:")
print(f"  W33 is {k}-regular with {n} vertices and {E} edges")

# Compute ζ_G(u)^{-1} = (1-u²)^{E-n} det(I - Au + (k-1)u²I)


def ihara_inverse(u):
    """Compute ζ_G(u)^{-1}"""
    M = np.eye(n) - u * W33_adj + (k - 1) * u**2 * np.eye(n)
    return ((1 - u**2) ** (E - n)) * np.linalg.det(M)


print("\n  Values of 1/ζ_G(u):")
for u in [0.05, 0.1, 0.15, 0.2]:
    val = ihara_inverse(u)
    print(f"    u = {u}: 1/ζ_G(u) = {val:.6e}")

# The poles of Ihara zeta relate to eigenvalues
# Pole when det(I - Au + (k-1)u²I) = 0
# i.e., when 1 - λu + (k-1)u² = 0 for some eigenvalue λ
# Solutions: u = [λ ± √(λ² - 4(k-1))] / [2(k-1)]

print("\n  Poles from adjacency eigenvalues:")
for ev in unique_adj:
    disc = ev**2 - 4 * (k - 1)
    if disc >= 0:
        u1 = (ev + np.sqrt(disc)) / (2 * (k - 1))
        u2 = (ev - np.sqrt(disc)) / (2 * (k - 1))
        print(f"    λ = {ev:6.2f} → u = {u1:.6f}, {u2:.6f}")
    else:
        u_re = ev / (2 * (k - 1))
        u_im = np.sqrt(-disc) / (2 * (k - 1))
        print(f"    λ = {ev:6.2f} → u = {u_re:.6f} ± {u_im:.6f}i")

# ==========================================================================
#                    SPECTRAL DETERMINANTS
# ==========================================================================

print("\n" + "=" * 70)
print("SECTION 3: Spectral Determinants")
print("=" * 70)

# Characteristic polynomial
from numpy.polynomial import polynomial as P

adj_char = np.poly(W33_adj)
print("\nADJACENCY CHARACTERISTIC POLYNOMIAL:")
print(f"  det(λI - A) = polynomial of degree {n}")
print(f"  Constant term: {adj_char[-1]:.0f}")
print(f"  Leading coefficient: {adj_char[0]}")

# Tree number (via Matrix-Tree theorem)
# κ(G) = (1/n) × product of non-zero Laplacian eigenvalues
nonzero_lap = [e for e in lap_eigs if abs(e) > 0.01]
tree_number = np.prod(nonzero_lap) / n
print(f"\nSPANNING TREE COUNT (Matrix-Tree theorem):")
print(f"  κ(W33) = (1/{n}) × Π μᵢ = {tree_number:.6e}")

# Determinant of adjacency
adj_det = np.linalg.det(W33_adj)
print(f"\nADJACENCY DETERMINANT:")
print(f"  det(A) = {adj_det:.0f}")

# ==========================================================================
#                    HEAT KERNEL AND ZETA REGULARIZATION
# ==========================================================================

print("\n" + "=" * 70)
print("SECTION 4: Heat Kernel Spectral Analysis")
print("=" * 70)

# Heat kernel trace: Z(t) = Σᵢ exp(-tμᵢ) = Tr(exp(-tL))


def heat_kernel_trace(t):
    return np.sum(np.exp(-t * lap_eigs))


print("\nHEAT KERNEL TRACE Z(t) = Tr(e^{-tL}):")
for t in [0.01, 0.05, 0.1, 0.5, 1.0, 2.0]:
    Z = heat_kernel_trace(t)
    print(f"  t = {t:5.2f}: Z(t) = {Z:.6f}")

# Spectral zeta function: ζ_L(s) = Σ μᵢ^{-s} for μᵢ > 0
# Converges for Re(s) > d/2 where d is some dimension


def spectral_zeta(s):
    """Compute spectral zeta function (excluding zero eigenvalue)"""
    nonzero = [mu for mu in lap_eigs if mu > 0.01]
    return np.sum([mu ** (-s) for mu in nonzero])


print("\nSPECTRAL ZETA FUNCTION ζ_L(s) = Σ μᵢ^{-s}:")
for s in [0.5, 1.0, 1.5, 2.0, 3.0]:
    zeta = spectral_zeta(s)
    print(f"  s = {s:4.1f}: ζ_L(s) = {zeta:.6f}")

# The "dimension" from zeta: at what s does ζ_L(s) diverge?
# For d-dimensional manifolds, ζ diverges as s → d/2

# ==========================================================================
#                    NUMBER THEORETIC CONNECTIONS
# ==========================================================================

print("\n" + "=" * 70)
print("SECTION 5: Number Theoretic Analysis")
print("=" * 70)

# The fine structure constant formula
pi = math.pi
alpha_inv = 4 * pi**3 + pi**2 + pi - 1 / 3282

print("\nFINE STRUCTURE CONSTANT DECOMPOSITION:")
print(f"  1/α = 4π³ + π² + π - 1/3282")
print(f"      = 4π³ + π² + π - 1/(2×3×547)")
print(f"      = {4*pi**3:.6f} + {pi**2:.6f} + {pi:.6f} - {1/3282:.6f}")
print(f"      = {alpha_inv:.9f}")


# Prime factorization of key numbers
def factorize(n):
    factors = {}
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors[d] = factors.get(d, 0) + 1
            n //= d
        d += 1
    if n > 1:
        factors[n] = factors.get(n, 0) + 1
    return factors


print("\nPRIME FACTORIZATIONS:")
key_nums = [40, 240, 27, 12, 196883, 196560, 3282, 51840]
for num in key_nums:
    facts = factorize(num)
    fact_str = " × ".join(
        f"{p}^{e}" if e > 1 else str(p) for p, e in sorted(facts.items())
    )
    print(f"  {num:>6} = {fact_str}")

# Continued fraction of 1/α
print("\nCONTINUED FRACTION OF 1/α:")


def continued_fraction(x, terms=10):
    cf = []
    for _ in range(terms):
        a = int(x)
        cf.append(a)
        frac = x - a
        if frac < 1e-10:
            break
        x = 1 / frac
    return cf


cf_alpha = continued_fraction(alpha_inv, 12)
print(f"  1/α = [{cf_alpha[0]}; {', '.join(map(str, cf_alpha[1:]))}]")

# Convergents
print("\n  Convergents:")
p, q = [cf_alpha[0], cf_alpha[0] * cf_alpha[1] + 1], [1, cf_alpha[1]]
print(f"    {p[0]}/{q[0]} = {p[0]/q[0]:.9f}")
print(f"    {p[1]}/{q[1]} = {p[1]/q[1]:.9f}")
for i in range(2, min(6, len(cf_alpha))):
    p_new = cf_alpha[i] * p[-1] + p[-2]
    q_new = cf_alpha[i] * q[-1] + q[-2]
    p.append(p_new)
    q.append(q_new)
    print(f"    {p_new}/{q_new} = {p_new/q_new:.9f}")

# ==========================================================================
#                    TRACE FORMULAE
# ==========================================================================

print("\n" + "=" * 70)
print("SECTION 6: Trace Formulae")
print("=" * 70)

# Closed walks of length k = Tr(A^k)
print("\nTRACE OF POWERS (closed walks of length k):")
A = W33_adj.astype(float)
for k in range(1, 9):
    Ak = np.linalg.matrix_power(A, k)
    trace = np.trace(Ak)
    # Also compute via eigenvalues
    trace_eig = np.sum(adj_eigs**k)
    print(f"  Tr(A^{k}) = {trace:>12.0f}  (eigenvalue sum: {trace_eig:>12.0f})")

# Total walks interpretation
print("\n  Interpretation:")
print(f"  Tr(A²) = 2×{E} = twice the edges (each edge = 2-walk)")
print(f"  Tr(A³) = 6×(triangles) = 6-count of triangles")
triangles = int(np.trace(np.linalg.matrix_power(A, 3)) / 6)
print(f"        → W33 has {triangles} triangles")

# ==========================================================================
#                    RAMANUJAN PROPERTY
# ==========================================================================

print("\n" + "=" * 70)
print("SECTION 7: Ramanujan Property")
print("=" * 70)

# A k-regular graph is Ramanujan if all eigenvalues λ satisfy:
# λ = k (largest), or |λ| ≤ 2√(k-1)

ramanujan_bound = 2 * np.sqrt(k - 1)
print(f"\nRAMANUJAN BOUND for {k}-regular graph: 2√({k}-1) = {ramanujan_bound:.4f}")

non_trivial_eigs = [e for e in adj_eigs if abs(e - k) > 0.1]
max_nontrivial = max(abs(e) for e in non_trivial_eigs)
is_ramanujan = max_nontrivial <= ramanujan_bound + 0.001

print(f"\nNon-trivial eigenvalues of W33:")
for e in unique_adj:
    if abs(e - k) > 0.1:
        status = "✓" if abs(e) <= ramanujan_bound + 0.001 else "✗"
        print(f"  λ = {e:7.3f}, |λ| = {abs(e):7.3f} {status}")

print(f"\nMaximum non-trivial |λ| = {max_nontrivial:.4f}")
print(f"Ramanujan bound = {ramanujan_bound:.4f}")
print(f"W33 is Ramanujan: {is_ramanujan}")

# For SRG(n,k,λ,μ), the restricted eigenvalues are:
# r = (λ-μ + √[(λ-μ)² + 4(k-μ)]) / 2
# s = (λ-μ - √[(λ-μ)² + 4(k-μ)]) / 2

lam, mu = 2, 4
disc = (lam - mu) ** 2 + 4 * (k - mu)
r = ((lam - mu) + np.sqrt(disc)) / 2
s = ((lam - mu) - np.sqrt(disc)) / 2

print(f"\nSRG restricted eigenvalues:")
print(f"  r = {r:.4f}")
print(f"  s = {s:.4f}")

# ==========================================================================
#                    SELBERG ZETA ANALOGY
# ==========================================================================

print("\n" + "=" * 70)
print("SECTION 8: Selberg Zeta Analogy")
print("=" * 70)

print(
    """
The Selberg zeta function for hyperbolic surfaces:
  Z_Γ(s) = Π_{[γ]} Π_{n=0}^∞ (1 - e^{-(s+n)ℓ(γ)})

where γ runs over primitive closed geodesics of length ℓ(γ).

For graphs, the Ihara zeta is analogous:
  ζ_G(u) = Π_{[p]} (1 - u^{|p|})^{-1}

where p runs over primitive cycles of length |p|.

Relationship to Riemann zeta:
  • Zeros of Selberg zeta ↔ eigenvalues of Laplacian on surface
  • Zeros of Ihara zeta ↔ eigenvalues of adjacency matrix

The Riemann hypothesis for graphs:
  All "non-trivial" zeros of ζ_G have |u| = 1/√(k-1)
  This is equivalent to the Ramanujan property!
"""
)

# Compute the "Riemann hypothesis radius"
RH_radius = 1 / np.sqrt(k - 1)
print(f"Riemann hypothesis radius: 1/√({k}-1) = {RH_radius:.6f}")

# ==========================================================================
#                    MODULAR FORMS CONNECTION
# ==========================================================================

print("\n" + "=" * 70)
print("SECTION 9: Modular Forms and Theta Series")
print("=" * 70)

# E8 theta function coefficients
print("\nE8 LATTICE THETA FUNCTION:")
print("  Θ_{E8}(τ) = Σ_{v ∈ E8} q^{|v|²/2}")
print("           = 1 + 240q + 2160q² + 6720q³ + ...")

# The coefficient 240 = |E8 roots| = W33 edges!
print(f"\n  The coefficient of q is {240} = |E8 roots| = W33 edges!")

# Eisenstein series E_4
print("\n  E8 theta = E₄(τ) (Eisenstein series of weight 4)")
print("  E₄(τ) = 1 + 240 Σ σ₃(n)q^n")
print("  where σ₃(n) = Σ_{d|n} d³")


# Compute first few σ₃
def sigma_3(n):
    return sum(d**3 for d in range(1, n + 1) if n % d == 0)


print("\n  Divisor sums σ₃(n):")
for n in range(1, 8):
    print(f"    σ₃({n}) = {sigma_3(n)}")

# ==========================================================================
#                    SUMMARY
# ==========================================================================

print("\n" + "=" * 70)
print("SUMMARY: Spectral and Number-Theoretic Structure")
print("=" * 70)

print(
    f"""
W33 SPECTRAL DATA:
  • Adjacency eigenvalues: {unique_adj}
  • Laplacian eigenvalues: {unique_lap}
  • Ramanujan: {is_ramanujan}
  • Spanning trees: {tree_number:.2e}
  • Triangles: {triangles}

NUMBER THEORY CONNECTIONS:
  • 240 = W33 edges = E8 roots = coefficient of q in Θ_{'{E8}'}
  • 1/α = 4π³ + π² + π - 1/3282
  • CF of 1/α begins with 137, 27, 1, 3, ... (27 = non-neighbors!)
  • 3282 = 2 × 3 × 547

ZETA FUNCTION STRUCTURE:
  • Ihara zeta relates eigenvalues to prime cycles
  • Ramanujan ↔ "Riemann hypothesis" for graph zeta
  • Spectral zeta ζ_L(s) encodes heat kernel

The spectral structure of W33 encodes:
  • Quantum information (eigenspaces)
  • Number theory (continued fractions, primes)
  • Geometry (heat kernel, zeta functions)
  • Arithmetic (modular forms via E8 theta)
"""
)

print("=" * 70)
print("                 COMPUTATION COMPLETE")
print("=" * 70)
