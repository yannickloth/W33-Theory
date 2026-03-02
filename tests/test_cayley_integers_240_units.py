"""Tests for Pillar 122 — Cayley Integers: The 240 Units = E₈ Roots."""
import sys
import pathlib
import math
import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "pillars"))
from THEORY_PART_CCXXII_CAYLEY_INTEGERS_240_UNITS import (
    hurwitz_units, verify_hurwitz_units, quaternion_multiply,
    hurwitz_units_closed_under_mult, d4_roots_from_hurwitz,
    cayley_integer_units, verify_cayley_units,
    q8_units, q8_in_hurwitz, hurwitz_in_cayley, unit_chain,
    e8_kissing_number, e8_root_inner_product_distribution,
    e8_even_unimodular, decomposition_112_128,
    cayley_dickson_dimensions, weyl_group_orders,
)


class TestHurwitzUnits:
    def test_count_24(self):
        assert len(hurwitz_units()) == 24

    def test_integer_type_8(self):
        info = verify_hurwitz_units(hurwitz_units())
        assert info["integer_type"] == 8

    def test_half_integer_type_16(self):
        info = verify_hurwitz_units(hurwitz_units())
        assert info["half_integer_type"] == 16

    def test_all_unit_norm(self):
        info = verify_hurwitz_units(hurwitz_units())
        assert info["all_unit_norm"]

    def test_closed_under_mult(self):
        assert hurwitz_units_closed_under_mult()


class TestQuaternionMultiply:
    def test_identity(self):
        e = (1.0, 0.0, 0.0, 0.0)
        i = (0.0, 1.0, 0.0, 0.0)
        assert quaternion_multiply(e, i) == i

    def test_i_squared(self):
        i = (0.0, 1.0, 0.0, 0.0)
        result = quaternion_multiply(i, i)
        assert abs(result[0] - (-1.0)) < 1e-10

    def test_ij_eq_k(self):
        i = (0.0, 1.0, 0.0, 0.0)
        j = (0.0, 0.0, 1.0, 0.0)
        k = (0.0, 0.0, 0.0, 1.0)
        result = quaternion_multiply(i, j)
        for a, b in zip(result, k):
            assert abs(a - b) < 1e-10


class TestD4Hurwitz:
    def test_both_24(self):
        info = d4_roots_from_hurwitz()
        assert info["both_24"]

    def test_d4_inner_products(self):
        info = d4_roots_from_hurwitz()
        assert set(info["d4_inner_products"]) == {-2, -1, 0, 1, 2}


class TestQ8Chain:
    def test_q8_count(self):
        assert len(q8_units()) == 8

    def test_q8_in_hurwitz(self):
        assert q8_in_hurwitz()

    def test_hurwitz_in_cayley(self):
        assert hurwitz_in_cayley()


class TestCayleyUnits:
    def test_count_240(self):
        assert len(cayley_integer_units()) == 240

    def test_integer_type_112(self):
        info = verify_cayley_units(cayley_integer_units())
        assert info["integer_type"] == 112

    def test_half_type_128(self):
        info = verify_cayley_units(cayley_integer_units())
        assert info["half_integer_type"] == 128

    def test_all_norm_2(self):
        info = verify_cayley_units(cayley_integer_units())
        assert info["all_norm_2"]

    def test_inner_products_integer(self):
        info = verify_cayley_units(cayley_integer_units())
        assert info["inner_products_integer"]

    def test_no_duplicates(self):
        units = cayley_integer_units()
        assert len(set(units)) == 240


class TestE8Properties:
    def test_kissing_number(self):
        """Each E8 root has exactly 56 nearest neighbors."""
        assert e8_kissing_number() == 56

    def test_ip_distribution(self):
        dist = e8_root_inner_product_distribution()
        assert dist[2.0] == 1
        assert dist[1.0] == 56
        assert dist[0.0] == 126
        assert dist[-1.0] == 56
        assert dist[-2.0] == 1

    def test_distribution_sums_to_240(self):
        dist = e8_root_inner_product_distribution()
        assert sum(dist.values()) == 240

    def test_even_unimodular(self):
        eu = e8_even_unimodular()
        assert eu["is_even"]
        assert eu["is_unimodular"]

    def test_cartan_det_1(self):
        eu = e8_even_unimodular()
        assert eu["cartan_det"] == 1


class TestDecomposition:
    def test_112_plus_128(self):
        dec = decomposition_112_128()
        assert dec["integer_is_112"]
        assert dec["half_is_128"]

    def test_d4_copies(self):
        dec = decomposition_112_128()
        assert dec["d4_first_copy"] == 24
        assert dec["d4_second_copy"] == 24


class TestUnitChain:
    def test_chain_counts(self):
        uc = unit_chain()
        assert uc["q8_count"] == 8
        assert uc["hurwitz_count"] == 24
        assert uc["cayley_count"] == 240

    def test_ratios(self):
        uc = unit_chain()
        assert uc["ratio_hurwitz_q8"] == 3
        assert uc["ratio_cayley_hurwitz"] == 10
        assert uc["ratio_cayley_q8"] == 30


class TestCayleyDickson:
    def test_dimensions_double(self):
        cd = cayley_dickson_dimensions()
        assert cd["dim_R"] == 1
        assert cd["dim_C"] == 2
        assert cd["dim_H"] == 4
        assert cd["dim_O"] == 8

    def test_unit_counts(self):
        cd = cayley_dickson_dimensions()
        assert cd["Z_units"] == 2
        assert cd["gaussian_units"] == 4
        assert cd["hurwitz_units"] == 24
        assert cd["cayley_units"] == 240


class TestWeylGroups:
    def test_orders(self):
        wg = weyl_group_orders()
        assert wg["W_D4"] == 192
        assert wg["W_E6"] == 51_840
        assert wg["W_E7"] == 2_903_040
        assert wg["W_E8"] == 696_729_600

    def test_transitive_action(self):
        wg = weyl_group_orders()
        assert wg["W_E8_div_240_eq_W_E7"]

    def test_10_factorial(self):
        wg = weyl_group_orders()
        assert wg["W_E8_div_W_D4"] == math.factorial(10)
