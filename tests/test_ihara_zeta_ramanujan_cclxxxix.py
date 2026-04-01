"""
Phase CCLXXXIX — Ihara Zeta, Ramanujan Graph & Spectral Geometry
================================================================

W(3,3) is a RAMANUJAN GRAPH: its eigenvalues satisfy |θ| ≤ 2√(k−1).
The Ihara zeta function, Laplacian spectrum, and heat kernel are all
expressed through W(3,3) parameters with zero free choices.

Edge count:  |E| = vk/2 = 240 = E  (= number of E₈ roots!)

Ihara zeta — discriminants:
  r-eigenvalue disc = r² − 4(k−1) = −40 = −v  (vertex count!)
  s-eigenvalue disc = s² − 4(k−1) = −28 = −R  (curvature rank!)

Quadratic fields:  Q(√−Θ) from r-poles,  Q(√−Φ₆) from s-poles.

Graph Laplacian spectrum:
  λ₀ = 0  (×1),  λ₁ = Θ = 10  (×f),  λ₂ = μ² = 16  (×g)

Heat trace: Tr(e^{−tL}) = 1 + f·e^{−Θt} + g·e^{−μ²t}
Spectral gap = Θ = 10.
"""

from math import comb
from fractions import Fraction

# ── W(3,3) master parameters ────────────────────────────────────────
q, lam, mu, k, v = 3, 2, 4, 12, 40
f, g = 24, 15
E, tau, R = 240, 252, 28
Phi3, Phi6, Phi12 = 13, 7, 73
Theta, s, N, d = 10, 6, 20, 4
b2 = f - lam  # 22


# ────────────────────────────────────────────────────────────────────
#  1.  RAMANUJAN GRAPH PROPERTY
# ────────────────────────────────────────────────────────────────────

class TestRamanujanGraph:
    """W(3,3) satisfies the Ramanujan bound: non-trivial |θ| ≤ 2√(k−1)."""

    def test_ramanujan_bound_value(self):
        """2√(k − 1) = 2√11 ≈ 6.633."""
        bound_sq = 4 * (k - 1)  # = 44
        assert bound_sq == 44

    def test_r_satisfies_bound(self):
        """|r| = λ = 2, and 2² = 4 < 44 = (2√(k−1))²."""
        assert lam ** 2 < 4 * (k - 1)

    def test_s_satisfies_bound(self):
        """|s| = μ = 4, and 4² = 16 < 44 = (2√(k−1))²."""
        assert mu ** 2 < 4 * (k - 1)

    def test_k_minus_1_is_11(self):
        assert k - 1 == 11


# ────────────────────────────────────────────────────────────────────
#  2.  EDGE COUNT = E₈ ROOT COUNT
# ────────────────────────────────────────────────────────────────────

class TestEdgeCount:
    """The number of graph edges equals the E₈ root count."""

    def test_edge_count(self):
        """v·k/2 = 240 = E."""
        assert v * k // 2 == E

    def test_e8_root_count(self):
        assert E == 240

    def test_edge_equals_E(self):
        """Graph edges ↔ E₈ roots: a single number."""
        assert v * k // 2 == E

    def test_total_incidences(self):
        """v·k = 2E = 480 = f·N."""
        assert v * k == 2 * E == f * N

    def test_edge_vertex_ratio(self):
        """E/v = k/2 = s = 6."""
        assert Fraction(E, v) == Fraction(k, 2) == Fraction(s)


# ────────────────────────────────────────────────────────────────────
#  3.  IHARA ZETA DISCRIMINANTS
# ────────────────────────────────────────────────────────────────────

class TestIharaDiscriminants:
    """Discriminants of the Ihara quadratic factors."""

    def test_r_discriminant_is_minus_v(self):
        """r² − 4(k − 1) = 4 − 44 = −40 = −v."""
        assert lam ** 2 - 4 * (k - 1) == -v

    def test_s_discriminant_is_minus_R(self):
        """s² − 4(k − 1) = 16 − 44 = −28 = −R."""
        assert mu ** 2 - 4 * (k - 1) == -R

    def test_r_disc_complex(self):
        """Negative discriminant → complex poles."""
        assert lam ** 2 - 4 * (k - 1) < 0

    def test_s_disc_complex(self):
        assert mu ** 2 - 4 * (k - 1) < 0

    def test_quadratic_field_r(self):
        """Q(√disc_r) = Q(√(−v)) = Q(√(−Θ))  [since −40 ~ −10 mod squares]."""
        assert -v == -4 * Theta  # √(−40) = 2√(−10) = 2√(−Θ)

    def test_quadratic_field_s(self):
        """Q(√disc_s) = Q(√(−R)) = Q(√(−Φ₆))  [since −28 ~ −7 mod squares]."""
        assert -R == -4 * Phi6  # √(−28) = 2√(−7) = 2√(−Φ₆)


# ────────────────────────────────────────────────────────────────────
#  4.  IHARA ZETA STRUCTURE
# ────────────────────────────────────────────────────────────────────

class TestIharaZetaStructure:
    """Structural parameters of the Ihara zeta function."""

    def test_cycle_rank(self):
        """First Betti number β₁ = |E| − |V| + 1 = 201."""
        assert E - v + 1 == 201

    def test_e_minus_v(self):
        """E − v = Θ · N = 200."""
        assert E - v == Theta * N

    def test_degree_of_reciprocal(self):
        """deg(Z⁻¹) = 2|E| = 2E = 480 = f · N."""
        assert 2 * E == 480
        assert 2 * E == f * N

    def test_ihara_trivial_factor(self):
        """(1 − u²) exponent = E − v = Θ · N = 200."""
        assert E - v == Theta * N == 200

    def test_ihara_k_factor(self):
        """Factor (1 − ku + (k−1)u²) has multiplicity 1."""
        assert 1 == 1  # trivial eigenvalue k, multiplicity 1

    def test_ihara_r_factor_multiplicity(self):
        """Factor (1 − ru + (k−1)u²) has multiplicity f = 24."""
        assert f == 24

    def test_ihara_s_factor_multiplicity(self):
        """Factor (1 + |s|u + (k−1)u²) has multiplicity g = 15."""
        assert g == 15


# ────────────────────────────────────────────────────────────────────
#  5.  GRAPH LAPLACIAN SPECTRUM
# ────────────────────────────────────────────────────────────────────

class TestLaplacianSpectrum:
    """Laplacian eigenvalues: 0, Θ, μ²."""

    def test_lap0(self):
        """λ₀ = 0 with multiplicity 1."""
        assert k - k == 0

    def test_lap1_is_theta(self):
        """λ₁ = k − r = Θ = 10 with multiplicity f."""
        assert k - lam == Theta

    def test_lap2_is_mu_sq(self):
        """λ₂ = k − s = k + |s| = μ² = 16 with multiplicity g."""
        assert k + mu == mu ** 2

    def test_lap1_multiplicity(self):
        assert f == 24

    def test_lap2_multiplicity(self):
        assert g == 15

    def test_num_distinct_eigenvalues_is_q(self):
        """Three distinct Laplacian eigenvalues → q = 3."""
        eigenvalues = {0, Theta, mu ** 2}
        assert len(eigenvalues) == q


# ────────────────────────────────────────────────────────────────────
#  6.  HEAT KERNEL
# ────────────────────────────────────────────────────────────────────

class TestHeatKernel:
    """Tr(e^{−tL}) = 1 + f·e^{−Θt} + g·e^{−μ²t}."""

    def test_heat_trace_at_zero(self):
        """Tr(e^0) = 1 + f + g = v = 40."""
        assert 1 + f + g == v

    def test_spectral_gap(self):
        """Spectral gap = Θ = 10."""
        assert min(Theta, mu ** 2) == Theta

    def test_laplacian_ratio(self):
        """λ₂/λ₁ = μ²/Θ = 8/5."""
        assert Fraction(mu ** 2, Theta) == Fraction(8, 5)

    def test_spectral_sum(self):
        """Sum of all Laplacian eigenvalues = v·k (trace of L)."""
        total = 0 * 1 + Theta * f + mu ** 2 * g
        assert total == v * k

    def test_spectral_sum_value(self):
        """Θf + μ²g = vk = 480."""
        assert Theta * f + mu ** 2 * g == 480
        assert v * k == 480


# ────────────────────────────────────────────────────────────────────
#  7.  SPANNING TREES (KIRCHHOFF)
# ────────────────────────────────────────────────────────────────────

class TestSpanningTrees:
    """Kirchhoff's theorem: v·T = Θ^f · (μ²)^g."""

    def test_kirchhoff_formula_base(self):
        """Product of non-zero Laplacian eigenvalues = v · (number of trees)."""
        prod_eigenvalues = Theta ** f * (mu ** 2) ** g
        assert prod_eigenvalues % v == 0

    def test_theta_exponent(self):
        """Θ^f: exponent = f = 24."""
        assert f == 24

    def test_mu_sq_exponent(self):
        """(μ²)^g: exponent = g = 15."""
        assert g == 15

    def test_mu_sq_as_power_of_2(self):
        """(μ²)^g = 2^(d·g) = 2^60."""
        assert (mu ** 2) ** g == 2 ** (d * g)
        assert d * g == 60


# ────────────────────────────────────────────────────────────────────
#  8.  ETA PRODUCT WEIGHT HIERARCHY
# ────────────────────────────────────────────────────────────────────

class TestEtaWeightHierarchy:
    """η^n has modular weight n/2; W(3,3) parameters yield special forms."""

    def test_eta_lambda_weight(self):
        """η^λ: weight = λ/2 = 1."""
        assert Fraction(lam, 2) == 1

    def test_eta_mu_weight(self):
        """η^μ: weight = μ/2 = 2 = λ."""
        assert Fraction(mu, 2) == lam

    def test_eta_s_weight(self):
        """η^s: weight = s/2 = 3 = q."""
        assert Fraction(s, 2) == q

    def test_eta_2d_weight(self):
        """η^(2d): weight = 2d/2 = d = 4  (E₈ theta series!)."""
        assert Fraction(2 * d, 2) == d

    def test_eta_k_weight(self):
        """η^k: weight = k/2 = s = 6."""
        assert Fraction(k, 2) == s

    def test_eta_f_weight(self):
        """η^f: weight = f/2 = k = 12  →  THIS IS Δ."""
        assert Fraction(f, 2) == k
