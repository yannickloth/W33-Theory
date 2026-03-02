"""Tests for Pillar 171 (CCLXXI): Persistent Homology."""
import pytest
from THEORY_PART_CCLXXI_PERSISTENT_HOMOLOGY import (
    persistent_homology_foundations,
    filtration_types,
    structure_theorem,
    stability_results,
    computation,
    topological_data_analysis,
    applications,
    extended_persistence,
    physics_connections,
    w33_persistence_chain,
    run_self_checks,
)


class TestFoundations:
    def test_name(self):
        r = persistent_homology_foundations()
        assert 'persistent' in r['name'].lower()

    def test_founders(self):
        r = persistent_homology_foundations()
        assert 'edelsbrunner' in r['founders'].lower()

    def test_barannikov(self):
        r = persistent_homology_foundations()
        assert 'barannikov' in r['precursor'].lower()

    def test_barcode(self):
        r = persistent_homology_foundations()
        assert 'birth' in r['representations']['barcode'].lower() or 'death' in r['representations']['barcode'].lower()

    def test_filtration(self):
        r = persistent_homology_foundations()
        assert 'nested' in r['definition']['filtration'].lower() or 'simplicial' in r['definition']['filtration'].lower()


class TestFiltrations:
    def test_vietoris_rips(self):
        r = filtration_types()
        assert 'distance' in r['vietoris_rips']['definition'].lower() or 'simplex' in r['vietoris_rips']['definition'].lower()

    def test_cech(self):
        r = filtration_types()
        assert 'ball' in r['cech']['definition'].lower() or 'intersection' in r['cech']['definition'].lower()

    def test_sublevel(self):
        r = filtration_types()
        assert 'sublevel' in r['sublevel_set']['definition'].lower() or 'f^{-1}' in r['sublevel_set']['definition']

    def test_alpha(self):
        r = filtration_types()
        assert 'delaunay' in r['alpha_complex']['definition'].lower()


class TestStructure:
    def test_persistence_modules(self):
        r = structure_theorem()
        assert 'functor' in r['persistence_modules']['definition'].lower() or 'module' in r['persistence_modules']['definition'].lower()

    def test_decomposition(self):
        r = structure_theorem()
        assert 'interval' in r['decomposition']['theorem'].lower()

    def test_uniqueness(self):
        r = structure_theorem()
        assert 'unique' in r['decomposition']['uniqueness'].lower()

    def test_multiparameter(self):
        r = structure_theorem()
        assert 'wild' in r['multiparameter']['carlsson_zomorodian'].lower() or 'no simple' in r['multiparameter']['challenge'].lower()


class TestStability:
    def test_bottleneck(self):
        r = stability_results()
        assert 'metric' in r['bottleneck_distance']['metric'].lower()

    def test_lipschitz(self):
        r = stability_results()
        assert 'lipschitz' in r['stability_theorem']['lipschitz'].lower()

    def test_wasserstein(self):
        r = stability_results()
        assert 'wasserstein' in r['wasserstein']['definition'].lower() or 'W_p' in r['wasserstein']['definition']

    def test_interleaving(self):
        r = stability_results()
        assert 'interleaving' in r['algebraic_stability']['interleaving'].lower()


class TestComputation:
    def test_ripser(self):
        r = computation()
        assert 'ripser' in r['software']['ripser'].lower()

    def test_gudhi(self):
        r = computation()
        assert 'gudhi' in r['software']['gudhi'].lower()

    def test_clearing(self):
        r = computation()
        assert 'clearing' in r['optimizations']['clearing'].lower()


class TestTDA:
    def test_pipeline(self):
        r = topological_data_analysis()
        assert 'point cloud' in r['pipeline']['step_1'].lower() or 'data' in r['pipeline']['step_1'].lower()

    def test_landscapes(self):
        r = topological_data_analysis()
        assert 'bubenik' in r['vectorization']['persistence_landscapes'].lower()

    def test_ml(self):
        r = topological_data_analysis()
        assert 'kernel' in str(r['machine_learning']).lower() or 'deep' in str(r['machine_learning']).lower()


class TestApplications:
    def test_materials(self):
        r = applications()
        assert 'amorphous' in str(r['materials_science']).lower()

    def test_biology(self):
        r = applications()
        assert 'protein' in str(r['biology']).lower()

    def test_cosmology(self):
        r = applications()
        assert 'cosmic' in str(r['cosmology']).lower()


class TestExtended:
    def test_zigzag(self):
        r = extended_persistence()
        assert 'zigzag' in r['zigzag']['definition'].lower() or 'reverse' in r['zigzag']['definition'].lower()

    def test_sheaf(self):
        r = extended_persistence()
        assert 'sheaf' in str(r['sheaf_theory']).lower()


class TestPhysics:
    def test_qcd(self):
        r = physics_connections()
        assert 'qcd' in r['lattice_physics']['qcd'].lower()

    def test_e8(self):
        r = physics_connections()
        assert '240' in r['e8_persistence']['root_system'] or 'root' in r['e8_persistence']['root_system'].lower()


class TestW33Chain:
    def test_chain(self):
        r = w33_persistence_chain()
        assert 'e8' in str(r['chain']).lower()

    def test_synthesis(self):
        r = w33_persistence_chain()
        assert 'robust' in str(r['synthesis']).lower() or 'stability' in str(r['synthesis']).lower()


class TestSelfChecks:
    def test_all_pass(self):
        checks = run_self_checks()
        for name, val in checks:
            assert val, f"Self-check failed: {name}"

    def test_count(self):
        checks = run_self_checks()
        assert len(checks) == 15
