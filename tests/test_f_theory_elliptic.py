"""
Tests for Pillar 135 - F-theory, Elliptic Fibrations & 12D Framework
"""
import pytest

from THEORY_PART_CCXXXV_F_THEORY_ELLIPTIC import (
    f_theory_dimensions, string_dualities, sl2z_modular_group,
    kodaira_fiber_types, e8_singularity, euler_characteristic_constraint,
    del_pezzo_surfaces, dp6_27_lines, dp8_240_roots,
    f_theory_gut, three_generations_f_theory,
    f_theory_k3_heterotic, landscape_count,
    j_invariant_in_f_theory,
    complete_chain_w33_to_f_theory,
)


# -- F-theory dimensions -------------------------------------------

class TestDimensions:
    def test_12_dimensions(self):
        assert f_theory_dimensions()['total_dimensions'] == 12

    def test_signature_10_2(self):
        assert f_theory_dimensions()['spacetime_signature'] == (10, 2)

    def test_compactification_2(self):
        assert f_theory_dimensions()['compactification_dimension'] == 2

    def test_remaining_4d(self):
        assert f_theory_dimensions()['remaining_spacetime'] == 4

    def test_cy4_complex_dim(self):
        assert f_theory_dimensions()['cy4_complex_dim'] == 4


# -- SL(2,Z) -------------------------------------------------------

class TestSL2Z:
    def test_s_squared_neg_i(self):
        assert sl2z_modular_group()['S_squared_is_neg_I'] is True

    def test_st_cubed_neg_i(self):
        assert sl2z_modular_group()['ST_cubed_is_neg_I'] is True

    def test_three_roles(self):
        assert len(sl2z_modular_group()['roles']) == 3

    def test_j_connection(self):
        assert sl2z_modular_group()['connection_to_j'] is True


# -- Kodaira fibers -------------------------------------------------

class TestKodairaFibers:
    def test_11_types(self):
        assert len(kodaira_fiber_types()) == 11

    def test_e8_is_II_star(self):
        e8 = e8_singularity()
        assert e8['kodaira_type'] == 'II*'

    def test_e8_ord_delta_10(self):
        assert e8_singularity()['ord_delta'] == 10

    def test_e8_is_maximal(self):
        assert e8_singularity()['is_maximal'] is True

    def test_e8_240_roots(self):
        assert e8_singularity()['roots'] == 240


# -- Euler constraint -----------------------------------------------

class TestEulerConstraint:
    def test_all_sum_24(self):
        assert euler_characteristic_constraint()['all_sum_to_24'] is True

    def test_chi_k3_24(self):
        assert euler_characteristic_constraint()['chi_k3'] == 24

    def test_config_count(self):
        configs = euler_characteristic_constraint()['configurations']
        assert len(configs) >= 5


# -- Del Pezzo surfaces ---------------------------------------------

class TestDelPezzo:
    def test_9_surfaces(self):
        assert len(del_pezzo_surfaces()) == 9

    def test_k_squared_formula(self):
        for s in del_pezzo_surfaces():
            assert s['k_squared'] == 9 - s['n']

    def test_dp6_27_lines(self):
        assert dp6_27_lines()['lines'] == 27

    def test_dp6_is_cubic(self):
        assert dp6_27_lines()['is_cubic_surface'] is True

    def test_dp6_e6_symmetry(self):
        assert dp6_27_lines()['symmetry'] == 'E_6'

    def test_dp8_240_lines(self):
        assert dp8_240_roots()['lines'] == 240

    def test_dp8_e8_symmetry(self):
        assert dp8_240_roots()['symmetry'] == 'E_8'

    def test_dp8_roots_match(self):
        assert dp8_240_roots()['roots_match'] is True

    def test_dp8_weyl_order(self):
        assert dp8_240_roots()['weyl_order'] == 696729600


# -- F-theory GUTs -------------------------------------------------

class TestGUT:
    def test_3_generations(self):
        assert f_theory_gut()['generations'] == 3

    def test_gut_e8(self):
        assert f_theory_gut()['gut_group'] == 'E_8'

    def test_matches_w33(self):
        assert f_theory_gut()['matches_w33'] is True

    def test_matter_27(self):
        gen = three_generations_f_theory()
        assert gen['matter_dim_27'] == 27

    def test_f3_structure(self):
        gen = three_generations_f_theory()
        assert 'F_3' in gen['f3_structure']


# -- F-theory / Heterotic duality ----------------------------------

class TestDuality:
    def test_duality_exists(self):
        assert f_theory_k3_heterotic()['duality'] is True

    def test_chi_k3_24(self):
        assert f_theory_k3_heterotic()['chi_k3'] == 24

    def test_gauge_rank_24(self):
        assert f_theory_k3_heterotic()['gauge_rank'] == 24

    def test_24_singular_fibers(self):
        assert f_theory_k3_heterotic()['singular_fibers'] == 24

    def test_7_dualities(self):
        assert len(string_dualities()) == 7


# -- j-invariant in F-theory ---------------------------------------

class TestJInvariant:
    def test_moonshine_connection(self):
        assert j_invariant_in_f_theory()['moonshine_connection'] is True

    def test_e8_theta_connection(self):
        assert j_invariant_in_f_theory()['e8_theta_connection'] is True

    def test_196884_coefficient(self):
        coeffs = j_invariant_in_f_theory()['first_coefficients']
        assert coeffs[2] == 196884  # q^1 coefficient

    def test_controls_coupling(self):
        assert j_invariant_in_f_theory()['controls_coupling'] is True


# -- Landscape and chain -------------------------------------------

class TestLandscape:
    def test_vast_landscape(self):
        assert landscape_count()['is_vast'] is True

    def test_sm_consistent(self):
        assert landscape_count()['sm_consistent_log10'] == 15


class TestChain:
    def test_chain_length(self):
        assert len(complete_chain_w33_to_f_theory()) == 6

    def test_chain_starts_w33(self):
        chain = complete_chain_w33_to_f_theory()
        assert chain[0][0] == 'W(3,3)'

    def test_chain_ends_3gen(self):
        chain = complete_chain_w33_to_f_theory()
        assert '3 generations' in chain[-1][1]
