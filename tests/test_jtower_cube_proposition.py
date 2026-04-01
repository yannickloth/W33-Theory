"""
Phase CCLXXVIII: j-tower cube-root proposition.

PROPOSITION: The five Heegner j-invariants attached to W(3,3) spectral data
decompose as perfect cubes of W(3,3) spectral invariants:
  j(-4)  =  k^3             = 1728
  j(-7)  = -g^3             = -3375
  j(-8)  =  (v/2)^3         = 8000
  j(-11) = -(2^(g/3))^3     = -32768   [g/3=5 is an integer since 3|g=15]
  j(-28) =  P^3             = 16581375  where P = q*(Phi4/2)*(Phi4+Phi6) = 255

COROLLARY: The j-tower is the complete intersection of:
  (a) Heegner discriminants with |D| <= 4*Phi6 = 28
  (b) cube root is a W(3,3) spectral invariant from the set {k, g, v/2, 2^(g/3), P}
"""

import sympy
import pytest

v, k, l, m, q = 40, 12, 2, 4, 3
Phi3, Phi4, Phi6 = 13, 10, 7
f_dim, g_dim = 24, 15
ev_r, ev_s = 2, -4

j_tower = {-4: 1728, -7: -3375, -8: 8000, -11: -32768, -28: 16581375}
Sigma = 2**(g_dim//3)   # = 2^5 = 32
P = q * (Phi4//2) * (Phi4 + Phi6)  # = 255


class TestJTowerCubeProposition:

    def test_g_divisible_by_3(self):
        """Sigma = 2^(g/3) requires 3|g."""
        assert g_dim % 3 == 0

    def test_Sigma_value(self):
        assert Sigma == 32
        assert Sigma == 2**5

    def test_P_value(self):
        assert P == 255
        assert P == q * (Phi4//2) * (Phi4 + Phi6)

    def test_j_neg4_equals_k_cubed(self):
        assert j_tower[-4] == k**3

    def test_j_neg7_equals_neg_g_cubed(self):
        assert j_tower[-7] == -(g_dim**3)

    def test_j_neg8_equals_half_v_cubed(self):
        assert j_tower[-8] == (v//2)**3

    def test_j_neg11_equals_neg_Sigma_cubed(self):
        """j(-11) = -(2^(g/3))^3 = -Sigma^3."""
        assert j_tower[-11] == -(Sigma**3)
        assert j_tower[-11] == -(2**(g_dim//3))**3

    def test_j_neg28_equals_P_cubed(self):
        assert j_tower[-28] == P**3

    def test_corollary_all_within_4Phi6_bound(self):
        """All tower discriminants satisfy |D| <= 4*Phi6 = 28."""
        for D in j_tower:
            assert abs(D) <= 4 * Phi6

    def test_corollary_no_larger_heegner_in_tower(self):
        """Heegner discs beyond -28 have cbrt NOT in the tower parameter set."""
        heegner_large_j = {-19: -884736, -43: -884736000, -67: -147197952000}
        tower_cbroots = {k, g_dim, v//2, Sigma, P}
        for D, j_val in heegner_large_j.items():
            cbrt = round(abs(j_val)**(1/3))
            assert cbrt**3 == abs(j_val), f"|j({D})| must be exact cube"
            assert cbrt not in tower_cbroots, f"|j({D})|^(1/3)={cbrt} should not be in tower set"
