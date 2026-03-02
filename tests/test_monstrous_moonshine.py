"""
Tests for Pillar 126 - Monstrous Moonshine: McKay's E8 Observation
"""
import pytest
import numpy as np
from math import comb

from THEORY_PART_CCXXVI_MONSTROUS_MOONSHINE import (
    e8_cartan_matrix, affine_e8_cartan_matrix, affine_e8_null_vector,
    sigma_k, eisenstein_e4, eisenstein_e6, delta_coefficients,
    j_invariant_coefficients, mckay_thompson_2A, mckay_thompson_3A,
    monster_irrep_dimensions, monster_order, coxeter_numbers,
    genus_zero_N_values, multiply_series, cube_series,
)


# ── Affine E8 ────────────────────────────────────────────────

class TestAffineE8:
    def test_cartan_shape(self):
        C = affine_e8_cartan_matrix()
        assert C.shape == (9, 9)

    def test_cartan_rank(self):
        C = affine_e8_cartan_matrix()
        assert np.linalg.matrix_rank(C.astype(float)) == 8

    def test_cartan_symmetric(self):
        C = affine_e8_cartan_matrix()
        assert np.array_equal(C, C.T)

    def test_null_vector(self):
        C = affine_e8_cartan_matrix()
        marks = affine_e8_null_vector()
        assert np.all(C @ marks == 0)

    def test_marks_values(self):
        marks = affine_e8_null_vector()
        assert list(marks) == [1, 2, 3, 4, 5, 6, 4, 2, 3]

    def test_marks_sum_30(self):
        marks = affine_e8_null_vector()
        assert sum(marks) == 30

    def test_nine_nodes(self):
        """9 nodes = 9 Monster involution classes (McKay observation)."""
        C = affine_e8_cartan_matrix()
        assert C.shape[0] == 9


# ── j-invariant ──────────────────────────────────────────────

class TestJInvariant:
    def test_c_minus1(self):
        j = j_invariant_coefficients(6)
        assert int(round(j[0])) == 1

    def test_c_0(self):
        j = j_invariant_coefficients(6)
        assert int(round(j[1])) == 744

    def test_c_1(self):
        j = j_invariant_coefficients(6)
        assert int(round(j[2])) == 196884

    def test_c_2(self):
        j = j_invariant_coefficients(6)
        assert int(round(j[3])) == 21493760

    def test_c_3(self):
        j = j_invariant_coefficients(6)
        assert int(round(j[4])) == 864299970

    def test_744_eq_3_times_248(self):
        assert 744 == 3 * 248


# ── Monster Irrep Decomposition ──────────────────────────────

class TestMonsterDecomp:
    def test_c1_decomp(self):
        dims = monster_irrep_dimensions()
        assert 196884 == dims[0] + dims[1]

    def test_c2_decomp(self):
        dims = monster_irrep_dimensions()
        assert 21493760 == dims[0] + dims[1] + dims[2]

    def test_c3_decomp(self):
        dims = monster_irrep_dimensions()
        assert 864299970 == 2 * dims[0] + 2 * dims[1] + dims[2] + dims[3]

    def test_trivial_irrep(self):
        dims = monster_irrep_dimensions()
        assert dims[0] == 1

    def test_smallest_nontrivial(self):
        dims = monster_irrep_dimensions()
        assert dims[1] == 196883


# ── McKay-Thompson Series ────────────────────────────────────

class TestMcKayThompson:
    def test_2A_leading(self):
        t2a = mckay_thompson_2A()
        assert t2a[0] == 1  # q^{-1}

    def test_2A_constant(self):
        t2a = mckay_thompson_2A()
        assert t2a[1] == 0

    def test_2A_c1(self):
        t2a = mckay_thompson_2A()
        assert t2a[2] == 4372

    def test_4372_decomp(self):
        assert 4372 == 2**12 + comb(24, 2)

    def test_3A_c1(self):
        t3a = mckay_thompson_3A()
        assert t3a[2] == 783

    def test_783_factorization(self):
        assert 783 == 27 * 29


# ── Coxeter Numbers ──────────────────────────────────────────

class TestCoxeter:
    def test_E6(self):
        assert coxeter_numbers()['E6'] == 12

    def test_E7(self):
        assert coxeter_numbers()['E7'] == 18

    def test_E8(self):
        assert coxeter_numbers()['E8'] == 30

    def test_sum_60(self):
        cn = coxeter_numbers()
        assert cn['E6'] + cn['E7'] + cn['E8'] == 60

    def test_difference(self):
        cn = coxeter_numbers()
        assert cn['E8'] - cn['E6'] == cn['E7']


# ── Genus Zero ───────────────────────────────────────────────

class TestGenusZero:
    def test_count_15(self):
        assert len(genus_zero_N_values()) == 15

    def test_contains_small(self):
        gz = genus_zero_N_values()
        for n in [1, 2, 3, 4, 5]:
            assert n in gz

    def test_max_25(self):
        assert max(genus_zero_N_values()) == 25


# ── W(3,3) Connection ────────────────────────────────────────

class TestW33:
    def test_moonshine_eq(self):
        assert 196884 == 196560 + 4 * 81

    def test_irrep_eq(self):
        assert 196884 == 1 + 196883

    def test_81_points(self):
        assert 81 == 3**4

    def test_monster_order_length(self):
        """Monster order has ~54 digits."""
        m = monster_order()
        assert len(str(m)) >= 50
