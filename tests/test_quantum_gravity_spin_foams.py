"""Tests for Pillar 193 - Quantum Gravity & Spin Foams."""
import pytest
import importlib

@pytest.fixture(scope="module")
def P193():
    return importlib.import_module("THEORY_PART_CCXCIII_QUANTUM_GRAVITY_SPIN_FOAMS")

class TestLoopQuantumGravity:
    def test_ashtekar(self, P193):
        r = P193.loop_quantum_gravity()
        assert 'Ashtekar' in r['foundations']['ashtekar']
    def test_40_nodes(self, P193):
        r = P193.loop_quantum_gravity()
        assert '40' in r['w33_lqg']['vertices_40']
    def test_holonomy(self, P193):
        r = P193.loop_quantum_gravity()
        assert 'Holonomy' in r['foundations']['holonomy'] or 'holonomy' in r['foundations']['holonomy'].lower()
    def test_immirzi(self, P193):
        r = P193.loop_quantum_gravity()
        assert 'Immirzi' in r['foundations']['barbero_immirzi']

class TestSpinNetworks:
    def test_penrose(self, P193):
        r = P193.spin_networks()
        assert 'Penrose' in r['penrose']['origin']
    def test_area_spectrum(self, P193):
        r = P193.spin_networks()
        assert 'j(j+1)' in r['quantization']['area_spectrum'] or 'j' in r['quantization']['area_spectrum']
    def test_discrete(self, P193):
        r = P193.spin_networks()
        assert 'discrete' in r['quantization']['discreteness'].lower()
    def test_planck(self, P193):
        r = P193.spin_networks()
        assert 'Planck' in r['quantization']['l_planck']

class TestSpinFoams:
    def test_eprl(self, P193):
        r = P193.spin_foams()
        assert 'EPRL' in r['eprl']['name']
    def test_ponzano_regge(self, P193):
        r = P193.spin_foams()
        assert 'Ponzano' in r['basics']['ponzano_regge']
    def test_bc_model(self, P193):
        r = P193.spin_foams()
        assert 'Barrett' in r['eprl']['bc_model'] or 'Crane' in r['eprl']['bc_model']
    def test_turaev_viro(self, P193):
        r = P193.spin_foams()
        assert 'Turaev' in r['basics']['turaev_viro']

class TestBlackHoleEntropy:
    def test_bekenstein(self, P193):
        r = P193.black_hole_entropy()
        assert 'Bekenstein' in r['bekenstein_hawking']['bekenstein']
    def test_hawking(self, P193):
        r = P193.black_hole_entropy()
        assert 'Hawking' in r['bekenstein_hawking']['hawking']
    def test_1451520(self, P193):
        r = P193.black_hole_entropy()
        assert '1451520' in r['w33_bh']['microstate_count']
    def test_log_correction(self, P193):
        r = P193.black_hole_entropy()
        assert 'log' in r['lqg_derivation']['logarithmic'].lower()

class TestCausalSetsCDT:
    def test_causal_sets(self, P193):
        r = P193.causal_sets_and_cdt()
        assert 'Bombelli' in r['causal_sets']['definition']
    def test_cdt_de_sitter(self, P193):
        r = P193.causal_sets_and_cdt()
        assert 'de Sitter' in r['cdt']['de_sitter']
    def test_spectral_dim(self, P193):
        r = P193.causal_sets_and_cdt()
        assert 'Spectral' in r['cdt']['spectral_dimension'] or 'spectral' in r['cdt']['spectral_dimension']

class TestGroupFieldTheory:
    def test_boulatov(self, P193):
        r = P193.group_field_theory()
        assert 'Boulatov' in r['basics']['boulatov']
    def test_tensorial(self, P193):
        r = P193.group_field_theory()
        assert 'renormalizable' in r['renormalization']['tensorial'].lower()
    def test_sp6f2(self, P193):
        r = P193.group_field_theory()
        assert 'Sp(6,F2)' in r['w33_gft']['field_on_sp6']

class TestSelfChecks:
    def test_all_pass(self, P193):
        assert P193.run_self_checks() is True
