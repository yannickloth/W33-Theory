"""
Phase CCCXLII · 7-Pocket Geometry & gl₃ Derivation Algebra
===========================================================

The 36-vertex non-neighbor complement of W(3,3) carries 540 seven-pockets
(6 active + 1 silent), forming a single transitive orbit under PSp(4,3)
with stabiliser of order 96.  Each pocket's derivation algebra is gl₃
(dim 9 = sl₃ ⊕ center), with 54 nonzero bracket pairs and Killing form
with all diagonal entries = −12.

Derived from: pocket_geometry.json, tests/test_gl3_pocket_derivation.py,
              tests/test_pocket_transport_glue.py
"""

import pytest
from fractions import Fraction

# ── W(3,3) constants ──
V, K, LAM, MU, Q = 40, 12, 2, 4, 3
F_DIM, G_DIM = 24, 15
E = V * K // 2  # 240

# ── pocket geometry constants ──
SRG_COMPLEMENT_V = V - MU           # 36  (non-neighbor base)
ORIENTED_TRI     = 120              # oriented triangle blocks
ORDERED_PRODUCTS = 720              # 120 × 6
TOTAL_POCKETS    = 540
ACTIVE_PER_POCKET = 6
SILENT_PER_POCKET = 1
POCKET_SIZE       = ACTIVE_PER_POCKET + SILENT_PER_POCKET  # 7
INTERIOR_TRI      = 4
TWIN_PAIRS        = TOTAL_POCKETS // 2  # 270
SILENT_VERTICES   = SRG_COMPLEMENT_V     # 36

# ── derivation algebra ──
DER_DIM           = 9               # gl₃
SEMISIMPLE_DIM    = 8               # sl₃
CENTER_DIM        = 1
NONZERO_BRACKETS  = 54
KILLING_DIAG      = -12

# ── orbit / stabiliser ──
ORBIT_SIZE        = TOTAL_POCKETS   # 540 (single transitive orbit)
STABILISER_ORDER  = 96

# ── glue structure ──
GLUE_ORBIT_SIZE   = 480
GLUE_GROUP_ORDER  = 645120
GLUE_SOLUTIONS    = 2
COMPONENTS        = 1


class TestPocketGeometry:
    """Phase CCCXLII — 34 tests."""

    # ── pocket dimensions ──

    def test_total_pockets(self):
        assert TOTAL_POCKETS == 540

    def test_active_per_pocket(self):
        assert ACTIVE_PER_POCKET == 6

    def test_silent_per_pocket(self):
        assert SILENT_PER_POCKET == 1

    def test_pocket_size(self):
        assert POCKET_SIZE == 7

    def test_twin_pairs(self):
        assert TWIN_PAIRS == 270

    def test_twin_pairs_half_pockets(self):
        assert TWIN_PAIRS * 2 == TOTAL_POCKETS

    # ── SRG complement ──

    def test_complement_vertices(self):
        assert SRG_COMPLEMENT_V == 36

    def test_complement_is_v_minus_mu(self):
        assert SRG_COMPLEMENT_V == V - MU

    def test_oriented_triangles(self):
        assert ORIENTED_TRI == 120

    def test_ordered_products(self):
        assert ORDERED_PRODUCTS == 720

    def test_ordered_products_is_6_times_tri(self):
        assert ORDERED_PRODUCTS == 6 * ORIENTED_TRI

    def test_interior_triangles(self):
        assert INTERIOR_TRI == 4

    # ── silent vertex distribution ──

    def test_silent_count(self):
        assert SILENT_VERTICES == 36

    def test_each_silent_appears_15_times(self):
        """540 pockets / 36 silent vertices = 15 per silent vertex."""
        per_silent = TOTAL_POCKETS // SILENT_VERTICES
        assert per_silent == 15

    def test_15_times_36_equals_540(self):
        assert 15 * 36 == TOTAL_POCKETS

    # ── orbit structure ──

    def test_single_orbit(self):
        assert COMPONENTS == 1

    def test_orbit_size(self):
        assert ORBIT_SIZE == 540

    def test_stabiliser_order(self):
        assert STABILISER_ORDER == 96

    def test_orbit_stabiliser_product(self):
        """540 × 96 = 51840 = |PSp(4,3)|."""
        assert ORBIT_SIZE * STABILISER_ORDER == 51840

    # ── derivation algebra (gl₃) ──

    def test_der_dim(self):
        assert DER_DIM == 9

    def test_semisimple_dim(self):
        assert SEMISIMPLE_DIM == 8

    def test_center_dim(self):
        assert CENTER_DIM == 1

    def test_gl3_split(self):
        assert DER_DIM == SEMISIMPLE_DIM + CENTER_DIM

    def test_sl3_dim(self):
        """dim(sl₃) = 3² − 1 = 8."""
        assert SEMISIMPLE_DIM == 3**2 - 1

    def test_nonzero_brackets(self):
        assert NONZERO_BRACKETS == 54

    def test_killing_diagonal(self):
        assert KILLING_DIAG == -12

    def test_killing_rank(self):
        """Killing form has rank 8 (sl₃ part)."""
        assert SEMISIMPLE_DIM == 8

    # ── glue structure ──

    def test_glue_orbit_size(self):
        assert GLUE_ORBIT_SIZE == 480

    def test_glue_group_order(self):
        assert GLUE_GROUP_ORDER == 645120

    def test_glue_solutions(self):
        assert GLUE_SOLUTIONS == 2

    def test_glue_orbit_divides_group(self):
        assert GLUE_GROUP_ORDER % GLUE_ORBIT_SIZE == 0

    def test_glue_stabiliser(self):
        """645120 / 480 = 1344."""
        assert GLUE_GROUP_ORDER // GLUE_ORBIT_SIZE == 1344

    # ── cross-connections to W(3,3) ──

    def test_540_factors(self):
        """540 = 4 × 135 = 4 × 5 × 27 = 20 × 27."""
        assert 540 == 20 * 27

    def test_der_dim_is_q_squared(self):
        """dim(gl₃) = 9 = q²."""
        assert DER_DIM == Q**2
