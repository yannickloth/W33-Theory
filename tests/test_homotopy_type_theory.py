"""Tests for Pillar 152: Homotopy Type Theory & Univalent Foundations."""
import pytest, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'pillars'))

from THEORY_PART_CCLII_HOMOTOPY_TYPE_THEORY import (
    martin_lof_type_theory,
    homotopy_interpretation,
    univalence_axiom,
    higher_inductive_types,
    synthetic_homotopy_theory,
    ias_special_year,
    voevodsky_vision,
    proof_assistants,
    higher_category_theory,
    constructive_mathematics,
    hott_physics,
    complete_chain,
    run_all_checks,
)


class TestMartinLof:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.r = martin_lof_type_theory()

    def test_year(self):
        assert self.r['year'] == 1972

    def test_author(self):
        assert self.r['author'] == 'Per Martin-Lof'

    def test_identity_type(self):
        assert 'Id' in self.r['key_types']['identity_type']

    def test_curry_howard(self):
        assert 'Propositions as Types' in self.r['curry_howard']['principle']


class TestHomotopyInterpretation:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.r = homotopy_interpretation()

    def test_type_is_space(self):
        assert self.r['dictionary']['type'] == 'Space (homotopy type)'

    def test_identity_is_path(self):
        assert self.r['dictionary']['identity_type'] == 'Path space'

    def test_hofmann_streicher(self):
        assert '1994' in self.r['key_insight']['hofmann_streicher']


class TestUnivalenceAxiom:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.r = univalence_axiom()

    def test_year(self):
        assert self.r['year'] == 2009

    def test_voevodsky(self):
        assert 'Voevodsky' in self.r['formulated_by']

    def test_equivalent_identical(self):
        assert 'equivalent' in self.r['statement']['consequence'].lower() or \
               'identical' in self.r['statement']['consequence'].lower()

    def test_function_extensionality(self):
        assert 'function extensionality' in self.r['implications']['function_extensionality'].lower()


class TestHigherInductiveTypes:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.r = higher_inductive_types()

    def test_circle(self):
        assert 'S^1' in self.r['examples']['circle']['name']

    def test_pi1_s1(self):
        assert 'Z' in self.r['examples']['circle']['fundamental_group']

    def test_developers(self):
        assert 'Shulman' in self.r['developers']


class TestSyntheticHomotopy:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.r = synthetic_homotopy_theory()

    def test_pi1_s1_proof(self):
        assert 'Licata-Shulman' in self.r['results']['pi1_s1']['proved_by']

    def test_hopf(self):
        assert 'S^3' in self.r['results']['hopf_fibration']['theorem'] or \
               'Hopf' in self.r['results']['hopf_fibration']['theorem']

    def test_constructive(self):
        assert 'constructive' in self.r['advantage']['constructive'].lower()


class TestIASSpecialYear:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.r = ias_special_year()

    def test_years(self):
        assert self.r['years'] == '2012-2013'

    def test_hott_book(self):
        assert self.r['hott_book']['year'] == 2013

    def test_collaborative(self):
        assert 'GitHub' in self.r['hott_book']['collaborative']

    def test_voevodsky_organizer(self):
        assert any('Voevodsky' in o for o in self.r['organizers'])


class TestVoevodsky:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.r = voevodsky_vision()

    def test_fields_medal(self):
        assert self.r['fields_medal'] == 2002

    def test_died_2017(self):
        assert self.r['died'] == 2017

    def test_motivation(self):
        assert 'error' in self.r['motivation']['error_in_paper'].lower()


class TestProofAssistants:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.r = proof_assistants()

    def test_coq(self):
        assert 'coq_rocq' in self.r['systems']

    def test_agda(self):
        assert 'agda' in self.r['systems']

    def test_cubical_agda(self):
        assert 'cubical' in self.r['systems']['agda']['feature'].lower()


class TestHigherCategoryTheory:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.r = higher_category_theory()

    def test_lurie(self):
        assert 'Lurie' in self.r['infinity_topoi']['lurie']

    def test_internal_language(self):
        assert 'internal language' in self.r['infinity_topoi']['internal_language']

    def test_grothendieck(self):
        assert 'Grothendieck' in self.r['grothendieck_hypothesis']['conjecture_by']


class TestConstructive:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.r = constructive_mathematics()

    def test_hott_foundation(self):
        assert 'constructive' in self.r['comparison']['hott']['foundation'].lower() or \
               'homotop' in self.r['comparison']['hott']['foundation'].lower()


class TestHoTTPhysics:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.r = hott_physics()

    def test_schreiber(self):
        assert self.r['cohesive_hott']['author'] == 'Urs Schreiber'

    def test_modalities(self):
        assert len(self.r['cohesive_hott']['modalities']) == 3


class TestCompleteChain:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.r = complete_chain()

    def test_six_links(self):
        assert len(self.r['links']) == 6

    def test_foundations(self):
        assert 'FOUNDATIONS' in self.r['miracle']['statement']


class TestRunAllChecks:
    def test_all_checks_pass(self):
        assert run_all_checks() is True
