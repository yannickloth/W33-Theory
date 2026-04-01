"""
Phase CCXLV: F_2 = 17 is a PURELY SPECTRAL invariant of W(3,3).

17 does not divide |Sp(4,3)| = 51840 or |PSp(4,3)| = 25920.
It has NO group-theoretic origin -- it is a spectral/combinatorial invariant.

Multiple representations:
  Phi4 + Phi6 = 10 + 7 = 17
  mu^2 + 1 = 16 + 1 = 17
  N - lambda - 1 = 20 - 2 - 1 = 17
  Im(lambda_r)^2 + Im(lambda_s)^2 = 10 + 7 = 17
  F_2 = 2^{2^2} + 1 (second Fermat prime)
"""

from fractions import Fraction
from math import comb
import pytest

v, k, l, m, q = 40, 12, 2, 4, 3
Phi3, Phi4, Phi6 = 13, 10, 7
f_dim, g_dim = 24, 15
s_param = k // l
N = comb(s_param, q)
E = k * v // 2
r_eig, s_eig = 2, -4
Sp4_order = 51840
PSp4_order = 25920
F2 = 17


class TestFermatPrimeF2Spectral:

    def test_F2_definition(self):
        """F_2 = 2^{2^2} + 1 = 2^4 + 1 = 17."""
        assert F2 == 2**(2**2) + 1 == 17

    def test_F2_is_prime(self):
        """17 is prime."""
        import sympy
        assert sympy.isprime(F2)

    def test_F2_not_divides_Sp4(self):
        """17 does NOT divide |Sp(4,3)| = 51840."""
        assert Sp4_order % F2 != 0

    def test_F2_not_divides_PSp4(self):
        """17 does NOT divide |PSp(4,3)| = 25920."""
        assert PSp4_order % F2 != 0

    def test_F2_is_Phi4_plus_Phi6(self):
        """17 = Phi4 + Phi6 = 10 + 7."""
        assert Phi4 + Phi6 == F2

    def test_F2_is_mu_squared_plus_1(self):
        """17 = mu^2 + 1 = 16 + 1."""
        assert m**2 + 1 == F2

    def test_F2_is_N_minus_lambda_minus_1(self):
        """17 = N - lambda - 1 = 20 - 2 - 1."""
        assert N - l - 1 == F2

    def test_F2_is_Im_r_sq_plus_Im_s_sq(self):
        """17 = Im(lambda_r)^2 + Im(lambda_s)^2 = Phi4 + Phi6."""
        Im_r_sq = (k-1) - (r_eig//2)**2
        Im_s_sq = (k-1) - (s_eig//2)**2
        assert Im_r_sq + Im_s_sq == F2

    def test_F2_equals_2_to_4_plus_1(self):
        """17 = 2^4 + 1 = 2^mu + 1."""
        assert 2**m + 1 == F2

    def test_F2_is_purely_spectral(self):
        """17 has no group-theoretic origin: it divides neither group order."""
        assert Sp4_order % F2 != 0
        assert PSp4_order % F2 != 0
        # But IS a spectral parameter:
        assert Phi4 + Phi6 == F2

    def test_Phi4_plus_Phi6_identity(self):
        """Phi4+Phi6 = (q^2+1)+(q^2-q+1) = 2q^2-q+2 = 17 at q=3."""
        poly_at_3 = 2*q**2 - q + 2
        assert poly_at_3 == F2

    def test_Sp4_prime_factors(self):
        """Sp(4,3) = 2^7 * 3^4 * 5: primes are {2, 3, 5}."""
        import sympy
        factors = set(sympy.factorint(Sp4_order).keys())
        assert factors == {2, 3, 5}
        assert 17 not in factors

    def test_multiple_representations_consistent(self):
        """All representations of 17 are consistent."""
        assert Phi4 + Phi6 == m**2 + 1 == N - l - 1 == F2
        Im_r_sq = (k-1) - (r_eig//2)**2
        Im_s_sq = (k-1) - (s_eig//2)**2
        assert Im_r_sq + Im_s_sq == F2
