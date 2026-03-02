"""Tests for Pillar 170 (CCLXX): Cluster Algebras."""
import pytest
from THEORY_PART_CCLXX_CLUSTER_ALGEBRAS import (
    cluster_algebra_foundations,
    laurent_phenomenon,
    finite_type_classification,
    cluster_categories,
    surfaces_triangulations,
    grassmannians_positivity,
    scattering_amplitudes,
    quantum_cluster_algebras,
    cluster_e8,
    w33_cluster_chain,
    run_self_checks,
)


class TestFoundations:
    def test_name(self):
        r = cluster_algebra_foundations()
        assert 'cluster' in r['name'].lower()

    def test_founders(self):
        r = cluster_algebra_foundations()
        assert 'fomin' in r['founders'].lower()

    def test_year(self):
        r = cluster_algebra_foundations()
        assert r['year'] == 2002

    def test_seed(self):
        r = cluster_algebra_foundations()
        assert 'skew' in r['seed']['exchange_matrix'].lower() or 'matrix' in r['seed']['exchange_matrix'].lower()

    def test_mutation_involution(self):
        r = cluster_algebra_foundations()
        assert 'involution' in r['mutation']['involution'].lower()


class TestLaurent:
    def test_theorem(self):
        r = laurent_phenomenon()
        assert 'laurent' in r['theorem']['statement'].lower()

    def test_positivity(self):
        r = laurent_phenomenon()
        assert 'non-negative' in r['positivity']['conjecture'].lower() or 'positiv' in r['positivity']['conjecture'].lower()

    def test_catalan(self):
        r = laurent_phenomenon()
        assert 'catalan' in r['examples']['catalan_numbers'].lower()


class TestFiniteType:
    def test_dynkin(self):
        r = finite_type_classification()
        assert 'dynkin' in r['theorem']['statement'].lower()

    def test_e8_25080(self):
        r = finite_type_classification()
        assert '25080' in str(r['cluster_counts']['E_8'])

    def test_a2_clusters(self):
        r = finite_type_classification()
        assert '5' in str(r['cluster_counts']['A_2'])

    def test_positive_roots(self):
        r = finite_type_classification()
        assert 'root' in r['root_system_connection']['positive_roots'].lower()


class TestCategories:
    def test_categorification(self):
        r = cluster_categories()
        assert 'categor' in r['categorification']['idea'].lower()

    def test_calabi_yau(self):
        r = cluster_categories()
        assert 'calabi' in r['derived_category']['2_calabi_yau'].lower()

    def test_tilting(self):
        r = cluster_categories()
        assert 'tilting' in r['tilting']['cluster_tilting'].lower()

    def test_gabriel(self):
        r = cluster_categories()
        assert 'dynkin' in r['representation_theory']['gabriel_theorem'].lower()


class TestSurfaces:
    def test_triangulations(self):
        r = surfaces_triangulations()
        assert 'triangul' in r['surface_type']['clusters'].lower()

    def test_flip(self):
        r = surfaces_triangulations()
        assert 'flip' in r['surface_type']['mutation'].lower()

    def test_snake_graphs(self):
        r = surfaces_triangulations()
        assert 'matching' in r['snake_graphs']['cluster_expansion'].lower()


class TestGrassmannians:
    def test_cluster_structure(self):
        r = grassmannians_positivity()
        assert 'cluster' in r['grassmannian']['cluster_structure'].lower()

    def test_amplituhedron(self):
        r = grassmannians_positivity()
        assert 'amplitud' in r['amplituhedron']['definition'].lower() or 'scatter' in r['amplituhedron']['definition'].lower()

    def test_total_positivity(self):
        r = grassmannians_positivity()
        assert 'positiv' in r['total_positivity']['definition'].lower()


class TestAmplitudes:
    def test_n4_sym(self):
        r = scattering_amplitudes()
        assert 'yang-mills' in r['n4_sym']['theory'].lower()

    def test_plabic(self):
        r = scattering_amplitudes()
        assert 'planar' in r['plabic_graphs']['definition'].lower() or 'bicolor' in r['plabic_graphs']['definition'].lower()


class TestQuantumCluster:
    def test_definition(self):
        r = quantum_cluster_algebras()
        assert 'berenstein' in r['definition']['berenstein_zelevinsky'].lower()

    def test_dt_invariants(self):
        r = quantum_cluster_algebras()
        assert 'donaldson' in r['donaldson_thomas']['dt_invariants'].lower()


class TestE8:
    def test_rank(self):
        r = cluster_e8()
        assert r['e8_finite_type']['rank'] == 8

    def test_clusters_25080(self):
        r = cluster_e8()
        assert r['e8_finite_type']['total_clusters'] == 25080

    def test_positive_roots_120(self):
        r = cluster_e8()
        assert '120' in r['e8_finite_type']['positive_roots']


class TestW33Chain:
    def test_chain(self):
        r = w33_cluster_chain()
        assert 'e8' in str(r['chain']).lower()

    def test_synthesis(self):
        r = w33_cluster_chain()
        assert 'dynkin' in str(r['synthesis']).lower()


class TestSelfChecks:
    def test_all_pass(self):
        checks = run_self_checks()
        for name, val in checks:
            assert val, f"Self-check failed: {name}"

    def test_count(self):
        checks = run_self_checks()
        assert len(checks) == 15
