"""Tests for Pillar 196 - Persistent Homology & TDA."""
import pytest
import importlib

@pytest.fixture(scope="module")
def P196():
    return importlib.import_module("THEORY_PART_CCXCVI_PERSISTENT_HOMOLOGY_TDA")

class TestPersistentHomologyBasics:
    def test_vietoris_rips(self, P196):
        r = P196.persistent_homology_basics()
        assert 'Vietoris' in r['simplicial_complexes']['vietoris_rips'] or 'Rips' in r['simplicial_complexes']['vietoris_rips']
    def test_barcodes(self, P196):
        r = P196.persistent_homology_basics()
        assert 'Carlsson' in r['barcodes']['carlsson_zomorodian']
    def test_birth_death(self, P196):
        r = P196.persistent_homology_basics()
        assert 'birth' in r['filtrations']['birth_death'].lower() or 'Birth' in r['filtrations']['birth_death']
    def test_filtration(self, P196):
        r = P196.persistent_homology_basics()
        assert 'filtration' in r['filtrations']['filtration'].lower() or 'Filtration' in r['filtrations']['filtration']

class TestStabilityMetrics:
    def test_bottleneck(self, P196):
        r = P196.stability_and_metrics()
        assert 'bottleneck' in r['bottleneck_distance']['definition'].lower() or 'Bottleneck' in r['bottleneck_distance']['definition']
    def test_wasserstein(self, P196):
        r = P196.stability_and_metrics()
        assert 'Wasserstein' in r['wasserstein_distance']['definition']
    def test_stability(self, P196):
        r = P196.stability_and_metrics()
        assert '2007' in r['stability_theorem']['csehh2007'] or 'Cohen' in r['stability_theorem']['csehh2007']

class TestComputational:
    def test_ripser(self, P196):
        r = P196.computational_methods()
        assert 'Bauer' in r['ripser']['bauer_2021']
    def test_smith(self, P196):
        r = P196.computational_methods()
        assert 'Smith' in r['matrix_reduction']['smith_normal_form']
    def test_alpha(self, P196):
        r = P196.computational_methods()
        assert 'alpha' in r['gudhi']['alpha_complex'].lower() or 'Alpha' in r['gudhi']['alpha_complex']

class TestMultiparameter:
    def test_no_barcode(self, P196):
        r = P196.multiparameter_persistence()
        assert 'no' in r['multipersistence_modules']['no_barcode'].lower() or 'No' in r['multipersistence_modules']['no_barcode']
    def test_rivet(self, P196):
        r = P196.multiparameter_persistence()
        assert 'RIVET' in r['rivet_software']['rivet']
    def test_betti(self, P196):
        r = P196.multiparameter_persistence()
        assert 'Betti' in r['rank_invariant']['multigraded_betti'] or 'betti' in r['rank_invariant']['multigraded_betti'].lower()

class TestApplications:
    def test_protein(self, P196):
        r = P196.applications_science()
        assert 'Xia' in r['protein_structure']['xia_wei']
    def test_brain(self, P196):
        r = P196.applications_science()
        assert 'Blue Brain' in r['neuroscience']['blue_brain']

class TestW33TDA:
    def test_40_points(self, P196):
        r = P196.w33_tda_synthesis()
        assert '40' in r['w33_point_cloud']['dataset']
    def test_sp6_symmetry(self, P196):
        r = P196.w33_tda_synthesis()
        assert '1451520' in r['sp6_symmetry']['symmetry_count']
    def test_fingerprint(self, P196):
        r = P196.w33_tda_synthesis()
        assert 'unique' in r['topological_fingerprint']['uniqueness'].lower()

class TestSelfChecks:
    def test_all_pass(self, P196):
        assert P196.run_self_checks() is True
