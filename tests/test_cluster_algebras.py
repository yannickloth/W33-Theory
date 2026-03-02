"""Tests for Pillar 150: Cluster Algebras & Combinatorial Dynamics."""
import pytest, math, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'pillars'))

from THEORY_PART_CCL_CLUSTER_ALGEBRAS import (
    cluster_algebra_foundations,
    laurent_phenomenon,
    finite_type_classification,
    quiver_mutations,
    cluster_grassmannian,
    y_systems,
    total_positivity,
    cluster_categories,
    cluster_surfaces,
    positivity_conjecture,
    e8_cluster_algebra,
    complete_chain,
    run_all_checks,
)


class TestClusterAlgebraFoundations:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.r = cluster_algebra_foundations()

    def test_year(self):
        assert self.r['year'] == 2002

    def test_authors(self):
        assert any('Fomin' in a for a in self.r['introduced_by'])

    def test_laurent_phenomenon(self):
        assert 'Laurent' in self.r['key_properties']['laurent_phenomenon']

    def test_positivity(self):
        assert 'NON-NEGATIVE' in self.r['key_properties']['positivity']


class TestLaurentPhenomenon:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.r = laurent_phenomenon()

    def test_a2_period_5(self):
        assert self.r['a2_period'] == 5

    def test_b2_period_6(self):
        assert self.r['b2_period'] == 6

    def test_g2_period_8(self):
        assert self.r['g2_period'] == 8

    def test_all_laurent(self):
        assert self.r['a2_example']['all_laurent'] is True


class TestFiniteType:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.r = finite_type_classification()

    def test_dynkin_types_include_e8(self):
        assert 'E_8' in self.r['classification']['dynkin_types']

    def test_same_as_lie(self):
        assert 'Lie algebras' in self.r['classification']['same_as']

    def test_e8_cluster_variables(self):
        assert self.r['cluster_counts']['E_8']['cluster_variables'] == 128

    def test_e8_positive_roots(self):
        assert self.r['cluster_counts']['E_8']['positive_roots'] == 120

    def test_catalan_5(self):
        assert self.r['catalan_numbers']['C_3'] == 5

    def test_catalan_14(self):
        assert self.r['catalan_numbers']['C_4'] == 14


class TestQuiverMutations:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.r = quiver_mutations()

    def test_gabriel_year(self):
        assert self.r['representation_theory']['year'] == 1972

    def test_gabriel_author(self):
        assert 'Gabriel' in self.r['representation_theory']['author']

    def test_mutation_steps(self):
        assert len(self.r['definition']['mutation_steps']) == 3


class TestClusterGrassmannian:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.r = cluster_grassmannian()

    def test_plucker(self):
        assert 'Plucker' in self.r['grassmannian']['plucker']

    def test_amplituhedron(self):
        assert 'amplituhedron' in self.r['amplituhedron']['arkani_hamed_trnka'].lower() or \
               'Amplituhedron' in self.r['amplituhedron']['arkani_hamed_trnka']


class TestYSystems:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.r = y_systems()

    def test_e8_period_30(self):
        assert self.r['periodicities']['E_8']['period'] == 30

    def test_zamolodchikov_1991(self):
        assert self.r['zamolodchikov']['year'] == 1991

    def test_e6_period_12(self):
        assert self.r['periodicities']['E_6']['period'] == 12


class TestTotalPositivity:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.r = total_positivity()

    def test_lusztig_1994(self):
        assert self.r['lusztig']['year'] == 1994

    def test_canonical_bases(self):
        assert 'canonical' in self.r['lusztig']['canonical_bases'].lower()


class TestClusterCategories:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.r = cluster_categories()

    def test_bmrrt(self):
        assert self.r['definition']['acronym'] == 'BMRRT'

    def test_calabi_yau_2(self):
        assert '2' in self.r['properties']['calabi_yau']


class TestClusterSurfaces:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.r = cluster_surfaces()

    def test_year(self):
        assert self.r['year'] == 2008

    def test_thurston(self):
        assert 'Thurston' in self.r['authors']

    def test_fock_goncharov(self):
        assert self.r['teichmuller']['year'] == 2006


class TestPositivityConjecture:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.r = positivity_conjecture()

    def test_proved_year(self):
        assert self.r['proof']['year'] == 2018

    def test_kontsevich(self):
        assert any('Kontsevich' in a for a in self.r['proof']['proved_by'])

    def test_scattering_diagrams(self):
        assert 'wall' in self.r['scattering_diagrams']['origin'].lower() or \
               'crossing' in self.r['scattering_diagrams']['origin'].lower()


class TestE8ClusterAlgebra:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.r = e8_cluster_algebra()

    def test_rank(self):
        assert self.r['properties']['rank'] == 8

    def test_cluster_variables(self):
        assert self.r['properties']['cluster_variables'] == 128

    def test_num_clusters(self):
        assert self.r['e8_clusters']['num_clusters'] == 25080

    def test_coxeter_30(self):
        assert self.r['e8_clusters']['coxeter_number'] == 30

    def test_y_period(self):
        assert self.r['y_system']['period'] == 30

    def test_w33_chain(self):
        assert any('W(3,3)' in p for p in self.r['w33_chain']['path'])


class TestCompleteChain:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.r = complete_chain()

    def test_six_links(self):
        assert len(self.r['links']) == 6

    def test_dynkin_in_miracle(self):
        assert 'DYNKIN' in self.r['miracle']['statement']


class TestRunAllChecks:
    def test_all_checks_pass(self):
        assert run_all_checks() is True
