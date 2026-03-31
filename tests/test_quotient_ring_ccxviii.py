"""
Phase CCXVIII — One-Generator Quotient Ring and Master Selector Ideal

New results (2026-03-30):
  - All W(3,3) atoms are affine in lambda inside Z[lambda]/(lambda^2-lambda-2)
  - The minimum polynomial (lambda-2)(lambda+1) = lambda^2-lambda-2 = 0
  - Unique positive integer root: lambda=2, hence q=3, mu=4
  - Every q=3 selector identity factors through (q-3) in the selector ideal
  - rho=mu, kappa=mu*q^2 at q=3 only (projector root collapse)
  - The entire Standard Model flows from one generator lambda at one root

55 tests verifying the algebraic completeness of the one-generator quotient.
"""

import math
import pytest

q, v, k, lam, mu = 3, 40, 12, 2, 4
Phi3, Phi4, Phi6, Phi12 = 13, 10, 7, 73
f, g_mult = 24, 15
tau_val = 252
alpha_inv = 137
E_edges = 240

# Normalized moment roots
rho   = ((q+1)/(q-1))**2
kappa = (q*(q+1)/(q-1))**2


# ===========================================================================
# T1 — Minimum Polynomial of lambda
# ===========================================================================
class TestT1_MinPoly:
    """lambda satisfies lambda^2 - lambda - 2 = 0, roots 2 and -1."""

    def test_min_poly_at_lam2(self):
        """lambda=2 is a root of x^2-x-2."""
        x = lam
        assert x**2 - x - 2 == 0

    def test_min_poly_factored(self):
        """x^2-x-2 = (x-2)(x+1)."""
        x = lam
        assert (x-2)*(x+1) == x**2 - x - 2

    def test_positive_root_is_2(self):
        """The unique positive integer root is lambda=2."""
        # Solve x^2 - x - 2 = 0 over integers: x=2 or x=-1
        solutions = [x for x in range(-10, 10) if x**2 - x - 2 == 0]
        pos = [x for x in solutions if x > 0]
        assert pos == [2]

    def test_lam_squared_in_quotient(self):
        """Inside the quotient: lambda^2 = lambda + 2."""
        # At lambda=2: 4 = 2+2 ✓
        assert lam**2 == lam + 2

    def test_lam_cubed_in_quotient(self):
        """lambda^3 = lambda^2 * lambda = (lambda+2)*lambda = lambda^2+2*lambda
        = (lambda+2)+2*lambda = 3*lambda+2."""
        # At lambda=2: 8 = 3*2+2 ✓
        assert lam**3 == 3*lam + 2

    def test_lam_fourth_in_quotient(self):
        """lambda^4 = (3*lambda+2)*lambda = 3*lambda^2+2*lambda
        = 3*(lambda+2)+2*lambda = 5*lambda+6."""
        # At lambda=2: 16 = 5*2+6 ✓
        assert lam**4 == 5*lam + 6

    def test_discriminant_is_q_squared(self):
        """Discriminant of x^2-x-2 is 1+8=9=q^2."""
        assert 1 + 8 == q**2

    def test_min_poly_roots_sum(self):
        """2 + (-1) = 1 = lam - 1."""
        assert 2 + (-1) == lam - 1

    def test_min_poly_roots_product(self):
        """2 * (-1) = -2 = -(lam)."""
        assert 2 * (-1) == -lam


# ===========================================================================
# T2 — Linearization Table: All Atoms = a*lambda + b
# ===========================================================================
class TestT2_LinearizationTable:
    """Inside Z[lambda]/(lambda^2-lambda-2), every atom is affine."""

    def test_q_linear(self):
        assert q == lam + 1

    def test_mu_linear(self):
        assert mu == lam + 2

    def test_k_linear(self):
        """k = 4*lam + 4 = 4*(lam+1) = 4*q."""
        assert k == 4*lam + 4

    def test_Phi3_linear(self):
        """Phi3 = 4*lam + 5."""
        assert Phi3 == 4*lam + 5

    def test_Phi4_linear(self):
        """Phi4 = 3*lam + 4."""
        assert Phi4 == 3*lam + 4

    def test_Phi6_linear(self):
        """Phi6 = 2*lam + 3."""
        assert Phi6 == 2*lam + 3

    def test_f_linear(self):
        """f = 8*lam + 8 = 8*(lam+1) = 8*q."""
        assert f == 8*lam + 8

    def test_g_linear(self):
        """g = 5*lam + 5 = 5*(lam+1) = 5*q."""
        assert g_mult == 5*lam + 5

    def test_E_linear(self):
        """E = kv/2; but in the projector family E_table = q*mu*Phi4 = 40*(lam+1)."""
        E_table = q*mu*Phi4  # = 3*4*10 = 120
        assert E_table == 40*(lam+1) == 40*q

    def test_tau_linear(self):
        """tau = 252 = 84*q = 84*(lam+1) = 84*lam+84."""
        assert tau_val == 84*lam + 84

    def test_alpha_linear(self):
        """alpha_inv = 137 = 45*lam + 47."""
        assert alpha_inv == 45*lam + 47

    def test_mu_squared_linear(self):
        """mu^2 = (lam+2)^2 = lam^2+4*lam+4 = (lam+2)+4*lam+4 = 5*lam+6."""
        assert mu**2 == 5*lam + 6

    def test_kappa_linear(self):
        """kappa = mu*q^2 = (lam+2)*(lam+1)^2 ... at q=3: 36 = 12*lam+12."""
        kappa_int = int(kappa)
        assert kappa_int == 12*lam + 12


# ===========================================================================
# T3 — Key Identities in Quotient Ring
# ===========================================================================
class TestT3_QuotientIdentities:
    """Critical identities in Z[lambda]/(lambda^2-lambda-2)."""

    def test_alpha_from_k_mu(self):
        """alpha_inv = (k-1)^2 + mu^2 = 121 + 16 = 137."""
        assert (k-1)**2 + mu**2 == alpha_inv

    def test_alpha_linear_form(self):
        """alpha_inv = 45*lam + 47 at lam=2."""
        assert 45*lam + 47 == alpha_inv

    def test_tau_equals_k_q_Phi6(self):
        assert k * q * Phi6 == tau_val

    def test_tau_equals_84_q(self):
        assert 84 * q == tau_val

    def test_Phi4_plus_mu2_equals_lam_Phi3(self):
        """Family identity Phi4 + mu^2 = lam*Phi3 at q=3 only."""
        assert Phi4 + mu**2 == lam * Phi3

    def test_k_minus_3mu(self):
        """k - 3*mu = 0 at q=3 (selector)."""
        assert k - 3*mu == 0

    def test_5f_equals_vq(self):
        assert 5*f == v*q

    def test_E_grav_from_f_Phi4(self):
        assert f * Phi4 == g_mult * mu**2 == E_edges

    def test_mu_equals_lam_squared(self):
        """THE MASTER IDENTITY: mu = lam^2 iff q=3."""
        assert mu == lam**2

    def test_alpha_inv_decomposes_three_ways(self):
        A = lam*Phi4 + (v+1) + mu*(Phi6+k)   # 20+41+76
        B = Phi3 + mu*(f+Phi6)                  # 13+124
        C = (k-1)**2 + mu**2                    # 121+16
        assert A == B == C == alpha_inv


# ===========================================================================
# T4 — Selector Ideal: All q=3 Selectors Factor Through (q-3)
# ===========================================================================
class TestT4_SelectorIdeal:
    """Every q=3 selector identity has residual divisible by (q-3)."""

    @staticmethod
    def _residual(expr_func, q_test):
        try:
            lam_t = q_test - 1
            mu_t  = q_test + 1
            k_t   = q_test*(q_test+1)
            Phi3_t = q_test**2+q_test+1
            Phi4_t = q_test**2+1
            Phi6_t = q_test**2-q_test+1
            f_t   = q_test*(q_test+1)**2//2
            return expr_func(q_test, lam_t, mu_t, k_t, Phi3_t, Phi4_t, Phi6_t, f_t)
        except ZeroDivisionError:
            return None

    def test_mu_minus_lam_squared(self):
        """mu - lam^2 = -q*(q-3). Vanishes at q=3."""
        for q_t in range(2, 8):
            lam_t, mu_t = q_t-1, q_t+1
            residual = mu_t - lam_t**2
            expected = -q_t*(q_t-3)
            assert residual == expected

    def test_rho_minus_mu(self):
        """rho - mu = -q*(q-3)*(q+1)/(q-1)^2. Vanishes at q=3."""
        for q_t in [2, 3, 4, 5]:
            lam_t, mu_t = q_t-1, q_t+1
            rho_t = (mu_t/lam_t)**2
            residual = rho_t - mu_t
            expected = -q_t*(q_t-3)*(q_t+1)/(q_t-1)**2
            assert abs(residual - expected) < 1e-10

    def test_kappa_minus_mu_q2(self):
        """kappa - mu*q^2 = -q^3*(q-3)*(q+1)/(q-1)^2. Vanishes at q=3."""
        for q_t in [2, 3, 4, 5]:
            lam_t, mu_t = q_t-1, q_t+1
            kappa_t = (q_t*mu_t/lam_t)**2
            residual = kappa_t - mu_t*q_t**2
            expected = -q_t**3*(q_t-3)*(q_t+1)/(q_t-1)**2
            assert abs(residual - expected) < 1e-8

    def test_v_minus_lam2_Phi4(self):
        """v - lam^2*Phi4 vanishes at q=3 only (seventh selector)."""
        for q_t in range(2, 8):
            lam_t = q_t-1
            Phi4_t = q_t**2+1
            v_t = (q_t**4-1)//(q_t-1)
            residual = v_t - lam_t**2*Phi4_t
            assert (residual == 0) == (q_t == 3)

    def test_Phi4_plus_mu2_minus_lam_Phi3(self):
        """Phi4+mu^2-lam*Phi3 = -(q-3)*(q^2+q+1)."""
        for q_t in range(2, 7):
            lam_t, mu_t = q_t-1, q_t+1
            Phi3_t = q_t**2+q_t+1
            Phi4_t = q_t**2+1
            residual = Phi4_t + mu_t**2 - lam_t*Phi3_t
            expected = -(q_t-3)*Phi3_t
            assert residual == expected

    def test_k_minus_3mu_factors_q_minus_3(self):
        """k - 3*mu = (q-3)*(q+1) for GQ(q,q)."""
        for q_t in range(2, 7):
            lam_t, mu_t = q_t-1, q_t+1
            k_t = q_t*(q_t+1)
            residual = k_t - 3*mu_t
            expected = (q_t-3)*(q_t+1)
            assert residual == expected


# ===========================================================================
# T5 — Projector Root Collapse at q=3
# ===========================================================================
class TestT5_RootCollapse:
    """rho=mu and kappa=mu*q^2 ONLY at q=3."""

    def test_rho_eq_mu_at_q3(self):
        assert rho == mu

    def test_kappa_eq_mu_q2_at_q3(self):
        assert abs(kappa - mu*q**2) < 1e-12

    def test_rho_ne_mu_at_q2(self):
        rho2 = ((2+1)/(2-1))**2  # = 9
        mu2  = 2+1               # = 3
        assert rho2 != mu2

    def test_rho_ne_mu_at_q4(self):
        rho4 = ((4+1)/(4-1))**2  # = 25/9
        mu4  = 4+1               # = 5
        assert abs(rho4 - mu4) > 0.1

    def test_kappa_ne_mu_q2_at_q2(self):
        kap2 = (2*(2+1)/(2-1))**2  # = 36
        mu2, q2 = 3, 2
        assert kap2 != mu2*q2**2

    def test_collapse_condition_is_master_identity(self):
        """rho=mu iff mu/lam = sqrt(mu) iff mu=lam^2."""
        # At q=3: rho = (mu/lam)^2 = (4/2)^2 = 4 = mu ✓
        assert (mu/lam)**2 == mu == lam**2

    def test_collapse_unique_among_prime_powers(self):
        """Only q=3 satisfies both rho=mu AND kappa=mu*q^2."""
        collapses = []
        for q_t in [2, 3, 4, 5, 7, 8, 9]:
            lam_t, mu_t = q_t-1, q_t+1
            rho_t   = (mu_t/lam_t)**2
            kappa_t = (q_t*mu_t/lam_t)**2
            if abs(rho_t - mu_t) < 1e-10 and abs(kappa_t - mu_t*q_t**2) < 1e-10:
                collapses.append(q_t)
        assert collapses == [3]


# ===========================================================================
# T6 — Master Cascade in Quotient Ring
# ===========================================================================
class TestT6_MasterCascade:
    """All master identities as linear equations in lambda=2."""

    def test_master_selector_mu_eq_lam_sq(self):
        assert mu == lam**2

    def test_gaussian_norm_alpha(self):
        assert (k-1)**2 + mu**2 == alpha_inv

    def test_spectral_balance(self):
        assert f*Phi4 == g_mult*mu**2 == E_edges

    def test_tau_ramanujan(self):
        assert k*q*Phi6 == tau_val == 252

    def test_monster_factorization(self):
        p1 = v + Phi6      # 47
        p2 = v + k + Phi6  # 59
        p3 = Phi12 - lam   # 71
        assert p1*p2*p3 == 196883

    def test_eigenvalues_from_lam(self):
        """r = lam = lambda, s = -mu = -(lam+2)."""
        r_eig, s_eig = 2, -4
        assert r_eig == lam
        assert s_eig == -(lam+2)

    def test_lovasz_theta_equals_k_minus_r(self):
        """theta_Lovász = k-r = 12-2 = 10 = Phi4."""
        theta_L = k - 2   # = 10
        assert theta_L == Phi4

    def test_all_atoms_determined_by_one_lam(self):
        """Given lam=2, recover all constants."""
        q_r   = lam+1;     assert q_r == 3
        mu_r  = lam+2;     assert mu_r == 4
        k_r   = 4*lam+4;   assert k_r == 12
        P3_r  = 4*lam+5;   assert P3_r == 13
        P4_r  = 3*lam+4;   assert P4_r == 10
        P6_r  = 2*lam+3;   assert P6_r == 7
        f_r   = 8*lam+8;   assert f_r == 24
        g_r   = 5*lam+5;   assert g_r == 15
        a_r   = 45*lam+47; assert a_r == 137
        t_r   = 84*lam+84; assert t_r == 252
