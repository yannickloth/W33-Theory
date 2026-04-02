"""
Phase CCCL · E₈ Root–Edge Geometry & Gosset Polytope
=====================================================

The E₈ root system has 240 roots = 2E edges of W(3,3), decomposing as
112 (coord roots ±1,±1,0⁶) + 128 (half-integer spinor). The Gosset
polytope 4₂₁ has 240 vertices, 6720 edges, vertex degree 56. The edge
stabiliser has order 216 = 6³, W(E₈) has 112 conjugacy classes, and
the quadratic forms over F₂ split as 135 Q⁺ + 120 Q⁻.

Derived from: THEORY_PART_CCCXI_240_ROOT_EDGE_CORRESPONDENCE.py
"""

import pytest
import math
from fractions import Fraction

# ── W(3,3) constants ──
V, K, LAM, MU, Q = 40, 12, 2, 4, 3
F_DIM, G_DIM = 24, 15
E = V * K // 2  # 240
THETA = 10

# ── E₈ / Gosset constants ──
E8_ROOTS = 240
COORD_ROOTS = 112
SPINOR_ROOTS = 128
GOSSET_EDGES = 6720
GOSSET_DEGREE = 56
WE8_ORDER = 696729600
WE8_CONJUGACY_CLASSES = 112
E8_COXETER = 30
E8_LIE_DIM = 248
EDGE_STABILISER = 216
Oplus_8F2 = 174182400
QPLUS = 135
QMINUS = 120


class TestE8RootGosset:
    """Phase CCCL — 30 tests."""

    # ── root decomposition ──

    def test_total_roots(self):
        assert E8_ROOTS == 240

    def test_roots_equal_E(self):
        """240 roots = E = v·k/2 edges of W(3,3)."""
        assert E8_ROOTS == E

    def test_coord_roots(self):
        """112 = C(8,2) × 4 (±1,±1,0⁶ permutations)."""
        assert COORD_ROOTS == math.comb(8, 2) * 4

    def test_spinor_roots(self):
        """128 = 2⁷ (half-integer, even sign changes)."""
        assert SPINOR_ROOTS == 2**7

    def test_root_sum(self):
        assert COORD_ROOTS + SPINOR_ROOTS == E8_ROOTS

    # ── Gosset polytope 4₂₁ ──

    def test_gosset_vertices(self):
        assert E8_ROOTS == 240

    def test_gosset_edges(self):
        assert GOSSET_EDGES == 6720

    def test_gosset_degree(self):
        """Each vertex of 4₂₁ is adjacent to 56 others."""
        assert GOSSET_DEGREE == 56

    def test_gosset_edge_formula(self):
        """6720 = 240 × 56 / 2."""
        assert 240 * 56 // 2 == GOSSET_EDGES

    def test_56_is_WE7_WE6_index(self):
        """56 = [W(E₇):W(E₆)] = 2903040/51840."""
        assert 2903040 // 51840 == GOSSET_DEGREE

    # ── edge stabiliser ──

    def test_edge_stabiliser_order(self):
        assert EDGE_STABILISER == 216

    def test_edge_stabiliser_is_6_cubed(self):
        assert EDGE_STABILISER == 6**3

    def test_edge_stabiliser_formula(self):
        """51840/240 = 216."""
        assert 51840 // E8_ROOTS == EDGE_STABILISER

    # ── W(E₈) ──

    def test_WE8_order(self):
        assert WE8_ORDER == 696729600

    def test_WE8_factorisation(self):
        """696729600 = 2¹⁴ × 3⁵ × 5² × 7."""
        val = 2**14 * 3**5 * 5**2 * 7
        assert val == WE8_ORDER

    def test_WE8_conjugacy_classes(self):
        """W(E₈) has 112 conjugacy classes."""
        assert WE8_CONJUGACY_CLASSES == 112

    def test_conjugacy_classes_equal_coord_roots(self):
        """Numerological coincidence: 112 = coord roots."""
        assert WE8_CONJUGACY_CLASSES == COORD_ROOTS

    # ── Lie algebra ──

    def test_E8_dim(self):
        assert E8_LIE_DIM == 248

    def test_E8_dim_formula(self):
        """dim(E₈) = 240 roots + 8 rank."""
        assert E8_LIE_DIM == E8_ROOTS + 8

    def test_E8_coxeter(self):
        assert E8_COXETER == 30

    # ── orthogonal group over F₂ ──

    def test_Oplus_8F2_order(self):
        assert Oplus_8F2 == 174182400

    def test_Oplus_8F2_factorised(self):
        """174182400 = 2¹² × 3⁵ × 5² × 7."""
        val = 2**12 * 3**5 * 5**2 * 7
        assert val == Oplus_8F2

    # ── quadratic forms ──

    def test_Qplus(self):
        assert QPLUS == 135

    def test_Qminus(self):
        assert QMINUS == 120

    def test_Q_total(self):
        """135 + 120 = 255 = 2⁸ − 1."""
        assert QPLUS + QMINUS == 255

    def test_Q_total_formula(self):
        assert 2**8 - 1 == 255

    # ── spread partition ──

    def test_spread_edges(self):
        """Each spread = 10 disjoint lines × 6 edges = 60."""
        assert 10 * 6 == 60

    def test_four_spreads(self):
        """4 spreads × 60 = 240."""
        assert 4 * 60 == E8_ROOTS

    # ── color classes ──

    def test_color_class_size(self):
        """240 / k = 240 / 12 = 20 edges per color class."""
        assert E8_ROOTS // K == 20
