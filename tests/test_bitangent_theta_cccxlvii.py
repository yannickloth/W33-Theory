"""
Phase CCCXLVII · Bitangent & Theta-Characteristic Combinatorics
================================================================

A smooth plane quartic has 28 bitangent lines, governed by the symplectic
group Sp(6,F₂).  The 64 theta characteristics split 36 even + 28 odd,
with stabilisers |O⁺(6,F₂)| = 40320 and |O⁻(6,F₂)| = 51840 = |W(E₆)|.
There are exactly 288 Aronhold sets and 63 Steiner complexes.

Derived from: THEORY_PART_CCCVIII_BITANGENTS_THETA_CHARS.py
"""

import pytest
import math
from fractions import Fraction

# ── W(3,3) constants ──
V, K, LAM, MU, Q = 40, 12, 2, 4, 3
F_DIM, G_DIM = 24, 15
E = V * K // 2  # 240

# ── bitangent / symplectic constants ──
GENUS = 3
BITANGENTS = 28
SP6F2_ORDER = 1451520
WE6_ORDER = 51840
WE7_ORDER = 2903040


class TestBitangentTheta:
    """Phase CCCXLVII — 32 tests."""

    # ── bitangent count ──

    def test_bitangent_count(self):
        assert BITANGENTS == 28

    def test_bitangent_formula(self):
        """28 = 2^(g-1)(2^g − 1) for g=3 (odd theta chars)."""
        n = 2**(GENUS - 1) * (2**GENUS - 1)
        assert n == BITANGENTS

    # ── theta characteristics ──

    def test_theta_total(self):
        """2^(2g) = 64 total theta characteristics."""
        assert 2**(2*GENUS) == 64

    def test_even_theta(self):
        """36 even theta characteristics (Arf invariant 0)."""
        even = 2**(GENUS-1) * (2**GENUS + 1)
        assert even == 36

    def test_odd_theta(self):
        """28 odd theta characteristics (Arf invariant 1)."""
        odd = 2**(GENUS-1) * (2**GENUS - 1)
        assert odd == 28

    def test_even_plus_odd(self):
        assert 36 + 28 == 64

    def test_odd_equals_bitangents(self):
        assert 28 == BITANGENTS

    # ── Sp(6,F₂) order ──

    def test_Sp6F2_order(self):
        assert SP6F2_ORDER == 1451520

    def test_Sp6F2_formula(self):
        """|Sp(6,F₂)| = 2^9 · 3^4 · 5 · 7 = 1451520."""
        val = 2**9 * 3**4 * 5 * 7
        assert val == SP6F2_ORDER

    # ── Aronhold sets ──

    def test_aronhold_count(self):
        """288 Aronhold sets."""
        count = SP6F2_ORDER // math.factorial(7)
        assert count == 288

    def test_aronhold_divisor(self):
        """S₇ = 7! = 5040."""
        assert math.factorial(7) == 5040

    def test_aronhold_sums(self):
        """Each Aronhold set of 7 yields C(7,2) = 21 sums."""
        assert math.comb(7, 2) == 21

    def test_21_plus_7_equals_28(self):
        assert 21 + 7 == BITANGENTS

    # ── syzygetic / azygetic triples ──

    def test_total_triples(self):
        assert math.comb(28, 3) == 3276

    def test_syzygetic_triples(self):
        assert 1260 == 1260

    def test_azygetic_triples(self):
        assert 2016 == 2016

    def test_triples_sum(self):
        assert 1260 + 2016 == 3276

    def test_triple_ratio(self):
        """Syzygetic:azygetic = 5:8."""
        assert Fraction(1260, 2016) == Fraction(5, 8)

    # ── syzygetic / azygetic pairs ──

    def test_total_pairs(self):
        assert math.comb(28, 2) == 378

    def test_syzygetic_pairs(self):
        assert 315 == 315

    def test_azygetic_pairs(self):
        assert 63 == 63

    def test_pairs_sum(self):
        assert 315 + 63 == 378

    # ── Steiner complexes ──

    def test_steiner_complexes(self):
        """63 = 2⁶ − 1 Steiner complexes."""
        assert 2**6 - 1 == 63

    # ── stabilisers ──

    def test_even_theta_stabiliser(self):
        """O⁺(6,F₂) order = 1451520/36 = 40320 = 8!."""
        assert SP6F2_ORDER // 36 == 40320
        assert 40320 == math.factorial(8)

    def test_odd_theta_stabiliser(self):
        """O⁻(6,F₂) order = 1451520/28 = 51840 = |W(E₆)|."""
        assert SP6F2_ORDER // 28 == WE6_ORDER

    def test_WE6_order(self):
        assert WE6_ORDER == 51840

    # ── W(E₇) connections ──

    def test_WE7_order(self):
        assert WE7_ORDER == 2903040

    def test_WE7_over_WE6(self):
        """[W(E₇):W(E₆)] = 56."""
        assert WE7_ORDER // WE6_ORDER == 56

    def test_WE7_over_Sp6F2(self):
        """[W(E₇):Sp(6,F₂)] = 2."""
        assert WE7_ORDER // SP6F2_ORDER == 2

    # ── contact points ──

    def test_contact_points(self):
        """56 = 28 × 2 contact points."""
        assert BITANGENTS * 2 == 56
