"""
Phase CCLXXXV: C6 -- 3|g(3) unique among prime q, Sigma=2^(Phi4/2).

THEOREM C6: For prime q, 3|g(q)=q(q^2+1)/2 iff q=3.
Proof: 3|g iff 3|q(q^2+1). If q≡1: q(q^2+1)≡2 mod 3. If q≡2: ≡1 mod 3. Only 3|q works.

COROLLARY: Sigma = 2^(g/3) is an integer (spectral invariant) only at q=3.
KEY IDENTITY: g/3 = Phi4/2, so Sigma = 2^(Phi4/2), linking s-sector to r-sector.
"""

import pytest

v, k, l, m, q = 40, 12, 2, 4, 3
Phi3, Phi4, Phi6 = 13, 10, 7
f_dim, g_dim = 24, 15
ev_r, ev_s = 2, -4

Sigma = 2 ** (g_dim // 3)  # = 32


class TestC6Sigma:

    def test_C6_three_divides_g_at_q3(self):
        assert g_dim % 3 == 0

    def test_C6_three_divides_g_iff_three_divides_q(self):
        for qq in [2, 3, 5, 7, 11, 13, 17]:
            g_val = qq * (qq**2 + 1) // 2
            assert (g_val % 3 == 0) == (qq % 3 == 0)

    def test_Sigma_equals_2_to_Phi4_over_2(self):
        """g/3 = Phi4/2: the D=-11 exponent is a Phi4-sector quantity."""
        assert g_dim // 3 == Phi4 // 2
        assert Sigma == 2 ** (Phi4 // 2)

    def test_j_neg11_equals_neg_Sigma_cubed(self):
        assert -(Sigma**3) == -32768
        assert -(2**g_dim) == -32768
