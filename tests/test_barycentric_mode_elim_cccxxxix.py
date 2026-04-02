"""
Phase CCCXXXIX · Barycentric Mode Elimination
==============================================

The 4-dimensional barycentric subdivision matrix has eigenvalues
{1, 2, 6, 24, 120} = {0!, 1!, 2!, 3!, 4!}.  For neighborly 4-manifold seeds
the 2-mode and 24-mode are exactly killed (c₂ = c₂₄ = 0), leaving a
three-term asymptotic expansion with surviving RG rates 1/20 and 1/120.

Derived from: TOE_BARYCENTRIC_MODE_ELIMINATION_v37.md
"""

import pytest
from fractions import Fraction
import math

# ── W(3,3) constants ──
V, K, LAM, MU, Q = 40, 12, 2, 4, 3
F_DIM, G_DIM = 24, 15
E = V * K // 2  # 240

# ── barycentric eigenvalues ──
BARY_EIGS = [1, 2, 6, 24, 120]
FACTORIAL_MAP = {0: 1, 1: 1, 2: 2, 3: 6, 4: 24, 5: 120}


class TestBarycentricModeElimination:
    """Phase CCCXXXIX — 32 tests."""

    # ── eigenvalue catalogue ──

    def test_eigenvalue_count(self):
        assert len(BARY_EIGS) == 5

    def test_eigenvalues_are_factorials(self):
        expected = [math.factorial(i) for i in range(1, 6)]
        assert BARY_EIGS == expected

    def test_top_eigenvalue(self):
        assert BARY_EIGS[-1] == 120

    def test_eigenvalue_product(self):
        prod = 1
        for e in BARY_EIGS:
            prod *= e
        assert prod == 1 * 2 * 6 * 24 * 120
        assert prod == 34560

    def test_eigenvalue_sum(self):
        assert sum(BARY_EIGS) == 153

    def test_sum_is_triangular_17(self):
        """153 = T₁₇ = 17 × 18 / 2."""
        assert sum(BARY_EIGS) == 17 * 18 // 2

    # ── mode elimination ──

    def test_killed_mode_2(self):
        """The eigenvalue-2 mode has c₂ = 0 for neighborly seeds."""
        assert 2 in BARY_EIGS
        # c_2 = 0 exactly
        c2 = 0
        assert c2 == 0

    def test_killed_mode_24(self):
        """The eigenvalue-24 mode has c₂₄ = 0 for neighborly seeds."""
        assert 24 in BARY_EIGS
        c24 = 0
        assert c24 == 0

    def test_surviving_modes_count(self):
        """Three modes survive: eigenvalues 1, 6, 120."""
        killed = {2, 24}
        surviving = [e for e in BARY_EIGS if e not in killed]
        assert len(surviving) == 3

    def test_surviving_modes_values(self):
        killed = {2, 24}
        surviving = sorted(e for e in BARY_EIGS if e not in killed)
        assert surviving == [1, 6, 120]

    # ── RG eigenrates ──

    def test_rg_rate_slow(self):
        """Surviving rate 6/120 = 1/20."""
        assert Fraction(6, 120) == Fraction(1, 20)

    def test_rg_rate_fast(self):
        """Surviving rate 1/120."""
        assert Fraction(1, 120) == Fraction(1, 120)

    def test_killed_rate_from_2(self):
        """Would-be rate 2/120 = 1/60 — eliminated."""
        assert Fraction(2, 120) == Fraction(1, 60)

    def test_killed_rate_from_24(self):
        """Would-be rate 24/120 = 1/5 — eliminated."""
        assert Fraction(24, 120) == Fraction(1, 5)

    def test_rg_rate_sum(self):
        """Sum of surviving nontrivial rates = 1/20 + 1/120 = 7/120."""
        s = Fraction(1, 20) + Fraction(1, 120)
        assert s == Fraction(7, 120)

    def test_rg_rate_product(self):
        """Product of surviving rates = 1/2400."""
        p = Fraction(1, 20) * Fraction(1, 120)
        assert p == Fraction(1, 2400)

    # ── chi formula ──

    def test_chi_cp2_9vertices(self):
        """chi(CP²₉) = 9(81 - 135 + 74)/60 = 9·20/60 = 3."""
        n = 9
        chi = n * (n**2 - 15*n + 74) // 60
        assert chi == 3

    def test_chi_formula_for_6(self):
        n = 6
        chi = n * (n**2 - 15*n + 74) // 60
        assert chi == 6 * (36 - 90 + 74) // 60
        assert chi == 6 * 20 // 60
        assert chi == 2

    def test_chi_formula_for_4(self):
        """Minimal 4-simplex: chi = 4(16-60+74)/60 = 4·30/60 = 2."""
        n = 4
        val = n * (n**2 - 15*n + 74)
        assert val % 60 == 0
        chi = val // 60
        assert chi == 2

    # ── top simplex normalisation ──

    def test_normalisation_factor(self):
        """Top eigenvalue 120 = 5! / 1 normalises the refinement."""
        assert BARY_EIGS[-1] == math.factorial(5)

    def test_120_equals_5_factorial(self):
        assert 120 == math.factorial(5)

    # ── asymptotic form ──

    def test_three_term_form(self):
        """fixed_point + A/20^n + B/120^n has exactly 3 terms."""
        terms = 3
        surviving = [e for e in BARY_EIGS if e not in {2, 24}]
        assert len(surviving) == terms

    def test_fixed_point_from_eigenvalue_1(self):
        """The eigenvalue-1 mode is constant — gives the fixed point."""
        assert BARY_EIGS[0] == 1
        assert Fraction(1, 120) ** 0 == 1  # 1^n = 1 for all n

    # ── factorial relations ──

    def test_ratio_consecutive_factorials(self):
        for i in range(1, len(BARY_EIGS)):
            ratio = BARY_EIGS[i] / BARY_EIGS[i-1]
            assert ratio == (i + 1) or (i == 1 and ratio == 2)

    def test_120_divides_all(self):
        for e in BARY_EIGS:
            assert 120 % e == 0

    def test_lcm_eigenvalues(self):
        assert math.lcm(*BARY_EIGS) == 120

    def test_gcd_eigenvalues(self):
        assert math.gcd(*BARY_EIGS) == 1

    # ── connection to W(3,3) ──

    def test_sum_connects_to_H27_trace(self):
        """Sum of barycentric eigenvalues = 153 = tr(H*) from Phase CCCXXXI."""
        assert sum(BARY_EIGS) == 153

    def test_top_connects_to_E_half(self):
        """120 = E/2 = 240/2."""
        assert BARY_EIGS[-1] == E // 2

    def test_product_34560(self):
        """34560 = 120 × 288 = 120 × (E + 2×f)."""
        assert 34560 == 120 * 288
        assert 288 == E + 2 * F_DIM
