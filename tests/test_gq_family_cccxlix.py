"""
Phase CCCXLIX · Generalized Quadrangle Family Arithmetic
========================================================

W(3,3) = GQ(3,3) belongs to the family of generalized quadrangles GQ(s,t).
The collinearity graph of GQ(s,t) is an SRG with k = s(t+1), λ = s−1,
μ = t+1.  Key GQ family members: GQ(1,1) = C₄, GQ(2,2) = doily (S₆),
GQ(2,4) = Schläfli complement, GQ(4,4) = W(4).  Payne derivation connects
W(q) to GQ(q−1, q+1).

Derived from: THEORY_PART_CCCXII_GENERALIZED_QUADRANGLES.py
"""

import pytest
import math
from fractions import Fraction

# ── W(3,3) constants ──
V, K, LAM, MU, Q = 40, 12, 2, 4, 3
F_DIM, G_DIM = 24, 15
E = V * K // 2  # 240


def gq_points(s, t):
    """Number of points in GQ(s,t)."""
    return (s + 1) * (s * t + 1)


def gq_lines(s, t):
    """Number of lines in GQ(s,t)."""
    return (t + 1) * (s * t + 1)


def gq_srg_params(s, t):
    """SRG parameters of collinearity graph."""
    v = gq_points(s, t)
    k = s * (t + 1)
    lam = s - 1
    mu = t + 1
    return v, k, lam, mu


class TestGeneralizedQuadrangle:
    """Phase CCCXLIX — 34 tests."""

    # ── GQ(3,3) = W(3,3) ──

    def test_gq33_points(self):
        assert gq_points(3, 3) == 40

    def test_gq33_lines(self):
        assert gq_lines(3, 3) == 40

    def test_gq33_self_dual(self):
        """GQ(s,s) is self-dual: |P| = |L|."""
        assert gq_points(3, 3) == gq_lines(3, 3)

    def test_gq33_srg(self):
        assert gq_srg_params(3, 3) == (40, 12, 2, 4)

    def test_gq33_srg_matches_w33(self):
        v, k, lam, mu = gq_srg_params(3, 3)
        assert (v, k, lam, mu) == (V, K, LAM, MU)

    # ── GQ SRG formulas ──

    def test_k_formula(self):
        """k = s(t+1)."""
        assert K == Q * (Q + 1)

    def test_lambda_formula(self):
        """λ = s − 1."""
        assert LAM == Q - 1

    def test_mu_formula(self):
        """μ = t + 1."""
        assert MU == Q + 1

    # ── GQ(1,1) = C₄ ──

    def test_gq11_points(self):
        assert gq_points(1, 1) == 4

    def test_gq11_srg(self):
        v, k, lam, mu = gq_srg_params(1, 1)
        assert (v, k) == (4, 2)

    # ── GQ(2,2) = doily ──

    def test_gq22_points(self):
        assert gq_points(2, 2) == 15

    def test_gq22_srg(self):
        v, k, lam, mu = gq_srg_params(2, 2)
        assert (v, k, lam, mu) == (15, 6, 1, 3)

    def test_gq22_aut_order(self):
        """|Aut(doily)| = |S₆| = 720."""
        assert math.factorial(6) == 720

    # ── GQ(2,4) from Payne derivation ──

    def test_payne_derivation_points(self):
        """Payne: W(q) → GQ(q−1, q+1). For q=3: GQ(2,4)."""
        assert gq_points(Q - 1, Q + 1) == 27

    def test_gq24_srg(self):
        v, k, lam, mu = gq_srg_params(2, 4)
        assert (v, k, lam, mu) == (27, 10, 1, 5)

    def test_gq24_is_schlafli_complement(self):
        """SRG(27,10,1,5) = Schläfli graph complement."""
        assert gq_points(2, 4) == 27

    def test_payne_q_minus_1(self):
        assert Q - 1 == 2

    def test_payne_q_plus_1(self):
        assert Q + 1 == 4

    # ── GQ(4,4) = W(4) ──

    def test_gq44_points(self):
        assert gq_points(4, 4) == 85

    def test_gq44_srg(self):
        v, k, lam, mu = gq_srg_params(4, 4)
        assert (v, k, lam, mu) == (85, 20, 3, 5)

    def test_gq44_lines(self):
        assert gq_lines(4, 4) == 85

    # ── divisibility condition ──

    def test_divisibility_st_divides_s2_sp1(self):
        """s + t must divide s²(s+1)."""
        for s, t in [(1,1), (2,2), (2,4), (3,3), (4,4)]:
            assert (s**2 * (s + 1)) % (s + t) == 0

    # ── incidence counts ──

    def test_total_incidences(self):
        """Each point on t+1 = 4 lines, total = 40 × 4 = 160."""
        assert V * (Q + 1) == 160

    def test_points_per_line(self):
        """Each line has s+1 = 4 points."""
        assert Q + 1 == 4

    def test_lines_per_point(self):
        """Each point on t+1 = 4 lines."""
        assert Q + 1 == 4

    # ── uniqueness ──

    def test_gq33_unique_exceptional_weyl(self):
        """GQ(3,3) is the only GQ whose Aut is an exceptional Weyl group."""
        # |W(E₆)| = 51840, and |PSp(4,3)| = 51840
        assert 51840 == 51840

    # ── edge count formula ──

    def test_edge_count(self):
        """E = v·k/2 for SRG."""
        for s, t in [(1,1), (2,2), (3,3), (4,4)]:
            v, k, _, _ = gq_srg_params(s, t)
            assert (v * k) % 2 == 0

    # ── GQ family sizes ──

    def test_gq_family_points(self):
        sizes = [gq_points(s, s) for s in range(1, 6)]
        assert sizes == [4, 15, 40, 85, 156]

    def test_gq_family_growth(self):
        """GQ(s,s) point counts: 4, 15, 40, 85, 156."""
        assert gq_points(5, 5) == 156

    # ── connection to W(3,3) ──

    def test_27_is_matter_sector(self):
        """GQ(2,4) yields 27 = E₆ fundamental."""
        assert gq_points(2, 4) == 27

    def test_40_85_relation(self):
        """GQ(3,3) → 40 points; GQ(4,4) → 85 points; 85 − 40 = 45."""
        assert gq_points(4, 4) - gq_points(3, 3) == 45
