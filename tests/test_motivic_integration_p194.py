"""Tests for Pillar 194 - Motivic Integration."""
import pytest
import importlib

@pytest.fixture(scope="module")
def P194():
    return importlib.import_module("THEORY_PART_CCXCIV_MOTIVIC_INTEGRATION")

class TestMotivicIntegrationBasics:
    def test_kontsevich(self, P194):
        r = P194.motivic_integration_basics()
        assert 'Kontsevich' in r['kontsevich']['origin']
    def test_k0(self, P194):
        r = P194.motivic_integration_basics()
        assert 'K_0' in r['grothendieck_ring']['definition']
    def test_40_points(self, P194):
        r = P194.motivic_integration_basics()
        assert '40' in r['w33_motivic']['point_count']
    def test_lefschetz(self, P194):
        r = P194.motivic_integration_basics()
        assert 'L' in r['grothendieck_ring']['lefschetz']
    def test_batyrev(self, P194):
        r = P194.motivic_integration_basics()
        assert 'Batyrev' in r['kontsevich']['batyrev']

class TestArcSpaces:
    def test_nash(self, P194):
        r = P194.arc_spaces()
        assert 'Nash' in r['arc']['nash']
    def test_change_of_var(self, P194):
        r = P194.arc_spaces()
        assert 'change of variables' in r['measure']['change_of_variables'].lower()
    def test_jet(self, P194):
        r = P194.arc_spaces()
        assert 'jet' in r['arc']['jet_scheme'].lower()
    def test_cylinder(self, P194):
        r = P194.arc_spaces()
        assert 'Cylinder' in r['arc']['cylinder'] or 'cylinder' in r['arc']['cylinder']

class TestMotivicZetaFunctions:
    def test_denef_loeser(self, P194):
        r = P194.motivic_zeta_functions()
        assert 'Denef' in r['denef_loeser']['definition']
    def test_milnor(self, P194):
        r = P194.motivic_zeta_functions()
        assert 'Milnor' in r['milnor']['classical']
    def test_monodromy(self, P194):
        r = P194.motivic_zeta_functions()
        assert 'monodromy' in r['denef_loeser']['monodromy'].lower()
    def test_rationality(self, P194):
        r = P194.motivic_zeta_functions()
        assert 'rational' in r['denef_loeser']['rationality'].lower()

class TestMotivicDT:
    def test_ks(self, P194):
        r = P194.motivic_donaldson_thomas()
        assert 'Kontsevich' in r['dt']['kontsevich_soibelman']
    def test_1451520(self, P194):
        r = P194.motivic_donaldson_thomas()
        assert '1451520' in r['w33_dt']['counting_w33']
    def test_wall_crossing(self, P194):
        r = P194.motivic_donaldson_thomas()
        assert 'wall-crossing' in r['wall_crossing']['ks_formula'].lower() or 'Wall' in r['wall_crossing']['ks_formula']
    def test_bps(self, P194):
        r = P194.motivic_donaldson_thomas()
        assert 'BPS' in r['dt']['bps']

class TestMotivicHomotopy:
    def test_morel_voevodsky(self, P194):
        r = P194.motivic_homotopy()
        assert 'Morel' in r['a1_homotopy']['morel_voevodsky']
    def test_fields_medal(self, P194):
        r = P194.motivic_homotopy()
        assert 'Fields' in r['a1_homotopy']['voevodsky']
    def test_algebraic_cobordism(self, P194):
        r = P194.motivic_homotopy()
        assert 'MGL' in r['spectra']['algebraic_cobordism'] or 'algebraic cobordism' in r['spectra']['algebraic_cobordism'].lower()

class TestApplicationsPhysics:
    def test_ngo(self, P194):
        r = P194.applications_to_physics()
        assert 'Ngo' in r['number_theory']['fundamental_lemma']
    def test_mirror(self, P194):
        r = P194.applications_to_physics()
        assert 'mirror' in r['string_theory']['mirror_symmetry'].lower() or 'Mirror' in r['string_theory']['mirror_symmetry']
    def test_universality(self, P194):
        r = P194.applications_to_physics()
        assert 'universal' in r['w33_synthesis']['universality'].lower()
    def test_feynman(self, P194):
        r = P194.applications_to_physics()
        assert 'Feynman' in r['string_theory']['feynman']

class TestSelfChecks:
    def test_all_pass(self, P194):
        assert P194.run_self_checks() is True
