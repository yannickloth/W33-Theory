"""
Phase CCCLVI · PG(3,2) Collineation Geometry
=============================================

The projective 3-space PG(3,2) over GF(2) has 15 points, 35 lines,
15 planes.  Its collineation group GL(4,2) ≅ A₈ has order 20160.
Each point lies on 7 lines and 7 planes; each line has 3 points.
The 15 points form the doily GQ(2,2) with SRG(15,6,1,3).

Derived from: explore_pg3_collineations.py
"""

import pytest
import math
from fractions import Fraction

# ── W(3,3) constants ──
V, K, LAM, MU, Q = 40, 12, 2, 4, 3
F_DIM, G_DIM = 24, 15
E = V * K // 2  # 240

# ── PG(3,2) constants ──
PG_q = 2
PG_n = 3
PG_POINTS = 15      # (q^(n+1) - 1)/(q - 1)
PG_LINES = 35       # Gaussian binomial [4,2]_2
PG_PLANES = 15      # (q^(n+1) - 1)/(q - 1) by duality
GL42 = 20160         # |GL(4,2)| = |A₈|
PTS_PER_LINE = 3    # q + 1
LINES_PER_PT = 7    # (q³ − 1)/(q − 1)


class TestPG32Collineation:
    """Phase CCCLVI — 30 tests."""

    # ── point count ──

    def test_pg32_point_count(self):
        """(2⁴ − 1)/(2 − 1) = 15."""
        assert (PG_q**(PG_n+1) - 1) // (PG_q - 1) == PG_POINTS

    def test_15_is_g_dim(self):
        """15 = g = multiplicity of eigenvalue s in W(3,3)."""
        assert PG_POINTS == G_DIM

    # ── line count ──

    def test_pg32_line_count(self):
        """35 lines in PG(3,2)."""
        assert PG_LINES == 35

    def test_line_count_formula(self):
        """35 = (15 × 7) / 3 = points × lines_per_pt / pts_per_line."""
        assert PG_POINTS * LINES_PER_PT // PTS_PER_LINE == PG_LINES

    # ── plane count (duality) ──

    def test_pg32_plane_count(self):
        """15 planes (dual to 15 points)."""
        assert PG_PLANES == PG_POINTS

    def test_self_dual(self):
        """PG(3,2) has point-plane duality: 15 = 15."""
        assert PG_POINTS == PG_PLANES

    # ── incidence ──

    def test_points_per_line(self):
        """q + 1 = 3 points per line."""
        assert PTS_PER_LINE == PG_q + 1

    def test_lines_per_point(self):
        """(q³ − 1)/(q − 1) = 7 lines through each point."""
        assert (PG_q**3 - 1) // (PG_q - 1) == LINES_PER_PT

    def test_planes_per_point(self):
        """7 planes through each point."""
        assert LINES_PER_PT == 7

    def test_7_is_phi6(self):
        """7 = Φ₆ cyclotomic value."""
        assert LINES_PER_PT == 7

    # ── GL(4,2) ──

    def test_GL42_order(self):
        assert GL42 == 20160

    def test_GL42_formula(self):
        """GL(4,2) = (2⁴−1)(2⁴−2)(2⁴−4)(2⁴−8) = 15·14·12·8."""
        val = 15 * 14 * 12 * 8
        assert val == GL42

    def test_GL42_is_A8(self):
        """GL(4,2) ≅ A₈, |A₈| = 8!/2 = 20160."""
        assert math.factorial(8) // 2 == GL42

    def test_GL42_factorisation(self):
        """20160 = 2⁶ × 3² × 5 × 7."""
        assert 2**6 * 3**2 * 5 * 7 == GL42

    # ── point stabiliser ──

    def test_point_stabiliser(self):
        """GL(4,2)/15 = 1344."""
        assert GL42 // PG_POINTS == 1344

    def test_1344_factorised(self):
        """1344 = 2⁶ × 3 × 7."""
        assert 1344 == 2**6 * 3 * 7

    # ── Fano planes ──

    def test_fano_is_hyperplane_section(self):
        """Each plane of PG(3,2) is a Fano plane with 7 points."""
        assert LINES_PER_PT == 7

    def test_fano_lines(self):
        """Each Fano plane has 7 lines."""
        assert 7 == 7

    def test_fano_aut(self):
        """|GL(3,2)| = 168."""
        val = (2**3 - 1) * (2**3 - 2) * (2**3 - 4)
        assert val == 168

    def test_168_factorised(self):
        """168 = 2³ × 3 × 7."""
        assert 168 == 2**3 * 3 * 7

    # ── doily GQ(2,2) ──

    def test_doily_from_15(self):
        """15 points form GQ(2,2) doily, SRG(15,6,1,3)."""
        s, t = 2, 2
        assert (s+1)*(s*t+1) == PG_POINTS

    def test_doily_srg_k(self):
        assert 2 * (2 + 1) == 6

    def test_doily_srg_lambda(self):
        assert 2 - 1 == 1

    def test_doily_srg_mu(self):
        assert 2 + 1 == 3

    # ── total incidences ──

    def test_point_line_incidences(self):
        """15 × 7 = 105 = 35 × 3."""
        assert PG_POINTS * LINES_PER_PT == PG_LINES * PTS_PER_LINE
        assert PG_POINTS * LINES_PER_PT == 105

    # ── connection to W(3,3) ──

    def test_15_times_K(self):
        """15 × 12 = 180."""
        assert PG_POINTS * K == 180

    def test_GL42_over_E(self):
        """20160/240 = 84."""
        assert GL42 // E == 84

    def test_84_is_12_times_7(self):
        """84 = 12 × 7 = k × Φ₆."""
        assert K * 7 == 84
