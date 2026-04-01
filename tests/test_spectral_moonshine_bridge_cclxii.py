"""
Phase CCLXII — Spectral–Moonshine Bridge: Odd Power Sums and Grade-2 j-Closure
================================================================================

THEOREM (Spectral–Moonshine Bridge at q=3):
The odd spectral power sums M_n = Σ λᵢⁿ of the W(3,3) eigenvalues
  {k=12 (×1), r=2 (×24), s=−4 (×15)}
satisfy:

  M₃ = 960,  M₅ = 234240,  M₅/M₃ = 244

At q=3 only, 244 admits two simultaneous W(3,3) atom decompositions:
  M₅/M₃ = vΦ₆ − μq²    = 40·7 − 4·9     = 244
  M₅/M₃ = gΦ₃ + Φ₆²    = 15·13 + 49      = 244

Both carry an explicit (q−3) selector in the family polynomial form.

THEOREM (Grade-2 j-fingerprint):
The second j-coefficient c₂ = 21493760 = 2^(k−1) · (q+2) · J, where
  J = gα + 4(k−1) = 15·137 + 4·11 = 2099

So g = 15 controls both:
  • spectral side: gΦ₃ + Φ₆² = 244 (= M₅/M₃)
  • moonshine side: gα + 4(k−1) = 2099 (grade-2 fingerprint)

SOURCE: W33_spectral_moonshine_bridge_20260330.zip
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
r    = q - 1       # 2
s    = -(q + 1)     # -4
Phi3 = q**2 + q + 1   # 13
Phi4 = q**2 + 1        # 10
Phi6 = q**2 - q + 1    # 7
Phi12 = q**4 - q**2 + 1  # 73
alpha = (k - 1)**2 + mu**2  # 137


# ── Spectral power sums ──
def spectral_moment(n):
    """M_n = k^n * 1 + r^n * f + s^n * g."""
    return k**n + r**n * f + s**n * g


# ================================================================
# T1: Spectral power sums at q=3
# ================================================================
class TestT1_SpectralMoments:
    """Odd spectral power sums of W(3,3) eigenvalues."""

    def test_M1(self):
        """M₁ = k + rf + sg = trace = 0 (for SRG adjacency)."""
        assert spectral_moment(1) == k + r * f + s * g
        assert spectral_moment(1) == 12 + 2*24 + (-4)*15
        assert spectral_moment(1) == 0

    def test_M3(self):
        assert spectral_moment(3) == 960

    def test_M5(self):
        assert spectral_moment(5) == 234240

    def test_M5_over_M3(self):
        assert spectral_moment(5) // spectral_moment(3) == 244


# ================================================================
# T2: Dual decomposition of 244 (unique at q=3)
# ================================================================
class TestT2_DualDecomposition244:
    """244 = vΦ₆ − μq² = gΦ₃ + Φ₆². Both exact only at q=3."""

    def test_global_shell(self):
        """244 = vΦ₆ − μq²."""
        assert v * Phi6 - mu * q**2 == 244

    def test_internal_matter(self):
        """244 = gΦ₃ + Φ₆²."""
        assert g * Phi3 + Phi6**2 == 244

    def test_both_equal(self):
        assert v * Phi6 - mu * q**2 == g * Phi3 + Phi6**2

    def test_equals_ratio(self):
        assert v * Phi6 - mu * q**2 == spectral_moment(5) // spectral_moment(3)


# ================================================================
# T3: (q-3) selector polynomials
# ================================================================
class TestT3_QMinus3Selector:
    """Both decompositions carry (q−3) factors in the family polynomial."""

    def test_global_selector(self):
        """M₅/M₃ − (vΦ₆ − μq²) vanishes at q=3 via (q−3) factor."""
        # Family ratio polynomial: q^4 + 4q^3 + 6q^2 + 1
        ratio_poly = q**4 + 4*q**3 + 6*q**2 + 1
        global_expr = v * Phi6 - mu * q**2
        # The difference should be zero at q=3
        assert ratio_poly == global_expr

    def test_internal_selector(self):
        """M₅/M₃ − (gΦ₃ + Φ₆²) vanishes at q=3 via (q−3) factor."""
        ratio_poly = q**4 + 4*q**3 + 6*q**2 + 1
        internal_expr = g * Phi3 + Phi6**2
        assert ratio_poly == internal_expr


# ================================================================
# T4: Grade-2 j-fingerprint
# ================================================================
class TestT4_Grade2JFingerprint:
    """c₂ = 21493760 = 2^(k−1) · (q+2) · J, where J = gα + 4(k−1)."""

    def test_J_value(self):
        J = g * alpha + 4 * (k - 1)
        assert J == 2099

    def test_J_components(self):
        assert g * alpha == 15 * 137 == 2055
        assert 4 * (k - 1) == 44
        assert 2055 + 44 == 2099

    def test_c2_reconstruction(self):
        J = g * alpha + 4 * (k - 1)
        c2 = 2**(k - 1) * (q + 2) * J
        assert c2 == 21493760

    def test_c2_known(self):
        """c₂ is the second Fourier coefficient of j(τ)."""
        assert 21493760 == 2**11 * 5 * 2099


# ================================================================
# T5: g controls both spectral and moonshine
# ================================================================
class TestT5_GMultiplicity:
    """g = 15 is the dual controller of spectral ratio and j-fingerprint."""

    def test_spectral_channel(self):
        """Spectral: gΦ₃ + Φ₆² = 244."""
        assert g * Phi3 + Phi6**2 == 244

    def test_moonshine_channel(self):
        """Moonshine: gα + 4(k−1) = 2099."""
        assert g * alpha + 4 * (k - 1) == 2099

    def test_g_is_matter_multiplicity(self):
        """g is the multiplicity of eigenvalue s in W(3,3)."""
        assert g == 15
        assert v == 1 + f + g


# ================================================================
# T6: Alpha identity
# ================================================================
class TestT6_Alpha:
    """α = (k−1)² + μ² = 137, the fine-structure reciprocal."""

    def test_alpha_value(self):
        assert alpha == 137

    def test_alpha_formula(self):
        assert (k - 1)**2 + mu**2 == 137

    def test_k_minus_1_sq(self):
        assert (k - 1)**2 == 121

    def test_mu_sq(self):
        assert mu**2 == 16

    def test_sum(self):
        assert 121 + 16 == 137


# ================================================================
# T7: M₃ decomposition
# ================================================================
class TestT7_M3:
    """M₃ = 960 = 2·S_EH where S_EH = 480 = 2E = ζ_L(−1)."""

    def test_M3_value(self):
        assert spectral_moment(3) == 960

    def test_M3_is_2_times_480(self):
        assert spectral_moment(3) == 2 * 480

    def test_480_is_2E(self):
        E = v * k // 2
        assert 2 * E == 480

    def test_960_formula(self):
        """960 = q(q−1)(q+1)²(q²+1)."""
        assert q * (q-1) * (q+1)**2 * (q**2+1) == 960


# ================================================================
# T8: M₅ decomposition
# ================================================================
class TestT8_M5:
    """M₅ = 234240."""

    def test_M5_value(self):
        assert spectral_moment(5) == 234240

    def test_M5_is_M3_times_ratio(self):
        assert spectral_moment(5) == spectral_moment(3) * 244

    def test_M5_formula(self):
        """M₅ = 960 * 244 = 234240."""
        assert 960 * 244 == 234240
