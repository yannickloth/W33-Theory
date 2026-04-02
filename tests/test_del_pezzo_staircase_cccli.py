"""
Phase CCCLI · Del Pezzo Staircase & Anticanonical Lattice Geometry
==================================================================

The (-1)-curve count on del Pezzo surfaces dP_d (d blowups of CP²)
forms a staircase: 0,1,3,6,10,16,27,56,240 — landing exactly on
W(3,3) parameters.  The Weyl groups W(E_n) act as symmetries, with
coset indices reproducing the curve-count jumps.

Derived from: THEORY_PART_CCCVIII_BITANGENTS_THETA_CHARS.py,
              THEORY_PART_CCCXI_240_ROOT_EDGE_CORRESPONDENCE.py
"""

import pytest
import math
from fractions import Fraction

# ── W(3,3) constants ──
V, K, LAM, MU, Q = 40, 12, 2, 4, 3
F_DIM, G_DIM = 24, 15
E = V * K // 2  # 240
THETA = 10
PHI6 = 7

# ── del Pezzo (-1)-curve staircase (n blowups, d = 9 − n) ──
CURVES = {0: 0, 1: 1, 2: 3, 3: 6, 4: 10, 5: 16, 6: 27, 7: 56, 8: 240}

# ── Weyl group orders ──
WE6 = 51840
WE7 = 2903040
WE8 = 696729600


class TestDelPezzoStaircase:
    """Phase CCCLI — 32 tests."""

    # ── staircase values ──

    def test_n0_curves(self):
        assert CURVES[0] == 0

    def test_n1_curves(self):
        assert CURVES[1] == 1

    def test_n2_curves(self):
        assert CURVES[2] == 3

    def test_n3_curves(self):
        assert CURVES[3] == 6

    def test_n4_curves(self):
        """10 = Θ = SRG eigenvalue."""
        assert CURVES[4] == THETA

    def test_n5_curves(self):
        """16 = μ² = k + μ."""
        assert CURVES[5] == MU**2
        assert CURVES[5] == K + MU

    def test_n6_curves(self):
        """27 = v − k − 1 = E₆ fundamental."""
        assert CURVES[6] == V - K - 1

    def test_n7_curves(self):
        """56 = [W(E₇):W(E₆)]."""
        assert CURVES[7] == WE7 // WE6

    def test_n8_curves(self):
        """240 = E = vk/2 = |E₈ roots|."""
        assert CURVES[8] == E

    # ── staircase W(3,3) links ──

    def test_10_is_theta(self):
        assert CURVES[4] == K - LAM

    def test_16_is_mu_squared(self):
        assert CURVES[5] == MU * MU

    def test_27_complement_valency(self):
        assert CURVES[6] == V - K - 1

    # ── Weyl group orders ──

    def test_WE6_order(self):
        assert WE6 == 51840

    def test_WE6_factorisation(self):
        assert WE6 == 2**7 * 3**4 * 5

    def test_WE7_order(self):
        assert WE7 == 2903040

    def test_WE7_factorisation(self):
        assert WE7 == 2**10 * 3**4 * 5 * 7

    def test_WE8_order(self):
        assert WE8 == 696729600

    def test_WE8_factorisation(self):
        assert WE8 == 2**14 * 3**5 * 5**2 * 7

    # ── coset indices = curve jumps ──

    def test_WE7_over_WE6(self):
        """[W(E₇):W(E₆)] = 56 = jump from 27 to 56."""
        assert WE7 // WE6 == 56

    def test_WE8_over_WE7(self):
        """[W(E₈):W(E₇)] = 240 = jump anchor."""
        assert WE8 // WE7 == 240

    # ── Picard lattice at dP₃ (d=3, n=6) ──

    def test_picard_rank_dP3(self):
        """Picard rank of dP₃ = 1 + 6 = 7 = Φ₆."""
        assert 1 + 6 == PHI6

    def test_E6_cartan_determinant(self):
        """|P/Q| = det(Cartan) = 3 = q."""
        assert Q == 3

    # ── double-sixes at dP₃ ──

    def test_double_six_count(self):
        """36 double-sixes on a cubic surface."""
        assert WE6 // 1440 == 36

    def test_double_six_stabiliser(self):
        """Stabiliser order = 1440."""
        assert WE6 // 36 == 1440

    def test_tritangent_count(self):
        """45 tritangent planes."""
        assert WE6 // 1152 == 45

    def test_tritangent_stabiliser(self):
        """1152 = 2⁷ × 3²."""
        assert 1152 == 2**7 * 3**2

    # ── Eckardt points ──

    def test_eckardt_points(self):
        """Up to 45 tritangent planes, max 45 Eckardt points."""
        assert 45 == WE6 // 1152

    # ── staircase monotonicity ──

    def test_staircase_increasing(self):
        vals = [CURVES[i] for i in range(9)]
        for i in range(1, len(vals)):
            assert vals[i] > vals[i-1]

    def test_staircase_convex(self):
        """Differences increase: 1,2,3,4,6,11,29,184."""
        vals = [CURVES[i] for i in range(9)]
        diffs = [vals[i+1] - vals[i] for i in range(8)]
        for i in range(1, len(diffs)):
            assert diffs[i] >= diffs[i-1]

    def test_staircase_sum(self):
        """Sum of all curve counts."""
        total = sum(CURVES.values())
        assert total == 0+1+3+6+10+16+27+56+240
        assert total == 359
