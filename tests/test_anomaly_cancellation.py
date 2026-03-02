"""
Tests for Pillar 129 - Anomaly Cancellation: Green-Schwarz and 496
"""
import pytest
from math import comb

from THEORY_PART_CCXXIX_ANOMALY_CANCELLATION import (
    anomaly_constraint, verify_so32_dim, verify_e8e8_dim,
    anomaly_polynomial_factorization, perfect_numbers, divisor_sum,
    triangular_number, check_dim_496, gravitational_anomaly_check,
    pontryagin_classes, d10_supergravity_content, w33_anomaly_connections,
    classical_group_dims,
)


# ── Dimension 496 ───────────────────────────────────────────

class TestDim496:
    def test_so32(self):
        d1, d2 = verify_so32_dim()
        assert d1 == 496 and d2 == 496

    def test_e8e8(self):
        assert verify_e8e8_dim() == 496

    def test_comb_32_2(self):
        assert comb(32, 2) == 496

    def test_only_so_and_e8(self):
        groups = check_dim_496()
        assert groups['SO'] == 32
        assert groups['E8xE8'] == True
        assert 'SU' not in groups

    def test_248_plus_248(self):
        assert 248 + 248 == 496

    def test_496_eq_2_times_248(self):
        assert 496 == 2 * 248


# ── Perfect Number ───────────────────────────────────────────

class TestPerfect:
    def test_496_perfect(self):
        assert divisor_sum(496) == 496

    def test_6_perfect(self):
        assert divisor_sum(6) == 6

    def test_28_perfect(self):
        assert divisor_sum(28) == 28

    def test_third_perfect(self):
        pn = perfect_numbers()
        assert pn[2][0] == 496

    def test_mersenne_31(self):
        assert 2**5 - 1 == 31
        assert all(31 % d != 0 for d in range(2, 6))

    def test_496_eq_16_times_31(self):
        assert 496 == 16 * 31 == 2**4 * 31


# ── Triangular Number ────────────────────────────────────────

class TestTriangular:
    def test_T31(self):
        assert triangular_number(31) == 496

    def test_T10(self):
        assert triangular_number(10) == 55


# ── Anomaly Polynomial ──────────────────────────────────────

class TestAnomaly:
    def test_factorization_coeff(self):
        apf = anomaly_polynomial_factorization()
        assert abs(apf['X4_F2_coeff'] + 1/30) < 1e-15

    def test_coxeter_30(self):
        apf = anomaly_polynomial_factorization()
        assert apf['coxeter_30'] == 30

    def test_constraint_496(self):
        ac = anomaly_constraint()
        assert ac['required_gauge_dim'] == 496

    def test_gravitational(self):
        grav = gravitational_anomaly_check()
        assert grav['solution'] == 496


# ── Pontryagin / A-hat ──────────────────────────────────────

class TestCharClasses:
    def test_a_hat_coeff(self):
        pc = pontryagin_classes()
        assert abs(pc['a_hat_p1_coeff'] + 1/24) < 1e-15

    def test_d10(self):
        content = d10_supergravity_content()
        assert content['spacetime_dim'] == 10
        assert content['n_gauge'] == 496


# ── Divisor Structure ────────────────────────────────────────

class TestDivisors:
    def test_nine_divisors(self):
        divs = [d for d in range(1, 496) if 496 % d == 0]
        assert len(divs) == 9

    def test_248_is_divisor(self):
        assert 496 % 248 == 0

    def test_binary_rep(self):
        assert bin(496) == '0b111110000'


# ── Rank 16 ──────────────────────────────────────────────────

class TestRank:
    def test_rank_so32(self):
        assert 32 // 2 == 16

    def test_rank_e8e8(self):
        assert 8 + 8 == 16

    def test_compactification(self):
        assert 26 - 10 == 16


# ── W(3,3) Connections ──────────────────────────────────────

class TestW33:
    def test_all_connections(self):
        conns = w33_anomaly_connections()
        for desc, val in conns.items():
            assert val, f"Failed: {desc}"

    def test_496_decomp(self):
        assert 496 == 2 * 240 + 16

    def test_240_edges(self):
        assert 240 == 10 * 24
