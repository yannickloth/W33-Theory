"""
Tests for Pillar 138 — The Modular Forms Bridge: From η^24 to Moonshine
"""
import pytest

from THEORY_PART_CCXXXVIII_MODULAR_FORMS_BRIDGE import (
    eisenstein_series, dimension_formula, modular_discriminant,
    ramanujan_tau, j_invariant_moonshine, hecke_operators,
    langlands_program, e4_theta_e8, key_numbers,
    modular_forms_in_physics, complete_chain_w33_to_modular,
)


# -- Eisenstein series ---------------------------------------------------

class TestEisenstein:
    def test_e4_240(self):
        es = eisenstein_series()
        assert es['series'][4]['first_coeffs'][1] == 240

    def test_e6_minus_504(self):
        es = eisenstein_series()
        assert es['series'][6]['first_coeffs'][1] == -504

    def test_e8_480(self):
        es = eisenstein_series()
        assert es['series'][8]['first_coeffs'][1] == 480

    def test_ring_generators(self):
        assert eisenstein_series()['ring_generators'] == ['E_4', 'E_6']

    def test_e4_e8_roots(self):
        assert eisenstein_series()['e4_240_is_e8_roots'] is True

    def test_e4_weight(self):
        assert eisenstein_series()['e4_weight'] == 4

    def test_e6_weight(self):
        assert eisenstein_series()['e6_weight'] == 6


# -- Dimension formula --------------------------------------------------

class TestDimFormula:
    def test_dim_0(self):
        assert dimension_formula()['dims'][0] == 1

    def test_dim_2(self):
        assert dimension_formula()['dims'][2] == 0

    def test_dim_4(self):
        assert dimension_formula()['dims'][4] == 1

    def test_dim_12(self):
        assert dimension_formula()['dim_12'] == 2

    def test_cusp_dim_12(self):
        assert dimension_formula()['cusp_dim_12'] == 1

    def test_first_cusp_weight(self):
        assert dimension_formula()['first_cusp_form_weight'] == 12

    def test_dim_24(self):
        assert dimension_formula()['dim_24'] == 3

    def test_dim_36(self):
        assert dimension_formula()['dim_36'] == 4


# -- Modular discriminant -----------------------------------------------

class TestDiscriminant:
    def test_eta_power_24(self):
        assert modular_discriminant()['eta_power'] == 24

    def test_weight_12(self):
        assert modular_discriminant()['weight'] == 12

    def test_is_cusp_form(self):
        assert modular_discriminant()['is_cusp_form'] is True

    def test_is_eigenform(self):
        assert modular_discriminant()['is_eigenform'] is True

    def test_significance_count(self):
        assert len(modular_discriminant()['twenty_four_significance']) >= 5


# -- Ramanujan tau -------------------------------------------------------

class TestRamanujanTau:
    def test_tau_1(self):
        assert ramanujan_tau()['values'][1] == 1

    def test_tau_2(self):
        assert ramanujan_tau()['tau_2'] == -24

    def test_tau_3(self):
        assert ramanujan_tau()['values'][3] == 252

    def test_multiplicativity(self):
        assert ramanujan_tau()['multiplicativity_check'] is True

    def test_recurrence(self):
        assert ramanujan_tau()['recurrence_check'] is True

    def test_deligne(self):
        t = ramanujan_tau()
        assert t['proved_by'] == 'Deligne' and t['proved_year'] == 1974


# -- j-invariant --------------------------------------------------------

class TestJInvariant:
    def test_c1(self):
        assert j_invariant_moonshine()['c1'] == 196884

    def test_c2(self):
        assert j_invariant_moonshine()['c2'] == 21493760

    def test_c1_decomposition(self):
        assert sum(j_invariant_moonshine()['c1_decomposition']) == 196884

    def test_c2_decomposition(self):
        assert sum(j_invariant_moonshine()['c2_decomposition']) == 21493760

    def test_hauptmodul(self):
        assert j_invariant_moonshine()['hauptmodul'] is True

    def test_borcherds(self):
        assert j_invariant_moonshine()['borcherds_proof_year'] == 1992


# -- Hecke operators ----------------------------------------------------

class TestHecke:
    def test_delta_eigenform(self):
        assert hecke_operators()['delta_is_eigenform'] is True

    def test_eigenvalue_tau(self):
        assert hecke_operators()['delta_eigenvalues'] == 'τ(n)'


# -- Langlands -----------------------------------------------------------

class TestLanglands:
    def test_modularity(self):
        assert langlands_program()['modularity_theorem'] is True

    def test_wiles_year(self):
        assert langlands_program()['wiles_year'] == 1995

    def test_fermat(self):
        assert langlands_program()['fermat_consequence'] is True

    def test_full_modularity(self):
        assert langlands_program()['full_modularity_year'] == 2001


# -- E_4 = theta E_8 ----------------------------------------------------

class TestE4Theta:
    def test_240(self):
        assert e4_theta_e8()['c1_is_240'] is True

    def test_roots(self):
        assert e4_theta_e8()['num_roots_e8'] == 240


# -- Key numbers ---------------------------------------------------------

class TestKeyNumbers:
    def test_744_equals_3_times_248(self):
        assert key_numbers()['744_equals_3_times_248'] is True


# -- Physics -------------------------------------------------------------

class TestPhysics:
    def test_count(self):
        assert modular_forms_in_physics()['count'] >= 6


# -- Chain ---------------------------------------------------------------

class TestChain:
    def test_length(self):
        assert len(complete_chain_w33_to_modular()) == 6

    def test_starts_w33(self):
        assert complete_chain_w33_to_modular()[0][0] == 'W(3,3)'
