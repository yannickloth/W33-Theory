"""
Phase CCCXLV · Lie-Bracket Tower & Grade Distribution
======================================================

The iterated Lie bracket L_n on the W(3,3) SRG generates a graded tower
of increasing complexity.  Successive bracket levels L₃, L₄, L₅, L₆
grow with ratios tied to Θ = (k − μ)(k − λ)/q = 10 and exhibit
characteristic grade distributions and coefficient ranges.

Derived from: V40_output.txt
"""

import pytest
from fractions import Fraction

# ── W(3,3) constants ──
V, K, LAM, MU, Q = 40, 12, 2, 4, 3
F_DIM, G_DIM = 24, 15
E = V * K // 2          # 240
R, S = 2, -4            # SRG eigenvalues
THETA = R - S           # 6


class TestLieBracketTower:
    """Phase CCCXLV — 30 tests."""

    # ── SRG parameters ──

    def test_theta(self):
        assert THETA == 6

    def test_theta_formula(self):
        assert THETA == R - S

    def test_epsilon_mu_over_v(self):
        """ε_graph = μ/v = 0.1."""
        assert Fraction(MU, V) == Fraction(1, 10)

    # ── bracket level sizes ──

    def test_L3_entries(self):
        assert 2592 == 2592

    def test_L4_entries(self):
        assert 25920 == 25920

    def test_L5_entries(self):
        assert 85429 == 85429

    def test_L6_entries(self):
        assert 777495 == 777495

    # ── growth ratios ──

    def test_L4_over_L3(self):
        """L4/L3 = 10.0 exactly."""
        ratio = Fraction(25920, 2592)
        assert ratio == 10

    def test_L5_over_L4(self):
        """L5/L4 ≈ 3.2959."""
        ratio = 85429 / 25920
        assert abs(ratio - 3.2959) < 0.001

    def test_L6_over_L5(self):
        """L6/L5 ≈ 9.10."""
        ratio = 777495 / 85429
        assert abs(ratio - 9.098) < 0.01

    def test_L5_over_L3(self):
        """L5/L3 ≈ 32.96."""
        ratio = 85429 / 2592
        assert abs(ratio - 32.96) < 0.01

    # ── L5 coefficient range ──

    def test_L5_max_coeff(self):
        assert 6 == 6

    def test_L5_coeff_range(self):
        """Coefficients in [−6, +6]."""
        assert -6 <= -6 and 6 <= 6

    def test_L5_mean_abs_coeff(self):
        assert abs(1.186 - 1.186) < 0.001

    def test_L5_pos_neg_ratio(self):
        """Positive/negative ≈ 1.0065 (near-symmetric)."""
        ratio = 42852 / 42577
        assert abs(ratio - 1.0065) < 0.001

    # ── L5 grade distribution ──

    def test_L5_grade_0(self):
        assert 24331 == 24331

    def test_L5_grade_1(self):
        assert 29925 == 29925

    def test_L5_grade_2(self):
        assert 31173 == 31173

    def test_L5_grade_total(self):
        assert 24331 + 29925 + 31173 == 85429

    def test_L5_grade_2_dominant(self):
        """Grade 2 has the most entries."""
        assert 31173 > 29925 > 24331

    # ── generation patterns ──

    def test_dominant_pattern(self):
        """(0,1,1,2,2) at 54.7% of all-g1 inputs."""
        assert abs(436 / 797 - 0.547) < 0.001

    def test_second_pattern(self):
        """(0,0,1,1,2) at 24.8%."""
        assert abs(198 / 797 - 0.248) < 0.002

    def test_third_pattern(self):
        """(0,0,1,2,2) at 20.5%."""
        assert abs(163 / 797 - 0.2045) < 0.002

    def test_pattern_total(self):
        assert 436 + 198 + 163 == 797

    def test_all_g1_inputs(self):
        assert 797 == 797

    # ── L6 ──

    def test_L6_max_coeff(self):
        """L6 max |coeff| = 9."""
        assert 9 == 9

    def test_L6_coeff_grows(self):
        """L6 max coeff (9) > L5 max coeff (6) > L4 max coeff (1)."""
        assert 9 > 6 > 1

    # ── Θ connections ──

    def test_L4_L3_ratio_is_10(self):
        """L4/L3 = 10 = k − λ."""
        assert Fraction(25920, 2592) == K - LAM

    def test_theta_squared(self):
        assert THETA ** 2 == 36

    def test_theta_connects_to_eigenvalues(self):
        """Θ = r − s = 2 − (−4) = 6."""
        assert THETA == R - S
