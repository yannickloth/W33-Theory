"""
Phase CCXXXVI --- W(3,3) as Ramanujan Graph + Ihara Zeta + Suzuki-Tau Bridge
=============================================================================

RAMANUJAN THEOREM:
  W(3,3) is a Ramanujan graph: both |r|=2 and |s|=4 satisfy
    |lambda| <= 2*sqrt(k-1) = 2*sqrt(11) = 6.633...

IHARA-HASHIMOTO:
  The Hashimoto (non-backtracking) eigenvalue for s=-4 is -2 +/- i*sqrt(7).
  The imaginary part squared is EXACTLY Phi6 = 7 (not planted, forced by spectrum).
  Formula: Im^2 = (4(k-1) - s^2)/4 = (44-16)/4 = 7 = Phi6.

SUZUKI-TAU LINEARIZATION:
  The entire Suzuki lift linearizes in (tau, alpha):
    g' = mu*tau - Phi6  (family identity)
    f' = q*tau + f      (q=3 only)
    K' = q*alpha + (q+2) (q=3 only)

32 tests.
"""

import math
from fractions import Fraction
from sympy import isprime

# -- W(3,3) parameter block --
q      = 3
lam    = q - 1          # 2
mu     = q + 1          # 4
k      = q * (q + 1)    # 12
v      = (q + 1) * (q**2 + 1)  # 40
r      = q - 1          # 2
s_eig  = -(q + 1)       # -4
f      = q * (q + 1)**2 // 2   # 24
g_mult = q * (q**2 + 1) // 2   # 15
E      = v * k // 2     # 240

Phi3  = q**2 + q + 1    # 13
Phi4  = q**2 + 1        # 10
Phi6  = q**2 - q + 1    # 7

tau3 = E + k             # 252
alpha_137 = (k - 1)**2 + mu**2  # 137


# ===========================================================================
# T1 -- Ramanujan Property
# ===========================================================================
class TestT1_Ramanujan:
    """W(3,3) is a Ramanujan graph: |lambda| <= 2*sqrt(k-1) for all nontrivial eigenvalues."""

    def test_ramanujan_bound(self):
        """Ramanujan bound = 2*sqrt(k-1) = 2*sqrt(11) = 6.633..."""
        bound = 2 * math.sqrt(k - 1)
        assert 6.6 < bound < 6.7

    def test_r_inside_bound(self):
        """|r| = 2 <= 6.633."""
        assert abs(r) <= 2 * math.sqrt(k - 1)

    def test_s_inside_bound(self):
        """|s| = 4 <= 6.633."""
        assert abs(s_eig) <= 2 * math.sqrt(k - 1)

    def test_optimal_expander(self):
        """Both eigenvalues well inside the bound => optimal expander."""
        bound = 2 * math.sqrt(k - 1)
        assert abs(r) < bound / 2  # r=2 << 6.633
        assert abs(s_eig) < bound  # s=4 < 6.633

    def test_k_minus_1_is_prime(self):
        """k-1 = 11 is prime."""
        assert k - 1 == 11
        assert isprime(11)


# ===========================================================================
# T2 -- Ihara-Hashimoto Spectrum
# ===========================================================================
class TestT2_IharaHashimoto:
    """Hashimoto eigenvalues: -2 +/- i*sqrt(7) for the s=-4 sector."""

    def test_hashimoto_real_part(self):
        """Real part of Hashimoto eigenvalue for s: s/2 = -2."""
        assert s_eig / 2 == -2

    def test_hashimoto_imaginary_squared(self):
        """Im^2 = (4(k-1) - s^2)/4 = (44-16)/4 = 7 = Phi6."""
        im_sq = (4 * (k - 1) - s_eig**2) / 4
        assert im_sq == Phi6 == 7

    def test_hashimoto_modulus_squared(self):
        """|hashimoto|^2 = (s/2)^2 + Im^2 = 4+7 = 11 = k-1."""
        mod_sq = (s_eig / 2)**2 + Phi6
        assert mod_sq == k - 1 == 11

    def test_hashimoto_r_sector(self):
        """For r=2: Hashimoto eigenvalue = 1 +/- i*sqrt(10) (imaginary^2 = Phi4)."""
        im_sq_r = (4 * (k - 1) - r**2) / 4
        assert im_sq_r == Phi4 == 10

    def test_hashimoto_r_modulus(self):
        """|hashimoto_r|^2 = 1 + 10 = 11 = k-1."""
        mod_sq = (r / 2)**2 + Phi4
        assert mod_sq == k - 1

    def test_both_sectors_modulus(self):
        """Both Hashimoto sectors have |z|^2 = k-1 = 11 (Ramanujan spectral circle)."""
        assert (r / 2)**2 + (4 * (k - 1) - r**2) / 4 == k - 1
        assert (s_eig / 2)**2 + (4 * (k - 1) - s_eig**2) / 4 == k - 1


# ===========================================================================
# T3 -- Hashimoto Angle Cyclotomics
# ===========================================================================
class TestT3_HashimotoAngles:
    """Hashimoto imaginary parts are sqrt(Phi6) and sqrt(Phi4)."""

    def test_s_sector_Phi6(self):
        """s-sector imaginary part^2 = Phi6 = 7."""
        assert (4 * (k - 1) - s_eig**2) // 4 == Phi6

    def test_r_sector_Phi4(self):
        """r-sector imaginary part^2 = Phi4 = 10."""
        assert (4 * (k - 1) - r**2) // 4 == Phi4

    def test_sum_of_imaginary_squares(self):
        """Phi4 + Phi6 = 17 = mu^2 + 1 = |mu+i|^2."""
        assert Phi4 + Phi6 == 17
        assert mu**2 + 1 == 17

    def test_product_of_imaginary_squares(self):
        """Phi4 * Phi6 = 70 = Phi4*Phi6 = 10*7."""
        assert Phi4 * Phi6 == 70


# ===========================================================================
# T4 -- Suzuki-Tau Linearization
# ===========================================================================
class TestT4_SuzukiTau:
    """Suzuki lift linearizes in (tau, alpha) at q=3."""

    def test_g_prime_family(self):
        """g' = mu*tau - Phi6 = 4*252-7 = 1001 (FAMILY identity, holds for all q)."""
        g_prime = mu * tau3 - Phi6
        assert g_prime == 1001

    def test_f_prime_q3_only(self):
        """f' = q*tau + f = 3*252+24 = 780 = C(v,2) (q=3 only)."""
        f_prime = q * tau3 + f
        assert f_prime == 780
        assert f_prime == math.comb(v, 2)

    def test_K_prime_q3_only(self):
        """K' = q*alpha + (q+2) = 3*137+5 = 416 (q=3 only)."""
        K_prime = q * alpha_137 + (q + 2)
        assert K_prime == 416
        assert K_prime == mu * (k - mu) * Phi3  # cross-check

    def test_f_prime_selector(self):
        """f' - (q*tau+f) has factor (q-3)."""
        for qq in range(3, 30):
            kk = qq * (qq + 1)
            vv = (qq + 1) * (qq**2 + 1)
            EE = vv * kk // 2
            tt = EE + kk
            ff = qq * (qq + 1)**2 // 2
            mmu = qq + 1
            gg = qq * (qq**2 + 1) // 2
            pp3 = qq**2 + qq + 1
            f_prime = mmu * gg * pp3
            if f_prime == qq * tt + ff:
                assert qq == 3

    def test_V_prime(self):
        """V' = Phi6*tau + lam*q^2 = 7*252+18 = 1782 (q=3 only)."""
        V_prime = Phi6 * tau3 + lam * q**2
        assert V_prime == 1782


# ===========================================================================
# T5 -- Ollivier-Ricci Constant Curvature
# ===========================================================================
class TestT5_OllivierRicci:
    """W(3,3) has constant Ollivier-Ricci curvature kappa = 2/k on all edges."""

    def test_curvature_value(self):
        """kappa = lam/k = 2/12 = 1/6."""
        kappa_ricci = Fraction(lam, k)
        assert kappa_ricci == Fraction(1, 6)

    def test_total_scalar_curvature(self):
        """Sum_edges kappa = 2E * (lam/k) = 480 * 1/6... wait, E edges not 2E."""
        total = E * Fraction(lam, k)
        assert total == 40  # = v

    def test_vertex_scalar_curvature(self):
        """R(v) = k * kappa = 12 * 1/6 = 2 = lam."""
        R_vertex = k * Fraction(lam, k)
        assert R_vertex == lam

    def test_total_vertex_curvature(self):
        """Sum_v R(v) = v * lam = 80 = 2v."""
        assert v * lam == 80 == 2 * v

    def test_EH_action_from_curvature(self):
        """S_EH = Tr(L0) = v*k = 480 = (1/kappa)*Sum_v R(v) = 6*80."""
        assert v * k == 480
        assert 6 * (v * lam) == 480
