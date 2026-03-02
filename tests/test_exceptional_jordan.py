"""
Tests for Pillar 128 - The Exceptional Jordan Algebra J_3(O) and E_6
"""
import pytest
import numpy as np
from math import comb

from THEORY_PART_CCXXVIII_EXCEPTIONAL_JORDAN import (
    jordan_algebra_dim, division_algebra_dims, all_jordan_dims,
    freudenthal_magic_square, exceptional_lie_dims,
    f4_from_jordan, e6_from_jordan, e7_from_jordan, e8_from_jordan,
    cubic_surface_27_lines, verify_jordan_identity_3x3,
    jordan_eigenvalues_3x3, exceptional_chain, w33_connections,
)


# ── Jordan Algebra Dimensions ────────────────────────────────

class TestJordanDims:
    def test_J3O_27(self):
        assert jordan_algebra_dim(3, 8) == 27

    def test_J3H_15(self):
        assert jordan_algebra_dim(3, 4) == 15

    def test_J3C_9(self):
        assert jordan_algebra_dim(3, 2) == 9

    def test_J3R_6(self):
        assert jordan_algebra_dim(3, 1) == 6

    def test_J2O_10(self):
        assert jordan_algebra_dim(2, 8) == 10

    def test_J1_always_1(self):
        for d in [1, 2, 4, 8]:
            assert jordan_algebra_dim(1, d) == 1

    def test_division_algebras(self):
        d = division_algebra_dims()
        assert d == {'R': 1, 'C': 2, 'H': 4, 'O': 8}


# ── Freudenthal Magic Square ─────────────────────────────────

class TestMagicSquare:
    def test_OO_E8(self):
        sq = freudenthal_magic_square()
        assert sq[('O', 'O')][1] == 248

    def test_OC_E6(self):
        sq = freudenthal_magic_square()
        assert sq[('O', 'C')][1] == 78

    def test_OH_E7(self):
        sq = freudenthal_magic_square()
        assert sq[('O', 'H')][1] == 133

    def test_OR_F4(self):
        sq = freudenthal_magic_square()
        assert sq[('O', 'R')][1] == 52

    def test_symmetric(self):
        sq = freudenthal_magic_square()
        for K1 in ['R', 'C', 'H', 'O']:
            for K2 in ['R', 'C', 'H', 'O']:
                assert sq[(K1, K2)][1] == sq[(K2, K1)][1]

    def test_RR_su2(self):
        sq = freudenthal_magic_square()
        assert sq[('R', 'R')][1] == 3


# ── Exceptional Groups ──────────────────────────────────────

class TestExceptionalGroups:
    def test_F4_52(self):
        f4 = f4_from_jordan()
        assert f4['dim'] == 52
        assert f4['total'] == 27

    def test_E6_78(self):
        e6 = e6_from_jordan()
        assert e6['dim'] == 78
        assert e6['fundamental_rep'] == 27
        assert e6['check_78'] == 78

    def test_E7_133(self):
        e7 = e7_from_jordan()
        assert e7['dim'] == 133
        assert e7['check_133'] == 133
        assert e7['fundamental_56'] == 56

    def test_E8_248(self):
        e8 = e8_from_jordan()
        assert e8['dim'] == 248
        assert e8['check_248'] == 248

    def test_exceptional_dims(self):
        d = exceptional_lie_dims()
        assert d == {'G2': 14, 'F4': 52, 'E6': 78, 'E7': 133, 'E8': 248}

    def test_exceptional_sum(self):
        d = exceptional_lie_dims()
        assert sum(d.values()) == 525


# ── Cubic Surface ────────────────────────────────────────────

class TestCubicSurface:
    def test_27_lines(self):
        cs = cubic_surface_27_lines()
        assert cs['num_lines'] == 27

    def test_matches_J3O(self):
        cs = cubic_surface_27_lines()
        assert cs['dim_J3O'] == 27

    def test_WE6_order(self):
        cs = cubic_surface_27_lines()
        assert cs['order_WE6'] == 51840

    def test_meeting_pairs(self):
        cs = cubic_surface_27_lines()
        assert cs['num_pairs_meeting'] == 216

    def test_total_pairs(self):
        cs = cubic_surface_27_lines()
        assert cs['num_pairs_meeting'] + cs['num_pairs_skew'] == comb(27, 2)


# ── Jordan Identity ──────────────────────────────────────────

class TestJordanIdentity:
    def test_identity_holds(self):
        ok, err = verify_jordan_identity_3x3()
        assert ok
        assert err < 1e-10

    def test_spectral(self):
        ok, n = jordan_eigenvalues_3x3()
        assert ok
        assert n == 3


# ── E8 Decomposition Chain ──────────────────────────────────

class TestChain:
    def test_chain_dims(self):
        chain, _ = exceptional_chain()
        assert chain == {'J_3(O)': 27, 'F4': 52, 'E6': 78, 'E7': 133, 'E8': 248}

    def test_78_eq_52_plus_26(self):
        assert 78 == 52 + 26

    def test_133_eq_78_27_27_1(self):
        assert 133 == 78 + 27 + 27 + 1

    def test_248_eq_133_112_3(self):
        assert 248 == 133 + 112 + 3


# ── W(3,3) Connections ──────────────────────────────────────

class TestW33:
    def test_all_connections(self):
        conns = w33_connections()
        for desc, val in conns.items():
            assert val, f"Failed: {desc}"

    def test_81_three_27s(self):
        assert 81 == 3 * 27

    def test_27_cubed(self):
        assert 27 == 3**3

    def test_240_roots(self):
        assert 240 == 248 - 8
