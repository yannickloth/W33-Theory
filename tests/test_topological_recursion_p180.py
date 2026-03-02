"""
Tests for Pillar 180 -- Topological Recursion & Spectral Curves from W(3,3)
"""
import pytest
import sys, os
from fractions import Fraction

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'pillars'))
from THEORY_PART_CCLXXX_TOPOLOGICAL_RECURSION import (
    spectral_curve_basics, topological_recursion_definition,
    witten_kontsevich, mirzakhani_volumes,
    bkmp_conjecture, higher_genus_surfaces
)


class TestSpectralCurve:
    def test_riemann_surface(self):
        r = spectral_curve_basics()
        assert 'Riemann' in r['components']['sigma']

    def test_five_components(self):
        r = spectral_curve_basics()
        assert len(r['components']) >= 5

    def test_airy_example(self):
        r = spectral_curve_basics()
        assert 'Airy' in r['examples']['airy'] or 'z^2' in r['examples']['airy']

    def test_hitchin_example(self):
        r = spectral_curve_basics()
        assert 'Hitchin' in r['examples']['hitchin']

    def test_w33_spectral_curve(self):
        r = spectral_curve_basics()
        assert 'W(3,3)' in r['w33_curve']['spectral_curve']

    def test_ramification(self):
        r = spectral_curve_basics()
        assert 'dx = 0' in r['ramification']['definition']


class TestTopologicalRecursion:
    def test_residue_formula(self):
        r = topological_recursion_definition()
        assert 'Res' in r['recursion']['formula']

    def test_universality(self):
        r = topological_recursion_definition()
        assert 'universal' in r['recursion']['universality'].lower()

    def test_symmetry_property(self):
        r = topological_recursion_definition()
        assert 'symmetric' in r['properties']['symmetry']

    def test_modular_forms(self):
        r = topological_recursion_definition()
        assert 'modular' in r['properties']['modularity'].lower()

    def test_free_energies(self):
        r = topological_recursion_definition()
        assert 'planar' in r['free_energies']['f_0']
        assert 'torus' in r['free_energies']['f_1']


class TestWittenKontsevich:
    def test_witten_1991(self):
        r = witten_kontsevich()
        assert '1991' in r['theorem']['witten']

    def test_kontsevich_1992(self):
        r = witten_kontsevich()
        assert '1992' in r['theorem']['kontsevich']

    def test_kdv(self):
        r = witten_kontsevich()
        assert 'KdV' in r['theorem']['kdv_hierarchy']

    def test_tau_1_1(self):
        r = witten_kontsevich()
        assert r['values']['tau_1_1'] == Fraction(1, 24)

    def test_airy_curve_branch(self):
        r = witten_kontsevich()
        assert 'z = 0' in r['airy_curve']['branch_point']


class TestMirzakhaniVolumes:
    def test_fields_medal(self):
        r = mirzakhani_volumes()
        assert 'Fields' in r['recursion']['discoverer']

    def test_polynomial_volumes(self):
        r = mirzakhani_volumes()
        assert 'polynomial' in r['recursion']['polynomial']

    def test_jt_gravity(self):
        r = mirzakhani_volumes()
        assert 'JT' in r['physics']['jt_gravity']

    def test_black_holes(self):
        r = mirzakhani_volumes()
        assert 'black hole' in r['physics']['black_holes'].lower() or 'Black hole' in r['physics']['black_holes']

    def test_v03(self):
        r = mirzakhani_volumes()
        assert r['volumes']['v_0_3'] == 1


class TestBKMP:
    def test_authors(self):
        r = bkmp_conjecture()
        assert 'Bouchard' in r['bkmp']['authors']

    def test_proved(self):
        r = bkmp_conjecture()
        assert 'Proved' in r['bkmp']['status'] or 'proved' in r['bkmp']['status'].lower()

    def test_gw_theory(self):
        r = bkmp_conjecture()
        assert 'gw_theory' in r

    def test_virtual_class(self):
        r = bkmp_conjecture()
        assert 'virtual' in r['gw_theory']['virtual_class']

    def test_w33_cy3(self):
        r = bkmp_conjecture()
        assert 'E6' in r['w33_cy3']['e6_cy3']


class TestHigherGenusSurfaces:
    def test_chi_sphere(self):
        r = higher_genus_surfaces()
        assert r['euler_values']['chi_sphere'] == 2

    def test_chi_torus(self):
        r = higher_genus_surfaces()
        assert r['euler_values']['chi_torus'] == 0

    def test_chi_pants(self):
        r = higher_genus_surfaces()
        assert r['euler_values']['chi_pants'] == -1

    def test_pants_decomposition(self):
        r = higher_genus_surfaces()
        assert 'pants' in r['surface_counting']['pants_decomposition']

    def test_hurwitz(self):
        r = higher_genus_surfaces()
        assert 'Lambert' in r['hurwitz']['spectral_curve']

    def test_moduli_dimension(self):
        r = higher_genus_surfaces()
        assert '6g-6+3n' in r['surface_counting']['moduli_dimension'] or '3(2g-2+n)' in r['surface_counting']['moduli_dimension']


class TestSelfChecks:
    def test_all_pass(self):
        from THEORY_PART_CCLXXX_TOPOLOGICAL_RECURSION import run_self_checks
        assert run_self_checks() is True
