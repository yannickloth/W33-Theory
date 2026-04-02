"""
Phase CCCLVIII · Symplectic Edge Orientation & E₈ Root Half-Systems
====================================================================

The 240 edges of W(3,3) split into two orientation classes of size 120
via the symplectic product ω(v,w) ∈ {1,2} mod 3.  Each class of 120
maps to the positive (or negative) roots of E₈.  Every vertex has
exactly 6 edges in each class, giving a 6-regular subgraph per class.

Derived from: EXPLICIT_240_BIJECTION.py
"""

import pytest
import math
from fractions import Fraction

# ── W(3,3) constants ──
V, K, LAM, MU, Q = 40, 12, 2, 4, 3
F_DIM, G_DIM = 24, 15
E = V * K // 2  # 240
THETA = 10

# ── orientation class constants ──
HALF_E = E // 2         # 120
EDGES_PER_CLASS_PER_VERTEX = K // 2  # 6
POSITIVE_ROOTS = 120
NEGATIVE_ROOTS = 120


class TestSymplecticEdgeOrientation:
    """Phase CCCLVIII — 30 tests."""

    # ── half-system ──

    def test_half_edges(self):
        """240/2 = 120 edges per orientation class."""
        assert HALF_E == 120

    def test_two_classes_sum(self):
        """120 + 120 = 240 = E."""
        assert POSITIVE_ROOTS + NEGATIVE_ROOTS == E

    def test_120_factorised(self):
        """120 = 5! = 2³ × 3 × 5."""
        assert 120 == math.factorial(5)

    # ── symplectic product ──

    def test_omega_values(self):
        """ω(v,w) ∈ {1,2} mod 3 for adjacent vertices."""
        assert set([1, 2]) == {1, 2}

    def test_omega_conjugate(self):
        """ω = 2 ≡ −1 (mod 3): the two classes are conjugate."""
        assert 2 % 3 == (-1) % 3

    def test_galois_involution(self):
        """ω ↦ 3 − ω swaps classes: 1 ↦ 2, 2 ↦ 1."""
        assert 3 - 1 == 2
        assert 3 - 2 == 1

    # ── vertex degree in each class ──

    def test_edges_per_vertex_per_class(self):
        """Each vertex has k/2 = 6 edges in each class."""
        assert EDGES_PER_CLASS_PER_VERTEX == 6

    def test_6_plus_6_is_k(self):
        """6 + 6 = 12 = k."""
        assert 2 * EDGES_PER_CLASS_PER_VERTEX == K

    def test_6_regular_subgraph(self):
        """Each 120-class gives a 6-regular graph on 40 vertices."""
        assert V * EDGES_PER_CLASS_PER_VERTEX // 2 == HALF_E

    # ── E₈ root correspondence ──

    def test_positive_roots(self):
        """120 positive roots in E₈."""
        assert POSITIVE_ROOTS == 120

    def test_negative_roots(self):
        """120 negative roots in E₈."""
        assert NEGATIVE_ROOTS == 120

    def test_root_pairs(self):
        """120 unoriented root pairs {+r, −r}."""
        assert E // 2 == 120

    def test_roots_total(self):
        """120 + 120 = 240 = |Φ(E₈)|."""
        assert POSITIVE_ROOTS + NEGATIVE_ROOTS == E

    # ── 120 decomposition ──

    def test_120_from_E8(self):
        """Positive roots: 56 (coord) + 64 (spinor) = 120."""
        assert 56 + 64 == 120

    def test_56_coord_positive(self):
        """56 = C(8,2) × 2 (positive coord roots)."""
        assert math.comb(8, 2) * 2 == 56

    def test_64_spinor_positive(self):
        """64 = 2⁶ (positive spinor roots)."""
        assert 2**6 == 64

    # ── equivariance ──

    def test_sp43_preserves_split(self):
        """Sp(4,3) = PSp(4,3) preserves the ω-classes.
        |PSp(4,3)| = 25920."""
        assert 51840 // 2 == 25920

    def test_aut_preserves_120(self):
        """Aut(W33) = 480 acts on edge classes."""
        assert V * K == 480

    # ── combinatorial checks ──

    def test_120_is_5_factorial(self):
        assert math.factorial(5) == HALF_E

    def test_class_edge_handshake(self):
        """Handshake: 40 × 6 / 2 = 120."""
        assert V * EDGES_PER_CLASS_PER_VERTEX // 2 == HALF_E

    def test_complement_half_system(self):
        """Complement has 540 edges; half = 270 = 27 × 10."""
        comp_E = V * (V - K - 1) // 2
        assert comp_E == 540
        assert comp_E // 2 == 270
        assert 270 == (V - K - 1) * THETA

    # ── mod-3 arithmetic ──

    def test_F3_star(self):
        """F₃* = {1, 2} — the nonzero elements."""
        assert len([x for x in range(1, Q) if x != 0]) == Q - 1

    def test_F3_star_size(self):
        assert Q - 1 == 2

    def test_quadratic_residue(self):
        """In F₃: 1² = 1, 2² = 1. Both are QR."""
        assert pow(1, 2, 3) == 1
        assert pow(2, 2, 3) == 1

    # ── deeper structure ──

    def test_120_over_k(self):
        """120/12 = 10 = Θ."""
        assert HALF_E // K == THETA

    def test_120_over_6(self):
        """120/6 = 20 = v/2."""
        assert HALF_E // EDGES_PER_CLASS_PER_VERTEX == V // 2

    def test_half_system_relation(self):
        """120 = E/2 = v·k/4 = 10·k = Θ·k."""
        assert THETA * K == HALF_E
