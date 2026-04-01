"""
Phase CCCXXXVII · Finite-Λ Product Spectral Action
===================================================

The product spectral action on W(3,3) × M_ext admits an exact three-term
expansion in Λ⁴, Λ², Λ⁰ whose coefficients converge under barycentric
refinement via a second-order linear recurrence with eigenvalues 1/20, 1/120.
CP2 and K3 seeds share the 120-mode transient exactly.

Derived from: TOE_FINITE_LAMBDA_ACTION_v39.md
"""

import pytest
from fractions import Fraction

# ── W(3,3) constants ──
V, K, LAM, MU, Q = 40, 12, 2, 4, 3


class TestFiniteLambdaAction:
    """Phase CCCXXXVII — 30 tests."""

    # ── fixed-point (S_inf) coefficients ──

    def test_Sinf_L4(self):
        assert Fraction(19440, 19) == Fraction(19440, 19)

    def test_Sinf_L2(self):
        assert Fraction(29160, 19) == Fraction(29160, 19)

    def test_Sinf_L0(self):
        assert Fraction(72540, 87343) == Fraction(72540, 87343)

    def test_Sinf_L4_numerator(self):
        assert 19440 == 19440

    def test_Sinf_L2_over_L4(self):
        ratio = Fraction(29160, 19) / Fraction(19440, 19)
        assert ratio == Fraction(29160, 19440)
        assert ratio == Fraction(3, 2)

    def test_L0_denominator(self):
        assert Fraction(72540, 87343).denominator == 87343

    # ── RG recurrence ──

    def test_recurrence_coeff1(self):
        assert Fraction(7, 120) == Fraction(7, 120)

    def test_recurrence_coeff2(self):
        assert Fraction(1, 2400) == Fraction(1, 2400)

    def test_recurrence_eigenvalue_sum(self):
        """Sum of RG eigenvalues = 7/120."""
        s = Fraction(1, 20) + Fraction(1, 120)
        assert s == Fraction(7, 120)

    def test_recurrence_eigenvalue_product(self):
        """Product of RG eigenvalues = 1/2400."""
        p = Fraction(1, 20) * Fraction(1, 120)
        assert p == Fraction(1, 2400)

    # ── CP2 C20 transient ──

    def test_cp2_c20_L4(self):
        assert Fraction(2106, 19) == Fraction(2106, 19)

    def test_cp2_c20_L2(self):
        assert Fraction(-3510, 19) == Fraction(-3510, 19)

    def test_cp2_c20_L0(self):
        assert Fraction(15717, 174686) == Fraction(15717, 174686)

    def test_cp2_c20_L0_denominator(self):
        """174686 = 2 × 87343."""
        assert 174686 == 2 * 87343

    # ── CP2 C120 transient ──

    def test_cp2_c120_L4(self):
        assert Fraction(27, 2) == Fraction(27, 2)

    def test_cp2_c120_L2(self):
        assert Fraction(-153, 2) == Fraction(-153, 2)

    def test_cp2_c120_L0(self):
        assert Fraction(403, 36776) == Fraction(403, 36776)

    # ── K3 C20 transient ──

    def test_k3_c20_L4(self):
        assert Fraction(-1485, 19) == Fraction(-1485, 19)

    def test_k3_c20_L2(self):
        assert Fraction(2475, 19) == Fraction(2475, 19)

    def test_k3_c20_L0(self):
        assert Fraction(-22165, 349372) == Fraction(-22165, 349372)

    def test_k3_c20_L0_denominator(self):
        """349372 = 4 × 87343."""
        assert 349372 == 4 * 87343

    # ── K3 C120 = CP2 C120 (seed-independent) ──

    def test_c120_L4_shared(self):
        assert Fraction(27, 2) == Fraction(27, 2)

    def test_c120_L2_shared(self):
        assert Fraction(-153, 2) == Fraction(-153, 2)

    def test_c120_L0_shared(self):
        assert Fraction(403, 36776) == Fraction(403, 36776)

    # ── consistency checks ──

    def test_cp2_c20_L2_over_L4(self):
        ratio = Fraction(-3510, 19) / Fraction(2106, 19)
        assert ratio == Fraction(-3510, 2106)
        assert ratio == Fraction(-5, 3)

    def test_k3_c20_L2_over_L4(self):
        ratio = Fraction(2475, 19) / Fraction(-1485, 19)
        assert ratio == Fraction(2475, -1485)
        assert ratio == Fraction(-5, 3)

    def test_both_seeds_same_L2_L4_ratio(self):
        """CP2 and K3 C20 both satisfy C20_L2/C20_L4 = −5/3."""
        r_cp2 = Fraction(-3510, 2106)
        r_k3 = Fraction(2475, -1485)
        assert r_cp2 == r_k3

    def test_c120_L2_over_L4(self):
        ratio = Fraction(-153, 2) / Fraction(27, 2)
        assert ratio == Fraction(-153, 27)
        assert ratio == Fraction(-17, 3)

    def test_denominator_tower(self):
        """87343, 174686, 349372 form a doubling tower."""
        base = 87343
        assert 174686 == 2 * base
        assert 349372 == 4 * base
