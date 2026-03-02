"""Tests for Pillar 203 - Noncommutative Geometry (Connes)."""
import pytest
import importlib

@pytest.fixture(scope="module")
def P203():
    return importlib.import_module("THEORY_PART_CCCIII_NONCOMMUTATIVE_GEOMETRY_CONNES")

class TestSpectralTriples:
    def test_dirac(self, P203):
        r = P203.spectral_triples()
        assert 'D' in r['definition']['dirac'] or 'operator' in r['definition']['dirac']
    def test_connes_2008(self, P203):
        r = P203.spectral_triples()
        assert 'Connes' in r['reconstruction']['connes_2008']
    def test_ko_dim(self, P203):
        r = P203.spectral_triples()
        assert 'KO' in r['real_structure']['ko_dimension']

class TestNCGStandardModel:
    def test_chamseddine(self, P203):
        r = P203.ncg_standard_model()
        assert 'Chamseddine' in r['spectral_action']['chamseddine_connes']
    def test_higgs(self, P203):
        r = P203.ncg_standard_model()
        assert 'Higgs' in r['higgs_mechanism']['inner_fluctuations'] or 'inner' in r['higgs_mechanism']['inner_fluctuations'].lower()
    def test_neutrino(self, P203):
        r = P203.ncg_standard_model()
        assert 'neutrino' in r['higgs_mechanism']['neutrino'].lower()

class TestCyclicHomology:
    def test_cyclic(self, P203):
        r = P203.cyclic_homology()
        assert 'cyclic' in r['cyclic_cohomology']['definition'].lower() or 'Cyclic' in r['cyclic_cohomology']['definition']
    def test_connes_moscovici(self, P203):
        r = P203.cyclic_homology()
        assert 'Connes' in r['local_index']['connes_moscovici']
    def test_chern(self, P203):
        r = P203.cyclic_homology()
        assert 'Chern' in r['chern_character']['k_theory'] or 'chern' in r['chern_character']['k_theory'].lower()

class TestQuantumGroupsNCG:
    def test_moyal(self, P203):
        r = P203.quantum_groups_ncg()
        assert 'Moyal' in r['nc_torus']['moyal']
    def test_woronowicz(self, P203):
        r = P203.quantum_groups_ncg()
        assert 'Woronowicz' in r['compact_quantum']['woronowicz']
    def test_podles(self, P203):
        r = P203.quantum_groups_ncg()
        assert 'Podle' in r['compact_quantum']['podles_sphere']

class TestIndexTheory:
    def test_kasparov(self, P203):
        r = P203.index_theory_ncg()
        assert 'Kasparov' in r['kk_theory']['kasparov']
    def test_poincare(self, P203):
        r = P203.index_theory_ncg()
        assert 'Poincar' in r['kk_theory']['poincare_duality']

class TestW33NCG:
    def test_sp6f2_order(self, P203):
        r = P203.w33_ncg_synthesis()
        assert '1451520' in r['sp6f2_spectral']['order']
    def test_dirac_w33(self, P203):
        r = P203.w33_ncg_synthesis()
        assert 'Dirac' in r['w33_spectral_triple']['dirac'] or 'adjacency' in r['w33_spectral_triple']['dirac'].lower()
    def test_three_families(self, P203):
        r = P203.w33_ncg_synthesis()
        assert 'three' in r['physics_w33']['three_families'].lower()

class TestSelfChecks:
    def test_all_pass(self, P203):
        assert P203.run_self_checks() is True
