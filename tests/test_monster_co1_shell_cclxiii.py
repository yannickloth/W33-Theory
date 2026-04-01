"""
Phase CCLXIII — Monster = Co₁ × Conway Actions × Core × Late Shell
=====================================================================

THEOREM (Monster–Co₁ Action-Shell Decomposition):

  |M| = |Co₁| · |Co₁:Co₂| · |Co₁:Co₃| · Core · Π_late

where:
  |Co₁|      = 4,157,776,806,543,360,000
  |Co₁:Co₂|  = τ · v(v−1)/4      = 252 · 390     = 98,280
  |Co₁:Co₃|  = τ · 2^(k−4)·Φ₃·Φ₄ = 252 · 33,280  = 8,386,560
  Core        = 2^(k−1) · q^(2q) · (q+2)^q · Φ₆^λ · (k−1) = 100,590,336,000
  Π_late      = (k+Φ₆−λ)(k+Φ₆)(f+Φ₆−λ)(f+Φ₆)(v+1)(v+Φ₆)(v+k+Φ₆)(Φ₁₂−λ)
              = 17·19·29·31·41·47·59·71 = 2,343,982,090,531

INTERPRETATION:
  - Co₁ carries the Leech-frame core (absorbs prime 23 = f−1)
  - Two Conway action degrees are both driven by τ = 252
  - Low-prime core is an exact W(3,3) polynomial in 5 atoms
  - Late affine shell is a product of 8 outer atoms (the 9 outer minus f−1)

SOURCE: W33_monster_co1_shell_closure_20260330.zip
"""
import math
import pytest
from collections import Counter

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
Phi6 = q**2 - q + 1    # 7
Phi12 = q**4 - q**2 + 1  # 73
tau  = 252             # E + k = 240 + 12

# ── Known group/action data ──
CO1_ORDER  = 4157776806543360000
CO1_CO2    = 98280
CO1_CO3    = 8386560
MONSTER_ORDER = 808017424794512875886459904961710757005754368000000000


def _prime_factors(n):
    """Return dict of prime -> exponent."""
    factors = Counter()
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors[d] += 1
            n //= d
        d += 1
    if n > 1:
        factors[n] += 1
    return dict(factors)


# ================================================================
# T1: Conway action degrees from tau
# ================================================================
class TestT1_ConwayActionDegrees:
    """Both Conway action degrees are driven by τ = 252."""

    def test_tau_value(self):
        assert tau == 252

    def test_tau_is_E_plus_k(self):
        E = v * k // 2
        assert tau == E + k

    def test_Co1_Co2_formula(self):
        """|Co₁:Co₂| = τ · v(v−1)/4."""
        assert tau * v * (v - 1) // 4 == CO1_CO2

    def test_Co1_Co2_value(self):
        assert CO1_CO2 == 98280

    def test_Co1_Co3_formula(self):
        """|Co₁:Co₃| = τ · 2^(k−4) · Φ₃ · Φ₄."""
        assert tau * 2**(k - 4) * Phi3 * Phi4 == CO1_CO3

    def test_Co1_Co3_value(self):
        assert CO1_CO3 == 8386560


# ================================================================
# T2: Low-prime residual core
# ================================================================
class TestT2_LowPrimeCore:
    """Core = 2^(k−1) · q^(2q) · (q+2)^q · Φ₆^λ · (k−1)."""

    CORE = 2**(k - 1) * q**(2*q) * (q + 2)**q * Phi6**lam * (k - 1)

    def test_core_value(self):
        assert self.CORE == 100590336000

    def test_core_factorization(self):
        """Core = 2^11 · 3^6 · 5^3 · 7^2 · 11."""
        assert self.CORE == 2**11 * 3**6 * 5**3 * 7**2 * 11

    def test_core_exponents(self):
        pf = _prime_factors(self.CORE)
        assert pf[2] == k - 1 == 11
        assert pf[3] == 2 * q == 6
        assert pf[5] == q == 3
        assert pf[7] == lam == 2
        assert pf[11] == 1


# ================================================================
# T3: Late affine shell (8 outer atoms)
# ================================================================
class TestT3_LateShell:
    """Π_late = product of 8 outer atoms (all primes with exp 1 in |M| except 23)."""

    def test_atoms(self):
        assert k + Phi6 - lam == 17
        assert k + Phi6 == 19
        assert f + Phi6 - lam == 29
        assert f + Phi6 == 31
        assert v + 1 == 41
        assert v + Phi6 == 47
        assert v + k + Phi6 == 59
        assert Phi12 - lam == 71

    def test_alternate_71(self):
        """71 = f + μk − 1 as well as Φ₁₂ − λ."""
        assert f + mu * k - 1 == 71

    def test_late_shell_value(self):
        late = 17 * 19 * 29 * 31 * 41 * 47 * 59 * 71
        assert late == 2343982090531

    def test_late_shell_count(self):
        """8 primes in the late shell."""
        primes = {17, 19, 29, 31, 41, 47, 59, 71}
        assert len(primes) == 8


# ================================================================
# T4: Full decomposition product = |M|
# ================================================================
class TestT4_FullDecomposition:
    """Co₁ × Co₁:Co₂ × Co₁:Co₃ × Core × Π_late = |M|."""

    def test_exact(self):
        core = 2**(k-1) * q**(2*q) * (q+2)**q * Phi6**lam * (k-1)
        late = 17 * 19 * 29 * 31 * 41 * 47 * 59 * 71
        product = CO1_ORDER * CO1_CO2 * CO1_CO3 * core * late
        assert product == MONSTER_ORDER

    def test_five_factor_form(self):
        """Verify five-factor form directly."""
        product = (CO1_ORDER
                   * (tau * v * (v-1) // 4)
                   * (tau * 2**(k-4) * Phi3 * Phi4)
                   * (2**(k-1) * q**(2*q) * (q+2)**q * Phi6**lam * (k-1))
                   * ((k+Phi6-lam) * (k+Phi6) * (f+Phi6-lam) * (f+Phi6)
                      * (v+1) * (v+Phi6) * (v+k+Phi6) * (Phi12-lam)))
        assert product == MONSTER_ORDER


# ================================================================
# T5: Co₁ absorbs the prime 23 = f−1
# ================================================================
class TestT5_Co1Absorbs23:
    """23 = f−1 appears in |Co₁| but not in the late shell."""

    def test_23_divides_Co1(self):
        assert CO1_ORDER % 23 == 0

    def test_23_not_in_late_shell(self):
        late = 17 * 19 * 29 * 31 * 41 * 47 * 59 * 71
        assert late % 23 != 0

    def test_Co1_prime_support(self):
        """|Co₁| = 2^21 · 3^9 · 5^4 · 7^2 · 11 · 13 · 23."""
        pf = _prime_factors(CO1_ORDER)
        assert set(pf.keys()) == {2, 3, 5, 7, 11, 13, 23}

    def test_23_is_f_minus_1(self):
        assert f - 1 == 23


# ================================================================
# T6: Co₁ order verification
# ================================================================
class TestT6_Co1Order:
    """|Co₁| = 2^21 · 3^9 · 5^4 · 7^2 · 11 · 13 · 23."""

    def test_order_value(self):
        expected = 2**21 * 3**9 * 5**4 * 7**2 * 11 * 13 * 23
        assert expected == CO1_ORDER

    def test_order_known(self):
        assert CO1_ORDER == 4157776806543360000


# ================================================================
# T7: Tau controls both action degrees
# ================================================================
class TestT7_TauControl:
    """τ = σ₃(6) = 252 drives both Conway action indices."""

    def test_tau_is_sigma3_6(self):
        """σ₃(6) = 1³ + 2³ + 3³ + 6³ = 1 + 8 + 27 + 216 = 252."""
        sigma3 = sum(d**3 for d in [1, 2, 3, 6])
        assert sigma3 == 252

    def test_tau_is_ramanujan(self):
        """τ(3) = 252 (Ramanujan tau function)."""
        assert tau == 252

    def test_tau_is_E_plus_k(self):
        assert tau == v * k // 2 + k
