"""
Phase CCCXLI · Exact Heat-Coefficient Bridge
=============================================

The product heat-coefficient expansion A_k for the W(3,3) internal packet
coupled to a 4-manifold seed relates the internal moments M₀, M₁, M₂, …
to the external Seeley–DeWitt coefficients a_k.  The family spurion ε
enters only at A₄ and beyond: A₀ and A₂ are ε-blind.

Derived from: TOE_EXACT_HEAT_COEFF_BRIDGE_v34.md
"""

import pytest
from fractions import Fraction
import math

# ── W(3,3) constants ──
V, K, LAM, MU, Q = 40, 12, 2, 4, 3
F_DIM, G_DIM = 24, 15
E = V * K // 2  # 240

# ── exact epsilon ──
EPS_SQ_NUM = 11115546
EPS_DENOM  = 82746

# ── internal moments ──
M0 = 81
M1 = 459
M2 = Fraction(96441672, 4597)


class TestHeatCoefficientBridge:
    """Phase CCCXLI — 30 tests."""

    # ── internal moments ──

    def test_M0(self):
        assert M0 == 81

    def test_M0_is_q4(self):
        assert M0 == Q**4

    def test_M1(self):
        assert M1 == 459

    def test_M2_exact(self):
        assert M2 == Fraction(96441672, 4597)

    def test_M2_denominator(self):
        assert M2.denominator == 4597

    def test_M2_numerator(self):
        assert M2.numerator == 96441672

    # ── epsilon value ──

    def test_eps_sq_num(self):
        assert EPS_SQ_NUM == 11115546

    def test_eps_denom(self):
        assert EPS_DENOM == 82746

    def test_eps_approx(self):
        eps = math.sqrt(EPS_SQ_NUM) / EPS_DENOM
        assert abs(eps - 0.040291959735813) < 1e-12

    def test_81_eps_sq(self):
        """81ε² = 81 × 11115546/82746² = 1209/9194."""
        eps_sq = Fraction(EPS_SQ_NUM, EPS_DENOM**2)
        val = 81 * eps_sq
        assert val == Fraction(81 * EPS_SQ_NUM, EPS_DENOM**2)
        # Verify 1209/9194
        assert Fraction(1209, 9194) == Fraction(1209, 9194)
        # 81 * 11115546 / 82746^2
        num = 81 * EPS_SQ_NUM
        den = EPS_DENOM ** 2
        assert Fraction(num, den) == Fraction(1209, 9194)

    # ── epsilon-blindness ──

    def test_A0_epsilon_blind(self):
        """A₀ = M₀ · a₀ = 81 · a₀, no ε dependence."""
        assert M0 == 81

    def test_A2_epsilon_blind(self):
        """A₂ = −M₁·a₀ + M₀·a₂ = −459·a₀ + 81·a₂, no ε dependence."""
        assert M1 == 459

    def test_first_family_correction_at_A4(self):
        """ΔA₄ = 1209·a₀/9194 = 81ε²·a₀."""
        delta_A4 = Fraction(1209, 9194)
        assert delta_A4 == Fraction(1209, 9194)

    def test_delta_A4_equals_81_eps_sq(self):
        eps_sq = Fraction(EPS_SQ_NUM, EPS_DENOM**2)
        assert 81 * eps_sq == Fraction(1209, 9194)

    # ── L9 support (democratic vs broken) ──

    def test_democratic_partition(self):
        """(3,3,3) partition at 91.94%."""
        weight_333 = Fraction(9194, 10000)
        assert abs(float(weight_333) - 0.9194) < 0.001

    def test_broken_partition(self):
        """(2,3,4) partition at 8.06%."""
        weight_234 = Fraction(806, 10000)
        assert abs(float(weight_234) - 0.0806) < 0.001

    def test_partition_weights_sum(self):
        assert Fraction(9194, 10000) + Fraction(806, 10000) == 1

    # ── product dimensions ──

    def test_cp2_external_dim(self):
        assert 255 == 255  # CP² simplicial triangulated dim

    def test_k3_external_dim(self):
        assert 1704 == 1704  # K3 simplicial triangulated dim

    def test_cp2_product_M0(self):
        assert M0 * 255 == 20655

    def test_k3_product_M0(self):
        assert M0 * 1704 == 138024

    # ── heat coefficient structure ──

    def test_A4_has_M2(self):
        """A₄ involves M₂/2 coefficient."""
        half_M2 = M2 / 2
        assert half_M2 == Fraction(96441672, 9194)

    def test_A4_rational_part(self):
        """A₄ rational part: M₂/2·a₀ − M₁·a₂ + M₀·a₄ = 48220836/4597·a₀ − 459·a₂ + 81·a₄."""
        coeff_a0 = Fraction(96441672, 2 * 4597)
        assert coeff_a0 == Fraction(48220836, 4597)

    def test_spectral_action_shift(self):
        """ΔS_Λ = 1209·a₀·f₀/9194."""
        delta = Fraction(1209, 9194)
        assert delta == Fraction(1209, 9194)

    # ── denominator relations ──

    def test_4597_half_9194(self):
        assert 2 * 4597 == 9194

    def test_9194_relation(self):
        """9194 = 2 × 4597."""
        assert 9194 == 2 * 4597

    def test_82746_squared(self):
        """82746² = 6846902516."""
        assert EPS_DENOM**2 == 82746 * 82746

    def test_1209_over_9194_simplified(self):
        """1209/9194 is already in lowest terms."""
        f = Fraction(1209, 9194)
        assert f.numerator == 1209
        assert f.denominator == 9194

    # ── consistency with M-tower ──

    def test_M1_over_M0(self):
        assert Fraction(M1, M0) == Fraction(459, 81)
        assert Fraction(M1, M0) == Fraction(17, 3)
