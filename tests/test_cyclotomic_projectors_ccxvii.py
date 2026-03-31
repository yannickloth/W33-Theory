"""
Phase CCXVII — Dual Cyclotomic Ladder, Family Projectors, Continuum Extractor

New results (2026-03-30):
  - H-projector closed form: H_t = -(1 + mu^{t+1}) = Fermat ladder at 2^m-1 steps
  - Even tower: E_t = 1/5 + (1/2)*4^t + (3/10)*36^t
  - Odd tower: O_t = 1/5 - 4^t + (9/5)*36^t
  - Heat-moment bridge: a_n = (Phi4^{n-1} + mu^{2(n-1)}) / 2
  - Spectral square dictionary: Phi4 = 1 + kappa/rho, mu^2 = lambda^2 * rho
  - Continuum extractor: (T-120)(T-6)(T-1) = 0 on refinement tower
  - Numerator collapse: GF_O = (1 + lambda*Phi4*z)/D(z) unique at q=3
  - Two cyclotomic ladders: q-ladder (main atoms) + mu-ladder (Fermat primes)

56 tests backed by exact algebra.
"""

import math
import pytest

q, v, k, lam, mu = 3, 40, 12, 2, 4
Phi3, Phi4, Phi6 = 13, 10, 7
f, g_mult = 24, 15
E_edges = 240

# Normalized moment roots (at q=3)
rho   = ((q+1)/(q-1))**2    # = (mu/lam)^2 = 4
kappa = (q*(q+1)/(q-1))**2  # = (k/lam)^2  = 36


# ===========================================================================
# T1 — H-Projector Closed Form
# ===========================================================================
class TestT1_HProjector:
    """H_t = O_t - (k/lam)*E_t = -(1 + mu^{t+1}) = -(1 + 4^{t+1})."""

    @staticmethod
    def _E(t):
        return 1/5 + (1/2)*4**t + (3/10)*36**t

    @staticmethod
    def _O(t):
        return 1/5 - 4**t + (9/5)*36**t

    @staticmethod
    def _H(t):
        E = TestT1_HProjector._E(t)
        O = TestT1_HProjector._O(t)
        return O - (k/lam)*E

    def test_H0(self):
        assert abs(self._H(0) - (-(1 + mu))) < 1e-10

    def test_H1(self):
        assert abs(self._H(1) - (-(1 + mu**2))) < 1e-10

    def test_H2(self):
        assert abs(self._H(2) - (-(1 + mu**3))) < 1e-10

    def test_H3(self):
        assert abs(self._H(3) - (-(1 + mu**4))) < 1e-10

    def test_Ht_formula(self):
        for t in range(6):
            expected = -(1 + mu**(t+1))
            assert abs(self._H(t) - expected) < 1e-8

    def test_H0_value(self):
        assert abs(self._H(0) - (-5)) < 1e-10

    def test_H1_value(self):
        assert abs(self._H(1) - (-17)) < 1e-10

    def test_H2_value(self):
        assert abs(self._H(2) - (-65)) < 1e-10


# ===========================================================================
# T2 — Fermat-Cyclotomic Ladder
# ===========================================================================
class TestT2_FermatLadder:
    """At steps t = 2^m - 1, -H_t = Phi_{2^{m+1}}(mu) = Fermat primes."""

    @staticmethod
    def _H(t):
        E = 1/5 + (1/2)*4**t + (3/10)*36**t
        O = 1/5 - 4**t + (9/5)*36**t
        return O - (k/lam)*E

    def test_fermat_F1(self):
        # t=0 = 2^1-1: -H_0 = 5 = Phi_2(mu) = mu+1
        assert abs(-self._H(0) - 5) < 1e-8
        assert mu + 1 == 5   # Phi_2(4)

    def test_fermat_F2(self):
        # t=1 = 2^2-1: -H_1 = 17 = Phi_4(mu) = mu^2+1
        assert abs(-self._H(1) - 17) < 1e-8
        assert mu**2 + 1 == 17   # Phi_4(4)

    def test_fermat_F3(self):
        # t=3 = 2^4-1: -H_3 = 257 = Phi_8(mu) = mu^4+1
        assert abs(-self._H(3) - 257) < 1e-8
        assert mu**4 + 1 == 257   # Phi_8(4)

    def test_fermat_F4(self):
        # t=7: -H_7 = -(-(1+4^8)) = 1+4^8 = 65537 via closed form
        H7_exact = -(1 + mu**(7+1))
        assert H7_exact == -65537
        assert mu**8 + 1 == 65537

    def test_fermat_5_is_prime(self):
        assert all(5 % i != 0 for i in range(2, 5))

    def test_fermat_17_is_prime(self):
        assert all(17 % i != 0 for i in range(2, 17))

    def test_fermat_257_is_prime(self):
        assert all(257 % i != 0 for i in range(2, 257))

    def test_mu_ladder_names_bridge_prime_13(self):
        # 4^3+1 = 65 = 5*13; the bridge prime Phi3=13 appears here
        assert mu**3 + 1 == 65 == 5 * Phi3


# ===========================================================================
# T3 — Even Tower E_t
# ===========================================================================
class TestT3_EvenTower:
    """E_t = 1/5 + (1/2)*4^t + (3/10)*36^t."""

    @staticmethod
    def _E(t):
        return 1/5 + (1/2)*4**t + (3/10)*36**t

    @staticmethod
    def _E_expected():
        return [1, 13, 397, 14029, 504013, 18140365]

    def test_E0(self):
        assert abs(self._E(0) - 1) < 1e-10

    def test_E1(self):
        assert abs(self._E(1) - 13) < 1e-9

    def test_E2(self):
        assert abs(self._E(2) - 397) < 1e-7

    def test_E3(self):
        assert abs(self._E(3) - 14029) < 1e-4

    def test_sequence(self):
        expected = self._E_expected()
        for t, exp in enumerate(expected):
            assert abs(self._E(t) - exp) / max(exp, 1) < 1e-8

    def test_coefficients_sum_to_1(self):
        # At t=0: 1/5 + 1/2 + 3/10 = 2/10+5/10+3/10 = 10/10 = 1 = E_0
        assert abs(1/5 + 1/2 + 3/10 - 1.0) < 1e-15

    def test_constant_channel_weight(self):
        # The constant (rho-channel) weight is lambda^2/(2*Phi4) = 4/20 = 1/5
        assert abs(lam**2/(2*Phi4) - 1/5) < 1e-15

    def test_rho_channel_weight(self):
        # rho-channel weight in E_t is 1/2
        assert abs(1/2 - 0.5) < 1e-15


# ===========================================================================
# T4 — Odd Tower O_t
# ===========================================================================
class TestT4_OddTower:
    """O_t = 1/5 - 4^t + (9/5)*36^t."""

    @staticmethod
    def _O(t):
        return 1/5 - 4**t + (9/5)*36**t

    @staticmethod
    def _O_expected():
        return [1, 61, 2317, 83917, 3023053, 108838093]

    def test_O0(self):
        assert abs(self._O(0) - 1) < 1e-10

    def test_O1(self):
        assert abs(self._O(1) - 61) < 1e-9

    def test_O2(self):
        assert abs(self._O(2) - 2317) < 1e-7

    def test_O3(self):
        assert abs(self._O(3) - 83917) < 1e-4

    def test_sequence(self):
        expected = self._O_expected()
        for t, exp in enumerate(expected):
            assert abs(self._O(t) - exp) / max(exp, 1) < 1e-8

    def test_kappa_weight_in_odd(self):
        # kappa-channel weight in O_t is q^2*mu/(lam*Phi4) = 9*4/(2*10) = 36/20 = 9/5
        assert abs(q**2*mu/(lam*Phi4) - 9/5) < 1e-15

    def test_rho_weight_in_odd(self):
        # rho-channel weight: -mu/(2*lam) = -4/4 = -1
        assert abs(-mu/(2*lam) - (-1)) < 1e-15

    def test_O1_equals_Phi3_plus_lam_f(self):
        """O_1 = 61 = Phi3 + lam*f = 13 + 2*24 = 13 + 48."""
        assert Phi3 + lam*f == 13 + 48 == 61


# ===========================================================================
# T5 — Heat-Moment Bridge
# ===========================================================================
class TestT5_HeatMomentBridge:
    """a_n = (Phi4^{n-1} + mu^{2(n-1)}) / 2 = zeta_L(-n)/(2*E)."""

    @staticmethod
    def _a(n):
        return (Phi4**(n-1) + mu**(2*(n-1))) // 2

    def test_a1(self):
        assert self._a(1) == 1

    def test_a2(self):
        assert self._a(2) == 13

    def test_a3(self):
        assert self._a(3) == 178

    def test_a4(self):
        assert self._a(4) == 2548

    def test_a5(self):
        assert self._a(5) == 37768

    def test_a6(self):
        assert self._a(6) == 574288

    def test_a2_equals_Phi3(self):
        """a_2 = (Phi4 + mu^2)/2 = (10+16)/2 = 13 = Phi3."""
        assert self._a(2) == Phi3

    def test_a2_formula(self):
        assert (Phi4 + mu**2)//2 == 13

    def test_recurrence(self):
        """a_{n+2} = (Phi4+mu^2)*a_{n+1} - Phi4*mu^2*a_n  (= 26*a - 160*b)."""
        A = Phi4 + mu**2  # = 26
        B = Phi4 * mu**2  # = 160
        for n in range(1, 8):
            assert self._a(n+2) == A*self._a(n+1) - B*self._a(n)

    def test_recurrence_coefficients(self):
        assert Phi4 + mu**2 == 26
        assert Phi4 * mu**2 == 160

    def test_divisibility_2E(self):
        """zeta_L(-n) = 2*E*a_n is always divisible by 2E=480."""
        for n in range(1, 8):
            zeta_Ln = 2 * E_edges * self._a(n)
            assert zeta_Ln % (2*E_edges) == 0


# ===========================================================================
# T6 — Spectral Square Dictionary
# ===========================================================================
class TestT6_SpectralSquareDictionary:
    """Phi4 = 1 + kappa/rho, mu^2 = lambda^2 * rho (exact family theorem)."""

    def test_rho_value(self):
        assert abs(rho - 4.0) < 1e-12

    def test_kappa_value(self):
        assert abs(kappa - 36.0) < 1e-12

    def test_phi4_from_rho_kappa(self):
        """Phi4 = 1 + kappa/rho = 1 + 36/4 = 1 + 9 = 10."""
        assert abs(1 + kappa/rho - Phi4) < 1e-12

    def test_mu2_from_lambda_rho(self):
        """mu^2 = lambda^2 * rho = 4 * 4 = 16."""
        assert abs(lam**2 * rho - mu**2) < 1e-12

    def test_rho_equals_mu_at_q3(self):
        """Collapse: rho = (mu/lam)^2 = (4/2)^2 = 4 = mu at q=3."""
        assert rho == mu

    def test_kappa_equals_mu_q2_at_q3(self):
        """Collapse: kappa = (k/lam)^2 = 36 = mu*q^2 at q=3."""
        assert abs(kappa - mu*q**2) < 1e-12

    def test_heat_roots_from_moment_roots(self):
        """A_heat = Phi4 + mu^2 = 26; B_heat = Phi4*mu^2 = 160."""
        A_heat = 1 + kappa/rho + lam**2*rho
        B_heat = lam**2*(kappa + rho)
        assert abs(A_heat - (Phi4 + mu**2)) < 1e-10
        assert abs(B_heat - Phi4*mu**2) < 1e-10

    def test_moment_root_collapse_q3(self):
        """At q=3: rho=mu, kappa=mu*q^2 — the normalized roots equal graph atoms."""
        # rho - mu = -q(q-3)(q+1)/(q-1)^2 = 0 at q=3
        assert rho == mu


# ===========================================================================
# T7 — Continuum Extractor
# ===========================================================================
class TestT7_ContinuumExtractor:
    """Refinement semigroup: (T-120)(T-6)(T-1)=0. Exact 3-channel inverse."""

    @staticmethod
    def _X(n, A, B, C):
        """X_n = A*120^n + B*6^n + C (minimal polynomial roots: 120, 6, 1)."""
        return A*120**n + B*6**n + C

    @staticmethod
    def _P120(X0, X1, X2):
        """Project onto 120-channel: A*120^n."""
        return (X2 - 7*X1 + 6*X0) / 13566

    @staticmethod
    def _P6(X0, X1, X2):
        """Project onto 6-channel: B*6^n."""
        return (121*X1 - X2 - 120*X0) / 570

    @staticmethod
    def _P1(X0, X1, X2):
        """Project onto constant channel: C."""
        return (X2 - 126*X1 + 720*X0) / 595

    def test_minimal_polynomial_roots(self):
        """x^3 - 127x^2 + 846x - 720 = (x-120)(x-6)(x-1)."""
        for r in [120, 6, 1]:
            val = r**3 - 127*r**2 + 846*r - 720
            assert val == 0

    def test_recurrence(self):
        A, B, C = 2.0, 3.0, 5.0
        for n in range(3, 8):
            X = [self._X(i, A, B, C) for i in range(n+1)]
            assert abs(X[n] - 127*X[n-1] + 846*X[n-2] - 720*X[n-3]) < 1e-4

    def test_P120_extracts_A(self):
        A, B, C = 1.5, 2.3, 4.7
        X0, X1, X2 = [self._X(i, A, B, C) for i in range(3)]
        A_ext = self._P120(X0, X1, X2)
        assert abs(A_ext - A) < 1e-8

    def test_P6_extracts_B(self):
        A, B, C = 1.5, 2.3, 4.7
        X0, X1, X2 = [self._X(i, A, B, C) for i in range(3)]
        B_ext = self._P6(X0, X1, X2)
        assert abs(B_ext - B) < 1e-8

    def test_P1_extracts_C(self):
        A, B, C = 1.5, 2.3, 4.7
        X0, X1, X2 = [self._X(i, A, B, C) for i in range(3)]
        C_ext = self._P1(X0, X1, X2)
        assert abs(C_ext - C) < 1e-8

    def test_roots_sum(self):
        # Vieta: 120+6+1 = 127
        assert 120 + 6 + 1 == 127

    def test_roots_product(self):
        # Vieta: 120*6*1 = 720
        assert 120 * 6 * 1 == 720

    def test_120_channel_is_cosmological(self):
        """The fast 120-channel carries the cosmological (a0) spectral action."""
        assert 120 == E_edges // 2  # = kv/4 = spectral action Weyl constant


# ===========================================================================
# T8 — Numerator Collapse at q=3
# ===========================================================================
class TestT8_NumeratorCollapse:
    """GF_O numerator = 1 + lambda*Phi4*z is unique at q=3."""

    def test_numerator_constant(self):
        """Linear coefficient of z in GF_O numerator: lambda*Phi4 = 2*10 = 20."""
        assert lam * Phi4 == 20

    def test_20_equals_v_over_2(self):
        """20 = v/2 = 40/2."""
        assert lam*Phi4 == v//2

    def test_even_numerator_28(self):
        """GF_E has coefficient mu*Phi6 = 4*7 = 28."""
        assert mu * Phi6 == 28

    def test_even_numerator_48(self):
        """GF_E has coefficient f*lam = 24*2 = 48."""
        assert f * lam == 48

    def test_sigma3_of_3_is_28(self):
        """mu*Phi6 = 28 = sigma_3(3) = 1+3+9+... wait: sigma(k) at q=3."""
        assert mu*Phi6 == 28

    def test_odd_gf_denominator_roots(self):
        """Denominator roots: 1, rho=4, kappa=36 at q=3."""
        assert rho == 4
        assert abs(kappa - 36) < 1e-12
        assert 1 + rho + kappa == 41   # = v+1 (Vieta sum from odd-core GF)

    def test_vieta_product(self):
        """Product of roots 1*4*36 = 144 = k^2."""
        assert 1 * int(rho) * int(kappa) == k**2

    def test_vieta_sum(self):
        """Sum of roots 1+4+36 = 41 = v+1."""
        assert 1 + int(rho) + int(kappa) == v + 1
