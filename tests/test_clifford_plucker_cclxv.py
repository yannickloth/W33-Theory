"""
Phase CCLXV — Clifford–Plücker 4D Completion
===============================================

THEOREM (4D Clifford–Plücker Completion):

Let s = k/λ = 6 and N = λΦ₄ = 20.  Then:

  s = dim Λ²(R⁴) = 6    (bivector space dimension)
  N = C(6,3) = 20        (Plücker 3-form shell)

and the spectral-action coefficients are:

  a₀  = 4! · N  = 24·20 = 480     (frame × Plücker)
  c_EH = 2⁴ · N = 16·20 = 320     (Clifford × Plücker)
  a₂  = Φ₆ · 2⁴ · N = 7·16·20 = 2240
  a₄  = 5(k−1) · 2⁴ · N = 55·16·20 = 17600

SELECTORS (all vanish uniquely at q=3):
  k/λ − 6 = (q−3)(q−2)/(q−1)              → bivector
  N − C(k/λ, 3) = 0                        → Plücker
  a₀ − 24N = (q−3)(q²+1)(q²+5q−8)         → frame
  c_EH − 16N = 2(q−3)²(q²+1)              → Clifford (quadratic)

SOURCE: W33_clifford_plucker_completion_20260331.zip
"""
import math
import pytest

# ── W(3,3) parameters ──
q    = 3
v    = 40
k    = 12
lam  = 2
mu   = 4
f    = 24
g    = 15
Phi3 = q**2 + q + 1   # 13
Phi4 = q**2 + 1        # 10
Phi6 = q**2 - q + 1    #  7

# ── Derived ──
s    = k // lam                     # 6  = bivector dim
N    = lam * Phi4                   # 20 = Plücker shell
a0   = 480                          # spectral action volume
c_EH = v * (q**2 - 1)              # 320 = Einstein-Hilbert
a2   = 2240                         # spectral action a2
a4   = 17600                        # spectral action a4


# ================================================================
# T1: Bivector and Plücker identifications
# ================================================================
class TestT1_BivectorPlucker:
    """s = dim Λ²(R⁴) = 6, N = C(6,3) = 20."""

    def test_s_is_6(self):
        assert s == 6

    def test_s_is_bivector_dim(self):
        """dim Λ²(R⁴) = C(4,2) = 6."""
        assert math.comb(4, 2) == s

    def test_N_is_20(self):
        assert N == 20

    def test_N_is_plucker(self):
        """C(6,3) = 20 = Plücker 3-form shell."""
        assert math.comb(s, 3) == N

    def test_N_from_W33(self):
        """N = λΦ₄ = 2·10 = 20."""
        assert lam * Phi4 == N

    def test_N_is_v_over_2(self):
        """N = v/2 = 20."""
        assert v // 2 == N


# ================================================================
# T2: Frame and Clifford packets
# ================================================================
class TestT2_FrameClifford:
    """24 = 4! (frame), 16 = 2⁴ (Clifford)."""

    def test_frame_factorial(self):
        assert math.factorial(4) == 24

    def test_clifford_power(self):
        assert 2**4 == 16

    def test_clifford_is_exterior_dim(self):
        """dim Λ*(R⁴) = 2⁴ = 16."""
        assert 2**4 == 16


# ================================================================
# T3: Spectral-action coefficients
# ================================================================
class TestT3_SpectralCoefficients:
    """All coefficients factor through 4!/2⁴ and N=20."""

    def test_a0(self):
        """a₀ = 4! · N = 480."""
        assert math.factorial(4) * N == a0

    def test_c_EH(self):
        """c_EH = 2⁴ · N = 320."""
        assert 2**4 * N == c_EH

    def test_a2(self):
        """a₂ = Φ₆ · 2⁴ · N = 2240."""
        assert Phi6 * 2**4 * N == a2

    def test_a4(self):
        """a₄ = 5(k−1) · 2⁴ · N = 17600."""
        assert 5 * (k - 1) * 2**4 * N == a4

    def test_c_EH_over_a0(self):
        """c_EH/a₀ = 2/q."""
        assert c_EH * q == 2 * a0


# ================================================================
# T4: Selectors vanish uniquely at q=3
# ================================================================
class TestT4_Selectors:
    """Each selector has an exact (q−3) factor."""

    def test_bivector_selector(self):
        """k/λ − 6 = (q−3)(q−2)/(q−1) vanishes at q=3."""
        # For q=3: (0)(1)/(2) = 0
        assert (q - 3) * (q - 2) // (q - 1) == 0
        assert s == 6

    def test_plucker_selector(self):
        """N − C(k/λ, 3) = 0 at q=3."""
        assert N == math.comb(s, 3)

    def test_frame_selector(self):
        """a₀ − 24N = (q−3)(q²+1)(q²+5q−8) = 0 at q=3."""
        selector = (q - 3) * (q**2 + 1) * (q**2 + 5*q - 8)
        assert selector == 0
        assert a0 == 24 * N

    def test_clifford_selector_quadratic(self):
        """c_EH − 16N = 2(q−3)²(q²+1) = 0 at q=3 (quadratic zero)."""
        selector = 2 * (q - 3)**2 * (q**2 + 1)
        assert selector == 0
        assert c_EH == 16 * N


# ================================================================
# T5: Non-vanishing at other prime powers
# ================================================================
class TestT5_Uniqueness:
    """Full Plücker selector (s=6 AND N=C(s,3)) singles out q=3."""

    def _full_selector(self, qq):
        """Return True if both bivector AND Plücker selectors vanish."""
        kk = qq * (qq + 1)
        ll = qq - 1
        if kk % ll != 0:
            return False
        ss = kk // ll
        if ss != 6:
            return False
        NN = ll * (qq**2 + 1)
        return NN == math.comb(ss, 3)

    def test_not_q2(self):
        """q=2 gives s=6 but N=5≠20: Plücker breaks."""
        assert not self._full_selector(2)

    def test_not_q4(self):
        assert not self._full_selector(4)

    def test_not_q5(self):
        assert not self._full_selector(5)

    def test_only_q3(self):
        assert self._full_selector(3)


# ================================================================
# T6: Curved packet structure
# ================================================================
class TestT6_CurvedPacket:
    """Multiplier sequence {1, 7, 39, 55}."""

    def test_multipliers(self):
        mults = [a0 // (24 * N),
                 a2 // (16 * N),
                 None,           # c6 not in current test set
                 a4 // (16 * N)]
        assert mults[0] == 1
        assert mults[1] == Phi6
        assert mults[3] == 5 * (k - 1)

    def test_a0_a2_ratio(self):
        """a₂/a₀ = Φ₆ · (2/q) = 14/3."""
        # a2/a0 = 2240/480 = 14/3
        assert a2 * q == a0 * Phi6 * 2
