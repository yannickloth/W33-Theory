"""Tests for Pillar 189 - Representation Stability."""
import pytest
import importlib

@pytest.fixture(scope="module")
def P189():
    return importlib.import_module("THEORY_PART_CCLXXXIX_REPRESENTATION_STABILITY")

class TestFIModules:
    def test_cef(self, P189):
        r = P189.fi_modules()
        assert 'Church' in r['fi_category']['church_ellenberg_farb']
    def test_noetherian(self, P189):
        r = P189.fi_modules()
        assert 'Noetherian' in r['noetherianity']['theorem']
    def test_40_stable(self, P189):
        r = P189.fi_modules()
        assert '40' in r['w33_fi']['dimensions']
    def test_generating_degree(self, P189):
        r = P189.fi_modules()
        assert 'degree' in r['noetherianity']['generating_degree'].lower()

class TestRepresentationStability:
    def test_multiplicity(self, P189):
        r = P189.representation_stability()
        assert 'Multiplicity' in r['stability']['multiplicity_stability']
    def test_configuration(self, P189):
        r = P189.representation_stability()
        assert 'Conf' in r['configuration']['definition']
    def test_arnold(self, P189):
        r = P189.representation_stability()
        assert 'Arnold' in r['configuration']['arnol_d'] or 'braid' in r['configuration']['arnol_d']
    def test_stability_range(self, P189):
        r = P189.representation_stability()
        assert '2i' in r['stability']['range']

class TestHomologicalStability:
    def test_harer(self, P189):
        r = P189.homological_stability()
        assert 'Harer' in r['classical']['mapping_class']
    def test_madsen_weiss(self, P189):
        r = P189.homological_stability()
        assert 'Madsen' in r['classical']['madsen_weiss']
    def test_grw(self, P189):
        r = P189.homological_stability()
        assert 'Galatius' in r['classical']['grw']
    def test_secondary(self, P189):
        r = P189.homological_stability()
        assert '2018' in r['modern']['secondary']

class TestSamSnowden:
    def test_sam_snowden(self, P189):
        r = P189.sam_snowden_theory()
        assert 'Sam' in r['noetherian']['sam_snowden']
    def test_vi(self, P189):
        r = P189.sam_snowden_theory()
        assert 'VI' in r['categories']['vi']
    def test_grobner(self, P189):
        r = P189.sam_snowden_theory()
        assert 'Gröbner' in r['categories']['grobner'] or 'Grobner' in r['categories']['grobner']

class TestTwistedStability:
    def test_mmm(self, P189):
        r = P189.twisted_stability()
        assert 'kappa' in r['applications']['characteristic_classes']
    def test_string_topology(self, P189):
        r = P189.twisted_stability()
        assert 'Chas' in r['applications']['string_topology']
    def test_steinberg(self, P189):
        r = P189.twisted_stability()
        assert 'Steinberg' in r['w33_twisted']['steinberg']

class TestApplicationsConnections:
    def test_cohen_lenstra(self, P189):
        r = P189.applications_and_connections()
        assert 'Cohen-Lenstra' in r['number_theory']['cohen_lenstra']
    def test_hurwitz(self, P189):
        r = P189.applications_and_connections()
        assert 'Hurwitz' in r['topology']['hurwitz_spaces']
    def test_three_families(self, P189):
        r = P189.applications_and_connections()
        assert 'Three' in r['w33_synthesis']['particle_families']

class TestSelfChecks:
    def test_all_pass(self, P189):
        assert P189.run_self_checks() is True
