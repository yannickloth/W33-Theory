"""
Tests for Pillar 177 -- Random Matrix Theory & W(3,3) Spectral Statistics
"""
import pytest
import sys, os, math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'pillars'))
from THEORY_PART_CCLXXVII_RANDOM_MATRIX_THEORY import (
    gaussian_ensembles, wigner_semicircle,
    level_repulsion_and_spacing, tracy_widom_distribution,
    montgomery_dyson_connection, determinantal_processes,
    rmt_gauge_theory, w33_spectral_analysis,
    rmt_number_theory_physics
)


class TestGaussianEnsembles:
    def test_dyson_classification_exists(self):
        r = gaussian_ensembles()
        assert 'dyson_classification' in r

    def test_three_betas(self):
        r = gaussian_ensembles()
        d = r['dyson_classification']
        assert 'beta_1' in d and 'beta_2' in d and 'beta_4' in d

    def test_goe_in_beta1(self):
        r = gaussian_ensembles()
        assert 'GOE' in r['dyson_classification']['beta_1']

    def test_gue_in_beta2(self):
        r = gaussian_ensembles()
        assert 'GUE' in r['dyson_classification']['beta_2']

    def test_gse_in_beta4(self):
        r = gaussian_ensembles()
        assert 'GSE' in r['dyson_classification']['beta_4']

    def test_sp6f2_symmetry(self):
        r = gaussian_ensembles()
        assert 'Sp(6,F2)' in r['w33_connection']['symmetry_group']

    def test_w33_40_points(self):
        r = gaussian_ensembles()
        assert r['w33_connection']['w33_points'] == 40


class TestWignerSemicircle:
    def test_semicircle_density(self):
        r = wigner_semicircle()
        assert 'sqrt' in r['semicircle_law']['density']

    def test_catalan_moments(self):
        r = wigner_semicircle()
        assert r['moments']['second_moment'] == 1
        assert r['moments']['fourth_moment'] == 2
        assert r['moments']['sixth_moment'] == 5

    def test_w33_degree_12(self):
        r = wigner_semicircle()
        assert r['w33_spectrum']['degree'] == 12

    def test_largest_eigenvalue_equals_degree(self):
        r = wigner_semicircle()
        assert r['w33_spectrum']['largest_eigenvalue'] == 12


class TestLevelRepulsion:
    def test_repulsion_powers(self):
        r = level_repulsion_and_spacing()
        assert r['repulsion']['beta_1_power'] == 1
        assert r['repulsion']['beta_2_power'] == 2
        assert r['repulsion']['beta_4_power'] == 4

    def test_gse_for_w33(self):
        r = level_repulsion_and_spacing()
        assert r['repulsion']['w33_beta'] == 4

    def test_logarithmic_rigidity(self):
        r = level_repulsion_and_spacing()
        assert 'ln' in r['spectral_rigidity']['gue']


class TestTracyWidom:
    def test_tw2_mean(self):
        r = tracy_widom_distribution()
        assert abs(r['statistics']['tw2_mean'] - (-1.7711)) < 0.01

    def test_tw2_variance(self):
        r = tracy_widom_distribution()
        assert abs(r['statistics']['tw2_variance'] - 0.8132) < 0.01

    def test_painleve(self):
        r = tracy_widom_distribution()
        assert 'Painleve' in r['tw_distributions']['painleve_ii']


class TestMontgomeryDyson:
    def test_year_1973(self):
        r = montgomery_dyson_connection()
        assert '1973' in r['pair_correlation']['year']

    def test_gue_kernel(self):
        r = montgomery_dyson_connection()
        assert 'GUE' in r['pair_correlation']['gue_kernel']

    def test_keating_snaith(self):
        r = montgomery_dyson_connection()
        assert 'keating_snaith' in r


class TestDeterminantal:
    def test_sine_kernel(self):
        r = determinantal_processes()
        assert 'sin' in r['gue_kernel']['sine_kernel']

    def test_airy_kernel(self):
        r = determinantal_processes()
        assert 'Ai' in r['gue_kernel']['airy_kernel']

    def test_fredholm_det(self):
        r = determinantal_processes()
        assert 'det' in r['fredholm']['gap_probability']


class TestRMTGaugeTheory:
    def test_gross_witten(self):
        r = rmt_gauge_theory()
        assert 'Gross' in r['gauge_matrix_models']['gross_witten']

    def test_coulomb_gas(self):
        r = rmt_gauge_theory()
        assert 'Coulomb' in r['eigenvalue_dynamics']['coulomb_gas']

    def test_e8_connection(self):
        r = rmt_gauge_theory()
        assert 'E8' in r['w33_matrix_model']['e8_connection']


class TestW33Spectral:
    def test_eigenvalues_correct(self):
        r = w33_spectral_analysis()
        assert r['eigenvalues']['principal']['value'] == 12
        assert r['eigenvalues']['positive']['value'] == 2
        assert r['eigenvalues']['negative']['value'] == -4

    def test_multiplicities(self):
        r = w33_spectral_analysis()
        assert r['eigenvalues']['principal']['multiplicity'] == 1
        assert r['eigenvalues']['positive']['multiplicity'] == 24
        assert r['eigenvalues']['negative']['multiplicity'] == 15

    def test_total_is_40(self):
        r = w33_spectral_analysis()
        total = r['eigenvalues']['total_multiplicity']
        assert total == 40

    def test_trace_zero(self):
        r = w33_spectral_analysis()
        assert r['eigenvalues']['trace_check'] == 0

    def test_spectral_gap(self):
        r = w33_spectral_analysis()
        assert r['spectral_connections']['spectral_gap'] == 10

    def test_ramanujan(self):
        r = w33_spectral_analysis()
        assert r['ramanujan']['is_ramanujan'] is True


class TestRMTUnification:
    def test_five_areas(self):
        r = rmt_number_theory_physics()
        u = r['unification']
        assert len(u) >= 5

    def test_dimension_40(self):
        r = rmt_number_theory_physics()
        assert '40' in r['w33_numerology']['dimension_40']

    def test_beta_sum_7(self):
        r = rmt_number_theory_physics()
        assert '7' in r['dimensional_bridge']['beta_sum']


class TestSelfChecks:
    def test_all_pass(self):
        from THEORY_PART_CCLXXVII_RANDOM_MATRIX_THEORY import run_self_checks
        assert run_self_checks() is True
