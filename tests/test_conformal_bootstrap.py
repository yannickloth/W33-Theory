"""
Tests for Pillar 181 -- Conformal Bootstrap from W(3,3)
"""
import pytest
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'pillars'))
from THEORY_PART_CCLXXXI_CONFORMAL_BOOTSTRAP import (
    bootstrap_axioms, conformal_blocks,
    ising_bootstrap, bootstrap_higher_symmetry,
    holographic_bootstrap, analytic_bootstrap
)


class TestBootstrapAxioms:
    def test_conformal_group(self):
        r = bootstrap_axioms()
        assert 'SO' in r['conformal_group']['euclidean']

    def test_ope_definition(self):
        r = bootstrap_axioms()
        assert 'O_i' in r['ope']['definition'] or 'operator' in r['ope']['definition'].lower()

    def test_crossing_equation(self):
        r = bootstrap_axioms()
        assert 'C_' in r['crossing']['equation'] or 'sum' in r['crossing']['equation']

    def test_sdpb(self):
        r = bootstrap_axioms()
        assert 'SDPB' in r['crossing']['numerical'] or 'semidefinite' in r['crossing']['numerical']

    def test_conformal_blocks_in_crossing(self):
        r = bootstrap_axioms()
        assert 'conformal_blocks' in r['crossing']


class TestConformalBlocks:
    def test_zamolodchikov(self):
        r = conformal_blocks()
        assert 'Zamolodchikov' in r['blocks']['recursion']

    def test_cross_ratios(self):
        r = conformal_blocks()
        assert 'u' in r['blocks']['cross_ratios'] and 'v' in r['blocks']['cross_ratios']

    def test_unitarity_scalar(self):
        r = conformal_blocks()
        assert '(d-2)/2' in r['unitarity_bounds']['scalar']

    def test_stress_tensor(self):
        r = conformal_blocks()
        assert 'Delta = d' in r['unitarity_bounds']['stress_tensor']

    def test_central_charges(self):
        r = conformal_blocks()
        assert 'c_t' in r['central_charges'] or 'C_T' in str(r['central_charges'])


class TestIsingBootstrap:
    def test_delta_sigma(self):
        r = ising_bootstrap()
        assert abs(r['critical_exponents']['delta_sigma'] - 0.5181489) < 0.001

    def test_delta_epsilon(self):
        r = ising_bootstrap()
        assert abs(r['critical_exponents']['delta_epsilon'] - 1.412625) < 0.001

    def test_eta(self):
        r = ising_bootstrap()
        assert abs(r['critical_exponents']['eta'] - 0.036) < 0.01

    def test_precision(self):
        r = ising_bootstrap()
        assert 'digit' in r['critical_exponents']['precision']

    def test_methodology_year(self):
        r = ising_bootstrap()
        assert '2012' in r['methodology']['year']

    def test_sdpb_solver(self):
        r = ising_bootstrap()
        assert 'SDPB' in r['methodology']['sdpb']

    def test_z2_from_w33(self):
        r = ising_bootstrap()
        assert 'Z2' in r['w33_ising']['z2_from_w33']


class TestHigherSymmetry:
    def test_n4_sym(self):
        r = bootstrap_higher_symmetry()
        assert 'N=4' in r['superconformal']['n4_4d']

    def test_chiral_algebra(self):
        r = bootstrap_higher_symmetry()
        assert 'chiral' in r['superconformal']['chiral_algebra'].lower()

    def test_o_n_models(self):
        r = bootstrap_higher_symmetry()
        assert 'Ising' in r['global_symmetry']['o_n_models']

    def test_sp6f2_bootstrap(self):
        r = bootstrap_higher_symmetry()
        assert 'Sp(6,F2)' in r['w33_bootstrap']['sp6_symmetry']

    def test_40_channels(self):
        r = bootstrap_higher_symmetry()
        assert '40' in r['w33_bootstrap']['crossing_channels']


class TestHolographic:
    def test_witten_diagrams(self):
        r = holographic_bootstrap()
        assert 'Witten' in r['holographic']['conformal_blocks']

    def test_cardy_formula(self):
        r = holographic_bootstrap()
        assert 'Cardy' in r['black_holes']['cardy_formula']

    def test_chaos_bound(self):
        r = holographic_bootstrap()
        assert 'Lyapunov' in r['black_holes']['chaos'] or 'lambda' in r['black_holes']['chaos']

    def test_flat_space_limit(self):
        r = holographic_bootstrap()
        assert 'flat' in r['holographic']['flat_space_limit'].lower()


class TestAnalyticBootstrap:
    def test_caron_huot(self):
        r = analytic_bootstrap()
        assert 'Caron-Huot' in r['inversion']['caron_huot']

    def test_double_discontinuity(self):
        r = analytic_bootstrap()
        assert 'dDisc' in r['inversion']['formula'] or 'double' in r['inversion']['ddisc'].lower()

    def test_large_spin(self):
        r = analytic_bootstrap()
        assert 'spin' in r['lightcone']['anomalous_dimensions'].lower() or 'l' in r['lightcone']['anomalous_dimensions']

    def test_three_trajectories(self):
        r = analytic_bootstrap()
        assert '12' in r['w33_analytic']['trajectory_1']
        assert '2' in r['w33_analytic']['trajectory_2']
        assert '-4' in r['w33_analytic']['trajectory_3']


class TestSelfChecks:
    def test_all_pass(self):
        from THEORY_PART_CCLXXXI_CONFORMAL_BOOTSTRAP import run_self_checks
        assert run_self_checks() is True
