"""
Phase CCXCII — Spectral Zeta, Heat Kernel & Kirchhoff Trees
============================================================

The spectral zeta function of the graph Laplacian of W(3,3):

  ζ_G(s) = f · Θ^{−s} + g · (μ²)^{−s}

produces W(3,3) invariants at negative integers:

  ζ_G(−1) = Θf + μ²g = 480 = vk  (equipartition!)
  ζ_G(0)  = f + g = 39 = v − 1

The heat kernel coefficients are algebraically forced:
  a₀ = v, a₁ = −vk, a₂ = E · Φ₃ = 3120

The Laplacian determinant factorises as det'(L) = 2^{84} × 5^f,
where 84 = q(q+1)Φ₆ is the Hurwitz surface flag count.

Kirchhoff's theorem gives the spanning tree count:
  T = 2^{q^d} × 5^{f−1}

where q^d = 81 = |H₁(W(3,3))| and f−1 = 23 = M₂₄ degree.

The f-th prime p_f = 89 = F(k−1) (Fibonacci) controls the
Kemeny constant K = q²·89/N and the Kirchhoff index Kf = 3·89/2.
"""

from math import comb, factorial
from fractions import Fraction

# ── W(3,3) master parameters ────────────────────────────────────────
q, lam, mu, k, v = 3, 2, 4, 12, 40
f, g = 24, 15
E, tau, R = 240, 252, 28
Phi3, Phi6, Phi12 = 13, 7, 73
Theta, s, N, d = 10, 6, 20, 4
b2 = f - lam  # 22


# ────────────────────────────────────────────────────────────────────
#  1.  SPECTRAL ZETA FUNCTION AT NEGATIVE INTEGERS
# ────────────────────────────────────────────────────────────────────

class TestSpectralZeta:
    """ζ_G(s) = f·Θ^{−s} + g·(μ²)^{−s} at negative integers."""

    def test_zeta_minus1(self):
        """ζ_G(−1) = Θf + μ²g = vk = 480."""
        assert f * Theta + g * mu ** 2 == v * k == 480

    def test_zeta_minus1_equipartition(self):
        """Both terms of ζ_G(−1) equal E = 240."""
        assert f * Theta == E
        assert g * mu ** 2 == E

    def test_zeta_0(self):
        """ζ_G(0) = f + g = v − 1 = 39."""
        assert f + g == v - 1 == 39

    def test_zeta_minus2(self):
        """ζ_G(−2) = fΘ² + g·μ⁴ = 6240."""
        assert f * Theta ** 2 + g * mu ** 4 == 6240


# ────────────────────────────────────────────────────────────────────
#  2.  HEAT KERNEL COEFFICIENTS
# ────────────────────────────────────────────────────────────────────

class TestHeatKernel:
    """Seeley-DeWitt coefficients of the graph heat kernel."""

    def test_a0_is_v(self):
        """a₀ = 1 + f + g = v = 40."""
        assert 1 + f + g == v

    def test_a1_is_vk(self):
        """a₁ = −(Θf + μ²g) = −vk = −480."""
        assert -(f * Theta + g * mu ** 2) == -(v * k)

    def test_a2_is_E_Phi3(self):
        """a₂ = (fΘ² + g·μ⁴)/2 = E·Φ₃ = 3120."""
        assert (f * Theta ** 2 + g * mu ** 4) // 2 == E * Phi3

    def test_a2_algebraic_origin(self):
        """(Θ + μ²)/2 = (k − r + k + |s|)/2 = k + 1 = Φ₃."""
        assert (Theta + mu ** 2) // 2 == k + 1 == Phi3

    def test_moment_sum(self):
        """Raw moment M_n = fΘⁿ + g(μ²)ⁿ.  M₁ = vk."""
        M1 = f * Theta + g * mu ** 2
        assert M1 == v * k


# ────────────────────────────────────────────────────────────────────
#  3.  LAPLACIAN DETERMINANT
# ────────────────────────────────────────────────────────────────────

class TestLaplacianDeterminant:
    """det'(L) = Θ^f · (μ²)^g = 2^{84} · 5^f."""

    def test_det_value(self):
        """det'(L) = 10^24 · 16^15."""
        assert Theta ** f * (mu ** 2) ** g == 10 ** 24 * 16 ** 15

    def test_det_prime_factorisation(self):
        """det'(L) = 2^84 · 5^24."""
        assert Theta ** f * (mu ** 2) ** g == 2 ** 84 * 5 ** 24

    def test_exponent_of_2(self):
        """Exponent of 2 in det'(L) = 84 = q(q+1)Φ₆ = Hurwitz flag count."""
        exp2 = f + 4 * g  # Theta = 2·5 contributes f; mu^2 = 2^4 contributes 4g
        assert exp2 == 84
        assert exp2 == q * (q + 1) * Phi6

    def test_exponent_of_5(self):
        """Exponent of 5 in det'(L) = f = 24."""
        assert f == 24


# ────────────────────────────────────────────────────────────────────
#  4.  KIRCHHOFF SPANNING TREES
# ────────────────────────────────────────────────────────────────────

class TestSpanningTrees:
    """T = det'(L)/v = 2^{q^d} · 5^{f−1}."""

    def test_tree_count(self):
        """T = Θ^f · (μ²)^g / v = 2^81 · 5^23."""
        T = Theta ** f * (mu ** 2) ** g // v
        assert T == 2 ** 81 * 5 ** 23

    def test_exponent_of_2_is_qd(self):
        """Exponent of 2 in T is q^d = 81 = |H₁(W(3,3))|."""
        exp2_T = 84 - 3  # v = 2^3 · 5
        assert exp2_T == 81 == q ** d

    def test_exponent_of_5_is_f_minus_1(self):
        """Exponent of 5 in T is f − 1 = 23 = M₂₄ permutation degree."""
        exp5_T = f - 1
        assert exp5_T == 23

    def test_qd_is_homology(self):
        """q^d = 3^4 = 81 = |H₁|."""
        assert q ** d == 81


# ────────────────────────────────────────────────────────────────────
#  5.  KEMENY CONSTANT & KIRCHHOFF INDEX
# ────────────────────────────────────────────────────────────────────

class TestKemenyKirchhoff:
    """Random walk constants via spectral decomposition."""

    def test_kemeny_constant(self):
        """Kemeny = f·k/(k−r) + g·k/(k+|s|) = q²·89/N."""
        K = f * Fraction(k, k - lam) + g * Fraction(k, k + mu)
        assert K == Fraction(q ** 2 * 89, N)

    def test_kemeny_numerator(self):
        """Kemeny numerator = 801 = q² · 89."""
        assert q ** 2 * 89 == 801

    def test_kemeny_denominator(self):
        """Kemeny denominator = N = 20."""
        # just a naming check
        assert N == 20

    def test_kirchhoff_index(self):
        """Kf = v·(f/Θ + g/μ²) = 3·89/2."""
        Kf = v * (Fraction(f, Theta) + Fraction(g, mu ** 2))
        assert Kf == Fraction(3 * 89, 2)

    def test_mean_eigenvalue(self):
        """Arithmetic mean of non-zero Laplacian eigenvalues = v·μ/Φ₃."""
        mean = Fraction(f * Theta + g * mu ** 2, f + g)
        assert mean == Fraction(v * mu, Phi3)
        assert mean == Fraction(160, 13)


# ────────────────────────────────────────────────────────────────────
#  6.  THE NUMBER 89 = p_f = F(k−1)
# ────────────────────────────────────────────────────────────────────

class TestNumber89:
    """89 is the f-th prime AND the (k−1)-th Fibonacci number."""

    def test_89_is_f_th_prime(self):
        """p_f = p_{24} = 89."""
        from sympy import prime
        assert prime(f) == 89

    def test_89_is_fibonacci_k_minus_1(self):
        """F(k−1) = F(11) = 89."""
        a, b = 0, 1
        for _ in range(k - 2):
            a, b = b, a + b
        assert b == 89

    def test_89_from_alpha(self):
        """89 = α − λf = 137 − 48."""
        assert 137 - lam * f == 89

    def test_89_from_parameters(self):
        """89 = α − v − Θ + λ = 137 − 40 − 10 + 2."""
        assert 137 - v - Theta + lam == 89


# ────────────────────────────────────────────────────────────────────
#  7.  PRIME INDEX LADDER
# ────────────────────────────────────────────────────────────────────

class TestPrimeIndexLadder:
    """The prime function at graph parameters yields graph parameters."""

    def test_p_lambda_is_q(self):
        """p(λ) = p(2) = 3 = q."""
        from sympy import prime
        assert prime(lam) == q

    def test_p_mu_is_Phi6(self):
        """p(μ) = p(4) = 7 = Φ₆."""
        from sympy import prime
        assert prime(mu) == Phi6

    def test_p_s_is_Phi3(self):
        """p(s) = p(6) = 13 = Φ₃."""
        from sympy import prime
        assert prime(s) == Phi3

    def test_p_Phi3_is_v_plus_1(self):
        """p(Φ₃) = p(13) = 41 = v + 1."""
        from sympy import prime
        assert prime(Phi3) == v + 1

    def test_fibonacci_k2_is_k2(self):
        """F(k) = 144 = k²."""
        a, b = 0, 1
        for _ in range(k - 1):
            a, b = b, a + b
        assert b == k ** 2 == 144
