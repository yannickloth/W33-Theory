"""Tests for Pillar 198 - Floer Homology."""
import pytest
import importlib

@pytest.fixture(scope="module")
def P198():
    return importlib.import_module("THEORY_PART_CCXCVIII_FLOER_HOMOLOGY")

class TestFloerBasics:
    def test_floer_1988(self, P198):
        r = P198.floer_homology_basics()
        assert 'Floer' in r['infinite_dim_morse']['floer_1988']
    def test_gromov(self, P198):
        r = P198.floer_homology_basics()
        assert 'Gromov' in r['pseudo_holomorphic_curves']['gromov_1985']
    def test_arnold(self, P198):
        r = P198.floer_homology_basics()
        assert 'Arnold' in r['arnold_conjecture']['statement']
    def test_action(self, P198):
        r = P198.floer_homology_basics()
        assert 'action' in r['infinite_dim_morse']['action_functional'].lower() or 'Action' in r['infinite_dim_morse']['action_functional']

class TestLagrangianFloer:
    def test_fooo(self, P198):
        r = P198.lagrangian_floer()
        assert 'Fukaya' in r['fukaya_category']['fooo']
    def test_a_infinity(self, P198):
        r = P198.lagrangian_floer()
        assert 'A_infinity' in r['fukaya_category']['a_infinity'] or 'A-infinity' in r['fukaya_category']['a_infinity'] or 'A_∞' in r['fukaya_category']['a_infinity']
    def test_bounding(self, P198):
        r = P198.lagrangian_floer()
        assert 'bounding' in r['obstructions']['bounding_cochains'].lower() or 'Bounding' in r['obstructions']['bounding_cochains']

class TestHeegaardFloer:
    def test_ozsvath_szabo(self, P198):
        r = P198.heegaard_floer()
        assert 'Ozsv' in r['ozsvath_szabo']['construction']
    def test_genus(self, P198):
        r = P198.heegaard_floer()
        assert 'genus' in r['knot_floer']['genus_detection'].lower()
    def test_concordance(self, P198):
        r = P198.heegaard_floer()
        assert 'epsilon' in r['concordance_invariants']['epsilon_invariant'].lower() or 'ε' in r['concordance_invariants']['epsilon_invariant']

class TestSymplecticInvariants:
    def test_spectral(self, P198):
        r = P198.symplectic_invariants()
        assert 'Oh' in r['spectral_invariants']['oh_schwarz'] or 'spectral' in r['spectral_invariants']['oh_schwarz'].lower()
    def test_hofer_zehnder(self, P198):
        r = P198.symplectic_invariants()
        assert 'Hofer' in r['symplectic_capacities']['hofer_zehnder']
    def test_displacement(self, P198):
        r = P198.symplectic_invariants()
        assert 'displacement' in r['symplectic_capacities']['displacement_energy'].lower() or 'Displacement' in r['symplectic_capacities']['displacement_energy']

class TestGaugeTheoryFloer:
    def test_kronheimer_mrowka(self, P198):
        r = P198.gauge_theory_floer()
        assert 'Kronheimer' in r['seiberg_witten_floer']['kronheimer_mrowka']
    def test_manolescu(self, P198):
        r = P198.gauge_theory_floer()
        assert 'Manolescu' in r['floer_homotopy']['manolescu_pin2']
    def test_atiyah_floer(self, P198):
        r = P198.gauge_theory_floer()
        assert 'Atiyah' in r['atiyah_floer']['conjecture']

class TestW33Floer:
    def test_lagrangians(self, P198):
        r = P198.w33_floer_synthesis()
        assert 'isotropic' in r['w33_lagrangians']['isotropic_subspaces'].lower()
    def test_sp6f2(self, P198):
        r = P198.w33_floer_synthesis()
        assert 'Sp(6' in r['w33_floer_groups']['sp6f2_action'] or '1451520' in r['w33_floer_groups']['sp6f2_action']
    def test_arnold_w33(self, P198):
        r = P198.w33_floer_synthesis()
        assert '40' in r['arnold_w33']['fixed_point_bound'] or 'Arnold' in r['arnold_w33']['fixed_point_bound']

class TestSelfChecks:
    def test_all_pass(self, P198):
        assert P198.run_self_checks() is True
