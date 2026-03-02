"""Tests for Pillar 123 -- E8 Theta Series: Modular Forms from the Lattice."""
import sys
import pathlib
import math
import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "pillars"))
from THEORY_PART_CCXXIII_E8_THETA_SERIES import (
    theta_coefficient_direct, sigma_k, theta_series_first_terms,
    eisenstein_e4_coefficients, eisenstein_e6_coefficients,
    verify_theta_equals_e4,
    j_invariant_coefficients, compute_delta_coefficients,
    verify_j_coefficients, ramanujan_tau_values, verify_ramanujan_tau,
    moonshine_decompositions, e8_times_e8, w33_e8_connection,
    the_number_240,
)


class TestThetaSeries:
    def test_a0_is_1(self):
        assert theta_coefficient_direct(0) == 1

    def test_a1_is_240(self):
        assert theta_coefficient_direct(1) == 240

    def test_a2_is_2160(self):
        assert theta_coefficient_direct(2) == 2160

    def test_a3_is_6720(self):
        assert theta_coefficient_direct(3) == 6720

    def test_a3_div_240_is_28(self):
        assert theta_coefficient_direct(3) // 240 == 28

    def test_first_terms_length(self):
        terms = theta_series_first_terms(10)
        assert len(terms) == 10


class TestSigmaK:
    def test_sigma3_1(self):
        assert sigma_k(1, 3) == 1

    def test_sigma3_2(self):
        assert sigma_k(2, 3) == 9

    def test_sigma3_3(self):
        assert sigma_k(3, 3) == 28

    def test_sigma3_formula(self):
        for n in range(1, 6):
            assert theta_coefficient_direct(n) == 240 * sigma_k(n, 3)


class TestEisenstein:
    def test_theta_equals_e4(self):
        assert verify_theta_equals_e4(10)

    def test_e4_first_coeff(self):
        e4 = eisenstein_e4_coefficients(3)
        assert e4[0] == 1
        assert e4[1] == 240

    def test_e6_first_coeff(self):
        e6 = eisenstein_e6_coefficients(3)
        assert e6[0] == 1
        assert e6[1] == -504


class TestDelta:
    def test_delta_0_is_0(self):
        delta = compute_delta_coefficients(5)
        assert delta[0] == 0

    def test_delta_1_is_1(self):
        delta = compute_delta_coefficients(5)
        assert delta[1] == 1

    def test_delta_2_is_minus_24(self):
        delta = compute_delta_coefficients(5)
        assert delta[2] == -24


class TestRamanujanTau:
    def test_known_values(self):
        info = verify_ramanujan_tau()
        assert info["all_correct"]

    def test_tau_1(self):
        tau = ramanujan_tau_values(3)
        assert tau[0] == 1

    def test_tau_2(self):
        tau = ramanujan_tau_values(3)
        assert tau[1] == -24

    def test_tau_3(self):
        tau = ramanujan_tau_values(3)
        assert tau[2] == 252


class TestJInvariant:
    def test_j_leading(self):
        info = verify_j_coefficients()
        assert info["j_minus1"] == 1

    def test_j_constant_744(self):
        info = verify_j_coefficients()
        assert info["j_0"] == 744

    def test_j_1_is_196884(self):
        info = verify_j_coefficients()
        assert info["j_1"] == 196884

    def test_j_2_is_21493760(self):
        info = verify_j_coefficients()
        assert info["j_2"] == 21493760


class TestMoonshine:
    def test_744_decomp(self):
        md = moonshine_decompositions()
        assert md["744_eq_720_plus_24"]

    def test_720_is_6_factorial(self):
        assert math.factorial(6) == 720

    def test_196884_decomp(self):
        md = moonshine_decompositions()
        assert md["196884_eq_196560_plus_324"]

    def test_324_is_4_times_81(self):
        md = moonshine_decompositions()
        assert md["324_eq_4_times_81"]

    def test_monster_irrep(self):
        md = moonshine_decompositions()
        assert md["196884_eq_1_plus_monster"]


class TestE8TimesE8:
    def test_e4_squared_equals_e8(self):
        info = e8_times_e8()
        assert info["E4_sq_eq_E8"]


class TestThe240:
    def test_240_factorization(self):
        info = the_number_240()
        assert info["e8_roots"] == 240
        assert info["112_plus_128"] == 240

    def test_28_is_C82(self):
        info = the_number_240()
        assert info["28_equals_C82"] == 28


class TestW33Connection:
    def test_connections(self):
        conn = w33_e8_connection()
        assert conn["a1_eq_240"]
        assert conn["a2_eq_2160"]
        assert conn["a3_eq_6720"]
        assert conn["324_eq_4_times_81"]
