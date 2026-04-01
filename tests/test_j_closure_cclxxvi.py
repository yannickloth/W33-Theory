"""
Phase CCLXXVI — Grade-2 j-Invariant Closure
===============================================

THEOREM (Grade-2 j Closure):

The second j-invariant coefficient 21493760 = c(2) of q(τ) = Σ c(n) q^n
closes exactly in W(3,3) language:

  2099 = g·α + 4(k−1) = 15·137 + 44
  2099 = (v+1)(v+k+Φ₆) − c_EH = 41·59 − 320

  c(2) = 21493760 = 2^(k−1) · (q+2) · 2099 = 2^11 · 5 · 2099

Both representations factor as (q−3)·(higher polynomial), confirming
q=3 uniqueness for the grade-2 moonshine coefficient.

SOURCE: W33_grade2_j_closure_20260330.zip
"""
import pytest

# ── W(3,3) parameters ──
q     = 3
v     = 40
k     = 12
lam   = 2
mu    = 4
Phi3  = 13
Phi6  = 7
f     = 24
g     = 15
alpha = 137
c_EH  = v * (q**2 - 1)  # 320


# ================================================================
# T1: Core prime 2099
# ================================================================
class TestT1_Core2099:
    """2099 = g·α + 4(k−1)."""

    def test_from_g_alpha(self):
        assert g * alpha + 4 * (k - 1) == 2099

    def test_alternative(self):
        """2099 = (v+1)(v+k+Φ₆) − c_EH."""
        assert (v + 1) * (v + k + Phi6) - c_EH == 2099

    def test_2099_is_prime(self):
        n = 2099
        assert all(n % d != 0 for d in range(2, int(n**0.5) + 1))

    def test_factor_41_59(self):
        """(v+1)(v+k+Φ₆) = 41 × 59."""
        assert (v + 1) * (v + k + Phi6) == 41 * 59 == 2419
        assert 2419 - c_EH == 2099


# ================================================================
# T2: Full grade-2 coefficient
# ================================================================
class TestT2_Grade2:
    """c(2) = 21493760 = 2^11 · 5 · 2099."""

    def test_c2_value(self):
        assert 21493760 == 2**11 * 5 * 2099

    def test_c2_from_graph(self):
        """c(2) = 2^(k−1) · (q+2) · (g·α + 4(k−1))."""
        val = 2**(k - 1) * (q + 2) * (g * alpha + 4 * (k - 1))
        assert val == 21493760

    def test_k_minus_1_exponent(self):
        assert k - 1 == 11

    def test_q_plus_2(self):
        assert q + 2 == 5


# ================================================================
# T3: Uniqueness scan
# ================================================================
class TestT3_Uniqueness:
    """q=3 is the unique prime power giving 2099."""

    def test_core_uniqueness(self):
        """Among prime powers 2..19, only q=3 gives 2099."""
        pp = [2, 3, 4, 5, 7, 8, 9, 11, 13, 16, 17, 19]
        hits = []
        for qq in pp:
            kk = qq * (qq + 1)
            gg = qq * (qq**2 + 1) // 2
            aa = (kk - 1)**2 + (qq + 1)**2
            val = gg * aa + 4 * (kk - 1)
            if val == 2099:
                hits.append(qq)
        assert hits == [3]

    def test_alternate_uniqueness(self):
        pp = [2, 3, 4, 5, 7, 8, 9, 11, 13, 16, 17, 19]
        hits = []
        for qq in pp:
            vv = (qq + 1) * (qq**2 + 1)
            kk = qq * (qq + 1)
            Phi6q = qq**2 - qq + 1
            cEHq = vv * (qq**2 - 1)
            val = (vv + 1) * (vv + kk + Phi6q) - cEHq
            if val == 2099:
                hits.append(qq)
        assert hits == [3]


# ================================================================
# T4: Cross-checks with known j-invariant data
# ================================================================
class TestT4_CrossChecks:
    """Relation to known moonshine data."""

    def test_c1_is_196884(self):
        """c(1) = 196884 = 196560 + 324."""
        c1 = 196884
        leech = 196560
        gap = (lam * q**2)**2
        assert c1 == leech + gap

    def test_c_EH_value(self):
        assert c_EH == 320

    def test_supersingular_factors(self):
        """41 and 59 are supersingular primes."""
        assert 41 in {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 41, 47, 59, 71}
        assert 59 in {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 41, 47, 59, 71}
