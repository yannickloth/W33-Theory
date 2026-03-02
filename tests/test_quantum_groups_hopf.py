"""Tests for Pillar 201 - Quantum Groups & Hopf Algebras."""
import pytest
import importlib

@pytest.fixture(scope="module")
def P201():
    return importlib.import_module("THEORY_PART_CCCI_QUANTUM_GROUPS_HOPF")

class TestHopfBasics:
    def test_antipode(self, P201):
        r = P201.hopf_algebra_basics()
        assert 'antipode' in r['axioms']['antipode'].lower() or 'S' in r['axioms']['antipode']
    def test_sweedler(self, P201):
        r = P201.hopf_algebra_basics()
        assert 'Sweedler' in r['sweedler']['notation']
    def test_group_algebra(self, P201):
        r = P201.hopf_algebra_basics()
        assert 'group' in r['examples']['group_algebra'].lower()
    def test_quasitriangular(self, P201):
        r = P201.hopf_algebra_basics()
        assert 'quasitriangular' in r['duality']['quasitriangular'].lower() or 'R-matrix' in r['duality']['quasitriangular']

class TestQuantumGroups:
    def test_drinfeld(self, P201):
        r = P201.quantum_groups()
        assert 'Drinfeld' in r['drinfeld_jimbo']['definition']
    def test_yang_baxter(self, P201):
        r = P201.quantum_groups()
        assert 'Yang-Baxter' in r['r_matrix']['yang_baxter']
    def test_kashiwara(self, P201):
        r = P201.quantum_groups()
        assert 'Kashiwara' in r['crystal_bases']['kashiwara']
    def test_root_of_unity(self, P201):
        r = P201.quantum_groups()
        assert 'root' in r['drinfeld_jimbo']['root_of_unity'].lower()

class TestRepTheory:
    def test_braiding(self, P201):
        r = P201.representation_theory_quantum()
        assert 'braid' in r['tensor_categories']['braiding'].lower()
    def test_verlinde(self, P201):
        r = P201.representation_theory_quantum()
        assert 'Verlinde' in r['tensor_categories']['verlinde_formula']
    def test_reshetikhin_turaev(self, P201):
        r = P201.representation_theory_quantum()
        assert 'Reshetikhin' in r['reshetikhin_turaev']['construction']

class TestKnotInvariants:
    def test_jones(self, P201):
        r = P201.knot_invariants()
        assert 'Jones' in r['jones_polynomial']['discovery']
    def test_homfly(self, P201):
        r = P201.knot_invariants()
        assert 'HOMFLY' in r['homfly_kauffman']['homfly_pt']
    def test_kashaev(self, P201):
        r = P201.knot_invariants()
        assert 'Kashaev' in r['volume_conjecture']['kashaev']
    def test_witten(self, P201):
        r = P201.knot_invariants()
        assert 'Witten' in r['tqft']['witten_rt']

class TestCategorification:
    def test_khovanov(self, P201):
        r = P201.categorification()
        assert 'Khovanov' in r['khovanov_homology']['definition']
    def test_klr(self, P201):
        r = P201.categorification()
        assert 'KLR' in r['categorified_quantum']['klr'] or 'Khovanov-Lauda' in r['categorified_quantum']['klr']

class TestW33Synthesis:
    def test_sp6f2(self, P201):
        r = P201.w33_quantum_group_synthesis()
        assert '1451520' in r['sp6f2_quantum']['order']
    def test_crystal_40(self, P201):
        r = P201.w33_quantum_group_synthesis()
        assert '40' in r['crystal_w33']['tensor_40']
    def test_three_families(self, P201):
        r = P201.w33_quantum_group_synthesis()
        assert 'three' in r['sp6f2_quantum']['three_families'].lower()

class TestSelfChecks:
    def test_all_pass(self, P201):
        assert P201.run_self_checks() is True
