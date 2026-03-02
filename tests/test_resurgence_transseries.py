"""
Tests for Pillar 178 -- Resurgence & Trans-series from W(3,3)
"""
import pytest
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'pillars'))
from THEORY_PART_CCLXXVIII_RESURGENCE_TRANSSERIES import (
    resurgence_foundations, trans_series_structure,
    stokes_phenomena, resurgence_in_qft,
    resurgence_string_theory, ecalle_alien_calculus
)


class TestResurgenceFoundations:
    def test_ecalle_year(self):
        r = resurgence_foundations()
        assert '1981' in r['core']['ecalle_year']

    def test_alien_derivative(self):
        r = resurgence_foundations()
        assert 'alien' in r['core']['alien_derivative'].lower()

    def test_bridge_equation(self):
        r = resurgence_foundations()
        assert 'bridge' in r['core']['bridge_equation'].lower()

    def test_40_saddle_points(self):
        r = resurgence_foundations()
        assert r['w33_connection']['saddle_points'] == 40

    def test_borel_transform(self):
        r = resurgence_foundations()
        assert 'Borel' in r['borel']['borel_transform'] or 'borel' in r['borel']['borel_transform'].lower()

    def test_stokes_lines(self):
        r = resurgence_foundations()
        assert 'Stokes' in r['borel']['stokes_lines'] or 'stokes' in r['borel']['stokes_lines'].lower()


class TestTransSeries:
    def test_general_form(self):
        r = trans_series_structure()
        assert 'exp' in r['formal_structure']['general_form']

    def test_perturbative_sector(self):
        r = trans_series_structure()
        assert 'perturbative' in r['formal_structure']['perturbative']

    def test_40_instanton_types(self):
        r = trans_series_structure()
        assert '40' in r['w33_multi_instanton']['sectors']

    def test_large_order_growth(self):
        r = trans_series_structure()
        assert 'k!' in r['large_order']['growth'] or 'factorial' in r['large_order']['growth'].lower()

    def test_stokes_constant(self):
        r = trans_series_structure()
        assert 'Stokes' in r['large_order']['stokes_constant']


class TestStokesPhenomena:
    def test_stokes_discovery(self):
        r = stokes_phenomena()
        assert 'Stokes' in r['stokes_basics']['discovery']

    def test_stokes_multiplier(self):
        r = stokes_phenomena()
        assert 'jump' in r['stokes_basics']['stokes_multiplier'] or 'discrete' in r['stokes_basics']['stokes_multiplier']

    def test_240_edges(self):
        r = stokes_phenomena()
        assert r['w33_stokes']['edge_count'] == 240

    def test_stokes_automorphism(self):
        r = stokes_phenomena()
        assert 'automorphism' in r['stokes_automorphism']['definition']

    def test_wild_fundamental_group(self):
        r = stokes_phenomena()
        assert 'wild' in r['stokes_automorphism']['group_structure']


class TestResurgenceQFT:
    def test_dunne_unsal(self):
        r = resurgence_in_qft()
        assert 'dunne_unsal' in r

    def test_bion(self):
        r = resurgence_in_qft()
        assert 'bion' in r['dunne_unsal']['bion'].lower()

    def test_fractional_instanton(self):
        r = resurgence_in_qft()
        assert 'fractional' in r['dunne_unsal']['fractional_instanton']

    def test_w33_landscape(self):
        r = resurgence_in_qft()
        assert r['w33_landscape']['saddle_count'] == 40

    def test_renormalon_cancellation(self):
        r = resurgence_in_qft()
        assert 'cancel' in r['w33_landscape']['renormalon_cancellation'].lower()


class TestResurgenceString:
    def test_genus_expansion(self):
        r = resurgence_string_theory()
        assert 'genus' in r['string_perturbation']['genus_expansion']

    def test_factorial_growth(self):
        r = resurgence_string_theory()
        assert '(2g)!' in r['string_perturbation']['growth']

    def test_eynard_orantin(self):
        r = resurgence_string_theory()
        assert 'Eynard' in r['topological_string']['eynard_orantin']

    def test_landscape_40(self):
        r = resurgence_string_theory()
        assert '40' in r['w33_string']['landscape_points']


class TestAlienCalculus:
    def test_leibniz(self):
        r = ecalle_alien_calculus()
        assert 'Leibniz' in r['alien_derivatives']['leibniz']

    def test_delta_omega(self):
        r = ecalle_alien_calculus()
        assert 'Delta' in r['alien_derivatives']['definition']

    def test_convolution(self):
        r = ecalle_alien_calculus()
        assert 'convolution' in r['resurgent_algebra']['convolution']

    def test_median_summation(self):
        r = ecalle_alien_calculus()
        assert 'median' in r['w33_alien']['median_summation']


class TestSelfChecks:
    def test_all_pass(self):
        from THEORY_PART_CCLXXVIII_RESURGENCE_TRANSSERIES import run_self_checks
        assert run_self_checks() is True
