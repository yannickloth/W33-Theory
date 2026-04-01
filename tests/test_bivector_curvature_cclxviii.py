"""
Phase CCLXVIII — Bivector–Curvature 4D Bridge
=================================================

THEOREM (Curvature-Dimensional Landing):

At q=3, μ = q+1 = 4 (the spacetime dimension), and:

  s = k/λ = 6 = dim Λ²(R⁴)               (bivector space)
  N = λΦ₄ = 20 = dim Riem_alg(R⁴)        (algebraic curvature tensor)

The refinement root 120 = s·N = 6·20 is exactly the product of
the 4D bivector dimension and the 4D algebraic Riemann curvature dimension.

SELECTORS (both vanish uniquely at q=3):

  s − C(μ,2) = −q(q−3)(q+1) / [2(q−1)]
  N − μ²(μ²−1)/12 = −(q−3)(q³−5q²+2q−4)/12

SPECTRAL-ACTION COEFFICIENTS:
  a₀  = f·N  = 24·20 = 480         (or 4!·N)
  c_EH = N·μ² = 20·16 = 320        (or 2⁴·N)
  a₂  = Φ₆·c_EH = 7·320 = 2240
  c₆  = qΦ₃·c_EH = 39·320 = 12480
  a₄  = 5(k−1)·c_EH = 55·320 = 17600

SOURCES: W33_curvature_bivector_completion_20260331.zip,
         W33_unique_twoscale_completion_20260331.zip
"""
import math
import pytest

# ── W(3,3) parameters ──
q    = 3
v    = 40
k    = 12
lam  = 2
mu   = 4   # = q+1 = spacetime dimension!
f    = 24
g    = 15
Phi3 = q**2 + q + 1   # 13
Phi4 = q**2 + 1        # 10
Phi6 = q**2 - q + 1    #  7

# ── Derived ──
s    = k // lam                     # 6
N    = lam * Phi4                   # 20

# ── Spectral-action data ──
a0   = 480
c_EH = 320
a2   = 2240
c6   = 12480
a4   = 17600


# ================================================================
# T1: Spacetime dimension μ = q+1 = 4
# ================================================================
class TestT1_SpacetimeDim:
    """μ = q+1 = 4 is the spacetime dimension."""

    def test_mu_is_4(self):
        assert mu == 4

    def test_mu_is_q_plus_1(self):
        assert mu == q + 1


# ================================================================
# T2: Bivector and Riemann dimensions
# ================================================================
class TestT2_GeometricDims:
    """s = dim Λ²(R⁴), N = dim Riem_alg(R⁴)."""

    def test_s_is_bivector_dim(self):
        """dim Λ²(R⁴) = C(4,2) = 6."""
        assert s == math.comb(mu, 2)

    def test_N_is_riemann_dim(self):
        """dim Riem_alg(R⁴) = μ²(μ²−1)/12 = 4²·15/12 = 20."""
        riem = mu**2 * (mu**2 - 1) // 12
        assert riem == N

    def test_N_formula(self):
        """Standard formula: dim Riem_alg(R^d) = d²(d²−1)/12."""
        assert N == 20

    def test_refinement_root(self):
        """120 = s·N = 6·20."""
        assert s * N == 120

    def test_not_isotropic(self):
        """120 ≠ 6² = 36: no single-scale 4D limit."""
        assert s * N != s**2


# ================================================================
# T3: Selectors vanish uniquely at q=3
# ================================================================
class TestT3_Selectors:
    """Both selectors have a (q-3) factor."""

    def test_bivector_selector(self):
        """s − C(μ,2) vanishes at q=3."""
        selector = s - math.comb(mu, 2)
        assert selector == 0

    def test_riemann_selector(self):
        """N − μ²(μ²−1)/12 vanishes at q=3."""
        selector = N - mu**2 * (mu**2 - 1) // 12
        assert selector == 0

    def test_selector_polynomial_bivector(self):
        """−q(q−3)(q+1)/[2(q−1)] = 0 at q=3."""
        num = -q * (q - 3) * (q + 1)
        assert num == 0

    def test_selector_polynomial_riemann(self):
        """−(q−3)(q³−5q²+2q−4)/12 = 0 at q=3."""
        num = -(q - 3) * (q**3 - 5*q**2 + 2*q - 4)
        assert num == 0


# ================================================================
# T4: Spectral-action coefficients via N and μ²
# ================================================================
class TestT4_SpectralAction:
    """All coefficients factor through N=20 and/or μ²=16."""

    def test_a0_via_f(self):
        """a₀ = f·N = 24·20 = 480."""
        assert f * N == a0

    def test_a0_via_factorial(self):
        """a₀ = μ!·N = 4!·20 = 480."""
        assert math.factorial(mu) * N == a0

    def test_c_EH_via_mu2(self):
        """c_EH = μ²·N = 16·20 = 320."""
        assert mu**2 * N == c_EH

    def test_c_EH_via_clifford(self):
        """c_EH = 2^μ · N = 16·20 = 320."""
        assert 2**mu * N == c_EH

    def test_mu2_equals_2mu(self):
        """At μ=4: μ² = 2^μ = 16 (coincidence!)."""
        assert mu**2 == 2**mu

    def test_a2(self):
        """a₂ = Φ₆·c_EH = 7·320 = 2240."""
        assert Phi6 * c_EH == a2

    def test_c6(self):
        """c₆ = q·Φ₃·c_EH = 3·13·320 = 12480."""
        assert q * Phi3 * c_EH == c6

    def test_a4(self):
        """a₄ = 5(k−1)·c_EH = 55·320 = 17600."""
        assert 5 * (k - 1) * c_EH == a4


# ================================================================
# T5: Coefficient ratios
# ================================================================
class TestT5_Ratios:
    """Clean ratio tower among coefficients."""

    def test_c_EH_over_a0(self):
        """c_EH/a₀ = μ²/f = 16/24 = 2/3 = 2/q."""
        assert c_EH * q == a0 * 2

    def test_a2_over_a0(self):
        """a₂/a₀ = Φ₆·μ²/f = 7·16/24 = 14/3."""
        assert a2 * 3 == a0 * 14

    def test_a4_over_a2(self):
        """a₄/a₂ = 5(k−1)/Φ₆ = 55/7."""
        assert a4 * 7 == a2 * 55

    def test_a4_over_a0(self):
        """a₄/a₀ = 5(k−1)·μ²/f = 55·16/24 = 110/3."""
        assert a4 * 3 == a0 * 110


# ================================================================
# T6: N = v/2 selector
# ================================================================
class TestT6_NHalfV:
    """N − v/2 = (q−3)(q²+1)/2 = 0 at q=3."""

    def test_N_is_v_half(self):
        assert N == v // 2

    def test_selector(self):
        assert (q - 3) * (q**2 + 1) // 2 == 0
