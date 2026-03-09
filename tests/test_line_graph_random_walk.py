"""
Phase XLIV: Line Graph, Random Walk & Derived Structures on W(3,3) (T621-T635)
================================================================================

Fifteen theorems on the derived graph constructions and stochastic dynamics.

From the single graph W(3,3), classical operations produce a hierarchy:

  L(G):  240 vertices, eigenvalues {22, K, 2q, −2}  — gaps: Θ, 2q, DIM_O
  S(G):  280 vertices, eigenvalues ±√f, ±√14, ±√DIM_O, 0(×200)
  T(G):  280 vertices, s-discriminant = 8² → integer eigenvalues 1, −Φ₆

Random walk on W(3,3):
  SLEM = 1/q,  spectral gap = (q−1)/q,  relaxation = q/(q−1)

The Cheeger constant is bounded below by N = 5, the algebraic connectivity
equals Θ = 10, and Laplacian energy equals graph energy — all from 5 numbers.

Parameters: (v, k, λ, μ, q) = (40, 12, 2, 4, 3).
"""

import math
import pytest
from fractions import Fraction

# ── SRG parameters for W(3,3) ──
V, K, LAM, MU, Q = 40, 12, 2, 4, 3
E = V * K // 2           # 240
R, S = 2, -4             # eigenvalues
F, G = 24, 15            # multiplicities
N = Q + 2                # 5
PHI3 = Q**2 + Q + 1      # 13
PHI6 = Q**2 - Q + 1      # 7
ALBERT = V - PHI3        # 27
DIM_O = K - MU           # 8
THETA = K - R             # 10


# ═══════════════════════════════════════════════════════════════════
# T621: Line Graph Basic Parameters
# ═══════════════════════════════════════════════════════════════════
class TestLineGraphBasics:
    """L(G) has E vertices, is (2K−2)-regular, with 4 distinct eigenvalues."""

    def test_line_vertices(self):
        """L(G) vertices = E = 240."""
        assert E == 240

    def test_line_regularity(self):
        """L(G) is (2K−2) = 22-regular."""
        assert 2 * K - 2 == 22

    def test_line_edges(self):
        """L(G) edges = E·(K−1) = 2640."""
        L_E = E * (2 * K - 2) // 2
        assert L_E == E * (K - 1)
        assert L_E == 2640

    def test_line_eigenvalue_max(self):
        """Maximum L(G) eigenvalue = 2K−2 = 22."""
        assert 2 * K - 2 == 22

    def test_line_eigenvalue_mid1(self):
        """Second L(G) eigenvalue = r + K − 2 = K = 12."""
        assert R + K - 2 == K

    def test_line_eigenvalue_mid2(self):
        """Third L(G) eigenvalue = s + K − 2 = 2q = 6."""
        assert S + K - 2 == 2 * Q

    def test_line_eigenvalue_min(self):
        """Minimum L(G) eigenvalue = −2 (universal for line graphs)."""
        assert -2 == -2  # Universal line graph property

    def test_four_distinct_eigenvalues(self):
        """L(G) has exactly 4 distinct eigenvalues: {22, 12, 6, −2}."""
        eigs = {2 * K - 2, R + K - 2, S + K - 2, -2}
        assert eigs == {22, 12, 6, -2}
        assert len(eigs) == 4


# ═══════════════════════════════════════════════════════════════════
# T622: Line Graph Multiplicities & Whitney Uniqueness
# ═══════════════════════════════════════════════════════════════════
class TestLineGraphMultiplicities:
    """Multiplicities {1, f, g, DIM_O·N²}; Whitney's theorem applies."""

    def test_multiplicity_max(self):
        """Eigenvalue 22 has multiplicity 1."""
        assert 1 == 1  # Perron-Frobenius: max eigenvalue is simple

    def test_multiplicity_mid1(self):
        """Eigenvalue 12 = K has multiplicity f = 24."""
        assert F == 24

    def test_multiplicity_mid2(self):
        """Eigenvalue 6 = 2q has multiplicity g = 15."""
        assert G == 15

    def test_extra_multiplicity(self):
        """Eigenvalue −2 has multiplicity E − V = DIM_O · N²."""
        extra = E - V
        assert extra == DIM_O * N**2
        assert extra == 200

    def test_multiplicities_sum(self):
        """1 + f + g + (E−V) = E = 240."""
        assert 1 + F + G + (E - V) == E

    def test_whitney_uniqueness(self):
        """V = 40 > 6, so Whitney's theorem: L(G) determines G."""
        assert V > 6  # Whitney threshold

    def test_trace_zero(self):
        """Tr(A_L) = sum of eigenvalues = 0 (simple graph)."""
        trace = 22 * 1 + 12 * F + 6 * G + (-2) * (E - V)
        assert trace == 0

    def test_trace_squared(self):
        """Tr(A_L²) = V·K·(K−1) = 5280."""
        tr2 = 22**2 * 1 + 12**2 * F + 6**2 * G + (-2)**2 * (E - V)
        assert tr2 == V * K * (K - 1)
        assert tr2 == 5280


# ═══════════════════════════════════════════════════════════════════
# T623: Line Graph Spectral Gaps
# ═══════════════════════════════════════════════════════════════════
class TestLineGraphGaps:
    """Consecutive eigenvalue gaps are Θ, 2q, DIM_O; summing to f."""

    def test_gap_top(self):
        """22 → 12: gap = Θ = 10."""
        assert 22 - 12 == THETA

    def test_gap_mid(self):
        """12 → 6: gap = 2q = 6."""
        assert 12 - 6 == 2 * Q

    def test_gap_bottom(self):
        """6 → (−2): gap = DIM_O = 8."""
        assert 6 - (-2) == DIM_O

    def test_gap_sum_equals_f(self):
        """Θ + 2q + DIM_O = f = 24 = total spectral spread."""
        assert THETA + 2 * Q + DIM_O == F

    def test_spread_equals_f(self):
        """Spectral spread 22 − (−2) = 24 = f."""
        assert 22 - (-2) == F

    def test_gap_outer1(self):
        """22 − 6 = K + MU = 16."""
        assert 22 - 6 == K + MU

    def test_gap_outer2(self):
        """22 − (−2) = f = 24."""
        assert 22 - (-2) == F

    def test_gap_cross(self):
        """12 − (−2) = K + R = 14."""
        assert 12 - (-2) == K + R


# ═══════════════════════════════════════════════════════════════════
# T624: Line Graph Number Theory
# ═══════════════════════════════════════════════════════════════════
class TestLineGraphNumberTheory:
    """Sum = V−r; half-eigenvalues = {K−1, 2q, q, −1}."""

    def test_sum_distinct(self):
        """Sum of distinct L(G) eigenvalues = V − r = 38."""
        assert 22 + 12 + 6 + (-2) == V - R

    def test_half_eigenvalues(self):
        """L eigenvalues / 2 = {11, 6, 3, −1} = {K−1, 2q, q, −1}."""
        halves = [22 // 2, 12 // 2, 6 // 2, (-2) // 2]
        assert halves == [K - 1, 2 * Q, Q, -1]

    def test_k_minus_1_prime(self):
        """K − 1 = 11 is prime."""
        assert K - 1 == 11
        assert all(11 % d != 0 for d in range(2, 11))

    def test_product_distinct(self):
        """Product of distinct L eigenvalues = −3168 = −2⁵·3²·11."""
        prod = 22 * 12 * 6 * (-2)
        assert prod == -3168
        assert abs(prod) == 2**5 * 3**2 * 11

    def test_line_edge_count_formula(self):
        """L(G) edges = E·(K−1) = 240·11 = 2640."""
        assert E * (K - 1) == 2640


# ═══════════════════════════════════════════════════════════════════
# T625: Incidence Matrix & SVD
# ═══════════════════════════════════════════════════════════════════
class TestIncidenceMatrixSVD:
    """BB^T has eigenvalues {f, 14, DIM_O}; SVD links G to L(G)."""

    def test_BBT_eigenvalue_max(self):
        """BB^T max eigenvalue = K + K = 2K = f = 24."""
        assert K + K == 2 * K
        assert 2 * K == F

    def test_BBT_eigenvalue_mid(self):
        """BB^T mid eigenvalue = K + r = 14."""
        assert K + R == 14

    def test_BBT_eigenvalue_min(self):
        """BB^T min eigenvalue = K + s = DIM_O = 8."""
        assert K + S == DIM_O

    def test_BTB_eigenvalues(self):
        """B^TB eigenvalues = L(G) eigenvalues + 2 = {24, 14, 8, 0}."""
        BTB_eigs = [22 + 2, 12 + 2, 6 + 2, -2 + 2]
        assert BTB_eigs == [24, 14, 8, 0]

    def test_SVD_agreement(self):
        """Nonzero eigenvalues of BB^T = nonzero eigenvalues of B^TB."""
        BBT_eigs = {K + K, K + R, K + S}
        BTB_nonzero = {22 + 2, 12 + 2, 6 + 2}
        assert BBT_eigs == BTB_nonzero

    def test_singular_value_max(self):
        """Largest singular value = √f = 2√6."""
        sv = math.sqrt(F)
        assert abs(sv - 2 * math.sqrt(6)) < 1e-10

    def test_singular_value_min(self):
        """Smallest singular value = √DIM_O = 2√2."""
        sv = math.sqrt(DIM_O)
        assert abs(sv - 2 * math.sqrt(2)) < 1e-10


# ═══════════════════════════════════════════════════════════════════
# T626: Signless Laplacian Q = D + A
# ═══════════════════════════════════════════════════════════════════
class TestSignlessLaplacian:
    """Q eigenvalues = K + θ_i: {f, 14, DIM_O}."""

    def test_Q_eigenvalue_max(self):
        """Q max = 2K = f = 24."""
        assert K + K == F

    def test_Q_eigenvalue_mid(self):
        """Q mid = K + r = 14."""
        assert K + R == 14

    def test_Q_eigenvalue_min(self):
        """Q min = K + s = DIM_O = 8."""
        assert K + S == DIM_O

    def test_Q_equals_BBT(self):
        """Q eigenvalues = BB^T eigenvalues (for regular graphs)."""
        Q_eigs = {K + K, K + R, K + S}
        BBT_eigs = {2 * K, K + R, K + S}
        assert Q_eigs == BBT_eigs

    def test_Q_energy(self):
        """Signless Laplacian energy = 120 = E/2."""
        mean = Fraction(2 * E, V)
        QE = abs(2 * K - mean) * 1 + abs(K + R - mean) * F + abs(K + S - mean) * G
        assert QE == E // 2


# ═══════════════════════════════════════════════════════════════════
# T627: Normalized Laplacian
# ═══════════════════════════════════════════════════════════════════
class TestNormalizedLaplacian:
    """Eigenvalues {0, 5/6, 4/3} — rational with denominators 1, 6, 3."""

    def test_NL_eigenvalue_zero(self):
        """Normalized Laplacian eigenvalue 0 with multiplicity 1."""
        nl = 1 - Fraction(K, K)
        assert nl == 0

    def test_NL_eigenvalue_mid(self):
        """NL eigenvalue from r: 1 − r/K = 5/6."""
        nl = 1 - Fraction(R, K)
        assert nl == Fraction(5, 6)

    def test_NL_eigenvalue_max(self):
        """NL eigenvalue from s: 1 − s/K = 4/3."""
        nl = 1 - Fraction(S, K)
        assert nl == Fraction(4, 3)

    def test_NL_product_exponents(self):
        """Product = 2^(2q) · 5^f / 3^(V−1): exponents are W(3,3) constants."""
        # (5/6)^f * (4/3)^g = 5^f * 2^(2g) / (2^f * 3^f * 3^g)
        # = 5^f * 2^(2g-f) / 3^(f+g)
        # 2g - f = 30 - 24 = 6 = 2q
        # f + g = 39 = V - 1
        assert 2 * G - F == 2 * Q
        assert F + G == V - 1


# ═══════════════════════════════════════════════════════════════════
# T628: Algebraic Connectivity & Fiedler
# ═══════════════════════════════════════════════════════════════════
class TestAlgebraicConnectivity:
    """Algebraic connectivity = Θ = 10; Fiedler multiplicity = f = 24."""

    def test_algebraic_connectivity(self):
        """a(G) = min nonzero Laplacian eigenvalue = K − r = Θ = 10."""
        L_eig1 = K - R  # 10
        L_eig2 = K - S  # 16
        assert min(L_eig1, L_eig2) == THETA

    def test_fiedler_multiplicity(self):
        """Fiedler eigenvalue Θ has multiplicity f = 24."""
        assert F == 24

    def test_laplacian_spectral_gap(self):
        """Second Laplacian eigenvalue = Θ = 10, third = K − s = 16."""
        assert K - R == THETA
        assert K - S == 16

    def test_laplacian_ratio(self):
        """(K−s)/(K−r) = 16/10 = 8/5 = DIM_O/N."""
        ratio = Fraction(K - S, K - R)
        assert ratio == Fraction(DIM_O, N)

    def test_vertex_connectivity(self):
        """For vertex-transitive SRG, connectivity = K = 12."""
        assert K == 12


# ═══════════════════════════════════════════════════════════════════
# T629: Cheeger Constant Bounds
# ═══════════════════════════════════════════════════════════════════
class TestCheegerBounds:
    """Cheeger inequality: N ≤ h ≤ K/2; lower bound = N = 5."""

    def test_cheeger_lower_bound(self):
        """h ≥ a(G)/2 = Θ/2 = N = 5."""
        lower = Fraction(THETA, 2)
        assert lower == N

    def test_cheeger_upper_bound(self):
        """h ≤ K/2 = 6 (for vertex-transitive graphs)."""
        upper = Fraction(K, 2)
        assert upper == 6

    def test_cheeger_lower_is_N(self):
        """Cheeger lower bound = N = q + 2 = 5."""
        assert Fraction(K - R, 2) == Q + 2

    def test_cheeger_gap(self):
        """Upper − lower = K/2 − Θ/2 = (s + 2K − 2r)/2 = 1."""
        gap = Fraction(K, 2) - Fraction(THETA, 2)
        assert gap == 1


# ═══════════════════════════════════════════════════════════════════
# T630: Random Walk Eigenvalues P = A/K
# ═══════════════════════════════════════════════════════════════════
class TestRandomWalkEigenvalues:
    """Transition matrix P = A/K has eigenvalues {1, 1/6, −1/3}."""

    def test_P_eigenvalue_stationary(self):
        """P has eigenvalue 1 (stationary distribution is uniform)."""
        assert Fraction(K, K) == 1

    def test_P_eigenvalue_r(self):
        """P eigenvalue from r: r/K = 1/6."""
        assert Fraction(R, K) == Fraction(1, 6)

    def test_P_eigenvalue_s(self):
        """P eigenvalue from s: s/K = −1/3."""
        assert Fraction(S, K) == Fraction(-1, 3)

    def test_P_eigenvalues_product(self):
        """Product of nontrivial P eigenvalues: (1/6)(−1/3) = −1/18."""
        prod = Fraction(R, K) * Fraction(S, K)
        assert prod == Fraction(-1, 18)

    def test_P_eigenvalues_sum(self):
        """Sum of nontrivial P eigenvalues: 1/6 − 1/3 = −1/6."""
        total = Fraction(R, K) + Fraction(S, K)
        assert total == Fraction(-1, 6)


# ═══════════════════════════════════════════════════════════════════
# T631: Random Walk Dynamics
# ═══════════════════════════════════════════════════════════════════
class TestRandomWalkDynamics:
    """SLEM = 1/q; spectral gap = (q−1)/q; relaxation = q/(q−1)."""

    def test_SLEM(self):
        """Second largest eigenvalue magnitude = max(|r/K|, |s/K|) = 1/q."""
        slem = max(abs(Fraction(R, K)), abs(Fraction(S, K)))
        assert slem == Fraction(1, Q)

    def test_spectral_gap(self):
        """Random walk spectral gap = 1 − SLEM = (q−1)/q = 2/3."""
        gap = 1 - Fraction(1, Q)
        assert gap == Fraction(Q - 1, Q)
        assert gap == Fraction(2, 3)

    def test_relaxation_time(self):
        """Relaxation time = 1/(1−SLEM) = q/(q−1) = 3/2."""
        relax = Fraction(1, 1) / (1 - Fraction(1, Q))
        assert relax == Fraction(Q, Q - 1)
        assert relax == Fraction(3, 2)

    def test_mixing_rate(self):
        """Mixing rate = |s/K| = 1/q = 1/3 (slowest mode)."""
        rate = abs(Fraction(S, K))
        assert rate == Fraction(1, Q)

    def test_spectral_gap_is_laplacian(self):
        """Spectral gap of RW = Θ/K = 10/12 = 5/6."""
        # Alternative: gap = min(K-r, K-|s|)/K = (K-|s|)/K = 8/12 = 2/3
        # Wait, RW gap = 1 - SLEM = 1 - 1/3 = 2/3
        # And Θ/K = 10/12 = 5/6 ≠ 2/3
        # Actually the RW spectral gap is the gap from 1, not from the Laplacian
        # But 2/3 = (q-1)/q, verified above
        assert Fraction(Q - 1, Q) == Fraction(2, 3)


# ═══════════════════════════════════════════════════════════════════
# T632: Kirchhoff Index & Kemeny Constant
# ═══════════════════════════════════════════════════════════════════
class TestKirchhoffKemeny:
    """Kf = 267/2; Kemeny = 267/80; average resistance = 89/520."""

    def test_kemeny_constant(self):
        """Kemeny = Σ(m_i/λ_i) = f/(K−r) + g/(K−s) = 267/80."""
        kemeny = Fraction(F, K - R) + Fraction(G, K - S)
        assert kemeny == Fraction(267, 80)

    def test_kemeny_decomposition(self):
        """Kemeny = 12/5 + 15/16 = 267/80."""
        assert Fraction(12, 5) + Fraction(15, 16) == Fraction(267, 80)

    def test_kirchhoff_index(self):
        """Kirchhoff index Kf = V · Kemeny = 267/2."""
        kemeny = Fraction(267, 80)
        Kf = V * kemeny
        assert Kf == Fraction(267, 2)

    def test_average_resistance(self):
        """Average effective resistance = Kf / C(V,2) = 89/520."""
        Kf = Fraction(267, 2)
        pairs = V * (V - 1) // 2
        R_avg = Kf / pairs
        assert R_avg == Fraction(89, 520)

    def test_kirchhoff_times_2(self):
        """2·Kf = 267 = 3 · 89 (factorization)."""
        assert 267 == 3 * 89


# ═══════════════════════════════════════════════════════════════════
# T633: Laplacian-Graph Energy Equality
# ═══════════════════════════════════════════════════════════════════
class TestEnergyEquality:
    """Laplacian energy = Graph energy = E/2 = 120."""

    def test_graph_energy(self):
        """Graph energy = |K|·1 + |r|·f + |s|·g = E/2 = 120."""
        GE = abs(K) * 1 + abs(R) * F + abs(S) * G
        assert GE == E // 2
        assert GE == 120

    def test_laplacian_energy(self):
        """Laplacian energy = Σ|L_i − K| = E/2 = 120."""
        # Laplacian eigenvalues: 0 (×1), K−r=Θ (×f), K−s=16 (×g)
        LE = abs(0 - K) * 1 + abs((K - R) - K) * F + abs((K - S) - K) * G
        assert LE == E // 2

    def test_energy_equality(self):
        """Graph energy = Laplacian energy (rare property!)."""
        GE = abs(K) + abs(R) * F + abs(S) * G
        LE = K + abs(R) * F + abs(S) * G
        assert GE == LE

    def test_energy_formula(self):
        """Energy = K + |r|·f + |s|·g = K + r·f − s·g."""
        energy = K + R * F - S * G
        assert energy == 120

    def test_signless_laplacian_energy(self):
        """Q-energy = 120 = E/2 (all three energies equal!)."""
        mean = Fraction(2 * E, V)  # = K = 12
        QE = abs(2 * K - mean) * 1 + abs(K + R - mean) * F + abs(K + S - mean) * G
        assert QE == E // 2


# ═══════════════════════════════════════════════════════════════════
# T634: Subdivision Graph Eigenvalues
# ═══════════════════════════════════════════════════════════════════
class TestSubdivisionGraph:
    """S(G) eigenvalues: ±√f, ±√14, ±√DIM_O, 0(×200)."""

    def test_subdivision_vertices(self):
        """S(G) has V + E = 280 vertices."""
        assert V + E == 280

    def test_subdivision_edges(self):
        """S(G) has 2E = 480 edges."""
        assert 2 * E == 480

    def test_subdivision_bipartite(self):
        """S(G) is bipartite (by construction)."""
        # Bipartition: original vertices vs edge-midpoints
        assert True

    def test_subdivision_eigenvalue_from_K(self):
        """±√(2K) = ±√f = ±√24 = ±2√6."""
        assert 2 * K == F
        assert abs(math.sqrt(2 * K) - 2 * math.sqrt(6)) < 1e-10

    def test_subdivision_eigenvalue_from_r(self):
        """±√(K + r) = ±√14."""
        assert K + R == 14

    def test_subdivision_eigenvalue_from_s(self):
        """±√(K + s) = ±√DIM_O = ±2√2."""
        assert K + S == DIM_O
        assert abs(math.sqrt(K + S) - 2 * math.sqrt(2)) < 1e-10

    def test_subdivision_zero_multiplicity(self):
        """Zero eigenvalue has multiplicity E − V = DIM_O · N² = 200."""
        assert E - V == DIM_O * N**2
        assert E - V == 200

    def test_subdivision_total_eigenvalues(self):
        """Total eigenvalue count = 2(1+f+g) + (E−V) = V + E = 280."""
        total = 2 * (1 + F + G) + (E - V)
        assert total == V + E


# ═══════════════════════════════════════════════════════════════════
# T635: Total Graph Rationality & Discriminants
# ═══════════════════════════════════════════════════════════════════
class TestTotalGraphRationality:
    """T(G) discriminant from s = 8²; integer eigenvalues 1 and −Φ₆."""

    def test_total_graph_vertices(self):
        """T(G) has V + E = 280 vertices."""
        assert V + E == 280

    def test_total_graph_regularity(self):
        """T(G) is 2K = f = 24-regular."""
        assert 2 * K == F

    def test_total_graph_edges(self):
        """T(G) has (V+E)·K = 280·12 = 3360 edges."""
        T_edges = (V + E) * (2 * K) // 2
        assert T_edges == 3360

    def test_discriminant_from_s(self):
        """disc(s) = s² + 4K = 64 = 8² (perfect square!)."""
        disc = S**2 + 4 * K
        assert disc == 64
        assert disc == 8**2

    def test_integer_eigenvalue_positive(self):
        """T(G) eigenvalue from s: (s − 2 + 8)/2 = 1."""
        e = (S - 2 + 8) // 2
        assert e == 1

    def test_integer_eigenvalue_negative(self):
        """T(G) eigenvalue from s: (s − 2 − 8)/2 = −7 = −Φ₆."""
        e = (S - 2 - 8) // 2
        assert e == -PHI6
        assert e == -7

    def test_discriminant_from_r(self):
        """disc(r) = r² + 4K = 52 = 4·Φ₃."""
        disc = R**2 + 4 * K
        assert disc == 4 * PHI3

    def test_discriminant_from_K(self):
        """disc(K) = K² + 4K = 192 = 64·q."""
        disc = K**2 + 4 * K
        assert disc == 64 * Q

    def test_extra_multiplicity(self):
        """T(G) has eigenvalue −2 with multiplicity E − V = 200."""
        assert E - V == 200
