"""Tests for Pillar 149: The Langlands Program."""
import pytest, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'pillars'))

from THEORY_PART_CCXLIX_LANGLANDS_PROGRAM import (
    langlands_letter,
    reciprocity_conjecture,
    functoriality_conjecture,
    fundamental_lemma,
    geometric_langlands,
    kapustin_witten,
    wiles_fermat,
    langlands_dual,
    automorphic_forms,
    trace_formula,
    langlands_awards,
    complete_chain,
    run_all_checks,
)


class TestLanglandsLetter:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.r = langlands_letter()

    def test_year(self):
        assert self.r['year'] == 1967

    def test_recipient(self):
        assert self.r['recipient'] == 'Andre Weil'

    def test_fields_medals(self):
        assert len(self.r['impact']['fields_medals']) >= 3

    def test_abel_prize(self):
        assert '2018' in self.r['impact']['abel_prize']


class TestReciprocity:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.r = reciprocity_conjecture()

    def test_n1_proved(self):
        assert self.r['classical_cases']['n_equals_1']['status'] == 'PROVED'

    def test_n2_wiles(self):
        assert 'Wiles' in self.r['classical_cases']['n_equals_2']['proved_by']

    def test_fermat_corollary(self):
        assert 'Fermat' in self.r['classical_cases']['n_equals_2']['corollary']

    def test_lafforgue_function_fields(self):
        assert 'Lafforgue' in self.r['classical_cases']['general_n']['function_fields']

    def test_l_functions_euler(self):
        af = automorphic_forms()
        assert 'euler' in af['hecke_operators']['euler_product'].lower()


class TestFunctoriality:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.r = functoriality_conjecture()

    def test_e8_self_dual(self):
        assert 'SELF-DUAL' in self.r['l_group']['examples']['E8']

    def test_gl_n_self_dual(self):
        assert 'self-dual' in self.r['l_group']['examples']['GL_n'].lower()

    def test_b_c_swap(self):
        assert 'Sp' in self.r['l_group']['examples']['SO_2n_plus_1']
        assert 'SO' in self.r['l_group']['examples']['Sp_2n']

    def test_w33_chain(self):
        assert 'W(3,3)' in self.r['e8_self_duality']['w33_chain']


class TestFundamentalLemma:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.r = fundamental_lemma()

    def test_ngo(self):
        assert 'Ngo' in self.r['proved_by']

    def test_year_proved(self):
        assert self.r['year_proved'] == 2008

    def test_fields_medal(self):
        assert self.r['fields_medal'] == 2010

    def test_25_years(self):
        assert self.r['year_proved'] - self.r['year_conjectured'] == 25

    def test_hitchin(self):
        assert 'hitchin' in self.r['proof_method']['key_innovation'].lower() or \
               'Hitchin' in self.r['proof_method']['hitchin_system']


class TestGeometricLanglands:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.r = geometric_langlands()

    def test_proof_year(self):
        assert self.r['gaitsgory_proof_2024']['year'] == 2024

    def test_team_size(self):
        assert self.r['gaitsgory_proof_2024']['team_size'] == 9

    def test_pages(self):
        assert '1000' in self.r['gaitsgory_proof_2024']['pages']

    def test_papers(self):
        assert self.r['gaitsgory_proof_2024']['papers'] == 5

    def test_bun_g(self):
        assert 'moduli' in self.r['objects']['bun_g'].lower()


class TestKapustinWitten:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.r = kapustin_witten()

    def test_year(self):
        assert self.r['year'] == 2007

    def test_s_duality(self):
        assert 'S-duality' in self.r['key_insight']['statement']

    def test_mirror_symmetry(self):
        assert 'mirror' in self.r['implications']['mirror_symmetry'].lower()

    def test_witten(self):
        assert any('Witten' in a for a in self.r['authors'])


class TestWilesFermat:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.r = wiles_fermat()

    def test_year(self):
        assert self.r['year'] == 1995

    def test_years_open(self):
        assert self.r['theorem']['years_open'] == 358

    def test_langlands_case(self):
        assert 'GL(2)' in self.r['modularity']['langlands_case']

    def test_bcdt(self):
        assert '2001' in self.r['modularity']['bcdt']


class TestLanglandsDual:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.r = langlands_dual()

    def test_all_exceptional_self_dual(self):
        assert self.r['exceptional_self_dual_count'] == 5

    def test_e8_self_dual(self):
        assert self.r['examples']['E8']['self_dual_lie'] is True

    def test_b_c_not_self_dual(self):
        assert self.r['examples']['B_n']['self_dual_lie'] is False
        assert self.r['examples']['C_n']['self_dual_lie'] is False

    def test_cartan_transpose(self):
        assert 'transpose' in self.r['construction']['cartan_matrix'].lower() or \
               'Transpose' in self.r['construction']['cartan_matrix']


class TestAutomorphicForms:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.r = automorphic_forms()

    def test_e8_theta_240(self):
        assert '240' in self.r['examples']['e8_automorphic']['theta_series']

    def test_e8_weight_4(self):
        assert '4' in self.r['examples']['e8_automorphic']['modular_form']

    def test_hecke_operators(self):
        assert 'T_p' in self.r['hecke_operators']['definition']


class TestTraceFormula:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.r = trace_formula()

    def test_selberg_year(self):
        assert self.r['selberg']['year'] == 1956

    def test_spectral_geometric(self):
        assert 'trace' in self.r['selberg']['spectral_side'].lower() or \
               'spectral' in self.r['selberg']['spectral_side'].lower()
        assert 'conjugacy' in self.r['selberg']['geometric_side'].lower()


class TestLanglandsAwards:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.r = langlands_awards()

    def test_four_fields_medals(self):
        assert self.r['total_fields_medals'] >= 4

    def test_abel_prize_2018(self):
        assert self.r['abel_prize']['langlands_2018']['year'] == 2018

    def test_scholze(self):
        assert 'scholze_2018' in self.r['fields_medals']


class TestCompleteChain:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.r = complete_chain()

    def test_six_links(self):
        assert len(self.r['links']) == 6

    def test_miracle_statement(self):
        assert 'NUMBER THEORY' in self.r['miracle']['statement']

    def test_unification_scope(self):
        assert len(self.r['unification']) >= 5

    def test_physics_in_unification(self):
        assert 'physics' in self.r['unification']


class TestRunAllChecks:
    def test_all_checks_pass(self):
        assert run_all_checks() is True
