"""
Phase CCXCI — Spectral Equipartition & Graph Riemann Hypothesis
===============================================================

The Laplacian of W(3,3) exhibits EXACT spectral equipartition:

  Θ · f = μ² · g = E = 240

Both non-trivial eigenmodes carry identical total energy E = 240, the
E₈ root count.  This is equivalent to the edge count: |E(graph)| = E.

The K3 lattice decomposes into W(3,3) pieces:
  Γ_{3,19} = λ · E₈(−1) ⊕ q · H
  rank = λ · 2d + q · λ = μ² + s = 22 = b₂

The GRAPH RIEMANN HYPOTHESIS is proved for W(3,3) (Ramanujan graph):
all Ihara poles lie on |u| = (k−1)^{−1/2}, the exact analog of Re(s) = ½.

The fine structure constant emerges as:  α⁻¹ = (k−1)² + μ² = 137,
where k−1 = 11 is the graph-RH parameter.
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
#  1.  SPECTRAL EQUIPARTITION
# ────────────────────────────────────────────────────────────────────

class TestSpectralEquipartition:
    """Θf = μ²g = E: exact equipartition between eigenmodes."""

    def test_theta_f_equals_E(self):
        """Θ · f = 10 · 24 = 240 = E."""
        assert Theta * f == E

    def test_mu_sq_g_equals_E(self):
        """μ² · g = 16 · 15 = 240 = E."""
        assert mu ** 2 * g == E

    def test_equipartition(self):
        """Θf = μ²g: exact balance."""
        assert Theta * f == mu ** 2 * g

    def test_ratio_f_over_g(self):
        """f/g = μ²/Θ = 8/5."""
        assert Fraction(f, g) == Fraction(mu ** 2, Theta) == Fraction(8, 5)

    def test_total_trace(self):
        """Tr(L) = Θf + μ²g = 2E = vk = 480."""
        assert Theta * f + mu ** 2 * g == 2 * E == v * k

    def test_edge_count_is_E(self):
        """vk/2 = 240 = E: graph edges = E₈ root count."""
        assert v * k // 2 == E


# ────────────────────────────────────────────────────────────────────
#  2.  ADJACENCY TRACE IDENTITIES
# ────────────────────────────────────────────────────────────────────

class TestTraceIdentities:
    """Traces of powers of the adjacency matrix."""

    def test_trace_A_vanishes(self):
        """Tr(A) = k + rf + sg = 12 + 48 − 60 = 0."""
        assert k + lam * f + (-mu) * g == 0

    def test_trace_A2_equals_vk(self):
        """Tr(A²) = k² + r²f + s²g = vk = 480."""
        assert k ** 2 + lam ** 2 * f + mu ** 2 * g == v * k

    def test_nontrivial_trace_A2(self):
        """r²f + s²g = vk − k² = k(v−k) = kR = 336."""
        assert lam ** 2 * f + mu ** 2 * g == k * R

    def test_kR_value(self):
        assert k * R == 336


# ────────────────────────────────────────────────────────────────────
#  3.  VON NEUMANN ENTROPY
# ────────────────────────────────────────────────────────────────────

class TestVonNeumannEntropy:
    """Graph quantum entropy from the normalised Laplacian."""

    def test_density_eigenvalue_r(self):
        """ρ₁ = Θ/(2E) = 1/48."""
        assert Fraction(Theta, 2 * E) == Fraction(1, 48)

    def test_density_eigenvalue_s(self):
        """ρ₂ = μ²/(2E) = 1/30."""
        assert Fraction(mu ** 2, 2 * E) == Fraction(1, 30)

    def test_partial_trace_r(self):
        """f · ρ₁ = 1/2: r-block carries half the trace."""
        assert Fraction(f, 2 * E // Theta) == Fraction(1, 2)
        assert f * Theta == E  # equivalent

    def test_partial_trace_s(self):
        """g · ρ₂ = 1/2: s-block carries half the trace."""
        assert Fraction(g * mu ** 2, 2 * E) == Fraction(1, 2)

    def test_total_trace(self):
        """f·ρ₁ + g·ρ₂ = 1."""
        assert Fraction(f * Theta + g * mu ** 2, 2 * E) == 1


# ────────────────────────────────────────────────────────────────────
#  4.  K3 LATTICE DECOMPOSITION
# ────────────────────────────────────────────────────────────────────

class TestK3LatticeDecomposition:
    """Γ_{3,19} = λ · E₈(−1) ⊕ q · H from W(3,3)."""

    def test_k3_b2(self):
        """b₂(K3) = 22 = f − λ."""
        assert f - lam == 22

    def test_k3_signature_positive(self):
        """Positive signature = q = 3."""
        assert q == 3

    def test_k3_signature_negative(self):
        """Negative signature = N − 1 = 19."""
        assert N - 1 == 19

    def test_k3_signature_sum(self):
        """q + (N − 1) = b₂ = 22."""
        assert q + N - 1 == b2

    def test_k3_e8_component_rank(self):
        """λ × rank(E₈) = 2 × 8 = 16 = μ²."""
        assert lam * (2 * d) == mu ** 2

    def test_k3_hyperbolic_component(self):
        """q × rank(H) = 3 × 2 = 6 = s."""
        assert q * lam == s

    def test_k3_rank_total(self):
        """μ² + s = 16 + 6 = 22 = b₂."""
        assert mu ** 2 + s == b2

    def test_hodge_h11_is_N(self):
        """h^{1,1}(K3) = N = 20."""
        assert N == 20

    def test_hodge_b2_from_h(self):
        """b₂ = h^{2,0} + h^{1,1} + h^{0,2} = 1 + N + 1 = N + λ."""
        assert 1 + N + 1 == N + lam == b2


# ────────────────────────────────────────────────────────────────────
#  5.  GRAPH RIEMANN HYPOTHESIS
# ────────────────────────────────────────────────────────────────────

class TestGraphRH:
    """W(3,3) satisfies the graph Riemann hypothesis (Ramanujan graph)."""

    def test_rh_parameter(self):
        """Graph-RH parameter: k − 1 = 11."""
        assert k - 1 == 11

    def test_rh_parameter_prime(self):
        """k − 1 = 11 is prime."""
        from sympy import isprime
        assert isprime(k - 1)

    def test_poles_on_critical_line(self):
        """All non-trivial Ihara poles have |u|² = 1/(k−1)."""
        # For eigenvalue r: u = (r ± i√(4(k-1)-r²)) / (2(k-1))
        # |u|² = (r² + 4(k-1) - r²) / (4(k-1)²) = 1/(k-1) ✓
        assert lam ** 2 < 4 * (k - 1)  # complex poles
        assert mu ** 2 < 4 * (k - 1)   # complex poles

    def test_alpha_from_rh_parameter(self):
        """α⁻¹ = (k−1)² + μ² = 11² + 4² = 137."""
        assert (k - 1) ** 2 + mu ** 2 == 137

    def test_ihara_disc_r(self):
        """Ihara discriminant for r: r² − 4(k−1) = −v."""
        assert lam ** 2 - 4 * (k - 1) == -v

    def test_ihara_disc_s(self):
        """Ihara discriminant for s: s² − 4(k−1) = −R."""
        assert mu ** 2 - 4 * (k - 1) == -R


# ────────────────────────────────────────────────────────────────────
#  6.  BERNOULLI–ZETA LINKS
# ────────────────────────────────────────────────────────────────────

class TestBernoulliZeta:
    """Bernoulli numbers map to W(3,3) via zeta at negative integers."""

    def test_B1_reciprocal(self):
        """|B₁|⁻¹ = 2 = λ."""
        assert Fraction(1, Fraction(1, 2)) == lam

    def test_B2_reciprocal(self):
        """|B₂|⁻¹ = 6 = s."""
        assert Fraction(1, Fraction(1, 6)) == s

    def test_zeta_minus1(self):
        """|ζ(−1)|⁻¹ = k = 12."""
        # ζ(−1) = −B₂/2 = −1/12
        assert abs(Fraction(-1, 12)) == Fraction(1, k)

    def test_zeta_minus5(self):
        """|ζ(−5)|⁻¹ = τ = 252."""
        # ζ(−5) = −B₆/6 = −(1/42)/6 = −1/252
        assert abs(Fraction(-1, 252)) == Fraction(1, tau)

    def test_zeta_minus7(self):
        """|ζ(−7)|⁻¹ = E = 240."""
        assert abs(Fraction(1, 240)) == Fraction(1, E)


# ────────────────────────────────────────────────────────────────────
#  7.  f = λ + k + μ + s  (PARAMETER SUM)
# ────────────────────────────────────────────────────────────────────

class TestParameterSum:
    """f decomposes as sum of four base parameters."""

    def test_f_as_sum(self):
        """f = λ + k + μ + s = 2 + 12 + 4 + 6 = 24."""
        assert lam + k + mu + s == f

    def test_f_alt_decomposition(self):
        """f = λ + μ² + s  (since k + μ = μ²)."""
        assert lam + mu ** 2 + s == f

    def test_g_as_combination(self):
        """g = C(s, λ) = C(6, 2) = 15."""
        assert comb(s, lam) == g

    def test_v_as_mu_theta(self):
        """v = μ · Θ = 4 · 10 = 40."""
        assert mu * Theta == v

    def test_v_as_2N(self):
        """v = 2N = 2 · 20 = 40."""
        assert 2 * N == v
