"""Tests for Pillar 200 - Geometric Langlands (Milestone!)."""
import pytest
import importlib

@pytest.fixture(scope="module")
def P200():
    return importlib.import_module("THEORY_PART_CCC_GEOMETRIC_LANGLANDS")

class TestGeometricLanglandsBasics:
    def test_langlands_1967(self, P200):
        r = P200.geometric_langlands_basics()
        assert 'Langlands' in r['classical_langlands']['langlands_letter_1967']
    def test_dual_group(self, P200):
        r = P200.geometric_langlands_basics()
        assert 'dual' in r['classical_langlands']['langlands_dual_group'].lower() or 'SO(7)' in r['classical_langlands']['langlands_dual_group']
    def test_d_modules(self, P200):
        r = P200.geometric_langlands_basics()
        assert 'Beilinson' in r['geometric_langlands']['beilinson_drinfeld']
    def test_hecke(self, P200):
        r = P200.geometric_langlands_basics()
        assert 'Hecke' in r['geometric_langlands']['hecke_eigensheaves']

class TestArinkinGaitsgory:
    def test_singular_support(self, P200):
        r = P200.arinkin_gaitsgory()
        assert 'singular' in r['arinkin_gaitsgory_2015']['singular_support'].lower() or 'Singular' in r['arinkin_gaitsgory_2015']['singular_support']
    def test_ind_coherent(self, P200):
        r = P200.arinkin_gaitsgory()
        assert 'ind' in r['arinkin_gaitsgory_2015']['ind_coherent_sheaves'].lower() or 'Ind' in r['arinkin_gaitsgory_2015']['ind_coherent_sheaves']
    def test_ben_zvi_nadler(self, P200):
        r = P200.arinkin_gaitsgory()
        assert 'Ben-Zvi' in r['betti_langlands']['ben_zvi_nadler']

class TestFarguesScholze:
    def test_2021(self, P200):
        r = P200.fargues_scholze()
        assert '2021' in r['fargues_scholze_2021']['geometrization'] or 'Fargues' in r['fargues_scholze_2021']['geometrization']
    def test_fargues_fontaine(self, P200):
        r = P200.fargues_scholze()
        assert 'Fargues' in r['fargues_scholze_2021']['fargues_fontaine_curve']
    def test_perfectoid(self, P200):
        r = P200.fargues_scholze()
        assert 'Scholze' in r['perfectoid_spaces']['scholze_2012']
    def test_diamonds(self, P200):
        r = P200.fargues_scholze()
        assert 'diamond' in r['perfectoid_spaces']['diamonds'].lower() or 'Diamond' in r['perfectoid_spaces']['diamonds']

class TestKapustinWitten:
    def test_s_duality(self, P200):
        r = P200.kapustin_witten()
        assert 'S-duality' in r['kapustin_witten_2007']['s_duality'] or 'duality' in r['kapustin_witten_2007']['s_duality'].lower()
    def test_branes(self, P200):
        r = P200.kapustin_witten()
        assert 'brane' in r['branes_and_sheaves']['a_branes'].lower() or 'A-brane' in r['branes_and_sheaves']['a_branes']
    def test_wilson(self, P200):
        r = P200.kapustin_witten()
        assert 'Wilson' in r['branes_and_sheaves']['wilson_lines']

class TestLanglandsPhysics:
    def test_agt(self, P200):
        r = P200.langlands_and_physics()
        assert 'AGT' in r['agt_correspondence']['alday_gaiotto_tachikawa_2010'] or 'Alday' in r['agt_correspondence']['alday_gaiotto_tachikawa_2010']
    def test_coulomb(self, P200):
        r = P200.langlands_and_physics()
        assert 'Coulomb' in r['coulomb_branches']['braverman_finkelberg_nakajima'] or 'coulomb' in r['coulomb_branches']['braverman_finkelberg_nakajima'].lower()
    def test_3d_mirror(self, P200):
        r = P200.langlands_and_physics()
        assert 'mirror' in r['coulomb_branches']['3d_mirror_symmetry'].lower() or 'Mirror' in r['coulomb_branches']['3d_mirror_symmetry']

class TestW33Langlands:
    def test_sp6f2(self, P200):
        r = P200.w33_langlands_synthesis()
        assert 'Sp(6' in r['sp6f2_langlands_group']['finite_langlands']
    def test_1451520(self, P200):
        r = P200.w33_langlands_synthesis()
        assert '1451520' in r['l_functions_w33']['l_function_special_value']
    def test_40_automorphic(self, P200):
        r = P200.w33_langlands_synthesis()
        assert '40' in r['automorphic_spectrum']['w33_points_as_data']
    def test_so7(self, P200):
        r = P200.w33_langlands_synthesis()
        assert 'SO(7' in r['sp6f2_langlands_group']['langlands_dual_so7']

class TestSelfChecks:
    def test_all_pass(self, P200):
        assert P200.run_self_checks() is True
