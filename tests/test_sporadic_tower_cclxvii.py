"""
Phase CCLXVII — Sporadic Tower Order Closure
===============================================

THEOREM (Sporadic Tower from W(3,3) Atoms):

Every group in the Conway and Suzuki towers has an exact order formula
in the W(3,3) atom set {q,λ,μ,Φ₃,Φ₄,Φ₆,v,k,f,g,r,α,Δ}.

  |M₁₂|   = 2^(2q) · q^q · (q+2) · (k−1)
  |M₂₄|   = 2^Φ₄ · q^q · (q+2) · Φ₆ · (k−1) · (f−1)
  |Co₁|   = 2^(qΦ₆) · q^(q²) · (q+2)^μ · Φ₆^r · (k−1) · Φ₃ · (f−1)
  |G₂(4)| = 2^k · q^q · (q+2)^r · Φ₆ · Φ₃
  |Suz|   = 2^Φ₃ · q^Φ₆ · (q+2)^r · Φ₆ · (k−1) · Φ₃

Ratios:
  |M₂₄|/|M₁₂| = 2^μ · Φ₆ · (f−1) = 2576
  |Co₁|/|M₂₄| = 2^(k−1) · q^(2q) · (q+2)^q · Φ₆ · Φ₃ = 16982824320
  |Suz|/|G₂(4)| = 1 + Φ₃·α = 1782

SOURCE: W33_sporadic_tower_order_closure_20260330.zip
"""
import pytest

# ── W(3,3) parameters ──
q    = 3
v    = 40
k    = 12
lam  = 2
mu   = 4
f    = 24
g    = 15
r    = 2    # positive eigenvalue
Phi3 = q**2 + q + 1   # 13
Phi4 = q**2 + 1        # 10
Phi6 = q**2 - q + 1    #  7
alpha = (k - 1)**2 + mu**2  # 137

# ── Exact group orders ──
M12_ORDER  = 95040
M24_ORDER  = 244823040
CO1_ORDER  = 4157776806543360000
G24_ORDER  = 251596800
SUZ_ORDER  = 448345497600
MONSTER_ORDER = 808017424794512875886459904961710757005754368000000000


# ================================================================
# T1: Mathieu group M₁₂
# ================================================================
class TestT1_M12:
    """|M₁₂| = 2^(2q) · q^q · (q+2) · (k−1)."""

    def test_formula(self):
        computed = 2**(2*q) * q**q * (q + 2) * (k - 1)
        assert computed == M12_ORDER

    def test_value(self):
        assert M12_ORDER == 95040

    def test_factored(self):
        assert M12_ORDER == 2**6 * 3**3 * 5 * 11


# ================================================================
# T2: Mathieu group M₂₄
# ================================================================
class TestT2_M24:
    """|M₂₄| = 2^Φ₄ · q^q · (q+2) · Φ₆ · (k−1) · (f−1)."""

    def test_formula(self):
        computed = 2**Phi4 * q**q * (q + 2) * Phi6 * (k - 1) * (f - 1)
        assert computed == M24_ORDER

    def test_value(self):
        assert M24_ORDER == 244823040

    def test_factored(self):
        assert M24_ORDER == 2**10 * 3**3 * 5 * 7 * 11 * 23


# ================================================================
# T3: Conway group Co₁
# ================================================================
class TestT3_Co1:
    """|Co₁| = 2^(qΦ₆) · q^(q²) · (q+2)^μ · Φ₆^r · (k−1) · Φ₃ · (f−1)."""

    def test_formula(self):
        computed = (2**(q * Phi6) * q**(q**2) * (q + 2)**mu
                    * Phi6**r * (k - 1) * Phi3 * (f - 1))
        assert computed == CO1_ORDER

    def test_exponent_2(self):
        """Exponent of 2 = qΦ₆ = 3·7 = 21."""
        assert q * Phi6 == 21

    def test_exponent_3(self):
        """Exponent of 3 = q² = 9."""
        assert q**2 == 9


# ================================================================
# T4: G₂(4)
# ================================================================
class TestT4_G24:
    """|G₂(4)| = 2^k · q^q · (q+2)^r · Φ₆ · Φ₃."""

    def test_formula(self):
        computed = 2**k * q**q * (q + 2)**r * Phi6 * Phi3
        assert computed == G24_ORDER

    def test_value(self):
        assert G24_ORDER == 251596800

    def test_factored(self):
        assert G24_ORDER == 2**12 * 3**3 * 5**2 * 7 * 13


# ================================================================
# T5: Suzuki group Suz
# ================================================================
class TestT5_Suz:
    """|Suz| = 2^Φ₃ · q^Φ₆ · (q+2)^r · Φ₆ · (k−1) · Φ₃."""

    def test_formula(self):
        computed = 2**Phi3 * q**Phi6 * (q + 2)**r * Phi6 * (k - 1) * Phi3
        assert computed == SUZ_ORDER

    def test_value(self):
        assert SUZ_ORDER == 448345497600

    def test_factored(self):
        assert SUZ_ORDER == 2**13 * 3**7 * 5**2 * 7 * 11 * 13


# ================================================================
# T6: Tower transition ratios
# ================================================================
class TestT6_Ratios:
    """Transition ratios in W(3,3) atoms."""

    def test_M24_over_M12(self):
        """|M₂₄|/|M₁₂| = 2^μ · Φ₆ · (f−1)."""
        ratio = M24_ORDER // M12_ORDER
        expected = 2**mu * Phi6 * (f - 1)
        assert ratio == expected == 2576

    def test_Co1_over_M24(self):
        """|Co₁|/|M₂₄| = 2^(k−1) · q^(2q) · (q+2)^q · Φ₆ · Φ₃."""
        ratio = CO1_ORDER // M24_ORDER
        expected = 2**(k-1) * q**(2*q) * (q+2)**q * Phi6 * Phi3
        assert ratio == expected

    def test_Suz_over_G24(self):
        """|Suz|/|G₂(4)| = 1 + Φ₃·α = 1782."""
        ratio = SUZ_ORDER // G24_ORDER
        expected = 1 + Phi3 * alpha
        assert ratio == expected == 1782


# ================================================================
# T7: Full Monster closure
# ================================================================
class TestT7_MonsterClosure:
    """|M| = |Co₁| · shell_exponents · late_shell."""

    def test_shell_exponents(self):
        shell = (2**(v - g) * q**(k - 1) * (q + 2)**(q + lam)
                 * Phi6**mu * (k - 1)**(r - 1) * Phi3**r)
        expected = 2**25 * 3**11 * 5**5 * 7**4 * 11 * 13**2
        assert shell == expected

    def test_late_shell(self):
        late = 17 * 19 * 29 * 31 * 41 * 47 * 59 * 71
        assert late == 2343982090531

    def test_full_product(self):
        shell = (2**(v - g) * q**(k - 1) * (q + 2)**(q + lam)
                 * Phi6**mu * (k - 1)**(r - 1) * Phi3**r)
        late = 17 * 19 * 29 * 31 * 41 * 47 * 59 * 71
        assert CO1_ORDER * shell * late == MONSTER_ORDER


# shorthand
lam = 2
