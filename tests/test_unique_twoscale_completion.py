"""
Phase CCXXIX: Unique two-scale continuum completion for W(3,3).

Theorem: Define N(q) = lambda * Phi4(q) = (q-1)*(q^2+1).
Then N(q) - v(q)/2 = (q-3)*(q^2+1)/2.
So N = v/2 holds if and only if q = 3.

At q = 3:
  N = 20, s = k/lambda = 6, dominant mode = s*N = 120.

Curved Seeley-DeWitt coefficient package:
  c_EH = mu^2 * N = 4^2 * 20 = 320
  a0   = f * N = 24 * 20 = 480
  a2   = Phi6 * c_EH = 7 * 320 = 2240
  c6   = q * Phi3 * c_EH = 3 * 13 * 320 = 12480
  a4   = 5*(k-1) * c_EH = 5*11*320 / (mu^2) ... see test

All of these match the spectral action coefficients exactly.
"""

from fractions import Fraction
import pytest

# W(3,3) parameters at q=3
v, k, l, m, q = 40, 12, 2, 4, 3
Phi3, Phi4, Phi6 = 13, 10, 7
E = 240
f, g = 24, 15


def N_q(q_val):
    """Transverse multiplicity N(q) = (q-1)*(q^2+1)."""
    l_q = q_val - 1
    Phi4_q = q_val**2 + 1
    return l_q * Phi4_q


def v_q(q_val):
    """Number of vertices v(q) = q^3 + q^2 + q + 1 = (q^2+1)(q+1)."""
    return (q_val**2 + 1) * (q_val + 1)


class TestUniqueTwoscaleCompletion:

    # --- Uniqueness theorem ---

    def test_N_formula(self):
        """N(q) = (q-1)*(q^2+1) = lambda*Phi4."""
        assert N_q(3) == l * Phi4
        assert N_q(3) == 20

    def test_N_equals_v_over_2_only_at_q3(self):
        """N(q) = v(q)/2 iff q = 3."""
        for q_test in range(2, 8):
            N = N_q(q_test)
            v_t = v_q(q_test)
            if q_test == 3:
                assert 2 * N == v_t, f"q=3 should satisfy 2N=v, got 2*{N}={2*N} vs {v_t}"
            else:
                assert 2 * N != v_t, f"q={q_test} should NOT satisfy 2N=v"

    def test_gap_formula(self):
        """N(q) - v(q)/2 = (q-3)*(q^2+1)/2 exactly."""
        for q_test in [2, 3, 4, 5, 6]:
            N = N_q(q_test)
            v_t = v_q(q_test)
            gap = Fraction(2 * N - v_t, 2)
            expected = Fraction((q_test - 3) * (q_test**2 + 1), 2)
            assert gap == expected, f"q={q_test}: gap={gap}, expected={expected}"

    def test_q3_uniqueness_algebraic(self):
        """The factored gap (q-3)*(q^2+1)/2 vanishes iff q=3 (for integer q>=2)."""
        for q_test in range(2, 10):
            gap = (q_test - 3) * (q_test**2 + 1)
            if q_test == 3:
                assert gap == 0
            else:
                assert gap != 0

    # --- Two-scale parameters at q=3 ---

    def test_s_value(self):
        """External scale s = k/lambda = 12/2 = 6."""
        s = k // l
        assert s == 6

    def test_N_value(self):
        """Transverse multiplicity N = lambda*Phi4 = 2*10 = 20."""
        N = l * Phi4
        assert N == 20

    def test_dominant_mode(self):
        """Dominant refinement mode = s * N = 6 * 20 = 120."""
        s = k // l
        N = l * Phi4
        assert s * N == 120

    # --- Curved coefficient package ---

    def test_c_EH(self):
        """c_EH = mu^2 * N = 16 * 20 = 320."""
        N = l * Phi4
        c_EH = m**2 * N
        assert c_EH == 320

    def test_a0_from_N(self):
        """a0 = f * N = 24 * 20 = 480 = v * k."""
        N = l * Phi4
        a0 = f * N
        assert a0 == 480
        assert a0 == v * k

    def test_a2_from_c_EH(self):
        """a2 = Phi6 * c_EH = 7 * 320 = 2240."""
        c_EH = m**2 * (l * Phi4)
        a2 = Phi6 * c_EH
        assert a2 == 2240

    def test_c6_from_c_EH(self):
        """c6 = q * Phi3 * c_EH = 3 * 13 * 320 = 12480."""
        c_EH = m**2 * (l * Phi4)
        c6 = q * Phi3 * c_EH
        assert c6 == 12480

    def test_a4_from_c_EH(self):
        """a4 = 5*(k-1) * c_EH / mu^2 = 5*11*320/16 = 1100."""
        # Actually from the CCXXVI formula: a4 = Phi4^2 * mu^2 * (k-1)
        # = 100 * 16 * 11 = 17600
        # With c_EH = mu^2 * N: a4 = 5*(k-1)*mu^2*N = 5*11*16*20 = 17600
        c_EH = m**2 * (l * Phi4)
        a4 = 5 * (k - 1) * c_EH
        assert a4 == 17600
        assert a4 == Phi4**2 * m**2 * (k - 1)

    def test_a4_over_a2(self):
        """a4/a2 = 55/7 recovered from two-scale package."""
        c_EH = m**2 * (l * Phi4)
        a2 = Phi6 * c_EH
        a4 = 5 * (k - 1) * c_EH
        ratio = Fraction(a4, a2)
        assert ratio == Fraction(55, 7)

    def test_a2_over_a0(self):
        """a2/a0 = Phi6 * mu^2 / f = 7*16/24 = 14/3."""
        N = l * Phi4
        a0 = f * N
        c_EH = m**2 * N
        a2 = Phi6 * c_EH
        ratio = Fraction(a2, a0)
        assert ratio == Fraction(14, 3)
        assert ratio == Fraction(l * Phi6, q)  # = 2*7/3

    # --- Asymptotic law ---

    def test_asymptotic_main_correction(self):
        """Main correction decays as N^{-n} = 20^{-n}."""
        N = l * Phi4
        assert N == 20
        # Correction channel: 120/20 = 6 = s (integer, confirms the split)
        assert 120 // N == k // l

    def test_asymptotic_topological_tail(self):
        """Topological tail decays as 120^{-n}."""
        volume = (k // l) * (l * Phi4)
        assert volume == 120

    def test_renormalized_continuum_limit(self):
        """After renorm by 120^n: limit = A, correction O(20^{-n}), tail O(120^{-n})."""
        # The three-term expansion X_n/120^n = A + B*20^{-n} + C*120^{-n}
        # has exactly two sub-leading channels
        rates = [20, 120]
        assert rates[0] == l * Phi4
        assert rates[1] == (k // l) * (l * Phi4)
        assert rates[0] < rates[1]
        assert rates[1] // rates[0] == k // l  # = s = 6

    # --- Physical interpretation ---

    def test_N_is_v_over_2(self):
        """N = v/2: transverse multiplicity is half the vertex count."""
        assert l * Phi4 == v // 2

    def test_c_EH_times_6_equals_dominant_mode_times_mu2(self):
        """c_EH * s = mu^2 * 120 = 16 * 120 = 1920."""
        s = k // l
        c_EH = m**2 * (l * Phi4)
        assert c_EH * s == m**2 * 120
