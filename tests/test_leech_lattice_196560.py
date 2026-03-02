"""Tests for Pillar 124 -- The Leech Lattice: 196560 Vectors and the Monster."""
import sys
import pathlib
import math
import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "pillars"))
from THEORY_PART_CCXXIV_LEECH_LATTICE_196560 import (
    leech_theta_coefficients, verify_leech_theta,
    moonshine_equation, leech_from_e8_construction,
    conway_groups, kissing_number_196560,
    dimensional_identities, golay_code_properties,
    e8_leech_monster_chain, complete_chain_verification,
    sigma_k, e4_coefficients, delta_coefficients,
)


class TestLeechTheta:
    def test_a0_is_1(self):
        theta = leech_theta_coefficients(3)
        assert theta[0] == 1

    def test_a1_is_0_no_roots(self):
        theta = leech_theta_coefficients(3)
        assert theta[1] == 0

    def test_a2_kissing_196560(self):
        theta = leech_theta_coefficients(3)
        assert theta[2] == 196560

    def test_a3(self):
        theta = leech_theta_coefficients(4)
        assert theta[3] == 16773120

    def test_a4(self):
        theta = leech_theta_coefficients(5)
        assert theta[4] == 398034000

    def test_all_known_coefficients(self):
        info = verify_leech_theta(6)
        assert info["all_correct"]


class TestMoonshine:
    def test_196884_eq_196560_plus_324(self):
        me = moonshine_equation()
        assert me["equation_holds"]

    def test_324_eq_4_times_81(self):
        me = moonshine_equation()
        assert me["324_equals_4_times_81"]

    def test_monster_irrep(self):
        me = moonshine_equation()
        assert me["196884_eq_1_plus_monster"]

    def test_81_is_3_to_4(self):
        me = moonshine_equation()
        assert me["81_is_3_to_4"]


class TestConstruction:
    def test_even_unimodular(self):
        lc = leech_from_e8_construction()
        assert lc["is_even"]
        assert lc["is_unimodular"]

    def test_min_norm(self):
        lc = leech_from_e8_construction()
        assert lc["min_norm_sq"] == 4

    def test_dimension_24(self):
        lc = leech_from_e8_construction()
        assert lc["dimension"] == 24

    def test_24_eq_3_times_8(self):
        lc = leech_from_e8_construction()
        assert lc["24_eq_3_times_8"]


class TestConway:
    def test_co0_order(self):
        cg = conway_groups()
        assert cg["Co0_order"] == 8_315_553_613_086_720_000

    def test_m24_order(self):
        cg = conway_groups()
        assert cg["M24_order"] == 244_823_040

    def test_w_e8(self):
        cg = conway_groups()
        assert cg["W_E8"] == 696_729_600


class TestKissingNumber:
    def test_factorization_48_times_4095(self):
        kn = kissing_number_196560()
        assert kn["eq_48_times_4095"]

    def test_factorization_2160_times_91(self):
        kn = kissing_number_196560()
        assert kn["eq_2160_times_91"]

    def test_2160_eq_theta_a2(self):
        kn = kissing_number_196560()
        assert kn["2160_eq_theta_e8_a2"]


class TestDimensions:
    def test_all_equal_24(self):
        di = dimensional_identities()
        assert di["all_equal_24"]

    def test_26_minus_2(self):
        di = dimensional_identities()
        assert di["critical_dim_26_minus_2_eq_24"]


class TestGolay:
    def test_759_weight_8(self):
        gc = golay_code_properties()
        assert gc["759_check"]

    def test_code_params(self):
        gc = golay_code_properties()
        assert gc["length"] == 24
        assert gc["dimension"] == 12
        assert gc["min_distance"] == 8

    def test_self_dual(self):
        gc = golay_code_properties()
        assert gc["is_self_dual"]


class TestChain:
    def test_order_increasing(self):
        chain = e8_leech_monster_chain()
        assert chain["group_order_chain_increasing"]

    def test_monster_54_digits(self):
        chain = e8_leech_monster_chain()
        assert chain["Monster_digits"] == 54

    def test_complete_chain(self):
        cc = complete_chain_verification()
        assert cc["chain_established"]
        assert cc["196884_eq_196560_plus_324"]
        assert cc["324_eq_4_times_81"]


class TestDeltaCoeffs:
    def test_delta_0(self):
        d = delta_coefficients(4)
        assert d[0] == 0

    def test_delta_1(self):
        d = delta_coefficients(4)
        assert d[1] == 1

    def test_delta_2(self):
        d = delta_coefficients(4)
        assert d[2] == -24
