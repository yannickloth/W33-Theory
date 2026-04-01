"""
Phase CCLIII — Dimensional-Curvature Closure and Tau=252
=========================================================

At q=3 the dimensional circle closes uniquely:
  d = mu = 4 => k = 3d = 12, r_c = 2d = 8, R = C(2d,2) = 28
  tau = (d-1)^2 * R = 9*28 = 252 = tau(3)

Four independent selectors each have unique q=3 solution:
  k = 3*mu  <=>  q(q-3)=0
  r_c = 2*mu  <=>  (q+1)(q-3)=0
  R = C(r_c,2)  <=>  q^2(q-3)(q+1)=0
  R = C(2*mu,2)  <=>  (q-3)(q+1)^2=0

Also: spectral square dictionary maps normalized moment roots
to heat roots via Phi4 = 1 + kappa/rho.

Sources: W33_dimensional_curvature_closure_20260330.zip,
         W33_spectral_square_dictionary_20260330.zip,
         W33_grade2_j_closure_20260330.zip
"""
import pytest
from math import comb
from fractions import Fraction

# ── W(3,3) parameters ──
q   = 3
v   = 40
k   = 12
lam = 2
mu  = 4     # = d (spacetime dimension)
r   = 2
s   = -4
f   = 24
g   = 15
Phi3 = 13
Phi4 = 10
Phi6 = 7
E   = 240

# ── Derived dimensional quantities ──
d  = mu              # spacetime dimension = 4
rc = k - mu          # compact rank = 8 = 2d
R  = mu * Phi6       # curvature count = 28 = C(2d,2)
tau3 = q**2 * R      # = 252 = Ramanujan tau(3)

# ── Normalized moment roots ──
rho   = mu                 # = 4 (small root, unnormalized)
kappa = mu * q**2          # = 36 (large root, unnormalized)


# ================================================================
# T1: Dimensional circle at q=3
# ================================================================
class TestT1_DimensionalCircle:
    """d=mu=4 closes a dimensional circle."""

    def test_d_equals_mu(self):
        """d = mu = q+1 = 4"""
        assert d == mu == 4

    def test_k_equals_3d(self):
        """k = 3d = 12"""
        assert k == 3 * d

    def test_rc_equals_2d(self):
        """r_c = k-mu = 2d = 8"""
        assert rc == 2 * d == 8

    def test_R_equals_C_2d_2(self):
        """R = C(2d,2) = C(8,2) = 28"""
        assert R == comb(2*d, 2)
        assert R == 28

    def test_R_equals_C_rc_2(self):
        """R = C(r_c,2) = C(8,2) = 28"""
        assert R == comb(rc, 2)

    def test_tau3_equals_d_minus_1_sq_times_R(self):
        """tau(3) = (d-1)^2 * R = 9*28 = 252"""
        assert tau3 == (d - 1)**2 * R
        assert tau3 == 252

    def test_tau3_equals_q_sq_R(self):
        """tau(3) = q^2 * R = 9*28 = 252"""
        assert tau3 == q**2 * R

    def test_R_equals_mu_Phi6(self):
        """R = mu*Phi6 = 4*7 = 28"""
        assert R == mu * Phi6


# ================================================================
# T2: Four unique selectors at q=3
# ================================================================
class TestT2_UniqueSelectors:
    """Each selector has polynomial factoring through (q-3)."""

    def test_k_minus_3mu(self):
        """k - 3*mu = (q+1)*(q-3) = 0 at q=3"""
        for qq in range(2, 20):
            kq = qq * (qq + 1)
            muq = qq + 1
            diff = kq - 3 * muq
            assert diff == (qq + 1) * (qq - 3)
            if qq == 3:
                assert diff == 0
            else:
                assert diff != 0

    def test_rc_minus_2mu(self):
        """r_c - 2*mu = (q+1)(q-3) = 0 at q=3"""
        for qq in range(2, 20):
            rcq = qq * (qq + 1) - (qq + 1)  # k - mu = q^2 - 1
            muq = qq + 1
            diff = rcq - 2 * muq
            assert diff == (qq + 1) * (qq - 3)

    def test_R_minus_C_rc_2(self):
        """2R - r_c*(r_c-1) = -q^2*(q-3)*(q+1) vanishes at q=3"""
        for qq in range(2, 15):
            muq = qq + 1
            Phi6q = qq**2 - qq + 1
            Rq = muq * Phi6q
            rcq = qq**2 - 1
            diff = 2 * Rq - rcq * (rcq - 1)
            expected = -(qq**2) * (qq - 3) * (qq + 1)
            assert diff == expected

    def test_R_minus_C_2mu_2(self):
        """2R - 2*mu*(2*mu-1) = 2*q*(q-3)*(q+1) vanishes at q=3"""
        for qq in range(2, 15):
            muq = qq + 1
            Phi6q = qq**2 - qq + 1
            Rq = muq * Phi6q
            diff = 2 * Rq - 2 * muq * (2 * muq - 1)
            expected = 2 * qq * (qq - 3) * (qq + 1)
            assert diff == expected


# ================================================================
# T3: Normalized moment roots and heat dictionary
# ================================================================
class TestT3_NormalizedRoots:
    """Moment roots rho, kappa and their heat dictionary."""

    def test_rho_value(self):
        """rho = mu = 4"""
        assert rho == mu == 4

    def test_kappa_value(self):
        """kappa = mu*q^2 = 36"""
        assert kappa == mu * q**2 == 36

    def test_rho_plus_kappa(self):
        """rho + kappa = v = 40"""
        assert rho + kappa == v

    def test_rho_times_kappa(self):
        """rho * kappa = k^2 = 144"""
        assert rho * kappa == k**2

    def test_Phi4_from_kappa_rho(self):
        """Phi4 = 1 + kappa/rho = 1 + 9 = 10"""
        assert Fraction(kappa, rho) + 1 == Phi4

    def test_mu_sq_from_lambda_sq_rho(self):
        """mu^2 = lam^2 * rho = 4*4 = 16"""
        assert lam**2 * rho == mu**2

    def test_discriminant(self):
        """(rho-kappa)^2 = (rho+kappa)^2 - 4*rho*kappa = v^2-4k^2"""
        assert (rho - kappa)**2 == v**2 - 4 * k**2
        assert (rho - kappa)**2 == 1024
        assert rho - kappa == -32  # kappa > rho


# ================================================================
# T4: Closed-form even/odd sequences
# ================================================================
class TestT4_ClosedForms:
    """E_t and O_t closed forms at q=3."""

    def _E(self, t):
        """E_t = 1/5 + (1/2)*4^t + (3/10)*36^t"""
        return Fraction(1, 5) + Fraction(1, 2) * Fraction(4**t) + Fraction(3, 10) * Fraction(36**t)

    def _O(self, t):
        """O_t = 1/5 - 4^t + (9/5)*36^t"""
        return Fraction(1, 5) - Fraction(4**t) + Fraction(9, 5) * Fraction(36**t)

    def test_E0(self):
        assert self._E(0) == Fraction(1, 5) + Fraction(1, 2) + Fraction(3, 10)
        assert self._E(0) == 1

    def test_O0(self):
        assert self._O(0) == Fraction(1, 5) - 1 + Fraction(9, 5)
        assert self._O(0) == 1

    def test_E1(self):
        """E_1 = 1/5 + 2 + 54/5 = 1/5 + 10/5 + 54/5 = 65/5 = 13"""
        assert self._E(1) == 13

    def test_O1(self):
        """O_1 = 1/5 - 4 + 324/5 = 1/5 - 20/5 + 324/5 = 305/5 = 61"""
        assert self._O(1) == 61

    def test_recurrence_E(self):
        """10*E_t = 3*36^t + 5*4^t + 2"""
        for t in range(5):
            lhs = 10 * self._E(t)
            rhs = 3 * 36**t + 5 * 4**t + 2
            assert lhs == rhs

    def test_recurrence_O(self):
        """5*O_t = 9*36^t - 5*4^t + 1"""
        for t in range(5):
            lhs = 5 * self._O(t)
            rhs = 9 * 36**t - 5 * 4**t + 1
            assert lhs == rhs


# ================================================================
# T5: Grade-2 j-coefficient closure
# ================================================================
class TestT5_Grade2J:
    """j_2 closes in terms of W(3,3) parameters."""

    def test_alpha_decomposition(self):
        """alpha = 137 = (k-1)^2 + mu^2 = 121+16"""
        alpha = (k - 1)**2 + mu**2
        assert alpha == 137

    def test_2099_from_g_alpha(self):
        """2099 = g*alpha + 4*(k-1)"""
        alpha = 137
        val = g * alpha + 4 * (k - 1)
        assert val == 2099

    def test_2099_alternative(self):
        """2099 = (v+1)*(v+k+Phi6) - c_EH"""
        c_EH = 320
        val = (v + 1) * (v + k + Phi6) - c_EH
        assert val == 2099

    def test_j2_full(self):
        """21493760 = 2^(k-1) * (q+2) * 2099"""
        j2 = 2**(k-1) * (q + 2) * 2099
        assert j2 == 21493760

    def test_2099_is_prime(self):
        """2099 is prime"""
        n = 2099
        assert all(n % d != 0 for d in range(2, int(n**0.5) + 1))


# ================================================================
# T6: Dimensional fixed-point uniqueness scan
# ================================================================
class TestT6_UniquenessScans:
    """Verify all four selectors select q=3 uniquely in scan."""

    def test_k_3mu_scan(self):
        hits = [qq for qq in range(2, 100) if qq*(qq+1) == 3*(qq+1)]
        assert hits == [3]

    def test_rc_2mu_scan(self):
        hits = [qq for qq in range(2, 100) if qq**2 - 1 == 2*(qq+1)]
        assert hits == [3]

    def test_R_C_rc_2_scan(self):
        hits = [qq for qq in range(2, 100)
                if (qq+1)*(qq**2-qq+1) == comb(qq**2-1, 2)]
        assert hits == [3]

    def test_R_C_2mu_2_scan(self):
        hits = [qq for qq in range(2, 100)
                if (qq+1)*(qq**2-qq+1) == comb(2*(qq+1), 2)]
        assert hits == [3]
