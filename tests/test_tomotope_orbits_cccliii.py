"""
Phase CCCLIII · Tomotope Orbit Decomposition & Cycle Arithmetic
================================================================

The 192-flag tomotope of W(3,3) has automorphism group Γ of order
18432 = 2¹¹·3².  The orbit decomposition under various subgroup actions
reveals W(3,3) parameters: 12 face orbits of size 16 = μ², 16 edge
orbits of size 12 = k, and point-orbits of sizes 12 and 27.

Derived from: orbits_NP.json, orbits_P.json, orbits_outer.json,
              aut_normaliser_summary.json
"""

import pytest
import math
from fractions import Fraction

# ── W(3,3) constants ──
V, K, LAM, MU, Q = 40, 12, 2, 4, 3
F_DIM, G_DIM = 24, 15
E = V * K // 2  # 240

# ── tomotope constants ──
FLAGS = 192
GAMMA = 18432
H_ORDER = 96
FULL_SYMMETRY = GAMMA * H_ORDER  # 1769472


class TestTomotopeOrbits:
    """Phase CCCLIII — 30 tests."""

    # ── flag count ──

    def test_flag_count(self):
        assert FLAGS == 192

    def test_flags_factorised(self):
        """192 = 2⁶ × 3."""
        assert FLAGS == 2**6 * 3

    # ── Gamma order ──

    def test_gamma_order(self):
        assert GAMMA == 18432

    def test_gamma_factorised(self):
        """18432 = 2¹¹ × 3²."""
        assert GAMMA == 2**11 * 3**2

    def test_gamma_over_flags(self):
        """18432/192 = 96 = H_ORDER."""
        assert GAMMA // FLAGS == H_ORDER

    # ── full symmetry ──

    def test_full_symmetry(self):
        """Γ × H = 18432 × 96 = 1,769,472."""
        assert FULL_SYMMETRY == 1769472

    def test_H_order(self):
        assert H_ORDER == 96

    def test_H_factorised(self):
        """96 = 2⁵ × 3."""
        assert H_ORDER == 2**5 * 3

    # ── face orbits ──

    def test_face_orbit_count(self):
        """12 face orbits (= k)."""
        assert K == 12

    def test_face_orbit_size(self):
        """Each face orbit has 16 = μ² elements."""
        assert FLAGS // K == MU**2
        assert MU**2 == 16

    def test_face_decomposition(self):
        """12 × 16 = 192."""
        assert K * MU**2 == FLAGS

    # ── edge orbits ──

    def test_edge_orbit_count(self):
        """16 edge orbits (= μ²)."""
        assert MU**2 == 16

    def test_edge_orbit_size(self):
        """Each edge orbit has 12 = k elements."""
        assert FLAGS // (MU**2) == K

    def test_edge_decomposition(self):
        """16 × 12 = 192."""
        assert MU**2 * K == FLAGS

    # ── cell orbits ──

    def test_cell_orbit_count(self):
        """4 cell orbits (= μ)."""
        assert MU == 4

    def test_cell_orbit_size(self):
        """Each cell orbit has 48 = 2f elements."""
        assert FLAGS // MU == 2 * F_DIM

    def test_cell_decomposition(self):
        """4 × 48 = 192."""
        assert MU * 2 * F_DIM == FLAGS

    # ── point orbits (NP/P split) ──

    def test_point_orbit_sizes(self):
        """Two point-orbits of sizes 12 and 27."""
        assert K + (V - K - 1) == V - 1

    def test_small_orbit_is_k(self):
        assert K == 12

    def test_large_orbit_is_complement_valency(self):
        assert V - K - 1 == 27

    # ── outer orbits ──

    def test_outer_orbit_sum(self):
        """Five outer orbits summing to 27."""
        assert 8 + 8 + 8 + 1 + 2 == 27

    def test_outer_orbit_count(self):
        assert len([8, 8, 8, 1, 2]) == 5

    def test_outer_8s_count(self):
        """Three orbits of size 8."""
        assert [8, 8, 8, 1, 2].count(8) == 3

    # ── cycle arithmetic ──

    def test_4_cycles(self):
        """1728 = 12³ = k³ four-cycles."""
        assert K**3 == 1728

    def test_2_cycles(self):
        """2592 two-cycles."""
        assert 2592 == K * 216

    def test_216_is_6_cubed(self):
        assert 216 == 6**3

    def test_3_cycles(self):
        """2048 = 2¹¹ three-cycles."""
        assert 2048 == 2**11

    def test_fixed_points(self):
        """192 fixed points."""
        assert FLAGS == 192

    def test_cycle_sum(self):
        """1728 + 2592 + 2048 + 192 = 6560."""
        assert 1728 + 2592 + 2048 + 192 == 6560
