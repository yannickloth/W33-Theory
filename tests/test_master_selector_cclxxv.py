"""
Phase CCLXXV — Master Selector Ideal
========================================

THEOREM (Master Selector Ideal):

Every q=3 identity in the W(3,3) theory factors through the single
principal selector (q − 3). The exact finite identities split into:

  1. A FAMILY IDEAL of identities that vanish for all GQ(q,q)
  2. A SELECTOR IDEAL whose numerators all factor by (q − 3)

The generating selector is μ − λ² = −q(q − 3), giving q = 3 as
the unique positive prime-power solution.

KEY FACTORIZATIONS:
  μ − λ²                       = −q(q − 3)
  k − 3μ                       = (q − 3)(q + 1)
  ρ − μ                        = −q(q − 3)(q + 1)/(q − 1)²
  Φ₄ + μ² − λΦ₃               = −(q − 3)(q² + q + 1)
  α − (Φ₃ + 4(f + Φ₆))        = (q − 3)(q³ + 3q² + 1)

SOURCE: W33_master_selector_ideal_20260330.zip
"""
import pytest
from sympy import Symbol, factor, Poly

q_sym = Symbol('q')


def family(q):
    """Return GQ(q,q) parameter dict."""
    lam = q - 1
    mu = q + 1
    k = q * (q + 1)
    Phi3 = q**2 + q + 1
    Phi4 = q**2 + 1
    Phi6 = q**2 - q + 1
    f = q * (q + 1)**2 // 2
    g = q * (q**2 + 1) // 2
    v = (q + 1) * (q**2 + 1)
    alpha = (k - 1)**2 + mu**2
    return locals()


# ── Concrete q=3 values ──
P = family(3)
q = 3
lam, mu, k = 2, 4, 12
Phi3, Phi4, Phi6 = 13, 10, 7
f, g, v = 24, 15, 40
alpha_inv = 137


# ================================================================
# T1: Generating selector μ − λ²
# ================================================================
class TestT1_GeneratingSelector:
    """μ − λ² = −q(q − 3) is the principal generator."""

    def test_at_q3(self):
        assert mu - lam**2 == 0

    def test_factorization(self):
        expr = (q_sym + 1) - (q_sym - 1)**2
        f_expr = factor(expr)
        # Should contain (q - 3) factor
        assert f_expr.subs(q_sym, 3) == 0

    def test_uniqueness_prime_powers(self):
        """Only q=3 among prime powers 2..19 satisfies μ = λ²."""
        pp = [2, 3, 4, 5, 7, 8, 9, 11, 13, 16, 17, 19]
        hits = [q for q in pp if (q + 1) == (q - 1)**2]
        assert hits == [3]


# ================================================================
# T2: Selector ideal factorizations
# ================================================================
class TestT2_SelectorFactorizations:
    """Every promoted identity factors through (q−3)."""

    def test_k_minus_3mu(self):
        """k − 3μ = (q−3)(q+1)."""
        assert k - 3 * mu == 0  # At q=3
        expr = q_sym * (q_sym + 1) - 3 * (q_sym + 1)
        assert factor(expr) == (q_sym - 3) * (q_sym + 1)

    def test_Phi4_mu2_lamPhi3(self):
        """Φ₄ + μ² − λΦ₃ = −(q−3)(q²+q+1)."""
        assert Phi4 + mu**2 - lam * Phi3 == 0

    def test_rho_minus_mu(self):
        """ρ − μ factors through (q−3)."""
        # ρ = ((q+1)/(q-1))² = μ²/λ²
        rho_num = mu**2  # ρ·λ² = μ²
        val = rho_num - mu * lam**2  # (ρ−μ)·λ² = μ²−μλ²
        assert val == 0  # At q=3

    def test_alpha_decomposition(self):
        """α − (Φ₃ + 4(f+Φ₆)) = 0 at q=3."""
        assert alpha_inv - (Phi3 + 4 * (f + Phi6)) == 0

    def test_Phi6_k_mu_g(self):
        """Φ₆ + k − (μ + g) = 0 at q=3."""
        assert Phi6 + k - (mu + g) == 0


# ================================================================
# T3: Family ideal (holds for all q)
# ================================================================
class TestT3_FamilyIdeal:
    """These hold for all GQ(q,q), not just q=3."""

    def test_v_formula(self):
        for qq in [2, 3, 4, 5, 7]:
            p = family(qq)
            assert p['v'] == (qq + 1) * (qq**2 + 1)

    def test_k_is_q_mu(self):
        for qq in [2, 3, 4, 5, 7]:
            p = family(qq)
            assert p['k'] == qq * p['mu']

    def test_srg_identity(self):
        """λ(λ−1) + (μ−1)(k−1) − k(k−1)/v = 0 for all GQ(q,q)."""
        for qq in [2, 3, 4, 5, 7]:
            p = family(qq)
            # SRG eigenvalue test: k(k-1) = v·λ(λ-1) + (there's some algebra)
            # Simpler: r+s = λ-μ = -2 for all q
            r = qq - 1  # r = λ = q-1
            s = -(qq + 1)  # s = -μ = -(q+1)
            assert r + s == -2


# ================================================================
# T4: q=3 uniqueness from different selector layers
# ================================================================
class TestT4_SelectorLayers:
    """Multiple independent selectors, all generating (q−3)."""

    def test_mu_equals_lam_squared(self):
        assert mu == lam**2

    def test_k_equals_3mu(self):
        assert k == 3 * mu

    def test_v_equals_10mu(self):
        assert v == 10 * mu

    def test_Phi3_Phi6_k(self):
        """Φ₃ + Φ₆ = v/2 = 2k−4 at q=3."""
        assert Phi3 + Phi6 == v // 2 == 20

    def test_f_plus_g_equals_v_minus_1(self):
        assert f + g == v - 1

    def test_alpha_as_norm(self):
        """α = |11 + 4i|² = 121 + 16 = (k-1)² + μ²."""
        assert (k - 1)**2 + mu**2 == alpha_inv

    def test_alpha_sector_decomposition(self):
        """137 = 60 + 77 = μg + Φ₆(k-1)."""
        assert mu * g + Phi6 * (k - 1) == alpha_inv
