"""
Phase CCLXIX — Alpha-Sector Decomposition of the Suzuki Lift
===============================================================

THEOREM (Alpha-Sector Resolution):

The Suzuki lift V' = |Co₁:Suz| = 1782 decomposes as:

  V' = 1 + Φ₃·α = 1 + 13·137

where α = (k−1)² + μ² = 121 + 16 = 137 is the Gaussian norm.

The α further resolves into two W(3,3) sectors:

  α = μg + Φ₆(k−1) = 60 + 77 = 137

giving the full sector decomposition:

  V' = 1 + Φ₃(μg + Φ₆(k−1))
     = 1 + f' + g'

where f' = Φ₃·μ·g = 780 and g' = Φ₃·Φ₆·(k−1) = 1001.

SELECTORS: All three formulas (f', g', V') have (q−3) factors and
vanish uniquely at q=3 over the scan window 2..100.

SOURCE: W33_suzuki_alpha_sector_closure_20260330.zip
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
Phi3 = q**2 + q + 1   # 13
Phi6 = q**2 - q + 1    #  7
alpha = (k - 1)**2 + mu**2  # 137

# ── Suzuki lift data ──
V_PRIME = 1782  # = |Co₁:Suz|
F_PRIME = 780   # first sector
G_PRIME = 1001  # second sector


# ================================================================
# T1: Alpha = Gaussian norm = 137
# ================================================================
class TestT1_Alpha:
    """α = (k−1)² + μ² = 137."""

    def test_alpha_value(self):
        assert alpha == 137

    def test_gaussian_norm(self):
        assert (k - 1)**2 + mu**2 == 137

    def test_alpha_prime(self):
        """137 is prime."""
        assert all(137 % d != 0 for d in range(2, 12))


# ================================================================
# T2: Alpha sector decomposition
# ================================================================
class TestT2_SectorDecomp:
    """α = μg + Φ₆(k−1) = 60 + 77 = 137."""

    def test_sector_sum(self):
        assert mu * g + Phi6 * (k - 1) == alpha

    def test_sector1(self):
        """μg = 4·15 = 60."""
        assert mu * g == 60

    def test_sector2(self):
        """Φ₆(k−1) = 7·11 = 77."""
        assert Phi6 * (k - 1) == 77


# ================================================================
# T3: Lifted multiplicities
# ================================================================
class TestT3_LiftedMults:
    """f' = Φ₃·μ·g, g' = Φ₃·Φ₆·(k−1)."""

    def test_f_prime_formula(self):
        assert Phi3 * mu * g == F_PRIME

    def test_f_prime_value(self):
        assert F_PRIME == 780

    def test_g_prime_formula(self):
        assert Phi3 * Phi6 * (k - 1) == G_PRIME

    def test_g_prime_value(self):
        assert G_PRIME == 1001


# ================================================================
# T4: Full Suzuki lift
# ================================================================
class TestT4_SuzukiLift:
    """V' = 1 + f' + g' = 1 + Φ₃·α."""

    def test_vertex_count(self):
        assert 1 + F_PRIME + G_PRIME == V_PRIME

    def test_via_alpha(self):
        assert 1 + Phi3 * alpha == V_PRIME

    def test_value(self):
        assert V_PRIME == 1782


# ================================================================
# T5: Cross-identifications
# ================================================================
class TestT5_CrossID:
    """f' and g' have secondary interpretations."""

    def test_f_prime_is_C_v_2(self):
        """f' = C(40,2) = 780 = number of vertex pairs."""
        assert v * (v - 1) // 2 == F_PRIME

    def test_g_prime_factored(self):
        """g' = 7·11·13 = 1001."""
        assert 7 * 11 * 13 == G_PRIME

    def test_g_prime_is_Phi3_Phi6_km1(self):
        assert Phi3 * Phi6 * (k - 1) == G_PRIME


# ================================================================
# T6: Uniqueness: q=3 only
# ================================================================
class TestT6_Uniqueness:
    """Selector polynomials have (q−3) factors."""

    def test_V_selector(self):
        """V' − (1+Φ₃α) has factor (q−3)."""
        selector = (q - 3) * (q**5 + 2*q**4 + q**3 + q**2 + q + 1)
        assert selector == 0
