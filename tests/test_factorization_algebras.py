"""Tests for Pillar 192 - Factorization Algebras."""
import pytest
import importlib

@pytest.fixture(scope="module")
def P192():
    return importlib.import_module("THEORY_PART_CCXCII_FACTORIZATION_ALGEBRAS")

class TestFactorizationAlgebrasBasics:
    def test_beilinson_drinfeld(self, P192):
        r = P192.factorization_algebras_basics()
        assert 'Beilinson' in r['definition']['beilinson_drinfeld']
    def test_locality(self, P192):
        r = P192.factorization_algebras_basics()
        assert 'locality' in r['definition']['locality'].lower() or 'Locality' in r['definition']['locality']
    def test_40_vertex_ops(self, P192):
        r = P192.factorization_algebras_basics()
        assert '40' in r['w33_factorization']['vertex_ops']
    def test_ope(self, P192):
        r = P192.factorization_algebras_basics()
        assert 'OPE' in r['definition']['ope'] or 'product expansion' in r['definition']['ope']

class TestCostelloGwilliam:
    def test_vol1(self, P192):
        r = P192.costello_gwilliam()
        assert '2017' in r['perturbative']['book_vol1']
    def test_bv(self, P192):
        r = P192.costello_gwilliam()
        assert 'BV' in r['bv']['classical_bv'] or 'symplectic' in r['bv']['classical_bv']
    def test_anomaly_free(self, P192):
        r = P192.costello_gwilliam()
        assert 'anomaly' in r['w33_bv']['anomaly_free'].lower()
    def test_master_eq(self, P192):
        r = P192.costello_gwilliam()
        assert 'master equation' in r['bv']['master_equation'].lower()

class TestFactorizationHomology:
    def test_ayala_francis(self, P192):
        r = P192.factorization_homology()
        assert 'Ayala' in r['definition']['ayala_francis']
    def test_circle(self, P192):
        r = P192.factorization_homology()
        assert 'HH' in r['computations']['circle'] or 'Hochschild' in r['computations']['circle']
    def test_excision(self, P192):
        r = P192.factorization_homology()
        assert 'Excision' in r['definition']['excision'] or 'excision' in r['definition']['excision']

class TestChiralAlgebras:
    def test_ran(self, P192):
        r = P192.chiral_algebras()
        assert 'Ran' in r['chiral']['ran_space']
    def test_verlinde(self, P192):
        r = P192.chiral_algebras()
        assert 'Verlinde' in r['conformal_blocks']['verlinde']
    def test_kz(self, P192):
        r = P192.chiral_algebras()
        assert 'KZ' in r['conformal_blocks']['kz_equation']

class TestPrefactorizationNets:
    def test_haag_kastler(self, P192):
        r = P192.prefactorization_and_nets()
        assert 'Haag' in r['aqft']['haag_kastler']
    def test_reeh_schlieder(self, P192):
        r = P192.prefactorization_and_nets()
        assert 'Reeh' in r['aqft']['reeh_schlieder']
    def test_vacuum(self, P192):
        r = P192.prefactorization_and_nets()
        assert 'Sp(6,F2)' in r['w33_nets']['vacuum']

class TestOperadicPerspective:
    def test_e_n(self, P192):
        r = P192.operadic_perspective()
        assert 'E_n' in r['operads']['e_n']
    def test_deligne(self, P192):
        r = P192.operadic_perspective()
        assert 'Deligne' in r['algebras']['deligne']
    def test_kontsevich(self, P192):
        r = P192.operadic_perspective()
        assert 'Kontsevich' in r['algebras']['kontsevich_formality']

class TestSelfChecks:
    def test_all_pass(self, P192):
        assert P192.run_self_checks() is True
