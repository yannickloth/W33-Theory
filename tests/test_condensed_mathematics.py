"""Tests for Pillar 153: Condensed Mathematics."""
import pytest, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'pillars'))

from THEORY_PART_CCLIII_CONDENSED_MATHEMATICS import (
    condensed_sets,
    liquid_vector_spaces,
    solid_abelian_groups,
    liquid_tensor_experiment,
    pyknotic_objects,
    scholze_vision,
    unification_vision,
    pro_etale_site,
    condensed_physics,
    formalization,
    e8_condensed,
    complete_chain,
    run_all_checks,
)


class TestCondensedSets:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.r = condensed_sets()

    def test_year(self):
        assert self.r['year'] == 2018

    def test_scholze(self):
        assert any('Scholze' in a for a in self.r['introduced_by'])

    def test_abelian(self):
        assert 'abelian' in self.r['advantages']['abelian_category'].lower()

    def test_profinite(self):
        assert 'profinite' in self.r['definition']['site'].lower()


class TestLiquidVectorSpaces:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.r = liquid_vector_spaces()

    def test_abelian_solution(self):
        assert 'abelian' in self.r['motivation']['solution'].lower()

    def test_applications(self):
        assert 'complex_geometry' in self.r['applications']


class TestSolidAbelianGroups:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.r = solid_abelian_groups()

    def test_p_adic(self):
        assert 'p-adic' in self.r['applications']['p_adic'].lower() or \
               'p_adic' in self.r['applications']


class TestLiquidTensorExperiment:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.r = liquid_tensor_experiment()

    def test_proposed_2020(self):
        assert self.r['year_proposed'] == 2020

    def test_completed_2022(self):
        assert self.r['year_completed'] == 2022

    def test_lean(self):
        assert 'Lean' in self.r['verification']['proof_assistant']

    def test_commelin(self):
        assert 'Commelin' in self.r['verification']['led_by']

    def test_quanta(self):
        assert 'Quanta' in self.r['significance']['quanta']


class TestPyknoticObjects:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.r = pyknotic_objects()

    def test_year(self):
        assert self.r['year'] == 2019

    def test_barwick(self):
        assert any('Barwick' in a for a in self.r['introduced_by'])

    def test_etymology(self):
        assert 'dense' in self.r['definition']['etymology'].lower() or \
               'compact' in self.r['definition']['etymology'].lower()


class TestScholzeVision:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.r = scholze_vision()

    def test_fields_medal(self):
        assert self.r['fields_medal'] == 2018

    def test_age_30(self):
        assert self.r['fields_medal_citation']['age_at_award'] == 30

    def test_bonn(self):
        assert 'Bonn' in self.r['institution']


class TestUnificationVision:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.r = unification_vision()

    def test_five_geometries(self):
        assert len(self.r['unified_geometry']) >= 5

    def test_kedlaya(self):
        assert 'Kedlaya' in self.r['kedlaya_description']['author']


class TestProEtaleSite:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.r = pro_etale_site()

    def test_year(self):
        assert self.r['bhatt_scholze']['year'] == 2013

    def test_profinite(self):
        assert 'profinite' in self.r['bhatt_scholze']['key_insight'].lower()


class TestCondensedPhysics:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.r = condensed_physics()

    def test_quantum(self):
        assert 'quantum' in self.r['connections']['functional_analysis']['relevance'].lower()


class TestFormalization:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.r = formalization()

    def test_lean(self):
        assert 'Lean' in self.r['lean_verification']['system']

    def test_frontier(self):
        assert 'frontier' in self.r['impact_on_math']['frontier'].lower() or \
               'cutting' in self.r['impact_on_math']['frontier'].lower()


class TestE8Condensed:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.r = e8_condensed()

    def test_w33_chain(self):
        assert any('W(3,3)' in p for p in self.r['w33_chain']['path'])


class TestCompleteChain:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.r = complete_chain()

    def test_six_links(self):
        assert len(self.r['links']) == 6

    def test_topology_miracle(self):
        assert 'TOPOLOGY' in self.r['miracle']['statement']


class TestRunAllChecks:
    def test_all_checks_pass(self):
        assert run_all_checks() is True
